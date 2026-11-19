import json
import shutil
import subprocess
import sys
from pathlib import Path

from common import Error, LABELS, ROOT, append, digest, emit, events, locked, now, relative, write


def wording(directory, state, old, new, reason):
    step = next((s for s in state["script"] if s["id"] == state["current_step"]), None)
    stage = step["action"]["stage"] if step else None
    if not step and all(s["action"]["stage"] == "fixture" for s in state["script"]):
        stage = "fixture"
    with locked(directory / "wording.lock"):
        record = {"wall": now(), "step": state["current_step"], "old": old, "new": new, "reason": reason}
        append(directory / "wording-log.jsonl", record)
        emit(directory, "note", stage=stage, data={**record, "text": new})
    return record


def scoped(root, name):
    path = Path(name)
    target = root / path
    if (path.is_absolute() or ".." in path.parts or not target.resolve().is_relative_to(root)
            or "\n" in name or "\r" in name or "\\" in name):
        raise Error(f"Invalid artifact path {name!r}")
    return target


def provenance():
    git = {}
    for name, args in {
        "toplevel": ["rev-parse", "--show-toplevel"], "head": ["rev-parse", "HEAD"],
        "branch": ["rev-parse", "--abbrev-ref", "HEAD"], "working_tree": ["status", "--porcelain", "--", "."],
    }.items():
        result = subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        git[name] = result.stdout.strip() if result.returncode == 0 else None
    files = [*ROOT.glob("*.py"), *ROOT.glob("bin/*"), *ROOT.glob("panes/*.py"),
             *ROOT.glob("demo/*.py"), *ROOT.glob("demo/*.sh"), *ROOT.glob("demo/*.json"),
             *ROOT.glob("demo/fixtures/**/*")]
    git["source_sha256"] = {relative(file): digest(file) for file in sorted(files) if file.is_file()}
    return git


def readme(log):
    lines = ["Cockpit evidence bundle", "", "What ran"]
    for event in log:
        stage = LABELS[event["stage"]]
        detail = (event["data"].get("title") or event["data"].get("arm")
                  or event["data"].get("verdict") or event["ref"] or "")
        if event["kind"] in ("task", "run", "result", "decision", "build"):
            lines.append(f'{event["step"] or "—"} {event["kind"]} {event["status"]} [{stage}] {detail}')
    lines += ["", "Verdicts"]
    for event in log:
        if event["kind"] == "result" and event["ref"]:
            receipt = scoped(ROOT, event["ref"])
            try:
                verdict = json.loads(receipt.read_text()).get("verdict", event["status"])
            except (OSError, ValueError, AttributeError):
                verdict = event["status"]
            lines.append(f'[{LABELS[event["stage"]]}] {verdict} — {event["ref"]}')
    lines += ["", "Wording history: ./wording-log.jsonl", "Commands: ./invocations.jsonl",
              "Source revisions: ./git-revisions.json", "Integrity: bin/verify-bundle <this directory>"]
    return "\n".join(lines) + "\n"


def bundle(directory, state):
    final = directory / "BUNDLE"
    temporary = directory / "bundle-tmp"
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir()

    def copy(source, name):
        target = scoped(temporary, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    try:
        with locked(directory / "wording.lock"), locked(directory / "events.lock"):
            for name in ("events.jsonl", "state.json", "wording-log.jsonl", "invocations.jsonl"):
                copy(directory / name, name)
            log = events(directory)
        for path in (directory / "panes").glob("*.log"):
            copy(path, "panes/" + path.name)
        for cast in state["casts"]:
            source = scoped(ROOT, cast)
            copy(source, source.name)
        refs = {event["ref"] for event in log if event["ref"]}
        for ref in sorted(refs):
            source = scoped(ROOT, ref)
            if not source.is_file():
                raise Error(f"Event reference is missing: {ref}")
            copy(source, ref)
        initial = directory / "source-at-start.json"
        revisions = {"at_start": json.loads(initial.read_text()) if initial.is_file() else None,
                     "at_bundle": provenance()}
        write(temporary / "git-revisions.json", revisions)
        (temporary / "README.txt").write_text(readme(log))
        inventory = sorted(path for path in temporary.rglob("*") if path.is_file())
        (temporary / "MANIFEST.sha256").write_text(
            "".join(f"{digest(path)}  {path.relative_to(temporary)}\n" for path in inventory)
        )
        verify(temporary)
        if final.exists():
            shutil.rmtree(final)
        temporary.rename(final)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return final


def verify(directory):
    listed = {}
    for line in (directory / "MANIFEST.sha256").read_text().splitlines():
        checksum, name = line.split("  ", 1)
        path = scoped(directory, name)
        if name in listed or not path.is_file() or path.is_symlink() or digest(path) != checksum:
            raise Error(f"Manifest verification failed for {name}")
        listed[name] = checksum
    on_disk = {str(path.relative_to(directory)) for path in directory.rglob("*")
               if path.is_file() or path.is_symlink()}
    if set(listed) | {"MANIFEST.sha256"} != on_disk:
        raise Error("Manifest does not match the bundle file inventory")
    for required in ("events.jsonl", "state.json", "wording-log.jsonl", "invocations.jsonl", "README.txt",
                     "git-revisions.json"):
        if required not in listed:
            raise Error(f"Bundle is missing {required}")
    for event in events(directory):
        ref = event["ref"]
        if event["kind"] == "result" and (not ref or not event["sha256"]):
            raise Error(f'Result event {event["seq"]} has no receipt')
        if ref:
            scoped(directory, ref)
            name = Path(ref).as_posix()
            if name not in listed or (event["sha256"] and event["sha256"] != listed[name]):
                raise Error(f'Event {event["seq"]} reference failed verification: {ref}')
    return len(listed)


if __name__ == "__main__":
    try:
        count = verify(Path(sys.argv[1]).resolve())
        print(json.dumps({"ok": True, "files": count}))
    except (Error, OSError, ValueError, IndexError, KeyError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        sys.exit(1)
