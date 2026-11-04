# What the evidence says the schema should be (derivation for v2.1)

Written 2026-09-22 overnight. It answers one question. Taken together, what do these say the Capability Capsule schema
must be?

- the papers;
- the AI4Research workflow;
- openJiuwen agent-core with Symphony;
- jiuwenswarm.

Each row runs **source finding → requirement → schema element → status in v2.0**. Status is one of:

- **covered**: v2.0 has it;
- **partial**: v2.0 has part of it;
- **missing**: v2.0 lacks it;
- **contradicted**: v2.0 says otherwise.

§2 lists the v2.1 decisions that follow.

**Sources at recorded heads:**

- agent-core `e23806c1` (2026-09-21)
- jiuwenswarm `02b37f47f` (2026-09-21)
- AI4Research `b0bf165f9`
- papers per `../verify/PAPER-LEDGER.md` and `../alt/READ-LOG.md`

**New in this pass:** stream D (jiuwenswarm) and the directive matrix (stream A). Streams B and C re-use findings
that the earlier rounds verified.

---

## 1. The matrix

### A. Directives (supervisor and Muk)

| # | Directive | Source | Element | v2.0 |
|---|---|---|---|---|
| A1 | a to g answered, each sayable in one line | assignment | REPORT §2 table | covered |
| A2 | lead with the schema: what it is, where it comes from, who follows it, what others do, why | Muk, memory `workshop-framing-schema-first` | REPORT §1, §5, §5 | covered |
| A3 | CC is a scheme, not a tool. The verifier is a tool it uses | supervisor 2026-09-21 | SCHEMA §1; REPORT §16 | covered |
| A4 | safety from declaration, not observation | Muk | the governing rule; REPORT §8 | covered |
| A5 | predicate parity: one predicate for the filter, dispatch and the body, not a heuristic | Muk, 2608.01050 | invariant 8; SCHEMA §4.3 | covered |
| A6 | tokens, only as far as they apply to AI4Research | Muk | REPORT §9.3; M2 | covered |
| A7 | Symphony and agent-core integration, hooks with gaps | Muk | SCHEMA §4.17; REPORT §10.1, §11.2 | covered |
| A8 | spatiotemporal composability is part of the schema and its function | Muk | SCHEMA §4.6; REPORT §13 | covered |
| A9 | supply what SkillFuzz needs, never claim safe sets | Muk | SCHEMA §4.9; REPORT §14 | covered |
| A10 | routing picks models only; a capsule states constraints | supervisor, memory `capsule-owns-selection` | `needs.model`; REPORT §16 | covered |
| A11 | AI4Research itself is not a capsule; a ceiling on size | supervisor 2026-09-18 | SCHEMA §4.10 | covered |
| A12 | ownership open for discussion; g kept short | Muk | REPORT §11.9, §18, §18 | covered |
| A13 | a paper-by-paper spine showing why the schema looks this way, and each team's impact | Muk | REPORT §7 | covered |
| A14 | compare with Symphony (fingerprint versus Declaration) and skills | Muk | REPORT §10.1, §10.7 | covered |
| A15 | integration with RSI, and the demands on verification | Muk | REPORT §11.4-11.5 | partial: RSI mapped to agent-core `RsiTreeNode` only, not to the jiuwenswarm RSI service and its activation store (D8-D10) |
| A16 | "our schema helps everyone do better" | Muk | REPORT §11.4-11.7, §16 | covered |
| A17 | build on openJiuwen, changing agent-core only where necessary | supervisor 2026-09-18 | SCHEMA §4.17: no required change | covered |
| A18 | diagrams over bullet points, accurate and well sized | Muk | figures traced to sections | covered |
| A19 | every cited paper read in full | Muk | ledgers | covered |
| A20 | jiuwenswarm taken into account | Muk, tonight | none beyond import rows | **missing** (stream D) |

### B. Papers (each finding that forces an element)

Both directions are checked. Every finding below has an element, and every element in SCHEMA v2.0 §3 has a reader
(the tool column) or a finding. The one exception is noted under §2.9.

