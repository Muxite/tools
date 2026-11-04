# W1 capsule plan: spatiotemporal composability, and a defensible plan

Written 2026-09-15. Worktree `w1-capsule-plan`. Nothing committed.

## OWNED

- `notes/report-capsules/REPORT.md`, every section except §2 and Appendix A
- `notes/report-capsules/deck-src/build_deck.py`, title slide, slides 2-4, slides 16-26 (script lines 389 to end)
- `notes/pass2/review/W1-capsule-plan.md`

## TOUCHED

- `notes/report-capsules/REPORT.md` §1.2, §3, §4.1, §4.2, §4.3, §4.4, §4.5, §5, §5.1, §6, App. B, App. D, G.2, G.4, G.6, G.7
- `notes/report-capsules/deck-src/build_deck.py` slides 2, 4, 16, 20, 23, 26
- Read only: AI4Research at `b0bf165f9`, DSH docs, `papers/2608.25512.txt`

## CHANGES

### A. Spatiotemporal composability, used rather than named

| Where | Before | After | Why |
|---|---|---|---|
| REPORT §1.2, new paragraph after the 4 DSH properties | the paper title appeared once, with no definition | both halves defined in plain words, with what a self-evolving harness loses without each, cited [1, Sec. 1.1], [1, Sec. 3, Sec. 3.2], [1, Sec. 1.2.2], and a pointer to where each half does work | the term was decorative; the user asked for it to carry weight |
| REPORT §4.1, new paragraph after Fig. 9 | nothing on parallel generalist nodes | spatial half applied inside a sprint, grounded in `graph_scheduler.py:2237-2245`, `:2261-2274`, `:3203`, plus the note that the generalist inherits the node's requested effects | answers "5 generalist nodes at once, do they trample each other?" |
| REPORT §4.2, new paragraph at the end | nothing on 2 sprints at once | append-only reads, single-writer cold path, gap identity, `DUPLICATE_CAPABILITY` as the backstop | the concurrency question note 30 raised had no answer in the report |
| REPORT §4.3, protected-components paragraph | DGM node 114 alone | Cordis's "a faulty self-modification can disable the very process needed to recover" added as the independent argument [1, Sec. 1.2.2] | the user asked for this citation to appear at R5 in §4 |
| REPORT §4.5, new paragraph before "Versioning is the first" | append-only justified by 3 converging systems | the time half added: a new version loads beside the old, the old is withdrawn by running its inverses, so an improvement lands without a restart [1, Sec. 3.1] | append-only was a convention; it is now a runtime property |
| REPORT §4.5 retirement paragraph | "Retirement is an appended record with a typed reason" | plus: disposal of effects and a tombstone that is never deleted | retirement was a status flag in the prose |
| REPORT G.2, new paragraph | 3 loops, no account of shared access | the library is the only shared object, and append-only is why no lock is needed | makes the 3-loop claim defensible under concurrency |
| REPORT G.6, new paragraph | retirement policy table only | 2 halves, tombstone and disposal, plus Theorem 70 ordering for dependents, plus what disposal cannot reach | note 20 §7.3 and §7.4, made explicit |
| REPORT G.7, new paragraph after Table G2 | 4 update options | an update appends 2 records and disposes of 1 set of effects | ties the update table to the lifecycle mechanism |
| REPORT App. D, 3 new bullets | no composability facts | the 2 definitions in the paper's own terms, and the honest bound that reversal is observational, not physical [1, Sec. 3.3] | the bound is the single most puncturable claim if left out |
| REPORT App. D Table D1, 2 new rows | 8 rows | "Loading a new version while sprints run" and "2 capsules active at the same time" | 1 row per half, as asked |
| REPORT §5.1 Table 7, 2 new rows 12 and 13 | 11 rows | the load/use/retire test and the overlapping-effects test, each with what says it holds and what says it fails | puts both halves in the plan, appended so rows 1-11 keep their numbers |
| REPORT §5 heading and §5.1 lead | "11 assumptions" | "13 assumptions", with the 2 platform rows named in the lead | count must match the table |
| REPORT §6, new step 9 | 8 steps | "Loading, replacing and retiring 1 capsule on DSH, and running 2 capsules with overlapping declared effects at the same time" | the 2 new Table 7 rows need an owner in the plan |
| Deck slide 2, DSH bullet | "...is a plugin" | "...is a plugin that can be loaded, replaced and retired while the system keeps running" | 1 face line, at the point DSH is introduced |
| Deck slide 4, SAY and IF ASKED | 88 words, no composability | both halves named and defined, plus the self-modification warning under IF ASKED | the figure already carries the time half on its face; no slide-face room under it (figure runs 1.55 to 6.95, footer at 7.02) |
| Deck slide 20, THUS strip | "5 parallel steps in 1 sprint count once, so 1 request cannot trigger a build" | "5 parallel steps count as 1 sighting, and declared write scopes keep them apart" | 1 face line for the space half; the build-trigger point moved into SAY verbatim |
| Deck slide 23, lifecycle line | "Retired: a record; only a security reason stops sprints" | "Retired: unload the plugin, keep the record" | 1 face line for the time half; the security-reason nuance was already in SAY |
| Deck slide 26, order of work | 8 steps | step 9 added, and SAY says why it stands apart | deck and report plans must match |

