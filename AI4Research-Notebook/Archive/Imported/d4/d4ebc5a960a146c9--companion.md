# Capability Capsule: the schema, spelled out

Companion to the workshop deck of 22 September 2026, one section per slide. Muk Chunpongtong.

*Code* marks a fact checked in source (agent-core `e23806c1`, AI4Research `b0bf165f9`); *design* marks a decision cited work motivates but does not prove. Every cited paper was read in full; page-level numbers are in `verify/PAPER-LEDGER.md`. `SCHEMA.md` v1.6 wins where the two differ.

# Summary

## a to g in one page

**The schema answers all seven requirements with one idea: declare first, so every check has a target, and check before any run uses a capability.**

| Req. | Question | Answer | Slides |
|---|---|---|---|
| a | What does it do, and why? | Every capability declares what it needs, guarantees and affects, and how its effects are undone, so the library can change safely (spatiotemporal composability). Admission tests that declaration before any run uses it, and availability decides what a run may bind. Declaring first is safer than watching afterwards, and each tool the schema serves is one the research says is needed | 3-8 |
| b | How is it built? | One hashed manifest, and records outside it that name the hash. Two levels, provisional and certified. One declared predicate evaluated by the filter, dispatch and the capsule itself (predicate parity). Imports enter as provisional | 9-14 |
| c | Where does it sit? | Selection at planning, pinning at the freeze, checks at dispatch, claims tied to bindings. The capsule layer sits on agent-core, feeds Symphony through its provider and graph-update hooks, and keeps what AI4Research plan steps already require | 15-18 |
| d | What does it depend on? | agent-core, Symphony, RSI, verification and routing, each through a record both sides agree on | 19-20 |
| e | What is similar? | Others judge a capability by watching it. Here the reference for "correct" is the author's declaration, tested before use | 21 |
| f | What is it better at? | Five advantages, including fewer selection tokens and removing what cannot run, each stated with what would prove it wrong | 22-25 |
| g | Can it be built? | Every part exists in openJiuwen, AI4Research or a paper; combining them is the work. Who owns which part is for discussion, since the capsule touches every team. Five milestones, provisional first | 26-27 |

*Table 1. The requirements, answered.*

# a. Function: what it does, and why

## Capability Capsule is a schema, not a tool

**Capability Capsule is a schema every capability declares, plus two decisions made with it: admit, and make available. It is a scheme that uses tools; it is never one itself.**

- **The layering (supervisor, 21 September).** "CC is more of a scheme, and verifier is a tool. CC can use tools, but CC is not a tool." The schema defines the rules; the capsule layer's code (store, importer, admission rule, provider, librarian) applies them on agent-core.
- **What stays with others.** Building is RSI's, measuring is the verifier's, choosing models is routing's, running is agent-core's. Capsules change code, prompts and manifests, never model weights. AI4Research itself is not a capsule (supervisor, 18 September).

| | What happens | Who |
|---|---|---|
| Declare | a capability states its inputs, outputs, preconditions, postconditions, effects and dependencies | its author, in the manifest |
| Admit | a version is kept only if tests of its declared job pass | the admission rule decides; the verifier measures |
| Make available | the capsule layer chooses which kept versions a run may bind | the librarian writes it; the run pins it at the freeze |
| Compose | capsules can be added, replaced, rolled back and removed without breaking one another, because each declares what it needs and how its effects are undone | the capsule layer, from the manifest and availability events |

*Table 2. The function.*

- **Scheme and schema.** The supervisor's word is *scheme*: this schema, plus the rules its capsule layer applies with it. The deck says schema for the contract, and capsule layer for the code that applies it.
- **Terms used from here on.** *RSI*, recursive self-improvement: the teammate's model that builds and improves capabilities. *Run pin*: the record of exactly what a run used. *Librarian*: the capsule-layer code that keeps, retires and replaces capsules. *M1 to M5*: the milestones (slide 27). *Invariant 8*: eligibility is decided only by declared predicates.

## What every capability declares, in one manifest

**The schema is what every capability fills in. Here it is for one AI4Research capability, fetching a paper's full text; the example is illustrative, and every field is defined in `SCHEMA.md` A1.**

```yaml
schema_version: "1.6"
capability_id: fetch-paper-fulltext     # stable; a contract change is a new id
capability_type: tool
revision: 3                             # a better version is a new revision
binding: {kind: tool, ref: fetch_fulltext, parallel_safe: true, idempotent: true}
inputs:  [{name: paper_id, type: arxiv_id, required: true}]
outputs: [{name: fulltext, type: document_text}]
effects:
  - {kind: network, scope: "export.arxiv.org", compensation: none needed, read only}
  - {kind: write, scope: "workspace/papers/", compensation: delete the written file}
preconditions:
  - {id: network-allowed, check: {path: run.policy.network, operator: includes, value: export.arxiv.org},
     state_source: run policy, evaluable_at: planning, on_unavailable: block}
  - {id: id-resolves, check: {path: inputs.paper_id, operator: resolves_in, value: arxiv},
     state_source: arXiv API, evaluable_at: dispatch, on_unavailable: block}
postconditions:
  - {id: text-present, statement: "fulltext has at least one page of text", anchor: deterministic, over: outputs}
  - {id: title-matches, statement: "the title in fulltext matches the arXiv record", anchor: reference,
     over: inputs_and_outputs}
dependencies: [{kind: service, name: arXiv API, pin: {endpoint: export.arxiv.org/api, version: "2026-07"}}]
load_mode: invoked
components: [{path: fetch_fulltext.py, sha256: "…"}]
lineage: {predecessor: "…revision 2 content_hash…", relation: supersedes}
```

- **What reads each part.** The filter reads `effects`, `inputs`, `outputs` and the planning-time precondition; dispatch reads both preconditions; the verifier runs the postconditions; agent-core loads `binding`; the run pin records the hash.
- **What is not in it.** The tests, the certificate and availability: records that name this manifest's hash.

## Composable in space and time, by declaration

**A library that changes while it is used needs two guarantees. Spatially, each capsule declares what it needs, so dependents react when a dependency changes. Temporally, each declares how its effects are undone, so versions can be added, replaced, rolled back and retired. The schema carries both.**

![Figure 1. Spatiotemporal composability. Space: a declared, pinned dependency, and the availability event that moves a dependent to revalidation when the dependency is revoked. Time: revisions, a run that keeps the version it pinned, and the boundary that decides how an effect is undone.](figures/compose.png)

