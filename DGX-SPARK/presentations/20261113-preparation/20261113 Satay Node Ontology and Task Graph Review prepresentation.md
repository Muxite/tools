# 20261113 Satay Node Ontology and Task Graph Review prepresentation

## Finding

The implementation is a small agent-controlled workflow, not the original AI4R frozen-plan engine. Its proof run has a simple successful path: inspect, assess applicability, integrate, build, screen, accept and report. For presentation, group those into five boxes: Inspect/choose → Integrate → Build → Screen → Decide/report. The compact view is a presentation grouping of seven real completed nodes, not a different execution.

No inference, compilation, service restart or code changes were performed for this review. Satay was queried read-only, apart from ordinary Git clone server activity. Danta and original staged evidence were not modified.

## Exact code and data inspected

- Local fresh shallow clone: [JiuwenSwarm](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113>), branch cc-siminfeng, exact Satay HEAD fe88a20682550603a5d32193403c74cc6e68e8b7. Windows long-path support was enabled in this clone to finish checkout. Working tree is clean. Existing ai4r_muk checkout was left untouched.
- Satay HEAD includes a newer RSI assignment commit than the inspected GitHub branch head (532d56c7). No remote push was performed in this review.
- D: v3 package pins JiuwenSwarm 6fd0ac45, not today's latest Satay HEAD. This is a legitimate historical snapshot; do not relabel it as the latest source.
- Reviewed the D: start guide, facts, scene index, staging review receipt, v3 source pins and proof-task records. Checked E: Danta's evidence and profiling indexes, and byte-compared four representative evidence files against their D: originals. Existing full-package hash receipts were read, not rerun in this review.
- Downloads still contains some older slides/reference material. The relevant current bundles and captures were moved to the D: staging tree. No additional relocation was needed.

## How the pieces actually connect

| Piece | Implemented behavior | Limit |
|---|---|---|
| Engineering task | Operator objective, source, resources, budget and contract_id. constraints.engine_slice selects expert_weight_readiness. | The proof instruction explicitly selected demand fill, prerequisites, one build and one screen. Do not claim autonomous technique discovery. |
| Lab contract | qwen36-quick-v1 fixes the workload and reference output. | Distinct from the engineering brief and ontology target. Acceptance here was correctness/engagement, not a speed verdict. |
| Engine ontology | Packaged YAML lists engine regions, quantities/units and relations. One slice groups relevant regions and quantities. | Local and provisional, hard-wired to expert_streaming's catalog; not a general external system-ontology compiler. |
| Component mapping | Component metadata names implements, modifies_region and quantities. expert_fill points to L4.selected_expert and M.read_request. | References are validated; arbitrary source edits are not semantically proved to affect only those boxes. |
| Planner | The coding agent decides actions and publishes decision-linked graph patches. | No separate search planner, automatic ontology-to-DAG compiler or learned workflow selector was demonstrated. |
| Work graph | Immutable patch history, revision checks, dependencies, node states, evidence and attempt references. Cycles are rejected within each revision. | The overall iterative process revises the graph; iteration does not require cyclic edges inside a snapshot. |
| Controller | Reconciles durable jobs, sends changed attempt states/evidence cursor/budget to the agent, waits for active jobs and resumes reasoning afterward. | It does not execute the graph's ready frontier as an independent graph scheduler. |
| Scheduler | Builder/lab submissions enter the existing durable host queue. | Graph metadata alone does not reserve CPU/GPU resources. |

Shared context is the task-scoped store plus source/artifact/image references. Dependency edges express order; they do not carry a copied payload from one agent node to another. Multiple CC tools can be used by the same agent.

## Verified proof-task graph

Task factory-cc5e8585445c484ba4d5b5b0dd96c31c used GPT-6.1 Sol according to its exported invocation record. The source shows CLI ask → controller → JiuwenSwarm Codex adapter → CC tools → build/lab queue.

All five intact exported graph records were compared exactly with a read-only SQLite query on Satay. The cloned taskgraph.replay implementation successfully reconstructed them locally.

