---
id: m1-cc-reference-index
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1@98bd9d913f9ddae5f0d6a3ae256bff10f25ee743; Resources/review-batches/2026-10-21-capsules/README.md
last_reviewed: 2026-10-23
next_action: Reconcile this source-grounded reference if the inspected M1 capsule or contract files change.
---
# M1 capability capsule reference

**Freshness boundary:** detailed role pages below describe the pinned 98bd9d9 source, compared only through d3d7f56. They are not a complete reference for inspected 809351f8. The later required typed Planner uses core `m1-13` and PDF `paper-m1-9`; see [[Activities/2026-10-23 Required M1 Planner]], [[Activities/2026-10-23 Final M1 Merge]], and [[Resources/Current Baseline]]. Other release/body deltas need their own source review.

This reference describes the implementation candidate at `ai4r_M1` commit `98bd9d913f9ddae5f0d6a3ae256bff10f25ee743`. It records observable code and declaration behavior, not acceptance or successful runtime evidence. The capsule and check assets were compared with the captured later remote `d3d7f565c6c05ccf764fe0780fde149b7dc89b95`; the capsule, native, and check source files cited here were unchanged in that comparison. Other product files did change, so this is not a claim that the entire branch is identical.

The maintained implementation remains in the repository. This vault reference summarizes boundaries and evidence so study design can target actual roles. It does not create independent CCs where M1 has only a host function or a combined node.

| Role at the historical pin | Reference | Source name or boundary at that pin |
|---|---|---|
| Intent compiler | [[Designs/CC Reference/Intent Compiler]] | `intent.compiler`, one worker capsule |
| Requirements compiler | [[Designs/CC Reference/Requirements Compiler]] | `requirements.compiler`, one worker capsule |
| Planner | [[Designs/CC Reference/Planner]] | `research.planner`, optional planning path; native one-shot Leader adapter |
| Semantic verifier | [[Designs/CC Reference/Semantic Verifier]] | `research.verifier`, separate reviewer subnode |
| Search | [[Designs/CC Reference/Search]] | `research.search`, two model calls with bounded captured retrieval |
| Screening | [[Designs/CC Reference/Screening]] | `research.screening`, model scoring plus pinned deterministic ranking helper |
| Hypothesis | [[Designs/CC Reference/Hypothesis]] | `research.hypothesis`, freezes a scientific blueprint |
| Builder | [[Designs/CC Reference/Builder]] | `research.builder`, governed coding call and static package checks |
| Benchmark | [[Designs/CC Reference/Benchmark]] | `research.benchmark`, deterministic host execution and measurement |
| Scientific Evaluation | [[Designs/CC Reference/Scientific Evaluation]] | `research.evaluation`, candidate assessment plus independent deterministic recomputation |
| Delivery | [[Designs/CC Reference/Delivery]] | `research.delivery`, report and manifest drafting plus host binding/checks |
| Shared enforcement | [[Designs/CC Reference/Shared Enforcement]] | compiler host, checks, binder, runner, gate, bridge and lifecycle |

## Reading the boundaries

The semantic reviewer receives the pinned declaration and exact subject output. It does not receive the producer's task inputs to redo the work. Input-dependent mechanical predicates live in the separate protected host checking path. This split is intentional and is preserved by the study design.

“One model call” below means a source-level worker call cap in the declaration or implementation. It does not prove an observed call, effective model, cost, or runtime acceptance. Reviewer calls have their own binding and budget. `benchmark` has no model call in its carrier. Source hashes and review coverage are in [[Resources/review-batches/2026-10-21-capsules/README]].

## Study boundary

The paired accuracy study is proposed and unrun: [[Experiments/CC Accuracy Study]]. Its development fixtures are separate from scorer keys, and held-out cases remain uncreated and custodian-controlled. The M1 code is not yet a validated study adapter. No results, comparative gains, held-out labels, or successful live execution are asserted.