- **Where the terms come from.** *A Programming Paradigm for Spatiotemporal Composability* (Cordis, 2608.25512) names the two dimensions for dynamically composed systems, with self-evolving agent harnesses as a motivating case: temporal, removing a component reverses what it did; spatial, components declare and resolve their dependencies, and their lifecycles follow those dependencies (p4-6). It is a formal model with one qualitative case study, and agent harnesses are its future work (p69, p82), so the schema borrows its vocabulary and boundary, not a measured result. Cordis also leaves an inverse's correctness to the author (p58-59); certification tests it here.
- **Space in the schema.** `inputs`, `preconditions` and pinned `dependencies`, declared ports between plan steps, and availability events that move dependents to `revalidation_pending` when a dependency is revoked or its contract breaks.
- **Time in the schema.** Every write, execute and network effect declares its `undo`: an `inverse` inside the boundary, a `compensation` outside it, or `irreversible` (invariant 6). Revisions never overwrite; retired is kept; a rollback is a new revision.
- **The boundary.** Reversal holds only for locations the system alone can modify and restore; data that leaves can only be withheld or compensated (2608.25512 p70-71). So the schema asks which side each effect is on, rather than promising to undo everything.
- **Between runs, not within one.** Cordis swaps components inside a running process. Here a run keeps the versions it pinned (invariant 3), and change reaches the next run.
- **Combinations are screened, not certified.** Severity is compositional: severe drift rose from 4.7% of plans with one skill loaded to 66.5% with five (SkillFuzz, 2607.02345 Fig. 6). The schema gives a screener such as SkillFuzz its contracts and records what it finds (composition reports, `SCHEMA.md` B7); a step never co-loads a set confirmed as high-risk.

| SkillFuzz reads (p4-5) | The schema supplies, authored and tested |
|---|---|
| preconditions, postconditions | `preconditions`, `postconditions` |
| modifies set, invariants | write and execute `effects` with scopes; postconditions `over: each call` |
| domain scope, abstract actions | `description`, typed `inputs` and `outputs`; effect kinds, `binding.kind` |
| extraction confidence | certificate level: provisional capsules are screened first |
| which skills share a context | `load_mode: context_injected`; the run pin's `co_loaded[]` |

*Table 3. What a composition screener reads, and where the schema supplies it. SkillFuzz's high-risk plan-level flags were confirmed in execution 80.6% of the time (Table II, p6-7; one run per condition).*

## Every tool the schema serves is one the research needs

**The schema exists for the tools around capabilities, and each of those tools answers a failure a paper measured. A field no tool reads is removed.**

| Tool in the new system | The failure it answers (paper) | What it reads or writes in the schema |
|---|---|---|
| Admission gate | 215 of 222 self-built tools failed every held-out test of their own job, and no in-session signal flagged them (Beyond Task Completion, 2604.00392 p1, p5; replayed after the sessions; Haiku 4.5, 3 tool-creating protocols of 5, 8 sessions, 3 seeds) | postconditions; certificate |
| Pre-commit improvement check | without the gate that requires marginal gain over the pool, pass@1 was 8 points lower; removing the 8 bad source skills afterwards recovered only 1.7 of 12.3 points lost (When Self-Evolution Backfires, 2608.05810 p5-7; one run) | availability rule 1; `build_context` |
| Executability filter | without a deterministic gate, a model picked a skill that could not run in 7.8% of 1,000 risk-enriched conversations (Don't Offer What Can't Be Done, 2608.01050 p5; selection only, nothing executed, replayed once) | preconditions, types, effects: predicate parity |
| Verifier audit | false-pass bias stopped retirement by the contribution rule (0 to 0.3, against 1.3 clean) while raw deprecations never reached zero, so the count hid it (The Blind Curator, 2607.07436 Table 1, p6; 3 seeds) | verifier audit; false-pass ceiling |
| Librarian | a retirement rule needs calibrating: harsh retirement fell below the no-skill floor, and the cap mainly controlled variance (Library Drift, 2605.19576 p3-6) | availability events with typed reasons |
| Gap-driven builds (RSI) | once building meant writing code, first-sight commitment was 85-99% for three of four models (2607.23332 Table 1, p6) | gap record, counted over distinct runs |
| Run pin and taint | contamination travels through what a skill was built from (2608.05810 p7); hashed step identities let a change invalidate exactly the downstream steps (Execution lineage, 2605.06365 p6-7), the path a revocation reuses (*design*) | run pin; lineage |
| Composition screening | severe drift toward unrequested goals rose from 4.7% of plans with one skill loaded to 66.5% with five, and 80.6% of plan-level high-risk flags were confirmed in execution (SkillFuzz, 2607.02345 Fig. 6 p9, Table II p6-7) | the contracts it reads; `load_mode`; composition reports (B7) |

*Table 4. Each tool, the failure behind it, and its part of the schema.*

- **Why a shared schema, not eight tools.** Each tool needs the same facts about a capability: its declared job, its conditions, its effects, its exact bytes. Without one contract each guesses what the others meant.
- **Libraries are worth it.** Alita-G's self-built tool library lifted GAIA validation pass@1 from 75.15% to 83.03% (2510.23601 p7), on the set it was built from. The failures above are about what gets kept and offered, not whether to keep anything.

## Declaring first is safer than watching afterwards

**A declared contract is checked before any run uses the capability, and every later check has a target. Watching outcomes finds a fault only after runs have built on it.**

![Figure 2. Two ways to judge a capability. Observed: build, use, watch, and retire later if the judge notices. Declared: declare, test the declaration at admission, filter before a model chooses, and compare at dispatch.](figures/declared.png)

- **Why AI4Research needs it most.** The pipeline freezes the plan and pins a capsule per step. A capsule bound at planning that cannot run fails its step at dispatch, and the frozen plan cannot swap it; in-run gates can reject or repair an output but not replace its capsule; and the output is claims from papers. In a chat, a blocked skill costs one turn; here it costs a step of a frozen run.
- **What a declaration buys.** A guarantee *by construction*, relative to the declaration: a capsule blocked by its own declared precondition could not have completed in that state (Don't Offer What Can't Be Done, 2608.01050 p3). Observation can only give a rate, after the fact.
- **Observation keeps a role.** Held-out tests, retirement and the verifier audit all observe behaviour. What changes is that each observes against a declared target, and the first check runs before any use rather than after runs have built on the capability.
- **Its limits.** A declaration can be false, so admission compares declared effects with observed ones (at tool-call level on agent-core today), and certification tests the capsule against its own declaration (predicate parity). Passing a precondition grants no right to any effect.

## Where declared and observed checking differ

**Five differences follow from checking a declaration first rather than watching outcomes.**

