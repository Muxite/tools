# R2: last editorial pass on the workflow report (2026-09-15)

Worktree `r2-general-report`. Nothing committed, no builder run, no subagent used. Code re-read at AI4Research
`b0bf165f9`, DeepSeek Harness `c291e7961a`; papers read in `papers/`.

## OWNED

- `notes/report-general/REPORT.md` (whole file)
- `notes/pass2/review/R2-general-report.md` (this file)

## TOUCHED

The 2 files above. `build_deck.py` was read only; every deck change it needs is under CROSS-REFS.

## CHANGES — first-time-reader rewrites

| Where | Before | After | Why |
|---|---|---|---|
| REPORT.md:226 §2.4 | "Work **was delivered** through tmux … which a deterministic materializer **now** fixes" | "Work **moves** through tmux … a defect a deterministic materializer **fixes at `b0bf165f9`**" | past tense implied a substrate the reader never saw being replaced; "now" is a draft-relative marker |
| REPORT.md:251 §2.5 | "**The model** holds for 1 user on a local machine" | "**This trust model** holds …" | "the model" in a bulleted list about models reads as the LLM |
| REPORT.md:141 §2.2 | "cited **below** as the capsule report" | "**called** the capsule report throughout" | forward reference to an ordering the reader has not met |
| REPORT.md:211 §2.4 | "On each tick the scheduler **takes 4 steps**" | "the scheduler **builds its ready set in 4 steps**" | contradicted App. E.5's "1 tick … takes 6 steps" for a reader reading both |
| REPORT.md:404 §3.2 | "The measured agents do **the easy half and not the hard half**, scoring only 11% to 16% …" | "The 4 measured agents score 78% to 81% on evidence auditability and 83% to 87% on novelty, against 11% to 16% on control testing, the dimension that asks whether a simpler explanation or a no-signal control would have produced the same result (p14)" | "the easy half" names a split the reader never saw; the replacement is the paper's own per-dimension numbers (2609.05079 p14) |
| REPORT.md:824 App. B | "Is \"nobody seals grading rules\" **still** true?" | "Does any other system seal its grading rules inside the run hash?" | quotes a claim from an earlier draft and asks whether it survived |
| REPORT.md:832 App. B | "PlanCompiler's 13 of 22 is another system's number." | "13 of 22 is PlanCompiler's number. Why does it count here?" | a verbless objection in a column headed Question |
| REPORT.md:707 §6.1 | "**Both rows meet the same objection**, that a bounded pre-freeze loop … The **second** objection is …" | "**Two objections meet these 2 rows. The first is** that …" | "the same objection" followed by a second one |
| REPORT.md:394 §3.1 | "**No external score exists**" (bold, standalone) | cut; the fact stands in Table 5, the §3.1 title and §6 | stray emphasis marker restating a table row |
| REPORT.md:483 §4.2 | "**57.9% of synthesis statements**" (bold) | unbolded | no other number in the report is bolded |
| REPORT.md:605 §5.3 | column header "What AI4Research would add **(proposed)**" | header "What AI4Research would add", plus a lead-in: "Nothing in its third column is built" | status as a word, not a parenthetical marker |

## CHANGES — mistakes, defensibility and layout

