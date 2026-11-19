import json
import math
import os
import re
import socket
import time
import uuid
from pathlib import Path

import layout
from common import Error, LABELS, PANES, ROOT, emit, events, locked, quiet, read, relative, write


def alive(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def validate(script):
    if not isinstance(script, list) or not script:
        raise Error("Script must contain a nonempty list of steps")
    seen = set()
    for step in script:
        sid = step["id"]
        if not re.fullmatch(r"s[0-9]+", sid) or sid in seen:
            raise Error(f"Invalid or duplicate step ID {sid}")
        seen.add(sid)
        if step["section"] not in ("problem", "change", "compare", "scope"):
            raise Error(f"{sid} has an invalid section")
        if not math.isfinite(step["timeout_s"]) or step["timeout_s"] <= 0:
            raise Error(f"{sid} needs a positive finite timeout")
        action = step["action"]
        kind = action["type"]
        if action["stage"] not in LABELS or kind not in ("shell", "emit", "show", "wait", "quiet_run"):
            raise Error(f"{sid} has an invalid action type or stage")
        if kind in ("shell", "quiet_run") and not action.get("command"):
            raise Error(f"{sid} needs a shell command")
        if kind == "show" and action.get("pane") not in PANES:
            raise Error(f"{sid} needs a valid pane")
        if kind == "emit" and not action.get("events"):
            raise Error(f"{sid} needs events to emit")
        if not isinstance(step["title"], str) or not isinstance(step["narration"], str):
            raise Error(f"{sid} needs a title and narration")


def find(state, step_id):
    for index, step in enumerate(state["script"]):
        if step["id"] == step_id:
            return index
    raise Error(f"Unknown step {step_id}")


def matches(event, expectation, step):
    return (event["step"] == step and event["kind"] == expectation["event_kind"]
            and event["status"] == expectation["status"])


def job_request(directory, request):
    path = str(directory / "experiment.sock")
    with socket.socket(socket.AF_UNIX) as client:
        deadline = time.monotonic() + 4
        while True:
            try:
                client.connect(path)
                break
            except (FileNotFoundError, ConnectionRefusedError):
                if time.monotonic() >= deadline:
                    raise Error("Experiment pane is unavailable")
                time.sleep(0.15)
        client.sendall(json.dumps(request).encode() + b"\n")
        with client.makefile("r") as stream:
            try:
                response = json.loads(stream.readline())
            except ValueError:
                raise Error("Experiment pane exited during the command") from None
    if response.get("error"):
        raise Error(response["error"])
    return response


def run_command(directory, step, speed):
    action = step["action"]
    sid = step["id"]
    stage = action["stage"]
    job_id = uuid.uuid4().hex[:10]
    output = relative(directory / "output" / f"{sid}-{job_id}.log")
    measuring = action["type"] == "quiet_run"
    emit(directory, "run", "start", step=sid, stage=stage, data={"output": output})
    try:
        result = job_request(directory, {
            "id": job_id, "output": output, "command": action["command"], "step": sid,
            "stage": stage, "speed": speed, "quiet": measuring, "timeout": step["timeout_s"],
        })
    except Error:
        if measuring and (directory / "QUIET").exists():
            quiet(directory, "off", sid, stage)
        raise
    success = result["exit"] == 0 and not result["timed_out"]
    emit(directory, "run", "ok" if success else "fail", step=sid, stage=stage, ref=output,
         data={**result, "output": output})
    if measuring:
        receipt = action.get("ref")
        if not success or not receipt:
            receipt = relative(directory / "output" / f"{sid}-{job_id}.json")
            write(ROOT / receipt, {**result, "output": output, "stage": stage})
        emit(directory, "result", "ok" if success else "fail", step=sid, stage=stage,
             ref=receipt.format(run=directory.name, job=job_id), cc=action.get("cc"), data=action.get("data", {}))
    if not success:
        detail = "timed out" if result["timed_out"] else f'exit {result["exit"]}'
        raise Error(f'{sid} command {detail}. See {output}.')


def run_action(directory, step, speed):
    action = step["action"]
    sid = step["id"]
    stage = action["stage"]
    kind = action["type"]
    started = emit(directory, "task", "start", step=sid, stage=stage,
                   data={"title": step["title"], "narration": step["narration"]})
    checked_from = started["seq"]
    check_step = sid
    if kind in ("shell", "quiet_run"):
        run_command(directory, step, speed)
    elif kind == "emit":
        for record in action["events"]:
            options = {key: value for key, value in record.items() if key not in ("kind", "status")}
            if "ref" in options:
                options["ref"] = options["ref"].format(run=directory.name)
            emit(directory, record["kind"], record.get("status", "ok"), step=sid, stage=stage, **options)
    elif kind == "show":
        with locked(directory / "state.lock"):
            state = read(directory / "state.json")
            with locked(directory / "activity.lock", exclusive=False):
                if (directory / "QUIET").exists():
                    raise Error("Quiet mode is active")
                if "view" in action:
                    state["view"] = action["view"]
                if "cc" in action:
                    state["selected_cc"] = action["cc"]
                layout.tmux("select-pane", "-t", state["pane_ids"][action["pane"]])
                write(directory / "state.json", state)
        emit(directory, "task", "ok", step=sid, stage=stage, data={"shown": action["pane"]})
    elif kind == "wait":
        check_step = action.get("match_step", sid)
        if action.get("allow_existing"):
            checked_from = 0
    else:
        raise Error(f"Unknown action {kind}")
    deadline = time.monotonic() + (step["timeout_s"] if kind == "wait" else 0)
    while True:
        if any(matches(event, step["expect"], check_step)
               for event in events(directory) if event["seq"] > checked_from):
            break
        if time.monotonic() >= deadline:
            raise Error(f'{sid} expected {step["expect"]["event_kind"]}/{step["expect"]["status"]}')
        time.sleep(0.5)
    if kind != "show":
        emit(directory, "task", "ok", step=sid, stage=stage, data={"title": step["title"]})


def worker(directory, start, multiple, speed):
    path = directory / "state.json"
    script = read(path)["script"]
    stop = len(script) if multiple else start + 1
    for index in range(start, stop):
        step = script[index]
        sid = step["id"]
        while True:
            with locked(directory / "state.lock"):
                state = read(path)
                if not state["paused"]:
                    state["current_step"] = sid
                    state["steps"][sid] = "start"
                    state["state"] = "running"
                    state["caption"] = step["narration"]
                    with locked(directory / "activity.lock", exclusive=False):
                        if not (directory / "QUIET").exists():
                            layout.caption(state["caption"])
                    write(path, state)
                    break
            time.sleep(1)
        error = None
        try:
            run_action(directory, step, speed)
        except Exception as exc:
            error = str(exc)
            emit(directory, "task", "fail", step=sid, stage=step["action"]["stage"],
                 data={"error": error})
        with locked(directory / "state.lock"):
            state = read(path)
            state["steps"][sid] = "fail" if error else "ok"
            state["last_error"] = error
            finished = error is not None or index == stop - 1
            if finished:
                state["worker"] = None
                state["autopilot"] = False
            if error:
                state["state"] = "failed"
            elif state["paused"]:
                state["state"] = "paused"
            elif index == len(script) - 1 and all(state["steps"].get(s["id"]) == "ok" for s in script):
                state["state"] = "complete"
            else:
                state["state"] = "ready" if finished else "running"
            write(path, state)
        if error:
            return 1
    return 0
