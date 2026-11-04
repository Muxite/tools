# 6. Decisions for the next trial

**Choose a small trial we can evaluate.** We propose boundaries and impact, then check with people working on affected areas before recording shared changes.

| Decision needed | Suggested starting point | Revisit when |
|---|---|---|
| Can we trust the current verifier behavior? | Review recent verifiers and test labelled valid, invalid and unclear inputs next week. | False acceptance, false rejection or missing findings. |
| Which context to give coding agents? | Full package baseline with focused links. Append new areas. | Matched trials show less context preserves correctness and lowers total effort. |
| How much detail per change? | Keep shared contracts clear. Add focused explanations where agents need context. | Repeated clarification, rework or failed integration. |
| What does AI CI check first? | Paths/links/names, then clarity and change impact. Agent findings are advisory. | Measured misses or noise justify stronger or fewer checks. |
| How much automation effort? | One bounded worker. Agree time/cost budget before implementation. | Saved review/rework effort outweighs running and maintaining it. |
| When use runner/sidecar? | Separately scoped tooling after client interfaces and permissions are ready. | Missing evidence requires an additional registered tool or case. |
| Who receives action alerts? | Affected contacts from Git mapping. Agree routing and triage destination. | Missed recipients, stale mapping or excessive pings. |

## If the plan is wrong

- **Bad AI finding:** record the counterexample. Correct the skill, rule or fixture. Recheck.
- **Missed design impact:** update the affected definition and linked context. Add a regression example.
- **Broken implementation:** use the [diagnosis flow](02-changes-decisions-timelines.md#bugs-and-issues). Design changes only when its meaning is wrong or incomplete.
- **Schedule pressure:** resequence independent work or agree a scope/target change. Preserve required exits and label missing evidence.

Record question, choice, reason and revisit signal in the existing issue/PR or design decision. Link revisions and evidence. No new approval layer.
