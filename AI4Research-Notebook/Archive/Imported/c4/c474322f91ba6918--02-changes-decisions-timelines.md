# 2. Changes, decisions and timelines

**Key point:** A change in another part of the project should trigger a design impact review sized to what it changes.

## When the PRD changes

For a timeline-only adjustment, update the plan's target, forecast, dependencies and evidence assumptions. Update design only if a product obligation, architecture boundary, phase exit or required evidence changes.

For a new or expanded feature set, map each new outcome to affected components, interfaces, workflows, failure paths and acceptance evidence. Update the shared architecture where system connections or commitments change. Add focused design detail when the feature needs substantial, coherent explanation. See [how to grow the package](04-growing-design-package.md).

## Route a defect by what is wrong

| Finding | Design response |
|---|---|
| PRD outcome is wrong or contradictory | Trace the source and affected design. Resolve the product obligation, then update architecture and implementation work. |
| Design boundary or assumption is wrong | Correct the authoritative design, identify compatibility effects, update connected pages and recheck dependent evidence. |
| Code differs from accepted design | Keep the design as the expected behavior. Correct code and verify it against the design. Logs help diagnosis but do not establish correctness. |
| Code reveals a design flaw | Treat it as a design change. Update the authoritative behavior before dependent implementation proceeds. |

Preserve old decisions and run evidence. Mark evidence stale only where changed assumptions invalidate it. The [existing design rules](../design-method.md#route-defects-to-their-owner) define the full impact trace.

## Timeline and phase transitions

Architecture describes dependency order, phase exits and required evidence. The team plan and task records describe dates and forecasts. When a date moves, show which dependencies and evidence move with it. Consider resequencing, authorized scope change or a later target. Do not weaken acceptance evidence to meet a date.

At M1 close, carry accepted evidence, unfinished work, blockers, open decisions and changed assumptions into the M2 baseline. Update architecture when obligations, boundaries or phase exits change. A schedule-only change stays in the plan.

## Example: model access misses the M1 target

The model-routing component reports that credentials will be late. Architecture identifies which exits require live access. Keep the static path as baseline, mark live integration blocked, and update dependencies and forecast. Mock results are not live integration evidence. Independent work can continue if the PRD allows it. Change the product outcome or exit only through an explicit team decision.

This follows the [maintained timeline guidance](../design-method.md#timeline-and-phase-changes). It shows how architecture makes trade-offs visible without taking over the schedule.