| Where | Before | After | Why |
|---|---|---|---|
| REPORT.md:111 §2.1 | "AI Scientist-v2 and Kosmos" | "AI Scientist-v2 (2504.08066) and Kosmos (2511.02824)" | first use of both papers is here, not in §4 |
| REPORT.md:187 §2.3 | "where Arbor and Kosmos re-plan" | "where Arbor (2606.11926) and Kosmos re-plan" | first use of Arbor |
| REPORT.md:171 §2.3 | nothing | "A hash detects an edit after the fact, wherever something recomputes it; it prevents no edit and authenticates no author." | W5 Q7 was answered nowhere in deck or report; a hostile reader asks it of every hash claim |
| REPORT.md:669 §6.1 #1 | settle: "an evidence-auditability score inside the published **58.4 to 60.3** band" | "an evidence-auditability **rate** inside the published **78% to 81%** band" | closes W3 doubt 6: 58.4-60.3 is the paper's total, not a per-dimension range. 78-81% is the per-dimension band at 2609.05079 p14 |
| REPORT.md:648 §6 | "Refusing literature verdicts for quotes not found in the retained source, so only re-verified spans reach the report" | "Refusing to raise a claim above insufficient when its text is not found in the cited retained section" | the old bullet claimed a span property the code does not enforce; the new one is `delivery.py:133-166` (insufficient, 0.3) and matches deck slide 19 |
| REPORT.md:721 §6.1 #5 | "**The older** coordinator substrate produced failures of its own" | "The coordinator substrate …, **which the move to dsh replaces**, produced failures of its own" | "older" said the substrate was already gone; §2.4 and App. B say it is the current one being replaced |
| REPORT.md:522, 535 §4.4 | "auto_research, with **7 parts**", last bullet "No evaluation published in the repository" | "built from **6 parts**", and the absence stated in prose after the list | an absence is not a part of the package |
| REPORT.md:636 §5.4 Table 8 | row "Code shared today \| 0 imports \| \|" | row cut; the fact is already in the paragraph above | a table row with an empty cell, and a duplicate |
| REPORT.md:1032 App. E.4 Table E4 | research-agents row ended with an empty "Not fixed" cell | "The plan and the rules that grade it" | same defect |
| REPORT.md:1097 App. E.7 | "**GPT-4o** fabricates citations 78% to 90%" | "**GPT-4**" | 2411.14199 p1 says GPT-4 (W4 cross-ref 2) |
| REPORT.md:892 App. C | no row for §5.2's version claim | "Developer preview; version `0.1.5-rc.2` \| dsh `README.md:11-13`; `apps/cli/package.json:4`" | every code claim needs a location; both verified at `c291e7961a` |
| REPORT.md:394 §3.1 | nothing | "No source records the token cost, the money or the wall-clock time of a sprint, so this report gives no cost figure." | W5 Q10 was a "nowhere" row; the first cost question a supervisor asks |
| REPORT.md:838 App. B | nothing | row "What does a run cost, and which models does it use?" | W5 Q10 and Q22, both "nowhere"; answered as a stated gap |
| REPORT.md:825 App. B | nothing | row "Does the hash stop tampering?" | mirrors the new §2.3 sentence |
| REPORT.md:400, 574 | §3.2 and §5.1 never referenced their own figures | "(Fig. 7)", "(Fig. 8)" | Fig. 7 and Fig. 8 were the only figures with no in-text reference |
| REPORT.md:605, 628, 1050, 1070 | Tables 7, 8, E5 and E6 had no lead-in | 1 lead-in sentence each, naming the table | guide §5: a numbered table takes a 1-sentence lead-in |
| REPORT.md:694 §6.1 | nothing | "Per-language work has started at the relevance gate, where Chinese character pairs were added by hand…" | detail moved out of the Table 10 cell so the fact survives the trim |

**Layout risk (W3 doubt 1).** Every §6.1 cell was measured. Before: 144, 171, 128, 132, 113 words in the evidence
column. After trimming: 116, 119, 114, 123, 113. Challenge 2, called out in the brief at about 170 words, lost 52.
No row was split and no challenge number moved: splitting a group into 2 numbered rows would have produced either a
7th challenge (contradicting "6 open problems" in §6.1, §6.2, App. B and deck slides 17 and 18) or 2 rows sharing 1
number in the delivered report. The register parser was re-simulated after the edits and still returns 5 groups, 6
numbered items, 3 cells each; `### 6.1 Challenges` and `### 6.2` each occur once. No heading text was changed
anywhere in the file.

