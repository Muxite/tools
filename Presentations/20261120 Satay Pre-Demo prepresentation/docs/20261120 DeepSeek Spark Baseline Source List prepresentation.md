# Baseline source list (DRAFT, freeze before the first measurement)

**Definition.** Arm A is the llama.cpp pin `9048bad8d6e3a0f9f1726e238e451181c7e02613`, the verified six-shard `IQ2_XXS` pack with Engram, run as the model card and the pinned `tools/server/README.md` say to run it. No extra hand-tuning. Every setting below has a source or is marked as a decision to make.

Sources read 2026-11-19: model card (https://huggingface.co/ISTA-DASLab/DeepSeek-V4.1-Flash-1017-GSQ-RCO-GGUF) and the pinned server README (`tools/server/README.md` at `9048bad8`). The README was then read in full except a ~126-character gap near the `/v1/systemone` example, along with `docs/moe-cache.md` and `docs/multi-gpu.md` at the pin.

| Setting | Documented source says | Retained stock contract used | Status |
|---|---|---|---|
| llama.cpp version | Card: "requires b11870 or newer" | pin `9048bad8` | **Confirmed:** b11870 resolves to `74bca39` (DSV4.1 flash support, 2026-10-25), an ancestor of `9048bad8` (623 commits ahead) |
| `-ngl` | Card examples: `-ngl 99`. README default: `auto` | 99 | **Matches card** |
| `-c` | Card: no value. README default: `0` (from model, 1M) | 4,096 | **Decision.** 1M cannot be allocated. Needed to fit memory, so a necessary deviation, not a tuning. Larger ctx (>4,096-in) for the long confirmation |
| `-b` | Card: none. README default **2,048** | 512 | **DECIDED: 2,048 (documented).** Retained 512 was not documented. Confirm it runs under the memory guards and record the compute-buffer cost; if not, record the failure and fall back |
| `-ub` | Card: none. README default 512 | 512 | Matches README |
| Threads `-t/-tb` | Card: none. README default `-1` (auto) | 8 / 8 | **Decision.** Explicit 8 is not documented |
| Routed experts on CPU (`-ot` / `--cpu-moe`) | Card: not mentioned. README: flags exist, no default | all routed gate/up/down forced to CPU | **Decision.** Without it the 138 GB backbone does not fit. Flag is documented, the choice of use is not |
| Load mode | README: `-lm` default `auto` (mmap unless unsupported). There is no `--mmap` flag | mapped | Matches, use default |
| Engram / lazy load | Card: tables memory-mapped. README `--lazy-mode` default `auto` = on for tensors >4 GiB; keep file on SSD | mapped, lazy | Matches |
| Native MoE cache `--moe-cache-mib` | README default 0 (disabled). `docs/moe-cache.md` recommends `python3 scripts/moe-cache-tune.py -- build/bin/llama-server -m model.gguf -cmoe -t 8 -c 32768` | unrecorded | **Decision 5** below |
| `-fit` | README default `on` (adjusts unset arguments to fit device memory) | unrecorded | Record the effective result |
| `-np` | README default `-1` (auto) | 1 slot | Decision (single slot for exact comparison) |
| Prompt cache / `--cache-reuse` | README: prompt cache enabled, reuse 0 | cross-request reuse **off** | **Decision.** Off so each request is a true cold prefill (TTFT) |
| `--cache-ram` | README default 8,192 MiB | unrecorded | Record effective value |
| `-fa`, `-ctk`, `-ctv` | README: auto, f16, f16 | unrecorded | Record effective values |
| Sampling | README default temp 0.8, top-k 40, top-p 0.95, seed -1 | greedy | **Decision.** Greedy needed for exact-token check |
| Reasoning | Card: `--reasoning on --reasoning-effort 50` (all card results at 50) | unrecorded | **Decision.** Pick; effort changes output length and thus TTFT-adjacent timing. Test with reasoning fixed |
| Drafting | none | off | Decision |
| Memory envelope | Card: no RAM figure for llama.cpp | 96 GiB cgroup, 16 GiB MemAvailable guard | Decision (harness safety, not a setting of stock) |

## Decisions
1. **`-b` = 2,048** (README default, per your call). It may move TTFT versus the retained 512, so record it in the wording log.
2. **CPU expert override:** treat as a documented-flag necessary for fit (stays in all arms) or as a configuration the tuning CC may choose. I recommend all arms share it, so arms differ only in what each CC adds.
3. **Reasoning mode and effort:** off, or the card's 50.
4. **Threads:** documented auto or explicit 8. (`docs/moe-cache.md` uses `-t 8` with `-cmoe`, which supports 8.)
5. **Native expert cache (new finding).** Stock already ships `--moe-cache-mib` and a tuning script for CPU-resident experts, off by default. Arm A uses the default (off), the documented out-of-box state. Because the repo documents tuning it, also run **A+ (stock with `moe-cache-tune.py` run as documented)** as a reported reference, not as the bar. Without A+, a skeptic can say the Expert Weight Cache CC only switched on a feature stock already has. That CC must show something the native cache lacks, such as one shared lease per expert per operation and a handle through the last reader.

## Freeze rule
After sign-off, record the effective values read back from the loader (not the command line), the README and card revision, and commit this file. Later edits go in a dated wording log, never in place.
