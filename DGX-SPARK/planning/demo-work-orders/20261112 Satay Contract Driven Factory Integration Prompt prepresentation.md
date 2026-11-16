---
id: satay-contract-driven-integration-20261112
status: active-demo-integration
source: Sources/Prompts/20261112 Compelling Demo and Simplified Verification Direction prepresentation.txt
last_reviewed: 2026-11-12
next_action: Integrate using existing JiuwenSwarm code while preserving Run 4 and Run 5
---
# 20261112 Satay Contract Driven Factory Integration Prompt prepresentation

## Execute the smallest useful integration

Claude: finish a convincing ten-minute AI4Research/JiuwenSwarm inference-engine factory demonstration on Satay. Reuse working JiuwenSwarm code first. The immediate task is integration, explanation and demonstration readiness, not another broad engine research campaign.

Use the existing llama.cpp-to-expert-streaming demonstration as the foundation. Preserve Run 4 as the recorded fallback. Let Run 5 finish under its existing source, contract, evaluator and resource identities. Do not restart it to introduce the architecture below. Develop changes without interfering with its measurements, and enable them for subsequent work or a short separately identified demonstration.

The supplied operator update reports Run 4 integrated five components, retained two and reverted one, and improved from 904 to 785 ms/token with byte-identical output. Verify its actual records before publishing. Those numbers imply approximately 13.2% lower time per token or 15.2% higher token throughput; do not confuse the percentages. They are distinct from the meeting's reported 16–23% RSI runtime improvements across two capsules.

Run 5 reportedly adds readiness counters, in-flight read join, decode-phase counters, purpose-specific module acceptance and a revisable task graph. Inspect the local implementation before doing any work: these may already satisfy much of this assignment. The operator's five-to-six-hour estimate is a historical estimate, not a fresh deadline or guarantee. Read the actual job state.

## Optimize for the most compelling real demonstration

The priority is the strongest interesting demonstration we can deliver, not merely minimum compliance with a diagram. Be ambitious about what the audience can understand and witness, while concentrating implementation on the moments that make the capability unmistakable.

The opening promise is concrete: “This large MoE is larger than Satay's available memory. Watch JiuwenSwarm use reusable engineering capabilities to improve the working engine, explain what changed, and adapt when evidence changes the plan.” Resolve the actual model and memory figures from the run.

Build the story around three memorable moments:
1. **See inside the engine.** Show actual selected experts and weight readiness, with a small before/after timeline that explains the stalls expert streaming addresses. If a signal is unavailable, show that honestly and use the strongest supported view.
2. **See the system change its mind.** Show one consequential choice: retain useful instrumentation despite no speed gain, abandon an ineffective setting, reuse an existing build, or add a missing measurement. Connect the observation to the revised action and preserved work.
3. **See a working improvement.** Connect the capsule, meaningful source change, built image, real generated output and directly measured result. Make the mechanism and result readable on one screen.

Prefer Run 5 if it supplies a clearer, fully supported story; prefer Run 4 if it supplies the stronger complete evidence. A newer run or a larger number of components is not automatically a better demonstration. Combine labeled evidence from separate runs only when their boundaries are explicit; never imply one continuous run produced everything.

Make the role of the CC clear: it brings reusable engineering knowledge, components and executable abilities that build expert streaming into an existing engine. Show enough of its guidance and invocation to distinguish this from replaying a prepared shell script. Show the real JiuwenSwarm task, not just a narrated recording of manually applied patches.

Use exactly two opening slides, then spend most of the time on actual behavior. A suggested pacing is 0:00–1:30 for orientation, 1:30–2:15 for the working baseline/task, 2:15–4:30 for CC use and source/build evidence, 4:30–6:30 for expert activity and the changed decision, 6:30–8:45 for the result, and 8:45–10:00 for what is reusable and the RSI handoff. Adjust this in rehearsal; it is not an execution script.

Keep the detailed ontology, source map and profiling tables in backup views. Prepare a concise explanation at each screen transition. Make recorded, live and reconstructed views distinguishable without distracting from the story. Rehearse the actual ten-minute sequence and remove anything that does not explain the capability, the mechanism or the evidence.

## Explicit permission to simplify the old restrictions

The user authorizes loosening the original AI4R restrictions and verifier architecture for this engineering workflow. Faithful reproduction of the old gates is not a goal. Do not reintroduce mandatory verifier agents, fixed output-port chains, a semantic review after every tool call, repeated approvals or serial compiler/planner ceremonies solely because old M1 documents contain them.

