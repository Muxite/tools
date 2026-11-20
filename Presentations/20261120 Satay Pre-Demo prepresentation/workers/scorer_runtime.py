"""Stock and candidate server runs. Importing this module does not start a server."""

from contextlib import contextmanager
import glob
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shlex
import signal
import socket
import subprocess
import tempfile
import time

from scorer import (ROOT, COMMIT, CONFIGS, GATES, REFERENCE, CheckError,
                    applicable, defer, lock, log_line, one_line, read_json, require,
                    sha256, stock_receipt, verdict, write_json)

MODEL = ROOT.parents[1] / "models/campaign/gguf/granite-3.1-1b-a400m-instruct-Q8_0.gguf"
STOCK_BIN = ROOT.parent / "build-stock-cuda87/bin/llama-server"
PROMPT = ("Write a short note about mixture of experts models and why memory bandwidth matters. "
          "Then list three facts.")
BASE_ARGS = ["-c", "2048", "-np", "1", "--temp", "0", "--seed", "1", "-lv", "4"]
PLACEMENT_ARGS = ["-ngl", "99", "-lm", "mmap"]
PLACEMENT_PATTERN = r"^blk\.[0-9]+\.ffn_down_exps\.weight$"
LAYERS = 24
SWEEP = (1, 31, 32, 33, 127, 128, 129, 511, 512, 513, 1023)
CACHED_SWEEP = (33, 129, 513)
STATS = {
    1: ("events", "lost", "bytes"),
    2: ("leases", "reuses", "evictions", "bytes_copied_saved", "peak_bytes"),
    3: ("assigned", "stock"),
    4: ("hits", "misses", "bytes_useful_at_consumption", "wasted_bytes", "lead_ns_total", "lead_samples"),
    5: ("decisions", "rows", "bypasses"),
}
ACTIVE_FIELDS = {2: {"cap_mib": r"[0-9]+", "backend": r"\S+"},
                 3: {"cap_bytes": r"[0-9]+", "peak_bytes": r"[0-9]+"},
                 5: {"n_batch": r"[0-9]+", "n_ubatch": r"[0-9]+", "limit": r"[0-9]+"}}
REFERENCE_PORTS = {"C1": 20990, "C2": 20991}
RUN_ERRORS = (CheckError, OSError, ValueError, http.client.HTTPException)


def port_pair(patch_digest):
    base = 21000 + 2 * (int(patch_digest[:16], 16) % 10000)
    return {"C1": base, "C2": base + 1}


def preflight(ports):
    devices = ["/dev/nvhost-gpu", "/dev/nvhost-ctrl-gpu", *glob.glob("/dev/nvgpu/igpu*/ctrl"),
               *glob.glob("/dev/nvidia[0-9]*")]
    require(any(os.access(path, os.R_OK | os.W_OK) for path in devices),
            "No accessible NVIDIA GPU device")
    for port in ports.values():
        try:
            with socket.socket() as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind(("127.0.0.1", port))
        except OSError as exc:
            try:
                result = subprocess.run(["pgrep", "-x", "llama-server"], capture_output=True, text=True)
                pids = ", ".join(result.stdout.split()) or "none"
            except OSError:
                pids = "unavailable"
            raise CheckError(f"Cannot bind 127.0.0.1:{port} ({exc}). llama-server PIDs: {pids}") from exc


def request(port, endpoint, payload=None, timeout=300):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        if payload is None:
            conn.request("GET", endpoint)
        else:
            conn.request("POST", endpoint, json.dumps(payload), {"Content-Type": "application/json"})
        response = conn.getresponse()
        body = response.read()
        require(response.status == 200, f"{endpoint} HTTP {response.status}: {body[:250]!r}")
        return json.loads(body)
    finally:
        conn.close()


@contextmanager
def operator_signals():
    def interrupt(signum, _frame):
        raise KeyboardInterrupt(f"Interrupted by signal {signum}")

    handlers = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        yield
    finally:
        for sig, previous in handlers.items():
            signal.signal(sig, previous)


