# Product requirements and design documents

This guide explains what a PRD and a technical design are for, what each should contain, how to produce them, and how to keep them useful as a project changes. It generalizes lessons from the workflow PRD and milestone design in this folder; it is not a description of that product.

## The short distinction

A **product requirements document (PRD)** describes the problem and the outcomes the product or project must deliver. It establishes scope, users or stakeholders, expected behavior, constraints, and how success will be recognized. It answers: **What needs to be true, for whom, and why?**

A **design document** explains a credible technical approach for meeting those requirements. It describes system boundaries, components, interactions, data, decisions, failure behavior, and verification. It answers: **How will the system make those outcomes true, and what evidence will show that it does?**

The PRD is the source of product intent. The design may clarify consequences or expose gaps, but it should not silently change scope or acceptance criteria. When design work shows that a requirement is unclear, infeasible, risky, or inconsistent, record the question and resolve it with the requirements owner. Keep the decision and updated source explicit.

| | PRD | Design |
| --- | --- | --- |
| Primary readers | Product owner, users, engineering, delivery and review roles | Engineers, architects, operators, reviewers, and future maintainers |
| Main concern | Outcomes, behavior, scope, priority, and acceptance | Structure, interfaces, data, execution, constraints, and failure handling |
| Useful level of detail | Enough to determine whether the outcome is met | Enough to build, integrate, operate, and verify the chosen solution |
| Should avoid | Prescribing implementation without a real need; vague or untestable outcomes | Repeating the PRD; presenting proposals as facts; hiding unresolved decisions |

These are complementary records, not competing versions of one specification. A project may use one PRD and several designs, such as an overall architecture plus a feature-level design. It may also use a compact combined document for a small change, provided requirements and technical decisions remain clearly distinguished.

## What a PRD is for

A PRD gives the team a shared, reviewable agreement about the change being pursued. It lets people decide whether the work is valuable and in scope before implementation details dominate the conversation. It also provides a stable basis for design, planning, acceptance, and later evaluation.

A PRD should let a reader identify:

- The problem, its evidence, the intended users or stakeholders, and the benefit sought.
- The target outcomes and observable behavior, including important scenarios and edge cases.
- What is included, what is explicitly excluded, and any dependencies or assumptions.
- Functional requirements and relevant quality constraints, such as reliability, performance, accessibility, privacy, or reproducibility.
- Priority or release boundaries, when sequencing matters.
- Acceptance criteria: conditions that can be checked and evidence that will count as success.
- Open questions, risks, owners, and decisions that could change the scope.

The source PRD illustrates a useful pattern: it gives a visible implementation order, groups requirements into coherent workflow and foundation areas, and decomposes large areas into smaller behaviors. Its whitelist/blacklist and dependency notes make milestone boundaries legible. Those techniques generalize; the particular stages, technologies, and milestone choices do not.

### A practical PRD structure

1. **Document control and summary** — title, owner, status, date/version, decision history, and a concise problem statement.
2. **Context and goals** — users, current problem, evidence, desired outcomes, and measures of success.
3. **Scope** — in-scope behavior, non-goals, release or milestone boundary, assumptions, and dependencies.
4. **User journeys or workflow** — the end-to-end scenarios through which users realize the outcomes.
5. **Requirements** — organized by capability or workflow; each item has a stable identifier, rationale, priority, and observable expected behavior.
6. **Acceptance criteria** — testable conditions tied to requirement identifiers, including negative and failure cases where material.
7. **Constraints and quality attributes** — only constraints that matter to the decision or delivery, with a measurable target or an explicit method for establishing one.
8. **Risks and unresolved questions** — question or risk, impact, owner, next evidence or decision, and whether it blocks the work.
9. **Appendix and references** — terminology, source research, related documents, and supporting material.

This is a menu, not a mandatory long form. Keep only sections that help readers make or carry out a decision. If an item does not apply, say so when its absence could otherwise be mistaken for an omission.

## What a design document is for

A design document makes the engineering approach inspectable before the approach is expensive to change. It gives implementers enough shared understanding to build compatible pieces, gives reviewers something concrete to challenge, and records why important choices were made. It is a model of the intended system at a particular scope and point in time, not a promise that every detail is already implemented.

Good design makes the path from requirement to implementation visible. It distinguishes current verified facts from proposed structure, identifies the requirements it supports, and explains how the design behaves when inputs are invalid, dependencies fail, or the system reaches a boundary. It should be precise where a mismatch would break integration or safety, and avoid speculative detail that does not guide a decision.

