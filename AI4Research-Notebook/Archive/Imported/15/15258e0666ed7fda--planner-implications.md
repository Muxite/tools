---
title: "Planner implications from shared-resource measurements"
date: 2026-10-16
tags:
  - research
  - planning
  - scheduling
status: exploratory
source: "[[sources/2026-10-16-shared-gpu/report|Shared GPU, same node — captured report]]"
---

# Planner implications from shared-resource measurements

The imported [shared-GPU report](sources/2026-10-16-shared-gpu/report.md) suggests that a task dependency graph is necessary for ordering work, but it cannot by itself explain where tasks can run, when they should overlap, or what latency they will experience. The measurements came from one RTX 5070 Ti workstation and small, workload-specific samples. They are prompts for project-wide investigation, not general GPU constants or architecture requirements.

## Separate feasibility from expected contention

A planner first needs to know whether a task can run on a candidate machine at all: required backend, device features, available memory, compatible runtime, and any task-specific placement rules. These are hard feasibility conditions. Among feasible choices, it can then estimate conditional contention: how a task may slow another when they share a resource. In the report, LLM decode beside CNN training slowed substantially, while training was only modestly affected; speech-to-text and NVENC encoding showed little GPU contention in those particular runs. That asymmetry makes a single “GPU busy” number inadequate. Estimates should depend on the pair of task phases, the machine, and the backend.

The report’s time-split estimate—weighting solo counter profiles by each task’s measured share and accounting for switching loss—roughly matched some observed combinations. It is a useful baseline to compare against, not a standalone predictive simulator: measured shares are inputs, and a planner still needs a way to estimate them under new workloads, placements, and interference. The report also raises open questions about burst patterns, switching costs, and real agent traffic that remain unmeasured.

## Placement includes data and state

Resource relationships need not become permanent precedence edges. The same logical task might choose a CPU implementation, a supported accelerator backend, or a shared service. Those choices determine which capacities and competing tasks matter. A useful discussion model is task alternatives plus a machine resource map and current occupancy, with conditional scheduling constraints derived for a candidate placement. A conflict on one machine may disappear, or change shape, on another. For video, record encoding and decoding capabilities separately: NVENC is the encoding path; a hardware decoder (for example, NVDEC) is a separate capability, with codec and backend support to check.

A DAG records producer-consumer ordering, but placement decisions also depend on where inputs and reusable state already reside. Copy bandwidth differed by direction and memory type in the measured setup; model first-token latency varied sharply depending on whether weights were already in GPU memory, in host RAM, or on disk. Container startup, model loading, and GPU-code compilation also add lifecycle costs that can dominate short tasks. Warm workers and caches may change the preferred placement even when the logical DAG is unchanged.

These effects should be considered as candidate-dependent transfer and readiness costs, with evidence and confidence attached. The report’s file-cache accounting and cold-start observations are especially environment-specific. Unified memory on ARM systems may reduce some CPU–GPU transfer costs, but that is an unmeasured hypothesis in this source and must not be treated as an established benefit. Shared memory bandwidth could introduce different contention instead.

## Model phases and service objectives matter

A model task does not have one fixed resource profile. Prompt prefill and token decoding used the GPU differently in the report: prefill showed more tensor activity, while decode leaned heavily on memory bandwidth. Thus estimates should be phase-specific where a task’s phases have meaningfully different demand. The measured decoding behavior on this card should not be generalized into a rule for all model sizes, accelerators, precisions, or inference backends.

Likewise, batching changes the objective tradeoff. In the reported Qwen 2.5 3B test, batching requests increased total throughput and reduced memory duplication, while per-request token latency rose at some batch sizes. A planner or serving policy must make its latency and throughput goals explicit; “maximize throughput” does not necessarily satisfy interactive work. Encoding capability should also be distinguished from general GPU compute: NVENC encoding used a specialized video path and barely registered in the report’s GPU compute counters. Backend support, codec settings, and device generation determine whether that path is available and useful.

## Research questions, not design mandates

A broader evaluation should vary machines, accelerator generations, backends, model and task phases, batch sizes, warm/cold state, and transfer locality. It should measure task-pair slowdowns and latency distributions as well as solo throughput, and label observations by environment and sample count. This would help answer which estimates can safely inform scheduling and where the system should retain uncertainty or prefer conservative choices.

Nothing in these observations calls for a new runtime schema or mutation of a frozen DAG. They identify information and experiments that may matter when discussing resource-aware planning across the project; any product or architecture change would need its own authorized requirements and design decision.
