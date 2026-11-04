# Presenter pack: Capability Capsule talk

Against `report-capsules/deck-src/build_deck.py` (26 slides, 20:15) and `report-capsules/REPORT.md` §5-§6.

## 1. The talk in 12 lines

1. Goal: agents that build, check and keep their own capabilities on DeepSeek Harness
2. Alita-G already does this loop; the question is what changes for runs of days and weeks
3. Alita-G: 75.15% to 83.03% on GAIA, but builds once, keeps every tool from a correct run, never tests or deduplicates. R1-R4
4. Beyond Task Completion: 96.8% of kept tools score zero on held-out tests of their own job
5. CoEvoSkills: hidden pass/fail alone 41.1%, a separate verifier's feedback 71.1%
6. Darwin Gödel Machine: judged by its own score, 1 version deleted what the detector reads. R3, R5
7. AllocBench: builders commit on first sight once code is involved, 4% to 92%. R6
8. Today: 79 hand-written capsules, 5 gaps
9. Design: generalist fills gaps and leaves a record; builds follow recurrence; 3 sessions plus a code gate; tests hidden from the builder
10. Selection: exact checks eliminate, embeddings only rank; library append-only and versioned
11. Evaluation: Tracks A, B, C; prediction: gate on, task scores flat, far fewer broken capsules
12. Verify first: gap census, effects check, control suites; then 8 steps and 3 question groups

## 2. One crib line per slide

- slide 1: a self-improving tool ecosystem on DeepSeek Harness
- slide 2: the goal, that it exists, what changes for long runs
- slide 3: MCP is a protocol; a tool is 1 of 3 server primitives
- slide 4: DSH has no core; a capsule wraps any plugin
- slide 5: each result, then its rule
- slide 6: Alita-G writes tools while solving tasks, 8 points on GAIA
- slide 7: keeps every tool from a correct run, never tests or deduplicates, freezes
- slide 8: R1-R4: 2 clocks, pinned versions, validate, no duplicates
- slide 9: 215 of 222 kept tools score zero while the task passed
- slide 10: pass/fail alone 41%, a separate verifier's feedback 71%
- slide 11: DGM edits its own code, driven by its score
- slide 12: 1 version scored 2.00 by deleting what the detector reads
- slide 13: R3, R5: held-out tests written first by a separate agent; code decides
- slide 14: 4% to 92% first-sight builds once code is involved
- slide 15: R6: a separate agent decides; build only on repeats
- slide 16: 79 capsules declare contracts; the code assumes a fixed library
- slide 17: proposed, nothing built or measured
- slide 18: walk the figure, gap record to new version next sprint
- slide 19: generalist runs unfilled steps, same gates, lowest trust, never writes the library
- slide 20: 5 parallel steps count once; 3 sessions see only what they need
- slide 21: each manifest field is a promise with a check; declared vs real effects is new
- slide 22: exact checks first, similarity only ranks
- slide 23: append-only and versioned; a running sprint keeps its version
- slide 24: 3 tracks, the prediction, 3 results that prove me wrong
- slide 25: what to verify first; the gap census can change the plan
- slide 26: versions first, cold path last; decide, test, ask

## 3. Hard questions and answers

1. **Why not just use Alita-G?** It builds once for a fixed benchmark, keeps every tool from a correct run, never tests after the rewrite and never deduplicates (distinct share 100% to 51% at 128 tools). Research runs never stop, and steps often have no right answer. Alita-G [2, Eq. (5), Tables 3-4]; report §2.2.
2. **Why 2 clocks?** No fixed task set, so building happens while sprints run and no sprint waits. Today a capsule change during planning aborts the freeze, so sprints pin versions and use a new capsule next sprint. Report §3, §4 R1-R2, App. G.1-G.2.
3. **Why does the implementer never see the tests?** Tools fitted to their task pass it and score zero on held-out tests, 215 of 222. An uncapped gate lets the builder learn the suite, so it hears admit or reject with a reason, a capped number of times, as CoEvoSkills bounds its oracle. [3, Table 5]; [4]; report §4.3.
4. **What if gaps never recur?** Building stops, a valid result: AllocBench's best policy waits for a repeat. The generalist and gap record stay, since they turn a plan that fails today with `UNSATISFIABLE_CAPSULE` into a completed one. Report Table 8, §6 closing; [6].
5. **How is this different from DGM?** DGM rewrites its own code for a benchmark score, and 1 version gamed it by deleting what the detector reads. Here weights and checker never change, only the append-only library, and protection is by write access, not hiding. [5, App. H, Sec. 5]; report §2.6, §4.3.
6. **What does the gate cost?** Per admission 3 model sessions, a verifier session, the effect check and audit re-runs for life, plus the generalist on every unfilled step until then. Unmeasured; whether reuse repays it is Table 7 row 3. Report §5.1.
7. **What is the first thing you would build?** `capsule_id@version` in the registry, planning snapshot and execution authority, because a change during planning aborts the freeze today. Then the generalist behind a flag. Report §6 steps 1-2, §4.5.
8. **How do you know it is working?** After about 10 sprints, 5 signals read together: gap recurrence, admission rate and rejection reasons, reuse against build cost, held-out conformance against the hand-written control, generality retention. Report §5.2 Table 8.
9. **What could kill it?** Gaps seen once (step 2), effects that never differ from declared (step 7), hand-written capsules failing their own suites, which means the tests are wrong (step 6), reuse that never repays (step 8). Report Table 7 rows 1-4.
10. **Why the manifest before the code?** The suite needs a contract before an implementation exists, and Beyond Task Completion wrote its suites before any tool. No paper compares the orders; Alita-G documents after. A design choice. Report §4.3; [2, Eq. (6)]; [3].

## 4. Numbers to have ready

| Number | What it is | Source |
|---|---|---|
| 75.15% to 83.03% | Alita-G GAIA pass@1 without and with its library, 165 questions | [2, Table 1] |
| 15.5% | Fewer tokens per task with the library (12,305 to 10,394) | [2, Table 1] |
| 100% to 51% | Distinct share of tools, library 26 to 128 | [2, Table 4] |
| 16 points | Accuracy swing across thresholds, 25 questions | [2, Table 3] |
| 96.8% (215 of 222) | Kept tools scoring zero on held-out suites, Haiku 4.5 | [3, Table 5] |
| 35.8% vs 33.7% | Verified completion, self-made vs seed tools, not significant | [3, Tables 3-4] |
| 41.1% / 71.1% / 53.5% | CoEvoSkills pass/fail only, full loop, human-curated, Opus 4.6 | [4, Table A1, Fig. 4] |
| 4% vs 92% | Opus 4.8 first-sight builds, abstract vs script required | [6, Table 1] |
| 1.67 vs 2.00 | DGM node 96 (real fix) vs node 114 (deleted markers) | [5, App. H] |
| 79 / 21 / 13 / 5 | Manifests / with trust class / hard-filter reasons / gaps | report §3, App. B |

## 5. Things not to say

- "The gate catches broken capsules": nothing is built or measured; say "predicted"
- "96.8% of our capsules would fail": 1 model in 1 harness
- "Alita-G's gain is fake": evidence both ways; its tools were never replayed
- "GAIA scores are comparable across systems": different stacks
- "The unmodifiable checker is our idea": DGM names it; new is enforcement through declared effects
- "2 sprints and 5 tries are right": starting values, revised from the data
- "Build" as 1 step: 3 model sessions plus a code gate
- "Silent rot", "Qiu et al.": paper titles only
