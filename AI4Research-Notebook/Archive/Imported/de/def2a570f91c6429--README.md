---
type: home
tags: [block-2, index]
---

# Block 2: the system design

The design of AI4Research's M1 system, drawn from the PRD ([[prd]]), one small module at a time. **Only parts the PRD has confirmed are drawn;** each module names the PRD section that confirms it. Schemas and Capability Capsule are in [[Block 1 - CC and Schemas/README|Block 1]] and are not repeated here.

**Start with [[build-steps|B1, B2 and B3 at a high level]].**

## Modules

| Module | What it covers | Confirmed by |
|---|---|---|
| [[ingestion-and-brief]] | the user's request and documents, template mapping, the Research Brief | PRD §3, §4.1 |
| [[default-dag]] | the hardcoded Default DAG in Swarmflow and its stage capsules | PRD §2, §3, §4.1 |
| [[evaluator-gate]] | the two-tier gate, `pass` / `fail` / `blocked`, `human_session` | PRD §3, §4.3 |
| [[operators]] | DeepSearch, CodeSearch, workspace I/O, behind the permission layer | PRD §3, §4.4 |
| [[model-access]] | one model through the Codex CLI; routing later | PRD §2, §3 |
| [[runtime-and-records]] | Swarmflow, memory, the run tree, CC's records, UI and config | PRD §3 |

## Rules for adding a module

- One page per part the PRD confirms; name the section. A part that is not confirmed is not drawn.
- One small diagram, a short in/out table if needed, links into Block 1, and the open questions.
- Keep each page short; Block 1 holds the detail.
