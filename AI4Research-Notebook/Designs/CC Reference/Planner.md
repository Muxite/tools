---
id: m1-cc-planner-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/planner.py; research/native.py; research/planning.py; research/binding.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Planner

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate. [[Activities/2026-10-23 Required M1 Planner]] and [[Activities/2026-10-23 Final M1 Merge]] supersede the one-shot/no-repair details for integrated typed planning: generic compatible graphs and one bounded structural correction are supported in source. Scientific release obligations remain; live execution is unqualified.

`research.planner` emits one data-only proposal from a frozen Brief, library snapshot, resource inventory, and plan policy. It proposes; it does not install capsules, grant effects, run checks, call tools, or decide acceptance. A static authored graph is also supported, so the planner is not necessarily active in every run.

**Ports.** Required inputs are `brief` (`research-brief:2.0.0`), `library_snapshot` (`library-snapshot:field-contract:1`), `resource_inventory` (`resource-inventory:field-contract:1`), and `plan_policy` (`plan-policy:field-contract:1`). Output `plan_proposal` is `plan-proposal:field-contract:3` (`research_assets/planner/planner.declaration.json`).

**Call and limits.** The capsule invokes `NativePlanner.propose` once. The native adapter verifies the pinned OpenJiuwen runtime; its Leader harness has text-only messages, no tools/subagents/skills or task loop, one governed bridge call, zero SDK retries, and bounded wait (`native.py`). Declaration budget is one model call, zero tool calls, 120 seconds; no network. This is an implemented adapter path in source, not proof that a live path was run.

**Checks and policy.** Proposal parsing preserves malformed candidate bytes for protected checks; a textual `INFEASIBLE` is captured and halts the plan. Host binding checks schema, Brief coverage, active library membership and planner selectability, port compatibility, dependency closure, acyclicity, one Delivery leaf with required Evaluation ancestry, mandatory check bundle presence, effect/network/resource feasibility, budgets, and whether suggested checks are known (`planning.py`, `binding.py`). Mandatory stages and checking profiles remain protected. The planner receives a frozen snapshot, not live library access. Optional compatible gates may be candidate choices only when admitted and policy-eligible.

**Failure and interpretation.** A structurally valid graph can still be poor or omit semantically useful work: source explicitly says quality and meaning are not verified, and coverage is checked by identifiers. A rejected proposal is not an accepted plan. Model-reported infeasibility, invalid proposal, binder rejection, and runtime failure are distinct outcomes and should not be collapsed. The controller can create a linked bounded rerun after a rejection/failure, but this is not a same-attempt automatic model repair loop.

**Planner-breadth test.** For each case, record available candidate pins, selectable flags, required-stage policy, resource inventory, maximum nodes, effects/network ceilings, plan-source mode, proposal, and each binder reason. Test a newly admitted optional gate that is compatible and eligible, a gate blocked for a known effect/resource reason, and a case where mandatory controls prevent relaxation. This distinguishes absent catalog entries, policy constraints, and poor model selection. No evidence currently proves the live planner is starved.

**Evidence and limits.** [[Designs/CC Reference/Source Map]] links the carrier, prompt, declaration, adapter, checks, and focused test files. Tests do not establish live proposal quality or candidate-breadth performance.
