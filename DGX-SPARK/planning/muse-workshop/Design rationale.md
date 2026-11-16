---
id: muse-final-design-rationale-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Design rationale

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a lab agent in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.

| Choice | Why | What must be demonstrated |
|---|---|---|
| Identified image with read-only code and separate state | Prevent silent candidate edits; correlate results with exact code/dependencies. Image digest alone does not enforce runtime immutability. | code-write denial, permitted state/output writes, loaded identity and effective mounts |
| External versioned profiler/tool packages | Tool update does not force engine rebuild; same engine supports plain/nsys/ncu wrappers. | compatible full tool distribution, grants, actual trace and report export |
| One experiment input bundle | Engine, model, config, fixture, reference, playbook, tools, marker manifest and resource profile are explicit materials. | integrity/readiness and comparison to the supplied policy |
| Useful missing-evidence outcomes | Missing markers/counters/decoders indicate a concrete next build rather than speculative optimization. | component/path/question and observed failure/coverage references |
| Factory knowledge/telemetry | Shared source of reference for builder and lab agent; raw evidence can be reanalyzed later. | durable references, hashes and export receipt before staging cleanup |
| Immutable first, TKCC later | No engine/factory exists yet to justify ABI/hotload/reset framework. | measure actual startup/warmup/evaluation costs; then bounded A7 pilots |

Strata inspires residency/routing/weight-access investigations; DwarfStar provides a gated NVTX implementation example. Together motivates representative inputs and tiered experimentation. NVIDIA/Incus document tool/runtime mechanisms. None supplies a measured Muse/Spark result for us. See [[Evidence]].