### A practical design structure

1. **Purpose, scope, and status** — design owner, reviewers, version/date, target release, linked PRD and requirement identifiers, and whether the design is draft, accepted, or superseded.
2. **Goals and non-goals** — the qualities and outcomes this design must support, plus deliberately deferred concerns.
3. **System context and boundaries** — external actors and systems, owned responsibilities, inputs, outputs, and what remains outside the system.
4. **End-to-end behavior** — a flow or sequence that shows components, decisions, state changes, and handoffs. Diagrams should agree with the prose and interfaces.
5. **Components and responsibilities** — each component's purpose, owner where useful, inputs/outputs, and dependencies. State allowed dependency directions and important invariants.
6. **Interfaces and contracts** — APIs, schemas, events, command shapes, preconditions, postconditions, errors, compatibility expectations, and ownership of each contract.
7. **Data and state** — sources, persistence, identity/versioning, lifecycle, consistency, retention, migration, and recovery where applicable.
8. **Execution and operations** — runtime/deployment assumptions, configuration, permissions, observability, scaling, and operational recovery as relevant to the design.
9. **Failure behavior and security boundaries** — likely failure modes, detection point, user/system outcome, retry or recovery rule, and known limitations.
10. **Decisions and alternatives** — important choices, alternatives considered, rationale, consequences, and links to durable decision records when a separate ADR is warranted.
11. **Verification and traceability** — which requirements are satisfied by which design elements, how each will be verified, and what evidence is expected.
12. **Open issues and change record** — unresolved choices, owner and next step; then a concise log of meaningful revisions.

The milestone design used as an input demonstrates several especially reusable elements: a concrete definition of “done,” an end-to-end flow, a module/interface/ownership map, durable-record definitions, future-compatibility rules, a failure-and-defense table, and an explicit list of open decisions. A design can use different sections, but it should answer those questions whenever they matter.

## How to architect a project through the design

Architecting is the work of turning accepted outcomes into a system shape that can be built and checked. The design's sections form a practical reasoning sequence. Do not begin by naming services or drawing boxes. Begin with the behavior the project must demonstrate, then derive the flow, boundaries, contracts, and evidence from it.

### 1. Define “done” as demonstrated behavior

For each milestone or release, name a small end-to-end scenario that proves the intended capability. State the input, the observable result, and what the scenario demonstrates about the system. Then list additional conditions that must hold even if the demo succeeds, such as rejected inputs, required records, permission boundaries, or reproducibility. Separate these from deliberately simplified areas and later milestones.

This prevents a milestone from being defined only by a component inventory (“build a router and a store”). It makes scope reviewable and gives architecture a target. Every acceptance criterion should map to a demonstrated behavior, an invariant, or an explicitly deferred item.

### 2. Draw the real end-to-end flow before decomposing modules

Trace a representative request from the external actor through intake, transformations, decisions, state changes, execution, and delivery. Show:

- Which step owns each transformation and what data crosses the boundary.
- Where a human or deterministic gate accepts, rejects, repairs, or defers work.
- Which steps are control logic, which produce or assess content, which persist records, and which are external dependencies.
- The normal completion path and the important return, rejection, or failure paths.
- Where execution is observed and which record connects the actions into one run.

Use a flow or sequence diagram to expose ordering and responsibility. Label arrow meanings and distinguish current infrastructure from new components. The diagram is a compact model of the behavior, not decoration: every box and connection should correspond to prose, an interface, or an explicit external dependency. If the diagram becomes too dense, split it into an overview and focused detail diagrams while keeping names consistent.

### 3. Derive module boundaries from responsibility and contracts

Once the flow is understood, group work into modules by cohesive responsibility and change ownership. For each proposed module, write its responsibility and out-of-scope boundary, its input/output interface, dependencies, owner or owning team, and verification evidence. Then check:

- Can the module be described by a clear contract rather than by a list of files?
- Does it own the decision or state assigned to it, or is that responsibility duplicated elsewhere?
- Are dependencies directional and explainable? Identify prohibited cycles or shortcuts.
- Can a module be changed or tested without reaching through another module's private internals?
- Are proposed modules distinguished from verified repository structure?

The design's module table pairs interfaces with the existing framework extension point and an owner. This makes architectural fit and accountability reviewable together. For a project with existing code, cite actual paths, entry points, and symbols as evidence; for greenfield work, label the structure as proposed until implementation confirms it.

### 4. Specify the contracts that let modules work together

