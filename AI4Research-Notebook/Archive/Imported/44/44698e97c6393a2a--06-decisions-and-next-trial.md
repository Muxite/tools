# 6. Decisions for the next trial

**Choose a small trial we can evaluate.** Architecture proposes boundaries and impact. Affected contributors agree shared changes.

| Decision needed | Suggested starting point | Revisit when |
|---|---|---|
| Which context to give coding agents? | Full package baseline with focused links. Append new areas. | Matched trials show less context preserves correctness and lowers total effort. |
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
