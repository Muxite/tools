**Every cited paper was read in full by Muk and by an agent.** Each number, its page and its caveat is in `capsule-openjiuwen/verify/PAPER-LEDGER.md` and `alt/READ-LOG.md`. The design source for self-improvement is the 2026-09-15 capsule report (→ [[Self-Improvement]]).

| Paper | Used for | Headline, with caveat |
|---|---|---|
| Beyond Task Completion (2604.00392) | admission tests the declared job | 215 of 222 self-built tools failed every held-out test. Haiku 4.5, 3 seeds |
| Don't Offer What Can't Be Done (2608.01050) | [[Predicate Parity]], tokens | 7.8% blocked picks without a gate. 59.1% and 90.5% fewer description tokens |
| Contract2Tool (2606.07904) | why not a heuristic, tokens | keyword filter 0.620 success; contract filter 0.980 at 2,528 tokens against 26,172. Synthetic |
| More Skills, Worse Agents? (2605.24050) | selection at scale | pass rate down 0.21 [0.15, 0.27] at 202 skills (Table 1, p9; the 0.49 and 0.28 endpoints are read off Fig. 1, an image, so documents cite the printed drop); 38.5% invoked no skill. It proposes retrieval pre-filtering as a mitigation (p10); it does not blame retrieval |
| The Blind Curator (2607.07436) | verifier audit | biased judge stopped retirement (0 to 0.3 against 1.3); deprecations never reached zero |
| When Self-Evolution Backfires (2608.05810) | improvement check | removing the gate cost 8 points; cleanup won back 1.7 of 12.3. One run |
| Library Drift (2605.19576) | librarian | harsh retirement below the no-skill floor; the cap controls variance |
| SkillFuzz (2607.02345) | load isolation | severe drift rare with one skill, 66.5% of plans with five loaded, "a fourteen-fold increase" (p9) |
| Cognitive Admission Control (2609.16313) | typed verdicts | unknown defers; only a violated check rejects |
| AllocBench (2607.23332) | gap-driven builds | first-sight commitment 85-99% for three of four models |
| Skill Drift Is Contract Violation (2605.10990) | unpinned dependencies with a written purpose | one-round repair 10% to 78% given the failed contract (p8-9), not significant against plain drift text (60%) or three-round Self-refine (80%); the written purpose is our design, not the paper's; no false alarms over 599 cases |
| Cordis (2608.25512) | spatiotemporal composability | vocabulary and the inside/outside boundary; a formal model with one qualitative case study; agent harnesses are its future work |
| SkillFuzz (2607.02345), again | composition screening | 80.6% of high-risk plan-level flags confirmed when executed (Table II) |
| Darwin Gödel Machine (2505.22954) | the gate is never a capsule | a node removed the logging its checker read, in 3 tasks |
| Alita-G (2510.23601), CoEvoSkills (2604.01687) | libraries help; separate verifier | 75.15% to 83.03% on its build set; 71.1%; 41.1% when the verifier's diagnostics are replaced by bare pass or fail (shows feedback matters, not separation) |
| Agent Contracts, ABC, GraSP, SkillDAG, Execution lineage, RelAIBuild | budgets, prior art, taint | see the ledger |

**Rule**: verify every reviewer in the source. Reviewers have been wrong (More Skills' 0.49 and 0.28 are in its Fig. 1; Haiku's title lengths; Sonnet's missing script) and right (the SkillPack cascade dates to `6f4eaa1b6`; RSI's held-out split is a code change).
