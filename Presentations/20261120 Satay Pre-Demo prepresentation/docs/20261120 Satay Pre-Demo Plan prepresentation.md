# Satay pre-demo plan (DRAFT, started 2026-11-19)

**Purpose.** Prove the *method* on Satay before the DGX Spark: freeze baseline, apply CCs, build, activate, run paired timing, check output, record receipts, decide. Retire process surprises. Satay numbers say nothing about Spark performance and are labelled that way.

**Machine.** Jetson Orin Nano, 7.4 GiB unified RAM, 3.7 GiB swap, 6 cores, SM87, CUDA 12.6, 21 GB free disk. Idle at start (jobq worker, empty queue). Not touched: the Codex TUI in tmux `main`, `~/satay-cc-prefill-20261119`.

**Models.**
| Role | Model | Size | Why |
|---|---|---|---|
| Functional | Granite 3.1 1B-A400M Q8_0 | 1.4 GB | MoE that fits; fast cells; activation, parity, route capture |
| Pressure | Qwen3.6-35B-A3B UD-Q4_K_XL | 22.4 GB | ~3× RAM, so storage pressure is natural (same shape as the Spark problem, smaller) |

**Source.** Same pin as the Spark: llama.cpp `9048bad8` (fresh checkout in `~/predemo/llama.cpp-stock`, unmodified). The earlier Satay tree is `cf34d3113` with a CPU-only build, so it is not reused as the comparator.

## Stages (each result gets its true stage label)
0. **Freeze.** Baseline settings with sources (Satay analogue of the Spark baseline file), machine state gate: nvpmodel/clock mode, thermal, swap, load, idle jobq check; before/after snapshot per cell.
1. **Stock build, SM87 CUDA, pin `9048bad8`** (W1 running). Receipt: commit, flags, hashes, smoke on Granite.
2. **Stock qualification.** A/A on both models (noise floor), settle cold-vs-warm filesystem cache procedure, memory peak sampler, client TTFT + native timing fields, exact-token compare, stop reason.
3. **Per-CC pass.** For each ★ CC, apply to the pin by CC (diff kept), verify before "done", build, confirm activation marker, then run at the highest stage reachable on Satay.
4. **Ablation rehearsal.** Cumulative add and leave-one-out on Granite (fast) and one short Qwen pressure cell set; A+ reference with native `--moe-cache-mib` tuned as documented.
5. **Loop rehearsal.** Planner → CC → builder → lab client → evidence on JiuwenSwarm `fe88a206` + transport patch, including one revise/supersede step on the graph.

## ★ CCs on Satay
| ★ | CC | Reachable stage on Satay | Check |
|---|---|---|---|
| 1 | Runtime Event Recorder Builder | native CC execution + runtime acceptance (Granite, then Qwen) | coverage/loss/overhead; capture-off vs on exact parity |
| 2 | Expert Weight Cache Builder | compile + runtime acceptance + hardware measurement on Qwen | common-pin Fill patch already on Satay; exact output; vs A and A+ |
| 3 | Weight Placement Planner Builder | fixture + runtime acceptance (effective tensor assignment read back) | admitted placement under one byte budget; displacement accounted |
| 4 | Expert Demand Predictor Builder | native CC execution (offline replay on captured traces, held-out coverage) then smoke | bytes useful at consumption, wasted reads |
| 5 | Batch Layout Mapper Builder | runtime acceptance (single-slot lengths, cached prefixes) | exact output across lengths; layout vs ordinary batching |

## Method checks this run must retire
- Does the baseline read back from the loader equal the frozen file?
- Are cells reproducible enough (A/A spread) to say anything at all? On a 7.4 GiB box with swap, expect large variance. If so, the lesson (more repeats, longer warm-up, swap off, clock lock) transfers to the Spark.
- Does the quiet gate actually keep other work off the machine?
- Does the activation marker distinguish "CC code present" from "CC code ran"?
- Is every receipt traceable from the headline sentence?
- Does the CC create-or-modify behaviour (door-builder rule) work on an existing tree, and does it refuse to say done before verification passes?

## Limits
Satay uses unified memory and a different GPU, so a CC's win here can vanish or flip on the Spark. The Spark's own history already shows stock beating a custom path on decode. Treat Satay as a plumbing test.

## Status log
- **W1 done (stage: compile, plus hardware smoke):** stock `9048bad8` built for SM87, 33m40s at `-j4`, clean tree, `llama-server --version` ok. Receipt `~/predemo/receipts/stock-build.json`. Runs on the GPU when launched from a real session: Granite Q8_0 `llama-bench` pp128 1534 ± 603 t/s, tg16 67.5 ± 5.6 t/s (2 reps).
- **Lessons already (method, not performance):**
  1. The Codex worker sandbox has no `/dev/nvmap`, so workers can build and analyse but not run on the GPU. Timed runs go from a real shell. This is a design constraint for the Spark loop too.
  2. ccache needed a writable `CCACHE_TEMPDIR`; first build had 0% hits (cold). Later builds should be much faster.
  3. No passwordless sudo here, so clocks cannot be locked and caches cannot be dropped by a script. CPU idles at 730 MHz under `schedutil`, and GPU clock ramps; pp128 spread is ±39%. Fix for timed windows: either run `sudo jetson_clocks` yourself first (`! sudo jetson_clocks`), or include warm-up reps and report the spread. Power mode is MAXN_SUPER. Per-file cache eviction without root: `dd of=/dev/null iflag=nocache count=0 if=<file>`.
  4. `llama-cli` rejected `-no-cnv`; use `llama-server` plus HTTP for the real runs.
- **W2 done (stage: compile):** common-pin Fill patch applied cleanly to `9048bad8` (9 files, diff sha256 in `receipts/fill-applied.diff.sha256`), SM87 build 1,876 s, `cuobjdump` confirms sm_87, `--version` ok. Receipt `receipts/fill-build.json`.
- **Fill smoke on Granite (stage: runtime acceptance, functional only):** greedy 48 tokens, output identical to stock in two configs (`-ngl 0`: 691a04a9…, `-ngl 99 -cmoe`: c4f294a8…; tokens hash). Activation observed: `expert_fill: active threads=8 …` and stats line.
- **Surprises this smoke retired (all transfer to the Spark):**
  1. **Silent non-activation.** With `LLAMA_EXPERT_FILL=1` and default flags, the output matched stock but nothing ran: the Jetson's `-lm auto` resolved to `load_mode = none` (no mmap), and the patch needs mmap-backed tensors. At default log level the `inactive` message was not printed at all. Library `I` lines only show at `-lv 4`. **Rule:** activation checks must run with `-lv 4`, must read the effective `load_mode` from the log, and must pass only on an `active` line, never on absence of an error. Output parity alone can pass while the CC never ran.
  2. **Baseline readback must include `load_mode`.** The Spark's `auto` may also pick `none`; record it in the frozen baseline and compare to the model card's mmap/lazy-Engram expectation.
  3. **Activation is not effect.** On Granite everything is resident: `bytes_requested == bytes_skipped_resident`, `bytes_read = 0`. Fill can only show a mechanism under memory pressure, so the Qwen (22 GB) cell is where it can matter.
  4. **Never reuse tokens across configs:** `-ngl 0` and `-ngl 99 -cmoe` give different greedy tokens (different backends). Parity is only valid within one configuration.
  5. Own-goal checks: `pkill -f` matched my own ssh command line; use `pgrep -x`. Port numbers must be valid.
