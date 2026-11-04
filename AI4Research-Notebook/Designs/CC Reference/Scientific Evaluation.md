---
id: m1-cc-scientific-evaluation-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/evaluation.py; research/checks/research.py; research/gate.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Scientific Evaluation

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

`research.evaluation` drafts one `evaluation-verdict` from a frozen hypothesis blueprint and accepted benchmark payload. It copies metric values and registered rules into an assessment, classifies each metric as PASS, FAIL, CONDITIONALLY_ACCEPTABLE, or INCONCLUSIVE under fixed outcome rules, and summarizes completeness/plausibility. It does not run experiments, change thresholds, add metrics, or trigger follow-up suggestions.

**Inputs and output.** Inputs include blueprint, accepted payload, registered rules, and exact refs. Output `evaluation_verdict` includes one ordered finding per metric, rule text, values, class, blockers, risks, follow-ups and overall classification. Valid scientific FAIL and INCONCLUSIVE are deliverable conclusions, not pipeline failures.

**Two distinct accuracy boundaries.** Worker produces a candidate verdict with one text model call. Protected deterministic host code recomputes per-metric and overall classification from frozen rules and values (`checks/research.py:validate_scientific_verdict`); a separate semantic verifier receives the pinned declaration and exact output only. Do not give semantic review the underlying inputs. The deterministic host is allowed to use the bound blueprint/payload as its typed rule oracle. Score worker correctness, semantic reviewer decisions, mechanical checks and final gate separately.

**Challenge matrix.** Freeze values/rules for valid PASS, scientific FAIL, missing-value INCONCLUSIVE, registered conditional middle, implausible outcome, multi-metric precedence, and planted wrong threshold/classification. Include a fully correct verdict that gets wrongly rejected and a structurally valid wrong verdict that is wrongly accepted. For each sample record expected worker class, semantic review verdict from declaration/output only, host predicate result, final gate action and reasons. False acceptance means incorrect artifact advances; false rejection means correct artifact is blocked. A verifier timeout is operational failure and never counted as either semantic disagreement.

**Model and boundary.** One text model call; no model tools or external experiment. No automatic correction loop. If model outputs a wrong class, mechanical check must stop release. The pipeline can still report the legitimate scientific result `FAIL` or `INCONCLUSIVE`.

**Evidence.** [[Designs/CC Reference/Source Map]] links the carrier, rule engine, verdict check, gate, and focused test files. These fixtures/tests do not establish blinded challenge accuracy or a completed M1 run.