| | Observed (outcome-judged) | Declared (this schema) |
|---|---|---|
| First check | after runs used it | before any run uses it |
| Reference for "correct" | task success, quality from use | the author's declaration, tested |
| What cannot run | offered, then fails or is refused | removed by code before any model chooses; at most a one-line exclusion remains |
| A lenient judge | keeps bad capabilities with no sign | its audited error rate, once measured, is on the certificate; until then its verdicts do not count |
| A wrong output in AI4Research | becomes a claim; the frozen plan cannot swap the capsule | traced from the claim to the exact binding and hash |

*Table 5. Where the two approaches differ.*

- Evidence for each row: the first two, Beyond Task Completion (2604.00392 p5); the third, Don't Offer What Can't Be Done (2608.01050 p5); the fourth, The Blind Curator (2607.07436 Table 1, p6); the fifth, the run pin (SCHEMA B4).

# b. Architecture: how it is built

## One manifest, one hash, records that name it

**The author writes one manifest; its hash is computed; every decision about the capsule is a separate record that names that hash.**

![Figure 3. The schema. The manifest carries every field; its hash covers every file; the records around it name the hash.](figures/schema.png)

- **Why records sit outside.** A record cannot contain its own hash, and keeping or retiring a capsule must never change the capsule.
- **Who applies them.** The capsule layer's **store** keeps manifests and files by hash; the **importer** turns existing tools into provisional capsules; the **admission rule** writes certificates from the verifier's results; the **provider** lists available capsules for Symphony; the **librarian** writes availability events.

## The records around the manifest, and who writes each

**Eight records sit outside the manifest. Each has one writer and named readers, and a field no reader uses is removed.**

| Record | Holds | Written by, read by |
|---|---|---|
| Certificate | level met, a verdict per check (satisfied, violated, unknown), observed effects, precondition parity, the verifier's audited error rates, models covered, nearest capsules, decision | admission rule; planner, librarian, routing |
| Availability event | what runs may use (active, admitted inactive, outside the cap, retired, revoked, local waiver, private) and a typed reason | librarian; planner |
| Verifier audit | false-pass and false-fail rates per anchor kind | verification; admission rule |
| Run pin | per step: offered, blocked, chosen or none, exact hashes, model, attempts, gate verdicts, exits, outcome, cost, selection tokens; and which claims each binding produced | the run; everyone |
| Candidate package | a manifest, body, tests from another author, how much of the tests the builder saw | RSI or a person; admission rule |
| Gap record | what planning needed and could not bind after repair, counted over distinct runs | planner; RSI |
| Plan step | what each node of the frozen plan requires, and its typed ports | planner; the run |
| Composition report | a set of capsules that shared a context, what a screener found, whether execution confirmed it | a screening tool; planner, librarian |

*Table 6. The records around the manifest.*

## Two levels: every capsule is tested, some are certified

**Nothing is admitted untested. Provisional means it loads, stays within its declared effects and passes a postcondition; certified means every output is tested by someone who never saw the code.**

![Figure 4. Admission and availability. A candidate passes provisional tests, then may pass certified tests. Admission makes it active or keeps it inactive until it improves on what it replaces.](figures/lifecycle.png)

- **Availability.** A new revision activates only if it improves on the baseline (When Self-Evolution Backfires gates on marginal gain over the pool, 2608.05810 p5-6), or, where no contribution is measured, passes every check its predecessor passed (*design*); otherwise it stays inactive. Retired is never deleted. Revocation blocks new runs and taints running outputs and the claims built on them.
- **New work.** Today's AI4Research freeze admits only `stable` capsules (*code* `execution_authority.py:55-56`), so provisional admission is new.

| Level | Tested before admission | Offered to |
|---|---|---|
| Provisional | manifest valid, file hashes match, binding loads, a smoke run stays within declared effects, one postcondition passes on inputs it was not built from | only steps that accept provisional capsules, because they check outputs downstream |
| Certified | every output covered by an anchored postcondition; tests from an author who never saw the implementation, the builder seeing at most pass or fail; an audited judge under the false-pass ceiling; precondition parity | every step |

*Table 7. The two levels.*

- **Why two.** The evidence draws one line: between a capability whose own job was tested thoroughly and one that merely ran (Beyond Task Completion, 2604.00392 p5). The split itself is *design*.
- **Why blind tests.** Hacking was more frequent when the checked functions were visible (Darwin Gödel Machine, 2505.22954 p70), so certification needs a sealed suite or pass-and-fail bits only.

## Predicate parity: one predicate, three evaluators

**A precondition is declared once, as data. The planner's filter and the dispatch check evaluate that same declaration, and certification tests that the capsule's own exit logic agrees with it. The filter never uses a separate heuristic.**

![Figure 5. Predicate parity. One declaration feeds three evaluators. The filter and dispatch share one evaluator by construction (invariant 8); the capsule body is tested against the declaration at certification, at the boundary and with missing and stale state, again on every new revision.](figures/parity.png)

- **Where the idea comes from.** *Don't Offer What Can't Be Done* (Wix, 2608.01050) gates skills by evaluating each skill's own exit conditions. Because gate and skill evaluate the same predicate, a blocked skill could not have completed: sound by construction, but only while **predicate parity** holds and both read fresh state (p2-3). One-sided: passing does not promise success.
- **Why not a heuristic.** In Contract2Tool (2606.07904 Table V, p8), a keyword top-5 filter cut tokens from 26,172 to 4,482 a task but success fell from 0.775 to 0.620; filtering on preconditions and effects exposed one tool, used 2,528 tokens, and succeeded 0.980 of the time (synthetic 100-tool registry, 102 tasks, mocked execution).
- **When state can be read.** The paper's gate reads account state when a message arrives. A frozen plan binds steps before upstream outputs exist, so each precondition says whether it is `evaluable_at: planning` (a credential, an installed tool, a reachable service, a licence, remaining budget) or only at dispatch (anything an upstream step produces). The filter uses only the first kind; dispatch checks all.
- **Today's gap.** AI4Research's candidate filter uses its own compatibility logic and never reads preconditions (*code* `elastic_planner.py:4553-4648`), while dispatch checks four fixed kinds against the task envelope (*code* `capability_capsules.py:1220-1242`): two predicate sets, so no parity.

## Parity rules, and the paper's three failure modes

**Eight rules keep the declaration and the capsule in agreement, and each failure mode the paper names leaves a record.**

