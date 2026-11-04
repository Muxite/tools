**Muk's directives for Capability Capsule, binding on every version.** Recorded 2026-09-22. Newest first. When a
document disagrees with this note, this note wins.

## 2026-09-30, later still: Model Routing PRD scope resolved; authoring.md must stay coder-current

- **Resolved:** the Model Routing PRD (4.3/"3.X") is about M1's own capsules, not the team's coding process — but only the ones that use a model (`skill`-kind). Tool capsules with no model call aren't routed. **CC describes each M1-required capsule's internal shape (as the per-capsule design pages already do) but does not prescribe how routing integrates into it** — that is the implementer's choice, same as the existing "models are not in the capsule layer" rule. No change needed to M05 or batch C's findings.
- **Standing commitment:** keep `capsule/authoring.md` "perfect and up to date," in line with what the coder actually needs to author a capsule. Check it whenever a batch touches capsule-authoring territory (M13 author kit is the most direct one, batch D).

## 2026-09-30, latest of all: read the whole connected PRD chain upfront, before designing any one module in it

- **Standing methodology change, after M08's redesign was found to have the baseline mechanism backwards.** Root cause: PRD 3.7 was read carefully for M08's own stage, but PRD 3.6 (upstream, whose output becomes M08's input) was not read first. The module's In list was designed from assumption, not from the adjacent stage's actual Whitelist text.
- **The rule now: before redesigning any module in a connected chain, read every PRD stage in that chain first, in one pass, tracing the data that actually flows between them** — not stage-by-stage, module-by-module, reactively. For the M02→M07c→M07d→M08→M20 chain (3.2, 3.5, 3.6, 3.7, 3.8), that means reading all five before touching any one of their module specs again.
- **This generalizes past this one chain.** Any module whose In comes from another module's Out needs that upstream module's own PRD sub-feature checked directly — "read the module's own stage" is necessary, not sufficient.

## 2026-09-30, latest still: design to fit the PRD, not just CC

- **Binding principle: the PRD is the ground truth; CC is the mechanism, not the goal.** When a module's spec is internally consistent with CC's own schema pages (Declaration fields, guards, policy) but doesn't deliver what the PRD's Whitelist literally asks for, that is not "done, minor gap" — it is not done. CC-schema consistency is necessary but never sufficient.
- **Why this is being said now:** the independent review's core finding was exactly this failure mode — batches A-E checked modules against CC's own pages, never against the PRD text, and called it "audited". M20's first draft repeated the same mistake at a smaller scale: it got excited that the gate fold mechanism (a CC-internal property) couldn't be tripped by a data value, without first checking whether the PRD's actual inputs (stdout/stderr, a baseline/treatment delta, a comparator) even existed anywhere upstream for it to work with.
- **How to apply going forward, starting with M08 and M07c:** derive a module's payload shape by reading the PRD stage's Whitelist line by line first, listing exactly what data it requires to exist, and only then fit that into CC's port/schema/Declaration conventions. Never start from "what's a clean CC schema" and hope it happens to satisfy the PRD — that ordering is what produced every gap this review found.

## 2026-09-30, latest: independent review, batch reorder, and the 3.8 deferral reversed

- **An independent agent (no inherited context from this session) reviewed the whole design against the PRD directly, not against CC's own schema pages.** Full report in [[HANDOFF]]. Headline: every module marked "audited" so far (M00a-c, M12, M10a, M04, M05, M13, M14) is CC's own infrastructure — nothing that actually maps to a PRD stage (M01, M07a-e, M08, M11) has been checked against the PRD text yet. One spot-checked claim (guards.md still has three un-prefixed agent-core citations at lines 370/374/379, contradicting the batch B "fixed" record) held up, so the rest of the report is being treated as credible.
- **Batch reorder, Muk's call: the PRD-bearing modules (M01, M07a-e, M08, M11) come next**, ahead of the original F-K build order. The CC-infrastructure modules (M10, M15-M19) wait.
- **The PRD 3.8 deferral (see the entry below, "a PRD feature is a gate") is reversed.** Its premise — "M09/M10 already have the data and the ability" — is false: M09 only ever sees one node's `evidence_bundle` and must never decide; M10 turns every `fail` into a halt, but PRD 3.8.5 requires a scientific `FAIL` to continue to Delivery as a valid outcome. As drawn, the pipeline actively contradicts the PRD it's built from, not just under-builds it. A new Scientific Evaluation module is now in scope, plus a fix to the gate's fold so a scientific verdict doesn't halt the run.

## 2026-09-30, later: build on existing structure; a PRD feature is a gate, not automatically a new module

- **Context:** the supervisor is pushing to oneshot the project codewise. Muk disagrees: capsules need more
  flexibility and testing first, and some structure has to be right before the rest is built on it.
- **The rule: prefer building on existing modules over authoring new ones.** When a PRD subsection looks like it
  names a new stage or component, check first whether an existing module already has the *data* and the *ability*
  to do it. If it does, the right move is usually to change what is switched on or prioritized in that existing
  module, not to write a new one. Minimize reauthoring; maximize reuse.
- **Applied to PRD 3.8 Scientific Evaluation:** no new module for now. `verifier_capsule` (M09) and the gate (M10)
  already have the data (the Stage Evidence Bundle, every Observation and Artifact) and the ability (a judge call,
  a check runner) that 3.8 needs. What 3.8 actually adds — a dedicated `Evaluation_Verdict.json`, the five-way
  verdict (`PASS`/`FAIL`/`INCONCLUSIVE`/`CONDITIONALLY_ACCEPTABLE`), a scientific `FAIL` routing to Delivery instead
  of halting — is a **prioritization and gating question**, not a missing-capability question. Leave it out of the
  build-order graph until it is prioritized; do not gate on it or build toward it yet.
- **How to apply this going forward in the M1 audit:** for every batch, before proposing a new module to cover a
  PRD subsection, check the existing modules' In/Out against it first. Log a "covered by existing structure, not
  yet gated" note instead of a new module wherever that holds.

## 2026-09-30: no destructive operation on docs/architecture or docs/tasks without a checkpoint and sign-off

- **Standing rule, after today's subagent incident** (an agent given explicit read-only instructions committed, pushed to shared `origin/ai4r_muk`, and deleted a file without checking inbound references; the file was recovered from a dangling git blob, not lost, but by luck). **No delete, force-push, reset, or broad `git add -A`/commit on `docs/architecture/` or `docs/tasks/` without a prior commit checkpoint on the affected file(s) and Muk's explicit sign-off.** A push to any shared remote is never automatic.
- **`m1-architecture.md` is repaired in place, not retired.** It is a near-complete draft (system graph, run graph, payload table, 19-module issue-ready spec, a build order that already sequences the Evaluator Gate as a prerequisite); it predates PRD section 3 and needs auditing against it, not discarding.
- **Code citations follow a stated policy** (`architecture.md`, "Code citations"): `path:line` at a named commit, never a branch; **[pin]** marks a citation read at a different commit than a dependency's declared pin; unverifiable claims go in Open, never asserted.

## 2026-09-29, late evening: M1 is designed in order, requirement_capsule first, then screening_capsule

- **Architecture guidance: design M1 in the PRD's order.** Section 3 of the M1 System PRD arrived (saved at jiuwenswarm `docs/product/prd-m1-section3.md`).
- **The first capsule to design is `requirement_capsule` (3.2), then `screening_capsule` (3.4).**
- **Why this order:**
  - RSI proves itself first on something easy (the Brief prompt and the defaults), then on something harder (the scoring rubric).
  - Both are model skills, so Model Routing gets real calls to route from the start.
- **`rank_opportunities` (3.4.7) is `screening_capsule`'s pinned pure helper,** with `evolution.rsi: none`: the PRD's arithmetic stays fixed while RSI tunes the rubric.
- **`compile_intent`** stays a built reference pure-tool capsule, which another person may take on.

## 2026-09-29, evening: compile_intent is the first capsule to build

- **`compile_intent` is the first "pure" capsule.** It is a `tool` with `effect_class: pure`, fixed rules and no model call. It represents the pure-tool wrapper: a capsule we hold in our own capsule location, reuse and test. Built at `capsules-build/compile_intent/`; documented in `capsule/example-compile-intent.md`.
- **Why first:** it is deterministic, so its tests are exact, and it unblocks RSI, which gets a real Declaration, code, checks and fixtures to mutate against.
- **The M1 design waits for the full PRD;** CC work continues meanwhile.

## 2026-09-29, later still: RSI is an allow-list

- **RSI applies only where the author explicitly allows it.** `evolution.frozen` (a deny-list) is replaced by `evolution.may_change`, the only parts RSI may change. Absent or empty means nothing, whatever `evolution.rsi` says. Entries are Declaration field paths (`[]` for every list item, `[<name>]` for one keyed item) or `files:<glob>`.
- **Rules.** `changes_allowed` replaces `frozen_kept`. The new `rsi_cannot_grant`: `may_change` never lists `evolution`. A dependency re-pin needs both its pin in `may_change` and a `purpose` (`repin_needs_purpose` stays).
- **Architecture, not PRD.** We never write the PRD. We push back on it, define CC, and turn it into issue-ready modules. Schemas and our tools are ours to decide; seams with RSI, the Verifier and model routing need their owners. Latest data wins over older PRD text.

## 2026-09-29, late night: composition and spatiotemporal composability

- **A single-node capsule is called a singleton**, the most common form (replaces "leaf").
- **All paper and design references live in `capsule/references.md`.**

- **Composition is optional, inspired by NVIDIA TensorRT.** A→gate→B→gate becomes A-B→gate (one capsule holding A and B, both still their own code, pinned and bundled; A's input in, B's output out; tested and gated as one block), and later fused AB→gate (one code item). Same task, streamlined testing, then optimised code. It can nest.
- **There is no direct A→B**; gates sit between capsules, chosen by the workflow (planner, Binding), never by A or B. **Gates are not RSI-able for now** (rule `referee_no_rsi`).
- **Spatiotemporal composability must be defined in the docs**, and why it is last: production software lets a separate layer free memory and resolve dependencies, and restarting is an accepted pattern (VS Code, Windows). Mid-run install and uninstall should be allowed later for long research runs; for testing, restart between sprints.

## 2026-09-29, night: capsules everywhere, RSI is opt-in, dependencies pinned

- **CC applies across the whole system (agreed with Ramika).** Any node can be a capsule: work steps, gates, verifiers, delivery. What is not a node stays outside capsules: admission, the library, the librarian, the record stores. Supersedes "nothing that decides is a capsule" (09-23) and "no capsule in delivery" (09-25).
- **RSI permissions are required and opt-in.** Every Declaration states whether RSI may change it. If the author does not authorise it, RSI may not improve that capsule.
- **Dependencies are always pinned; updating them is RSI** (decided after an adversarial review, replacing "unpin with a purpose"). A dependency may carry a free-text `purpose`; only such a dependency may be re-pinned by RSI, and only if `evolution.rsi` allows. The librarian records a `dependency_update` Finding; a security fix withdraws the vulnerable version first and never waits for RSI. Remote capsules, and capsules depending on them, cannot be certified. Knowing a dependency's purpose raised repair of drifted tools from 10% to 78% (Skill Drift).
- **CC is a schema connected to a series of tools, serving many roles** across the system: selection, admission, running, verification, permissions, the library, improvement, composition, observability, import.
- **Trust levels must be shown.** CC must fit the permission system of a jiuwenswarm-based AI4Research.
- **The capsule folder must cover everything CC is:** why, what, every field, composition (A, B, A-B, AB), library and test storage, admission, trust, RSI improving capsules, RSI building capsules from generalist gaps, the generalist, Symphony, permissions. Check with an adversarial review.

## 2026-09-29, evening: each fact in one place; a capsule is a graph

- **No duplicated definitions.** The Declaration schema lives only in `capsule/fields.md` (`schemas/declaration.md` removed); other pages link to the owner of a fact instead of restating it. The docs are read by people and by their agents, who compare and edit.
- **The capsule folder is self-contained:** what a capsule is, what forms it can take (composition), and everything it connects to.
- **Every capsule is a graph, usually of one node.** A leaf's node is its own code; a composite has `members` (nodes) and `wiring` (edges). A sequence or a tree is a graph, so `structure` is removed.

## 2026-09-29, later: one source of truth

- **The design lives only in jiuwenswarm `docs/architecture/` on `ai4r_main_branch`.** Edit it there, in Obsidian, and commit when approved. No copies elsewhere: `huawei/ai4research-design/` and obby `Block 1 - CC and Schemas/` are deleted. This replaces the 09-28 entries that named `ai4research-design` as the working copy and obby Block 1 as an exact copy.
- **obby holds notes only:** Directives, HANDOFF, `Reference/`, `Parked/`, `Archive/`. See [[README]].
- **The lint** is `tundle/tools/architecture_sync.py`; it runs on the repo folder and must print `ok`.

## 2026-09-29: models are not in the capsule layer (agreed with model routing)

- **Selection picks capsules, never models.** No central library selects both a model and a capsule.
- **The model is the author's job.** Whether a capsule uses a model, which one, and whether it is routed at runtime are decided by its author inside the capsule's own hashed files. A capsule that wants a routed model calls the router from its own code; the capsule layer never sees it.
- **The Declaration has no model field and no role field.** `needs.model` is removed. Roles are set in the Binding. Observation `routing_policy` is removed; Observation `model` stays (which model served a call the runner made). Policy section `routing` is renamed `budgets`.
- **The Declaration describes the work well enough to pick a model from it:** summary, ports, checks, effects, needs.


## 2026-09-28, night: CC and the core schemas only; design parked

- **Scope:** the package is Capability Capsule (what it is, its fields, the tools it uses and needs) and the core schemas. Design and plan are parked in `Parked - Design/`; the design comes later. The only design shown is one page, `read/first-design.md`: a possible first design, the primary workflow as a fixed system on jiuwenswarm, researched at `ai4r_main_branch` HEAD.
- **Two folders:** `read/` is what people read and review, and the schemas must be read by humans and be exactly right; `background/` is context only.
- **No roles** or role assignments anywhere in the package.
- **M1 = the PRD's M1.** Every field is marked **checked** (required for M1 and tested for M1 completion) or **unchecked** (in the shared schema, not required or tested for M1; it unlocks capabilities beyond the original workflow, e.g. most RSI, tracking and merge). RSI is built on another branch that shares the schema. Unchecked does not mean it will not be built.
- **The schema is made complete:** `needs.dependencies`, `needs.secrets`, `needs.resources`, Candidate `source` (provenance, attestation), `lineage.co_parents` with relation `merges`, and composites (`members`, `structure`, `wiring`), all unchecked.
- **Exception handling (proposed):** a capsule completes its Declaration by default and puts difficulty in the output; `guarantees.failure_modes` is the only way to end without an output; an undeclared exception is `CAPSULE_RAISED_UNDECLARED`, always `blocked` (checked at M1).
- **RSI framing:** new capsules grow what the system can do; improved capsules improve it; isolated, individually testable capsules make both easier.
- **The capsule folder ships first** to jiuwenswarm `docs/architecture/capsule/` on `ai4r_main_branch`: commit and push allowed, simple descriptive title, no body, no Claude trailer. `fields.md` is the most important page.

## 2026-09-28, evening: Block 1 is done; Block 2 draws the system from the PRD

- **Block 1** is Capability Capsule and the schemas: `Block 1 - CC and Schemas/` (renamed from `Design/`). It is kept
  as reference and changed only when a decision here requires it. Its working copy is `huawei/ai4research-design/`.
- **Block 2** is the system design: `Block 2 - System Design/`. No big designs: one small Mermaid module per part the
  PRD has confirmed, each naming its PRD section, plus B1, B2 and B3 at a high level. It is edited in obby directly.
- "Block 1 and 2" are sets of documents; B1, B2 and B3 are build steps.

## 2026-09-28, later: the design follows the PRD

- **The PRD arrived** (Ramika; copy in `Block 1 - CC and Schemas/process/prd.md`). It sets M1's boundaries; the design follows it.
  "M1" now means the PRD's milestone 1. Build steps: **B1** = Phase 1, the hardcoded Default DAG in Swarmflow (the M1
  release path); **B2** = the Phase 2 tests (Cluster Mode, Leader Agent, Code Mode); **B3** = the parallel tracks
  (dynamic planner aligned to Cluster Mode, RSI on sample DAG fixtures, dynamic routing, judges and the librarian).
