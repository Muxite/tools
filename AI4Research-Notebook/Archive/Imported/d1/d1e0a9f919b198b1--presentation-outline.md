---
title: "GPU workload profiling: research briefing"
date: 2026-10-19
status: literature-based pre-build recommendations
tags: [presentation, profiling, GPU, cloud, experiments]
---

# GPU workload profiling: research briefing

Live Page ID: `page_c01c86235d1081918893b0ef4e6833dd`.

The live presentation is a 25-slide, diagram-led technical briefing. It opens with the chip-development value, follows workload execution through NVIDIA GPU resources, compares memory and sharing arrangements, then maps local and cloud observability to pre-build experiment recommendations. Its GB10 section compares the two Blackwell systems, distinguishes CUDA-core marketing counts from actual profiler signals, diagrams the OCI/cgroup/GPU evidence join, and lays out a bounded overnight runner. The local reproducible build and checked PPTX live in [`presentation/`](presentation/README.md).

AI4Research is not built. This is literature research and experiment planning; no new profiling runs or chip-design decisions are claimed. The imported Claude artifact is not used as scientific evidence. Existing raw experiment logs have not been audited, so revisions are conditional on what those records already answer.

## Presentation flow

1. Chip-development value: workload labels hide the resource path.
2. Execution path: application, CPU, runtime/driver, GPU engines and output.
3. NVIDIA resource map: SMs, pipelines, caches, device memory, links and codec engines.
4. Counter meaning: SM activity, pipeline activity and DRAM activity answer different questions.
5. Memory arrangements: discrete GPU memory, CUDA managed memory and coherent Grace–Blackwell systems.
6. Data movement and sharing: PCIe/NVLink, batching, streams, MPS and MIG.
7. Phase and media paths: startup versus steady service; CPU/CUDA/NVDEC/NVENC.
8. Observability: host tools, NVML, DCGM, Nsight Systems/Compute and provider telemetry.
9. Action: audit existing records, run only decisive contrasts, improve data collection and state what to avoid.
10. Future connection: keep task/phase, machine/state and measured outcome distinct until the prediction target is validated.

Every recommendation carries a primary source or qualified research basis, applicable scope and measurement limitation in slide text or speaker notes. Provider documentation establishes what their systems collect; it does not establish that every field predicts chip performance.

Current action brief: [pre-build recommendations](prebuild-recommendations.md). Research notes: [literature map](literature/README.md). Future predictor context: [experiment-agent brief](experiment-agent-brief.md).

For the proposed hardware-specific collection and research runner, see [GB10 workload profiling plan](gb10-profiling-plan.md). It includes the two-machine comparison, OCI/cgroup/Nsight/DCGM measurement ladder, overnight campaign phases, and the boundary with the existing sidecar design.
