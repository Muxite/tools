# Provisional capability hypotheses to test through engineering

These are source-grounded proposals, not a prescribed tool catalog or operations observed in a new GPU campaign. The current user priority is to discover the entire initially needed portfolio through real inference-improvement work. Add, merge, reprioritize and reject entries using actual campaign evidence. No measured engineering time savings asserted.

| Priority | Capability | Reuse | Remaining useful output |
|---|---|---|---|
| P0 | Agent-visible source/model/release inspection | Existing CC finite calls; actual model config/GGUF reader | Bounded report with facts, incompatibilities, unresolved requirements |
| P0 | Identified engine-image build | BuildKit + Buildx/Bake | Image, source/build receipt, dependency/base identities, logs |
| P0 | Cross-machine delivery preparation | Docker archive or existing registry | Hashes, platform/config identities, logical launch/input requirements |
| P0 | Handoff validation | Existing schema/YAML libraries and bounded checks | Ready/draft/rejected with exact missing or conflicting evidence |
| P0 | External engineering/test operation capture | Agent native streams, command wrappers, durable files | Linked agent/task/operation/build/job/attempt evidence, incomplete spans |
| P0 shared | Lab admission/status/result bridge | Other team's lab agent + existing APIs | Request/attempt mapping, acknowledged requirements, actual result refs |
| P0 lab-owned | Sandbox provisioning/execution/reconciliation | Incus API + private Docker SDK | Qualified environment, confirmed stop and new-attempt recovery |
| P1 | Saved profiler-report analysis | Nsight shipped reports + NCU Python API | Versioned summary, metric units, retained raw references, coverage |
| P1 | Test policy/client adapters | llama.cpp tools, GenAI-Perf, relevant upstream tests | Clearly scoped smoke/quality/performance outcomes |
| P1 | Engine instrumentation | Source-aware NVTX/counter helpers | Reviewed patch, build and measured emitted-coverage checks |
| Investigate | Expert trace summarization | MoE-Infinity/Strata mechanisms and tests | Route/residency/dispatch distinctions and missing fields |
| Discover | Methodology CCs | Actual experiment procedures and agent instructions | Reusable decision/measurement/integration methods with worked and failed cases |
| Discover | Engine component CCs | Existing source, snippets, modules, classes/functions, libraries or kernels | Tested asset, compatibility/state/dependency requirements, incorporation instructions and actual build evidence |
| P2 | Broader scheduling/tracking | dstack/Temporal/SkyPilot/MLflow | Adopt only if less integration/operations effort than narrow adapter |

Several capabilities can belong in one CC. A tool is not necessarily one capsule, and a trace/image is not automatically a capsule. Investigate component CCs during the campaign and integrate the valuable ones when feasible; their correct form and boundary are open. The product engine is not wrapped as a whole-engine CC. The build CC is required; demonstrate a small useful initial profiling/test set and empirically justified tool/methodology/component assets rather than promising all possible future capabilities.
