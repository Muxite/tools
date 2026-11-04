# Very condensed design

**AI4Research M1 · experimental coder handoff · October 7, 2026**

Send this single file with the PRD received October 6, 2026. This is a deliberately lossy projection of the design-package at commit `16e1d7089`, for testing how much detailed design an AI coder can recover and implement. The existing build-package/design-package remains the maintained architecture; this file neither replaces it nor creates another maintained baseline. For this experiment, the coder's design inputs are this file and that PRD. Repository instructions, code and native coding records still govern implementation.

The PRD supplies feature requirements, exclusions, artifact names, budgets, acceptance and implementation sequence. This file supplies the essential architecture and explicitly retained decisions. Omitted detail is not permission to waive a PRD obligation. Do not routinely open the full package during the experiment: record consequential gaps rather than hiding the reduced-input condition. No implementation or acceptance is established by this document.

**Compression:** approximately 3,200 words, about 89% below the 22 design Markdown pages' 29,384 words. The comparison counts whitespace-separated Markdown words and excludes PRD/CC source files, rendered diagram pages/assets and optional development tooling. It measures document size, not retained completeness.

## 1. Product, scope and delivery

Given a user-supplied research objective, baseline and validation resources, produce cited opportunities, one selected hypothesis, a bounded POC, comparable baseline/treatment measurements, scientific evaluation and a report with traceable evidence. Negative or inconclusive science is a valid deliverable when execution and interpretation were sound. Keep scientific conclusions separate from infrastructure acceptance.

The product is user-scoped. Account/profile identity survives a workspace or run; the authorized local execution host controls access to local assets and executable research. A cloud-backed account/profile store is permitted, but does not grant cloud execution, local project access or remote control. M1 has one active authorized execution context and a sequential research run, without enterprise tenancy or distributed workers.

Keep three meanings distinct: **Delivery Phase** is a product delivery boundary; **Implementation Stage** is an engineering checkpoint; SwarmFlow runtime `phase` is an executing script segment. A workflow node is an objective instance; a coding TASK is a development record. Similar numbers or words do not make these interchangeable.

| Delivery boundary | Required shape and completion |
|---|---|
| Phase 1 — Governed Research Baseline | Fixed research workflow plus operational shell; Implementation Stages 0–7. Every governed boundary has checked evidence and durable release. |
| Phase 2 — Local-Isolated RSI Validation | Bounded offline improvement of a sandbox copy; Implementation Stage 8. Required Target 1 contributes to the core M1 gate. |
| Phase 3 — Dynamic System Integration | Attempt applicable advanced compilation, Agent Team/Cluster planning, dynamic CC discovery/binding, heterogeneous routing, alternate verifier and Code Mode. Preserve the operational fixed baseline. Record actual PASS, BLOCKED or INCOMPLETE outcomes; non-blocking does not mean optional to ignore. |

Core M1 acceptance requires PRD Definition of Done, all Implementation Stage 0–8 exits, integrated Phase 1, required Phase 2 and mandatory failure cases. A bounded first slice is not phase completion. Product-required `Phase_3_Completion_Report.md` and `M1_Implementation_Report.md` retain the PRD's accounting role; they are not additional coding approval cards.

Future compatibility may influence contracts, but fusion, interaction-screening search, mid-run installation/compensation, multiple planning epochs, remote workers, model training and unrestricted self-improvement are not automatically M1 implementation work. Do not promote a future field into an executable feature merely because a schema can express it.

## 2. System responsibilities

Use Python services, the existing TypeScript UI, one Docker application service, mounted SQLite run state and immutable artifact/evidence files. Multiple native processes may live inside the service; logical module boundaries do not require microservices. Preserve local session authentication and a loopback host endpoint. Separate persistent profile storage from disposable workspace state. Docker application packaging is not proof of generated-code confinement.

Reuse existing JiuwenSwarm/OpenJiuwen UI and transport, SwarmFlow orchestration, native harness/agent components, Symphony discovery, Codex integration and diagnostics where their actual behavior fits. Check the installed dependency before selecting an adapter. Existing caches, exception handling, retries and replay must not bypass the authority described below. Use the smallest implementation that preserves those boundaries; choose files and private helpers in native plans.