| Revision | Actual change |
|---|---|
| 1, host seed | Nine proposed nodes: inspect → applicability → baseline-build → baseline-measure → integrate → candidate-build → candidate-measure → accept → report. |
| 2, decision 1 | Cancel baseline-build, baseline-measure and candidate-measure. Add candidate-screen. Rewire integrate to applicability and accept to candidate-screen. Mark inspection/applicability done. |
| 3, decision 2 | Mark integration done. |
| 4, decision 3 | Link completed build 3445e556 and mark candidate-build done. |
| 5, decision 5 | Link screen bbc85611 and mark screen, accept and report done. |

Final history: ten nodes total, seven done and three cancelled. All ten carry engine_slice=expert_weight_readiness. The node inputs also reference contract:qwen36-quick-v1. The seventh active step is report; no additional hidden workflow is needed for this demo.

The [verified reconstructed graph](<20261113 Satay Verified Proof Task Graph prepresentation.json>) is a new derived artifact. It preserves the recorded history and was not written back into original evidence.

## Small changes worth considering later

1. **Seed the requested work, not an unconditional experiment template.** initial_plan always inserts baseline rebuild/measurement and an ABBA candidate-measure node. This task forbade those actions, so the agent cancelled them immediately. A scope-aware seed or a tiny initial inspect node would avoid pointless bookkeeping. Do not build another planner to solve this.
2. **Keep the ontology claim narrow.** The slice validates names and supports traceability. Node requires_evidence identifiers are validated, but graph completion does not enforce that all those quantities were measured. Component ranking is explicitly heuristic. This is enough for a prototype linkage, not full ontology-driven planning.
3. **Explain optional dispatch linkage accurately.** API readiness checks run only when node_id is supplied. With a node link they reject terminal nodes and unfinished dependencies. An explicitly blocked node whose dependencies are all done is not itself rejected by dispatch_precondition. These are optional hardening points, not reasons to enlarge the demo graph.
4. **Fix structured export redaction before using exports as machine-readable replay input.** The exported observations.json and events.json contain malformed JSON. Raw byte redaction matches the token suffix in metric names and consumes part of a numeric value/key. A synthetic non-secret metric reproduces this. Preserve originals; sanitize structured objects before JSON serialization and validate exported JSON. Do not weaken credential protection or re-export private state indiscriminately.

The malformed records do not invalidate the graph comparison: all five graph objects were independently recovered intact, matched to live SQLite and replayed using the actual implementation. Other affected records should not be silently repaired or treated as parsed data.

## Presentation recommendation

Show two different diagrams, each small:

- **Engine:** selected experts → weight readiness/read requests/page cache → CPU expert execution. Label the detailed slice and component modifications.
- **Work:** inspect/choose → integrate → build → screen → decide/report, with a return arrow labeled revise from evidence. Explain that the return arrow represents a new graph revision, not a cycle in a frozen DAG.

Then show revision 2 briefly: the agent removed unnecessary baseline/ABBA work to honor the narrow task. This is a concrete illustration of adaptation, but the operator already specified the technique and scope.

The new live captures are CLI requests to images a9a0c71c and a15f04f0, not HTTP API calls. The separate J-OM13 result belongs to fill-plus-predictive-read image1274abb8. Keep this distinction in every scene. Current staged facts already handle it correctly.

## Source anchors

All paths below refer to the exact local Satay clone:

- [Ontology and slice validation](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/ontology.py:46>)
- [Slice definition](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/ccs/expert_streaming/ONTOLOGY.yaml:153>)
- [Initial graph template](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/taskgraph.py:280>)
- [Graph replay](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/taskgraph.py:179>)
- [Conditional dispatch check](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/api.py:46>)
- [Dispatch node checks](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/taskgraph.py:219>)
- [Agent/controller loop](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/controller.py:431>)
- [Heuristic component ranking](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/expert_streaming.py:14>)
- [Byte scrubbing after structured serialization](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/export.py:100>)
- [Redaction patterns](<C:/Users/m50066326/huawei/other-repos/jiuwenswarm-satay-20261113/jiuwenswarm/factory/redact.py:5>)
