# 3. Package growth

**Keep one shared architecture with linked detail.** Update what the change affects.

## Package structure

| Area | Maintain |
|---|---|
| Shared core | Outcomes, system connections, authority and phase exits |
| Topic/feature pages | Component behavior, decisions, dependencies and failure paths |
| Reference | Canonical contracts, exact fields and connected examples |

- Small feature: update its existing topic and affected boundaries.
- Large feature set: update the system view and add linked feature detail.
- Each contract has one authoritative home. Focused coding packages link or pin required context and baseline.
- Summaries explain and link. They do not fork contract definitions.

## Work granularity

- Use one-shot work for a clear path that can be checked end to end.
- Use several PRs when independent changes help progress.
- Probe an uncertain boundary early. Split or combine later work when clarification, rework, review burden or integration failures show friction.

Choose locally. No fixed PR-size limit or extra approval stage. Preserve contracts and old evidence.

## Evidence for detail

Compare pinned PRD/design inputs at equal scope, matched model/settings and isolated contexts. Measure clarification, compatibility, failures, evidence and total effort. Intent-only results cannot establish full-M1 sufficiency. Frozen inputs stay immutable. [Trade-offs](../decision-review.md) remain traceable.