Added words for composability across the report: about 340, inside the 200-350 band the brief set.

### B. Grounding the plan in the code, and cutting work

| Where | Before | After | Why |
|---|---|---|---|
| REPORT §3, end of the opening paragraph | no evidence that gaps happen | the 2 recorded cases, `define_study_protocol` and `contradiction_gap_analysis`, each closed by a human writing a capsule (`harness/metadata/pre-scheduler-stabilization-log-20260829.md:110`, `:521`, `:493`, `:554`) | the design's premise now has 2 observed instances; it also partly answers step 5 |
| REPORT §3 Table 3, observation row | "The sandbox access log" | "The write-guard record the existing sandbox already produces" | AI4Research already produces it; the report was proposing to build one |
| REPORT §4.3, `EFFECT_UNDECLARED` paragraph | "running the suite inside the DSH sandbox with every access logged" | the write half already exists in `hands_runtime.py:295`, `:559-618`, `:655-673`, so step 7 needs no new runtime; reads and network are what DSH adds | removes a dependency of step 7 on DSH |
| REPORT §4.3, protected-component check | "The hard capsule filter already rejects on 13 reasons" | plus `elastic_planner.py:4553-4644`, plus the fact that the filter is a pure function of 1 node and the catalog, plus the smallest test and its stop signal | makes step 3 a 1-function change with an in-memory test |
| REPORT §4.3, limitations list | "four limitations" | five: effects are observed only on the cases the suite runs | the hardest question on `EFFECT_UNDECLARED` had no written answer |
| REPORT §4.4 | "Stage 0 and most of Stage 3 already exist" with no locator | `elastic_planner.py:4553-4644`, `:4968-4975`, `:4955-4967`, `:4980-4989` | every code claim gets file:line |
| REPORT §4.5, new paragraph after the hash sentence | step 1 read as a new versioning scheme | the registry already carries a version per entry and already rejects duplicate `(kind, id, version)` (`capability_capsules.py:311-327`); only the lookups resolve by bare id (`:437-450`; `execution_authority.py:37`); the test is the existing fixture with a second version added | step 1 is smaller than it looked, and now has a stop signal |
| REPORT §4.5, audit loop | "re-runs every admitted capsule's held-out suite" | plus a schedule ordered by blast radius and time since last check | answers "what does the audit cost at 1,000 capsules?" |
| REPORT §6, new paragraph after the step list | 8 equal-looking steps | step 2 can read its census from `capsule_candidate_catalog.json`, which planning writes for every plan before the plan fails (`elastic_planner.py:4939-4943`, `:4664-4674`); step 5 measures how often rather than whether; step 8 is 3 roles built in order, decision agent first; step 9 is independent | the cheapest and most decisive test no longer waits on the generalist, and the largest step is split in place without renumbering |
| REPORT §6, supervisor list | no DSH question | "Which DSH version is the integration target?" | step 9 is the first work that needs a running DSH |
| REPORT §6, closing paragraph | "the gap census of step 2" | plus: it reads a file planning already writes, so it is the cheapest of the 9 steps | strengthens the recommendation without new claims |
| REPORT App. B, registry bullet | "79 capsule manifests, 5 of which are not in the registry, so 74 manifests are registered and 6 registry entries have no manifest" | "85 capsule manifests, of which 79 are capability capsules other than the 3 artifact adapters ... every registry entry resolves to a manifest that exists" | the 6 orphan entries do not exist. They are the 3 adapters, 1 guard and 2 resources, and all 6 have manifests. 79 is correct once its basis is stated |
| REPORT App. B, gate bullet | "5 fail-closed rejection reasons" unnamed | all 5 named with `harness/docs/architecture/capability-capsule-runtime-gate.adr.md:47-53`, raise sites `capability_capsules.py:1269`, `:1302-1380`, and the located test `tests/harness/test_capability_capsules.py:164-224` named as the fixture to extend | every admission work item now has a fixture |
| REPORT App. B, binding paragraph | "13 reasons" with no locator | `elastic_planner.py:4553-4644` for the 13, plus the 5 from `capability_admission.py:12-26`, plus the scheduler lines | 13 is the count the node-level filter adds; 18 distinct codes reach a candidate |
| REPORT App. B, 5-gap bullets | prose only | file:line on all 5, plus what already exists for each | the inventory is where code claims live |
| Deck slide 16, observation row | "sandbox access log" | "the write record the sandbox already keeps" | matches Table 3 |
| REPORT §4.1 | "The rest is unchanged" | "Everything else runs as the general report describes" | first-time-reader rule |
| REPORT §4.1 bullet | "the sandbox access log" | "the sandbox write record" | consistent with the mechanism that exists |

