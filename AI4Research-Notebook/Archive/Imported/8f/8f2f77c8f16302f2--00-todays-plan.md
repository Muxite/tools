# Today: design plan

**Design is ready to build and review.** Reported full builds appear to follow it. Untested branches and verifier quality remain open.

## First: review verification next week

- Receive generated code/logs. Compare verifier criteria, context, findings and gates with [design](../reference/compiler-verification.md).
- Prepare labelled cases. Get agreement on disputed expectations. Record wrong decisions and missing evidence.
- Unclear intent may yield a faithful candidate IR. Without workable purpose/result, the gate must halt before Requirements. No invented intent. Valid JSON is insufficient.

## Build capsules throughout the work

Review each CC's design, checks, verifier and actual output before connecting the next boundary. [M1 work split](07-m1-capsules-and-rsi.md).

## Decisions still open

- Compactness: use full context now. Both PRD/design changed in the comparison. Cause remains unproven.
- Granularity: adjust detail from clarification, rework, boundary failures and total effort.

Keep the existing package. Append linked detail. Correct affected definitions.

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

Blue: records. Teal: work. Amber: human decision. Red: unresolved.

**Build:** [compiler](../immediate-plan.md) through released `Research_Brief.json`, then remaining [M1 path](../m1-design.md). AI CI has separate tooling scope.

[My checklist and risks](08-build-and-review-sequence.md) | [Decisions](06-decisions-and-next-trial.md)
