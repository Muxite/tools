---
id: cc-pilot-development-cases
status: proposed
source: jiuwenswarm/docs/architecture/design-package/README.md; jiuwenswarm/docs/architecture/design-package/2-capability-capsules.md
last_reviewed: 2026-10-20
next_action: Audit adapter feasibility, then freeze input-only manifest hashes before pilot execution.
---
# Development case index

These are six synthetic, proposed, unrun development cases. The intent/brief tasks use experiment-specific adapters and do not claim to implement M1 contracts. A runnable M1 adapter remains pending code audit.

Each case separates agent-facing inputs from scorer-only material. Execution adapters may read only the `prompt.txt` and fixture file(s) linked in the **Inputs** column. Do not pass `scorer-key.md` or `manifest.json` to an agent. The manifest hashes the prompt and fixtures only; it excludes scorer keys. This directory contains no held-out case contents.

| Case | Task family | Inputs for execution only | Scorer-only key |
|---|---|---|---|
| DEV-01 | Synthetic intent normalization adapter | [[Experiments/Development-Cases/DEV-01/prompt.txt\|prompt]] · [[Experiments/Development-Cases/DEV-01/fixture.json\|fixture]] | [[Experiments/Development-Cases/DEV-01/scorer-key\|scorer key]] |
| DEV-02 | Synthetic research-brief adapter | [[Experiments/Development-Cases/DEV-02/prompt.txt\|prompt]] · [[Experiments/Development-Cases/DEV-02/fixture.json\|fixture]] | [[Experiments/Development-Cases/DEV-02/scorer-key\|scorer key]] |
| DEV-03 | Daily coding: CSV summary repair | [[Experiments/Development-Cases/DEV-03/prompt.txt\|prompt]] · [[Experiments/Development-Cases/DEV-03/summarize.py\|code fixture]] · [[Experiments/Development-Cases/DEV-03/fixture.csv\|CSV fixture]] | [[Experiments/Development-Cases/DEV-03/scorer-key\|scorer key]] |
| DEV-04 | Experiment design | [[Experiments/Development-Cases/DEV-04/prompt.txt\|prompt]] · [[Experiments/Development-Cases/DEV-04/fixture.txt\|fixture]] | [[Experiments/Development-Cases/DEV-04/scorer-key\|scorer key]] |
| DEV-05 | Results reporting with missing values | [[Experiments/Development-Cases/DEV-05/prompt.txt\|prompt]] · [[Experiments/Development-Cases/DEV-05/fixture.json\|fixture]] | [[Experiments/Development-Cases/DEV-05/scorer-key\|scorer key]] |
| DEV-06 | Literature synthesis | [[Experiments/Development-Cases/DEV-06/prompt.txt\|prompt]] · [[Experiments/Development-Cases/DEV-06/fixture.txt\|fixture]] | [[Experiments/Development-Cases/DEV-06/scorer-key\|scorer key]] |

Each case folder has `manifest.json` with SHA-256 hashes for input files only. It has no answer key path/hash. Hashes must be refreshed and frozen with the protocol before a run. Read [[Experiments/cc-effectiveness-protocol|CC Effectiveness Protocol]] for split protection, blind scoring, and adapter readiness.

## Held-out cases

At least three held-out cases remain uncreated and custodian-controlled. Their identities, prompts, fixtures, keys, and hashes are not present here. A custodian must prepare and lock them independently before proposer tuning; any leaked case is retired before evaluation.