### W2 cross-references applied

All 6 applied as given, with no conflict.

1. §4.2 recurrence sentence now carries the 2-sprint start and [6, Fig. 1]
2. §4.3 gate-try cap now carries the 5-round oracle and the 15-retry surrogate loop [4, Alg. 1]
3. §5.1 Table 7 gate-tries cell rewritten to the oracle budget with [4, App. B]
4. §5 Table 6 Track B cell now carries "over 5 harvests, 26 to 128 tools [2, Table 4]"
5. G.4 first sentence rewritten with the AllocBench price result [6, App. E] and the 4th-harvest result [2, Table 4]
6. §4.5 keeps "append-only and versioned" verbatim in its heading and first sentence
7. Consequential fix: §6 "Gate submissions per build: 5, CoEvoSkills' cap on evolution iterations" became "the ground-truth oracle budget of CoEvoSkills". Deck slide 25 already said "the bound CoEvoSkills puts on its pass/fail oracle" and needed no change

### The hardest question per §4 decision, and where the text answers it

| Decision | Hardest question | Answered in |
|---|---|---|
| §4.1 generalist | 5 generalist nodes run at once. Do they trample each other? | §4.1, new paragraph after Fig. 9 |
| §4.1 generalist | Does the generalist become a way around the typed contracts? | §4.1 bullet 1 and the cap in G.3, referenced from §4.1 |
| §4.2 roles | 3 model sessions per build is expensive. What does each separation buy? | Table 5, 1 measured failure per row |
| §4.2 recurrence | 2 sprints both hit the gap. Do you build twice? | §4.2, new final paragraph |
| §4.3 manifest first | Nobody compares the 2 orders. Why this one? | §4.3 opening, stated as a design choice |
| §4.3 gate | Effects depend on inputs. What does observing a suite prove? | §4.3 limitations, new first bullet |
| §4.3 gate | Who updates the gate, and how is that not self-modification? | §4.3, humans release, every admission records the version |
| §4.3 protection | Is this secrecy? DGM's node 114 had the checks hidden | §4.3, protection is by write access, with declared effects making it checkable |
| §4.4 selection | A planner model already picks. Why embeddings? | §4.4, cost per node, plus the head-to-head in Table 7 |
| §4.5 versions | Is this a new versioning scheme? | §4.5, new paragraph: the registry already versions; 3 lookups change |
| §4.5 audit | What does the audit cost as the library grows? | §4.5, schedule by blast radius and staleness |
| §4.5 retirement | Retiring cannot un-publish evidence | §4.5 and G.6, flagging plus the argument for strict admission |

## CROSS-REFS

Things another lane or a builder must match.

