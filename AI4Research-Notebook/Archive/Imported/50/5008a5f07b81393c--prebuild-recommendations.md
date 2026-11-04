---
title: "Before AI4Research: workload-profiling recommendations"
date: 2026-10-19
status: literature-based-experiment-plan
tags: [prebuild, experiments, recommendations, gpu]
---

# Before AI4Research: what to measure next

## Today's value and scope

AI4Research is not built yet. Today's work is literature research and experiment planning with standalone workloads. The deliverable is a recommendation about what data and tests we need, which existing experiment families to refine, and which approaches to avoid. No AI4Research integration, new profiling runs, predictor build or chip-design recommendation is claimed here.

The eventual task-history predictor and chip simulator explain why these measurements matter. They are future consumers of the evidence, not prerequisites for today's work. The earlier Claude artifact is excluded as scientific evidence. Existing experiment families below come from the prior discussion; their raw records have not been audited here and their reported numbers are not used to justify recommendations.

Hardware-specific collection assumptions and the GB10 overnight campaign are now captured separately in [GB10 workload profiling plan](gb10-profiling-plan.md). In particular, “CUDA-core utilization” means supported SM/pipeline/kernel metrics, not a literal per-core percentage; cross-machine comparisons are not controlled UMA experiments.

## Recommended order

**P0 — Audit the evidence before adding combinations.** Obtain workload commands and input hashes, actual backend/engine, device and software versions, process/context/stream identities, measurement settings, repetitions, and raw timing/counter exports. Establish whether full traces exist, whether collection preserved concurrency, and whether existing comparisons used matching conditions. Reanalyse existing records before rerunning anything.

**P1 — Resolve mechanisms with a few controlled contrasts.** Focus on profiler effects, batching versus process sharing, phase/input dependence, and solo demand versus contention sensitivity. Keep startup and loading outside the steady-state comparison. Each new run should answer a stated question and change a collection or modeling decision.

**P2 — Fill missing workload diversity.** Add a small representative kernel or task only when current examples leave a resource behavior untested. Candidate gaps include cache/locality-sensitive work, irregular memory access, launch-heavy small kernels, or CPU/GPU shared-memory traffic. Add a second hardware class only when available and needed to test a specific transfer assumption. Do not purchase hardware based on this review alone.

## Questions, provisional answers and discriminating tests

