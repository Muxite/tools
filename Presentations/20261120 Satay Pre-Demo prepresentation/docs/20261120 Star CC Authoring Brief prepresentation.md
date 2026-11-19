# Star CC authoring brief (for capsule authors and the factory agent)

Purpose: turn the five starred builder CCs from proposals into CC v2 capsules that JiuwenSwarm's factory agent can use to implement a **diff into llama.cpp** pinned at `9048bad8d6e3a0f9f1726e238e451181c7e02613`. The system ontology and dictionary already exist (`unified-dictionary.yaml/.md`, `metadata-alignment.md`, `EXAMPLE.md`); reuse their file kinds and terms, do not extend them. This is not a new ontology project.

## Door-builder rules (apply to every CC)
- The **contract, ontology slice and planner** say what to build (colour, size, hole for the handle). The **CC** knows how to build it and must finish the job.
- If the ontology or work order is silent on a detail, the CC chooses a sensible default and records it as `chosen_by_cc` with its reason. It never refuses to build for lack of a detail.
- If the part already exists in the tree (an earlier version, a Fill-style patch), the CC **modifies it to what is specified** instead of adding a second copy.
- The CC must **verify its own work** before it may report done: apply check, compile of every touched unit, activation marker present, parity test, and the CC-specific checks below. Failed checks are reported as failed, never as done.
- Name the CC for what it builds. Components are not actions.
- Label every result with its true stage: fixture | native CC execution | compile | runtime acceptance | hardware measurement.

## Shared engineering rules for the diff
- Base: `9048bad8`. Minimal touch. New code in new files under `src/` where possible.
- **Off by default**, enabled by one environment variable, so the binary equals stock when off.
- **Activation marker** at INFO level (visible only with `-lv 4`): one line `<capsule>: active <effective settings>` or `<capsule>: inactive (<reason>)`, once at first use, and one `stats` line at exit. Silence must never be an acceptable state when the variable is set.
- Needs `-lm mmap` where it touches mapped weights (Jetson `auto` resolves to `none`).
- Never change token order, router IDs, mixture weights, quantization, or sampling. Greedy output must stay byte identical to stock within one configuration.
- Any error falls back to the stock path and logs `inactive (...)`.
- Memory it owns is accounted against the shared capacity ledger and bounded by a stated cap.

## The five

### 1. Runtime Event Recorder Builder (`observability.build_runtime_event_recorder`)
- Component → subcomponent: Generation runtime → Runtime event recording.
- Builds: a recorder that joins request, phase (prefill/decode), microbatch, layer, selected expert IDs, bytes transferred, consumer-ready time, using monotonic ns, into a bounded in-memory ring flushed at exit or phase end. No file I/O in the hot path.
- Output: JSONL, one record per (microbatch, layer), plus a coverage/loss/overhead summary.
- Touchpoints: stock `ggml_backend_sched_eval_callback` for `ffn_moe_topk-*` nodes; `src/llama-context.cpp` (`sched_copy_experts`) for transfer sizes.
- Env gate: `LLAMA_EVENT_REC=<path>`. Cap: `LLAMA_EVENT_REC_MIB` (default 64).
- Verify: capture off vs on identical output; record count equals layers × microbatches expected; loss counted and reported; overhead measured and reported.
- Adapt: `observability.expert_route_capture` 1.0.1 (6,144 Granite selections, exact parity) and the wait-analysis fixtures.

### 2. Expert Weight Cache Builder (`engine.build_expert_weight_cache`)
- Component → subcomponent: Weight residency → Expert weight cache.
- Builds: bounded reuse of already-staged expert slices, with one shared lease per expert per operation and a handle held through the last reader, on the stock copy path in `sched_copy_experts`. Do not double the stock `--moe-cache-mib`: if the native cache is enabled, this capsule stays inactive and says so.
- Output: the same bytes as stock, delivered with fewer repeated transfers.
- Invariants: slice bytes identical to the file; no slice released before its last reader finishes; capacity cap respected; fallback to a plain copy on any lease error.
- Env gate: `LLAMA_EXPERT_CACHE=1`, cap `LLAMA_EXPERT_CACHE_MIB`.
- Verify: parity; stats line shows leases, reuses, evictions, bytes copied saved; a replay test for lifetime and error paths.
- Reference implementation (material, not to be copied blindly): the common-pin Fill patch (`expert-fill-common-source.patch`) and `engine.expert_streaming`.

### 3. Weight Placement Planner Builder (`placement.build_weight_placement_planner`)
- Component → subcomponent: Weight residency → Weight placement planner.
- Builds: a planner that turns an inventory (tensor names, bytes), phase lifetimes and one byte budget (host memory cap, KV, compute buffers, headroom) into an admitted placement, accounting for aliases, replicas, temporary copies, and displacement. The engine part is small: `--placement-plan <file>` read by `common/arg.cpp` to produce buffer-type overrides equivalent to `-ot`, plus a log of effective assignments per tensor class.
- Output: a plan file and the effective assignment readback.
- Invariants: the admitted bytes never exceed the budget; every tensor placed exactly once; unplaced → stock default.
- Verify: unit tests on the planner (synthetic and real Qwen/Granite inventories); effective assignments equal the plan; parity with stock for the same assignment.
- Adapt: `engine.heterogeneous_placement_lab`, `placement_budget.py` and its tests.

### 4. Expert Demand Predictor Builder (`routing.build_expert_demand_predictor`)
- Component → subcomponent: Weight residency → Expert demand prediction.
- Builds: optional early readiness hints for the next layer's experts from previous-layer routing and a short history. The authoritative router is never replaced. Hints go to the weight cache or to read-ahead advice on mapped ranges.
- Output: `hint(layer, expert ids, confidence, lead)` calls; wasted-read budget.
- Invariants: hints never alter compute or IDs; wasted bytes capped; hint failure is silent fallback.
- Env gate: `LLAMA_EXPERT_PREDICT=1`.
- Verify: parity; stats line gives hits, misses, bytes useful at consumption, wasted bytes, lead time; offline replay on captured traces gives held-out coverage.
- Adapt: Expert Pregate, `factory.expert_prediction`, `engine.expert_cache_lab`.

### 5. Batch Layout Mapper Builder (`engine.build_batch_layout_mapper`)
- Component → subcomponent: Generation runtime → Request and batch orchestration.
- Builds: the mapping from prompt rows to microbatches (boundaries and sizes) for single-slot prefill, chosen so weights are re-read as few times as the memory budget allows, within compute-buffer limits. Mixed-slot batches take the stock bypass.
- Output: layout decision log (lengths, cached prefix, boundaries).
- Invariants: token order, positions and cached-prefix handling unchanged; exact output across lengths.
- Env gate: `LLAMA_BATCH_LAYOUT=1`.
- Verify: 14-length sweep with and without cached prefixes, identical to stock; bypass confirmed for multi-slot.
- Adapt: `engine.prompt_batch_layout` 1.0.1 (an initial mixed-slot mismatch led to the stock bypass).

## Deliverables per capsule
`cc.yaml` (CC v2), `GUIDE.md` (what it builds, defaults, create-or-modify, done criteria), `METHOD.md` (checks and stage labels), `ONTOLOGY.yaml` (slice using the existing dictionary terms), `components/<name>/component.yaml` valid against `factory/schemas/component.schema.json`, a task template `tasks/<name>.json`, and a validation note listing what was and was not run.
