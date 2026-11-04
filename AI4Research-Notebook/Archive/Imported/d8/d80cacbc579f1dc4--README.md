---
title: "Workload profiling literature — reuse before new experiments"
date: 2026-10-19
status: initial-literature-review
tags: [literature, gpu, prediction, simulation]
---

# Workload profiling literature

Three Luna agents researched prediction, interference and simulation using primary papers and project sources. This is an initial research map, not an exhaustive systematic review. No new experiments were run. The earlier shared Claude artifact was excluded as evidence.

Read the [experiment-agent brief](../experiment-agent-brief.md) for the project objective and [prediction](prediction.md), [contention](contention.md), and [simulation](simulation.md) for detailed source notes.

## Prioritized reading and reuse

| Source | What to reuse | What still needs validation here |
|---|---|---|
| [Towards GPU Utilization Prediction for Cloud Deep Learning, HotCloud 2020](https://www.usenix.org/system/files/hotcloud20_paper_yeung.pdf) | Computation-graph features as inputs to prediction without profiling every submitted job. | Its coarse GPU-busy target is not a component-wise stress vector; heterogeneous research tools need a broader representation. |
| [NeuSight: Forecasting GPU Performance for Deep Learning Training and Inference, ASPLOS 2025](https://doi.org/10.1145/3669940.3707265), [code/data](https://github.com/scai-tech/NeuSight) | Tile-level learned performance prediction conditioned on device and model descriptions. | DL latency forecasting does not establish component pressure for arbitrary processes or reliable forecasts for every proposed chip. |
| [Orion, EuroSys 2024](https://anakli.inf.ethz.ch/papers/orion_eurosys24.pdf) | Kernel-level profiling and scheduling with complementary resource phases. | Our task/backend families, hardware, sharing mode, and fidelity of predicted rather than measured profiles. |
| [Understanding GPU Resource Interference One Level Deeper, SoCC 2025](https://anakli.inf.ethz.ch/papers/gpu_interference_socc25.pdf), [microbenchmarks](https://github.com/eth-easl/gpu-util-interference) | Resource-specific sensitivity methods covering placement, pipelines, caches and bandwidth. | Whether history predicts sensitivity for unseen tasks; whether selected interventions explain our observed bottlenecks. |
| [Accel-Sim, ISCA 2020](https://doi.org/10.1109/ISCA45697.2020.00047), [framework](https://accel-sim.github.io/) | Trace-driven GPU simulation and validation infrastructure. | ISA/feature support, calibration, representative regions and validation for the actual target; traces do not automatically adapt to changed software. |
| [Chakra, 2023 paper](https://arxiv.org/abs/2305.14516), [schema/tools](https://github.com/mlcommons/chakra) | Standard execution-graph representation for AI performance modeling and co-design. | Mapping AI4Research process and capsule provenance to operations; kernel-level architectural behavior needs another model. |
| [Blackwell microbenchmark study and artifact, IPDPS 2026](https://github.com/UD-CRPL/IPDPS_26_B200_Microbenchmark) | Existing B200/H200 microbenchmarks and calibration methodology. | B200 results cannot stand in for all Blackwell devices, including GB10 or consumer parts. Run only the calibration needed on our exact device and supported feature set. |

## Spend experimental effort on the gap

Existing literature already motivates graph-based prediction, profiling-based sharing and architectural simulation. Use its implementations and datasets when compatible. Reproducing a small baseline remains useful for calibration and a fair comparison; avoid a broad campaign to rediscover effects already demonstrated.

Our proposed question is whether real AI4Research histories predict phase-resolved component demand and interference for held-out workloads, with useful uncertainty, and whether those predictions preserve conclusions in a calibrated architecture study. That is a research direction, not a novelty conclusion.

Start with an audit of available data and simulator compatibility. Then compare task-family averages, nearest-neighbor retrieval, analytical models and a learned model under the same feature-availability rules. Distinguish predictions before launch from estimates refined by a measured prefix. Use task-family and hardware holdouts rather than splitting duplicate executions randomly.

Retain both resource demand and sensitivity to competing demand; they are different targets. Select diverse and uncertain cases for new measurements. Before chip sweeps, correlate a supported baseline simulation with observed behavior and identify the resource changes the model actually represents. Include workload mix and software assumptions in any architectural conclusion.

## Presentation implications

We can already present the research objective, prior-work map, proposed representation and validation plan. Measured findings, achieved predictor accuracy and chip-design recommendations must come from the experiment agent's evidence. A defensible slide narrative distinguishes prior literature, our observations, predictions and hypotheses. No local result or accuracy number is supplied by this review.
