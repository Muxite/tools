# Results assessment

## Candidate-specific evidence

| Label | Candidate and observation | What it supports | What it does not support |
|---|---|---|---|
| **[MEASURED SAMPLE]** | R07 ran six live-model cases on candidate `sha256:9227fcdb936e38b7261d39403e8f7d2daa487b3d8b54b7e0d136b2f96ed1e1a3`. All six labels matched: actionable and permissible omissions completed; topic-only, contradictory, unsupported-interpretation, and protected lost-constraint cases halted. The record reports zero observed false acceptances and zero observed false refusals. | A connected model-backed compiler path produced and durably released a Research Brief in the actionable sample, handled the omission sample, and halted the four negative samples as expected. The run includes live verifier challenge evidence. | Reliability, general semantic quality, PRD-wide acceptance, or performance guarantees. The record explicitly reports one repetition, uncontrolled provider variability, and possibly unavailable billing/served-model identity. Protected injected challenge outputs are not product outputs and cannot support admission. |
| **[MEASURED SAMPLE]** | The later R08 resource-only-reference-document run used candidate `sha256:4b33bcb6df44328b27be2fb24b819eb7a879c4715c757a5ae51297d72f484bad`. The product run actually completed and reported durable release of the exact Brief after four model calls; its outcome recorder marked the case `FAIL` because the independent verifier script raised `KeyError: 'invalid_for_product'`. The task record links separate authenticated no-replay and exact release/export checks. | A successful product outcome was observed for this specific resource-role case, and there is follow-up evidence intended to inspect exact release/export independently. | A clean end-to-end acceptance result until the independent checker discrepancy is reconciled and the required evidence is confirmed against the recorded candidate. Do not treat the checker exception as a demonstrated product defect or erase the failed outcome record. |
| **[IMPLEMENTATION EVIDENCE]** | The task matrix cites a final local suite result of 209 passed, zero skipped for candidate `4b33bcb6`, and records local API, state, runtime, and fault-path checks separately. | The implementation has meaningful deterministic and connected local test coverage; it is a useful source of reusable engineering patterns. | Browser interaction, actual Compose/Docker deployment, all M1 Capsules, or quality of every live semantic response. |

## Unverified acceptance

| Label | Requirement/evidence state |
|---|---|
| **[UNVERIFIED]** | T014 remains open. Browser visual/interactive inspection, submission journey, disconnect/reconnect, and interactive export/download behavior were not executed. AC-019 retains this limitation. |
| **[UNVERIFIED]** | The Docker/Compose runtime check was blocked because Docker was unavailable. T015 records the prerequisite blocker; AC-020 remains blocked. Static packaging and local tests are not deployment evidence. |
| **[UNVERIFIED]** | The complete M1 Phase 1 end-to-end research journey, Phase 2 RSI, and Phase 3 integrations are outside the M0-001 compiler-only scope and are not established by this branch. |
| **[UNVERIFIED]** | Six semantic cases at one repetition each do not establish repeatability or a population quality rate. There is no numeric quality threshold that can be inferred from these records. |

## Reconciliation notes

- **[IMPLEMENTATION EVIDENCE]** R07 and R08 are different candidates and experiments. R07’s six-case result must not be attached to R08’s candidate; R08’s actual completion must not replace R07’s six-case results.
- **[IMPLEMENTATION EVIDENCE]** The task matrix is more current and nuanced than the initial R06 record: it distinguishes the R07 sample, the R08 follow-up, current local candidate checks, and blocked browser/container checks. Use the task matrix plus the underlying run records rather than an earlier summarized result.
- **[OPEN QUESTION]** Inspect the R08 verifier implementation and exact independent release/export records; determine whether the case-result `FAIL` is solely an evidence-checker defect, then rerun the affected check against immutable candidate `4b33bcb6` evidence if the required environment is available. Any rerun is a new observation; retain the original record.
- **[RECOMMENDATION]** Keep four outcome labels separate in future summaries: `product run outcome`, `evidence verifier outcome`, `local automated checks`, and `environmental proof status`.
