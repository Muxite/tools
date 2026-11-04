**Where this layer lands in the code.** Muk's point that Symphony gives us something to build on is the
right lead, so lead with it. Kept light, per the directive that individual code items are illustrative
and open to change — the deck only has to show the design can work on what exists.

> We are not choosing where to put this. **openJiuwen already has the sockets.**

| Attachment point | Code | What CC does there |
|---|---|---|
| **`CapabilityProvider`** ← *the flagship* | `symphony/interfaces/capability.py:13` | implement **two methods** — `capabilities()` and `source_snapshot()` — and Symphony indexes only admitted capsules. Nothing inside Symphony changes. No concrete provider exists in agent-core yet, so CC's would be the first. Used from M3; M1 plans by ports |
| `SkillGraphUpdater` | `symphony/interfaces/graph.py:14` | add / update / delete as admission changes |
| `submit_observation` | `symphony/graph_engine.py:156` | run evidence back into the graph |
| **Symphony Flow** | `symphony/flow/engine.py:54` | the merge pipeline; CC supplies the declaration, lineage and pinned members it lacks — [[Symphony Flow]] |
| Load path | `harness/extension_binder.py:27` | reverse-order unbind, reused. For M1 the load itself goes through **our own small loader** with a sha256 check before import, not `harness.tool.file` ([[Layer 2 Presentation]]) |
| Dispatch | `ability_manager._railed_execute_single_tool_call():1315`, `BEFORE_TOOL_CALL` | the per-call check keyed on the capsule. **Not enough alone:** a workflow `ToolComponent` calls a tool with no `AbilityManager`, rail or permission check, so M1 wraps every tool in one `CapsuleTool` (precedent: `decorate_tool_with_trace`) |
| Rails | `harness/rails/` | one rail persists the Binding and its invocations |
| Permission engine | `security/permission_engine/core.py:272` | irreversible severe effect → `ASK`; unattended → `DENY` |
| Records storage | `extensions/store/` (`db`, `kv`, `vector`) | where CC's records live — **no new database** |
| Our M1 skeleton | planner-binder, freeze, Kahn runner, gate | new control code on openJiuwen, not the archived AI4Research harness — [[Layer 2 Presentation]], [[Impacts on the Workflow]] |

Related: [[openJiuwen Landscape]], [[Dependencies]], [[What openJiuwen Is Missing]].