| PRD responsibility | Elaborate into these cooperating parts | Output or authority |
|---|---|---|
| Ingestion (§3.1) | Original-input capture, qualification/extraction, supplied asset binding | Qualified intake with origins; no undeclared retrieval. |
| Requirement Compilation / Intention Compilers (§3.2, §4.7) | Intent compiler and intent gate, then Requirement compiler and Brief gate | Accepted intermediate intent, then `Research_Brief.json`. |
| Planner / Harness Core (§4.8, §4.6) | Fixed graph or bounded proposal, protected binder, plan gate/freeze, scheduler, shared runner | Frozen graph and Node Execution Contracts; scheduler controls readiness. |
| Capability Capsule (§4.1) | Reusable declaration, pinned implementation/dependencies, admission/library lifecycle | Eligible versions and attributable invocations; a prompt alone is not the contract. |
| Evaluator Gate & Verifier (§4.2) | Deterministic checks, read-only verifier CC assessment, protected host decision, durable commit | Exact accepted artifacts or non-advancing outcome; host owns release. |
| Data Foundations (§4.5) | Run-state authority, immutable evidence storage, derived records and scoped exports | SQLite owns lifecycle; files preserve evidence; memory assists reasoning. |
| Models & Routing (§3.0, §4.3) | Protected audited bridge, role/profile configuration, call/time accounting | Baseline Codex access; bounded alternatives in Phase 3. |
| RSI (§4.4) | Target profile, fixed improver, isolated candidate runner, fixture oracle/referee, lineage/admission | Protected comparison evidence and inactive candidates; activation is separate. |
| Platform shell (§5) | Installation/startup, CLI/headless/Web/TUI, visibility, identity/security, terminal sessions, configuration | Operable product using the same workflow service and authority. |

The runner binds accepted inputs, invokes work or verifier CCs, enforces scoped tools/resources and captures actual execution. The scheduler selects dependency-ready nodes; the native harness supervises execution. The binder establishes contracts and checks; the gate decides acceptance; run-state commits release. Combining internal helpers must not combine their authority into a producer-controlled success path.

A **CC declaration** describes reusable capability, typed inputs/outputs, implementation identity, dependencies, effects/permissions, limits and verification obligations. A **Node Execution Contract** binds a run-specific objective, participating CC pins, actual inputs, required outputs/evidence, checks and effective limits. An **invocation** is one CC call with its own observations. Multi-CC nodes require per-call checks and aggregate node acceptance. Each CC's effective permissions are the intersection of its admission, node contract and run policy; never union permissions across CCs. Node-wide budgets include all subordinate calls.

## 3. Prepare, freeze, research, deliver

The flow is:

**Qualified intake → checked intent → checked Research Brief → binding and plan gate → frozen graph → Search & Ideation → Idea Screening → Hypothesis Generation → POC Implementation → Scientific Benchmarking → Scientific Evaluation → Delivery.**

Each work result passes its assigned gate before becoming an input to dependent work. Preparation uses protected fixed templates through the same runner and gates before the research graph exists. This lets a planner run without already possessing its own finished graph. Graph freeze authorizes research execution; preparation never authorizes execution of a proposed graph.

