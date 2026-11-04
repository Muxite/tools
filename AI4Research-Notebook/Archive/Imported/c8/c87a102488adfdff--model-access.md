---
type: module
status: confirmed
source: "PRD §3 Codex CLI Integration, Foundational Models, §2 Model Routing"
tags: [block-2, module]
---

# Model access

**Confirmed by:** PRD §3 (Codex CLI Integration, the first step to implement; Foundational Models), §2 (routing is a parallel track).

In M1 every model call goes to one model through the Codex CLI, using the team's subscription. Dynamic routing is a B3 track.

```mermaid
flowchart LR
    CAP([capsule needing a model]) --> RU[runner]
    RU -->|M1: fixed| CX[Codex CLI]
    CX --> SUB([one model, via the subscription])
    RU -.->|B3: per call| RT[router: ranks models, uses the top one]
    RU -->|model used| OBS[(Observation)]
```

**Uses from Block 1:** [[observation]] (records the model), [[run-contract]] (the Binding's budget and model limits).

**Open:** Codex exists in JiuwenSwarm only as an external CLI agent, not a model provider; what "Codex CLI adapter" means for M1 is question 1 in [[prd-inputs]].
