# Goals and roadmap

This is a synthesis of the user's current direction and retained planning, not a new execution authorization. The current target is DGX Spark with the qualified local Strata/DeepSeek baseline. Earlier Muse and Jetson materials explain the evolution.

## Goal hierarchy

| Goal | Concrete outcome | Evidence of completion / remaining work |
|---|---|---|
| Useful inference-engine product | Reproducible source/configuration/image that runs the target model within a hardware/resource envelope | Existing qualified runs and prefill result are scoped to pinned assets; numerical/quality acceptance remains incomplete |
| Adaptive software factory | Agent turns an objective into hypotheses, bounded experiments and justified continuations | Agent reasoning and admitted lab execution exist; fresh connected branch-to-GPU interruption/recovery acceptance is still needed |
| Reusable engineering components | Tools, skills and implementation components carry interfaces, applicability, source identities and checks | Source library is cataloged in COMPONENTS; sealing or a microbenchmark does not establish engine integration |
| Reliable empirical learning | Negative results, raw outputs, engagement checks and costs survive retries/restarts | Preserve failed exactness, dump truncation and timeout episodes; validate endurance and independent confirmation |
| Efficient research loops | More useful verified decisions per time, compute, memory and agent cost | Measure comparable tasks and outcome quality; response-byte savings alone are insufficient |
| Portable team/RSI handoff | Another agent can understand intent, reconstruct sources and resume with explicit dependencies | This package plus original image/evidence exports; clean-root restoration remains a separate test |

## Near-term sequence

1. Reconcile live state with the captured source and artifacts. Use the current baseline and retain old failed contracts.
2. Complete one connected investigation: choose a branch, use the existing admitted experiment path, interrupt/recover without duplicate work, attach verified results and decide what follows.
3. Reuse retained numerical captures, then qualify repeatability and observer cost. Separate measured output divergence from hypotheses about its cause.
4. Select one evidence-supported intervention, integrate it and confirm on independent workloads under a predeclared numerical/quality policy.
5. Measure factory cost and fresh-root recovery, then widen to bounded multi-cycle campaigns with retention/crash limits.

These milestones have acceptance conditions, not invented due dates. November20 was a progress checkpoint in the November13 handoff, not a renewed presentation task or proof deadline. Earlier ten-minute demo schedules and overnight GPU allocations are historical.

## Research directions and dependencies

- Expert cache/read scheduling and prediction need real demand/readiness/stall traces, including wasted reads and contention. Preserve all demanded experts for scheduling comparisons.
- CPU/GPU placement and resident budgets need Spark-specific accounting and matched speed/quality measurements.
- Prefill chunk policy has scoped positive evidence but an unresolved longer-generation exactness failure.
- Quantized dispatch and scratch reuse need actual engine integration and engagement, beyond subsystem oracles.
- KV reuse, context memory and serving scheduling are candidate jobs; do not present the catalog as delivered serving improvements.
- Persistent engine reuse/hot loading was an earlier conditional proposal. Establish startup cost, state reset and recovery fidelity before making it a dependency.

## Planning evolution

| Period | Direction | How to use it now |
|---|---|---|
| Nov6–9 workshop | Contract/tool/component/image separation, lab ownership and telemetry; Muse/Spark design | Architectural rationale; compiler split, Incus deployment and examples are proposals, not mandatory current implementation |
| Nov11 interface and demo planning | Manager-mediated evidence, lab investigation autonomy, six-role component-to-image flow | Preserve boundaries; older full-lab deck and generic demo sequencing were superseded |
| Nov12–13 Jetson demo | Use actual expert-streaming components, build and inference evidence, then hand off to RSI | Reusable story and real historical evidence; no automatic Spark portability claim |
| Nov13 Spark migration | Native builds, SSH durable execution, memory controls and newer Strata with existing DeepSeek assets | Setup history and resource lessons; superseded by later measured Spark state where explicit |
| Nov14–15 Spark research | Bounded factory/engine loops, branch methods, prefill/placement results, numerical diagnosis | Immediate working direction and evidence, with latest connected-development addendum taking precedence |

Sources: [current loop](reference/factory-source/docs/architecture/factory/INFERENCE-FACTORY-LOOP.md), [development review](reference/factory-source/docs/architecture/factory/DEVELOPMENT-REVIEW-2026-11-16.md), [connected development](reference/factory-source/docs/architecture/factory/CONNECTED-DEVELOPMENT-2026-11-16.md), [planning catalog](PLANNING-INDEX.md), and [presentations](PRESENTATIONS.md).
