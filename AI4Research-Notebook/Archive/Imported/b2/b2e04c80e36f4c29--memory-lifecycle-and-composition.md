# Memory lifecycle and composition: targeted M2 evidence

**Snapshot: 7 October 2026.** Exploratory research only; no design or M1 requirements. The existing [capsule-feeds note](capsule-feeds.md) already covers ExpeL, experience provenance, retrieval and selection. This addendum focuses on evidence absent there: invalidation of stale/conflicting lessons and composition-level postconditions. Primary full texts were inspected at the sections cited below; no code or benchmark was executed here.

## Human synopsis

Direct experiments now test superseded memories rather than treating relevance as validity. They show two different problems: explicit update order can still be hard to preserve across long contexts, while implicit changes require recognizing that a later fact invalidates a related older assumption. A recent preprint reports that making memory validity/revocation explicit helps on controlled reversal and small file-backed tasks, but relies on structured conflict keys and performs poorly on harder multi-hop/very-long cases. Treat this as promising narrow evidence, not a general memory design prescription.

For composition, a formal robotics paper demonstrates how module-level assumptions and guarantees can be composed into system properties and runtime monitors. This is an analogy for M2 contract tests, not evidence that agent memories or capsules compose safely. A useful experiment should keep lessons advisory and authority fixed, then measure both safe reuse of current lessons and rejection/quarantine of obsolete or unresolved conflicts.

## Primary evidence

### MemoryAgentBench: Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions

