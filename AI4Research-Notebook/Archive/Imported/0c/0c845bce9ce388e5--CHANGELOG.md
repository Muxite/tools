# Day pass change log, 2026-09-15

One entry per lane. Each names the commit or branch, the files touched, what changed and why, and what was
rejected. Read `README.md` in this folder first.

## Lane 0: the run that was misdescribed (commit `50a9225`)

- The overnight pass attached the 2026-09-02 run's evidence-gate failure (Run A, log l.638) to the 14-node run the
  workflow report describes. The report's run is the 2026-09-03 sprint at log l.793-796 (Run C): the "only these 5"
  fidelity catch, 1 bounded intent repair, 14 of 14 nodes at attempt 1, ledger revision 106, closure `closed` with
  `all_required_gates_passed=true`, 8 files delivered. Tables 5 and 6, deck slide 13 (row and SAY), the presenter
  pack (hard question 8 and the "things not to say" list) and the ledger (new Run C column, with the mistake recorded
  so it is not repeated) now say so. No run count is quoted anywhere (ledger rule).
- The "dating doubt" in MORNING-README is closed: the report's date was right; the borrowed failure was wrong.

## Lane F: figures scaled until they read (commits `2454411`, `figures:` series)

- `figures.py` RATIO raised per drawing (1.4 to 1.6) so the smallest text is about 6.5 pt at report width and 9 pt
  on a slide; boxes widened and labels shortened wherever the larger text would overflow (workflow, freeze, binding,
  claim, trust, versions, stack, sprint-roles, admission, loops, mcp, goal-rules).
- The DAG figure (general Fig. 4, capsule Fig. 9; slides 8 and 19) was laid out again: card 33 units wide, 4 panels
  31.5 x 21, the node key on its own row under the panels, the tick note dropped (its content is in §2.4 prose and
  App. F). Aspect 0.62 to 0.545, so the slide image is 19% wider and the card text about 45% larger.
- The trust figure's Compile box says "Compile: 6 model calls" with "intent, requirement, plan; code checks each";
  the slide-face line that used to explain it is gone and the figure box grew to 4.7 in.
- `figures.py fig <name,name>` renders a subset (the whole set takes about a minute).
- Checked from renders: every figure slide and every figure page (general p2, p5, p6; capsule p13, p14, p16, p19).

## Lane W4: state of the art (branch `w4-sota`, merged `6b421ec`)

- See `review/W4-sota.md`. Every rung label in §4 is now the survey's own (the home-made "exec" label is gone);
  AI Scientist-v2's scores corrected to 6, 6 and 7 (paper p9); Kosmos's by-type figures now use the paper's own
  words (reproducible, validated, accurate); Arbor's gate is "a held-out merge gate the merge tool alone can open",
  not "no model" (p30 shows a model extracts the metric); 4 systems a supervisor would name are named and excluded
  with a sourced reason (Co-Scientist, Robin, Agent Laboratory, "Towards End-to-End Automation of AI Research").
- Talk: slide 14 0:40 to 0:30, slide 15 1:00 to 0:40; the SAY names only Arbor and AI Scientist-v2. Net 30 s saved.
- Rejected: W4's cross-reference to change "GPT-4o" to "GPT-4" in App. E.7. The OpenScholar abstract (p1) says GPT-4o;
  only the introduction says GPT-4. The report cites p1, so it stays.

## Lane W2: the papers in the capsule report (branch `w2-papers`, merged `2bc0371`)

- See `review/W2-papers.md`. Every number in §2, Tables 1-2 and App. A.1-A.5 matches its paper. Setups fixed: the
  96.8% is over 3 seeds x 8 sessions per protocol on EvolveTool-Bench (99 tasks is the whole benchmark, not the
  denominator); 165 GAIA questions is derived (13 flips = 7.88 points), now shown in App. A.1.
- Results now drive the design in the text: Alita-G's harvest 3 to 4 (28 tools, 8 clusters, accuracy flat) -> the
  build budget; CoEvoSkills' 5-round oracle -> the gate-try cap of 5; DGM's never-pruned archive -> append-only
  versioning; AllocBench's first confirmed repeat -> the 2-sprint threshold.
- Deck: the "(now precise)" tag on R3 is gone; strips state model, benchmark and n; 3 strips shortened to fit.

## Lane W3: the challenges (branch `w3-challenges`, merged `73d4aeb`)

- See `review/W3-challenges.md`. All 6 challenges verified at `b0bf165f9`; 4 rows corrected where the evidence was
  thinner than the sentence (the frozen-evaluator "no defined behavior" claim: the code records a policy pass; #5
  leads with the CLI-agent path, not an April incident; #6's failure was retryable and met a 1-attempt policy; the
  0.85 verdict is at `delivery.py:155`). Each challenge's strongest objection is answered under its table and in
  App. B. Talk: slides 17-18 carry 4 rows (1, 2, 3+4, 5+6); the report keeps 6. §7 Table 13 gains the decision each
  question asks for and Q-G5 (owners).
