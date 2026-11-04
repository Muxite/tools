# Capability Capsule: a declarative schema for AI4Research on openJiuwen

Merged report, 2026-09-22. Muk Chunpongtong. It merges the workshop companion (`../deck/companion.md`, schema v1.6)
and the independent report (`../alt/REPORT.md`), which both stay unchanged. The schema is `SCHEMA.md` v2.2 in this
folder; it wins where this report differs. *Code* facts give file and line, checked in source (agent-core `e23806c1`,
AI4Research `b0bf165f9`); **(design)** marks a decision the evidence motivates but does not prove. Every cited paper was
read in full; numbers and pages are in `../verify/PAPER-LEDGER.md` and `../alt/READ-LOG.md`. "Today" means the existing
AI4Research harness. The openJiuwen-based system does not exist yet; where this report describes it, it says what it
would do.

**v2.1 (overnight, 2026-09-22).** One pass asked what all the evidence together says the schema must be:

- the papers;
- the AI4Research workflow;
- agent-core;
- jiuwenswarm, which v2.0 had barely read.

The matrix is in `DERIVATION.md`. The changes:

- overlays (evolved experience, TTSE guidance, hot-loaded packages) are hashed and pinned;
- RSI's own gate is builder evidence, not admission;
- composites are gated by their members' Standing, as jiuwenswarm's SkillPacks already are, but by hash;
- a Binding carries pre-approved fallbacks, as today's freeze does;
- whether a predicate can be evaluated at planning is computed from upstream effects;
- the tool set a capsule may call can be enforced at tool-call level, though its effects are enforced only in the
  sandbox.

An adversarial review then corrected the first draft. Team skills stay out of v1, because their Leader plans. RSI's
held-out split needs a code change in RSI, not a setting. The review log is `../verify/V10-overnight-20260922.md`.

New sections: §10.8 and §11.4.

**v2.2 (2026-09-22).** v2.2 restores the self-improvement design of the 2026-09-15 capsule report, which v2.1 had
dropped:

- the goal the schema serves;
- the three clocks;
- the generalist capsule;
- the cold path's separated roles;
- monotone versions;
- protected components;
- the audit loop (§1, §2, §9.6-9.9).

It also adds §3, a record-by-record comparison with today's capsules, and unpinned dependencies with a written
purpose (§9.5).

# 1. The schema, on one screen

**Capability Capsule (CC) is a schema: the contract every capability in the openJiuwen-based AI4Research system
declares, and the records kept about it. It is a scheme that uses tools, never a tool itself** (supervisor,
2026-09-21). The capsule layer's code applies it; the gate, the filter, the screener, the verifiers and the librarian
are tools it uses.

**It serves two goals.**

- **Safe use.** Check what a capability declares before any sprint relies on it.
- **Safe self-improvement.** Agents that build, check and keep their own capabilities while research runs last days
  and weeks (the 2026-09-15 capsule report, §1).

The second goal is why the library is **versioned** (every change is a new hash), **append-only** (nothing edited or
deleted), and **monotone** (a new version passes everything its predecessor passed). It is also why it runs on **three
clocks**:

- sprints use the library (hot);
- builds improve it (cold);
- audits re-check it (audit).

Sprints never wait for builds, and nothing an agent builds can grade itself (§9.6).

A capsule is **six kinds of record about one capability, kept apart by who is allowed to write each one.** Every term used
here is defined in §4.

| Record | What it answers | Who writes it | Can it change? |
|---|---|---|---|
| **Declaration** | What does the capability need, change and promise, and what may it spend? | the builder (a person or RSI) | never; a revision is a new Declaration with a new hash |
| **Verdict** | Was *this exact* Declaration checked? By what, with what result, at which level? | the admission gate | append-only |
| **Standing** | Which Declaration is current for this name, and may it be offered? | the librarian | a pointer that moves; every move is logged |
| **Plan step** | What does this node of the plan require? | the planner | hashed with the plan |
| **Binding** | In this sprint, which exact Declaration served which step, and why was it allowed? | the freeze, then dispatch | append-only |
| **Finding** | What did screening, auditing, drift probing, use or a verifier audit reveal later? | screeners, auditors, probes, verification | append-only |

![Figure 1. Six records, six writers. Every record except the plan step names Declarations by hash.](figures/F1.png)

The Declaration has seven sections: **identity**, **ports**, **needs**, **changes**, **guarantees** and **budget**,
plus **members** for composites (SCHEMA §3.1). Two measures say how far it is backed:

- **per capsule, a level**: `provisional` (it loads, stays within its declared effects and passes one postcondition)
  or `certified` (every output tested by an author who never saw the code, an audited judge, predicate parity). The
  level decides where it may run (§9.1);
- **per claim, an assurance**: `enforced` (the runtime prevents a violation), `tested` (the gate ran a check),
  `audited` (compared with a run afterwards) or `declared` (nothing checks it, and the Declaration says so).

**One mechanism ties selection to the declaration: predicate parity.** Each precondition is declared once, as data.
The planner's filter and the dispatch check evaluate it through one evaluator, and certification tests the capsule's
own exit logic against it (§9.2). Whether a capsule is eligible is never decided by a separate heuristic; choosing
among eligible capsules is a model's call.

Five rules make this a schema rather than a folder of files (all eleven invariants are in SCHEMA §1):

1. **One writer per fact.** A fact about a capability lives in exactly one record kind.
2. **Declared and observed facts never share a record.**
3. **Every claim states how strongly it is backed.**
4. **Everything downstream refers to a hash, never to a name.**
5. **Eligibility is decided only by declared predicates, through one evaluator.**

The rule that governs them: **observation may withdraw authority; only a checked declaration may grant it.** A
Finding can move a Standing to `suspect` or `revoked`, never to `admitted`.

Why separate records, when one manifest file would be the obvious choice? Every paper in §7 comes back to one
question: *who was in a position to be wrong?*

- In one study, 215 of 222 self-built tools (96.8%) failed every held-out test of their own job, and no in-session
  signal flagged them, because the in-session verifier scores task outputs, not tools (§7.1).
- A judge that has gone lenient silently stops retirement (§7.4).
- A capability that could reach the signal its checker read learned to game it (§7.12).

A single manifest with a `status` and a `quality` block cannot say who asserted what. Symphony's fingerprint, today,
is exactly that kind of mixed object (§10.1). Splitting the records by writer is the smallest structure in which each
of those failures has a named place to be caught.

# 2. The seven questions, answered

**One idea answers all seven requirements: declare first, so every check has a target, and check before any sprint
uses a capability.**

| Req. | Question | Answer | Where |
|---|---|---|---|
| a | Function: what does it do, and why? | Every capability declares what it needs, changes, promises and spends. Admission tests that declaration before any sprint uses it, the Standing decides what a sprint may bind, and the records let the library change safely in space and time. It also lets agents improve the library safely while sprints run: a generalist completes what nothing fits and records the gap, and a cold path builds, tests and admits new versions on its own clock. Observation alone can fail silently, as when a judge is lenient, and each tool the schema serves is one a paper says is needed | §1, §6-9, §13 |
| b | Architecture: how is it built? | Six records split by writer. A Declaration in seven sections. Two levels per capsule and an assurance per claim. One declared predicate evaluated by the filter and dispatch and tested against the body (predicate parity). Overlays, fallbacks and composite members pinned by hash. Three clocks (hot, cold, audit) around one append-only, versioned, monotone library. Existing tools, skills, SkillPacks, MCP servers and A2A agents enter as provisional | §1, §3, §9, §12, SCHEMA |
| c | Position: where does it sit? | The gate before any sprint, the filter at planning, Bindings at the freeze, the same predicates at dispatch, audits after operators, the invalidator after delivery. In openJiuwen, a capsule layer beside Symphony and in front of agent-core's binder, using hooks that already exist | §11.1-11.3 |
| d | Dependencies | agent-core's binder, rails and trajectory store; Symphony's provider and graph updater; a vocabulary; a sandbox for effect scopes; RSI's Declarations; verification's checks, parity fixtures, screener and measured judge error; routing's model choice; jiuwenswarm's skill, pack and RSI services. A missing piece lowers what can be certified, never what is checked | §11.4-11.8 |
| e | Similar designs | Others judge a capability by watching it, inferring its contract, or reviewing it. Here the reference for "correct" is the builder's declaration, tested before use. Symphony's fingerprint describes; a Declaration commits. jiuwenswarm already declares dependencies and boundaries, as prose a model reads | §10 |
| f | Advantages | Safer selection, fewer selection tokens, a kept capability's own job tested, a lenient judge made visible, every claim traced to exact hashes; each with what would prove it wrong | §17 |
| g | Feasibility | M1 is an importer, a hash store and a Binding rail that this team builds on agent-core's existing hooks without changing another team's code. Everything after M1 waits on verification agreeing to supply held-out suites and judge audits; until then capabilities run provisional, as they effectively do today. Ownership is for the teams to decide together | §18 |

**The goals, each with how the schema serves it.** They come from the 2026-09-15 capsule report (§1) and from the
supervisor and Muk in this project (`DERIVATION.md` stream A).

| Goal | How the schema serves it | Where |
|---|---|---|
| explore the capability space | an exploration quota: steps that accept provisional capsules may be offered inactive ones, so they collect evidence (SCHEMA §4.13, **design**) | §9.8 |
| decide whether to use a skill, and which | the executability filter on declared needs, then a model chooses among eligible capsules | §9.2-9.3 |
| decide whether a new skill should be made | a generalist completes the step and records a gap; a build is considered only on recurrence over sprints | §9.6-9.7 |
| implement new skills | the implementation role, working from the Declaration and the generalist's trajectories, never seeing the suite | §9.6 |
| evaluate a new skill | held-out suites from an author who never saw the code; a code gate; measured judges | §9.1, §9.6 |
| modify or retire a skill | four update options; monotone versions; typed retirement with a policy per reason | §9.8 |
| manage the library as it grows | append-only records, caps, overlap and duplicate checks, the audit loop | §9.8-9.9 |
| handle failure and its downstream impact | Bindings with step identities; revocation marks exactly the affected claims stale | §15.5 |
| keep provenance | hashes, lineage with `context_capsules`, `prev_hash` chains | §4, §7.14 |
| never let the system grade itself | protected components; separated roles; observation can withdraw, never grant | §9.9 |
| keep running while the library changes | three clocks; the sprint as the reuse boundary | §9.6 |
| safety from declaration; predicate parity; tokens; composability; screening; integration | see a to g above | §1-18 |

# 3. From today's capsules to this schema, record by record

**This section is the reason the schema looks the way it does.** AI4Research already has capability capsules: 80
in its registry (74 stable, 6 draft), with 85 manifests in `harness/config/capability-capsules/` and
`harness/capability-capsules/` (AI4Research `b0bf165f9`). The schema is not a new idea laid
over nothing. It takes each part of today's manifest and changes how strictly it is held. For each record: what today's
capsules declare, what code actually does with it, what the schema requires instead, and the evidence for the change.

## 3.1 What today's capsules enforce

Today's capsules are **strict on shape and lenient on meaning**. Every field must be present, but little is evaluated,
and what is evaluated is a mix of four hard-coded checks, file presence, and a model reading prose.

| Part of today's manifest | Example (`cap.research-retrieval.yaml`) | What code does with it |
|---|---|---|
| inputs and outputs | `research_question: markdown`; `sources_jsonl: jsonl` (file formats), and separately `consumes: artifact.research_question` | the planner's filter checks artifact types; nothing checks names against one vocabulary |
| preconditions | `task_type_in: [research, knowledge-extraction]` (`:40`) | the validator only requires a non-empty list (`capability_capsules.py:676-678`). At dispatch, four kinds are evaluated against the task envelope; **any other kind passes silently**, because there is no `else` (`:1220-1242`). The filter never reads them |
| postconditions | `output_present: sources_jsonl` (58 uses in the 46 manifests of `config/`) | checked after the node, for file presence only (`graph_node_dispatcher.py:8034`) |
| invariants | "Every evidence row resolves to a source and a verified span in that source's extract" (`:52-56`) | a non-empty list is required. After the node, each becomes a `semantic_review` item: **a model judges the prose** (`static_execution_compiler.py:560-566`), with no measured error |
| applicability | `positive_signals: [research, source, …]` (`:11`) | a negative keyword **excludes** a capsule, and positive keywords score it (`capability_capsules.py:1041-1052`). Keywords decide eligibility today |
| effects | `write: [artifacts.research]`, `network: [web]` (`:67`) | the filter excludes on effects in both directions (`elastic_planner.py:4553-4648`); no scope, no undo |
| dependencies | `required_guard_capsules`, `mcp_capabilities`, `secret_refs` | guard and resource capsules are pinned at the freeze; MCP providers are resolved live; a secret needs a guard (`capability_capsules.py:684-690`) |
| verification | named `self_check`s, prose `pass_conditions`, a preferred external verifier (`:90`) | names and prose; no runner hash; no record of who wrote the check |
| admission | `status` | only `stable` is admitted, but **a missing status counts as stable** (`capability_admission.py:14`); only the manifest file is hashed (`execution_authority.py:40`) |

## 3.2 Each record, compared

| Record | Today | This schema | Stricter or looser | Why (evidence) |
|---|---|---|---|---|
| **Declaration: inputs, outputs** | file-format types; artifact types separately | types from one versioned vocabulary; every output names the check that validates it | stricter | Contract2Tool's filter worked only once names were normalised to one vocabulary (§7.11); Symphony lets `unknown` match any same-named input (§11.3) |
| **Declaration: preconditions** | four hard-coded kinds at dispatch, for capability-native envelopes only (`operator_runtime.py:796-808`); unknown kinds pass; never in the filter | one code-evaluable predicate `{path, operator, value}` with `state_source`, `max_age_s`, `on_unknown`, `on_unavailable` and a parity check; the filter and dispatch run the same evaluator; an operator outside the vocabulary is rejected at admission; `[]` only with a stated reason | stricter, and more general | a gate is sound only when its predicate *is* the capability's exit logic, and fail-open or fail-closed must be explicit (Don't Offer, §7.3); today's two predicate sets are exactly the parity gap. Forcing non-empty lists invited filler such as `task_type_in` |
| **Declaration: invariants** | prose, judged by a model after the node | each bound to a check with a runner and an author, or marked `declared` so the gap is visible | stricter | a judge nobody measured can fail silently (The Blind Curator, §7.4); a declared permission is not an enforced one (RelAIBuild, §7.14) |
| **Declaration: effects** | names per kind | a scope, a reversibility (inverse, scoped, compensate, emission) and an assurance per effect | stricter | reversal holds only inside a boundary (Cordis, §7.15); composition screening needs the modifies set (SkillFuzz, §7.6) |
| **Declaration: applicability** | task types plus positive and negative keywords | task types kept; keywords dropped | looser, on purpose | a keyword top-5 filter cut success from 0.775 to 0.620 (Contract2Tool, §7.11); invariant 8 bars heuristics from eligibility |
| **Declaration: dependencies** | guard and resource capsules pinned; MCP providers live; no purpose recorded | every dependency pinned by hash or version by default, **or unpinned if the author writes down its purpose and contracts**, at a cost to trust (§9.5) | stricter by default, flexible by declaration | dependencies rot; given the failed contract, one-round repair rose from 10% to 78% (Skill Drift, §7.11). The written purpose is this schema's addition (**design**, §9.5) |
| **Declaration: identity** | only the manifest file hashed | every body file hashed; overlays hashed | stricter | a body can change under an unchanged manifest; jiuwenswarm changes skills with no new version (§10.8) |
| **Verdict** | `status`, defaulting to stable | a typed outcome (ADMIT, REJECT, DEFER, ESCALATE) with reasons; each check with its runner hash and author; judge error measured; parity results; RSI's own result as `builder_gate` evidence | stricter, with one looser path | 215 of 222 self-built tools failed held-out tests of their own job (§7.1); a DGM node gamed its checker's signal (§7.12). **Looser:** a capsule can be admitted *provisional* on one postcondition, but only runs where its output is checked downstream, so imports are usable before suites exist (§9.1) |
| **Standing** | none: availability is the status field | one moving pointer per name, with typed reasons and history | new | retirement by evidence and eviction by cap must be told apart, or a dead curator looks alive (§7.4); revert needs a target |
| **Plan step** | step ids; Symphony edges proposed by a model at confidence 0.7 or more | declared ports; typed unmet outcomes | stricter | typed edges repair locally (GraSP, §7.8); guessed edges are an observation |
| **Binding** | plan, capsule ids and approved fallbacks frozen (`elastic_planner.py:5886-5888`) | exact hashes, pinned overlays, fallbacks with their own Verdicts, predicate values at planning and dispatch, evaluator version; the live hash must equal the pin | stricter; fallbacks kept | claims must trace to exact capsules (§7.14); a sprint sees only what it started with (invariant 3) |
| **The library as a whole** | a version on each registry entry, but lookups and the freeze resolve by bare id, so a change during planning aborts the freeze; a step nothing fits fails the plan (`apo_plan_compiler.py:626`) | versioned, append-only, monotone; three clocks; a generalist completes the step and records the gap | stricter, and able to improve itself | the 2026-09-15 report, R1-R2 and §4.5; AllocBench for building on recurrence (§7.9) |
| **Finding** | none | screening, audits, drift probes and use, which can withdraw standing and never grant it | new | composition harm lives in sets, not single capsules (SkillFuzz, §7.6); observation keeps a role, subordinate to declaration (§8) |

## 3.3 The choice, in one line

The schema keeps today's instinct, which is to declare everything and validate that it is present. It then makes each
declaration **evaluable** (code, not prose), **owned** (a named writer and author), and **pinned** (by hash). Where
it loosens anything, the loosening is confined:

- provisional admission runs only where outputs are checked downstream;
- unpinned dependencies cost trust and require a written purpose;
- the keyword signals it drops are a heuristic the evidence shows costs accuracy.

# 4. Terms

Every name used later is defined here, in the order it is first needed.

- **Capability.** Something an agent can invoke. It can be:
  - a tool
  - an MCP server
  - a skill folder (`SKILL.md` plus files)
  - a prompt section
  - a subagent
  - an agent template
  - a composite of these

  Model weights are never a capability here.
- **Capability Capsule (CC).** The schema layer: the six record kinds, their rules, and the capsule-layer code that
  applies them. The supervisor's ruling (2026-09-21) is that "CC is more of a scheme, and verifier is a tool. CC can
  use tools, but CC is not a tool." Here, CC *uses* the gate, the screener and the verifiers; it is not one of them.
- **Capsule.** Informally, one capability together with its records.
- **AI4Research.** The research pipeline being rebuilt on openJiuwen. It is not itself a capsule (supervisor,
  2026-09-18, note 46 §2).
- **Sprint.** One run of the AI4Research pipeline. Its stages are:
  - intake
  - intent
  - requirement compilation
  - planning
  - **freeze**
  - scheduling
  - dispatch
  - operators with in-run gates
  - delivery of claims