Hu, Wang & McAuley; first posted 7 July 2025, inspected arXiv v4 dated 28 June 2026; published at ICLR 2026. [Paper/version history](https://arxiv.org/abs/2507.05257v4) · [full text](https://arxiv.org/html/2507.05257v4). Inspected §§3.1, 3.3, 4.2–4.3.4 and Appendix K.2.

**Reported evidence.** The benchmark defines selective forgetting as revising, overwriting or removing earlier information after contradictory evidence. Its FactConsolidation data orders an original fact before a contradictory counterfactual rewrite, and tests single-hop and multi-hop questions over contexts of 6K–262K tokens. Prompts explicitly tell agents that later serial numbers are newer and should win. Performance falls with context length; for example, GPT-4o drops from 92% to 88% on single-hop between 6K and 32K, and from 28% to 10% on multi-hop. A separate GPT-4.1-mini overwrite-policy ablation only improves single-hop by 4 points (36→40) while multi-hop drops 5→4; a conservative explicit-negation policy lowers average performance. This is direct evidence about update retention and long-context composition, not spontaneous freshness detection.

**Limits / inference.** Fact edits are synthetic/counterfactual and ordered; the instruction supplies a resolution rule. Accuracy is QA over facts, not whether a reusable scientific procedure remains valid after environment or protocol drift. M2 could add challenge cases where age alone is insufficient and where conflict must remain unresolved; the benchmark motivates those cases but does not validate that policy.

### STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?

Chao et al.; arXiv first posted 7 May 2026 (v1). [Paper/version history](https://arxiv.org/abs/2605.06527v1) · [full text](https://arxiv.org/html/2605.06527v1). Inspected §§3–5 and Appendix A.

**Reported evidence.** STALE builds 400 expert-validated implicit-conflict scenarios and 1,200 queries. A later observation may contradict the same attribute (Type I) or change a related attribute so an older belief becomes invalid without direct contradiction (Type II). It separately tests direct state resolution, resistance to queries that assume the stale state, and downstream application of the update. The strongest evaluated base model reaches 55.2% overall; a CUPMem prototype with write-side state adjudication reports 68.0% using GPT-4o-mini, versus 8.7% for the GPT-4o-mini baseline. These share a backbone and benchmark but use different context/memory pipelines; the comparison is not a matched single-component ablation. Diagnostics show retrieval of new evidence often coexists with failures to apply it. This supports separating retrieval from state adjudication and downstream behavior.

**Limits / inference.** It is a preprint and controlled personalization benchmark: each case has a single conflict pair; scenarios are LLM-generated then human-reviewed; judge scoring is LLM-based; distractor sessions are not from the same persona. CUPMem is one prototype, not independent confirmation. The paper motivates testing indirect invalidation and premise resistance for experience feeds; it does not establish a general rule for revoking scientific lessons.

### TEPA: Revoking Stale Memories for Conflict-Robust Language Agents

Zhou et al.; first posted 7 Aug 2026, inspected v2 dated 10 Aug 2026; preprint. [Paper/version history](https://arxiv.org/abs/2608.07429v2) · [full text](https://arxiv.org/html/2608.07429v2). Inspected §§4–5, 6 (results), 7 (limitations), Appendices B–C.

**Reported evidence.** TEPA stores keyed precedents with Active/Hypothesis/Revoked states, removes contradicted values from ordinary retrieval, and keeps revoked entries for audit. In 50-seed controlled hidden-regime full reversal, append-only and last-write-wins score .210 vs no-memory .309 and TEPA .950; separate generated-file execution gives .203/.298/.950 respectively. A preference-update stream similarly shows stale profiles harming reversal; TEPA-Full adds trial validation for promoting new candidates. On clean single-hop MemoryAgentBench fact consolidation, revocation matches last-write-wins. This is direct evidence for comparing active stale exposure against explicit revocation in scoped conflict settings.

**Limits / inference.** Results are author-reported preprint claims, not independent replications. Drift executors are deterministic; “file execution” uses generated files and tool libraries, not a real scientific workflow. Key/value conflict extraction is structured and the authors say implicit/open-ended conflict is harder. Multi-hop and 262K-context results are boundary failures. For M2, revocation should be evaluated as an advisory retrieval lifecycle; neither this paper nor its high narrow-task score authorizes a lesson to alter policy, capsule identity, permissions or gates.

### A Compositional Approach to Verifying Modular Robotic Systems

Luckcuck et al.; arXiv first posted 10 Aug 2022, inspected v4 dated 31 July 2026; version accepted at Robotics and Autonomous Systems. [Paper/version history](https://arxiv.org/abs/2208.05507v4) · [full text](https://arxiv.org/html/2208.05507v4). Inspected §§3.3–3.7, §4 (rover case study), and §5.

**Reported evidence.** The authors specify ROS nodes with first-order-logic assume-guarantee contracts, provide inference rules for composing node contracts into system-level safety/mission properties, and synthesize runtime monitors from guarantees. Their remote-inspection rover case study demonstrates the method across nodes verified with heterogeneous formal and non-formal methods. They caution that contracts must be checked against actual system requirements; the system graph is manually abstracted, and formal links from every verification method to the contract are out of scope.

**Analogy only / inference.** This is formal software verification for a ROS system, not an LLM-memory experiment. It gives M2 a useful test shape: verify local pre/postconditions, then check whether compatible assumptions/guarantees imply the composite’s required postcondition; monitor the composition boundary. It does not prove that capsule contracts are complete, that a natural-language lesson is valid, or that a learned procedure generalizes.

## Optional M2 experiment: lesson validity without authority promotion

Use one frozen, already admitted workflow and a fixed task suite. Keep capsule version, protocol, tools, permissions, and protected release gate identical. Randomize only the advisory feed condition:

1. no lesson;
2. a current, source-linked lesson whose scope and preconditions match;
3. the same lesson made obsolete by a pinned environment/protocol change;
4. old and new contradictory lessons together;
5. a plausible conflict with insufficient evidence to choose a current value;
6. a relevant-looking lesson from a different scope/version.

Have an independent predeclared oracle for expected task results and effects. Record exactly which entries were selected, their provenance/scope/version, and the observed tool effects. Measure valid lesson reuse, stale/conflicting lesson use, unnecessary rejection of valid lessons, correct “unresolved” handling, scientific result validity, side effects, trace reconstruction and cost. Include null/negative outcomes and repeats. Do not count an agent’s own “this lesson is stale” statement as adjudication.

For composition, add a paired arm with the same component sequence: (a) verify local contracts only; (b) additionally verify compatibility of upstream guarantees with downstream assumptions and a prespecified composite postcondition at the consumer boundary. Inject a small number of schema/version/precondition mismatches. Measure false acceptance, false blocking, and ability to identify which contract edge failed. The robotics paper motivates this structure by analogy; the system oracle and safeguards remain M2 choices, not established by that paper.

## Boundary and evidence gaps

These papers mostly test user facts/preferences, synthetic counterfactual knowledge, or generated-file tasks. They do not show that experience from a scientific run remains valid after a changed hypothesis protocol, dataset, instrument calibration, code/container, or sampling regime. They also do not establish how to resolve provenance conflicts between sources of different authority. The highest-value next evidence is therefore a small controlled scientific workflow with real pinned inputs/environment, deliberately varied current/stale/contradictory lessons, independent outcome/effect checks, and an unresolved state that stays advisory rather than silently becoming a policy or binding.

Independent model/condition/version checks: [audit findings](audit-findings.md).