1. **Heading changed.** `## 5. Evaluation: 3 tracks, a stated prediction and 11 assumptions that must hold` became `... and 13 assumptions that must hold`. No slicing script reads this string. `build_reading.py:339` slices only on `The 5 gaps of Table 3, as read in source:`, which is untouched.
2. **Table 7 grew from 11 to 13 rows.** New rows are appended as 12 and 13, so "Rows 8 to 11 of Table 7" in §6 and the deck footer "Table 7 rows 8-11" stay correct. Deck slide 24 footer "Table 7 rows 1-3" stays correct.
3. **Table D1 grew from 8 to 10 rows.** No table was renumbered. No new numbered table was created.
4. **§6 has 9 steps, not 8.** Table 7 rows 12 and 13 point at step 9. Deck slide 26 lists 9. Anything else quoting "8 steps" must change.
5. **`79` is now defined in App. B** as capability capsules other than the 3 artifact adapters, out of 85 manifests. **Appendix A.6 (W2's lane) still says "the 79 hand-written AI4Research manifests"**, which is consistent with the new definition and needs no edit, but the owner should confirm.
6. **App. B correction:** "6 registry entries have no manifest" was wrong and is removed. Every registry entry resolves to a manifest.
7. **Slide TIME deltas:** slide 2 goal 0:45 to 0:50 (+0:05), slide 4 DSH 0:50 to 1:00 (+0:10), slide 26 next 0:50 to 1:10 (+0:20). **Total +0:35**, inside the +1:30 allowance. Capsule deck goes 20:30 to 21:05; both decks 35:55 to 36:30 against a 40:00 target.
8. **SAY budgets rechecked** for all 21 noted slides: every one is between 20 words and TIME x 2.3. Tightest are slide 4 (135 of 138), slide 20 (138 of 138) and slide 23 (159 of 161).
9. **Figure numbers, table numbers and R1-R6 are untouched.** No `d.figure(` call was edited. Slides 5-17 (script lines 186-388) were not edited.
10. **Neither builder nor render script was run.** The deck script parses (`ast.parse` clean). All report tables have consistent column counts.

## DOUBTS

1. **The manifest count.** 85 manifests exist; 79 is the count of capability capsules excluding the 3 artifact adapters. I kept 79 and pinned its basis rather than renumbering the report and deck. *Settled by:* the user saying whether the headline should be 79 or 85.
2. **"13 reasons."** 13 is what `_hard_capsule_candidate_row` adds; `capability_admission.rejection_reasons` adds 5 more, so 18 distinct codes can exclude a capsule. I kept 13 in the body and stated the extra 5 in App. B. *Settled by:* deciding which number the talk should say.
3. **Step 9 placement.** I put the DSH composability proof last so no step is renumbered, then wrote that it is independent and can run first. A supervisor may read the numbering as the priority. *Settled by:* the user reordering it to step 1 and accepting the renumber.
4. **No slide-face room on slide 4.** The stack figure runs to 6.95 in and the footer sits at 7.02, so both halves of composability live in the SAY there, with 1 face line moved to the goal slide instead. *Settled by:* regenerating `fig-stack.png` shorter, or accepting the goal-slide line.
5. **Cordis locators are section numbers, not pages.** The extracted text gives Sec. 1.1 on p. 4, Sec. 1.2.2 on p. 5, Sec. 3 on p. 9, Sec. 3.2 on p. 16, Theorem 70 on p. 47. The report's existing style cites `[n, Table 3]`, so I used sections. *Settled by:* the user preferring page numbers.
6. **The gap census from archived catalogs is untested.** No `capsule_candidate_catalog.json` exists anywhere in the repo, so the claim rests on reading `elastic_planner.py:4939-4943`, not on a file. Whether deployments retain these directories is unknown. *Settled by:* looking at a real sprint output directory on the runtime host.
7. **The sandbox write guard is a before-and-after snapshot of declared roots, not an access log.** It catches writes to watched paths and says nothing about reads, network reach or writes outside the roots. I said so in §4.3, but the cheapening of step 7 depends on the write half being enough to start. *Settled by:* running the check on 1 existing capsule and seeing whether it says anything useful.
8. **The 2 stabilization-log cases and the 2 hand-written capsules are separate log rows.** Rows 110 and 521 record nodes with no admissible capsule; rows 493 and 554 record humans registering a new capsule around an existing worker. That they are the same 2 gaps is likely and unproven, so §3 claims only that both kinds of event happened, not that each rejection was closed by a named capsule. *Settled by:* reading the sprint ids in rows 110, 521, 493 and 554 against each other. Related: `generalist_fallback` and `capability_authoring` appear nowhere in the code, which App. G's "everything here is proposed" covers, but only implicitly.
