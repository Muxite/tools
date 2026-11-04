# Implementation handoff: prepare the M1 Capsule work

**Status: planning handoff only.** This document turns findings into inputs for the native TASK-registration process. It does not authorize implementation, allocate TASK/AC/IF identifiers, or supersede the current M1 register.

## Starting evidence

- **[IMPLEMENTATION EVIDENCE]** Reuse candidate `73ed9e8` only as a source tree and a set of candidate-specific observations. Its compiler assignment is M0-001 and its source closure is recorded in [source-baseline.json](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/source-baseline.json).
- **[IMPLEMENTATION EVIDENCE]** Current task evidence separates a final local candidate (`4b33bcb6`, 209 passed/zero skipped in its cited suite), the R07 live sample (`9227fcdb`, six expected dispositions at one repetition), R08's product completion/evidence-checker exception (`4b33bcb6`), and blocked browser/deployment checks.
- **[DESIGN AUTHORITY]** Reconcile the current [Intention Compiler build scope](../../design-package/builds/intention-compiler/README.md), [Capsule lifecycle](../../design-package/capsule/authoring.md), [node and subnode contract](../../design-package/reference/node-execution.md), [checking boundary](../../design-package/reference/checking.md), and [Capsule–routing interface](../../design-package/reference/capsule-model-routing.md) with current PRD (4) before registering dependent code work.

## Suggested task decomposition for native registration

| Label | Bounded implementation slice | Required handoff condition |
|---|---|---|
| **[RECOMMENDATION] Foundation reuse/reconciliation** | Review compiler runner, immutable capture, qualification, pinning/admission, binding, model bridge, verifier/gate, storage, and client. Reuse only compatible modules; record changed interfaces and environmental gaps. | Exact current source/contract crosswalk plus locally reproducible candidate inventory. |
| **[RECOMMENDATION] Compiler quality and environment closeout** | Resolve R08 checker discrepancy; execute missing browser and Docker journeys when prerequisites are available; repeat labeled live cases only under a frozen, authorized configuration. | Current-candidate result records with case expectations, observed results, false-accept/refusal counts, limits, and no inferred reliability rate. |
| **[RECOMMENDATION] Remaining Phase 1 capability slices** | Implement and connect Search, Screening, Hypothesis, Builder, Benchmark, Evaluation, and Delivery Capsules with separate verifier/check/gate bindings and their typed artifact handoffs, prioritizing a vertical workflow path. | Each stage tied to current PRD acceptance and architecture contract; negative/halt behavior and exact accepted output demonstrated before downstream use. |
| **[RECOMMENDATION] Phase 2 RSI slice** | Separately register bounded local-isolated RSI Target 1 against the eligible `rank_opportunities` helper, protected custodian/referee, fixtures, lineage, and human activation boundary. | Phase 1 prerequisites satisfied or independent prep explicitly documented; protected evaluation evidence remains outside mutation scope. |
| **[RECOMMENDATION] Phase 3 integrations** | Register model-router API, dynamic planning/binding, advanced compiler, and other applicable integrations only under their declared owners and phase boundaries. Preserve fixed Phase 1 fallbacks. | Cross-module IF ownership and dependency readiness recorded; unavailable owner module/API/credentials marked blocked rather than mocked as acceptance. |

## Shared coding constraints to carry into registered TASKs

- **[DESIGN AUTHORITY]** Keep declaration schema `1.0.0`; keep route profile and model-selection policy outside the Capsule declaration.
- **[DESIGN AUTHORITY]** One subnode binds one pinned CC; a verifier is a separately assigned read-only CC; deterministic checks and the protected gate retain their own authority.
- **[DESIGN AUTHORITY]** Bind accepted typed inputs and exact output/evidence identities; protect independent verifier budgets; block if mandatory prerequisites or enforcement are unavailable.
- **[DESIGN AUTHORITY]** Phase 1 stays fixed and non-interactive. Phase 3 router/API behavior cannot become an implicit prerequisite to the baseline.
- **[RECOMMENDATION]** For each new assignment, freeze PRD/package/schema/dependency/source revisions, capture exact candidate identity, run deterministic checks first, record live-model evidence separately, and leave browser/container checks explicit when unavailable.

## Entry criteria for implementation registration

1. **[DESIGN AUTHORITY]** The M1 register and owning TASK records are updated using the current Code SOP; the dossier remains subordinate working context.
2. **[OPEN QUESTION]** The Capsule inventory and task ownership split are reviewed against current PRD (4), including which work/verifier capsules are required for the intended milestone.
3. **[OPEN QUESTION]** The shared binder/router/bridge cross-module agreement has one owner and a stable native IF record; current interface changes are not hidden in copied M0 artifacts.
4. **[RECOMMENDATION]** Every implementation slice names its supported phase, positive and negative cases, prerequisites, exact evidence outputs, and what remains out of scope.
