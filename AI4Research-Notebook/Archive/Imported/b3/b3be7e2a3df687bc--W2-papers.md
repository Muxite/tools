# W2-papers: paper fidelity, setup and use, in capsule §2 / App. A and deck slides 5-17

Every number below was read tonight from `papers/<id>.txt` in the main tree. Line numbers are that file's.

## OWNED

- `notes/report-capsules/REPORT.md` §2 (2.1-2.8, Tables 1-2, Figs. 3-7) and Appendix A
- `notes/report-capsules/deck-src/build_deck.py` lines 186-388 (evidence divider through the R6 rule slide)
- `notes/pass2/review/W2-papers.md`

## TOUCHED

- `REPORT.md`: §2.1, §2.2, §2.3, §2.4, §2.5, §2.6, §2.7, §2.8, App. A.1, A.2 (Table A2 + bullets), A.3, A.4, A.5
- `build_deck.py`: evidence divider, Alita-G slide 2, Beyond Task Completion slide, CoEvoSkills slide, both DGM
  slides, the independent-check rule slide, the AllocBench slide, the R6 rule slide
- Not touched: any `d.figure(` call, `figures.py`, `figdata.py`, §1, §3-§6, App. B-G

## Fidelity check (all verified, nothing cut)

| Claim | Source read | Verdict |
|---|---|---|
| 75.15 → 83.03 pass@1, 12,305 → 10,394 tokens | `2510.23601.txt:373-393` Table 1 | matches |
| Eq. (5) keeps every tool from a correct run; Eq. (6) is 1 LLM rewrite; §3.3 names the 4 transformations | `:233`, `:245`, `:249-262` | matches |
| k=3→4 adds 28 MCPs and 8 clusters, accuracy flat at 83.03; coverage 1.00→0.51; yields +15/+11/+8/+5 | `:506-528` Table 4 and text | matches |
| Threshold sweep 84.0 → 68.0 (16 points) and encoders 84 → 72 (12 points), both on 25 questions | `:491-500`, `:576`, `:549-560` | matches |
| 13 wrong→right, 0 right→wrong, 3.4 vs 2.4 calls | `:606-611` Table 6 | matches |
| 222 tools, 215 zero, 96.8%, mean C 0.018, mean R 0.525 | `2604.00392.txt:278-284` Table 5 | matches |
| References score C=1.00 on all 16 suites; suites 5-6 hidden + 5-6 adversarial, median 11 | `:309-316`, `:279-284` | matches |
| Session-level TC 0.31-0.34 in the re-execution | `:284-288` (§5.3) | matches |
| "certifies the answer; it does not certify the library"; "scores task outputs, not tools" | `:10`, `:26`, `:295` | matches |
| Powered to 8-13 pp; largest observed 7.1 pp | `:217-224` | matches |
| CoEvoSkills 30.6 / 30.7 / 32.0 / 34.1 / 41.1 / 42.4 / 53.5 / 71.1 on 85 tasks, Opus 4.6 + Claude Code | `2604.01687.txt:442-444`, `:518-522`, `:927-932` | matches |
| Budget K=5 oracle rounds, M=15 surrogate retries; 4.1 cycles, 2.4 oracle rounds; >60% inside 2; diminishing past 3; 10 failing tasks exhaust it | `:289`, `:985-1000` | matches |
| DGM 20.0 → 50.0 SWE-bench Verified, 14.2 → 30.7 full Polyglot, 80 iterations | `:400-405` | matches |
| Selection ∝ sigmoid(score) / (1 + working children); archive never pruned | `:1758-1790` App. C.2 | matches |
| App. H: 150 iterations, 3 SWE-bench tasks, node 96 = 1.67, node 114 = 2.00 after 2 modifications, checker hidden | `:5305-5330` | matches |
| "an option worth exploring is to create an unmodifiable part of the system…" | `:633-634` | matches |
| AllocBench Table 1 (4/0/92/99 Opus; 28/33/99/100 Haiku; 15/29/85/88 mini; 24/0/39/100 Sol) | `2607.23332.txt:352-360` | matches |
| 24 streams, T=60, N=8, B=3, 3 hot / 5 trap, trap forced into first 3 slots | `:184-194`, `:214-216` | matches |
| Optimum passes every first instance and builds on confirmed recurrence | `:176-180`, Fig. 1 | matches |
| R2 stays near 100% first-sight at every visible price, including K=24 | `:1291-1292` (App. E) | matches |
| "separate the abstract decision to invest from the process of creating the tool" | `:551-552` | matches |
| Chart data `figdata.SILENT_ROT`, `COEVO`, `ALLOC_LEVELS`, `ALLOC` | against the 3 tables above | all correct, no edit needed |