**Checked and left alone:** challenge count 6; 43 = 23 + 20 in §2.1, §2.6, §6.1, App. B and Table E2; 80 registry
entries against 79 manifests (74 registered, so 5 unregistered manifests and 6 entries with no manifest) in Table 1,
§2.8 and §6.1; 102 physical operators with 63 enabled; 45 logical operators; the 14-node run of 2026-09-03 described
only as log l.793-796 describes it, with every required gate passed, never beside a 15/15 run and never as part of a
run count; 18 sources in App. A against 18 rows in Table A1; figures 1 to 8 plus E1 and E2 in order; tables 1 to 13
plus A1, B1, C1 and E1 to E7 in order; every table's column count; every `*Table N.*` and `![Fig. N.` line intact. No
em dash, "we", "our", ⚠, TODO or bracketed marker remains in the file, and no doubled word.

## CROSS-REFS

**Deck edits needed (`build_deck.py`, another agent's lane).** No factual disagreement with the report remains after
this pass. Two items are worth taking:

1. `build_deck.py:82-83`, slide 4 IF ASKED: `"No model decides after the freeze" is too strong: 20 of the 43
   registered checks are rubrics judged by a model` quotes a claim the deck never makes and then retracts it.
   Replace with: `20 of the 43 registered checks are rubrics a model judges; scheduling, routing and admission are
   code` (W5 §2.4, same wording).
2. `build_deck.py:233`, slide 12 table row `["trust declared at all", "21 of 79 manifests", ""]` carries an empty
   third cell. The same defect was removed from the report in Table 8 and Table E4. Move it to the THUS strip:
   `21 of 79 manifests declare a trust class, so most evidence carries no declared class` (W5 §2.4).

Optional, if slide 14 is reopened: the report now states the per-dimension bands 78% to 81% (evidence auditability)
and 83% to 87% (novelty) from 2609.05079 p14. Slide 14 says only the 11% to 16% figure, which stays correct.

**Heading changes:** none. No `###` or `##` line in `REPORT.md` was modified.

**Other lanes:** `PRESENTER-PACK-workflow.md` §5 hard question 8 ("Why is the 14-node run not a pass?") still
describes Run A while the report describes the 2026-09-03 run that passed every required gate. W3 raised this; it is
outside this lane and still open.

## DOUBTS

1. The brief asked for over-long §6.1 cells to be split into extra rows. Trimming was chosen instead, for the
   numbering reason above. Settled by rendering the challenge-register page and §6.1 and looking at the 5 cells that
   sit between 113 and 123 words; if any still runs past a page, group B is the one to split.
2. "78% to 81%" is the normalized per-dimension rate for evidence auditability, while 58.4 to 60.3 is a total out of
   100 points. Both units now appear in §3.2 and §6.1. Settled by 2609.05079 p14 and p8, or by dropping the band from
   the settle column and naming the dimension alone.
3. The trimmed Table 10 cell no longer says that every extracted claim carries its paper anchor as an evidence id.
   The mechanism still appears in §2.7 and App. C. Settled by a reader check of whether §6.1 alone has to stand.
4. §2.4 now says work "moves through" tmux keystroke injection, file inboxes and SQLite in the present tense, on the
   strength of App. B and W3. The dispatcher code was not re-read for a replacement substrate already in place.
5. "A defect a deterministic materializer fixes at `b0bf165f9`" was carried over from the prior draft's "now fixes";
   the materializer has no App. C row. Settled by naming the file and line, or by cutting the clause.
6. The §5.2 developer-preview and `0.1.5-rc.2` claims are read from `README.md:11-13` and `apps/cli/package.json`;
   the desktop and desktop-host packages carry the same version, and no repository-wide VERSION file was found.
7. The new cost sentence in §3.1 asserts that no source records token cost or wall-clock time. That is a negative
   from W5's coverage sweep, not from a search of the metadata directory. Settled by a grep for latency or token
   fields in `harness/metadata/`.
8. App. B has grown to 21 answer rows. It reads as a question bank rather than a page; whether it should be split by theme
   is the user's call.
