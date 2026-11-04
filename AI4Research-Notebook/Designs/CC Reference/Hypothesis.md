---
id: m1-cc-hypothesis-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/hypothesis.py; research/checks/research.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Hypothesis

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

`research.hypothesis` converts the selected opportunity and Research Brief into one frozen experiment blueprint before code generation or measurement. It states claim/mechanism/independent variable, metric definitions, baseline identity, outcome rules, sample repetitions, seed, environment/resource refs, verification plan, and patch-scope constraints.

**Ports.** Inputs include brief, selected opportunity, baseline and validation resource records, and bound resource/environment context. Both resources must be available and share one prepared environment. Output is `hypothesis-blueprint`.

**Model and checks.** One text model call; no tools or network. Host validation checks schema, metrics/rules, disjoint success/falsification regions, baseline/validation identities, all Brief targets and constraints, resources/environment, frozen hashes, repetitions and seed ranges, and patch scope. Conditional outcomes are allowed only in registered middle regions. Post-hoc thresholds, invented measurements/dependencies, or changes to baseline, validation data, measurement functions, or outcome rules are disallowed.

**Failure and score.** Missing environment/resource or inconsistent baseline fails before measurement. Invalid rules, omitted constraints, overlapping success/falsification, or unenforceable scope are invalid output/check failure. Accuracy scoring compares every declared field to fixture facts and marks unsupported experimental claims as incorrect. A legitimate no-go/insufficient-resource result is an answer class only if the contract allows it; it is distinct from runtime failure.

**Isolation and evidence.** Candidate generation is read-only through the model bridge. It does not execute code or conduct trials. [[Designs/CC Reference/Source Map]] links the carrier, blueprint checks, asset registration, and focused tests. No measurement was performed for this reference.
