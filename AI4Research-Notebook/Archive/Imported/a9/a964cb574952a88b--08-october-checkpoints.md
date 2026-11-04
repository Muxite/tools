# Design checkpoints through October 31

**Proposed review checkpoints, not completion promises.** Review evidence at each checkpoint. Adjust dependent work when prerequisites or findings change.

| Dates, 2026 | Design work | Checkpoint result |
|---|---|---|
| Oct 9â€“12 | Agree current compiler boundary, CC responsibilities and open decisions. | Linked baseline and affected areas. [Node/CC view](07-m1-capsules-and-rsi.md#inside-a-node). |
| Oct 13â€“18 | Review available compiler bundles, Brief quality and failure cases. | Verified findings or explicit evidence gaps. [Diagnosis flow](02-changes-decisions-timelines.md#bugs-and-issues). |
| Oct 19â€“24 | Add focused corrections. Trial cheap document checks and bounded agent review within agreed scope. | Changed design links, review findings and cost/noise observations. [AI CI flow](05-coordination-support.md#proposed-notification-flow). |
| Oct 25â€“28 | Review runner/sidecar readiness and RSI prerequisites alongside product work. | Useful evidence where ready. Missing interfaces/fixtures stay recorded. [Tooling boundary](05-coordination-support.md#runner-and-sidecar-in-ai-ci), [RSI parallel work](07-m1-capsules-and-rsi.md#rsi-can-prepare-alongside-product-work). |
| Oct 29â€“31 | Consolidate current design and choose the next work. | Accepted evidence, unresolved issues, revised priorities and next-phase dependencies. |

## Does the schedule require a design change?

| Situation | Response |
|---|---|
| Dates slip, behavior stays valid | Update planning or work order. Keep design. |
| Complexity slows delivery | Simplify implementation within existing contracts. Revise design if boundaries or behavior change. |
| Required scope or exit must change | Agree the requirement change, then update affected design and tasks. |
| Work finishes early | Use time for verification or the next agreed work. No automatic scope expansion. |

Record the reason and notify affected contributors. Link changed design sections. Recheck affected evidence. **Schedule pressure alone does not remove required checks.**

Use existing issues/PRs and TASK records. Keep required exits intact. These checkpoints do not claim full M1 completion or require tooling deployment.
