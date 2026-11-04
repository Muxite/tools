# Typed-selection source audit — 7 October 2026

Independent primary-source checks of [typed-selection.md](typed-selection.md). No implementation was tested. Figures below clarify what can be compared; they do not establish capsule-selection performance.

| Claim | Checked source and result |
|---|---|
| AgentAbstain accuracy | [v1, 11 July 2026](https://arxiv.org/html/2607.10059v1), §§2.2–2.4/3.1–3.2: eight-category macro paired accuracy; both variants must pass. Seventeen model/harness combinations across four harnesses, not a full crossing. Once per pair/model, no repeat variance. |
| ToolRobustBench aggregation | [v1, 23 August 2026](https://arxiv.org/html/2608.23635v1), §§4–5/9: 15,456 records includes 1,344 clean and 14,112 perturbed records. Clean .979 averages baseline rows; .664–.766 are per-model macro scores across perturbation families. Mixed-family runs are separate. |
| PlanBench historical baseline | [v4, 26 November 2023](https://arxiv.org/html/2206.10498v4), §7 Table 1: 198/600 and 35/600 are cost-optimal Blocksworld for GPT-4 and InstructGPT-3 respectively, not a Mystery comparison. Current note has corrected labels. Table 2's printed 14/600 percentage has a decimal-place error; use the fraction. |

An earlier note snapshot mislabeled the PlanBench comparison as original versus mystery-domain plan generation. That claim has been corrected in the current note. The audit independently confirms the corrected task/model attribution.

Our inference: score discovery, compatibility and abstention separately, with a prespecified outcome oracle. Aggregating different stages or counting paired accuracy as pure refusal accuracy would obscure what the system needs to improve. None of these papers jointly tests the capsule contract proposed in our experiment.
