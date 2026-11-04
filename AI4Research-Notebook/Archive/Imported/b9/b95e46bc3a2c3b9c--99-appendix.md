# Appendix B. Figures from the papers

Each figure is cropped from the paper's own PDF by `../deck/figures/extract_paper_figs.py`, with its page and caveat.

![Figure 16. Don't Offer What Can't Be Done (2608.01050), Fig. 1, p4: the three-stage pipeline. Only stage 2, a deterministic gate on each skill's own exit conditions, removes candidates.](figures/papers/dont-offer-pipeline.png)

![Figure 17. Don't Offer What Can't Be Done (2608.01050), Fig. 2, p4: skill-description tokens. The gate removes 59.1% after semantic matching, 90.5% combined. Ten skills, one month; description tokens only.](figures/papers/dont-offer-tokens.png)

![Figure 18. Contract2Tool (2606.07904), Table V, p8: a keyword top-5 filter cuts tokens but lowers success; contract-based filtering exposes one tool, cuts tokens tenfold and raises success. Synthetic registry, mocked execution.](figures/papers/contract2tool-exposure.png)

![Figure 19. More Skills, Worse Agents? (2605.24050), Fig. 1, p3: pass rate falls as the library grows from the oracle skills to 202. Human-authored skills; 38 task-model pairs.](figures/papers/more-skills-drop.png)

![Figure 20. The Blind Curator (2607.07436), Fig. 2, p5: deterministic checks and an LLM judge catch different defects. One domain; flag rates, not scores.](figures/papers/blind-curator-qc-vs-judge.png)

![Figure 21. When Self-Evolution Backfires (2608.05810), Fig. 4, p7: rollback after the fact recovers little; removing the source skills recovers 1.7 of 12.3 points, and the pool gated before commit ends at 72.0%. One run.](figures/papers/backfires-contamination.png)

![Figure 22. SkillFuzz (2607.02345), Fig. 6, p9: severe drift is rare for single skills and rises with the number co-activated, to 66.5% at five, which the paper calls a fourteen-fold increase.](figures/papers/skillfuzz-depth.png)
