---
id: muse-final-future-experiments-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# TKCC evolution: bounded future experiments

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a lab agent in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.



Prerequisite for E1/E2: an admitted working engine/image and two supplied representative workloads; image/model files already staged. One GPU at a time. The following are pilot effort limits, not expected completion times or general acceptance thresholds. Budget expiry yields incomplete evidence, not a pass/fail on engine merit.

| Pilot | Fixture/repetitions and stop budget | Observe/check | Decision |
|---|---|---|---|
| E1 startup decomposition | Five paired fresh-start / same-image-warm blocks per workload; two workloads; one GPU-hour | staging, launch, load, warmup/autotune/graph, trial wall seconds; rate/peak/correctness; actual cache state | Is startup large enough to justify reuse work? Fresh process is not cold SSD/page cache. |
| E2 same-image reset | Ten A–B–A request/session/cancel cycles against fresh-engine warm reference; one GPU-hour | reset KV/session/RNG/scheduler/prefix state; continuation/sentinel correctness; memory drift; stale handles | Reuse only within demonstrated state/reset coverage. Leak/unknown state → fresh restart. No implementation reload. |
| E3 cheap-tier fidelity | Builder supplies immutable single-Muse-block harness and real captured activations; up to four prebuilt candidates; two workloads; three repetitions; one builder-day plus one GPU-hour | initially run all candidates in cheap and full tier; detect false rejects/sign reversals beyond A/A noise; validate numerical boundaries | Useful screening must save total experiment time without hiding full-tier wins/regressions. Full quality remains mandatory. |
| E4 hotload boundary | Optional builder-supplied image with equivalent A/B projection modules; five A–B–A cycles; one builder-day plus one GPU-hour | actual module/code identity; drain in-flight work; load/reset/graph recapture/unload/wall time; outputs/memory drift | Go only with compatible boundary, rollback and real loaded identity. Otherwise unsupported/no-go; static selection is not hot reload. |

Every cycle records image/product/module, environment, fixture, state policy, run/generation and raw outputs. E4 recovery after crash or unknown state is a clean engine restart. No retry silently repeats uncertain effects. The lab spends bounded observation effort; implementation changes remain Builder-side.
