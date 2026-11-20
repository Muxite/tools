"""Offline stages and the persistent verdict used by all three entry points."""

import argparse
from collections import Counter
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
STOCK = ROOT.parent / "llama.cpp-stock"
RECEIPT = ROOT.parent / "receipts/stock-build.json"
RECEIPT_SHA256 = "765fffdaafb8627c24edab1ff6ed44fbbea3a34866420404f0e732a13688d7d0"
COMMIT = "9048bad8d6e3a0f9f1726e238e451181c7e02613"
SCORER_VERSION = 2
REFERENCE = ROOT / "reference.json"
CONFIGS = {"C1": ["-ngl", "0", "-lm", "mmap"],
           "C2": ["-ngl", "99", "-cmoe", "-lm", "mmap"]}
GATES = {
    1: ("LLAMA_EVENT_REC", "<absolute path to fresh JSONL file>", "runtime_event_recorder"),
    2: ("LLAMA_EXPERT_CACHE", "1", "expert_weight_cache"),
    3: ("LLAMA_PLACEMENT_PLAN", "1", "weight_placement_planner"),
    4: ("LLAMA_EXPERT_PREDICT", "1", "expert_demand_predictor"),
    5: ("LLAMA_BATCH_LAYOUT", "1", "batch_layout_mapper"),
}
STAGES = [f"S{i}" for i in range(1, 8)]
CMAKE = {
    1: {"CMakeLists.txt", "src/CMakeLists.txt", "tools/server/CMakeLists.txt"},
    2: {"CMakeLists.txt", "src/CMakeLists.txt", "ggml/src/CMakeLists.txt"},
    3: {"CMakeLists.txt", "src/CMakeLists.txt", "common/CMakeLists.txt"},
    4: {"CMakeLists.txt", "src/CMakeLists.txt", "tools/server/CMakeLists.txt"},
    5: {"CMakeLists.txt", "src/CMakeLists.txt", "tools/server/CMakeLists.txt"},
}
EXTRA = {
    1: {"tools/server/server-context.cpp", "tools/server/server-context.h"},
    2: {"ggml/src/ggml-backend.cpp", "ggml/include/ggml-backend.h"},
    3: {"common/arg.cpp", "common/common.h", "common/common.cpp"},
    4: {"tools/server/server-context.cpp"},
    5: {"tools/server/server-context.cpp"},
}


class CheckError(Exception):
    """A concise failure or unmet prerequisite suitable for the verdict."""


def require(condition, reason):
    if not condition:
        raise CheckError(reason)


def one_line(reason):
    return " ".join(str(reason).split()) or type(reason).__name__


