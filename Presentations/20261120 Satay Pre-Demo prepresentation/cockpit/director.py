import argparse
import json
import math
import os
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import artifacts
import layout
import recorder
import workflow
from common import (COMMAND, Error, LABELS, PANES, ROOT, RUN, SESSION, SOCKET, active, append, emit,
                    events, locked, now, quiet, read, relative, tmux, write)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Error(message)


def parse(argv):
    parser = Parser(prog="cockpit")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("down", "attach", "status", "next", "back", "resume", "bundle", "_quiet", "_help"):
        commands.add_parser(name)
    commands.add_parser("up").add_argument("--script", default="demo/script.json")
    commands.add_parser("run").add_argument("step")
    commands.add_parser("pause").add_argument("--toggle", action="store_true")
    commands.add_parser("focus").add_argument("pane", choices=PANES)
    commands.add_parser("diff").add_argument("cc")
    commands.add_parser("result").add_argument("arm")
    commands.add_parser("view").add_argument("view", choices=("results", "diff"))
    commands.add_parser("say").add_argument("text")
    commands.add_parser("record").add_argument("action", choices=("start", "stop"))
    auto = commands.add_parser("autopilot")
    auto.add_argument("--from", dest="step")
    auto.add_argument("--speed", type=float, default=1)
    wording = commands.add_parser("_wording")
    wording.add_argument("action", choices=("add",))
    wording.add_argument("old")
    wording.add_argument("new")
    wording.add_argument("reason")
    return parser.parse_args(argv)


def invoke(directory, argv):
    launcher = os.environ.get("COCKPIT_INVOKER", str(COMMAND))
    exact = [launcher, *(argv[1:] if argv[0] == "_wording" else argv)]
    append(directory / "invocations.jsonl", {
        "wall": now(), "argv": exact, "command": shlex.join(exact),
        "cwd": os.environ.get("COCKPIT_INVOKER_CWD", str(ROOT)),
    })


def spawn(directory, *args):
    with (directory / "director.log").open("ab") as log:
        return subprocess.Popen(["python3", "-B", *args], cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=log, start_new_session=True).pid


def running():
    return tmux("has-session", "-t", SESSION, check=False).returncode == 0


def setup(args, argv):
    if running():
        directory = active()
        invoke(directory, argv)
        return {"run": directory.name, "socket": relative(SOCKET)}
    script = read(artifacts.scoped(ROOT, args.script))
    workflow.validate(script)
    catalog = read(ROOT / "demo/ccs.json")
    directory = RUN / (now().replace("-", "").replace(":", "")[:15] + "-" + uuid.uuid4().hex[:6])
    directory.mkdir()
    for name in ("output", "panes", "artifacts"):
        (directory / name).mkdir()
    for name in ("events.jsonl", "wording-log.jsonl", "invocations.jsonl"):
        (directory / name).touch()
    state = {"run": directory.name, "script_source": args.script, "script": script, "catalog": catalog,
             "state": "ready", "paused": False, "current_step": None, "steps": {}, "worker": None,
             "autopilot": False, "last_error": None, "selected_cc": "expert_weight_cache",
             "view": "results", "result_arm": None, "caption": "", "recording": None, "casts": []}
    save(directory, state)
    write(directory / "source-at-start.json", artifacts.provenance())
    try:
        state["pane_ids"] = layout.setup(directory)
        state["pane_snapshot"] = layout.snapshot(state["pane_ids"])
        save(directory, state)
    except Exception:
        tmux("kill-session", "-t", SESSION, check=False)
        shutil.rmtree(directory)
        raise
    pointer = RUN / "active.tmp"
    pointer.write_text(directory.name + "\n")
    pointer.replace(RUN / "active")
    invoke(directory, argv)
    return {"run": directory.name, "socket": relative(SOCKET)}


def save(directory, state):
    write(directory / "state.json", state)


def stage_of(state):
    for step in state["script"]:
        if step["id"] == state["current_step"]:
            return step["action"]["stage"]
    return "fixture" if all(s["action"]["stage"] == "fixture" for s in state["script"]) else None


def clean_worker(directory, state):
    if state["worker"] and not workflow.alive(state["worker"]):
        state["worker"] = None
        state["autopilot"] = False
        state["state"] = "failed"
        state["last_error"] = "Director worker exited"
        if state["current_step"]:
            state["steps"][state["current_step"]] = "fail"
            emit(directory, "task", "fail", step=state["current_step"], stage=stage_of(state),
                 data={"error": state["last_error"]})
        save(directory, state)


