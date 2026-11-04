---
title: Quantitative and version audit: memory lifecycle and composition
date: 2026-10-07
tags: [research-audit, memory, versioning]
status: research-note
---

# Audit findings

Checked against the cited primary versions/current metadata available on 2026-10-07. This is claim audit, not a paper synopsis.

| Claim in `memory-lifecycle-and-composition.md` | Check against primary source | Finding / recommended wording |
|---|---|---|
| **TEPA reversal:** 50-seed controlled drift and generated file-execution show append-only/LWW about .21 vs no-memory .31; TEPA .95. | [TEPA v2 (2026-08-10)](https://arxiv.org/abs/2608.07429), §§4–5 setup, Results §§7.1–7.2, Tables 2, Apps C/E. | **Pass, but separate the two conditions and exact controls.** Controlled hidden-regime full reversal: append-only **.210**, last-write-wins **.210**, no memory **.309**, TEPA **.950**. File-backed executable full reversal: append-only **.203**, last-write-wins **.203**, no memory **.298**, TEPA **.950**. These are paired controls on the same task stream/backend within each setting; both use deterministic executors and 50 seeds. “About .21 vs .31” is the controlled condition, not a combined value. The file-backed condition is generated/local file I/O, not a real scientific workflow. v2 explicitly calls this a preprint (§1), and assumes schema-extracted conflict keys; results are not independent replication. |
| **STALE:** CUPMem gets 68.0% on GPT-4o-mini vs 8.7% baseline. | [STALE v1 (2026-05-07)](https://arxiv.org/abs/2605.06527), §4.1/Table 2, §4.2, §5, App. D.4/E.1/F. | **Same backbone, not same end-to-end setup or an isolated ablation.** Table 2 reports plain GPT-4o-mini **8.7%** and CUPMem **68.0%** overall (mean over six Type-I/II × SR/PR/IPA cells); §5 explicitly says “under the same backbone.” Both use the same benchmark and judge, but the plain LLM gets serialized dialogue history, with evidence-preserving truncation for context overflow (`*`, §4.1); memory-framework systems ingest once under their native protocols and answer three probes from fixed constructed memory. Phrase “same GPT-4o-mini backbone, different memory pipelines”; do not imply prompt/context-matched or a single-component causal ablation. 400 scenarios/1,200 queries; LLM-generated and human-validated (§2.4, App. A.1). |
| **MemoryAgentBench overwrite ablation:** overwrite prompts 36→40 SH, 5→4 MH; conservative explicit negation lowers average. | [MemoryAgentBench v4 (2026-06-28)](https://arxiv.org/abs/2507.05257), App. K.1–K.2, Table 19. | **Numbers pass; missing model/frame qualifier.** These are the separate **GPT-4.1-mini baseline** overwrite-policy ablations: baseline 36.0/5.0 (FC-SH/FC-MH, avg 20.5); Policy A (“always prefer later”) 40.0/4.0 (avg 22.0, +1.5); Policy B (“only explicit negation”) 28.0/4.0 (avg 16.0). App. K.2 is not the GPT-4o context-length comparison. Separately, Table 5 reports GPT-4o 6K→32K as SH 92→88 and MH 28→10. State the model alongside each result; these are prompt ablations in the benchmark’s serial-number/update-rule setup, not a general selective-forgetting guarantee.
| **ROS paper:** arXiv v4 dated 2026-07-31; “version accepted at Robotics and Autonomous Systems.” | [arXiv current record](https://arxiv.org/abs/2208.05507), v4; [publisher record](https://www.sciencedirect.com/science/article/pii/S0921889026003209); [University of Manchester publication record](https://research.manchester.ac.uk/en/publications/a-compositional-approach-to-verifying-modular-robotic-systems/). | **Version is right; acceptance wording is safer than “published.”** arXiv metadata says v4 last revised 2026-07-31. The university record lists *Accepted/In press* 2026-07-19. The publisher assigns RAS vol. 205/article 105648 and a November 2026 issue date, which is still future relative to the note’s 2026-10-07 snapshot. “Accepted/in press at Robotics and Autonomous Systems” is accurate; avoid claiming issue publication as of the snapshot.

## Cross-note correction log

The earlier working snapshot of [[typed-selection]] incorrectly attached PlanBench’s **35/600 (5.8%)** cost-optimal-plan result to the obfuscated/mystery condition. The current version has been corrected: PlanBench Table 1 reports **198/600 GPT-4** and **35/600 InstructGPT-3** on Blocksworld cost-optimal planning. The latter is a model-column comparison, not an obfuscated-domain score. If any earlier copy was captured, update it.

## Review coverage

- Full text inspected at pinned versions: MemoryAgentBench v4, STALE v1, TEPA v2, and ROS paper v4. Specific sections/tables are listed above.
- Version metadata checked against arXiv records; ROS acceptance/publication status additionally checked with the university and publisher records.
- No changes made to the audited source note or tracked/design-package files.