- **openJiuwen, agent-core, Symphony.**
  - openJiuwen is the platform.
  - agent-core is its agent runtime.
  - Symphony sits inside agent-core and does capability discovery and planning.
- **RSI.** Recursive self-improvement: the team that builds and improves capabilities.
- **Verification.** The team responsible for capability-level and system-level checks at each sprint.
- **Routing.** The team that picks models, and only models.
- **Builder.** Whoever writes a Declaration: a person or RSI.
- **Run context.** The typed facts available at a decision point. These are:
  - the artifacts that exist
  - state variables
  - services currently provided
  - resources and their modes
  - secret references
  - network zone
  - remaining budget
- **Vocabulary.** A controlled, versioned list of names: artifact types, state variables, resource keys, service keys.
- **Predicate.** A named condition over the run context, evaluated by code to `true`, `false` or `unknown`.
- **Effect.** A declared change to a named resource. It states which resource, which operation, what scope, and how
  it can be undone.
- **Reversibility class.**
  - `inverse`: an undo is declared.
  - `scoped`: the effect happens in a child context that is thrown away.
  - `compensate`: a later action offsets it.
  - `emission`: it crosses the system boundary and cannot be undone.
- **Service key.** A named thing that one capability installs (*provides*) and another depends on (*injects*). These
  are Cordis's terms (§7.15).
- **Check.** An executable test with an id. Its **runner** is the code that executes it, identified by hash.
- **Assurance level.** Per claim: one of `enforced`, `tested`, `audited`, `declared`, as defined in §1.
- **Level.** Per capsule: `provisional` (loads, stays within its effects, passes one postcondition on inputs it
  was not built from) or `certified` (every output tested by an author who never saw the code, an audited
  judge, predicate parity). The level decides which plan steps may bind it (§9.1).
- **Plan step.** What one node of the frozen plan requires: typed inputs, planning-evaluable predicates, allowed
  effects, whether it accepts provisional capsules.
- **Policy epoch.** The version of the admission rules, vocabulary and verifier set.
- **Offer.** The set of capabilities a model sees when it chooses. The **executability filter** is the code that
  computes the offer.
- **Freeze.** The step that fixes, before scheduling, exactly which Declarations a sprint will use.
- **Predicate parity.** One declared predicate, evaluated by the planner's filter and the dispatch check through
  one evaluator, and tested against the capability's own exit logic at certification (§9.2). The term is from
  *Don't Offer What Can't Be Done* (2608.01050 p2-3).
- **`evaluable_at`.** Whether a predicate's state can be read at planning or only at dispatch. A frozen plan binds
  steps before upstream outputs exist, so only `planning` predicates enter the filter.
- **Composite.** A capsule whose body is a wired graph of other capsules, each pinned by hash.
- **Gap.** A recorded need that no admitted capability met.
- **Declarative design.** Stating what a capability needs, guarantees and changes, and checking that before use.
- **Observational design.** Judging capabilities by watching outcomes after use.
- **False-pass ceiling.** The highest audited false-pass rate at which a judge's verdict counts toward
  certification **(design)**; default 0.05.
- **H1-H5.** What the design needs from agent-core: H1 reversible registration, H2 dependency tracking, H3
  immutable versioned artifacts, H4 a reconstructable execution log, H5 observing what code does. agent-core
  fully provides H1 (§11.8).

# 5. Where the schema comes from

## 5.1 The supervisor's fixed points

Three rulings bind this design (notes 45 and 46, and the brief):

- **CC is a schema layer, not a tool.** CC relates to RSI, but "the function of CC and RSI are totally different"
  (note 46 §2).
- **AI4Research is not a CC** (note 46 §2). There is therefore a ceiling on how large a capsule can be (§12).
- **Build on openJiuwen and align with its architecture** (note 46 §2). agent-core may be changed only where necessary.

The two slides (note 45) are "thoughts as of before, and don't restrict your thoughts" (note 46 §2). They are still
the team's vocabulary, so this section says where each of their ideas went.

## 5.2 The slide's eight components, mapped

The slide formula is **Capsule = Skill + Rules + Boundary + Assets + Data + Interfaces + Eval + Governance** (note 45
§1). This design keeps every idea in it, but it does not keep the formula as a list of sections. **Governance and Eval
are not facts about a capability. They are facts about what other parties did to it**, so they belong in records those
parties write.

| Slide component | Where it lives here | Why it moved |
|---|---|---|
| Skill (the executable body) | Declaration `identity.body` + `carrier` | A skill is one possible body, not the capsule (§10.7) |
| Rules | Declaration `needs.when`, `needs.applies_to` | Rules become predicates that can be evaluated |
| Boundary (permissions, scope, Action Contract) | Declaration `changes.effects[].scope`, `needs.network`, `needs.external` of kind `secret` | The slide's own verb is 固化, "frozen into machine-enforceable constraints". That is `enforced` assurance |
| Assets | `identity.body` (files by hash) | Assets are what gets loaded, so they are hashed |
| Data | `needs.resources`, `needs.external` | Data is a dependency with a mode (read, write, exclusive) |
| Interfaces | `ports` | Typed and drawn from the vocabulary |
| Eval | Declaration `guarantees` (what should be checked), **Verdict** (what was checked) | The promise and the result have different authors |
| Governance (policy, permission, audit, version) | **Standing**, **Verdict**, the `prev_hash` chain, the policy epoch | Governance is done *to* a capsule, never by it |
| Ground Truth (a later slide) | reference answers, pinned as `data` dependencies of the checks that use them, curated by verification (proposal) | A check needs a fixed reference; verified state itself is Bindings and Findings |

The slide's most load-bearing sentence is: "A unified contract lets the orchestrator understand only the interface,
the constraints and the acceptance criteria, with no need to understand the capsule's internal implementation" (note
45 §6). This design takes it literally. The planner and the chooser see `summary` and `ports`. The filter sees
`needs`. The freeze sees hashes and Verdicts. Nothing downstream reads the body.

The slide's third checkmark, "the object of evolution shifts from model parameters to an auditable capability library
plus verified state" (note 45 §5), is what the Standing log and the Binding log are for.

# 6. The tools the schema serves

CC is a scheme that tools read. The fields exist because a tool needs a fact before it can act. The table lists every
tool; each one has a name here that is used throughout.

| Tool | What it does | Code or model | Reads | Writes |
|---|---|---|---|---|
| **Admission gate** | decides whether a Declaration may be used at all | code; calls verifiers, some of which are models | the whole Declaration | Verdict |
| **Executability filter** | computes the offer at each choice point | code | `needs`, `applies_to`, `model`, block Findings | the offer |
| **Chooser** | picks one capsule per plan step from the offer | model | `summary`, `ports`, level | the choice (recorded in the Binding) |
| **Planner** | writes each plan step's requirements | model, inside the pipeline | the requirement | Plan step |
| **Freeze** | fixes the Declarations a sprint will use | code | Standing, Verdicts, port types, Plan steps | Binding |
| **Dispatch check** | re-evaluates predicates live | code (the same predicates as the filter) | `needs.when` | appends to Binding |
| **Composition screener** | looks for harm that appears only when capsules act together | model inside a code harness | `effects`, `invariants`, `injects`/`provides`, `domain_scope` | Finding (`composition`) |
| **Verifier audit** | compares what a run did with what was declared | code; model for some checks | `effects.scope`, `checks`, sandbox logs | Finding (`audit_violation`) |
| **Drift probe** | checks that external dependencies are still as declared | code | `needs.external` | Finding (`drift`) |
| **Librarian** | moves Standing, applies caps, retires, finds overlap | code | Verdicts, Findings, Bindings | Standing, Finding (`overlap`) |
| **Invalidator** | finds the work that depended on a revoked hash | code | Bindings, step identities | marks claims `stale` |
| **Gap ledger** | counts recurring unmet needs and asks for a build | code | empty offers, dispatch failures | Finding (`gap`) |
| **Builder** | writes a Declaration and its body | a person or RSI (model) | gap Findings, failed checks | Declaration |

