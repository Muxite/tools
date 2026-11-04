---
type: process
tags: [process]
---

# The architect's role, 25 September to 31 October

| | Role this month | Component |
|---|---|---|
| **Muk** | architect: leads the overall design; Capability Capsule owner; also codes | CC |
| Xiaoyang | primary coder; agent architecture (PRD 4.2, `Agent.md`); owns the issue template | the Default DAG, runner, routing |
| Ramika | PRD: sets M1's boundaries and acceptance | verification: the Evaluator gate |
| Saurav | blue team: attacks the design and the code | RSI, on sample DAG fixtures |

The [PRD](prd.md) decides *what* M1 must do; the architect designs *how* the inside is structured and what is possible. Where they meet is [PRD alignment](prd-inputs.md).

## What I do

1. **Keep one design.** The workflow in [six parts](../components/components.md), the [schemas](../schemas/schemas.md) between them, the [invariants](../schemas/invariants.md) and the [policy](../schemas/policy.md) shape. This vault is the source of truth; decisions are recorded in obby's Directives.
2. **Lock the schemas first.** Propose every schema, collect questions inline, resolve them, and take each page to v1: new schemas and seams are approved field by field, and adopted ones by their change list ([what to approve](../schemas/schemas.md#what-to-approve-and-what-to-adopt)). Issues are cut only against signed schemas, so each issue is isolated.
3. **Own Capability Capsule.** The Declaration, admission, the precondition evaluator, the Declarations of M1's capsules and the `make_capsule.md` experiment; how the tools that serve CC work, and when each arrives ([early and later capsules](../capsule/stages.md)).
4. **Define the seams.** Where CC connects to jiuwenswarm, Swarmflow and agent-core ([integration](../design/integration.md)), and what we ask of the teams that own them.
5. **Review before merge.** Each issue follows the [issue template](issue-template.md). The coder, human or AI, runs the `builder` checks; I run the `reviewer` checks before it merges.
6. **Code.** Proposed: the schema validator and author kit, admission, the precondition evaluator, the pass-through planner and freeze. The Default DAG script, the runner and the store go to Xiaoyang; the Evaluator gate to Ramika.
7. **Keep it honest.** Every design claim goes through an adversarial review before it is shared.

## What unblocks what

The aim is to unblock as much work as possible, as early as possible. In order:

1. **Agree the schemas the first issues touch:** Declaration, Artifact, Observation, Verification, run contract, policy `b1`.
2. **Build the records store and the Default DAG skeleton in Swarmflow**, with stub capsules and the Codex CLI connection; stand up DeepSearch and CodeSearch as services, since they cannot share our process. It runs end to end on day one.
3. **Build the runner and the Evaluator gate.** Then three streams proceed in parallel: the PRD capsules (ported skills and their Declarations), the `verifier_capsule`, and the evaluation fixtures and checks.
4. **Sample-run data from the skeleton** unblocks the parallel tracks: RSI, the dynamic planner and routing, each on fixtures, and the `make_capsule.md` experiment.

## The plan to 31 October

| When | Build step | Done means |
|---|---|---|
| first | Codex CLI connection | one model answers through JiuwenSwarm (the PRD's first step) |
| then | **B1**, Phase 1 | the Default DAG runs end to end in Swarmflow, the Evaluator gate after every step, triage through `human_session`, every call observed and pinned; the `make_capsule.md` experiment run: this is M1 |
| beside B1 | **B2**, Phase 2 | Cluster Mode, Leader Agent and Code Mode tested against the B1 baseline |
| beside B1 | **B3**, parallel tracks | RSI on sample DAG fixtures, the dynamic planner, dynamic routing; merged only after B1 is stable |

**Blue-team drills** (Saurav), each ending in a typed failure, a test and an owner:

| Attack | Caught by | Expected | Step |
|---|---|---|---|
| one byte of a stage skill changed after admission | runner | refused, `CARRIER_CHANGED`; the gate is `blocked` | B1 |
| a stage capsule calls an operator it does not pin | runner rail, permission rail | refused, `OPERATOR_NOT_ADMITTED` | B1 |
| a prompt that tries to steer the Research Brief outside the Default DAG | tier 1 `brief_matches_dag`, then the verifier | `fail`, then triage | B1 |
| a stage output that does not match its schema | tier 1 | `fail`; the verifier is not called | B1 |
| a step that runs past its token budget | Swarmflow's ledger, tier 1 `within_budget` | `blocked` or `fail`, then triage | B1 |
| `effect_class: pure` with an effect that writes | admission | rejected, `EFFECT_CLASS_INCONSISTENT` | B1 |
| a capsule call that skips the runner | review, and the missing Observation | shows as a call with no record | B1 |
| the verifier passes a report with an unsupported claim | the `judge_unmeasured` label; calibration | a known gap until judges are calibrated | B3 |

Proposed: Saurav writes the reviewer-only checks for B1 and B2, and Muk reviews them. The schema claims to attack first: that each Binding really pins the code that runs (`code_sha256`), and that no record is written twice (INV-2).
