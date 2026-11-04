# Overnight change log, 2026-09-15

One entry per sprint. Each entry lists the commit, the files touched, and what changed and why.
Rejected review findings are logged with the reason so they are not re-raised.

## Sprint 0: setup and baseline

- Git repo initialised with the git dir outside OneDrive (`C:\Users\mukch\projects\report-writing-set.git`);
  a 60-byte `.git` pointer sits in `report-writing-set/`. Tag `sprint-0-baseline`.
- Backups: `versions/* (before overnight 2026-09-15)` for the 4 deliverables and the 4 source files.
- New tooling: `notes/report-general/build/render.py` (slides and pages to PNG plus contact sheets, via
  our own hidden PowerPoint/Word instance; refuses to run if the user has Office open) and
  `build/checks/*.py` (forbidden strings, figure numbers, section word counts, SAY-vs-TIME, reading-page
  markers). One install: `pywin32`.
- `notes/40-style-card.md` extended with a third, larger sample of the user's own prose (rev0 draft).
- Known benign check finding: `check_markers` flags "There are two limitations" twice in the general
  report (§2.1 line 119 and §2.2 line 145). The slicer searches for the end marker after the start
  marker, so the first hit is the right one. Pre-existing, not changed.

## Sprint 1: capsule report and deck, the three questions (commit `sprint-1`)

