# Feature provenance: built into llama.cpp vs made by us (DRAFT, 2026-11-19)

Method: partial clone of `ggml-org/llama.cpp`; `git log --diff-filter=A` for files and `git log -S<string> -- <path>` for strings, restricted to ancestors of the pin `9048bad8` (2026-11-17). Our side: `siminfeng` and `xs-dev/llama-opt` git logs and patch file dates on Satay. Dates are commit dates. "Upstream" = stock at the pin; "ours" = not found anywhere in upstream history.

## Upstream (built in, stock at the pin)
| Feature | First commit | Date | Note |
|---|---|---|---|
| `--override-tensor` / `-ot` | `e0e912f49` (#11397) | 2025-04-02 | Mature |
| `--cpu-moe` | `a06ed5fea` (#14992) | 2025-07-31 | Mature |
| `--n-cpu-moe` | `ec428b02c` (#15077) | 2025-08-05 | Mature |
| `-fit` / `--fit-target` auto-fit | `b1f3a6e5d` (#16653) | 2025-12-15 | Default on, so it can alter unset args |
| `--load-mode` (replaces mlock/mmap/dio flags) | `e6dd0e29a` (#20834) | 2026-07-23 | Source of the "auto → none on Jetson" surprise |
| `--lazy-mode` / `-lzm` | `bebc9350e` (#27969) | 2026-08-30 | Engram mapping relies on it |
| `ggml_backend_sched_set_eval_callback` | `f3f65429c` | 2024-06-26 | Old, stable |
| DeepSeek V4.1 Flash (`deepseek41`) | `74bca3950` (#31086) | 2026-10-25 | The b11870 tag resolves here |
| `sched_copy_experts` (selective expert copy moved to user code) | `6753a033f0` (#29943) | 2026-10-06 | Only 6 weeks old; the scheduler's "callback while copying input weights" |
| **Native MoE cache** (`--moe-cache-mib`, `src/llama-moe-cache.cpp`) | `d6cf9acb2` (#29887) | 2026-10-07 | GPU cache for host-resident experts. **Overlaps our Expert Weight Cache** |
| Native cache: run missed experts on CPU, `docs/moe-cache.md`, `scripts/moe-cache-tune.py` | `e95426f16` (#30966) | 2026-11-08 | Stock tuning guidance; 9 days before the pin |
| Native cache: "CPU part does not wait for cached experts" | `cf34d3113` (#31888) | 2026-11-08 | Our earlier Satay base |

## Ours (not found in upstream history)
| Feature | Where | Date | Note |
|---|---|---|---|
| Expert Fill (buffered fill, `expert_fill`, `LLAMA_EXPERT_FILL`) | `llama-opt` commit `c0427fe6c`; exports `12`–`15` | 2026-11-12 | Built on `cf34d3113` |
| Router prefetch, Pregate, mmap advice, thread names | `llama-opt` `5cded3e76`, `6e9d96cf4`, `93a61111e`; siminfeng `cc/mmap_advice` | 2026-11-12 | Same integration day |
| `ggml_backend_sched_set_cpu_callback` (CPU before-node hook) | Common-pin Fill patch (9 files) | re-ported 2026-11-19/20 | Not in upstream; needed by Fill's router-ID reads |
| `src/llama-expert-fill.h` | Common-pin Fill patch | same | Not in upstream |
| expert-streaming assignments, c2 page-cache protocol | siminfeng `a3f6544`, `682c637` | 2026-11-11/12 | Lab/evidence side |

## What this changes for the demo
1. **The Expert Weight Cache CC overlaps a stock feature that is about six weeks old and under active change.** Stock's GPU cache (since 2026-10-07) and its tuning script (2026-11-08) exist. The CC must do something the native cache does not, and the A+ arm (native cache tuned as documented) is not optional.
2. **Our Nov 13 J-OM13 result was measured against a base that already contained the native cache path** (`cf34d3113`, cache default off). It did not compare to the tuned native cache either.
3. **`sched_copy_experts` is also recent upstream.** A CC that hooks it follows an interface that may still move. Pin the commit and re-check when the pin changes.
4. **Our hook (`set_cpu_callback`) and Fill are ours.** Claims about them are claims about our code, not about llama.cpp.
5. **The Jetson `load_mode = none` behaviour comes from the 2026-07-23 load-mode refactor.** It is stock behaviour, not ours.

Open: confirm dates for the exact string `LLAMA_EXPERT_FILL` and `set_cpu_callback` against upstream (background query still running at time of writing; both are expected "not found").