Retain a useful responsibility when it earns its cost; simplify or remove redundant machinery. A verifier can be a targeted deterministic check, an existing lab evaluation, or a focused review when semantic judgment is actually needed. It does not have to be another LLM agent or a distinct service. Low-risk inspection, ordinary source edits, guidance updates and presentation changes should not trigger a full acceptance pipeline.

The planner may explore, compose capabilities, revise pending work and request missing measurements within the authorized task. Grant access to the task resources it actually needs rather than forcing every read through a predecessor. Reuse working checks and release evidence instead of asking every action to prove the whole system again.

Keep a small set of credibility and execution essentials: identify what ran; retain actual failures and observations; keep comparison criteria fixed for scored attempts; prevent conflicting heavy jobs; respect cancellation and the task's resource budget. These support a trustworthy demo. They do not require restoring the old verifier hierarchy.

Document what was deliberately relaxed, what remains enforced in code and what relies on the trusted local operator/agent. Do not claim sandboxing or independent verification that the implementation does not provide. If an existing restriction blocks a useful authorized action, simplify it deliberately and record the change; do not silently bypass it while claiming the old guarantee still holds.

Evaluate integration choices by whether they improve engineering freedom, useful progress, recoverability and clarity of evidence. The target is a capable iterative software factory with a convincing demonstration, not an elaborate compliance exercise.



## Architecture proposal and authorized design change

Use a contract-driven, continuously revisable engineering loop:

Task and domain context -> accepted objective/constraints -> next useful actions -> resource-aware execution -> evidence and assessment -> revised next actions, until the objective is satisfied, further progress is unjustified, or the resource budget is exhausted.

Keep meaningful Intention Compiler, Planner, Task Graph, Scheduler and Verifier responsibilities. They do not need to be five new services, five LLM calls or five mandatory serial steps. Map the responsibilities to existing code. Do not add ornamental boxes that do not affect execution.

The accepted contract holds the outcome, constraints, resource ceiling and evaluation obligations. It does not freeze the engineering route. Commit only the currently justified actions, retain tentative future work as revisable, and reconsider affected work when evidence changes.

A DAG is a useful representation of dependencies at a particular revision. A frozen end-to-end execution policy is the restriction being replaced. Repeated attempts and plan revisions have distinct identities; history remains append-only even when the pending plan changes. Do not claim DAGs inherently cannot support iterative systems.

The illustrative ten-step argument is conditional: ten independent, mandatory steps each succeeding with probability 0.9 produce 0.9^10 = 34.9% probability that all succeed, with no retry, recovery or alternative route. It is not a measured AI4R failure rate or proof that this design achieves a particular reliability gain. Demonstrate actual recovery and preserved work instead.

This is a substantive user-authorized change to the M1 freeze policy, using the CC-v2/factory code and retaining genuine AI4Research-Main lineage. Record the departure in the owning design/task records. Do not claim unchanged compliance with the old no-replan clauses. Do not build an adapter that routes this workflow back through the frozen scheduler, or merge/reset an active branch merely for appearance.

## Reuse map: inspect before implementing

The read-only source inspection found these existing pieces. Verify current local versions; the supplied Run 5 changes were not present in the inspected remote factory snapshot.

| Existing JiuwenSwarm owner | Reuse or extend for this assignment |
| --- | --- |
| research/compiler.py, IntentionCompiler; accepted Research Brief concepts | Preserve intent, constraints, resource references, uncertainty and provenance. If the factory already has a sufficient pinned brief, map and validate it; do not require a redundant compiler journey. |
| factory/controller.py, Controller | Existing evidence-driven agent loop, snapshots, reconciliation, budget tracking, run/resume/cancel. Make its planning responsibility explicit and add only missing graph/contract behavior. |
| factory/store.py, Store and ScopedStore | Existing observations, evaluations, artifacts, attempts, scoped reads and advance_decision(expected_rev). Reuse this durable shared state; do not introduce another database or event bus. |
| factory/jobs.py, Jobs | Existing durable submission, fingerprints, retry/status/cancel and queue integration. Extend resource coordination only where a real bypass or gap exists. |
| factory/manager.py, Manager | Image admission, immutable image checks, lab submission and evaluation boundaries. Preserve these; do not let planner output replace them. |
| factory/builder.py, build_job.py, components.py; existing builder/inspector/lab_client/evidence capsules | Existing build, integration, inspection and evidence actions. Reuse real CC invocations and artifacts. |
| ccv2/agent_mcp.py and existing CC runtime | Discovery, declarations, module execution and grants. Extend the current format only if required by a concrete missing capability. |
| factory/story.py, export.py, replay.py | Extend existing story/replay with ontology labels, current graph and evidence-backed decision changes. Avoid building a new dashboard framework. |
| research/planning.py, binding.py and planner catalog | Reuse suitable validation, eligibility and vocabulary. Do not import their whole-run freeze assumptions into the iterative path. |