For each cross-boundary call or stored object, define the contract at the level needed for independent implementation: shape and meaning of inputs/outputs, required preconditions, postconditions, errors, identity/versioning, and who may create or change it. Add examples for complex payloads. Identify which checks are deterministic and which depend on judgment or external services.

State system invariants explicitly: properties that must remain true across modules and implementation choices. Examples include “a downstream step runs only after its prerequisite is accepted,” “the executed version is the version that was reviewed,” or “every invocation has a traceable run identifier.” Derive each invariant from a requirement, risk, or design decision and name where it is enforced and verified.

Avoid inventing a new service or abstraction for every concept. Put a contract at a boundary when multiple components need to agree, when compatibility matters, or when a change can cause silent corruption. A private implementation detail can remain in code.

### 5. Design records and state as part of the architecture

For every durable record or mutable state item, specify its purpose, key or identity, author, readers, mutability, lifecycle, and relationship to a run or entity. Explain which records are append-only or immutable, how versions relate, and how recovery or migration works where relevant. Include transient state only when its ownership or concurrency affects correctness.

This step often reveals missing architecture: if a gate needs evidence, where is it stored? If a run must be reproducible, what exactly is pinned? If a component retries, how does it avoid duplicate effects? If a record changes, how are readers told which version is authoritative? A record table makes these questions explicit and can guide schema design without duplicating every schema field into the overview.

### 6. Decide what must be true now for later evolution

Identify only future capabilities that are credible enough to affect today's interfaces. For each, state the later capability and the specific present-day constraint that keeps the path open. For example, an identifier may need to be stable across versions, or dispatch may need to consume a contract that a later planner can produce. Say what remains deferred and what should not be built yet.

This avoids two errors: hard-coding a temporary choice so deeply that the next milestone requires a rewrite, and building speculative generality without a requirement. Capture the rule in a reviewable table: future capability, required design property now, enforcement location, and milestone or decision owner.

### 7. Challenge the design with concrete failure cases

Walk the flow with both ordinary failures and deliberate misuse. For each case, record the triggering condition, the component that detects it, the expected outcome, whether execution continues, and the evidence left behind. Include failures at boundaries: invalid input, stale or changed code/data, unavailable dependency, conflicting choices, malformed output, duplicate request, timeout, permission denial, and partial completion when relevant.

The source design's “what can go wrong” table is useful because it connects each attack or failure to a detector and expected result, and it names known gaps that are not yet caught. Use the same discipline: a defense belongs in the design only if the proposed mechanism actually detects or contains the case. Label residual risk honestly and decide whether it blocks this milestone.

### 8. Keep open decisions visible until they are decided

Do not disguise uncertainty as a settled architecture. Keep an open-decision table with the question, why it matters, options or default, decision owner, due point or evidence needed, and whether it blocks implementation. When decided, move the rationale and consequences into the design or an ADR and mark the open item resolved with a link. If a default is allowed, state when it takes effect and who can object.

### 9. Close the loop with traceability and implementation evidence

Review the architecture in both directions:

- **Requirement to design:** for every in-scope requirement, identify the flow step, module/contract, and verification evidence that realize it.
- **Design to requirement:** for every substantial module, record, or constraint, identify the requirement, risk, or operational need that justifies it. Remove or defer unsupported complexity.

After implementation, update current-state architecture only when repository evidence confirms the design. Record the code version or commit inspected, paths and tests that support claims, and any deviations. A proposed design and a verified architecture overview have different jobs; do not silently make one stand in for the other.

### A design review walk-through

Use the document in this order during review: (1) read the definition of done and challenge whether it proves the milestone; (2) follow the diagram and verify every handoff and gate; (3) inspect module interfaces, ownership, and dependency directions; (4) check contracts, invariants, and record lifecycle; (5) evaluate future-compatibility rules and scope cuts; (6) walk the failure table; (7) resolve or assign open decisions; (8) trace requirements to verification. This sequence follows the design's reasoning and tends to expose architectural gaps before detailed implementation review.

## How to create the pair

Treat writing as a sequence of discovery and review, not as filling in headings from top to bottom.

