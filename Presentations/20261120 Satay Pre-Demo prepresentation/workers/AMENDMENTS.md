# Scorer amendments

Version 2 applies uniformly to every candidate, past and future, against the original llama.cpp pin `9048bad8`. The evidence paths and excerpts below were supplied with the maintenance request.

## S5 marker lines (2026-11-20 00:49:15 UTC)

- **Evidence.** Stage S5 in `~/predemo/ab/out/wo5-C/score.json`, with the log at `~/predemo/ab/out/wo5-C/work-*/runtime/attempt-*/S5/C1/server.log`. The log contains an active marker, a `batch_layout_mapper: layout length=21 … begin=0 end=21 …` marker, and a stats marker.
- **Scorer defect.** The frozen implementation and protocol expected exactly two prefixed lines, while the maintenance report described a limit of three. Any exact limit rejects diagnostics permitted by the work orders, including WO5 half-open row spans and WO1 and WO4 stats-style detail lines.
- **Amended rule.** Require one active or inactive status marker and at least one stats marker with the required decimal counters after the pre-shutdown checkpoint for a clean exit. Use the last qualifying shutdown stats line. Allow additional prefixed lines and report their count and first five normalized lines in `extra_marker_lines`. Keep the S4 stock hash and zero-marker checks.

## S6 WO1 JSONL replay (2026-11-20 00:49:15 UTC)

- **Evidence.** The last line in `~/predemo/ab/out/wo1-C/work-*/runtime/attempt-*/S5/C1/events.jsonl` is a summary with `expected=1152`, `written=1151`, `lost=1`, `overflow=0`, and `incomplete=1`.
- **Scorer defect.** The frozen parser tried to read the loss summary as an event requiring a prefill or decode phase. The work order requires loss counting, and the summary accounts for the missing event.
- **Amended rule.** Parse at most one `summary` or `stats` JSONL object. Skip blank lines and require every other object to have a prefill or decode phase and either type `event` or an omitted type. With a summary, require the event count to equal its `expected - lost`. With no summary, warn, fail on logged loss, and require coverage of 24 layers times the microbatch count derived from the completion. Report event and phase counts, distinct observed layer and phase-scoped microbatch IDs, lost, incomplete, overflow, and whether a summary was present. Derive observed IDs from `layer` or `layer_id`, and `microbatch`, `microbatch_id`, `ubatch`, or `ubatch_id` when present. Report unavailable incomplete and overflow counters as null.

## S7 WO5 cached-prefix sweep (2026-11-20 00:49:15 UTC)

- **Evidence.** Stage S7, `C2 cached 513` in `~/predemo/ab/out/wo5-C/score.json` reports `cached and cold hashes differ`. The `cache_prompt` description in `tools/server/README.md` at `9048bad8` warns that logits can differ across batch sizes.
- **Scorer defect.** Cached prefixes can change microbatch boundaries even in stock llama.cpp, so cross-mode hash equality is an invalid pass condition.
- **Amended rule.** Compare gate-on and gate-off token hashes and `cache_n` at each length within each mode. Keep the zero-reuse requirement for cold runs and the primed-prefix reuse bounds for cached runs. Record `cached_vs_cold_differs` for the same gate and length as information only, with null when the cold result is unavailable.

## Original version 1 scorer hashes

```text
ea5f4f01849b5e0c9ef1eb148c0f7d0f6b55b86054b3f9ff1e403d7cec691a47  scorer.py
0176ed9385d09b085f4bcd62c69c23da40138f86fb947db6701b30b35a4c4080  scorer_runtime.py
```