def status(directory, state):
    log = events(directory)
    is_quiet = (directory / "QUIET").exists()
    if state["state"] == "down":
        panes = {name: {"id": pane, "pid": None, "dead": True} for name, pane in state["pane_ids"].items()}
    elif is_quiet:
        panes = state["pane_snapshot"]
    else:
        with locked(directory / "activity.lock", exclusive=False):
            panes = (state["pane_snapshot"] if (directory / "QUIET").exists()
                     else layout.snapshot(state["pane_ids"]))
    return {
        "run": directory.name, "current_step": state["current_step"], "state": state["state"],
        "pending_steps": [s["id"] for s in state["script"] if state["steps"].get(s["id"]) not in ("ok", "start")],
        "last_event": log[-1] if log else None, "quiet": is_quiet, "selected_cc": state["selected_cc"],
        "panes": panes, "view": state["view"], "result_arm": state["result_arm"],
        "paused": state["paused"], "autopilot": state["autopilot"], "recording": state["recording"],
        "last_error": state["last_error"], "caption": state["caption"],
    }


def schedule(directory, state, args):
    current = state["current_step"]
    multiple = args.command == "autopilot"
    requested = getattr(args, "step", None)
    if state["worker"]:
        if (args.command == "next" or (args.command == "run" and current == requested)
                or (multiple and state["autopilot"] and requested in (None, current))):
            return {"step": current, "state": state["state"]}
        raise Error("A step is already scheduled")
    if requested:
        index = workflow.find(state, requested)
    elif current:
        finished = state["steps"].get(current)
        if args.command == "next" and finished == "fail":
            raise Error(f"{current} failed. Retry with cockpit run {current}.")
        index = workflow.find(state, current) + (finished == "ok")
    else:
        index = 0
    if index >= len(state["script"]):
        return {"step": current, "state": state["state"]}
    speed = getattr(args, "speed", 1)
    if not math.isfinite(speed) or speed <= 0:
        raise Error("Speed must be a positive finite number")
    restored = layout.recover(directory, state)
    state["pane_snapshot"] = layout.snapshot(state["pane_ids"])
    step = state["script"][index]
    state["current_step"] = step["id"]
    if state["steps"].get(step["id"]) == "fail":
        emit(directory, "decision", stage=step["action"]["stage"],
             data={"decision": "retry", "reason": state["last_error"] or "Operator requested a retry."},
             step=step["id"])
    state["state"] = "paused" if state["paused"] else "running"
    state["autopilot"] = multiple
    state["worker"] = spawn(directory, "director.py", "_worker", directory.name, str(index),
                            str(int(multiple)), str(speed))
    save(directory, state)
    return {"step": step["id"], "state": state["state"], "recovered": restored}


def select_result(directory, state, args):
    found = next((e for e in reversed(events(directory)) if e["kind"] == "result" and e["status"] == "ok"
                  and e["data"].get("arm") == args.arm), None)
    if not found:
        raise Error(f"No result receipt for arm {args.arm}")
    state["view"], state["result_arm"] = "results", args.arm
    return {"arm": args.arm, "stage": found["stage"], "stage_label": LABELS[found["stage"]],
            "ref": found["ref"], "sha256": found["sha256"], "receipt": read(artifacts.scoped(ROOT, found["ref"]))}