The current controller may already serve as the planner and Jobs as the scheduler. That is acceptable if the responsibilities are real, visible and exercised through the JiuwenSwarm entrypoint.

Show a concise before/after source map: existing file/symbol, retained behavior, actual changed behavior, and evidence of execution. A diagram alone is not integration.

## Input: a small inference-engine ontology slice

Treat an inference-engine ontology as domain input to this task. We do not need to finish the whole ontology or create a universal ontology platform. If a maintained ontology exists, reuse its identifiers. Otherwise introduce an explicitly provisional, versioned slice for this demonstration.

It should identify:

- Engine revision, source tree, component, build artifact and runnable image.
- Model and quantization; workload and correctness/performance contract.
- Engine layers: startup, API, request scheduling, generation loop, model operations, kernels/runtime, hardware, and cross-cutting memory/state.
- MoE router, selected expert, expert weight range, prediction, read request, readiness, execution placement and memory budget.
- Observation point, quantity definition, observation, assessment and supported claim.

Useful relationships include component implements capability; component modifies engine region; operation reads weight range; expert executes on compute unit; observation measures quantity for an identified subject; image built from source; assessment evaluates artifact under contract.

Link expert streaming to L3 generation timing, L4 routing/expert execution and M memory/readiness. Include L5 CPU/GPU work where observed. The domain model must allow experts to execute on CPU: do not repeat the meeting minutes' unqualified “SSD to GPU memory” description as an implementation fact. Existing fill/pregate behavior can improve access to mapped expert weights without moving expert computation to GPU.

Use the ontology operationally in at least two places: selecting/explaining relevant capabilities, and declaring/interpreting required evidence. It should help the system recognize that prediction recall and ready-before-demand are different quantities. Loading an unused JSON file or painting ontology labels over an unrelated execution is insufficient.

Keep the engine's request scheduler separate from the factory's engineering-job scheduler in code descriptions and presentation diagrams.

## A small node ontology within that larger vocabulary

A node is a bounded unit of engineering intent in a task, not necessarily one tool call, one capsule, one agent, or a transformer layer. It may use several tools or CC modules. A reusable workflow fragment is a pattern of such intents, with applicability conditions; a node instance is bound to this task.

Use the existing records wherever possible. Define these meanings without requiring a new DSL:

| Concept | Minimum meaning |
| --- | --- |
| Task contract | Objective, constraints, domain-context version, resources, budget and acceptance obligations. |
| Plan revision | Current justified work, tentative work, evidence consulted and reason for change. |
| Work node | Identity, desired outcome, affected domain entities, required evidence/preconditions, eligible capability, expected artifacts/observations and resource needs. |
| Attempt | One immutable dispatch of a node with resolved source/artifact/configuration/CC/contract identities and job identity. |
| Dependency | A genuine prerequisite, such as an identified successful build before running its image. It is not a requirement to pass all knowledge through the preceding node. |
| Observation | A measurement or fact with subject, source, units/boundary where applicable, time and validity scope. |
| Assessment | A judgment under a pinned criterion, distinct from execution success and raw evidence. |
| Decision | Keep, reject, inspect, retry, replace, defer, stop or supersede, with supporting references. |
| Resource claim | What an attempt needs exclusively or within a budget, resolved by the existing scheduler. |

Useful node intents are inspect, integrate, build, measure and assess/decide. These are not a compulsory five-stage pipeline. A task can reuse a valid image, ask for new evidence, skip inapplicable work or compose an alternative.

Pending nodes can be superseded or blocked. Running attempts retain their actual bindings. Cancellation must record whether the job stopped; superseding a node does not magically cancel its process. Failed attempts remain evidence. Success is scoped: execution succeeded, evidence complete, correctness passed and performance improved are different statements.