- **M1's capsules are the PRD's:** six stage skills and `verifier_capsule`, plus operators (`op.deepsearch`,
  `op.codesearch`, `op.workspace_io`) as `tool` capsules; the Declaration is the machine form of `make_capsule.md`.
  CC's M1 experiment compares runs with and without per-capsule contracts.
- **The requirement step runs before freeze;** its accepted Research Brief is the semantic contract. Every capsule that
  runs is pinned in the run contract, including the verifier. The node gate decides `pass`, `fail` or `blocked`;
  `fail` and `blocked` go to JiuwenSwarm's `human_session`. Policy epochs can be current side by side, one per track.
- **Routing (Xiaoyang):** the router ranks models at call time and uses the top one; freeze pins limits, never a model.
- **Branch rules (Xiaoyang):** everyone has a child branch; never work on the same part in two child branches at once;
  fetch main into your child branch before starting.
- **Structure work to unblock as much as possible, as early as possible** (Muk): the order is in
  `Block 1 - CC and Schemas/process/architect-role.md`.
- **Questions back to the PRD** are in `Block 1 - CC and Schemas/process/prd-inputs.md` (e.g. what "Codex CLI adapter" means, since
  Codex exists only as an external CLI harness; what BLOCKED means; the Research Brief's owner).

## 2026-09-28: fix the review findings; two-tier sign-off; fewer, generated diagrams

- **Three adversarial reviews found 5 blockers** in B1's admission path, gaps against the capsule checklist, and
  diagrams that contradicted the field tables. Muk: "fix them now... choose whatever works best for the system or
  whatever would not take too much effort to change in the future." The documents had not been shared.
- **A capsule's output is always an Artifact; control code writes records.** The IntentIR and the semantic contract
  are typed Artifacts (`intent_ir`, `semantic_contract`), not records.
- **Admission is the only writer of test cases and test suites**; a Candidate carries its tests inline. A check says
  where it can run (`applies_at: admission | node | both`); the node gate always has its output type's check.
- **Sign-off has two tiers**, amending the 2026-09-25 evening rule that every page is reviewed field by field:
  *approve* (new or a seam) and *adopt with a rename list* (IntentIR, Plan, Verdict, Standing). Finding is deferred to
  B2. → `ai4research-design/schemas/schemas.md`, "What to approve, and what to adopt".
- **Fewer diagrams, generated where possible**, amending "a small Mermaid on every schema page": the schema map and
  the three kept schema views are generated from the field tables by `tools/sync.py`; the other schema-page diagrams
  and the B2 and B3 sequence diagrams are cut.
- **The design package lives in obby, as the subfolder `Block 1 - CC and Schemas/`** (renamed from `Design/`), not in a shared repo yet (Muk, 2026-09-28: "dont put
  them there yet"). Keep it small; every major question should be answerable from it.
- **CC's end goal (Muk):** users install tools, skills and MCP servers from anywhere, put them through an isolated
  verification cycle, and get capability capsules that guarantee what the tool does and at what quality; stores or
  many repositories could then carry capsules. **For now** it is a schema for our own system, built in the near term.
- **"Milestone 1" is the PRD's 31 October target**, not the old internal M1 to M5.

## 2026-09-25, night: milestone 1 is AI4Research's intended functionality

- **Ramika (PRD) wants our idea of the final design, plus what his first milestone needs.** Its exact scope is not
  known yet, so we propose material for the final design.
- **Milestone 1 = the functionality the original AI4Research aspired to, as if it had worked.** The schemas and the
  temporary designs shown now are for that.
- **Naming:** "milestone" is the PRD's word only. Our old ladder M1 to M3 is renamed **build steps B1 to B3**, all
  inside milestone 1. Old M4 and M5 are "after M1". Older notes saying M1 to M5 mean the old ladder.
  → `ai4research-design/design/overview.md`, and naming decision 16 in the vault.

## 2026-09-25, evening: M3 this month; lock the schemas first

- **Target: M3 by 31 October**, meaning the intended functionality of the current AI4Research. Supersedes "M3 is not
  expected this month".
- **First priority: lock every schema.** Issues cannot be handed to a coder (human or AI) until the schemas they touch
  are agreed, because that is what isolates them.
- **One Markdown page per schema**, short: what it is, a small Mermaid of what it connects to, every field with its
  purpose, and whether it is necessary at all ("I don't want to ask for too many schemas"). Check wording conflicts.
- **Sign-off:** everyone reviews; when all approve, the page is **v1** of that spec.
- **Issue template in the shape of a CC Declaration** (with NA where a field does not apply), so the AI coder builds
  and verifies to the spec and Muk verifies before merge. The template is Xiaoyang's (he leads coding).
- **Split the big Mermaid into one small diagram per component:** what is inside and what it connects to.
- **An organised, standalone Obsidian vault**, to become its own git repository: components, schemas and traces,
  all linked by inputs and outputs. "Very integrated design."
  → `huawei/ai4research-design/`, see [[Post-Meeting 2026-09-25 - Schema Map]].
- **Node outputs and verification need their own schemas;** results never go in the capsule. Muk asked for the
  schema of node outputs, of what is sent to verification, and of the status that comes back, and whether routing
  sends verification anything. → Artifact and Verification schemas; routing's choice travels on the invocation.
- **One central place for all presentations,** each at the version everyone has stated is the latest and most
  revised. → `ai4research-design/presentations/`, with a confirm-latest table.

## 2026-09-25: adversarial reviews use Opus

- **Keep adversarial review, but run it on Opus** (Muk: "keep adversarial review but use opus now"). This replaces
  "Reviews use Sonnet only" in [[HANDOFF]] and the process list below. Still one reviewer at a time, and every
  finding is checked in source before it is applied.

## 2026-09-25: M1 uses Symphony, and capsules in every stage

- **Symphony is in M1.** Supersedes the Layer 2 line "ports first, Symphony later" for M1. CC's provider feeds it;
  the planner resolves capsule ids through it. `plan()` is not used, because the planner is hardwritten.
- **CC is used throughout M1, wherever it applies, just as later.** Request and other stages are partially handled by
  capsules, chained with gates: a stage may have one gate or several. The stages themselves are not simplified.
- **What M1 simplifies is planning, dispatch and the library.** That is where the complexity lives, and M1 makes it
  trivial: a hardwritten plan, one fixed node, a fixed capsule set instead of a library.
- **Observability exists from M1.** Every capsule call is observed and recorded from day one.
- **No capsule in delivery.** Delivery stays control.
- **M1 keeps intent compilation lean:** two capsules, compile_intent (normalize + IntentIR) and review_fidelity; the
  deterministic checks sit inside the decide_acceptance gate.
- **In M1 the planner-binder and freeze are pass-throughs:** hardwritten, no decisions, they only carry the contract's
  one capsule through to a pinned run contract.
- **The frontend is an open question.** Perhaps CLI to begin. Users may attach files, text and so on; intake keeps
  attachments as references.
- **The contract is central in M1.** The requirements compiler compiles it; it determines what must be done (want,
  given, allowed capsules, checks) and drives the planner-binder and the step gate.
- **Use the AI4Research stages and the decks' names** in every diagram (checked against notes/08 and research/01-05):
  intake -> intent compilation (normalize_input, compile_candidate, validate_intent, review_fidelity, bounded repair,
  decide_acceptance) -> requirement compilation (template, compile, checks, advisory review, bounded repair,
  acceptance) -> **semantic contract** (RequirementIR v2) -> planner-binder -> freeze (**run contract**) ->
  schedule + dispatch -> delivery. Acceptance steps are gates. M1 code names from M1-DESIGN.md sit inside them.
- **Dispatch hands the task to the dispatch runner.** The runner assembles what the capsule's Declaration describes
  (code by hash, inputs, permissions) and makes the calls at the right sites: loader, wrapper, PermissionEngine, run,
  Binding. Every capsule call goes through it, so diagrams show dispatch as capsules being run, not those steps.
  Supersedes "requirements is control in M1" and "no delivery capsule". Control (planner, freeze, gates) stays code.
- **The planner is hardwritten.** One task, a fixed plan, no model and no selection.
- Open: Symphony's graph takes only skill, subagent and agent nodes, so a tool capsule such as `count_spaces` is not
  graphed today. Either M1's capsules are skills, or Symphony only indexes them.

## 2026-09-25: meta-RSI works on the whole pipeline

- **Meta-RSI is over the entire workflow, not one loop.** It keeps a **tree of whole-workflow versions**: one AI4Research
  goes through meta-RSI and becomes a new version of the whole thing (hot loop, cold loop, library, policies together).
  How it chooses and what it may change are still open. Drawn in the big-picture map, draft 8.

## 2026-09-24 — layer 2: M1 on openJiuwen

- **M1 is on openJiuwen, a fresh start.** Do not use or extend the original AI4Research tools or implementation
  (`capability_capsules.py`, the elastic planner, the tmux pane operators): "seriously fragile and not good to
  extend". AI4Research findings appear only as lessons, never as a build target.
- **No M1 spike yet.** Present code ideas.
- **Emphasis on M1.** Show M2 to M5 only as feasible and structurally compatible.
- **Where agent-core has no answer, borrow a pattern from big-company software** and cite it, with how it works
  where it ships, what CC copies and where it lands.
- **Planning: ports first, Symphony later. Execution: our own Kahn runner. Versions: a linked list for M1.**
- **Muk also implements.** One roles slide; other teams appear only as what CC needs from them and gives back.
- **State and tests:** the author declares whether a capsule holds state; test aids are never evidence; tests are
  saved by id. → [[Layer 2 Presentation]]

## 2026-09-23, after the presentation — the model, and how to argue

- **A capsule points at code and never holds it.** A hat on a head; the hash is how a changed head is noticed.
- **Leaf or composite, never both.** Capsules contain capsules.
- **No capsule is its own final judge.** Internal checks are allowed and are never evidence.
- **Tests and gates carry ids**; the space cost is accepted.
- **Lineage is a tree**, because repositories branch and fork, and the latest is not always the best.
- **Make targets clear, see what others did, then copy it.** "I am going to put TensorRT as the structure for my CC
  optimizer", not "I want to make GPT-6 but better". CC itself is not already done: its components exist and have
  backing, and the assembly is ours.
- **Staged items are good, but the target must exist and be clear.** Staging is appended information about when a
  part is enforced, never what is presented as the goal.
→ [[Post-Presentation Decisions]]

## 2026-09-23 — scope, merging, quality, and how to cite

**The thesis line, and everything hangs off it:**

> **A 能力胶囊 is flexible in form and strict in verification and quality assurance.**

- **Every stage applies capabilities.** "This does not mean the whole workflow becomes a cap cap itself,
  but it means each stage can apply capabilities." The unit is the *work a stage does*. → [[Every Stage Applies Capabilities]]
- **A capsule holds a set of capabilities; n = 1 is the degenerate case.** One schema, optional sections
  switching on by type, so the library places everything under one rule. A capsule may contain its own
  DAG and be placed in the outer DAG as a block.
- **Nothing that decides is ever a capsule.** A capsule may produce an assessment; judging the system is
  barred, domain work is not. → [[The Ceiling]]
- **The overlap and merge system.** Recurring, high-quality pairs and structures become merged capsules;
  A, B and A-B all coexist; internals lock on merge; **there is no split operation**. → [[Overlap and Merge]]
- **Quality, not just correctness.** Capsules must be shown to fit criteria, to function, and to be good
  *often enough* — a rate over a window, with a minimum observation count and a calibrated judge. Block
  only for safety; label for quality. → [[Quality Not Just Correctness]]
- **One schema, progressively activated.** The schema is whole from day one; what is staged is how much
  of it is enforced. Parts can be missing and the system still demos. → [[Milestone Ladder]]
- **Start at one node.** Demonstrate it works before building large DAGs. More fields and more testing
  are overhead on every capsule author.
- **Spatiotemporal composability comes late**, and honestly: it gives install and uninstall mid-run, it
  is **not** foolproof and **not** full reversibility.
- **Symphony's library, ranking and sorting already work.** Do not redo or fix them.
- **Cite the biggest company, one question per citation, and spread them across the whole deck** — not
  condensed into one slide. "Inspiration from other software" is a good look at Huawei.
  → [[Inspiration from Other Software]]
- **Show impacts beyond the three teammate features**, and show where the layer lands in code — Symphony
  is the best anchor because it gives us a point to build on.
  → [[Impacts on the Workflow]], [[Where It Attaches]]
- **A diagram of what is in the library and what a capsule can be.** → [[What Is In The Library]]
- **English only**, with 能力胶囊 kept as the term's original name.
- **Delivery:** dense, diagrams where they earn it. Talking fast is not the goal — take the time, but
  every line must land a key point exactly.

## Everything important on the slide; notes in point form; no inference passed off as a finding (2026-09-22, late night)

- **All important data is on the slide.** Muk may skim or skip the notes, so no number, source or conclusion the
  argument needs lives only in the notes.
- **Speaker notes in point form:** short bullets Muk can glance at, not paragraphs.
- **Hunt for cases like SkillFuzz:** a paper cited for more than it showed (our inference stated as its finding), a
  value read off a figure, or a "proved wrong if" line that does not fit its study. Fix each one.

## Compress, make each slide mean more; code items are illustrative (2026-09-22, late night)

- **Fewer, denser slides**, each carrying one meaningful point. Merge rather than add.
- **Individual code items are open to change.** File paths, line numbers and exact field names are not the argument;
  the deck only has to show the design can work on what exists. Keep code references light.
- **A pre-workshop rundown** for Muk: what to hold in their head going in, given they have read the research and the
  schema.

## Show what the research found, and cut slides that add attack surface (2026-09-22, late night)

- **"Link to research" means what actually happened in each study and what it showed**, not numbers and arXiv ids.
  For each study: what they built or ran, what happened, and what that means for the CC part it justifies.
- **Spend slides on this rather than on tables.** Cut slides that neither answer a to g nor explain; each extra table
  is more to defend without serving the goal. Appendix detail stays in the report, not the deck.

## What CC is for (a)

**CC makes capabilities easier to pick, verify, improve and remove.** Underneath all four is the schema itself: the
Declaration (one unified schema, with optional parts), and how the capability itself is held.

| Verb | Why it is easier with the schema |
|---|---|
| **Pick** | inputs and outputs are known. Deterministic finding on declared requirements cuts out most options, and only then does semantic matching choose among the survivors. **Selection is cheap because it is strict**, and the documents must name exactly which requirements are checked |
| **Verify** | everything is declared, so each check has a target: held-out tests against the declaration, observed effects against declared effects, and the hash proving the checked thing is the run thing |
| **Improve** | performance and trust are logged. Parents and children are known through lineage and dependency hashes |
| **Remove** | spatiotemporal composability |

## Rewrite the deck and report around a clean a to g (2026-09-22, evening)

- **a to g first and foremost**, in both the deck and the report. Rewrite in logical order rather than trimming the old.
- **Deck:** far fewer slides; key stats on the slides, not in speaker notes; drop the "thus" strips so diagrams are
  bigger; no "questions for the room"; advantages may take two slides, each citing its paper.
- **Show the records:** one slide with each record (Declaration, Verdict, Standing, Finding, Binding) and what goes in
  it: where the hash, parentage and provenance live, and what a Finding is for. The Declaration's fields in
  standardised `section.field` names.
- **Diagrams must be right:** the planner never writes to a capsule; capsules are assigned to DAG nodes when the plan
  is frozen, and then do their job.
- **Verify the real AI4Research selection:** it does filter deterministically first (types, effects, network, proof
  classes, trust, admission), never on preconditions, then one model call reads the full rows of every eligible
  capsule.
- Run through the slides to check they work.

## Build onto openJiuwen, reuse what exists; a schema that is useful (2026-09-22, late)

- The goal is to **build onto openJiuwen**: where something already exists (in agent-core, jiuwenswarm, Symphony or
  AI4Research), use it rather than design a new one. CC is a schema that exists **to be useful**.
- Verify claims where possible; **never overclaim**; make it easy to show, with a real example, why CC is better.

## Length, content and defensibility (2026-09-22, late)

- **No time target.** The deck is as long or short as needed to get through all primary content effectively, and no
  longer. Explain the key parts, what a to g requires, and the justifications with data.
- **Make no claim that cannot be defended.** Every number sourced; every design choice marked as design.
- **Show today's state:** what jiuwenswarm skills and capabilities look like right now, how Symphony works, how a
  skill, Symphony and a capsule differ, and why CC is better for the openJiuwen system and for AI4Research's role.

## Start extra small, and do not be too strict (2026-09-22, late)

- The new CC library should be **extra small** to begin with.
- CC must **not be so strict that it stops AI4Research reaching its goals**: soften CC's checks and let more things
  run under CC. **Resolve the judge issue** (semantic research outputs can only be judged, and unmeasured judges
  used to block them), and rewrite the report and deck to match.

## Fit openJiuwen's own structure (2026-09-22, night)

- Everything in the schema must fit openJiuwen appropriately, **as its structure is recorded in this vault**
  ([[openJiuwen Landscape]], `agent-core/Core 00-06`, `jiuwenswarm/Swarm 00-05`): use its layers, its names and its
  existing mechanisms, and say where each CC record and mechanism lives in it.

## The library is a version tree; CC exposes, RSI chooses (2026-09-22, night)

- The schema must be really good for version tracking. The library it serves is a **tree of capabilities**: branches,
  parents and children, so RSI can pick a child or a parent to branch from.
- **RSI has its own selection policy.** CC does not choose for RSI. CC **stores and exposes useful information**,
  efficiently, and marks as **optional** whatever it cannot guarantee.
- **The split of who knows what is vital**, and not all of it is CC's responsibility: part is RSI's. CC exposes data
  and lets it be tracked effectively.

## Gates, inherited tests, and exempt generalists (2026-09-22, night)

- **Node gates.** Explain how the schema serves the gate every node must pass, and who writes it. An admitted capsule
  should very likely pass the part of the gate that comes from its own declaration.
- **Tests travel with the capsule.** The tests a capsule was verified with are associated with it, so RSI can build a
  child and show it is better: it passes the parent's tests and more, including tests RSI authors.
- **`exempt`.** A schema field that exempts a capsule from the library's verification policies, so the generalist (the
  low-trust do-anything capsule) exists and RSI has material to improve on instead of everything failing unexplained.
  **More than one generalist may exist** (for example a Codex generalist and a Claude generalist). Exempt capsules are
  still bound by the plan's gates when used in AI4Research.

## Authors answer for state and undo; CC declares first, then checks (2026-09-22, evening)

- Capabilities are not inherently stateless: an MCP server over a live Postgres database changes state, and undo is
  not guaranteed. Spatiotemporal composability does not undo a context poisoned by bad tools that were later removed.
- **Responsibility goes to the author.** What happens inside a capability is the author's. The author must declare up
  front what it changes, whether it is idempotent, how it is undone (or that it cannot be), and what it touches.
  CC's liability is checking the declaration against what is observed, so problems are found before use, not the
  hard way.
- **Composition keys off the declared class:** pure and idempotent capabilities compose freely; compensable ones
  compose with the undo path tracked; irreversible or undeclared ones are gated.

## A capsule holds no task, and multiplicity is real (2026-09-22, afternoon)

- **A capsule is an abstraction** pulled from the library and told to do a task through its inputs and outputs. It
  never has tasks written into it: no step, node, sprint, workflow, stage, task type, upstream capsule or worker. That
  would make it specific instead of the general tool for the task. **CC is a schema.**
- **The planner does not hold a list of capsules and schedule them.** Plan steps say what is needed; the Binding and
  its invocations say what filled it. Keep the workflow mostly as it is.
- **The schema must handle real multiplicity:** the same capsule on many steps and in many sprints, several capsules
  in one step, fan-out over items, retries and fallbacks, and who owns each.

## The thesis

- CC is **a schema that serves the AI4Research workflow and its tools, built on agent-core in openJiuwen.**
- In the workflow, capabilities must be right, because each one feeds the following nodes. A wrong capability
  propagates errors.
- Other systems **observe**: Symphony's fingerprint, Skill Drift probing skills, Alita-G checking results. CC
  **declares**, because a declaration can be verified and found wrong.
- CC must ensure every admitted capability's effects match its declaration.

## a to g

- **Structure.** Key slides at the start answer each letter. The main body then elaborates each part and why. Never
  one compressed page.
- **(c) Position.** CC sits at the **planning, freeze and dispatch** stages of the workflow. Say where in the system
  and the code, and what it touches, with research behind it.
- **(d) Dependencies** means what **CC itself** depends on:
  - other systems (agent-core code, Symphony, the workflow's stages);
  - materials;
  - other teams and models.

  It is *not* a capability's internal dependencies. Those are handled inside the schema: pinned by default, or
  unpinned by an author who writes the dependency's purpose.
- **(e) Similar designs.** Symphony first, then other similar designs, then papers with similar traits.
- **(f) Better.** That leads into why CC is better.
- **(g) Feasibility.** Much of this has been done before, but never combined into one schema.

## How to write

- **Organise the rationale by function**: "we do X because of paper A; we do Y because of papers B and C". Never
  paper by paper.
- **Justify every component.** If it is not crucial to function, do not write it. Keep the worked example.
- **Focus on the schema** and how the schema supports tools, not the tools themselves.
- **Quote code lightly.** An abstract location such as "the planner's filter" is fine.
- **The content must answer these directly:**
  - How does the schema support self-improvement?
  - How does it help verification?
  - How does it help the librarian keep capsules versioned and structured, so we know what each is derived from?
  - Who carries past performance?
  - What carries trust?
  - What helps RSI?
- **Show the fields** of the schema and what they should be, including how the capability itself is held (skill,
  tool, MCP, A2A).
- **Say how capabilities are retrieved** in the proposed system, based on the research.
- **Include spatiotemporal composability.**

## Research base

- **Tuesday's (2026-09-15) papers:** Cordis, Alita-G, Beyond Task Completion, CoEvoSkills, Darwin Gödel Machine,
  AllocBench, SkillWeaver, SkillDAG.
- **The group's reading list:** Cognitive Admission Control, The Blind Curator, More Skills Worse Agents, SkillFuzz,
  SkillProbe, When Self-Evolution Backfires, AllocBench, Skill Drift Is Contract Violation.
- **Every cited paper is read in full.** Look deeper; no slop.

## Process

- **Record everything important in the tundle obby vault, organised.** Update existing notes; keep the vault clean.
- **Adversarial reviews use Opus** (since 2026-09-25; Sonnet before), one at a time. Verify every finding in source.
- **Store research, materials and repos as markdown** in `capsule-openjiuwen/kb/` to build the documents from.
- **Close review agents when they are done.**

→ [[HANDOFF]], [[Capability Capsule]]
