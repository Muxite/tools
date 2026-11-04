# R2 capsule deck: last editorial pass on slide faces and speaker notes

Written 2026-09-15. Worktree `r2-capsule-deck`. Nothing committed.

## OWNED

- `notes/report-capsules/deck-src/build_deck.py`, the whole file except every `d.figure(` call
- `notes/pass2/review/R2-capsule-deck.md`

## TOUCHED

- `build_deck.py`: title slide, 3, 4, divider 5, 9, 10, 11, 13, divider 17, 18, 19, 20, 21, 23, 24, 25, 26,
  plus slide 2 (1 bullet)
- No `d.figure(` call, `figures.py`, `figdata.py`, `deckkit.py` or `REPORT.md` was touched
- `notes/report-general/build/deck-times.json` was written by the builder and reverted with `git checkout`, so the
  only tracked change in this worktree is `build_deck.py`
- To run the builder I copied `notes/report-general/build/fig/` from the main tree into the worktree. That path is
  in `.gitignore:2`, so it is not part of the diff

## CHANGES

### Presenter rule (face carries the point, SAY says the face plus a little more, 20 to TIME x 2.3)

| Slide | Before -> After | Why |
|---|---|---|
| 1 title | SAY 19 words -> 36, adding "It keeps a library of capabilities that the system checks, adds to and retires while it runs." | below the 20-word floor; the subtitle's claim was never spoken |
| divider 17 | TIME 0:05 SAY 8 words -> TIME 0:10, "Now the design, which puts the 6 rules together into 1 system. Nothing in it is built or measured yet." | below the floor, and the face's "Proposed" line went unspoken |
| 10 CoEvoSkills | SAY 115 words against a 115-word budget -> 113 ("no better than just reading" -> "no better than reading"; "with most skills done in about 2" -> "and most skills need about 2") | over budget on the strict check |
| 19 generalist | new face item `capped per plan`; SAY gains the cap and drops 4 words elsewhere | the cap was IF ASKED only, so the face did not carry it |
| 23 lifecycle | 3rd right-hand card line `Model weights never change: the library does`; SAY gains the same point | "what may change" was in the report (App. G.5) and nowhere on a face |
| 24 evaluation | THUS, table and bullets unchanged; SAY now says the track-A reason that the face states | SAY must say the face's content |
| 4, 9, 13, 20, 21, 25, 26 | SAY rewritten or extended, see below | |

No MUST HIT anywhere; no "I'm not going to", "I'm not claiming", "to be fair", "quick one on", no fairness hedge,
no em dash, no we/our on any face (checked over the built file).

### First-time-viewer rule

| Slide | Before -> After | Why |
|---|---|---|
| 3 MCP | SAY "Quick one on MCP, because people use it to mean tool. It's a client-server protocol." -> "MCP is a client-server protocol for reaching tools, data and prompts." | announces why the slide exists and corrects the audience before they speak (W5 1.4) |
| 3 MCP | SAY "since the latest revision every request carries its own version" -> "In revision 2026-07-28 every request carries its own version" | "the latest revision" is relative to an unstated earlier one; the footer names the revision |
| 9 BTC face | "These 222 tools are not Alita-G's; Alita-G's own tools were never tested on new inputs." -> "222 tools from 3 other tool-making methods on 1 model; Alita-G's tools were never tested this way." | rebuts a comparison the slide never draws, in the "not X" shape (W5 1.4) |
| 9 BTC SAY | "This paper asks the question Alita-G never does: do these tools work beyond the 1 task that made them?" -> "This paper asks what Alita-G never does: whether these tools work beyond the 1 task that made them." | rhetorical question |
| 9 BTC SAY | "So how did Alita-G gain 8 points? First, these are not Alita-G's tools... Second, its tools came from..." -> "Alita-G's 8 points came from tools built on the same GAIA questions it was scored on, the kind of input a fitted tool passes." | question raised in order to be answered, plus a numbered rebuttal (W5 1.4); the duplicate IF ASKED bullet "Alita-G's own tools were never tested on held-out inputs" was cut, since the face now says it |
| 19 generalist SAY | "the frozen task graph, now with capsules on each step" -> "the frozen task graph from the workflow talk, with a capsule on each step" | "now with" implies a version the viewer never saw |
| 19 generalist SAY | "runs as before" -> "runs as the workflow talk described" | banned relative phrase; matches REPORT §4.1's own fix |
| 21 admission SAY | "A new version isn't a duplicate of the capsule it replaces." -> "The duplicate check compares a candidate with every registered capsule except the one it versions." | answers an objection nobody raised, in the "not X" shape (W5 1.4) |
| 23 lifecycle SAY | drafted "None of this is a new invention: DeepSeek Harness already publishes..." -> "DeepSeek Harness already publishes..." | caught in my own draft; same defensive shape |
| 25 verify first SAY | "do the same gaps come back? If most appear once..." and "do real effects ever differ...? If they don't..." -> "it counts how often the same gap comes back. If most appear once..." and "2 checks on the capsules we already have: whether real effects ever differ..." | 2 rhetorical questions raised to be answered |

