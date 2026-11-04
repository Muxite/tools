# 3. Package growth

**Build on the existing design package.** Keep it as the foundation. Add small, linked pages for new features and link them from the package index.

## Package structure

- **New area:** append a focused design page with the context below.
- **Changed behavior:** update the affected existing definition and link the addition. Record what it replaces. Git preserves the earlier version.
- **Shared change:** update the shared contract or system view where needed. Each definition keeps one authoritative home.

### Each addition needs

| Include | Keep it simple |
|---|---|
| Purpose | What is added and why? |
| Builds on | Link the existing design package and revision used. |
| Affected design | Name the area, file or section. Quote the relevant rule or link to it. |
| Connections | State inputs, outputs and affected contracts or components. |
| Coding context | Link required definitions and examples. State expected behavior and how to check it. |

**Approximate impact is useful.** Mark uncertain links as suspected and say what needs checking. Future contributors and coding agents need a starting point, not invented precision.

## Work granularity

- Use one-shot work for a clear path that can be checked end to end.
- Use several PRs when independent changes help progress.
- Probe uncertain boundaries early. Split or combine later work when clarification, rework or integration failures show friction.

Choose locally. No fixed PR-size limit or extra approval stage. Preserve contracts and old evidence.

## Evidence for detail

Compare pinned PRD/design inputs at equal scope, matched model/settings and isolated contexts. Measure clarification, compatibility, failures, evidence and total effort. Intent-only results cannot establish full-M1 sufficiency. Frozen inputs stay immutable. [Trade-offs](../decision-review.md) remain traceable.
