---
name: deliverable-production
description: Run a whole report-and-talk project end to end - fix the audience and collapse scope first, derive the slide count from the time budget, keep Markdown and specs as the source of truth, build then render then check then review, and hand back a package with a state table, a changelog that records rejections, a presenter pack and unresolved doubts. Covers the production order, the read-aloud rule that catches structural problems early, cutting and timing discipline, running several agents on worktree lanes without collisions, and the mistakes that cost the most. Use when starting or planning a report, deck or documentation deliverable, when coordinating several agents on one, or when deciding what to hand back at the end.
---

# Producing a report and a talk

This is the project-level method: the order of work, who does what, and what to hand back. The building and
checking tools are in the deck-builder, diagram-maker, report-writing and deliverable-review skills; this skill
says when to reach for each and what to decide before any of them matter.

It comes from a project that produced 2 reports and 2 talks in 6 days. The deck went 17 planned slides, up to 38,
back down to 23. Both inflations came from internal polish; both contractions came from contact with reality.
Everything below is aimed at skipping that oscillation.

## Production order

```
 1  AUDIENCE        who is in the room, what they know, what they will attack
 2  SCOPE           collapse it: pick the target and write down what that deletes
 3  EVIDENCE        one note per source, read-only, each claim marked verified or claimed
 4  LEDGERS         one file for numbers, one for sources; nothing is quoted that is not in them
 5  OUTLINE         deck and report outlines side by side, checked against each other
 6  READ IT ALOUD   with a timer, from the outline
 7  REPORT.md       Markdown first; the .docx is a build artifact
 8  FIGURES         primitives and data first, then figures
 9  DECK SPEC       JSON, with TIME and SAY on every slide
10  BUILD           figures, then deck, then report
11  RENDER          every slide and page to PNG, plus contact sheets
12  LOOK            at every one, at report width
13  CHECK           style, numbering, coverage, cited numbers, timing
14  REVIEW          fresh-context reviewers, then propagate every fix
15  PACKAGE         state table, changelog, presenter pack, what is left for the owner
```

Steps 1-2 are the highest-leverage hours in the project. Committing to one target platform in the source project
answered 9 open questions and cut about a third of the report.

## Decide before building

- **Audience, written down.** Who is in the room, what each group already knows, what to define, and who will ask
  hard questions. Two audiences at once (an expert and newcomers) is normal: keep the main line accessible and
  push depth into optional slides and IF ASKED notes. Anticipated questions are a deliverable, not a nicety.
- **Scope collapse.** Pick the target, platform or framing early and record what it removes. An unmade scope
  decision is paid for in every later section.
- **Slide count from the time budget.** At roughly 45 seconds per slide, a 20-minute talk is about 25 slides.
  Write that number down before building, and treat it as a constraint rather than an outcome.
- **Settle slide density once.** Slides carry the talk; the notes rephrase them plus a little. Do not re-open
  this halfway through: reversing it rewrites every slide.
- **One rules file.** Keep the project's decisions in a single document and mark superseded rules instead of
  deleting them, so an old note never silently contradicts a newer decision.

## Read it aloud, early

The single most valuable check in the project was reading the talk aloud with a timer. It exposed that the
structure dragged after the main figure, and it exposed a 20% under-estimate of delivery time: 20:30 planned,
about 25:00 delivered.

Do it at step 6, from the outline, before slides exist. Then again before the first full review pass. Budget
about 25% over planned time until the estimates have been calibrated against real delivery.

## Sources of truth

- **Reports are Markdown. Decks are specs. Figures are code.** The `.docx` and `.pptx` are outputs.
- **Never hand-edit a built file and regenerate over it.** If the owner edited one, diff it, carry the edits into
  the source, then rebuild and diff again:

  ```
  tundlekit deck diff build/deck.pptx edited/deck.pptx --search deck-src
  tundlekit text docx-diff report.md edited/report.docx --search report-src
  ```

- **One place to change each thing.** Every chart number in one data file with its source beside it; every colour
  in one palette; shared rows behind a figure and its table in one constant. This is what keeps a number
  identical across a figure, a slide chart and a table cell through many reworks.
- **Fail loud.** A missing figure should abort the build; a stale anchor should refuse rather than silently
  slice the wrong text.
- **Back up before every write** to `versions/<name> (before <change> <date>).<ext>`, and keep source
  repositories read-only.

## Build, render, check

