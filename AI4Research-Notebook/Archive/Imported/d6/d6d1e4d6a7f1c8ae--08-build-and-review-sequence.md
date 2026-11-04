# My architecture plan toward M1

**Priority: evidence, verifier quality and implementation blockers.** Design is ready. Overall build quality remains unproven.

## SMART review targets

| When | My action | Result |
|---|---|---|
| Before next week's review | Receive four builds' code/logs. | Build/version inventory. Missing files listed. |
| Next week | Review both compiler verifiers in available full builds. | Criteria, reasons and gate findings with code/evidence links. |
| By next week's end | Prepare clear, unclear, conflicting and malformed cases per runnable full build. Review available results. | Expected/actual result, gate/evidence and assessment where applicable. Count wrong, blocked and unrun cases. |
| With each CC | Review inputs/outputs, checks and connections. | One connected case, remaining gaps listed. |
| Each progress review | Classify findings. Choose next work. | Next action and required agreement per issue. |

Unusable intent stops before Requirements. Four cases are a start, not quality proof. [Test details](../reference/compiler-verification.md#cases-and-evidence).

## Agreement needed

- Scope: people working on requirements/affected components.
- Interfaces/checks: people working on connected components/verification.
- Files/review timing: people working on the build/run.

Record decisions/evidence in existing issues/PRs and TASK records.

## Review and update flow

```mermaid
flowchart TD
    I[/Generated code and run evidence/] --> R[Review design conformance and labelled cases]
    I -->|missing files| U[Record gap and check availability]
    R --> F[/Findings with expected and observed behavior/]
    F --> A[Record next action and required agreement]
    A --> D[Update affected design or implementation records]
    D --> N[Review new evidence and choose next boundary]
    U --> I
    N --> R
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class I,F record
    class R,A,D,N tool
    class U unresolved
```

Blue: records. Teal: review/update work. Red: missing evidence.

## Risks and effort

- Missing code/logs: check availability early. List gaps.
- Wrong verifier: compare reasons/results with agreed expectations.
- Process overhead: fix blockers first. Keep AI CI small.

Most effort: verifiers and blockers. Next: [CC connections/RSI readiness](07-m1-capsules-and-rsi.md). Update affected design only. Delay alone changes planning, not required checks.