def interactive(directory, state, args):
    cmd = args.command
    if cmd in ("next", "run", "autopilot"):
        return schedule(directory, state, args)
    if cmd == "back":
        if state["worker"]:
            raise Error("A step is already scheduled")
        current = state["current_step"]
        index = workflow.find(state, current) - 1 if current else -1
        state["current_step"] = state["script"][index]["id"] if index >= 0 else None
        state["state"] = "paused" if state["paused"] else "ready"
        state["caption"] = state["script"][index]["narration"] if index >= 0 else ""
        layout.caption(state["caption"])
        return {"step": state["current_step"]}
    if cmd == "focus":
        pane = args.pane
        result = {"pane": pane}
    elif cmd == "view":
        state["view"] = args.view
        pane, result = "result", {"view": args.view}
    elif cmd == "result":
        pane, result = "result", select_result(directory, state, args)
    elif cmd == "diff":
        names = [card["id"] for card in state["catalog"]]
        cc = args.cc
        if cc in ("next", "prev"):
            diff_ccs = {e["cc"] for e in events(directory) if e["data"].get("diff_stat")}
            candidates = [name for name in names if name in diff_ccs] or names
            index = candidates.index(state["selected_cc"]) if state["selected_cc"] in candidates else -1
            cc = candidates[(index + (1 if cc == "next" else -1)) % len(candidates)]
        if cc not in names:
            raise Error(f"Unknown Capability Capsule {cc}")
        state["selected_cc"] = cc
        state["view"] = "diff"
        pane, result = "result", {"cc": cc, "view": "diff"}
    elif cmd == "say":
        text = " ".join(args.text.split())
        record = artifacts.wording(directory, state, state["caption"], text, "Spoken caption")
        state["caption"] = text
        layout.caption(text)
        return {"caption": text, "wording": record}
    elif cmd == "record":
        cast = recorder.start(directory, state, spawn) if args.action == "start" else recorder.stop(directory, state)
        return {"cast": cast, "recording": bool(state["recording"])}
    elif cmd == "_help":
        help_text = "n next   b back   d / D diffs   r results\np pause / resume   q quiet   ? help\n\nDiff pager: j / k, PgUp / PgDn, g\nPress any key to close."
        command = "printf '%s\\n' " + shlex.quote(help_text) + "; read -r -s -n 1"
        tmux("display-popup", "-E", "-w", "52", "-h", "10", "bash -c " + shlex.quote(command))
        return {"help": True}
    else:
        raise Error(f"Unknown command {cmd}")
    tmux("select-pane", "-t", state["pane_ids"][pane])
    return result


def dispatch(directory, state, args):
    cmd = args.command
    if cmd == "status":
        return status(directory, state)
    if cmd == "down" and state["state"] == "down":
        return {"state": "down"}
    if cmd == "bundle":
        if state["worker"] or state["recording"] or (directory / "QUIET").exists():
            raise Error("Finish the current step, leave quiet mode and stop recording before bundling.")
        return {"bundle": relative(artifacts.bundle(directory, state))}
    if not running():
        raise Error("Private tmux server is down. Use cockpit up.")
    if cmd in ("pause", "resume"):
        state["paused"] = (not state["paused"] if args.toggle else True) if cmd == "pause" else False
        if not state["paused"] and not state["worker"]:
            complete = all(state["steps"].get(s["id"]) == "ok" for s in state["script"])
            state["state"] = "failed" if state["last_error"] else "complete" if complete else "ready"
        else:
            state["state"] = "paused" if state["paused"] else "running"
        return {"state": state["state"], "paused": state["paused"]}
    if cmd == "_quiet":
        if state["worker"]:
            raise Error("The active step manages quiet mode")
        mode = "off" if (directory / "QUIET").exists() else "on"
        if mode == "on":
            state["pane_snapshot"] = layout.snapshot(state["pane_ids"])
        quiet(directory, mode, state["current_step"], stage_of(state))
        return {"quiet": mode == "on"}
    if cmd == "_wording":
        return artifacts.wording(directory, state, args.old, args.new, args.reason)
    with locked(directory / "activity.lock", exclusive=False):
        if (directory / "QUIET").exists():
            raise Error("Quiet mode is active")
        if cmd == "down":
            if state["worker"]:
                raise Error("Wait for the active step before stopping the server")
            recorder.stop(directory, state)
            tmux("kill-session", "-t", SESSION, check=False)
            state["state"] = "down"
            return {"state": "down"}
        return interactive(directory, state, args)


def main(argv):
    if argv and argv[0] == "_worker":
        _, run_id, index, multiple, speed = argv
        return workflow.worker(RUN / run_id, int(index), bool(int(multiple)), float(speed))
    args = parse(argv)
    RUN.mkdir(exist_ok=True)
    with locked(RUN / "director.lock"):
        if args.command == "up":
            result = setup(args, argv)
        else:
            try:
                directory = active()
            except Error:
                if args.command == "down":
                    print(json.dumps({"ok": True, "state": "down"}))
                    return 0
                raise
            with locked(directory / "state.lock"):
                state = read(directory / "state.json")
                clean_worker(directory, state)
                invoke(directory, argv)
                if args.command != "attach":
                    before = json.dumps(state)
                    result = dispatch(directory, state, args)
                    if json.dumps(state) != before:
                        save(directory, state)
    if args.command == "attach":
        if (directory / "QUIET").exists():
            raise Error("Quiet mode is active")
        os.environ.pop("TMUX", None)
        os.environ.pop("TMUX_PANE", None)
        os.execvp("tmux", ["tmux", "-S", str(SOCKET), "attach-session", "-t", SESSION])
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip()
        print(json.dumps({"ok": False, "error": detail or f"Command failed ({error.returncode})"}))
        sys.exit(1)
    except (Error, OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        sys.exit(1)