1. **Establish the problem and evidence.** Talk to users and stakeholders, inspect the current workflow or system, and collect constraints. Separate observed facts from assumptions and desired future behavior.
2. **Draft the PRD boundary.** State the problem, outcomes, scope, and non-goals. Decompose broad goals into behaviors that a team can discuss and verify. Assign stable identifiers to requirements and acceptance criteria.
3. **Resolve ambiguity early.** Identify conflicting goals, undefined terms, missing thresholds, and decisions that affect scope. Name owners and the evidence needed. Do not turn an unknown into an invented fact to make the document look complete.
4. **Explore design options.** Sketch the flow and boundaries, identify dependencies and constraints, compare plausible approaches, and test the riskiest assumptions with prototypes, measurements, or code inspection when useful.
5. **Write the design against the accepted requirements.** Reference requirement IDs rather than copying whole requirement sections. Explain how components and contracts realize them; mark proposed elements and assumptions clearly.
6. **Review across roles.** Ask product or domain owners to confirm outcomes and exclusions; ask implementers to challenge interfaces and failure cases; ask operators, security reviewers, or other specialists to review the concerns relevant to them.
7. **Check consistency and readiness.** Confirm every in-scope requirement has a design path and verification method; diagrams, terms, and tables agree; dependencies and ownership are clear; and unresolved issues have owners. Record decisions and acceptance status explicitly.
8. **Plan implementation from the agreed records.** Break work into ordered tasks only after boundaries and interfaces are understood enough to coordinate. Tasks and tests should point back to stable requirement IDs and design sections.

The design process is iterative: a design review can reveal that the PRD needs correction, and requirement clarification can change the design. Preserve the chain of authority by updating the right source document and recording the decision, rather than allowing a plan, ticket, diagram, or code comment to become an undocumented substitute.

## How to maintain them

Maintain documents when the underlying intent or system changes, not merely on a calendar. Use version control and normal review so readers can see what changed and why. Assign one accountable owner to each document; invite subject-matter owners to maintain their sections or interfaces.

Update the **PRD** when user needs, outcomes, scope, priorities, constraints, or acceptance conditions change. A scope or acceptance change should be reviewed by the requirements owner and communicated to design and delivery owners. Keep completed or rejected requirements identifiable; do not silently rewrite history where the decision matters.

Update the **design** when component boundaries, interfaces, data contracts, major dependencies, execution behavior, operational assumptions, or significant failure handling change. Small implementation details that do not affect those shared decisions usually belong in code and tests. Record a durable decision separately when it has broad consequences, multiple viable alternatives, or needs a clear reversal path.

For every meaningful change:

- Identify the affected requirement IDs, design sections, contracts, diagrams, tasks, and verification evidence.
- Update the authoritative source first, then update dependent references and artifacts.
- Re-check that examples, diagrams, tables, and prose describe the same current behavior.
- Mark facts that have not been checked as unverified; attach an owner and a path to evidence.
- Record the decision, date, reviewer or approver where applicable, and effective implementation version when known.
- Label obsolete designs as superseded and link to the replacement; do not leave multiple documents looking equally authoritative.

Use a lightweight review trigger: whenever a change affects a documented boundary or contract, ask whether the PRD or design is now misleading. If yes, update it in the same work item or create an owned follow-up with a due point. Keep a small change log for orientation, while relying on version control for the full history.

## Quality checks

Before treating a PRD as ready, ask:

- Can a reader explain the problem, intended outcome, scope, and non-goals?
- Are requirements understandable and observable, with acceptance conditions that can be checked?
- Are assumptions, dependencies, and open questions visible and owned?

Before treating a design as ready, ask:

- Can implementers trace the relevant requirements to components, interfaces, and verification?
- Are boundaries, data ownership, dependencies, and important invariants explicit?
- Does the end-to-end flow cover normal behavior and meaningful failure paths?
- Are facts distinguished from proposals, and are unresolved decisions visible?
- Do diagrams, schemas, examples, and prose agree?
- Is there a clear owner and a clear signal for when the design must be revisited?

Completeness is relative to scope and risk. A small change may need only a short requirements statement and a compact design. A multi-team or safety-critical change may need formal contracts, alternatives, operations, security analysis, and separate decision records. The aim is not maximum document length; it is enough shared, current information for people to make decisions, implement coherently, and verify the promised result.

## Source examples

- [Workflow PRD](../PRD%20-%20Workflow%20(No%20Vertical%20%2B%20Foundational%20Model)%20(1).txt) — example of milestone scope, ordered capabilities, decomposed behaviors, dependencies, and explicit included/excluded work.
- [M1 design](team/M1-DESIGN.md) — example of a flow-centered technical design with a definition of done, module interfaces, records, failure analysis, future constraints, and open decisions.
- [Architecture overview template](../ARCHITECTURE_TEMPLATE.md) — a repository-level current-state reference. This is adjacent to, but distinct from, a feature or milestone design: it describes verified architecture and evidence rather than proposing the whole solution for a change.