| Rule | Why |
|---|---|
| A precondition is a check {path, operator, value} over declared state, with a `state_source`; intent is never a precondition | code can evaluate it; ambiguous intent stays a model's call (2608.01050 p3) |
| Filter and dispatch run one evaluator over one declaration (inv 8); types, effects and level come from the same declared fields | no second predicate set to drift |
| Only preconditions `evaluable_at: planning` enter the filter, and only after their parity test passes; the rest wait for dispatch | an untested or not-yet-readable predicate never hides a capsule |
| Certification tests the body at each boundary, with state missing and stale | the paper's parity regression fixtures (p5 §6.1) |
| Any change to exit logic or a precondition is a new revision and repeats the tests | parity is a release invariant, not a one-time property (p6) |
| `on_unavailable` says what happens when a readable state source fails; block by default, `pass` only with a reason | the policy must be explicit and tested (p5 §6.2); the default is *design* |
| A body that stops on a declared precondition reports its id | the run pin can compare the gate with what the body did |
| Passing preconditions grants no right to any effect | hiding what cannot run narrows what a model can be talked into, but is not access control (p2) |

*Table 8. Parity rules.*

| Failure mode (2608.01050 p5) | Signal | Record |
|---|---|---|
| predicate drift: gate and body disagree | body exits on a precondition dispatch passed, or a parity test fails | run pin `exit`; certificate; `revalidation_pending` |
| state staleness | filter passed, dispatch blocks | run pin `blocked[]` with its `state_source` |
| backend-contract drift | a dependency's contract fails | `dependency_contract_violated` |

*Table 9. The paper's three failure modes, as records.*

## Existing tools, skills, MCP and A2A enter as provisional

**Nothing is rewritten to enter. An importer fills every field it can derive and invents no guarantee; a person confirms the effects and writes one postcondition; the capsule enters as provisional.**

| Source | Derived automatically | Written to certify | Loads as |
|---|---|---|---|
| agent-core `ToolCard` (*code* `base.py:78`) | name, description, inputs, idempotent, parallel-safe and exposure flags, file hashes if local | outputs, postconditions | tool |
| MCP server (public specification) | each tool's name, description and schemas; effect proposals from its read-only, destructive, idempotent and open-world hints | postconditions | whole server |
| `SKILL.md` skill, jiuwenswarm or skillhub (*code*) | name, description, a hash per file, the skillhub version | inputs, outputs, postconditions | skill |
| A2A agent (public specification) | name, description, version, input and output modes, URL | typed inputs and outputs, postconditions | A2A client |
| old AI4Research manifest (*code*) | contract, effects; `invariants` and `pass_conditions` become postconditions | a suite from an author who never saw the code | from `operator_compatibility` |
| Symphony fingerprint, ScienceDiscovery package (*code*) | typed inputs and outputs, file hashes, revision | postconditions | as the source |

*Table 10. What an importer derives, and what an author adds.*

- A remote MCP server or A2A agent has no files to hash, so it is pinned by endpoint and version.
- agent-core loads a whole MCP server, so an MCP capsule is one server; `McpToolCard` has no field for MCP's hints, so the importer reads the server's own tool list (*code* `mcp/base.py:169-175`).
- Imported contracts are proposals: from documentation, preconditions were inferred perfectly (F1 1.00) but effects worst of any evidence source (0.77), and risk was the weakest field everywhere (at most 0.67) (Contract2Tool, 2606.07904 Table III, p7). Hence a person confirms the effects.

# c. Position: where it sits

## Where the schema is read in an AI4Research run

**A capsule touches a run at four points: selection at planning, pinning at the freeze, checks at dispatch, and claims at delivery. Admission runs any time and changes only what the next run sees.**

![Figure 6. Where each part of the schema is read. Top: one sprint. Bottom: admission, any time.](figures/fits-slide.png)

- **Top row, a sprint.** The filter on declared fields, a model binds each step and a second reviews the fit, the freeze pins exact hashes, and agent-core runs them while in-run gates judge the outputs.
- **Bottom row, any time.** A gap after repair goes to RSI, the verifier checks the build, the admission rule decides, and availability changes only the next run's candidates.

| Pipeline stage | What the schema supplies or records |
|---|---|
| intake, intent, requirement compilation | nothing: intent never sees capabilities |
| planning | the filter on declared types, effects, preconditions and level; a model binds each step reading name, description and level; a second model reviews the fit, within bounded repair; after repair, one gap record to RSI |
| freeze | the plan, its evaluation plan, each binding's hash and certificate, and the model candidates, in the run pin |
| scheduling and dispatch | each binding's live hash must equal its pin (new); preconditions re-evaluated on fresh state; credentials and service health observed, never frozen; routing picks among the frozen model candidates |
| operators and in-run gates | effects observed at tool-call level; gate verdicts, attempts, outputs and exits recorded per binding |
| delivery of claims | each claim records its binding, so a revoked capsule taints exactly its claims |

*Table 11. The schema at each stage of the AI4Research workflow.*

- **Kept from today** (*code*): the three-step selection (`elastic_planner.py:4553-4648`, `:4727`, `:5685`), the gap after bounded repair (`:4100-4152`), and the freeze's rejection of capsules changed during planning (`execution_authority.py:81-94`).
- **Verification at each sprint.** A system-level failure names a step, and the run pin turns it into the exact capsule versions to revalidate.

## Plan steps and dependencies, today and in the schema

**Both AI4Research and Symphony already give plan steps requirements. The schema keeps what they do and replaces inference with declaration.**

| | Today (*code*) | In the schema |
|---|---|---|
| Step inputs | typed; Symphony's `unknown` matches any input of the same name (`input_matching.py:23-33`) | exact types from one versioned vocabulary; `unknown` only for steps accepting provisional capsules |
| Edges between steps | AI4Research `depends_on` step ids; Symphony edges a model proposes at confidence ≥ 0.7 | declared ports, output to input |
| Preconditions | AI4Research: four kinds at dispatch, never in the filter; Symphony: none | one declared predicate, filter and dispatch (predicate parity) |
| What a capability depends on | AI4Research pins guard and resource capsules at the freeze, resolves MCP providers live | every dependency pinned, or floating with declared contracts |
| A capsule changes | rejected if changed during planning, then frozen copies run | kept, plus a hash check at dispatch |
| A step fails | descendants blocked, reopened on recovery (`graph_scheduler.py:3999-4055`) | kept; a changed upstream output also marks downstream bindings stale |
| Unmet requirement | AI4Research: bounded re-planning, then failure; Symphony: `needs_input` | typed: needs input, no capsule fits (gap record), cannot load, state unknown |

*Table 12. Node requirements and dependencies.*

## How the schema plugs into agent-core and Symphony

**The capsule layer is new and sits beside Symphony on agent-core. It uses hooks that already exist: Symphony's capability provider and graph updater, and agent-core's binder, tool-call rail and trajectory store.**

