WORK ORDER 4: expert demand predictor (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, an optional predictor of the next layer's experts used only to hint early readiness. The authoritative router is never replaced.
- Single-slot prefill. One-layer lookahead. Predict up to 4 expert IDs ranked by frequency over the current layer and the two previous microbatches (ties to the lower ID). Predictor memory at most 1 MiB per context; potential wasted reads at most 8 MiB per request.
- Hints go to read-ahead advice (`madvise`) on mapped expert ranges when the weights are mmap-backed; if not mmap-backed or unsupported, be inactive with a reason.
- Gate: `LLAMA_EXPERT_PREDICT=1`. Unset: stock behaviour.
- INFO log lines (`-lv 4`): `expert_demand_predictor: active <effective settings>` once on an eligible run; `expert_demand_predictor: inactive (<reason>)` when requested but unavailable or after a terminal hint failure; `expert_demand_predictor: stats hits=<n> misses=<n> bytes_useful_at_consumption=<n> wasted_bytes=<n> lead_ns_total=<n> lead_samples=<n>` at exit.
- Invariants: hints never change compute, IDs, or output; byte identical to stock; any failure falls back silently except for the inactive line.
- Allowed paths: `src/`, `tools/server/server-context.cpp`, CMake files for new sources. Do not touch router, sampling or model files.