| Research step | Preserve this handoff and boundary |
|---|---|
| Ingestion | Bind original objective and permitted `.txt`/`.md`/`.pdf` content with supplied project/data resources and attribution. Reject empty/unreadable required input. No arbitrary repository cloning, dataset downloading or ingestion search. |
| Requirement Compilation | Extract intent without inventing solutions; distinguish mandatory outcomes, preferences, constraints, defaults and unknowns. Construct the complete accepted Brief for planning and research. Material unresolved ambiguity blocks readiness. |
| Search & Ideation | Use fixed bounded local/permitted academic retrieval. Retain citations and relevant exact excerpts; produce 1–3 grounded ideas. No open-web crawler, search swarm or autonomous query-repair loop. |
| Idea Screening | Consolidate once, score novelty/feasibility/compute alignment with reasons, filter forbidden dependencies and select Top-1. Retain rejected reasons. Preserve baseline sum and the pure `rank_opportunities` helper for RSI. |
| Hypothesis Generation | Produce one claim with mechanism, supplied baseline/data, variables, measurement definitions and pre-registered success/falsification/inconclusive criteria. Freeze the protocol before building or measuring. |
| POC Implementation / Builder | Produce bounded intervention, benchmark harness, dependency declaration and build evidence. Perform permitted local CodeSearch and mechanical readiness checks; no scientific run, dependency installation, large refactor or repair loop during build. |
| Scientific Benchmarking | Trusted provisioning installs only frozen declared dependencies under restrictions. Execute baseline then treatment with comparable hardware/data/configuration/seed policy; retain empirical metrics and raw logs. No interpretation or threshold change. |
| Scientific Evaluation | Check empirical origin, completeness and validity; apply the frozen criteria. Produce scientific verdict, limits and follow-ups. No rerun, new live leaderboard query or post-result criterion adjustment. |
| Delivery | Assemble the PRD report and supporting artifacts from accepted results, citations, protocol and measurements. Disclose warnings and negative science. Infrastructure transfers the accepted package; no external publication or knowledge write-back. |

Keep original inputs, resource references and the Brief available to authorized consumers; do not reduce the system to a chain of lossy summaries. Preserve the PRD's artifact names and export meanings. The coder owns exact wire fields and serialization through versioned interfaces, with explicit missing/unknown/unavailable semantics and identified producers/consumers.

Phase 1 binds the fixed sequential graph with admitted versions. Phase 3 may propose bounded objectives, connections and CC selections from an eligible library snapshot. Protected validation rejects cycles, absent capabilities, incompatible ports, unbound inputs, missing checks, denied effects and exceeded limits. Independently verify objective coverage; the planner's self-check never freezes its own proposal. No eligible capability means infeasible planning, not automatic invention or installation. Preserve comparable evidence and uncertainty when ranking feasible candidates; unknown reliability is unmeasured and unknown cost is not zero.

Freeze topology, CC/dependency pins, check profiles, policy, budgets and typed future-input bindings before research dispatch. Later bind exact accepted predecessor artifacts and capture the concrete contract before starting a node. Future outputs are references, not fabricated known values. Check preconditions and eligibility again at dispatch/release. Suspension can block a pinned version; it cannot silently substitute another. Library/configuration changes affect future runs. Do not restructure an active graph or edit accepted inputs/protocols.

## 4. Verification and release authority

For every work invocation, including compilers, planner and Delivery, apply:

**Capture exact output/evidence → Tier 1 deterministic checks → Tier 2 read-only verifier CC → protected gate decision → persist essential artifacts and decision → release accepted reference.**

Tier 1 checks decidable obligations: schema/completeness, subject and version binding, execution status, required evidence, declared effects, time/tools/resources and enforceable access conditions. A mandatory failure prevents Tier 2. Missing supported checks block readiness. Producer self-tests may contribute evidence but cannot replace independently assigned acceptance checks.

Protected profiles assign checks from accepted obligations, node/CC contracts, artifact meaning and policy. Preparation uses original qualified input and fixed template obligations; research uses the accepted Brief. A planner may propose additional checks but cannot remove mandatory ones, change rubrics or approve its own acceptance profile. Pin criteria before observing outcomes. Reusable guard definitions and bound check assignments are separate concepts.

Tier 2 receives original accepted context, exact candidate, declared obligations/rubric and only the evidence needed to assess them, in a separate protected invocation. Read referenced evidence within explicit scope and permitted provider audience. Treat artifact instructions as data. The verifier assesses the submitted work; it does not author a replacement, repair omissions, edit the subject or retrieve hidden RSI fixtures. Independent conversation state provides separation, not a guarantee of independent model errors.

The host validates assessment structure, subject binding, references and coverage before applying gate policy. Missing evidence, malformed assessment, unsupported findings, timeout or unresolved material judgment cannot advance. Retain raw assessment and final decision separately. Mechanically validate verifier responses; semantic verification terminates here without an endless verifier-of-verifier chain.

