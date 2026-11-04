---
id: cc-v2-07-quality-and-improvement
status: v2-reference-implementation
source: November 4 CC v2 revision
last_reviewed: 2026-11-04
next_action: Qualify selected adapter and consumer evidence policy
---
# Quality and improvement

The baseline is useful identity, input/output validation, explicit effects, bounded execution and honest durable receipts. Keep JSON broad unless stronger schema prevents a meaningful error. Consumer policy sets use-case evidence thresholds.

| Claim | Required evidence |
|---|---|
| Package validates | Actual validation. |
| Call succeeded | Adapter execution and valid outputs. |
| Guarantee passed | Supported check, exact subject/scope and evidence. |
| Method useful | Appropriate scientific evaluation. |
| Product qualified | Consumer-specific environment and acceptance. |
| Product improved | Comparable baseline/candidate under frozen policy. |

Empty checks mean `not_requested`. Self-tests, external evaluation and promotion differ. Unsupported guarantees block rather than disappear. Native trusted-local provides no isolation proof; see [03](03-calls-and-receipts.md).

An improvement loop proposes changes, fixes source identity, builds/seals, evaluates protected criteria, then promotes or rejects. Preserve negative results and interruptions. Evaluator changes are separately reviewed and cannot quietly make their own candidate pass.

For MAPIE, nominal interval coverage is a target, not proof every dataset attains it. Record data splits, method/version, randomness, observed coverage and width. Predictive-method evidence differs from protocol conformance. [05](05-examples-and-conformance.md) records runnable examples and evidence.
