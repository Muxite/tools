# 5. AI CI

**AI CI proposal: scripts, bounded agent review and targeted alerts.** Architecture maintains design-check guidance. Affected contributors resolve findings.

## Design CI

| Part | Job |
|---|---|
| Scripts/tools | Case-sensitive paths, links, glossary spelling, schema references, diagram freshness |
| Agent skills | Reusable instructions, examples and review criteria |
| Agent workers | Use skills/tools to flag unclear meaning, missing context and likely impact |
| People | Resolve disputed meaning and consequential decisions |

Bound jobs by time/cost. Save checked revision, input identities and findings. AI review can be wrong. Document checks do not prove product acceptance.

## Runner and sidecar in AI CI

**Use the designed tooling boundary.** AI workers operate outside the runner. CI triggers jobs. Neither tooling design adds authority to product agents.

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

Blue: records. Teal: work/tools. Amber: human decision. Boxes show responsibilities, not extra required services.

| Tooling design | What it contributes |
|---|---|
| [Sidecar](../development-tools/sidecar/README.md) | Registered validation/diagnostic tools, explicit target, effects, limits and retained results |
| [Client runner](../development-tools/test-runner/README.md) | Readiness, submit, observe, assess and export through supported client seams |

- Missing authentication, readiness or client compatibility blocks the job. Interrupted/inconclusive results stay visible.
- Launcher owns lifecycle/cleanup of its resources. Runner has no Docker socket or private product-state access.
- Development reports inform diagnosis. They cannot replace product verifiers/gates or insert accepted outputs.
- Start with existing scripts and one review worker. Add this integration when useful and separately scoped. Product startup and exits stay independent.

## GitHub and Discord

- **GitHub:** drafts, issues, PRs, decisions and evidence. Existing TASK/specification records retain work authority. Merge design after relevant human review.
- **Discord:** targeted alerts and discussion links. Return decisions to GitHub.
- **Routing:** assignees, requested reviewers and Git-tracked module/contact map. Ping for action/blockers/shared contracts. Group routine updates.

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

Surface failed checks/jobs too. Keep unanswered actions visible. Delivery does not prove reading. Restrict mentions to intended recipients. Integration is proposed, not deployed.

**Measure value:** useful alerts, missed changes, rework and review effort against tool cost. Token counts describe size, with tokenizer/version recorded.

**Inspired by:** [GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions) for event-driven checks, and [Anthropic's agent patterns](https://www.anthropic.com/engineering/building-effective-agents) for simple workflows before added autonomy. Useful because steps stay inspectable and cost can be bounded.

**Bot example:** [pr-discord-notifier](https://github.com/asirago/pr-discord-notifier) posts opened, edited and closed PR notices. Our recipient routing needs separate logic. Start with a GitHub workflow and [Discord webhook](https://docs.discord.com/developers/resources/webhook).
