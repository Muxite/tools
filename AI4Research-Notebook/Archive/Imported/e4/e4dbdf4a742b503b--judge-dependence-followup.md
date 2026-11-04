# Judge-panel dependence: compact comparison (2026-10-07)

**Status:** primary-source comparison, not design authority. Both records are single-version arXiv preprints: Kohli, v1 submitted 2026-05-28; Hossain, Yousefi & Lim, v1 submitted 2026-09-18. Neither establishes an error rate for JiuwenSwarm.

## Main source: Kohli

[Kohli, *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels*](https://arxiv.org/abs/2605.29800), [full text](https://arxiv.org/html/2605.29800v1), §§3.1–3.4, 4.1–4.6, 5.3–5.4, §6 Limitations, Appendices D–F.

The paper tests nine models from seven families at temperature zero. For each ChaosNLI task (MNLI, SNLI, AlphaNLI), it entropy-stratifies 1,000 items; each item has 100 human labels and majority as reference. On MNLI, Kish design-effect n_eff=2.18 (item-bootstrap 95% CI 2.07–2.31); eigenvalue check 2.16. Actual panel accuracy is 72.0%, versus 71.8% for its best member (+0.2pp, within noise). Separately, an item-aware independent-vote Condorcet null predicts ~94% (gap 22.0pp, 95% CI 19.5–24.1). On 1,000 proportionally sampled RewardBench pairs with randomized A/B placement, n_eff=1.99 (1.83–2.20), error correlation .44, actual accuracy 92.7%, and gap 6.8pp. Prompt, label-order, and temperature variants leave NLI n_eff near 2.15–2.18; chain-of-thought raises correlation.

**Interpretation limits:** n_eff approximates variance, not accuracy; the gap separately compares actual accuracy with a specified null. Kish assumes exchangeability; the eigenvalue check supports it for this bank. The §4.4 ~2.6 asymptote holds observed mean correlation fixed; it is not a universal ceiling. All four tasks are classification/binary preference, not open-ended review or infrastructure conformance. NLI majority labels remain imperfect on ambiguous items. Item-bootstrap intervals omit judge-bank selection uncertainty; results are a model snapshot.

## Comparison with Hossain et al.

[Hossain, Yousefi & Lim, *Agreement Overstates Evidence: Error Dependence in LLM Judge Consensus*](https://arxiv.org/abs/2609.22512), [full text](https://arxiv.org/html/2609.22512v1), §§2–4, Appendix M. Its main bank is ten logical judges (five 7–9B models × two prompt styles): on 1,133 complete RewardBench v2 pairs, error correlation=.206 and n_eff=3.51; UltraFeedback (1,885 pairs) gives n_eff=3.36, PKU-SafeRLHF (635) gives 2.89. A separate three-frontier-judge bank has correlation=.56 on 400 shared RewardBench pairs. Hossain’s primary RewardBench bank differs from Kohli’s nine-model, frontier-heavy panel, sample, benchmark version, and prompt; the estimates are not contradictory replications. Hossain’s frontier result is directionally closer, but still not a matched panel.

## Design inference

For any M2 panel experiment, measure accuracy and item-level error dependence on frozen, profile-specific labeled cases; record judge bank, model versions, prompt, sample, and uncertainty. Report n_eff alongside actual panel accuracy, best-member accuracy, and a predeclared baseline; recalibrate after bank or prompt changes. This is a candidate measurement protocol, not a requirement inferred directly from either paper. Vote count or provider diversity cannot substitute for evidence provenance, completeness, or host-enforced policy. Consensus may help flag disagreement or escalation, but it should not grant permissions or override required evidence.

**Non-transfer limit:** these studies test discrete judgments with known labels. They do not evaluate capsule-artifact verification, multi-obligation evidence review, or permission enforcement. Their results inform risk hypotheses and experiment design only.