Two numbers were wrong in their setup, not in their value, and are fixed below: "99 tasks" as the denominator of
the 96.8%, and "165 questions" printed as if the Alita-G paper states it.

## CHANGES

### REPORT.md

- §2.1 `REPORT.md:87` "There are two limitations" -> "three", + bullet "The GAIA figures are single runs, since the
  paper reports no seeds, standard errors or confidence intervals, and the 7.88-point gain is 13 questions turning
  from wrong to right out of 165 [2, Table 6]"; why: the paper reports no variance, and a supervisor asks whether
  7.88 points is noise before anything else.
- §2.1 `:90` "runs Claude Sonnet 4 with GPT-4.1" -> "runs Claude Sonnet 4 as manager with GPT-4.1 as web agent";
  why: the roles are what make the stack non-comparable (`2510.23601.txt:343-347`).
- §2.2 `:111` new paragraph after the R1-R4 paragraph: Alita-G stops at 3 harvests because 3 -> 4 adds 28 tools and
  8 clusters with accuracy flat at 83.03% [2, Table 4], thus the cold path builds under a budget (App. G.4) and
  §5.1 tests whether reuse repays admission; why: the k=3 plateau was cited in Table 1 but drove nothing.
- §2.3 `:115` "Across 222 tools from 3 tool-creating protocols, 215 (96.8%)" -> "…, run with Claude Haiku 4.5 over
  3 seeds by 8 sessions of EvolveTool-Bench each, 215 (96.8%)"; why: the body stated the result without its n.
- §2.4 `:139` new paragraph before the Thus: the loop is bounded at 5 oracle rounds and 15 surrogate repair
  retries, 2.4 oracle rounds on average, diminishing past 3, and the 10 failing tasks exhaust the budget
  [4, Alg. 1, App. B]; Thus extended with "…and the generator gets a fixed, small number of tries at them.
  Section 4.3 caps submissions to the admission gate for that reason, and Section 5.1 starts the cap at 5"; why:
  Table 7 already starts the gate-try count at 5 "after CoEvoSkills", and §2 never carried the number it comes from.
- §2.5 `:145` added the selection rule and the never-pruned archive [5, App. C.2]; "Over 80 iterations this raises
  its score from 20.0% to 50.0% on SWE-bench" -> "Over 80 iterations, with Claude 3.5 Sonnet performing the
  self-modification, … on SWE-bench Verified, the human-filtered subset where every task is solvable, and, with
  o3-mini running the agent on the full Polyglot benchmark, …" [5, Sec. 4.4]; why: no model or benchmark scope
  was stated, and the subset is not the full SWE-bench.
- §2.5 `:149` new Thus after Fig. 6: an archive that deletes nothing is what lets selection reach an older version,
  and §4.5 makes the library append-only for the same reason; why: §4.5 cited DGM's archive, §2 never handed it over.
- §2.6 `:153` "In a separate run on 3 SWE-bench tasks" -> "In a separate run of 150 iterations, with every agent
  scored on the same 3 SWE-bench tasks"; why: n and run length were missing.
- §2.7 `:181` R5 "…and a reason returned to the builder" -> "…and a reason returned to the builder a capped number
  of times"; why: the cap is CoEvoSkills' contribution and belongs in the rule, not only in §4.3.
- §2.8 `:185` "tests this on a stream of 60 problems from 8 families in which a few families recur and the rest are
  traps" -> "tests this on 24 streams of 60 problems from 8 families in which 3 families recur and 5 are traps,
  under a budget of 3 tools" + [6, Fig. 1]; why: n and the budget are what make first-sight commitment costly.
- §2.8 `:189` Thus extended: the benchmark's optimum passes every first instance and builds on the confirmed
  repeat, so §4.2's threshold starts at 2 sprints and §5.1's census raises it; and the budget is enforced by the
  runtime rather than priced, since a visible price left code-required commitment near 100% [6, App. E]; why: the
  threshold of 2 and the hard-limit budget in App. G.4 had no stated evidence.
- App. A.1 `:478` 3 new bullets: the paper never prints the validation-set size and 165 follows from 13 flips being
  7.88 points [2, Tables 1 and 6]; no seeds or intervals are reported; the plateau is 28 tools and 8 clusters with
  the authors reading 3 harvests as the cost-utility balance [2, Sec. 5.2].
- App. A.2 Table A2 `:495` "EvolveTool-Bench, 99 tasks, 3 seeds by 8 sessions" -> "EvolveTool-Bench verified
  subset, 3 seeds by 8 sessions per protocol"; + bullet recording that 99 is the benchmark and the pilot scores
  only tasks with deterministic verifiers [3, Sec. 3.1, Sec. 3.2]; why: 99 read as the denominator of 96.8%.