def sha256(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        try:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.close()
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def stock_receipt():
    require(sha256(RECEIPT) == RECEIPT_SHA256, "Stock build receipt differs from the pinned receipt")
    return read_json(RECEIPT)


@contextmanager
def lock(path, *, blocking=False):
    with path.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        except BlockingIOError as exc:
            raise CheckError(f"Another scorer holds {path}") from exc
        yield


def verdict(out, state, stage, status, reason, start=None, **details):
    seconds = round(time.monotonic() - start, 3) if start is not None else None
    state["scorer_version"] = SCORER_VERSION
    state["stages"][stage] = dict(status=status, reason=one_line(reason),
                                  wall_seconds=seconds, **details)
    state["total_passed"] = sum(item["status"] == "pass" for item in state["stages"].values())
    state["done_claimable"] = all(
        state["stages"].get(key, {}).get("status") == "pass" for key in STAGES[:5]
    )
    state["build_ccache_hit_rate"] = state["stages"].get("S3", {}).get("ccache_hit_rate")
    state["active_reached"] = state["stages"].get("S5", {}).get("active_reached")
    write_json(out / "score.json", state)
    log_line(out, f"{stage} {status} | {one_line(reason)}"
                  + (f" ({seconds}s)" if seconds is not None else ""))


def log_line(out, message):
    with (out / "score.log").open("a", encoding="utf-8") as stream:
        print(message, file=stream)
    print(message, flush=True)


def applicable(wo, stage):
    return (stage != "S6" or wo in (1, 3)) and (stage != "S7" or wo == 5)


def defer(out, state, reason, status):
    for stage in STAGES[3:]:
        if applicable(state["wo"], stage):
            verdict(out, state, stage, status, reason)
        else:
            verdict(out, state, stage, "skipped", "Stage does not apply to this work order")


def output_dir(argument):
    path = Path(argument).resolve()
    require(path == ROOT or ROOT in path.parents, f"Use an output directory inside {ROOT}")
    require(not set(path.relative_to(ROOT).parts[:1]) & {".git", ".agents", ".codex", ".aws"},
            "Output directory overlaps protected workspace data")
    return path


def git(source, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(["git", "-C", source, "-c", "core.fsmonitor=false", *args],
                            env=env, capture_output=True)
    if result.returncode:
        raise CheckError(result.stderr.decode(errors="replace").strip()
                         or f"git {args[0]} returned {result.returncode}")
    return result.stdout


def apply_patch(work, candidate):
    source = work / "src"
    subprocess.run(["cp", "-a", "--reflink=auto", "--", STOCK, source], check=True)
    require(git(source, "rev-parse", "HEAD").decode().strip() == COMMIT,
            "Stock copy is not at the pinned commit")
    require(not git(source, "status", "--porcelain=v1", "--untracked-files=all", "--ignored"),
            "Stock copy has staged, modified, untracked or ignored paths")
    git(source, "update-index", "--refresh")
    patch = work / "candidate.diff"
    patch.write_bytes(candidate)
    git(source, "apply", "--check", "--index", "--", patch)
    git(source, "apply", "--index", "--", patch)
    return source


def scope(wo, source, patch):
    raw = git(source, "diff", "--cached", "--no-renames", "--name-status", "-z", "HEAD", "--")
    fields = raw.decode("utf-8", errors="surrogateescape").split("\0")[:-1]
    changes = {path: status for status, path in zip(fields[::2], fields[1::2])}
    # Also account for patch entries whose net change cancels out.
    stats = git(source, "apply", "--numstat", "-z", "--", patch)
    for entry in stats.decode("utf-8", errors="surrogateescape").split("\0")[:-1]:
        parts = entry.split("\t", 2)
        path = parts[2] if len(parts) == 3 else entry
        if path:
            changes.setdefault(path, "?")

    def allowed(path, status):
        if path in EXTRA[wo] or path in CMAKE[wo]:
            return True
        if wo == 5:
            return path == "src/llama-batch-layout.h" and status == "A"
        if not path.startswith("src/"):
            return False
        return not path.startswith(("src/llama-sampler", "src/llama-model", "src/models/",
                                    "src/llama-graph.", "src/llama-arch."))

    paths = sorted(changes)
    forbidden = [path for path in paths if not allowed(path, changes[path])]
    return paths, forbidden


def build_commands(work, source):
    flags = stock_receipt()
    require(flags["status"] == "passed" and flags["source_verified"]
            and flags["source_commit"] == COMMIT, "Stock build receipt does not match the pin")
    build_dir = work / "build"
    replacement = {"-S": source, "-B": build_dir}
    args = iter(flags["configure_flags"])
    configure = [flags["tools_and_compilers"]["cmake"]["path"]]
    for arg in args:
        configure.append(arg)
        if arg in replacement:
            next(args)
            configure.append(str(replacement[arg]))
    # The stock build ended with zero embedded UI assets after failed downloads.
    configure.append("-DLLAMA_USE_PREBUILT_UI=OFF")
    return [configure, [configure[0], "--build", str(build_dir),
                        "--target", "llama-server", "--parallel", "3"]]


def build(work, source):
    build_dir = work / "build"
    commands = build_commands(work, source)
    cache = ROOT / "ccache"
    cache.mkdir(exist_ok=True)
    tmp = work / "tmp"
    tmp.mkdir()
    stats_path = work / "ccache.stats.log"
    env = {key: value for key, value in os.environ.items() if not key.startswith("CCACHE_")}
    env.update(CCACHE_DIR=str(cache), CCACHE_TEMPDIR=str(tmp), CCACHE_BASEDIR=str(work),
               CCACHE_NOHASHDIR="1", CCACHE_STATSLOG=str(stats_path),
               CCACHE_CONFIGPATH="/dev/null", CMAKE_BUILD_PARALLEL_LEVEL="3",
               TMPDIR=str(tmp), LC_ALL="C", PYTHONDONTWRITEBYTECODE="1")
    env.pop("MAKEFLAGS", None)
    env.pop("MFLAGS", None)
    log = work / "build.log"
    error = None
    with lock(ROOT / ".scorer-build.lock", blocking=True), log.open("w") as stream:
        deadline = time.monotonic() + 5400
        for label, command in zip(("configure", "build"), commands):
            print(f"[scorer {label}] {shlex.join(command)}", file=stream, flush=True)
            try:
                result = subprocess.run(["timeout", "--verbose", "--kill-after=30s",
                                         f"{max(0.001, deadline - time.monotonic()):.3f}s",
                                         *command], cwd=work, env=env, stdout=stream,
                                        stderr=subprocess.STDOUT)
                if result.returncode == 124 or (
                        result.returncode == 137 and "timeout: sending signal" in log.read_text(errors="replace")):
                    error = f"{label} exceeded the shared 90-minute configure/build limit"
                elif result.returncode:
                    error = f"{label} exited {result.returncode}. See {log}"
            except OSError as exc:
                error = f"{label}: {exc}"
            if error:
                break

    counts = Counter(stats_path.read_text(encoding="utf-8").splitlines()) if stats_path.exists() else Counter()
    hits = counts["direct_cache_hit"] + counts["preprocessed_cache_hit"]
    misses = counts["cache_miss"]
    details = dict(build_log=str(log), build_dir=str(build_dir), ccache_hits=hits,
                   ccache_misses=misses, ccache_hit_rate=hits / (hits + misses) if hits + misses else None,
                   warning_count=0)
    with log.open(errors="replace") as stream:
        for line in stream:
            if line.startswith("[scorer build] "):
                break
        details["warning_count"] = sum(bool(re.search(r"\bwarning(?:\s+#\d+-D)?:", line, re.I))
                                       for line in stream)
    if not error and not os.access(build_dir / "bin/llama-server", os.X_OK):
        error = "Build completed without an executable llama-server"
    return error, details


def score(wo, patch, out, scope_only):
    out.mkdir(parents=True, exist_ok=True)
    with lock(out / ".score.lock"):
        require(not (out / "score.log").is_symlink(), "score.log must not be a symbolic link")
        work = Path(tempfile.mkdtemp(prefix="work-", dir=out))
        state = dict(schema_version=1, wo=wo, stock_commit=COMMIT, work_dir=str(work),
                     stages={}, patch_sha256=None)
        (out / "score.log").write_text("", encoding="utf-8")
        start = time.monotonic()
        try:
            data = patch.read_bytes()
            state["patch_sha256"] = hashlib.sha256(data).hexdigest()
            source = apply_patch(work, data)
        except (OSError, subprocess.SubprocessError, CheckError) as exc:
            verdict(out, state, "S1", "fail", exc, start)
            for stage in ("S2", "S3"):
                verdict(out, state, stage, "skipped", "S1 did not produce a patched tree")
            defer(out, state, "S1 did not produce a patched tree", "skipped")
            return
        verdict(out, state, "S1", "pass", "Checked and applied against pinned pristine source", start)

        start = time.monotonic()
        try:
            paths, forbidden = scope(wo, source, work / "candidate.diff")
            reason = ("Forbidden paths: " + ", ".join(map(repr, forbidden)) if forbidden
                      else f"All {len(paths)} touched paths are allowed")
            verdict(out, state, "S2", "fail" if forbidden else "pass", reason, start,
                    touched_paths=paths, forbidden_paths=forbidden)
        except (OSError, CheckError) as exc:
            verdict(out, state, "S2", "fail", exc, start)

        if scope_only:
            verdict(out, state, "S3", "skipped", "Offline scope self-test requested")
            defer(out, state, "Offline scope self-test did not build a server", "skipped")
            return
        start = time.monotonic()
        try:
            error, details = build(work, source)
        except (OSError, ValueError, KeyError, CheckError) as exc:
            error, details = one_line(exc), {}
        verdict(out, state, "S3", "fail" if error else "pass",
                error or "Built llama-server using the stock CUDA build recipe", start, **details)
        if error:
            defer(out, state, "S3 did not produce a runnable build", "skipped")
            return

    # Let the runtime entry point acquire the same output lock used on resume.
    subprocess.run([ROOT / "run_checks.sh", out, "--expected-work-dir", str(work)], check=True)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="action", required=True)
    offline = commands.add_parser("score", prog="score.sh")
    offline.add_argument("wo", type=int, choices=range(1, 6))
    offline.add_argument("candidate_diff", type=Path)
    offline.add_argument("outdir")
    offline.add_argument("--scope-only", action="store_true", help="S1/S2 self-test without a build")
    runtime = commands.add_parser("run", prog="run_checks.sh")
    runtime.add_argument("outdir")
    runtime.add_argument("--expected-work-dir", help=argparse.SUPPRESS)
    commands.add_parser("reference", prog="make_reference.sh")
    args = parser.parse_args()
    try:
        if args.action == "score":
            score(args.wo, args.candidate_diff.resolve(), output_dir(args.outdir), args.scope_only)
        else:
            import scorer_runtime
            if args.action == "run":
                scorer_runtime.run(output_dir(args.outdir), args.expected_work_dir)
            else:
                scorer_runtime.make_reference()
    except (OSError, ValueError, CheckError, subprocess.SubprocessError) as exc:
        print(one_line(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    # Keep exception types and constants shared with the lazily loaded runtime.
    sys.modules["scorer"] = sys.modules[__name__]
    sys.exit(main())
