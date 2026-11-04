---
id: m1-cc-requirements-compiler-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research_assets/compiler/requirements.declaration.json; research/capsules/requirements.py; research/checks/compiler.py; research/compiler.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Requirements compiler

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

`requirements.compiler` turns an already accepted Intent and qualified intake into a source-attributed M1 Research Brief. M1 deliberately separates this from Intent: the first worker interprets; this one links requirements to acceptance and evidence, applies only protected defaults, and creates the Brief consumed by downstream research.

**Ports and inputs.** Required inputs: `intent` (`intent-ir`), `intake` (`qualified-intake:field-contract:2`), and `defaults` (`default-policy:field-contract:1`). The carrier reads the accepted request and supplied source texts, binds exact input refs, and supplies Research Brief and common schemas. Required output `brief` is `research-brief:2.0.0` (`capsules/requirements.py`).

**Obligations and checks.** The declaration allows one text model invocation, no tools, no network, 60 seconds. `brief_schema` covers exact output structure. Protected checks verify schema, source identity, and requirement coverage; the composite node only passes the actually committed Intent into Requirements (`checks/compiler.py`, `compiler.py`). Development scoring should check every mandatory user requirement, acceptance condition and evidence link, exact attribution, all deliverables, and the absence of invented requirements or policy. Keep default attribution distinct from user-specified content.

**Failure and lifecycle.** Requirements cannot run on an unaccepted Intent. Missing/corrupt accepted references, schema errors, check failures, verifier failures, or budget exhaustion prevent Brief acceptance and propagate a node failure/halt. Automatic retries are set to zero for the fixed compiler. An accepted Brief is the downstream boundary, not an editable suggestion.

**Isolation and reviewer boundary.** Read-only candidate generation through the governed model bridge, text only and no network/tools. Host checks may compare the Brief to bound intake and accepted Intent. The semantic reviewer remains limited to pinned declaration and exact Brief output; original intake is scorer/host material and is not passed to the semantic reviewer.

**Test design.** Include fully answerable, conflicting, missing, and defaultable requests. A correct output must preserve explicit constraints and cite exact sources; a false inclusion should fail accuracy even if the JSON is well formed. Include wrong-but-structural output pairs in the verifier/gate suite, and valid output pairs to measure false rejection. Report semantic decision separately from deterministic host checks.

**Evidence and limits.** [[Designs/CC Reference/Source Map]] links the carrier, declaration, prompt, host checks, orchestration, and focused test files. Runtime readiness remains unproven. This reference does not substitute a generic pilot adapter for the actual port contract.
