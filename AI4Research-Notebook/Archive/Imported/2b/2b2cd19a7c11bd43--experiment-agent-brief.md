---
title: "AI4Research workload profiling — brief for the experiment agent"
date: 2026-10-19
status: exploratory-research-direction
tags: [ai4research, workload-profiling, gpu, chip-design]
---

# AI4Research workload profiling: brief for the experiment agent

> **Scope clarification, October 19:** AI4Research is not built yet. Today's assignment is literature research and recommendations for standalone profiling experiments. Use [Before AI4Research: what to measure next](prebuild-recommendations.md) as the current action brief. The longer-term system direction below is context, not today's implementation plan.

## Project context

AI4Research is a scientific research system built on JiuwenSwarm/OpenJiuwen. It turns a user’s research objective and baseline into a checked research brief, searches and screens opportunities, formulates a falsifiable hypothesis, builds a bounded proof of concept, benchmarks baseline and treatment, evaluates the evidence, and delivers a report with supporting artifacts.

Reusable Capability Capsules supply the work. The platform binds exact versions and inputs, controls execution, checks outputs independently, and preserves provenance. A workflow node, a capsule call, an OS process, and a GPU kernel are distinct units; one can produce many of the next. Profiling needs to connect these levels.

The workload-profiling direction below is a proposed project-wide research program. It is not a claim that the current product already implements a hardware predictor. The maintained M1 design executes one workflow node at a time; experiments with concurrent jobs explore future behavior rather than describe that scheduler. Some model calls use external services: local waiting time does not expose the remote GPU’s behavior.

## Research objective

Use real AI4Research work to build a historical workload corpus that helps predict which GPU resources a new task will demand, how that demand changes over time, and how alternative hardware could affect execution. The eventual audience includes chip architects, not only workflow schedulers.

The proposed loop is:

**Task and implementation description → retrieve comparable historical profiles → predict phase-level resource demand with uncertainty → simulate execution under a stated hardware model → validate predictions and retain evidence.**

The central hypothesis is that structured features and historical examples can provide useful component-level predictions for unseen tasks. This is a hypothesis to test, not an established finding or novelty claim.

## What the vectors represent

Keep three linked records rather than one undifferentiated embedding:

1. **Workload features:** task/capsule and code version, model/operator structure when available, input sizes and shapes, batch and context lengths, precision, backend, selected algorithms, and execution phases. Label which features are available before launch.
2. **Execution conditions:** exact hardware, memory topology and capacities, software versions, sharing mechanism, concurrent jobs, model/cache residency, and relevant clock/power conditions.
3. **Measured outcomes:** time-resolved resource observations, latency, throughput, memory peaks, transfers, and evidence pointers. These are training targets and validation evidence, not inputs to a claimed pre-execution prediction of the same run.

Retain raw records, physical units, feature definitions, missing-value masks and provenance alongside vectors. Start with interpretable features and a standardized nearest-neighbor baseline. Evaluate whether learned embeddings improve predictions over task-family averages, simple regression and analytical baselines. Semantic similarity between task descriptions alone does not establish similar hardware behavior.

Preserve phase order and duration. Two tasks with the same average vector may have different peaks, synchronization points and interference. A short profiling prefix can refine predictions, but report that as a separate prediction mode with its own cost.

## What “GPU stress” should mean

Define explicit prediction targets rather than a single GPU-utilization score:

- Compute-pipeline demand: tensor/matrix, floating-point, integer and other relevant instruction classes.
- Memory behavior: DRAM traffic and bandwidth, cache traffic/locality and misses, working-set capacity, and supported shared-memory statistics.
- Execution constraints: occupancy, register/shared-memory limits, issue behavior, dependencies, stalls, launches and synchronization.
- Data movement: host/device and device/device copies, links, and memory placement or migration where observable.
- Specialized engines: video encoding and decoding separately, plus their supporting compute and transfer work.
- End-to-end behavior: CPU preparation, storage/network waits, initialization, model loading, power/energy where attributable, and GPU-active execution.

For every target specify units, observation scope, aggregation window and instrumentation. Missing or unsupported counters are unknown, not zero. Device-wide activity during a co-run is not automatically attributable to either process. Nsight Systems provides execution timelines; selected Nsight Compute measurements add kernel-level detail. Detailed collection can require replay and perturb execution, so measure its effect and keep production-like timing separate from intrusive counter passes. [NVIDIA profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html), [Nsight Systems guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html).

High utilization is evidence of activity, not by itself proof that a component limits performance. Chip-design conclusions need a validated model or controlled sensitivity tests showing what changes when a resource changes.

## Prediction, simulation and chip-development evidence

Build two connected layers: a workflow/process model for CPU work, queues, transfers, startup and phase ordering; and a GPU model for representative kernels or regions where architectural detail matters. A kernel timeline alone does not contain instruction dependencies or memory addresses needed by many detailed simulators.

Predicting a familiar task on existing hardware and forecasting a changed chip are different tests. Keep workload demand separate from hardware-dependent response. More cache, bandwidth, compute units or a different interconnect can alter bottlenecks; do not scale observed utilization percentages as though they were intrinsic workload properties. Changes to algorithms, compiler choices or inputs may also require new traces. Assess simulator support for the actual ISA, instructions, memory system and sharing mode before selecting it.

The architectural deliverable should be a representative, weighted workload suite and sensitivity results: which resource changes improve latency, throughput or energy; which tasks benefit; which regress; and how uncertain those conclusions are. Explain the assumed workload mix. AI4Research traces do not automatically represent all future computing demand.

## Priorities for further experiments

First review the [literature research](literature/README.md), reuse available methods, code and datasets, and use established effects as calibration checks rather than novelty claims. Focus new measurements on what prior work does not establish for our tasks and hardware.

1. Trace real AI4Research calls through their subprocesses, shared model servers, kernels and phases. Identify which work actually executes on the observed GPU.
2. Build a small, diverse corpus. Vary input shape, backend, precision, residency and concurrency deliberately; retain repeats, errors and out-of-memory outcomes.
3. Evaluate historical-profile retrieval before increasingly complex predictors. Hold out entire task families, implementations and hardware targets; avoid splitting near-identical repeated runs across training and test sets.
4. Score component-wise errors, phase/peak errors, bottleneck classification, latency prediction, uncertainty calibration and out-of-distribution detection. Set acceptance thresholds before evaluation; there is no agreed numerical target yet.
5. Validate representative simulator cases against measurements before sweeping architectural parameters. Use selective profiling for uncertain examples rather than exhaustively measuring every combination.

Hardware conditions matter: an unavailable video engine may force a CPU path; a different backend may choose different kernels; unified memory can change placement, transfer and contention behavior. Treat each as an explicit condition, not a permanent dependency between logical tasks.

## Presentation preparation

Organize the presentation around: research question; AI4Research workload provenance; prior work and what we reused; corpus and measurement method; prediction accuracy on held-out cases; validated simulation and architectural sensitivity; limitations and next experiments.

Separate **published prior results**, **our measured results**, **model predictions**, and **unvalidated hypotheses** on every slide. Every experimental chart should identify workload, machine, software, sample count, uncertainty and evidence location. This brief contributes no new measured findings and does not use the earlier shared artifact as a source.

## Project sources

Project description checked against the current [product receipt](../../product/README.md), [PRD V10](../../product/received-prds/prd-m1-v10-2026-10-15.txt), [system design](../../architecture/design-package/1-system.md), and [capsule description](../../architecture/design-package/2-capability-capsules.md). The profiling research direction comes from the user’s October 19, 2026 instruction. It does not amend the product requirements or maintained architecture.
