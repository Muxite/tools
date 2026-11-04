# Build and review sequence

**Review evidence as each boundary becomes usable.** Capsule building, verifier development and design review continue throughout the build.

| When | Design work | Evidence or next decision |
|---|---|---|
| Next week | Review recent AI-built compiler verifiers. Test unclear intent and other execution branches. | Correct assessments, gate behavior, false acceptances/refusals and remaining gaps. [Verification cases](../reference/compiler-verification.md#cases-and-evidence). |
| With each work CC | Build its declaration, checks and verifier assignment alongside implementation. | Candidate output, assessment and gate decision. [Node/CC view](07-m1-capsules-and-rsi.md#inside-a-node). |
| Before connecting boundaries | Review inputs/outputs and run connected cases. | Compatible contracts and inspectable integration evidence. |
| As findings arrive | Correct design, code or verification. Revisit compactness and detail where needed. | Linked revisions and affected checks. [Diagnosis flow](02-changes-decisions-timelines.md#bugs-and-issues). |
| As prerequisites become ready | Prepare RSI in parallel. Trial useful AI CI and separately scoped runner/sidecar tools. | Attributable results and visible gaps. [RSI](07-m1-capsules-and-rsi.md#rsi-can-prepare-alongside-product-work), [tooling](05-coordination-support.md#runner-and-sidecar-in-ai-ci). |

## Does progress require a design change?

| Situation | Response |
|---|---|
| Work is late but expected behavior remains valid | Resequence work or revise planning. Keep design. |
| Missing context or a bad design assumption causes rework | Correct affected design and tasks. Recheck. |
| Code or verification is wrong | Fix that layer. Use evidence before changing design. |
| Required scope or exit changes | Agree the requirement change, then update design. |

Keep required checks, accepted artifacts and active-run pins intact. Use existing issues/PRs and TASK records. Notify affected contributors.
