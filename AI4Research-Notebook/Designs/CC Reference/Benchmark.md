---
id: m1-cc-benchmark-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/benchmark.py; research/science.py; research/checks/research.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Benchmark

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

`research.benchmark` is a deterministic host orchestration capsule. It makes no model call. It provisions the frozen environment, captures hardware inventory, runs baseline first and then treatment for each frozen repeat/seed, captures actual receipts/stdout/stderr, parses metric rows, and calculates paired empirical payload values.

**Inputs and outputs.** Inputs are the exact accepted blueprint, READY build receipt, POC manifest and bundle, lock, resources, configuration, and executor capability. Outputs are `benchmark_payload`, `execution_receipt`, and `provisioning_receipt`. Each measurement row binds sequence, role, repeat index, seed, subject artifact, hardware identity, exit/termination and captured output refs.

**Hard boundary.** Benchmark verifies the build receipt and ref identity before provisioning. Baseline failure halts before treatment. It does not infer platform compatibility from a label; root provisioner separately qualifies the actual platform. Execution, package setup, hardware access and resource limits belong to protected executor services.

**Failure and checks.** Provisioning failure, receipt mismatch, baseline failure, timeout/nonzero exit, malformed/nonfinite/missing metric output, sequence gaps, resource mismatch, or invalid arithmetic are distinct failures. Actual failed attempts and empirical rows are retained. `validate_benchmark` and stage checks independently validate receipt binding, order, repeats, environment, raw evidence, and computed values. Null metric fields need explicit missing reasons; they are never zero.

**Study implications.** Benchmark itself is not a model-vs-CC task for this accuracy pilot. Use synthetic receipt/evidence fixtures to test arithmetic and failure accounting, or report benchmark as the shared model-free control. Do not claim performance improvement without real pinned hardware and actual measurements.

**Evidence.** [[Designs/CC Reference/Source Map]] links the carrier, metric arithmetic, executor boundary, protected checks, and focused test files. No benchmark ran in this audit.
