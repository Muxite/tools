---
id: activity-20261021-paper2agent-talk
status: completed-documentation
source: Sources/Prompts/2026-10-21-paper2agent-presentation-request.txt
last_reviewed: 2026-10-21
next_action: Rehearse aloud, verify benchmark numbers and leak points against the paper, then present
---
# Paper2Agent talk built

Built an eight-slide deck (planned 9:20) with workflow, leakage and fit diagrams, from a tundlekit spec. Lint clean; every slide rendered through PowerPoint and inspected. See [[Designs/Paper2Agent Briefing/presentation/README]] for the claim ledger. Not rehearsed. Benchmark numbers come from earlier evidence notes and were not re-checked against the Nature paper.

## Revision 2

After two pasted outside reviews, renamed "leak points" to "coupling points", relabelled the verifier as one that may repair (repo: up to six attempts), added a coverage row and a bundled-baseline row, and named the Nature version on slide 2. Checked the repo for the verifier, tutorial-derived test and withheld-oracle claims; the "failing tools are dropped" claim was not found there. Rebuilt, lint clean, all slides rendered and inspected.

## Revision 3

Muk asked that the answer to "does this have value to AI4Research" come first. Slide 1 now states it, and a new slide 2 gives the decision: value, why not adopt now, what we ask. Later slides are trimmed to keep the planned time at 9:05 across nine slides. Lint clean; every slide rendered and checked.

## Revision 4

Applied a pasted outside review: the talk now explains the problem, the six-stage method with a before-and-after example, reported results with scope, value to AI4Research, and a two-level capsule fit (factory vs generated tools). The coupling diagram is one limits slide with three points and a "what a pass shows" entry. Pilot controls, detailed results, M1 gaps, the pilot protocol and the admission gate are hidden backup slides. Nine main slides, planned 9:10. Lint clean, all fourteen slides rendered and inspected. Not rehearsed.

## Revision 5

Applied a second outside review: new worked-example slide, softened claims (compatible and authorized agent, scattered evidence, fidelity on tested cases, documented-intent wording), acquisition made a separate capsule, "one operation or a coherent set", shorter limits script, a corrected backup control pairing, and time trimmed to keep nine minutes fifteen across ten main slides. Lint clean; all fifteen slides rendered; the worked example and capsule figures inspected.

## Revision 6

Muk asked for a much shorter talk, about ten slides. Cut to eight shown slides plus two hidden backups (ten in the file), planned at 5:40. Dropped the before-and-after slide, the separate capsule-fit slide and two backup tables; their points moved into the worked-example slide, its notes and the pilot backup. Lint clean; all ten slides rendered.

## Revision 7

Visual redesign after a pasted design review. New builder `build_pptx.py` (native shapes) replaces the tundlekit route for the shown deck; eight shown slides and two hidden backups. Output is `Paper2Agent Talk rev7.pptx` because PowerPoint had the earlier file open; the revision 6 file is kept as `Paper2Agent Decision Talk (rev6).pptx`. All ten slides were rendered through the running PowerPoint (read-only, window closed afterwards) and inspected; overlaps found in the first render were fixed. tundlekit lint does not apply to this builder.

## Revision 8

Muk said the talk must start with the value of Paper2Agent to AI4Research, then that it should cover the value of the idea and the methodology without a deep dive. The value slide moved to slide 2 as two panels (the idea, the methodology), and the title slide leads with the value. Output is `Paper2Agent Talk rev8.pptx`. Rendered and inspected.