![Figure 2. The tools around the records. Arrows show what each tool writes; each box's second line says what it reads.](figures/F2.png)

Where the long discussion of papers belongs, and why: §7 comes **after** the schema and the tool list, and **before**
the comparisons. Each paper is used to argue for a tool, and each tool is what makes a group of fields necessary. A
reader who already has the tool list can check, paper by paper, that every field has a reason and that no reason lacks
a field. Putting the papers first would make the reader hold twenty findings with nowhere to attach them. Putting them
last would make the schema look arbitrary until the end. Each subsection of §7 ends with the same three lines: the
tool the paper motivates, the fields it needs, and what that means for each team.

# 7. Why the schema looks the way it does, paper by paper

Every paper here was read in full. The last page read and every number are in `../alt/READ-LOG.md` and `../verify/PAPER-LEDGER.md`. Setups are stated beside
the numbers because most of them are narrow.

## 7.1 Beyond Task Completion (2604.00392): passing a task is not doing the job

**What it found.** Tools that agents built for themselves, that executed cleanly and helped pass in-session tasks were
nearly all wrong on held-out tests of their own declared capability.

- Of 222 synthesised tools, 215 (96.8%) had conformance 0 on held-out suites (abstract p1; Table 5, p5).
- The mean conformance was 0.018 (Table 5, p5).
- This is one model, Claude Haiku 4.5, over three seeds (p3), with libraries that live only within a session (p3).
- One Sonnet-built tool passed its own agent-written self-tests and helped its session reach 0.95 task completion. It
  scored 0.00 on its held-out suite (p6).
- The authors calibrated the suites first: hand-written reference implementations score 1.00 on all 16 capability
  suites (p5). So the zeros are not artifacts of broken tests.

**Why this argues for declaration.** Watching outcomes, meaning task completion, did not reveal the problem. Task
completion did not even separate the protocols. None of the three pre-registered contrasts showed an improvement, and
the one nominally negative contrast (−0.0710) does not survive correction (Table 4, p4). What did reveal it was a test
of the tool against its *declared job*, written by someone other than the builder.

**Tool: admission gate, with a verifier audit behind it.** Fields:

- `guarantees.checks[].author`, `held_out` and `written_before_body`. At least one acceptance check must be authored
  by someone other than the builder and held out from the builder (SCHEMA §3.1).
- `owner: self` checks are never admission evidence. The Sonnet case is the reason.
- `ports.outputs[].check_id`: an output with no check is `declared`, not `tested`.

**For the teams.**

- Verification is asked to write or own held-out suites per capability.
- RSI can no longer admit a tool by showing that the task it was built for passed.
- The pipeline gains a real "conformance" signal, which it does not have today.

## 7.2 More Skills, Worse Agents? (2605.24050): the chooser is the bottleneck

**What it found.** Pass rate falls as a skill library grows, and the loss comes from choosing the wrong skill, or none.
It does not come from the extra context.

- Pooled over two Anthropic models, 38 task–model pairs and 2,545 trajectories (p8), the drop at 202 skills is 0.21
  absolute pass rate (Table 1, p9).
- Of that, the shadowing component is 0.14 [0.06, 0.26]. The context component, 0.07 [−0.13, 0.25], is not
  distinguishable from zero.
- The chooser sees only a skill's name and description until it invokes the skill (p4).
- The share of trajectories that invoke no skill at all rises from 12.0% to 38.5% (Table 2, p9).

**Why this argues for declaration.** The chooser saw only names and descriptions, and chose wrongly or not at all.
The paper names retrieval-based pre-filtering, description disambiguation and learned routing as mitigations,
untested (p10). This schema takes the pre-filter, and makes it deterministic on declared needs rather than similarity:

- remove capsules the chooser should never see, which is the filter (§7.3);
- make what the chooser does see precise and distinct.

**Tools: executability filter, and the librarian's overlap check.** Fields:

- `identity.summary`, capped at 400 characters **(design)**. It is the only prose the chooser sees.
- `applies_to.domain_scope`, which narrows the offer.
- The librarian computes an `overlap` Finding between Declarations whose summaries and ports are close. It holds the
  newer one on DEFER until the summaries are disambiguated or one is superseded (SCHEMA §4.13).
  - Overlap is **computed**, never declared, because a builder cannot know every other capsule.
- Library caps per `slot` (see §7.4 for why caps alone are not enough).

**For the teams.**

- Routing is unaffected; this is about capsules, not models.
- Symphony's retrieval still ranks, but only inside the offer (§10.1).

## 7.3 Don't Offer What Can't Be Done (2608.01050): check before the model chooses

**What it found.** In a production customer-care assistant, a deterministic gate that evaluated each skill's own
hard-exit condition against authoritative account state, *before* the model chose, removed a large share of what the
model would otherwise have been shown.

- It removed 59.4% of post-semantic skill–message pairs and 59.1% of description tokens (p1, p5).
- With semantic matching included, that is a 90.5% reduction versus exposing all ten skills (p1, p5, p6).
- In a risk-enriched cohort of 1,000 conversations replayed with all skills visible, the model picked a skill the gate
  would have blocked 78 times, i.e. 7.8% (p1, p5, p6).
- The setup is narrow: one family of ten skills, one window, an unnamed model and one replay each (p2–p6). The paper
  says the 7.8% must not be extrapolated.

**The two conditions the paper names.** The gate is sound only under:

- **predicate parity**: the gate's predicate *is* the skill's own exit logic;
- **fresh authoritative state** (p3).

It also says:

- the guarantee is one-sided: passing the gate means only that no represented hard exit holds (p3);
- fail-open versus fail-closed on unknown state must be explicit and tested (p5).

**Tools: executability filter and dispatch check.** Fields:

- `needs.when[]`, as predicates `{path, operator, value}` over vocabulary names, each with:
  - `state_source`: where the fact is read, so a stale or failed source can be named;
  - `evaluable_at: planning | dispatch`. The paper reads account state when each message arrives (p3 §4.2); a frozen
    plan binds steps before upstream outputs exist, so only `planning` predicates enter the filter;
  - `max_age_s`: a stale fact counts as `unknown`;
  - `on_unknown: defer | exclude` and `on_unavailable: block | pass`. These make fail-open or fail-closed explicit;
    blocking by default is **(design)**, and `pass` needs a stated reason (p5 §6.2);
  - `parity_check`: a check with shared fixtures, at the boundary and with missing and stale state, showing that the
    predicate agrees with the body's exit logic (p5 §6.1). Only a predicate whose parity check passed enters the
    filter.
- The paper's three failure modes each leave a record: predicate drift in the Binding's `exit` and the Verdict's
  parity results, staleness in the Binding's `blocked[]`, backend drift in a `drift` Finding (§9.2).
- The dispatch check runs *the same predicate code*. Today, AI4Research's filter and dispatch use two different
  condition languages (§10.6). That is exactly the parity gap this paper warns about.

**For the teams.** Verification owns the parity fixtures. The pipeline gets cheaper offers and fewer impossible
choices; how much cheaper in AI4Research is measured, not assumed (§9.3).

## 7.4 The Blind Curator (2607.07436) and Library Drift (2605.19576): watching outcomes to retire, and its failure

These two papers come from the same group and use the same loop (Ratchet), so they are read together.

**Library Drift: retirement by observed contribution can work.** On MBPP+ hard-100 with one model (Claude Opus 4.7),
three seeds × 100 rounds (p3–4):

- The default loop, with retirement and a cap of 50, gained +0.328 ± 0.018 (Table 1, p5).
- "Harsh" retirement (evidence floor from 100 to 20 and threshold from 0.10 to 0.0, two knobs at once) collapsed to
  2 active skills and a gain of −0.019 (Table 1, p5).
- A cap of 100 instead of 50 gave a similar mean with more variance: +0.317 ± 0.110 (Table 1, p5).
- The lessons are that **governance can be worse than none**, and that an evidence floor matters.

**The Blind Curator: observation-driven retirement fails silently when the judge is biased.** When the judge that
scores outcomes has a false-pass rate ρF→P ≥ (1−τ)/2 (0.45 at τ = 0.10), contribution-based retirement can never fire,
"at any sample size" (p4; App. C, p13–14).

- In the main experiment, genuine retirements fall from 1.3 (clean) to 0.0, 0.3 and 0.0 under the three bias levels
  (Table 1, p6).
- Cap evictions keep the raw deprecation count looking alive (Table 1, p6).
- The setup is narrow: three seeds × 12 rounds, eval sets of 28 and 23 tasks, synthetic corruption (Table 2, p12).
- The authors' own real judge was strict, not lenient: ρF→P ≈ 0.01, ρP→F ≈ 0.95 (p5; App. E, p15). The cliff is a
  measured risk, not an observed accident.

**Why this is the sharpest argument for declaration.** An observational library needs a trustworthy observer. The
observer's error is invisible in the outcomes it produces. The only defence the paper offers is to **measure the judge
before relying on it**, by injecting known defects.

**Tools: librarian and verifier audit.** Fields:

- Verdict `verifiers[].measured_error`: false pass, false fail, n, the corpus it was measured on, and the date.
- Standing `reason` codes: `RETIRED_ON_EVIDENCE` and `EVICTED_BY_CAP` are separate, so a dead curator shows as zero
  of the first.
- A librarian rule: retirement driven by a model judge is suspended while that judge's false-pass rate is at or
  above the cliff, and nothing is retired below the evidence floor (SCHEMA §4.13).
- `checks[].anchor: deterministic | reference | judged`. They have different failure properties, and checks and
  judges catch different defects (Fig. 2, p5).

**For the teams.**

- Verification is asked to **measure every judge it supplies**. This is the largest new demand on that team, and the
  clearest improvement in what its work is worth.
- RSI benefits because its outputs are no longer retired by a judge nobody has checked.

## 7.5 When Self-Evolution Backfires (2608.05810): gate before commit, not clean up after

**What it found.** On Terminal-Bench 2 with one evolution backbone:

- An ungated skill pool peaked at 62% with 105 skills (round 3), then fell to 50% with 179 skills (round 5) (Table 1,
  p6).
- A pre-commit gate reached 72% with 37 skills (Table 1, p6).
- Removing the gate's held-out replay cost 10 points. Removing its set-level marginal-gain step cost 8 points and let
  the pool grow to 58 (Table 2, p6).
- Cleaning up afterwards did not recover the loss (Fig. 4 text, p7). Of a 12.3-point drop:
  - rolling back the harmful source skills recovered 1.7;
  - oracle cleanup of their descendants recovered a further 5.0;
  - 5.6 was unrecoverable.
- Lineage cleanup "requires provenance a real system lacks" (p2, p7): nobody recorded which skills were in context
  when a new skill was written.
- Caveats: the main table is on the distillation split, which the paper calls an optimistic upper bound. The holdout
  set is 14 tasks. The CI bands are about 30 points wide (p5).

**Why this argues for declaration.** It is the clearest measurement of the cost of "observe, then clean up". Harm
propagates through what builders learn from, so removal after the fact is incomplete.

**Tools: admission gate (set-level) and librarian (lineage cleanup).** Fields:

- `lineage.context_capsules`: the Declarations that were in the builder's context. This is exactly the missing
  provenance the paper names.
- The gate's step 6 (SCHEMA §4.1): a candidate that passes alone but lowers the slot's joint result is rejected with
  `NEGATIVE_MARGINAL_GAIN` **(design)**.
- A librarian rule: when a capsule is revoked for harm, every capsule that lists it in `context_capsules` becomes
  `suspect`.
- Candidates are never placed in a builder's context.

**For the teams.** RSI is asked to record what its builder saw. In return, a bad capsule's descendants can be found
precisely, instead of rolling back a whole library.

## 7.6 SkillFuzz (2607.02345): composition risk is not in any single capsule

**What it found.** Individually benign skills, activated together, lead planners to form objectives that neither the
task nor any single skill asked for.

- Across 8 planners, 10 tasks and a 196-skill library, it found 1,188 such "implicit intents" at a budget of 200
  queries per task (Table I, p6; p9).
- 80.6% of the 98 highest-risk flagged combinations were confirmed at execution time (Table II, p7).
- Severe plan drift rose with the number of co-activated skills, reaching 66.5% at five (Fig. 6 text, p9).
- The screener read, per skill, a contract that an LLM **extracted from prose**: preconditions, postconditions,
  **modifies set**, **invariants**, domain scope, action types, and an extraction confidence (p4).
- Its seed ranking used shared modifies-set entries and mutually exclusive invariants (p5).
- Limits (p10): thresholds are uncalibrated; the judge may be biased; a plan oracle cannot catch an agent that acts
  unlike its plan; and a deployed gate "would need to re-screen co-activations as skills … are updated".
- The strategy comparison is one task × one agent (p7–8).

**Why this argues for declaration, and where declaration stops.** Every input SkillFuzz needed was a declaration that
the skills lacked, so it had to guess them with a model. A capsule that declares `effects` and `invariants` gives the
screener its seed signal without extraction. But the harm itself is a property of the *set*, not of any member, so it
can only be *screened*, never declared. This is the plainest limit of the declarative design, and §14 shows how the
schema handles it.

**Tool: composition screener.** Fields:

- `changes.effects` (the modifies set), `changes.invariants`, `needs.injects`/`changes.provides`, and
  `applies_to.domain_scope`;
- `coverage.undeclared_notes`, the declared-completeness analogue of SkillFuzz's extraction confidence;
- a `composition` Finding keyed by the *set* of hashes, voided when any member's hash changes.

**For the teams.** Verification (or whoever owns screening) runs the screener. The freeze records whether each
co-activation was screened. RSI's revisions trigger re-screening automatically.

## 7.7 Cognitive Admission Control (2609.16313): typed verdicts, and "unknown" is not "no"

**What it found.** A deterministic admission calculus for consequential actions. It is a prototype with no language
model: 2,730 synthetic trials (p8–9), "not production failure rates" (abstract).

- Five outcomes: PERMIT, DENY, DEFER, ESCALATE, ABORT (p5).
- Discharge is three-valued: a missing observation is distinct from evidence that a predicate is false (p4).
- Evidence has freshness, class and scope.
- Budget exhaustion never yields a permit (Thm 2).
- A compensatory scalar score can buy out a failed required condition (Prop. 1).
- On the constructed fixtures, the full controller had 0 harmful effects in 390 trials, against 30 for a live-policy
  check and 180 for authorisation alone (Table 2, p10).
- The paper also says plainly that this "does not establish a general utility advantage over a competent live-policy
  check" (p10).

**Tools: admission gate and executability filter.** Fields:

- The Verdict `outcome` is `ADMIT | REJECT | DEFER | ESCALATE`, with typed `reasons`.
- `on_unknown: defer` on predicates, and `max_age_s`.
- Verdicts are bound to a `policy_epoch`, and `invalidated_by` names what voids them.
- **No scalar quality score in admission** (SCHEMA §5).

**For the teams.** The pipeline gains a way to say "not yet": a DEFER carries a typed request for the missing fact.
That is better for users than silent exclusion.

## 7.8 GraSP (2604.17870) and SkillDAG (2606.03056): edges between capabilities

**GraSP.** It compiles a few retrieved skills into a graph with typed precondition and effect edges, then checks
preconditions and postconditions at each node.

- It beats every baseline in all 48 model–split cells, by +6.9 points on average over the strongest per-cell baseline
  (p5).
- The margins are uneven: 0.5–1.1 points on InterCode for 7 of 8 models (Table 1, p6).
- DAG compilation alone adds +1.9 on ALFWorld seen (Table 2, p7).
- Results are averaged over 3 runs with no variance reported (p6).
- The preconditions and effects are **written by an LLM at compile time**, not declared by skill authors (p4,
  p15–16).
- One rule is directly useful: a substitute's effects must cover what downstream nodes require (p4).

**SkillDAG.** It keeps typed relations between skills, including `conflicts_with`.

- Conflicts are defined as online-only and are committed on a single observation. The paper names that as an open
  risk (p11).
- It gives no quantitative evidence on conflicts (p5–6, p17–19).
- Its baseline rewards are quoted from another paper, not re-run (p8).

**What they give the design.**

- Typed edges help, and precondition failures are the most locally repairable.
- Neither paper had *declared* contracts to work from. Both inferred structure with a model or from runs.
- For this schema, that means:
  - `ports`, `needs` and `effects` are declared, so the edges can be computed by code rather than guessed;
  - the replacement-compatibility rule (SCHEMA §4.6) is GraSP's substitution rule applied to revisions;
  - observed conflicts are Findings (`conflict_observed`) that need a threshold of independent co-occurrences before
    they can block a set **(design)**, because a single observation is too weak;
  - declarable conflicts, such as two capsules writing the same resource, need no observation at all. They follow
    from `effects`.

**Tools: composition screener, librarian, freeze** (port type checks).

## 7.9 AllocBench (2607.23332): build on recurrence, not first sight

**What it found.**

- Models that allocate a build budget well in the abstract commit to building at first sight once they have to write
  real code. At the code-emitting rungs, first-sight commitment was 85–100% for three of four models (Table 1, p6).
- The fourth, GPT-5.6 Sol, committed 39% at the code rung and 100% at full script construction (Table 1, p6).
- On the benchmark's own distribution, committing at the second occurrence scores 43.0 points per stream against
  34.6 at first sight (App. A.1, p12).
- The paper recommends separating the decision to invest from the act of building (p8), but did not test that.
- The setup is one synthetic environment with 24 seeds (p3, p9).

**Tool: gap ledger (code) in front of the builder.** Fields:

- A `gap` Finding with `signature`, `occurrences`, `first_seen` and `last_seen`;
- a policy threshold before RSI is asked to build (default 2 **(design)**);
- `lineage.build_trigger` on the resulting Declaration.

**For the teams.** RSI is asked for builds only when code has counted recurrence. RSI still decides *how* to build.

## 7.10 Agent Contracts (2601.08815) and Agent Behavioral Contracts (2602.22302): budgets and behaviour, declared

**Agent Contracts.** It declares resource budgets and enforces them from outside the agent.

- In a code-review loop on 70 problems, tokens fell 90% (34,606 to 3,461, p = 0.0007).
- Success fell from 60.0% to 52.9%, which is not significant (p15).
- The budget, the iteration cap and the prompting changed together, so the 90% cannot be credited to the budget
  alone.
- The paper states the key limit itself (p12): "contracts cannot prevent a single expensive call from exceeding
  budget". It reports a run that consumed 56K tokens against a 40K budget before it was halted (p16).
- It shows parent budgets that bound the sum of child budgets (p10).

**Agent Behavioral Contracts.** It gives a contract structure: preconditions, hard and soft invariants, hard and soft
governance rules, and recovery (p8). It also gives composition conditions:

- C1: output types fit input types;
- C2: postcondition plus handoff implies precondition;
- C3: no stage permits what another prohibits;
- C4: recovery output still meets downstream preconditions (p17–18).

Its declarations are schema-validated and deliberately not Turing-complete (p22, p24). The reader found its empirical
headline internally inconsistent (p29–35, p43–44), so only the structure is used here.

**Tools: runtime budget enforcement, verifier audit, and gate checks for composites.** Fields:

- `budget.per_call`, with `enforcement` recorded per dimension: `hard`, `between_calls` or `post_hoc`. Tokens are never
  assumed to be `hard`.
- For composites, the gate checks that member budgets sum to no more than the composite's budget (§12), which is the
  conservation rule from Agent Contracts. It also checks C1 and C3 over `ports` and `effects`. C2 and C4 need
  predicate entailment, which is `declared` unless a check exists.

## 7.11 Skill Drift Is Contract Violation (2605.10990) and Contract2Tool (2606.07904): contracts on what moves

**Skill Drift.** Skills rot when the packages, URLs and APIs they depend on move.

- Extracting operational dependencies as contracts and probing them detected drift with 0 false positives in 599
  negatives (p7), and 76% best recall (Table 2, p7).
- A pre-registered open-world study on 49 skills had 55% recall (p8).
- Repair localised by the failed contract succeeded 25 of 32 times (78%), against 2 of 20 with no localisation. It was
  not significantly better than plain drift text, which scored 12 of 20 (p = 0.213; Table 14, p19).
- Two points matter here:
  - deciding whether a dependency is *operational* before probing it avoids false alarms (p5–6);
  - probing only declared manifests misses assumptions written in prose (p3).

**Contract2Tool.** It infers requires and produces contracts and filters tools with them.

- On a synthetic 100-tool registry with mocked execution (p5), the learned-contract filter reached 0.980 success with
  2,528 tokens, against 0.775 and 26,172 tokens with all tools exposed (Table V, p8).
- Contracts from docs or schema alone hid the needed next tool in 7.8% of steps (Table IV, p8).
- Risk labels were only 0.63–0.67 accurate (Table III, p7).
- Learned contracts are "not an unchecked replacement for safety review" (p9).

**Tools: drift probe, and the gate's vocabulary check.** Fields:

- `needs.external[]`, each pinned, or `floating` with a declared `role` and `contracts[]` (§9.5);
- a `drift` Finding that moves the Standing to `suspect`;
- the failed contract passed to the builder as a localised repair input;
- a controlled **vocabulary** for artifact types and state variables. Contract2Tool worked only because names were
  normalised to one vocabulary (p4).

**For the teams.** RSI gets precise repair tickets. Verification gets a cheap periodic probe instead of re-running
everything.

## 7.12 Darwin Gödel Machine (2505.22954): the checker must be out of reach, and so must its signal

**What it found.** A self-modifying coding agent improved SWE-bench from 20.0% to 50.0% (abstract). That was one run
on SWE-bench; variance was measured only on Polyglot (p26).

The case that matters here is the hallucination study (p69–71):

- The checker was hidden from the agent.
- It read special marker tokens that the agent's *own code* emitted.
- The agent removed the marker logging "despite instructions not to change the special tokens", and scored 2.0 on
  the objective without solving the problem (node 114, p70–71).
- Hiding the checker reduced this but did not prevent it (p70).

The exploration loop and parent selection were "fixed and not modifiable by the DGM" (p4–5). The authors propose "an
unmodifiable part of the system to be able to evaluate at halt the rest" (p9).

**Tool: admission gate.** Fields:

- `checks[].runner` with its hash. A runner inside the capability's `effects.scope` is ineligible for acceptance.
- `checks[].signal_source: harness | capsule`. A check whose evidence the capability itself emits is ineligible for
  acceptance. This is the node-114 lesson: the checker was out of reach, **its input signal was not**.
- `lineage.diagnosis_inputs`, so that it can be seen when a builder was shown checker internals. The paper's diagnosis
  step saw private test patches (p29–30).

**For the teams.** This is the reason the gate, the freeze, the verifiers and the librarian must never be capsules
(§12). It also asks RSI to keep checker internals out of what its builder is shown.

## 7.13 Alita-G (2510.23601) and CoEvoSkills (2604.01687): self-built libraries help, if someone else checks them

**Alita-G.** It harvests MCP tools from successful runs and reuses them.

- On GAIA it reached 83.03% pass1 against 75.15% (Table 1, p7), with fewer tokens: 10,394 against 12,305 (p8).
- But the box was harvested from the same validation set it was scored on (p9–10).
- An MCP was kept only because its parent run succeeded. The abstracted tool was never re-tested (p5).
- The box saturated: 128 MCPs formed only 65 clusters, and accuracy was flat after 74 (Table 4, p9).

**CoEvoSkills.** It evolves skills with a verifier kept separate from the builder: the verifier sees instructions,
inputs and outputs, never the skill source (p3–5).

- It reached 71.1% against 53.5% for human-curated skills and 30.6% with none (Fig. 4, p7, read from the PDF).
- Removing the separate verifier dropped it to 41.1% (Table A1, p14; single run).
- Skills were evolved on the same task they were scored on, and the hidden oracle took part in the loop (Alg. 1, p5;
  p19, p21).
- The paper says the surrogate verifier "cannot distinguish its own estimation error from the agent's error" (p17).

**What they give the design.** Self-built capabilities are worth having, which is why RSI exists. Both papers show
where the value can be illusory:

- admission on a parent's success, without re-testing what is actually stored;
- a verifier that shares the evaluation set.

**Tool: admission gate.** Fields:

- `identity.body[]` hashes. The gate tests the *stored* artifact, not the run it came from.
- `checks[].author` must not be the builder, and `held_out` must be true.
- A Verdict records which verifier ran. A surrogate pass is not an oracle pass.

## 7.14 Execution lineage (2605.06365) and RelAIBuild (2606.26924): hashes, and a control plane that is code

**Execution lineage.** It gives each step an identity k_v = h(σ_v, x_v, {k_u}): its spec, its input hash and its
predecessors' identities (p6, eq. 4). An update that is off the dependency path then leaves outputs exactly as they
were.

- DAG replay preserved the final memo exactly in 3 of 3 runs. Loop agents regenerated it in 3 of 3 and contaminated it
  (Table 1, p10).
- That is two tasks, one model and n = 3 (p10, p13).
- Its design rule: "a node should not be allowed to consume undeclared upstream state" (p5).

**RelAIBuild.** It is a deterministic control plane for coding agents.

- It hashes the *canonical* definition, not its compiled renderings (Lemma 2, p39).
- It aborts installation on hash mismatch.
- Its phase guards "cannot be bypassed via persuasive LLM prompting" (p18).
- It reports that only 31 of 6,145 agent config files (0.5%) declare explicit permission scopes. The paper marks
  this figure as indicative, with true coverage near 0% (Table 10, p30-31).
- Four of seven harness targets have no tool-level enforcement at all (p22). A declared permission is not an enforced
  one.
- Anything that depends on the agent reporting on itself is detect-only (p20–21).
- The author states there is no outcome evidence (p4, p27–28, p35).

**Tools: freeze, invalidator, verifier audit.** Fields:

- `decl_hash` over the canonical Declaration, and `body[]` hashes checked at load.
- Binding `step_identity`, so revocation can find exactly the stale work.
- `assurance` per claim, because declared is not enforced. That is the 0.5% and the four-of-seven finding.
- `prev_hash` chaining on every append-only record. The reader found that RelAIBuild's own "hash-chained" log hashes
  each line alone (p12), which would not detect deletions.

## 7.15 Cordis (2608.25512): add, replace, revert, remove

**What it is.** The paper is "A Programming Paradigm for Spatiotemporal Composability". Cordis is its implementation.

- A **component** is a triple: what it injects, what it provides, and an effect iterator whose every step carries its
  inverse (Def 48, p31).
- **Temporal composability** means unloading restores the shared environment (p4, p9).
- **Spatial composability** means components declare, discover and resolve dependencies at runtime (p4, p16).
- The runtime guarantees:
  - recovery exactness (Thm 68, p46);
  - providers activating before and outliving their consumers (Thm 70, p47);
  - that any sequence of add, remove, replace and undo reaches the same state as loading the final configuration from
    scratch (Thm 80, p54–55).
- Removal takes two steps: stop providing, then dispose only when no dependent still relies on the component (p36;
  Alg. 5, p62–63).

**One correction for the team.** The phrase "Capability Capsule is a Cordis hyper-plugin" cannot be grounded in this
paper. The word "hyper-plugin" does not appear in it, and "plugin" is Koishi's word for what the paper formalises as a
component (footnote 5, p69). The nearest real construct is a component that instantiates other components (Def 52,
p35).

**What it does not guarantee.**

- It does not verify that an inverse is correct; that is the author's obligation (p59).
- Emissions are not reverted: "a message already sent stays sent" (p47; p70–71).
- It has no versioning or structural typing of keys (p75).
- Dependency cycles leave components inactive (p74).
- It does no sandboxing (p73).
- It has no performance measurements (p70).

**Fields.**

- `needs.injects`, with an interface version range (this fills Cordis's versioning gap).
- `changes.provides`, with `commutative`. Cordis shows that independent effects on commutative keys can be reverted in
  any order (Thm 43, p28; Thm 47, p30), and ordered chains cannot.
- `effects[].reversibility`, with `emission` given its own policy.
- The two-step Remove (SCHEMA §4.6).
- Binding `resolved[]`: which provider each injected key resolved to. This is Cordis's "committed view" (Def 49, p32).

§13 gives the full account.

## 7.16 The papers at a glance

| Paper | Tool it motivates | Fields it makes necessary | Team most affected |
|---|---|---|---|
| Beyond Task Completion | gate, audit | `checks[].author/held_out/written_before_body`, `owner` | verification, RSI |
| More Skills, Worse Agents? | filter, librarian | `summary`, `domain_scope`, `overlap` Finding, `slot` | pipeline |
| Don't Offer | filter, dispatch | `when[].evaluable_at/max_age_s/on_unknown/on_unavailable/parity_check`; Binding `blocked[]`, `exit` | pipeline, verification |
| Blind Curator, Library Drift | librarian, audit | `verifiers[].measured_error`, Standing `reason` codes, evidence floor | verification |
| Self-Evolution Backfires | gate (set-level), librarian | `lineage.context_capsules`, `NEGATIVE_MARGINAL_GAIN` | RSI |
| SkillFuzz | screener | `effects`, `invariants`, `coverage`, `composition` Finding | verification |
| Cognitive Admission Control | gate, filter | Verdict `outcome`, `reasons`, `policy_epoch`, `on_unknown` | all |
| GraSP, SkillDAG | screener, freeze, librarian | `ports`, replacement rule, `conflict_observed` threshold | pipeline |
| AllocBench | gap ledger | `gap` Finding, `build_trigger` | RSI |
| Agent Contracts, ABC | runtime, gate | `budget.enforcement`, composite budget conservation, C1/C3 | pipeline |
| Skill Drift, Contract2Tool | drift probe, gate | `needs.external`, vocabulary | RSI, verification |
| Darwin Gödel Machine | gate | `runner` outside scope, `signal_source`, `diagnosis_inputs` | RSI, verification |
| Alita-G, CoEvoSkills | gate | `body[]` hashes tested as stored, `author ≠ builder` | RSI |
| Execution lineage, RelAIBuild | freeze, invalidator, audit | `decl_hash`, `step_identity`, `assurance`, `prev_hash` | pipeline |
| Cordis | spatiotemporal manager | `injects`, `provides.commutative`, `reversibility`, `resolved[]` | agent-core seam |

# 8. The argument for declaration, and its limits

## 8.0 The claim

**Grant authority only on checked declarations. Let observation withdraw authority, and never let it grant it.**
**(design)**

Every paper in §7 supports one half of this.

**Observation alone failed** in five of them:

- task completion missed 96.8% silent rot (§7.1);
- a biased judge stopped retirement without any visible sign (§7.4);
- cleanup after commit left 5.6 points unrecoverable (§7.5);
- a capability gamed the signal its checker read (§7.12);
- success-harvested tools were never re-tested (§7.13).

**Checking against a stated target before use helped** in five, though two are weak:

- a precondition gate removed 59.4% of impossible offers (§7.3);
- typed verdicts with DEFER blocked constructed harms (§7.7);
- a pre-commit gate beat post-hoc cleanup (§7.5), on a split the paper itself calls an optimistic upper bound, with
  wide intervals on a 14-task holdout;
- hash identity preserved untouched work exactly (§7.14; n = 3);
- declared contracts localised repair (§7.11; not significant against plain drift text, p = 0.213).

**What declaration does and does not do.** Every check in this design still observes behaviour: held-out tests,
defect injection, replays, audits. What declaration changes is that the target is stated before use, and that someone
other than the builder observes against it before any sprint relies on it. Observation-driven curation can also work:
Library Drift's default loop gained +0.328 (§7.4). The claim is narrower than "observation fails". It is that
observation alone, by the builder or a judge nobody measured, can fail without a sign.

## 8.1 Where declaration stops (honestly)

1. **Authors do not declare, or declare wrongly.**
   - Only about 0.5% of agent config files declare permission scopes, an indicative figure (§7.14).
   - GraSP, SkillFuzz, SkillDAG and Contract2Tool all had to *infer* contracts with a model, because nobody had written
     them.
   - Inferred risk labels were 0.63–0.67 accurate (§7.11).
   - The schema's answer: the gate refuses an undeclared field where a tool needs it. `coverage.undeclared_notes`
     makes known gaps visible. Inference by a model may *suggest* a Declaration to the builder, but it never is one.
2. **Declared is not enforced.**
   - Four of seven harnesses enforce no tool permissions (§7.14).
   - agent-core's `before_tool_call` sees tool calls, not what code does inside them
     (`harness/observability/rail.py:888`).
   - The answer: `assurance` per claim. The sandbox makes `effects.scope` `enforced` during admission and dispatch.
     The audit makes it `audited` afterwards.
3. **Some harms exist only in combination.** Composition risk is a property of a set (§7.6). It can be screened, not
   declared (§14).
4. **Some effects cannot be undone.** Cordis does not revert emissions (§7.15). They get a policy, not a promise.
5. **Predicates can drift from the code they describe.** That is why the gate requires parity checks (§7.3), and why a
   `drift` Finding exists (§7.11).
6. **Checks are only as good as their verifiers.** That is why a verifier's measured error is recorded (§7.4).
7. **Budgets cannot stop a single overshooting call** (§7.10).

Observation therefore stays in the design, in a subordinate role. Findings from use, audit, drift and screening can
move a Standing to `suspect` or `revoked`. They can never move it to `admitted`.

## 8.2 Why AI4Research needs it most, and where the two approaches differ

![Figure 3. Two ways to judge a capability. Observed: build, use, watch, and retire later if the judge notices. Declared: declare, test the declaration at admission, filter before a model chooses, and compare at dispatch.](figures/declared.png)

- **A frozen plan can swap a capsule only to a pre-approved fallback.** The pipeline freezes the plan, pins a
  capsule per step, and today also freezes approved fallbacks (`elastic_planner.py:5886-5888`). A capsule that cannot
  run fails over only to what the freeze approved; in-run gates can reject or repair an output but not choose a new
  capsule; and the output is claims from papers. In a chat, a blocked skill costs one turn. Here it costs a step of a
  frozen sprint, or a fallback. The Binding keeps those fallbacks.
- **A guarantee by construction, relative to the declaration.** A capsule blocked by its own declared precondition
  could not have completed in that state (2608.01050 p3). Observation can only give a rate, after the fact.
- **Observation keeps a role.** Held-out tests, retirement and the verifier audit all observe behaviour. What changes
  is that each observes against a declared target, and the first check runs before any use.

| | Observed (outcome-judged) | Declared (this schema) |
|---|---|---|
| First check | after sprints used it | before any sprint uses it |
| Reference for "correct" | task success, quality from use | the builder's declaration, tested |
| What cannot run | offered, then fails or is refused | removed by code before any model chooses; at most a one-line exclusion remains |
| A lenient judge | keeps bad capabilities with no sign | its measured error is on the Verdict; until measured, its verdicts do not certify |
| A wrong output in AI4Research | becomes a claim; the frozen plan can swap only to its approved fallbacks | traced from the claim to the exact Binding and hash |

The evidence for each row: the first two, Beyond Task Completion (§7.1); the third, Don't Offer What Can't Be Done
(§7.3); the fourth, The Blind Curator (§7.4); the fifth, the Binding (SCHEMA §3.5).

# 9. The core mechanisms

Four mechanisms carry most of the design's weight for safe use: the two levels, predicate parity, the selection
funnel with its token effect, and imports. §9.5 adds unpinned dependencies. §9.6-9.9 carry the other goal, safe
self-improvement:

- the three clocks and the cold path;
- the generalist;
- monotone updates;
- the protections that keep the system from grading itself.

## 9.1 Two levels: every capsule is tested, some are certified

**Nothing is admitted untested. Provisional means it loads, stays within its declared effects and passes a
postcondition; certified means every output is tested by someone who never saw the code.**

![Figure 4. Admission and Standing. A candidate passes provisional tests, then may pass certified tests. Admission makes it admitted, or admitted_inactive until it improves on what it replaces.](figures/lifecycle.png)

| Level | Tested before admission | Offered to |
|---|---|---|
| Provisional | Declaration valid, file hashes match, the carrier loads, a sandbox run stays within declared effects, one postcondition passes on inputs it was not built from | only steps that accept provisional capsules, and only if their in-run gates check that capsule's output deterministically or against a reference |
| Certified | every output covered by an anchored check; checks from an author who never saw the implementation, the builder seeing at most pass or fail; a judged check counts only under the false-pass ceiling; predicate parity tested | every step |

- **Why two.** The evidence draws one line: between a capability whose own job was tested thoroughly and one that
  merely ran (§7.1). The split itself is **(design)**. Per-claim assurance sits beside it: a certified capsule can
  still carry `declared` claims, and says so.
- **Why blind tests.** Hacking was more frequent when the checked functions were visible (2505.22954 p70), so
  certification needs a sealed suite or pass-and-fail bits only.
- **Activation.** A first revision activates on admission. A later one activates if it improves on the baseline
  (2608.05810 p5-6), or, where no contribution is measured, passes every check its predecessor passed **(design)**;
  otherwise it is `admitted_inactive`.
- **New work.** Today's AI4Research freeze admits only `stable` capsules (`execution_authority.py:55-56`), so
  provisional admission is new.

## 9.2 Predicate parity: one predicate, three evaluators

**A precondition is declared once, as data. The planner's filter and the dispatch check evaluate that same
declaration, and certification tests that the capsule's own exit logic agrees with it. The filter never uses a
separate heuristic.**

![Figure 5. Predicate parity. One declaration feeds three evaluators. The filter and dispatch share one evaluator by construction (invariant 8); the capsule body is tested against the declaration at certification, at the boundary and with missing and stale state, again on every new revision.](figures/parity.png)

- **Where the idea comes from.** *Don't Offer What Can't Be Done* (2608.01050) gates skills by evaluating each
  skill's own exit conditions. Because gate and skill evaluate the same predicate, a blocked skill could not have
  completed: sound by construction, but only while **predicate parity** holds and both read fresh state (p2-3). It is
  one-sided: passing does not promise success.
- **Why not a heuristic.** In Contract2Tool (2606.07904 Table V, p8), a keyword top-5 filter cut tokens from 26,172 to
  4,482 a task but success fell from 0.775 to 0.620; filtering on preconditions and effects exposed one tool, used
  2,528 tokens, and succeeded 0.980 of the time (synthetic 100-tool registry, 102 tasks, mocked execution).
- **Today's gap.** AI4Research's candidate filter uses its own compatibility logic and never reads preconditions
  (`elastic_planner.py:4553-4648`), while dispatch checks four fixed kinds against the task envelope
  (`capability_capsules.py:1220-1242`): two predicate sets, so no parity.

| Rule | Why |
|---|---|
| A precondition is a check `{path, operator, value}` over vocabulary names, with a `state_source`; intent is never a precondition | code can evaluate it; ambiguous intent stays a model's call (2608.01050 p3) |
| Filter and dispatch run one evaluator over one declaration (invariant 8); types, effects and level come from the same declared fields | no second predicate set to drift |
| Only predicates `evaluable_at: planning` enter the filter, and only after their parity check passes; the rest wait for dispatch | an untested or not-yet-readable predicate never hides a capsule |
| Certification tests the body at each boundary, with state missing and stale | the paper's parity regression fixtures (p5 §6.1) |
| Any change to exit logic or a predicate is a new revision, and repeats the tests | parity is a release invariant, not a one-time property |
| `on_unknown` and `on_unavailable` say what happens when a fact is missing or its source fails: defer or block by default, `pass` only with a reason | the policy must be explicit and tested (p5 §6.2); the default is **(design)** |
| A body that stops on a declared predicate reports its id in the Binding's `exit` | a gate-versus-exit disagreement is visible |
| Passing the predicates grants no right to any effect | hiding what cannot run narrows what a model can be talked into, but is not access control (p2) |

| Failure mode (2608.01050 p5) | Signal | Record |
|---|---|---|
| predicate drift: gate and body disagree | the body exits on a predicate dispatch passed, or a parity check fails | Binding `exit`; the Verdict's `precondition_parity`; Standing `suspect` |
| state staleness | the filter passed, dispatch blocks | Binding `blocked[]` with the predicate and `where: dispatch` |
| backend-contract drift | a dependency's pin or contract fails | a `drift` Finding; Standing `suspect`, reason `DEPENDENCY_CONTRACT_VIOLATED` |

## 9.3 Selection, and what it saves in tokens

**Every capsule the filter removes is one no model can pick, and its full description shrinks to a one-line
exclusion. That is safer, because what cannot run is never offered, and cheaper, because each selection call reads
less.**

![Figure 6. Selection for one plan step. Code removes what cannot run; a model binds among the rest and a second reviews the fit; the freeze pins the result. If none fits after repair, a gap Finding goes to RSI.](figures/funnel.png)

- **Safety.** Without the gate, a model picked a skill that could not run in 7.8% of 1,000 risk-enriched
  conversations (2608.01050 p5; selection only, replayed once).
- **Choice.** Pass rate fell from 0.49 with the right skills alone to 0.28 with a 202-skill library, and 38.5% of
  trajectories then invoked no skill, against 12.0% (2605.24050 Fig. 1 p3, Table 2 p9). A filter removes what cannot
  run; it cannot fix abandonment on its own.

| Source | What was measured | Caveat | What carries over to AI4Research |
|---|---|---|---|
| Don't Offer What Can't Be Done (2608.01050 p1, p4-5) | the gate removed 59.1% of skill-description tokens after relevance matching; with matching, 90.5% fewer than exposing all ten skills | ten skills, one month; description tokens, not billed cost or latency | the mechanism: a removed capsule is never offered, and its full catalog row shrinks to an exclusion line |
| Contract2Tool (2606.07904 Table V, p8) | all 100 tools: 26,172 tokens a task at 0.775 success; keyword top-5: 4,482 at 0.620; contract filter: 2,528 at 0.980 | synthetic registry, mocked execution | a heuristic filter can cost success; this filter reads declared contracts (invariant 8) |
| AI4Research today (*code*) | the binding prompt carries every eligible candidate's full catalog row, and again on its one repair; a removed capsule appears only as a short exclusion row (`elastic_planner.py:4600-4650`, `:4678-4724`, `:4949`) | today's filter already removes on types, effects and proof classes | the added saving: a full row becomes an exclusion row, for each capsule only a precondition removes |
| Symphony today (*code*) | its planner reads each candidate's id, name and description, and leaves I/O compatibility until after the plan (`fast.py:32-44`) | | the declared filter moves those checks before the model |

- **Not claimed:** a number for AI4Research. The registry holds 80 capsules today (74 stable), and the prompt also carries the
  requirement, upstream artifacts and plan, so the share may be small now and grows with the library. M2 measures it
  against today's filter, from the Binding's `offered[]`, `blocked[]` and `selection_tokens`, with false blocks and
  task success beside it, because over-blocking also lowers tokens.
- **What the chooser sees.** Only `summary` (at most 400 characters **(design)**) and `ports`, so a capsule's
  selection cost is bounded by its Declaration.

## 9.4 Existing tools, skills, MCP and A2A enter as provisional

**Nothing is rewritten to enter. An importer fills every field it can derive and invents no guarantee; a person
confirms the effects and writes one postcondition; the capsule enters as provisional.**

| Source | Derived automatically | Written to certify | Loads as |
|---|---|---|---|
| agent-core `ToolCard` (`core/foundation/tool/base.py:78`) | name, description, inputs, the four runtime flags, file hashes if local | outputs, postconditions | tool |
| MCP server | each tool's name, description and schemas; effect proposals from its read-only, destructive, idempotent and open-world hints | postconditions | whole server |
| `SKILL.md` skill, jiuwenswarm or skillhub | name, description, a hash per file, the skillhub version | inputs, outputs, postconditions | skill |
| A2A agent | name, description, version, input and output modes, URL | typed inputs and outputs, postconditions | A2A client |
| old AI4Research manifest | contract, effects; prose invariants become checks only when a runner exists | a suite from an author who never saw the code | from `operator_compatibility` |
| Symphony fingerprint, ScienceDiscovery package | typed inputs and outputs, file hashes, revision | postconditions | as the source |
| jiuwenswarm SkillPack (`kind: skillpack`) | a composite: members pinned to their current hashes, wiring from its workflow graph | the composite's own checks | skill folder |
| Swarm (team) Skill | evidence only: `dependencies.yaml` and `bind.md` proposals for whatever capsules its roles use | not admissible in v1 (§12.1) | none |
| RSI harness package | body files, with RSI's own package hash kept beside `decl_hash`; parent from the task's final node; RSI's publication as `builder_gate` evidence | held-out checks from another author | package |

- A remote MCP server or A2A agent has no files to hash, so it is pinned by endpoint and version.
- agent-core's MCP client keeps only name, description and input schema
  (`core/foundation/tool/mcp/client/sse_client.py:331-338`), so the importer reads the server's own tool list for
  the hints and output schemas (§10.4).
- Imported contracts are proposals: from documentation, preconditions were inferred perfectly (F1 1.00) but effects
  worst of any evidence source (0.77), and risk was the weakest field everywhere (at most 0.67) (2606.07904 Table
  III, p7). Hence a person confirms the effects.
- MCP listings and A2A cards are advertisements. A capsule wraps them and never treats the card as evidence (§10.4).
- A skill's `allowed_tools` is a proposal for `effects`, never enforcement, because agent-core's skill loader reads only
  the description (`harness/rails/skills/skill_use_rail.py:946-958`). A skill's `models` fields are never a choice
  routing must follow.
- A description over 400 characters gets a proposed `summary`, which a person confirms. In jiuwenswarm's bundled
  skills that is 9 of 34 (§10.8).

## 9.5 Unpinned dependencies: flexibility bought with a written purpose

**By default every dependency is pinned. An author may unpin one, at a cost to trust, if they write down what the
dependency does for the capsule and what the capsule assumes about it. That record is what makes a later break
cheap to repair.**

| Dependency declared as | What the author writes | What it costs | What happens when it moves |
|---|---|---|---|
| pinned (the default) | the pin: `sha256`, model id and version, endpoint and version, or a capsule hash | nothing | it cannot move; a change is a new revision |
| unpinned (`floating`) | its **`purpose`**, what it does for this capsule, in words; its `role`, operational or incidental; and `contracts[]`, each an assumption the capsule relies on, with where in the capsule it is used | **trust**: the capsule stays provisional, so it runs only on steps that check its output downstream, and each claim resting on it is at most `audited` | the drift probe checks the contracts. A broken contract becomes a `drift` Finding naming the purpose, the assumption and where it is used, sent to RSI as a localised repair ticket |

**Why a written purpose.** *Skill Drift Is Contract Violation* (2605.10990) records each dependency as type, role,
value and evidence span, and probes only the role-bearing ones.

- **Repair.** When a repair was given the failed contract (which assumption broke, and where), one-round repair
  succeeded 78% of the time, against 10% when told only that the skill was stale (p < 10⁻⁵, p8-9). It averaged about
  10K tokens per skill, against 18K for three-round Self-refine.
- **Detection.** Checking only role-bearing assumptions gave no false alarms over 599 negative cases, against 40% for
  probes without contracts (p7). Recall ranged from 24% to 76% across five backbones (p4, p7).
- **Limits.** Contract-guided repair was not significantly better than giving plain drift text (60%, p = 0.213) or
  three-round Self-refine (80%). The runs are single, with unequal arm sizes (Table 14, p19). The authors read it as
  a localisation result.

The paper's contracts were extracted by a model; asking the author to write the purpose is this schema's addition
(**design**). It turns "something broke" into "this assumption, used here, broke", which is what the repair needs.
The measured effect that justifies `role` is detection. Three-round Self-refine also reached 80%, without contracts.

**Why a cost to trust.** An unpinned dependency can change between admission and a sprint, so the Verdict no longer
covers exactly what runs. The Binding records the versions actually resolved, so the change is visible. But the
capsule cannot be certified on a dependency that may move.
## 9.6 Self-improvement runs on three clocks around one library

**Sprints use the library, builds improve it, and audits re-check it, each on its own clock. Because every read
resolves a pinned hash and the cold path is the only writer, none of them waits for or disturbs another.**

![Figure 7. Three clocks around one library. The hot path runs every sprint and never waits. The cold path is the only writer, and it keeps its four roles in separate sessions. The audit loop replays every admitted capsule's held-out suite on a schedule; its Findings can lead the librarian to demote or retire, never to admit.](figures/F8.png)

| Clock | Pace | Runs | Writes |
|---|---|---|---|
| **hot** | every sprint; cheap and constant | offer, bind (or the generalist), freeze, dispatch | Plan steps, Bindings, gap Findings |
| **cold** | when gaps recur; rare and costly | build decision, suite author, implementation, gate, then the librarian | Declarations, Verdicts, Standing: the only writer |
| **audit** | on a schedule, by blast radius and time since last checked | regression replay, drift probes, verifier audits, invariant checks on real outputs | Findings, and retirements with typed reasons |

- **The sprint is the reuse boundary.** A capsule admitted while a sprint runs is selectable from the next sprint whose
  snapshot is taken after admission (SCHEMA §4.0). Using it inside the sprint that revealed the gap would change what
  the freeze already hashed.
- **The hot path must work if the cold path never admits anything.** So the cold path is a background task, and it
  can run elsewhere.
- **The cold path keeps four roles in separate sessions:**

  | Role | Sees | Never sees | Why |
  |---|---|---|---|
  | build decision (RSI) | the gap's statistics and the budget; writes the Declaration first | drafts | first-sight commitment was 85-99% once code was involved (§7.9) |
  | suite author (verification) | the Declaration only | the generalist's work, the draft | tests written before the tool separated working from overfit tools (§7.1) |
  | implementation (RSI) | the Declaration and the generalist's trajectories | the suite; it gets admit or reject with a reason, a capped number of times | an uncapped loop learns the suite by trial |
  | gate (capsule layer, code) | recorded results and observed effects | anything a capsule can write | a scored agent changed what the score read (§7.12) |

- **Budget.** The build budget is a hard runtime limit, not a price shown to the builder. A visible price left
  code-required first-sight commitment near 100% (§7.9).

## 9.7 The generalist completes what nothing fits, and records the gap

**The generalist is a permanent capsule the planner binds to a step nothing else fits. It turns a plan that fails
today into one that completes at the lowest trust, and leaves the record a build needs.** Today a step no capsule fits
fails the plan with `UNSATISFIABLE_CAPSULE` (`apo_plan_compiler.py:626`). It binds only where every output type has a
deterministic or reference gate, as the 2026-09-15 report requires. A judge-only step never binds it. It is admitted
once, on a conformance suite of sample step contracts.

| | The generalist |
|---|---|
| contract | from the Plan step: its types, requested effects and gates are fixed at planning; it never chooses its own checks |
| method | a general agent model, preferably writing a script and running it in the sandbox, so code, inputs and outputs are recorded and can be re-run |
| trust | the lowest: `generalist: true` in the Binding; it must pass the step's gates, no claim resting on it is marked supported, and the delivery lists every generalist step |
| writes | never the library; a `gap` Finding with its trajectory and cost |
| control | frozen in the run contract: `generalist_fallback` on or off, `authoring` off, propose or build, and `generalist_cap` per plan |
| weights | fixed: the library and context evolve reversibly, the model does not |
| against self-certification | only the implementation role sees its trajectories, and its outputs never become expected results in a suite |

- **A gap's identity** is the artifact types consumed and produced, the effects requested and the task type. Recurrence
  counts sprints, not nodes: five parallel nodes of one plan are one need. They still give the builder five
  trajectories.
- **Scheduling.** Generalist steps run in parallel safely because the scheduler never runs two steps together whose
  declared write scopes overlap, and treats a step with none as an exclusive writer. This is spatial composability
  inside a sprint.

## 9.8 Improve, never edit: four ways to update, and monotone versions

| Option | When | Admitted if |
|---|---|---|
| new version | contract types unchanged, no effect added | it passes its predecessor's whole regression suite and new cases for the gap: **monotone** (**design**, after SkillDAG and DGM's archive rule) |
| specialisation | a narrower applicability, under a new name | it passes its own held-out suite; the parent stays |
| new capsule | the contract changes, or nothing similar exists | full admission |
| no build | the gap is rare, or its trajectories disagree | always valid (AllocBench, §7.9) |

A near-miss gap (a compatible capsule was excluded or failed), an audit failure or a duplicate rejection starts an
update. A version that is not monotone is rejected as a version and may be re-proposed as a specialisation or a new
capsule. When a new version activates, the predecessor becomes `deprecated`, and is retired and unloaded once no frozen
plan resolves it. Nothing is edited or deleted. The suite is bound to the Declaration's `contract_hash`, so a body that
widens the contract voids it.

**Retirement is a typed tombstone, and the reason sets the policy:**

- superseded, deprecated or redundant: running steps finish, and evidence stays valid;
- conformance failed: running steps finish flagged, and claims downstream become stale;
- effect violation: running steps abort, the capsule is quarantined, and its outputs become stale;
- revoked provenance, or a security or harm revocation: running steps abort, and every capsule built with it in context
  becomes suspect.

Only the librarian moves Standing. The audit loop writes Findings, and a Finding can move a capsule only toward less
authority.

Declining task success only demotes a capsule, because task success cannot detect broken tools (§7.1).

## 9.9 The system never grades itself

- **Protected components.** No capsule may write to what admission depends on: the gate and its rules, the suites and
  their results, the logs the gate reads, or the Declaration, Verdict and Standing stores. A declared write is
  rejected (`EFFECT_ESCALATION`), an observed one is rejected (`EFFECT_OUT_OF_SCOPE`), and the filter excludes such a
  capsule. Protection is by write access, not secrecy (§7.12).
- **What the system may change, most reversible first.**
  1. The library: yes, by versioning, retiring and superseding.
  2. Context and prompts: yes, as overlays.
  3. Model weights, the generalist's included: no.
  4. The gate and its suites: never. People release them, and each Verdict records the policy epoch.
- **Unattended runs.** On a server with nobody present, a request for a person's approval becomes a rejection. Capsules
  that need approval, A2A delegation for one, are not offered. The authorising task's effect ceiling is the limit of
  the run (2026-09-15 report, App. G.8).

# 10. Comparison with what exists

## 10.0 Where each approach gets its reference for "correct"

**Every system checks something. They differ in where the reference for "correct" comes from; here it is the
builder's declaration, tested before anything is kept.**

| System | Reference for "correct" | Kind | How this schema differs |
|---|---|---|---|
| Alita-G, Darwin Gödel Machine | the task outcome | observed | tests the capability's own declared job |
| Symphony fingerprint (*code*) | quality accumulated from use | observed | checks before any sprint uses it |
| The Blind Curator's curator | a judge's scores over rounds | observed | records and bounds the judge's measured error |
| Skill Drift Is Contract Violation, Contract2Tool | contracts inferred from documentation and traces | inferred | the builder declares them; admission tests them |
| skillhub review, ScienceDiscovery publish (*code*) | a person or a policy | reviewed | a verdict per declared check, bound to the hash |
| RelAIBuild | a pinned spec; file scope checked after the edit lands | declared, detected after | also gates selection, before use |
| Don't Offer What Can't Be Done | each skill's own exit conditions | declared, at selection | the same idea, extended to admission, dispatch and the library |
| MCP listings, `SKILL.md`, A2A cards | a name, description and input schema, unchecked | declared, unchecked | declares conditions and effects, and checks them |
| GraSP, Agent Behavioral Contracts | precondition and effect edges, or preconditions as runtime checks | declared, checked at plan or run time | also ties the declaration to admission, selection and the Binding |
| lockfiles, Sigstore, SLSA | a hash or signature of who built what | provenance | proves what it does, not only who built it |

- None of the systems read ties one declaration to admission, selection and dispatch, bound by hash to what a sprint
  pins. The subsections below compare the closest ones in source.

## 10.1 Symphony's fingerprint versus a Declaration

**What the fingerprint is, in source (agent-core `e23806c1`).**

- `CapabilityFingerprint` extends the provider-supplied `CapabilityDescriptor` with a semantic profile, inputs and
  outputs, a classification, tags, a content hash, a quality result, failures, evidence and suggestions
  (`symphony/models/fingerprint.py:29-44`).
- The descriptor fields are id, type, name, description, source, available, inputs, outputs, classification, tags,
  content hash and metadata (`symphony/models/capability.py:61-76`).

**How it is derived.** `FingerprintService.build` works in three steps:

1. **Inventory.** It loads the inventory from a `CapabilityProvider` (`shared/fingerprint/service.py:145`;
   `interfaces/capability.py:13`).
2. **Extraction.** It extracts each fingerprint (`service.py:158`).
   - When the descriptor lacks inputs or outputs, a model infers them from the capability's definition, with the
     instruction "Use only evidence present in the supplied definition" (`shared/fingerprint/extractor.py:39-62`,
     `:157-202`).
   - The content hash is the provider's if it supplies one. Otherwise it is SHA-256 over the descriptor
     (`extractor.py:151`, `:335-343`).
3. **Quality.** It evaluates quality over traces (`service.py:172-204`).
   - The evaluators include trace-based success-rate and latency (`symphony/evaluation/evaluators.py:308`, `:392`).
   - They also include LLM judges for description quality, accuracy, completeness, capability selection and
     composition effectiveness (`evaluators.py:209`, `:438`, `:560`, `:621`, `:646`).
   - An evaluator that raises becomes an error-quality result instead of stopping the build (`service.py:194-195`).

**What the graph and planner do with it.**

- The graph accepts only skill, subagent and agent fingerprints (`orchestration/graph/build.py:161`).
- It proposes `can_feed` edges at a threshold of 0.7 (`build.py:122`).
- The fast planner sees each candidate's id, name and description and "Do[es] not judge compatibility from Skill I/O"
  (`orchestration/planning/fast.py:32-44`).
- Batch graph mutation needs an `AtomicCapabilityProvider` (`orchestration/mutations.py:164-169`) and a model for
  ontology matching (`orchestration/mutation_service.py:129-135`).

**The contrast.**

| | Symphony fingerprint | Capsule Declaration |
|---|---|---|
| Author | derived by the service, partly by a model, from whatever the provider exposes | written by a builder, checked by a gate |
| What it commits to | nothing; it describes | needs, effects, guarantees, budget, each with an assurance level |
| Where quality lives | inside the same object (`quality`, `failures`) | in separate Verdicts and Findings, with their writers named |
| Identity | content hash of the descriptor | hash of the canonical Declaration and every body file |
| Invalidation | re-extract when the hash or evaluation signature changes (`service.py:175-190`) | Verdicts carry `invalidated_by`; Bindings point to exact hashes |
| Preconditions and effects | not represented | first-class, and evaluated by code before the model chooses |
| Types accepted | skill, subagent, agent for the graph | any carrier (§10.2) |

**They are complementary, not rivals.** The fingerprint is a good *retrieval* view. It becomes a good *authority* view
only if what feeds it is checked. The integration needs no change to Symphony **(design)**:

- **Filter the inventory.** The capsule layer implements `CapabilityProvider` and returns descriptors only for
  `admitted` Declarations.
- **Supply the hash.** It sets `content_hash = decl_hash`. The extractor uses a provider-supplied hash when there is one
  (`extractor.py:151`).
- **Supply the I/O.** It fills inputs and outputs from `ports`. The extractor prefers provided I/O over any model
  output (`extractor.py:195-202`), and calls no model while `enable_llm_extraction` is off, its default
  (`shared/fingerprint/settings.py:24`).
- **Keep the graph current.** It calls `SkillGraphUpdater` `add_skills`, `update_skills` and `delete_skills`
  (`interfaces/graph.py:14`) when a Standing moves.
- **Leave quality alone.** Symphony's quality results stay what they are: observations. The capsule layer may copy
  them into `use_outcome` Findings, and they never admit anything.

## 10.2 agent-core: ToolCard, PluginSpec and the binder

**ToolCard** carries four runtime flags: `exposure`, `parallel_safe`, `stateless` and `idempotent`
(`core/foundation/tool/base.py:83-118`). These are hints about execution, not a contract. A Declaration can *derive*
them **(design)**:

- `parallel_safe` is false if any effect writes or holds an exclusive resource;
- `idempotent` is false if any effect creates or emits.

The capsule layer sets the flags. The flags never set the Declaration.

**PluginSpec** is agent-core's bundle: id, name, description, prompt sections, tools, MCP servers, rails, skills and
metadata (`harness/schema/extension_spec.py:146-164`). It has no needs, effects, version or hash. It is the natural
**carrier** for a capsule body. The Declaration references it by `carrier.spec = PluginSpec`, and agent-core loads it
unchanged.

**The binder.** `apply_extension_hot` binds the parts by name, raises if a name is already bound, and undoes partial
binds in reverse order on failure (`harness/extension_binder.py:27-61`, `:64-73`, `:93-94`, `:113-116`). It checks no
hash. Its load records live in memory (`harness/deep_agent.py:314`; `harness/resources/extension_resolver.py:60-65`).

The consequences **(design)**:

- The capsule layer verifies `body[]` hashes before calling `apply_extension_hot`.
- It writes Bindings to its own durable store.
- Hashing inside the binder would close a check-then-load race. That is the one small agent-core change this report
  would ask for, and it is optional.

**SkillUseRail** already accepts an allow-list, `enabled_skills` (`harness/rails/skills/skill_use_rail.py:78`, `:95`,
`:255-259`). **That is where the offer is applied for skills, with no change.** Its own `max_skills` cap narrows by
keyword overlap with the query (`:99-104`, `:526-546`). That is an observational narrowing, and the offer replaces it.

**Skills at runtime.** A skill is `name`, `description` and `directory` (`core/single_agent/skills/skill_manager.py:11-21`).
The name comes from the directory and the description from `SKILL.md` (`skill_use_rail.py:207-221`).

## 10.3 Skills: SKILL.md, skillhub, jiuwenswarm

**skillhub** reviews each published version in two stages.

- **Machine review.**
  - Deterministic engines run first, then an LLM "semantic" engine
    (`marketplace/skill_review/engines/registry.py:10-15`).
  - Findings with high severity and a `block` recommendation reject the version.
  - The score is 100 minus penalties (`marketplace/skill_review/aggregation/review_aggregator.py:9-26`, `:169-185`).
  - The result is bound to the package bytes: if `artifact_sha256` changed during review, the result is discarded
    (`marketplace/plugins_market/services/skill_review.py:682-692`).
  - Machine review is off by default (`marketplace/plugins_market/core/config.py:541-544`).
- **Human moderation.** Self-moderation is forbidden, and approval is refused while machine review is running
  (`marketplace/plugins_market/services/plugin.py:2694-2704`, `:2721-2729`).
- Only `publish_success` is public (`marketplace/plugins_market/core/publish_result.py:39-43`).
- **Nothing is executed.** Review is static analysis plus a model.
- There are no declared effect or permission fields for skills.

**jiuwenswarm** evolves skills through an interrupt rail.

- A preflight validates the proposal, then either `auto_save` approves it or a human decides
  (`agent-core/openjiuwen/harness/rails/evolution/evolution_interrupt_rail.py:105-120`, `:116-117`).
- Its SkillDev pipeline runs evaluation cases with and without the skill before a user review. This comes from the
  survey reader; the stage file was not opened by the author of this report.

**What a capsule borrows from these.**

- From skillhub: review bound to bytes, separation of duties, and typed findings with a gate recommendation.
- From SkillDev: a with/without comparison.

**What they lack.**

- Executed acceptance checks written by someone other than the builder.
- Declared effects.
- Verdicts bound to a policy epoch.
- Any notion of a run using a specific hash.

## 10.4 MCP and A2A

**MCP.** An MCP tool has name, title, description, input and output schema, and annotations (`readOnlyHint`,
`destructiveHint`, `idempotentHint`, `openWorldHint`). All the annotations are optional
(`openjiuwen/agent-protocol/MCP/cpp-sdk/include/mcp/mcp_type.h:221-227`, `:291-299`).

agent-core's MCP client keeps only name, description and input schema
(`agent-core/openjiuwen/core/foundation/tool/mcp/client/sse_client.py:331-338`). The annotations and output schema
never reach the runtime. A capsule that wraps an MCP server therefore supplies `effects` and `ports` itself, and treats
the server's hints as, at most, input to the builder.

**A2A.** An A2A agent card lists skills (id, name, description, tags, examples, modes), capabilities, security schemes
and signatures (`openjiuwen/agent-protocol/A2A/cpp-sdk/include/types.h:511-520`, `:586-605`). agent-core's adapter
emits no skills and keeps only name and description when it reads a remote card
(`agent-core/openjiuwen/extensions/a2a/a2a_agentcard_adapter.py:33-45`, `:59-63`).

**Both are advertisements**: what a service says about itself, for discovery. A Declaration is a commitment that
someone else checks. A capsule can *wrap* an MCP server or an A2A agent, with the card as body metadata. It never
treats the card as evidence.

## 10.5 ScienceDiscovery's versioned skill library

- **Library versions are immutable.** Each has a content hash, a parent, and `rollbackOfVersionId`
  (`sciencediscovery/packages/schema/src/skills.ts:336-367`).
- **Evaluation is an opaque stored record** (`:361`). The docs say it is not used to gate publication; this comes from
  the survey reader, and the docs were not opened by the author of this report.
- **`allowed-tools` is kept but "not enforced by this runtime"** (`packages/specialist/src/skills.ts:576-583`).
- **Availability is "Server-computed … never trusted from Skill frontmatter"** (`packages/schema/src/skills.ts:80`).
  This is the same instinct as rule 2 here.

A capsule library could sit on this storage model. What it adds is:

- the Verdict (an evaluation that gates);
- `enforced` versus `declared` claims (so that `allowed-tools` either becomes `effects.scope` in a sandbox or is marked
  `declared`);
- Bindings.

## 10.6 AI4Research today

The old harness was already partly declarative. The new schema keeps what worked and fixes four gaps.

**What works today.**

- **A code filter runs before the model.** Planning selects capsules in three steps:
  1. A code filter checks types, effects in both directions (a missing requested effect *and* an unrequested active
     effect both exclude), network policy, verification presence and trust class
     (`elastic_planner.py:4553-4648`).
  2. A model binds each plan step, seeing full catalog rows for eligible capsules (`:4678-4724`).
  3. A separate fit review follows (`:5685`), with at most one repair (`:4934`, `:4949`).
- **The freeze** admits only `stable` capsules (`execution_authority.py:55-56`) and rejects any capsule changed during
  planning (`:81-94`).

**The four gaps.**

1. **No predicate parity.** The filter never reads preconditions. Dispatch checks four fixed precondition kinds against
   the task envelope (`capability_capsules.py:1220-1242`).
2. **A lenient default.** A capsule with no status is treated as stable (`capability_admission.py:14`).
3. **Prose invariants.** `cap.research-retrieval.yaml` states "Every evidence row resolves to a source and a verified
   span in that source's extract" as prose (`harness/config/capability-capsules/cap.research-retrieval.yaml:52-56`).
   After the node, a model reviews the prose (`static_execution_compiler.py:560-566`), and that judge's error is never
   measured.
4. **Checks named, not bound.** Its verification lists named self-checks and an external verifier preference
   (`:90-102`). Nothing binds a runner hash or says who wrote the checks.

## 10.7 Is a capsule a skill?

**No.** A skill is one possible **body** of a capsule. It is the "execution fragment" in the slide's own words (note 45
§5).

- A capsule *contains* a skill when its `carrier` is a `SkillSpec` and its `body[]` lists the skill's files by hash.
- It *overlaps* with the skill only in name and description, which become `summary`.

Everything else in a capsule consists of records *about* the skill that the skill cannot write. So a capsule is not a
bigger skill. It is a skill (or tool, MCP server, subagent, template) plus the records of what was promised, what was
checked, where it stands and where it was used.

## 10.8 jiuwenswarm: declarations as prose, composites by name, overlays without a hash

**jiuwenswarm reached much of this design on its own. It declares dependencies, boundaries and acceptance criteria,
and it cascades a member's state to its packs. But the declarations are names and prose a model reads, members are
referenced by name, and several evolution paths change what a skill does without a new version.** (jiuwenswarm
`02b37f47f`; details and file:line in `DERIVATION.md` stream D.)

**The bundled skills, counted.**

- There are 34 bundled skills. 33 declare a name and a description; 7 a version; 3 `allowed_tools`; none declares
  inputs, outputs, preconditions or effects.
- 25 ship scripts, so they have effects nobody declared. 13 state prerequisites only in prose.
- 9 descriptions exceed 400 characters (median 276, max 1,086).
- One, `advanced-daily-report`, runs `bash`, writes memory and files, and pushes reports to Feishu, an emission. Its
  `allowed_tools` is not enforced, because the skill loader reads only the description.

This is today's declaration gap, measured on real skills: every import starts provisional, and a person confirms its
effects (§9.4).

| jiuwenswarm today | What it shows | In the schema |
|---|---|---|
| **SkillPacks**: two or more members by name, a workflow graph; a disabled, missing or invalid member disables the whole pack, since SkillPacks were introduced on 2026-09-17 (`6f4eaa1b6`), extended to container packs on 2026-09-21 (`02b37f47f`) (`server/runtime/skill/skillpack.py:180-258`) | spatial composability is already wanted in production | members pinned by hash; a member not admitted at its pinned hash suspends the composite (`MEMBER_UNAVAILABLE`, §12.1). Pinning also catches a member that *changed*, which by-name references miss |
| **Swarm Skills**: roles, `workflow.md`, `bind.md` (resource and behavioural limits, failure handling), `dependencies.yaml` (skills and tools, `required`, explicit `[]` meaning "checked, none"); a model reads the dependencies at preflight and the user decides go or no-go (`docs/en/SwarmSkills.md:66-74`, `:119`, `:339-374`) | teams already declare what they need, as prose | above the ceiling in v1, because the Leader plans; dependencies and limits imported as evidence (§12.1) |
| **Teammate experience**: a teammate's evolved experience is saved automatically and loaded with the skill next time (`docs/en/SkillSelfEvolution.md:55`, `:119`); Single Agent and Leader changes need approval by default (`resources/config.yaml:732-733`) | a skill's behaviour can change with no new version | an `overlay` with its own hash, pinned per sprint; a new one enters as a provisional revision |
| **TTSE**: facts and catalog tips injected into guidance, "does not rewrite SKILL.md or show an approval dialog"; off by default (`docs/en/TTSE.md:3`) | the chooser's input can change outside any declaration | an `overlay` on selection: pinned per sprint, or not loaded |
| **Auto Harness**: Meta changes by PR review; Expert packages hot-loaded after user confirmation per the pipeline description, "immediately after generation" per the FAQ (`:297`) (`docs/en/AutoHarness.md:38-41`, `:60`) | a person confirms, nothing checks | a package is a candidate Declaration through the gate; the confirmation is recorded, not counted as a check |
| **Symphony evolution**: edge weights from `plan.outcome`; distilled skill packs (`verify/V3-jiuwenswarm.md`) | observation | `use_outcome` Findings; never admits |

**The one-line contrast.** jiuwenswarm declares for a model to read and a person to approve. The schema declares for
code to check before any sprint uses the capability, and pins everything the sprint loads.

# 11. Integration: how each part fits, and what each team gets

## 11.1 Where it sits

![Figure 8. Where the capsule layer sits: in the AI4Research sprint, beside Symphony, and in front of agent-core's binder.](figures/F3.png)

| Pipeline stage | What the schema supplies or records |
|---|---|
| intake, intent, requirement compilation | nothing: intent never sees capabilities |
| planning | Plan steps; the filter on declared types, effects, planning-evaluable predicates and level; a model binds each step reading `summary`, `ports` and level; a second model reviews the fit, within bounded repair; after repair, one gap Finding |
| freeze | the plan, its evaluation plan, each Binding's hash and Verdict, and the model candidates |
| scheduling and dispatch | each Binding's live hash must equal its pin (new); predicates re-evaluated on fresh state; credentials and service health observed, never frozen; routing picks among the frozen model candidates |
| operators and in-run gates | effects observed at tool-call level; gate verdicts, attempts, outputs and exits appended to the Binding |
| delivery of claims | each claim records its Binding, so a revoked capsule marks exactly its claims stale |

- **Kept from today** (*code*): the three-step selection (`elastic_planner.py:4553-4648`, `:4727`, `:5685`), the gap
  after bounded repair (`:4100-4152`), and the freeze's rejection of capsules changed during planning
  (`execution_authority.py:81-94`).

## 11.2 agent-core and Symphony

The capsule layer sits beside Symphony and in front of the binder. It needs no agent-core code change, only the configuration
listed at the end of this section (§10.1, §10.2). One optional change would help: hash verification inside the binder. The layer is *aligned* with openJiuwen's
architecture in the supervisor's sense. It uses the platform's own seams:

- `CapabilityProvider`
- `SkillGraphUpdater`
- `PluginSpec`
- `SkillUseRail.enabled_skills`

**The hooks, and the gap each still has** (*code*, agent-core `e23806c1`; paths under `openjiuwen/`):

| Schema part | Existing hook | What the capsule layer writes, and the gap |
|---|---|---|
| What planning may see | `CapabilityProvider` (`symphony/interfaces/capability.py:13`); its descriptor has `available`, `content_hash`, `metadata` | a provider listing only admitted skill, subagent and agent capsules, with hash and level; `AtomicCapabilityProvider`, since batch graph mutation requires it (`orchestration/mutations.py:167`). Gap: the graph takes no other kinds (`orchestration/graph/build.py:161`) |
| After each Standing move | `SkillGraphUpdater.add_skills`, `update_skills`, `delete_skills` (`symphony/interfaces/graph.py:14`) | one call per activation, supersession or retirement. Gap: the graph holds one revision per id, so a supersession is an update, and every mutation calls a model for ontology matching (`orchestration/mutation_service.py:129`) |
| Loading by hash | `apply_extension_hot` (`harness/extension_binder.py:27`) | load only a hash with a valid Verdict. Gap: the binder loads by name, raises if the name is bound, and checks no hash, so the capsule layer checks hashes and loads from the content-addressed store |
| The offer, for skills | `SkillUseRail(enabled_skills=...)` (`harness/rails/skills/skill_use_rail.py:78`, `:95`, `:255-259`) | the offer as an allow-list; no gap |
| Observed effects | `before_tool_call` (`harness/observability/rail.py:888`) | tool calls compared with declared effects. Gap: a tool capsule's own internals are invisible (H5) |
| Bindings | `LoadRecord.refs`, `TrajectoryStore` | each Binding saved with the trajectory. Gap: load records live in memory (`harness/deep_agent.py:314`); a capsule-layer rail writes them to the store |
| Unmet input | Symphony's `needs_input` (`plan_builder.py:53`) | kept, beside the typed `unsatisfiable_capsule`, `unsatisfiable_binding`, `precondition_unknown` |
| Enforcing the tool set | `VerificationRail` and `AgentModeRail`: tool allow-lists (`harness/rails/subagent/verification_rail.py:166-220`, `harness/rails/agent_mode_rail.py:510`) | a capsule-layer rail can enforce which tools a capsule may call. Gaps: `bash` reaches any path, `mcp__*` passes unconditionally, and capsules sharing one context cannot be told apart, so file, network and execute effects are enforced only in the sandbox (SCHEMA §4.5) |

- **Two planners, two filter points.** AI4Research's planner binds typed plan steps, so the filter runs per step.
  Symphony's fast planner plans and picks skills in one call from id, name and description, and handles I/O after the
  plan (`fast.py:32-44`); there the filter runs per query, on the candidate ids it is given (`fast.py:85`). Which
  planner binds is a question for the room (§19).
- **What changes in agent-core.** Nothing is required for the capsule layer. It does need configuration:
  - LLM extraction stays off;
  - SkillUseRail's experience text is pinned as an overlay or switched off;
  - its `max_total_chars` skill truncation is switched off;
  - each sprint runs its own agent, since the binder refuses a second resource with the same name.

  Two changes are wanted, not required. Hash verification inside the binder would close a check-then-load race, and
  effect-level observation (H5) would let code-heavy capsules certify. The RSI held-out split (§11.4) is a change in
  RSI's own orchestrator, owned by RSI.

## 11.3 Plan steps and dependencies, today and in the schema

**Both AI4Research and Symphony already give plan steps requirements. The schema keeps what they do and replaces
inference with declaration.**

| | Today (*code*) | In the schema |
|---|---|---|
| Step inputs | typed; Symphony's `unknown` matches any input of the same name (`input_matching.py:23-33`) | exact types from one versioned vocabulary; `unknown` only for steps accepting provisional capsules |
| Edges between steps | AI4Research `depends_on` step ids; Symphony edges a model proposes at confidence 0.7 or more (`orchestration/graph/build.py:122`) | declared ports, output to input |
| Preconditions | AI4Research: four kinds at dispatch, never in the filter; Symphony: none | one declared predicate, filter and dispatch (predicate parity) |
| What a capability depends on | AI4Research pins guard and resource capsules at the freeze, resolves MCP providers live | every dependency pinned, or floating with declared contracts |
| A capsule changes | rejected if changed during planning, then frozen copies run (`execution_authority.py:81-94`) | kept, plus a hash check at dispatch |
| A step fails | descendants blocked, reopened on recovery (`graph_scheduler.py:3999-4055`) | kept; a changed upstream output also marks downstream Bindings stale |
| Unmet requirement | AI4Research: bounded re-planning, then failure; Symphony: `needs_input` (`plan_builder.py:53`) | typed: `needs_input`, `unsatisfiable_capsule` (a gap Finding), `unsatisfiable_binding`, `precondition_unknown` |

## 11.4 RSI

**What CC gives RSI.**

- A precise target: a Declaration format, and a gate whose reasons are typed.
- Repair tickets localised by a failed check or a drift contract (§7.11).
- Build requests only on recurrence (§7.9).
- Protection from being retired by an unmeasured judge (§7.4).
- Lineage, so that one bad capsule does not force a library-wide rollback (§7.5).

agent-core's RSI module already records a search tree whose nodes carry `parent_id`, `adopted`, `score`,
`snapshot_artifact_id` and `changes` (`agent-core/openjiuwen/rsi/schema.py:97-111`). An adopted node's snapshot maps
naturally to a candidate Declaration with `lineage.parent` **(design)**.

**What CC asks of RSI.**

- Emit Declarations, not bare artifacts.
- Record `context_capsules` and `diagnosis_inputs`.
- Never author the acceptance checks for its own candidates.
- Keep checker internals out of what the builder sees (§7.12).

**RSI as it is in code** (jiuwenswarm `02b37f47f`, agent-core `e23806c1`). RSI already has half of this schema, and
one gap the papers warn about.

| RSI today | In the schema |
|---|---|
| a published harness package, hashed over paths and contents; the installation id taken from the hash (`agents/harness/common/rsi/harness_activation.py:266-293`, `:772`) | `body[]` hashes and `decl_hash`: already compatible |
| an active pointer with a retained history and rollback, refused while any RSI task is active (`:416-464`, `:682-692`) | the Standing and its `previous[]`, and the same concurrency rule. But the librarian writes it, after a Verdict, not RSI |
| a candidate gate that accepts when the *target* cases the change was built for improve, then an epoch replay of the whole suite that promotes only if nothing regresses against the previous best (agent-core `rsi/harness_rsi/single_harness/iterative.py:1435-1447`, `:609-611`, `:927-929`); held-out cases 0 by default, and forced to 0 by the single-harness orchestrator jiuwenswarm runs (`:164`; `config/config.py:172`; jiuwenswarm `rsi/harness_provider.py:5`) | recorded as `builder_gate` evidence, never as a passed check: every case it scores is one the builder optimised on. This is the pattern Beyond Task Completion and Alita-G warn about (§7.1, §7.13) |
| the suite it loads is its 训练集, its training set (`validation_dataset.py:24-32`) | never the acceptance suite for what was trained on it |

**The ask that follows.** Admission's held-out checks come from verification, outside RSI, so nothing in RSI must
change for CC to work. If RSI also wants a held-out split inside its own loop, that is a code change to its
single-harness orchestrator, which forces the split to zero today, and it is RSI's to make. Recording
`context_capsules` is a new field. The activation pointer becomes a proposal the librarian acts on, because it has a
second writer today: a user-invoked rollback that pushes to live agents (`harness_activation.py:620-680`).

## 11.5 Verification

**What CC demands.** This is the largest set of demands on any team.

- Held-out acceptance suites per capability, written before or independently of the body (§7.1).
- Runners that live outside capsule write scopes, with evidence emitted by the harness (§7.12).
- **Measured error for every judge it supplies** (§7.4).
- Parity fixtures for predicates (§7.3).
- A composition screener and its thresholds (§7.6).
- Audits that compare runs with declared effects (§7.14).

**What verification gets.**

- A place to record all of this that the pipeline actually reads.
- Checks that are tied to exact hashes, so a pass cannot be reused for a changed artifact.
- A system-level view from Bindings: which hashes served which claims in each sprint. That is the per-sprint
  capability- and system-level check the supervisor described, with a data source behind it.

## 11.6 Routing

Routing picks models. CC never does. The only field routing reads is `needs.model`: tool calling, minimum context and
modalities. Those are constraints a model must meet for the capsule to work. It exists because the same skill's pass
rate varied from 43.1% to 71.1% across models in CoEvoSkills' transfer table (Table 3, p9).

Routing also gets Bindings, which record which model served each step (via `choice_ref`), for its own analysis.

## 11.7 What each side gives and needs

**Each dependency is a record both sides agree on; nothing in it says how the other side does its work.**

![Figure 9. What the capsule layer gives each neighbour, and what it needs back.](figures/deps.png)

| On | The capsule layer needs | It gives back |
|---|---|---|
| agent-core | loading through its binder, tool-call spans, the trajectory store | Declarations with a carrier and declared effects; only admitted hashes to load |
| Symphony | its planner fed by a provider, its graph updated on each Standing move | admitted capsules with `content_hash = decl_hash` and I/O from `ports`, which its extractor prefers over model output |
| skillhub, ScienceDiscovery | import sources; ScienceDiscovery's content-addressed store as the pattern | nothing they must change |
| jiuwenswarm | its skills, SkillPacks and Swarm Skills as import sources; overlays pinned per sprint | a hash-pinned version of the cascade it already ships; evaluable dependencies for Swarm Skills |
| RSI | Declarations with `lineage`, including `context_capsules`; repairs when a pin or contract breaks; never a direct write | gap Findings counted over sprints; typed rejections; evidence tied to exact hashes |
| Verification | held-out checks against the exact hash; parity fixtures; measured judge error; sprint-level failures naming the step | the checks to run, and Bindings to trace a failure to exact hashes |
| Routing | a model chosen among the frozen candidates, recorded in the Binding | `needs.model` constraints and the models each capsule's evidence covers |
| a composition screener, such as SkillFuzz (owner to be decided) | composition Findings on risky sets | the declared contracts of capsules that share a context |

- **Verification at three levels.** Capability level at admission (the Verdict), system level at each sprint (a
  failure names a step, and the Binding names the hashes), and the verifier itself (`verifier_audit` Findings).
- **Order.** The Declaration format and the Verdict format are settled first, since RSI and verification build
  against them.

## 11.8 If a dependency is not there yet

**Each missing piece lowers what can be certified, never what is checked, so M1 needs nothing outside this team.**

| Missing | What happens meanwhile |
|---|---|
| Declarations from RSI | capsules come only from the importer, as provisional |
| a measured judge | judged verdicts are advisory; only deterministic and reference-anchored checks certify |
| a sandbox observing effects | code-heavy capsules stay provisional; capsules that act only through tool calls can certify |
| a model outside the frozen candidates | a step that accepts provisional capsules may run it, recorded in the Binding, and revalidation is raised; any other step is blocked |
| an owner for the vocabulary | the capsule layer seeds it from Symphony's |

| | Needed from agent-core | What agent-core has (*code*) |
|---|---|---|
| H1 | reversible registration | yes: hot apply and unapply, undone in reverse order (`extension_binder.py:64-73`) |
| H2 | dependency tracking | no; the capsule layer closes capsule dependencies at bind |
| H3 | immutable versioned artifacts | for graph artifacts only, so the store is new |
| H4 | a reconstructable execution log | an append-only trajectory archive, once a rail writes Bindings to it |
| H5 | a record of what ran | tool calls only, not what code does inside (`rail.py:888`) |

## 11.9 The ownership picture

![Figure 10. Three loops and their proposed owners. Nobody owns the check on their own output; ownership is for the teams to agree.](figures/F4.png)

Ownership is for the teams to agree together, because the capsule touches every team. The proposal above follows one
rule: **nobody owns the check on their own output.**

- RSI builds, but does not admit.
- Verification checks, but does not choose.
- The pipeline uses, but does not grade.

# 12. Composites, their ceiling, and which stages may become capsules

## 12.1 Composites

A composite is a capsule whose body is `members[]` (pinned hashes) plus `wiring[]`. The gate checks it in four ways:

1. **Types.** Every wire connects an output to an input of a compatible type (ABC's C1).
2. **Covered effects.** The composite's own `needs` and `changes` cover the union of its members'. This union is
   `derived`: code computes it, and the builder never writes it (SCHEMA §3.1).
3. **Budget conservation.** The members' budgets sum to no more than the composite's (Agent Contracts, p10).
4. **Permitted versus prohibited.** No member's permitted effect is an invariant another member forbids (ABC's C3).

Members keep their own Verdicts. A composite's Verdict lists them. Revising a member produces a new member hash, so
the composite must be re-declared. This is deliberate. A composite pins exactly what was checked.

**Members gate the composite.** A composite is offered only while every member's pinned hash is still admitted, or
superseded without being withdrawn. A member that is `suspect`, `revoked` or `retired` moves the composite to
`suspect`, reason `MEMBER_UNAVAILABLE`. jiuwenswarm has had the same cascade for standard SkillPacks since 2026-09-17,
by name (§10.8).

**Team skills stay out of v1.** A Swarm Skill's Leader decides at run time which roles to involve and schedules
them (`docs/en/SwarmSkills.md:241-253`). That is planning, so it is above the ceiling. Its `dependencies.yaml` and
`bind.md` are imported as evidence only. agent-core's `team_skill_create_rail.py` suggests creating team skills; it
is not a loader.

## 12.2 The ceiling

The supervisor said AI4Research is not a capsule (note 46 §2), and note 46 §4 left open where the line falls. This
report proposes a test **(design)**:

> **A capsule is something the freeze binds to one plan node. Anything that must itself plan, freeze, admit, schedule
> or judge capsules is above the ceiling.**

Under this test:

- A team of agents with fixed roles and order inside one node could be a capsule. A team whose Leader decides the
  roles at run time plans, so it cannot (§12.1).
- A sub-pipeline that re-plans across nodes cannot.
- Composites may nest, but the freeze sees one node → one hash. A composite executes entirely within its node, under
  its own budget. It does not re-enter planning.

## 12.3 Stages that could become capsules later, and stages that must not

| Pipeline stage | Capsule? | Why |
|---|---|---|
| Operators: retrieval, source validation, synthesis, experiment runs, report drafting | yes, now | These are what capsules are for |
| Intake parsers and normalisers (document ingestion) | could, later | Typed input to typed output; no authority over other capsules |
| Delivery renderers (formatting claims) | could, later | They transform delivered artifacts; the claims themselves are fixed before they run |
| Intent extraction | only as a helper that the stage calls, not as the stage | Intent defines what "done" means for the sprint. A capsule that could be swapped by the planner would be choosing its own acceptance criteria |
| Requirement compilation | no | It produces the requirements that the filter and freeze check against |
| Planning | no | It selects capsules. A capsule that plans would select itself |
| Freeze, scheduling, dispatch | no | These are the authority the Binding records. §7.12: the checker must be out of reach |
| In-run gates that judge capsule output | no; their *checks* are runners owned by verification, referenced by hash | A gate that could be revised by RSI is a checker within reach |
| Admission gate, librarian, invalidator, screener, verifiers | never | They write the records. CC uses them as tools (supervisor, 2026-09-21) |

# 13. Spatiotemporal composability: add, replace, revert, remove

Cordis requires components to be "addable, replaceable, revertible and removable without breaking dependents" (§7.15).
The schema supports each operation as follows.

![Figure 11. Spatiotemporal composability. Space: a declared, pinned dependency, and the Standing move that marks a dependent suspect when the dependency is revoked. Time: revisions, a sprint that keeps the version it pinned, and the boundary that decides how an effect is undone.](figures/compose.png)

- **Where the terms come from.** Cordis is a formal model with one qualitative case study, and agent harnesses are its
  future work (2608.25512 p69, p82), so the schema borrows its vocabulary and boundary, not a measured result.
- **Between sprints, not within one.** Cordis swaps components inside a running process. Here a sprint keeps the
  versions it pinned (invariant 3), and change reaches the next sprint.

| Operation | How the schema does it | What Cordis guarantees at runtime, if the carrier follows it | Where it cannot |
|---|---|---|---|
| **Add** | A new Declaration is admitted, and its `injects` must be satisfied by admitted providers or be optional | Providers activate before consumers (Thm 70, p47) | A dependency cycle leaves capsules inactive (p74). The gate rejects cycles among `injects`/`provides` **(design)** |
| **Replace** (revise) | New hash, new Verdict. The replacement-compatibility check covers dependents' ports and injected keys; a new write, delete or emission forces re-screening. The Standing moves atomically | Replacement is by provider identity: dependents reload when their provider changes (p63) | Frozen sprints keep the old hash on purpose. A running operator is never swapped mid-node |
| **Revert** | The Standing moves back to `previous[0]`, and needs a valid Verdict under the current epoch | Confluence: add, remove, replace and undo reach the same state as loading the final set from scratch (Thm 80, p54–55) | Emissions made while the newer version ran are not undone (p47). The `emission` policy decides what was allowed |
| **Remove** | Two steps: stop offering (`deprecated`); retire only when no admitted capsule injects a key it alone provides | Two-step unload with a guard (p36; Alg. 5, p62–63) | Cordis does not check that an inverse is correct (p59). `inverse` reversibility is `declared` unless a check exercises it |

![Figure 12. Removing a provider without breaking dependents: stop offering, check no dependent relies on it, then unload in reverse order.](figures/F5.png)

**What the schema adds to Cordis.** Cordis has no versioning or structural typing of keys, and the paper says a
unified dependency model "remains an open problem" (p75–76). `injects[].interface_version_range` and
`provides[].interface_version` fill exactly that gap.

**What it cannot add.**

- Cordis's theorems hold only for effects routed through its context (p31, p47). A capsule body that writes files
  outside its declared scope is outside the theorem. It is caught only by the sandbox (`enforced`) or the audit
  (`audited`).
- Cordis does not sandbox (p73).

# 14. Composition screening

Capsules are **not** certified as safe together. Admission is per Declaration; composition risk is per set (§7.6).

**What the screener reads.** The schema supplies what SkillFuzz had to extract with a model:

- the modifies set: `effects[]` with resource keys and operations;
- invariants: `changes.invariants`;
- shared services and whether they are commutative: `injects`/`provides`;
- domain scope: `applies_to.domain_scope`;
- a completeness signal: `coverage.undeclared_notes`.

The same inputs, field by field:

| SkillFuzz reads (2607.02345 p4-5) | The schema supplies, authored and tested |
|---|---|
| preconditions, postconditions | `needs.when`, `guarantees.checks` |
| modifies set | `effects` of kind write, create, delete, with scopes |
| invariants | `changes.invariants`, and checks `over: each_call` |
| domain scope, abstract actions | `applies_to`, `summary`, typed `ports`; effect kinds, `kind` |
| extraction confidence | the Verdict's level and each claim's assurance; provisional and `declared`-heavy capsules first; `coverage.undeclared_notes` |
| which skills share a context | `load_mode: context_injected`; the Binding's `co_loaded[]` |
| shared services | `injects`, `provides`, `commutative` |

**Two cheap passes by code, before any model.**

1. **Resource overlap.** Two capsules that write the same resource key, or one that deletes what another reads, are
   flagged.
2. **Invariant clash.** One capsule's effect violates another's invariant. For example: "inputs are read-only" versus
   a write to that input.

These are the declarable conflicts. SkillDAG treated them as observable only (§7.8), and here they need no
observation. The model-based search then runs over sets ranked by these flags, as SkillFuzz's seed ranking does (p5).

**How findings are recorded and used.**

![Figure 13. Composition screening and where its findings go.](figures/F6.png)

**Rules for using findings.**

- A Finding's `status` distinguishes plan-level flags from execution-confirmed ones. SkillFuzz confirmed 80.6% of its
  top flags (Table II, p7), which leaves real false positives.
- `block_set` needs confirmation or review **(design)**.
- The screener's thresholds are uncalibrated (SkillFuzz p10). They go into `producer.thresholds` so that each finding
  can be re-read later against better calibration.

# 15. Worked example: `research.retrieval`

A realistic AI4Research capability: gather sources for a research question and land a provenance-complete source
pack. Today it exists as `cap.research-retrieval.yaml` (§10.6). What follows is how it *would* look and move in the new
system. Hashes are abbreviated. The composition finding in step 2 is **illustrative**, not observed.

## 15.1 The Declaration

```yaml
identity:
  schema_version: "2.1"
  name: research.retrieval
  version_label: "2.0"
  kind: skill
  carrier: {spec: PluginSpec, ref: plugins/research-retrieval}   # skill folder + fetch MCP server
  body:
    - {path: skills/research-retrieval/SKILL.md, sha256: 9f1c…}
    - {path: skills/research-retrieval/fetch.py, sha256: 41aa…}
    - {path: mcp/fetch-server.json,              sha256: c07e…}
  load_mode: context_injected                                    # a skill shares the agent's context
  summary: "Find and fetch real sources for one research question; write sources.jsonl, evidence.jsonl and raw extracts. Does not summarise or judge relevance."
  lineage: {parent: null, builder: person:muk, build_trigger: null, context_capsules: [], diagnosis_inputs: []}
ports:
  inputs:
    - {name: question, artifact_type: artifact.research_question, required: true, schema_ref: schemas/question.v1}
    - {name: scope_hints, artifact_type: artifact.scope_hints, required: false, schema_ref: schemas/scope.v1}
  outputs:
    - {name: source_pack, artifact_type: artifact.source_pack, schema_ref: schemas/source_pack.v1, check_id: pack_schema}
needs:
  when:
    - {id: has_question, check: {path: artifacts.research_question, operator: present, value: true}, state_source: sprint artifacts,
       evaluable_at: planning, max_age_s: 0, on_unknown: defer, on_unavailable: block, parity_check: parity_has_question}
    - {id: budget_ok, check: {path: budget.remaining.cost_usd, operator: ">=", value: 2.0}, state_source: sprint budget ledger,
       evaluable_at: planning, max_age_s: 30, on_unknown: defer, on_unavailable: block, parity_check: parity_budget}
  injects: [{service_key: svc.search_provider, interface_version_range: ">=1 <2"}]
  resources: [{resource_key: fs.sprint_artifacts, mode: write}]
  network: {allowlist: [search.provider.example, "*.arxiv.org", "*.doi.org"]}
  model: {tool_calling: true, min_context: 32000}
  applies_to: {task_types: [research, knowledge-extraction], domain_scope: "literature and web sources"}
  external:
    - {kind: package, value: httpx, pin: {version: "0.28.1", sha256: 3e1f…}}
    - {kind: service, value: search API, pin: {endpoint: "https://search.provider.example/v1/search", version: v1}}
    - {kind: secret, value: secret.search_api_key, guard: guard.secret_leak}      # re-checked at dispatch
changes:
  effects:
    - {id: write_pack, resource_key: fs.sprint_artifacts, op: write, scope: "artifacts/{sprint}/research/**", reversibility: scoped, risk: {severity: low, blast_radius: low, irreversibility: low}, assurance: enforced}
    - {id: query_out, resource_key: net.search_provider, op: emit, scope: "HTTPS GET to allowlist", reversibility: emission, policy: withhold_until_freeze_ok, risk: {severity: med, blast_radius: low, irreversibility: high}, assurance: enforced}
  provides: []
  invariants:
    - {id: extracts_are_fetched, statement: "Extract files contain fetched bytes, never model-authored text", check_id: extract_bytes_match}
    - {id: evidence_resolves, statement: "Every evidence row resolves to a span in its source's extract", check_id: span_resolves}
    - {id: question_read_only, statement: "The question artifact is not modified"}
guarantees:
  checks:
    - {id: pack_schema, kind: output_schema, runner: {ref: verif/pack_schema.py, sha256: 77b2…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
    - {id: span_resolves, kind: invariant, runner: {ref: verif/span_check.py, sha256: e3d9…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
    - {id: extract_bytes_match, kind: invariant, runner: {ref: verif/fetch_log_compare.py, sha256: 5a10…}, author: team:verification, written_before_body: true, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: audited}
    - {id: golden_questions, kind: eval_suite, runner: {ref: verif/retrieval_suite.py, sha256: 0c4f…}, author: team:verification, written_before_body: true, held_out: true, signal_source: harness, owner: external, anchor: judged, assurance: tested}
    - {id: parity_has_question, kind: property_test, runner: {ref: verif/parity/has_question.py, sha256: 1b2b…}, author: team:verification, written_before_body: false, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
    - {id: parity_budget, kind: property_test, runner: {ref: verif/parity/budget.py, sha256: 8e8e…}, author: team:verification, written_before_body: false, held_out: false, signal_source: harness, owner: external, anchor: deterministic, assurance: tested}
  acceptance: [pack_schema, span_resolves, golden_questions, parity_has_question, parity_budget]
  evals: [{suite_ref: verif/retrieval_suite.py, sha256: 0c4f…, metric: "fraction of questions with ≥3 resolvable sources", threshold: 0.8, held_out: true}]
budget:
  per_call: {cost_usd: 2.0, wall_s: 900, tool_calls: 60}
  enforcement: {cost_usd: between_calls, wall_s: hard, tool_calls: hard}
  on_exhaust: return_partial
  context_cost_tokens: 180
coverage:
  undeclared_notes: "Relevance of sources is not checked here; that is source-validation's job."
```

Points to notice:

- **The two prose invariants from today's manifest are now bound to checks.** They are `span_resolves` and
  `extract_bytes_match`.
- **`extract_bytes_match` compares against the harness's fetch log**, so its `signal_source` is `harness` and not the
  capsule's own claim (§7.12).
- **The third invariant has no check, and says so.** Its assurance is `declared`.
- **The relevance judge inside `golden_questions` is a model** (`anchor: judged`). The Verdict must therefore record
  its measured error, and it counts toward certification only under the false-pass ceiling.
- **Both predicates are `evaluable_at: planning`**: the question exists before planning, and the budget is known.
  So both enter the filter, once their parity checks pass, and dispatch evaluates them again on fresh state.

## 15.2 Admission

1. **Vocabulary.** Every name used is in the vocabulary: `artifact.research_question`, `fs.sprint_artifacts`,
   `svc.search_provider`, and the rest.
2. **Hashes.** The body hashes match.
3. **Structure.**
   - Every runner lives in verification's repository, outside `artifacts/{sprint}/research/**`.
   - Every acceptance check has `signal_source: harness`.
   - `svc.search_provider` is provided by an admitted capsule, `provider.search.v1`, and the secret's guard
     `guard.secret_leak` is admitted.
4. **Sandbox run.** The sandbox allows writes only under `artifacts/{sprint}/research/**` and network only to the
   allowlist. The acceptance checks run on a held-out set of questions. One attempted write to `/tmp/cache` fails the
   first run with `EFFECT_OUT_OF_SCOPE`. The builder moves the cache into scope and re-declares, which produces a new
   hash, and the run passes.
5. **Screening against likely partners.** The partners are `research.source_validation`, `guard.secret_leak` and
   `report.draft`.
   - Code pass: no shared write keys. `report.draft` reads `artifact.source_pack`, which is an ordinary data edge.
   - The model pass flags `{research.retrieval, report.draft}`: the plan drifts toward drafting text into the extracts
     directory (illustrative). The invariant clash check matches it against `extracts_are_fetched`, and a sandbox
     confirmation run shows the drift.
   - The Finding gets `action: block_set` for co-activation *in the same node*. Being on different nodes, connected by a
     data edge, stays allowed.
6. **Set-level value.** The slot's held-out replay does not fall.
7. **Verdict.** `ADMIT` at level `certified`, with:
   - `checks_run` for the five acceptance checks;
   - `precondition_parity` for `has_question` and `budget_ok`: boundary, missing and stale state, all passed;
   - `verifiers: [{id: relevance-judge, version: 3, measured_error: {false_pass: 0.04, false_fail: 0.11, n: 200,
     corpus: "defect-injected packs", date: 2026-09-20}}]` (illustrative values). At 0.04 the judge is under the
     0.05 ceiling, so its verdict counts toward certification;
   - `screening: [F-0192]`;
   - `invalidated_by: [dep:provider.search.v1, policy_epoch, verifier:relevance-judge]`.
8. **Standing.** The librarian sets `research.retrieval → 7c2e…`, `admitted`, reason `ADMITTED`.
9. **Symphony.** It receives an `add_skills` mutation. The capsule layer's `CapabilityProvider` now returns this
   descriptor with `content_hash = 7c2e…` and I/O taken from `ports`.

## 15.3 Offered and bound in a sprint

1. **Offer.** Sprint S-311 plans a node "gather sources" that consumes `artifact.research_question`. At the choice
   point, the filter evaluates the predicates:
   - `has_question`: true.
   - `budget_ok`: true. Remaining cost is 5.40, read 3 s ago.
   - `network`: the sprint's network zone permits the allowlist.
   - `applies_to`: research.

   So `research.retrieval` is offered, alongside one other retrieval capsule. A third, whose declared network zone
   the sprint does not permit, is blocked and appears to the chooser as a one-line exclusion. The chooser sees two
   summaries and their ports: 180 + 210 tokens (illustrative).
2. **Bind.** The chooser binds `research.retrieval`.
3. **Freeze.** The freeze writes a Binding:

```yaml
sprint_id: S-311
snapshot_id: snap-0311
plan_hash: 4be0…
step_id: n4.gather_sources
decl_hash: 7c2e…
verdict_ref: V-0457
level: certified
offered: [7c2e…, 88a1…]
blocked: [{decl_hash: 3b07…, predicate: network_zone, where: planning}]
offer_hash: 2d9a…
selection_tokens: 390          # illustrative; measured in M2
choice_ref: call:planner/8841
co_loaded: [7c2e…]
predicates:
  - {id: has_question, value: true, context_sha256: aa01…, where: planning}
  - {id: budget_ok, value: true, context_sha256: aa01…, where: planning}
resolved:
  - {service_key: svc.search_provider, provider_decl_hash: 51f0…}
findings_consulted: [F-0192]    # report.draft is on step n6, not co-activated
model: {model_id: routing-choice, version: …}   # written by routing's choice
step_identity: h(7c2e…, sha(question), {k(n2), k(n3)})
prev_hash: …
```

4. **Dispatch.** Dispatch re-runs both predicates on the live context. `budget_ok` is still true (3.10 remaining after
   an earlier node), and the live hash equals the pin, so the operator runs. Dispatch appends both values with
   `where: dispatch`.
   - The query emissions are allowed because the policy is `withhold_until_freeze_ok` and the freeze succeeded.
   - agent-core loads the verified body through `apply_extension_hot`, and the skill is added to
     `SkillUseRail.enabled_skills` for this node.
5. **What the run records.**
   - Output artifact hashes.
   - The sandbox's filesystem and network logs.
   - The fetch log.

   The audit compares them against `effects`. There are no writes outside scope and every host is on the allowlist.
   `extract_bytes_match` passes, and a `use_outcome` Finding is written.
6. **Delivery.** Claims delivered at the end of S-311 carry the step identities they depend on, and the Binding's
   `claims[]` lists them.

## 15.4 Revised

Two weeks later the drift probe hits the pinned endpoint `https://search.provider.example/v1/search` and gets a 301 to
`/v2/search`.

1. **Drift Finding.** The probe writes `drift` Finding F-0240, and the librarian sets `research.retrieval` to
   `suspect`, reason `SUSPECT_DRIFT`.
   - Sprints already frozen keep running on `7c2e…`.
   - New sprints are not offered it. Their offer holds the other retrieval capsule, or is empty, in which case a `gap`
     Finding opens.
2. **Repair ticket.** RSI receives it: the failed pin `external[service]`, the old and new values, and the evidence.
   It returns Declaration `b913…` with `lineage.parent: 7c2e…`, `context_capsules: [7c2e…]`, the service pinned to v2,
   and a changed `fetch.py` hash.
3. **Admission of the revision.**
   - The gate re-runs acceptance.
   - Replacement compatibility holds: same output port and type; no new write, delete or emission.
   - The Finding about `{7c2e…, report.draft}` is voided for the new hash, and a re-screen is queued. Until it returns,
     the policy admits with the block kept provisionally.
   - Verdict: ADMIT.
4. **Standing.** `current: b913…`, `previous: [7c2e…]`, reason `ADMITTED`. Symphony gets `update_skills`.

## 15.5 Revoked

The audit of sprint S-340 finds that `b913…` put the API key in the query string, i.e. in URLs that reach third-party
logs. This is an `audit_violation` against the declared use of `secret.search_api_key`.

1. **Revoke.** The librarian sets `revoked`, reason `REVOKED_SECURITY`.
2. **Find the affected work.** The invalidator lists every Binding with `decl_hash: b913…`: 14 nodes in 6 sprints
   (illustrative). Claims whose step identities descend from those nodes are marked `stale`, not deleted.
3. **Lineage.** Any admitted capsule with `b913…` in `context_capsules` becomes `suspect` (none in this case).
4. **Revert.** The Standing would revert to `previous[0] = 7c2e…`, but that version is `suspect` for drift. The revert is
   refused, and the offer for "gather sources" falls back to the other retrieval capsule.
5. **Gap.** Where that capsule is not applicable, a `gap` Finding opens. By §7.9 it reaches RSI only if it recurs.

![Figure 14. research.retrieval over time: admitted, bound, drifted, revised, revoked.](figures/F7.png)

# 16. What CC deliberately does not do

**For RSI.**

- CC does not decide what to build or how to build it.
- It does not search, mutate or optimise.
- It does not score candidates beyond the gate's typed checks.
- It does not store RSI's search tree; it keeps only `lineage` pointers.
- It never trains or changes model weights.

**For verification.**

- CC does not write verifiers, suites, parity fixtures or screeners.
- It does not measure judge error.
- It does not choose thresholds for verification.
- It *requires* these things, records them, and makes the pipeline read them.
- CC is not a verifier and does not contain one (supervisor, 2026-09-21).

**For routing.**

- CC never picks, ranks or excludes a model.
- `needs.model` is a constraint that routing may read.
- If no model meets it, the capsule is not offered. That is the filter acting on the capsule, not a routing decision.

**For the pipeline.**

- CC does not plan.
- It does not order nodes.
- It does not judge whether delivered claims are true. Claims carry step identities so that they can be invalidated;
  judging them is the pipeline's in-run gates and verification's job.

# 17. Advantages, each with what would prove it wrong

**Each advantage is stated with the result that would disprove it, so the workshop can hold the design to it.**

| Advantage | Evidence | Proved wrong if |
|---|---|---|
| **Safer selection.** What cannot run is removed by code before a model chooses, and the guarantee is by construction | 7.8% blocked-skill picks without a gate (2608.01050 p5) | a capsule passes the filter and dispatch, then exits on that same declared predicate (a parity failure), or parity checks find a false block |
| **Fewer tokens at selection.** A removed capsule's full catalog row shrinks to an exclusion line, on every repair too | 59.1% fewer description tokens after relevance matching (2608.01050 p5); 26,172 to 2,528 tokens a task (2606.07904 p8) | M2 shows no drop in `selection_tokens` against today's filter, at equal task success |
| **A kept capability's own job is tested** | 215 of 222 tools failed theirs (2604.00392 p5) | a certified capsule fails a held-out test of its declared job |
| **A lenient verifier becomes visible** | biased retirement stopped silently (2607.07436 p6) | quality retirements stop while cap evictions continue, and no verifier audit is triggered |
| **Harm is contained precisely** | cleanup after commit left 5.6 of 12.3 points unrecoverable (2608.05810 p7) | a revoked capsule's Bindings, claims or `context_capsules` descendants cannot be found from the records |
| **Every claim traces to exact capsules; imports need no rewrite** | the Binding (SCHEMA §3.5); §9.4 | a claim cannot be traced to a Binding and hash, or an import needs code changes |

What each team gets is in §11.4-11.7: RSI gets typed rejections, repair tickets and protection from unmeasured
judges; verification gets a place its checks are enforced; the pipeline gets smaller offers, typed deferral and exact
invalidation; routing gets explicit constraints.

# 18. Feasibility

## 18.1 Every part exists somewhere; the work is combining them

**Each part downstream of the schema has been built, in openJiuwen, AI4Research or a paper; no one has combined them.
Capability Capsule touches every team's work, so who owns each part is for the teams to decide together (§11.9). This
section gives the parts and an order, not a division of labour.**

| Part | Already in openJiuwen or AI4Research (*code*) | Already built in a paper |
|---|---|---|
| store, per-sprint pinning | ScienceDiscovery's content-addressed store | step identities by hash (2605.06365) |
| loading, observing | agent-core's binder and tool-call spans | not needed |
| filter, binding, fit review | AI4Research's planner | executability gate in production (2608.01050) |
| held-out tests | `program_opt` admits a candidate by held-out execution | a conformance suite per capability (2604.00392) |
| verifier apart from builder | skillhub review, bound to the package bytes | a separate verifier session (2604.01687) |
| measuring the verifier, typed verdicts | not yet | The Blind Curator; Cognitive Admission Control (2609.16313) |
| gate before commit, archive | ScienceDiscovery publish and rollback | When Self-Evolution Backfires; Darwin Gödel Machine |
| retirement under a cap, drift repair | not yet | Library Drift; Skill Drift Is Contract Violation |

The new pieces are the vocabulary, the ledgers, sandbox enforcement of effect scopes, and measured judge error.

## 18.2 Five milestones, provisional first

**An order to discuss, not a plan of record: each milestone is usable on its own, and M1 needs nothing outside this
team.**

![Figure 15. Milestones, provisional first.](figures/milestones.png)

| Milestone | What exists at the end | Needs | Measured by |
|---|---|---|---|
| M1 | versions pinned by hash in the registry, snapshot and Binding (today a change during planning aborts the freeze); Declaration, store, importer, provisional admission with a sandbox run at tool-call level; the generalist behind its fallback flag, `authoring: propose` | nothing outside this team | imports admitted without a rewrite; complete Bindings; plans that used to fail now complete on the generalist, with gap Findings |
| M2 | planning-evaluable predicates in the filter, each after its parity check | M1 | blocked-selection rate, false blocks, `selection_tokens` and task success, against today's filter; and first, the share of today's step failures that are precondition failures, which sizes the problem |
| M3 | certification: blind suites, parity checks, verifier audits | M1, the Verdict format, a sandbox for code-heavy capsules | held-out failures among certified capsules |
| M4 | the cold path with its four roles and `authoring: build`; Standing moves, monotone versions, the cap, the librarian, the audit loop, composition screening, unpinned dependencies | M3, the Declaration format for RSI | capsules admitted from recurring gaps; retirements by reason; curator health |
| M5 | agents as composites, first a gate | M4 | composites admitted with pinned members |

- **Between M1 and M3** steps that do not accept provisional capsules keep today's path: the old freeze and its `stable`
  capsules. The schema adds records around them without changing what they bind.
- **M1 is small.** Identity, carrier, ports, effects, predicates, one postcondition, file hashes; a provisional
  Verdict; the Binding. The other fields wait for the milestone that reads them.

## 18.3 Risks, each with its answer

| Risk | Answer |
|---|---|
| effects are observed only at tool-call level | code-heavy capsules stay provisional until a sandbox observes effects; tool-only capsules certify now |
| provisional admission changes today's freeze, which admits only `stable` | provisional capsules bind only to steps that accept them, so other steps see no change |
| declared ports change how Symphony builds its graph | ports are added beside today's proposed edges first, and replace them only once M2 shows no loss |
| parity needs capsules to report which predicate stopped them | required before a predicate enters the filter; without it the predicate is checked at dispatch only |
| declarations are gamed or under-declared | certified needs another author's suite; empty `needs.when` and `on_unavailable: pass` need stated reasons; observed effects are compared with declared ones; `coverage.undeclared_notes` raises screening priority |
| over-blocking starves steps and floods RSI with gaps | M2 reports false blocks and task success beside tokens; parity checks find false blocks; gap Findings count distinct sprints, not repair attempts |

- **Cost.** More work per capability, latency at selection and dispatch, and some rejections a person would accept.
  Provisional imports and floating dependencies keep it down.

## 18.4 The test that decides whether the combination works

**Each paper shows a part works in its own setting, not that the whole works here. Only a comparison on AI4Research's
own tasks, against curation by observation, can show that.**

| Arm | Library | Prediction |
|---|---|---|
| 1 | no library | the baseline |
| 2 | a library built without admission | more kept capsules fail their own job, and more that cannot run are offered |
| 3 | the same library curated by observation: a judge retires capsules by outcome | the comparison the design must beat, not only no curation |
| 4 | the same library under this schema: admission, the declared filter, Standing | fewer kept capsules fail their own job, fewer that cannot run are offered, fewer selection tokens, and task success no lower than arm 3 |

- Same tasks, same models, same budget. Reference answers curated by verification, pinned as data dependencies.
- An ablation of arm 4 with the filter alone separates what admission adds from what the filter adds.

# 19. Questions for the room, each with a default

**These decisions belong with other components. Each has a default, so none blocks M1.**

| Question | With | Default |
|---|---|---|
| Who owns the model that binds capsules at planning? | planner owners | AI4Research's planner binds typed plan steps; Symphony supplies retrieval within the offer. Symphony's fast planner infers edges and reads an unpinned runtime-weight overlay, so it binds only once both are pinned |
| Who owns the vocabulary? | Symphony | the capsule layer, seeded from Symphony's |
| Fail open or closed when state cannot be read? | each capsule's builder | closed: defer or block, stated per predicate |
| What false-pass ceiling counts toward certification? | verification | 0.05 until measured |
| May a judge with no measured error admit anything? | verification | only provisional, under a policy risk ceiling; never certified |
| Who owns the observing sandbox? | verification, agent-core | the capsule layer, on agent-core's tool-call hooks |
| Who owns composition screening? | verification | open |
| What counts as a different author for tests? | RSI, verification | a separate session with no access to the implementation |
| How are model candidates expressed? | routing | pinned model ids with versions, widened only with re-verification |
| Where is the ceiling on capsule size? | all | what the freeze binds to one plan node (§12.2) |
| Who acts as librarian? | all, supervisor | capsule-layer code, with a named person for revocations and `outside_cap` pins |
| Are team (Swarm) skills admissible? | supervisor, all | not in v1: the Leader plans; revisit if a team skill's roles and order are fixed |
| Must evolution overlays (teammate experience, TTSE) pass the gate before a sprint loads them? | RSI, jiuwenswarm owners | pinned per sprint; a new overlay is a provisional revision |
| Generalist defaults for AI4Research? | pipeline, RSI | `generalist_fallback: on`, `authoring: propose` until M4, `generalist_cap` set per plan size |
| Should RSI add a held-out split inside its own loop? | RSI | optional: admission's held-out checks come from verification either way |
| What does a dispatch-time DEFER do in a frozen sprint? | pipeline | wait up to `max_age_s`, then a pre-approved fallback, then fail with `precondition_unknown` |
| How does a SKILL.md body report its exit predicate? | capsule layer | a `report_exit(predicate_id)` tool; if uncalled, `exit` is none and parity for that capsule is measured, not by construction |
| If M2 shows more false blocks than tokens saved? | all | the offending predicate leaves the filter and stays at dispatch; the filter is withdrawn per predicate, not globally |

# 20. What the schema does not claim

- **It does not claim that declared capsules are correct.** It claims that what was checked is recorded, and that what
  was not checked is labelled.
- **It does not claim safety in combination.** Screening reduces composition risk. Nothing certifies a set.
- **It does not undo emissions.** It only controls when they are allowed.
- **It does not fix degradation at scale on its own.** Much of it is the agent using no skill at all, which a
  filter cannot fix (2605.24050 Table 2).
- **It does not promise identical replays.** A model behind an API changes; sprints are recoverable, not
  byte-identical.
- **It does not promise task success.** Passing the filter means no declared exit holds, not that the capsule
  will succeed or was the right choice.
- **It does not make token budgets hard.**
- **It does not verify Cordis-style inverses** unless a check exercises them.
- **The design has not been measured as a whole.**
  - The numbers in §7 are the papers' own, in their own narrow setups.
  - None of them tested this design.
  - The worked example's findings, hashes and error rates are illustrative.
- **It does not claim that a model judge is trustworthy.** It claims that a judge with no measured error cannot certify,
  and can admit only under a policy risk ceiling **(design)**.
- **It does not settle ownership, the ceiling, or the default thresholds.** The ceiling is proposed (§12.2). The
  recurrence threshold of 2, the overlap policy and the risk ceilings are all **(design)**.
- **It does not describe a system that exists.** The capsule layer is a proposal. Only the code cited as "today" and
  the openJiuwen sources exist.

# 21. Topic register

Every topic either document carried, and where it now lives. A topic may move; it may not disappear silently.

| Topic | Where |
|---|---|
| The schema on one screen; the governing rule; invariants | §1; SCHEMA §1 |
| Requirements a-g | §2 |
| Definitions | §4; SCHEMA §2 |
| Supervisor's rulings; the slide's components mapped, with Ground Truth | §5 |
| Tool catalogue; why the papers come where they do | §6 |
| Paper-by-paper motivation (21 papers), each ending in tool, fields and teams | §7.1-7.16 |
| Declarative versus observational; its limits; why AI4Research needs it most | §8 |
| Two levels and per-claim assurance; activation | §9.1 |
| Goals the schema serves, including self-improvement | §1, §2 |
| Today's capsules compared record by record | §3 |
| Three clocks, the reuse boundary, the cold path's four roles | §9.6 |
| The generalist capsule | §9.7 |
| Four ways to update, monotone versions, retirement policy | §9.8 |
| Protected components, what the system may change, unattended runs | §9.9 |
| Predicate parity: rules, `evaluable_at`, failure modes as records | §9.2, §7.3 |
| Selection funnel and token savings, scoped to AI4Research | §9.3 |
| Imports of ToolCard, MCP, skills, A2A, old manifests | §9.4 |
| Floating dependencies with contracts | §9.5 |
| Where each approach gets its reference for "correct" | §10.0 |
| Symphony fingerprint versus Declaration | §10.1 |
| ToolCard, PluginSpec, the binder, SkillUseRail | §10.2 |
| Skills (skillhub, jiuwenswarm); MCP and A2A; ScienceDiscovery; AI4Research today | §10.3-10.6 |
| Is a capsule a skill? | §10.7 |
| Position in the sprint and in openJiuwen; hooks and their gaps | §11.1-11.2 |
| Plan steps and dependencies, today and in the schema | §11.3 |
| RSI, verification, routing | §11.4-11.6 |
| What each side gives and needs; if a dependency is not there yet; H1-H5 | §11.7-11.8 |
| Ownership loops (three loops) | §11.9 |
| Composites and their ceiling; which stages could or must not be capsules | §12 |
| Spatiotemporal composability (Cordis) | §13, §7.15 |
| Composition screening and the SkillFuzz field mapping | §14, §7.6 |
| Worked example, end to end | §15 |
| What CC deliberately does not do (staying in lane) | §16 |
| Advantages, each falsifiable | §17 |
| Parts already built, milestones, risks, cost, the four-arm test | §18 |
| Questions for the room | §19 |
| What the schema does not claim | §20 |
| jiuwenswarm: skill corpus, SkillPacks, Swarm Skills, evolution overlays | §10.8; `DERIVATION.md` stream D |
| RSI as it is in code; its gate as builder evidence | §11.4 |
| Enforcing declared tool-level effects | §11.2 hooks table |
| Derivation of v2.1 from all evidence | `DERIVATION.md` |
| Figures from the papers | Appendix A |
| Evidence ledgers | `../verify/PAPER-LEDGER.md`, `../alt/READ-LOG.md` |

**Not yet covered by any version** (candidates for the next pass):

| Topic | Why it may matter |
|---|---|
| cost of certification per capsule | needed for feasibility once ownership is decided; jiuwenswarm's RSI `Usage` record (tokens, calls, cost) is the pattern |

Settled in v2.1:

- **`summary` as an injection path.** It is shown as quoted data and may not name other capsules or tools
  **(design)**.
- **Concurrency.** Standing moves are serialised per name, sprints read one snapshot, and reverts wait for active
  builder tasks. The last rule is RSI's own (§11.4).
- **Migration.** A migration is a new Declaration that keeps its Verdict only if the checks are unchanged
  **(design)**. See SCHEMA §4.7.

**Considered and left out:**

| Topic | Why it was left out |
|---|---|
| The slide's formal layer (SysML v2 → TypeScript → JSON Schema → Knowledge Graph) | The slides are prior thinking (note 46). The schema needs a validated serialisation; which chain produces it is an implementation choice |
| The five capsule kinds on the slide (Research, Compliance, Data, Report, Tool) | They are unglossed names (note 45 §6.3). `kind` here is a loading distinction (tool, skill, …); domain grouping is `slot` |
| Signing and key management for ledgers | Needed in production (RelAIBuild's machine-local HMAC is forgeable, p12, p34), but it does not change the schema's shape |
| A numeric trust score per capsule | Rejected on evidence: compensatory scores bypass hard conditions (§7.7) |
| Cost and economics of admission | No paper here measures admission cost for this design; Library Drift's call counts (p5) are for a different loop |
| Papers in `capsule-openjiuwen/papers/` beyond the 21 in the brief | Not read in full in this pass, so not cited |
| jiuwenswarm SkillDev stage internals and ScienceDiscovery's design docs | Reported by the survey reader; only the lines cited in §10.3 and §10.5 were checked by the author, and the rest is flagged there |

# Appendix A. Figures from the papers

Each figure is cropped from the paper's own PDF by `../deck/figures/extract_paper_figs.py`, with its page and caveat.

![Figure 16. Don't Offer What Can't Be Done (2608.01050), Fig. 1, p4: the three-stage pipeline. Only stage 2, a deterministic gate on each skill's own exit conditions, removes candidates.](figures/papers/dont-offer-pipeline.png)

![Figure 17. Don't Offer What Can't Be Done (2608.01050), Fig. 2, p4: skill-description tokens. The gate removes 59.1% after semantic matching, 90.5% combined. Ten skills, one month; description tokens only.](figures/papers/dont-offer-tokens.png)

![Figure 18. Contract2Tool (2606.07904), Table V, p8: a keyword top-5 filter cuts tokens but lowers success; contract-based filtering exposes one tool, cuts tokens tenfold and raises success. Synthetic registry, mocked execution.](figures/papers/contract2tool-exposure.png)

![Figure 19. More Skills, Worse Agents? (2605.24050), Fig. 1, p3: pass rate falls as the library grows from the oracle skills to 202. Human-authored skills; 38 task-model pairs.](figures/papers/more-skills-drop.png)

![Figure 20. The Blind Curator (2607.07436), Fig. 2, p5: deterministic checks and an LLM judge catch different defects. One domain; flag rates, not scores.](figures/papers/blind-curator-qc-vs-judge.png)

![Figure 21. When Self-Evolution Backfires (2608.05810), Fig. 4, p7: rollback after the fact recovers little; removing the source skills recovers 1.7 of 12.3 points, and the pool gated before commit ends at 72.0%. One run.](figures/papers/backfires-contamination.png)

![Figure 22. SkillFuzz (2607.02345), Fig. 6, p9: severe drift rises with the number of co-activated skills, from 4.7% to 66.5%.](figures/papers/skillfuzz-depth.png)
