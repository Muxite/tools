"""Descriptive paired analysis for CC pilot JSONL records (Python standard library only)."""
import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

DIMS = ("factual_support", "task_coverage", "reasoning_synthesis", "usability_format")
METRICS = ("elapsed_seconds", "input_tokens", "output_tokens", "tool_calls", "cost_usd")
STATUSES = {"completed", "cap_stop", "failed", "invalidated", "interrupted"}
REQUIRED = ("schema_version", "protocol_id", "case_id", "split", "pair_id", "repetition",
            "condition", "order_position", "assignment_seed", "started_at", "ended_at", "status",
            "termination_reason", "prompt_sha256", "fixture_manifest_sha256", "environment",
            "cc_versions", "limits", "measurements", "measurement_null_reason", "artifact",
            "scores", "deviations")
PAIR_FIELDS = ("protocol_id", "split", "repetition", "prompt_sha256", "fixture_manifest_sha256", "limits")


def _finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_record(rec, line_no="record"):
    if not isinstance(rec, dict):
        raise ValueError(f"{line_no}: record must be a JSON object")
    missing = [key for key in REQUIRED if key not in rec]
    if missing:
        raise ValueError(f"{line_no}: missing required keys: {', '.join(missing)}")
    if rec["schema_version"] != "1.0":
        raise ValueError(f"{line_no}: unsupported schema_version")
    for key in ("protocol_id", "case_id", "split", "pair_id", "assignment_seed"):
        if not isinstance(rec[key], str) or not rec[key]:
            raise ValueError(f"{line_no}: {key} must be a non-empty string")
    if rec["split"] not in ("development", "heldout"):
        raise ValueError(f"{line_no}: invalid split")
    if not isinstance(rec["repetition"], int) or isinstance(rec["repetition"], bool) or rec["repetition"] < 1:
        raise ValueError(f"{line_no}: repetition must be a positive integer")
    if rec["condition"] not in ("cc", "plain_agent"):
        raise ValueError(f"{line_no}: unknown condition {rec['condition']!r}")
    if rec["order_position"] not in (1, 2):
        raise ValueError(f"{line_no}: order_position must be 1 or 2")
    if rec["status"] not in STATUSES:
        raise ValueError(f"{line_no}: invalid status {rec['status']!r}")
    if rec["status"] == "completed" and rec["termination_reason"] is not None:
        raise ValueError(f"{line_no}: completed record must have null termination_reason")
    if rec["status"] != "completed" and not rec["termination_reason"]:
        raise ValueError(f"{line_no}: non-completed record needs termination_reason")
    for key in ("prompt_sha256", "fixture_manifest_sha256"):
        if not isinstance(rec[key], str) or not rec[key]:
            raise ValueError(f"{line_no}: {key} must be a non-empty hash/reference")
    for key in ("environment", "limits", "measurements", "measurement_null_reason"):
        if not isinstance(rec[key], dict):
            raise ValueError(f"{line_no}: {key} must be an object")
    if not isinstance(rec["cc_versions"], list) or not isinstance(rec["deviations"], list):
        raise ValueError(f"{line_no}: cc_versions and deviations must be arrays")
    if not isinstance(rec["environment"].get("model"), str) or not rec["environment"]["model"]:
        raise ValueError(f"{line_no}: environment.model must be pinned")
    if not isinstance(rec["environment"].get("tools"), list):
        raise ValueError(f"{line_no}: environment.tools must be an array of pinned tools")
    wall = rec["limits"].get("wall_seconds")
    if not _finite_number(wall) or wall <= 0:
        raise ValueError(f"{line_no}: limits.wall_seconds must be finite and positive")
    for metric in METRICS:
        if metric not in rec["measurements"]:
            raise ValueError(f"{line_no}: measurements missing {metric}")
        value = rec["measurements"].get(metric)
        if value is None:
            if not rec["measurement_null_reason"].get(metric):
                raise ValueError(f"{line_no}: null {metric} requires a measurement_null_reason")
        elif not _finite_number(value) or value < 0:
            raise ValueError(f"{line_no}: {metric} must be a finite non-negative number or null")
    scores = rec["scores"]
    if scores is not None:
        if not isinstance(scores, dict):
            raise ValueError(f"{line_no}: scores must be an object or null")
        for dim in DIMS:
            value = scores.get(dim)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 4:
                raise ValueError(f"{line_no}: {dim} must be an integer from 0 to 4")
        total = scores.get("total")
        if total != sum(scores[d] for d in DIMS):
            raise ValueError(f"{line_no}: total must equal dimension sum")
        if not isinstance(scores.get("critical_errors", []), list):
            raise ValueError(f"{line_no}: critical_errors must be an array")
    if rec["artifact"] is not None and not isinstance(rec["artifact"], dict):
        raise ValueError(f"{line_no}: artifact must be an object or null")


