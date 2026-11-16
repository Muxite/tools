---
id: muse-final-alignment-and-decisions-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

> **Post-presentation update, November6:** [[Post-presentation contract and ontology]] supersedes the top-level “request CC” framing. Use a detailed contract compiled from intent/ontology/requirements; CCs are capability units, and the package/image is the deliverable. Separate factory-tool from product-component CCs. Delivered slides remain unchanged while more notes arrive.

# Current alignment and decisions

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a lab agent in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.

| Decision | Reason / evidence boundary |
|---|---|
| One compatible Builder can build engines, tools and skills | Reuse CC contract, materials and image/native/delegate implementation mechanisms; no separately required factory implementation. |
| OCI image + private Docker inside Incus | Reuses current Docker-backed image convention and separates candidate from lab tools. GPU/Incus provider still needs qualification. |
| Optional ontology in request materials | Carry externally authored semantics; do not create competing vocabulary or require a finished ontology. |
| Lab agent follows bounded branches | Avoid repeated manual tool discovery; mandatory checks precede optional costly diagnostics. |
| Separate normal, Systems and Compute attempts | Profiling can perturb overlap, timing, caches and memory. Saved report analysis usually needs no new GPU run. |
| NVTX source helpers live builder-side | Checked patches and regression cases prevent repeated mistakes; lab reports actual emitted coverage only. |
| Resource profile is separate from engine residency budget | Safety cgroups and experimental expert-cache policy answer different questions. |
| TKCC evolves after measurement | First determine whether loading/warmup dominates; persistent code replacement is an engine interface, not a container feature. |

## Superseded interpretations

The November5 native-in-Incus/local-workbench recommendation was an earlier accepted direction. The November6 immutable-image, test-only proposal now takes precedence. General scoped development sessions and in-lab rebuild arrows are removed. Factory knowledge/telemetry replaces lab-local durable evidence storage. Existing source snapshots, original user wording and backups remain historical evidence.

## Decision resolution workflow

For a consequential fork retain: question/constraints → smallest alternatives → primary-source research → independent challenge → recommendation/reason → qualification test → revisit trigger. This is a note/review workflow, not another runtime subsystem. Direct Incus OCI remains a valid alternative if nested qualification fails; do not build both providers preemptively.