| Paper | Finding that forces the schema | Element | v2.0 |
|---|---|---|---|
| 2604.00392 Beyond Task Completion | 215 of 222 self-built tools failed held-out tests of their own job, and in-session signals missed it | author other than the builder, `held_out`, certified level | covered |
| 2605.24050 More Skills, Worse Agents? | the chooser is the bottleneck; 38.5% invoked no skill at 202 | `summary` cap, filter, overlap Finding | covered |
| 2608.01050 Don't Offer | a gate on the skill's own exit predicates is sound under parity and fresh state; policy on unavailable state must be explicit | `needs.when` with `evaluable_at`, `on_unavailable`, parity checks, `blocked[]`, `exit` | covered |
| 2607.07436 Blind Curator | a lenient judge stops retirement silently | `measured_error`, reason codes, curator health | covered |
| 2605.19576 Library Drift | harsh retirement is worse than none; caps mainly control variance | evidence floor, caps | covered |
| 2608.05810 Self-Evolution Backfires | gate before commit; cleanup needs provenance | set-level gate, `context_capsules` | covered |
| 2607.02345 SkillFuzz | harm is compositional; the screener needs contracts | effects, invariants, `co_loaded`, composition Findings | covered |
| 2609.16313 Cognitive Admission Control | typed verdicts; unknown is not no; no compensatory score | outcome, DEFER, no scalar | covered |
| 2604.17870 GraSP, 2606.03056 SkillDAG | typed edges help; conflicts on one observation are weak | ports, replacement rule, conflict threshold | covered |
| 2607.23332 AllocBench | build on recurrence | gap Finding, threshold | covered |
| 2601.08815, 2602.22302 contracts | budgets bind between calls; composition conditions C1-C4 | `budget.enforcement`, composite checks | covered |
| 2605.10990, 2606.07904 drift and contracts | dependencies rot; inferred effects are weak (0.77); a keyword filter cost success | pinned or floating dependencies, a person confirms effects, the declared filter | covered |
| 2505.22954 Darwin Gödel Machine | the capability reached its checker's signal | runner outside scope, `signal_source` | covered |
| 2510.23601 Alita-G, 2604.01687 CoEvoSkills | a tool kept on its parent's success, or scored on the set it was built from, is not tested | the stored body tested, held out, author not the builder | covered, and **D9 shows RSI today does exactly this** |
| 2605.06365, 2606.26924 lineage, RelAIBuild | hash identity; a declared permission is not an enforced one | `decl_hash`, step identity, assurance, `prev_hash` | covered |
| 2608.25512 Cordis | add, replace, revert, remove; reversal needs a boundary | `injects`/`provides`, reversibility, two-step remove | covered, and **D6 shows jiuwenswarm cascades already** |

### C. AI4Research workflow and agent-core (re-checked at the heads above)

| Finding (code) | Requirement | Element | v2.0 |
|---|---|---|---|
| the filter never reads preconditions; dispatch checks four kinds (`elastic_planner.py:4553-4648`, `capability_capsules.py:1220-1242`) | one predicate set | invariant 8 | covered |
| the binding prompt carries full rows, again on repair (`elastic_planner.py:4678-4724`, `:4949`) | tokens measured against today | M2, `selection_tokens` | covered |
| the freeze admits only `stable` and rejects changes during planning (`execution_authority.py:55-56`, `:81-94`) | levels, and a hash check at dispatch | Binding, level | covered |
| the binder loads by name, with no hash check (`harness/extension_binder.py:27-60`) | load by hash | SCHEMA §4.5 | covered |
| the skill loader reads only `description` or `description_<lang>` from frontmatter (`harness/rails/skills/skill_use_rail.py:946-958`) | anything else a skill declares has no runtime effect today | the capsule layer carries the declaration | **new evidence**, consistent with v2.0 |
| `VerificationRail` rejects tools outside an allow-list and guards workspace paths, but lets `mcp__*` pass unconditionally (`harness/rails/subagent/verification_rail.py:166-220`); `AgentModeRail` enforces a plan-mode allow-list (`harness/rails/agent_mode_rail.py:510`) | tool-level effects can be *enforced*, not only observed, by a rail of this pattern; MCP needs its own rule | enforcement path for `effects` | **missing** (v2.0 names only `before_tool_call` observation) |
| agent-core recognises skill kinds `team-skill` and `swarm-skill` (`harness/rails/skills/team_skill_create_rail.py:32`) | team skills have a runtime path as skill folders | `kind`, carrier | **contradicted**: v2.0 says teams have no binder path |
| harness-RSI candidate gate: accepted if the *target* cases improve, non-target "not_evaluated", no errors, no missing tools or skills (`rsi/harness_rsi/single_harness/iterative.py:1435-1447`); `candidate_holdout_cases` defaults to 0 (`rsi/harness_rsi/config/config.py:172`) and is forced to 0 in single-harness mode (`iterative.py:164`) | RSI's acceptance is builder-side, on the cases a change was built from | RSI output is a candidate Declaration, never a Verdict | partial: v2.0 says RSI never admits, but does not name what RSI's own gate is |

