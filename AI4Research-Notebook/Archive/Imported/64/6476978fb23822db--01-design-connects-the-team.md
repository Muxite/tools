# 1. Design connections

**Design connects the SDLC:** requirements, design, implementation, verification and updates. SDLC means software development life cycle.

## Authority and reasoning

| Source | Defines |
|---|---|
| PRD | Product outcomes and obligations |
| Design | Boundaries, interfaces, authority and failures |
| Native specifications | Implementation and acceptance cases |
| Run evidence | What happened |

- Follow current design for implementation. Changed product obligations need a recorded, authorized decision.
- Separate requirements, decisions, assumptions and proposals. Cite sources. State unknowns.
- Decisions: question, alternatives, choice, reason, revisit signal. Preserve earlier decisions.

## Minimum design content

- Purpose, phase, approach, inputs/producers and outputs/consumers.
- Boundaries, permissions, dependencies, limits, failures/recovery.
- Checks, release conditions, evidence and rationale.

Define shared fields. Keep independent checking and protected durable release. [Principles](../principles.md) | [Contracts](../reference/README.md) | [Component obligations](../research-design.md#architectural-component-obligations).

## Example coordination flow

```mermaid
flowchart LR
    P[/Product requirements/] --> D[/Design and shared contracts/]
    M[/Component constraints/] --> D
    D --> I[Implementation work]
    I --> V[Verification work]
    V --> E[/Observed behavior and checks/]
    E --> H{Team diagnoses mismatch}
    H -->|code mismatch| I
    H -->|design gap| D
    H -->|verification problem| V
    H -->|unclear cause| U[Investigate with evidence]
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef human fill:#fff4d8,stroke:#b58100,color:#694b00
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class P,D,M,E record
    class I,V tool
    class H human
    class U unresolved
```

Blue: records. Teal: work/tools. Amber: human decisions. Red: unresolved.

Coordination decisions are separate from product gates.

**Inspired by [NASA systems engineering](https://www.nasa.gov/reference/systems-engineering-handbook/):** trace changes to reasons and impacts. Use a lighter process for our exploratory team.
