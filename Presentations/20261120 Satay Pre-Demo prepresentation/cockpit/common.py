import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "run"
SOCKET = RUN / "tmux.sock"
SESSION = "cockpit"
PANES = ("plan", "data", "experiment", "cc", "result")
LABELS = {
    "fixture": "fixture",
    "native": "native CC execution",
    "compile": "compile",
    "runtime": "runtime acceptance",
    "hardware": "hardware measurement",
    None: "—",
}
COMMAND = ROOT / "bin/cockpit"


class Error(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


@contextlib.contextmanager
def locked(path, exclusive=True):
    with path.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        yield


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


def events(directory):
    lines = (directory / "events.jsonl").read_text().splitlines(keepends=True)
    return [json.loads(line) for line in lines if line.endswith("\n")]


def append(path, record):
    with path.open("a") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def active():
    try:
        run_id = (RUN / "active").read_text().strip()
    except FileNotFoundError:
        raise Error("No run. Start one with cockpit up.") from None
    return RUN / run_id


def tmux(*args, check=True):
    return subprocess.run(
        ["tmux", "-S", str(SOCKET), *map(str, args)], cwd=ROOT,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check,
    )


def emit(directory, kind, status="ok", *, step=None, cc=None, stage=None, ref=None, data=None):
    args = ["bin/ev", kind, status]
    for key, value in (("step", step), ("cc", cc), ("stage", stage), ("ref", ref)):
        if value is not None:
            args.extend(["--" + key, str(value)])
    if data is not None:
        args.extend(["--data", json.dumps(data)])
    return json.loads(subprocess.check_output(
        args, cwd=ROOT, text=True, env={**os.environ, "COCKPIT_RUN": directory.name},
    ))


def quiet(directory, mode, step=None, stage=None):
    env = {**os.environ, "COCKPIT_RUN": directory.name}
    if step:
        env["COCKPIT_STEP"] = step
    if stage:
        env["COCKPIT_STAGE"] = stage
    return json.loads(subprocess.check_output(
        ["bin/ev", "quiet", mode], cwd=ROOT, text=True, env=env,
    ))


def digest(path):
    with path.open("rb") as stream:
        result = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))
