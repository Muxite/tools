import json
import os
import pty
import shutil
import struct
import subprocess
import sys
import termios
import time
from collections import Counter
import fcntl
import select
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "panes")]
import artifacts
import cc
import data
import experiment
import plan
import result
import workflow
from common import Error, PANES, ROOT, RUN, digest, events, quiet, read, write
from panes.view import ANSI, CONTROL, visible

RENDERERS = dict(plan=plan.render, data=data.render, experiment=experiment.render,
                 cc=cc.render, result=result.render)


def atomic(directory):
    log = events(directory)
    assert len(log) == 48
    assert [event["seq"] for event in log] == list(range(1, 49))
    elapsed = [event["t_ns"] for event in log]
    assert all(isinstance(t, int) for t in elapsed) and elapsed == sorted(set(elapsed))
    assert Counter(event["data"]["writer"] for event in log) == {str(n): 6 for n in range(1, 9)}
    assert all((event["step"], event["stage"]) == ("s00", "fixture") for event in log)
    print("48 intact, consecutive events from 8 writers, with integer monotonic timestamps")


def cpu(pids):
    def ticks(pid):
        status = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return int(status[11]) + int(status[12])

    before = {name: ticks(pid) for name, pid in pids.items()}
    time.sleep(10)
    changes = {name: {"pid": pid, "delta_ticks": ticks(pid) - before[name]} for name, pid in pids.items()}
    print(json.dumps({"seconds": 10, "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"), "panes": changes}))
    assert all(0 <= change["delta_ticks"] <= 1 for change in changes.values()), changes


def fixture_state(directory):
    for name in ("output", "panes", "artifacts"):
        (directory / name).mkdir()
    for name in ("events.jsonl", "wording-log.jsonl", "invocations.jsonl"):
        (directory / name).touch()
    state = {"run": directory.name, "script": read(ROOT / "demo/script.json"),
             "catalog": read(ROOT / "demo/ccs.json"), "current_step": None, "steps": {},
             "paused": False, "state": "ready", "caption": "", "last_error": None, "view": "results",
             "selected_cc": "expert_weight_cache", "result_arm": None, "casts": []}
    state["pane_ids"] = dict(zip(PANES, range(len(PANES))))
    write(directory / "state.json", state)


def validate_fixture(directory):
    state = read(directory / "state.json")
    log = events(directory)
    kinds = Counter(event["kind"] for event in log)
    assert state["state"] == "complete" and state["current_step"] == "s14"
    assert len(state["steps"]) == 14 and set(state["steps"].values()) == {"ok"}
    assert all(event["stage"] == "fixture" for event in log)
    assert [e["status"] for e in log if e["kind"] == "task"] == ["start", "ok"] * 14
    assert [e["data"]["mode"] for e in log if e["kind"] == "quiet"] == ["on", "off"]
    assert not (directory / "QUIET").exists()
    assert kinds["result"] == 3 and len(log) == 62, kinds
    print(f'14 steps, {len(log)} fixture events, {kinds["result"]} result receipts, one quiet interval')


def validate_tamper(bundle):
    receipt = bundle / "demo/fixtures/arm-b.json"
    original = receipt.read_bytes()
    receipt.write_bytes(original + b"\n")
    try:
        artifacts.verify(bundle)
    except Error:
        pass
    else:
        raise AssertionError("Verifier accepted a changed receipt")
    finally:
        receipt.write_bytes(original)
    event_path = bundle / "events.jsonl"
    manifest = bundle / "MANIFEST.sha256"
    original_events, original_manifest = event_path.read_text(), manifest.read_text()
    log = events(bundle)
    next(e for e in log if e["kind"] == "result")["ref"] = "missing.json"
    event_path.write_text("".join(json.dumps(e) + "\n" for e in log))
    manifest.write_text("\n".join(
        digest(event_path) + "  events.jsonl" if line.endswith("  events.jsonl") else line
        for line in original_manifest.splitlines()
    ) + "\n")
    try:
        artifacts.verify(bundle)
    except Error:
        pass
    else:
        raise AssertionError("Verifier accepted a result without a receipt")
    finally:
        event_path.write_text(original_events)
        manifest.write_text(original_manifest)
    print("Verifier rejected both altered receipt bytes and a missing result reference")


def standalone_panes(directory):
    processes = {}
    masters = []
    try:
        for name in PANES:
            master, slave = pty.openpty()
            masters.append(master)
            dims = struct.pack("HHHH", 25, 60, 0, 0)
            fcntl.ioctl(slave, termios.TIOCSWINSZ, dims)
            if name == "experiment":
                args = ["-c", 'import experiment; experiment.follow("experiment", experiment.render, experiment.paths)',
                        str(directory)]
            else:
                args = [str(ROOT / "panes" / (name + ".py")), str(directory)]
            if args[0] == "-c":
                args[1] = "import sys; sys.path.insert(0, 'panes'); " + args[1]
            try:
                processes[name] = subprocess.Popen(["python3", "-B", *args], cwd=ROOT, stdin=slave,
                                                   stdout=slave, stderr=slave, start_new_session=True)
            finally:
                os.close(slave)
        for master in masters:
            ready, _, _ = select.select([master], [], [], 3)
            assert ready and b"\x1b[2J" in os.read(master, 8192), "Pane did not render"
        quiet(directory, "on", "s14", "fixture")
        cpu({name: proc.pid for name, proc in processes.items()})
        quiet(directory, "off", "s14", "fixture")
    finally:
        for process in processes.values():
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=3)
        for master in masters:
            os.close(master)


