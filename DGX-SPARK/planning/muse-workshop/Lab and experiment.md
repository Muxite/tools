---
id: muse-final-lab-and-experiment-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# Experiment inputs and bounded playbook

**Starting proposal:** the builder submits an immutable ARM64 OCI engine release image. A Factory lab manager coordinates with a deterministic executor in a separate management container outside the experiment Incus instance. The experiment instance runs the private Docker runtime and engine on DGX Spark. Builder edits/instruments/builds; lab control stages, launches, tests, observes and returns evidence. No in-lab source workbench, rebuild or binary substitution.

**Software Factory owns the durable knowledge and telemetry plane.** Every raw trace, event/counter record, correctness result, assessment, failed/partial attempt and coverage gap returns there with identities, hashed manifest and export receipt. Lab storage is protected staging. Stop owned processes on completion/timeout; retain unexported files and do not clean them until receipt. Bounded retries/retention capacity can block new admission rather than discard evidence.

TKCC-style persistent execution is a valuable evolution. It adds engine-specific loading/reset/graph-recapture/recovery work and is not an initial dependency. No actual Muse engine/factory, Spark profiling qualification or measured performance is claimed here.

| Input | Purpose |
|---|---|
| release image + submission manifest + baseline reference | exact product, declared startup/native service and comparison |
| model pack/config/tokenizer/template | actual model/data/representation/settings identities |
| workload + independent correctness/benchmark policy | request distribution, shape/state and acceptance conditions |
| versioned playbook + resource/tool releases | mandatory stages, permitted branches, budgets/timeouts and grants |
| marker/diagnostic manifest | expected producer format, source sites and coverage/correlation |

1. Verify bytes, compatibility, required resources; launch/readiness and current generation.
2. Run supplied numerical/quality/state checks. Candidate agreement with itself is not a correctness oracle.
3. Run representative unprofiled trials with protected client/lightweight engine/host observations.
4. If unresolved, obtain a bounded Systems CUDA/NVTX capture for a declared phase/question. Analyze its saved report before recapturing.
5. If a particular kernel question remains, run a separate selected Compute capture, retaining invocation, metrics, replay/cache settings and coverage.
6. Stop/finalize owned processes; export every outcome to Factory knowledge/telemetry; retain files until receipt, then clean staging.

The executor follows the versioned playbook and permitted deterministic branches within budgets. Factory agents can analyze saved results and submit follow-up jobs through the Manager API. Failed intake, stale endpoint, timeout, denied counters, truncated reports and incomplete export stay distinct. Heavy captures never supply authoritative serving scores. No fixed universal overhead or acceptance threshold is invented.
