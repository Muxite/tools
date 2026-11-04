# Review: workflow deck (general), slides 1 to 20

Read once, in order. Source: `build_deck.py`; render `overnight/render/general-deck/`; report `REPORT.md`.

## Verdict

1. Mostly followable from slides alone: titles and THUS strips carry the spine, and slides 4 to 11 need no speaker.
2. It drags over 5, 6 and 7: 2:50 of pre-freeze detail, and slide 6's figure redraws the BINDING row of slide 4.
3. It jumps at 14 and 15: slide 14's title reads as an AI4Research score, and slide 15's THUS ranks AI4Research
   against a table with no AI4Research row.
4. Four slides need words only in the notes: 9 (1 box hides 6 model calls), 11 ("0.9"), 15 (who 71.70 is), 20
   ("none of this is built yet").
5. Time is exactly 15:20, so every addition must be funded by a cut in section 3.

## Findings

| # | Slide | Flaw class | What is wrong (quoted) | Proposed exact edit | Sev |
|---|---|---|---|---|---|
| 1 | 2 | No source footer | 4 claims, footer empty | Add footer `Report §1` | must |
| 2 | 9 | Box hides >1 model call | 1 MODEL box "Compile / intent, requirement, plan" | Relabel "Compile: 6 model calls, each checked by code (slide 4)" | must |
| 3 | 11 | Unexplained number | "not_supported · 0.9", "partially_supported · 0.85" | Line above the table: "each verdict carries a confidence number; 0.85 is the best a claim with no experiment reaches" | must |
| 4 | 14 | Title over-claims | "TruthInsightBench: 11% to 16% on control testing" | "Published coding agents earn 11% to 16% of the control-testing points" | must |
| 5 | 15 | Slide cannot carry its THUS | "AI4Research checks the most and generates the least" over a table with no AI4Research row | Add the row report Table 6 already has: `AI4Research (code read) \| frozen DAG, 1 compile \| grading rules hashed with the plan; 23 code gates, 20 rubrics \| no external score` | must |
| 6 | 15 | Setup unstated | "Terminal-Bench test 77.36 vs 71.70" | "Terminal-Bench test 77.36, against 71.70 for Claude Code" | must |
| 7 | 18 | Term before definition | "Move to dsh; hash-and-approve runners" | "Move to DeepSeek Harness; hash-and-approve runners" | must |
| 8 | 20 | "Proposed" not stated | 4 unmarked bullets; "None of this is built yet" only in SAY | Line above the bullets: "Proposed. None of this is built or measured." | must |
| 9 | 8 | Tiny font | "FIXED AT THE FREEZE" card: `contract_sha256`, `on_failure_exhausted stop \| fail_run` and the "Each tick, per node…" block render near 10 pt | Cut that block and the "capsule bound per node (illustrative)" letter key; reflow the card at 14 pt | must |
| 10 | 3 | Title is a topic label | "What AI4Research is, in 6 terms" | "A capsule is a contract, a freeze is a hash: the 6 terms" | should |
| 11 | 3 | Data before needed | "80 registered, 79 manifests"; "(45)"; "(102, 63 enabled)" | Drop all 4 counts; change slide 12's cell to "21 of the 79 capsule manifests" | should |
| 12 | 4 | Term before definition | Labels "IntentIR" (defined slide 5) and "Dispatch / Kahn order, ticks" (never defined) | "Compile intent / structured record of the request"; "Dispatch / dependency order, ticks" | should |
| 13 | 5 | Number with no referent | THUS "20 of the 43 checks are model rubrics" | "20 of the 43 registered checks are judged by a model, not by code" | should |
| 14 | 7 | Internal codes | "capsule_plan", "scheduler_input", "run_contract.frozen"; "test_policy · evaluation_binding" | Gloss each box under its name ("the plan", "operators bound", "the grading rules", "the schedule", "the sealed contract"); retitle the callout "inside the hash: what counts as success" | should |
| 15 | 12 | Non-parallel row, codes | Row "trust declared at all \| 21 of 79 manifests \| " with an empty cell; `measured_execution` | Move that row below the table as a sentence; head the column "Evidence class (the label stored with the result)" | should |
| 16 | 14 | Colour named wrongly | "red, hatched: dimensions that need the agent to try to break its own result" while bars render orange | Drop "red, " | should |
| 17 | 5, 15, 20 | Font below floor | Table headers built with `head=13`; slide 15 body `size=14` | `head=14` throughout; `size=15` on slide 15 | should |
| 18 | 17, 18 | Mismatch with report | Column head "What would fix it"; report Tables 9 to 12 say "What would settle it" | Use "What would settle it" on both | should |
| 19 | 17 | Empty bottom third | 3 rows at 15 pt end at 62% of slide height | Add "1 to 3 of 6" after the section label; body 17 pt, `row_h=1.1` | should |
| 20 | 18 | Term before definition | "Count plan defects per run; the generalist capsule" | "Count plan defects per run; a fallback capsule for steps nothing fits (capsule talk)" | should |
| 21 | 19 | Internal code | "NOT_TESTED is not FAIL" | "a check that did not run is not counted as a failure" | should |
| 22 | 20 | Title is a topic label | "Next, and what needs deciding" | "The platform move first, the external number before any comparison" | should |
| 23 | 1, 2 | SAY over budget; empty bottom | Slide 1 SAY is 38 words at 0:15, 2.53 per second against a 2.3 cap; slide 2's bullets end at 70% | Cut "and where it runs next" from slide 1 SAY; slide 2 bullets to 24 pt | nice |

