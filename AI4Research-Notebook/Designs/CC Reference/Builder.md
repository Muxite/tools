---
id: m1-cc-builder-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/builder.py; research/checks/research.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Builder

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate. [[Activities/2026-10-23 Builder Upgrade]] records a separate candidate with bounded build/test/repair; it is not shared M1 or runtime-qualified by this note. Keep that candidate distinct from the historical no-execution contract below.

`research.builder` implements exactly the frozen intervention in an assigned workspace. This is a governed coding job, not a general shell-enabled CC. The dedicated Builder path supplies the model callback; the carrier later retrieves exactly three files and packages them deterministically.

**Inputs and outputs.** Inputs include accepted blueprint, baseline and validation data, measurement functions, frozen environment lock, and Builder workspace contract. It must emit `requirements.txt`, `poc_patch.py`, and `run_benchmark.py`, then host returns a manifest and zip bundle with pinned refs/dependencies and receipt.

**Limits and authority.** One governed model call; no model tools, network, package installation, dependency discovery, trial execution, or credential access. Code cannot change baseline, validation data, measurement functions, or outcome rules. Static host inspection checks exact file set, pinned dependencies, syntax/AST, prohibited modules and dynamic execution, registered metric IDs, and one JSON metrics line. No generated execution occurs during Builder validation.

**Failure and lifecycle.** Missing executor, missing/extra files, syntax or AST violation, unpinned dependency, prohibited import, wrong output contract, or unavailable workspace fails the attempt; preserve receipt and failure reason. READY means static build checks passed, not that benchmark behavior or scientific correctness is proven. Benchmark requires the exact accepted READY receipt and matching artifact refs.

**Study challenge.** Use safe, tiny source fixtures with independent executable tests for required behavior, preservation and edge cases. Score test pass rate and critical invariant violations; static validity alone is not correctness. Separate model-produced code error from executor failure, timeout, and packaging failure. Never run an artifact before capturing and checking its immutable inputs.

**Evidence.** [[Designs/CC Reference/Source Map]] links the carrier, bundle inspection, environment checks, and focused test files. Container/runtime acceptance is not established by the source audit.
