# M1 capsules and parallel RSI work

**A node owns a responsibility. Its subnodes bind pinned capability capsules (CCs).** Work CCs produce candidates. Verifier CCs assess. Protected gates commit acceptance.

## Inside a node

```mermaid
flowchart TD
    I[/Accepted inputs or qualified compiler intake/] --> W
    P[/Pinned CC and execution contracts/] -.-> W
    subgraph N[Example governed node]
        subgraph Work[Work subnode: one bound CC]
            W[Work CC: produce candidate]
            W --> C[/Candidate output/]
        end
        C --> K[Deterministic checks]
        K -->|valid| V
        K -->|invalid or unavailable| G
        subgraph Verify[Verifier subnode: separately bound CC]
            V[Verifier CC: read-only]
            V --> A[/Assessment and reasons/]
        end
        A --> Q[Validate assessment and subject]
        Q --> G[Protected subnode gate: commit decision]
        G -->|accepted| F[Protected node finalization]
        G -->|not accepted| H[Halt: retain candidate evidence]
        F -->|failed or incomplete| H
    end
    F -->|durable release| O[/Released output to consumers/]
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef control fill:#f0e7ff,stroke:#7152a3,color:#45306a
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    style N fill:#f5f7fa,stroke:#64748b,color:#334155
    style Work fill:#f5f7fa,stroke:#64748b,color:#334155
    style Verify fill:#f5f7fa,stroke:#64748b,color:#334155
    class I,P,C,A,O record
    class W,K,V,Q tool
    class G,F control
    class H unresolved
```

Blue: records. Teal: execution/checking. Purple: protected control. Red: halt. Internal candidates and assessments are handled by the CC system, not external deliverables. Repeat this pattern for additional work subnodes before node release.

## Baseline capsules to build for M1

| Area | Work CC responsibilities |
|---|---|
| Current compiler build | Intention, Requirements |
| Ground and register | Search, Screening, Hypothesis |
| POC node | Builder, Benchmark |
| Conclude | Evaluation, Delivery |

Provide separately pinned verifier CC assignments for each work output. These are responsibilities, not a requirement for nine different verifier implementations. Build declarations, implementation pins and checking profiles together. Phase 3 integration responsibilities follow the [phase plan](../delivery-phases.md). Gates, binder and runner are protected infrastructure, not CCs.

[Node detail](../m1-design.md#execution-and-model-routing) | [CC rules](../capsules.md) | [Authoring](../capsule/authoring.md)

## Build work and verification together

- Define each CC's inputs, outputs and acceptance criteria before its implementation is judged.
- Build checks and verifier assignments alongside work CCs. Use actual candidates to assess fidelity, usefulness and reasonable conclusions.
- Test verifier behavior with labelled good, bad and unclear cases. A verifier is not automatically correct because an AI agent built it.
- Check connected subnodes before extending the path. Keep failures and reasons visible. Verifiers assess, gates release.

## RSI can prepare alongside product work

```mermaid
flowchart TD
    B[/Shared contracts, audited model access and evidence/] --> P[Build compiler and remaining product path]
    B --> R[Prepare RSI target profile, guards and fixtures]
    R --> E[Check parent, contract and measurable improvement]
    E -->|ready| S[Isolated RSI: propose and compare sandbox child]
    E -->|missing prerequisite| U[Block dependent optimization, continue independent work]
    S --> C[/Sandbox child and paired security/evaluation evidence/]
    P --> D[/Product acceptance evidence/]
    C --> M[/M1 exit accounting: both lanes and applicable integrations/]
    D --> M
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef control fill:#f0e7ff,stroke:#7152a3,color:#45306a
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class B,C,D,M record
    class P,R,E,S tool
    class U unresolved
```

- **Target 1, required:** Screening's pure `rank_opportunities` helper. Preserve sum-of-three scores, stable ascending-ID ties and Top-1. Improve only a sandbox copy. Live ranking stays unchanged in M1.
- **Target 2, conditional:** allowed Screening prompt/work-rubric text. Required dimensions, interfaces and verifier/referee stay fixed. Defer to M2 if bounded headless model support is unavailable.
- **Parallel means development:** prepare RSI without a finished planner. Optimization needs its own eligible parent and meaningful fixtures. Integrated completion still needs predecessor exits.
- **Freeze protection:** no edits to verifier, referee, hidden fixtures, gate policy or activation. No automatic promotion. Any future use needs admission and explicit human activation.

[RSI targets and protocol](../offline-rsi.md) | [M1 phases](../delivery-phases.md)
