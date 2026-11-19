import json
import os
import signal
import socket
import subprocess
import sys
import threading
from pathlib import Path

from view import LABELS, ROOT, follow, header, tail
from common import quiet


def execute(directory, job):
    output = ROOT / job["output"]
    env = {**os.environ, "COCKPIT_RUN": directory.name, "COCKPIT_STEP": job["step"],
           "COCKPIT_STAGE": job["stage"] or "", "COCKPIT_SPEED": str(job["speed"]),
           "COCKPIT_JOB": job["id"]}
    measuring = job["quiet"]
    if measuring:
        quiet(directory, "on", job["step"], job["stage"])
    expired = threading.Event()
    try:
        with output.open("xb", buffering=0) as stream:
            stream.write(("$ " + job["command"] + "\n").encode())
            process = subprocess.Popen(
                ["bash", "-c", job["command"]], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                stdout=stream, stderr=subprocess.STDOUT, start_new_session=True,
            )

            def expire():
                expired.set()
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

            timer = threading.Timer(job["timeout"], expire)
            timer.start()
            try:
                code = process.wait()
            finally:
                timer.cancel()
                timer.join()
            stream.write(f"\n[exit {code}]\n".encode())
        return {"exit": code, "timed_out": expired.is_set()}
    finally:
        if measuring:
            quiet(directory, "off", job["step"], job["stage"])


def serve(directory):
    path = directory / "experiment.sock"
    path.unlink(missing_ok=True)
    with socket.socket(socket.AF_UNIX) as listener:
        listener.bind(str(path))
        listener.listen(1)
        while True:
            connection, _ = listener.accept()
            with connection, connection.makefile("r") as stream:
                try:
                    job = json.loads(stream.readline())
                    result = execute(directory, job)
                except Exception as error:
                    result = {"error": str(error)}
                try:
                    connection.sendall(json.dumps(result).encode() + b"\n")
                except (BrokenPipeError, ConnectionResetError):
                    pass


def source(state, log):
    current = state["current_step"]
    runs = [event for event in log if event["kind"] == "run" and event["data"].get("output")]
    exact = next((event for event in reversed(runs) if event["step"] == current), None)
    step = next((step for step in state["script"] if step["id"] == current), None)
    if exact or not step or step["action"]["type"] in ("shell", "quiet_run"):
        return exact
    return runs[-1] if runs else None


def paths(directory, state, log):
    event = source(state, log)
    return [ROOT / event["data"]["output"]] if event else []


def render(directory, state, log, width, height, offset):
    lines = [header("EXPERIMENT  •  COMMAND OUTPUT")]
    event = source(state, log)
    if not event:
        step = next((step for step in state["script"] if step["id"] == state["current_step"]), None)
        if step:
            lines.extend(["", f'{step["id"]} {step["title"]}', step["narration"]])
        else:
            lines += ["", "Awaiting a step from the director."]
        return lines, 0
    path = ROOT / event["data"]["output"]
    label = LABELS[event["stage"]]
    lines.append(f'{event["step"]} [{label}] {path.name}')
    if path.is_file():
        lines.extend(tail(path, height - 2))
    return lines, 0


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    threading.Thread(target=serve, args=(directory,), daemon=True).start()
    follow("experiment", render, paths)
