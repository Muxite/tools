---
id: feature-capability-capsule-factory
status: proposed
source: [[Paper2Agent Capability Factory]]; [[AI4Research Capability Growth]]; [[CC as Universal Component]]; maintained PRD V10 §§3.1.2, 4.4.3–4.4.7; design decisions D21, R5, D45–D46; Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt; Sources/Prompts/2026-10-23-m2-component-handoffs.txt
last_reviewed: 2026-10-23
next_action: Use fixed durable control with bounded adaptive agents after the manual carrier works
---
# Capability Capsule Factory

## October 23 implementation handoff

[[Resources/Handoffs/m2-labs/local-factories|Current scoped handoff]] is the implementation route. Spark is primarily a restricted benchmark host; development/builds happen elsewhere where practical. The existing no-sudo two-image benchmark workflow stays independent. VMs, a registry, shared local inference and a full capacity controller are not bootstrap prerequisites. M2 infrastructure remains unimplemented by this documentation revision. The full target below is retained; first-delivery scope and sequencing follow the handoff.


**M2 scope correction:** this factory and VM/container architecture are M2. Earlier M1-scope limitations below describe the starting baseline, not a requirement to extend M1 or obtain a new M1 approval. [[Designs/Per Lab Capability Factory Design]] is the current deployment/build design; [[Designs/Lab Capsule and Factory Design Plan]] owns M2 development order.

## Feature definition

A proposed, governed authoring workflow that turns user-authorized scientific papers and/or pinned repository inputs into reviewable resources and candidate Capability Capsules (CCs). It records provenance and evidence from source selection through validation. Outputs remain candidates until the existing admission process accepts them; generating or packaging a CC grants no permission to bind or execute it. This feature is not implemented or adopted in M1.

## Scope and stages

The pilot should demonstrate one bounded, repeatable research-to-capability journey as a **flat workflow** of separately governed stages: (1) prepare authorized, pinned sources; (2) review paper material when supplied; (3) select concrete upstream operations for a user task; (4) run upstream references in a qualified environment; (5) build a thin candidate wrapper; (6) independently compare wrapper behavior and failures with references; and (7) validate clean installation, actual calls and package contents. Paper-only input may yield a reviewed reading resource; repository-only input may yield candidate tools while explicitly recording absent paper evidence.

**M1 boundary:** Our modified AI4Research M1 design supports bounded agent/tool CCs and the protected admission/runtime path. Its integrated generic Planner does not by itself implement factory lifecycle, build permissions or admission authority; composite CC creation/execution remains outside the M1 factory delivery (D21). A product-integrated pilot requires an accepted amendment wherever its actual profile/terminal, permission or plan/binding needs change an owning contract; compare with the integrated generic Planner first and reuse native stages where they fit. Independent M2 prototypes may proceed under their own authorized scope with qualification boundaries intact. Do not describe factory automation or a composite as current M1 behavior or attribute our adapter choices to upstream JiuwenSwarm.

**Future:** Consider a composite/plannable factory only after a flat pilot demonstrates repeated value and a maintained design specifies pinned members, typed edges, member-level checks, bounded effects/budgets and aggregate acceptance. Broader self-improvement or automatic promotion is separate future work.

## Inputs, outputs and owners

Inputs: an explicit task and scope; user-authorized paper/supplement and/or repository identity/revision; available data, credentials and compute; and declared licensing/access constraints. Missing prerequisites narrow or block the affected output and remain visible.

Outputs: versioned source/resource manifests and hashes; paper review records where relevant; operation-selection rationale; environment and reference-run records; candidate CC source/declaration and change manifest; independent comparison and runtime/package reports; and a candidate package bound to those records. Keep resources/evidence, factory-stage CCs, and generated product CCs as three distinct identities.

Native owners: M1-001 for composition/native adapter and runtime qualification; M1-003/004/005 for intent, research-stage and planner/plan changes; M1-002 for store, library, binding, runner, gates and evidence custody. These are affected workstreams, not a feature assignment or acceptance claim. Preserve existing task/AC/IF identities. Admission remains under M1-002 and the established governance path.

## Two hard limits

1. **Source authority:** Current PRD §3.1.2 excludes live scraping/direct GitHub cloning during intake; R5 requires dependencies from a prepared lock catalog and D45 keeps Builder tool commands offline. Any general acquisition/preparation capability needs its own authorization, policy and provenance handoff. Public availability does not establish license rights.
2. **Assurance and execution:** Semantic Verifier remains output-only (pinned declaration plus exact output). Source tracing, changed-input comparisons, scientific fidelity and real runtime calls require distinct protected checks. A successful package build or selected-tool check proves neither scientific validity nor whole-repository correctness. Normal admission, activation and runtime controls remain mandatory.

## Build order and unresolved choices

First reconcile profile/terminal types, source-preparation policy and binder changes against PRD V10 and the maintained decisions; then choose a repeated use case, map native stages, specify contracts/evidence, and implement product-integrated changes through the owning design process. Independent M2 lab prototypes can proceed under their own authorized scope while keeping current product contracts and qualification boundaries intact. Compare it with the native workflow on matched positive/negative cases, changed inputs, failures, fresh install and unauthorized effects. Decide later how acquisition becomes a separately admitted capability, how source/resource versions and resumable partial runs are represented, which admission route consumes packages, and whether evidence justifies a composite. The proposal records no prototype, test result or architecture approval.

For stage-level evidence and source limitations, read [[Paper2Agent Capability Factory]]. For workflow-profile and whole-system implications, read [[AI4Research Capability Growth]]. This one-page definition is the fast entrypoint, not a replacement for either note.

## Per-VM deployment

The factory is part of each lab AI4R with independent jobs, versions and Docker images. Generated product CCs use the container carrier. [[Designs/Per Lab Capability Factory Design]] defines build/local-admission/contribution; [[Designs/Lab Capsule and Factory Design Plan]] connects the VM and capsule designs. The earlier scientific-source workflow remains useful; this is a local factory in each VM.

## Spark factory resource contract

[[Designs/Spark Shared Services and Storage]] makes acquisition and peak-space admission shared host responsibilities. Factories retain independent candidate histories; parent repair journeys cap attempts/new bytes and retain compact provenance instead of every image or clone.

## October 23 development-process implication

[[Activities/2026-10-23 Capsule Branches and Factory Direction]] records user-requested capsule modules and the proposed factory choice: **fixed durable lifecycle with bounded adaptive agents inside stages**. Keep source/dependency identity, declaration/check freezing, budgets, durable evidence, qualification and promotion under protected control; let agents adapt authoring/repository work within finite grants. The inspected integrated capsule source implements no demonstrated factory automation or per-capsule container runtime; earlier branch records retain their historical scope. Generalist task-bound checking is a named M1 extension on candidate branches; the factory remains M2.
