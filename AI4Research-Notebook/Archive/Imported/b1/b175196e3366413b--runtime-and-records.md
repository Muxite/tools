---
type: module
status: confirmed
source: "PRD §3 Harness Core, Data Foundations, Visibility, UI, System Configurations"
tags: [block-2, module]
---

# Runtime and records

**Confirmed by:** PRD §3 (Harness Core; Data Foundations; Visibility / Statistics; UI; System Configurations).

JiuwenSwarm is the runtime: Swarmflow runs the DAG, its memory holds context, and its run tree shows progress. CC's records sit beside it and join it by ids.

```mermaid
flowchart LR
    UI([web workbench or TUI]) --> SW[Swarmflow: runs the Default DAG]
    CFG[(config.yaml: models, workspace, budgets)] --> SW
    SW --> RU[CC runner, around each capsule call]
    RU --> MEM[(Task Memory, Coding Memory: context)]
    RU --> REC[(CC records: run contract, Observations, Verification results)]
    SW --> TREE[(run tree, token budgets, security logs)]
    REC -.->|joined by run and step ids| TREE
```

**Uses from Block 1:** [[run-contract]], [[observation]], [[verification-record]], [[integration]] (Swarmflow connection points).

**Open:** whether CC's records store conflicts with the PRD's "no custom database schema" in M1 ([[prd-inputs]]).
