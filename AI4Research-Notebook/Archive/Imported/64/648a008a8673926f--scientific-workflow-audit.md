# Scientific-workflow note audit

Audit date: 2026-10-07. Checked primary full text (not author code).

## AutoLabs — pass with qualification

[Version of record, Scientific Reports (25 June 2026)](https://www.nature.com/articles/s41598-026-45593-z); primary full-text sections “RAG pipeline,” configuration definitions, and “Hardware validation.” The three retrieved procedures and reported mean changes are correct. Name the compared conditions: `MA (PR)` improves overall F1 by 0.044; `MA-TU-GSC (PR)` changes overall/chemical/parameter F1 by −0.024/−0.034/+0.002 and average quantity nRMSE worsens by 0.028. This is not an isolated architecture comparison: the second condition adds tool use and guided self-check. The note now says so. Hardware distinction passes: five protocols were simulated, but only Experiments 1–2 were physically run end-to-end; final generated-file loading was 100% for Experiments 1–4, with occasional Experiment 5 multi-plate issues. Simulation used no robotic-arm motion.

## RoboCulture — denominator passes; autonomy qualification retained

[Pinned arXiv v2 (24 May 2025)](https://arxiv.org/abs/2505.14941v2), §§II-B, II-F, III; Table II. Six randomized plate placements × 96 target wells = 576 target-well attempts. “Success” counts insertions completed after retry; max three retries per well, 38 retry cases, six final failures: 570/576 = 98.96% (reported 0.990). “Perfect” means no edge contact/retry: (576−38−6)/576 = 92.36% (reported 0.924). These rates are not counts of low-level motion attempts.

Results §II-F says the 50M and 30M groups split at detected saturation, while an operator manually instructed the unsaturated 10M group’s early split at 12 h; initial seeding was manual. Discussion §III instead says “splitting was manually initiated as a safety precaution.” The degree of autonomous split triggering is therefore ambiguous; the ignored overview now flags this internal inconsistency. The same study was later published under the changed title [“RoboCulture enables modular robotic plate-based cell automation,” Cell Reports Physical Science 7(7), 103335 (2026)](https://doi.org/10.1016/j.xcrp.2026.103335); treat it as a publication/version of this study, not independent replication.
