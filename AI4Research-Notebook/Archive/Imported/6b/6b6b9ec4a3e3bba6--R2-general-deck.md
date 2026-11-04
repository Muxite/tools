# R2: the workflow deck read as a first-time viewer, and made easy to present (2026-09-15)

Worktree `r2-general-deck`. Builder run to `scratch-general.pptx` only. Nothing committed.

## OWNED

- `notes/report-general/build/build_deck.py`, every line except the `d.figure(` calls
- `notes/pass2/review/R2-general-deck.md` (this file)

## TOUCHED

The 2 files above. `notes/report-general/build/deck-times.json` was rewritten by the builder (general 15:15).
`notes/report-general/build/fig/` was copied in from the main tree so the builder could run; it is gitignored
build input, not a new source file. `scratch-general.pptx` is gitignored.

## CHANGES

### Presenter rule (the face carries the point, the SAY says it and more)

| Slide | Before | After | Why |
|---|---|---|---|
| 6 | title "Binding: code narrows, a model picks, code binds" | "Code narrows, a model picks, and code binds the pick" | the eyebrow already says Binding; the title is now the sentence a presenter reads out |
| 10 | title "Gates: results do not say who decided" | "A result does not say whether code or a model decided" | same label strip, and the takeaway is now a full sentence |
| 11 | title "Claims: no model, and provenance rather than truth" | "No model extracts claims, and a verdict proves provenance" | same |
| 12 | title "Experiment code: hand-written or unobserved" | "Experiment code is hand-written or unobserved" | same |
| 13 | title "Evidence so far: 1 run end to end, 0 external scores" | "1 run end to end, and 0 external scores" | same |
| 20 | title "Next, and what needs deciding" | "DeepSeek Harness comes first, and 3 decisions wait" | a topic label became the point, and it matches report §7's "3 decisions waiting" |
| 7 | face "Tested: a frozen node's priority set to 999 fails verification…" | "Setting a frozen node's priority to 999 fails verification…" | a bare label dropped, and the line now fits 1 line, which freed room for the new face line below it |
| 7, 9, 11, 12, 13, 15, 20 | SAY did not say the new face lines | each SAY now states them in the face's reading order | a viewer of the slides alone follows; the speech removes the effort |

### First-time viewer (nothing relative to an unshown alternative)

| Slide | Before | After | Why |
|---|---|---|---|
| 4 | IF ASKED "\"No model decides after the freeze\" is too strong: 20 of the 43 registered checks are rubrics judged by a model" | "20 of the 43 registered checks are rubrics a model judges; scheduling, routing and admission are code" | quoted a claim the slide never makes in order to retract it (W5 2.4) |
| 13 | THUS "demonstrated end to end, but not yet routinely without someone attending" | "demonstrated end to end; an unattended run from a prompt alone has not finished" | the "but not yet" clause conceded instead of stating; SAY matched to it (W5 2.4) |
| 12 | table row "trust declared at all / 21 of 79 manifests / (empty)" | row deleted; face line "21 of the 79 capsule manifests declare a trust class, so most evidence carries no declared class." at y 5.00 | an empty verdict cell in a table about paths read as an aside (W5 2.4); the THUS strip was occupied, so the fact became its own face line |
| 20 | face "Proposed. None of this is built or measured yet." | "None of these 5 steps is built or measured." | "Proposed." was a bare label; the count matches the 5 bullets W3 left |
| 7 | IF ASKED "The cost: no plan-level search, so the plan cannot change…" | "Arbor and Kosmos re-plan every cycle; this design trades that away for grading rules fixed in advance" | the cost is on the face now, and the bullet names the systems that pay it differently |
| — | W5 2.4's slide 9 "'Compile' here is the 6 model calls drawn on slide 4" | no change needed | that sentence is not in this deck at this revision |

### Coverage (W5 Part 2.2, every 0-second proposal, and the 2 SAY additions)

