# Skeptical review: research index and optional experiment (2026-10-07)

Scope: [README](README.md) and [optional-use-experiment.md](optional-use-experiment.md), checked against existing design/evidence notes; no new literature review.

The notes are appropriately framed as exploratory, not coding authority. They correctly say role separation does not prove statistical independence and keep the frozen condensed design from replacing the PRD/full design. Keep these boundaries.

Three small tightenings would prevent ambiguity:

1. **Gate role:** README says “A verifier supplies a verdict; the protected gate interprets accepted evidence.” This could imply the gate simply accepts the semantic verdict. Prefer: “Tier 1 must pass; Tier 2 returns grounded findings; the host validates subject/evidence identity and applies the profile’s fixed acceptance rule before release.”
2. **Outcome oracle:** “Independent” should mean separate from the tested verifier, not statistically independent. Require a pre-run reference from a qualified human or deterministic validator, blinded to treatment where feasible. Separate protocol conformance, task success, and scientific-validity labels; allow “indeterminate/disputed” outcomes. Define false advancement/block against the predeclared reference and profile rule.
3. **Causal controls:** In addition to fixed model/harness/environment/budget and repeated attempts, require paired tasks, randomized arm/order, fresh isolated contexts (to prevent feed carryover), fixed seeds/state where applicable, and retention of every run. Otherwise order or memory effects can masquerade as feed benefit. Treat curated procedure and experience as distinct contrasts; an irrelevant length-matched control alone does not isolate them.

“Do not score a verifier with its own verdict” is sound if the reference oracle is independent of both verdict and treatment selection. No unsupported literature requirement found; the condensed-design warning is sufficient.

Parent resolution: README now identifies host binding validation and frozen policy; the optional experiment brief now specifies pre-run human/deterministic references, blinded adjudication where feasible, distinct conformance/task/science outcomes including indeterminate, and paired/randomized runs with isolated contexts/reset state. These remain experimental controls, not added product requirements.