```
tundlekit deck lint deck-src/deck.json
tundlekit deck build deck-src/deck.json -o build/deck.pptx --times-file deck-times.json
tundlekit text lint report.md
tundlekit text fignums report.md --refs notes.md
tundlekit review coverage report.md build/deck.pptx --cuts cuts.txt
tundlekit claims trace report.md --papers papers --ledger LEDGER.md
tundlekit render office build/deck.pptx -o .review/deck
```

Two independent channels, and neither replaces the other:

- **Checks** catch wording, numbering, coverage, untraced numbers and timing.
- **Rendering** catches layout. Overflow estimators have blind spots, so a clean build is not evidence that the
  slide looks right. Look at every contact sheet, then every figure at full size.

Then run the reviews (review-prompts skill) and propagate each finding to every other instance of the same class.

## Time and cutting

- Give every slide a TIME; check the total, and the combined total when several talks share a slot.
- **Control time by hiding or deleting insertion slides, never by trimming core slides.** Mark optional slides
  `"insert": true` and build with `--inserts shown|hidden|off`.
- Cut in this order: extra papers, then comparisons, then challenge lists, then background depth. Never cut a
  main point, a rule slide or the design overview.
- Keep the spoken script inside the budget: words at most seconds × 2.3, aiming near 1.7.

## Several agents on one deliverable

Concurrent sessions in one directory overwrite each other. Use isolated lanes instead.

- Each helper works on its own branch in its own worktree, outside any synced folder.
- **Each lane declares what it owns and what it merely touches**, at sub-file granularity when needed ("this
  script, except the figure calls").
- **One commit per lane**, so the history shows who changed what and any lane can be reverted alone.
- **Lanes never run the builders.** The coordinator builds, renders, merges and resolves conflicts.
- **Read-only audit lanes** produce a proposal file with exact replacement text and locations; an owning lane
  applies it later.
- Cross-lane dependencies go in an explicit cross-references section; a lane that departs from another lane's
  proposed text records why.

Two failure modes to plan against. **Parallelism amplifies a single misreading**: one wrong fact applied by four
lanes costs four times as much to unwind, so verify a correction against the source before it fans out. And
**a lane usually cannot render**, so never ask one for a layout verdict it cannot reach: make rendering the
coordinator's job, run between merges.

## Handing back

A package the owner can read in about 10 minutes, not a pile of diffs.

| Document | Must contain |
|---|---|
| README | a state table (now vs was, per deliverable, counts and timings), check status, a numbered read order with a time estimate, decisions taken without asking, what is left for the owner, a copy-pasteable rebuild block, and a map from each instruction to where it landed |
| CHANGELOG | one entry per lane or pass: branch, files, what changed and why, **and what was rejected, with the reason**, so it is not raised again |
| Review | one reviewer, one deliverable, with its findings table and an applied/rejected section |
| Presenter pack | the spine in one paragraph; a slide table; hard questions with sources; numbers to have ready; things not to say; insertion slides with a cut order |
| Doubts | every unresolved question, each with an explicit **Settled by:** line naming the evidence or decision that would resolve it |

The presenter pack's slide table and its "things not to say" section are what the presenter actually uses:

| # | Title | TIME | Crib line |
|---|---|---|---|

"Things not to say" pairs each tempting overstatement with its correction: a proposed design is not a measured
one, a rate measured on 1 model is not a general rate, and a count from one inventory is not interchangeable
with another.

Frame everything left over as a choice, not a defect.

## Mistakes that cost the most

- Polishing instead of testing. Every real improvement came from a run-through, a render or an opened source.
- Oscillating on slide density and length. Settle it once.
- Correcting instances of an unreliable class of number instead of banning the class.
- Letting a wrong fact fan out through parallel lanes before it was checked against the source.
- Treating an estimator's silence as proof that a layout is fine.
- Leaving the reader-facing and fully-annotated variants of a report unseparated until the end. Decide at the
  start which one carries code locations and keep the other beside it.
- Editing a built Office file and regenerating over it.

## Checklist

- [ ] audience written down; scope collapsed and its deletions recorded
- [ ] slide count derived from the time budget before building
- [ ] outlines side by side; the talk read aloud with a timer at outline stage
- [ ] Markdown and specs are the only sources; Office files are outputs; backups before every write
- [ ] numbers in one data file with sources; colours in one palette
- [ ] built, rendered and looked at, at report width, before any review
- [ ] checks clean: style, numbering, coverage, cited numbers, timing
- [ ] reviews run in fresh contexts; every finding propagated to all instances
- [ ] lanes isolated, one commit each; rendering done by the coordinator
- [ ] package handed back: state table, changelog with rejections, presenter pack, doubts with Settled by lines
