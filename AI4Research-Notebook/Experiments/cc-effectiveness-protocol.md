---
id: cc-effectiveness-protocol
status: proposed
source: jiuwenswarm/docs/architecture/design-package/README.md; jiuwenswarm/docs/architecture/design-package/2-capability-capsules.md; AI4Research_private_planning/cc-plan-approved-revision-2026-10-14-r2/oneshot-study.md
last_reviewed: 2026-10-20
next_action: Audit runnable M1 adapter; freeze development cases and custodian-held heldout manifest before any run.
---
# CC versus plain-agent research protocol

> **Proposed and unrun.** Six development cases span experiment-specific intent/brief adapters and day-to-day research work. No results, wins, or held-out outcomes are asserted.

Links: [[Workstreams/CC Effectiveness]] · [[Workstreams/Lab Infrastructure]] · [[Home]] · [[Resources/M1 Readiness]]

## Question and scope

For bounded daily research tasks, does a workflow using explicit capability capsules (CCs) produce better independently scored deliverables than a plain agent given the same task, model, tools, evidence, and limits? The treatment is the deployed CC workflow bundle. This pilot does not identify the separate contribution of each CC component or establish general superiority.

## Tasks and readiness boundary

The six development cases cover intent and brief adapters, routine code repair, experiment design, result reporting, and literature synthesis. They use self-contained synthetic fixtures; prompts and development scoring keys are in [[Experiments/Development-Cases/README|Development Cases]]. A runnable M1 adapter is **pending code audit**. Before execution, confirm the repository supports the needed artifact interfaces, CC versions, run capture, isolated workspaces, and scorer handoff. The M1 architecture pages describe design contracts, not proof that this particular pilot adapter is implemented.

## Matched conditions

| Dimension | CC condition | Plain-agent condition |
|---|---|---|
| Workflow | Frozen CC set and contracts; record CC IDs/versions and execution trace | One general-purpose agent without CC-specific templates |
| Model | Same provider, exact model/version, sampling settings, context limit | Same |
| Tools | Same tool allowlist and versions | Same |
| Evidence | Same frozen prompt and fixture bundle | Same |
| Budget | Same wall time, model calls, tokens, tool calls, output-size caps | Same |
| State | Fresh directory and conversation; no cross-run memory | Same |

Pin runner image digest, OS/runtime, dependency locks, CC declaration/body/check hashes, model endpoint, tool versions, prompt/fixture hashes, rubric and analysis version. Compare paired environment `model`, tools, and limits in raw records. Provider model drift or missing pin is an explicit limitation and may invalidate a pair.

## Pilot and scoring

Run three paired repetitions per development task. Randomize which arm runs first within each pair and counterbalance order within task. Give each attempt an identical frozen prompt/fixture and pristine state. Record failed, interrupted, capped, and invalidated runs; do not repair outputs.

Score blindly on four equal-weight 0–4 dimensions: factual support, task coverage, reasoning/synthesis, and usability/format. Task-specific criteria and critical errors are in the development case key. Scorers see only prompt, fixture, artifact and key. A second scorer adjudicates any 2+ point dimension disagreement. Preserve initial scores and adjudication. Primary endpoint is CC minus plain total score in complete valid pairs. Report dimension outcomes, critical errors, paired time/usage metrics only where both sides measured them, per-condition resource measurements for all runs including failures, status counts by condition, per-task summaries, and excluded-pair reasons. A separate exploratory sensitivity summary may include otherwise comparable completed pairs with documented deviations; label it exploratory and keep it out of the primary endpoint. Null remains unavailable, never zero.

Three repetitions per task are an operational feasibility/rubric pilot, not a basis for statistical generality. Report descriptive distributions and no significance claim. The analyzer retains failures, excludes non-completed or protocol-deviant pairs from the primary endpoint, and does not hide missing measurements: [raw-results schema](raw-results-schema.md), [analysis script](tools/analyze_pairs.py).

## Held-out protection

At least three held-out cases are planned. An independent custodian creates and locks their identities, prompts, fixtures, and keys in a restricted manifest before proposer design/tuning. This notebook has no held-out prompt or answer material. The proposer sees development cases only. Score held-out outputs after both arms complete, under blind IDs. Any leak retires the case before evaluation. Never fabricate or infer held-out outcomes.

## Interpretation and Spec Kit

A CC comparison measures the bundle as deployed. Spec Kit is a capability hypothesis for producing specification artifacts; it is not automatically activated by a task type. Any claim about its benefit requires a separate matched comparison with pinned conditions.

Related design: [[Designs/cc-containerization-and-lab-isolation|CC Containerization and Lab Isolation]] · [[Designs/skills-to-cc-mapping|Skills to CC Mapping]].
