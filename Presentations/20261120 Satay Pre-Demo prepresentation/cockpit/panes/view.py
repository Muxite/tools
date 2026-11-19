import json
import os
import re
import select
import sys
import termios
import time
import textwrap
import tty
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import LABELS, ROOT, events, locked, read

RESET = "\x1b[0m"
COLORS = {
    "fixture": 33, "native": 36, "compile": 35, "runtime": 34, "hardware": 32,
    "note": 37, "quiet": 33, "plan": 36, "fail": 31,
}
ANSI = re.compile(r"\x1b\[[0-9;]*m")
CONTROL = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\a]*(?:\a|\x1b\\))|[\x00-\x1f\x7f]")


def tone(text, color):
    return f"\x1b[{color}m{text}{RESET}"


def visible(text, width):
    parts = ANSI.split(text)
    escapes = ANSI.findall(text)
    line = ""
    for index, part in enumerate(parts):
        if width <= 0:
            break
        clean = CONTROL.sub("", part.expandtabs(4))
        line += clean[:width]
        width -= len(clean)
        if index < len(escapes):
            line += escapes[index]
    return line + RESET


def wrap(text, width):
    return textwrap.wrap(str(text), max(1, width)) or [""]


def header(title):
    return tone(title, "1;36")


def stamp(path):
    try:
        info = path.stat()
        return info.st_size, info.st_mtime_ns
    except FileNotFoundError:
        return None


def ref_path(event):
    return ROOT / event["ref"] if event.get("ref") else None


def tail(path, length):
    with path.open(errors="replace") as stream:
        stream.seek(0, os.SEEK_END)
        stream.seek(max(0, stream.tell() - 65536))
        return list(deque(stream.read().splitlines(), maxlen=max(1, length)))


def follow(name, render, paths=None):
    directory = Path(sys.argv[1])
    terminals = sys.stdin.isatty() and name in ("plan", "cc", "result")
    previous = None
    offset = 0
    view_key = None
    old_tty = termios.tcgetattr(0) if terminals else None
    if terminals:
        tty.setcbreak(0)
    try:
        while True:
            if (directory / "QUIET").exists():
                time.sleep(2)
                continue
            with locked(directory / "activity.lock", exclusive=False):
                if (directory / "QUIET").exists():
                    continue
                size = os.get_terminal_size()
                state_path = directory / "state.json"
                event_path = directory / "events.jsonl"
                state_stamp = stamp(state_path)
                event_stamp = stamp(event_path)
                if previous is None or previous[0:2] != (state_stamp, event_stamp):
                    state, log = read(state_path), events(directory)
                    key = state["view"], state["selected_cc"], state.get("result_arm")
                    if key != view_key:
                        offset, view_key = 0, key
                if terminals and select.select([0], [], [], 0)[0]:
                    keys = os.read(0, 64)
                    if keys in (b"j", b"\x1b[B", b"\x1b[6~", b" "):
                        offset += max(1, size.lines - 4) if keys in (b"\x1b[6~", b" ") else 1
                    elif keys in (b"k", b"\x1b[A", b"\x1b[5~"):
                        offset = max(0, offset - (size.lines - 4 if keys == b"\x1b[5~" else 1))
                    elif keys == b"g":
                        offset = 0
                extras = tuple(stamp(path) for path in (paths(directory, state, log) if paths else []))
                signature = state_stamp, event_stamp, size, offset, extras
                if signature != previous:
                    lines, offset = render(directory, state, log, size.columns, size.lines, offset)
                    sys.stdout.write("\x1b[?25l\x1b[H\x1b[2J" + "\r\n".join(
                        visible(line, size.columns) for line in lines[:size.lines]
                    ) + RESET)
                    sys.stdout.flush()
                    previous = state_stamp, event_stamp, size, offset, extras
            time.sleep(1)
    finally:
        if terminals:
            termios.tcsetattr(0, termios.TCSADRAIN, old_tty)
        sys.stdout.write("\x1b[?25h")
