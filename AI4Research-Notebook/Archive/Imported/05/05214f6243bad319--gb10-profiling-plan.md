---
title: "GB10 workload profiling: experiment and data plan"
date: 2026-10-19
status: exploratory, source-backed recommendation
tags: [GB10, NVIDIA, Linux, profiling, OCI, cgroups, AI4Research]
---

# GB10 workload profiling: start at the GPU, join upward

## The decision this work should enable

Build evidence that lets a future AI4Research planner answer: **for this capability implementation, input and phase, on this machine and runtime, which GPU pipelines and memory paths are demanded, and what limits completion or concurrent work?** Keep the chip-design question downstream: which representative workloads actually benefit from more compute, Tensor throughput, cache, memory bandwidth/capacity, copy or codec engines, and how confidently?

Do not treat “CUDA-core utilization” as a literal per-core gauge or one percentage. CUDA cores are execution lanes inside SMs. NVIDIA’s tools expose counters and derived metrics at SM, sub-pipeline, cache, memory and kernel levels. A useful first set is SM active/issue activity, FP and Tensor-pipeline activity, occupancy and warp stalls, L1/TEX and L2 traffic/hit behavior where supported, DRAM activity/bytes/bandwidth, kernel duration, and copy/codec activity when relevant. Query metrics on the actual GB10 and use only supported signals. High activity means work occurred; a bottleneck claim also needs a performance response to a controlled change.

## What the two machines let us learn

| System | Useful role | Do not assume |
|---|---|---|
| GB10, Grace Blackwell, Linux aarch64, 128 GB shared LPDDR5x UMA | Primary target. Observe integrated CPU/GPU work, shared-memory pressure and GB10 Blackwell execution. DGX Spark documentation describes 20 Arm cores, 128 GB UMA, 273 GB/s, 6,144 CUDA cores, two copy engines, NVENC and NVDEC; confirm the exact board/firmware/software on our unit. | 128 GB is not GPU-exclusive capacity. CPU, GPU and OS share system DRAM. `nvidia-smi` may report framebuffer memory as unsupported on iGPU/UMA; NVIDIA also warns `cudaMemGetInfo` can understate allocatable memory when OS reclaim and swap are possible. |
| Ryzen 7 3700X, Linux x86-64, RTX 5070 Ti, 16 GB GDDR7 discrete GPU | Existing comparison point. It shares the Blackwell GPU generation with GB10 but has a separate GPU, GDDR7 VRAM, PCIe path, different CPU ISA/microarchitecture, GPU size, clocks, bandwidth and memory capacity. | A cross-machine difference cannot be attributed to UMA alone. It is an external-validity contrast across complete systems. Use controlled within-machine changes to isolate a mechanism; then compare the two systems as operating points. |