| Q# | Slide | What was added |
|---|---|---|
| 1 | 2 | new bullet 4 "Everything up to the challenges is code read in source at commit b0bf165f9; the next steps are proposed"; the plan bullet reworded from the "Plan:" label to a sentence; SAY matched |
| 3 | 7 | new face line "Search happens inside steps only, so a plan cannot change when execution shows it was wrong." |
| 7 | 7 | SAY + "A hash detects an edit after the fact, wherever something recomputes; it does not prevent one and it does not authenticate an author." TIME 1:00 to 1:10 |
| 5 | 9 | the scope moved onto the face through the title: "Nothing observes the CLI path, and trust ends at 1 user"; SAY gains "All of this holds for 1 user on 1 machine, and a shared unattended server needs a different trust model"; the old IF ASKED line now points at challenge 5 instead of repeating the face |
| 8 | 14 | title rewritten to "Control testing is verification: agents score 11% to 16%", which answers "why this benchmark first" on the face |
| 11 | 15 | SAY + "Arbor and Kosmos re-plan every cycle, and the freeze trades that away for grading rules that are fixed before the run." TIME 0:40 to 0:50 |
| 13 | 15 | new face line under the table "Every result here is the authors' own measurement, except openJiuwen, which is a code read."; the duplicate IF ASKED bullet removed; SAY matched |
| 17 | 11 | the takeaway line under the figure now carries both facts: "A verdict with no experiment tops out at 0.85, and an insufficient claim still becomes a conclusion."; SAY matched; the freed IF ASKED slot names the mechanism (`delivery.py:256-261`) |
| 18 | 15 | new face line above the table "The 4 systems span the design space: generation first, scale, a held-out check, and the same thesis." (table moved to y 1.85) |
| 14 | 13 | new IF ASKED "Passing-flag counts are not a reliable measure here, so no run count is quoted" |
| 23 | 17 | already on the face from W3 ("a span that fails its re-hash is dropped and no gate reads the flag"); no change |
| 10 | — | skipped, no source for token, money or wall-clock cost |

### Cross-references received from the report lane

| Ask | Done |
|---|---|
| slide 4 IF ASKED: drop the quoted-then-retracted line | yes, exactly as worded |
| slide 12: drop the empty-cell row and carry the fact | row dropped; the fact is a face line at y 5.00, not the THUS strip, because the THUS states the design that follows ("proposed: a model writes runners that run only after hash-and-approve") and a design slide's THUS is the plan, not a statistic. The fact is on the face either way |
| §2.4 "ready set in 4 steps", a tick has 6 steps (App. E.5) | slide 8 IF ASKED now names both counts and lists the 4 ready-set steps and the 6 tick steps, each with its report locator |
| §6 direction bullet on insufficient claims | slide 19 already reads "a claim not found in its cited section never rises above insufficient"; no change |
| §6.1 #1 settle signal is 78% to 81% evidence auditability, not 58.4 to 60.3 | slides 17 and 19 quote no band; slide 17's settle cell says "read the 6 dimensions". Slide 14 keeps 58.4 to 60.3, correctly labelled on the face as **Totals** ("Totals do not separate the agents"), which is the reason the settle signal moved to a per-dimension band. Nothing to change, but see DOUBTS 8 |
| §6.2 wording "asks a person" | slide 18's settle cell changed from "declare halt, inconclusive or human" to "declare halt, inconclusive or ask a person" |

### Mistakes checked

