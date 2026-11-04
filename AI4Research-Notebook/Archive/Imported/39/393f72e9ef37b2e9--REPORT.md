# Capability Capsule: a schema for picking, verifying, improving and removing capabilities in AI4Research on openJiuwen

Muk Chunpongtong, 2026-09-22. The source of truth is `merged/SCHEMA.md` (v2.8). Every cited paper was read in full,
and every fact about openJiuwen, jiuwenswarm and AI4Research was read in source at agent-core `e23806c1`, jiuwenswarm
`02b37f47f` and AI4Research `b0bf165f9`. **(design)** marks a decision the research motivates but does not prove. None
of the numbers below measures CC itself, which has not been built: each comes from its paper's own setting.

**How to read it.** Chapter 1 states the problem. Chapter 2 answers the seven workshop questions, a to g, each with
its evidence, and ends with how each part of the schema serves the tools around it. Chapters 3 to 8 give the detail
behind the answers, chapter 9 follows one capability through its life, chapter 10 compares today's capabilities with
the schema record by record, chapter 11 lists what the schema does not claim, and chapter 12 says which parts of the schema
come first and which come later. Appendix A says what each
openJiuwen and AI4Research part CC uses does, and Appendix B reproduces figures from the papers.

# 1. What Capability Capsule is, and the problem it solves

**Capability Capsule (CC) is a schema: the contract every capability in the AI4Research workflow declares, and the
records kept about it.** A capability is anything an agent can call on to do part of a job: a tool, a skill folder, an
MCP server, an A2A agent, a subagent. CC is built onto openJiuwen's agent-core. It is a scheme that uses tools, such as
a filter, a gate and verifiers, and is never a tool itself (supervisor, 2026-09-21).

**The problem.** AI4Research turns a research request into a frozen plan of steps, and each step's capability feeds
the next. A capability that is wrong, or cannot run, spreads its error into every later step and into the delivered
claims. Today, capabilities either declare almost nothing or declare a lot that nothing checks:

| | A jiuwenswarm skill | An AI4Research capsule |
|---|---|---|
| **What it declares** | a name and a description (33 of 34 bundled skills) | every field, with task types in all 85 manifests |
| **Inputs, outputs, effects** | none declared (0 of 34) | types and effect names, with no scope and no undo |
| **Preconditions** | in prose only (13 of 34) | 44 of 95 declared preconditions are kinds dispatch never evaluates |
| **Identity** | copied in with no hash | only the manifest file is hashed, not the code |
| **Limits** | `allowed_tools` is never read by agent-core's skill rail; permissions ship off | a missing status counts as stable |

Most systems learn that a capability was wrong by **observing** it afterwards. CC has each capability **declare** what
it needs, does and changes, because a declaration can be checked, and found wrong, before any sprint relies on it.
Observation keeps a role: it can lower trust, never grant it. And CC is strict only where it must be: it refuses a run
only for safety, and records every quality shortfall as a label on the result, so research that can only be judged
still runs.

# 2. The answers, a to g

## a. Function: CC makes capabilities easier to pick, verify, improve and remove

![Figure 1. The function of CC: four verbs resting on one schema.](figures/V1.png)

| | What makes it easier | Evidence |
|---|---|---|
| **Pick** | Inputs and outputs are known, and a capsule holds no task, so it is found by what it takes and returns. Code removes every capsule whose declared requirements do not fit the step; a model then chooses among the few left, reading only a short summary and the ports. Selection is cheap *because* it is strict | without a code gate, a model picked an unrunnable skill in 7.8% of 1,000 conversations (Don't Offer What Can't Be Done, 2608.01050 p5) |
| **Verify** | Everything is declared, so every check has a target: held-out tests of the declared job, observed effects against declared ones, and a hash proving the checked thing is the thing that runs | 215 of 222 self-built tools failed held-out tests of their own job (Beyond Task Completion, 2604.00392 p1, p5) |
| **Improve** | Performance, trust and lineage are kept in records the builder cannot write. The library is a version tree, a child inherits its parent's tests, and RSI chooses where to branch | an ungated skill pool fell from 62% to 50% as it grew; a pre-commit gate reached 72% (When Self-Evolution Backfires, 2608.05810 Table 1) |
| **Remove** | Each capsule declares what it needs, what it provides and how each effect is undone, so it can be replaced, reverted or removed without breaking what depends on it, and a revocation reaches exactly the runs that used it | cleanup after harm won back only 1.7 of 12.3 points (2608.05810 p7) |

## b. Architecture: the capsule's records, and the run's records

![Figure 2. What CC keeps about one capability in the library (left), and what the workflow keeps about one run (right). The planner writes what a DAG node needs and never writes to a capsule. The freeze assigns capsules to the node by hash, and dispatch records each run.](figures/R1.png)

**Each fact lives with the party accountable for it.** The builder cannot write its own Verdict, and nothing that runs
can edit what it promised:

| Record | Written by | Holds | Why it exists |
|---|---|---|---|
| **Declaration** | the builder, once; a change is a new Declaration | identity, lineage, ports, needs, changes, guarantees | what the capability promises |
| **Verdict** | the admission gate | outcome, level, typed reasons, the suites and judges used | whether this exact hash was checked, and how |
| **Standing** | the librarian | the current version per name, its history, its state | which version is live, and may it be offered |
| **Finding** | screeners, audits, probes, and the planner for gaps | a gap, a fit failure, drift, a use outcome, a composition risk | what was learned later. A Finding can lower trust, never grant it |
| **Binding** | the freeze, then dispatch | the capsules serving one DAG node, by hash and role, with fallbacks, and one invocation per run | which capsule served which node, and what each run did |

- **Hash.** `decl_hash` covers the Declaration and every file of the body, so a check proves exactly what ran.
  `contract_hash` covers the contract alone, so a test suite written before the code stays bound to it.
- **Parentage and provenance** live in the Declaration: `identity.lineage.parent` and `identity.lineage.provenance`.

**The Declaration's fields.** One unified schema for every kind of capability, with a required core and optional parts
declared when they apply:

| Section | Required fields | Optional fields |
|---|---|---|
| `identity` | `name`, `kind`, `carrier`, `body[].sha256`, `summary` (at most 400 characters), `load_mode` | `overlays[]` |
| `identity.lineage` | `parent`, `relation`, `builder` | `co_parents`, `context_capsules`, `provenance`, `build_trigger`, `builder_ref` |
| `ports` | `inputs[]`, `outputs[]`, each output naming the check that validates it | |
| `needs` | `when[]` (preconditions a program can evaluate), `external[]` (its own dependencies, pinned by default), `network` | `resources[]`, `injects[]`, `model` |
| `changes` | `effect_class`, `effects[]` with scope, `idempotent` and reversibility | `provides[]`, `invariants[]` |
| `guarantees` | `checks[]`, `acceptance` | `evals[]`, `exempt` (generalists only) |
| `budget`, `members` | a budget for agents, `members[]` for composites | |

A Declaration **describes a capability, never a use**: it names no step, task, workflow stage, capsule to run with, or
worker. And **the author answers for what the capability does**: what it touches, whether it can be undone. CC answers
for checking that declaration against what it observes.

**How the capability itself is held.** The Declaration never contains the code. It names the agent-core carrier that
loads it and hashes every file:

| Kind | Carrier in agent-core | What is hashed |
|---|---|---|
| skill | `SkillSpec`, a `SKILL.md` folder | every file in the folder |
| tool | `ToolCard` | its source files |
| MCP server | `McpServerSpec` | its files, or, if remote, endpoint, version and a fingerprint of its tool list |
| A2A agent | the A2A client | endpoint, version and a fingerprint of its card |
| agent, generalist | `AgentTemplateSpec`, through a harness provider | the template files |
| composite | its members | each member's `decl_hash` |

**Trust: refuse only for safety, label everything else.**

| Level | Reached by | Runs on | Its claims |
|---|---|---|---|
| **exempt** | generalists only, enrolled on safety and a smoke run | steps nothing else fits | never supported |
| **provisional** | loads, stays within its declared effects, passes one postcondition | any step that does not require certified capsules | supported only where every gating check is code, a reference, or a calibrated judge |
| **certified** | held-out tests by another author, measured judges | any step | supported where its checks pass |

A run is refused only for identity or safety: a wrong hash, a write to a protected component, an effect outside the
declaration, an irreversible effect without approval, or a revoked capsule. Everything else becomes a label on the
result, with a reason. Judges gate from the first day, and 5% of their passes are re-checked so they calibrate in
normal use (§5). Refusing on missing evidence has a cost: without fetching missing evidence, 90 of 120
effects completed instead of 120 (Cognitive Admission Control, 2609.16313 p10). There is no numeric trust score anywhere.

## c. Position: every stage applies capabilities; CC's control acts at planning, freeze and dispatch

**The unit is the work a stage does, not the stage.** Every stage that does work picks, binds and runs a
capsule: `intent -> IntentIR` is a capability, and so is the faithfulness check that assesses it. The
workflow keeps its shape -- stages, ordering, scheduling and gates all stay where they are -- and what
changes is that a stage's work is supplied by a declared capsule instead of being hardcoded.

**The workflow does not become a capsule.** That reading was ruled out on 2026-09-18 and is not what this
says. What is never a capsule is anything that **decides**: the planner's filter and binding, the freeze,
dispatch, the admission gate, the librarian, and the gate's own rules and suites. A capsule may produce
an **assessment**; it may never be the thing that decides. The schema enforces this by write access, not
by classifying intent: no capsule may write to the gate, the suites, the logs admission reads, or the
record stores.