### D. jiuwenswarm (new tonight)

| # | Finding | Evidence | Requirement | v2.0 |
|---|---|---|---|---|
| D1 | of 34 bundled skills, 33 declare `name` and `description`; 7 a `version` (21%); 3 `allowed_tools` (9%); 1 `models`; 1 `mcp`; none declares inputs, outputs, preconditions or effects; 1 has invalid YAML | `resources/agent/workspace/skills/*/SKILL.md`, counted by `scratchpad/skill_corpus.py` | the importer must propose most of a Declaration; nothing today is an evaluable contract | covered by imports (provisional), now **measured** |
| D2 | 25 of 34 ship scripts; 13 state prerequisites only in prose; 29 describe outputs only in prose | same | effects exist but are undeclared; preconditions exist as prose | consistent with the importer rule "a person confirms effects" |
| D3 | 9 of 34 descriptions exceed 400 characters (median 276, max 1,086) | same | the `summary` cap forces a rewrite for about a quarter of imports | partial: the cap exists, but the import path does not say who writes the summary |
| D4 | `advanced-daily-report` lists `bash`, `write_memory`, `write_file` and pushes reports to Feishu; its `allowed_tools` is not enforced by the loader (C, row 5) | `advanced-daily-report/SKILL.md:6`, `:11` | an emission and writes, undeclared and unenforced: the case for `effects` with reversibility | covered in principle |
| D5 | `pdf-extraction` declares `models.recommended` and `models.compatible` | `pdf-extraction/SKILL.md:23-31` | a skill naming models is a choice; the schema allows only constraints | **missing**: no import rule for model fields |
| D6 | SkillPacks: `kind: skillpack`, at least two members **by name**, a workflow graph parsed from the body; enabled only if requested and no member is blocked; a *disabled* member has blocked a standard pack since SkillPacks were introduced (`6f4eaa1b6`, 2026-09-17); `02b37f47f` (2026-09-21) extended this to container packs | `server/runtime/skill/skillpack.py:180-258`, `:285-320`; `skill_manager.py:1177-1210` | composites exist in production with a disable cascade (spatial composability), but members are unpinned, so a member's change silently changes the pack | partial: v2.0 composites pin members, but has no rule that a member's Standing gates the composite |
| D7 | Swarm Skills: a directory with `SKILL.md`, roles, `workflow.md`, `bind.md` (resource and behavioural constraints, failure handling) and `dependencies.yaml` (skills and tools, `required`, `purpose`, explicit `[]` meaning "checked, none"). The agent reads the dependencies at preflight and the user decides go or no-go | `docs/en/SwarmSkills.md:66-74`, `:119`, `:339-374` | jiuwenswarm independently reached declared dependencies, boundaries and acceptance criteria, but as names and prose evaluated by a model | **contradicted**: v2.0 excludes teams in v1 |
| D8 | the RSI service installs a harness only when the task is COMPLETED and `published`; hashes the package deterministically; derives the installation id from the hash; keeps an active pointer with immutable history; refuses rollback while any RSI task is queued, running or paused | `agents/harness/common/rsi/harness_activation.py:266-293`, `:416-464`, `:682-692`, `:715-772` | RSI already has hash identity, a Standing-like pointer and a concurrency rule, but RSI itself writes the pointer | partial: v2.0 has the concepts, but not the writer split against this code |
| D9 | "published" means some candidate gate accepted (`iterative.py:3963-3972`), and the gate is target-local, with no holdout (C, row 8); the suite it loads is called 训练集 (training set) | `validation_dataset.py:24-32` | RSI's publication is observation on the build set: evidence for a candidate, not admission | covered by the rule, now with **in-house evidence** |
| D10 | `RsiTreeNode` records `parent_id`, `adopted`, `score`, `snapshot_artifact_id`, `changes`, `failure_class` | `agents/harness/common/rsi/models.py:292-306` | lineage exists; `context_capsules` and author separation do not | partial |
| D11 | skill self-evolution is off by default and approval-gated for Single Agent and Leader (`auto_save: false`), but a **Teammate always saves automatically**, and the experience is loaded with the skill next time | `resources/config.yaml:732-733`; `docs/en/SkillSelfEvolution.md:55`, `:119` | an experience layer changes what a bound capsule does without a new hash | **missing** |
| D12 | TTSE induces FACT and TIP entries and injects catalog guidance; "does not rewrite SKILL.md or show an approval dialog"; off by default | `docs/en/TTSE.md:3`; `config.yaml:739-740` | an unreviewed overlay on *selection*: the chooser's input changes outside the Declaration | **missing** |
| D13 | Auto Harness: Meta changes go by PR review; Expert packages go build and verify, then **user confirmation**, then hot-load | `docs/en/AutoHarness.md:38-41`, `:60` | a hot-loaded package is a new body. The confirmation is a person, not a check | partial. The same page's FAQ says packages are hot-loaded "immediately after generation" (`:297`), so the confirmation step is documented inconsistently. The tundle note `obby/jiuwenswarm/Swarm 03` said no approval; corrected 2026-09-22 |
| D14 | Symphony evolution changes edge weights from `plan.outcome` events, and distils "skill packs" of existing members | `verify/V3-jiuwenswarm.md` C2-C3 | observation that must never admit | covered (`use_outcome` Findings) |

