=====WO1=====
WORK ORDER 1: runtime event recorder (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, a runtime event recorder for MoE inference.
- Records, per (microbatch, layer) at the point the router's selected expert IDs (`ffn_moe_topk-*` nodes) are available: request id, phase (prefill or decode), microbatch index, layer index, the selected expert IDs, monotonic nanosecond timestamps, and the bytes the scheduler submits to copy expert weights for that layer when it does.
- Bounded in-memory ring (default 64 MiB, `LLAMA_EVENT_REC_MIB` overrides, whole decimal MiB), no file I/O in the hot path, flushed to a freshly created JSONL file at normal exit. When the ring is full, count the loss and drop the newest; report it in stats.
- Gate: environment variable `LLAMA_EVENT_REC=<path to JSONL file>`. Unset means the binary behaves exactly as stock, with zero extra work beyond one cached getenv check.
- Log lines at INFO level (visible with `-lv 4`), once each: `runtime_event_recorder: active <effective settings>` on first use; `runtime_event_recorder: inactive (<reason>)` if the gate is set but the recorder cannot run (bad path, file exists, unsupported path); `runtime_event_recorder: stats events=<n> lost=<n> bytes=<n>` at exit.
- Invariants: token output, router IDs, mixture weights, sampling and ordering unchanged; greedy output byte identical to stock with the gate unset and with it set. Any error falls back to stock behaviour.
- Allowed paths: new files under `src/`, edits under `src/`, `tools/server/server-context.cpp`, `tools/server/server-context.h`, and CMake files needed to compile new sources. Do not touch router, sampling or model files.
=====WO2=====
WORK ORDER 2: expert weight cache for staged slices (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, bounded reuse of already-staged expert weight slices on the stock scheduler copy path (`sched_copy_experts` in `src/llama-context.cpp` and the scheduler's input-weight copy callback), so an expert slice copied to a device buffer for one operation is reused instead of copied again within the same operation.
- One shared lease per expert per graph operation, held through its last reader, released at scheduler synchronization. Demand-only admission, unleased LRU eviction, capacity cap default 64 MiB (`LLAMA_EXPERT_CACHE_MIB`, whole decimal MiB; invalid or zero means stock path). One cache per context.
- Do not duplicate the stock native MoE cache (`--moe-cache-mib`, `src/llama-moe-cache.cpp`): if it is enabled, stay inactive and say so.
- Gate: `LLAMA_EXPERT_CACHE=1`. Unset: binary identical in behaviour to stock.
- INFO log lines (`-lv 4`): `expert_weight_cache: active cap_mib=<effective> backend=<name>` on first eligible use; `expert_weight_cache: inactive (<reason>)` on bypass or failure; `expert_weight_cache: stats leases=<n> reuses=<n> evictions=<n> bytes_copied_saved=<n> peak_bytes=<n>` at exit.
- Invariants: slice bytes identical to the file; never release a slice before its last reader finishes; cap respected; any lease error falls back to a plain copy; output byte identical to stock.
- Allowed paths: `src/`, `ggml/src/ggml-backend.cpp`, `ggml/include/ggml-backend.h` (only if a hook is genuinely needed), CMake files for new sources. Do not touch router, sampling or model files.
=====WO3=====
WORK ORDER 3: weight placement planner readback (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, the engine side of a weight placement planner: load an explicit placement plan file and turn it into tensor buffer-type overrides equivalent to `-ot`, and log the effective assignment.
- Option `--placement-plan <file>` (register in `common/arg.cpp`, env `LLAMA_ARG_PLACEMENT_PLAN`), honoured only when the gate `LLAMA_PLACEMENT_PLAN=1` is also set. Plan file: JSON `{"version":1,"overrides":[{"pattern":"<tensor name regex>","buft":"CPU"}]}`, at most 4 MiB, at most 4095 entries; unknown fields or versions are an error reported as inactive.
- Each tensor placed exactly once; unmatched tensors keep the stock default. Missing file or bad JSON means inactive with a reason, never a crash.
- INFO log lines (`-lv 4`): exactly one `weight_placement_planner: active cap_bytes=<n> peak_bytes=<n>` or one `weight_placement_planner: inactive (<reason>)`; one `weight_placement_planner: stats assigned=<n> stock=<n>` at exit.
- Invariants: output byte identical to stock with the gate unset, and identical to stock `-ot` for the same assignments with the gate set.
- Allowed paths: `common/arg.cpp`, `common/common.h`, `common/common.cpp`, `src/`, CMake files for new sources.
=====WO4=====
WORK ORDER 4: expert demand predictor (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, an optional predictor of the next layer's experts used only to hint early readiness. The authoritative router is never replaced.
- Single-slot prefill. One-layer lookahead. Predict up to 4 expert IDs ranked by frequency over the current layer and the two previous microbatches (ties to the lower ID). Predictor memory at most 1 MiB per context; potential wasted reads at most 8 MiB per request.
- Hints go to read-ahead advice (`madvise`) on mapped expert ranges when the weights are mmap-backed; if not mmap-backed or unsupported, be inactive with a reason.
- Gate: `LLAMA_EXPERT_PREDICT=1`. Unset: stock behaviour.
- INFO log lines (`-lv 4`): `expert_demand_predictor: active <effective settings>` once on an eligible run; `expert_demand_predictor: inactive (<reason>)` when requested but unavailable or after a terminal hint failure; `expert_demand_predictor: stats hits=<n> misses=<n> bytes_useful_at_consumption=<n> wasted_bytes=<n> lead_ns_total=<n> lead_samples=<n>` at exit.
- Invariants: hints never change compute, IDs, or output; byte identical to stock; any failure falls back silently except for the inactive line.
- Allowed paths: `src/`, `tools/server/server-context.cpp`, CMake files for new sources. Do not touch router, sampling or model files.
=====WO5=====
WORK ORDER 5: batch layout mapper (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, a mapper from prompt rows to microbatches for single-slot plain causal-text prefill, packing full microbatches within the stock reservation so weights are re-read as few times as the configured batch limits allow. Mixed-slot or multi-slot serving takes the stock path.
- State at most 128 fixed bytes per context, no added dynamic buffers. Half-open row spans in logs.
- Gate: `LLAMA_BATCH_LAYOUT=1` (any other value: inactive with a reason). Unset: stock behaviour.
- INFO log lines (`-lv 4`): `batch_layout_mapper: active n_batch=<rows> n_ubatch=<rows> limit=<rows>`; `batch_layout_mapper: inactive (<reason>, e.g. multiple slots configured)`; `batch_layout_mapper: stats decisions=<n> rows=<n> bypasses=<n>` at exit.
- Invariants: token order, positions and cached-prefix handling unchanged; output byte identical to stock across prompt lengths, with and without a cached prefix.
- Allowed paths: new `src/llama-batch-layout.h`, `tools/server/server-context.cpp`, CMake only if needed.
