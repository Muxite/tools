---
id: muse-final-tools-md
status: current-design-proposal
source: Sources/Prompts/2026-11-09-post-presentation-workshop-takeaways.txt
last_reviewed: 2026-11-09
next_action: Review the revised proposal and qualify the engine and lab interfaces during implementation
---

> **Latest feasibility recommendation, November 9:** [[Asynchronous lab manager and executor]] proposes a Factory Lab Manager API plus deterministic external executor. The earlier always-present reasoning lab agent is optional, not a starting requirement. The Manager is the Factory’s logical lab gateway. This recommendation remains a design proposal.

# Reusable capabilities with useful outputs

| CC use | Example input | Reusable operation | Output / integration |
|---|---|---|---|
| Tool/skill: source inspection | Repository + ontology references | Identify implementation boundaries and unresolved assumptions | Source map and candidate integration plan |
| Tool/skill: NVTX engineering | Source + diagnostic hypothesis + marker convention | Agent placement plan, checked patch, build and executed coverage checks | Instrumented source, coverage report, new engine image after builder packaging |
| Tool/skill: build/package | Pinned source + component selections + dependencies | Produce and identify the release | Immutable OCI image + manifest |
| Tool/skill: lab measurement | Release/configuration/fixture IDs + bounded playbook | Readiness, correctness, protected timing, conditional Systems/Compute capture | Results, reports, coverage and failures |
| Component: expert-weight access | Defined engine interface + weight representation | Retrieve/cache selected expert weights | Module incorporated into engine code; native miss/residency counters |
| Component: expert execution | Tensor/shape contract + numeric expectations | Execute selected expert projections and accumulation | Source/library/kernel integrated into release; correctness tests |

These are proposed capability examples, not deployed modules. The builder receives both categories. Factory tools need not ship inside the engine; component implementations may ship there. The engine runs through its own service/launch interface rather than a whole-engine CC wrapper. Several capabilities can share a package and a CC can compose other CCs.

Temporary composition makes a workflow for a job; persistent composition produces a reusable composite CC. All-to-CC source adaptation can reuse the factory workflow with source-specific agents. A trace, weight pack or image is an artifact, not automatically another CC.

Profiler packages can change independently of engine code. Activation exposes a qualified version, wrapper and scoped paths; removal stops temporary processes and releases grants while retained reports remain in Factory. Host permissions and driver changes remain separately qualified platform work. See [[NVTX engineering CC]] and [[Post-presentation design revision]].

