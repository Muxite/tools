# Review: general workflow report (REPORT.md, draft v0.6), read front to back

## 1. Verdict

1. The spine holds §1 to §5: 3 claims stated, §2 walks the freeze stage by stage, §3 admits there is no external score, §4 places 4 systems on a ladder, §5 separates runtime from contract.
2. The thread breaks at §4.5 Table 6, whose AI4Research row says the 14-node run's "evidence gate not passed" while Table 5 (§3.1) says "the sprint closed with all required gates passed". One is wrong.
3. §6 is the weakest section after the merge. The 6 challenges are internally consistent and Appendix C tracks them correctly (`6.1 #2`, `6.1 #6`), but §6.2 tags only challenges 1, 2, 3 and 6; challenges 4 and 5 get no direction, and 2 of the 7 bullets carry no number.
4. Three systems enter the body unnamed and unsourced: CaMeL (§2.5), CREDENCE (§6), Rel(AI)Build (§6, pointing at §2.3 where it does not appear). The "capsule report" is cited 5 times, never identified, absent from Appendix A.
5. Missing for a supervisor: the cost of the dsh move, a target score plus owner and date for the first benchmark run, and an owner per challenge.

## 2. Findings

| # | Location | Flaw class | What is wrong (quote) | Proposed exact edit | Sev |
|---|---|---|---|---|---|
| 1 | §4.5 Table 6 (l.525) vs §3.1 Table 5 (l.377) | inconsistency | "with the run's own evidence gate not passed" against "the sprint closed with all required gates passed, with no manual verdict and no bypass" | Pick one. If the evidence gate differs from the required node gates, say so in Table 5: "all required gates passed; the run's own evidence gate was not reached (Log l.793-795)". Otherwise delete the clause from Table 6 | must |
| 2 | §6.1 Table 9 (l.640) | unsourced number, paper unnamed | "since experts judge verifiable claims correctly 60.8% of the time" | "since in DeepFact (2603.05912) PhD-level experts working unassisted judge verifiable claims correctly 60.8% of the time (p5)" | must |
| 3 | §6.1 Table 10 (l.648); App. B (l.742) | number before definition | "the strongest verdict is partially supported at 0.85" | 0.85 appears only inside Fig. 6. Add to §2.7 after "yields the class `source_reported`": "That verdict is partially supported, scored 0.85 (Fig. 6)." | must |
| 4 | §6 (l.629) | broken cross-reference, paper unnamed | "since Rel(AI)Build already hashes its specification … (Sections 2.3 and 4.3)" | "since Rel(AI)Build (2606.26924) already content-hashes its specification at approval (App. E.4) and Arbor already runs a held-out gate with no model (Section 4.3)" | must |
| 5 | §6 (l.625) | paper unnamed, no number | "cruder than the rule-based baseline CREDENCE measures" | "cruder than the rule-only baseline of CREDENCE (2606.19819), which reaches 0.811 Semantic-F1 against 0.88 to 0.91 for model decomposition (p22-23)" | must |
| 6 | §2.5 (l.243, l.246) | term before definition | "the property CaMeL enforces for control flow" | "the property CaMeL (2503.18813) enforces for control flow (p1)". CaMeL currently gets its id only in Appendix E.4 | must |
| 7 | §2.2 (l.143), §2.5 (l.250), §6.1 (l.657, l.662) | unsourced reference | "the capsule report"; "(capsule report, Appendix G.8)"; "(Section 4.1 there)" | Identify it once in §1: "A companion report covers the capability capsule library; references below name its own sections." Add it to Appendix A | must |
| 8 | §2.3 (l.158-159) | jargon, term before definition | "so it runs only for a plan whose nodes carry a frozen execution authority" | "Execution authority" is never defined. Replace with "so it applies only once nodes carry frozen operator bindings" | must |
| 9 | §2.3 (l.157) vs App. E.4 step 6 (l.914) | inconsistency | §2.3 names 2 abort codes; E.4 names only `CAPSULE_CHANGED_DURING_PLANNING` | E.4 step 6: "…and the same check on operator definitions aborts with `OPERATOR_CHANGED_DURING_PLANNING`" | should |
| 10 | §6.2 (l.675-686) | inconsistency | "The directions below follow from the challenges" — bullets tag 1, 2, 3, 6 only | Tag the first 2 bullets "(challenge 5)"; add "Counting plan defects per run before deciding whether the freeze keeps its cost (challenge 4)" | should |
| 11 | §7 (l.688-695) | self-contradiction | "Open questions: 4 questions, 2 already decided" | Retitle "7. Open questions: 2 decisions taken, 2 questions outstanding" and split Table 13 into decided (Q-G1, Q-G2) and open (Q-G3, Q-G4) | should |
| 12 | §2.3 (l.182 vs l.190) | voice (numerals) | "The freeze has 3 costs:" 8 lines above "There are four limitations to the freeze:" | "The freeze has three costs:" — both are discourse quantifiers | should |
| 13 | §3.1 (l.389), §4.2 (l.465) | voice (markers) | "**No external score exists**"; "**57.9% of synthesis statements**" | Delete both bold spans; bold appears nowhere else | should |
| 14 | §2.6 Table 3 (l.263) | redundancy | "Scientific gate \| The artifact type \| Applied according to the artifact type" | Circular. State what it checks, or delete the row and say in prose that scientific gates are selected by artifact type | should |
| 15 | §4 (l.419-422) | unsourced number | Rungs IV, VI and VIII carry no locator; rung II carries "(p44)" | Move the locator to the lead-in: "4 rungs of the ladder are used (p44):" | should |
| 16 | §1 (l.48) | unsourced number | "80 entries … and 74 of the 79 capsule manifests are registered" | 80 registry entries against 79 manifests invites the obvious question. Add the reconciling clause and an Appendix C locator | should |
| 17 | §6.1 Tables 9, 10, 12 (l.640, 648, 669) | layout | Single Evidence cells of 120 to 160 words | Break each Evidence cell into 3 or 4 rows, or make §6.1 per-challenge subsections. As printed they are paragraphs wearing table borders | should |
| 18 | §5.1 (l.546) | term before definition | Fig. 8 caption names "Claw-SWE-Bench, 2606.12344" before the text introduces it | Move Fig. 8 below l.548 | nice |
| 19 | §1 (l.34) vs §5.4 (l.598) | inconsistency | "OpenJiuwen Solar" against "openJiuwen" elsewhere | Fix the capital O in §1 | nice |
| 20 | §2.4 (l.220) | over-claim | "so a retry never repeats a paid call" | Add to the stage limitation: "Fingerprint collisions are not measured" | nice |

