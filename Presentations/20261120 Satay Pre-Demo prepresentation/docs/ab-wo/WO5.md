WORK ORDER 5: batch layout mapper (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, a mapper from prompt rows to microbatches for single-slot plain causal-text prefill, packing full microbatches within the stock reservation so weights are re-read as few times as the configured batch limits allow. Mixed-slot or multi-slot serving takes the stock path.
- State at most 128 fixed bytes per context, no added dynamic buffers. Half-open row spans in logs.
- Gate: `LLAMA_BATCH_LAYOUT=1` (any other value: inactive with a reason). Unset: stock behaviour.
- INFO log lines (`-lv 4`): `batch_layout_mapper: active n_batch=<rows> n_ubatch=<rows> limit=<rows>`; `batch_layout_mapper: inactive (<reason>, e.g. multiple slots configured)`; `batch_layout_mapper: stats decisions=<n> rows=<n> bypasses=<n>` at exit.
- Invariants: token order, positions and cached-prefix handling unchanged; output byte identical to stock across prompt lengths, with and without a cached prefix.
- Allowed paths: new `src/llama-batch-layout.h`, `tools/server/server-context.cpp`, CMake only if needed.