---

### E. The 2026-09-15 capsule report: the self-improvement goal (added for v2.2)

The Tuesday report (tundle `AI4Research Capability Capsule Report - Muk.docx`) set the project goal: agents that build,
check and keep their own capabilities while long runs continue. It derived rules R1-R6 from the papers. v2.1 had lost
most of this. v2.2 restores it.

| # | Tuesday requirement | Source | Element in v2.2 | v2.1 |
|---|---|---|---|---|
| E1 | the goal: agents that explore, choose, build, evaluate, modify, retire and trace capabilities | §1 | SCHEMA §1 goals; REPORT §2 goals table | **missing** |
| E2 | R1: using and building run at the same time, on separate clocks; sprints never wait | §2.1, App. G.2 | three clocks (SCHEMA §4.0) | **missing** |
| E3 | R2: every sprint pins exact versions; the sprint is the reuse boundary | App. G.1 | invariant 3; Binding; §4.0 | covered |
| E4 | R3 and R5: held-out tests written first from the contract; code gate; capped admit/reject feedback; no capsule writes the gate, tests, logs or registry | §2.3-2.7, §4.3 | cold path roles (§4.12); protected components (§4.1) | partial: author separation only |
| E5 | R4: duplicates rejected; close capsules versioned | §2.1, App. C | overlap and `DUPLICATE`; four update options (§4.7) | partial |
| E6 | R6: the agent that decides never builds; builds follow recurrence counted in sprints | §2.8, §4.2 | build decision role; gap identity and sprint counting (§3.6, §4.12) | partial |
| E7 | the generalist capsule: contract from the node, lowest trust, never writes the library, leaves a gap record; two frozen flags; a cap | §4.1, App. G.3 | §4.14; run contract (§3.4); `generalist` in the Binding | **missing** |
| E8 | append-only and versioned; improve, never edit; monotone new versions; four update options | §4.5, App. G.7 | §4.7 | partial |
| E9 | the audit loop: scheduled replay of regression suites, by blast radius | App. G.2, G.6 | §4.13 | **missing** |
| E10 | retirement reasons select policy; task success only demotes | App. G.6 | §4.13 | partial |
| E11 | what the system may change, most reversible first; the gate never | App. G.5 | §4.16 | partial (invariant 4) |
| E12 | unattended servers: an approval request becomes a rejection | App. G.8 | §4.15 | **missing** |
| E13 | scheduler: no two steps with overlapping write scopes together | §4.1 | §4.4 | **missing** |
| E14 | the build budget is a hard limit, never a price shown to the builder | App. G.4 | §4.12 | **missing** |
| E15 | the generalist's outputs never become expected results | §4.2 | §4.12, §4.14 | **missing** |