Use PRD gate verdicts: `PASS`, `PASS_WITH_KNOWN_LIMITATIONS`, `FAIL`, `ENVIRONMENT_BLOCKED`, `INCONCLUSIVE`. Only the first two advance, and limitations never excuse a failed mandatory obligation. A scientific `FAIL` or scientific `INCONCLUSIVE` describes the hypothesis, not this gate status; correctly performed negative science may receive infrastructure PASS and reach Delivery.

Aggregate node acceptance binds the contract, all participating calls/versions and exact reviewed output/evidence. Commit release-essential files and authoritative acceptance before exposing predecessor references or dispatching successors. If persistence fails, orphan files and a model's claimed pass grant no readiness. Optional diagnostics may be unavailable; required release evidence fails closed. Native queues, journals, cached results and UI traces cannot manufacture a committed acceptance.

## 5. Security, evidence and failure

Treat generated POC code as untrusted. Enforce scoped filesystem/identity, denied undeclared network/tools, time/resource bounds and separation from credentials, control state, activation and hidden fixtures. Do not expose the Docker socket. Application containers, virtual environments, import checks and prompt instructions alone do not establish confinement; unavailable mandatory isolation blocks execution. Enforce PRD §3.6.2's generated-code prohibition on OS/network modules, including `os`, `sys`, `subprocess`, `requests`, `urllib`, `shutil`; trusted provisioning infrastructure has a different role.

All supported model calls cross the audited bridge. Preserve protected local IPC and owned process contexts. Record effective model/role/configuration, time/calls and reliably available usage/spend; unavailable telemetry stays unavailable. Account allowance/reset data is not per-invocation cost. Keep credentials out of declarations, artifacts and evidence. Scoped exports and provider requests must respect confidentiality before disclosure; retrospective verification cannot undo an external effect or leak.

Run-state owns immutable inputs/configuration, graph/contracts, attempts, gate decisions, accepted references and lifecycle. Store exact artifacts and observed evidence with run/node/attempt/invocation correlation. Preserve failed attempts, raw assessments, version identities, tool/build/measurement logs and required evidence before cleanup. Derive Capsule Run Records, Run Bundles, conformance views and scorecards from that evidence. A scorecard neither activates a version nor proves unmeasured reliability; native memory is a reasoning aid.

Any blocking execution, security, budget, verification or storage failure stops new dispatch and contains active work while preserving available observations. Default automatic repair/replay is zero. Browser disconnection does not cancel server-owned execution. Cancellation stops new work without erasing effects; restart preserves accepted results and marks interrupted attempts paused for inspection. M1 recovery uses a fresh attributable run, not automatic in-place replay of uncertain effects.

Interactive modes expose a correlated triage request with failed obligation, subject, evidence and permitted correction. Headless mode returns non-success immediately with verdict/reason and identifiers when available; never wait for input. Human inspection, acknowledgment, environment repair or corrected input cannot override mandatory failure. Correction creates a linked new run with new configuration/binding/checks; keep the old verdict. If storage is unavailable, report that honestly instead of claiming durable triage. Avoid duplicate requests on reconnection.

Phase 1 compilation is non-interactive. Phase 3 advanced compilation may use bounded pre-acceptance clarification through the authenticated native surface, with frozen turn/time/call limits and recorded attribution. It still requires independent acceptance. Headless compilation uses supplied answers or blocks; it does not open a dialogue. Clarification is not failure-driven repair of an accepted graph.

## 6. Library and offline RSI

Publish declaration and implementation/dependency closure as immutable versions. Admission determines eligibility; activation selects an admitted default for future runs; suspension revokes eligibility; rollback retains history. Hand-authored versions also require admission. Composite declarations preserve member pins, ports, dependencies, effects and required member verification. Reject unsupported composition rather than silently dropping obligations. Metadata does not promise runtime support.

Required Phase 2 Target 1 improves a sandbox copy of Screening's pure `rank_opportunities` helper with a fixed improver. Keep the public contract, required dimensions, Top-1 behavior and effect boundary fixed; the live baseline remains unchanged. Define reusable target-profile, controller, candidate runner, referee/oracle and evidence interfaces without depending on a completed planner. Actual optimization requires the executable parent and meaningful fixtures.

