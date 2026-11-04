# So-what pass: workflow talk (20 slides) and REPORT.md sections 1-7

Audience assumed: 1 supervising software engineer, co-op students who know agents/DAGs/CI, not this codebase.

## Part 1. Slides

| Slide | Element (quote) | So what | Verdict | Sec saved |
|---|---|---|---|---|
| 1 | Title + subtitle | orients scope of talk | keep | 0 |
| 2 | "the freeze is the 1 boundary" | names the central concept | keep | 0 |
| 2 | "generate well and check weakly...checks strictly" | states the whole thesis | keep | 0 |
| 2 | "DeepSeek Harness supplies the runtime...contract layer" | states platform decision up front | keep | 0 |
| 2 | "Plan: pipeline...evidence...SoTA...platform...challenges" | roadmap for 20 slides | keep | 0 |
| 3 | capsule / operator / sprint / gate / freeze rows | vocabulary reused every later slide | keep | 0 |
| 3 | "in -> out" row | frames whole system as one transform | keep | 0 |
| 4 | full pipeline figure (Fig.1) | gives the one mental map of the system | keep | 0 |
| 4 | model/code color legend | needed to read every later diagram | keep | 0 |
| 5 | IN/OUT strip | scopes the stage | keep | 0 |
| 5 | compile intent / validate / fidelity review / fill / check rows | shows model-then-code pattern with a real caught error | keep | 0 |
| 5 | THUS "20 of 43 checks are rubrics" | plants the rubric caveat used again slides 10,17,19 | keep | 0 |
| 6 | hard filter/select/validate/fit review/bind diagram | shows narrow-pick-narrow pattern | keep | 0 |
| 6 | orange "none fits: UNSATISFIABLE_CAPSULE..." callout | restates what THUS strip already says | cut | 5 |
| 6 | THUS "model picks only among admitted capsules" | crisp restatement of the whole stage | keep | 0 |
| 7 | freeze chain diagram (5 hashed artifacts) | the report's central mechanism, must stay | keep (protected) | 0 |
| 7 | "inside the hash" 5-item bullet list | headline sentence already makes the point; items are implementation nouns with no independent payoff | tighten to: "grading rules, not just the plan" | 8 |
| 7 | "Tested: priority set to 999...still says PASS" | concrete proof the hash actually catches tampering | keep | 0 |
| 7 | THUS strip | the freeze's one-line payoff | keep (protected) | 0 |
| 8 | "FIXED AT THE FREEZE" node-E field list | shows what a frozen node looks like | keep | 0 |
| 8 | contract_sha256 "9f3a..." line | a fake truncated hash conveys nothing beyond "there is one" | cut | 3 |
| 8 | "capsule bound per node" A-G roles | needed to follow the T1-T4 story | keep | 0 |
| 8 | T1 "F shares write scope with A" | shows concurrency-safety mechanism concretely | keep | 0 |
| 8 | T2 "B fails its frozen gate...repaired" | shows repair-with-findings mechanism | keep | 0 |
| 8 | T3 "a passed node never regresses" | states a real safety property | keep | 0 |
| 8 | T4 "D,E,G skipped: blocked_by_failed_dependency" | shows failure containment, the slide's title claim | keep | 0 |
| 8 | closing sentence "Each tick, per node: projection re-verified..." | restates the tick algorithm already shown visually | cut | 5 |
| 8 | color legend | needed to read the 4 tick panels | keep | 0 |
| 9 | trusted pipeline (request->compile->bind->frozen) | anchors what "trusted" covers | keep | 0 |
| 9 | untrusted box (papers/web/tool output) | defines what "untrusted" covers | keep | 0 |
| 9 | registry path (calls recorded) vs CLI-agent path (unobserved) | the whole trust argument in one contrast | keep | 0 |
| 9 | "untrusted text meets tools" annotation | names the actual risk in 4 words | keep | 0 |
| 9 | "'Compile' here is the 6 model calls...slide 4" | cheap continuity cue across slides | keep | 0 |
| 9 | THUS strip | states the risk plainly | keep | 0 |
| 10 | deterministic_command / llm_eval / code task / registry checks rows | shows the 4 gate kinds actually differ | keep | 0 |
| 10 | "results do not mark which" (registry row) | sets up the rubric-opacity theme | keep | 0 |
| 10 | THUS "a receipt is not evidence" | the one sentence worth remembering | keep | 0 |
| 11 | 5-schema chain diagram | shows claims as a pipeline, not a black box | keep | 0 |
| 11 | "No model anywhere in this chain" | the single most surprising fact on the slide | keep | 0 |
| 11 | 5-row decision table (not_supported .9 / insufficient .35 / supported .9 / partially_supported .85 / insufficient .3) | only the no-experiment/.85 row is used by the callout below; 4 other confidence numbers add no argument | tighten to 2 rows: experiment vs no-experiment | 12 |
| 11 | "0.85 is the best a claim with no experiment reaches" | the number the whole slide is built on | keep | 0 |
| 11 | THUS strip | states provenance-not-truth plainly | keep | 0 |
| 12 | native / adapter / trust-declared rows | shows the one trusted family vs the untrusted rest | keep | 0 |
| 12 | THUS "proposed: model writes runners...hash-and-approve" | the one forward-looking claim on this slide | keep | 0 |
| 13 | 14-node run / regression / journey tests / external scores rows | the entire evidentiary basis of the talk in one table | keep | 0 |
| 13 | THUS "not yet routinely without someone attending" | the honest one-line verdict | keep | 0 |
| 14 | 6-dimension bar chart | shows the actual shape of the gap (auditability high, control testing low) | keep | 0 |
| 14 | "totals do not separate agents...report per dimension" | the methodological point the whole benchmark choice rests on | keep | 0 |
| 15 | 5-system comparison table | the SoTA table, stays by rule | keep (protected) | 0 |
| 15 | THUS "checks the most and generates the least" | the report's second claim, restated | keep | 0 |
| 16 | "harness 27.4 points, model 29.4 points" | justifies why platform choice matters at all | keep | 0 |
| 16 | freeze/dispatch/gates/claims rows (dsh provides / AI4Research adds) | shows the runtime/contract split cleanly | keep | 0 |
| 16 | THUS strip | the platform decision in one line | keep | 0 |
| 17 | challenges #1-3 | challenges slides stay by rule | keep (protected) | 0 |
| 18 | challenges #4-6 | challenges slides stay by rule | keep (protected) | 0 |
| 19 | ahead rows (sealed rules / no unfound-quote verdict / NOT_TESTED != fail) | the closing thesis, restated concisely | keep | 0 |
| 19 | behind rows (1 experiment family / English-only / no benchmarks) | the honest counterweight | keep | 0 |
| 19 | THUS "the lead is a design property" | the single sentence the whole talk builds to | keep | 0 |
| 20 | 4 proposed-next bullets + Q-G3/Q-G4 table | the next-slide, stays by rule | keep (protected) | 0 |