**Why v2.1 lost it.** The overnight derivation started from the merged v2.0, whose two parents (v1.6 and the
independent version) were written after the Tuesday report and focused on the workshop brief. The topic register
listed "self-improvement loop" as lost, but the derivation read only the papers, code and this session's directives.
**How to avoid it:** stream E is now part of the derivation, and the Tuesday report is a named source.

## 2. Decisions for v2.1

Each decision gives what changes, why, and what would reverse it.

1. **Overlays are part of what a sprint pins** (D11, D12, D13).
   - **Change.** Any content loaded into a bound capsule's context or into the chooser's input is either in the
     Declaration's `body[]` (and so hashed) or declared as an `overlay` with its own hash. Examples: an experience
     layer, TTSE facts and tips, a hot-loaded package.
   - **In a sprint.** The Binding records the overlay hashes. An overlay not pinned at the freeze is not loaded for
     that sprint.
   - **Unreviewed keep-paths.** Teammate experience and TTSE produce new overlay versions, which enter as provisional
     revisions. They never change a certified Binding in place.
   - *Why:* invariant 3 (a sprint sees only the versions it started with) and invariant 1 are otherwise bypassed by
     content that changes without a hash.
   - *Reversed if* overlays are shown never to change behaviour. The evidence says they are designed to.
2. **The RSI interface maps to the RSI service in code** (A15, D8-D10, C row 8).
   - **Mapping.**
     - An installed harness package becomes a candidate Declaration: `body[]` = the package files, `decl_hash` beside
       jiuwenswarm's package hash, `lineage.parent` from the task's `final_node_id`.
     - RSI's `published` becomes builder evidence in the Verdict's `builder_gate` field, a sibling of `suite`.
   - **Writer split.** The activation pointer becomes the Standing, written by the librarian after a Verdict, not by
     RSI.
   - **Asks of RSI.**
     - accept verification's held-out suite for admission (a held-out split inside RSI needs a code change: the
       single-harness orchestrator forces it to 0);
     - record `context_capsules`.
   - **Adopted from RSI's code.** The rollback guard: no revert while a builder task on the same name is active.
   - RSI's gate also replays the whole suite each epoch and promotes only without regression against the previous best
     (`iterative.py:927-929`). That is still the builder's own suite, so it stays evidence.
   - *Reversed if* RSI's gate gains a held-out split owned by someone other than the builder. It would then count as
     `tested`, not only as evidence.
3. **Composites are gated by their members' Standing** (D6).
   - **Rule.** A composite is offered only while every member's Standing is `admitted` and equal to its pinned hash.
     Otherwise the composite moves to `suspect`, reason `MEMBER_UNAVAILABLE`.
   - **Import.** A SkillPack enters as a composite with members pinned at import.
   - *Why:* jiuwenswarm has shipped this cascade since 2026-09-17, by name (corrected after review: not first in `02b37f47f`). Hash pinning closes the silent-change
     gap.
