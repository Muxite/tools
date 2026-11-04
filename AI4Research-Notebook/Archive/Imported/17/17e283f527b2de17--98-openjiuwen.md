# Appendix A. The openJiuwen and AI4Research parts CC uses

CC is built onto what already exists. This appendix says what each part is and does, where it lives, and how CC uses
it. Paths are in agent-core `e23806c1` (under `openjiuwen/`), jiuwenswarm `02b37f47f` and AI4Research `b0bf165f9`
(under `harness/`), each read in source. The fuller notes are in the tundle obby vault (`openJiuwen Landscape`,
`agent-core/Core 00-06`, `jiuwenswarm/Swarm 00-05`).

## A.1 agent-core: identity, loading and running

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **Card and Config** | a Card (`ToolCard`, `AgentCard`, `WorkflowCard`) is a capability's static, serialisable identity; a Config holds its runtime resources. agent-core's own rule forbids putting a session id or runner in a Card | `.claude/rules/architecture.md:31`; `core/foundation/tool/base.py:78` | the Declaration is card-like: identity and contract, never a use |
| **`ToolCard` flags** | `exposure`, `parallel_safe`, `stateless`, `idempotent` on each tool | `core/foundation/tool/base.py:78-110` | computed by CC's gate from declared effects, never trusted as written |
| **`AbilityManager`, `Runner.resource_mgr`** | registers tools, workflows, agents and MCP servers, which agent-core calls abilities, as process-wide state | `core/single_agent/ability_manager.py:142`; `core/runner/runner.py` | the path through which admitted capsules are registered |
| **Runner** | executes agents and workflows on one engine, with sessions, streaming and checkpoints | `core/runner/runner.py` | runs each capsule; unchanged |

## A.2 agent-core: the DeepAgent harness

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **DeepAgent** | the coding-agent framework built on the core: model calls, tools, subagents, a task loop, a workspace | `harness/` | the agent that runs research steps |
| **Rails** | lifecycle hooks (before and after a model call or tool call, and more) through which features plug in without forking the loop | `harness/rails/` | CC adds one rail, to record runs durably and compare tool calls with declared effects |
| **Extension specs** | `SkillSpec`, `McpServerSpec`, `AgentTemplateSpec`, `PluginSpec`: how each kind of extension is described for loading | `harness/schema/extension_spec.py` | the carriers a Declaration names |
| **Extension binder** | loads and unloads extensions at run time (`apply_extension_hot`), undoing registrations in reverse order; loads by name with no hash check | `harness/extension_binder.py:27` | loads capsules from CC's hashed store, after CC checks the hash |
| **`SkillUseRail`** | offers skills to an agent through an allow-list (`enabled_skills`); the agent sees each skill's description and loads it when it chooses; it never reads a skill's `allowed_tools` | `harness/rails/skills/skill_use_rail.py:52`, `:946-958` | applies CC's offer for skills |
| **Permission engine** | decides per tool call whether it is allowed, asked about, or denied (`ALLOW`, `ASK`, `DENY`); `PermissionInterruptRail` raises the question to a person. Off by default in jiuwenswarm | `harness/security/permission_engine/core.py:140` | an irreversible, severe effect is an `ASK`, and a `DENY` on unattended runs |
| **Verification subagent** | a built-in subagent that reviews another agent's work with a model | `harness/subagents/verification_agent.py:274`, `:318` | one of the judges CC gives a standing to |
| **`LoadRecord`** | the in-memory record of what an agent loaded | `harness/resources/extension_resolver.py:60` | what CC's rail persists into Bindings |

## A.3 agent-core: protocols, teams, sessions and storage

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **Harness protocol** | a provider-neutral interface for hosting any agent harness. Vocabulary `Session > Turn > Step`. A Turn has exactly one start and one terminal event and may pause and resume; each tool call is an item; a `TurnResult` carries usage and cost | `harness_protocol/events.py:23-31`, `:148`, `:178`; `results.py:149` | one capsule run is a Turn, or an item for a tool; cost comes from `TurnResult` |
| **Harness providers** | ready implementations of that protocol: `native` (DeepAgent), `native_v2`, `claudecode`, `codex`, `dsh`, built with `create_harness(manifest, provider=...)` | `harness_providers/factory.py:160` | each generalist is an agent template naming a provider, such as Codex or Claude Code |
| **`HarnessCard`** | a harness's identity, protocol version and the host capabilities it requires | `harness_protocol/models.py:132` | enrolment checks those requirements |
| **Agent Teams** | a Leader and Teammates over a message bus and task database; a Teammate may be an external Claude or Codex CLI (`external_cli`) | `agent_teams/` | not a capsule in v1, because the Leader plans |
| **Session VCS** | version control for an agent's context: `commit`, `snapshot`, `rewind`, `fork` | `core/session/vcs/manager.py:104-185` | a context that held a revoked capsule is not reused: a new session, or a fork from before it loaded |
| **Checkpointers** | save state so a run can resume after an interrupt or crash | `core/session/checkpointer/`, `extensions/checkpointer/` | not a record of what ran; CC does not rely on them for evidence |
| **`SysOperation` sandboxes** | where filesystem, shell and code actually execute, locally or in a sandbox isolated per system, session or custom scope (jiuwenbox is one) | `core/sys_operation/config.py:93`; `extensions/sys_operation/` | admission runs a capsule here to observe its effects; `{instance}` scopes map to a session sandbox |
| **Stores** | pluggable database, key-value and vector stores | `extensions/store/` (`db`, `kv`, `vector`) | where CC keeps its records, rather than a new database |
| **A2A** | client and server for agent-to-agent calls, with agent cards | `extensions/a2a/` | carrier for remote agents; CC fingerprints the card |

