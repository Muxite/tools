# 3. Choose and adjust work granularity

**Key point:** Vary explanation depth and implementation batch size to fit risk. Keep accepted contracts and evidence stable while adjusting future work.

## Separate design depth from PR size

These are related but different choices:

- **Design depth** is how much intent, boundary, behavior, failure handling and evidence the team must make explicit before work.
- **Work granularity** is whether implementation is delivered as one cohesive change or a series of reviewable PRs.

Use more design detail when uncertainty, cross-component coupling, irreversibility or failure cost is high. Use less explanation for a local, reversible change whose contract is already clear. A short document does not imply a small PR, and many PRs do not automatically mean the design is clear.

## Choose the work shape

| Work shape | Fits when | Protect with |
|---|---|---|
| One-shot vertical change | The path is cohesive, interfaces are known and the result can be verified end to end | Clear scope, frozen shared contracts and complete acceptance evidence |
| Several PRs | Slices can be understood, reviewed and checked independently, or parallel work helps | Explicit producer/consumer contract, dependency order and integration evidence |
| Small probe, then implementation | A boundary or assumption is uncertain and cheap to test | A narrow question, observable result and decision about what follows |

Do not split tightly coupled behavior just to meet a fixed PR-size rule. Do not deliver a large one-shot change when early interface evidence could reduce uncertainty.

## Notice friction and adjust the next slice

Track a few signals in ordinary work rather than creating a new dashboard:

- Repeated clarification or rework around the same missing design detail
- Cross-PR integration failures or consumer assumptions that do not match
- Review taking too long because a change mixes unrelated responsibilities
- Evidence becoming stale because work changed a contract or assumption

Repeated clarification suggests adding the missing design detail before the next slice. Integration failures suggest validating the shared interface with a small producer-consumer path before parallelizing. Review overload suggests separating independent concerns. If splitting creates more coordination than it saves, combine the tightly coupled pieces behind one explicit contract.

These are proposed signals, not established numeric thresholds. Start with a short sample and adjust the next increment, not accepted history. Keep contract versions, gate authority and evidence identities explicit. When an interface itself changes, update its authoritative definition, identify affected consumers, and repeat only the checks whose assumptions changed. The [design method](../design-method.md#change-and-knock-on-effects) defines the existing change trace.

## Example: an assumption fails across PRs

Stop dependent changes when the first contract test or consumer check shows the shared assumption is wrong. Determine whether code diverged from a correct design or the design was incorrect. Fix code in the first case. In the second, agree and update the design contract before dependent implementation resumes. Preserve prior PR and test evidence, mark affected evidence stale, and validate the corrected boundary with a small connected path. Then choose whether later work remains split or should be bundled.

The October 8 full/compact comparison is one data point, not a universal granularity rule. The reviewed full-document results were close, while the compact outputs still needed debugging. Continue comparisons on matched inputs and measure verified behavior, clarification, rework and review effort before selecting a default.