4. **Team skills stay out of v1** (D7; revised after review).
   - A Swarm Skill's Leader decides at run time which roles to involve and schedules them
     (`docs/en/SwarmSkills.md:241-253`). That is planning, so it is above the ceiling.
   - `team_skill_create_rail.py` suggests creating team skills; it is not a loader.
   - `dependencies.yaml` and `bind.md` are imported as evidence.
   - *Reversed if* a team skill's roles and order are fixed, so the freeze could bind it as one node.
5. **The tool set can be enforced, the effects only in the sandbox** (C row 6, D4; narrowed after review).
   - A rail following `VerificationRail` enforces which tools a bound capsule may call.
   - `bash` reaches any path, `mcp__*` passes through, and capsules sharing a context cannot be told apart. So file,
     network and execute effects are `enforced` only in the sandbox, and `audited` at tool-call level.
   - Carriers may not bring rails.
6. **Model fields in skills are evidence, not choices** (D5).
   - **Rule.** An importer never maps `models.recommended` to anything routing must follow. `models.compatible` may
     seed `models_used` only after the capsule's checks pass on those models.
7. **The importer writes a summary proposal** (D3).
   - **Rule.** When a description exceeds 400 characters, the importer proposes a `summary` and a person confirms it.
     The full text stays in the body.
   - **Injection.** The summary is shown to the chooser as quoted data. It may not name other capsules or tools
     **(design)**. This settles the "summary as an injection path" topic as far as the schema can.
8. **The not-yet-covered topics:**
   - **Concurrency:** Standing moves are serialised per name and logged; a sprint reads one snapshot; reverts wait for
     active builder tasks (from D8). *Settled.*
   - **Schema migration:** migrating is a new Declaration with `lineage.relation: migrated_from`. It keeps its Verdict
     only if every check id and runner hash is unchanged; otherwise it is re-admitted **(design)**. *Settled.*
   - **Cost of certification:** open until ownership is decided; the jiuwenswarm `Usage` model (tokens, calls, cost
     per RSI task, `agents/harness/common/rsi/models.py:59-100`) is the pattern for recording it. *Kept open.*
9. **No field is cut.** Every v2.0 field kept a reader. `coverage.undeclared_notes` is now also read by the importer
   (D1-D2).

10. **Added after review** (`../verify/V10-overnight-20260922.md` §3):
   - pre-approved fallbacks in the Binding (today's freeze already has them);
   - the planning-time evaluability of a predicate computed from upstream declared effects;
   - evaluator and vocabulary versions in the Binding;
   - computed fields moved out of the hashed Declaration into the Verdict;
   - agent-core's own overlays (SkillUseRail experience text, `max_total_chars` truncation) pinned or switched off;
   - a superseded member does not suspend its composite.

11. **v2.2: restore self-improvement** (stream E): goals; three clocks; the generalist; the cold path's four roles;
    monotone updates; protected components; the audit loop; unattended runs; scheduling by write scope. Also added:
    a record-by-record comparison with today's capsules (REPORT §3), and unpinned dependencies with a written purpose.
    Given the failed contract, one-round repair went from 10% to 78% (2605.10990 p8-9).

12. **v2.3: a consistency pass after review** (`../verify/V10-overnight-20260922.md` §4):
    - Standing has one writer, the librarian, and Findings move it only toward less authority;
    - the generalist binds only where every output has a deterministic or reference gate, and is admitted on a
      conformance suite;
    - the freeze checks the snapshot, so admissions during planning no longer abort a sprint;
    - `contract_hash` binds a suite to the contract written first;
    - one rule for new versions, and one running-plan policy per reason;
    - the run contract is recorded in the plan; claims carry a status; Findings carry a visibility;
    - unattended runs cover every place a person was asked;
    - an exploration quota;
    - restored from the 2026-09-15 report: provenance fields, its rejection reasons, negative controls, practice
      feedback before the gate.

## 3. What would change this derivation

- **agent-core loads skill frontmatter beyond `description`.** Then `allowed_tools` could be enforced at load, and
  decision 5 would move into agent-core.
- **RSI enables held-out cases.** Decision 2 would then record RSI's gate as `tested`.
- **jiuwenswarm pins SkillPack members by hash.** Decision 3's import step would become trivial.
