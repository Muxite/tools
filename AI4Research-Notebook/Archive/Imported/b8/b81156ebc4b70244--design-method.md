# Design method and architectural integrity

**For design authors and human reviewers.** Question answered: what must architecture explain, how deeply, and how do we keep it coherent as it changes? Start product reading at [README](README.md). This document guides design work; it is not an additional coding-agent prerequisite.

## Purpose and authority

Architecture transfers our project knowledge to implementers: what the system is for, why its boundaries exist, what information crosses them, and what future work those boundaries must accommodate. A foundation for a house needs different decisions from an isolated concrete slab. Future context changes present design even when future features are not built now.

AI4Research supports evidence-backed research. This includes reproducing claims, designing bounded experiments and evaluating results. Long-running agent work is costly. Block a materially wrong or unusable request before spending downstream effort. Do not optimize for a plausible answer at any cost. Preserve reproducibility, traceability, auditability and readable artifacts. Optional omissions are not automatically blockers. A correctly obtained negative result is valuable research.

| Authority | Owns |
|---|---|
| Verbatim PRD | Product behavior, M1 scope, invariants and product acceptance |
| Maintained architecture | Components, connections, authority, shared representations, deployment and architectural obligations realizing the PRD |
| Native implementation specifications | Concrete realization, interface agreements, executable acceptance cases and evidence under repository governance |
| Runtime evidence | What the implementation actually did; a document or diagram cannot supply this proof |

**Implementation precedence:** The PRD owns overall requirements and required outcomes. Design interprets the PRD and owns the architecture and implementation-facing details that achieve those outcomes. If implementation guidance conflicts with the current design, follow the design. Product obligations remain binding. A change to an obligation needs an explicitly recorded, authorized decision.

