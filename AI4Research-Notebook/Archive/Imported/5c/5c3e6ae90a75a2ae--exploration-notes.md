# Exploration notes: tasks sharing one GPU

Companion to the deck `2 Exploration notes - shared GPU.pptx`. Context file for later work on AI4Research workload profiling.

## What this is

Informal, preliminary hands-on testing. Purpose: get a feel for what kind of problem profiling is when LLMs, training, video encode and speech-to-text share one GPU, and what that implies for how the program should be built (scheduling, the planner, capsules, model routing). It is not a formal test report.

Strength of the numbers: directional. One machine (RTX 5070 Ti), 2 to 12 repeats per point, imported report not yet audited. No GB10 (DGX Spark) run. Every number needs a re-measure on the target hardware. The method carries over; the numbers do not.

Source data: `sources/2026-10-16-shared-gpu/report.md` and `chart-data.json` (tables B.1 to B.8, appendix A). Raw traces and the run ledger stay on the test machine.

## The central idea this feeds

Measure the impact of code on hardware already owned. Benchmark each capsule alone, in a container, in a quiet window, and store a resource vector with the capsule version. Link vector shape to speeds a cloud also exposes (tokens/s, first-token time, slowdown). Read cloud metrics through those links to infer what the cloud compute is doing, rank which resource saturates first, and derive hardware changes to test. Deck: `1 Central - owned hardware to cloud.pptx`.

Why the container level: GPU, CPU, PCIe and memory-system interactions are complex. The container is a clean boundary (cgroups give exact CPU, RAM and I/O per container even while sharing). Kernel and driver internals are left alone and observed through their effect (slowdown).

## Scope of the tests

| Set | What | Runs |
|---|---|---|
| X0 | idle floor | 6 |
| X1 | hardware calibration | 3 |
| X2 | LLM prefill vs decode, 4 model sizes (0.5B to 14B) | 21 |
| X3 | each task type alone (LLM, CNN training, speech-to-text, NVENC) | 8 |
| X4 | batching vs separate copies | 28 |
| X5 | every task pair | 32 |
| X6 | cold start | 6 |
| X7 | idle, A, B, A+B counter timelines | 28 |
| JIT | GPU-code cache | 8 |
| Start | container starts | 1,760 starts |

Total: 140 runs and 1,760 container starts. Repeats 2 to 12 per point. 4 model sizes, 4 task types, 13 pair cells.

## Findings

### 1. Tasks have distinct resource vectors (alone)

| Task | Memory read | Tensor cores | Compute units | GPU busy |
|---|---|---|---|---|
| LLM decode (7B) | 78% | 0% | 92% | 96% |
| LLM prefill (7B) | 14% | 18% | 59% | 63% |
| CNN training (fp32) | 30% | 13% | 65% | 69% |
| CNN training (mixed) | 19% | 13% | 60% | 64% |
| Speech-to-text | 1% | 1% | 3% | 3% |
| NVENC video encode | 1% | 0% | 0% | 0% |

Kernel shape separates tasks with similar busy: decode kernels median 2.5 us at 193k launches/s; prefill 6.8 us; training 77 us; speech 1.7 us; NVENC 4.5 us. Long training kernels hold the GPU while tiny decode kernels wait for a turn. Time-based GPU utilization (what CloudWatch and DCGM utilization show) reads high for memory-bound decode while tensor cores idle.

### 2. Decode hits the memory-bandwidth wall at 7B

| Model | Memory read (GB/s) | Decode tok/s |
|---|---|---|
| 0.5B | 294 | 738 |
| 3B | 545 | 283 |
| 7B | 737 | 157 |
| 14B | 723 | 80 |

Ceilings measured on the test GPU: 850 GB/s matrix-vector, 770 GB/s copy. PCIe pinned about 28.7 GB/s, pageable 10 to 17 GB/s. The GB10 is listed at 273 GB/s shared with the CPU, about a third; bigger local models would decode more slowly there. Memory read per token = GB/s divided by tok/s (7B: 737 / 157 = 4.7 GB). Prefill is compute-bound and decode is memory-bound.

Partial offload cliff (7B): 156.7 tok/s with 28 of 28 layers on the GPU, 22.2 at 20 of 28, 12.6 at 12, 8.8 at 4, 7.1 at 0. The PCIe copy dominates once layers move to the CPU.

### 3. Interaction: who slows whom

Slowdown of the row task beside the column task (1.00 = unchanged):

