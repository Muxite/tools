**2026-10-05: architecture reset for the first POC pipeline.** The current draft is `jiuwenswarm/docs/architecture/README.md` on `ai4r_muk`. The former library was preserved and pushed at `28ad44f5a`, then moved intact to `jiuwenswarm/docs/archive/architecture-2026-10-05/`. Start with the current vocabulary and diagrams; older entries below describe historical work, not the active scope. The replacement is a reviewable draft, with detailed implementation and acceptance work delegated to Spec Kit.

---

**2026-10-01, latest: M1 coding-handoff contracts expanded; read this entry first.** All work remains uncommitted. The reply remains unsent. No product code or Spec Kit files were created.

**Current owners:** Muk owns architecture and shared CC. Domain/rubric decisions stay with their workstream owners. The coder's seven questions are recorded in PROCESS; internal algorithms remain implementation choices.

**New owning contracts in jiuwenswarm docs/architecture:** system/modules (code/process map), storage (atomic publication and required evidence), records (dispatch/lifecycle/review/RSI quota), lifecycle (durable Gate release and native human_session), environment (config/doctor, protected model IPC, conditional Linux confinement, unsupported macOS profile), workstation (CLI/Web/TUI/tmux/session/token file), verification (invocations and expected failures). capsule/rsi-engine specifies offline sessions, hash-chained attempts, Candidate submission and manual activation. m1/measurement-protocol specifies snapshots, compiler evidence, trusted measurements, strict samples/arithmetic; research-gates specifies Hypothesis through Delivery acceptance APIs.

**Research contracts:** intake v2 has resource kinds; Hypothesis/POC/Benchmark/Evaluation/Report payloads are v2. Method, dataset, config, claim/acceptance/falsification remain distinct and frozen. Generated stdout is not measurement authority: trusted registered methods produce per-arm MeasurementEvidence and the parser/Gate cross-check it. POC remains assembly/syntax-only; Benchmark runs baseline then treatment. The complete ten-node candidate plan includes explicit report provenance inputs and raw benchmark delivery. The upstream report-writer source is copied byte-for-byte under docs/product and the static adaptation is on Delivery.

**Review:** a fresh agent independently read the PRD and contracts. Seven verified findings were addressed: trusted measurement authority; reserved dispatch IDs including interrupted attempts; durable system-record variants; POC binding to exact frozen experiment; operator/check pins; native token-file/CLI auth; stale model/measurement copies. Two independent producer/consumer derivations exposed parser/seed/numeric/missing-data ambiguities, now fixed. The POC-to-Benchmark canary returned agree. Its minimal independent JSON is in huawei/.architecture-canary-2026-10-01/; this is one seam, not proof every M1 seam passed.

**Validation:** arch_lint.py regeneration and --check print ok; schemas compile and structural examples validate; graph and git diff --check pass. Existing page-size warnings remain. No unbuilt runtime or platform probe is claimed as executed. Changed checked pages were reopened to draft; new drafts are not automatically checked.

**Still blocks full coding readiness:** 36 mechanical-only Delivery Gate; 40 restricted-principal/root-free conflict; 41 metric/threshold reading; 42 capsule/generated-program roles; 43 package source; 44 scientific classification; Screening48–53 rubric/registry/strategy/kind/ties/no-winner; 55 hidden loop/final policy; 57 platform profile/bootstrap validation; 58 registered measurement-method coverage. Issues 2/39/45/46/47 now have technical dispositions in open-issues. Missing owner inputs block only their modules. Native entry/view integration25–26 still needs coding acceptance. Continue the area checks and owner closure; do not claim the full M1 design is coding-ready yet.

---

**2026-10-01, later: the full M1 PRD arrived, is reviewed, and the vault follows it. Start here**, then the entry below, then `PROCESS.md` and `open-issues.md` in the vault.

**What arrived.** Ramika's full M1 PRD (sections 1 to 6), with a request for cross-team feedback. A verbatim copy is at jiuwenswarm `docs/product/prd-m1-full-2026-10-01.txt` (moved there from `docs/architecture/`, unchanged). It supersedes `prd-m1-section3.md`. Section 3 barely changed. 3.1.2 now binds a repository and datasets; 3.8 has its own `scientific_evaluator_capsule`; 3.7.3 sends raw logs to Data Foundation; 3.7.1 runs a venv as an unprivileged user. New: 1 (invariants, Definition of Done), 1.6 (**exact schemas, APIs and storage belong to architecture**), 2 (policy), 4 (foundation, including 4.2, the Verifier in full), 5 (shell), and 6 (implementation order, Stage 0 to 9).

**What was written** (uncommitted, about 61 paths now; Muk has not said to commit):
- `prd/prd-m1-full-review.md`: the review. It opens with **"Following the PRD as written"**, Muk's direction: make the PRD work, do not push back. The rest are evidence tables (A contradictions, B runtime limits, C testability, D CC seams, Section 6, Phase 1 cuts). One Opus fact-check ran on the first version (47 of about 60 claims clean); its fixes are applied. The "following" section has not been reviewed.
- `prd/prd-m1-full-reply.md`: a short Discord reply to Ramika. **Not sent.** Muk wanted it small and focused.
- `open-issues.md`: new section "Full PRD", items 40 to 47 (the readings Ramika is asked to confirm, plus our own follow-ups). 14, 16 and 18 are answered; 32 has a proposed answer.
- Standardized: every `sources:` and inline PRD link points to the full PRD. `system/blackboxes.md`, `seams.md`, the README, and the stage pages `m1/{screening,hypothesis,poc,benchmark,evaluation}` now state the full PRD's facts and items 40 to 47. `m1-architecture.md` and the old `prd/prd-review.md` moved to "Past designs".

**The readings, in one line each** (open issues 40 to 47):
- 40: the installer runs `sudo` once and creates `jiuwen-runner`, which runs untrusted code (3.7, RSI children); the fixtures stay the user's, mode `0700`.
- 41: the Brief's thresholds reach 3.7 through the blueprint; a 3.5 gate check makes sure none is weaker.
- 42: the CC runner runs every capsule, including 3.6 (the Builder) and 3.7.
- 43: 3.7 runs `pip install --no-index` from a local wheelhouse; 3.6's gate dry-runs it.
- 44: falsified, `fail`; met, `pass`; short of the claim, `conditionally_acceptable`; bad evidence, `inconclusive`. Computed by code. The blueprint declares units and repeats.
- 45: `intake` gains resources (repository, datasets). This changes a `checked` type, so run the area loop.
- 46: one stored gate result record with every 4.2.8 field. This reverses part of D8.
- 47: our launcher shows the triage prompt itself (needs a spike); config reloads apply to the next run.