![Figure 3. Every stage applies capabilities. The workflow's stages keep their shape and draw their work from the library; control -- the planner, the freeze, dispatch, the gate and the librarian -- stays above the line and is never a capsule.](figures/scope.png)

**Where CC's own control acts: planning, the freeze and dispatch**, plus the in-run gates and delivery.

![Figure 4. Where CC acts in one sprint: at planning, at the freeze, at dispatch, in the node gates and at delivery. Admission, audits and the librarian run outside the sprint. Everything runs on agent-core.](figures/P1.png)

**How AI4Research selects capsules today, and what CC changes.** AI4Research already filters by code before any model
looks (`elastic_planner.py:4553-4648`, `capability_admission.py:12-26`). What it filters on, and what the model then
reads, is where CC differs:

| | AI4Research today | With CC |
|---|---|---|
| **The code filter** | input and output types, effects in both directions, network policy, proof classes, trust class, and admission status | the same, plus declared preconditions, model limits, Standing and composition |
| **Preconditions** | never read by the filter; dispatch evaluates four kinds and skips the rest, 44 of 95 | one predicate, evaluated at planning and again at dispatch by the same code |
| **Task type** | only checked to be non-empty | not in the capsule at all; it belongs to the plan step |
| **What the model reads** | the full catalog rows of every eligible capsule, for every node at once, in one prompt, again on repair (`:4678-4760`) | a short summary and the ports of each node's survivors |

Evidence that filtering on declared requirements pays: a gate on skills' own exit conditions removed 59.1% of
description tokens (2608.01050 p5), and on a synthetic 100-tool registry a filter on declared contracts reached 0.980
success at 2,528 tokens a task, against 0.620 for a keyword filter (Contract2Tool, 2606.07904 Table V).

**Capsules are assigned to DAG nodes at the freeze.** The planner writes what each node needs and never names or
writes a capsule. Code filters, a model chooses, and the freeze assigns capsules to nodes by hash. The workflow's own
scheduler keeps order, parallelism, workers and retries. A capsule holds no task, so the same capsule serves any node
its ports fit: today 42 of 85 capsules name the capsule that must run before them, and CC removes that (§8).

![Figure 5. How a plan is built and run. Demand (the plan) and supply (the library) meet only at the freeze.](figures/S1.png)

**Outside the sprint,** admission decides what may be offered, audits re-check what was admitted, and the librarian
keeps Standing. **Symphony** is downstream: CC
decides what it may index, and Symphony retrieves and ranks within that (§2e).

## d. Dependencies: what CC itself depends on

This is about CC as a system. A capability's own dependencies are something else: fields of its Declaration, pinned by
default, or unpinned with a written purpose at a cost to trust (§6).

![Figure 6. What CC depends on: the systems it runs on, the teams it relies on, the models it uses, and the materials it is built from.](figures/D1.png)

| On | What CC uses | If it is missing |
|---|---|---|
| **agent-core** | carrier specs, the binder, rails, the trajectory store, the permission engine, sandboxes, openJiuwen's stores | CC needs configuration only, no change to agent-core |
| **Symphony** | its provider and graph-update interfaces | Symphony keeps working, but indexes unchecked capabilities |
| **The AI4Research workflow** | the planner, the requirement compiler (each step's acceptance), the freeze, the scheduler, the node gates | nothing to act on |
| **Authors and importers** | truthful Declarations | CC finds the mismatch later, by observation |
| **RSI** | builds from gap Findings, reads the tree and its parents' visible suites, chooses where to branch | capabilities come only from importing existing ones |
| **Verification** | check runners, held-out suites, judges and their measurement | only code and reference checks count |
| **Routing** | picks models within each capsule's declared limits | none: CC never picks models |
| **Models** | a chooser, a fit reviewer, judges, and generalists such as a Codex and a Claude generalist | steps nothing fits fail and leave nothing to learn from |

**Reuse first.** Where openJiuwen, jiuwenswarm, Symphony or AI4Research already does something, CC uses it. What CC adds
new is only the Declaration format, its records, one predicate evaluator shared by the filter and dispatch, the
admission gate, judge standing, and the tree index. Chapter 8 maps each part to the openJiuwen piece it reuses.

## e. Similar designs: Symphony first, then others, then papers

**How Symphony works.** Symphony is agent-core's module for skills, subagents and agents as capability assets. It takes
capabilities in through a provider interface, describes each with a fingerprint derived from its description and I/O,
lets the agent browse them as a tree by meaning, links them with edges a model proposes (kept at confidence 0.7 or
more), and has Fast and Beam planners turn candidates into a route the user confirms. It learns from outcomes; six of
its nine evaluation metrics are model judges, off by default, and a saved route counts as verified after one
successful run.

| Symphony stage | On its own | With CC upstream |
|---|---|---|
| intake | whatever the product installed | only admitted capsules, with `content_hash = decl_hash` and declared I/O, which its extractor already prefers |
| retrieval | by meaning, before any requirement is checked | after CC's code filter removes what cannot apply |
| edges | proposed by a model; an `unknown` input matches any same-named output | declared, typed ports |
| quality | accumulated inside the fingerprint | in records the builder cannot write; Symphony's signals can lower trust, never grant it |
| versions | one revision per id | pinned per sprint, in a version tree |

**Most designs observe; CC declares and checks.**

| Design | How it knows a capability is right | How CC differs |
|---|---|---|
| **Symphony** | a fingerprint derived partly by a model, quality from use | declared, checked, and kept apart from quality records |
| **jiuwenswarm skills** | a name and description; SkillPacks list members by name; Swarm Skills list dependencies by name, each with a purpose, checked by the agent at start-up | the same instincts, checked by code and pinned by hash |
| **Darwin Gödel Machine, RSI's tree** | keeps every variant, picks parents by score | the same tree with each node's record exposed; the parent is RSI's choice, and a child must pass its parent's tests |
| **Skill Drift Is Contract Violation** | probes skills with contracts it extracts | the author declares the contracts |
| **SkillProbe** | compares declared and actual capabilities, extracting the declared side from prose | the declared side is structured |
| **Don't Offer What Can't Be Done** | a deterministic gate on a skill's own exit conditions, at selection | the same idea, from admission to dispatch |

**A skill, Symphony and a capsule are different things.** A skill is one capability. Symphony is a system that finds
and chains capabilities. A capsule is the contract and records around any capability, a skill included. CC wraps
skills and feeds Symphony; it replaces neither.

## f. Advantages: why declaring is better, each stated so it can be proved wrong

**For picking and verifying:**

| Advantage | Evidence | Proved wrong if |
|---|---|---|
| **Safer picking** | Don't Offer What Can't Be Done: a model picked an unrunnable skill in 7.8% of 1,000 conversations without a gate | a capsule passes the filter and dispatch, then fails that same declared precondition |
| **Cheaper picking** | same paper: 59.1% fewer description tokens | M2 shows no drop against today's filter, at equal task success |
| **Fewer, right options** | More Skills, Worse Agents? (2605.24050): pass rate fell by 0.21 (95% CI 0.15 to 0.27) as a library grew to 202 skills | a small library does worse than a large one |
| **Verified job** | Beyond Task Completion: 215 of 222 self-built tools failed held-out tests of their own job | a certified capsule fails a held-out test of its job |
| **Honest effects** | SkillProbe (2603.21019): 30.4% of the top 2,500 ClawHub skills were flagged conditional | a certified capsule is seen with an undeclared effect |
| **Visible judges** | The Blind Curator (2607.07436): a biased judge silently stopped retirement | retirements stop and no audit follows |

**For improving and changing the library:**

| Advantage | Evidence | Proved wrong if |
|---|---|---|
| **Gated growth** | When Self-Evolution Backfires: an ungated pool fell from 62% to 50%; a gated one reached 72% | the gated library does worse |
| **Build on recurrence** | AllocBench (2607.23332): models committed to building at first sight 85 to 99% of the time | recurring gaps go unbuilt |
| **Useful verifier feedback** | CoEvoSkills (2604.01687): 71.1% with diagnostics from a verifier that never sees the source, 41.1% with the oracle's pass or fail alone | builds with practice feedback do no better than pass or fail alone |
| **Precise removal** | When Self-Evolution Backfires: cleanup after harm won back 1.7 of 12.3 points | a revoked capsule's uses or claims cannot be found |
| **State known first** | SkillProbe, citing a 2026 study: about 13% of 10,240 MCP servers had undocumented high-risk operations | an admitted capsule changes external state it did not declare, and no audit catches it |
| **Works from day one** | Cognitive Admission Control: without fetching missing evidence, 90 of 120 effects completed instead of 120 | judged research steps end with nothing that may run |

**What each study did, and what it showed.** The tables above give one number per advantage. This is what happened
in each study, and what CC takes from it. Every number is from the paper's own setting, not from CC.

- **Don't Offer What Can't Be Done** (2608.01050, p1-p6). A production customer-care assistant with ten skills. Before
  the model chose, code evaluated each skill's own hard-exit condition against live account state and hid what could
  not run. It removed 59.1% of description tokens, and in 1,000 risk-enriched conversations replayed with every skill
  visible, the model picked a skill the gate would have blocked 78 times. The authors say that rate must not be
  extrapolated, and name two conditions for soundness: the same predicate as the skill's own logic, and fresh state.
  CC takes the gate and both conditions, and applies them at admission, planning and dispatch.
- **More Skills, Worse Agents?** (2605.24050, Tables 1-2, p9). SkillsBench tasks with two models, each run with only
  its helpful skills and then inside libraries of 52, 102 and 202. At 202 the pass rate fell by 0.21 (95% CI 0.15 to
  0.27). A look-alike skill chosen instead of the right one explained 0.14, and extra context was not distinguishable
  from zero. Runs using no skill rose from 12.0% to 38.5%. CC filters by code first, shows the chooser only a summary
  and ports, and starts small. The paper suggests pre-filtering but did not test it.
- **Contract2Tool** (2606.07904, Table V, p8). On a synthetic 100-tool registry with mocked execution, filtering by
  what each tool requires and produces reached 0.980 success at 2,528 tokens with learned contracts and 0.990 with
  correct ones, against 0.775 at 26,172 with every tool shown. Accurate contracts are what such a filter needs; that
  learned ones came close is why CC's importer proposes and a person confirms.
- **Beyond Task Completion** (2604.00392, Table 5, p5-p6). Agents built their own tools in-session, and each tool was
  then run against held-out suites for the job it claimed, suites first checked so that hand-written references score
  1.00. 215 of 222 scored 0. One tool passed its own self-written tests and helped its session reach 0.95 task
  completion, then scored 0.00. So admission needs a check written by someone other than the builder.
- **CoEvoSkills** (2604.01687, Fig. 4, Table A1). Skills evolved with a verifier that never saw their source reached
  71.1%, against 53.5% for human-curated skills. Replacing the verifier's diagnostics with the oracle's bare pass or
  fail dropped it to 41.1% (one run, same tasks for evolving and scoring). The ablation shows diagnostic feedback
  matters, not separation itself. CC gives practice feedback from a separate verifier, and keeps the sealed gate at
  pass or fail.
- **SkillProbe** (2603.21019, p10-p13). An audit of the top 2,500 ClawHub skills comparing declared capabilities, read
  from prose by regex and a model, with what the code does. 9.9% were clean and 30.4% conditional, at every popularity
  tier, and on the same 20 skills one model said 45% conditional and another 5%. CC has effects declared as data,
  rejects undeclared ones, and records which judge ran.
- **Darwin Gödel Machine** (2505.22954, p69-p71). A self-improving coding agent whose hidden checker read marker tokens
  emitted by the agent's own code. The agent removed that logging despite instructions and scored without solving the
  problem. Keeping an archive of every variant also beat always building on the latest. So a check counts only if it
  and its evidence are out of the capability's reach, and the library is a version tree.
- **The Blind Curator** (2607.07436, Table 1). A loop that retires skills by judged contribution, run with judges of
  known bias. At a false-pass rate of 0.45 retirement can never fire, at any sample size; real retirements fell from
  1.3 to 0.3 at that rate, and to 0.0 at the milder and harsher rates also tested, while evictions by the size cap kept
  the counts moving. The authors' own real judge was strict, so this is
  a measured risk. CC gives judges a standing earned on planted defects.
- **Cognitive Admission Control** (2609.16313, Table 2, p10). A deterministic controller over 2,730 synthetic trials
  admitted 0 harmful effects in 390, against 30 for a live-policy check and 180 for authorisation alone. Without
  fetching missing evidence it completed 90 of 120 effects instead of 120. Separately, the paper proves that a scalar
  rule with a compensatory score admits some case that violates a required condition (Prop. 1, p6), which is why its
  own controller uses none. CC's verdicts are typed, a missing fact defers with a request, and there is no score.
- **When Self-Evolution Backfires** (2608.05810, Tables 1-2). A skill library grown on Terminal-Bench 2 over five
  rounds peaked at 62% ungated and fell to 50% at 179 skills. Gated before commit, it reached 72% with 37. Of a
  12.3-point drop, rollback won back 1.7 and an oracle clean-up of descendants 5.0 more, because nobody had recorded
  what each builder saw. CC gates before commit and records the builder's context in lineage.
- **AllocBench** (2607.23332, Table 1). Models that waited for recurrence in the abstract committed to building at
  first sight 85 to 99% of the time (three of four) once asked to write a script. Waiting for a second occurrence
  scored 43.0 against 34.6. So code counts recurrence and asks RSI to build.
- **SkillFuzz** (2607.02345, Tables I-II). Searching a 196-skill library for benign sets that steer planners to goals
  nobody asked for found 1,188, with 80.6% of the 98 riskiest confirmed when executed. The screener had to extract each
  skill's contract from its instruction prose, because a skill carries no structured declaration to read. CC supplies
  that structure, so nothing needs extracting. The paper did not compare extracted contracts with declared ones. Sets
  are screened, never certified.
- **Skill Drift Is Contract Violation** (2605.10990, Table 2). Probing contracts on each skill's packages, URLs and
  APIs found drift with 0 false alarms in 599 negatives and 76% best recall. Repair given the failed contract worked 25
  of 32 times, though not significantly better than plain drift text. CC pins by default and asks an unpinned
  dependency to state its contracts.
- **Cordis** (2608.25512, Thm 80). It proves that when components declare needs, provisions and an inverse for every
  effect, any order of add, remove, replace and undo reaches the same state. It does not check that an inverse is
  correct, and a sent message stays sent. CC checks declared undo and gives emissions their own policy.

**Two real examples.** Both capabilities exist today, and every fact was read in source. What CC would do is design.

*A jiuwenswarm skill that posts to Feishu undeclared.* `advanced-daily-report` declares a name, version, description,
tags and `allowed_tools: [read_memory, write_memory, bash, read_file, write_file]`
(`resources/agent/workspace/skills/advanced-daily-report/SKILL.md` lines 1-7). Its body reads Git and a NetEase
mailbox through scripts and pushes reports to Feishu on a schedule (lines 11, 19-20, 73). agent-core's skill rail
reads only the description and never `allowed_tools`, and permissions ship off, so nothing limits or records any of it.
Under CC those effects are declared, the skill is irreversible, it is offered only on steps that allow external
posting, and each post goes through openJiuwen's own permission engine as an `ASK`.

*An AI4Research approval that planning never sees.* `cap.research-experiment-run` declares `approval_satisfied`,
"Required approval is present for non-fixture or external modes" (`cap.research-experiment-run.yaml:32-33`). The
planner's filter never reads preconditions, and dispatch evaluates four kinds and skips this one
(`capability_capsules.py:1220-1242`), so a plan can be bound and frozen and fail mid-sprint. The worker checks
approval itself, and its own comment calls that "the only remaining check on unapproved external execution"
(`plugins/autosci/bin/autosci_bridge.py:10659`). Under CC the worker's existing check becomes the predicate's
evaluator, so planning, dispatch and the worker all run the same code.

## g. Feasibility: most of it exists, so CC starts small and by hand

**Each part has been built somewhere; nobody has combined them into one schema.**

| Part | Already built in openJiuwen or AI4Research | Already built in a paper |
|---|---|---|
| filter before a model | AI4Research's hard filter | Don't Offer What Can't Be Done; Contract2Tool |
| pinned hashes | AI4Research's freeze; jiuwenswarm's RSI package hashes | Execution lineage; RelAIBuild |
| a gate per node | AI4Research's evaluation plan | held-out tests: Beyond Task Completion |
| declared versus observed effects | AI4Research's sandbox write record; agent-core's `idempotent` and `stateless` tool flags | SkillProbe |
| a version tree | RSI's tree of attempts | the Darwin Gödel Machine's archive |
| gated self-improvement | agent-core RSI's candidate gate | When Self-Evolution Backfires; AllocBench |
| composition and removal | jiuwenswarm's SkillPack cascade; agent-core's reversible binder | Cordis; SkillFuzz |

**The schema itself is not hard to implement.** A Declaration is a file; its hash is SHA-256 over its files; each record
is a row in openJiuwen's stores. The first version needs no automation, and reuses what exists:

| To start | What already exists | What is new |
|---|---|---|
| seed capsules | 85 AI4Research manifests and 34 jiuwenswarm skills to choose from | about ten Declarations, written and verified by hand: a person writes each, runs its checks, and records the Verdict |
| holding and loading | agent-core's carriers and binder | a hash check before loading |
| offering at planning | AI4Research's hard filter and selection call | the filter reads declared preconditions; the model reads summaries and ports |
| indexing | Symphony, through `CapabilityProvider` and `SkillGraphUpdater` | an adapter that lists only admitted capsules, with their hash and declared I/O |
| records | openJiuwen's stores and rails | one rail that writes Bindings and invocations |

**The hard part is getting the tools to work with it,** not the schema: one predicate evaluator that the filter,
dispatch and each worker agree on; the admission gate and sandbox observation as automation; judge calibration; and
RSI and verification working to the records. These come later, each measured against today before the next.

| Milestone | What exists at the end |
|---|---|
| **M1** | one node running end to end under the schema, then three, then about ten hand-authored, hand-verified capsules by hash, offered through today's filter and indexed by today's Symphony, with run records and claim labels. It needs no other team (§12.1) |
| **M2** | declared preconditions in the filter and at dispatch through one evaluator, judge spot checks, both measured against today |
| **M3** | the admission gate and sandbox observation automated; certification with held-out suites and measured judges |
| **M4** | the build path with RSI, the librarian, the audit loop, composition screening |
| **M5** | generalists by default, and agents as composites |

**What to use first, and what waits.** The first job is the workflow running end to end, one node and then a few. The
schema is adopted in stages, each adding one record or one check to what already runs. The staging is **design**.

| Stage | What runs | The CC parts in use | What waits |
|---|---|---|---|
| **One node** | one capsule and a generalist | the Declaration, body hashes checked before loading, one predicate evaluator shared by the filter and dispatch, the Binding with its invocations, claim status | everything else |
| **Three nodes** | outputs feed inputs | typed ports, the dispatch re-check on fresh state, approval for irreversible effects, gap Findings | versions, judges, the tree |
| **About ten** | several sprints | Standing with one librarian, versions, judge standing from spot checks, drift probes | screening, caps |
| **RSI builds** | the library grows | the lineage tree, inherited suites, recurrence counted before a build | retirement by evidence |
| **About a hundred** | choosing gets hard | ranking inside the offer, caps per slot, overlap Findings, retirement | |

The selection evidence is evidence about *large* libraries: the pass-rate drop was measured at 202 skills, and a
look-alike description wins only when there are look-alikes. With three capsules the choice is trivial, and the value
is simpler: knowing what ran, what it was allowed to do, and what supports each claim.

## h. In sum: how each part serves the tools, and AI4Research

| Schema part | The tools it serves | What AI4Research gains |
|---|---|---|
| `ports`, `needs.when` | the planner's filter, dispatch | fewer binds that cannot run, and smaller prompts |
| body hashes, `decl_hash` | the freeze, the binder, audits | proof of what ran, and exact revocation |
| `changes.effects`, `effect_class` | the sandbox, the permission engine, the scheduler | undeclared effects caught, safe retries and parallelism |
| `guarantees.checks`, judge standing | the admission gate, the node gates, verification | checks with targets, and results labelled by how far to trust them |
| `summary`, typed ports | Symphony, the chooser | cheaper, better choices |
| `lineage`, suites, Findings | RSI, the librarian | children shown to be better, gaps that drive builds |
| Binding and invocations | the trajectory store, delivery | every claim traced to the run that produced it |
| `exempt` | generalists | steps nothing fits still complete, and leave material to improve on |

Together these make AI4Research pick better, fail earlier and more honestly, and improve without losing track of what
it has.

# 3. Foundation: what a capability declares, and how the capability itself is held

**One unified schema for every kind of capability,** with a required core and optional parts that are declared when
they apply. Everything CC does (pick, verify, improve, remove) reads these fields. Source of truth:
`merged/SCHEMA.md` §3.1.

## 3.1 The Declaration's fields

![Figure 7. What is in a capsule. Ten fields are enforced at M1; the rest are declared from day one and inert until the component that reads them exists.](figures/decl.png)

**One schema, whole from day one; what is staged is how much of it is enforced.** A field is declared
in the schema from the start and sits inert until the component that reads it exists, so nothing is
redesigned later and a system with parts missing still works demonstrably. The milestone column below
says when each part *starts being enforced*, not when it is invented.

**Enforced at M1, ten fields:** `identity.name`, `identity.kind`, `identity.carrier`,
`identity.body[].sha256`, `identity.summary`, `ports.inputs[]`, `ports.outputs[]`, `needs.when[]`,
`changes.effect_class`, `guarantees.checks[]`.

Everything else is optional until the milestone that needs it: `identity.lineage` at M4 (RSI),
`needs.model` and `budget` at M3 (routing), `guarantees.acceptance`, `evals` and the quality criterion
at M3, `changes.provides` and `invariants` at M2, `overlays`, `load_mode` and `exempt` at M3, and
`members[]` with `structure` at M4 (the merge engine).

**Every enforced field is a cost** -- work for whoever writes a capsule, and a check the gate must run.
That is the reason the core is ten fields rather than forty.

**A capsule holds a set of capabilities, and n = 1 is the degenerate case.** A single tool is a capsule
of one; a bundle is several loaded as one body under `PluginSpec`; a composite carries `members[]`, each
independently admitted, plus the internal `structure` that wires them. All three are placed by the same
rule, which is what "flexible in form" means.

The table lists every section of the Declaration, what is required and what is optional, and which of the four
verbs reads it. The rule of thumb: a field is required when a check, a filter or a revocation cannot work without
it, and optional when it only helps where it applies.

Written by the builder (a person, or RSI). It is immutable: any change is a new Declaration with a new hash.

| Section | Field | Required? | What it should be | Read by (verb) |
|---|---|---|---|---|
| identity | `name`, `version_label`, `schema_version` | required | a stable name; free-text version; the schema version it is read under | pick, improve |
| | `kind` | required | tool, mcp, skill, prompt, subagent, agent, composite | pick, verify |
| | `carrier` | required | the agent-core spec it loads through (below) | verify, remove |
| | `body[]` | required | every file, each with its SHA-256; a remote service is pinned by endpoint and version instead | verify |
| | `summary` | required | at most 400 characters; the only prose a model reads when choosing | pick |
| | `load_mode` | required | `invoked` (behind a boundary) or `context_injected` (shares the agent's context) | pick, remove |
| | `lineage` | required: `parent` (empty for a root), `relation`, `builder`; the rest optional, kept when the builder supplies it | parent, relation (supersedes, specialises, rollback_of, migrated_from), `build_trigger`, `context_capsules`, provenance (generating model, prompt, trajectory) | improve, remove |
| | `overlays[]` | optional | evolved experience, guidance or packages loaded with it, each hashed | verify |
| ports | `inputs[]`, `outputs[]` | required | each with a type from one versioned vocabulary; each output names the check that validates it | pick, verify |
| needs | `when[]` (preconditions) | required; empty only with a stated reason | predicates `{path, operator, value}`, each with `state_source`, `max_age_s`, what happens when the fact is unknown or its source is down, and a parity check | pick, verify |
| | `external[]` (the capability's own dependencies) | required; may be empty | each pinned (hash, model id and version, endpoint and version, or capsule hash), **or** unpinned with `purpose`, `role` and `contracts` (optional) | improve, remove |
| | `network` | required | none, an allowlist, or open | pick, verify |
| | `resources[]`, `injects[]`, `model` | optional | resources with a mode; services it needs; model constraints (never a model choice) | pick, remove |
| changes | `effect_class` | required | `pure`, `idempotent`, `compensable` or `irreversible`: the author's attestation for the whole capability, checked against its effects | pick, verify, remove |
| | `effects[]` | required; empty only if it changes nothing | per effect: resource (`ws:` inside the capsule layer's boundary, `ext:` outside it), operation (read, write, create, delete, emit, execute), scope, `idempotent`, reversibility (inverse, scoped, compensate, emission; only compensate or emission on `ext:`), risk with blast radius | verify, remove |
| | `provides[]`, `invariants[]` | optional | services it installs; invariants, each with a check | remove, verify |
| guarantees | `exempt` | optional; only `reason: generalist` | a do-anything capsule outside the library's verification policies; plan gates still apply, level `exempt` | pick, verify |
| | `checks[]`, `acceptance` | required (unless exempt); at least one postcondition | each check: kind (including negative controls), anchor (deterministic, reference, judged), runner hash, author, held out or not, where its signal comes from | verify |
| budget | `per_call`, `enforcement`, `on_exhaust` | required for agents; optional otherwise | limits between calls, and how each is enforced | verify |
| members | `members[]`, `wiring[]` | composites only | members keyed by role, each pinned by hash; one Declaration may fill several roles | remove |
| coverage | `undeclared_notes` | optional | what the builder knowingly leaves out | verify |

**Computed by the gate, never written by the builder:**

- `decl_hash`: over everything;
- `contract_hash`: over everything but the body, so a suite written first is bound to the contract;
- agent-core's runtime flags;
- a composite's derived needs and changes;
- `context_cost_tokens`.

**A Declaration describes a capability, never a use** (invariant 12). It names no step, plan, workflow, stage,
task type, capsule to run before or after it, or worker. It is told what to do through its inputs. A capability valid
only for some inputs says so with `needs.when` predicates over them, never with a task list. The uses live in the Plan
step, the Binding and the Binding's invocations (chapter "Plan and schedule").

**Why both a class and per-effect undo.** Each effect's `reversibility` and `idempotent` flag is what verification
checks, one effect at a time. The `effect_class` is the author's one-word summary of the whole capability, which the
planner, the scheduler and dispatch read to decide retries, fan-out and approval without re-deriving it. The gate
checks that the two agree, so the summary can never be kinder than the effects behind it.

**The author answers for what the capability does** (invariant 13). CC cannot see inside a remote database,
so the author declares up front what it touches, whether each change is idempotent, and how it is undone or that it
cannot be. CC answers for checking that declaration against what it observes. A mismatch is a typed reason and a
Standing move recorded against the builder. **There is no numeric trust score.**

## 3.2 Three trust levels, and trust per claim

![Figure 8. Admission and Standing for ordinary capsules. A candidate passes provisional tests, then may pass certified tests. Provisional capsules run only where their output is checked later. Generalists are enrolled at level exempt instead, because they have no job of their own to test, and are not shown.](figures/lifecycle.png)

A level says **how far a capsule's results can be trusted**, and it is earned by what was tested before admission.
The levels exist because passing a task is not proof of doing the job: 215 of 222 self-built tools failed held-out
tests of their own job while no in-session signal flagged them (Beyond Task Completion, 2604.00392 p1, p5). But a low
level does not stop a capsule from running. It decides what its results support: that is the rule that keeps CC
from being so strict that AI4Research cannot do its work (below).

| | Exempt (generalists only) | Provisional | Certified |
|---|---|---|---|
| tested before admission | enrolled, not admitted on a job: loads, stays within its declared effects, refuses a protected write, completes sample step contracts under their gates | loads, stays within its declared effects in a sandbox run, and passes one postcondition on inputs it was not built from | every output covered by a check written by someone who never saw the code; a judged check counts only if the judge's error is measured and low enough; predicate parity tested |
| may bind | a step nothing else fits, named by the run contract, where every output has a gate of any kind | any step that does not require certified capsules | any step |
| its claims are | never `supported` | `supported` only where every gating check is deterministic, reference-based or a calibrated judge; otherwise labelled | `supported` where its checks pass |

**Block only for safety, label for quality** (invariant 14). A check refuses a run only for identity or safety.
Everything about quality changes what a result is worth, recorded on each delivered claim with a reason, not whether it
may run:

| Refuses the run (identity and safety) | Labels the claims (quality) |
|---|---|
| the body's hash is not the pinned hash | the capsule is provisional, not certified |
| a write to a protected component | a gating judge is not yet calibrated |
| an observed effect outside the declaration | the capsule is a generalist (exempt) |
| an irreversible effect without its approval | an input the result rests on is unsupported or stale |
| a revoked capsule, or one suspect for security or harm | |
| a failed node gate (the workflow decides repair or fail, as today) | |

**Exempt** is for generalists only: do-anything capsules with no job of their own, so there is nothing to
admit them on. Several may exist, such as a Codex and a Claude generalist.

Each individual claim also carries an assurance, in the order enforced > tested > audited > declared. So a
certified capsule can still say honestly that one promise is only declared.

## 3.3 How the capability itself is held

**What a skill is, in agent-core.** A `SKILL.md` folder of instructions and scripts, described by a `SkillSpec`. The
harness's `SkillUseRail` offers skills through an allow-list (`enabled_skills`); the agent sees each description and
loads a skill when it chooses to. A skill has no typed interface and declares no effects. A capsule wraps it and
adds both.

The Declaration never contains the capability's code. It **names and hashes** it, and says which agent-core carrier
loads it.

| Kind | Carrier (agent-core) | What is hashed | How it is loaded |
|---|---|---|---|
| tool | `ToolCard` | the tool's source files | the binder, as a tool |
| MCP server | `McpServerSpec` | local: its files. Remote: pinned by endpoint and version | the binder, as a whole server |
| skill | `SkillSpec` (a `SKILL.md` folder) | every file in the folder | the binder, with the offer applied through `SkillUseRail`'s allow-list |
| A2A agent | the A2A client | pinned by endpoint and version; its card is metadata, never evidence | the A2A client |
| subagent, agent template | `AgentTemplateSpec` | the template files | the binder |
| prompt section | `PromptSectionSpec` | the text | the binder |
| bundle | `PluginSpec` (tools, MCP, skills; **no rails**, which would put a capsule in reach of the checks) | every file | the binder |
| composite | its members | each member's `decl_hash` | through each member's carrier |

**Why:**

- The Declaration holds a hash and a carrier, and loading goes through the capsule layer's immutable store, because
  agent-core's binder loads by name with no hash check. The hash proves that what ran is what was checked (Execution
  lineage; RelAIBuild).
- Real skills declare almost nothing today: of 34 jiuwenswarm skills, none declares inputs, outputs or effects. So an
  **importer** proposes what it can derive, a person confirms the effects, and the capsule enters as provisional.

# 4. Pick: capabilities are easier to pick because selection is strict

**Inputs and outputs are known, and deterministic finding on declared requirements cuts out most options. Only then
does semantic matching choose among the survivors.** Picking happens at the planning stage, and is checked again at
dispatch.

## 4.1 How a capability is retrieved and chosen (per plan step)

![Figure 9. Picking for one plan step: code removes what cannot apply, a model chooses among the rest, a second model reviews the fit, and the freeze pins the result. If nothing fits, one of the generalists the run contract names, or a gap record.](figures/funnel.png)

| Stage | Done by | What it uses | What it does |
|---|---|---|---|
| **1. Eligibility** | code, deterministic | the declared requirements below | removes every capsule that cannot apply. Each removed capsule becomes a one-line exclusion |
| **2. Ranking** | code, then similarity | structural fit (output types feed the step's inputs), then similarity (for example Symphony's retrieval, or embeddings) | orders the survivors. Similarity **only ranks**; it never admits or excludes |
| **3. Choice** | a model | only `summary` (at most 400 characters) and `ports` of each survivor | picks one, or none |
| **4. Fit review and dispatch check** | a second model; then code | the step's needs; the **same** predicates, re-evaluated on fresh state | confirms the fit; at dispatch, refuses or defers if a predicate no longer holds |

If nothing survives, the step binds one of the generalists the run contract names (when it allows them) or records a
gap.

## 4.2 The deterministic criteria in stage 1 (what "strict" means)

These are the only reasons code may remove a capsule before a model sees it. Each compares a field the author
declared with a fact about the step or the sprint, so every exclusion can be traced to a declaration and argued with.

| Criterion | Declared field | Compared with |
|---|---|---|
| input and output types | `ports` | the step's required inputs and outputs, in one vocabulary |
| preconditions that can be read at planning | `needs.when` | current facts: credentials, installed tools, reachable services, licences, budget left. A predicate counts as readable at planning only if no upstream step changes its state |
| effects | `changes.effects` | the effects the step allows, and the run's effect ceiling; no write to a protected component |
| trust level | the Verdict's level | whether the step requires certified capsules (off by default); generalists only if nothing else fits |
| network | `needs.network` | the sprint's network zone |
| restriction | the capsule's `name` | the step's `restrict_to[]`, when a registered workflow sets one (demand side only) |
| model constraints | `needs.model` | the models the sprint may use |
| standing | Standing | only admitted capsules (plus a small exploration quota of inactive ones on steps that do not require certified capsules) |
| composition | composition Findings | no capsule in a set confirmed as harmful with capsules already bound |

**Not used in stage 1:**

- **invariants**, which are checked on outputs and used to screen which capsules may share a context;
- **postconditions**, which are verified at admission and after the node.

## 4.3 Why it is done this way

![Figure 10. Predicate parity. One declared precondition is evaluated by the planning filter and the dispatch check through one evaluator, and tested against the capability's own exit logic.](figures/parity.png)

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| exclude by code before any model chooses | without such a gate, a model picked a skill that could not run in 7.8% of 1,000 risk-enriched conversations (Don't Offer What Can't Be Done, 2608.01050 p5) |
| exclude on the capability's **own** declared preconditions, evaluated identically at planning and dispatch (predicate parity) | a gate on the skill's own exit conditions is sound only when gate and skill agree, and both read fresh state (2608.01050 p2-3) |
| filter on declared contracts, never on keywords | a keyword top-5 filter cut success from 0.775 to 0.620; filtering on declared requirements and effects reached 0.980 with 2,528 tokens a task, against 26,172 for all tools (Contract2Tool, 2606.07904 Table V) |
| let similarity only rank | the chooser is the bottleneck: pass rate fell by 0.21 (95% CI 0.15 to 0.27) as the library grew to 202 skills, and 38.5% of runs invoked no skill (More Skills, Worse Agents?, 2605.24050). Alita-G's accuracy ranged from 68.0% to 84.0% across six similarity thresholds on 25 questions, peaking at 0.70 (2510.23601 Table 3, p9) |
| rank by structural fit first | typed edges between capabilities help, and precondition failures are the most locally repairable (GraSP, 2604.17870; SkillDAG, 2606.03056) |
| show the chooser only a short summary and the ports | failures in use were picking the wrong API and passing wrong parameters (SkillWeaver, 2504.07079 p8). SkillWeaver's selector also removed APIs whose preconditions did not hold (p6) |

## 4.4 Why selection is cheap

**Ranking, sorting and retrieval are not part of this design.** Symphony already ships them --
`retrieval/`, `discovery/`, `graph_engine.py`, `orchestration/` -- and they work. CC decides *what
Symphony may index*, through `CapabilityProvider`, a protocol with two methods; Symphony ranks within
what CC admits. Nothing inside Symphony changes, and no part of this document proposes to redo or fix
it. Ranking inside the offer matters only once the library is large, and by then it is already built.

- Each capsule removed in stage 1 is never shown to a model, and its full catalog row shrinks to one exclusion line.
- In the papers, the gate removed 59.1% of description tokens after relevance matching, and 90.5% with matching
  (2608.01050 p4-5). Contract2Tool's contract filter cut 26,172 tokens a task to 2,528.
- In AI4Research, today's binding prompt carries each eligible capsule's full row, again on repair.
- **The saving here is measured (M2) against today's filter,** alongside false blocks and task success. It is not
  assumed.

# 5. Verify: capabilities are easier to verify because everything is declared

**Every check has a target: the declaration. Held-out tests check the declared job. Observed effects are compared with
declared effects. The hash proves the thing checked is the thing that runs.** Verification happens at admission (the
gate), at the freeze (hash and level), at dispatch (the same predicates on fresh state), in the in-run gates (declared
checks on outputs), and later in the audit loop.

## 5.1 What the schema provides to verification

![Figure 11. Two ways to judge a capability. Observed: build, use, watch, and retire later if a judge notices. Declared: declare, test the declaration at admission, filter before a model chooses, and compare at dispatch.](figures/declared.png)

### Three layers, not one

![Figure 12. Three verification layers off one Declaration. Conformance and correctness are binary; quality is a rate over a window with a declared minimum number of observations. The judge sits outside the capsule and is never itself a capsule.](figures/quality.png)

Verification is usually treated as correctness alone. That is not enough: a capsule must be shown to
fit the criteria, to function, and to be of good quality **often enough**. "Often enough" is a
distributional claim, and no per-run check produces one.

| Layer | The question | Shape of the answer | Fed by |
|---|---|---|---|
| **Conformance** | Is it what it says it is? | binary, static and on the first run | `identity.body[].sha256`, declared ports, and observed effects compared with declared |
| **Correctness** | Does it do its job on cases it has not seen? | binary, per case | `guarantees.checks[]`, held-out suites, and each output's named check |
| **Quality** | Is it good **often enough**, over time? | **a rate over a window, never a verdict** | `guarantees.acceptance` and `evals[]`, a named judge with its own Standing, and Standing carrying the running rate |

What quality needs that the schema must make explicit:

- **A declared quality criterion per output**, separate from its correctness check, so that "good" has a
  stated meaning rather than one inferred after the fact.
- **A declared minimum number of observations** before a quality claim means anything. With expensive
  sprints there will be tens of runs, not millions, and a rate over three runs is noise. Until the
  minimum is met the claim is labelled **unmeasured**, and unmeasured is never silently treated as
  passing.
- **A named judge whose own calibration is recorded**, because non-deterministic outputs can only be
  judged. Judges are calibrated by spot checks, and a judge is never itself a capsule. Grading the
  grader by planting known answers is well supported: PIT seeds faults into code and measures which ones
  the *test suite* catches, and CloudWatch Synthetics runs scripted known-input canaries on a schedule so
  the signal stays alive even with no real traffic.
- **A judge that fails its own calibration is removed from gating, not labelled.** This is the one place
  the labelling rule does not apply, and industry is unambiguous: in crowdsourcing, a worker who falls
  below the accuracy threshold on hidden test questions is removed from the job and their judgments are
  discarded. Keeping a failing checker in service behind a warning has no precedent. Label the
  **capsule**; remove the **judge**.
- **Standing carries the distribution**, not a pass or fail: what moves is a quality rate over a window.

**Block a regression. Label a capsule with no better replacement.**

This rule needs stating carefully, because in its loose form it is the **minority position**. Mature
release engineering blocks and rolls back on ordinary quality signals, not only on safety: Google's SRE
error budget policy halts all changes other than P0 and security fixes once the budget is spent; SRE
canarying pauses and rolls back on a bad canary; AWS pipelines roll back automatically when the
high-severity alarm fires during bake time; Spinnaker's Kayenta fails a canary that scores below its
marginal threshold.

What every one of those systems blocks, though, is a **new change**, and the last known-good version
keeps serving. None of them removes a capability outright and leaves the caller with nothing. That is
the distinction the schema needs:

- **A regression against a known-good version is blocked.** A new version that measures worse than the
  one it would replace does not take its place. This matches industry exactly.
- **A capsule with no better replacement is labelled, not blocked.** It still runs, visibly marked with
  what is known and unknown about it. Blocking the only version of a capability has no support in any of
  those sources, and it is the case this schema is actually about: research steps whose outputs can only
  be judged, where refusing to run means the work does not happen at all.
- **Safety still blocks unconditionally**, with or without a replacement: a hash mismatch, a protected
  write, an effect outside the declaration, an irreversible effect without approval, a revoked capsule.

That is why the refusal list is short and the labelling vocabulary is long.

**There is direct support for the third case.** Envoy's load balancer has a **panic threshold**, 50% by
default: when too few hosts in a cluster are healthy it *disregards health status entirely* and balances
across all of them, because excluding too much is worse than using degraded parts. Its outlier detection
carries the same guard in `max_ejection_percent`, where a host is not ejected if that would push the
cluster past the cap. A strict quality gate here would produce exactly that failure -- a library that
blocks its way down to nothing -- and the industry's answer is to stop excluding.

**Deprecate and revoke are different actions, and Kubernetes separates them the same way.** A failed
*readiness* probe takes a pod out of the Service endpoints while the container keeps running; a failed
*liveness* probe restarts it. "Stop routing to it" and "kill it" are two decisions with two triggers. A
capsule that is merely poor stops being offered. Only safety revokes.

This is also why a merged block cannot inherit a quality record from its members: quality is
distributional, so a block's quality is not the product of its members' and must be earned.

| Question verification asks | What in the schema answers it |
|---|---|
| Is this the exact thing that was checked? | `decl_hash` (over the Declaration and every body file); `contract_hash` (over the contract, so a suite written first stays bound to it); the Binding's pinned hashes; the live hash compared at dispatch |
| What must it do? | `ports` (typed outputs, each with its check); `guarantees.checks` (postconditions, invariants, negative controls); `acceptance` |
| What must hold for it to work? | `needs.when` (preconditions), tested against the capability's own exit logic at the boundary and with missing and stale state (predicate parity) |
| What may it touch? | `changes.effects`, with scope. The sandbox run observes what it actually touched, and a mismatch is rejected |
| Is it stateful, and can its changes be undone? | `effect_class`, each effect's `idempotent` and `reversibility`. The gate checks the class against the effects, runs a claimed idempotent capability twice and compares the state, and runs each declared compensation and compares the state with the state before |
| Has a remote body changed? | the Verdict's `remote_fingerprint` of its advertised interface, compared at every dispatch; a change refuses the run |
| Who wrote the test, and could the builder see it? | `checks[].author`, `held_out`, `written_before_body`, how much of the suite the builder saw |
| How good is the judge? | the Verdict's `verifiers[].measured_error`: false pass and false fail, the corpus, the date |
| What was the result, and why? | the Verdict: ADMIT, REJECT, DEFER or ESCALATE, with typed reasons, the level, each check with its runner hash, and parity results |

## 5.2 Why it is done this way

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| test the capability's **declared job** with held-out suites from someone other than the builder | 215 of 222 self-built tools failed every held-out test of their own job, and no in-session signal flagged them (Beyond Task Completion, 2604.00392 p1, p5) |
| **compare observed effects with declared effects**, and reject undeclared ones | skills' documentation and code diverge, including "shadow functions" the code has and the declaration hides. Of the top 2,500 ClawHub skills, 30.4% were flagged conditional, and only 9.9% were clean (SkillProbe, 2603.21019 p8, p12). About 13% of 10,240 MCP servers had undocumented high-risk operations (cited there, p5). SkillProbe must first extract the declaration from prose; CC's is structured |
| keep a check, **and its signal**, out of the capability's reach | a Darwin Gödel Machine node removed the logging its hidden checker read, and scored without solving the task (2505.22954 p70). SkillWeaver's "no exception means verified" let APIs pass by silencing errors (2504.07079 App. D.2.1) |
| separate the verifier from the builder; give the builder at most pass or fail, capped | CoEvoSkills' verifier never sees the skill source; replacing its diagnostic feedback with the oracle's bare pass or fail dropped 71.1% to 41.1% (2604.01687 Table A1). So practice feedback comes from a separate verifier, and only the sealed gate is pass or fail. The ablation does not test separation itself |
| typed verdicts; unknown is not no; no single score | a compensatory score can buy out a failed hard requirement (Prop. 1, p6); missing evidence differs from evidence of failure (Cognitive Admission Control, 2609.16313) |
| **measure every judge** before its verdict counts | a lenient judge silently stopped retirement (The Blind Curator, 2607.07436 Table 1). SkillProbe's verdicts moved from 5% to 45% conditional depending on the model (2603.21019 Table 2) |
| test predicate parity before a predicate filters anything | a gate is sound only while it agrees with the capability's own exit logic (Don't Offer What Can't Be Done, 2608.01050 p2-3, p5) |
| make the author declare state and undo, and check it | what runs behind an interface is the author's; about 13% of 10,240 MCP servers had undocumented high-risk operations (cited by SkillProbe, 2603.21019 p5). Declaring first finds a stateful or irreversible capability before a sprint relies on it (**design**, Muk 2026-09-22) |
| typed mismatches and Standing moves, never a numeric trust score | a compensatory score can buy out a broken declaration (Cognitive Admission Control, 2609.16313 Prop. 1, p6) |
| hash every body file, and load by hash | a hash proves identity; agent-core's binder loads by name. RelAIBuild hashes the canonical definition and aborts on mismatch (2606.26924) |

## 5.3 The gate every node must pass

The node gate is compiled in code at the freeze and hashed into the Binding. It has three parts, each written by a
different party:

| Part | Written by | Today in AI4Research |
|---|---|---|
| **step acceptance**: what this request needs | the requirement compiler, from the user's request (Plan step `requires.acceptance[]`) | each requirement names one of 43 registry checks, 23 deterministic and 20 semantic (`evaluation_plan.py:277-312`) |
| **capsule checks**: what the capability promised | the Declaration's author for the promise; the check's `author` for the runner, never the builder of a certified capsule | the manifest's `self_check`, `pass_conditions` and `postconditions` as text; text not in the registry becomes a model-judged item (`evaluation_plan.py:322-340`) |
| **artifact-type checks** | the vocabulary's owner | registry checks marked `auto_apply` (`evaluation_plan.py:314-319`) |

- **An admitted capsule very likely passes its own part:** it passed the same runners at admission, on inputs it was
  not built from. It may still fail the step's part, which tests what this request needs and which it never declared.
  So the gate is not redundant: admission checks the capability on samples, the gate checks this run.
- **Each gate verdict names its part**, so a failure is charged correctly: a failed capsule check counts against the
  capsule; a failed step check while the capsule's own checks pass is a fit failure, recorded as a near miss.
- **No runner, no gate.** A promise with no runner is `declared` and cannot gate. Every judge with a runner gates,
  whatever its standing (next section). Today a node with no criteria gets a default model judge of its objective
  (`evaluation_plan.py:352-356`); that stays, and its passes are labelled until the judge is calibrated.

## 5.4 Judges: calibrate early, label always

**The problem.** Most AI4Research outputs are semantic (syntheses, analyses, hypotheses, drafts), so they can only be
judged: 20 of the 43 checks in today's registry are semantic. A judge nobody has measured can be lenient without
anyone noticing: under a biased judge, retirement silently stopped while other activity looked normal (The Blind
Curator, 2607.07436 Table 1). And a verdict depends on the model: one audit marked 45% of skills conditional with one
model and 5% with another (SkillProbe, 2603.21019 Table 2). A strict rule, "no unmeasured judge may gate", would have
left most research steps with nothing that could run.

**The resolution: a judge always gates, and its standing decides what a pass is worth.** Standing is kept per judge,
per model and per artifact type:

| Standing | How it is reached | What a pass supports |
|---|---|---|
| **unmeasured** | the default | the step passes and runs on; claims resting on it are labelled `unsupported`, reason `judge_unmeasured` |
| **calibrated** | at least 30 items of that artifact type, about half with injected defects, with the upper bound on its false-pass rate recorded (**design**) | claims `supported` at assurance `audited`, when that bound is within the step's `judge_tolerance` (0.2 by default, **design**) |
| **measured** | at least 200 items, with the bound under the certification ceiling (0.05 by default) | counts toward certification |

- **Judges calibrate through normal use.** A small share of judged passes (5% by default, **design**) is re-checked by
  a person or a reference check, and each re-check becomes a calibration item. A judge reaches `calibrated` in ordinary
  sprints, so nothing waits for the full suites of M3. Defect injection is the method shown to work (2607.07436 p4-5).
- **A spot check that disagrees** writes a `verifier_audit` Finding. If the judge's bound rises past its standing, it
  drops a standing, and the claims it passed since its last check are re-labelled `judge_demoted`.
- **Retirement still needs a measured judge,** because that is where a lenient judge does silent harm.
- **Why a label and not a block.** Refusing on missing evidence costs real work: a controller that could not fetch missing
  evidence completed 90 of 120 effects, against 120 when it deferred and fetched it (Cognitive Admission Control, 2609.16313 p10). A labelled claim
  keeps the work and tells the reader exactly how far to trust it.

## 5.5 Trust levels and per-claim assurance (see Foundation)

- **Exempt** (generalists only) runs where nothing else fits and every output is gated; it never supports a claim.
- **Provisional** runs on any step that does not require certified capsules; its claims say how far they are supported.
- **Certified** runs anywhere.
- Each claim is at most as trusted as the weakest check behind it: enforced > tested > audited > declared.

## 5.6 Protected components

No capsule may write the gate, the suites, the records admission reads, or the Declaration, Verdict and Standing
stores. Declaring such a write is rejected, and so is doing one. Protection comes from write access, not secrecy: the
DGM node gamed a checker that was hidden from it.

# 6. Improve: capabilities are easier to improve because performance, trust and lineage are logged

**Performance and trust are logged. Parents and children are known through lineage and dependency hashes. Gaps and
their trajectories feed builds. New versions must pass everything their predecessor passed.** This is the schema's
support for self-improvement, the 2026-09-15 report's goal.

## 6.1 The questions, answered from the schema

Self-improvement needs answers to a few plain questions: what did this capability do before, how far is it
trusted, where did it come from, and what would help a builder make a better one. Each answer below sits in a record
the capability's builder cannot write, which is what makes it usable as evidence.

| Question | What carries it |
|---|---|
| **How does the schema support self-improvement?** | the library is **versioned** (every change a new hash), **append-only** and **monotone** (a new version passes all its predecessor passed); gap Findings tell builders what is missing; three clocks keep builds off the sprint's path; protected components mean nothing a builder makes can grade itself. Details below |
| **How does it support verification?** | every check has a declared target, the hash proves identity, and declared effects are compared with observed ones (§5) |
| **Who carries past performance?** | **Binding invocations**: every run of every hash (each fan-out item, attempt and fallback), with outcome, cost, exits and gate verdicts. **`use_outcome` and audit Findings**: what was learned after use. **The Verdict's `contribution`**: gain against the pool at admission. The librarian reads all three for activation, caps and retirement. None is written by the capability or its builder, so none can be edited in the capability's favour |
| **What carries trust?** | per capsule, the **level** (exempt, provisional, certified); per claim, the **assurance** (enforced > tested > audited > declared); each delivered claim's **status** (supported, unsupported, stale). An exempt generalist's claims are never supported. An unpinned dependency caps its claims at audited |
| **How does the librarian know what each capsule is derived from?** | **Standing**: one pointer per name, with its history. **`lineage`**: the parent; the relation (supersedes, specialises, rollback_of, migrated_from); `build_trigger` (the gap that caused the build); `context_capsules` (what the builder had in context); provenance (generating model, prompt, trajectory). **Hashes**: `decl_hash`, `contract_hash`, and each dependency's pinned hash. Children are found by querying lineage. The whole tree, rejected nodes included, is exposed to RSI (below) |
| **What helps RSI?** | **gap Findings**: the gap's identity, recurrence counted over sprints, the generalists' trajectories and cost, near-miss capsules. **The parent's suites**, inherited by the child: the visible ones readable, the sealed ones as pass or fail. **Typed rejection reasons.** **Drift Findings** naming the broken assumption and the dependency's written purpose. **Lineage.** RSI's own gate result, kept as builder evidence. A hard build budget |
| **Can RSI prove a child is better than its parent?** | yes, on the parent's own tests. The Verdict lists every suite a hash was checked with, and a child inherits them. RSI reads the visible suites and adds its own cases; it sees sealed suites only as pass or fail. The child is better when it passes every inherited suite, its new cases, and a fresh held-out addition written by verification, with a contribution at least the parent's. RSI's own cases can reject a child, never certify it |
| **How is the library kept small and useful?** | caps per slot; an evidence floor before retirement; retirement by evidence kept apart from eviction by cap; overlap flagged and settled by a duplicate test, never by similarity |

## 6.2 Start extra small, grow by recurrence

**The library starts with about ten capsules** (**design**): the ones behind the most frequent plan-step types in
recent AI4Research sprints, at most one per slot, imported from today's manifests, with caps of one to three per
slot. Everything else runs on generalists, which may now take judged steps too, with their claims labelled, and each
such step leaves a gap Finding. The library grows only when a gap recurs, and the **first option for a recurring gap
is to import** an existing capability (another AI4Research manifest, a jiuwenswarm or skillhub skill, an MCP server)
before building one.

Why small: a bigger library made agents worse (pass rate fell by 0.21, 95% CI 0.15 to 0.27, as a library grew to 202 skills, and
38.5% of runs invoked no skill at all; More Skills, Worse Agents?, 2605.24050). A cap mainly controlled variance
(Library Drift, 2605.19576 p3-6). And building on first sight is a known failure: builds wait for recurrence
(AllocBench, 2607.23332).

## 6.3 The capability tree: CC stores and exposes, RSI chooses

The library is a **tree of capabilities**. Every Declaration ever submitted is a node, rejected and retired ones
included, since the store is append-only. Edges are `lineage.parent` with its relation, plus optional `co_parents`.
Standing points each name at one node; the tree keeps them all. RSI branches from any node, and its own selection
policy decides which.

| | What | Guaranteed? |
|---|---|---|
| **CC stores, from its own records** | per node: hash, name, parent, relation, builder; the Verdict with each suite's result, inherited suites included; Standing and its history; every invocation's outcome, gate verdicts by source and cost; Findings; its children | yes |
| **CC stores if the builder supplies it** | `co_parents`, `build_trigger`, `context_capsules`, `diagnosis_inputs`, provenance, `builder_ref` (for example RSI's tree node id), build cost | optional: kept and exposed, never inferred |
| **RSI owns** | which node to branch from, what to change, how many children, when to stop, its own scores and tree state, its own gate | not CC's |

- **The tree index** is the librarian's read model: one row per node (parent, depth, children count, Standing,
  level, suites passed, invocations, gate results by source, cost, open Findings), updated incrementally because every
  record is append-only and keyed by hash. Queries: ancestors, descendants, siblings, the frontier, a name's subtree.
- **CC enforces only this on a child:** its parent exists; it inherits the parent's suites; it is rejected if a
  parent was revoked for security, harm or provenance (`PARENT_REVOKED`), unless a named person waives it.
- **CC never ranks nodes for RSI** and never reads RSI's scores. There is no score in the index.

## 6.4 How self-improvement runs

![Figure 13. Self-improvement on three clocks around one library. Sprints never wait for builds; only the cold path writes; the audit loop can only lower Standing.](figures/F8.png)

- **Three clocks around one library:**
  - hot: sprints read only what their freeze pinned, and never wait;
  - cold: builds and admits, and is the only writer;
  - audit: replays suites on a schedule, and can only lower Standing.
- **The generalists** complete a step nothing fits. Each is an **exempt** capsule (`guarantees.exempt {reason:
  generalist}`): outside the library's verification policies, since it has no job of its own, but bound by every plan
  gate. Several may exist, for example a Codex and a Claude generalist; the run contract names which a sprint may use.
  None writes the library; each leaves a gap Finding with its trajectory, gate verdicts and cost, so RSI has material
  to improve on and a failure can be explained.
- **The cold path** has four roles in separate sessions:
  - a build decision, which never sees drafts;
  - a suite author, which sees only the Declaration;
  - an implementation, which reads the parent's visible suites but never the sealed ones, and gets capped
    admit-or-reject feedback;
  - a code gate.
- **Five ways to update**, tried in this order:
  - import an existing capability that already does the job;
  - a new version, which must be **monotone**;
  - a specialisation;
  - a new capsule;
  - no build.

## 6.5 Why it is done this way

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| keep every node, and expose results and children per node, for RSI's own parent selection | the Darwin Gödel Machine keeps an archive of every agent, never pruned, and picks parents by performance and inversely to the number of children (2505.22954 p4); keeping only the latest agent did worse (p8). RSI already keeps its own tree with `parent_id`, `adopted` and `score` (agent-core `rsi/schema.py:96-111`) |
| a child inherits its parent's suites, with a fresh held-out addition each generation | in one case, hacking appeared when checked functions were visible (Darwin Gödel Machine, 2505.22954 p70; a 3-task side experiment); monotone edits keep prior hits (SkillDAG, 2606.03056) |
| exempt generalists, gated by the plan | a step nothing fits otherwise fails and leaves nothing to learn from; recurrence of gaps, not first sight, should trigger a build (AllocBench, 2607.23332) |
| keep a library at all, and let agents extend it | self-built tools lifted Alita-G's GAIA pass@1 from 75.15% to 83.03% on its build set (2510.23601 p7). SkillWeaver's APIs raised WebArena success from 22.6% to 29.8% (2504.07079 Table 1) |
| gate before commit, including the capsule's value to the pool | an ungated pool fell from 62% to 50% as it grew. A pre-commit gate reached 72%, and removing its marginal-gain step cost 8 points. Cleanup afterwards recovered little (When Self-Evolution Backfires, 2608.05810 Table 1-2, p7) |
| record `context_capsules` | cleaning up descendants "requires provenance a real system lacks" (2608.05810 p2, p7) |
| build only on recurrence, and keep the decision apart from the build | once code was involved, models committed to building at first sight 85-99% of the time (AllocBench, 2607.23332 Table 1). Waiting for the second occurrence scored 43.0 against 34.6 (App. A.1) |
| keep performance in records the builder cannot write | SkillWeaver kept usage logs inside each API's docstring, which the synthesiser itself edits (2504.07079 p4-5) |
| measure the judge before retiring on its verdicts; separate retirement from eviction | biased judging stopped retirement by contribution (0 to 0.3, against 1.3 clean), while cap evictions kept the count looking alive (The Blind Curator, 2607.07436 Table 1). Harsh retirement fell below the no-skill floor (Library Drift, 2605.19576) |
| require monotone new versions (**design**) | SkillDAG requires online edits to keep prior hits (2606.03056); DGM keeps every variant that still compiles and can edit, never pruning on score, so a monotone rule is CC's own choice (2505.22954 p5) |
| let an author unpin a dependency only with a written purpose and contracts | given the failed contract, one-round repair rose from 10% to 78% (Skill Drift Is Contract Violation, 2605.10990 p8-9; not significant against plain drift text, 60%). jiuwenswarm's Swarm Skills already write a purpose per dependency (up to 150 characters); CC ties it to unpinning and to repair (**design**) |

# 7. Remove: capabilities are easier to remove because of spatiotemporal composability

**Stated plainly first, because it is the part most likely to be challenged.** Composability lets a
capability be installed and uninstalled while the system runs, and lets dependents be notified when one
goes away. It is **not foolproof, and it is not full reversibility.** Registrations come back out;
emissions already sent do not, external state is not rolled back, and a context poisoned by a bad tool
stays poisoned. This is the last milestone, not the first.

The mechanism itself already exists in agent-core: `apply_extension_hot` and `unapply_extension_hot`
bind and unbind tools, MCP servers, rails, prompt sections, skills and subagents, undoing them in
reverse order, and rolling back a partial failure. `_unbind` raises `Unsupported hot unbind` for kinds
it does not handle, so unloading is not universal even at the mechanism level. What this schema adds is
not the unloading. It is the **declaration of whether unloading is safe**.

**No runtime that was checked promises that unloading actually happens.** This is not a limitation of
one implementation; it is what every serious platform says about itself:

| Platform | What it says |
|---|---|
| **POSIX `dlclose`** | unloading is reference-counted, `RTLD_NODELETE` disables it entirely, and "a successful return from `dlclose()` does not guarantee that the symbols associated with handle are removed from the caller's address space" |
| **musl libc** | "`dlclose` is a no-op." Libraries stay loaded for the life of the process, because leftover references can crash after unload and unloading leaks thread-local storage. Both behaviours conform to POSIX |
| **Java (JLS §12.7)** | a class may be unloaded "if and only if its defining class loader may be reclaimed by the garbage collector". Unloading is an optimisation, and programs must not depend on it |
| **.NET collectible `AssemblyLoadContext`** | unload is **cooperative**: `Unload()` "just initiates the unloading", and it completes only when no thread holds the plugin's methods on its stack and no outside reference pins it. Completion has to be checked, not assumed |
| **OSGi** | after an uninstall, wirings still in use are "pending removal" and keep their class loader until dependents are refreshed. One leftover reference pins the whole bundle |
| **Erlang/OTP** | the best-known hot-swap system in existence keeps exactly two versions, current and old. Loading a third purges the old one "and any processes lingering in it are terminated" -- it unloads by **killing** what is still running |
| **Linux kernel** | a forced module unload sets taint flag `R`. The kernel does not treat it as trustworthy |
| **Kubernetes** | retirement is drain then force: remove from endpoints, run `preStop`, `SIGTERM`, a grace period, then `SIGKILL` |

**So the word "uninstall" must mean "no longer routed, and drained".** It must never mean "its code and
memory are gone". That is the honest promise, it is the one every platform above actually makes, and it
is why this milestone is last: the schema's contribution is not the unloading but the **declaration of
whether unloading is safe**, plus the draining discipline around it.

The design follows Kubernetes' shape: **stop offering it, wait for in-flight work to finish, and reclaim
on restart.** Nothing claims the old capability has ceased to exist inside a running process.

**Each capsule declares what it needs and provides (space), and how each of its effects is undone (time). So it can be
added, replaced, reverted or removed without breaking the capsules that depend on it. A revocation reaches exactly the
work it affected, and composition risk is screened.**

## 7.1 What the schema provides

![Figure 14. Spatiotemporal composability. Space: declared needs and pinned dependencies, so a dependent reacts when a dependency is revoked. Time: revisions, a sprint that keeps what it pinned, and the boundary that decides how an effect is undone.](figures/compose.png)

| Operation | What the schema declares or records | Rule |
|---|---|---|
| **add** | `injects` (services it needs), `provides` (services it installs), each with an interface version | admitted only if every needed service has an admitted provider, and there are no cycles |
| **replace** | a new version: new hash, new Verdict | monotone, and compatible: outputs still cover every port a dependent consumes, and `provides` still covers every key a dependent injects. No new write, delete or emission without re-screening |
| **revert** | Standing history (`previous[]`) | back to an earlier hash that still has a valid Verdict |
| **remove** | Standing moves: deprecated, then retired | stop offering it first; retire only when no admitted capsule relies on a service only it provides; agent-core unloads its registrations in reverse order |
| **undo effects** | `effects[].reversibility`: inverse, scoped (a child context thrown away), compensate, or emission (crosses the system boundary) | an emission is never "undone"; it is withheld until the freeze allows it, or compensated |
| **revoke** | the reason sets the policy | superseded: running steps finish. Conformance failed: running steps finish, and downstream claims go stale. Effect violation: running steps abort, and the capsule is quarantined. Revoked provenance: running steps abort, and every capsule built with it in context becomes suspect |
| **trace the damage** | each invocation's step identity (hash of the capsule, its inputs and its predecessors), and its claims | a change invalidates exactly the downstream steps and claims |
| **composites** | members pinned by hash | a composite is offered only while every member is still admitted |
| **screen combinations** | effects (the modifies set), invariants, the Binding's `context` capsules, `load_mode`, `injects`/`provides` | sets are screened, never certified; a confirmed harmful set is never co-loaded |

**Change happens between sprints, not within one.** A sprint keeps the hashes it pinned.

## 7.2 What composability does not undo, and what the schema does instead

Removing a capsule undoes its registrations, not what it did. Two things stay:

- **External state.** A capability over a live database changes it. Effects on `ext:` resources can only be
  `compensate` or `emission`, and the author must say which, per effect, with `idempotent` and the capability's
  `effect_class`.
- **The context.** A capsule loaded into an agent's context shaped every later decision there. So a context capsule
  counts like the primary for revocation: every invocation it shared a context with is traced and its claims go stale,
  and a context that held a revoked hash is never reused.

**What composition may do depends on the declared class:**

| | pure | idempotent | compensable | irreversible |
|---|---|---|---|---|
| automatic retry | yes | yes | after the compensation ran and was checked | no, a named person decides |
| fan-out in parallel | if parallel safe | if parallel safe | if parallel safe, each item's undo recorded | one item at a time |
| exploration, speculative runs | yes | yes | no | no |
| inputs it may act on | any | any | any | supported claims only |
| approval | none | none | none | the step and the run's effect ceiling must allow it; high severity needs a named person, and an unattended run blocks |

Undeclared behaviour counts as irreversible until an audit says otherwise.

## 7.3 Why it is done this way

![Figure 15. Removing a provider without breaking its dependents: stop offering it, check that no admitted capsule relies on it, then unload in reverse order.](figures/F5.png)

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| declare needs and provided services, and each effect's undo | Cordis defines spatiotemporal composability: components added, replaced, reverted and removed without breaking dependents, with the runtime guaranteeing providers outlive consumers (2608.25512 Thm 70, p47), and add, remove and undo reaching the same state as a fresh load (Thm 80) |
| treat emissions as a policy, not a promise | "a message already sent stays sent": Cordis cannot revert what crosses its boundary (2608.25512 p47, p70-71) |
| remove in two steps | Cordis unloads a provider only when nothing relies on it (2608.25512 p36, Alg. 5) |
| version interfaces and pin dependencies | Cordis leaves structural typing of keys and versioning open (2608.25512 p75) |
| compute step identities, so a change invalidates exactly its downstream | with DAG replay, untouched work stayed identical (3 of 3 runs), while loop agents regenerated and contaminated it (Execution lineage, 2605.06365 Table 1; n = 3) |
| screen sets, not only single capsules | severe drift was rare with one skill loaded and rose fourteen-fold to 66.5% with five (p9); 80.6% of high-risk flags were confirmed in execution (SkillFuzz, 2607.02345 Fig. 6, Table II). SkillProbe found the high-risk skills form one connected risk network (2603.21019 p12-13) |
| undo is keyed to a declared class, and external changes are never called reversible | Cordis's guarantees hold only inside its boundary, up to an observational equivalence, and an inverse's correctness is the author's obligation, unchecked by its runtime (2608.25512 p58-59, p70-71) |
| a context capsule counts like the primary when revoked | severe drift rose with the number of skills loaded together (SkillFuzz, 2607.02345 Fig. 6): what shares a context shapes the run |
| gate composites on their members, by hash | jiuwenswarm's SkillPacks already disable a pack when a member is disabled, but reference members by name, so a *changed* member goes unnoticed |

# 8. Merge: capabilities are easier to place in bigger blocks because recurrence is evidence

A capsule holds a **set** of capabilities. A single capability is a capsule of one, so nothing in this
chapter is a special case: it is what the schema does once a library has run long enough to have
evidence. The result is that placements can be made at a larger grain, where a larger grain is better.

**There is no split operation.** Splitting an existing capability is complicated and unnecessary: if
every capsule can exist as a set of one, every combination can be built up, and no further atomisation
is needed.

This is a **design choice, and it goes against the grain.** Compilers routinely split and dissolve:
LLVM's `HotColdSplitting` cuts cold regions out into new functions, its partial inliner inlines only part
of one, and Oracle's view merging removes a view's boundary entirely by inlining its body whenever that
is cheaper. Hierarchy is normally flattened for optimisation. The choice here is to buy simplicity --
one direction of travel, no decomposition machinery, no question of what a split block's lineage means --
at the cost of never recovering a finer grain than the one the parts were authored at. Present it as a
choice, not as what everyone does.

## 8.1 What the schema provides

![Figure 16. What a library holds, and what a capsule can be: a single carrier, a bundle, a composite with its own DAG, or a generalist. Judges, gates, the librarian, the planner, ranking and tasks are never in it.](figures/library.png)

- `members[]` — each member pinned by `decl_hash`, so a block's internals cannot move under it.
- `structure` — the block's internal DAG: nodes, edges with a relation, direction, and loop guards.
- `identity.lineage` — `relation: merge`, with `parent` and `co_parents` naming the capsules the block
  was built from, so a block is never an orphan and RSI can branch from the block or from a member.
- `guarantees.checks[]` on the block itself, evaluated as the union of its members' suites plus its own.
- The block's ports, `needs` and `changes` derived from its members: ports from the boundary of the
  internal DAG, `changes` covering the union of members', `needs` the union minus what members satisfy
  internally.

## 8.2 How a merge happens

![Figure 17. Overlap and merge. Everything starts at n = 1; each edge accumulates evidence; a recurring, high-quality structure becomes a candidate block with a derived Declaration and pinned members; A, B and A-B all remain and the chooser picks per node.](figures/merge.png)

1. **Everything starts at n = 1.** Individually declared, individually admitted, individually placed.
2. **Observe each edge.** Evidence accumulates per ordered pair: how often A→B occurs, and how often it
   succeeds.
3. **Qualify.** An edge becomes a candidate only on **both** enough support and a high enough success
   rate. A recurring *structure*, not only a pair, qualifies the same way.
4. **Propose, gate, place.** The candidate gets a derived Declaration, its members pinned, and A and B
   recorded as `co_parents`. It is tested **as a block**. A person approves it. The librarian then
   decides whether to place it.
5. **A, B and A-B all remain.** Nothing is retired **by the act of merging**, and the chooser picks per
   node. (A merged block is an ordinary library member afterwards, and the librarian may retire it later
   on evidence like anything else. Industry is less patient still: Redshift drops an automated
   materialized view that is unused or no longer beneficial, and Azure SQL drops an index that did not
   help.)

## 8.3 The asymmetry, and why it is the load-bearing part

> Two capsules that each **fail** their declarations are assumed to fail together too, in either order,
> so failing parts are never merged.
>
> Two capsules that each **pass** are **not** assumed to pass together. The block earns its own quality
> record, or it has none.

This is conservative in both directions, and the second half follows from quality being distributional
(see the Verify chapter): a block's quality is not the product of its members' qualities and cannot be
inferred from them. A merged capsule is measured as a capsule, exactly as an n = 1 capsule is.

**The first half is an assumption, and is labelled as one.** It would be proved wrong by a pair that
succeeds together while each member fails alone.

## 8.4 Recurrence when sprints are expensive

Sprints are costly and infrequent, so thresholds tuned for high-frequency systems do not transfer.
Google's materialized-view recommender reads thirty days of query history; task mining reads thousands
of events. This system will have tens of observations. Three consequences:

- **Count recurrence in sprints, not nodes**, with a threshold of 2. Small fixed counts are what
  industry uses: HotSpot promotes a method on a fixed invocation count scaled by compiler load, LuaJIT
  calls a loop hot at 56 iterations, and Akamai caches an object only on its **second** request within a
  window -- in Akamai's data, 74% of some 400 million cached objects were used exactly once, which is the
  cost of acting on a single sighting.
- **A merge is proposed to a person, never applied automatically.** Google's rewrite is automatic
  because its evidence is enormous; Microsoft's process mining marks an opportunity for a person to act
  on, because the evidence is thin and expensive. This design is in the second regime, and says so.
- **Seed the first candidates from known workflow structure.** Some chains run every sprint by
  construction, so the mechanism can be demonstrated before much evidence exists.
- **Gate on benefit, not on frequency alone.** Redshift builds an automated materialized view only when
  the expected benefit beats the cost to create and refresh it, and SQL Server only auto-applies a tuning
  action when the estimated gain exceeds a floor. Recurrence opens the question; it does not answer it.

**A departure, carefully scoped.** Two different minimums must not be confused:

- **A minimum before a quality claim counts is standard practice.** Envoy's outlier detection computes
  no success-rate verdict for a host below `success_rate_request_volume`, and runs no detection at all
  unless `success_rate_minimum_hosts` have enough traffic. SonarQube ignores its coverage conditions
  until there are at least 20 new lines to cover. Kayenta gives "no data" its own class, excludes it from
  the score, and fails the canary outright when half the metrics are missing. Google's SRE workbook makes
  the same point arithmetically: at ten requests an hour, one failure is a 10% error rate.
- **A minimum before *merging* is the departure.** For triggering a combined unit, everyone found uses
  small fixed counts and a benefit floor, then validates and reverts, because their observations are
  cheap. Ours are rare and expensive, so the caution moves to the front and a person approves. That is
  the part with no precedent, and it is the part to defend.

## 8.5 What happens to A-B when A becomes A-prime

The hardest question in the design, and each answer matches something a large company already ships.

| Question | Answer | Where this is already done |
|---|---|---|
| Does A-B break? | No. It pinned A by hash and keeps running on it; a frozen sprint keeps what it pinned | **Amazon** Step Functions: a new child version does not change a parent until the parent's reference moves |
| Does A-B silently become A-prime-B? | Never. Internals are locked; a member change is a new block, not an edit | **Google** Bazel: change an input's content checksum and the cached output is simply not reused |
| Is A-B now wrong? | Stale, not invalid, and still usable. If A is *revoked* rather than superseded, A-B moves to `suspect` with `MEMBER_UNAVAILABLE` | **Google** BigQuery: a materialized view refreshes on a compatible base change and is invalidated otherwise |
| Do we build and test A-prime-B automatically? | No, lazily. It becomes a candidate only when A-prime passes replacement compatibility against A and something asks for the pair again | **Google** Bazel: rebuild on demand when inputs no longer match, never eagerly on every change |
| What if A-prime is strictly better? | Still no automatic rebuild. The librarian may promote A-prime-B as a candidate; A-B is not retired | **Google** BigQuery: the base table always remains |

**In one line:** pinned members never move; a changed member makes a candidate, not an edit; and
candidates are built when asked for, not when changed.

## 8.6 The costs, stated plainly

Merging is not free. These belong with the design, not in an appendix.

- **Scheduler granularity.** A merged block is one node, holds one lease, and takes the union of its
  members' write scopes. Better placement quality, and **less parallelism inside the block**.
- **Retry.** A failure inside a merged block retries the **whole block**, unless the block declares
  internal retry.
- **Attribution.** A gap inside a merged block is attributed to the **block, not the member**, so
  attribution coarsens as blocks grow.

## 8.7 Two things industry does that this design should copy

- **Measure the block before trusting it.** Oracle's SQL Plan Management puts a new plan into history as
  **unaccepted**, test-runs it against the best accepted plan, and accepts it only if it performs as well
  or better. It is "not usable until the optimizer verifies plan performance". That is exactly the
  asymmetry above, already shipped.
- **Revert what does not help.** SQL Server and Azure SQL watch the affected queries after forcing a plan
  or creating an index, and automatically revert any action that did not improve performance. A merged
  block that measures no better than its members should be demoted the same way.

## 8.8 What merging buys today, and what it does not

Worth stating plainly, because it is the first question a compiler person asks. What this chapter
specifies is **composition**: the block pins its members by hash, their internals are locked, and it runs
them in order, unchanged. That buys a larger placement grain, a block-level quality record and a single
lineage to branch from. It buys **no execution saving at all** -- if A and B each iterate over N items,
the block still iterates twice.

**Fusion** -- rewriting the block's internals so the two run in one pass, dropping a check of B that A
already guarantees, folding shared work -- is a separate, later operation, and it is what would make
merging pay for itself. It is deliberately out of scope here. The boundary matters:

- The rule that would change is "internals are locked", which becomes **the contract is locked, the
  implementation is free**. The union-of-suites rule stays, so a dropped check has to be shown redundant
  by the suite that covered it still passing.
- The composite itself is the **oracle**: a fused block is compared against running its members in order,
  on replayed inputs.
- Legality would have to come from author declarations. TensorRT fuses from a published catalogue of pairs
  known to give the same result; there is no such catalogue for capabilities, and the **iteration shape** a
  fusion pass needs is not in the schema today.
- Failure behaviour changes observably: unfused, A failing on item 5 leaves no B effects; fused, items 1 to
  4 already have B applied.

Recorded as a next step, not a commitment. See `tundle/obby/Fusion After Merge.md`.

## 8.9 An open risk

Redshift forbids an automated materialized view from referencing another one -- no view of a view. If a
merged block A-B may later merge with C, this design goes **beyond** that precedent, and the depth at
which attribution and retry costs stop being worth the grain is not known. Record it as open.

## 8.10 Why it is done this way

Most of this mechanism already exists in openJiuwen, in `symphony/flow/`, and the design reuses it
rather than rebuilding it. `ExperienceRecipe.combination_structure` is already a capability set with its
own DAG; `qualified_edges` already requires both support and a success rate; the distillation already
excludes failing edges from grouping, which is the pruning assumption enforced in code;
`resolve_status_grade` already grades a pack as `candidate` or `verified`; `content_identity()` already
versions on real change rather than on counts; `PackageReviewGate` already runs ten deterministic checks
before an isolated reviewer sees a redacted copy.

What `symphony/flow` does not have is a declaration. A recipe carries no ports, effects, preconditions
or guarantees; A-B is not linked to A and B; the grade comes from observed success counts with no
held-out test; and members are referenced by id rather than pinned by hash. Those five gaps are what
this chapter adds, and they are the whole of it.

The industry references are cited for one question each, and only for what they demonstrably ship. The
research is cited second, where industry does not cover it: AllocBench for why the party that proposes
a build must not be the party that builds it, and Cordis for the boundary of composability.

# 9. Plan and schedule: a capsule holds no task, and the workflow keeps its shape

**A capsule is an abstraction: pulled from the library and told what to do through its inputs.** It never has a
task, a step or a place in a workflow written into it, so it stays the general tool for whatever step its ports fit.
The planner states what each node needs, capsules state what they can do, and only the Binding joins them. The
workflow keeps its stages, and its scheduler keeps order, parallelism and workers. Source of truth: `merged/SCHEMA.md`
§0.6, §3.4, §3.5, §4.3a.

## 9.1 What a capsule does not hold

Invariant 12: a Declaration names no step, node, sprint, plan, workflow, stage or task type, no capsule to run before
or after it, and no worker. A capability valid only for some inputs says so with `needs.when` predicates over its
inputs, never with a task list.

Today's AI4Research manifests hold no step, node or sprint id, but they do hold uses (85 files, read at `b0bf165f9`):

| Today's field | How many | In the schema |
|---|---|---|
| `applicability.task_types` | 85 of 85 | kept only as import evidence; the task type lives on the Plan step |
| `composition.requires_after` naming another capsule | 42 of 85, e.g. `cap.research-report-draft` requires `cap.research-evidence-synthesis` | a data dependency through ports when an artifact connects them; otherwise the plan's `depends_on` |
| `operator_compatibility.preferred` | named worker operators | dropped; the workflow assigns the worker and the invocation records it |
| a workflow position in the name or description | 14 of 85: 11 in the name ("Fixed Research Evidence Synthesis"), 3 in the description ("Freeze the accepted Part A evidence … for Part B consumption") | a neutral `summary`, which may not name stages, workflows, tasks or other capsules |

## 9.2 How a plan is put together and run (per sprint)

| # | Stage | Owner | What the schema supplies or records |
|---|---|---|---|
| 1 | write the plan | the planner | Plan steps: typed inputs and outputs, allowed effects, task type, `depends_on`, optional fan-out. No capsule names, as today (`elastic_planner.py:1328-1329`). The planner sees the library only as the set of port types available |
| 2 | repair against supply | the planner, from a code defect | a node no capsule chain can implement comes back as `CAPABILITY_IMPLEMENTATION_MISMATCH` (`:4137-4146`): supply reshapes the plan only through types |
| 3 | expand by composition | code | derived Plan steps (`derived_from`), each matched on its own; one capsule may fill several |
| 4 | offer and choose | the capsule layer's filter, then models | chapter "Pick": declared criteria first, then a choice from `summary` and `ports` |
| 5 | freeze | code | one Binding per step: `bound[]` (primary, context, dependency), fallbacks, overlays, all by hash |
| 6 | schedule | **the workflow's scheduler, not CC** | constraints only: declared write scopes, `resources` modes, and the gate's `parallel_safe` flag. The scheduler keeps topological order (`graph_scheduler.py:2179-2215`), its cap of 8, conflict hold-backs (`:3203`), worker leases and the step's retry count |
| 7 | dispatch | code | one **invocation** per actual run: predicates on fresh state, live hash equal to the pin, and a fallback run when the primary cannot run |
| 8 | gates and delivery | the workflow | each claim keeps the invocation that produced it |

**The planner never holds a list of capsules to schedule.** It says what a node needs; the offer, the freeze and
dispatch fill it. Registered workflows that name capsules per stage today (`allowed_capsules`) keep that as
`restrict_to[]` on the Plan step: a choice on the demand side, never stored on the capsule.

## 9.3 Real multiplicity

![Figure 18. Real multiplicity. One Declaration serves many Bindings; each Binding has one primary and any context or dependency capsules; each Binding has many invocations, one per fan-out item, attempt or fallback.](figures/M1.png)

| Relation | Cardinality |
|---|---|
| name to Declarations | 1 : N versions over time; 1 : 1 within a sprint (its snapshot); concurrent sprints may run different versions |
| Plan step to Binding | 1 : 1 per sprint |
| Binding to capsules | 1 : N: one primary, any context capsules, closed dependencies, pre-approved fallbacks |
| Declaration to Bindings | 1 : N: one capsule serves many steps, plans and sprints |
| Binding to invocations | 1 : N: fan-out items × attempts × fallbacks |
| composite to members | 1 : N, keyed by role; one Declaration may fill several roles |

**Fan-out.** A Plan step may declare `over: {input, max_parallel}` and `gather: {mode: all | best_effort, min_items}`. The capsule's port takes one
item; each item is one invocation with an `item_key`. **The capsule never knows it is mapped.** Items run in parallel
up to the smallest of `max_parallel`, the sprint's cap and the free workers, and one at a time if the capsule is not
`parallel_safe`. Effect scopes may use `{instance}`, so parallel items never write the same place. A capsule whose
port takes a whole collection is bound without `over`: the types decide. Today there is no fan-out: a `many` output
is one run writing a directory (`elastic_planner.py:1366-1378`). When items fail, `gather.mode` decides: `all` (the
default) fails the step, `best_effort` passes the successes and lists the failures, down to `min_items`. The step's
gate checks the gathered manifest in code before anything downstream reads it.

**Still six records.** The Binding is written by the freeze; its `invocations[]` are appended by dispatch. Today
attempts overwrite a mutable state file that keeps the last 20 (`task_lifecycle.py:54-56`), and frozen fallbacks are
never read at run time.

## 9.4 Where it lives in openJiuwen

CC adds records and checks, and uses openJiuwen's own layers and names for everything else. **Reuse comes first:**
what CC adds new is only the Declaration format, the records, one shared predicate evaluator, the admission gate, judge
standing and the tree index. The structure is the one
recorded in the tundle obby vault; the full table is `merged/SCHEMA.md` §4.17a.

| CC part | The openJiuwen piece it uses | How it fits |
|---|---|---|
| **Declaration** | the **Card** side of openJiuwen's Card-versus-Config rule (`ToolCard`, `AgentCard`, `WorkflowCard`; `.claude/rules/architecture.md`) | a Card is static, serialisable identity, and putting a session id or runner in one is an anti-pattern. Invariant 12 is the same rule: the Declaration is card-like and every use lives in run records. It adds what cards lack: preconditions, effects, trust |
| **loading a capability** | `AbilityManager` and `Runner.resource_mgr` for core abilities (tools, workflows, agents, MCP); `harness/extension_binder` for harness extensions; `create_harness(manifest, provider=...)` for agent templates | the same registration paths, fed from CC's hashed store |
| **Plan steps, scheduling, fan-out** | whichever engine runs the AI4Research plan: today its own graph scheduler; on openJiuwen a core workflow graph (Pregel), Agent Teams tasks, or a Swarmflow script with parallel and pipeline operators (agent-core `agent_teams/workflow`, surfaced by jiuwenswarm) | CC does not change with the engine; fan-out is Swarmflow's parallel operator or a workflow loop |
| **invocation** | the harness protocol: a capsule run as an agent is one **Turn** (exactly one start and one terminal event; `TurnResult` with usage and exact cost); a tool capsule's call is one provider **item** (`ItemLifecycleEvent`) | one invocation per Turn or item. A pause and resume stays one invocation, since `PAUSED` and `RESUMED` keep the same Turn; a retry after a terminal event is a new one (**design**, following the one-terminal-event rule). `observed_cost` comes from `TurnResult`; the event sequence and correlation ids are its trace |
| **trajectories** | `agent_evolving`'s canonical OTLP `Trajectory`, and Symphony's trajectory v2 evidence format | consumed, not redesigned: `trajectory_ref` points at one |
| **durable records** | `TrajectoryStore` and `LoadRecord` (in memory); jiuwenswarm's hash-chained Eternal Conversation history where a session opts in; checkpointers (`core/session/checkpointer`, Redis in `extensions`), which resume a run after a crash but do not record what ran; openJiuwen's pluggable stores in `extensions` (DB, KV, vector) | a capsule-layer rail writes Bindings and invocations durably, into openJiuwen's own stores rather than a new database |
| **judges** | the harness's built-in `verification` subagent (spec S_18); `agent_evolving`'s evaluators; Symphony's evaluation metrics (six of nine are model judges, off by default); AI4Research's 20 semantic registry checks and its default `llm_eval` gate | each is a judge with a standing per model and artifact type (§4.5c): it gates from day one, spot checks calibrate it, and only a measured one certifies (**design**) |
| **effects and approvals** | the harness `PermissionEngine` (`ALLOW`, `ASK`, `DENY`) with `PermissionInterruptRail`, and jiuwenswarm's policy mapping severity to them; `SysOperation` sandboxes with `SYSTEM`, `SESSION` or `CUSTOM` isolation, such as jiuwenbox | an irreversible, high-severity effect is an `ASK`, and `DENY` on an unattended run; an `{instance}` scope is a per-invocation `SESSION` sandbox. Permissions are off by default in jiuwenswarm, so a CC sprint turns them on |
| **ToolCard flags** | `exposure`, `parallel_safe`, `stateless`, `idempotent` | computed by the gate from the declared effects and `effect_class`, never trusted as written |
| **context taint** | Session VCS: `commit`, `snapshot`, `rewind`, `fork` | a context that held a revoked hash is not reused: the next invocation starts a new session, or forks from a snapshot taken before the capsule loaded (**design**) |
| **generalists** | `harness_providers`: `native`, `claudecode`, `codex`, `dsh`, behind `HarnessProtocol`; Agent Teams' `external_cli` role | each generalist's carrier is an `AgentTemplateSpec` naming a provider; enrolment checks the host capabilities its `HarnessCard` requires |
| **remote bodies** | A2A `AgentCard` (`extensions/a2a`); MCP servers | `remote_fingerprint` hashes the card or the tool listing |
| **overlays** | the experience layer (`evolutions.json`), written through `agent_evolving`'s `EvolutionStore` after preview and approval; the TTSE bank | pinned per sprint, or not loaded |
| **the tree, RSI** | agent-core's `rsi/harness_rsi` and its tree nodes (`RsiTreeNode`, `rsi/schema.py:96-111`), which jiuwenswarm projects for its web view (`agents/harness/common/rsi/models.py:292`); `agent_evolving`'s candidate validation from one snapshot | `builder_ref` joins RSI's tree; RSI's gate is builder evidence, and CC's gate admits |
| **Symphony** | `CapabilityProvider`, `SkillGraphUpdater` (above) | CC decides what Symphony may index |
| **prod-eligibility** | openJiuwen's aim for production use: globally unique identity, effects declared across hosts, admission records others can audit, no assumption that a person is watching | `decl_hash`, `ext:` effects, Verdicts, unattended runs |

**Names.** openJiuwen's vocabulary is `Session > Turn > Step`, with `Round` reserved for multi-agent phases. Three CC
terms sit beside it and must not be confused with it:

| CC term | Means | Not to be confused with |
|---|---|---|
| **Plan step** | one node of the AI4Research plan (`step_id`) | an agent-core **Step**, one cycle of an agent loop |
| **invocation** | one actual run of a capsule for a Plan step: a Turn for an agent capsule, an item for a tool capsule | a Turn or item that is not a capsule run |
| **capability** | anything an agent can call on; openJiuwen calls tools, workflows, agents and MCP servers **abilities**, and a capsule wraps one ability or skill | a Card, which is only its identity |

## 9.5 Why it is done this way

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| no task, step or neighbour in the Declaration | a use written into a capsule makes it specific, and puts plan facts where the builder, not the planner, writes them (invariant 9, **design**). Today 42 manifests fix their predecessor inside the capsule |
| match on declared contracts and ports, not task labels | filtering on declared preconditions and effects reached 0.980 success at 2,528 tokens a task, a keyword filter 0.620 (Contract2Tool, 2606.07904 Table V) |
| order comes from typed data edges or the plan | typed edges between capabilities repair locally (GraSP, 2604.17870); guessed edges are an observation |
| one invocation per run, with its step identity | a change must invalidate exactly the downstream runs (Execution lineage, 2605.06365 p6-7); fan-out and retries must be counted to judge a capability fairly |
| context capsules recorded per Binding | severe drift rose with the number of skills loaded together (SkillFuzz, 2607.02345 Fig. 6), so what shared a context must be known |
| the scheduler stays the workflow's | CC is a scheme, not a tool (supervisor, 2026-09-21); the workflow already orders, caps and leases (`graph_scheduler.py`), and CC only supplies declared constraints |

# 10. Integration: what each consumer reads, and when it turns on

The schema exists to be useful. Every field is there because something reads it, and nothing is enforced
before its reader exists. This section names the readers.

## 10.1 The three teammate features

| Consumer | Reads from the Declaration | Attaches to what already exists | Turns on |
|---|---|---|---|
| **Verification** | `guarantees.checks[]`, `acceptance`, `ports.outputs[].check`, `changes.effects[]`; then the Verdict, and the suites a parent passed | `EvaluationSuite` (`symphony/evaluation/suite.py`), `GoalEvaluator.should_spot_check()` (`harness/goal/evaluation.py`) for judge calibration, `PackageReviewGate` (`symphony/flow/review.py`) for the static gate | one check at M1; suites, judges and quality at M3 |
| **RSI** | `identity.lineage`, Standing, and the suites a parent passed | joins RSI's own tree by `builder_ref` against `RsiTreeNode.parent_id` (`rsi/schema.py`) | M4 |
| **Model routing** | `needs.model`, `budget` | `ModelAllocator` (`agent_teams/models/allocator.py`) and `IntelliRouterModelClient`, neither of which reads anything about a capability today | M3 |

## 10.2 Verification is the largest consumer, and the point is simple

**Every check needs a target, and today there is none.** Nothing on any carrier says what a capability is
supposed to do: `ToolCard`'s entire behavioural surface is `parallel_safe`, `stateless` and `idempotent`,
and `SkillSpec` is a directory, a mode and an allow-list. So a test can only be written about a *task*,
which is why self-built tools pass their tasks and fail held-out tests of their own job.

A declaration is what turns a check into something that can be aimed. Three layers follow from it, and
they are different problems (see the Verify chapter): conformance is binary and static, correctness is
binary per case, and quality is a **rate over a window** that needs a declared minimum number of
observations before it means anything.

## 10.3 RSI: CC exposes, RSI chooses

CC stores and exposes information efficiently, and marks as optional whatever it cannot guarantee. It
does not choose for RSI. The split of who knows what is deliberate:

- **CC's side:** lineage, Standing, the suites a capsule passed, its quality rate, and the hash of
  everything involved. All of it readable, none of it interpreted.
- **RSI's side:** which parent to branch from, when to build, and what to try. CC never sets that policy.

A child must pass the parent's suites plus its own, which is the monotone rule. A merged block earns its
own quality record rather than inheriting one from its members.

## 10.4 Model routing: the first capability-level facts a router could use

Routing today keys on the endpoint (`IntelliRouterModelClient`, failover and retry across deployments)
and on the team member (`ModelAllocator`, round-robin, by-name or router-backed). Neither reads anything
about the capability being run. `needs.model` and `budget` are the first facts that would let a router
choose on what the work actually requires. CC supplies them and takes no view on the routing policy.

## 10.5 Why the integrations are small

Each one attaches to something that already exists, and none of them asks another team to change its
design. That is the test the schema has to pass: if an integration requires a teammate to rebuild, the
schema is asking for too much.

# 11. Impacts across the workflow, and where the layer attaches

Requirement (d) has usually been read narrowly, as the three teammate features. Every decision in this
schema also lands on parts of the workflow nobody owns as a feature, and those are what a reviewer will
probe first.

## 11.1 What changes in each part of the workflow

| Part | Today | Impact |
|---|---|---|
| Planner | a hard filter on types, effects, network, proof classes, trust and status; then one model call that reads the full rows of every eligible capsule for every node | the filter gains declared preconditions; the model reads only `summary` and `ports` |
| Freeze | pins each node's capsule by manifest hash and aborts if a definition changed | pins `decl_hash`, the Verdict, **and every member's hash**, so a merged capsule's freeze is larger |
| **Scheduler** | ready nodes in topological order, at most eight in parallel, conflicting write scopes held back, one lease per operator | the shape is unchanged, but **merging changes granularity**: a merged block is one node, holds one lease, and takes the union of its members' write scopes. Better placement quality, **less parallelism inside the block** |
| Dispatch | four hard-coded precondition kinds | the same predicates as the filter, re-evaluated on fresh state through one evaluator, plus a hash check |
| **Retry and fallback** | per node | a failure inside a merged block **retries the whole block**, unless the block declares internal retry |
| Node gates | compiled from requirement checks, checks by type, and the manifest's own claims | three parts with named writers; judges carry a Standing |
| **Findings and attribution** | per node | a gap inside a merged block is attributed to **the block, not the member**, so attribution coarsens as blocks grow |
| Delivery and claims | invariants judged as prose | each claim keeps the invocation that produced it, plus a status |
| Gap handling | an unsatisfiable node fails the plan | a generalist named by the run contract, plus a gap Finding |
| Intake, intent, requirements | no capabilities today | **the work of each stage is supplied by a capsule too** |

The three emphasised rows are the honest costs of merging. They belong here rather than in an appendix,
because the trade they represent (grain against parallelism, precision and blast radius) is the
substance of the decision.

## 11.2 Where the layer attaches in the code

The design does not choose where to put itself. openJiuwen already has the sockets, and the largest one
is a protocol with two methods.

| Attachment point | Where | What CC does there |
|---|---|---|
| **`CapabilityProvider`** | `symphony/interfaces/capability.py` | implement `capabilities()` and `source_snapshot()`, and Symphony indexes only admitted capsules. Nothing inside Symphony changes |
| `SkillGraphUpdater` | `symphony/interfaces/graph.py` | add, update and delete as admission changes |
| `submit_observation` | `symphony/graph_engine.py` | feed run evidence back into the graph |
| Symphony Flow | `symphony/flow/engine.py` | the merge pipeline; CC supplies the declaration, lineage and pinned members it lacks |
| The load path | `harness/extension_binder.py` | the hash check before load, which does not exist today |
| Dispatch | `AbilityManager`'s railed tool-call path, and the `BEFORE_TOOL_CALL` event | a check keyed on the capsule, not only on the tool name |
| Rails | `harness/rails/` | one rail persists the Binding and its invocations |
| Permission engine | `harness/security/permission_engine/` | an irreversible severe effect is an `ASK`, and a `DENY` on unattended runs |
| Stores | `extensions/store/` (`db`, `kv`, `vector`) | where CC's records live, rather than a new database |
| AI4Research | the planner's filter, the freeze, dispatch | the workflow-side changes in 11.1 |

Locations are illustrative and open to change. The point they carry is that the design can work on what
exists, not that any one line number is load-bearing.

## 11.3 Why it is done this way

If a schema requires new infrastructure it will not be adopted, and if it requires other teams to
rebuild their components it will not be agreed. Every attachment above is either a protocol that already
exists, a hook that already fires, or a store that already holds other things. The one genuinely new
piece of machinery is the shared predicate evaluator, and it exists so that the filter and dispatch
cannot drift apart.

# 12. Worked example: `research.retrieval`

A realistic AI4Research capability: gather sources for a research question and land a provenance-complete source
pack. Today it exists as `cap.research-retrieval.yaml` (§10). What follows is how it *would* look and move in the new
system. Hashes are abbreviated. The composition finding in step 2 is **illustrative**, not observed.

## 12.1 The Declaration

```yaml
identity:
  schema_version: "2.8"
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
  resources: [{resource_key: ws:sprint_artifacts, mode: write}]
  network: {allowlist: [search.provider.example, "*.arxiv.org", "*.doi.org"]}
  model: {tool_calling: true, min_context: 32000}
  external:
    - {kind: package, value: httpx, pin: {version: "0.28.1", sha256: 3e1f…}}
    - {kind: service, value: search API, pin: {endpoint: "https://search.provider.example/v1/search", version: v1}}
    - {kind: secret, value: secret.search_api_key, guard: guard.secret_leak}      # re-checked at dispatch
changes:
  effect_class: compensable                                      # checked against the effects below
  effects:
    - {id: write_pack, resource_key: ws:sprint_artifacts, op: write, scope: "artifacts/{sprint}/research/**", idempotent: false, reversibility: scoped, risk: {severity: low, blast_radius: low, irreversibility: low}, assurance: enforced}
    - {id: query_out, resource_key: ext:search_provider:queries, op: emit, scope: "HTTPS GET to allowlist", idempotent: true, reversibility: emission, policy: withhold_until_freeze_ok, risk: {severity: med, blast_radius: low, irreversibility: high}, assurance: enforced}
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
  capsule's own claim (the Darwin Gödel Machine lesson, §5).
- **The third invariant has no check, and says so.** Its assurance is `declared`.
- **The relevance judge inside `golden_questions` is a model** (`anchor: judged`). The Verdict must therefore record
  its measured error, and it counts toward certification only under the false-pass ceiling.
- **Both predicates are `evaluable_at: planning`**: the question exists before planning, and the budget is known.
  So both enter the filter, once their parity checks pass, and dispatch evaluates them again on fresh state.

## 12.2 Admission

1. **Vocabulary.** Every name used is in the vocabulary: `artifact.research_question`, `ws:sprint_artifacts`,
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
   - `invalidated_by: [dep:provider.search.v1, policy_epoch, verifier:relevance-judge]`: the Verdict lapses if the
     search provider's pinned version changes, if the admission policy is revised (a new `policy_epoch`), or if the
     judge is re-audited.
8. **Standing.** The librarian sets `research.retrieval → 7c2e…`, `admitted`, reason `ADMITTED`.
9. **Symphony.** It receives an `add_skills` mutation. The capsule layer's `CapabilityProvider` now returns this
   descriptor with `content_hash = 7c2e…` and I/O taken from `ports`.

## 12.3 Offered and bound in a sprint

1. **Offer.** Sprint S-311 plans a node "gather sources" that consumes `artifact.research_question`. At the choice
   point, the filter evaluates the predicates:
   - `has_question`: true.
   - `budget_ok`: true. Remaining cost is 5.40, read 3 s ago.
   - `network`: the sprint's network zone permits the allowlist.

   The node's task type ("research") is on the Plan step only. The capsule declares no task, so it is offered because
   its input port takes `artifact.research_question` and its predicates hold.

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
bound:
  - {decl_hash: 7c2e…, role: primary, verdict_ref: V-0457, level: certified}
  - {decl_hash: 9d41…, role: dependency, verdict_ref: V-0391, level: certified}   # guard.secret_leak, closed at bind
fallbacks: [{decl_hash: 88a1…, verdict_ref: V-0460}]
offered: [7c2e…, 88a1…]
blocked: [{decl_hash: 3b07…, predicate: network_zone, where: planning}]
offer_hash: 2d9a…
selection_tokens: 390          # illustrative; measured in M2
choice_ref: call:planner/8841
predicates:
  - {id: has_question, value: true, context_sha256: aa01…}   # at the offer
  - {id: budget_ok, value: true, context_sha256: aa01…}
resolved:
  - {service_key: svc.search_provider, provider_decl_hash: 51f0…}
findings_consulted: [F-0192]    # report.draft is on step n6, not co-activated
invocations: []                 # dispatch appends one per run
prev_hash: …
```

4. **Dispatch.** Dispatch re-runs both predicates on the live context. `budget_ok` is still true (3.10 remaining after
   an earlier node), and the live hash equals the pin, so the operator runs. Dispatch appends an invocation:

```yaml
- invocation_id: S-311/n4/1
  item_key: null                # not a fan-out step
  attempt: 1
  decl_hash: 7c2e…              # the primary; a fallback run would name 88a1…
  operator: research-worker-2   # assigned by the workflow, never named in the Declaration
  model: {model_id: routing-choice, version: …}
  predicates: [{id: has_question, value: true}, {id: budget_ok, value: true}]   # on fresh state
  inputs_hash: …
  step_identity: h(7c2e…, sha(question), {k(n2), k(n3)})
```
   - The query emissions are allowed because the policy is `withhold_until_freeze_ok` and the freeze succeeded.
   - agent-core loads the verified body through `apply_extension_hot`, and the skill is added to
     `SkillUseRail.enabled_skills` for this node.
5. **What the run records.**
   - Output artifact hashes.
   - The sandbox's filesystem and network logs.
   - The fetch log.

   The audit compares them against `effects`. There are no writes outside scope and every host is on the allowlist.
   `extract_bytes_match` passes, and a `use_outcome` Finding is written.
6. **Delivery.** Claims delivered at the end of S-311 carry the step identities they depend on, and the invocation's
   `claims[]` lists them.
7. **The same capsule again.** The plan also has node n7, "gather sources for the follow-up question". It gets its own
   Binding to the same `7c2e…` and its own invocations, and its step identity differs because its input does. Had the
   planner asked for sources for each of 12 sub-questions, n4 would carry `over: {input: questions, max_parallel: 4}`:
   12 invocations with `item_key` 1 to 12, four at a time, each writing under its own `{instance}` path.

## 12.4 Revised

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

## 12.5 Revoked

The audit of sprint S-340 finds that `b913…` put the API key in the query string, i.e. in URLs that reach third-party
logs. This is an `audit_violation` against the declared use of `secret.search_api_key`.

1. **Revoke.** The librarian sets `revoked`, reason `REVOKED_SECURITY`.
2. **Find the affected work.** The invalidator lists every invocation that ran `b913…`: 14 nodes in 6 sprints
   (illustrative). Claims whose step identities descend from those nodes are marked `stale`, not deleted.
3. **Lineage.** Any admitted capsule with `b913…` in `context_capsules` becomes `suspect` (none in this case).
4. **Revert.** The Standing would revert to `previous[0] = 7c2e…`, but that version is `suspect` for drift. The revert is
   refused, and the offer for "gather sources" falls back to the other retrieval capsule.
5. **Gap.** Where that capsule is not applicable, a `gap` Finding opens. By the recurrence rule (§6) it reaches RSI only if it recurs.

![Figure 19. research.retrieval over time: admitted, bound, drifted, revised, revoked.](figures/F7.png)

## 12.6 The merge example: the chain that runs every sprint

The abstract A-B of §8 has a concrete instance, and it is the first candidate the algorithm would ever
propose, because it has the highest support in the system.

**The chain.** `intent -> IntentIR -> faithfulness`. Each part is the *work of a stage* (§2c): a
capability with an input, an output, declarable effects and a checkable postcondition. Each is admitted
and tested on its own, so each stays reusable elsewhere after the merge.

**The gate is outside the block.** `faithfulness` **assesses**: it emits a Finding about the IntentIR.
The gate **decides**. By §4.10's rule a capsule may assess but never decide, so the merge candidate is
the first three and the gate evaluates the resulting block exactly as it evaluates any node. Drawn this
way, the gate sitting visibly outside the merged block is the clearest single picture of the rule.

**Why it qualifies.** The chain runs in almost every sprint by construction, so it does not have to wait
for statistical recurrence: it is seeded from known workflow structure (§8). Its edges carry both high
support and a high success rate, which is what `qualified_edges` requires.

**What the merged capsule looks like.**

- `identity.lineage`: `relation: merge`, `parent` and `co_parents` naming the three members.
- `members[]`: three entries, each pinned by `decl_hash`, with the internal `structure` wiring
  IntentIR's output into faithfulness's input by declared port type.
- `ports`: the boundary of that internal DAG -- the raw intent in, the IntentIR and its assessment out.
- `changes`: the union of the members'. `needs`: the union minus what the members satisfy internally.
- `guarantees.checks[]`: the union of the three members' suites, plus at least one check of the block's
  own contract. **It does not inherit a quality record**: the block earns its own rate (§4.5c).

**What it costs.** The three nodes become one, so they take one lease and the union of their write
scopes; a failure anywhere inside retries the whole block; and a gap inside is attributed to the block
rather than to the member. Those are the trades in §11.1, and they are the reason a merge is approved by
a person rather than applied automatically.

**When `intent -> IntentIR` is revised.** The block keeps its pinned hash and keeps running. It is marked
stale against the new version, not invalid. A merged capsule over the new version is a *candidate*, built
only when something asks for the chain again and the new version passes replacement compatibility. If the
old version were revoked rather than superseded, the block would move to `suspect` with
`MEMBER_UNAVAILABLE`.

# 13. Capabilities today, and why CC is better

This chapter shows what capabilities look like today in jiuwenswarm and in AI4Research, compares AI4Research's
capsules with the schema record by record, and ends with why CC is better for both. Two real examples are in §2f.

The pattern across all of it is not that the ideas are missing. Every layer names them and leaves them unenforced:
agent-core's `ToolCard` carries `parallel_safe`, `stateless` and `idempotent`, written by the author and defaulting to
safe when absent (`core/foundation/tool/base.py:92`, `:241`); jiuwenswarm classifies each tool call by side effects and
risk tier, derives those facts from tool names, and ships the boundary disabled
(`rails/permissions/tool_capabilities.py:39-49`, `auto_config.py:99-103`, `resources/config.yaml:1130`); AI4Research
declares 95 preconditions its planner's filter never reads; Symphony counts a route as verified after one successful
run. So CC asks for no new idea. It asks that the same facts be declared once, in one place, and read by code before a
capability is used.

## 13.1 jiuwenswarm skills today

Counted in jiuwenswarm `02b37f47f`, over the 34 bundled skills in `resources/agent/workspace/skills/`
(`merged/DERIVATION.md` D1-D4, D11):

| | Today | Source |
|---|---|---|
| **What a skill declares** | 33 of 34 declare a `name` and `description`; 7 a version; 3 `allowed_tools`; 1 `models`; none declares inputs, outputs, preconditions or effects; 1 has invalid YAML | D1 |
| **What it really does** | 25 of 34 ship scripts; 13 state their prerequisites only in prose; 29 describe their outputs only in prose | D2 |
| **Tool limits** | `allowed_tools` is not enforced: agent-core's skill loader reads only the description (`skill_use_rail.py:946-958`), and skills get `bash` by default (`:77`, `:94`). `advanced-daily-report` writes files and pushes reports to Feishu, none of it declared | D4 |
| **Identity and versions** | installed by plain copy, with no hash; an experience layer changes a skill's behaviour without a new version, and a teammate's experience is saved without review (`config.yaml:732-733`) | Landscape; D11 |
| **Groups** | SkillPacks list members by name and are disabled together when one member is disabled (`skillpack.py:180-258`); Swarm Skills list dependencies by name in `dependencies.yaml`, each with `required` and a purpose of up to 150 characters, which the agent checks itself at start-up (`docs/en/SwarmSkills.md:339-372`) | source |
| **Permissions** | off in the shipped configuration, so every tool call is allowed until a user turns them on | Swarm 05 |

## 13.2 AI4Research capsules today

Capsules are looked up by id alone: the `version` field, present in 43 of the 85 manifests, plays no part in the
lookup (`capability_capsules.py:449-451`). Bundled jiuwenswarm skills, for comparison, go through no admission at all.

**This section is the reason the schema looks the way it does.** AI4Research already has capability capsules: 80
in its registry (74 stable, 6 draft), with 85 manifests in `harness/config/capability-capsules/` and
`harness/capability-capsules/` (AI4Research `b0bf165f9`). The schema is not a new idea laid
over nothing. It takes each part of today's manifest and changes how strictly it is held. For each record: what today's
capsules declare, what code actually does with it, what the schema requires instead, and the evidence for the change.

### What AI4Research's capsules enforce

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

## 13.3 Each record, compared

Each row takes one record of today's capsules, says what AI4Research does with it now, what the schema does
instead, whether that is stricter or looser, and why. Most rows are stricter: a field that is present but never
evaluated becomes a field that code evaluates. A few are deliberately looser, where today's strictness blocks
useful work without making anything safer.

| Record | Today | This schema | Stricter or looser | Why (evidence) |
|---|---|---|---|---|
| **Declaration: inputs, outputs** | file-format types; artifact types separately | types from one versioned vocabulary; every output names the check that validates it | stricter | Contract2Tool's filter worked only once names were normalised to one vocabulary; Symphony lets `unknown` match any same-named input (§4) |
| **Declaration: preconditions** | four hard-coded kinds at dispatch (`capability_capsules.py:1220-1242`), reached only for capability-native envelopes (`operator_runtime.py:796-808`); unknown kinds pass; never in the filter | one code-evaluable predicate `{path, operator, value}` with `state_source`, `max_age_s`, `on_unknown`, `on_unavailable` and a parity check; the filter and dispatch run the same evaluator; an operator outside the vocabulary is rejected at admission; `[]` only with a stated reason | stricter, and more general | a gate is sound only when its predicate *is* the capability's exit logic, and fail-open or fail-closed must be explicit (Don't Offer); today's two predicate sets are exactly the parity gap. Forcing non-empty lists invited filler such as `task_type_in` |
| **Declaration: invariants** | prose, judged by a model after the node | each bound to a check with a runner and an author, or marked `declared` so the gap is visible | stricter | a judge nobody measured can fail silently (The Blind Curator); a declared permission is not an enforced one (RelAIBuild) |
| **Declaration: effects** | names per kind | a scope, an `ext:` or `ws:` resource, `idempotent`, the capability's `effect_class`, a reversibility (inverse, scoped, compensate, emission) and an assurance per effect | stricter | reversal holds only inside a boundary (Cordis); composition screening needs the modifies set (SkillFuzz) |
| **Declaration: applicability** | task types in all 85 manifests, plus positive and negative keywords | both dropped from the capsule. The task type lives on the Plan step; input limits are `needs.when` predicates over inputs | moved to the demand side | a capsule holds no task (invariant 12), so it is reused wherever its ports fit; a keyword top-5 filter cut success from 0.775 to 0.620 (Contract2Tool); invariant 8 bars heuristics from eligibility |
| **Declaration: uses written in** | `requires_after` names the capsule to run first in 42 of 85 manifests; named worker operators; a fixed workflow position in 14 names or descriptions | none: order comes from data (ports) or the plan's `depends_on`; the worker is the workflow's choice; `summary` may not name stages or workflows | stricter | a plan fact written into the supply fixes the plan's order inside the capsule, where the builder, not the planner, writes it (invariant 9) |
| **Declaration: dependencies** | guard and resource capsules pinned; MCP providers live; no purpose recorded | every dependency pinned by hash or version by default, **or unpinned if the author writes down its purpose and contracts**, at a cost to trust (§3) | stricter by default, flexible by declaration | dependencies rot; given the failed contract, one-round repair rose from 10% to 78% (Skill Drift Is Contract Violation). jiuwenswarm's Swarm Skills already write a purpose per dependency; CC ties it to unpinning and to repair (**design**, §6) |
| **Declaration: identity** | only the manifest file hashed | every body file hashed; overlays hashed | stricter | a body can change under an unchanged manifest; jiuwenswarm changes skills with no new version (§2e) |
| **Verdict** | `status`, defaulting to stable | a typed outcome (ADMIT, REJECT, DEFER, ESCALATE) with reasons; each check with its runner hash and author; judge error measured; parity results; RSI's own result as `builder_gate` evidence | stricter, with one looser path | 215 of 222 self-built tools failed held-out tests of their own job; a DGM node gamed its checker's signal. **Looser:** a capsule can be admitted *provisional* on one postcondition, but only runs where its output is checked downstream, so imports are usable before suites exist (§3) |
| **Standing** | none: availability is the status field | one moving pointer per name, with typed reasons and history | new | retirement by evidence and eviction by cap must be told apart, or a dead curator looks alive; revert needs a target |
| **Plan step** | step ids; Symphony edges proposed by a model at confidence 0.7 or more; no fan-out, a `many` output is one run writing a directory | declared ports; typed unmet outcomes; the task type; optional fan-out (`over`), derived steps, `restrict_to` | stricter, and more general | typed edges repair locally (GraSP); guessed edges are an observation; one capsule mapped over items is real multiplicity |
| **Binding** | plan, capsule ids and approved fallbacks frozen (`elastic_planner.py:5886-5888`), but no runtime file reads the fallbacks; attempts overwrite a mutable state file, keeping the last 20 | `bound[]` with roles (primary, context, dependency), exact hashes, pinned overlays, fallbacks with their own Verdicts, evaluator version; an invocation per run (item, attempt, fallback), with predicate values on fresh state; the live hash must equal the pin | stricter; fallbacks usable | claims must trace to the exact run; a sprint sees only what it started with (invariant 3) |
| **The library as a whole** | a version on each registry entry, but lookups and the freeze resolve by bare id, so a change during planning aborts the freeze; a step nothing fits fails the plan (`apo_plan_compiler.py:626`) | versioned, append-only, monotone; three clocks; a generalist completes the step and records the gap | stricter, and able to improve itself | the 2026-09-15 report, R1-R2 and its §4.5; AllocBench for building on recurrence |
| **Finding** | none | screening, audits, drift probes and use, which can withdraw standing and never grant it | new | composition harm lives in sets, not single capsules (SkillFuzz); observation keeps a role, subordinate to declaration (§1) |

## 13.4 The choice, in one line

The schema keeps today's instinct, which is to declare everything and validate that it is present. It then makes each
declaration **evaluable** (code, not prose), **owned** (a named writer and author), and **pinned** (by hash). Where
it loosens anything, the loosening is confined:

- provisional capsules and generalists run on judged steps too, with their claims labelled rather than refused;
- unpinned dependencies cost trust and require a written purpose;
- the keyword signals it drops are a heuristic the evidence shows costs accuracy.

## 13.5 Why CC is better, for openJiuwen and for AI4Research

Each row is a gap that exists today, what CC does about it, and the measured reason the gap matters. The evidence is
from each paper's own setting; none of it measures CC as a whole, which M2 begins to do against today's filter.

| Gap today | What CC does | Why it matters |
|---|---|---|
| nothing code can filter on: jiuwenswarm skills declare no inputs, outputs, preconditions or effects, and AI4Research's filter never reads preconditions | declared ports and preconditions; code removes what cannot apply before a model chooses | without such a gate, a model picked an unrunnable skill in 7.8% of 1,000 conversations (2608.01050 p5) |
| eligibility by keywords, or by a model reading every row | a filter on declared contracts | on a synthetic 100-tool registry: all tools 0.775 success at 26,172 tokens a task; a keyword top-5 filter 0.620 at 4,482; a filter on declared contracts 0.980 at 2,528 (2606.07904 Table V) |
| more capabilities to choose from | about ten seed capsules, growth only where gaps recur | the pass rate fell by 0.21 (95% CI 0.15 to 0.27) as a library grew to 202 skills (2605.24050) |
| nothing proves what ran: skills copied with no hash, AI4Research hashing only the manifest, experience layers changing behaviour with no new version | every file hashed; overlays pinned per sprint; the live hash must equal the pinned one | with pinned replay, untouched work stayed identical in 3 of 3 runs while loop agents regenerated it (2605.06365 Table 1; n = 3) |
| undeclared effects, unenforced tool limits, permissions off | declared effects compared with what is observed; a CC sprint turns permissions on | 30.4% of the top 2,500 ClawHub skills were flagged conditional (2603.21019 p12) |
| quality judged by a model nobody measured | every judge keeps a standing, calibrated by spot checks; its passes are labelled until then | a biased judge silently stopped retirement (2607.07436 Table 1) |
| a self-built capability passes its task, not its job | held-out tests from another author before certification | 215 of 222 self-built tools failed held-out tests of their own job (2604.00392 p1, p5) |
| unreviewed evolution paths (teammate experience, TTSE) | a new overlay is a provisional revision, pinned per sprint | an ungated skill pool peaked at 62% with 105 skills, then fell to 50% with 179; a pre-commit gate reached 72% with 37 (2608.05810 Table 1) |
| harm found late cannot be undone | step identities and claim links reach exactly the affected work | of a 12.3-point drop, rolling back the harmful skills recovered 1.7 (2608.05810 p7) |

**Why this matters most for AI4Research.** A frozen plan chains steps, so one wrong capability spreads into every later
step and into the delivered claims. Sprints run for days and often unattended, so a problem found afterwards has
already done its damage. And the output is research claims, which must say what they rest on. CC catches what it can
before a run, labels what it cannot yet check, and traces what it missed to exactly the claims it touched.

# 14. What the schema does not claim

- **It does not claim that declared capsules are correct.** It claims that what was checked is recorded, and that what
  was not checked is labelled.
- **It does not claim safety in combination.** Screening reduces composition risk. Nothing certifies a set.
- **It does not undo emissions or external state.** It only controls when they are allowed, and checks a declared
  compensation once. What a capability does behind its interface is its author's (invariant 13).
- **It does not see a remote body change its behaviour behind an unchanged interface.** It catches a changed
  interface at dispatch, and changed behaviour only by observation, so such effects are at most `audited`.
- **It does not clean a poisoned context.** It traces and marks stale the claims a revoked context capsule touched,
  and never reuses that context. Influence that leaves no claim cannot be traced.
- **It does not fix degradation at scale on its own.** Much of it is the agent using no skill at all, which a
  filter cannot fix (2605.24050 Table 2).
- **It does not promise identical replays.** A model behind an API changes; sprints are recoverable, not
  byte-identical.
- **It does not promise task success.** Passing the filter means no declared exit holds, not that the capsule
  will succeed or was the right choice.
- **It does not make token budgets hard.**
- **It does not verify Cordis-style inverses** unless a check exercises them.
- **The design has not been measured as a whole.**
  - The numbers cited are the papers' own, in their own narrow setups.
  - None of them tested this design.
  - The worked example's findings, hashes and error rates are illustrative.
- **It does not claim that a model judge is trustworthy.** It claims that every judge's standing is recorded, that a
  pass from an unmeasured judge is labelled rather than trusted, and that only a measured judge counts toward
  certification or retirement **(design)**.
- **It does not claim that labelled results are right.** Softening lets more work run; the labels say how much of it
  is backed. A reader who ignores the labels gets today's trust level, not CC's.
- **It does not settle ownership, the ceiling, or the default thresholds.** The ceiling is proposed (SCHEMA §4.10). The
  recurrence threshold of 2, the overlap policy and the risk ceilings are all **(design)**.
- **It does not describe a system that exists.** The capsule layer is a proposal. Only the code cited as "today" and
  the openJiuwen sources exist.

## The question deliberately held open

**What cannot be represented as a capsule at all** is left open on purpose, rather than answered and
later retracted.

What *is* settled is the boundary. A capsule may produce an **assessment**; it may never be the thing
that **decides**. So a faithfulness check or a domain verifier is a capsule -- it emits a Finding and
something else acts on it -- while the gate, admission, the librarian's Standing moves, the planner's
filter, the freeze and dispatch never are. The schema enforces this by write access rather than by
classifying intent: no capsule may write to the gate, the suites, the logs admission reads, or the
record stores.

Candidates for the rest of the answer: anything whose effects cannot be declared, and anything that
needs to choose *other capabilities* at run time. Naming the boundary we know is stronger than an answer
that would have to be withdrawn.

# 15. What is needed when: one schema, progressively activated

Not everything is needed at once, and the usual objection to a staged schema does not apply here.

> **The schema is whole from day one. What is staged is how much of it is enforced.**

A field is declared in the schema from the start and sits **inert** until the component that reads it
exists. `needs.model` means nothing until routing reads it; `lineage` means nothing until RSI reads it;
`members[]` means nothing until the merge engine runs. So nothing is redesigned later, parts can be
missing while the system still demonstrably works, and the milestones below describe **activation, not
construction**.

This ordering is a recommendation, not a plan anyone has agreed, and nothing in it is measured.

## 15.1 The milestones

| | What is running at the end | What it proves |
|---|---|---|
| **M1** | **One node.** The minimal Declaration; the body's content hash checked before load; one predicate evaluator shared by the planner's filter and by dispatch; one Binding written per run | the thing that was checked is the thing that ran, and a declared precondition is evaluable |
| **M2** | **A few chained nodes.** Output ports feeding input ports by declared type; the dispatch re-check on fresh state; a node gate; a gap Finding when nothing fits | a wrong capability is caught before it poisons the nodes downstream |
| **M3** | **A library, about ten capsules.** Verdict, Standing, versions, the librarian, held-out suites, judges calibrated by spot checks, quality as a rate | admission is cheap enough to run on every capsule |
| **M4** | **Overlap and merge.** Edge evidence, qualified pairs and structures, merged capsules with derived Declarations and pinned members, block-level suites, A, B and A-B coexisting | bigger blocks can be placed at higher quality, and RSI has material to improve |
| **M5** | **Spatiotemporal composability.** Install and uninstall mid-run, dependents notified, registrations undone in reverse, within stated limits | the library can change under a running system |

## 15.2 What is enforced at M1

`identity.name`, `identity.kind`, `identity.carrier`, `identity.body[].sha256`, `identity.summary`,
`ports.inputs[]`, `ports.outputs[]`, `needs.when[]`, `changes.effect_class`, `guarantees.checks[]`.

Declared but inert until the milestone that needs them: `identity.lineage` (RSI, M4); `needs.model` and
`budget` (routing, M3); `guarantees.acceptance`, `evals` and the quality criterion (M3);
`changes.provides` and `invariants` (M2); `overlays`, `load_mode` and `exempt` (M3); and `members[]`
with `structure` (the merge engine, M4).

**Field count is a cost.** Every *enforced* field is work for whoever writes a capsule and a check the
gate must run. A large required core discourages the adoption the whole design depends on, which is why
the core is ten fields and not forty.

**Required-ness lives in the gate, not in the schema.** Protocol Buffers removed `required` on purpose:
its guidance is to write "required" as documentation instead, because a required field can become
unnecessary later but can never be removed. That is exactly the shape this section needs. The schema
marks nothing required; **the gate's policy epoch decides what is enforced**, and that policy is
versioned, can be relaxed, and is recorded on every Verdict. It is what makes "progressively activated"
a mechanism rather than a promise.

## 15.3 What is off the ladder entirely

**Ranking, sorting and retrieval inside the offer.** Symphony already does these and they work:
`retrieval/`, `evaluation/`, `discovery/`, `graph_engine.py`, `orchestration/` and `experience/` all
ship today. CC decides *what Symphony may index*, through a protocol with two methods, and does not
rank. This is stated once and not revisited.

## 15.4 M1 on a file that already exists

`harness/capability-capsules/cap.research-claim-extract.yaml`, one of thirty-nine in that folder,
already declares:

```yaml
preconditions:
  - check: source_evidence_present
    description: Source evidence includes enough text or anchors to extract claims.
```

That is a name and a sentence of prose. Nothing evaluates it: the planner's hard filter never reads
preconditions at all, and dispatch checks only four fixed kinds. **M1 is exactly that delta, on one
node** — make the precondition an evaluable predicate, run it through one evaluator at both planning
and dispatch, hash the body and check the hash before load, and write one Binding recording what ran.

Today's manifests already carry *more* fields than M1 enforces, and most of them are prose no machine
reads. The M1 core is **smaller** than what AI4Research capsules already declare. It is just evaluable.

## 15.5 Left open

How the filter with declared preconditions is compared with today's filter; what the run contract's
defaults should be for research steps; who owns the shared predicate evaluator; and the cost of
certification per capsule.

**Where the detail lives.** The schema is `merged/SCHEMA.md`, why each part exists is
`merged/DERIVATION.md`, the knowledge base the documents are built from is `kb/`, and the directives and
decisions are in the tundle obby vault.

# Appendix A. The openJiuwen and AI4Research parts CC uses

CC is built onto what already exists. This appendix says what each part is and does, where it lives, and how CC uses
it. Paths are in agent-core `e23806c1` (under `openjiuwen/`), jiuwenswarm `02b37f47f` and AI4Research `b0bf165f9`
(under `harness/`), each read in source. The fuller notes are in the tundle obby vault (`openJiuwen Landscape`,
`agent-core/Core 00-06`, `jiuwenswarm/Swarm 00-05`).

## A.1 agent-core: identity, loading and running

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **Card and Config** | a Card (`ToolCard`, `AgentCard`, `WorkflowCard`) is a capability's static, serialisable identity; a Config holds its runtime resources. agent-core's own rule forbids putting a session id or runner in a Card | `.claude/rules/architecture.md:31`; `core/foundation/tool/base.py:78` | the Declaration is card-like: identity and contract, never a use |
| **`ToolCard` flags** | `exposure`, `parallel_safe`, `stateless`, `idempotent` on each tool | `core/foundation/tool/base.py:78-110` | computed by CC's gate from declared effects, never trusted as written |
| **`AbilityManager`, `Runner.resource_mgr`** | registers tools, workflows, agents and MCP servers, which agent-core calls abilities, as process-wide state | `core/single_agent/ability_manager.py:142`; `core/runner/runner.py` | the path through which admitted capsules are registered |
| **Runner** | executes agents and workflows on one engine, with sessions, streaming and checkpoints | `core/runner/runner.py` | runs each capsule; unchanged |

## A.2 agent-core: the DeepAgent harness

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **DeepAgent** | the coding-agent framework built on the core: model calls, tools, subagents, a task loop, a workspace | `harness/` | the agent that runs research steps |
| **Rails** | lifecycle hooks (before and after a model call or tool call, and more) through which features plug in without forking the loop | `harness/rails/` | CC adds one rail, to record runs durably and compare tool calls with declared effects |
| **Extension specs** | `SkillSpec`, `McpServerSpec`, `AgentTemplateSpec`, `PluginSpec`: how each kind of extension is described for loading | `harness/schema/extension_spec.py` | the carriers a Declaration names |
| **Extension binder** | loads and unloads extensions at run time (`apply_extension_hot`), undoing registrations in reverse order; loads by name with no hash check | `harness/extension_binder.py:27` | loads capsules from CC's hashed store, after CC checks the hash |
| **`SkillUseRail`** | offers skills to an agent through an allow-list (`enabled_skills`); the agent sees each skill's description and loads it when it chooses; it never reads a skill's `allowed_tools` | `harness/rails/skills/skill_use_rail.py:52`, `:946-958` | applies CC's offer for skills |
| **Permission engine** | decides per tool call whether it is allowed, asked about, or denied (`ALLOW`, `ASK`, `DENY`); `PermissionInterruptRail` raises the question to a person. Off by default in jiuwenswarm | `harness/security/permission_engine/core.py:140` | an irreversible, severe effect is an `ASK`, and a `DENY` on unattended runs |
| **Verification subagent** | a built-in subagent that reviews another agent's work with a model | `harness/subagents/verification_agent.py:274`, `:318` | one of the judges CC gives a standing to |
| **`LoadRecord`** | the in-memory record of what an agent loaded | `harness/resources/extension_resolver.py:60` | what CC's rail persists into Bindings |

## A.3 agent-core: protocols, teams, sessions and storage

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **Harness protocol** | a provider-neutral interface for hosting any agent harness. Vocabulary `Session > Turn > Step`. A Turn has exactly one start and one terminal event and may pause and resume; each tool call is an item; a `TurnResult` carries usage and cost | `harness_protocol/events.py:23-31`, `:148`, `:178`; `results.py:149` | one capsule run is a Turn, or an item for a tool; cost comes from `TurnResult` |
| **Harness providers** | ready implementations of that protocol: `native` (DeepAgent), `native_v2`, `claudecode`, `codex`, `dsh`, built with `create_harness(manifest, provider=...)` | `harness_providers/factory.py:160` | each generalist is an agent template naming a provider, such as Codex or Claude Code |
| **`HarnessCard`** | a harness's identity, protocol version and the host capabilities it requires | `harness_protocol/models.py:132` | enrolment checks those requirements |
| **Agent Teams** | a Leader and Teammates over a message bus and task database; a Teammate may be an external Claude or Codex CLI (`external_cli`) | `agent_teams/` | not a capsule in v1, because the Leader plans |
| **Session VCS** | version control for an agent's context: `commit`, `snapshot`, `rewind`, `fork` | `core/session/vcs/manager.py:104-185` | a context that held a revoked capsule is not reused: a new session, or a fork from before it loaded |
| **Checkpointers** | save state so a run can resume after an interrupt or crash | `core/session/checkpointer/`, `extensions/checkpointer/` | not a record of what ran; CC does not rely on them for evidence |
| **`SysOperation` sandboxes** | where filesystem, shell and code actually execute, locally or in a sandbox isolated per system, session or custom scope (jiuwenbox is one) | `core/sys_operation/config.py:93`; `extensions/sys_operation/` | admission runs a capsule here to observe its effects; `{instance}` scopes map to a session sandbox |
| **Stores** | pluggable database, key-value and vector stores | `extensions/store/` (`db`, `kv`, `vector`) | where CC keeps its records, rather than a new database |
| **A2A** | client and server for agent-to-agent calls, with agent cards | `extensions/a2a/` | carrier for remote agents; CC fingerprints the card |

## A.4 agent-core: evolution, RSI and Symphony

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **`agent_evolving`** | training, evaluators, optimisers and the canonical OTLP `Trajectory`; skill experience is written through an `EvolutionStore` after preview and approval | `agent_evolving/trajectory/model.py:132`, `store.py:23`; `checkpointing/evolution_store.py:41` | trajectories are consumed as they are; experience layers are pinned per sprint as overlays; its evaluators are judges with a standing |
| **RSI** | recursive self-improvement for agent harnesses; keeps a tree of attempts (`RsiTreeNode`: parent, adopted, score) and its own candidate gate | `rsi/`; `rsi/schema.py:96-111` | builds capsules from gaps; its tree joins CC's by `builder_ref`; its gate is builder evidence, and CC's gate admits |
| **`symphony/flow`** | a distil-to-install pipeline for capability sets: recurrence-qualified edges, structural grouping, `candidate`/`verified` grading, content-hashed packages, a ten-check static review gate, an isolated LLM reviewer, and an immutable versioned store | `symphony/flow/` (`engine.py`, `distill.py`, `models.py`, `packager.py`, `review.py`, `store.py`) | the merge engine, reused as it is. CC adds what it lacks: a Declaration on the block, lineage to its members, a held-out test, and members pinned by hash |
| **Symphony** | capability assets for skills, subagents and agents: fingerprints, a retrieval tree, an orchestration graph with Fast and Beam planners, experience and evaluation | `symphony/` | downstream of CC: it indexes only what CC admits, through `CapabilityProvider` (`interfaces/capability.py:13`) and `SkillGraphUpdater` (`interfaces/graph.py:14`) |

## A.5 jiuwenswarm, the product

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **Skills** | `SKILL.md` folders; the 34 bundled skills declare a name and description and nothing about inputs, outputs or effects | `resources/agent/workspace/skills/` | import sources, entering as provisional |
| **SkillPacks, Swarm Skills** | packs of skills listed by name; team skills with roles, a workflow and a `dependencies.yaml` whose entries carry a purpose | `server/runtime/skill/skillpack.py`; `docs/en/SwarmSkills.md:339-372` | packs become composites pinned by hash; team skills are not capsules in v1 |
| **Swarmflow** | deterministic multi-stage team workflows with parallel and pipeline operators (agent-core `agent_teams/workflow`) | `docs/en/TUISwarmFlowGuide.md` | one way the plan's fan-out could run |
| **TTSE, teammate experience** | evolution paths that keep facts and experience without review | `resources/config.yaml:732-733` | pinned per sprint as overlays, or not loaded |
| **Auto Permission** | classifies each tool call: a `ToolCapability` with category, operation family, resource class, `static_side_effects` and `risk_tier`, plus the call's read, write and external paths; medium risk routes to a reviewer, and decisions go to an append-only hashed audit. The facts are derived from tool names (`host_static`, `name_classification_hint`, `unknown`), and `permissions.enabled` is `false` by default | `agents/harness/common/rails/permissions/tool_capabilities.py:39-49`, `auto_decision.py:499-501`, `reviewer_route.py:230`, `persistent_audit.py`, `resources/config.yaml:1129-1132` | the nearest existing thing to declared effects: CC declares the same facts per capability, so they can be checked before selection rather than at the moment of the call |
| **Eternal Conversation** | an opt-in, hash-chained, append-only history of a session's tool calls and results | `agents/harness/common/rails/eternal_conversation/` | a durable record CC can read where a session opts in |

## A.6 AI4Research, the workflow CC extends

| Part | What it does today | Where | What CC changes |
|---|---|---|---|
| **Planner** | a model writes the plan (PlanIR) and may not name a capsule; a node no capsule can implement goes back for repair | `lib/elastic_planner.py:1328-1329`, `:4137-4146` | nothing: plan steps state needs, never capsules |
| **Hard filter** | removes capsules by types, effects in both directions, network, proof classes, trust and admission status; never reads preconditions | `lib/elastic_planner.py:4553-4648`; `lib/capability_admission.py:12-26` | adds declared preconditions, model limits, Standing and composition |
| **Selection call** | one model call reads the full rows of every node's eligible capsules and binds each node | `lib/elastic_planner.py:4678-4760` | the model reads only a summary and ports per node |
| **Freeze** | pins each node's capsule by manifest hash; aborts if a definition changed | `lib/execution_authority.py:28-94` | pins every body file and the Verdict, by snapshot |
| **Scheduler** | ready nodes in order, up to 8 in parallel, conflicting write scopes held back, one lease per operator | `lib/graph_scheduler.py:2179-2215`, `:3203`; `lib/operator_runtime.py:504-515` | unchanged; CC supplies declared constraints |
| **Dispatch** | resolves the capsule and checks four precondition kinds | `lib/operator_runtime.py:796-808`; `lib/capability_capsules.py:1220-1242` | the same predicates as the filter, on fresh state, and a hash check |
| **Evaluation plan** | compiles each node's gate from requirement checks, checks by type and the manifest's own claims | `lib/evaluation_plan.py:277-356` | three parts with named writers; judges get a standing |

# Appendix B. Figures from the papers

Each figure is cropped from the paper's own PDF by `../deck/figures/extract_paper_figs.py`, with its page and caveat.

![Figure 20. Don't Offer What Can't Be Done (2608.01050), Fig. 1, p4: the three-stage pipeline. Only stage 2, a deterministic gate on each skill's own exit conditions, removes candidates.](figures/papers/dont-offer-pipeline.png)

![Figure 21. Don't Offer What Can't Be Done (2608.01050), Fig. 2, p4: skill-description tokens. The gate removes 59.1% after semantic matching, 90.5% combined. Ten skills, one month; description tokens only.](figures/papers/dont-offer-tokens.png)

![Figure 22. Contract2Tool (2606.07904), Table V, p8: a keyword top-5 filter cuts tokens but lowers success; contract-based filtering exposes one tool, cuts tokens tenfold and raises success. Synthetic registry, mocked execution.](figures/papers/contract2tool-exposure.png)

![Figure 23. More Skills, Worse Agents? (2605.24050), Fig. 1, p3: pass rate falls as the library grows from the oracle skills to 202. Human-authored skills; 38 task-model pairs.](figures/papers/more-skills-drop.png)

![Figure 24. The Blind Curator (2607.07436), Fig. 2, p5: deterministic checks and an LLM judge catch different defects. One domain; flag rates, not scores.](figures/papers/blind-curator-qc-vs-judge.png)

![Figure 25. When Self-Evolution Backfires (2608.05810), Fig. 4, p7: rollback after the fact recovers little; removing the source skills recovers 1.7 of 12.3 points, and the pool gated before commit ends at 72.0%. One run.](figures/papers/backfires-contamination.png)

![Figure 26. SkillFuzz (2607.02345), Fig. 6, p9: severe drift is rare for single skills and rises with the number co-activated, to 66.5% at five, which the paper calls a fourteen-fold increase.](figures/papers/skillfuzz-depth.png)
