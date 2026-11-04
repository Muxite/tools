# 6. Decisions

**Use evidence. Get agreement for shared changes.**

| Decision | Starting point | Revisit signal |
|---|---|---|
| Verifier quality | Review code and labelled cases next week. | Wrong acceptance/refusal, missing findings |
| Compactness | Full package with focused links. Append new areas. | Matched trials preserve correctness with less context/effort |
| Granularity | Clear contracts. Detail where needed. | Clarification, rework, failed integration |
| AI CI scope/cost | Scripts, one bounded worker, advisory findings. Agree budget. | Saved effort, misses or noise |
| Runner/sidecar | Separate tooling scope once interfaces/permissions are ready. | Missing evidence needs another registered tool/case |
| Notifications | Git contact map. Agree routing/triage. | Missed recipients, stale contacts, excessive pings |

## If the plan is wrong

- Bad AI finding: record counterexample. Correct skill/rule/fixture. Recheck.
- Missed design impact: update affected definition/context. Add regression example.
- Broken code: use [diagnosis flow](02-changes-decisions-timelines.md#bugs-and-issues). Change design only when wrong/incomplete.
- Delay: resequence work or agree changed scope/target. Preserve exits and evidence gaps.

Existing issue/PR or design decision: question, choice, reason, revisit signal, revisions/evidence. No new approval layer.