| Row \ beside | LLM decode | CNN training | Speech-to-text | NVENC |
|---|---|---|---|---|
| LLM decode | x2.27 | x2.08 | x1.02 | x1.12 |
| CNN training | x1.16 | n/a | x1.00 | x1.06 |
| Speech-to-text | x1.03 | x0.98 | n/a | x1.02 |
| NVENC | x1.08 | x1.08 | x1.05 | n/a |

Means: LLM suffers x1.62 and causes x1.09; training suffers x1.07 and causes x1.38; speech x1.01 / x1.02; NVENC x1.07 / x1.07. Repeats: 2 per pair, 8 for LLM beside LLM; LLM beside training ranged x1.7 to x2.4 over two runs. Rule: memory-bound LLM decode is the victim, long-kernel training is the aggressor, speech and NVENC are near-free neighbours.

### 4. Four LLM processes make less than one

4 processes: 258 tok/s total vs 284 for one (91%). Each stream gets 22 to 26% of solo speed. Per token: 3.5 ms alone vs 15.8 ms with three others. The GPU switches between processes and loses time at each switch; it does not split 25% each. The trace span reads 37% because it includes time switched out.

### 5. Copies lose to batching

4 separate processes: 258 tok/s, 8.9 GiB. 4 requests batched in one process: 614 tok/s, 2.5 GiB. One request alone: 284 separate, 274 batched. Batch of 8: 1,417 tok/s (n=2, recheck). Each separate process holds its own weights; a batch reads the weights once for every request.

### 6. Blend of solo vectors predicts shared usage

Time-split blend: device = floor + sum over processes of (solo - floor) x time share / solo busy. Mean error over 15 pair-counter cells: 4.0 pp for the blend vs 16.0 pp for the plain sum; better in 12 of 15 cells. Per pair, blend vs sum: LLM+training 2.8 vs 21.8; LLM+LLM 8.4 vs 22.5; LLM+NVENC 1.0 vs 3.7. Per counter (blend vs sum): SMs active 9.2 vs 16.1; SM issue 3.8 vs 24.0; tensor 0.3 vs 1.2; DRAM read 6.7 vs 36.7; DRAM write 0.2 vs 1.9. Time shares came from the co-run per-process trace; predicting shares before launch is the open step. Switching loss (blend minus measured, DRAM read): 9% LLM+training, 2% LLM+NVENC, 22% LLM+LLM. Validated on 3 pairs.

### 7. Startup and residency dominate small tasks

- First token of a 7B model: 6.14 s from disk, 2.7 s from RAM, 0.049 s resident.
- JIT cache: 64.4 s without a shared cache, 5.3 s with.
- Container start: 3 ms native, 49 ms warm exec, 219 ms with GPU (+216 ms). a 9.3 GB image leaves the median unchanged (153 ms).
- Bursts: 1 start 152 ms, 4 at once 191, 8 at once 263, 16 at once 423 (2.8x).
- Speech-to-text (Whisper turbo): 13.5 to 21.6 s for 10 to 100 s clips, GPU busy 3%. Subtitle burn-in is CPU-bound: 36 CPU-s for a 10 s clip up to 330 CPU-s for 100 s, so a resident speech worker removes most of the node time and GPU encoding frees the CPU.

### 8. What stays visible per process on a busy GPU

Container (cgroup v2): CPU time, RAM peak, I/O, out-of-memory events; exact even while sharing. Process (CUPTI / Nsight Systems): kernel sequence, GPU memory per process, time share; visible while sharing. Device counters (SM, tensor, DRAM, PCIe): whole GPU, equal one task only when it ran alone; one counter session at a time. Profiling raises idle power from 17 W to 27 W. Identical runs launch identical kernel sequences (353,970 kernels in one task), so stored vectors stay comparable.

## What it means for the program

### Scheduling the DAG and the planner (key point)

Some branches parallelise easily and some only look parallel. A fan-out of k nodes gives a k-fold speedup only if the nodes use different resources.

| Parallel branch | Measured | Effect on the schedule |
|---|---|---|
| LLM call beside another LLM, different model | x2.27 each; four together 258 vs 284 tok/s | No wall-time gain; parallel costs about the same as serial, with four weight copies in memory |
| LLM calls to the same model | batched 614 tok/s at 2.5 GiB vs 258 at 8.9 GiB | Parallelises well through one batching server |
| LLM call beside training or an experiment | LLM x2.08, training x1.16 | A critical-path LLM node can double in duration; the experiment node barely moves |
| LLM call beside speech or video encode | x1.00 to x1.12 | Close to free parallelism |
| Many container starts at once | 16 at once 423 ms vs 152 ms | Fan-out startup is not free; warm containers cut it |

