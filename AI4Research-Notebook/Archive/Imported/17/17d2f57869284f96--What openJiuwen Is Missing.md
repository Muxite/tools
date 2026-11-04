**The "why CC" evidence, and it replaces argument with facts.** Every row is an absence verified in
source at agent-core `e23806c1` on 2026-09-23. No new claim is needed: what is missing *is* the schema.

| Missing | Evidence |
|---|---|
| effects, preconditions, postconditions, guarantees on any carrier | `ToolCard`'s whole behavioural surface is `parallel_safe`, `stateless`, `idempotent` (`core/foundation/tool/base.py:78`); `SkillSpec` is `dir`, `mode`, `enabled_skills` |
| a version on any carrier spec | none on `PluginSpec`, `AgentTemplateSpec`, `SkillSpec`, `ToolCard`, `AgentCard` |
| a hash on any load path | `apply_extension_hot` loads by name/path; `LoadRecord` carries no hash |
| a persistent record of what was installed | `DeepAgent._load_records` (`harness/deep_agent.py:314`) is an in-memory dict |
| capability lineage | only `RsiTreeNode.parent_id` (`rsi/schema.py:102`) — an RSI search tree, not a library |
| a pre-execution gate keyed on a **capability** | the permission engine keys on `tool_name` + `tool_args` only (`harness/security/permission_engine/core.py:272`) |
| a concrete `CapabilityProvider` | the protocol exists (`symphony/interfaces/capability.py:13`), no implementation does; CC's would be the first (checked 2026-09-24) |
| MCP tool annotations | agent-core drops `readOnlyHint` and the rest when it loads an MCP tool (checked 2026-09-24) |
| a guard on the workflow tool path | a workflow `ToolComponent` calls a tool with no `AbilityManager`, rail or permission check (`tool_comp.py:61-70`) |
| capability-aware model routing | `IntelliRouterModelClient` and `ModelAllocator` route by endpoint and by member; nothing reads a capability |

## The companion: what CC therefore does *not* build

Just as important, and it is the reuse-first story:

- **`symphony/flow`** — hashing, versions, the immutable store, the ten-check review gate, the isolated
  LLM reviewer, rendering and install. See [[Symphony Flow]].
- **`extension_binder`** — hot load and unload, undone in reverse order.
- **`EvaluationSuite`**, **`GoalEvaluator`** (including `should_spot_check()`), **`PermissionEngine`**.
- **Symphony's whole retrieval side** — retrieval, discovery, the graph engine, orchestration.

## Corrections to our own `kb/repos/` notes

1. `SkillManifestParser` (`symphony/shared/fingerprint/parser.py:129`) **already reads `inputs`/
   `outputs`** from `SKILL.md` frontmatter. Only `SkillUseRail` is blind. Our note says otherwise.
2. The Symphony README's status table is **stale** — retrieval is implemented, not 待迁入.
3. `symphony/flow/` appears in **none** of the three repo notes.

Related: [[Declared vs Observed]], [[Today's Capsules vs the Schema]], [[Where It Attaches]].