| Question | What literature lets us say now | Recommended evidence and resulting decision |
|---|---|---|
| Is the profiler changing the behavior we want to measure? | Detailed kernel counters can require replay and serialization. Range modes can preserve supported concurrent workloads, but aggregate results have different attribution limits. [NVIDIA profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html). | Compare profiler-off timing, lightweight timeline capture, and selective detailed collection on the same condition. If overlap or timing changes materially, keep production timing and diagnostic counter passes separate. Set the tolerance before comparison. |
| Are process-copy losses caused by scheduling, duplicated state, or batching differences? | MPS changes process sharing; batching also changes kernel shapes and amortization. Neither is a neutral process-count change. [MPS documentation](https://docs.nvidia.com/deploy/mps/latest/index.html). | Hold total requests, model, precision and input mix fixed. Compare separate processes, one batching server, and separate processes with MPS if supported. Report throughput, per-request tail latency, memory and overlap. Decide which execution-mode features belong in future records. |
| Can solo utilization identify which co-runner will hurt a task? | Solo demand and sensitivity to shared resources are different. Interference involves block placement, pipelines, caches and memory paths. [SoCC 2025 study](https://anakli.inf.ethz.ch/papers/gpu_interference_socc25.pdf). | Keep A-alone and B-alone, then measure both jobs in A+B. Add one resource-targeted stressor for an ambiguous case. Decide whether a resource-sensitivity field adds information beyond solo demand. A stressor supports a mechanism hypothesis, not unique causal proof. |
| Does low DRAM bandwidth rule out a memory bottleneck? | No. Latency, locality, limited concurrent requests and other memory paths can constrain execution below peak DRAM bandwidth. [NVIDIA triage guide](https://docs.nvidia.com/nsight-compute/ComputeTriage/index.html). | Inspect representative cache/latency/issue signals and change working-set size or access pattern while keeping useful work comparable. Decide whether a simple compute-versus-bandwidth label is sufficient; keep other explanations open. |
| Is task identity enough to reuse a historical profile? | Input shape, batch, software and phases affect behavior. Per-kernel profiling is useful in sharing research. [Orion](https://anakli.inf.ethz.ch/papers/orion_eurosys24.pdf). | Split prefill/decode or equivalent phases and test a small/large input contrast. Decide the minimum phase and input descriptors before collecting a larger corpus. Preserve absolute work/traffic as well as normalized utilization. |
| Is a long speech/video run evidence of GPU demand? | CPU stages and dedicated video engines can dominate different paths. NVENC and NVDEC are separate capabilities. [NVENC guide](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.0/nvenc-video-encoder-api-prog-guide/index.html), [NVDEC guide](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.0/nvdec-video-decoder-api-prog-guide/index.html). | Verify backend logs and timeline. For one case, separate preprocessing, accelerator work and postprocessing; test encode-only and decode-only before a transcode, and identify software fallback. Decide which CPU/engine/transfer observations are necessary. |
| Does a warm/cold comparison tell us about steady-state contention? | It answers a different question: readiness and initialization cost. | For the same implementation, separate process/container launch, context/JIT setup, loading, first result and subsequent service. Control OS page cache and model residency where feasible. Decide which state fields must accompany timing. Reuse existing launches if adequately instrumented. |
| Can one device establish prediction on future chips? | No. Cross-device forecasting and detailed simulation have explicit input and support assumptions. [NeuSight](https://github.com/scai-tech/NeuSight), [Accel-Sim](https://accel-sim.github.io/). | First check trace/model compatibility and reproduce one supported baseline. Test another device only for a named transfer hypothesis. Defer architecture sweeps until calibration is credible. |

## Revisions to the existing experiment families

| Existing family | Keep | Revise or expand | Avoid |
|---|---|---|---|
| Solo and pair runs | Matching solo baselines and per-task completion/throughput | Both-sided slowdown, phase alignment, explicit sharing mode, one targeted co-runner for ambiguous mechanisms | Universal time-sharing rules or a single symmetric interference score |
| Separate copies versus batching | Fixed-work comparisons and memory accounting | Match request mix; measure queueing and tail latency; distinguish independent processes, batching and supported MPS | Declaring batching universally best from aggregate throughput |
| Container/model cold and warm starts | First-result and readiness measurements | Separate cache/JIT/loading/process state and steady-state service | More broad launch sweeps without an unresolved decision |
| Speech and video tasks | End-to-end timing and CPU accounting | Backend verification, encode/decode separation, transfer/engine visibility, a persistent-worker contrast where justified | Treating the task label as proof of CUDA or GPU use |

## Things we need

- An immutable run manifest and raw exports, including failed, timed-out and out-of-memory runs.
- Separate workload descriptors, hardware/state conditions and measured targets, with feature-availability timestamps.
- Phase-level timing, selected interpretable counters, units, observation scope, and missing-value markers.
- Matching baselines, randomized or alternating condition order, sufficient repeats for the intended conclusion, and visible uncertainty.
- A question, controlled contrast, analysis rule and stopping condition for every proposed expansion.
- A small coverage map showing which resource behaviors the current workload set exercises and which remain missing.

## Things to avoid

- Starting AI4Research integration or collecting a huge vector dataset before validating the records and labels.
- Using semantic task similarity, GPU-busy percentage or memory allocation alone as a hardware-pressure model.
- Treating reduced device counters during co-running as an identified context-switch penalty. Demand changes, scheduling, clocks, cache effects and attribution can also affect the comparison.
- Using full-run target counters to claim a prediction made before execution, or placing duplicate runs in both training and test sets.
- Conflating operational cold startup with the separate ML problem of an unfamiliar task with no historical neighbor.
- Treating unified memory as one uniform platform, assuming media-engine availability, or transferring a profile between devices without checking.
- Expanding every model/batch/process/backend combination or profiling every counter on every run.
- Recommending more bandwidth, cache or compute for a chip before demonstrating sensitivity with a supported and validated model or experiment.

## Today's output and the next handoff

Today we can deliver this prioritized question-and-test list and the revised presentation. The experiment owner can then map each question to existing raw records, mark it answered/partly answered/missing, and run only the smallest unresolved contrasts. Each resulting recommendation should state: **what we need or should avoid; the evidence; the applicable conditions; and what would change the recommendation**.

Luna research notes: [contention questions](literature/prebuild-contention-questions.md) and [prediction preparation](literature/prebuild-prediction-questions.md). These are literature-based recommendations, not new experimental findings.