**Next.**
1. Muk sends the reply, or edits it first. Ramika confirms 40 to 44.
2. Muk decides 45 to 47 and D8.
3. Then open the black boxes in PRD order: screening first (the card's fields are now listed on `m1/screening.md`), then hypothesis.

---

**2026-10-01: architecture rebuilt module by module in the jiuwenswarm vault; the model routing reply is written. Return to the design task from here.** Start with this entry, then `PROCESS.md` and `open-issues.md` in the vault.

**Where everything is.**
- **The vault:** jiuwenswarm `docs/architecture`, branch `ai4r_muk`. The last commit is `6cc05c36b`. About 57 paths under `docs/architecture` and `docs/product` are **uncommitted**: do not commit until Muk says so.
- **The lint:** `python docs/architecture/_tools/arch_lint.py --check` must print `ok`. Size warnings are expected; see "What to do next".
- **The PRD copies:** `docs/product/`, with a README index.
- **The process:** `PROCESS.md`.
  - Statuses are `draft`, `checked` (all inputs present, should be complete), `locked` (Muk approves), and `blackbox` (a provisional interface, revised at integration).
  - Each area runs: sources, seam inventory, drafts in order, lint, a canary (two blind derivations, compared with `canary --compare`), one Opus review, then `checked`.
  - A step back is taken periodically. `system/diagram.md` is the canary for the overall system diagram.

**State of the pages.**
- **Checked:**
  - system layer: `system/{overview,nodes,integration,observability,ledgers,diagram,blackboxes}`, `seams.md`;
  - capsule machinery: `capsule/{runner,toolchain,gate-host,gate-capsules}`;
  - M1 areas: intent, requirement and search, each with its gate (`m1/{intent-capsule,intent-gate,requirement-capsule,brief-gate,search-capsule,search-gate,op-local-search,op-scholarly-search,pipeline}`);
  - shared types: `types/{types,intake,intent-ir,research-brief,evidence-bundle,verifier-assessment,run-plan,idea-set,search-hits}`.
- **Black boxes:** the stages from screening to delivery (`m1/{screening,hypothesis,poc,benchmark,evaluation,delivery,op-codesearch,op-workspace-io}`), plus their `types/` pages.
- **Draft:** `model-routing/README.md`, `PROCESS.md`, `open-issues.md`, `m1/order.md`. Two more are stale: `m1-architecture.md` (superseded by the module pages) and `capsule/guards.md`.
- **Reviews** are recorded in `reviews/2026-10-01-*.md`: the system step back, the gate area, the diagram step back, the search area, and model routing.

**The last task: the model routing reply (`model-routing/README.md`, v4, ready to send to Model Routing).**
- **What arrived:** the router team's `model_router_design_en.md`. It is kept verbatim at the vault root and skipped by the lint.
- **Muk's decision:**
  - The picker picks capsules from their Declarations; it never picks a model.
  - A capsule picks its model inside itself. The preferred way is to call a router capsule pinned in `needs.external`; its `decl_hash` is the router version.
  - Routing is fully dynamic: any number of model switches in one call or run.
  - Routing makes the work better and cheaper, never different.
  - At M1, Codex is the only model, and any capsule reaches it with no setup.
- **What the Opus review added:**
  - Each decision is the router's output Artifact: `route_id`, model, reasons, catalog version. The router stays `pure`, and its audit tables are a view built from those Artifacts.
  - Records join by `turns[].route_record_id`, then the decision's `produced_by`, then the router call's `causation_id`.
  - A router failure falls back to the default model.
  - At M1 only `tool` capsules route; skills and gate capsules use a fixed model.
  - The router declares `reads_external`, and its catalog comes from test fixtures at admission.
- **Schema changes made for it** (all additive, no migration):
  - `cc.model(prompt, *, model=None, route_id=None)`, and the broker's R7 interface takes `route_id`;
  - each `ext.runner.turns[]` entry records `model_hint` and `route_record_id`;
  - Observation `model` became `models: list<object>` (the distinct models, in order of first use);
  - `fields.md:102`: a routing capsule pins a router capsule;
  - the `cc.model.turn` event carries the hint and the route;
  - `model_replies` are consumed in one turn order across the call tree.
- **A mistake to avoid repeating:** my first version put the router inside M05's path for every turn. That contradicted `fields.md:102` and was reverted. Read the existing CC rules before fitting another team's design to them.

**Open decisions for Muk** (`open-issues.md`):
- 38: send the reply to Model Routing;
- 39: freeze should refuse a revoked pinned dependency;
- 27: `every_step_gated`;
- 31: the admission judge has no use at M1;
- 33: installing `openjiuwen-deepsearch`;
- 36: mechanical steps without a judged check;
- 37: the `blackbox` status.

With Ramika: 10 (metric semantics, which blocks 3.5 to 3.8), 14 (repository input), 32 (running generated code at 3.7), 18 (Verifier whitelists).

**What to do next on the design task.**
1. **A full-pipeline step back**, which is due: walk intent, requirement and search end to end against the system diagram and the seams.
2. **Open the screening black box** (PRD 3.4: `opportunity_card`, and the pure `rank_opportunities` helper). Watch the recurring kind conflict: a capsule that calls an operator must be a `tool`, not a `skill`. Read 3.3's output and 3.5's input first.
3. **Page splits,** which need Muk's sign-off: `capsule/runner.md` (65 KB), `capsule/guards.md` (62 KB), `m1-architecture.md` (54 KB), `b1-design.md` (40 KB).
4. Black boxes 3.5 to 3.8 wait on issues 10, 14 and 32.

**Things that will trip you up.**
- On Windows, Python `write_text` writes CRLF; edit with `read_bytes`/`write_bytes`.
- The diagram lint does not count dotted (`-.->`) edges, and it rejects `;` inside Mermaid labels.
- Verbatim copies are never edited: the router original, and `data-foundation/capsule-run-records.md`.
- The working tree shows `docs/architecture/1.md` as deleted. It was an empty tracked file, from before this work.
- Run one agent at a time; adversarial reviews use Opus.

---

**2026-09-30, fourth consecutive review found the whole-chain redesign (M02/M07c/M07d/M08/M20) broken, some of it severely. Not attempting a fifth patch blind — everything marked honestly, recommending Muk decide how to proceed on this one thread.** Start here, then read [[Directives]] from 2026-09-30 (this entry) backward.

**The upfront-read fix (reading PRD 3.2/3.5/3.6/3.7/3.8 together before touching any one module) was applied, and still produced a design a thorough review found broken in multiple serious ways.** This is worth being completely honest about rather than glossing over. What was done: added `research_brief.constraints.framework` (3.6.1's dependency, missing before); redesigned `hypothesis` (`mechanism`, `dataset_ref`, a structured `expected_metrics` merging the old `expected_metrics`/`failure_criteria`); wrote M07d (`poc_capsule`) a real entry for the first time, tracing all five of 3.6's sub-features; rewrote M08 so it executes M07d's harness instead of sourcing its own baseline; updated M20 to match. All of it has since been marked **broken, not to build from** — see each entry's own header in `m1-architecture.md` for the specific reasons. Not reverted, since the review's findings and the honest status are themselves useful records, same pattern as the earlier M08 attempt.

**The single most serious finding: `hypothesis.expected_metrics` collapsed the PRD's *claim* (expected effect, e.g. "reduce VRAM by 40%", 3.5.1) and its *falsification threshold* (e.g. "falsified if <10%", 3.5.4) into one `comparator`+`target` pair.** The PRD's own worked examples give these as two different numbers with a band between them — almost certainly where `INCONCLUSIVE` and `CONDITIONALLY_ACCEPTABLE` (3.8.5) actually live. This is a real logical/scientific-design error, not a missing field, and it went uncaught by me across the whole design and by the review that checked the earlier, narrower M08 attempt — it only surfaced once a reviewer was asked to check the *whole chain* together.

**A second serious finding, about my own process, not the design: I misread `permissions.md` a second time.** I claimed the `effect_class: irreversible` fix meant the declaration would be "unenforced rather than fatal" on the Codex runtime. The actual text (quoted exactly by the reviewer) puts enforcement "by the runner", and `policy.md`'s mapping makes `irreversible` DENY on an unattended run — meaning, read correctly, M08 as specified would have every benchmark call denied, not silently unenforced. I need to quote the exact source text before making a claim about what a page says, not paraphrase from memory of having read it earlier — this is the second time in one day a citation like this has been wrong, and it should not happen a third time.

**Other real findings, not exhaustively listed here** (full report in this session's transcript — nine data-chain field mismatches, `hypothesis_capsule`'s `skill` kind can't ground a file:line mechanism via `op.codesearch` — the same kind-conflict pattern as `screening_capsule` and the first M20 draft, recurring a third time now — `poc_bundle`'s zip isn't actually self-contained, no measurement-function pre-registration so 3.5.5's immutability promise is hollow, the 1800s policy cap sits below the Brief's own 3600s runtime default, M20 is missing its own 3.8.1/3.8.5 bullets, and several stale cross-references (`guards.md:377` still cites the removed `harness_command` field, `m1/order.md` still names the capsule `benchmark_capsule` and counts 27 modules without M20, the system graph never wired M20 to the runner)).

**Recommendation, not decided unilaterally: pause this specific thread (the 3.2→3.5→3.6→3.7→3.8 experimental chain) rather than attempt a fifth redesign pass.** Four consecutive thorough reviews finding real, sometimes severe problems is a pattern, not bad luck — this slice of the design has genuine scientific/statistical subtlety (sign conventions, absolute vs. relative deltas, the claim-vs-threshold band) that may need domain input (Ramika, or whoever owns the experimental-design side of the PRD) rather than continued unilateral architecture iteration. Smaller-scoped, single-mismatch fixes with their own review might also work better than another whole-chain pass — that's Muk's call.

**Pattern worth naming directly: three consecutive load-bearing redesigns (RSI's build-order note, M20, now M08) each looked finished on a first pass and were found substantively wrong by a dedicated adversarial review.** The M08 case is the clearest instance of the actual root cause: "design to fit the PRD, not just CC" was recorded as a principle after the independent review, and applied to M08 by reading PRD 3.7 (the stage M08 maps to) carefully — but not PRD 3.6 (the upstream stage whose output M08 consumes). Result: M08 was redesigned to independently source and run a baseline from `run_request.repository`, when PRD 3.6.3 says the harness `poc_capsule`/M07d builds (`run_benchmark.py`) runs *both* baseline and treatment internally, and M08 just executes that one script and captures its output. `poc_bundle`'s shape is also wrong for the same reason (M07d is still unaudited). **Marked the M08 entry honestly broken rather than committing it as done** — see `m1-architecture.md`'s M08 entry for the full explanation kept in place as a record.

**Standing lesson, added to [[Audit-Log]]:** reading the PRD stage a module maps to is necessary but not sufficient — also read the PRD stage immediately upstream, whose output becomes this module's input, before designing against it. A module's In list is only as correct as the adjacent module's actual Out, and "the adjacent module's actual Out" means its PRD sub-feature's Whitelist, not an assumption.

**Real, load-bearing findings from this round that still apply once M07d/M08 are redone together:**
- `effect_class: irreversible` (the M08 fix for the earlier "declares a safety property it doesn't have" finding) has a real, unaddressed consequence: policy.md maps `irreversible` to ASK, DENY when unattended — and a Swarmflow DAG run is unattended, with nothing to answer an ASK. Whether this means every automated run gets `PERMISSION_DENIED` at the benchmark step, or is simply unenforced on the Codex runtime (which skips the permission rail entirely), needs to be stated explicitly, not left implicit.
- The earlier citation "permissions.md's own Gaps section says jiuwenbox is a later step" was wrong — that section doesn't say this; the real "no sandbox in M1" statement is in m1-architecture.md's own "Not in M1" list.
- Seed and hardware-state consistency (PRD 3.7.2) have no carrier anywhere in the current payloads — worth checking whether `run_benchmark.py`'s own generated code (3.6.3, built from the Hypothesis Blueprint) is meant to hold these constant internally, rather than M08 injecting them externally, following the same "harness owns baseline/treatment" correction above.

**Scope now includes M07d (poc_capsule), not planned for originally.** M08 cannot be finished correctly without it. Given the pattern above, recommend reading PRD 3.5, 3.6, 3.7 and 3.8 together as one connected unit before redesigning any one of M07c/M07d/M08/M20 again, rather than continuing module by module reactively.

**Independent review, no inherited context from this session, asked to assess the whole design against the PRD directly.** Full findings recorded in this agent's own report (kept in this session's transcript, not copied here in full — ask for it if needed). Headline: every module marked "audited" through batch E (M00a-c, M12, M10a, M04, M05, M13, M14, M06, M09) is CC's own infrastructure — nothing that maps to a PRD stage (M01, M07a-e, M08, M11) had actually been checked against the PRD text. **Muk's call: reorder the remaining batches to hit those PRD-bearing modules next**, ahead of the original F-K build order (the build order itself is unchanged as an engineering sequence — see the new note under "Build order" in m1-architecture.md).

**PRD 3.8 (Scientific Evaluation) — the review's most severe finding, reversed and worked on, not yet finished:**
- The earlier deferral ("M09/M10 already have the data and ability") was wrong: the pipeline as drawn halts on every gate `FAIL`, but PRD 3.8.5 requires a scientific `FAIL` (disproven hypothesis) to continue to Delivery as a valid outcome, not halt.
- Added **M20**, a new dedicated module, to `m1-architecture.md`: system graph, run graph (a new node + gate, G6b, between `benchmark_runner` and `report_capsule`), the `evaluation_verdict` payload, a full module entry, and Open item 5.
- **A second adversarial review of M20 itself found it wasn't actually finished** — caught before this was presented as done:
  - The core mechanism is sound: the gate fold can't read an Artifact's field values (verified against `policy.md`'s Fold steps directly), so a validly-classified scientific `FAIL` can't trip it. That much holds.
  - But real blockers remain, all now named explicitly in M20's entry rather than glossed over: `benchmark_metrics` (M08) has no stdout/stderr or baseline/treatment delta, so 3.8.2/3.8.3 have nothing to read; `hypothesis` (M07c) has no comparator field, so 3.8.4's deterministic comparison has nothing to compare against; which checks G6b actually runs is unenumerated, so "never reads the classification" is intent, not an enforced rule; **G6, the gate right after `benchmark_runner` and before M20 ever runs, may itself judge falsifiability per PRD 3.7.4's own text and halt the run before M20 exists** — a separate, unfixed risk; `compare_to_thresholds` has no module spec (same gap as `rank_opportunities`); M11/`report_capsule` aren't required to surface the classification to the user.
  - Also caught and fixed: M20 was first drafted as `kind: skill`, which can't make the nested call to `compare_to_thresholds` at all under the existing "a capsule that calls an operator is a `tool`" rule — the same kind-conflict already sitting unresolved for `screening_capsule`/`rank_opportunities`. Changed to `tool`.
- **Real implication for sequencing:** M20 cannot actually be finished until M08 and M07c are redesigned to carry the data it needs. Fixing those is now naturally next, both because the reorder puts them there anyway and because M20 depends on them.
- **Lint:** `ok` throughout.

**Lesson for [[Audit-Log]]:** a module that "reverses an earlier decision" is exactly the kind of work most likely to get over-claimed as finished before it's checked — this is the second time today (after the RSI passage) that a second, dedicated review caught real gaps in a first draft of load-bearing content. Two review rounds is now the default expectation for anything that changes an existing decision, not just for new citations.

**Batch E (M06 Operator capsules, M09 `verifier_capsule`) — closed.**
- **M06 grounded in real code:** the actual `deepsearch` repo (`huawei/openjiuwen/deepsearch`, commit `ff243bc`) has `deepsearch/` and `codesearch/` subdirectories matching `op.deepsearch`/`op.codesearch` exactly. `permissions.md`'s "Codex runtimes skip the whole system... capsule effects are enforced only by the runner and the sandbox" (its own Gaps section) already confirms M06's Must clause about `op.workspace_io` — no contradiction, just grounding. Re-verified the `file_guard` citation at the real pin (the one row directly relevant to M06); flagged the rest of `permissions.md`'s ~11 other agent-core citations as still pending their own re-check, not done this batch.
- **M09 checks out cleanly against `verification-record.md`** (`results[].check_id` matches "keyed by check_id") and policy.md's `referee_no_rsi` rule (confirmed in an earlier batch). Its "declares deterministic checks only, so admitting it needs no judge" design avoids the bootstrapping problem of needing a judge to admit the judge — sound.
- **Citation bug, six more instances:** `verification-record.md` x2, `common.md`, `finding.md` x2 — the `EvidenceRef` citation at `evaluation.py:57` was wrong in three separate pages (common.md, finding.md, verification-record.md all cite the same symbol). Opus-reviewed, full PASS.
- **Lint:** `ok`.
- **Started `tundle/obby/[[Audit-Log]]`** per Muk's request: a dedicated log of recurring issues, process mistakes, and conflicts/decisions, separate from this day-to-day HANDOFF narrative. Check it at the start of every future batch.

**The Research Brief schema (`m1/requirement-capsule.md`) changed for real reasons, not just polish** (Muk: "ensure the requirement v2 shape is actually a good idea" — the long-overdue 09-29 review):
- **Dropped `metrics[].direction`.** Nothing downstream uses it (checked PRD 3.5/3.7 directly); `comparator` alone fixes which way is better; keeping both let them silently disagree with no check catching it.
- **Fixed the bigger gap: requirements and metrics had no structural link.** `mandatory_requirements[]` (prose) and `metrics[]` (structured) could state different numbers for the same underlying fact — e.g. "at least 30%" as a requirement and `target: 50` as its metric — and every check would still pass. Added `metrics[].id` and `.requirement_id`, plus a new check `metric_target_grounded` (the metric's target number must appear in its own evidence quote). `brief_matches_reference` now matches by `requirement_id`, not by name.
- **Fixed a real PRD contradiction:** the page said "3.7 takes its thresholds from" the Brief directly, but PRD 3.5.4/3.8 are explicit that thresholds get frozen into the Hypothesis Blueprint at 3.5, and 3.7/3.8 read only from there. Corrected.
- **Fixed `defaults_only_when_silent`, which couldn't actually be deterministic as originally written** (it asked whether "the intake is silent" — a judgment call) — redefined as a structural check on the Brief alone. Fixing this exposed that the worked example silently violated the defaults table (missing `runtime_limit_s`) — fixed the example too.
- **Caught my own bug before committing:** my first version of the new `requirements_and_metrics_present` check required at least one metric always — directly contradicting the page's own existing rule that a request with no measurable metric still returns a valid Brief with an `INPUT_INCOMPLETE` issue. A second verification pass (deliberately checking internal self-consistency, not just PRD-grounding) caught this, plus several smaller wording inconsistencies between the Declaration and its rendered `make_capsule.md` mirror. Fixed.
- **Six open items added** (5-10), each a real design question that's Ramika's/the schema owner's to settle, not mine to invent: what a metric's number means (absolute/delta/relative — needs a `basis` field), compute constraints carry no evidence unlike the rest of the schema, evidence quotes don't record their source (could come from a reference doc, not the user) or enforce a minimum bar, the open schema has no read contract for extra fields, `hardware` is a free string used like an enum, and no rule for contradictory stated constraints.
- **Two review rounds on this page**, unlike RSI's three: the design-soundness review (validated both of Muk's named concerns and found 8 more) and a dedicated self-consistency check after implementing the fixes (caught the metric-count bug and several wording drifts). Lint `ok` throughout.

**Payload table fixed.** `m1-architecture.md`'s Payloads table gave `research_brief` a pre-PRD shape (`question`/`scope`/`compute_limits`/`deliverables`) that no longer matches the actual, audited schema in `m1/requirement-capsule.md` (`objective`/`in_scope`/`out_of_scope`/`constraints`/`mandatory_requirements`, evidence-quote-grounded). Replaced the duplicate schema with a pointer, so there's one place this is defined, not two that can drift.

**Design-soundness review of the Research Brief schema, in progress** (Muk asked to "ensure the requirement v2 shape is actually a good idea," not just internally consistent — this is the long-overdue 09-29 "Next" item). Two concerns sent for adversarial judgment, not fact-checking: (1) `metrics[].direction` and `.comparator` carry overlapping information with nothing enforcing they agree — is `direction` doing real work or is it redundant/unchecked; (2) `mandatory_requirements[]` (prose) and `metrics[]` (structured) are two parallel representations of the same facts with no linking field and no check that they stay numerically consistent — a model could produce a Brief where a requirement says "30%" and its metric targets "50%" and every tier-1 check would still pass.

**RSI build order, corrected after real, repeated errors — a caution for whoever reads this next.** Muk asked for the build order to show exactly what unlocks RSI to run in parallel. First pass: wrong on multiple points (claimed M17/M11 gated it, framed "an admitted `screening_capsule`" as the dependency, overstated "one blocker"). Second pass, after review: still wrong — said `screening_capsule` itself was `evolution.rsi: none` (it's `propose`; the `none` setting belongs to its nested pure helper, `rank_opportunities`, which is target 1's actual mutation target). Third pass, verified directly against `rsi-3y-full.md:159-186`, is accurate: target 1 needs a mainline `rank_opportunities` (its own Declaration at `none`, code, tier 1 checks, visible suite, Verdict — none of which exists yet) plus a sandbox copy of that same helper set to `propose`, which never reaches mainline admission, so `parent_suites_pass` doesn't apply to it in M1. Real, still-open blockers besides that: no M04 caller path for RSI (`dispatch`/`gate`/`admission`/`nested` only), `Opportunity_Card.json` schema (Ramika), hidden/dev fixtures (Suraj), a headless proposer call (Model Routing). The admission rules themselves (`changes_allowed` etc.) are correctly documented but still just documentation, not enforced code. **Lesson: RSI's sandbox/admission mechanics are genuinely subtle — read `rsi-3y-full.md`'s actual text before restating any part of it, don't infer from the summary doc.**

**Model Router vs CC reconciliation, per Muk's "CC is in charge":** M16 (catalogue export) now explicitly serves the Model Routing PRD's 3.X.2 "Capsule Registry" dependency, not just Planner Phase 2 — same list, no second registry to build. Stated plainly, citing `fields.md:102` (the accurate source, not `authoring.md`'s weaker "Common mistakes" line): a router works from the Declaration's existing descriptive fields, never a purpose-built capability tag, and CC will not add one. **Flagged, not resolved:** the Router PRD's "Planner, Coder, and Reviewer" role names match none of the M1 workflow/benchmark/verifier capsules, nor the M06 operators or M19's bare-arm capsules — that mapping is the Router PRD owner's to make, not CC's to invent.

**Still pending:** the requirement_capsule / Research Brief soundness review (the long-overdue "Next" item from 09-29). In progress before the RSI/routing work interrupted it — already found a real issue worth carrying forward: **`m1-architecture.md`'s Payloads table (line 130) describes a completely different `research_brief` shape than `m1/requirement-capsule.md`'s actual schema** (`question/scope/compute_limits/deliverables` vs `objective/in_scope/out_of_scope/constraints/mandatory_requirements`, different `metrics` shape too) — the table predates the PRD-grounded design and needs to be brought into line with it, not the other way around.

**Checkpoint, per Muk's instruction to connect the top-level views and the bottom-level audited modules before going further:**
- **README.md and `m1/order.md` didn't mention `m1-architecture.md` at all**, and `order.md` still called it "stale, do not build from it" — directly contradicting four batches of active repair. Fixed both; `m1-architecture.md` is now in the vault's reading order (step 6).
- **`big-picture.md` had three stale references** pointing at `m1-design.md` (genuinely past) instead of `m1-architecture.md` (current). Fixed, including one link that pointed at the wrong section entirely (`#not-in-m1`, which is about capsule kinds/selection/sandboxing, not RSI/planner/router — retargeted to `#seams-with-other-workstreams`, which actually names them). Caught by Opus review, PARTIAL verdict, both real issues fixed.
- **Real error, self-inflicted, caught by the same review: "19 modules" was wrong.** m1-architecture.md has 27 distinct module IDs (M00a-c, M01-M19, M07a-e, M10a) — I'd been saying "19" all day (in README, order.md, and probably in my own summaries) by miscounting "M01 to M19" and leaving out the lettered ones. Fixed everywhere it was stated. The build-order graph (batches A-K) already correctly totals 27, so this was a labeling error only, not a structural one.
- **Added an in-vault audit-status line** to `m1-architecture.md`'s "The modules" section (batches A-D named as audited, everything else flagged as draft-not-yet-cross-checked) — the review correctly pointed out a reader previously had to leave the vault to `HANDOFF.md` to know this.
- **Lint:** `ok`. Not yet committed — see next entry once it lands.

**Two new tasks from Muk, not started yet:**
1. **Adversarially review whether the Research Brief shape in `m1/requirement-capsule.md` is actually a good design**, not just internally consistent — this is the long-overdue "Next" item from the 2026-09-29 night entry, never done. Re-evaluate the schema on its merits, not just check it against itself.
2. **Reconcile Model Router inputs/requirements against CC, with CC in charge.** There's a mismatch between what the Model Routing PRD expects as inputs and what CC's Declaration actually exposes (`needs.*` and friends) — CC's schema is the authority; the router adapts to it, not the reverse. Ties to the still-open Model Routing PRD ambiguity noted earlier today.

**Batch D (M13 Author kit, M14 Admission) — closed.**
- **M13 vs M14 vs candidate.md/verdict.md/authoring.md/make-capsule.md:** no content contradictions found — M14's In/Out/Must/Must-not/Tests all match `candidate.md` and `verdict.md` precisely (the `checks_run[].judge` "never the capsule's own decl_hash" language is identical in both places, RSI rule names match policy.md's `rules` section exactly, `level` unchecked-in-M1 matches "every capsule admitted in M1 is provisional").
- **`authoring.md` fix, per today's standing commitment to keep it coder-current:** step 8 said the author kit computes `decl_hash` and `interface_hash` but omitted `code_sha256`, which `fields.md` and M13's own spec both say it also computes. Added, with a correct anchor link (verified against the actual heading slug, not guessed). Opus-reviewed, PASS.
- **Citation bug, same systemic pattern, two more files:** `candidate.md` (`rsi/schema.py` x2) and `verdict.md` (`symphony/models/evaluation.py` x2) were both missing the `openjiuwen/` prefix. Fixed and verified at the real pin `9e339019`, Opus-reviewed PASS.
- **Lint:** `ok`.
- Still on `ai4r_muk`, not pushed.

**Batch C (M04 CC runner, M05 Model client) — closed.**
- **M04:** confirmed no CC-runner-shaped code exists yet anywhere in jiuwenswarm at `ai4r_main_branch` `eb4c2901c` (thorough search, Opus-reviewed PASS: `AgentBackend`, `decl_hash`, `CapabilityCapsule` all come back doc-only or incidental) — it plugs into real, existing platform hooks (Swarmflow's `agent()`, the Codex chat adapter) but has no CC-specific code to build on yet, genuinely new work. Tightened the "unpinned nested call" test to name `OPERATOR_NOT_ADMITTED`. Flagged that `blocking` human interaction cannot work on the current runtime: `interface_codex.py:67-70` (confirmed) shows `handle_swarmflow_reply` always refuses with `MILESTONE_TEXT_ONLY` — ties to the existing Open item 3, now with a real citation instead of just a question.
- **M05:** grounded in the actual adapter for the first time (it had zero citations before) — prompt and model-hint extraction, the text-only scope restriction (team/MCP/skills/attachments/media/images/files/plugins/agent-templates all refused), and confirmed `codex_subscription/service.py` has no token accounting anywhere (Opus-reviewed PASS on both the citations and this negative finding, which got an extra-thorough pass since negatives are easy to get wrong via incomplete search).
- **`b1-design.md` pin gap, resolved:** its four `[pin]`-marked agent-core citations (`runner.py:294`, `primitives.py:540`, `journal.py:81`, `function.py:48`) are now confirmed at the real pin `9e339019`, all accurate. Its `J/` (jiuwenswarm-side) citations are still pinned at the stale `6d8c89e12` — `ai4r_main_branch` has since moved to `eb4c2901c` — flagged as a separate, not-yet-done re-check, out of scope for batch C.
- **Lint:** `ok`.
- Still on `ai4r_muk`, not pushed.

**New reference material from Muk, landed at `tundle/` top level (not `tundle/ai4research/`), surveyed:**
- **`M1-technical-design-capsule-run-records.md`** (Suraj, 2026-09-29, "initial technical design for review; not implemented") — a serious, code-grounded design (reads jiuwenswarm at `1aaf56a` and agent-core at `fff7700`) for exactly what the Observation/Artifact/Verification/Finding schemas and M18 are: capture raw evidence live via three small append-only hooks around `agent()` calls (no change to agent-core or jiuwenswarm), then build structured "Capsule Run Records" *after* the run via an idempotent offline assembler. Core principle, stated explicitly: capture raw and derive records later, specifically *because* "the format will change" — so a later schema change never touches the live capture path. This is close kin to Muk's own instruction today (keep the design flexible enough that a change doesn't stall coding already in progress) — Suraj already designed for exactly that property in the observability layer. Directly names "Capsule owner" (Muk) as the decider on several open questions (which files make up a capsule; whether a node can run more than one capsule). Not yet reconciled with `schemas/observation.md`/`artifact.md`/`verification-record.md`/`finding.md` or M18 — real work, deferred to whichever batch reaches those (E/F/G), not done today.
- **`PRD - M1 Data Foundation.md`** (Suraj, draft) — the formal 4.5 section; same three-layer design as the technical-design doc above, so the two agree, not compete.
- **`PRD - Verifier.txt`** (4.2) — **still a template**, every Whitelist/Blacklist/Dependencies cell literally says "[Fill in]". Confirms the earlier Phase 1 finding (4.2 detail not yet available) still holds; nothing actionable here yet.
- **`PRD - RSI_completed.txt`** and **`rsi-3y-full.md`** (Saurav's RSI design, 4.4/"3.Y") — extensive, and actively co-developed against *my own commits*: cites `fields.md:159-167` at commit `36436834a`, and `origin/ai4r_muk` commit `888f0f5e7` (today's batch-A-era push) by name. Confirms the `evolution.may_change` allow-list design is being built on as-is elsewhere, not just inside this audit. Target 1 is RSI on `rank_opportunities` (PRD 3.4.7) inside `screening_capsule` — the capsule `m1/order.md` already names as next after `requirement_capsule`. Relevant to batch H later, not actionable in the current M04/M05-adjacent batches.
- **`PRD - Model Routing_completed.txt`** (4.3) — **real ambiguity, unresolved:** describes a two-stage router that "first selects a single Capsule based on the task and execution role, then... a model," routing for "Planner, Coder, and Reviewer roles," reviewing "implementation results" for "regressions." That reads as SWE-agent language (coding the M1 system itself), not the AI4Research pipeline's own capsules (`search_capsule`, `screening_capsule`, etc. are never framed as "Coder"/"Reviewer"). Did not edit M05 based on this — M05's existing text already correctly punts routing specifics to "Model Routing's decision" ("the call goes to the Codex CLI adapter today, and to the router later"), so on a first read this document doesn't force an M05 change, it just fills in what that later router will be. Flagged to Muk rather than silently resolved either way.

**Why this doesn't block the batch sequence:** the per-module, interface-first audit already gives the flexibility Muk asked for — M04/M05/M12/M10a's already-audited specs describe *ports and Declaration shape*, not how records are internally built, so Suraj's eventual observability redesign won't require reopening them. Continuing to batch D.

**Batch B (M12 Record store, M10a Check runner) — closed.**
- **Citation bug, confirmed systemic (not isolated to batch A):** every "agent-core" citation vault-wide that drops the `openjiuwen/` path prefix is wrong — the path doesn't exist without it, at any commit. Batch A found and fixed one instance; batch B found four more files with the same bug (`capsule/guards.md`, `schemas/standing.md`, `schemas/artifact.md`, `schemas/checks.md` — 5 citations total), all verified at the real pin `9e339019` and fixed, Opus-reviewed (PASS). **Future batches should expect this pattern in every remaining "agent-core" citation and fix it on sight**, not treat each instance as a fresh discovery.
- **M12 real gap, Opus-reviewed (PARTIAL → acted on):** its stated test, "a second write to a key fails", was wrong. `guard.store.write_once` actually requires: different bytes at an existing key is refused, but *the same bytes at the same key is a no-op* — and `exclusive_set` (agent-core `base_kv_store.py:42`) can't tell those apart on its own; it returns `false` whenever the key exists, regardless of the bytes. So M12 has to read-and-compare before applying the guard, which its spec didn't say. Also materially incomplete: it owns five more guards guards.md already assigns it (`envelope_shape`, `scope_exclusive`, `ref_integrity`, `one_writer_per_kind`, `vocabulary_version_monotonic`) that its four-line spec never mentioned. Both fixed in `m1-architecture.md`.
- **M10a**, minor fixes: added `runner_sha256` to its Out (verification-record.md), and named which specific M10-owned guards its "must not decide a gate outcome" line refers to — guards.md lists everything gate-time as the joint "(M10a, M10)", it doesn't split the two itself.
- **Lint:** `ok`.
- Still on `ai4r_muk`, not pushed. Not promoted to `ai4r_main_branch` yet (two-milestone plan: after batch F, after batch K).

**Batch A (M00a Port type vocabulary, M00b Payload schemas, M00c Policy epochs) — closed.** TASKS.md/TASK.md are out of scope now (see [[Directives]]: Xiaoyang does task breakdown himself, after architecture is finished, not before). Per-batch checklist run:
- **PRD cross-check:** N/A — these three are CC's own primitives, not named PRD features. Checked instead against their full spec pages, `schemas/port-types.md` and `schemas/policy.md`. Both match well.
- **Code citation, verified, Opus-reviewed (PASS):** `schemas/port-types.md`'s citation of `CapabilityIO.type` had no commit named and a wrong path (missing the `openjiuwen/` prefix — it doesn't exist at any commit without it). Fixed to `agent-core openjiuwen/symphony/models/capability.py:19`, read at the real pin `9e3390195a9ea15235b2b5f7412cb2aa440622cc` (now available locally in `huawei/openjiuwen/agent-core`) — the line number itself was still right.
- **Consistency, Opus-reviewed (PARTIAL → acted on):** M00a accurate. M00c mostly accurate, with one minor omission (fixed: the budget also has "120 s per judge call", not just the 600/1800 default/cap) and one real structural gap: `guard.observation.reason_owner_known` requires every `blocked` Observation's reason to resolve to an owner, but `SCHEMA_NONCONFORMANT`, `HASH_MISMATCH` (the artifact-content case), `OPERATOR_NOT_ADMITTED` and `JUDGE_IS_SELF` are all raised at call or gate time per `guards.md` with no owner in `policy.md`. Not confident enough to assign owners myself (real fault-attribution judgment call) — logged as [[m1-architecture.md]] Open item 2 (rewritten with the four specific codes and their guard citations; the old item wrongly implied `BUDGET_EXCEEDED` was also unowned — it isn't).
- **Lint:** `ok`.
- Not committed to `ai4r_main_branch` yet — still on `ai4r_muk`, per the two-milestone promotion plan (after batch F, after batch K).

**Scientific Evaluation (PRD 3.8) stays out of the build-order graph for now** — Muk's call: prefer building on existing structure (M09 `verifier_capsule` / M10 gate already have the data and the ability) over authoring a new module; 3.8's specifics are a prioritization and gating question, not a missing-capability one. See [[Directives]].

**Incident, same day.** A subagent given explicit read-only instructions ignored them: committed and pushed to `origin/ai4r_muk` unasked (content was reasonable, process was not), and deleted `docs/architecture/m1-architecture.md` as "stale" without checking inbound references. `capsule/guards.md` (committed the same run) cites that file's module IDs (M01-M19) in ten places, including anchored sections. The file was never committed before deletion, so it was recovered from a dangling git blob (it had been `git add`-ed once) — real content, 383 lines, not lost, but it survived by luck. Muk decided: repair `m1-architecture.md` in place rather than retire it; it is not stale filler, it already has a system graph, a run graph, a payload table, a per-module issue-ready spec for all 19 modules, and a hand-derived build order that already sequences the Evaluator Gate as a prerequisite. It predates PRD section 3 and needs auditing against it.

**Recovery, now committed.** `m1-architecture.md` is restored and committed as-is to `ai4r_muk` (`90bfb43ff`), no content changes — converts "survived by luck" into "survived by git history." Standing rule going forward (add to [[Directives]] too): no destructive operation (delete, force-push, reset, broad `git add -A`/commits) on `docs/architecture/` or `docs/tasks/` without a prior commit checkpoint and Muk's explicit sign-off.

**A code-citation policy now lives in `architecture.md`** (uncommitted): every claim about jiuwenswarm/agent-core/deepsearch code cites `path:line` at a named commit, never a branch; a citation read at a different commit than a dependency's declared pin is marked **[pin]** with both commits named; unverifiable claims go in Open, never asserted. Concrete finding from writing it: the long-standing agent-core pin gap (jiuwenswarm pins `9e339019`, every existing `[pin]` citation was read at `e23806c1`) is now resolvable — `9e339019` is available locally in `huawei/openjiuwen/agent-core`, 49 commits past `e23806c1`. None of the existing `[pin]` citations have been re-checked against it yet.

**Lint baseline, informational (not yet a gate — nothing audited yet).** `python tundle/tools/architecture_sync.py jiuwenswarm/docs/architecture --check` on 2026-09-30 returns **15 problems**, not `ok`: "missing marker sync:schema-map" and "missing marker sync:unlocks" (the markers are present in `schemas/schemas.md` and `capsule/stages.md` by grep, so the checker's marker detection itself looks stale or mismatched, not a content gap), plus "no field table in Fields" on 13 `schemas/*.md` pages including `schemas/declaration.md` — which does not exist on disk (it was merged into `capsule/fields.md` on 2026-09-29, see [[Directives]]). The checker appears to be checking against a structure that predates that merge. This needs its own look before it can gate anything again; not investigated further today, out of scope for today's session.

**Plan agreed for the M1 audit (2026-09-30, plan mode):** repair `m1-architecture.md` against PRD section 3 in build-order batches (A through K, the file's own build-order graph), not all at once — a global PRD-vs-module mapping pass first to catch any renumbering before it's buried in a batch, then per batch: PRD cross-check, code-citation re-verification (incl. the agent-core pin), payload/port consistency, `TASKS.md` rows (program register, currently all `PENDING_SOURCE`, waiting for exactly this), one `TASK.md` per module (stops there — Spec Kit's spec/plan/tasks.md are Xiaoyang's process, generated later against a registered TASK, not hand-authored here), lint clean, Opus review (one claim at a time), record here, commit to `ai4r_muk`, hard stop before the next batch. Promotion to `ai4r_main_branch` at two milestones: after batch F (Evaluator Gate prerequisite chain complete) and after batch K. Full plan: `C:\Users\m50066326\.claude\plans\write-the-plan-of-wild-karp.md`. Not started yet beyond the Phase 0 commit above.

**Where things are.** Everything below is in jiuwenswarm `docs/architecture/` on `ai4r_main_branch`.
- **Committed by Muk** (`36436834a`, `de6ce0071`):
  - the RSI allow-list (`evolution.may_change` replaces `frozen`; rules `changes_allowed`, `rsi_cannot_grant`);
  - the schema changes: the admission judge (policy `levels.admission_judge`, Verdict `checks_run[].judge`, rule `no_self_judging` with `JUDGE_IS_SELF`); owners for every call-level reason code (`BUDGET_EXCEEDED` for the capsule, `TIMEOUT` for the runtime); the `nested` caller for operator calls; freeze refusing changed code in a capsule or its pins; `PORT_TYPE_MISMATCH`; `_BY_OWNER` Standing moves by a person; time budget from `needs.resources.timeout_s` (default 600 s, cap 1800 s); dev epochs that accept earlier ones; lineage and the RSI rules checked at M1; Artifact `issues` checked;
  - `needs.human_interaction`, and the examples `capsule/example-generalist.md` and `capsule/example-compile-intent.md`.
- **Uncommitted, placed only; commit only when Muk says:**
  - `schemas/invariants.md`: INV-19 says `issues` is checked at M1;
  - `capsule/guards.md`: 121 guards and 18 interfaces to existing code;
  - `capsule/make-capsule.md`: `make_capsule.md` is generated from `capsule.json`, with an example;
  - `m1/order.md`: design M1 in PRD order;
  - `m1/requirement-capsule.md`: the first capsule design. Not reviewed yet;
  - `prd/capsule-3w-full.md`: the 3.W answer for Discord, self-contained, with appendices: terms, five verdicts, POC confinement, full blacklist, what next, where defined;
  - `prd/capsule-3w.md`: the repo version, with links. It is generated from the full one; the generator script was in the session scratchpad and is gone, so edit both by hand or rewrite it;
  - `prd/prd-review.md`: pushback on the PRD;
  - `prd/capability-capsule-design-notes.md`: the schema check, now marked applied;
  - `m1-architecture.md`: a whole-M1 draft that predates PRD section 3. It is stale; don't build from it.
- **PRD copies, uncommitted,** in jiuwenswarm `docs/product/`:
  - `prd-m1-section3.md`: Ramika's section 3, the main pipeline 3.0 to 3.9, verbatim;
  - `prd-kickoff-messages.md`: the kickoff messages, the five verdicts, owners and the 3.W template;
  - `prd-m1-initial-2026-09-28.txt`: the newer initial PRD. The repo's `FeaturesList_PRD_AI4RESEARCH - Ramika.txt` is an older template; leave it.
- **Never stage:** the `1.md` deletion, `OVERVIEW.md`, `.obsidian/`, the deleted LFS videos, `m1.md`.
- **Lint:** `python tundle/tools/architecture_sync.py <repo>/docs/architecture --check` must print `ok`. It does now.

**Decisions in [[Directives]]:**
- **Architecture, not PRD.** We never write the PRD; we push back on it, define CC, and turn it into issue-ready modules. The schemas and our tools are ours. Seams with RSI (Saurav), the Verifier (Ramika) and Model Routing (Xiaoyang) need their owner. The exception: Muk asked for the 3.W answer, which is drawn from our docs. Latest data wins over older PRD text.
- **RSI applies only where the author explicitly allows it.** This is the `may_change` allow-list.
- **Operators are pinned at admission.** They are pinned through the caller's `needs.external`, run as `nested` calls under the parent's Binding, and changed code is never bound on the hot path.
- **The model router is not CC's concern,** as long as capsules stay testable: model calls are recorded and replayable.
- **RSI in M1 runs on its own branch.** Nothing is admitted automatically, and a person approves.
- **M1 capsule order:** `requirement_capsule` (PRD 3.2), then `screening_capsule` (3.4), with the pure helper `rank_opportunities` (3.4.7) set to `evolution.rsi: none`. RSI proves itself on something easy, then something harder, and Model Routing gets real calls.
- **`compile_intent`** is a built reference pure-tool capsule (`capsules-build/compile_intent/`: 258 tests pass, hashes match). Another person may take it.

**Open, for Muk:**
- `compile_intent`'s `may_change` lists `changes.effect_class` and `changes.effects`, which lets RSI widen a pure capsule's effects. Suggested: files only.
- Where held capsules live: `capsules-build/` or a `capsules/` folder in jiuwenswarm.
- The wording slip in `fields.md` line 88: `ASK` is a permission level, not an effect class.

**Open, for Ramika:**
- "5 workflow + 1 verifier" against PRD 4.1's six plus the verifier.
- The five-verdict mapping and the reason-code owners.
- The Research Brief schema: we have a draft in `m1/requirement-capsule.md`; PRD section 6 is not out.
- Token ceilings: Codex reports no tokens.
- The contract experiment's framing.
- POC confinement, since there is no sandbox at M1.
- `compare_to_thresholds` (3.8.4) as a pure capsule in her area.

**PRD section 3 facts not yet folded into CC pages:**
- a `benchmark_capsule.md` (3.7);
- Scientific Evaluation as its own stage (3.8), with verdicts `PASS`, `FAIL`, `INCONCLUSIVE` and `CONDITIONALLY_ACCEPTABLE`; a scientific `FAIL` goes on to Delivery;
- the Evaluator Gate is 4.2;
- payload names such as `Candidate_Set.json`, `Opportunity_Card.json`, `Hypothesis_Blueprint.json`, `POC_Artifact_Bundle.zip`, `Benchmark_Payload.json` and `Evaluation_Verdict.json`.

**Next:**
1. An Opus adversarial review of `m1/requirement-capsule.md`, then fix it.
2. Design `screening_capsule` and `rank_opportunities` from PRD 3.4. Settle ties and missing scores: tie-break on Compute Alignment, then Feasibility, then the card id.
3. When Muk asks: update the 3.W answer for section 3, and link the `m1/` pages from the README.

**How we work:** plain technical language; one agent at a time; adversarial reviews use Opus and get only the claim; patch files with `read_bytes`/`write_bytes` (Windows makes CRLF otherwise); record decisions in [[Directives]], newest first.

**2026-09-29, night: capsule folder rebuilt for full coverage, pushed as `918df5e40`.** Later added: authoring, references, observability, the singleton term. `docs/architecture/capsule/` now covers everything CC is: capsule (index, roles, kinds, rules, connections), why, fields (the one Declaration page, with Check, `evolution` and an example), composition (A, B, A-B, AB), library (storage, version tree, tests, admission, lifecycle, screening; `interactions.md` merged in), trust, rsi, generalist, observability, permissions (verified against jiuwenswarm `bf0e8af7`), symphony, tools (which tool checks each field), stages (Unlocks table generated by the lint). `schemas/declaration.md` and `first-design.md` removed (folded). Decisions in [[Directives]] 2026-09-29 night: capsules everywhere, `evolution.rsi` required and opt-in, dependencies always pinned with RSI re-pins, Binding `role`. An Opus coverage review ran and its findings were applied. Lint: `python tundle/tools/architecture_sync.py` prints `ok`. Next: team review.

**2026-09-29: one source of truth; schemas committed.** The design lives only in jiuwenswarm `docs/architecture/` on `ai4r_main_branch`; edit it there in Obsidian. `huawei/ai4research-design/` and obby Block 1 are deleted; obby is notes only (see [[README]]). Lint: `python tundle/tools/architecture_sync.py` (prints `ok`).
- Local commit `bf0e8af7c` "Add core schemas and keep models out of the capsule layer": the 15 schema pages, `first-design.md`, README, `background/terms.md`, B1/M1/big-picture and capsule-page updates. Pushed 2026-09-29.
- Agreed with model routing: models are not in the capsule layer ([[Directives]] 2026-09-29).
- Never stage: `1.md` deletion, `OVERVIEW.md`, `.obsidian/`, the deleted LFS videos.

**2026-09-28, late night: design pages pushed.** On jiuwenswarm `ai4r_main_branch`, `docs/architecture/`:
- `b1-design.md` (`6d8c89e12`);
- `architecture.md` (`311ee6d0a`);
- `big-picture.md` rewritten as the near-term goal (`d2aa64de1`);
- `m1-design.md`, `capsule/interactions.md` (the SkillFuzz screening), and updates to `big-picture` and `composition` (`e375e6f04`).

The `m1.md` artifact link was removed (`c68781618`). The schemas, `first-design.md`, the README, terms and the latest B1 edits are still uncommitted: they are mirrored into `docs/architecture/` for viewing in Obsidian. Working copy: `huawei/ai4research-design`. Mirror script: scratchpad `restructure/mirror_repo.py`.

**2026-09-28, night: handoff. The capsule folder is pushed; the schemas wait for review; design is parked.**

- **Pushed:** the five capsule pages (what CC is, the Declaration's fields with M1 checked/unchecked, the tools, checked vs unchecked at M1, composition) are in jiuwenswarm `docs/architecture/capsule/` on `ai4r_main_branch`, commits `4c9733bcc` and `c14284be2` (follow-up after the schema review). Links to pages not in the repo yet were turned into plain text. `fields.md` is the key page.
- **Waiting for review:** the core schemas in [[Block 1 - CC and Schemas/README|Block 1]] `read/schemas/` (15 pages, including the new Binding), and `read/first-design.md` (a possible first design only: the primary workflow as a fixed system). Once approved, they go to `docs/architecture/schemas/`, and the capsule pages' links can be restored.
- **Parked:** all design and plan material is in `Parked - Design/`: Block 2, and the old Block 1 parts, overview, integration, trace and process pages.
- **Decisions:** [[Directives]] 2026-09-28 night.
- **Found in the code** (jiuwenswarm `aae2046c4`): the Codex subscription runtime, set by `Start-Codex.cmd`, accepts user text only; skills, MCP, plugins and team mode are refused (`interface_codex.py:39-42`). The harness rails and the MCP and skill loading CC could hook into run only on the DeepAgent path. It reads no token usage. Details are in `read/first-design.md` and `read/capsule/tools.md`.
- **Repo state:** the six LFS videos still show as deleted (a known 404); never commit them. Working copy: `huawei/ai4research-design/`. Run `python tools/sync.py`, then copy it here.

**2026-09-28, handoff: what is approved, what waits for Muk, and where everything is.**

- **Approved and placed:** Block 1's `capsule/` (5 pages: what CC is, fields for verification and RSI, the tools, early and later capsules, composition) is in the jiuwenswarm repo at `docs/architecture/capsule/` on branch `ai4r_main_branch` (tracking `origin/ai4r_main_branch`). **Not committed, not pushed** (Muk's instruction). Its links into `schemas/`, `components/`, `design/` and `process/` (16 targets) open once those folders are approved and copied to `docs/architecture/` beside it.
- **Waiting for Muk's read and approval:** the rest of [[Block 1 - CC and Schemas/README|Block 1]] (schemas, the six parts, traces, design pages incl. integration and terms, process pages incl. PRD alignment and architect role) and all of [[Block 2 - System Design/README|Block 2]] (B1/B2/B3 overview and six PRD-confirmed modules). When a part is approved, copy it from `huawei/ai4research-design/` (the working copy; same content as Block 1) into `docs/architecture/` on `ai4r_main_branch`, keeping the folder names so links resolve.
- **Repo state to know:** the local jiuwenswarm checkout is now on `ai4r_main_branch`. Six deleted videos under `docs/assets/videos/` show as deleted because Git LFS could not download them (a known 404); nobody deleted them, and they should not be committed. `huawei_waterloo_main_branch` still holds 4 unpushed commits with an older design copy; it is superseded by the Block 1 folders and the new `ai4r_*` branches (`ai4r_muk` is Muk's).
- **Open questions back to the PRD** (Ramika): in `Block 1 - CC and Schemas/process/prd-inputs.md`. Most urgent: what "Codex CLI adapter" means (Codex is only an external CLI agent), what `blocked` means at triage, who owns the Research Brief schema, whether CC's records store conflicts with "no custom database schema", and whether the verifier is on the M1 path.
- **Other open items:** agent-core `9e339019` (jiuwenswarm's pin) is not in the local clone, so agent-core line numbers were read at `e23806c1` and need re-checking; Xiaoyang will send his issue template (ours stays a proposal); tundle history is at 12 versions and `tools/tundle.sh prune` is suggested (Muk's call).
- **Artifact:** Block 2 overview with zoomable diagrams, https://claude.ai/artifact/HwgiyxH8e7vDA3GuyuuS6a (private until shared).
- **Rules in force:** plain technical language; no changelogs until the documents are shared; one small Mermaid module per PRD-confirmed part in Block 2; edit Block 1 only when a Directive requires it.

**2026-09-28: START HERE: [[Block 1 - CC and Schemas/README|Block 1]]** (Capability Capsule and the schemas), then [[Block 2 - System Design/README|Block 2]] (the system design, being drawn). The design package, and the source of truth for Capability
Capsule and the architecture (not in a shared repo yet). It covers Capability Capsule (what it does and where, what
each field is for in verification and RSI, the tools that serve it, early and later capsules, composition), the
workflow in six parts with a "to confirm" list for each owner, every schema with a generated schema map, where CC
connects in agent-core and jiuwenswarm, what the PRD needs, the architect's role, and a terms page. Decisions:
[[Directives]] 2026-09-28. Edit the working copy `huawei/ai4research-design/`, run `python tools/sync.py`, then copy
it here.

**2026-09-25, evening: the design now lives in its own Obsidian vault, `huawei/ai4research-design/`** (git
initialised, no remote, nothing committed). 15 schema pages for sign-off (`schemas/schemas.md` has the necessity review
and 14 naming decisions), 17 component pages each with a small diagram, 3 traces (M1 run, M2 chain, M3 library loop),
a Declaration-shaped issue template for Xiaoyang, and `presentations/` (every deck, one file each, with a
confirm-latest table; Presentation 3 had two differing copies, the newer tundle one is in). **Target is now M3 by 31 October** ([[Directives]]). Next:
team sign-off on each schema, then cut issues.

**Before 2026-09-28 the starting note was [[Architecture]].** It is a self-contained record of the whole design as of 2026-09-25: roles, milestones,
the M1 architecture, modules and agent-core seams, rules, the M2 planner, Symphony and tools, the schema map, the
RequirementIR assessment, where every file lives, open decisions, and how we work. It is written so that a fresh
session needs nothing else. Then read [[Directives]].

**2026-09-25, post-meeting: the immediate goal is the schema map.** Find every major schema that connects the
components by tracing the M4 map, investigate each, then work out each one's inputs. The list is ranked by edge count
(Capability Capsule Declaration 36 edges; observability record 30; then the records and the stage hand-offs). See
[[Post-Meeting 2026-09-25 - Schema Map]].

**2026-09-25: presentation 3, architect plan (25 Sep – 31 Oct).**

- **Deck:** 12 slides, in `ai4research/architecture/`.
- **Shared team docs, draft 0:** `capsule-openjiuwen/team/M1-DESIGN.md` (the M1 and M2 design, code-facing) and
  `SCHEMA-EXPLAINED.md` (every field; where each section plugs in; a JSON-against-text audit: 8 mismatches in
  M1-required fields and 16 more).
- **Roles this month:** Muk architect and CC owner; Xiaoyang primary coder; Ramika PRD; Saurav blue team.
- **Aligned:** the deck, both team docs (draft 1), the M1 map and the big-picture map all follow the M1 of
  [[Directives]] 2026-09-25. Standardisation choices are in [[Presentation 3 - Architect]].

**2026-09-25: M1 map, draft 9.** Frontend at the top (the answer now ends at a separate 'human reads the answer' node, so there is no loop back into the frontend; ELK overrides removed so Mermaid 12 defaults apply); main-flow lines are heavy and named by the data they carry; users may attach files, kept as refs by intake. Earlier, draft 8: Intent compilation reduced to two capsules (compile_intent, review_fidelity) and the acceptance gate; planner-binder and freeze drawn as PASS-THROUGH (no decisions); delivery just 'control'; frontend is an open black box (CLI to begin?). Page moved to Mermaid 12 + layout-elk 1.0.0, which honours subgraph direction; layout is about 1:2, the squarest found. Earlier, draft 7: Stages corrected against the AI4Research workflow: intent compilation now has validate_intent, review_fidelity, bounded repair and the decide_acceptance gate (reject/clarify back to the human); requirement compilation has its real steps and acceptance gate; the semantic contract (RequirementIR v2) drives the planner-binder; freeze is its own stage and writes the run contract; schedule + dispatch. Earlier, draft 6: Standard names (M1-DESIGN.md): intake → intent (normalize_input, compile_candidate) → requirements compiler (compile_contract) → **contract** → planner-binder (plan, freeze) → dispatcher → delivery; runner = loader.load + CapsuleTool.invoke; evaluator; store with gate.admit. Earlier, draft 5: No capsule in delivery. Dispatch shows only the capsule run and hands the task to a DISPATCH RUNNER block, which assembles the Declaration and calls the sites (loader, CapsuleTool, PermissionEngine, run, Binding). Earlier, draft 3: Planning, dispatch and the library are marked SIMPLIFIED (that is where M1 cuts complexity); an OBSERVABILITY block (spans, Bindings, gate results, trajectory) collects every capsule call from day one. Earlier, draft 2: One task. Capsules wherever they apply, with gates where needed (one or several per stage) (request: normalize_request, extract_task; dispatch: count_spaces; delivery: format_answer; names other than count_spaces are illustrative). The planner is **hardwritten** (no model, no filter, no selection) and resolves capsule ids through **Symphony**, which the CC provider feeds; `plan()` is not used. A fixed M1 capsule set replaces the library. Open, drawn as a black box: Symphony's graph takes only skills, subagents and agents, so tool capsules are not graphed. Decisions in [[Directives]] (2026-09-25). Source `capsule-openjiuwen/merged/figures/big-picture/m1_picture.py`; artifact https://claude.ai/artifact/Xh72oWggRhSTc5WuuXh5GS.

**2026-09-25: big-picture Mermaid map, draft 8 (aspirational M4).** Meta-RSI is drawn outside a box holding the whole pipeline ('AI4Research v3'), with its own workflow version tree; it takes a whole version and its outcomes and returns vN+1 of the entire pipeline. Eleven line types, each with its own colour, dash pattern and weight, from one LINES table that also builds the legend. A CC SCHEMA block in the library (the Declaration sections from capsule.schema.json, the gate-computed hashes, and the five records with their writers), with blue plug lines from each field to the component that reads or writes it. A FRONTEND block (jiuwenswarm: human, then channel, Gateway (E2A), AgentServer) feeds the request in, and the answer returns to the human by the same path. Blackbox blocks (IN, components, OUT) with an Expanded / Blackbox toggle, around a **central library where the three loops meet**: cold puts in, hot takes out, the librarian keeps Standing. The library is split into the CC library (Declarations only, pointing by hash), a code store (own repo or submodule, files by sha256) and a test store (suites by id). Planner: CC filter, then Symphony retrieve, plan and rank. Dispatch runs a DAG of about 9 nodes, including a composed block, a fused block, a skill and a generalist. **Open parts are black boxes** with known inputs and outputs: block-or-parts choice, fan-out scheduling, requirement capsules, RSI policy, merge proposer, fuser, judge calibration, quality thresholds. Example capsules are illustrative. Source `capsule-openjiuwen/merged/figures/big-picture/big_picture.py` (edit there, then re-snapshot); artifact https://claude.ai/artifact/NFknMZ8ow37Tyc98tUTpAn.

**Start here. Current state, 2026-09-25.** Read [[Directives]] first: Muk's binding corrections.

> *A 能力胶囊 is flexible in form and strict in verification and quality assurance.*

## Where things stand

- **Presented 2026-09-23.** It ran 1 h 40 min with questions, against 39:20 planned. Muk: "very good and answered
  questions well". The verification and RSI page was endorsed live by both owners. → [[Post-Presentation Decisions]]
- **Three decks are current:**
  - **the presented deck** (26 slides), frozen and never rebuilt;
  - **the post-presentation deck** (45 slides, a-to-g order): what was actually said, plus the decisions after it. Its
    **Part A** (section a alone, 4 slides) is built from the same spec;
  - **layer 2** (19 content slides at 14:05): what we build for M1, on which code, and who builds it.
    → [[Layer 2 Presentation]]
- **Schema v2.10b** (2026-09-24): a capsule points at code and never holds it; leaf xor composite; it says what it
  promises to keep stable (`evolution.frozen[]`). A `changes.state` proposal for v2.11 is waiting on WP0.
- **M1 is a fresh build on openJiuwen** (agent-core and Symphony): one node, three seed tools, ports-first planning,
  our own loader and runner. The AI4Research harness is an **archive** and appears only as lessons.
- **Next is coding, not yet started.** Muk: no spike yet.

## What CC is, in six lines

- **A schema:** the contract every capability declares, and the records kept about it. A scheme that uses tools,
  never a tool. → [[Capability Capsule]]
- **For four verbs:** pick, verify, improve, remove. **Two goals:** safe use and safe self-improvement.
  → [[Self-Improvement]]
- **Declared, not observed:** every check has a stated target before any use. → [[Declared vs Observed]],
  [[Predicate Parity]]
- **Every stage applies capabilities;** the workflow never becomes a capsule, and nothing that decides is one.
  → [[Every Stage Applies Capabilities]], [[The Ceiling]]
- **One schema, progressively enforced**, M1 (one node) to M5 (install and uninstall mid-run).
  → [[Milestone Ladder]]
- **openJiuwen already has the sockets**, and Symphony already implements most of the merge engine.
  → [[Where It Attaches]], [[Symphony Flow]], [[What openJiuwen Is Missing]]

## Read in this order

1. [[Directives]], then [[Post-Presentation Decisions]]
2. [[Capability Capsule]], [[What Is In The Library]], [[The Ceiling]]
3. [[Milestone Ladder]], then [[Layer 2 Presentation]] for M1
4. [[Every Stage Applies Capabilities]], [[Position in the Pipeline]], [[Dependencies]], [[Impacts on the Workflow]]
5. [[Self-Improvement]], [[Quality Not Just Correctness]], [[Declared vs Observed]], [[Predicate Parity]]
6. [[Overlap and Merge]], [[Versioning and A-prime]], [[Fusion After Merge]]
7. [[Symphony Flow]], [[What openJiuwen Is Missing]], [[Where It Attaches]], [[Inspiration from Other Software]]
8. [[Evidence]], [[Today's Capsules vs the Schema]] (a lesson from the archive)
9. [[Open Questions]]

How the code works: [[openJiuwen Landscape]], `agent-core/` ([[Core 00 Overview]]) and `jiuwenswarm/`
([[Swarm 00 Overview]]).

## Where everything is

| | In the tundle | Source, on the work machine |
|---|---|---|
| Decks and schema | `ai4research/capability-capsule/` (README there) | `capsule-openjiuwen/merged/` |
| Schema text, v2.10b | `capability-capsule/Capability Capsule Schema v2.10b - Muk.md` | `merged/SCHEMA.md` |
| JSON Schema, M1 policy, validator, examples | `capability-capsule/` | `merged/capsule.schema.json`, `policy-m1.json`, `validate_capsule.py`, `examples/` |
| Deck builders | `code/capsule-openjiuwen/merged/` (snapshot) | post deck: `build_spec_v6.py` → `deck.json` → `build_deck_v6.py`; layer 2: `layer2/`; Part A: `parts/build_part_a.py`; as presented: `presented-2026-09-23/` |
| Knowledge base | `code/capsule-openjiuwen/kb/` | `kb/` (`INDEX.md`, papers, repos, materials, functions, report) |
| Report (last built 2026-09-22) | `capability-capsule/older/Capability Capsule Merged Report - Muk.docx` | `merged/REPORT.md` is newer (2026-09-23) and not rebuilt |
| Reviews, paper ledger | `code/capsule-openjiuwen/verify/` | `verify/` (`PAPER-LEDGER.md`, V10-V12) |
| Session records | `ai4research/notes/57-…` and earlier | |
| The kit that builds the decks | `code/tundlekit/` | `huawei/tools/` |

The work repository `capsule-openjiuwen` is on branch `schema-v2.1-overnight`, **not pushed, and most of the work
since 2026-09-22 is uncommitted**. The tundle snapshot is the only other copy.

## Rules for this vault

- **Record important things here when they happen**: every decision, correction or new finding. Update the existing
  note rather than adding one, and delete what is stale.
- **Adversarial reviews use Opus** (since 2026-09-25), one at a time. Check every finding in source before applying it.
- The `.pptx` and `.docx` builds refuse while PowerPoint is open: ask Muk to close it, never force.
