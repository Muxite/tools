---
id: muse-layers-profiling-explained
status: current-explanation-target-environment-unqualified
source: November 5 presentation discussion; pinned CC/Muse/Strata/DwarfStar sources; official NVIDIA/Incus docs
last_reviewed: 2026-11-05
next_action: Qualify the immutable image GPU/profiler path before claiming Muse measurements
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Inference layers, NVTX and Nsight explained

The layers locate engineering questions. They can share a process, fuse operations and interact directly; they do not prescribe a five-service implementation.

## What happens in each layer

| Layer | Plain meaning | Example during Muse inference | What a diagnostic can distinguish |
|---|---|---|---|
| API/protocol | Receive a request and deliver a response. | Parse HTTP input, apply the selected chat/template settings, return SSE content/errors. | Client transport, parsing or streaming behavior versus engine work. |
| Scheduling/execution | Decide which accepted work runs next and advance it. | Admit sessions, form batches, run prompt prefill, schedule subsequent decode steps, handle cancel/reset. | Queue delay, batching efficiency, long-prefill interference and session fairness. |
| Muse operations | Perform the model's mathematical computation. | Embeddings, attention using KV state, learned expert routing, expert projections/SwiGLU, weighted combination, logits and sampling. | Which logical layer/operator is expensive or incorrect. |
| Tensor/state/weight runtime | Supply the numeric data and manage its storage/lifetime. | Load weights, allocate workspaces, retain KV, find selected expert weights in resident/cache/mapped/streamed storage. | Weight waits, duplicate copies, allocation peaks, state growth and cache effects. |
| CUDA/GB10 | Execute GPU work and coordinate it with the CPU. | Launch native kernels on streams, manage device-accessible buffers/events, perform copies and synchronize only where needed. | Launch gaps, device duration, overlap, synchronization and selected-kernel behavior. |

**Scheduling versus CUDA execution:** the scheduler might choose a batch of decode requests. The engine then runs the Muse operation graph for that batch and submits many GPU kernels. A fast kernel does not remove time the request spent waiting in a queue.

**Prefill** processes prompt tokens and establishes context state; **decode** repeatedly computes the next token using that state. They use related operations with different shapes, memory demands and opportunities to batch work. Their bottlenecks must be measured, not assumed.

## Tensor, weights, state and pack

| Term | Meaning | Lifetime / example |
|---|---|---|
| Tensor | A shaped numeric array, with dimensions, datatype and memory layout. | May hold weights, temporary activations or persistent state. It is a data structure, not a separate engine stage. |
| Weights | Learned numerical parameters used by model operations. | Usually fixed for the checkpoint; representation/quantization may differ between candidate packs. |
| Activation | An intermediate tensor produced by computation on the current inputs. | Reused or released during a forward step. |
| Workspace | Temporary storage used to execute an operation efficiently. | Can be shared between operations/sessions under a safe scheduling policy. |
| KV cache | Stored attention keys and values for previous tokens. | Persists with a session/context; changes as tokens are added/reset. It is not the expert-weight cache. |
| Expert residency/cache | Which expert weights are already accessible in the chosen fast tier. | Responds to placement policy and workload; a miss may trigger another weight-access path. |
| Weight pack | Prepared model-weight files plus the format/layout/index/representation information an engine reads. | An identified data artifact/material, potentially outside the image as read-only mounts. Exact format depends on the chosen engine. |

**Pack versus pack CC:** the pack is data. A pack-preparation/inspection CC is executable tooling that reads or creates that data. Conversion must preserve the declared model semantics or be explicitly evaluated as a representation change.

**Diagnostics versus diagnostic CC:** diagnostics are inspections/measurements that explain behavior. A diagnostic CC exposes acquisition or analysis tools through a repeatable interface. A trace, logit dump or report returned by the tool is normally an artifact, not another runnable capsule.

## How NVTX fits Muse operations

NVTX adds semantic names/context to code regions: `prefill`, `decode`, attention, routing, expert lookup, dispatch or state restoration. The instrumentation CC supplies reusable rules/helpers, proposes source sites, applies a patch and verifies observed coverage. A marker manifest maps source sites to component IDs, phase, shape, and request/session/batch context.

An optimized implementation can fuse several logical operations into one kernel. Conversely, a logical operation can launch several kernels. NVTX helps preserve the logical meaning while a CUDA capture shows the actual execution.

```text
Muse operation: selected expert work
    router selects IDs / weights
    residency lookup finds required weights
    host dispatch region submits CUDA work
    GPU executes one or more expert kernels
    weighted outputs are combined
```

A named host range is not a GPU timer. For example:

```cpp
nvtxRangePushA("moe.dispatch");
expert_kernel<<<grid, block, 0, stream>>>(...);
nvtxRangePop();
```

The host can close the range before the GPU finishes the kernel. CUDA activity supplies device start/end. Adding a device-wide synchronization merely to align the bars changes execution and can destroy the overlap we want to understand.

Push/pop ranges nest on one thread. Start/end ranges use a handle and can overlap or cross threads. Scoped C++ helpers can close ranges reliably; C instrumentation must cover every return/error path. Use stable names and numeric correlation instead of allocating a distinct string for every token. High-volume layer/expert tracing is diagnostic, not automatic permanent scored-run overhead.

[NVTX overview](https://nvidia.github.io/NVTX/) · [Range API](https://nvidia.github.io/NVTX/doxygen/group___m_a_r_k_e_r_s___a_n_d___r_a_n_g_e_s.html)

## Systems versus Compute

| Tool | Useful question | Typical evidence |
|---|---|---|
| Nsight Systems | Where does time go across host activity, CUDA submissions, GPU work, copies and waits? | Timeline with CUDA/API activity and NVTX context; raw `.nsys-rep`. |
| Nsight Compute | What limits this selected kernel under these shapes/settings? | Supported kernel metrics/counters, memory/compute/occupancy analysis and raw report. |

Use Systems to locate a stage/kernel question; use Compute when counters can discriminate it. Compute may replay work for multiple metrics and perturb cache/state/timing. A diagnostic result is therefore retested in a separate matched unprofiled serving run before claiming an end-to-end gain.

[Systems guide](https://docs.nvidia.com/nsight-systems/UserGuide/) · [Compute profiling/replay](https://docs.nvidia.com/nsight-compute/ProfilingGuide/)


## Current execution and evidence placement

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a lab agent in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.

See [[Deployment choices]], [[NVTX engineering CC]], [[Resource provisioning]].
