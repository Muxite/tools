# Today: our design plan

**The proposed design is ready for implementation and review.** Reported full-package builds appear to produce the intended results and follow the design. We have not tested all execution branches, so overall quality is not established.

## First: review verification next week

- Check with people working on compiler and verification. Review AI-built verifier criteria, inputs, findings and gate behavior against the [verification design](../reference/compiler-verification.md).
- Prepare labelled unclear, actionable and failure cases. Review available results with contributors. Record false acceptance, false rejection and missing evidence.
- **Unclear intent:** a faithful candidate IR may exist. If no workable purpose/result can be established, the verifier must identify the gap and the gate must halt before Requirements. It must not invent intent or accept JSON just because it has valid fields.

## Build capsules throughout the work

Check with people working on each CC as it is built. Keep its design, checks and verifier assignment connected. Review actual outputs before connecting the next boundary. This lets verification expose missing context and unreasonable results early. [M1 capsules and RSI](07-m1-capsules-and-rsi.md) show the work split.

## Decisions still open

- **Compactness:** use full context for now. Both PRD and design changed in the comparison, so design length alone is not proven to explain the result.
- **Granularity:** add or remove detail where clarification, rework or boundary failures show a need. Compare total implementation and review effort.

Keep the existing package. Add linked feature detail. Correct affected definitions when findings justify it.

## Where we go next

```mermaid
flowchart LR
    P[/Current design package/] --> I[Inspect compiler evidence and failures]
    I --> H{What needs to change?}
    H -->|design| D[Linked design additions or corrections]
    H -->|code or checks| T
    H -->|unclear| U[Investigate affected work]
    U --> I
    D --> C[Bounded AI CI and targeted alerts]
    C --> T[Existing implementation records and coding work]
    T --> E[/New evidence for the next decision/]
    E --> I
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef human fill:#fff4d8,stroke:#b58100,color:#694b00
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class P,E record
    class I,D,C,T tool
    class H human
    class U unresolved
```

Blue: records. Teal: work/tools. Amber: human decision. Red: unresolved.

**Build overview:** complete the [Intention Compiler](../immediate-plan.md) through released `Research_Brief.json`, then the remaining [M1 research path](../m1-design.md). AI CI supports coordination under separate tooling scope.

[Our actions, targets and effort](08-build-and-review-sequence.md) | [Decisions](06-decisions-and-next-trial.md)