## 3. Layout findings (PNGs)

| Page(s) | What is wrong |
|---|---|
| 14 → 15 | Table 6 splits mid-row. Page 15 opens with an orphan row whose System cell is blank, showing only "by the merge tool" and "against 71.70 for Claude Code", so the Arbor row is unreadable without flipping back. Keep the §4 payoff table on one page |
| 17 → 18 | Table 9 splits with the repeated header empty in the `#` and `Challenge` columns, so page 18 opens with a headless block starting "claims correctly 60.8% of the time." The caption lands on page 18 |
| 18 → 19 | Table 11 splits mid-cell: page 19 opens with the fragment "(Section 2.3)" alone in a blank row |
| 27 → 28 | Table E4 splits mid-cell; page 28 opens with the orphan word "planes" (from "Deterministic control planes") |
| 28 → 29 | Table E5 splits with no repeated header; page 29 opens with 3 rows under no column labels |
| 1 → 2, 9 → 10 | Tables 1 and 4 also split, but the header repeats and the caption follows. Acceptable |
| 11 | About 45% blank because Fig. 7 was pushed to page 12, so the 4 TruthInsightBench reasons cite a figure overleaf |
| 20 | Half-empty: 2 bullets, §7 and Table 13. Reflow §6.2 and §7 onto one page |
| Global | No table exceeds the text width, no figure is too small to read, no heading is orphaned |

## 4. "So what" cuts

| Cut | Location | Words |
|---|---|---|
| "Each subsection below follows the same order: what the stage does, how code keeps the model in check…" The first subsection teaches this | §2, l.73-74 | 38 |
| "A research run produces schema-validated evidence artifacts rather than free prose. Section 3 summarizes the run and test evidence so far." Repeats the §1 claim list | §1, l.57-58 | 25 |
| "The scheduler does not plan everything and then run it; it repeatedly picks the nodes that are ready." This audience knows DAG schedulers | §2.4, l.202-203 | 25 |
| Bullet "Substitutability. A swappable service boundary is made of 3 roles … 'complete, never one role'." No consequence for AI4Research | §5.2, l.569-570 | 30 |
| App. B row "Is the 1-sentence design rule measured?" §1 already calls it a design target, not a measured property | App. B, l.755 | 22 |
| Status inventory: "Ready statuses are pending, queued, blocked, worker-blocked and failed review…" 14 names, no rule attached | App. E.5, l.969-971 | 55 |
| Table E2 restates the 23/20 check split already given in §2.1 and reused in §2.6 and §6.1 | App. E.2, l.876-881 | 35 |
| Table 3's circular "Scientific gate" row (finding 14) | §2.6, l.263 | 15 |

About 245 words, all scaffolding or repetition, no evidence lost.

## 5. Five questions the supervisor will ask

1. **Did the clean 14-node run pass its own gates?** Not answered: Tables 5 and 6 contradict (finding 1), undercutting §3's only positive evidence.
2. **What does the dsh move cost, and what breaks?** Not answered. §5.3 lists 8 stages and what AI4Research "would add", with no effort estimate, no sequence, and no statement of which of the 24 journey tests survive. §6.1 challenge 5 names the move as the fix without pricing it.
3. **What TruthInsightBench score counts as success, and who runs it by when?** Partly answered. §3.2 gives 4 reasons and says report per dimension; Q-G4 still calls the choice proposed. No target, owner or date, although §4's plateau (58.4 to 60.3, smallest p = 0.118) makes a threshold stateable now.
4. **With no re-planning, how often does a bad plan kill a run?** Answered as unmeasured (§2.3, §6.1 challenge 4). The report should price that measurement, since counting plan defects per run is cheap next to the other 5 challenges.
5. **Who owns each of the 6 challenges, and in what order?** Not answered. §7 assigns owners only to the 4 questions, so 6 challenges and 7 directions land with no owner and no ordering. An Owner column on §6.2 closes it.

