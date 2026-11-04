---
id: m1-cc-shared-enforcement-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/compiler.py; research/runner.py; research/gate.py; research/checks/stages.py; research/library.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Shared compiler, checks, gates, and lifecycle

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

## Actual combined roles

The fixed Intention Compiler is a host node containing two distinct worker CCs: `intent.compiler` followed by `requirements.compiler`. It has no third standalone “compiler CC.” The Planner is a separate optional proposal capsule in planned runs; static authored graphs also exist. `research.verifier` is a role bound per work output, not an extra producer stage and not a task-specific answer key. Benchmark execution is a capsule carrier backed by protected host executor services, not a model agent.

## Producer and reviewer separation

Worker output is first captured exactly. Deterministic checks can bind typed inputs and runtime observations. The semantic verifier is a separate fresh subnode whose model-facing material is limited to the exact registered declaration and output. The protected gate combines mandatory checks, verifier assessment, output refs, and lifecycle state. Only an advancing gate commits output for downstream use. Failed, blocked, inconclusive, or environment-unavailable outcomes must remain visible.

## Effects, isolation, and budget

The Library binds exact declaration/body/check/profile pins and standing. Binder freezes plan, resources, effects, ports, required stages, authority and aggregate budget. Capsule declarations describe candidate needs; the parent policy constrains actual authority. The audited bridge captures model-call identity/usage where observed and has a fixed Codex route by default with governed provider routes available under configuration. Tests must freeze effective model/route across arms and charge worker and verifier calls to a common total task cap. Null usage stays unavailable.

Per-CC containerization is a separate deployment design decision from whole-lab isolation. Builder-generated code and measurement jobs warrant stronger confinement than a bounded read-only model-only worker. A container per CC alone does not isolate a lab with shared secrets, writable mounts, unrestricted egress, or a privileged daemon. See [[Designs/cc-containerization-and-lab-isolation]].

## Study and acceptance evidence

The source/test repository can establish declared interfaces and local mechanics; it does not establish live model route, native runtime acceptance, adapter fidelity, or accuracy. Preserve exact source pins and test references in the study ledger. Use false-acceptance/false-rejection challenge cases at producer, semantic reviewer, deterministic gate, and final decision layers. Mandatory checking profiles are fixed in every study arm; optional planner-selected gates can only add eligible checks, never replace mandatory ones.

[[Designs/CC Reference/Source Map]] links the compiler host, runner, gate, check modules, binder, library and focused tests. The per-file hashes for audited sources are listed in the review batch.
