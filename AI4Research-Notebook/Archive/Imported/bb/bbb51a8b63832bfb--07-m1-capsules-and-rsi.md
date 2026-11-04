# M1 capsules and RSI

**Nodes own responsibilities. Subnodes bind pinned capability capsules (CCs).** Work CCs produce candidates. Verifier CCs assess. Protected gates accept/release.

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

Blue: records. Teal: execution/checks. Purple: protected control. Red: halt. Candidates/assessments stay inside the CC system. Additional work subnodes repeat this pattern before node release.

## Baseline capsules to build for M1

| Area            | Work CCs                      |
| --------------- | ----------------------------- |
| Compiler        | Intention, Requirements       |
| Ground/register | Search, Screening, Hypothesis |
| POC             | Builder, Benchmark            |
| Conclude        | Evaluation, Delivery          |

Pinned verifier assignment per work output. Nine distinct verifier implementations are not required. Build declarations, implementation pins and checking profiles together. Gates/binder/runner are infrastructure. [Phase 3 scope](../delivery-phases.md).

[Node detail](../m1-design.md#execution-and-model-routing) | [CC rules](../capsules.md) | [Authoring](../capsule/authoring.md)

## Build work and verification together

- Define inputs/outputs and acceptance criteria before judging implementation.
- Review actual candidates for fidelity, usefulness and reasonable conclusions.
- Check verifiers with good, bad and unclear cases. AI-built does not mean correct.
- Check connected subnodes before extending the path. Keep failures/reasons.

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

- Target 1, required: sandbox Screening `rank_opportunities`. 
- Target 2, conditional: permitted Screening prompt/work-rubric text. Dimensions/interfaces/referee stay fixed. Defer to M2 without bounded headless model support.
- Parallel development: prepare without a finished planner. Optimization needs eligible parent, meaningful fixtures and measurable headroom. Completion needs predecessor exits.
- Never mutate verifiers/referee, hidden fixtures, gate policy or activation. No automatic promotion. Future use requires admission and human activation.

[RSI protocol](../offline-rsi.md) | [M1 phases](../delivery-phases.md)
