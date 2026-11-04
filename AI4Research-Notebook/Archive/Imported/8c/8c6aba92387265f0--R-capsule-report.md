# Capsule report: supervisor read-through, 14 Sep 2026

Source read in order: `notes/report-capsules/REPORT.md` (804 lines). Layout from
`notes/overnight/render/capsule-report/` (35 pages).

## 1. Verdict (5 lines)

1. The argument holds front to back: goal (§1), evidence with R1-R6 earned before use (§2), today's 5 gaps (§3), design (§4), evaluation (§5), order of work (§6). Every rule is cited before it is applied, and §4's opener states plainly that nothing is built.
2. The reader loses the thread at §5.1: `k` is used in Table 7 rows 2, 3 and 5 but defined only in §5.2, and the prose sorts 11 rows into 4 groups the table does not mark.
3. The second loss is §6: three lists in three different item forms follow each other, and the "so what" arrives only in the final paragraph.
4. Two factual seams a supervisor will find: §2.3's "31% to 34%" contradicts Table A4 (28.7% to 35.8%), and §5.1's "Typed selection is already settled" contradicts §6 step 4 and Appendix B.
5. Missing: any cost or effort number for the cold path, an owner or size per step in §6, and any mitigation for the shared-misreading risk §4.3 itself names.

## 2. Findings

| # | Location (§ and line) | Flaw class | What is wrong (quote) | Proposed exact edit | Severity |
|---|---|---|---|---|---|
| 1 | §2.3, line 112 | unsourced number | "The sessions carrying these tools still passed 31% to 34% of their verified tasks." Table A4 (line 500-504) gives 35.8%, 29.2%, 28.7% for the 3 tool-creating protocols | "The sessions carrying these tools still passed 28.7% to 35.8% of their verified tasks [3, Table 3]." | must |
| 2 | §5.1, line 352 | inconsistency | "Typed selection is already settled, since all 79 manifests populate consumed and produced types." §6 step 4 and App. B line 581 say the 2 type vocabularies cannot be crossed | "Typed selection is settled once the 2 type vocabularies are normalized (Section 6, step 4); all 79 manifests already populate consumed and produced types." | must |
| 3 | §5.1 Table 7 row 9, line 364; §6 line 402 | over-claim | "starting at 5, the number of rounds within which CoEvoSkills reports its skills converge [4]". App. A.3 line 532 and §4.3 line 279 make 5 the cap CoEvoSkills sets on oracle rounds, not a measured convergence point | "starting at 5, the cap CoEvoSkills sets on its ground-truth oracle rounds [4]" in both places | must |
| 4 | §5.1, line 352 | over-claim | "4 parameters with proposed starting values". Rows 10 and 11 carry no value: row 11's own cell reads "No source gives a value" | "2 parameters with proposed starting values and 2 rules with no value yet" | must |
| 5 | §4.3, line 290; Table 7 row 4, line 359 | unsourced number | "where 20 of 43 registered checks are model-judged rubrics". 43 appears nowhere in Appendix B or the general report | Add the count to Appendix B's inventory list with its commit-read basis, or cut the fraction and write "where much of the registered checking is model-judged rubrics" | must |
| 6 | §5.1 Table 7 caption, line 368 | term before definition | "k is the review window of Section 5.2". k is used 3 times inside the table before §5.2 defines it | Move the definition into §5.1's lead: "11 assumptions ... (Table 7). k below is the first review window, proposed as 10 sprints (Section 5.2)." | should |
| 7 | §5.1 Table 7 row 5, line 360 | over-claim | "CoEvoSkills' 41.1% to 71.1% is 1 run on 1 model [4, Table A1]". §2.4 line 132 bounds only the ablations: "The 41.1% and 42.4% ablations are single runs" | "CoEvoSkills' 41.1% ablation is 1 run on 1 model [4, Table A1]" | should |
| 8 | §6, line 399 | inconsistency | "Decide before building, with the proposed start in each line (Table 7, rows 8 to 11)". 3 of the 7 bullets (k, resubmission, DSH code mode) are not in rows 8 to 11 | "Decide before building, with the proposed start in each line. Rows 8 to 11 of Table 7 carry 4 of these; the rest are settled here." | should |
| 9 | §5 Table 6, line 340; §6, lines 386-395 | inconsistency | Track A is measured "on GAIA, SWE-bench and the AutoSci routes", but none of the 8 steps stands up a GAIA or SWE-bench harness | Add step 9: "Standing up the GAIA and SWE-bench runs that Track A scores" | should |
| 10 | §4.5, line 321 | voice | "The pin names a version; the content hash is what makes the pin checkable, because ..." Semicolon, and a 62-word sentence | "The pin names a version. The content hash is what makes the pin checkable, because the freeze already copies ..." | should |
| 11 | Throughout prose (lines 271, 305, 321, 786) | voice | Semicolons in body prose. Style card rule 10: none in the user's own sample | Split each at the semicolon into 2 sentences; leave semicolons inside table cells, where they separate list items | should |
| 12 | §2.2, line 106 | voice | "For a fixed benchmark these choices are proportionate and the results stand." This is the "that's fine for X, but ..." form the guide lists as a past mistake | Cut the sentence. The Table 1 column "AI4Research" already carries the contrast | should |
| 13 | §4.2, line 260; G.1, line 708; §4.2, line 254 | voice | Hedging verbs: "Trajectories that disagree with each other suggest the capability is ill-defined", "could in principle be built", "Parallel nodes in 1 plan are usually 1 need" | "Trajectories that disagree mean the capability is ill-defined"; "A new capsule can be built and used inside the sprint ..."; "Parallel nodes in 1 plan are 1 need spread over its inputs" | should |
| 14 | §2.3, line 124 vs App. A.2, line 480 | redundancy | The same sentence appears twice verbatim: "The 96.8% was measured on tools written by 3 other protocols, and Alita-G's own tools were never replayed on held-out inputs" | Keep it in §2.3 (with "(Table A2)"); open A.2 with the table instead | nice |
| 15 | §4.5, line 325 vs G.7 Table G2, line 790 | inconsistency | §4.5's new-version bullet omits what G2 adds: "the predecessor is then retired as superseded" | Append to the §4.5 bullet: "and its predecessor is retired as superseded" | nice |
| 16 | §4, line 202 | term before definition | "no suitable capsule for a node" precedes the gloss of node in §4.1 line 221 | Gloss at first use in §4: "for a node, meaning 1 step of a sprint's task graph" | nice |
| 17 | App. C Effects row, line 614 | term before definition | "blast radius" is used in App. C and glossed only in G.4 line 750 | "cost, blast radius (how much of the system a failure can damage)" | nice |

