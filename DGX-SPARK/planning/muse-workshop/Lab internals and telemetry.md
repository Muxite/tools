---
id: muse-final-lab-internals-and-telemetry-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Lab observations return to Factory

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a lab agent in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.

See [[Deployment choices]], [[Lab and experiment]], [[Resource provisioning]] and [[Data to collect]]. The current plan removes the earlier local workbench/edit/rebuild loop. A worker confirms ownership/readiness/stop and protects host/client evidence; Factory persists all raw artifacts and interpretations. Agent diagnosis is separate from the benchmark verdict.