@contextmanager
def server(binary, directory, port, args, gate=None, cache=False):
    directory.mkdir()
    env = {key: val for key, val in os.environ.items()
           if not key.startswith(("LLAMA_", "GGML_")) and key not in (
               "LD_PRELOAD", "CUDA_VISIBLE_DEVICES", "CUDA_DEVICE_ORDER", "CUDA_CACHE_PATH",
               "CUDA_CACHE_DISABLE")}
    env.update(LD_LIBRARY_PATH=str(binary.parent), LC_ALL="C", TMPDIR=str(directory),
               XDG_CACHE_HOME=str(directory / "cache"), CUDA_CACHE_PATH=str(directory / "cache/cuda"))
    if gate:
        env[gate[0]] = gate[1]
    cache_arg = "--cache-prompt" if cache else "--no-cache-prompt"
    command = [str(binary), "-m", str(MODEL), "--host", "127.0.0.1", "--port", str(port),
               *BASE_ARGS, cache_arg, *args]
    write_json(directory / "invocation.json", {"argv": command, "gate": dict([gate]) if gate else {}})
    log = directory / "server.log"
    with log.open("wb") as stream:
        process = subprocess.Popen(command, cwd=directory, env=env, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 120
            while True:
                require(process.poll() is None, f"Server exited during startup ({process.returncode}). See {log}")
                try:
                    if request(port, "/health", timeout=1) == {"status": "ok"}:
                        break
                except RUN_ERRORS:
                    pass
                require(time.monotonic() < deadline, f"Server was not healthy within 120 seconds. See {log}")
                time.sleep(0.5)
            yield port
            require(process.poll() is None, f"Server exited before shutdown ({process.returncode}). See {log}")
            pre_shutdown_bytes = log.stat().st_size
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        require(process.returncode == 0, f"Server did not shut down cleanly ({process.returncode}). See {log}")
        write_json(directory / "shutdown.json", {"returncode": 0, "pre_shutdown_bytes": pre_shutdown_bytes})


def completion(port, path, prompt=PROMPT, n_predict=48, cache=False):
    result = request(port, "/completion", dict(prompt=prompt, n_predict=n_predict, temperature=0,
                                               seed=1, cache_prompt=cache, return_tokens=True,
                                               stream=False))
    write_json(path, result)
    tokens = result.get("tokens") if isinstance(result, dict) else None
    require(isinstance(tokens, list) and 1 <= len(tokens) <= n_predict
            and all(type(token) is int and token >= 0 for token in tokens)
            and result.get("stop") is True and "error" not in result, f"Invalid completion: {path}")
    # Same bytes as jq -c '.tokens' in one_shot.sh, including its trailing newline.
    data = json.dumps(tokens, separators=(",", ":")) + "\n"
    return hashlib.sha256(data.encode("ascii")).hexdigest(), result


def one_shot(binary, directory, port, args, gate=None):
    with server(binary, directory, port, args, gate) as handle:
        return completion(handle, directory / "completion.json")


def log_text(directory):
    return (directory / "server.log").read_text(encoding="utf-8", errors="replace")


def shutdown_marker_lines(directory, wo):
    checkpoint = read_json(directory / "shutdown.json")
    with (directory / "server.log").open("rb") as stream:
        offset = checkpoint["pre_shutdown_bytes"]
        if offset:
            stream.seek(offset - 1)
            if stream.read(1) != b"\n":
                stream.readline()
        tail = stream.read().decode("utf-8", errors="replace")
    return marker_lines(tail, GATES[wo][2])


def marker_lines(text, name):
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
        line = re.sub(r"^(?:\d+(?:\.\d+)+\s+)?(?:[DIWE]\s+)?", "", line)
        if line.startswith(name + ":"):
            lines.append(line[len(name) + 1:].strip())
    return lines


def stats_counters(lines, wo):
    for line in reversed(lines):
        if not line.startswith("stats "):
            continue
        fields = re.findall(r"(?:^|\s)([^=\s]+)=([^\s]+)", line[6:])
        required = [(key, value) for key, value in fields if key in STATS[wo]]
        if (sorted(key for key, _ in required) == sorted(STATS[wo])
                and all(value.isascii() and value.isdigit() for _, value in required)):
            return line, {key: int(value) for key, value in required}
    return None, {}


def markers(text, wo, *, shutdown_lines=None, allow_extra=False):
    lines = marker_lines(text, GATES[wo][2])
    active = [line for line in lines if re.fullmatch(r"active(?:\s+.+)?", line)]
    inactive = [line for line in lines if re.fullmatch(r"inactive \(.+\)", line)]
    stats, counters = stats_counters(lines if shutdown_lines is None else shutdown_lines, wo)
    error = None
    if len(active) + len(inactive) != 1 or (not allow_extra and len(lines) != 2):
        error = f"Expected one active or inactive line. Found {len(active) + len(inactive)} in {len(lines)} markers"
    elif stats is None:
        location = " in the clean shutdown log suffix" if shutdown_lines is not None else ""
        error = f"Expected a stats line with decimal counters ({', '.join(STATS[wo])}){location}"
    elif active:
        if wo in (1, 4) and active[0] == "active":
            error = "Active line is missing effective settings"
        for key, value in ACTIVE_FIELDS.get(wo, {}).items():
            if not re.search(rf"(?:^|\s){key}={value}(?:\s|$)", active[0]):
                error = error or f"Active line is missing valid {key}"
    extras = [line for line in lines if line not in active and line not in inactive]
    if stats in extras:
        extras.reverse()
        extras.remove(stats)
        extras.reverse()
    return bool(active), counters, lines, extras, error


def gate_for(wo, directory):
    name, value, _ = GATES[wo]
    return name, str(directory / "events.jsonl") if wo == 1 else value


def main_stage(wo, binary, root, ports, reference, enabled):
    root.mkdir()
    cases = {}
    failed = []
    for name, args in CONFIGS.items():
        directory = root / name
        case = cases[name] = {"directory": str(directory)}
        errors = []
        try:
            digest, _ = one_shot(binary, directory, ports[name], args,
                                 gate_for(wo, directory) if enabled else None)
            expected = reference["configs"][name]["tokens_sha256"]
            case.update(tokens_sha256=digest, stock_tokens_sha256=expected, clean_exit=True)
            if digest != expected:
                errors.append("stock token hash mismatch")
        except RUN_ERRORS as exc:
            errors.append(one_line(exc))
        if (directory / "server.log").exists():
            text = log_text(directory)
            if enabled:
                shutdown_lines = shutdown_marker_lines(directory, wo) if case.get("clean_exit") else None
                active, counters, lines, extras, error = markers(
                    text, wo, shutdown_lines=shutdown_lines, allow_extra=True)
                marker = GATES[wo][2]
                case.update(active_reached=active, counters=counters, markers=lines,
                            extra_marker_lines={"count": len(extras),
                                                "first_5": [f"{marker}: {line}".rstrip() for line in extras[:5]]})
                if error:
                    errors.append(error)
            else:
                lines = marker_lines(text, GATES[wo][2])
                case["markers"] = lines
                if lines:
                    errors.append("marker prefix present with gate unset")
        elif enabled:
            case["active_reached"] = False
        if errors:
            case["error"] = " | ".join(errors)
            failed.append(f"{name}: {case['error']}")
    details = {"configs": cases}
    if enabled:
        details["active_reached"] = any(case["active_reached"] for case in cases.values())
    return failed, details


def positive_int(value):
    return type(value) is int and value > 0


def reject_constant(value):
    raise ValueError(f"Invalid JSON constant {value}")


def replay_records(path):
    counts = {"prefill": 0, "decode": 0}
    layers, microbatches = set(), set()
    summary = None
    with path.open(encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line, parse_constant=reject_constant)
                require(isinstance(record, dict), "expected a JSON object")
                kind = record.get("type", "event")
                if kind in ("summary", "stats"):
                    require(summary is None, "expected at most one summary or stats record")
                    summary = record
                    continue
                phase = record.get("phase")
                require(kind == "event" and phase in ("prefill", "decode"),
                        "expected an event with phase prefill or decode")
            except (ValueError, CheckError) as exc:
                raise CheckError(f"JSONL line {index}: {exc}") from exc
            counts[phase] += 1
            layer = record.get("layer", record.get("layer_id"))
            ubatch = record.get("microbatch", record.get("microbatch_id",
                                record.get("ubatch", record.get("ubatch_id"))))
            if type(layer) in (int, str):
                layers.add(layer)
            if type(ubatch) in (int, str):
                microbatches.add((phase, ubatch))
    return counts, layers, microbatches, summary


def replay_microbatches(directory, text):
    completion_data = read_json(directory / "completion.json")
    require(isinstance(completion_data, dict), "Replay completion must be a JSON object")
    ubatch = re.search(r"llama_context:\s+n_ubatch\s*=\s*([0-9]+)", text)
    batch = re.search(r"llama_context:\s+n_batch\s*=\s*([0-9]+)", text)
    timings = completion_data.get("timings", {})
    require(isinstance(timings, dict), "Replay completion is missing timings")
    prompt_n, predicted_n = timings.get("prompt_n"), timings.get("predicted_n")
    require(batch and ubatch and positive_int(prompt_n) and positive_int(predicted_n)
            and timings.get("cache_n") == 0, "Missing uncached request and batch counters")
    require(prompt_n <= int(batch[1]) and 0 < int(ubatch[1]) <= int(batch[1]),
            "Replay request must fit one server batch with a positive microbatch limit")
    return {"prefill": (prompt_n + int(ubatch[1]) - 1) // int(ubatch[1]), "decode": predicted_n - 1}


def replay(root):
    cases = {}
    failed = []
    for name in CONFIGS:
        directory = root / name
        case = cases[name] = {"directory": str(directory)}
        try:
            require((directory / "shutdown.json").is_file(), "Replay requires a clean S5 server exit")
            counts, layers, observed_microbatches, summary = replay_records(directory / "events.jsonl")
            text = log_text(directory)
            lines = marker_lines(text, GATES[1][2])
            _, counters = stats_counters(lines, 1)
            records = sum(counts.values())
            case.update(layers=LAYERS, phase_records=counts, records=records, events=records,
                        layers_seen=len(layers), microbatches_seen=len(observed_microbatches),
                        prefill_events=counts["prefill"], decode_events=counts["decode"],
                        summary_present=summary is not None, reported_events=counters.get("events"),
                        lost=0, incomplete=None, overflow=None)
            if summary is not None:
                expected, lost = summary.get("expected"), summary.get("lost")
                require(type(expected) is int and type(lost) is int and 0 <= lost <= expected,
                        "JSONL summary requires integer counters with 0 <= lost <= expected")
                case.update(expected_records=expected, lost=lost)
                for key in ("incomplete", "overflow"):
                    if key in summary:
                        value = summary[key]
                        require(type(value) is int and value >= 0,
                                f"JSONL summary {key} must be a nonnegative integer")
                        case[key] = value
                require(records == expected - lost, "JSONL event count differs from summary expected minus lost")
            else:
                case["warnings"] = ["JSONL summary missing"]
                logged_loss = [int(value) for line in lines if line.startswith("stats ")
                               for value in re.findall(r"(?:^|\s)lost=([0-9]+)(?:\s|$)", line)]
                case["lost"] = max(logged_loss, default=0)
                require(case["lost"] == 0, "JSONL summary missing and stats log reports loss")
                microbatches = replay_microbatches(directory, text)
                expected = {phase: LAYERS * count for phase, count in microbatches.items()}
                case.update(microbatches=microbatches, expected_phase_records=expected,
                            expected_records=sum(expected.values()))
                require(records == sum(expected.values()),
                        "JSONL event count does not equal layers × microbatches with zero loss")
        except RUN_ERRORS as exc:
            case["error"] = one_line(exc)
            failed.append(f"{name}: {case['error']}")
    return failed, {"configs": cases}


def model_buffers(directory):
    return sorted([buffer, size] for buffer, size in re.findall(
        r"load_tensors:\s+(\S+) model buffer size\s*=\s*([0-9.]+) MiB", log_text(directory)))


def placement(binary, root, port, reference):
    root.mkdir()
    plan = root / "plan.json"
    write_json(plan, {"version": 1, "overrides": [{"pattern": PLACEMENT_PATTERN, "buft": "CPU"}]})
    directory = root / "candidate-plan"
    details = {"pattern": PLACEMENT_PATTERN, "plan": str(plan)}
    try:
        digest, _ = one_shot(binary, directory, port,
                             [*PLACEMENT_ARGS, "--placement-plan", str(plan)], gate_for(3, directory))
        active, counters, lines, _, error = markers(log_text(directory), 3)
        baseline = reference["placement"]
        buffers = model_buffers(directory)
        details.update(tokens_sha256=digest, stock_ot_tokens_sha256=baseline["tokens_sha256"],
                       active_reached=active, markers=lines, counters=counters,
                       model_buffers=buffers, stock_ot_model_buffers=baseline["model_buffers"])
        errors = []
        if digest != baseline["tokens_sha256"]:
            errors.append("Stock -ot token hash mismatch")
        if error or not active or counters.get("assigned") != LAYERS:
            errors.append(error or f"Plan did not log active assignment of {LAYERS} tensors")
        if sum(line.startswith("stats ") for line in shutdown_marker_lines(directory, 3)) != 1:
            errors.append("Placement stats line was missing from the clean shutdown log suffix")
        if not buffers or buffers != baseline["model_buffers"]:
            errors.append("Logged model buffer allocation differs from stock -ot")
        return errors, details
    except RUN_ERRORS as exc:
        return [one_line(exc)], details


def plain_token(port):
    value = request(port, "/tokenize", {"content": " the", "add_special": False})
    tokens = value.get("tokens") if isinstance(value, dict) else None
    require(isinstance(tokens, list) and len(tokens) == 1 and positive_int(tokens[0]),
            "The Granite sweep seed must tokenize to one ordinary token")
    return tokens[0]


def sweep_response(port, directory, token, length, cached):
    if cached:
        prime = length - 16
        _, result = completion(port, directory / f"prime-{length}.json", [token] * prime, 1, True)
        require(result.get("tokens_evaluated") == prime, f"Expected {prime} priming prompt tokens")
    digest, result = completion(port, directory / f"length-{length}.json", [token] * length, 8, cached)
    require(result.get("tokens_evaluated") == length, f"Expected {length} target prompt tokens")
    timings = result.get("timings")
    require(isinstance(timings, dict), "Sweep completion is missing timings")
    reused = timings.get("cache_n")
    return digest, reused


def sweep(binary, root, ports, reference):
    root.mkdir()
    cases, errors = {}, []
    cache_supported = reference["cached_prefix"]["supported"]
    for name, args in CONFIGS.items():
        cases[name] = cases_for_config = {}
        for cached, lengths in ((False, SWEEP), (True, CACHED_SWEEP)):
            if cached and not cache_supported:
                continue
            mode = "cached" if cached else "cold"
            for enabled in (False, True):
                label = f"{mode}-{'on' if enabled else 'off'}"
                directory = root / f"{name}-{label}"
                values = cases_for_config[label] = {}
                try:
                    with server(binary, directory, ports[name], args,
                                gate_for(5, directory) if enabled else None, cached) as port:
                        token = plain_token(port)
                        require(token == reference["cached_prefix"]["sweep_token"],
                                "Sweep token differs from stock")
                        for length in lengths:
                            digest, reused = sweep_response(port, directory, token, length, cached)
                            values[str(length)] = dict(tokens_sha256=digest, cache_n=reused)
                except RUN_ERRORS as exc:
                    errors.append(f"{name} {label}: {one_line(exc)}")
            off, on = (cases_for_config[f"{mode}-{gate}"] for gate in ("off", "on"))
            if cached:
                for gate, values in (("off", off), ("on", on)):
                    for length, result in values.items():
                        cold = cases_for_config[f"cold-{gate}"].get(length)
                        result["cached_vs_cold_differs"] = (
                            result["tokens_sha256"] != cold["tokens_sha256"] if cold else None)
            for length in map(str, lengths):
                if length not in off or length not in on:
                    continue
                if off[length]["tokens_sha256"] != on[length]["tokens_sha256"]:
                    errors.append(f"{name} {mode} {length}: gate-on and gate-off hashes differ")
                if cached:
                    reused = off[length]["cache_n"]
                    if (not positive_int(reused) or reused != on[length]["cache_n"]
                            or not int(length) - 16 <= reused < int(length)):
                        errors.append(f"{name} cached {length}: expected equal reuse of the primed prefix")
                elif off[length]["cache_n"] != 0 or on[length]["cache_n"] != 0:
                    errors.append(f"{name} cold {length}: expected zero cached tokens")
    return errors, {"configs": cases, "cached_prefix_status": "checked" if cache_supported else "skipped"}


def reference_metadata():
    return {"schema_version": 1, "stock_commit": COMMIT, "model": str(MODEL),
            "server_flags": BASE_ARGS, "prompt": PROMPT, "n_predict": 48,
            "hash_encoding": "sha256 of compact JSON token ID array plus LF",
            "gates": {str(wo): {"env": name, "value": value, "marker": marker}
                      for wo, (name, value, marker) in GATES.items()}}


def load_reference():
    require(REFERENCE.is_file(), f"Run {ROOT / 'make_reference.sh'} first")
    value = read_json(REFERENCE)
    require(isinstance(value, dict), "Reference must be a JSON object")
    require(all(value.get(key) == val for key, val in reference_metadata().items()),
            "Reference metadata does not match the frozen recipe")
    for name, args in CONFIGS.items():
        config = value.get("configs", {}).get(name, {})
        require(config.get("args") == args and re.fullmatch(r"[a-f0-9]{64}", config.get("tokens_sha256", "")),
                f"Missing or invalid stock hash for {name}")
    require(value.get("placement", {}).get("pattern") == PLACEMENT_PATTERN
            and re.fullmatch(r"[a-f0-9]{64}", value["placement"].get("tokens_sha256", ""))
            and value["placement"].get("model_buffers"), "Invalid placement reference")
    cached = value.get("cached_prefix", {})
    require(type(cached.get("supported")) is bool and positive_int(cached.get("sweep_token")),
            "Invalid stock cached-prefix probe")
    require(value.get("model_sha256") == sha256(MODEL), "Local Granite model differs from the reference")
    return value


def pending(out, state, reason):
    defer(out, state, reason, "pending-run")
    log_line(out, shlex.join([str(ROOT / "run_checks.sh"), str(out)]))


def run(out, expected_work_dir=None):
    require(out.is_dir(), f"Missing output directory {out}")
    with lock(out / ".score.lock"):
        require(not (out / "score.log").is_symlink(), "score.log must not be a symbolic link")
        state = read_json(out / "score.json")
        require(state["stock_commit"] == COMMIT and state["stages"].get("S3", {}).get("status") == "pass",
                "Runtime checks require a passing S3 in this output directory")
        wo = state["wo"]
        work = Path(state["work_dir"]).resolve()
        require(work.parent == out, "Scorer work directory is outside this output directory")
        require(expected_work_dir is None or work == Path(expected_work_dir),
                "A different score run replaced this output directory")
        binary = work / "build/bin/llama-server"
        ports = port_pair(state["patch_sha256"])
        state["ports"] = ports
        try:
            with lock(ROOT / ".scorer-runtime.lock"), operator_signals():
                preflight(ports)
                require(os.access(binary, os.X_OK), f"Missing executable {binary}")
                reference = load_reference()
                run_dir = work / "runtime"
                run_dir.mkdir(exist_ok=True)
                # Retain each attempt and use fresh recorder paths on resume.
                run_dir = Path(tempfile.mkdtemp(prefix="attempt-", dir=run_dir))
                state.update(runtime_dir=str(run_dir), reference_sha256=sha256(REFERENCE))
                for stage in ("S4", "S5", "S6", "S7"):
                    state["stages"].pop(stage, None)
                for stage in ("S4", "S5", "S6", "S7"):
                    if not applicable(wo, stage):
                        verdict(out, state, stage, "skipped", "Stage does not apply to this work order")
                        continue
                    if stage == "S6" and wo == 1 and not any(
                            case.get("clean_exit") for case in state["stages"]["S5"].get("configs", {}).values()):
                        verdict(out, state, stage, "skipped", "S5 produced no clean WO1 server runs to replay")
                        continue
                    start = time.monotonic()
                    try:
                        if stage in ("S4", "S5"):
                            errors, details = main_stage(wo, binary, run_dir / stage, ports,
                                                         reference, stage == "S5")
                        elif stage == "S6" and wo == 1:
                            errors, details = replay(run_dir / "S5")
                        elif stage == "S6":
                            errors, details = placement(binary, run_dir / stage, ports["C2"], reference)
                        else:
                            errors, details = sweep(binary, run_dir / stage, ports, reference)
                    except RUN_ERRORS as exc:
                        errors, details = [one_line(exc)], {}
                    reasons = {"S4": "Both stock hashes matched and both logs were marker-free",
                               "S5": "Both stock hashes matched and both logs had the required markers",
                               "S6": "Replay or placement comparison passed",
                               "S7": "Mapper sweep matched with the gate off and on"}
                    verdict(out, state, stage, "fail" if errors else "pass",
                            " | ".join(errors) if errors else reasons[stage], start, **details)
        except RUN_ERRORS as exc:
            pending(out, state, one_line(exc))
        except KeyboardInterrupt:
            pending(out, state, "Operator interrupted the runtime run")


def make_reference():
    with lock(ROOT / ".scorer-runtime.lock"), operator_signals():
        require(not REFERENCE.exists(), f"Reference already exists at {REFERENCE}")
        preflight(REFERENCE_PORTS)
        receipt = stock_receipt()
        stock_hash = sha256(STOCK_BIN)
        require(receipt["source_commit"] == COMMIT
                and stock_hash == receipt["binaries"]["llama-server"]["sha256"],
                "Stock server binary differs from the pinned receipt")
        reference = reference_metadata()
        reference.update(model_sha256=sha256(MODEL), stock_server_sha256=stock_hash, configs={})
        directory = Path(tempfile.mkdtemp(prefix="stock-reference-", dir=ROOT))
        for name, args in CONFIGS.items():
            digest, _ = one_shot(STOCK_BIN, directory / name, REFERENCE_PORTS[name], args)
            reference["configs"][name] = {"args": args, "tokens_sha256": digest}
        port = REFERENCE_PORTS["C2"]
        baseline, override = directory / "placement-baseline", directory / "placement-ot"
        one_shot(STOCK_BIN, baseline, port, PLACEMENT_ARGS)
        digest, _ = one_shot(STOCK_BIN, override, port,
                             [*PLACEMENT_ARGS, "-ot", PLACEMENT_PATTERN + "=CPU"])
        buffers = model_buffers(override)
        baseline_buffers = model_buffers(baseline)
        cpu_side = lambda rows: sum(float(size) for buffer, size in rows
                                    if buffer.startswith("CPU") or buffer == "CUDA_Host")
        require(buffers and baseline_buffers and cpu_side(buffers) > cpu_side(baseline_buffers),
                "Stock -ot did not log increased CPU-side model buffer allocation")
        reference["placement"] = dict(pattern=PLACEMENT_PATTERN, buft="CPU",
                                      args=PLACEMENT_ARGS, tokens_sha256=digest, model_buffers=buffers,
                                      baseline_model_buffers=baseline_buffers)
        cache_dir = directory / "cached-prefix"
        with server(STOCK_BIN, cache_dir, REFERENCE_PORTS["C1"], CONFIGS["C1"], cache=True) as port:
            token = plain_token(port)
            _, reused = sweep_response(port, cache_dir, token, CACHED_SWEEP[0], True)
        reference["cached_prefix"] = dict(supported=positive_int(reused), cache_n=reused,
                                          sweep_token=token)
        reference["artifacts"] = str(directory)
        write_json(REFERENCE, reference)
        print(f"Wrote {REFERENCE}")