## 3. Layout (page numbers from the render)

| Page | What | Fix |
|---|---|---|
| 13-14 | Table 5 splits mid-row. Page 14 opens with a row whose Role and Sees cells are empty and whose text begins "reason, a capped number of times" | Keep the Implementation-agent row whole: `cantSplit` on the row, or start Table 5 on page 14 |
| 20-21 | Table 7 splits mid-row. Page 21 opens with "2 sprints, the first confirmed repeat AllocBench's best policy waits for [6]" and the cells "again" and "rises" with no antecedent; its "When" cell (Step 2, before 8) is stranded on page 20 | Same fix. Header does repeat correctly on page 21 |
| 20 | Orphan: §5.1's heading and lead sit at the top of page 20 with the table body running to 21 | Acceptable once the row split above is fixed |
| 24-25, 26-27, 28-29, 29-30, 30-31 | Tables A2, A7, C1, C2, D1 all split across pages, but each repeats its header row and breaks between rows | No change needed |
| 13, 11, 14, 33 | Figs. 9, 8, 10 and G1 checked full size: labels legible, no figure wider than the text column, every caption sits with its figure | No change needed |

## 4. "So what" cuts

| # | Where | Cut | Words saved |
|---|---|---|---|
| 1 | App. D, lines 648-650 | The Agent Notes archive manifest, the i18n sidecar and the pairing-gate quote. The appendix is titled "facts this report relies on" and no section relies on these 3 | ~115 |
| 2 | §4.1, line 230 | "The rest is unchanged: a node becomes ready in Kahn order ... never updated during the run." Appendix F states all of it with source lines. Replace with "The rest is unchanged (Appendix F)." | ~75 |
| 3 | G.3, line 746 | The specialization-is-reversible paragraph. It belongs with G.5 and adds nothing to flags, cost and cap; keep only the last sentence on generalist weights | ~55 |
| 4 | §6, lines 401-402, 406 | The 3 bullets that restate Table 7 rows 8, 9 and §5.2 word for word. Replace with "Recurrence threshold, gate tries and the review window: the proposed starts of Table 7, rows 8 and 9, and Section 5.2" | ~45 |
| 5 | §4.3, line 283 | "Fixed rules return the same decision for the same recorded results, so every admission can be replayed and every rejection names its reason." Restates the sentence before it | ~25 |
| 6 | §2.3, line 124 or App. A.2, line 480 | The duplicated Table A2 sentence (finding 14) | ~28 |
| 7 | §4.2, line 267 | "This is Alita-G's loop of writing tools while solving tasks [2], run incrementally across sprints ..." §6's closing paragraph makes the same point as the recommendation | ~26 |
| 8 | §2.2, line 106 | "For a fixed benchmark these choices are proportionate and the results stand." (finding 12) | ~12 |

Total ~380 words, no claim lost.

## 5. Five questions the supervisor will ask