Architecture can require a module-specific test because the PRD need not name every mechanism. It cannot weaken product acceptance. [Decisions](principles.md#decisions-and-source-amendments) disclose authorized departures, including D5 and D6.

## What we claim and what we leave open

| Statement class | Required treatment |
|---|---|
| Product requirement | Cite the current source; retain its exclusions |
| Authorized architecture decision | State selected behavior, authority and rationale; identify any source departure |
| Standardization choice | Specify one compatible representation; do not claim it is scientifically optimal |
| Assumption | State its consequence and how it is checked; failed mandatory assumptions block affected work |
| Implementation choice | Give purpose, constraints, expected outcome and evidence obligations; let the owning specification select the mechanism |
| Future context | State the boundary to preserve and the feature not yet provided |

Do not present guesses as facts. Do not hide a material product or compatibility decision behind “implementation detail.” Readiness requires resolved behavior at shared boundaries; it does not require a preselected private function or algorithm.

## Required depth

For each major responsibility specify purpose, inputs and producers, outputs and consumers, broad approach, prerequisites, authority, limits, failure/recovery, evidence, phase and reason for the boundary. The [component obligations](research-design.md#architectural-component-obligations) connect this standard to full M1.

Shared fields are architecture. Define their meaning, requiredness, types, identity, attribution, uncertainty and use. Use exact schemas at consequential compatibility boundaries. Other artifacts need field contracts. Manifests identify named content, versions, hashes, relationships, audience and omissions. They cannot substitute for readable, substantive artifacts. Agents must not independently invent conflicting representations.

Define **producer obligations → deterministic checks → semantic assessment → protected decision → consumer use**. Verifier CCs assess. Protected non-CC code controls progression. Work cannot self-certify. The Intent boundary is one application of this principle, not the complete system.

Future planning, new model routes and wider RSI targets need preserved contracts, lineage, permission boundaries and evidence now. They do not justify speculative infrastructure. Internal algorithms and storage/transport adapters may vary only within the declared behavior and compatibility constraints.

## Three tiers and human review

| Tier | Read to answer | Human review |
|---|---|---|
| Immediate: three-document route | What is the whole system, who connects, who decides, where does it run and what is built? | Review product intent, architecture, authority, deployment and phase coverage without opening schemas |
| Potential: selected topics | How does a responsibility work, why, and what passes or blocks? | Review affected components and both sides of changed connections; retain consequential rationale |
| Reference: contracts/examples | What information must compatible implementations exchange? | Relevant domain and interface reviewers inspect critical fields, identities, assumptions and evidence relationships |

All three tiers require human review at their relevant scope. One reviewer need not read every reference file. Authors select the affected reading set and explain its change impact. Automated checks support human judgment; they do not replace it. This is design review, not a new coding approval workflow or a runtime permission gate.

Use plain technical English and one canonical term per component. Every sentence must explain behavior, constraint, connection, rationale or review evidence. Prefer purposeful tables and point form. Shorten repetition, not information required to make a decision. Diagrams must show actual authority and label omitted repeated checks.

## Change and knock-on effects

1. Identify the source requirement, decision or assumption being changed and its phase.
2. Trace producers, consumers, artifact fields, permissions, model disclosure, deployment, persistence, inspection and failure behavior. Include indirect consumers such as exports, RSI and historical readers.
3. Change authoritative definitions first; update affected tier summaries, examples and diagrams together. Received PRD/source bytes remain immutable.
4. Determine compatibility: field/meaning changes need a version disposition and consumer migration; private changes still need affected evidence rechecking. Frozen runs and historical decisions retain original identities. Update existing repository authorities when implementation allocation/interfaces change.
5. Recheck connected scenarios and obtain human review at affected tiers. Report unresolved conditions and stale implementation evidence; do not manufacture a pass.

| Change | Typical affected boundaries |
|---|---|
| Brief metric or assumption | Intent/default attribution, planning coverage, hypothesis criteria, benchmark measures, verdict rationale, report |
| CC port or permission | Declaration/admission, binder, invocation, checks, routing/effects, library and RSI profile |
| Artifact field/version | Producer, schema/field contract, consumers, readable views, export/import and examples |
| Container or identity | Startup, published/private ports, session authentication, model IPC, volumes, isolation, doctor and clients |
| Gate or evidence policy | Check assignments, review context, release transaction, failure behavior, scheduler and invalidated verification |

Use current canonical behavior so readers do not need to reconstruct history. Existing TASKS/TASK/native specifications retain their authority. Do not create a parallel handoff or change-card system.

## Team decisions and implementation handoff

**Architecture turns product intent into work that owners and coding agents can implement.** The PRD sets product outcomes. Architecture defines component boundaries, shared contracts, dependencies, authority, failure behavior and phase evidence. Coding work is too detailed to carry the whole system picture.

### Owners decide together

There is no PM. Owners bring their component knowledge and evidence. Ownership does not grant unilateral authority over other components.

| Owner | Also responsible for |
|---|---|
| PRD owner | PRD and Capability Capsule verifiers |
| Architecture owner | Capability Capsule and end-to-end design |
| Testing and verification owner | Code evidence and RSI |
| Model-routing owner | Model routes, codebase constraints and code acceptance |

People may hold multiple roles. Roles can rotate each month. Keep decisions, rationale, component ownership and open work in Git so the next owner can continue without private handoff context.

We use impact review and recorded decisions because NASA uses them to trace changes across requirements, interfaces, risk and schedule. We are not a production team and do not need a formal board. Use a lightweight review sized to the impact. The owners affected by a shared contract, outcome, authority, phase exit or evidence change review it and make a team decision. Local reversible choices stay with the component owner, who informs affected owners.

For a material decision:

- State the question and why it matters.
- Compare options against outcomes, technical risk, schedule, interfaces and evidence.
- Record the choice, reason, owner and follow-up in the existing design and linked work records.
- Mark replaced decisions as superseded. Keep their history. Do not create a second change log.
- Keep unresolved cross-component choices visible. Continue independent work and pause only dependent work.

### Timeline and phase changes

Architecture owns dependency order, phase exits and required evidence. The team plan and task records own target dates, current forecasts and estimate assumptions. Keep targets separate from forecasts.

When a date moves:

- Show which dependencies and evidence are affected.
- Compare resequencing, scope trade-offs, available capacity and a later target.
- Let affected owners decide before changing a team commitment.
- Do not quietly change outcomes or acceptance evidence to meet a date.

At M1 close, carry accepted evidence, unfinished work, blockers, open decisions and changed assumptions into the M2 baseline. Plan dependent work from that baseline. Update architecture when obligations, boundaries or phase exits change. A schedule-only change belongs in the plan unless it changes one of those design commitments.

**Example: model access misses the M1 target.** The model-routing owner reports that provider credentials will arrive late. A mock route exists, and the static path works. The team identifies which exits require real provider access. Keep the static path as the baseline, mark the real integration blocked, and update tasks and forecast. Do not count mock results as integration evidence or weaken an exit. If the PRD allows it, the blocked route need not block the core M1 exit. The team can then resequence work or move the target with the impact visible.

### Design standards and coding handoff

Every new or changed component design must make these items clear:

- Purpose and phase.
- Inputs, their producers and qualification rules.
- Outputs, their consumers and release conditions.
- Responsibilities, authority and boundaries.
- Dependencies, limits and failure behavior.
- Checks, evidence, gates and rationale.

Use canonical names from the shared Git glossary. Link exact schemas, versions and existing Architecture Main/Context. Show the design as tasks and acceptance evidence that implementers can pick up. The implementation owner may use Spec Kit or another workflow to decompose tasks. Product interfaces and benchmark clients must not depend on Spec Kit. State which implementation choices can vary and which shared contracts require design review.

Use diagrams for flow, ownership, authority and dependencies. Keep Mermaid or other text-based diagram source as the maintained version. Treat rendered images as generated views. This gives people and agents a graph they can inspect, edit and compare. Check links, identifiers, diagram source and generated views together.

Write in plain technical English. Use normal sentence structures. Prefer lists for steps, tables for comparisons and diagrams for relationships. Keep one main point in each sentence. Reduce semicolons, em dashes and repeated prose when they make reading slower.

### Route defects to their owner

| Defect | Design-level response |
|---|---|
| PRD bug or contradiction | Record the source clause and impact. The PRD owner proposes a product correction and gets the affected team decision. Keep the received PRD bytes and revision traceable. Update architecture and coding tasks after the product obligation is resolved. Pause dependent work only. |
| Design bug | Correct the authoritative design and record the reason and compatibility effect. Update affected contracts, diagrams, references and tasks. Mark dependent evidence stale and repeat affected checks. |
| Code bug where code differs from correct design | Record the mismatch in the implementation task or PR. The code owner fixes it and verifies against the accepted design. Logs help diagnose the fault but are not the decision record. |
| Code exposes a design flaw | Route it as a design bug. Do not hide a design change in an implementation exception. |

### Git and review path

Keep drafts on the author's topic branch. Push the branch so owners can review the actual changes. Ask affected owners to review impact, contracts, evidence and diagrams. Revise from review, then merge to `main` after human review. Put scope, affected components, decision links and evidence in the change description. Update required English and Chinese counterparts in the same change. Preserve Git history and keep the maintained source beside its checks.

### Human reading length and detail

The required first-pass route is README, M1 design and principles. Keep their combined prose at or below **3,400 words**. The package checker strips fenced source blocks before counting prose. Review diagrams separately as visual summaries. If prose exceeds the target, move deep explanation to a linked topic page and keep the decision, ownership and key consequences in the first-pass route.

There is no fixed maximum for detailed component and contract pages. Keep content that resolves a boundary, decision, failure path, evidence obligation or implementation question. Link to its authoritative home instead of copying it. Prefer detail needed to decide shared behavior. Leave private algorithms to implementation plans.

### High-level design CI

Architecture maintains small scripts and reusable agent skills or workers that review changes to system design and documentation. Mechanical checks can find broken links, missing sections, inconsistent identifiers, schema/version drift, diagram-source changes without refreshed views, and missing English or Chinese counterparts. Agents can flag likely meaning drift and notify affected owners. Owners review meaning and decide changes. Agents do not silently rewrite, translate or approve consequential design.

Run checks as bounded, attributable jobs with retained results. Use Sidecar where it fits. Keep this review lane separate from product gates. Start with cheap checks and add more when experience shows value. Token counts must name the tokenizer and version. They are a size signal, not a quality score.

We are an AI-native research project without active users. We choose fast learning and novel methods over production-level stability. AI can speed up implementation, so we put more effort into verification. Use short experiments with a clear question, success measure and stop condition. Protect the operational baseline and research evidence. Measure verified results, rework and defects. AI review is useful input, not independent proof.

### Full and compact packages

Full costs more to read and maintain. Compact costs less, but may require more clarification. Maintaining both requires a second edit and review pass and creates drift risk. The October 8 snapshot measured 36% fewer explanatory words in compact (15,961 versus 25,066), with 10 compact diagram views and 26 full views. These figures describe that frozen snapshot, not current package totals. Shared contracts were preserved. No paired implementation results yet show whether compact performs as well. Use the matched experiment to compare ambiguity, compatibility defects, clarification and correction effort at equal scope. Decide from results, not size alone. Then keep one package authoritative and freeze the other as historical evidence.

## Mechanical document checks

Keep deterministic checks beside the design. The portable package validator already checks schemas, examples, local links/anchors, the orientation word target and diagram projections. Experiment checkers pin paired inputs, compare shared content and count words. Extend these tools before adding another one. Structure/link failures and file/word drift are good script targets. Token counts vary by tokenizer and model. Report them with the tokenizer and version, and do not treat them as design quality. Scripts cannot judge whether rationale is sufficient, decisions are sound or the workflow is understandable. Keep owner review and matched implementation evidence.

## Integrity review

| Pass | Required evidence of design integrity |
|---|---|
| Coverage | Actual PRD obligations and exclusions mapped to responsibilities/phases; explicit source exceptions |
| Compatibility | Producer fields meet consumer needs; versions, references, authority and human views agree |
| Feasibility | No circular prerequisites; model access, provisioned resources, isolation and persistence can coexist; mandatory unsupported assumptions block |
| Scenarios | Normal and failing connected paths, including scientific negatives, data loss, restart, unavailable services and RSI isolation |
| Mechanical/visual | Valid contracts/examples, local links, hashes, portable copy; every diagram audited and changed views rendered/inspected |
| Human | Independent immediate-route read, selected deeper review, critical field review and unresolved-question disposition |

Architecture obligations guide implementation tests: prove a real consumer uses released output, invalid output cannot release it, effects are confined before execution, and evidence reconstructs the decision. Concrete fixtures and thresholds belong to native specifications unless already prescribed by the PRD or design.

Ready to specify means no unresolved material behavior or shared-contract question. Ready to connect requires actual compatible producer/consumer evidence. Ready for M1 requires its product exits and evidence. These are different claims.

## Measuring sufficient detail

A cut-down experiment carries the same full M1 scope, separately supplied PRD receipt, decisions and authoritative contracts. Reduce explanatory depth and examples, never silently weaken obligations. Pin both input snapshots, isolate agent contexts and use matched assignments/evaluation. Measure invented interfaces, clarification, omitted responsibilities, compatibility, failure handling and evidence quality alongside input length. An Intent-only trial measures only that boundary; it cannot establish full-M1 sufficiency. Results inform later design depth; no size target proves effectiveness.

## Focused human review questions

1. Does the immediate route explain all M1 responsibilities and Docker/browser/model/isolation placement?
2. Can each consumer use the specified output, including negative and unavailable outcomes?
3. Do permissions, verdicts, decisions and persistence have one clear owner?
4. Are assumptions and future seams honest, feasible and compatible with M1 scope?
5. What changed, which evidence became stale, and what must still be demonstrated?

The [review record](coverage.md) reports performed checks and their limits. Human review completion must be recorded from actual review, not inferred from an author polishing the text.


## Reading ownership and consolidation

The immediate route is README → system architecture → principles. Phase exits and the bounded assignment are selectively required before reviewing that build. Component authors/reviewers use the second tier; implementation agents use the relevant field contracts as well. Human field review focuses on changed meanings, authority and cross-component compatibility, rather than reading every diagnostic type.

| Definition | Authoritative home | Summaries may do |
|---|---|---|
| System connections and placement | System architecture; deployment detail in placement | Identify owners and link details |
| Planning/freeze/dispatch | Workflow | Explain dependency release without restating every check |
| Independent checking and release | Guard design; exact records in reference | State who assesses and who decides |
| Scientific stage obligations | Research design | Summarize journey and valid negative delivery |
| Offline improvement | Offline RSI | Locate profile/referee/admission/activation boundaries |
| Field spelling/type/version | Exact schema or field catalog | Explain meaning without redefining representation |

Consolidate repeated explanation only after its authoritative home answers purpose, connections, approach, pass/block behavior, authority and rationale. Preserve useful examples and deeper causal explanation in the full package. [Decision review](decision-review.md) records selected tradeoffs. New comparison pairs are frozen separately; no revision rewrites an old input identity.
