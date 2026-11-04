---
id: m1-cc-screening-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/screening.py; research/capsules/ranking.py; research/checks/research.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Screening

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

M1 `research.screening` is one capsule whose model assessment is followed by a pinned pure ranking helper. The helper is not an additional autonomous CC. The model normalizes near-duplicates while preserving every input identity and scores novelty, feasibility, and compute alignment; trusted helper performs eligibility/ranking/selection under exact rules.

**Inputs and outputs.** Inputs are candidate set, screening rubric, and Research Brief. Outputs are `screening_result` and `opportunity_card`. Each source idea must retain its ID, citations, and material variant in the score record. The output includes score dimensions, total, reasons, dependency flags, eligibility/disposition, rank, selected ID, and explanation.

**Limits and effects.** One bounded text model call; no tools or direct network. A pinned helper/prompt must be inside admitted implementation/dependency closure. Ranking orders eligible ideas by descending total, then ascending ID. No eligible candidate is an explicit failure/non-selection, not an arbitrary Top1.

**Checks and failure.** Host validation checks exact candidate coverage, unique IDs, dimensions/ranges/sums/citation IDs, dependency flags/dispositions, deterministic ranking and selected opportunity consistency. Model judgments remain subjective; deterministic tie correctness is not evidence novelty is true. Failed helper pin, malformed/incomplete scores, invented citation, non-deterministic winner, or no eligible idea is recorded distinctly.

**Study score.** Measure (a) deterministic consistency against a scriptable ranking oracle, (b) selection quality against frozen domain labels, (c) unsupported rationale/citation errors, and (d) correct non-selection/abstention. Separate wrong Top1, wrong ranking, false eligible, and operational failures. A structurally valid but poor subjective score can be a wrong answer even if ranking arithmetic passes.

**Evidence.** [[Designs/CC Reference/Source Map]] links the carrier, ranker, check wiring, and focused test files. No live case results are asserted.
