---
type: index
tags: [index]
---

# The workflow, in six parts

The whole system, split into six parts along the lines of who owns them. The PRD's stages map onto them as in the [overview](../design/overview.md#the-prds-stages-and-where-each-lives). Each part page shows what is inside it in one diagram, lists **how we understand it, for its owner to confirm**. Which records each part reads, writes and stores are in its page properties (`reads`, `writes`, `stores`). The picture of all six and what passes between them is on the [overview](../design/overview.md#the-system-six-parts). In the part diagrams, green is a capsule, orange our control code, purple a gate, brown a record, grey what openJiuwen already has, dashed white another part, and the dashed parallelogram the policy.

<!-- sync:components -->
| Part | Owner | Made of | Build steps |
|---|---|---|---|
| [Request to contract](request-to-contract.md) | Xiaoyang · Muk | Ingestion and intake, Intention compilation, Requirement compilation | B1 ingestion, template mapping, Research Brief; B2 Leader Agent |
| [Plan and freeze](plan-and-freeze.md) | Muk · Xiaoyang | Planner-binder, Freeze, Symphony and the CC provider | B1 Default DAG pass-through; B2 chaining beside Cluster Mode; B3 dynamic planner |
| [Run and deliver](run.md) | Xiaoyang · Muk | The Default DAG, Runner, Routing, Precondition evaluator, Observability, Delivery | B1 the Default DAG in Swarmflow; B3 fan-out, fallbacks, routing, claims |
| [Verification](verification.md) | Ramika | The Evaluator gate: two tiers, triage | B1 the Evaluator gate after every step; B3 held-out suites and calibrated judges |
| [The library](library.md) | Muk · Ramika · Xiaoyang | Admission, Library, Librarian | B1 M1 capsules and the operator whitelist; B3 suites, levels, librarian |
| [RSI](rsi.md) | Saurav | RSI (the cold path) | B3, a parallel track on sample DAG fixtures |
<!-- /sync:components -->

## What each person reviews

Everyone still signs every schema. Read in this order, and the rest only needs a skim:

1. **Your parts' "to confirm" list.** It is how we read the part and what it owes the others. Tick what is right; under anything that is not, write `> Q (name): ...`.
2. **The records your parts write.** You are their author: are the fields what you will produce?
3. **The records your parts only read.** Do they hold what you need?

<!-- sync:review -->
| Person | Parts you lead | Records they write | Records they only read |
|---|---|---|---|
| Xiaoyang | [Request to contract](request-to-contract.md), [Run and deliver](run.md) | [Intent: RawIntent and IntentIR](../schemas/intent.md), [Observation: one capsule call](../schemas/observation.md), [Artifact: what a node outputs](../schemas/artifact.md), [Verification: request and result](../schemas/verification-record.md), [Delivery](../schemas/delivery-record.md) | [Semantic contract](../schemas/semantic-contract.md), [Plan](../schemas/plan.md), [Run contract and Binding](../schemas/run-contract.md), [Declaration](../schemas/declaration.md), [Port type vocabulary](../schemas/port-types.md), [Check, test case and test suite](../schemas/checks.md), [Standing](../schemas/standing.md), [Policy: every "how" in one place](../schemas/policy.md) |
| Muk | [Plan and freeze](plan-and-freeze.md), [The library](library.md) | [Plan](../schemas/plan.md), [Run contract and Binding](../schemas/run-contract.md), [Artifact: what a node outputs](../schemas/artifact.md), [Check, test case and test suite](../schemas/checks.md), [Verdict](../schemas/verdict.md), [Standing](../schemas/standing.md), [Finding](../schemas/finding.md) | [Semantic contract](../schemas/semantic-contract.md), [Observation: one capsule call](../schemas/observation.md), [Verification: request and result](../schemas/verification-record.md), [Declaration](../schemas/declaration.md), [Port type vocabulary](../schemas/port-types.md), [Candidate](../schemas/candidate.md), [Policy: every "how" in one place](../schemas/policy.md) |
| Ramika | [Verification](verification.md) | [Verification: request and result](../schemas/verification-record.md), [Check, test case and test suite](../schemas/checks.md), [Finding](../schemas/finding.md) | [Semantic contract](../schemas/semantic-contract.md), [Observation: one capsule call](../schemas/observation.md), [Artifact: what a node outputs](../schemas/artifact.md), [Declaration](../schemas/declaration.md), [Port type vocabulary](../schemas/port-types.md), [Policy: every "how" in one place](../schemas/policy.md) |
| Saurav | [RSI](rsi.md) | [Candidate](../schemas/candidate.md), [Finding](../schemas/finding.md) | [Observation: one capsule call](../schemas/observation.md), [Artifact: what a node outputs](../schemas/artifact.md), [Verification: request and result](../schemas/verification-record.md), [Declaration](../schemas/declaration.md), [Check, test case and test suite](../schemas/checks.md), [Verdict](../schemas/verdict.md), [Policy: every "how" in one place](../schemas/policy.md) |
<!-- /sync:review -->