def load_records(path):
    records = []
    with open(path, encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON: {exc}") from exc
            validate_record(rec, line_no)
            records.append(rec)
    return records


def _summary(values):
    return {"n": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "values": values}


def analyze(records):
    # Validate direct callers too; tests and notebooks often call analyze() without JSONL loading.
    for index, rec in enumerate(records, 1):
        validate_record(rec, f"record {index}")
    pairs = defaultdict(dict)
    task_repetitions = {}
    statuses = Counter()
    deviations = []
    for rec in records:
        statuses[rec["status"]] += 1
        for item in rec["deviations"]:
            deviations.append({"pair_id": rec["pair_id"], "condition": rec["condition"], "deviation": item})
        repetition_key = (rec["case_id"], rec["repetition"])
        prior_pair_id = task_repetitions.setdefault(repetition_key, rec["pair_id"])
        if prior_pair_id != rec["pair_id"]:
            raise ValueError(f"multiple pair_ids for case/repetition {repetition_key}")
        key = (rec["case_id"], rec["pair_id"])
        condition = rec["condition"]
        if condition in pairs[key]:
            raise ValueError(f"duplicate {condition} record in pair {key}")
        pairs[key][condition] = rec

    accepted, excluded, deviation_sensitivity = [], [], []
    for key, arms in sorted(pairs.items()):
        cc, plain = arms.get("cc"), arms.get("plain_agent")
        reasons = []
        if not cc or not plain:
            reasons.append("missing arm")
        else:
            for field in PAIR_FIELDS:
                if cc[field] != plain[field]:
                    reasons.append(f"mismatched {field}")
            for field in ("model", "tools"):
                if cc["environment"].get(field) != plain["environment"].get(field):
                    reasons.append(f"mismatched environment.{field}")
            if cc["order_position"] == plain["order_position"]:
                reasons.append("duplicate order_position")
            if cc["status"] != "completed" or plain["status"] != "completed":
                reasons.append("arm not completed")
            if cc["scores"] is None or plain["scores"] is None:
                reasons.append("missing score")
            if cc["deviations"] or plain["deviations"]:
                reasons.append("protocol deviation")
        if reasons:
            excluded.append({"case_id": key[0], "pair_id": key[1], "reasons": reasons,
                             "statuses": {arm: rec["status"] for arm, rec in arms.items()}})
            # Exploratory sensitivity only: admit pairs whose sole exclusion is a documented deviation.
            if (reasons == ["protocol deviation"] and cc["status"] == plain["status"] == "completed"
                    and cc["scores"] is not None and plain["scores"] is not None):
                deviation_sensitivity.append((key, cc, plain))
        else:
            accepted.append((key, cc, plain))

    totals = [c["scores"]["total"] - p["scores"]["total"] for _, c, p in accepted]
    dimensions = {d: _summary([c["scores"][d] - p["scores"][d] for _, c, p in accepted]) for d in DIMS}
    measurements = {}
    for metric in METRICS:
        measurements[metric] = {
            "all_runs_by_condition": {
                condition: {
                    **_summary([r["measurements"][metric] for r in records
                                if r["condition"] == condition and r["measurements"][metric] is not None]),
                    "null_count": sum(r["measurements"][metric] is None for r in records if r["condition"] == condition),
                    "null_reasons": dict(Counter(r["measurement_null_reason"][metric] for r in records
                                                  if r["condition"] == condition and r["measurements"][metric] is None))}
                for condition in ("cc", "plain_agent")},
            "accepted_pairs": {
                "cc": _summary([c["measurements"][metric] for _, c, _ in accepted if c["measurements"][metric] is not None]),
                "plain_agent": _summary([p["measurements"][metric] for _, _, p in accepted if p["measurements"][metric] is not None]),
                "paired_differences_cc_minus_plain": _summary([
                    c["measurements"][metric] - p["measurements"][metric]
                    for _, c, p in accepted if c["measurements"][metric] is not None and p["measurements"][metric] is not None])}}
    per_task = {}
    for task in sorted({key[0] for key, _, _ in accepted}):
        task_pairs = [(c, p) for key, c, p in accepted if key[0] == task]
        ds = [c["scores"]["total"] - p["scores"]["total"] for c, p in task_pairs]
        per_task[task] = {"n": len(ds), "score_difference": _summary(ds),
                          "cc_regressions": sum(d < 0 for d in ds), "ties": sum(d == 0 for d in ds),
                          "cc_improvements": sum(d > 0 for d in ds),
                          "critical_errors": {"cc": sum(len(c["scores"].get("critical_errors", [])) for c, _ in task_pairs),
                                              "plain_agent": sum(len(p["scores"].get("critical_errors", [])) for _, p in task_pairs)}}
    condition_status = {condition: dict(sorted(Counter(r["status"] for r in records if r["condition"] == condition).items()))
                        for condition in ("cc", "plain_agent")}
    sensitivity_diffs = [c["scores"]["total"] - p["scores"]["total"]
                         for _, c, p in deviation_sensitivity]
    return {"record_count": len(records), "status_counts": dict(sorted(statuses.items())),
            "status_counts_by_condition": condition_status,
            "accepted_completed_pairs": len(accepted), "primary_analysis_available": bool(accepted),
            "excluded_pairs": excluded, "total_score_cc_minus_plain": _summary(totals),
            "dimensions_cc_minus_plain": dimensions, "per_task": per_task,
            "measurements": measurements, "deviations": deviations,
            "exploratory_deviation_sensitivity": {"label": "exploratory; includes only otherwise-comparable completed pairs with deviations",
                                                   "n": len(sensitivity_diffs), "score_difference": _summary(sensitivity_diffs)},
            "note": "Descriptive only. Excluded pairs remain visible; no inference beyond this sample."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(analyze(load_records(args.jsonl)), indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    else:
        print(result)


if __name__ == "__main__":
    main()