Provide one concrete instance for expert streaming: objective “make selected expert weights ready before use”; references to the engine/model/workload; a readiness measurement requirement; the selected component/CC; a build/run dependency; and an acceptance rule appropriate to the module. Resolve it from real records, not invented sample evidence.

## Shared environment and evidence, with precise dependencies

Most relevant information already lives in the source checkout, model files, CC library, image store and evidence database. Nodes should query authorized shared resources by identity. Avoid copying complete state through successive node output messages.

The old main scheduler already supports stored accepted references and host inputs as well as future-output bindings. The improvement is flexible access and planning over current shared evidence, not an assertion that old nodes literally transferred all data directly.

Shared state must remain inspectable and versioned. A mutable checkout path is not enough to identify an experiment. Record the source revision and relevant dirty diff or snapshot, image digest, effective settings, model/workload identity and observation scope. Reuse existing snapshot machinery rather than inventing it.

Before dispatch, validate the decision revision and relevant preconditions. If new evidence invalidates a pending action, replan only the affected work. Preserve unrelated successful artifacts. Dependency edges explain true ordering; artifact references explain what was consumed; evidence references explain why an action was chosen.

Do not treat all available files as automatically authorized or trustworthy. Retain current scoped access and protected evaluation boundaries. Shared environment does not mean unrestricted cross-task access.

## Real planner and scheduler behavior

The planner chooses useful next work from the contract, current evidence and reusable fragments. It can retrieve a known integrate/build/measure fragment, combine it with a readiness-instrumentation fragment, and omit or replace a step whose prerequisites or expected value no longer hold. Reuse current catalog/fragments where they exist; do not create a workflow-search research project for the demo.

The scheduler decides what can run now given dependencies, resource availability, cancellation and budgets. It must prevent heavy compiles and lab measurements from colliding on Satay. The inspected Jobs implementation already claims shared build/GPU serialization: find and close bypasses in worker procedures before replacing the queue. Do not rely on watchdog termination and reruns as the normal scheduling policy.

Resource release requires actual process/job reconciliation. A stale lease timeout is not proof that an old process stopped. Running work must remain discoverable after a controller turn ends or reconnects.

Replan on relevant new evidence: incompatible patch, build failure, missing observation, failed precondition, unavailable resource, ineffective component, or evidence that a better route exists. Avoid a costly LLM planning round for every heartbeat or unchanged status poll. Use maximum wall time, model/tool cost and hardware budgets with progress-aware stopping, not a requirement to exhaust a fixed number of candidates.

Keep the best qualified result available. An inconclusive experiment or failed optional component need not erase a successful engine. Infrastructure failure is distinct from a scientific negative; retry only when justified and within the remaining budget.

Pin each attempt's evaluator and comparison reference. An observability module is evaluated on signal validity and declared overhead, a performance module on supported performance benefit and correctness. Replanning must never silently weaken the judge. If a criterion changes legitimately, create a new declared contract and fresh supporting evaluation.

## What to show: one genuine plan revision

Select the clearest actual evidence-backed revision from the existing runs. If Run 5 already provides one, use it. Otherwise demonstrate a small new task through the integrated path without rerunning the full engine campaign.

The screen should show:

1. The accepted objective and supplied domain context.
2. The current small graph, selected reusable actions and resource queue.
3. The observation that changes the situation.
4. The pending node or assumption that becomes invalid.
5. The revised action, why it is useful, and previously completed work retained.
6. The real CC invocation and resulting artifact/evidence.

A failure recorded earlier can be replayed and labeled. A controlled failure exercise must be disclosed. Do not fabricate spontaneous recovery or present a retroactively drawn graph as the planner that ran the historical task. If Run 4 lacks the new graph, label its view as a reconstruction from recorded evidence.

## Ten-minute presentation

Keep exactly two opening slides.

Slide 1: llama.cpp architecture on Satay, the large-MoE memory problem, and the exact integration points of expert streaming. Show CPU experts where applicable.

Slide 2: intent/contract plus domain ontology -> revisable planner/task graph -> resource scheduler and CC execution -> shared evidence and assessment -> next decision. Place the shared environment beside the loop. Show which JiuwenSwarm pieces are reused.

Then show the working baseline, a real task instruction, CC-guided source changes, actual image build receipt, expert activity/readiness evidence, one meaningful plan change and direct baseline-to-final result. Use labeled recordings for long builds and runs. Put ontology details and source mappings in backup material.

