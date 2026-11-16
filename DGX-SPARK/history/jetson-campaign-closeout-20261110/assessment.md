# What Jetson adds to the x86 findings

Evidence basis: original handoff plus committed campaign at `73484492c67cbf5b38d2cd8522f7f780975907aa`. Read [preservation and audit limits](README.md). Numerical results below are local to Orin Nano sm_87 with its own GGUF hashes. No new hardware experiment ran here.

## A stronger component demonstration candidate

The per-type dispatch patch has a larger observed effect than x86 Q8 activation reuse and a useful negative control:

| J-E007 engine setting | Recomputed change | Meaning |
|---|---|---|
| BF16 gate/up unfusion | +19.21% | Existing dispatch chooses a different kernel path. Earlier BF16 checks show numerical differences; do not call this computation-preserving bit identity. |
| Q4_K-expert mixE4K gate/up unfusion | +23.64% | Same model representation; matching retained greedy text and printed quality summaries. This is stronger than a synthetic microbenchmark, but remains bounded output evidence. |
| Q8_0 gate/up unfusion | −6.21% | Explicit counterexample: the component must not auto-enable for all precisions. |

Source: [component README](snapshot/campaign/cc/moe_dispatch_sm87/README.md), [patch 03](snapshot/campaign/cc/moe_dispatch_sm87/patches/03-unfuse-ids-by-type.patch), [raw benchmark directory](snapshot/campaign/experiments/jetson/J-E007-unfuse-by-type), [audit](record-audit.json). Two invocations per arm, five in-process samples each; clocks were not pinned, and the first sample was discarded under the stated warm-up rule. These are encouraging local measurements, not a general performance distribution or sm_120 qualification.

**Critical mechanism:** the change is at graph fusion. Fewer kernels are not automatically faster: separating gate/up/GLU lets the normal dispatcher choose better work on this platform. The standalone backend-op kernel screen did not reproduce the full-engine effect. This independently reinforces the x86 lesson that a passing isolated operation may miss the changed path entirely.

## Memory and storage findings change the tool requirements

- **Cache hit rate is not the objective.** Upstream expert cache reportedly achieved about 64% hits yet slowed the over-memory workload by 17–23% on UMA. x86 caching helped its discrete-GPU workload. Different Qwen variants, pins, weights, CPUs and storage prevent a controlled one-factor cross-host conclusion. Record applicability instead of declaring cache universally good or UMA universally incompatible.
- **Fewer IO bytes can be worse.** Whole-file random advice cut bytes but roughly halved speed. Router-informed prefetch reportedly cut bytes about 57% and slowed decode around 38%. Small 4–5 KiB reads and near-zero lead time lost the large-read advantage. A failed current prefetch implementation does not establish that all aligned asynchronous loaders fail.
- **Local storage is part of the system description.** The drive's fio matrix reports roughly 570 MiB/s large-read throughput and much lower small-random throughput. Record IO size/count/queueing and cache state, not only total bytes. Device-global counters do not establish which process caused each read when work overlaps.
- **Memory guarantees need explicit domains.** CUDA device allocations reportedly escaped a host-memory cgroup limit. Jetson shares DRAM; device-total “VRAM” strings and NVML [N/A] must not become a separate 8 GB pool or a measured zero. Available-memory auto-fit picked an enormous context in one test. Request must pin context and state which memory limits are enforced versus observed.
- **Watchdog intent is not confirmed termination.** One result said watchdog_killed with exit zero because a quoted kill command was broken. Zram swap-rate thresholds also caused false positives. Preserve trigger, kill request, observed process exit/OOM and confirmed cleanup as separate observations; thresholds are host policy, not universal constants.

## Workload-specific reuse can beat a new loader

SPEC2 uses upstream n-gram self-speculation on copy-heavy prompts. Saved request records reproduce +63.14% rewrite and +96.81% repeat. This is a runtime decoding strategy, not a new engine-code component or loader. A natural-text replay predicted no comparable IO deduplication benefit; that is a simulation, not contradictory live evidence. Copy-heavy requests have different draft acceptance. The chat prompt produced one token and is invalid, so no general conversational gain is established.

## Engineering lessons that save implementation effort

1. The Jetson branch already extends the Build CC with `--target jetson-orin`, native sm_87/arm64 settings and ccache normalization. Our earlier “builder is amd64-only” applies to the **x86 snapshot**, not this version. Inspect/diff these branches before reimplementing target support; do not merge either branch wholesale.
2. Random staging paths initially destroyed cache reuse. After normalization, a rebuild was about 141 seconds versus 3,154 seconds for the first native build. Warm x86 timing does not predict Jetson build timing. Embedded paths still changed binaries; bit-reproducibility was not achieved. Binary hashes still identify actual outputs even when builds differ—retain them rather than following the closeout's overbroad “never binary hash” wording.
3. `sg docker -c`, explicit NVIDIA runtime/device environment, model conversion venv, and stale RUNPATHs are real portability requirements. Build identity includes platform/runtime/toolchain and actual app/library hashes. A local RepoDigest does not prove remote pullability.
4. Eleven attempts failed on tool-specific flags. The same inference engine ships several CLIs with different options. A preflight/effective-configuration tool is justified; do not maintain one universal llama.cpp flag list.
5. `pgrep -f` self-matching stalled a pipeline for about 8.7 hours. Manager needs explicit job completion/dependency observations rather than string-matched process polling. PID-only polling is better but still needs process-generation identity and persisted completion state across restarts.

## Evidence and authority cautions

- Decision numbers collide across hosts. Use `(campaign, lane, decision_id)` or stable namespaced IDs, never join on `D027` alone.
- Both original ZIP documents match the final committed snapshot. Several source paragraphs predate final results; latest scoped addenda supersede them.
- 376 lab-output files referenced by saved results are absent from the Git snapshot. The statement that all raw logs were committed is not sufficient proof of portable evidence completeness. Do not silently substitute x86 files at the same paths.
- Model file hashes differ across hosts. A tensor manifest can distinguish metadata from tensor-payload differences, but identical weights alone would not establish identical tokenizer/templates/runtime semantics. `llama-bench` even labels mixE4K as Q8_0 in a summary field; inspect the actual tensor representation.
- The closeout tables disagree on archive sizes (a generic 3.7 GB entry versus about 1.39 GB elsewhere). Read per-build record sizes and verify actual bytes at transfer; do not provision from narrative estimates.
- Host-loss protection is still absent. Reported sandbox/reconciler tests do not establish whole-host survival or complete streaming trace recovery.

The strongest next scientific question is whether the per-type graph-fusion decision transfers to sm_120—not whether it can be declared portable from the source. First preserve exact graph/workload/precision identities and define acceptance, then run the target's own A/A and matched A/B.
