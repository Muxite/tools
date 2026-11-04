**Muk, 2026-09-23: capsules — degenerate and composite alike — must be shown to fit the criteria, to
function, and to be of good quality *often enough*. That is a verification task CC has to support, and
the schema has to supply what it needs.**

"Often enough" is a distributional claim, and nothing in a per-run check produces one. Treating
verification as correctness alone was the gap.

## Three layers, not one

| Layer | Question | Shape of the answer | Fed by |
|---|---|---|---|
| **Conformance** | Is it what it says it is? | binary, static + first run | `identity.body[].sha256`, declared ports, `changes.effects[]` compared against observed; the ten static checks in [[Symphony Flow]] |
| **Correctness** | Does it do its job on cases it has not seen? | binary per case | `guarantees.checks[]`, held-out suites, `ports.outputs[].check` |
| **Quality** | Is it good **often enough**, over time? | **a rate over a window, never a verdict** | `guarantees.acceptance` and `evals[]`, a named judge with its own Standing, and Standing carrying the running rate |

## What the schema must supply that it does not yet make explicit

- **A declared quality criterion per output**, separate from its correctness check — a rubric or judge
  plus a target, so "good" has a stated meaning instead of being inferred after the fact.
- **A minimum observation count before a quality claim means anything.** This is where expensive sprints
  bite hardest: with tens of observations a rate is mostly noise. The declaration should say how many
  runs its quality claim needs; until then the claim is labelled **unmeasured**, never silently treated
  as passing.
- **A named judge, with the judge's own calibration recorded.** Non-deterministic outputs can only be
  judged, so the judge's reliability is part of the evidence. Calibrated by spot checks —
  `GoalEvaluator.should_spot_check()` already exists in agent-core. **Judges are never capsules**
  ([[The Ceiling]]).
- **Standing carries the distribution, not a pass/fail.** It is already "a moving pointer, every move
  logged"; make explicit that what moves is a quality rate over a window.
- **Block for safety, label for quality.** v2.8's rule, and it stays prominent. A capsule of mediocre
  quality still runs, visibly marked; it is not silently excluded. This is what keeps CC from stopping
  AI4Research reaching its goals.

## Why this is what makes the thesis true

> A 能力胶囊 is **flexible in form and strict in verification and quality assurance.**

Flexibility of form is what makes adoption cheap; strictness of verification is what makes flexibility
safe. A capsule can *represent the verification of a task* — which matters most for non-deterministic
tasks, where the output can only be judged rather than checked.

## Consequence for merging

A block's quality is not the product of its members' qualities and cannot be inferred from them. Hence
the asymmetry in [[Overlap and Merge]]: failing parts never merge, but passing parts do not make a
passing block — it earns its own record.

Related: [[Declared vs Observed]], [[Milestone Ladder]] (quality activates at M3), [[Self-Improvement]].
