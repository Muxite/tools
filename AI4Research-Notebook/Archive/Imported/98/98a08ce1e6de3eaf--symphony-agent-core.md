# Ask: Symphony and agent-core ↔ Capability Capsule

From Muk (Capability Capsule) to the owners of Symphony and agent-core, for the 2026-09-22 workshop. Written
2026-09-22 against `SCHEMA.md` v1.6 and agent-core `e23806c1`, read in source. The supervisor allows changes to
agent-core only where necessary; this page asks for none that are not listed.

## The hooks the capsule layer will use, all of which exist today

| Hook | File (agent-core `openjiuwen/`) | Use |
|---|---|---|
| `CapabilityProvider`, `AtomicCapabilityProvider` | `symphony/interfaces/capability.py:13` | list only available skill, subagent and agent capsules, with `content_hash` and level in `CapabilityDescriptor.metadata`; atomic, since batch graph mutation requires it (`symphony/orchestration/mutations.py:167`). The graph takes no other kinds (`symphony/orchestration/graph/build.py:161`) |
| `SkillGraphUpdater.add_skills`, `update_skills`, `delete_skills` | `symphony/interfaces/graph.py:14` | one call per activation, supersession or retirement. Ids are keyed as skills (`mutations.py:396`), one revision per id, and each mutation needs a model (`mutation_service.py:129`) |
| `CapabilityIO`, `SymphonyModel` | `symphony/models/capability.py:15` | the manifest's inputs and outputs, in Symphony's shape |
| `apply_extension_hot` | `harness/extension_binder.py:27` | load a capsule from the immutable store after the capsule layer checks its hash and certificate; the binder itself loads by name, with no hash check (`extension_binder.py:33-36`) |
| `before_tool_call` | `harness/observability/rail.py:888` | observed tool calls, compared with declared effects |
| `LoadRecord.refs`, `TrajectoryStore` | `harness/resources/extension_resolver.py:60`, `agent_evolving/trajectory/store.py:23` | the run pin; load records live in memory (`harness/deep_agent.py:314`), so a new capsule-layer rail writes pins to the store |

## What would change, and why

| Change | Where | Why |
|---|---|---|
| a filter on declared types, effects, preconditions and level runs **before** the planner model | the capsule layer's provider, or a step before Symphony's planner | Symphony's planner is told not to judge I/O compatibility, which is handled after the plan (`symphony/orchestration/planning/fast.py:43-44`); predicate parity puts declared checks before choice (2608.01050 p3) |
| declared ports instead of edges a model proposes at confidence ≥ 0.7 | `symphony/orchestration/graph/build.py:122` | declared edges are checkable, inferred ones are not |
| `unknown` types match only for steps that accept provisional capsules | `symphony/orchestration/planning/input_matching.py:23-33` | today `unknown` matches any same-named input |
| effect-level observation below tool calls | agent-core, or a sandbox | the one likely agent-core change; until then effects are observed at tool-call level |

## To settle together

- Who owns the model that binds capsules to plan steps (default: Symphony's planner, fed by the provider, filter first).
- Who owns the type and state vocabulary (default: the capsule layer, seeded from Symphony's).
