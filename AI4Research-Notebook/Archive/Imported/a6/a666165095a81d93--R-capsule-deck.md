# Review: Capability Capsule deck (26 slides, 20:15)

Read once, slide 1 to 26, no backtracking. Budget check: `deck-times.json` = 920 + 1215 s = **35:35**, so
there is 4:25 of headroom under the 40:00 target. The must-fixes below cost seconds, not minutes.

## Verdict

1. Yes, the talk can be followed from the slides alone, with 1 exception: **AI4Research is never defined**, and it
   first appears as a bare column header on slide 7, so the audience meets "our system" without being told what it is.
2. The evidence-to-rule build-up holds: Alita-G → R1-R4 (8), the 3 failure papers → R3 precise + R5 (13),
   AllocBench → R6 (15), and every badge on the design figure (18) traces back. Rules match report Table 4 exactly.
3. It drags at 19 (4-panel DAG plus a 9 pt freeze card in 45 s), 21 (3-column gate figure in 65 s) and 25
   (7 assumption rows in 55 s, 13 pt type).
4. It jumps twice: slide 7 assumes AI4Research, and slide 18 shows "R1-R6" as black badges 10 slides after the rules
   were last stated, with notes that never name them.
5. Tonight's changes are close: slide 9's new line is the right idea but omits the load-bearing fact (the 222 tools
   are not Alita-G's); 24 drops the control group that the report treats as body text; 25 and 26 are correct but
   over-full and under-sized.

## Findings

| # | Slide | Flaw class | What is wrong (quote) | Proposed exact edit | Severity |
|---|---|---|---|---|---|
| 1 | 7 (first use), 2 | Term before definition | Column header `AI4Research`, and `2 EVIDENCE` runs before any definition | Slide 2, bullet 1 → "AI4Research, our multi-agent framework, compiles a request into a frozen graph of gated steps. It is to improve itself and its tools by keeping a library of capabilities it adds to while it runs" | must |
| 2 | 8, 15 | Source footer missing | Both rule slides render with only a page number; `rule_slide()` calls `d.slide("→ Design rule", title, stage="build")` with no source | `rule_slide(..., src="Capsule report §2.2, Table 1; Table 4")` on 8 and `src="Capsule report §2.8; Table 4"` on 15 | must |
| 3 | 24 | Coverage mismatch | Control group is only in IF ASKED: "the 79 hand-written capsules take the same held-out tests"; report §5 states it in body prose | Add 4th bullet: "Control: the 79 hand-written capsules take the same held-out tests, so a failure belongs to the generated capsule, not the test" | must |
| 4 | 9 | Over-claim / incomplete reconciliation | "Alita-G was scored on the questions its tools came from; its tools were never tested on new inputs." | Replace with: "These 222 tools are not Alita-G's. Alita-G was scored on the questions its tools came from, and its tools were never tested on new inputs, so its 8 points are unexplained either way." | must |
| 5 | 19 | Layout / tiny font | Freeze card lines `contract_sha256 9f3a…`, `on_failure_exhausted stop \| fail_run` render at about 9 pt | Drop `contract_sha256`, `operators`, `evaluator_gate` rows from the card and re-render the remaining 6 fields 2 sizes larger | must |
| 6 | 20 | Illustrative content unmarked | "gap record: 2 sprints, 7 instances" and Sprint 3 building, with no marker, though 2 sprints is an open question | Add under the hot-path band: "threshold 2 sprints is illustrative: the real value comes from the census" | should |
| 7 | 25 | Tiny table, too many rows | 7 rows at `size=13, head=13`, below the 14 pt floor | Keep rows 1-4, move "practice feedback", "embeddings rank" and "start values" to IF ASKED, set `size=15, head=14` | should |
| 8 | 4 | Term before definition | Figure says "DSH today: tools only" and "DSH: planned"; the abbreviation is never expanded on a slide | Band label → "DEEPSEEK HARNESS (DSH) · everything is a plugin, with no privileged core" | should |
| 9 | 9 | SAY over budget | 157 words in 65 s = 2.42 words/s, above the 2.3 cap | Cut "Its paper also shows 1 tool reused on a different question, so the evidence goes both ways." to IF ASKED (now on the slide per finding 4) | should |
| 10 | 18 | Property only in prose | Legend "R1-R6: the design rules"; notes say only "The black badges are the 6 rules: every one of them sits on a box" | Notes → "…: R1 separate clocks on the cold path, R6 and R4 on the decider, R3 on the suite author, R5 on the gate, R2 on the sprint plan" | should |
| 11 | 15 | Thin slide / empty half | 4 lines occupy the top third; 30 s | Merge into 14 as a THUS strip: "THUS R6: a separate agent decides whether to build and never builds; nothing is built the first time a gap appears" | should |
| 12 | 19 | Jargon | "T1 Kahn ready set: A, B, F", "node E, as SchedulerInput holds it", "blocked_by_failed_dependency" | "T1 Ready: A, B, F (all dependencies passed)"; "step E, as the scheduler holds it"; "skipped: a dependency failed" | should |
| 13 | 19 | Meta note / talk-order dependency | SAY: "This is the task graph from the workflow talk, now with capsules." | "This is the frozen task graph, now with capsules on each step." | should |
| 14 | 2, 24 | Layout | Wrapped bullets lose their indent: "runs", "research runs", "design", "selection" start at the left margin | Set a hanging indent in `d.bullets`, or shorten each bullet to 1 line | nice |
| 15 | 5 | Timing | TIME 0:05 with 14 SAY words | Set 0:10 | nice |
| 16 | 22, 23 | Jargon / unexplained ids | "artifact types, effect ceiling, trust floor: exact, eliminates"; row label `cap.lit-review`, `.multilingual v1.0` | "types match, effects allowed, trust high enough: exact, eliminates"; label the row "one capsule (example): literature review" | nice |
| 17 | 13 | Numbering | R3 restated in new words ("passes held-out tests for its own job") without saying it is the same rule made precise | "R3 (now precise) Every capsule passes held-out tests…" | nice |

## Presentability

- **9** Three numbers on screen (100.0, 91.7, 96.8) plus the Alita-G reconciliation in 65 s. Point at the orange bar
  only, say "215 of 222", then read the 2 bold lines. With finding 4 the reconciliation is on the slide, so the SAY
  drops to the 2 sentences that matter.
- **13** The presenter has a 4-column table and 5 rule lines and nothing to point at first. Say the table left to
  right, one row per sentence, then R3 and R5.
- **19** The worst slide to present: 4 panels, a 7-state legend and a freeze card. Decide what the pointer visits:
  the card, then T2 (C on the generalist), then T4 (skipped). Everything else is the workflow talk.
- **20** Two halves and one arrow between them. Say "top half" and "bottom half" aloud (the notes do); the slide
  should also say it: add "1 sighting per sprint" as a label on the sprint band.
- **21** 6 manifest rows, 6 checks, 6 rejection codes = 18 items in 65 s. Announce that only 1 row is new
  (effects) and read that row; name the other 5 as a group.
- **24** "far fewer broken capsules" is a number with no context. Add the baseline in the THUS: "prediction, gate off
  vs on: similar task scores, and far fewer than the 96.8% of tools that fail their own tests".
- **25** 7 rows, 55 s. After the cut (finding 7) it is 4 rows and the gap census is the only one to dwell on.
- **26** Bottom-left third is empty and the list has no reason attached. Add a line under the list: "riskiest
  assumptions first: steps 2, 6 and 7 can all fail before the cold path exists".

## Terms used before definition

| Term | First use | Defined | Note |
|---|---|---|---|
| AI4Research | 7 (table column) | never | must fix, finding 1 |
| DSH | 4 (figure boxes) | never expanded on a slide | finding 8 |
| trust class | 4 ("trust class" in the capsule band) | 16 ("how far their outputs can be trusted") | 12 slides apart |
| Kahn ready set, SchedulerInput | 19 | never | finding 12 |
| effect ceiling, trust floor, provenance rank, fail-closed | 22 | never | finding 16 |
| node (vs "step" everywhere else) | 19 (card) | never reconciled | pick one word |
| generalist, gap record, sprint, manifest, suite author, EFFECT_ESCALATION, cold path, MCP | 18, 16, 7, 4, 18, 21, 18, 3 | same slide, in the figure or inline | all clean |

## "So what" cuts

| Cut | Why | Saves |
|---|---|---|
| Slide 15 folded into 14 as a THUS strip | R6 is 1 sentence; it does not need its own slide | 0:30 |
| Slide 11 bullets 1 and 2 merged; drop "added to the archive if it still works" | Only "the benchmark score drives it" feeds slide 12 | 0:15 |
| Slide 25 rows 5-7 to IF ASKED | The 3 head-to-heads are already on slide 26 as "test first" | 0:20 |
| Slide 3 SAY cut to the protocol sentence and the primitives sentence | This audience knows MCP; the figure carries the rest | 0:15 |
| Slide 22 sub-labels read as a group, not line by line | The point is the order, not the 4 stage names | 0:15 |

Total 1:35, which buys back the additions in findings 1, 3, 4 and 10 with room left.

## 5 questions the supervisor will ask that slides and notes do not answer

1. What does a generalist step cost against a capsule step, in tokens or wall clock? Slide 19 claims lowest trust and
   slide 24 prices "reuse repays admission", but no number or even an order of magnitude appears anywhere.
2. Who checks the suite author? The report names the risk (manifest writer and suite author sharing one misreading of
   a new capability), the deck never does, and the answer decides whether the gate is real.
3. How long is this, and who builds it? The 8 steps on slide 26 have no effort estimate, no owner and no sequencing
   against the co-op term.
4. What is the blast radius of a wrong admission? Slide 23 says results are "flagged" and the notes say results
   cannot be un-published, but nothing says who is told, or whether a downstream report is retracted.
5. DSH is 0.1.5-rc.2 and has never been run here. What must land on DSH before step 1, and what is the fallback if
   the sandbox access log (which the whole effects check depends on) is not usable?

## Applied / rejected

Applied (all in `deck-src/build_deck.py`; `ast.parse` clean, no build run):

- **1 (must)** Slide 2: new first bullet "AI4Research, our multi-agent framework, compiles a request into a frozen
  graph of gated steps; today all 79 of its capsules are hand-written" (report §1, §3). Same sentence opens the SAY;
  TIME 0:40 → 0:45 to pay for it (95 words, cap 103).
- **2 (must)** `rule_slide()` takes `src=None` and passes it to `d.slide()`. Slide 8: "Capsule report §2.2, Table 1;
  §4, Table 4 · Alita-G (arXiv 2510.23601); R3 from Beyond Task Completion and CoEvoSkills, next". Slide 15:
  "Capsule report §2.8; §4, Table 4 · AllocBench (arXiv 2607.23332)". Table 4 sits in §4, not §4.1 (REPORT.md:215).
- **3 (must)** Slide 24: 4th bullet "Control: the 79 hand-written capsules take the same tests; a failure is the
  build, not the test". To keep the box clear of the THUS strip, bullet 1 loses its tail "and what is left is better
  selection", which slide 25 row 2 already carries ("narrow to selection only").
- **4 (must)** Slide 9 second `point()` → "These 222 tools are not Alita-G's; Alita-G's own tools were never tested
  on new inputs." (88 chars: 1 line is the limit at y=6.6, where 2 lines trip `_check`). The "scored on the questions
  its tools came from" half stays in the SAY, which is 156 words against the 161 the new 1:10 allows, so no trim.
- **5 (must)** Slide 19 freeze card: **left for the morning**. It is drawn in `figures.py:538` inside
  fig-dag-capsule.png, which I do not own.
- **Legibility** Slide 25 table `size=13, head=13` → `14, 14`, all 7 rows kept: estimated height 4.66 in from
  y=1.55, so the last row ends above the THUS strip at 6.38.
- **8 (should)** Slide 4 title → "DeepSeek Harness (DSH): every layer is a plugin", so the figure's "DSH" is tied to
  a name. The band label itself is inside fig-stack.png.
- **10 (should)** Slide 18 SAY → "…R1 on the cold path, R4 and R6 on the build-decision agent, R3 on the suite
  author, R5 on the gate, and R2 on the sprint plan" (checked against the badge coordinates in `figures.py:434-435`).
  197 words against a 230 cap.
- **13 (should)** Slide 19 SAY → "This is the frozen task graph, now with capsules on each step."
- **15 (nice)** Divider "The evidence" TIME 0:05 → 0:10 (14 SAY words).
- **17 (nice)** Slide 13 → "R3  (now precise) Every capsule passes held-out tests for its own job before it is kept"
  (shortened tail so the line still fits on 1 line at 19 pt).

Rejected:

- **6 (should)** Slide 20 "2 sprints is illustrative": the band is inside fig-sprint-roles.png, and the THUS strip is
  already at its 96-character limit. The notes flag it under IF ASKED.
- **7 (should)** Slide 25 row cuts: rows 5-7 dropped is a content cut, left for the user (see below); 14 pt fits with
  all 7 rows, so the legibility half is done.
- **9 (should)** Slide 9 SAY trim: TIME is now 1:10, so 156 words is under the 2.3 words/s cap.
- **11 (should)** Slide 15 folded into 14: a slide cut, left for the user.
- **12 (should)** Slide 19 jargon ("Kahn ready set", "SchedulerInput", "blocked_by_failed_dependency"): all inside
  fig-dag-capsule.png, drawn by `figures.py`.
- **14 (nice)** Hanging indent in `d.bullets`: `deckkit.py` is not mine. Slide 24's bullets are now 1 line each bar 1.
- **16 (nice)** Slides 22, 23 labels: inside fig-select.png and fig-versions.png, drawn by `figures.py`.
- Presentability note on 24 ("far fewer than the 96.8% of tools that fail their own tests"): the THUS strip warns
  above roughly 96 characters and that text is 119.

Proposed cuts, for the user to decide (nothing cut tonight): slide 15 folded into 14 as a THUS strip (0:30);
slide 25 rows 5-7 to IF ASKED (0:20); slide 11 bullets 1 and 2 merged (0:15); slide 3 SAY cut to the protocol and
primitives sentences (0:15); slide 22 sub-labels read as a group (0:15). Total 1:35 against the 0:10 added tonight.