## Applied / rejected

Applied 2026-09-14, 16 Edits to `notes/report-general/REPORT.md`, no other file changed.

**Applied**

- Finding 1 (run contradiction). Table 5's row now reads "every node passed on its first attempt and the ledger reached revision 106. The run executed its 14 nodes and delivered the 8 requested files, and its own evidence gate was not passed, so the sprint closed degraded". Table 6 is unchanged and now agrees. `LEDGER-VERIFIED-NUMBERS.md:92-101` shows the clause removed from Table 5, "all required gates passed", is Run B's property (`all_required_gates_passed=true`, 2026-09-03, 15/15), while the 14-node run recorded `evidence_gate.status=failed_for_full_requested_scope` and `closure_status=open_degraded`. The borrowed property was the defect. Neither table names 2 runs, and no forbidden phrase is used.
- Consequences of finding 1: the §3 heading no longer calls the run "clean"; §6.1 challenge 1 drops "1 clean"; §6.1 challenge 6 now reads "The run that finished without intervention did so only with 6 PDFs attached".
- Findings 2, 4, 5, 6: DeepFact (2603.05912) p5 restored on the 60.8% figure; CaMeL (2503.18813) p1, CREDENCE (2606.19819, Appendix E.7) and Rel(AI)Build (2606.26924) identified at first use; the Rel(AI)Build cross-reference now points at Appendix E.4 and Section 4.3.
- Finding 3: 0.85 defined in place in §6.1 Table 10 as "the confidence Fig. 6 attaches to a case-insensitive substring match against the cited section". §2.7 was left alone, since the definition now precedes every use.
- Finding 7: the capsule report identified at first use in §2.2 as the companion report "Capability Capsule in AI4Research" and added to the Appendix A source paragraph, which already lists internal documents.
- Finding 8: the §2.3 run-on split into 2 sentences, and "a frozen execution authority" replaced with "their capsule bindings and frozen execution candidates (Appendix E.3)", both defined in Appendix E.3.
- Finding 9: Appendix E.4 step 6 now names `OPERATOR_CHANGED_DURING_PLANNING` beside `CAPSULE_CHANGED_DURING_PLANNING`.
- Finding 10: §6.2 bullets 1 and 2 tagged (challenge 5), and a challenge 4 direction added, "Counting plan defects per run before deciding whether the freeze keeps its cost".
- Finding 11: §7 retitled "Open questions: 2 decisions taken, 2 questions outstanding". Table 13 not split.
- Finding 15: the "(p44)" locator moved to the lead-in, so it covers all 4 rungs.
- Finding 16: the Table 1 capsule cell now reconciles the counts, "so 5 manifests are unregistered and 6 registry entries have no manifest" (`report-capsules/REPORT.md:579`, `notes/HANDOFF.md:61`).
- Cuts: the §2 section-order preamble (38 words) and the §1 pointer sentence "Section 3 summarizes the run and test evidence so far" (12 words).

**Rejected**

- Finding 12 ("3 costs" to "three costs"): `build/build_reading.py:197` slices REPORT.md on the literal "The freeze has 3 costs:". Changing it breaks the build.
- Finding 13 (2 bold spans): 16-Edit cap reached, and no claim is affected.
- Finding 14 / cut of the Table 3 scientific-gate row: deleting the row drops a gate kind, and no opened source states what a scientific gate checks, so the row could not be restated without a new claim.
- Cut of Table E2: removing it opens a gap in the E1 to E7 numbering that would cost about 9 renumbering edits for 35 words.
- Cut of the App. E.5 status inventory: §2.4 references the ready and terminal status groups, so the inventory is the only place the names are given.
- Cuts of the §2.4 scheduler sentence, the §5.2 substitutability bullet and the App. B design-rule row: 16-Edit cap.
- Findings 18, 19, 20 (Fig. 8 placement, "OpenJiuwen Solar", fingerprint collisions): 16-Edit cap, all marked nice.
- Finding 17 and all layout findings: handled by the builder.

**Unresolved**

- Dates. The ledger dates the 14-node run 2026-09-02 and the 15/15 sprint 2026-09-03; §2.1 and Table 5 both date the 14-node run 2026-09-03, and Appendix C cites Log l.793-795, which is one of the 2 further 14-node passes the ledger records at l.781 and l.795, not the Run A entry at l.638. The date and the log line were left as drafted, since no opened source settles which line the report's run is. If the report's 14-node run is the l.795 pass rather than Run A, its evidence-gate status is not independently recorded in the ledger, and the ledger's own rule is that passing-flag counts are not a reliable measure. The statement now in both tables is the conservative one either way.