### Per-slide: does the slide alone communicate, do notes add a little more?

Slides 1-3, 5, 9, 10, 12, 13, 16, 19, 20: slide alone is clear; notes add one worked example or a forward pointer, not more. Good match.

Slide 4: diagram alone communicates the shape but not the "who checks whom" story; notes narrate that in one pass. Good match, notes needed.

Slide 6: slide alone is clear; notes add "fit reviewer can be the same model" and 3 named substitutes, genuinely more (IF ASKED), fine.

Slide 7: slide alone communicates; notes add the CaMeL/PlanCompiler/Rel(AI)Build comparison and the "no plan-level search" cost, more than "a little" but appropriately gated behind IF ASKED.

Slide 8: dense even alone; notes add little beyond narrating the same 4 ticks. Slide is doing most of the work; notes are redundant with the visible captions rather than adding to them.

Slide 11: slide alone communicates the shape of the rule but not a worked case; the Reranker A/B example lives only in notes, so slide + notes together tell the story, slide alone would not. Borderline: acceptable since this is the SAY script, but the slide's own callout ("0.85 is the best...") already carries the point without the worked example.

Slide 14, 15: slide alone communicates; notes restate the same numbers rather than adding new ones (Kosmos/Arbor/AI-Scientist figures already on slide 15's table). Minor redundancy, not a cut since it's the protected SoTA slide.

Slides 17-18: slides alone communicate (evidence + fix columns are self-contained); notes add one example each (human-review baseline, log line numbers), a little more, good match.

## Part 2. REPORT.md sections 1-7 (tighten/cut only)

| Section | Element (quote) | So what | Verdict | Words saved |
|---|---|---|---|---|
| §1 | "A research run produces schema-validated evidence artifacts rather than free prose." | restates a point already made by Table 1 and the opening claims | cut | 12 |
| §2.3 | "A targeted search on 2026-09-13 found no reviewed system that seals..." | the date is process scaffolding, not a claim the reader needs | tighten to: "No reviewed system seals its own evaluation criteria inside the run's integrity hash." | 8 |
| §2.1 | "...against 20 of 50 for GPT-4.1 and 26 of 50 for Claude" | a third comparator adds no new argument once GPT-4.1 is given | tighten to drop the Claude figure | 7 |
| §4.1 | "prototype, hyperparameter tuning, research agenda, and ablations" | names 4 stages where the point is only that stages exist with stopping criteria | tighten to "with explicit stopping criteria per stage" | 8 |
| §4.4 | "sampled 5 times at temperature 0" | the sampling protocol detail does not change the "no evaluation published" argument | tighten to "sampled for stability" | 5 |

Everything else in §1-7 carries a distinct, load-bearing claim (a number, a failure mode, or a named comparator) that the "ahead on checking, behind on generating" argument depends on; none of it reads as filler for this audience.

## Totals

- Slides: 5 cuts/tightens found (of ~65 scored elements), about 33 seconds saved against 15:25 (roughly 3.5%). The deck has already been through several reduction passes (per HANDOFF.md), so most remaining bullets carry a distinct so-what.
- Report §1-7: 5 tighten/cut rows, about 40 words saved (of roughly 2,600 prose words).

## Top 5 cuts, surest first

1. Slide 11: collapse the 5-row claim-verdict decision table to 2 rows (experiment vs no-experiment); only the 0.85 row is used by the slide's own callout.
2. Slide 7: drop the 5-item "inside the hash" bullet list; the headline sentence already states the point.
3. §1: cut "A research run produces schema-validated evidence artifacts rather than free prose," restated already.
4. Slide 6: drop the orange UNSATISFIABLE_CAPSULE callout; the THUS strip below it says the same thing.
5. Slide 8: cut the fake truncated "contract_sha256: 9f3a..." line; it signals "there is a hash" and nothing else.