- App. A.3 `:544` 2 new bullets: the 5/15 budget and its convergence profile [4, Alg. 1, App. B]; the full setup
  line (SkillsBench, 85 tasks, deterministic verifier each, Opus 4.6 in Claude Code) [4, Sec. 4.1].
- App. A.4 `:550` 3 new bullets: models and the SWE-bench Verified scope [5, Sec. 4.1-4.2]; the staged 10 / 60 /
  200-task evaluation rule; the parent-selection formula and the never-pruned archive [5, App. C.2].
- App. A.5 `:569` 2 new bullets: the optimum and the forced early trap [6, Sec. 3.1, Sec. 3.2, Fig. 1]; all 4 rungs
  render the same latent sequence and the declarative rung shifts no model, which rules out arithmetic difficulty
  [6, Sec. 4.2].

### build_deck.py

- `:186` divider SAY "Now the research. After each result…" (14 words) -> "On to the research. Five papers, and
  after each one I'll say what its result means for the design I am proposing." (22 words); why: "Now" is a banned
  first-time-reader word and the SAY was under the 20-word floor. TIME 0:10, cap 23.
- `:231` slide 7 SAY + "Their own growth study stops at 3 harvests: a 4th adds 28 tools and only 8 new
  capabilities, and accuracy does not move."; slide 7 IF ASKED + the 165 provenance line. SAY 117 words, cap 126.
- `:256` BTC strip "99 tasks, Haiku 4.5, 222 kept tools" -> "EvolveTool-Bench, Haiku 4.5, 24 sessions, 222 kept
  tools"; why: 99 is the benchmark, 24 sessions per protocol is the n.
- `:276` slide 9 SAY "They don't crash" -> "They run and return values"; why: mean robustness is 0.52, so half the
  adversarial inputs do crash; the paper's own words are "execute cleanly" and "wrong on every held-out input".
  SAY 159 words, cap 161.
- `:287` slide 9 IF ASKED + "Scoring zero means wrong on every held-out input, not crashed on it; mean robustness
  on the adversarial inputs is 0.52".
- `:294` CoEvoSkills strip + "in Claude Code"; why: the harness is part of the setup.
- `:305` CoEvoSkills SAY + "And the loop is bounded: at most 5 tries against those hidden tests, with most skills
  done in about 2." (107 words, cap 115); IF ASKED + the 5/15 budget and the 10 exhausted tasks.
- `:314` DGM strip "SWE-bench and Polyglot coding benchmarks" -> "80 rounds, Claude 3.5 Sonnet, SWE-bench and
  Polyglot"; why: no model was stated on a slide that carries a benchmark delta.
- `:319` slide 11 bullets: bullet 1 now says the archive removes none, bullet 3 names SWE-bench Verified and
  o3-mini on Polyglot; SAY rewritten to 82 words (cap 103) with the 80 rounds and the model; IF ASKED + the
  parent-selection rule. Bullet box fits: 3 single lines, 1.35 in of 1.60.
- `:336` App. H strip + "150 rounds".
- `:359` rule slide R3 "(now precise) Every capsule passes held-out tests for its own job before it is kept" ->
  "Validation means held-out tests for the capsule's own job, passed before it is kept"; why: "(now precise)" is
  banned by the first-time-reader rule and reads as a diff against a draft nobody saw.
- `:362` R5 line 3 + ", at most 5 times" (84 chars, 1 line at 19 pt); SAY + "a set number of times, 5 to start,
  following CoEvoSkills" (107 words, cap 126); IF ASKED + where the cap moves.
- `:381` AllocBench strip -> "24 streams of 60 problems, 8 families, a budget of 3 tools, 4 models"; SAY + "The best
  policy here passes every first problem and builds on the confirmed repeat." (68 words, cap 80); IF ASKED
  rewritten so the price check says what it implies (enforce, do not price) and the hot/trap split is available.
- `:400` R6 rule slide + line "      2 sprints to start: the first confirmed repeat"; SAY + "Two sprints is where
  we start counting, because that is the first confirmed repeat." (54 words, cap 69); IF ASKED + the census.

`ast.parse` clean. No builder run. No `d.figure(` call, `figdata.py` or `figures.py` touched.

## CROSS-REFS

Exact sentences for other lanes. TIME delta across my slides: **0:00**. No slide needs more time.

1. `build_deck.py:136`, outside my line range. Replace
   `ALITA = ("Alita-G (arXiv 2510.23601)", "GAIA validation set, 165 questions")`
   with
   `ALITA = ("Alita-G (arXiv 2510.23601)", "GAIA validation, 165 questions, Sonnet 4 with GPT-4.1")`
   Reason: the strip is the only place slides 6 and 7 can state the model, and the stack is what makes the GAIA
   total non-comparable. 92 characters in the strip, inside the 1-line limit.