## "So what" cuts

1. **Slide 6 entire (0:55, 98 SAY words).** Its figure redraws slide 4's BINDING row. Keep the 3 facts by editing
   slide 4 to "Hard filter / 13 exclusion codes, 80 capsules" and "Validate / 8 codes", plus a THUS on slide 4:
   "the model picks only among capsules code admitted; if none fits, the plan fails at the freeze". Funds 5, 9, 19.
2. **Slide 8: "Each tick, per node: projection re-verified, operator from frozen candidates, capsule run in its write
   scope, closed on PASS" plus the letter key** (about 40 words at 10 pt). The tick panels show it already.
3. **Slide 3: the 4 registry counts** ("80 registered, 79 manifests", "(45)", "(102, 63 enabled)"). Unused until
   slide 12, which restates 79. About 12 words.
4. **Slide 15: the "Plans" column** (4 cells). Title and THUS are both about checking, and the width pays for the
   AI4Research row. About 20 words.
5. **Slide 19 entire (0:35, 65 SAY words).** It restates slide 2's claims and the headline of 17 and 18, and slide 20
   opens on the same next steps. Keep only if the 0:35 is not needed elsewhere.

## Shown before it is defined

- `IntentIR`: slide 4 figure; defined slide 5.
- `Kahn order` / `Kahn ready set`: slides 4 and 8; never defined.
- `rubric`: slide 4 box and slide 5 THUS; defined slide 10.
- `43` registered checks: slide 5 THUS; the 23 + 20 split arrives slide 10.
- `manifest`: slide 6 "copied from the manifest"; never defined.
- `0.9 / 0.85 / 0.35 / 0.3`: slide 11; never explained.
- `measured_execution`, `fixture_or_adapter_only`: slide 12; never explained.
- `dsh`: slide 18; the deck otherwise writes "DeepSeek Harness".
- `generalist capsule`: slide 18; belongs to the capsule talk, which runs after.
- `NOT_TESTED`, `FAIL`: slide 19; only in an IF ASKED note on slide 13.

## Footers on slides 17 and 18

Both hold after the merge to 6. Report §6.1 numbers exactly 6 across 4 tables: Table 9 has challenge 1, Table 10 has 2,
Table 11 has 3 and 4, Table 12 has 5 and 6. Group D (capsule library) adds no numbered challenge, so nothing is
orphaned. Slide 17 shows 1, 2, 3 and cites "Report §6.1, Tables 9 to 11": correct. Slide 18 shows 4, 5, 6 and cites
"Tables 11 and 12": correct. Two fixes only: the column head (finding 18), and slide 18 naming no section, so make its
footer "Report §6.1, Tables 11 and 12".

## Applied / rejected

Applied in `build_deck.py` (13 edits, no figure or REPORT.md change):

- **1** slide 2: `d.slide(... "Report §1", stage="freeze")`.
- **2** slide 9: the "Compile" box lives in `fig-trust.png`, so the PNG was left alone and a slide-face line was added
  under it: "'Compile' here is the 6 model calls drawn on slide 4, each one checked by code." Figure `max_h` 4.75 → 4.2
  to make room above the THUS strip.
- **3** slide 11: `point()` line "Each verdict carries a confidence number: 0.85 is the best a claim with no experiment
  reaches." Figure moved to y=2.02, `max_h` 4.1 → 3.9.