Kept as the argument, per the brief: rule slides R1-R6, the 4 "Wrong if..." bullets on slide 24, slide 12's
"It didn't break the check, it broke what the check reads", and slide 24 IF ASKED's control-group bullet.

### Coverage (W5 Part 1.2 and Part 3)

| Q# | Slide | What went in | Seconds |
|---|---|---|---|
| 20 | divider 5 | subtitle "Each result, then the design rule it leads to" -> "5 results: 1 shows the loop works, 3 show that judging by the outcome alone fails, 1 shows when to build"; SAY rewritten to match | +5 (TIME 0:10 -> 0:15; the face now makes a 5-part claim) |
| 8 | 9 | face point rewritten (above) | 0 |
| 13 | 13 | R5 line already read "the builder hears only admit or reject, at most 5 times", which is stronger than the proposed "a capped number of times" | no change needed |
| 11 | 13 | SAY + "Each of the 3 results comes from a different model, so what carries across them is the pattern, and the control for my own numbers is the 79 hand-written capsules." | +10 |
| 14 | 19 | face strip + "capped per plan"; SAY + "and is capped per plan, so it cannot route around the typed contracts"; IF ASKED bullet rewritten to say where the cap's value comes from (gap census, step 2) | 0 |
| 4 | 20 | SAY + "So 1 admission costs 3 model sessions, an effect check, and a suite re-run for as long as the capsule lives." | +10 |
| 25 | 21 | IF ASKED + "The suite author and the implementer can share 1 misreading of a new capability, since a research step has no ground-truth oracle. The control group and the effects check catch it" | 0 |
| 17 | 23 | face card + "Model weights never change: the library does"; SAY + "The model weights never change. What changes is the library, then the context and prompts." | 0 |
| 15 | 23 | SAY + "DeepSeek Harness already publishes durable data as version-named successors, so append-only versioning is the platform's own rule." | +11 |
| 18 | 23 | SAY + "Every admitted capsule's suite is re-run on a schedule, so one that breaks later is caught and retired." | +9 |
| 3 | 24 | track-A cell -> "task scores with no library, a library without the gate, and with it, since the evidence splits on whether a library helps"; SAY says the same | 0 |
| 16 | 25 | row 7 assumption cell "start values: 2 sprints, 5 gate tries" -> "starts: 2 sprints from AllocBench, 5 gate tries from CoEvoSkills" | 0 |
| 23 | 26 | SAY + "Steps 1 to 7 change code that already exists and read data the system already writes, so the cold path at step 8 is the only new subsystem." | +10 |
| 4 (optional) | 11 | proposed as a 4th DGM face bullet; a 4th 18 pt bullet at y=5.35 overflows the body area, so it went to IF ASKED as "Self-improvement is not cheap: 1 SWE-bench run of this loop cost about USD 22,000, against about USD 10,000 for either baseline" | 0 |

Q12 (what happens when the builder never passes the gate) was **not** added to slide 20's SAY. It costs 9 seconds
that the 22:00 cap does not have, and it is already answered under IF ASKED on slide 18, "Out of tries or time, the
gap goes back to the build-decision agent".

### Mistakes

