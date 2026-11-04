---
id: cc-pilot-raw-results-schema
status: proposed
source: AI4Research-Notebook/Experiments/cc-effectiveness-protocol.md
last_reviewed: 2026-10-20
next_action: Freeze schema version with run manifest before collecting records.
---
# Raw results JSONL schema

UTF-8 JSON Lines: one run record per line. Preserve outputs separately by path and SHA-256. Null means unknown, unavailable, or not applicable and requires a keyed reason; it never means zero. Preserve every status, including failures and interruptions. The analyzer validates every record and excludes invalid or non-completed pairs with reasons.

Required record keys: `schema_version` (`"1.0"`), `protocol_id`, `case_id`, `split` (`development`/`heldout`), `pair_id`, positive integer `repetition`, `condition` (`cc`/`plain_agent`), `order_position` (1/2), `assignment_seed`, `started_at`, `ended_at`, `status`, `termination_reason`, `prompt_sha256`, `fixture_manifest_sha256`, `environment`, `cc_versions`, `limits`, `measurements`, `measurement_null_reason`, `artifact`, `scores`, `deviations`.

Allowed statuses are `completed`, `cap_stop`, `failed`, `invalidated`, and `interrupted`. A non-completed record has a termination reason. A completed record has null termination reason. `environment` includes pinned `model` and `tools` so paired arms can be checked. `limits.wall_seconds` is finite and positive. Analyzer output includes status counts by condition and measured resource values for every run, including failed runs; primary paired resource summaries include only valid completed pairs. A separately labelled exploratory sensitivity summary includes otherwise-comparable completed quality pairs with documented deviations. `limits` includes `wall_seconds` and all configured caps; paired arms must match. `measurements` has `elapsed_seconds`, `input_tokens`, `output_tokens`, `tool_calls`, and `cost_usd`. Every value is finite and non-negative or null with a nonempty matching `measurement_null_reason`. `scores` is null until blind scoring; otherwise it has four integer dimensions 0–4, a total equal to their sum, and `critical_errors` array. Deviations are retained and cause pair exclusion from the primary comparison.

Placeholder example only; it does **not** describe a run:

```json
{"schema_version":"1.0","protocol_id":"cc-effectiveness-protocol@draft-1","case_id":"DEV-01","split":"development","pair_id":"DEV-01-R1","repetition":1,"condition":"cc","order_position":1,"assignment_seed":"placeholder-seed","started_at":null,"ended_at":null,"status":"interrupted","termination_reason":"placeholder: no execution occurred","prompt_sha256":"placeholder-unfrozen","fixture_manifest_sha256":"placeholder-unfrozen","environment":{"model":"placeholder-unpinned","tools":[]},"cc_versions":[],"limits":{"wall_seconds":600,"tokens":null,"tool_calls":null},"measurements":{"elapsed_seconds":null,"input_tokens":null,"output_tokens":null,"tool_calls":null,"cost_usd":null},"measurement_null_reason":{"elapsed_seconds":"not measured","input_tokens":"not measured","output_tokens":"not measured","tool_calls":"not measured","cost_usd":"not available"},"artifact":null,"scores":null,"deviations":[]}
```

See [analysis script](tools/analyze_pairs.py) and [[Experiments/cc-effectiveness-protocol|CC Effectiveness Protocol]].