- Applied from its cross-references: §2.3 fourth limitation and §2.6 now state the 1-evaluator-node budget; App. C
  gained 11 rows.

## Lane W5: question coverage (`proposals/W5-coverage.md`)

- 25 ranked questions per talk with where each is answered today, 10 zero-cost or 10-second story placements, the
  questions to keep as IF ASKED, and 9 reactionary phrasings with story-form replacements. Applied by the round-2
  deck lanes (below).

## Lane W1: the capsule plan and spatiotemporal composability (branch `w1-capsule-plan`, merged `4473bec`)

- See `review/W1-capsule-plan.md`. Both halves of Cordis's composability are defined in plain words in section 1.2
  and Appendix D, then used: the space half in section 4.1 (5 generalist nodes in 1 sprint do not interfere; write-scope
  code cited) and section 4.2 (2 sprints over 1 library); the time half in section 4.5 (a new version loads beside the old,
  the old is withdrawn by running its inverses, no restart) and G.6/G.7 (retirement is disposal of effects plus a
  tombstone). Cordis's own warning that a faulty self-modification can disable the process needed to recover is
  the independent argument for R5 in section 4.3. Table 7 gains rows 12 and 13 (a test per half on DSH) and section 6 a
  step 9 that runs them. Deck: slides 2, 4, 20, 23, 26; capsule deck 20:30 to 21:05.
- Plan grounded in the code: the gap census (step 2) reads the capsule-candidate catalog planning already writes
  for every plan, so it needs no generalist and can be taken from past runs; the declared-versus-observed effects
  check (step 7) starts from the write-guard record the sandbox already produces; versioning (step 1) is smaller
  because the registry already stores a version per entry and rejects duplicate (kind, id, version); the selection
  change (step 3) is 1 pure function. App. B corrected: 85 manifests exist, 79 is the count without the 3 artifact
  adapters, and every registry entry resolves to a manifest.
- Open for the user (W1 doubts): headline 79 or 85; 13 or 18 exclusion reasons in the talk; whether step 9 should be
  numbered earlier; Cordis locators as sections or pages.

## Round 2: first-time-reader passes (branches `r2-*`, merged)

- **Workflow report** (`review/R2-general-report.md`): draft-relative wording removed (past-tense substrate story,
  "still true?", "the easy half and not the hard half"); the hash sentence added to §2.3 (detects after the fact,
  prevents nothing, authenticates no one); §6.1 #1's settle signal corrected to the 78% to 81% evidence-auditability
  band (58.4 to 60.3 is the paper's total); §6.1 cells trimmed to 113-123 words with no row split; arXiv ids at first
  use; Fig. 7 and 8 now referenced; App. B gains the cost and model-identity gaps as stated gaps. GPT-4o kept in E.7.
- **Workflow deck** (`review/R2-general-deck.md`): titles are sentences ("A result does not say whether code or a
  model decided"); every W5 zero-cost placement applied plus the 2 SAY additions (hash, re-planning); the slide 4
  self-retracting IF ASKED, the slide 12 empty-cell row and "Proposed." label removed; slide 13 THUS no longer
  concedes; 0 layout warnings. 14:55 to 15:15. Slide 9 and 14 titles adjusted after the pass.
- **Capsule report** (`review/R2-capsule-report.md`): SkillWeaver glossed, "sandbox hand" dropped, Table 7 rows
  referenced by name (the table has no row-number column), the cross-paper model sentence added to §2.7 (3 results,
  3 models, the pattern carries, the 79 hand-written capsules are the control), §6 states that steps 1 to 7 change
  running code, step 8 is the only new subsystem and step 9 the only step needing a running DSH.
- **Capsule deck**: see `review/R2-capsule-deck.md`.
- Reading pages rebuilt and republished: SoTA reader version 9, challenge register version 9.

## Lane I: insertion slides, logo, author (commits after `day-pass-2026-09-15`)

- `deckkit.py`: `slide(..., insert=True)`, sub-numbering, INSERT note, separate timing, `DECK_INSERTS`; dividers and
  the title slide reset the insert state (a helper found the trap). `check_timing.py` reads core and insertion time
  separately; guide §7a states the rules.
- Workflow deck: 6 insertion slides (Table E4, Kosmos, openJiuwen, 4 systems left out, objections, what settles each).
  Capsule deck: 8 (Alita-G vs 96.8%, Table A7, Fig. G1, generalist flags, Table G1, Table 8, Table D1 in 2). Table G2
  was left out to stay under 5:30; say so and it goes in as 23b.
- Logo: `assets/huawei-logo.svg` (Huawei standard logo) embedded as SVG with a PNG blip; `Deck.logo()`.
- Author line on both reports; docx core properties author and title; bylines "Muk Chunpongtong · September 2026".
- Capsule report §2.5, §2.6, §4.5: DGM's staged evaluation and reward hacking wired into the design text.