Planner inputs this suggests: a resource class per node, node duration under sharing (solo duration x pair factor), and a memory budget for model copies. Parallel width is a resource decision, not just a graph property. Design-package context: parallel nodes are outside M1 (planner.md:216); Cluster Mode is in M1 (D33), so the planner effect arrives once parallel nodes exist.

### Measurement

Record several dimensions plus kernel size and rate; separate startup, cold and steady phases; measure both directions of every pair; count memory per copy.

### Capsules

Declare resource dimensions in the declaration (the declaration has `gpu_device` exclusive and `wall_s` but no memory field today); the measured vector is stored with the version (`declaration_sha256` keys it) and refreshed when the version, image or driver changes. The profiling run is a host-side tool needing privileges (quiet GPU, Nsight, DCGM, SYS_ADMIN); the simulator (vectors and shares in, predicted usage out) is a pure tool capsule whose output is an assessment. Constraints: owner ruling 9 (owner-rulings.md:123) forbids continuous CPU/GPU sampling in run capture; sidecar/README.md:107 excludes profiling integration and product telemetry.

### Model routing and runtime

Keep models resident (125x first-token gain), share the GPU-code cache (12x), keep warm containers for short tasks (4.5x), batch instead of cloning model copies (3.5x less memory, 2.4x throughput). Hypothesis: few resident models with batched requests. Model quality for routing is not measured.

### Local models on the DGX Spark

Decode is memory-bandwidth-bound, weights share one pool with experiments, and two heavy jobs slow each other. Device-level dashboards on the GB10 are blind to per-process memory bandwidth (nvidia-smi shows Memory-Usage Not Supported on DGX Spark).

## Reading cloud data through these results

| Cloud observable | Rule | Inferred pressure |
|---|---|---|
| decode tok/s per stream | bytes per token = GB/s / tok/s; wall at 7B | memory bandwidth |
| time to first token | 6.14 s disk, 2.7 s RAM, 0.049 s resident | model load path, cache misses |
| per-stream tok/s vs solo | 22 to 26% with 4 LLMs; x2.08 beside training | time-slicing and switching loss |
| aggregate tok/s, memory per replica | batched 614 at 2.5 GiB vs 258 at 8.9 GiB | memory capacity used by copies |
| GPU utilization (time-based) | decode 96% busy with 0% tensor | high utilization can mean memory-bound |

Candidate bottleneck order (hypothesis from one machine): memory bandwidth, memory capacity, sharing and switching loss, load path (storage to GPU), launch and startup. Candidate hardware changes: more bandwidth per accelerator; larger or pooled memory and a faster CPU-GPU tier; finer-grain preemption or partitioning; faster storage-to-GPU path; lower launch and context cost. Cloud data decides the real order.

## Precedent

MuxFlow (arXiv 2303.13803, "CompanyX", not ByteDance): MPS space-sharing of online and offline jobs; xCUDA caps offline memory and kernel launches; SysMonitor evicts offline jobs. A solo profile feeds an MLP per GPU type that predicts shared speed; Kuhn-Munkres matching picks pairs. Production: 26% to 76% GPU utilization (sharing plus protection; the predictor results were not ready). Testbed of 1,000 T4 GPUs: 4.0x utilization. Inference, not agents. Other platforms: NVIDIA time-slicing (no memory isolation), MIG (static hardware partitions), Alibaba cGPU (per-container quota).

## Not tested / open

- Video decode (NVDEC), prefill beside other tasks, more than four tasks, multi-GPU, MPS and MIG.
- Any GB10 run; behaviour of real AI4Research capsules.
- Predicting time shares before launch (shares came from co-run traces); blend validated on 3 pairs.
- Cloud data not yet collected; the cloud-inference rules are untested against it.
- Planner effect of non-parallel-friendly branches is argued from pair results, not simulated end to end.
- Numbers n=2 to 12 on one machine, unaudited.

## Where things are

- Decks (Desktop): `1 Central - owned hardware to cloud.pptx`, `2 Exploration notes - shared GPU.pptx`.
- Build folder: `jiuwenswarm/docs/research/resource-aware-planning/presentation/deck-tundlekit/` (`split_decks.py`, `split_central.py`, figure scripts `figs1*.py`, `figures/`).
- Data: `jiuwenswarm/docs/research/resource-aware-planning/sources/2026-10-16-shared-gpu/`.
- Older full 42-slide deck: `build_spec.py` / `deck.json` in the build folder.