| Check | Result |
|---|---|
| 43 = 23 Python gates + 20 rubrics | consistent on slides 5, 10, 15, 17 and in the slide 4 IF ASKED |
| 80 registered, 79 manifests; 21 of 79 declare a trust class | slide 3 and slide 12; the slide 12 line now says "capsule manifests" so the 79 is not read as the registry |
| the 2026-09-03 run | slide 13 row and SAY: 14 nodes executed at attempt 1, 8 files delivered, every required gate passed. No run count anywhere; the new IF ASKED says why one is not quoted |
| Table 6 equals slide 15 | all 5 rows word for word, minus the rung column, which W4 left off the face deliberately |
| footers | slide 13 log locator corrected from l.793-795 to l.793-796 to match report Table 5; every other footer re-read against the report's section, table and figure numbers and holds |
| challenge rows | slide 17 rows 1 and 2, slide 18 rows "3, 4" and "5, 6", matching report §6.1 Tables 9 to 12 (W3's map) |
| paper titles plus arXiv id at first use | added for PlanCompiler (2604.13092, slide 5), CaMeL (2503.18813) and Rel(AI)Build (2606.26924) (slide 7), and Co-Scientist, Robin, Agent Laboratory (slide 15) |
| DeepSeek Harness spelled out at first use | slide 2 bullet 3; no "DSH" anywhere in the deck |
| em dashes, MUST HIT, "I'm not", fairness hedges, we/our on faces | none found |

### Layout

| Slide | Before | After |
|---|---|---|
| 17 | WARN: the title needed 1.15 in of a 0.75 in box, so it wrapped to 2 lines across the rule | title shortened to "No outside score, and a verdict that stops at provenance" (56 characters against the 57 the box holds at 30 pt) |
| 20 | WARN: 5 bullets needed 2.50 in of a 2.40 in box | bullets moved to y 2.22 with h 2.55; text bottom 4.55 in against the question table at 4.80 |
| 15 | the tightest table in the deck, and 2 face lines to place | `row_h` 0.75 to 0.62 and y 1.60 to 1.85; lead line at 1.45, provenance line at 5.88, THUS unchanged at 6.38 |
| 7 | 1 line under the figure | 2 lines in 1 box at y 5.72, h 0.62; bottom 6.34 against the THUS at 6.38 |
| 12 | table of 4 rows to 4.75 | 3 rows to 4.75 with the new face line at 5.00 |

Builder output after the pass: `20 slides, planned 15:15`, `both decks: 35:45 (ok)`, **0 WARN**.

## TIME

| Slide | Before | After |
|---|---|---|
| 7 Freeze | 1:00 | 1:10 |
| 15 State of the art | 0:40 | 0:50 |
| every other slide | unchanged | unchanged |
| **Deck total** | **14:55** | **15:15** |
| Both talks | 35:25 | 35:45 (capsule 20:30) |

Every SAY is between 20 words and TIME x 2.3; the tightest are slide 2 (102 of 103), slide 9 (113 of 114) and
slide 15 (112 of 114).

## CROSS-REFS

1. **Report §2.3, another lane.** The hash sentence now spoken on slide 7 has no home in the report. Add to the
   freeze subsection: "A hash detects an edit after the fact wherever something recomputes. It neither prevents
   the edit nor authenticates an author." Source: `notes/overnight/Q2-how-hashes-work.md:61-65`.
2. **Report §3.1, another lane.** No source records token cost, money or wall-clock time for a sprint (W5 Q10).
   The talk offers none; a supervisor will ask. Measuring 1 sprint would produce the sentence.
3. **Report §2.8 / App. C, another lane.** The deck now says "21 of the 79 capsule manifests"; the report says
   "21 of 79 manifests" in §6.1 Table 12. Same fact, and the word "capsule" is worth adding there too.
4. **Presenter pack.** `PRESENTER-PACK-workflow.md` still carries slide titles for slides 6, 9, 10, 11, 12, 13,
   14, 17 and 20, all of which changed this pass, and its hard question 8 was already flagged by W3 as
   contradicting the report. Its owner should regenerate it from the built deck.
5. **Q-G5 count.** Slide 20's title now says "3 decisions wait", matching report §7 "3 decisions waiting".
   Anything still quoting "2 questions outstanding" (`HANDOFF.md` §10) needs the same change.

## DOUBTS

1. W5 asked for the slide 9 scope line as a new face line above the THUS strip. The figure ends at 6.25 and the
   strip starts at 6.38, and the figure call is not mine to move, so the scope went into the title instead. The
   title therefore says "CLI path" rather than "CLI-agent path"; the full term survives in the THUS strip and
   the figure. Settled by a render of slide 9.
2. W5's slide 14 title ("TruthInsightBench scores verification: published agents reach 11% to 16% on control
   testing") is 89 characters and the title box holds 57 at 30 pt, so it would have wrapped across the rule. The
   rewrite keeps "control testing" and the range and asserts the equation with verification, which the report
   states in §3.2 but does not put in those 4 words. A supervisor could object that control testing is 1
   verification dimension of 6, not verification itself.
3. Slide 15 now has 6 things stacked between the rule and the THUS strip. The estimator puts the table bottom at
   5.57 in with the provenance line at 5.88, but PowerPoint grows the AI4Research row past its declared height.
   Settled by looking at `slide-15.png` after the next render; if it is tight, the lead line is the one to cut.
4. Slide 11's takeaway line dropped the words "confidence number", so 0.85 is now introduced as "a verdict …
   tops out at 0.85". The figure's decision table is what has to make that readable at slide width.
5. "21 of the 79 capsule manifests declare a trust class, so most evidence carries no declared class" is W5's
   sentence. The second clause infers the evidence class from the manifest count; no source counts evidence
   items by declared class. Settled by counting declared classes in the delivered artifacts of 1 run.
6. Slide 17's header row is still 1.65 in tall for 1 line of text, which is where the spare space on that slide
   sits. Lowering only the header needs a per-row height, which `deckkit.table` does not take.
7. The deck is 15:15 and both talks 35:45 against a 40:00 target. Everything in W5 Part 2.2 is applied, so the
   spare 4 minutes are available for the capsule deck rather than this one.
8. The report lane's §6.1 #1 now settles on a 78% to 81% evidence-auditability band, but `REPORT.md` in this
   worktree still reads "58.4 to 60.3 band" at line 660, so the 2 lanes have to be merged before the deck's
   slide 14 totals line can be read against it. Settled by a grep for "58.4" after the merge: the only surviving
   use should be slide 14's totals line and App. A Table A1.
9. `notes/report-general/build/fig/` had to be copied into the worktree for the builder to run. It is
   gitignored, so it will not reach the merge, but the next agent in a fresh worktree hits the same
   `FileNotFoundError` on `fig/slide/fig-workflow.png`.