- **Alita-G vs 96.8%** (`Q1-alita-g-vs-96-percent.md`): the 2 numbers come from different tools and
  systems. §2.3 now states flat that the 96.8% was measured on tools from 3 other protocols and that
  Alita-G's own tools were never replayed; App. A.2 gains Table A2 (paper, tools measured, benchmark,
  model, scored on) and the later App. A tables are renumbered A3-A7 (body tables untouched). Deck
  slide 9 gains a slide-face line under the chart ("Alita-G was scored on the questions its tools came
  from; its tools were never tested on new inputs") and the SAY note says it first. Body-table option
  (a Table 2 in §2.3 with renumbering of Tables 2-6 and 4 deck footers) was rejected as churn.
- **Hashes** (`Q2-how-hashes-work.md`, 7 hashes traced to file:line): Table C1 identity row now has a
  check (`HASH_MISMATCH`), Table C2 gains that reason, App. D gains 3 bullets on DSH archive and
  sidecar hashes, §4.5 gains 2 sentences on how the pin plus content hash makes "used from the next
  sprint" checkable. General report §2.3 freeze-hash sentence corrected from the code trace.
- **The ending**: §5 heading now "3 tracks, a stated prediction and 11 assumptions that must hold";
  new §5.1 Table 7 (assumption, why uncertain, test, says it holds, says it fails, when) with 11 rows;
  new §5.2 Table 8 (5 signals x continue / narrow to selection / stop building, first verdict after
  k = 10 sprints, proposed); §6 questions folded from 17 in 5 groups to 17 in 3 groups (decide before
  building with proposed starts, test before trusting, for the supervisor), closing paragraph added.
  Proposed starting values (2 sprints, 5 tries, k = 10) are marked as questions; the CoEvoSkills "5"
  was reworded from "bound on its oracle" to "the number of rounds within which CoEvoSkills reports
  convergence" after checking the paper text (line 671). §5 + §6 grew from ~960 to ~1,880 words,
  most of it Table 7; candidate trim if wanted: merge the 4 parameter rows.
- Deck: slide 24 rebuilt (tracks, 3 disproofs, prediction strip), new slide 25 "What to verify first"
  (7 rows, 0:55), slide 26 next/deciding in 3 groups (0:50). 25 -> 26 slides, 19:15 -> 20:15; both
  talks 35:35. Titles of slides 7 and 24 lost "our"/"we" ("why a live run is harder", "How to know it
  works"). `PRESENTER-PACK-capsule.md` drafted (spine, crib line per slide, 10 hard Q&A, numbers).

## Sprint 5: so-what pass, package, final build (commit `overnight-final`)

- So-what reviews (`review/SOWHAT-capsule.md`, `SOWHAT-general.md`, Sonnet): capsule talk 19 s and
  115 words of candidates; workflow talk 33 s and 40 words. Not applied: every candidate is the user's
  call, and one (the "Akin to how people learn" analogy) was kept by the user on 2026-09-14.
- Presenter packs: `PRESENTER-PACK-capsule.md`, `PRESENTER-PACK-workflow.md`.
- Reading pages: `challenge-register.html` republished (version 8); `sota-reader.html` rebuilt on disk,
  republish blocked by the permission prompt (left for the user).
- `HANDOFF-SHORT.md` and `report-capsules/DECK-PLAN.md` gained a 2026-09-15 header; the stale
  "27 slides, 19:20" line is marked superseded.
- Workflow deck slide 13 (caught by the presenter-pack agent): title "1 clean run" and the row "all
  required gates passed" mirrored the old report wording, which the ledger attributes to the 15/15 run.
  Now "1 run end to end" and "14 nodes executed, 8 files delivered; its own evidence gate not passed, so it
  closed degraded", SAY aligned; 3 "clean run" phrases in notes reworded; slide 15 IF ASKED no longer says
  Arbor's held-out score is selected over many test calls (cut tonight as an inference the paper contradicts).
- Timing tweaks: capsule slide 9 1:05 -> 1:10, "The evidence" divider 0:05 -> 0:10, slide 2 0:40 -> 0:45;
  workflow title slide 0:15 -> 0:20. Both talks 35:55.

## Sprint 3: translation-drift experiment (`notes/overnight/TRANSLATION-DRIFT.md`)

- 4 fresh Sonnet translators, each seeing only the previous hop: zh0 -> en1 -> zh2 -> en3 -> zh4, on
  fixture A (AI4Research README lines 179-311, architecture and execution chain, 132 lines) and fixture B
  (deepseek-harness README.zh.md, 97 lines, with its official English pair as an external reference).
  `tcheck.py` ran on every hop (no identifier damage). A fresh Sonnet critic aligned the hops.
- Result: 16 meaning drifts (terminology 9, modal 2, omission 2, quantifier 1, invented actor 1,
  embellishment 1); entered at hop 1: 1, hop 2: 7, hop 3: 5, hop 4: 3. Drift accumulated (8 rows by zh2,
  16 by zh4) and no row reverted. Clearest modal case: "不允许无限自循环" (not allowed) became "不得"
  (must not) at hop 4 only. "安全" drifted safety -> security in both fixtures at the same point; the
  official English pair does not show it, so it is a chain artefact.
- Not put into the reports: it is a 2-fixture, 1-night, 1-model-family experiment with no published
  source. The optional sentence for workflow challenge 2 is in MORNING-README.

## Sprint 4: human-style reviews and fixes (commit `sprint-4`)

Four Opus reviewers each read one deliverable once, start to finish, from the rendered PNGs and the
source (`notes/overnight/review/R-*.md`, each with an "Applied / rejected" section at the end).

- **Capsule deck**: AI4Research defined on slide 2; rule slides 8 and 15 gained source footers;
  slide 9's slide-face line now says the 222 tools are not Alita-G's; slide 24 carries the control group
  on its face; slide 25 table raised to 14 pt; slide 4 title spells out DeepSeek Harness; SAY on slide 18
  names the 6 rules by badge. 20:15 -> 20:30. Left for the morning (drawn inside figure PNGs): the
  small "FIXED AT THE FREEZE" card on slide 19; proposed cuts with seconds are listed in the review.
- **Capsule report**: §2.3 "31% to 34%" kept (the paper's re-execution figure, `2604.00392.txt:288`)
  with locator; the reviewer's proposed 28.7% to 35.8% was the earlier run and would have been wrong.
  "Typed selection is already settled" reworded (step 4 still unifies 2 vocabularies). CoEvoSkills "5"
  is "the cap on evolution iterations" (paper line 943). k defined before Table 7. 43-checks locator.
  App. D hash bullets cut to 1 sentence. Rows can no longer split across pages (builder change
  `build_report.py`: `cantSplit` on every row; headers already repeat).
- **General deck**: AI4Research row added to the SoTA table (slide 15), "71.70 for Claude Code";
  slide 14 title says "Published agents score 11% to 16%"; slide 11 glosses the confidence numbers;
  slide 9 says Compile is the 6 model calls of slide 4; "dsh" -> "DeepSeek Harness"; slide 20 marked
  Proposed; slide 2 footer; glosses for manifest and NOT_TESTED. Left for the morning: the exact plan
  to cut slide 6 (0:55) into slide 4 is written in the review.
- **General report**: the run contradiction resolved. Table 5 had "closed with all required gates
  passed", which the ledger records for Run B (2026-09-03, 15/15), not the 14-node run. Both Table 5
  and Table 6 now say the 14-node run executed 14 nodes, delivered 8 files, did not pass its own
  evidence gate and closed degraded. §3 heading: "1 internal run executed end to end". CaMeL, CREDENCE,
  Rel(AI)Build and DeepFact identified with arXiv ids at first use; the companion capsule report named
  and added to App. A; 0.85 defined in §6.1; "80 entries vs 79 manifests" reconciled; §2.3 freeze-hash
  run-on split; App. E.4 names both abort codes; §6.2 gives challenge 4 a direction and tags the DSH
  bullets as challenge 5. Open doubt: the ledger dates the 14-node run 2026-09-02, the report 09-03.

## Sprint 2: workflow report and SoTA sourcing (commit `sprint-2`)

- `notes/report-general/REPORT.md` §6: 11 challenges merged to 6 (old 1, 2, 4 -> 1; 3, 5 -> 2; 6, 8 -> 3;
  7, 9 -> 4; 10 -> 5; 11 -> 6), each with evidence, a Section pointer and "what would fix it". §6 went
  from 1,421 to 1,296 words. §6.2 and App. C references renumbered. Group D (capsule pointer) untouched.
  Dropped from §6.1 with reason: the 57% train/test overlap and 11% to 16% control-testing figures are
  already in §4.1 and Table A1; the literal cue list and Chinese punctuation detail remain in App. C.
- `build/build_deck.py` slides 17-18: 2 tables of 3 challenges (#, challenge, evidence with file:line,
  fix). TIME unchanged (0:45 + 0:45).
- `REPORT.md` §4 (SoTA): 25 claims checked against opened sources: 15 verified, 7 corrected, 3 cut.
  All 7 openJiuwen bullets now carry `file:line` at `agent-core@6ecf8218` (App. C gains 7 rows).
  Most important correction: Table 6 said "1 clean 14-node run"; the ledger records that Run A's own
  evidence gate did not pass, so the row now reads "14 nodes executed and 8 files delivered, with the
  run's own evidence gate not passed; no external score". Cut as inferences the papers do not make:
  AI Scientist-v2 "model reviewer as the final check", Arbor "no model decides the merge" (p. 30 shows
  a model extracts the metric) and Arbor "held-out score selected over many test calls" (p. 33 says
  evaluated once). openJiuwen budgets 50/4/6/4 are shipped config values; code defaults are 30/4/5/3.
  Full table: `notes/overnight/Q3-sota-verification.md`. `SOTA-SYSTEMS.md` gained an Arbor section.
- `REPORT.md` §2.3: freeze-hash sentence made precise (operator twin, early return when no node
  carries an execution authority), from the code trace in `Q2-how-hashes-work.md`.
- Reading pages rebuilt: `general/sota-reader.html`, `general/challenge-register.html` (11 challenges:
  6 workflow + 5 capsule). Not republished as artifacts yet.
