---
id: cc-v2-development-receipt
status: bounded-feasibility-implemented
source: Approved November 4 CC v2 plan and actual development evidence
last_reviewed: 2026-11-04
next_action: Repair Docker host availability and qualify the remaining provider boundaries
---
# CC v2 development receipt

The maintained entrypoint is [[Designs/CC and Strata delivery/CC Protocols/README|CC Protocol v2]]. [Delivery receipt](delivery-receipt.json) records exact scope, findings and results. [Result manifest](result-manifest.json) records final bytes. Original v1 documents/tools and their hashes remain in this batch and the protocol history folder.

Three independent adversarial agents produced protocol, coding and scientific/Factory probes. Fifteen findings across the review cycles were resolved and rechecked at their tested boundaries. Original reports remain unchanged except for appended verification history:

- [Protocol findings](adversarial-protocol.json) and [verification](adversarial-protocol-verification.json).
- [Coding findings and final verification](adversarial-coding.json).
- [Factory findings](adversarial-factory.json) and [verification](adversarial-factory-verification.json).

Actual final tests: 21 local regressions; real pinned upstream stdio MCP discovery/calls/replay; MAPIE native artifact pipeline and negative scientific case; native upstream TaskTool/SysOperation worktree repair with executed assertions; actual pinned Strata reader/full verification of a synthetic product and rejection of tampering. No live model or GPU engine was used.

The image worker never started: Docker Desktop could not access/rename its startup socket despite a bounded supported recovery attempt. Registry digest resolution and command-construction tests do not establish image execution or isolation. The notebook-wide validator retains one preexisting unrelated broken repository link; no new link/metadata errors were reported.