- **4** slide 14 title: "Published coding agents earn 11% to 16% on control testing" (58 chars, stays 1 line at 30 pt).
- **5** slide 15: the AI4Research row was added (`d.table` takes rows). To pay for it, `row_h` 0.95 → 0.75, `y` 1.65 →
  1.60, `head` 13 → 14. Estimated height 4.64 in, ending at 6.24, clear of the THUS at 6.38. The "Plans" column was
  kept: dropping it is a 4-cell rewrite and the row fits without it.
- **6** slide 15: "Terminal-Bench test 77.36, against 71.70 for Claude Code".
- **7** slide 18: "Move to DeepSeek Harness; hash-and-approve runners; sandbox access logs".
- **8** slide 20: "Proposed. None of this is built or measured yet." at 18 pt bold above the bullets; bullets moved to
  y=2.35, h=2.6, so the question table at y=5.05 is untouched.
- **13** + the `rubric` gloss, slide 5 THUS: "code checks every model output; 20 of the 43 checks are rubrics, judged by
  a model". The full wording proposed in finding 13 is 94 chars against the strip's 89-char cap.
- **18** slides 17 and 18: column head "What would settle it".
- **21** slide 19: "a check that did not run is not a failure (NOT_TESTED)".
- `manifest` gloss, slide 3: "YAML contract (its manifest) for 1 capability; 80 registered, 79 manifests".
- Slide 18's footer already reads "Report §6.1, Tables 11 and 12" in the script; no edit was needed.

Not applied:

- **9** slide 8: the "FIXED AT THE FREEZE" card and the letter key are inside `fig-dag.png`, which `figures.py` draws.
  **Left for the morning:** it needs a figure change, not a script change.
- **10** slide 3 title: a "should"; the 6-term table is the definition slide and the current label is honest about that.
- **11** slide 3 counts: dropping them also requires editing slide 12's cell, which is a second slide's claim.
- **12** slide 4: "IntentIR" and "Kahn order" are labels inside `fig-workflow.png`. Figure change, not script.
- **14** slide 7: the internal codes are box labels inside `fig-freeze.png`. Figure change, not script.
- **15** slide 12: moving the row out of the table is a table plus body-text rewrite, above the edit budget here.
- **16** slide 14: "red, hatched" is the figure's own legend wording inside `fig5-benchmarks.png`.
- **17** fonts: applied only where it was free (`head=14` on slide 15). Slide 5 and slide 20 keep `head=13` and slide 15
  keeps `size=14`, because the AI4Research row needs that width; raising them risks overflow that cannot be checked
  without a build.
- **19** slide 17: raising the body to 17 pt and `row_h` to 1.1 pushes 4 rows of dense evidence text; not safe unbuilt.
- **20** slide 18 "generalist capsule": the gloss belongs to the capsule talk, and the cell is already 3 lines.
- **22** slide 20 title: a "should"; the new "Proposed" line now carries the slide's real point.
- **23** slide 1 SAY and slide 2 bullet size: "nice", and no TIME changes were made this pass.
- Cut 1 (**slide 6 entire**): not applied. Slide 4 is a single PNG from `figures.py`, so its 3 facts cannot become
  labels there, and its figure runs y=1.55 to 6.95, leaving no room for a THUS strip at 6.38. Proposed edit, for the
  user: redraw `fig-workflow.png` with "Hard filter / 13 exclusion codes, 80 capsules" and "Validate / 8 codes",
  shorten it to `max_h=5.0`, add `d.therefore(s, "the model picks only among capsules code admitted; if none fits, the
  plan fails at the freeze")`, then delete the slide 6 block (lines for "2 Workflow · Binding") and move its
  UNSATISFIABLE_CAPSULE sentence into slide 7's SAY. No later footer or SAY names "slide 6" by number, so nothing else
  breaks.
- Cuts 2, 3, 4, 5: 2 is inside a PNG; 3 needs slide 12 edited too; 4 was unnecessary once the row fitted; 5 (cut slide
  19) removes a slide, which is the user's call, not a triage fix.
- Terms left unglossed for lack of a script-side first use: `IntentIR`, `Kahn order` (both PNG-only), `43 registered
  checks`, `measured_execution` / `fixture_or_adapter_only`, `generalist capsule`.

Slide count unchanged at 20; no TIME value was changed, so the deck still plans to 15:20.