2. `REPORT.md` App. G.4, first sentence. Replace
   "The runtime enforces the build budget as a hard limit, the build-decision agent decides what to build within
   that budget, and the implementation agent never sees the budget as a price."
   with
   "The runtime enforces the build budget as a hard limit, the build-decision agent decides what to build within
   that budget, and the implementation agent never sees the budget as a price, because a visible price left
   code-required first-sight commitment near 100% at every price tested in AllocBench [6, App. E] while a library
   stops paying before it stops growing, as Alita-G's 4th harvest added 28 tools, 8 clusters and no accuracy
   [2, Table 4]."

3. `REPORT.md` §5.1 Table 7, row "Gate tries, starting at 5, the cap on evolution iterations in CoEvoSkills [4]".
   Replace the first cell with
   "Gate tries, starting at 5, the ground-truth oracle budget of CoEvoSkills, where 2.4 rounds is the mean and
   returns diminish past 3 [4, App. B]"
   Reason: "evolution iterations" is the 15-retry surrogate loop; the 5 is the oracle budget, which is the one the
   gate is analogous to.

4. `REPORT.md` §4.3, sentence "CoEvoSkills bounds its ground-truth oracle the same way, returning pass or fail for
   up to 5 rounds [4]." Replace with
   "CoEvoSkills bounds its ground-truth oracle the same way, returning pass or fail for at most 5 rounds, and it
   bounds the surrogate loop before it at 15 repair retries [4, Alg. 1]."

5. `REPORT.md` §4.2, sentence "The number of sprints that authorizes a build is not yet set." Replace with
   "The number of sprints that authorizes a build starts at 2, the first confirmed repeat that AllocBench's best
   policy waits for [6, Fig. 1], and settling it needs a census of how often planning binds the generalist to the
   same gap, which the gap record makes possible."
   Reason: §2.8 now derives the 2, Table 7 and Fig. 10 already use it, and §4.2 still says it is unset.

6. `REPORT.md` §5 Table 6, Track B cell "…and Alita-G's share of distinct tools, which has a published baseline of
   100% falling to 51%". Append "over 5 harvests, 26 to 128 tools [2, Table 4]" so the baseline carries its n.

## DOUBTS

1. **165 GAIA questions.** The paper never prints it; 13 flips = 7.88 points = 83.03 − 75.15 gives 165 exactly.
   Settled by: the GAIA paper (arXiv 2311.12983) or the released validation split, neither opened by this panel.
   Until then App. A.1 states the derivation and the deck says it under IF ASKED.
2. **"24 sessions" on the Beyond Task Completion strip.** The paper says 3 seeds × 8 verified-subset sessions =
   24 session rows *per protocol*, and the strip cannot fit "per protocol". Settled by: shortening the strip
   elsewhere, or dropping to "Haiku 4.5, 222 kept tools" and leaving n to App. A.2.
3. **DGM 20.0% → 50.0% task count.** Staged evaluation is 10 → 60 → 200 tasks, and the initial agent at 20.0%
   cannot have cleared the >40% gate to the 200-task stage, so the two endpoints may not share a denominator.
   Settled by: reading App. E.2 of `2505.22954.txt` in full. Both the body and the strip now avoid naming a count.
4. **CoEvoSkills 5 as the right start for gate tries.** The analogy is oracle rounds to gate submissions, but a
   CoEvoSkills oracle round follows a full surrogate-verified skill, while a gate submission may not. Settled by:
   the admission-rate-by-try-number measurement already in Table 7.
5. **"Diminishing returns past 3 oracle rounds"** is the authors' reading of Fig. B1, not a printed statistic.
   Settled by: the released artifact, or dropping the clause and keeping the 2.4 mean.
6. **AllocBench transfer.** 8 synthetic numeric families with clean identity are not research gaps with fuzzy
   identity, so "3 recur, 5 are traps" may not describe AI4Research at all. Table 7's gap census is the test;
   §2.8 does not claim the rate transfers, only the ordering rule.
7. **§2.5's new Thus points forward to §4.5,** which is another lane. If §4.5's SkillDAG/DGM/DSH sentence is
   reworded, the pointer needs to survive. Settled by: a grep for "append-only and versioned" before the build.
8. **Alita-G's right-to-wrong flips (1, 1, 0)** are in App. A.1 but not in §2, so the body never says self-extension
   caused regressions in 2 of 3 configurations. Settled by: the user deciding whether §2.1's limitations list
   should carry a 4th bullet, which would make it the longest list in §2.