1. **What does the cold path cost per sprint?** Not answered. G.4 (line 750) says the runtime enforces a build budget but names no figure, and §6's closing costs it in kind ("3 model sessions and an effect check per admission"). The only dollar figure in the report is DGM's USD 22,000 (App. A.4), which is never connected. Add an estimate anchored on the generalist's recorded token cost, or state plainly that the cost is unestimated until step 2.
2. **Does the 96.8% apply to our capsules?** Answered, and well. §2.3 limitation 1 bounds it to 1 model in 1 harness, the new Table A2 shows it was measured on 3 other protocols' tools, and §4.3 limitation 3 says "how far the 96.8% transfers to them is unmeasured".
3. **What if the gate rejects everything, or admits everything?** Answered. Table 8 rows 2 and 4 give both extremes, and §5.2 makes the control the first thing checked when a signal fails.
4. **What stops the suite author and the build-decision agent sharing the same wrong idea of the task?** Named but not answered. §4.3 limitation 2 states the risk ("the suite author and the capsule author can share the same misreading of the task") and nothing in §4, §5 or App. G proposes a check for it. The honest fix is a Table 7 row: no source settles it, and the control-group suites of step 6 are the first place it would show.
5. **How long does each of the 8 steps take, and who does it?** Not answered anywhere. §6 orders the work and names the disproof it reads first, but gives no size, owner or dependency. A supervisor allocating co-op students will ask before anything else.

## Applied / rejected

Applied, 14 edits to `notes/report-capsules/REPORT.md`, 14 Sep 2026.

| # | Disposition | Note |
|---|---|---|
| 1 | Applied, corrected | The review is wrong that 31% to 34% is unsourced. `papers/2604.00392.txt:288` reads "session-level TC in the re-execution (0.31-0.34 across the three systems)", and that re-execution is where the 222 preserved tools come from; Table A4 reports the earlier Table 3 matrix (0.287 to 0.358). §2.3 keeps 31% to 34%, gains the locator [3, Sec. 5.3] and names Table A4's range as the earlier run; Table A4's caption records the same distinction so the seam does not return |
| 2 | Applied | §5.1 lead-in now reads that all 79 manifests populate the types and step 4 unifies the 2 vocabularies, so exact matching spans all of them |
| 3 | Applied, reworded | The 5 is the cap on evolution iterations, `papers/2604.01687.txt:943` and `:958`, and is set as K=5 ground-truth oracle rounds at `:289`, `:496`. Table 7 row 9 and the §6 bullet now say "the cap on evolution iterations in CoEvoSkills". §4.3 and App. A.3 already said a round cap of 5, so both are left as they stand |
| 4 | Applied, reworded | "4 parameters, 2 with proposed starting values, 1 stated as a rule and 1 read from the census". Row 10 states its breaking-change rule in the assumption cell, so calling it valueless or census-read would be wrong |
| 5 | Applied | Locator added in §4.3 and Table 7 row 4: 20 of the 43 registered checks, general report Section 2.6, which states 23 deterministic gates and 20 semantic rubrics |
| 6 | Applied | k defined in the §5.1 lead-in, before the table |
| 7 | Applied | Row 5 now bounds the 41.1% ablation only |
| 8 | Applied | §6 pointer now says rows 8 to 11 carry 4 of the 7 lines and the rest are settled there |
| 9 | Rejected | Adding a 9th step is a new claim about scope, not a wording fix. Track A's harness question is real and belongs to the user |
| 10, 11 | Partly applied | Semicolons split at §4.5 (the pin sentence), §4.3 Fig. 11 pointer and §4.3 deny-list sentence. The G.7 update-triggers sentence keeps its semicolons, since its 3 items carry internal commas |
| 12 | Applied | Cut from §2.2 |
| 13 | Partly applied | "suggest" to "mean" in §4.2. G.1's "could in principle" and §4.2's "usually" not applied: budget, and dropping "usually" would turn a bounded statement about parallel nodes into a universal one |
| 14, 15, 16, 17 | Rejected | Edit budget. All 4 are nice-to-have and none is a factual error |
| Cut 1 | Applied | App. D's 3 hash bullets are now 1 bullet naming the 2 DSH hashes |
| Cut 2 | Applied | §4.1 now points to Appendix F and keeps the frozen-gate clause |
| Cuts 3, 5, 6, 7 | Rejected | Edit budget. Cut 5 is not pure restatement either, since the replay and named-reason claims are only in that sentence |
| Cut 4 | Rejected | It conflicts with finding 8, which asks for an accurate pointer in the same lines. The pointer was fixed instead |
| Question 4 | Skipped, listed | A Table 7 row for the shared-misreading risk is defensible, since §4.3 limitation 2 names it and negative controls written from the manifest are the mechanism. It was not added: a 12th row contradicts the "11 assumptions" count in the §5 heading, the §5.1 lead-in and the Table 7 caption, and the renumbering runs past the edit budget. The row to add is: negative controls from the manifest's negative signals, run on the step 6 sample, holding if the sample fails cases its own author's tests pass |
| Questions 1, 5 | Not addressed | Cost per sprint and step sizing are user decisions, not editorial fixes |
| Layout | Not addressed | The render is not owned here |