End by identifying the versioned CC and evidence handed to RSI. The factory improves an engine during this task; the next presenter improves the reusable capability for future tasks. Their segment is separate. Do not add a new RSI optimization campaign to our ten minutes.

## Speed, parallel work and minimal validation

Claude coordinates multiple Codex workers at the maximum supported reasoning setting, recording the actual configuration rather than inventing “Codex max” flags. Use parallelism for independent code reading, small integration changes, presentation and evidence packaging. Reserve the hardware queue for the active measurements.

First identify already implemented requirements. Then implement the smallest missing behavior. Do not duplicate a Run 5 task graph, redo accepted component builds, migrate to a new store, build a general ontology service, replace the frontend, or add broad profiling/placement experiments to the critical path.

Use existing tests and targeted checks for changed behavior. The essential checks are: stale decisions do not dispatch; revising pending work preserves completed and running attempt identities; reconnecting does not duplicate a job; conflicting heavy work cannot run together; and acceptance remains tied to the correct artifact and contract. Reuse existing coverage and combine checks where practical. Do not build an exhaustive new testing framework.

Only rerun engine evaluation when changes affect the measured engine, configuration, workload or relevant conditions. A new graph label or explanatory view does not require another multi-hour model campaign. Reuse Run 4/5 evidence only within its actual validity scope. Keep the planned final untraced comparison if needed to support the final image claim.

Prioritize: protect current runs and fallback; reuse/map existing architecture; close missing planner/scheduler/ontology behavior; verify those boundaries; finish the visible story. Broader adaptive placement and profiler research from the earlier prompt remain optional work after demonstration readiness.

## Completion and return

Deliver working changes in the existing JiuwenSwarm branch, not a separate conceptual prototype. Preserve real M1 ancestry and record the authorized policy change in maintained design/task records.

Return a short implementation summary with:
- What already existed, what was reused, and the exact remaining code changes.
- The small domain/node vocabulary and where it actually affects behavior.
- One real task invocation, its graph revisions and evidence-backed decision.
- Reconciled Run 4/5 status, exact result provenance and selected demo path.
- Two slides, existing story/replay updates, runbook and RSI handoff.
- Checks actually run, meaningful limitations and unresolved items.

Do not claim a new universal reliability rate, an unmeasured engine improvement, or completion of the entire AI4R ontology. The finish line is a clear, working, traceable integration demonstration.

## Source inspection receipt and precedence

Read-only inspection on November 12 resolved remote branch heads directly with git ls-remote; an older local origin/AI4Research-Main tracking ref differed, so it was not used as the current authority.

- AI4Research-Main: 141c1c401138f916af0a41aca791adf226d814c7.
- ai4r_M1: 32c77d69d7b64705194dc56d5aac39d02be4924e.
- ai4r_M1plus: 98c6d01bf0d9680ef6175842ac7dc66bc9894ec2.
- ai4r_ccv2: 2889a1d6342e9baa7721648eca196bbce79a31d4.
- ai4r/iterative-cc-factory: b1cee120b851de5ce82d279689c726f4a9f7a904.

Main's docs/architecture/design-package/reference/run-plan.md says no replan, substitution or pin change after freeze; research/scheduler.py execute_plan requires plan['frozen'], resolves future outputs against the frozen producer/dependency and skips work whose predecessors were not accepted. The inspected M1 and M1plus schedulers retain that restriction. Main supports a bounded linked continuation for infeasible planned runs; it is not completely devoid of replanning, but it does not provide the desired in-run revision policy.

The factory snapshot already has Controller, Store.advance_decision(expected_rev), durable Jobs, Manager admission, and story/replay support. It still contains a speed-based keep_component check requiring ratio > 1. Run 5 reportedly has newer module-specific acceptance and graph work; verify local changes before modifying either. Remote source inspection is not runtime validation, and the operator's Run 4/5 report is not independently verified by this document.

The meeting's “9 capsules and 12 modules” is a dated report. Reconcile current discovery counts and distinguish converted executable modules from planned/catalog entries rather than silently replacing one count with another.

This prompt governs immediate integration and presentation priorities. The earlier expanded expert-streaming prompt remains background for deeper engine development; it must not add optional research to the demo's critical path. The profiling PDF is a proposed Strata/Spark reference, adapted to actual llama.cpp/Satay behavior. New meeting evidence supersedes the earlier “meeting notes pending” status. Original source records remain historical and unchanged.