The NVIDIA GB10 platform guide documents UMA and its bandwidth, while NVIDIA lists RTX 5070 Ti as Blackwell with 16 GB GDDR7. These are usefully related systems, not matched twins. Record exact SKU, GPU UUID, compute capability, CPU/core layout, OS/kernel, driver, CUDA/runtime, clocks, container runtime and memory state at every campaign and run. Sources: [DGX Spark hardware](https://docs.nvidia.com/dgx/dgx-spark/hardware.html), [DGX Spark known issues and UMA memory reporting](https://docs.nvidia.com/dgx/dgx-spark/known-issues.html), [RTX 5070 family specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070-family/).

## Start with the supported measurement ladder

1. **Kernel-level GPU explanation:** Nsight Compute on GB10. Collect a small, question-selected set of per-kernel metrics: SM/pipe throughput, FP versus Tensor work, occupancy/register/shared-memory limits, relevant stalls, cache and DRAM traffic/bandwidth, kernel time. Query the installed tool’s supported metrics for the exact GPU before freezing a collector. Nsight Compute currently lists GB10x support; that does not guarantee every metric or mode on every system image. Detailed profiling/replay can perturb execution, so keep timing-only runs separate and measure collection overhead. [GPU support](https://docs.nvidia.com/nsight-compute/ReleaseNotes/topics/gpu-support.html), [metric interpretation](https://docs.nvidia.com/nsight-compute/ComputeTriage/).
2. **Whole-run timeline:** Nsight Systems for CPU threads, CUDA API/queues, kernels, synchronization, copies and overlap. Mark application phases with NVTX if available; otherwise record wrapper events with monotonic timestamps and correlate process and GPU timelines. Use this to explain launch gaps and pipeline ordering. [DGX Spark Nsight overview](https://docs.nvidia.com/dgx/dgx-spark/nsight.html).
3. **Broad device interval signals:** first test `dcgmi discovery` and `dcgmi profile --list` on the actual host. DCGM can expose SM, Tensor-pipe, DRAM and link activity as interval averages; it does not identify a kernel/instruction and its profiling counters conflict with Nsight counter sessions. DCGM profiling support is documented for datacenter products, so treat availability on this GB10 system as a preflight question, not a given. [DCGM profiling and platform limits](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html).
4. **Possible GPU process/job accounting:** if DCGM process/job statistics are supported and retained, associate a PID or explicit scheduler job window with GPU summaries. NVIDIA documents per-PID and caller-defined job reports, but warns they are sampled, limited to supported retained fields and not a replacement for cgroup or application accounting. Probe this on GB10 before relying on it. [DCGM process/job statistics](https://docs.nvidia.com/datacenter/dcgm/latest/learn/core-services/process-and-job-statistics.html).
5. **Linux attribution:** on cgroup v2, retain the capsule container’s cgroup path and sample `cpu.stat`, `memory.current`, `memory.peak` where available, `memory.stat`, `memory.events`, `memory.swap.current`, `io.stat`, `pids.current`, and `cpu.pressure`, `memory.pressure`, `io.pressure`. Use `/proc`/process-tree data for thread and PID identity; use `perf stat` selectively for CPU counters with permissions/events recorded. Cgroups account and constrain host resources, but do not turn a device-wide GPU counter into per-container SM attribution. [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [Linux PSI](https://docs.kernel.org/accounting/psi.html), [Docker stats/API](https://docs.docker.com/reference/cli/docker/container/stats/).

Use `nvidia-smi`/NVML for inventory, process presence, power, clocks, temperatures, utilization, links and basic state—not as the CUDA-core profiler. On the GB10 UMA system, use kernel/cgroup/OS memory evidence and CUDA allocation context; do not treat the familiar dedicated-framebuffer “used/total” number as a common field across both hosts.

## Packaging and joining the data

**Recommendation: make a pinned OCI container image the normal executable package for a tool-style Capability Capsule (CC).** The CC declaration remains the contract: identity, inputs/outputs, permissions and invocation rules. Its executable body resolves to an immutable OCI image digest plus entrypoint/config. This matches the work CCs already do—package reusable AI/model/tool execution with its runtime dependencies—and gives profiling a stable unit to launch, track and repeat. It also fits physical-AI simulation and other GPU-heavy capabilities. Treat agent-style CCs separately where they are bounded instructions calling a model bridge; an image can package their local helper process, while model access and authority stay governed by their existing host path.

This is a proposed packaging direction for future AI4Research work, not a current architecture fact. The assumption that most AI4Research GPU demand will come from work capsules is plausible because model execution, inference, training and simulation naturally sit there; measure actual task mix before treating that as established. A small deterministic planner graph can be inexpensive, while its model calls or delegated capsules may still dominate. Profile phases before assigning the cost to the graph itself.

Record capsule ID/version/declaration and code hash; OCI index digest plus the selected `linux/arm64` or `linux/amd64` child-manifest digest; input/data hashes; interface mode (`stdio` or HTTP); and actual command/config. OCI indexes support different platform manifests under one multi-platform reference, but an ARM64 image and x86-64 image are distinct executable environments and must be recorded separately. Build and validate images outside the scarce GPU measurement window; pre-pull them on the GB10 where possible. Keep build digest, selected platform digest and host runtime/driver in the run record. [OCI image specification](https://specs.opencontainers.org/image-spec/), [OCI image index](https://specs.opencontainers.org/image-spec/image-index/), [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/).

The NVIDIA Container Toolkit supplies GPU device/library access to a container through the host stack. It does not package the host kernel, GPU, clocks, driver or memory topology into the image. Docker `--gpus` and NVIDIA’s runtime expose devices to the container; that provides a useful process/cgroup boundary for CPU and host-memory records, while GPU counters often remain device-wide. Container boundaries alone do not grant exclusive GPU execution or per-container CUDA-core attribution. Pin the image digest and record host driver/runtime compatibility. [Docker GPU access](https://docs.docker.com/engine/containers/gpu/), [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/overview.html), [DGX Spark Docker GPU runtime](https://docs.nvidia.com/dgx/dgx-spark/nvidia-container-runtime-for-docker.html).

Recommended join chain:

```text
campaign_id
  └─ run_id + capsule_ref + code_hash + OCI child digest + input_hash
       └─ container_id + cgroup_path + host PID tree + GPU UUID/context
            └─ monotonic phase events ↔ Nsight Systems timeline ↔ Nsight Compute kernel records
                 └─ machine/software/memory-state manifest + outcome + raw evidence hashes
```

Stdio and HTTP remain capsule interfaces. The runner records request/response boundaries, status/exit code, output hash and phase timestamps; it does not change capsule semantics to expose a profiler API. Add optional NVTX phase ranges only when the implementation can safely provide them. Keep workload descriptors available before launch separate from measured outcomes: never call a post-run counter vector a prediction input.

## A small, useful GB10 campaign

### Phase A — validate the sensor and runtime path

Run a short, known-good smoke capsule in a pinned `linux/arm64` image with `--gpus all`; verify architecture, image child digest, GPU visibility, expected CUDA runtime, child-process tracking, cgroup files, output correctness and log/timestamp joins. Confirm that DCGM discovery and Nsight tools see the GB10; list available NCU metrics. Capture a no-work idle baseline and a simple workload before building the campaign. A counter that is missing, unsupported, blank or globally scoped is marked as such—not zero.

### Phase B — calibrate mechanisms, not the whole combinatorial space

Use the smallest representative set that spans materially different resource patterns: (a) FP/SIMT compute, (b) Tensor-heavy matrix work, (c) streaming DRAM traffic, (d) cache/reuse or irregular-latency work, (e) launch/CPU-bound tiny work, and (f) copy or codec work only if real capsules invoke it. Prefer existing capsule/benchmark implementations. A small synthetic kernel may validate a counter, but it is calibration, not evidence of the project task mix.

For each case compare unprofiled timing-only execution against timeline capture, then a separate selective NCU pass. Measure warm-up/initialization separately from steady state. Vary one workload feature at a time (e.g. working-set size, precision or batch) only where it discriminates a hypothesis. Check whether stronger resource demand changes achieved latency/throughput; utilization alone is not a recommendation.

### Phase C — two-machine transfer check

Replay a few identical input/interface cases on GB10 and RTX 5070 Ti, resolving each platform’s OCI child image. Compare phase timing, pipeline mix, bytes/bandwidth, cache/stall evidence and outcomes in native units plus carefully normalized device-specific measures. State clearly that this checks whether a useful profile transfers across two system configurations; it does not estimate the isolated causal effect of unified memory. To study UMA itself, compare explicit shared-memory access and copy/staging strategies on GB10 while holding code and useful work constant, and compare an analogous transfer contrast on the discrete system.

### Phase D — only then test sharing sensitivity

Keep the existing solo/pair question, but first establish reliable solo profiles. Then choose a small, evidence-driven pair: same pipeline, shared memory path, or a distinct engine. Record both jobs’ completion/latency and the device-wide counter timeline. A quiet host is essential: device-wide measurements can only be associated to the sole scheduled capsule when background activity is checked before, during and after the interval. Do not subtract one noisy global average and call it per-container utilization.

Set repeat counts from pilot variance and the smallest effect that would change a recommendation. Alternate case order or bracket the campaign with a control run to detect thermal/clock drift. Preserve all failures and OOM runs; specify a stop rule, max duration, max host-memory use, disk budget and maximum GPU temperature/power state. Overnight runs should halt safely on failed preflight or another GPU process, not start concurrently or kill existing work.

## Runner shape: authorized queue, small quiet window

The repository already describes an off-hot-path finite-job benchmark sidecar and an optional privileged host launcher. It already uses pinned image digests, job IDs, resource budgets, GPU-exclusive windows, evidence retention and cleanup of job-owned resources. That is a strong architectural precedent for a later profiling campaign. **It does not currently authorize this research profiler:** the maintained design explicitly says the sidecar benchmark pilot is separate from the product gate, excludes capsules from sidecar tools/credentials, and adds no profiling integration/new product telemetry. A GB10 profiler pilot therefore stays an independent research operation until a future owner approves a specific design change. See [sidecar design](../../architecture/design-package/development-tools/sidecar/README.md), [decision D36](../../architecture/design-package/method/decisions.md#d36), and [decision D40](../../architecture/design-package/method/decisions.md#d40).

For the research pilot, use a small CPU-only queue coordinator plus a narrow host-side launcher/profiler. Keep Docker/host credentials and profiler control in the host executor; do not mount `/var/run/docker.sock` into the capsule or generic runner. The coordinator consumes an allowlisted, pre-authorized campaign manifest—not arbitrary shell-command input—with pinned images, input hashes, case parameters, order, budgets and repeat policy. It builds/pulls images outside the GPU window. At the start of the authorized window, it preflights the host, launches the first job, then proceeds serially through eligible jobs until the queue is empty or an operator stop arrives. Slurm job arrays are an established pattern for managing collections of similar batch jobs; the same queue-and-job identity idea can be applied locally without adopting Slurm. [Slurm job arrays](https://slurm.schedmd.com/job_array.html).

Use extra authorized time for additional repeats under a declared adaptive rule: prioritize cases with high variance/uncertainty, missing coverage or a drift-control need; stop at per-case and campaign caps. Persist the queue cursor and append each run’s outcome so interruption does not lose completed evidence. A retry is a new run record; retain crashes, OOMs and invalid outputs. Stop safely on failed preflight, other GPU activity, thermal/power limits, exhausted disk/memory budgets or explicit stop. Cost is modest for prebuilt serial jobs but includes energy, heat, storage, wear, and analyst time; record wall time and energy where supported rather than presuming all repeats are equally useful.

The workload container gets only the intended GPU, fixed read-only inputs, bounded writable output, no unnecessary network, and conservative CPU/process/memory/time/disk limits. The host executor records target/GPU identity and checks idleness, temperature, memory/swap and active processes before each launch; it owns timeout/cleanup and preserves evidence. No process is preempted to make an experiment fit. Docker/Linux cgroups are useful for capsule process-tree and CPU/memory/I/O tracking; verify the actual cgroup v2 paths and counter semantics on the GB10.

```text
prebuilt OCI image + authorized campaign manifest
                    │
                    ▼
       CPU-only coordinator (queue / stop / cursor)
                    │  job_id, capsule_ref, case_id
                    ▼
    host launcher (GPU lease check + profiler + cleanup)
                    │
                    ▼
      capsule container ── cgroup + PID tree + stdio/HTTP IDs
                    │
       ┌────────────┴───────────────┐
       ▼                            ▼
Linux cgroup/PSI              NVIDIA device-wide signals
CPU/RAM/I/O/processes         NSYS timeline / NCU kernels
       └────────────┬───────────────┘
                    ▼
       joined, versioned run record → historical profiles
```

This maps naturally to `stdio` and HTTP: supervise the stdio child directly or health-check and call the capsule service over a private per-job network; collect result boundaries and stderr/stdout separately. The HTTP server and each request need distinct identifiers in the manifest. Containerization improves process-tree/cgroup tracking and environment repeatability. It does not make kernel metrics container-scoped, guarantee deterministic GPU performance, or make HTTP and stdio paths equivalent. For cold-start tests, launch a fresh container and record startup/model-load phases. For steady-state tests, keep the process warm and label that condition; do not mix repeated in-process samples with independent cold launches.

**Overhead evidence needs care.** A 2023 NVIDIA AGX Orin study describes container overhead as negligible in its abstract, but detailed results show CPU-mediated slowdowns for some lightweight training and inference cases, with smaller effects on heavier workloads. Its results come from a specific Orin, JetPack/CUDA/PyTorch/Docker stack, power mode, data and instrumentation. Use it to justify measuring container startup, CPU feed, energy and end-to-end latency separately; do not treat it as a GB10 overhead estimate. [Paper](https://arxiv.org/abs/2312.07220).

## Future AI4Research data contract (hypothesis, not an implementation request)

Keep three linked records, not one overloaded vector:

1. **Capability/workload identity:** capsule ID, pinned version/declaration and code hash; implementation/backend; OCI image-index and resolved platform digest; interface; input shape/size; model/operator/precision/batch; phase and concurrency; features available before launch.
2. **Execution context:** full CPU/GPU SKU and ISA, UMA/discrete topology and capacity, memory bandwidth, links/engines, OS/kernel/driver/CUDA/container versions, device UUID, cgroup limits, clocks/thermal/power state, residency/warmth, swap, background jobs and sharing mode.
3. **Observed profile/outcome:** phase boundaries, kernel IDs/times, selected SM/FP/Tensor/occupancy/stall/cache/DRAM/copy/codec signals, cgroup CPU/memory/IO/PSI, latency/throughput/energy where supported, quality/completion/OOM, source and measurement scope, sampling/replay method, missing mask and uncertainty, raw evidence references.

In planner language, the current capsule resource declarations describe **eligibility and need** (e.g. one GPU or exclusive GPU), not predicted SM/Tensor/cache demand. Keep those distinct. A later predictor can retrieve historical profiles by exact capsule/code/image/hardware context, then learn whether workload features predict resource demand and whether that improves scheduling or chip sensitivity estimates. Store counters by hardware/tool/metric version; do not compare unlabelled percentages across a GB10 and RTX 5070 Ti. The pipeline is:

```text
known task + capsule + input + target machine
    → retrieve comparable historical profiles
    → predict per-resource pressure + uncertainty
    → optional runtime observations update the estimate
    → planner chooses feasible capsule/order/concurrency
    → outcomes become new versioned evidence
```

The future planner should consume profile references or derived features without letting telemetry rewrite capsule declarations, alter frozen run plans, or count future observations as pre-execution knowledge. The design package currently makes capsule resources generic `read`/`write`/`use`/`exclusive` declarations; this note proposes no schema or planner change.

## Recommendation summary

- **Need:** treat OCI image digest as the executable identity for a tool-style CC; prebuild before the quiet window; preserve declaration/check/gate control as separate capsule records; per-kernel NCU metrics + NSYS phases; cgroup-v2 host accounting; pinned capsule/input/hardware identities; memory/swap/thermal/background state; raw exports and correctness; repeatability and missingness.
- **Run:** a finite authorized queue serially; continue until drained or stopped; use spare time for capped, uncertainty-directed repeats; persist run identity and every outcome.
- **Test:** tool support/overhead first; a compact resource-pattern suite on GB10; then selected cross-machine transfer cases; only then sharing pairs.
- **Avoid:** “CUDA-core utilization” as one direct value; treating a shared UMA pool as VRAM; treating Docker stats as GPU counters; attributing global GPU signals without a checked quiet window/process-job evidence; assuming DCGM profiling works on GB10 before probing; mixing DCGM counters with Nsight counter sessions; comparing x86 and ARM images as identical execution environments; and extending product/sidecar architecture in this exploratory research note.

## Primary sources

- [GB10/DGX Spark hardware](https://docs.nvidia.com/dgx/dgx-spark/hardware.html) · [Known issues and UMA memory reporting](https://docs.nvidia.com/dgx/dgx-spark/known-issues.html) · [Porting guide](https://docs.nvidia.com/dgx/dgx-spark-porting-guide/optimization.html)
- [RTX 5070 Ti specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070-family/)
- [Nsight Compute GB10 support](https://docs.nvidia.com/nsight-compute/ReleaseNotes/topics/gpu-support.html) · [Compute triage](https://docs.nvidia.com/nsight-compute/ComputeTriage/) · [Nsight Systems on DGX Spark](https://docs.nvidia.com/dgx/dgx-spark/nsight.html)
- [DCGM profiling](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html) · [DCGM process/job statistics](https://docs.nvidia.com/datacenter/dcgm/latest/learn/core-services/process-and-job-statistics.html)
- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) · [Linux PSI](https://docs.kernel.org/accounting/psi.html) · [Docker stats](https://docs.docker.com/reference/cli/docker/container/stats/)
- [OCI image spec](https://specs.opencontainers.org/image-spec/) · [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/overview.html) · [DGX Spark Docker runtime](https://docs.nvidia.com/dgx/dgx-spark/nvidia-container-runtime-for-docker.html)
- [Docker GPU access](https://docs.docker.com/engine/containers/gpu/) · [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/) · [Slurm job arrays](https://slurm.schedmd.com/job_array.html)
- [Containerized DNN training/inference on AGX Orin (HiPC 2023)](https://arxiv.org/abs/2312.07220) — supports negligible overhead for the paper’s individual workloads and tested Orin/software/power setup; use as a precedent, not as a GB10 measurement or a universal overhead guarantee.