The proposer sees only authorized mutable implementation, visible development fixtures and permitted aggregate feedback. Trusted enforcement outside the target rejects forbidden changes. Freeze evaluator, scoring, security, evidence custody and full affected dependency closure. RSI may not mutate contracts, gate/verifier/check assets, fixtures, activation controls, model weights or permissions. Preserve every attempt, diff, identity, budget, comparison and violation.

Separate development, hidden-loop, hidden-final and milestone data. The oracle controls hidden fixtures and lifetime queries; the independent referee scores exact parent/child under comparable settings. Preserve 30 hidden-loop queries per session, 90 per loop-set lifetime, loop feedback only passed/total/queries-left, and one terminal final evaluation. Retain the supplied calibration/headroom requirements, including at least 20 cases per hidden split, 10 known-bad and 3 known-good planted children. Hidden content/per-case answers and final feedback never enter future proposer context.

Target 1 delivers a sandbox child and paired evidence, not automatic production promotion. Admission and any eligible human activation remain separate from score improvement. Target 2 may change permitted Screening work prompt/rubric text while interfaces and verifier/referee criteria stay fixed; if bounded headless model execution is unavailable, defer Target 2 to M2 without waiving Target 1. Platform benchmarking is an ordinary scoped client comparing matched system configurations, distinct from the research Benchmark CC and protected RSI evaluation.

## 7. Retained amendments and first build

Two adopted differences must travel with the PRD: **D5** changes the literal one-generation default in §§3.2/4.7 into two bounded compiler invocations within one non-interactive entry, with independent intent/Brief gates and frozen combined budgets. **D6** adopts one Docker application service and SQLite release authority plus portable artifact/evidence files, revising packaging/container-deferral and supplementary persistence assumptions in §§4.1.4/4.5.2/5.1.2/5.2.1–2/5.4.3. It preserves authenticated local execution, separate durable product profiles and independently enforced POC restrictions. Do not describe amended behavior as unchanged PRD compliance. Other conflicts require an explicit recorded decision, following PRD §1.7.

The first build is **Intent Compilation and Verification Slice (formerly TRIAL-1)** within Phase 1: existing local web text submission → original-input/run capture → Intent compiler CC → intent Evaluator Gate → durable accepted intermediate intent or visible halt. Its verifier checks omissions, unsupported additions, constraints, scope drift and ambiguity against original input. No full Brief, research DAG, RSI execution or complete milestone is implied. Preserve historical TASK/AC/IF identities; do not reuse an occupied Codex-adapter identity for this slice. Registration is pending, not evidence of completed implementation.

Verify the connected slice with advancing input and intentional malformed output, semantic omission/invention, injected reviewer instructions, ambiguity, unavailable model, timeout, denied effects, stale/swapped artifact, persistence failure and browser disconnect. Prove no accepted reference/downstream readiness on a blocked case. Show model separation, protected policy and actual durable release; documentation, mocks and producer narratives alone cannot establish PASS.

## 8. Coder responsibility and the compression experiment

Use TASKS → owning TASK/IF agreements → one registered native Spec Kit directory. TASKS owns allocation/dependencies; TASK owns identity, scope and versioned shared interfaces; `spec.md` owns ACs, `plan.md` detailed design/procedures, `tasks.md` work and evidence correspondence. Generate concrete schemas/APIs, module decomposition, prompts, thresholds and fixtures here. Read applicable repository instructions and callers; no additional approval cards or automatic commits are introduced.

Reconstruct low-level choices using the smallest PRD-compatible design. Register assumptions and unresolved inputs in native records; continue independent work while blocking affected dependencies. Verify blocks, connected boundaries and integrated behavior against actual candidates. Distinguish PASS/FAIL/BLOCKED/NOT_RUN/STALE; retain failures and gaps. Do not broaden the assigned build simply because this file sketches all M1.

For this experiment, record the supplied PRD/design identity, assigned scope, assumptions the coder invented, questions it could not resolve, verification outcomes and any consultation of the full package. The team can then compare behavioral gaps and rework under reduced inputs. This file deliberately drops exhaustive clause coverage, full CC field inventories, payload examples, reuse audits, diagram views, detailed scenario matrices and most rationale. Successful reconstruction must be measured, not assumed from compression or document agreement.
