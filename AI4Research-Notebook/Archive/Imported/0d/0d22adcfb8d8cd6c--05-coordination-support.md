# 5. AI CI

**Proposal: cheap scripts, bounded agent review, targeted alerts.** Maintain design-check guidance. Get agreement for disputed changes.

## Design CI

| Part | Job |
|---|---|
| Scripts/tools | Path casing, links, glossary, schema references, diagram freshness |
| Skills | Reusable review instructions, examples, criteria |
| Workers | Flag unclear meaning, missing context, likely impact |
| People | Resolve consequential decisions |

Limit time/cost. Retain checked revision, inputs, findings. AI can be wrong. Document checks do not prove product acceptance.

## Runner and sidecar in AI CI

**Development tooling only.** AI workers operate outside the runner. CI triggers finite jobs.

```mermaid
flowchart TD
    C[/Changed revision and selected cases/] --> J[CI or authorized development agent]
    J --> L[Host launcher: environment and finite job]
    L --> S
    subgraph Dev[Development tooling boundary]
        S[Sidecar: registered tools under limits]
        S --> R[Client-validation runner: bounded case]
        S --> X[Diagnostic adapter]
    end
    R -->|scoped authenticated client| A[/AI4Research application/]
    A -->|permitted observations and exports| E[/Retained development evidence/]
    X --> H[Host executor: enforce target/effects]
    H --> E
    R --> E
    E --> Q{Affected contributors diagnose}
    Q --> N[/Issue or PR with next action/]
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef human fill:#fff4d8,stroke:#b58100,color:#694b00
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    style Dev fill:#f5f7fa,stroke:#64748b,color:#334155
    class C,A,E,N record
    class J,L,S,R,X,H tool
    class Q human
```

Blue: records. Teal: tools. Amber: human decision. Boxes show responsibilities.


| Design | Purpose |
|---|---|
| [Sidecar](../development-tools/sidecar/README.md) | Registered diagnostics/validation, target/effect limits, retained results |
| [Runner](../development-tools/test-runner/README.md) | Readiness, submit, observe, assess, export through authenticated client interfaces |

- Missing readiness/authentication/compatibility blocks. Incomplete results stay visible.
- Launcher cleans up owned resources. Runner: no Docker socket or private product-state access.
- Reports cannot replace product verifiers/gates or insert accepted outputs.
- Separate tooling scope. Product startup/exits stay independent. Start with scripts and one worker.

## GitHub and Discord

- GitHub: drafts, issues, PRs, decisions/evidence. Existing TASK records retain authority. Relevant human review before design merge.
- Discord: action alerts/discussion links. Return decisions to GitHub.
- Route by assignees, reviewers, Git-tracked module/contact map. Group routine updates. Ping for action/blockers/shared contracts.

## Proposed notification flow

```mermaid
flowchart TD
    G[/GitHub design or system-info change/] --> S[CI scripts: mechanical checks]
    S --> W[Agent worker: review using skills and tools]
    W --> F[/Findings and affected areas in GitHub/]
    F --> B[Bot routes alert to affected contacts]
    B -->|mapped and delivered| D[/Discord action link/]
    B -->|unmapped or delivery failed| U[Visible GitHub triage finding]
    D --> H{Contributors resolve findings}
    U --> H
    H -->|correction needed| G
    H -->|ready| R[/Recorded decision and next action/]
    classDef record fill:#e8f1fe,stroke:#1d4f91,color:#123d70
    classDef tool fill:#e0f5ef,stroke:#1b7f72,color:#12554a
    classDef human fill:#fff4d8,stroke:#b58100,color:#694b00
    classDef unresolved fill:#ffe9e9,stroke:#b63636,color:#7f2020
    class G,F,D,R record
    class S,W,B tool
    class H human
    class U unresolved
```

Blue: records. Teal: work/tools. Amber: human decisions. Red: unresolved.

Expose failed checks/jobs, unmapped contacts and failed delivery. Keep unanswered actions visible. Restrict mentions. Delivery does not prove reading. Integration is proposed, not deployed.

Measure alerts, misses, rework/review effort against cost. Token counts need tokenizer/version.

**Inspired by:** [GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions) for event triggers; [Anthropic agent patterns](https://www.anthropic.com/engineering/building-effective-agents) for simple, inspectable workflows.

**Example:** [pr-discord-notifier](https://github.com/asirago/pr-discord-notifier) posts opened/edited/closed PR notices. Routing needs separate logic. Start with a workflow and [Discord webhook](https://docs.discord.com/developers/resources/webhook).
