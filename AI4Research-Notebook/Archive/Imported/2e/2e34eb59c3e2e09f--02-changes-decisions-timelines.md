# 2. Changes and diagnosis

**Find the mismatch first.** Compare requirement, design, code and checks at their recorded revisions.

## Bugs and issues

```mermaid
flowchart TD
    E[/Bug report and reproduction/] --> H{Affected contributors diagnose}
    H -->|sound design, code differs| C[Code issue: fix implementation]
    H -->|code follows design, requirement unmet| D[Design issue: correct design and code]
    H -->|wrong check, fixture or environment| V[Fix verification or prerequisite]
    H -->|requirement disputed| P[Record requirement question]
    H -->|cause unknown| U[Investigate affected work]
    C --> R[Recheck affected behavior]
    D --> R
    V --> R
    P --> A{Agree requirement before product change}
    A --> H
    U --> H
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef human fill:#fff4d8,stroke:#b58100,color:#694b00
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class E record
    class C,D,V,R tool
    class H,A human
    class U,P unresolved
```

Blue: records. Teal: work/tools. Amber: human decisions. Red: unresolved.

- **Issue:** reproduction, expected/actual result, code commit, PRD revision, evidence, affected modules, next action.
- **Design link:** commit-pinned file and section/lines. Uncommitted draft: exact bytes/hash, labelled.
- **Notify:** affected implementation/check contributors. Include design for disputed meaning, requirements for disputed obligations. Link existing TASK/specification records.

## Change trace

- Trace producers/consumers, permissions, deployment, exports and evidence.
- Update definitions, versions/migration, summaries and diagrams.
- Preserve sources/runs. Mark affected evidence stale. Recheck.

## Timelines and phases

| Change | Response |
|---|---|
| Date only | Update planning. Distinguish target, forecast and estimate assumptions. |
| Scope, boundary or exit | Get affected contributors' agreement. Update affected design. |
| M1 to M2 | Carry evidence, unfinished work, blockers and changed assumptions. |

**Example:** late credentials. Resequence independent work or revise target. Mocks cannot meet a live-integration exit.

[Phase exits](../delivery-phases.md) | [Failure handling](../failure-and-human.md)
