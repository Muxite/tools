# Arm-C Expert Weight Cache activation

Base commit `9048bad8d6e3a0f9f1726e238e451181c7e02613`.

## Files touched

- `ggml/include/ggml-backend.h`
- `ggml/src/ggml-backend.cpp`
- `src/llama-context.cpp`
- `src/llama-context.h`
- `src/llama-expert-fill.h` (new)
- `src/llama-mmap.cpp`
- `src/llama-model-loader.cpp`
- `src/llama-model.cpp`
- `src/llama-model.h`

## Environment variables

| Variable and value | Effect |
| --- | --- |
| `LLAMA_EXPERT_FILL=1` | Requests fill on Linux. Initialization requires supported, contiguous, mmap-backed expert tensors and available file offsets. |
| `LLAMA_EXPERT_FILL_THREADS` | Worker threads per file. Default 8 and maximum accepted value 256. |
| `LLAMA_EXPERT_FILL_CHUNK_KIB` | Chunk size in KiB. Default 1024 and maximum accepted value 65536. |
| `LLAMA_EXPERT_FILL_MIN_TOKENS` | Inclusive lower bound on tokens per microbatch. Defaults to zero. |
| `LLAMA_EXPERT_FILL_MAX_TOKENS` | Inclusive upper bound on tokens per microbatch. Zero or unset leaves the upper bound open. |
| `LLAMA_EXPERT_FILL_RANDOM=1` | Applies random advice to mapped expert weight ranges during mapping. |
| `LLAMA_EXPERT_FILL_RANDOM=decode` | Applies random advice to those ranges at the first single-token microbatch. |
| `LLAMA_EXPERT_FILL_DIAG=1` | Enables diagnostic timing, fault, and residency counters. |
| `LLAMA_EXPERT_FILL_DIAG_CSV` | With diagnostics enabled, optionally writes per-token statistics to the specified CSV path. |
| `LLAMA_EXPERT_FILL_POPULATE=1` | Enables the optional `MADV_POPULATE_READ` pass when supported. |
| `LLAMA_EXPERT_PREFETCH=1` | Enables the CPU host-consumer prefetch hook and expert-range random advice when fill is unrequested. |
| `LLAMA_EXPERT_PREFETCH_NEXT=1` | Enables next-layer prediction for the prefetch path. |
| `LLAMA_MMAP_ADVICE=random` | Requests random advice for the mapping when the expert prefetch path is off. It skips `POSIX_FADV_SEQUENTIAL` and `WILLNEED`. |

The patch adds zero CLI flags and zero `LLAMA_ARG_*` settings.

## Log markers

- `expert_fill: active threads=... chunk_kib=... random=... files=...`
- `expert_fill: inactive (...)` for initialization or fill exceptions, unsupported host router IDs, or failed decode-time random advice.
- `expert_fill: random advice applied at decode`
- `expert_fill: stats calls=...` for aggregate fill counters.
- `expert_fill: diag token=...` for stderr diagnostics every 16 single-token microbatches, and `expert_fill: diag tokens=...` for aggregate stderr diagnostics.
- `expert_fill: populate unsupported`
- `expert_prefetch: CPU host-consumer hook enabled; device-only experts skipped, next=..., LRU=32 ids/32 tokens`
- `expert_prefetch: skipping non-mmap or non-expert-contiguous tensors/invalid ids (once)`
- `expert_prefetch: skipping unsupported router ids (once)`
- `expert_prefetch: advise calls=...` for aggregate advice and prediction counters.
- `llama_mmap: expert prefetch (RANDOM expert ranges, default non-expert advice)`
- `llama_mmap: LLAMA_MMAP_ADVICE=random (no FADV_SEQUENTIAL, no WILLNEED, MADV_RANDOM)`