![Figure 7. Integration. Left: imports and the capsule layer. Right: agent-core, with Symphony's graph and planner and the harness. Arrows are existing interfaces; RSI, the verifier and routing are tools the scheme uses.](figures/integration.png)

- **Two planners, two filter points.** AI4Research's planner binds typed plan steps, so the filter runs per step. Symphony's fast planner plans and picks skills in one call from id, name and description, and handles I/O compatibility after the plan (`fast.py:32-44`); there the filter runs per query, on the candidate ids it is given (`fast.py:85`). Which planner binds is a question for the room.
- **Scope of Symphony.** Its graph accepts only skill, subagent and agent capabilities (`orchestration/graph/build.py:161`), so tool, MCP and A2A capsules reach a run through the capsule layer's filter and the binder, not through Symphony's graph.
- **What changes in Symphony.** Declared ports would replace edges a model proposes at confidence 0.7 or more (`orchestration/graph/build.py:122`).
- **What changes in agent-core.** Effect-level observation is the one likely change; the supervisor allows changes only where necessary.

## The hooks exist, and what each still needs

**Every connection starts from an interface agent-core already has. Each also has a gap, checked in source, that the capsule layer's own code fills.**

| Schema part | Existing hook (*code*, agent-core `e23806c1`) | What the capsule layer writes, and the gap |
|---|---|---|
| What planning may see | `CapabilityProvider` (`interfaces/capability.py:13`), read by Symphony's fingerprint service and orchestration; its `CapabilityDescriptor` has `available`, `content_hash` and `metadata` | a provider listing only available skill, subagent and agent capsules, with hash and level; `AtomicCapabilityProvider`, since batch graph mutation requires it (`mutations.py:167`). Gap: the graph takes no other kinds (`build.py:161`) |
| After each availability change | `SkillGraphUpdater.add_skills`, `update_skills`, `delete_skills` (`interfaces/graph.py:14`) | one call per activation, supersession or retirement. Gap: ids are keyed as skills (`mutations.py:396`), the graph holds one revision per `capability_id`, so a supersession is an update, and every mutation calls a model for ontology matching (`mutation_service.py:129`) |
| Manifest model | `CapabilityIO`, `SymphonyModel` (`models/capability.py:15`), `ToolCard` (`tool/base.py:78`) | a manifest model reusing `CapabilityIO` |
| Loading by hash | `apply_extension_hot` (`extension_binder.py:27`), paths for tools, MCP servers, skills and subagents | load only a hash whose certificate is valid. Gap: the binder loads by name and raises if the name is bound (`extension_binder.py:33-36`), with no hash check, so the capsule layer checks the hash and loads from the content-addressed store, whose paths cannot change |
| Observed effects | `before_tool_call` (`rail.py:888`) | tool calls compared with declared effects. Gap: for a skill, subagent or agent capsule its tool calls are its effects; a tool capsule's own internals are invisible (H5) |
| Run pin | `LoadRecord.refs` (`extension_resolver.py:60`), `TrajectoryStore` (`trajectory/store.py:23`) | each binding saved with the trajectory. Gap: load records live in memory (`deep_agent.py:314`); a new capsule-layer rail writes the pin to the store |
| Unmet input | Symphony's `needs_input` (`plan_builder.py:53`) | kept, beside typed `unsatisfiable_capsule`, `unsatisfiable_binding`, `precondition_unknown` |

*Table 13. Connection points. Paths are under `openjiuwen/symphony/` (interfaces, models, orchestration), `openjiuwen/harness/`, `openjiuwen/core/foundation/` and `openjiuwen/agent_evolving/` in agent-core.*

# d. Dependencies

## What the schema needs from the system and each teammate

**Each dependency is a record both sides agree on; nothing in it says how the other side does its work.**

![Figure 8. What the capsule layer gives each neighbour, and what it needs back.](figures/deps.png)

| On | The capsule layer needs | It gives back |
|---|---|---|
| agent-core | loading through its binder, tool-call spans, the trajectory store | manifests with a binding and declared effects; only admitted hashes to load |
| Symphony | its planner fed by a provider, its graph updated on each change | available capsules, a snapshot id per run, declared ports |
| skillhub, ScienceDiscovery, jiuwenswarm | import sources; ScienceDiscovery's content-addressed store as the pattern | nothing they must change |
| Saurav, RSI | candidate packages with tests from another author and how much of them the builder saw; repairs when a contract breaks; never a direct write | gap records counted over runs; evidence tied to exact versions; a say in retirements it proposes |
| Ramika, verification | a verdict per check against the exact hash; audited error rates; sprint-level failures naming the step | the postconditions and preconditions to test; run pins to trace failures |
| Xiaoyang, routing | a model chosen among the frozen candidates, recorded in the run pin | the models each capsule's evidence covers |
| a composition screener, such as SkillFuzz (owner to be decided) | composition reports on risky combinations | the declared contracts of capsules that share a context |

*Table 14. What each side provides.*

- **Verification at three levels.** Capability level at admission (certificate), system level at each sprint (a failure names a step), and the verifier itself (its audit).
- **Order.** RSI and verification are staffed for four months, so the candidate package and the verdict format are settled first.
- **agent-core** fully provides one of the five platform properties the design needs (backup, H1-H5).

## If a dependency is not there yet

**Each missing piece lowers what can be certified, never what is checked, so M1 needs nothing outside this team.**

| Missing | What happens meanwhile |
|---|---|
| candidate packages from RSI | capsules come only from the importer, as provisional |
| a verifier audit | judged verdicts are advisory; only deterministic and reference-anchored checks count |
| effect-level observation | code-heavy capsules stay provisional; capsules that act only through tool calls can certify |
| a model outside the frozen candidates | a step that accepts provisional capsules may run it, recorded in the run pin, and the capsule goes to `revalidation_pending`; any other step is blocked |
| an owner for the type vocabulary | the capsule layer seeds it from Symphony's |

*Table 15. Working before every neighbour is ready.*

# e. Similar designs

## Others watch a capability, this schema declares it

**Every system checks something. They differ in where the reference for "correct" comes from, and here it is the author's declaration, tested before anything is kept.**

| System | Reference for "correct" | Kind | How this schema differs |
|---|---|---|---|
| Alita-G, Darwin Gödel Machine | the task outcome | observed | tests the capability's own declared job |
| Symphony fingerprint (*code*) | quality accumulated from use | observed | checks before any run uses it |
| The Blind Curator's curator | a judge's scores over rounds | observed | records and caps the judge's audited error |
| Skill Drift Is Contract Violation, Contract2Tool | contracts inferred from documentation and traces | inferred | the author declares them; admission tests them |
| skillhub review, ScienceDiscovery publish (*code*) | a person or a policy | reviewed | a verdict per declared postcondition, bound to the hash |
| RelAIBuild | a pinned spec; file scope checked after the edit lands | declared, detected after | also gates selection, before use |
| Don't Offer What Can't Be Done | each skill's own exit conditions | declared, at selection | the same idea, extended to admission, dispatch and the library |
| MCP listings, `SKILL.md`, A2A cards | a name, description and input schema, unchecked | declared, unchecked | declares conditions and effects, and checks them |
| GraSP, Agent Behavioral Contracts | precondition and effect edges, or preconditions as runtime checks | declared, checked at plan or run time | also ties the declaration to admission, selection and the run pin |
| lockfiles, Sigstore, SLSA | a hash or signature of who built what | provenance | proves what it does, not only who built it |

*Table 16. Where each approach gets its reference.*

- Declared contracts exist elsewhere: GraSP (2604.17870) declares precondition and effect edges, Agent Behavioral Contracts (2602.22302) declares preconditions as checks. None of the systems read ties one declaration to admission, selection and dispatch, bound by hash to what a run pins.
- Why declared and tested is the stronger reference: observation finds a fault only after runs used the capability, inference guesses at contracts (Contract2Tool's documentation-derived effects scored 0.77), and review checks a person's reading, not the behaviour. A tested declaration is checked first, by code, against the capability's own behaviour.

# f. Advantages

## Five advantages, each with what would prove it wrong

**Each advantage is stated with the result that would disprove it, so the workshop can hold the design to it.**

| Advantage | Evidence | Proved wrong if |
|---|---|---|
| **Safer selection.** What cannot run is removed by code before a model chooses, and the guarantee is by construction | 7.8% blocked-skill picks without a gate (2608.01050 p5) | a capsule passes the filter and dispatch, then exits on that same declared precondition (a parity failure), or parity tests find a false block |
| **Fewer tokens at selection.** A removed capsule's full catalog row shrinks to an exclusion line, on every repair too | 59.1% fewer description tokens after relevance matching (2608.01050 p5); 26,172 to 2,528 tokens a task (2606.07904 p8) | M2 shows no drop in `selection_tokens` against today's filter, at equal task success |
| **A kept capability's own job is tested** | 215 of 222 tools failed theirs (2604.00392 p5) | a certified capsule fails a held-out test of its declared job |
| **A lenient verifier becomes visible** | biased retirement stopped silently (2607.07436 p6) | quality retirements stop while evictions continue, and no audit is triggered |
| **Every claim traces to exact capsules; imports need no rewrite** | the run pin; Table 10 | a claim cannot be traced to a binding and hash, or an import needs code changes |

*Table 17. The advantages, each falsifiable.*

## Code removes what cannot run before a model chooses

**Every capsule the filter removes is one no model can pick, and its full description shrinks to a one-line exclusion. That is safer, because what cannot run is never offered, and cheaper, because each selection call reads less.**

![Figure 9. Selection for one plan step. Code removes what cannot run; a model binds among the rest and a second reviews the fit; the freeze pins the result. If none fits after repair, a gap record goes to RSI.](figures/funnel.png)

- **Safety.** Without the gate, a model picked a skill that could not run in 7.8% of 1,000 risk-enriched conversations (2608.01050 p5). Hiding what cannot run also narrows what a model can be talked into, but does not replace access control (p2).
- **Choice.** Pass rate fell from 0.49 with the right skills alone to 0.28 with a 202-skill library, and 38.5% of trajectories then invoked no skill, against 12.0% (More Skills, Worse Agents?, 2605.24050 Fig. 1 p3, Table 2 p9; Haiku drove the abandonment). A filter removes what cannot run; it cannot fix abandonment on its own.

## Tokens: what the papers measured, and what carries over

**Removing what cannot run shrinks the context every selection call reads. The papers measured the size of that effect; AI4Research's planner shows the mechanism applies; M2 measures how much it saves here.**

| Source | What was measured | Caveat | What carries over to AI4Research |
|---|---|---|---|
| Don't Offer What Can't Be Done (2608.01050 p1, p4-5) | the gate removed 59.1% of skill-description tokens after relevance matching; with matching, 90.5% fewer than exposing all ten skills | ten skills, one month; description tokens, not billed cost or latency | the mechanism: a removed capsule is never offered, and its full catalog row shrinks to an exclusion line |
| Contract2Tool (2606.07904 Table V, p8) | all 100 tools: 26,172 tokens a task at 0.775 success; keyword top-5: 4,482 at 0.620; contract filter: 2,528 at 0.980 | synthetic registry, mocked execution | a heuristic filter can cost success; this filter reads declared contracts (inv 8) |
| AI4Research today (*code*) | the binding prompt carries every eligible candidate's full catalog row, and again on its one repair; a removed capsule appears only as a short exclusion row (`elastic_planner.py:4600-4650`, `:4678-4724`, `:4949`) | today's filter already removes on types, effects and proof classes | the added saving: a full row becomes an exclusion row, for each capsule only a precondition removes |
| Symphony today (*code*) | its planner reads each candidate's id, name and description, and leaves I/O compatibility until after the plan (`fast.py:32-44`) | | the declared filter moves those checks before the model |

*Table 18. Token savings: measured, and carried over.*

- **Not claimed:** a number for AI4Research. The catalog holds 46 capsules today, and the prompt also carries the requirement, upstream artifacts and plan, so the share may be small now and grows with the library. M2 measures it against today's filter, from the run pin's `offered[]`, `blocked[]` and `selection_tokens`, with false blocks and task success beside it, because over-blocking also lowers tokens.

## What the schema does not claim

**Four limits, stated so the design is held to what it offers and no more.**

- **Fixing degradation at scale.** Much of it is the agent using no skill at all, which a filter cannot fix (2605.24050 Table 2).
- **Identical replays.** A model behind an API changes; runs are recoverable, not byte-identical.
- **Safe combinations.** Severe drift rose from 4.7% to 66.5% of plans as loaded skills went from one to five (2607.02345 Fig. 6), and every gate judges one capsule at a time. What the schema offers instead is screening: it supplies a screener's contracts and records what the screener finds (B7).
- **Task success.** Passing the filter means no declared exit holds, not that the capsule will succeed or that it was the right choice.

# g. Feasibility

## Every part exists somewhere, the work is combining them

**Each part downstream of the schema has been built, in openJiuwen, AI4Research or a paper; no one has combined them. Capability Capsule touches every team's work, so who owns each part is for the room to decide together; this section gives the parts and an order, not a division of labour.**

| Part | Already in openJiuwen or AI4Research (*code*) | Already built in a paper |
|---|---|---|
| store, per-run pinning | ScienceDiscovery's content-addressed store | step identities by hash (Execution lineage, 2605.06365) |
| loading, observing | agent-core's binder and tool-call spans | not needed |
| filter, binding, fit review | AI4Research's planner | executability gate in production (Don't Offer, 2608.01050) |
| held-out tests | `program_opt` admits a candidate by held-out execution | a conformance suite per capability, replayed after the run (Beyond Task Completion, 2604.00392) |
| verifier apart from builder | skillhub review | a separate verifier session (CoEvoSkills, 2604.01687) |
| measuring the verifier, typed verdicts | not yet | The Blind Curator; Cognitive Admission Control (2609.16313) |
| gate before commit, archive | ScienceDiscovery publish and rollback | When Self-Evolution Backfires; Darwin Gödel Machine |
| retirement under a cap, drift repair | not yet | Library Drift; Skill Drift Is Contract Violation |

*Table 19. Each part, and where it has been built.*

## Five milestones, provisional first

**An order to discuss, not a plan of record: each milestone is usable on its own, and M1 needs nothing outside this team. Risks and the four-arm test are in the backups.**

![Figure 10. Milestones, provisional first.](figures/milestones.png)

| Milestone | What exists at the end | Needs | Measured by |
|---|---|---|---|
| M1 | manifest, store, importer, run pin, provisional admission with a smoke run at tool-call level | nothing outside this team | imports admitted without a rewrite; complete run pins |
| M2 | planning-evaluable preconditions in the filter, each after its parity test | M1 | blocked-selection rate, false blocks, `selection_tokens` and task success, against today's filter |
| M3 | certification: blind suites, parity tests, the verifier audit | M1, a verdict format, a sandbox for code-heavy capsules | held-out failures among certified capsules |
| M4 | availability events, gap records, the cap, the librarian | M3, the candidate package format | retirements by reason; curator health |
| M5 | agents as composites, first a gate | M4 | composites admitted with pinned children |

*Table 20. Milestones.*

- **M1 is small.** Identity, binding, inputs and outputs, effects, preconditions, one postcondition, file hashes; a provisional certificate; the run pin. The other fields wait for the milestone that reads them.

# Questions for the workshop

## Questions for the room, each with a default

**These decisions belong with other components. Each has a default, so none blocks M1.**

| Question | With | Default |
|---|---|---|
| Who owns the model that binds capsules at planning? | planner owners | Symphony's planner, fed by the capsule layer's provider, with the declared filter in code first |
| Who owns the type and state vocabulary? | Symphony | the capsule layer, seeded from Symphony's |
| Fail open or closed when state cannot be read? | each capsule author | closed (block), stated per precondition |
| What false-pass ceiling counts toward certification? | verification | 0.05 until measured |
| Who owns the observing sandbox? | verification, agent-core | the capsule layer, on agent-core's tool-call hooks |
| What does a sprint-level failure send? | verification | the run and step, traced through the run pin |
| What counts as a different author for tests? | RSI, verification | a separate session with no access to the implementation |
| How are model candidates expressed? | routing | pinned model ids with versions, widened only with re-verification |
| Who acts as librarian, and who owns Ground Truth? | all, supervisor | capsule-layer code, with a named person for revocations; verification curates reference answers as pinned data |

*Table 21. Questions for the workshop.*

# Backups

## Eight invariants hold whatever the specification becomes

1. The contract is the only interface.
2. The library is append-only. A better version is a new revision.
3. A run sees only the versions it started with.
4. Whatever decides never builds, and nothing may change the gate or the verifier.
5. A capsule is certified only on tests from an author who never saw its implementation.
6. Every write, execute and network effect is declared with how it is undone, or as irreversible.
7. Admission has a threshold, and this team owns it.
8. Whether a capsule is eligible, at planning and at dispatch, is decided only by its declared predicates, through one evaluator, never by a separate heuristic. Choosing among eligible capsules is a model's call.

- Rule 4: in a 3-task side experiment a Darwin Gödel Machine node removed the logging its hidden checker read (2505.22954 p70). The gate and the verifier are never capsules.
- Rule 8: predicate parity (slides 12 and 13).

## Every manifest field, and its reason

| Field | Required for | Why it is there |
|---|---|---|
| `schema_version`, `capability_id`, `capability_type`, `name`, `revision`, `version` | all | read under its own schema; a stable id; the kind the binder loads by; a new revision for every change (inv 2) |
| `description` | all | the model that binds reads name and description, so that text is admitted (2605.24050 p4, by definition) |
| `binding` | all | tool, MCP server, skill or subagent through the binder; A2A through its client; `ToolCard`'s flags. Workflows and teams have no path, so are not admissible in v1 |
| `inputs`, `outputs` | all; complete when certified | exact types, in Symphony's `CapabilityIO` shape |
| `effects` | all | read, write, execute, network, cost, risk; each with a scope and how it is undone, or irreversible (inv 6); no scope may include the verifier's inputs |
| `preconditions` | all; empty only with a stated reason | one declared predicate for filter, dispatch and parity tests (inv 8) |
| `postconditions` | all: one when provisional, every output when certified | tests of the capsule's own job, anchored deterministic, reference or judged; checks and judges are complementary (2607.07436 Fig. 2) |
| `unanchored` | certified | aspects no postcondition covers; a step can refuse capsules with any |
| `dependencies` | all | pinned by hash, model id and version, service endpoint and version, or capsule hash; a secret needs a guard; never the verifier |
| `load_mode` | all | context-injected or invoked behind a boundary (*design*), because severe drift rose with the number of skills loaded into one context (2607.02345 p9) |
| `components` | all | a hash per file; AI4Research hashes only the manifest file (*code* `execution_authority.py:40`) |
| `lineage` | all | supersedes, specialises, rollback_of |
| `budget`, `children` | agents | limits between calls (2601.08815 p12-14); the exact capsules a composite contains (inv 3) |

*Table 22. Manifest fields.*

## Strict by default, flexible by declaration

| Dependency declared as | What follows |
|---|---|
| no role | pinned; any change is a new revision |
| floating, with a role and contracts | may move; the capsule stays provisional; admission checks each contract once |
| contract violated | `dependency_contract_violated` to RSI, naming the broken assumption |

*Table 23. Floating dependencies, after v1.*

- Role-bearing checks gave no false alarms over 599 cases, against 40% for contract-free probes; recall ranged 24% to 76% across five backbones (Skill Drift Is Contract Violation, 2605.10990 p4, p7; single runs).

## What the schema gives the librarian

| Job | What the schema gives |
|---|---|
| Admit | a verdict per check; for a deferral, the evidence it waits for |
| Keep the active set small | revisions activate only on improvement; cap evictions record the cap and value lost |
| Retire | trials, threshold and contribution, tied to the verifier's audit |
| Watch the verifier | quality retirements against cap evictions: the pattern a lenient judge produced triggers an audit (*design*, after 2607.07436 p6) |
| Watch parity | block rate per capsule and precondition; gate-versus-exit disagreements |
| Merge, replace, revoke, fill gaps | nearest capsules; successors; taint down to claims; certificate expiry; unanswered gaps |

*Table 24. The librarian's jobs.*

## agent-core fully provides one of five needed properties

| | Needed | What agent-core has |
|---|---|---|
| H1 | reversible registration | yes: hot apply and unapply, undone in reverse order |
| H2 | dependency tracking | no; the capsule layer closes capsule dependencies at bind |
| H3 | immutable versioned artifacts | for graph artifacts only, so the store is new |
| H4 | a reconstructable execution log | an append-only trajectory archive, once wired |
| H5 | a record of what ran | tool calls only, not what code does inside |

*Table 25. agent-core, checked in source.*

## openJiuwen schemas each hold part of this one

| Schema | Has | Lacks |
|---|---|---|
| agent-core `ToolCard` | identity, inputs, exposure, parallel-safe, stateless and idempotent flags | outputs, postconditions, hashes, versions |
| Symphony `CapabilityDescriptor` and fingerprint | typed inputs and outputs, `content_hash`, `available` | preconditions, effects, admission |
| skillhub review | a review per version, a policy version, a zip hash | a contract; a version can be force-overwritten |
| ScienceDiscovery library | per-file hashes, revisions, skills pinned per run | postconditions, effects, an audited verifier |

*Table 26. openJiuwen schemas, read in source.*

## Admission checks, each run by a tool

| Check | Level |
|---|---|
| manifest valid, file hashes match, binding loads | both |
| smoke run within declared effects, at tool-call level | both |
| one postcondition passes on inputs it was not built from | provisional |
| every output covered; tests from an author who never saw the code | certified |
| precondition parity: boundary, missing and stale state | certified |
| model judgment | counts only under the false-pass ceiling |
| an `unknown` verdict | defers with a typed evidence request; only a violated check rejects (2609.16313 p5) |

*Table 27. Every check is run by a tool; the capsule layer owns the threshold.*

## The supervisor's components, mapped onto the schema

| Supervisor's component (18 September) | Where it lives here |
|---|---|
| Rules, Boundary, Interfaces | preconditions, effects, typed inputs and outputs |
| Skills | the body |
| Governance | lineage, certificates, availability events |
| Eval | the certificate references the tests; the gate stays outside |
| Assets, Data | declared as dependencies, not carried inside |
| Ground Truth | proposed: reference answers pinned as data, curated by verification |

*Table 28. The supervisor's slides of 18 September, mapped.*

## Risks, each with its answer

**Six risks, each with the design answer that keeps it contained.**

| Risk | Answer |
|---|---|
| effects are observed only at tool-call level | code-heavy capsules stay provisional until a sandbox observes effects; tool-only capsules certify now |
| provisional admission changes today's freeze, which admits only `stable` | provisional capsules bind only to steps that accept them, so other steps see no change |
| declared ports change how Symphony builds its graph | ports are added beside today's proposed edges first, and replace them only once M2 shows no loss |
| parity needs capsules to report which precondition stopped them | required before a precondition enters the filter; without it the precondition is checked at dispatch only |
| declarations are gamed or under-declared | certified needs another author's suite; `[]` preconditions and `on_unavailable: pass` need stated reasons; observed effects are compared with declared ones |
| over-blocking starves steps and floods RSI with gaps | M2 reports false blocks and task success beside tokens; parity tests find false blocks; gap records count distinct runs, not repair attempts |

*Table 29. Risks and answers.*

- **Cost.** More work per capability, latency at selection and dispatch, and some rejections a person would accept. Provisional imports and floating dependencies keep it down.

## The test that decides whether the combination works

**Each paper shows a part works in its own setting, not that the whole works here. Only a comparison on AI4Research's own tasks, against curation by observation, can show that.**

| Arm | Library | Prediction |
|---|---|---|
| 1 | no library | the baseline |
| 2 | a library built without admission | more kept capsules fail their own job, and more that cannot run are offered |
| 3 | the same library curated by observation: a judge retires capsules by outcome | the comparison the design must beat, not only no curation |
| 4 | the same library under this schema: admission, the declared filter, availability | fewer kept capsules fail their own job, fewer that cannot run are offered, fewer selection tokens, and task success no lower than arm 3 |

*Table 30. The four-arm test.*

- Same tasks, same models, same budget. Ground Truth reference answers, curated by verification, pinned as data dependencies.
- An ablation of arm 4 with the filter alone separates what admission adds from what the filter adds.

# Appendix: figures from the papers

Each figure is cropped from the paper's own PDF by `figures/extract_paper_figs.py`, with its page and caveat.

![Figure A1. Don't Offer What Can't Be Done (2608.01050), Fig. 1, p4: the three-stage pipeline. Only stage 2, a deterministic gate on each skill's own exit conditions, removes candidates.](figures/papers/dont-offer-pipeline.png)

![Figure A2. Don't Offer What Can't Be Done (2608.01050), Fig. 2, p4: skill-description tokens. The gate removes 59.1% after semantic matching, 90.5% combined. Ten skills, one month; description tokens only.](figures/papers/dont-offer-tokens.png)

![Figure A3. Contract2Tool (2606.07904), Table V, p8: a keyword top-5 filter cuts tokens but lowers success; contract-based filtering (CMTF) exposes one tool, cuts tokens tenfold and raises success. Synthetic registry, mocked execution.](figures/papers/contract2tool-exposure.png)

![Figure A4. More Skills, Worse Agents? (2605.24050), Fig. 1, p3: pass rate falls as the library grows from the oracle skills to 202. Human-authored skills; 38 task-model pairs.](figures/papers/more-skills-drop.png)

![Figure A5. The Blind Curator (2607.07436), Fig. 2, p5: deterministic checks and an LLM judge catch different defects. One domain; flag rates, not scores.](figures/papers/blind-curator-qc-vs-judge.png)

![Figure A6. When Self-Evolution Backfires (2608.05810), Fig. 4, p7: rollback after the fact recovers little; removing the source skills recovers 1.7 of 12.3 points, and the pool gated before commit (VaG) ends at 72.0%. One run.](figures/papers/backfires-contamination.png)

![Figure A7. SkillFuzz (2607.02345), Fig. 6, p9: severe drift rises with the number of co-activated skills, from 4.7% to 66.5%.](figures/papers/skillfuzz-depth.png)