| Slide | Found | Fix |
|---|---|---|
| 2 goal | "A system like this already exists (Alita-G)" names a paper 4 slides before its arXiv id appears | "(Alita-G, arXiv 2510.23601)" |
| 4 DSH | SAY said "The framework underneath calls that the time half of composability" and IF ASKED said "The same paper warns...", naming no paper | footer gains "· A Programming Paradigm for Spatiotemporal Composability (arXiv 2608.25512)"; SAY reads "That is the time half of composability"; IF ASKED reads "The composability paper warns..." |
| 18-23 | "Proposed" appeared only on the divider before them, and the supervisor's first question is what is built | eyebrow "4 Design" -> "4 Design (proposed)" on all 6 design slides |
| 24, 26 | footers "Table 7 rows 1-3" and "Table 7 rows 8-11" | "Table 7" on both, per the report lane's cross-reference |
| 26 | SAY "it's the only step that proves the platform does what its paper claims" | "it is the only step that needs a running DeepSeek Harness", the report §6 wording |

Verified identical to the report and left alone: 79 hand-written capsules and 5 gaps (§3, App. B); 13 assumptions
in Table 7 (§5.1) with slide 25 showing 7 of them; 9 work steps in §6 and 9 on slide 26; 2 sprints and 5 gate
tries as proposed starts (§6); k = 10 sprints (§5.2); Alita-G 75.15 -> 83.03 with 15.5% fewer tokens and the
3-harvest plateau (§2.1, App. A.1); 96.8% of 222 tools (§2.3); 41.1% against 71.1% (§2.4); DGM 20.0% -> 50.0% on
SWE-bench Verified (§2.5); AllocBench 4% abstract against 92% code-required for Opus (§2.8); the 26 -> 128 tools
and 100% -> 51% distinct share; 16 points on 25 questions; 13 wrong-to-right flips out of 165. Every footer's
section, figure and table number was checked against `REPORT.md` (Figs. 8-13 for slides 18-23, Tables 6-8 for
24-25). R1-R4 on slide 8, R3 and R5 on slide 13, R6 on slide 15, all 6 collected on the slide 18 figure and named
in its SAY: ascending throughout.

### Layout

The builder ends with **0 WARN**. Three problems were found and fixed during the pass, 2 of them caused by my own
additions and invisible to the builder's own checks:

1. Slide 9, the rewritten face point needed 0.65 in in a 0.62 in box. Shortened to 97 characters, 1 line at 17 pt.
2. Slide 24, the longer track-A cell grew the table from 2.54 in to 2.83 in, so its bottom would have landed at
   y = 4.58 over the bullets at y = 4.30. `d.table`'s own check only fires past y = 7.1, so it printed nothing.
   Reworded to 122 characters, which keeps the cell at 2 lines and the table bottom at 4.30.
3. Slide 25, the longer row-7 cell pushed the table bottom from 6.14 in to 6.44 in, under the THUS strip at 6.38
   (the "THUS strip over a table" flaw class). "start values:" -> "starts:" keeps the cell at 2 lines and the
   table bottom at 6.21.

Found by replaying `deckkit`'s own row-height estimate over the built file and comparing each table's predicted
bottom with the next shape below it. W1's finding that slide 4's figure fills the face still holds, so the
composability line stays on slide 2 and the paper's name went into slide 4's footer instead.

## TIME

| Slide | Before | After |
|---|---|---|
| divider 5 The evidence | 0:10 | 0:15 |
| 9 Beyond Task Completion | 1:10 | 1:05 |
| 13 independent check | 0:55 | 1:05 |
| divider 17 The design | 0:05 | 0:10 |
| 20 build | 1:00 | 1:10 |
| 23 lifecycle | 1:10 | 1:25 |
| 26 next | 1:10 | 1:20 |

**Capsule deck 21:05 -> 21:55** (cap 22:00). **Both decks 36:00 -> 36:50** (target 40:00, max 45:00). Every one of
the 26 slides is now between 20 words and TIME x 2.3; the tightest are slide 5 (34 of 34.5), slide 19 (102 of
103.5), slide 20 (159 of 161), slide 23 (193 of 195.5), slide 25 (125 of 126.5) and slide 26 (181 of 184).

## CROSS-REFS

