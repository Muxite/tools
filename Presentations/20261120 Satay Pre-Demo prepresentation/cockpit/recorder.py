import errno
import fcntl
import os
import pty
import shlex
import shutil
import struct
import sys
import termios
import time
from pathlib import Path

import layout
from common import Error, SESSION, SOCKET, now, read, relative, tmux, write


def pipe(path):
    with path.open("ab", buffering=0) as target:
        partial = b""
        while chunk := sys.stdin.buffer.read1(65536):
            lines = (partial + chunk).split(b"\n")
            for line in lines[:-1]:
                target.write(f"[{now()}] ".encode() + line + b"\n")
            partial = lines[-1]
        if partial:
            target.write(f"[{now()}] ".encode() + partial)


def client(directory):
    write(directory / "record-client.json", {"tty": os.ttyname(0)})
    os.environ.pop("TMUX", None)
    os.environ.pop("TMUX_PANE", None)
    os.execvp("tmux", ["tmux", "-S", str(SOCKET), "attach-session", "-t", SESSION, "-f", "ignore-size"])


def capture(directory, cast, asciinema, width, height):
    pid, master = pty.fork()
    if pid == 0:
        fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", height, width, 0, 0))
        os.environ["TERM"] = "xterm-256color"
        os.environ["XDG_CONFIG_HOME"] = str(directory / "asciinema-config")
        command = shlex.join(["python3", "-B", "recorder.py", "client", str(directory)])
        os.execv(asciinema, [asciinema, "rec", "--quiet", "--idle-time-limit", "2",
                             "--cols", str(width), "--rows", str(height),
                             "--title", f"cockpit {directory.name}", "--command", command, str(cast)])
    try:
        while os.read(master, 65536):
            pass
    except OSError as error:
        if error.errno != errno.EIO:
            raise
    finally:
        os.close(master)
        _, status = os.waitpid(pid, 0)
        write(directory / "record-done.json", {"exit": os.waitstatus_to_exitcode(status)})


def attached(directory):
    marker = directory / "record-client.json"
    if not marker.exists():
        return None
    tty = read(marker)["tty"]
    clients = tmux("list-clients", "-t", SESSION, "-F", "#{client_tty}", check=False)
    return tty if tty in clients.stdout.splitlines() else None


def start(directory, state, spawn):
    if state.get("recording"):
        return state["recording"]
    asciinema = shutil.which("asciinema")
    if not asciinema:
        fallback = Path.home() / ".local/bin/asciinema"
        if not os.access(fallback, os.X_OK):
            raise Error("asciinema is unavailable")
        asciinema = str(fallback)
    for name in ("record-done.json", "record-client.json"):
        (directory / name).unlink(missing_ok=True)
    number = len(state["casts"]) + 1
    cast = directory / f"cockpit-{number:02d}.cast"
    for name, pane in state["pane_ids"].items():
        layout.pipe(directory, pane, name, True)
    dims = tmux("display-message", "-p", "-t", layout.WINDOW, "#{window_width} #{window_height}")
    width, height = map(int, dims.stdout.split())
    spawn(directory, "recorder.py", "capture", str(directory), str(cast), asciinema, str(width), str(height + 1))
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        if attached(directory):
            state["recording"] = relative(cast)
            state["casts"].append(relative(cast))
            return state["recording"]
        if (directory / "record-done.json").exists():
            break
        time.sleep(0.1)
    for name, pane in state["pane_ids"].items():
        layout.pipe(directory, pane, name, False)
    raise Error("asciinema did not attach")


def stop(directory, state):
    cast = state.get("recording")
    if not cast:
        return None
    if tty := attached(directory):
        tmux("detach-client", "-t", tty, check=False)
    deadline = time.monotonic() + 4
    done = directory / "record-done.json"
    while not done.exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    for name, pane in state["pane_ids"].items():
        layout.pipe(directory, pane, name, False)
    if not done.exists():
        raise Error("asciinema is still closing")
    state["recording"] = None
    if read(done)["exit"] != 0:
        raise Error("asciinema exited with an error")
    return cast


if __name__ == "__main__":
    mode, path, *args = sys.argv[1:]
    if mode == "pipe":
        pipe(Path(path))
    elif mode == "client":
        client(Path(path))
    elif mode == "capture":
        cast, binary, width, height = args
        capture(Path(path), Path(cast), binary, int(width), int(height))