## A.4 agent-core: evolution, RSI and Symphony

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **`agent_evolving`** | training, evaluators, optimisers and the canonical OTLP `Trajectory`; skill experience is written through an `EvolutionStore` after preview and approval | `agent_evolving/trajectory/model.py:132`, `store.py:23`; `checkpointing/evolution_store.py:41` | trajectories are consumed as they are; experience layers are pinned per sprint as overlays; its evaluators are judges with a standing |
| **RSI** | recursive self-improvement for agent harnesses; keeps a tree of attempts (`RsiTreeNode`: parent, adopted, score) and its own candidate gate | `rsi/`; `rsi/schema.py:96-111` | builds capsules from gaps; its tree joins CC's by `builder_ref`; its gate is builder evidence, and CC's gate admits |
| **`symphony/flow`** | a distil-to-install pipeline for capability sets: recurrence-qualified edges, structural grouping, `candidate`/`verified` grading, content-hashed packages, a ten-check static review gate, an isolated LLM reviewer, and an immutable versioned store | `symphony/flow/` (`engine.py`, `distill.py`, `models.py`, `packager.py`, `review.py`, `store.py`) | the merge engine, reused as it is. CC adds what it lacks: a Declaration on the block, lineage to its members, a held-out test, and members pinned by hash |
| **Symphony** | capability assets for skills, subagents and agents: fingerprints, a retrieval tree, an orchestration graph with Fast and Beam planners, experience and evaluation | `symphony/` | downstream of CC: it indexes only what CC admits, through `CapabilityProvider` (`interfaces/capability.py:13`) and `SkillGraphUpdater` (`interfaces/graph.py:14`) |

## A.5 jiuwenswarm, the product

| Part | What it is and does | Where | How CC uses it |
|---|---|---|---|
| **Skills** | `SKILL.md` folders; the 34 bundled skills declare a name and description and nothing about inputs, outputs or effects | `resources/agent/workspace/skills/` | import sources, entering as provisional |
| **SkillPacks, Swarm Skills** | packs of skills listed by name; team skills with roles, a workflow and a `dependencies.yaml` whose entries carry a purpose | `server/runtime/skill/skillpack.py`; `docs/en/SwarmSkills.md:339-372` | packs become composites pinned by hash; team skills are not capsules in v1 |
| **Swarmflow** | deterministic multi-stage team workflows with parallel and pipeline operators (agent-core `agent_teams/workflow`) | `docs/en/TUISwarmFlowGuide.md` | one way the plan's fan-out could run |
| **TTSE, teammate experience** | evolution paths that keep facts and experience without review | `resources/config.yaml:732-733` | pinned per sprint as overlays, or not loaded |
| **Auto Permission** | classifies each tool call: a `ToolCapability` with category, operation family, resource class, `static_side_effects` and `risk_tier`, plus the call's read, write and external paths; medium risk routes to a reviewer, and decisions go to an append-only hashed audit. The facts are derived from tool names (`host_static`, `name_classification_hint`, `unknown`), and `permissions.enabled` is `false` by default | `agents/harness/common/rails/permissions/tool_capabilities.py:39-49`, `auto_decision.py:499-501`, `reviewer_route.py:230`, `persistent_audit.py`, `resources/config.yaml:1129-1132` | the nearest existing thing to declared effects: CC declares the same facts per capability, so they can be checked before selection rather than at the moment of the call |
| **Eternal Conversation** | an opt-in, hash-chained, append-only history of a session's tool calls and results | `agents/harness/common/rails/eternal_conversation/` | a durable record CC can read where a session opts in |

## A.6 AI4Research, the workflow CC extends

| Part | What it does today | Where | What CC changes |
|---|---|---|---|
| **Planner** | a model writes the plan (PlanIR) and may not name a capsule; a node no capsule can implement goes back for repair | `lib/elastic_planner.py:1328-1329`, `:4137-4146` | nothing: plan steps state needs, never capsules |
| **Hard filter** | removes capsules by types, effects in both directions, network, proof classes, trust and admission status; never reads preconditions | `lib/elastic_planner.py:4553-4648`; `lib/capability_admission.py:12-26` | adds declared preconditions, model limits, Standing and composition |
| **Selection call** | one model call reads the full rows of every node's eligible capsules and binds each node | `lib/elastic_planner.py:4678-4760` | the model reads only a summary and ports per node |
| **Freeze** | pins each node's capsule by manifest hash; aborts if a definition changed | `lib/execution_authority.py:28-94` | pins every body file and the Verdict, by snapshot |
| **Scheduler** | ready nodes in order, up to 8 in parallel, conflicting write scopes held back, one lease per operator | `lib/graph_scheduler.py:2179-2215`, `:3203`; `lib/operator_runtime.py:504-515` | unchanged; CC supplies declared constraints |
| **Dispatch** | resolves the capsule and checks four precondition kinds | `lib/operator_runtime.py:796-808`; `lib/capability_capsules.py:1220-1242` | the same predicates as the filter, on fresh state, and a hash check |
| **Evaluation plan** | compiles each node's gate from requirement checks, checks by type and the manifest's own claims | `lib/evaluation_plan.py:277-356` | three parts with named writers; judges get a standing |
