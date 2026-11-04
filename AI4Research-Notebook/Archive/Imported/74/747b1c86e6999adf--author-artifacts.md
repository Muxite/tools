---
title: Author artifacts — pinned inspection leads
date: 2026-10-07
status: read-only-inspection
tags: [research, provenance, artifacts]
---

# Author artifacts: what was actually inspected

These are source-inspection leads, not admitted dependencies or tested integrations. On 7 October 2026, read-only `git ls-remote` resolved the branches below; the linked files were inspected at those exact revisions. No checkout, installation, model call or code execution occurred.

| Artifact | Observed revision | Useful inspection lead |
|---|---|---|
| PNNL AutoLabs, `master` | `06a2f33db19f935c4e7f9ea5d9d1488847b6d3fe` | [Pinned README](https://github.com/pnnl/AutoLabs/blob/06a2f33db19f935c4e7f9ea5d9d1488847b6d3fe/README.md), [evaluator.py](https://github.com/pnnl/AutoLabs/blob/06a2f33db19f935c4e7f9ea5d9d1488847b6d3fe/evaluator.py) |
| Gomes group Coscientist, `main` | `417e82b85743f88719ba7cf8838220fcb872e2ae` | [Pinned README](https://github.com/gomesgroup/coscientist/blob/417e82b85743f88719ba7cf8838220fcb872e2ae/README.md) |

AutoLabs' README describes a design/simulation/evaluation application and provides startup instructions, including creating the requirements file if missing. Its top-level `evaluator.py` at this revision contains only `name = "tmp"`. This establishes the contents of that particular file, **not** the absence of evaluation elsewhere or failure of the entire repository. A worker investigating reuse should locate the actual scoring implementation and its fixtures instead of assuming a plausible filename implements the paper's oracle.

Coscientist's README distinguishes supporting data directories from `simple_implementation`; the paper also warns that this simpler public implementation may not produce the same results. Supporting artifacts can help inspect a reported experiment without constituting a drop-in reproduction of its system. See the scoped [laboratory evidence](scientific-workflow-transfer.md).

Our inference: keep paper-version identity, repository revision, selected file identity and observed test results distinct in any future capsule-feed import. A pinned revision establishes which bytes were inspected; it does not establish completeness, correctness, compatibility or admission. Preserve an incomplete or untested status rather than filling gaps from the paper's prose. Any later experiment should record its own environment and results and disclose departures from the reported system.

Coverage is deliberately limited to these files. Branches may move after the recorded observation; use the revision links to inspect this snapshot. Other repository links in the research notes remain unpinned leads unless explicitly recorded otherwise.