1. **Slide 9's face point is 11 characters shorter than W5's text.** The coordinator asked for "These 222 tools
   come from 3 other tool-making methods on 1 model; Alita-G's tools were never tested this way." (108 chars); at
   17 pt that wraps to 2 lines and overflows its 0.62 in box. The deck says "222 tools from 3 other tool-making
   methods on 1 model; Alita-G's tools were never tested this way." Same claim, 1 line, same type size. If the
   report quotes the deck line anywhere, use the shorter form.
2. **Slide 25 row 7 now reads "starts: 2 sprints from AllocBench, 5 gate tries from CoEvoSkills"**, not W5's
   "start values: ...", for the same 1-column width reason.
3. **Nothing in `REPORT.md` needs to change for this pass.** Every claim added to a face or a SAY was taken from
   text already in the report: the admission cost from §4.2 Table 5 and §4.5; the DSH successor-versioning fact
   from §4.5 and App. D; the audit re-run from §4.5; the model-weights rule from App. G.5; the generalist cap from
   §4.1 and App. G.3; the shared-misreading limit from §4.3; the DGM USD 22,000 from App. A.4; the 2-and-5 sources
   from §2.8 and §4.3; "steps 1 to 7 change code that already runs, step 8 is the only new subsystem, step 9 the
   only step needing a running DSH" from §6.
4. **The composability paper is now named on a deck face** (slide 4 footer, "A Programming Paradigm for
   Spatiotemporal Composability (arXiv 2608.25512)"). It was reference [1] in the report and unnamed on every
   slide. If a footer style rule says papers appear only in `DEMONSTRATED BY` strips, this is the exception.
5. **Design-slide eyebrows now read "4 Design (proposed) · …"**. Any crib sheet, render index or presenter pack
   that quotes the eyebrow text for slides 18 to 23 needs the same change.

## DOUBTS

1. **Slide 24's table bottom and the first bullet both sit at y = 4.30.** That is the geometry the deck already
   shipped with, and the estimate is conservative (a real 2-line 17 pt row is nearer 0.63 in than the estimated
   0.68), but it is 0.00 in of clearance. Settled by: rendering slide 24 to PNG and looking, which I was asked not
   to do.
2. **"4 Design (proposed)" on 6 eyebrows may read as over-labelling** next to the divider that already says it.
   Settled by: the user seeing 1 rendered design slide and saying whether the divider was enough.
3. **21:55 leaves 5 seconds of headroom.** Any sentence a later pass adds to a capsule SAY will need a TIME rise
   that breaks 22:00, and the tightest 6 slides above have between 1.5 and 3 words of slack each. Settled by: the
   user raising the capsule cap, or cutting a slide.
4. **Q12 is unanswered on a face.** "What happens when the builder never passes the gate" lives only in slide 18's
   IF ASKED. It is a supervisor question and the answer ("not building is a valid answer") is already the last
   line of the R6 rule slide, so it is reachable, but no face says the tries are finite except the R5 line's "at
   most 5 times". Settled by: 9 seconds of budget.
5. **"Model weights never change: the library does"** compresses App. G.5's 4-item reversibility order into 1
   line to fit a 55-character column. The SAY carries the fuller version ("the library, then the context and
   prompts"), and the admission checker's "never by the system itself" appears on neither. Settled by: the user
   deciding whether the checker's immutability needs a face of its own.
6. **The divider 5 subtitle asserts a grouping** ("3 show that judging by the outcome alone fails") that counts
   Beyond Task Completion, CoEvoSkills and the Darwin Gödel Machine as 1 argument each. That matches §2.7 Table 2
   exactly, but DGM occupies 2 slides, so a viewer counting slides will count 6 evidence slides against 5 results.
   Settled by: accepting it, since the DEMONSTRATED BY strips name 5 distinct papers.
7. **Slide 3's "In revision 2026-07-28 every request carries its own version and capabilities, so there's no
   session to set up"** drops the contrast with older MCP that made the point interesting. It is now a flat fact
   about a named revision, which is what the first-time-viewer rule asks for and slightly less informative for
   anyone who knows the older protocol. Settled by: the user preferring the comparison back.
8. **I could not render.** Every layout finding here comes from `deckkit`'s estimator plus a shape-overlap replay
   over the built `.pptx`, not from looking at a slide. The 3 problems it caught were all real; what it cannot
   catch is anything inside a figure, or a table whose real PowerPoint wrapping differs from the estimate.
