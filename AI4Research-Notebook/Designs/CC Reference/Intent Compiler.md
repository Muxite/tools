---
id: m1-cc-intent-compiler-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research_assets/compiler/intent.declaration.json; research/capsules/intent.py; research/checks/compiler.py; research/compiler.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Intent compiler

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

M1 implements a distinct `intent.compiler` capsule. Its job is to turn a qualified intake into an attributable `intent-ir` candidate: a structured interpretation of purpose, constraints, deliverables, evidence obligations, and uncertainty. Intent is not the final Research Brief and must not silently add Requirements policy.

**Ports and inputs.** Required input `request` is a `qualified-intake:field-contract:2`. Carrier reads the exact request text and source texts addressed by that intake, and may include an already-recorded plan outcome when present. Output `intent` is `urn:jiuwenswarm:m1-design:intent-ir:1.0.0`. The model receives the contract schema and common schema alongside the payload (`capsules/intent.py`).

**Obligations and enforcement.** The declaration caps the text model at one invocation, zero tool calls, 60 seconds, and no network. The carrier uses the audited bridge and shared strict JSON serializer. `intent_schema` is the output-shape guarantee. Protected compiler checks separately verify schema, source spans, exact identity, and run observations (`checks/compiler.py`, `compiler.py`). Request fidelity and downstream usability remain producer obligations supported by host checks; M1 does not claim that output-only semantic review can compare against unseen inputs.

**Failure and lifecycle.** Invalid serialization or missing call capability fails the attempt. Failed checks or a non-advancing verifier/gate do not commit the Intent; Requirements consumes only the actual accepted internal Intent. The fixed compiler has zero automatic retries; a candidate can be retained as evidence without being accepted. No autonomous clarification or web search loop exists.

**Isolation and effects.** Declared effect is read-only except bounded disclosure through the approved model bridge. Text only, no tools, network, or writable roots. The worker sees bound intake resources; it has no direct authority to change the request or policy. The separate reviewer sees declaration plus exact output only.

**Assessment.** The first accuracy fixture should check source-attributed meaning, preserved explicit constraints and deliverables, uncertainty rather than invention, and correct refusal/blocked readiness where the input cannot support a firm interpretation. Score producer correctness against an independent key over original request material. Separately challenge semantic reviewer false acceptance and false rejection using only the declaration/output pair; do not give the reviewer original intake as additional context.

**Evidence and limits.** [[Designs/CC Reference/Source Map]] links the carrier, declaration, prompt, host checks, orchestration, and focused test files. Source presence and unit tests are not evidence of a successful live model run or study adapter. Intent and Requirements are separate CCs inside one fixed host compiler node, not a single invented capsule.
