---
id: muse-final-presentation-outline-md
status: current-design-proposal
source: Sources/Prompts/2026-11-09-post-presentation-workshop-takeaways.txt
last_reviewed: 2026-11-09
next_action: Use revised slides for design discussion and qualify the proposed interfaces
---

# Post-presentation revision: ten main slides and eight appendices

| Slide | Content |
|---|---|
| 1 | Software Factory and its lab boundary |
| 2 | CCs are reusable capabilities, distinct from the release contract |
| 3 | Tools across the Muse inference engine |
| 4 | Two CC roles produce different reusable outputs |
| 5 | NVTX CC: reusable judgment support and repeatable edits |
| 6 | Crash-surviving lab control and immutable engine deployment |
| 7 | A playbook spends profiling effort only where needed |
| 8 | Combine profiler data with engine facts and matched trials |
| 9 | Together Compiler (TKCC): potential evolution |
| 10 | Start with attributable experiments; evolve when evidence justifies it |
| A1 | A1  Muse text layer: precise instrumentation boundaries |
| A2 | A2  Required observability: producer, units, and diagnostic value |
| A3 | A3  Qualification and recovery across failure boundaries |
| A4 | A4  Detailed contract and ontology references |
| A5 | A5  Illustrative release package for the Muse engine |
| A6 | A6  NVTX tool CC: skill materials plus finite executable helpers |
| A7 | A7  Bounded experiments before adopting persistent execution |
| A8 | A8  Resource limits: safety envelope versus inference experiment |

The whole engine release has its own runtime interface. A4/A5 describe the proposed contract and package, not a renamed whole-engine CC. See [[Post-presentation design revision]].

The latest lab-control recommendation is a Manager API and deterministic executor; reasoning remains optional. See [[Asynchronous lab manager and executor]].