def capture_fallback(directory):
    state = read(directory / "state.json")
    log = events(directory)
    lines = ["tmux capture-pane was blocked by EPERM on the private Unix socket.",
             "The sections below are standalone renderer output at representative pane sizes."]
    for size, dims in [
        ("200x55", ((51, 33), (51, 17), (94, 53), (53, 24), (53, 27))),
        ("160x45", ((41, 27), (41, 14), (75, 43), (42, 19), (42, 22))),
    ]:
        for name, (width, height) in zip(PANES, dims):
            lines.extend(["", f"=== {size} {name.upper()} ({width}x{height}) ==="])
            body, _ = RENDERERS[name](directory, state, log, width, height, 0)
            lines.extend(CONTROL.sub("", ANSI.sub("", visible(line, width))) for line in body[:height])
        state["view"] = "diff"
        width, height = dims[-1]
        lines.extend(["", f"=== {size} DIFF ({width}x{height}) ==="])
        body, _ = result.render(directory, state, log, width, height, 0)
        lines.extend(CONTROL.sub("", ANSI.sub("", visible(line, width))) for line in body[:height])
        state["view"] = "results"
    (ROOT / "docs/layout-capture.txt").write_text("\n".join(lines) + "\n")


def recorder_probe(directory):
    binary = shutil.which("asciinema") or str(Path.home() / ".local/bin/asciinema")
    cast = directory / "socket-probe.cast"
    subprocess.run(["python3", "-B", "recorder.py", "capture", str(directory), str(cast),
                    binary, "80", "24"], cwd=ROOT, timeout=8, check=True)
    header, *frames = [json.loads(line) for line in cast.read_text().splitlines() if line]
    assert header["version"] == 2 and header["idle_time_limit"] == 2
    assert any(frame[1] == "o" and "tmux.sock" in frame[2] for frame in frames)
    pane = directory / "panes/probe.log"
    subprocess.run(["python3", "-B", "recorder.py", "pipe", str(pane)], cwd=ROOT,
                   input=b"first\r\nsecond", check=True)
    first, second = pane.read_bytes().splitlines(keepends=True)
    assert first.startswith(b"[20") and first.endswith(b"] first\r\n")
    assert second.startswith(b"[20") and second.endswith(b"] second")
    print("asciinema started in a PTY and captured the tmux socket error. Pane pipe preserved both sample lines.")


def standalone():
    with TemporaryDirectory(prefix="test-standalone-", dir=RUN) as path:
        directory = Path(path)
        fixture_state(directory)
        workflow.validate(read(directory / "state.json")["script"])
        # Execute the actual fixture commands and ledger. Replace only tmux display calls
        # and the unavailable Unix-socket dispatch to the experiment pane.
        with patch.object(workflow.layout, "caption"), patch.object(workflow.layout, "tmux"), patch.object(
            workflow, "job_request", side_effect=experiment.execute
        ):
            assert workflow.worker(directory, 0, True, 4) == 0, read(directory / "state.json")["last_error"]
        validate_fixture(directory)
        state = read(directory / "state.json")
        artifacts.wording(directory, state, "threshold met", "synthetic threshold met", "fixture scope")
        bundle = artifacts.bundle(directory, state)
        print(f'Standalone bundle verified: {artifacts.verify(bundle)} files')
        validate_tamper(bundle)
        subprocess.run(["bin/verify-bundle", str(bundle)], cwd=ROOT, check=True)
        if len(sys.argv) > 2 and sys.argv[2] == "--capture":
            capture_fallback(directory)
        print("Standalone PTY observers, without a tmux server:")
        standalone_panes(directory)
        recorder_probe(directory)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "atomic":
        atomic(Path(sys.argv[2]))
    elif action == "recording":
        bundle = Path(sys.argv[2]).resolve()
        cast, = bundle.glob("*.cast")
        with cast.open() as stream:
            header = json.loads(next(stream))
            assert header["version"] == 2 and header["idle_time_limit"] == 2
            frames = [json.loads(line) for line in stream]
        assert any(frame[1] == "o" and "fixture" in frame[2] for frame in frames)
        for name in PANES:
            pane = bundle / f"panes/{name}.log"
            assert pane.stat().st_size > 0 and pane.read_bytes().startswith(b"[20")
        print(f'Asciicast has {len(frames)} frames and five timestamped pane logs')
    elif action == "quiet":
        status = json.loads(sys.argv[2])
        cpu({name: pane["pid"] for name, pane in status["panes"].items()})
    elif action == "fixture":
        validate_fixture(Path(sys.argv[2]))
    else:
        standalone()
