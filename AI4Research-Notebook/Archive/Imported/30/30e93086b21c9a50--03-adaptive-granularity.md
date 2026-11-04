# 3. Package growth

**Keep the existing package. Append linked feature detail.**

## Package structure

```mermaid
flowchart TD
    N[/New requirement or feature/] --> H{Which design changes?}
    H -->|new area| A[Add focused design page]
    H -->|existing behavior| B[Revise affected definition]
    H -->|shared boundary| C[Update shared contract and consumers]
    A --> L[/Existing package plus linked additions/]
    B --> L
    C --> L
    L --> T[Update existing TASK and specification records]
    T --> I[Coding agents implement and verify]
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef human fill:#fff4d8,stroke:#b58100,color:#694b00
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class N,L record
    class A,B,C,T,I tool
    class H human
```

Blue: records. Teal: work/tools. Amber: human decisions. Red: unresolved.

| Addition needs | Include |
|---|---|
| Purpose | Change and reason |
| Foundation | Package/revision and required context |
| Impact | Area/file/section. Quote or link design. Mark suspected impacts. |
| Boundaries | Inputs, outputs, components/contracts |
| Completion | Expected behavior, examples, checks |

Changes may follow several paths. Link from index. Keep one authoritative definition. Record replacements. Git retains history.

## Work granularity

- One-shot: clear path, end-to-end check.
- Several PRs: useful independent changes. Check uncertain boundaries early.
- Split/combine when clarification, rework or integration failures show a need. No fixed size rule or extra approval stage.

## Evidence for detail

Compare equal scope, pinned PRD/design, matched models/settings, isolated contexts. Measure failures, clarification and total effort. Intent-only results cannot establish full-M1 sufficiency. Preserve frozen inputs and [trade-offs](../decision-review.md).
