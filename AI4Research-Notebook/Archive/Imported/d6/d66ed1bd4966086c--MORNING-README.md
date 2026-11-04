# Morning README, 2026-09-15

Read this first. About 10 minutes for the read order below, then open the 4 deliverables.

## State

| Deliverable | Now | Was |
|---|---|---|
| Capsule deck `AI4Research Capability Capsule Presentation - Muk.pptx` | 26 slides, 20:30 | 25 slides, 19:15 |
| Capsule report `AI4Research Capability Capsule Report - Muk.docx` | 35 pages, Tables 1-8 + A1-A7, B-G | 33 pages |
| Workflow deck `general/AI4Research General Presentation - Muk.pptx` | 20 slides, 15:25 | 20 slides, 15:20 |
| Workflow report `general/AI4Research General Report - Muk.docx` | 30 pages, 6 challenges | 31 pages, 11 challenges |
| Both talks | 35:55 against the 40:00 target | 34:35 |

All checks pass (`notes/report-general/build/checks/run_all.py`: no em dashes, no we/our on slide faces,
figure numbers consistent, every SAY within TIME x 2.3, reading-page markers intact). Word and PowerPoint
were closed all night; the built files were never opened in Office. Backups of everything before tonight:
`versions/* (before overnight 2026-09-15)`. Git: one commit per sprint, tags `sprint-0-baseline`,
`sprint-1-end`, `sprint-2-end`, `sprint-4-end`, `overnight-final`; roll back any file with
`git checkout <tag> -- <path>` and rebuild.

## Read order

1. `Q1-alita-g-vs-96-percent.md`: why Alita-G gains 8 points while 96.8% of kept tools score 0.
   Short answer: different tools. The 96.8% is 215 of 222 tools from 3 other protocols, on Haiku 4.5,
   replayed on hidden inputs. Alita-G's tools were never replayed; its 83.03% is an end-task score on the
   same 165 GAIA questions its tools were harvested from, where a fitted tool passes. The link between the
   papers is the shared curation rule (task passed, keep the tool), not a measurement on Alita-G.
2. `Q2-how-hashes-work.md`: 7 hashes traced to file:line (the freeze's `contract_sha256`, 12 artifact
   refs, the per-node execution authority that covers each bound capsule's whole manifest, the check-registry
   seal, DSH archive and i18n sidecar hashes, and the proposed capsule content hash), what each protects
   against, what a hash does not do, and 4 IF ASKED answers.
3. `PRESENTER-PACK-capsule.md` then `PRESENTER-PACK-workflow.md`: spine, 1 crib line per slide, 10 hard
   questions each with answers and sources, numbers to have ready, things not to say.
4. `Q3-sota-verification.md`: 25 SoTA claims checked, 15 verified, 7 corrected, 3 cut.
5. `TRANSLATION-DRIFT.md`: the zh/en round-trip experiment.
6. `CHANGELOG.md`: every change by sprint, with what was rejected and why.
7. `review/R-*.md` (4 human-style reviews with applied/rejected sections) and `review/SOWHAT-*.md`
   (cut candidates with seconds and words saved; not applied, see below).

## The capsule ending, in short (report §5-§6, slides 24-26)

- §5.1 Table 7: 11 assumptions, each with why it is uncertain, the test, what says it holds, what says it
  fails, and which work step reads it. Rows 1-3 are the 3 results that would disprove the design, row 4 the
  control group, rows 5-7 the "to try" choices, rows 8-11 the parameters (recurrence threshold, gate tries,
  breaking-change rule, generalist cap).
- §5.2 Table 8: the verdict after k = 10 sprints, from 5 signals (gap recurrence, admission rate and
  rejection mix, reuse vs build cost, held-out conformance vs the human control, generality retention), each
  pointing to continue, narrow to selection only, or stop building.
- §6: 8 work steps unchanged; the 17 questions in 3 groups (decide before building, with proposed starts
  of 2 sprints and 5 gate tries; test before trusting; for the supervisor) and a closing paragraph. The first
  result that would change the recommendation is the gap census of step 2.
- Proposed starting values are marked as questions. 2 sprints follows AllocBench's best policy (wait for
  the first confirmed repeat); 5 is CoEvoSkills' cap on evolution iterations; k = 10 is 5 times the threshold.

## Decisions I took without asking

- Rendering uses your own PowerPoint and Word through COM in a hidden instance (LibreOffice is not
  installed); it needed `pip install pywin32`. It refuses to run if you have Office open.
- The git dir lives outside OneDrive at `C:\Users\mukch\projects\report-writing-set.git`. Built .docx and
  .pptx files are ignored except in the final commit.
- Alita-G reconciliation went into Appendix A.2 as Table A2 plus 1 flat sentence in §2.3, not a body table
  in §2.3 (that would have renumbered Tables 2-6 and 4 deck footers).
- Challenge merge target was 6. Group D (capsule pointer) untouched.
- The translation-drift result is not in either report: 2 fixtures, 1 night, no published source. If you
  want it in workflow challenge 2, the sentence is: "In a 4-hop Chinese to English round trip over 230
  README lines, 16 meaning drifts appeared, 2 of them modal, and none reverted (`TRANSLATION-DRIFT.md`)."
- The so-what cut lists were NOT applied. They are conservative-safe to apply, but every cut is your call.

## Left for you

- Figure-internal text that is too small: capsule slide 19 "FIXED AT THE FREEZE" card; workflow slide 9
  Compile box (a slide-face line now explains it). Both are drawn in `figures.py`.
- Workflow deck slide 6 could fold into slide 4 (0:55 saved); the exact edit is in `review/R-general-deck.md`.
- The SoTA reader artifact (`general/sota-reader.html`) is rebuilt on disk but its republish was blocked by
  the permission prompt; the challenge register did republish (version 8). To republish: ask for it, or
  publish the file to `https://claude.ai/artifact/JTwSNeJWJLcyg6y25AX3Yo`.
- One dating doubt in the workflow report: the ledger dates the 14-node run 2026-09-02, the report 09-03.
- Open design questions stay as listed in capsule §6 (recurrence threshold, gate tries, breaking change,
  generalist cap, interactive vs autonomous, network policy).

## How to rebuild

```
cd notes\report-general\build
python build_deck.py "..\..\..\general\AI4Research General Presentation - Muk.pptx"
python build_report.py ..\REPORT.md "..\..\..\general\AI4Research General Report - Muk.docx"
cd ..\..\report-capsules\deck-src
python build_deck.py "..\..\..\AI4Research Capability Capsule Presentation - Muk.pptx"
python build_report.py ..\REPORT.md "..\..\..\AI4Research Capability Capsule Report - Muk.docx"
cd ..\..\report-general\build
python build_reading.py
python render.py all
python checks\run_all.py
```
