# Plan and schedule: a capsule holds no task, and the workflow keeps its shape

**A capsule is an abstraction: pulled from the library and told what to do through its inputs.** It never has a
task, a step or a place in a workflow written into it, so it stays the general tool for whatever step its ports fit.
The planner states what each node needs, capsules state what they can do, and only the Binding joins them. The
workflow keeps its stages, and its scheduler keeps order, parallelism and workers. Source of truth: `merged/SCHEMA.md`
§0.6, §3.4, §3.5, §4.3a.

## What a capsule does not hold

Invariant 12: a Declaration names no step, node, sprint, plan, workflow, stage or task type, no capsule to run before
or after it, and no worker. A capability valid only for some inputs says so with `needs.when` predicates over its
inputs, never with a task list.

Today's AI4Research manifests hold no step, node or sprint id, but they do hold uses (85 files, read at `b0bf165f9`):

| Today's field | How many | In the schema |
|---|---|---|
| `applicability.task_types` | 85 of 85 | kept only as import evidence; the task type lives on the Plan step |
| `composition.requires_after` naming another capsule | 42 of 85, e.g. `cap.research-report-draft` requires `cap.research-evidence-synthesis` | a data dependency through ports when an artifact connects them; otherwise the plan's `depends_on` |
| `operator_compatibility.preferred` | named worker operators | dropped; the workflow assigns the worker and the invocation records it |
| a workflow position in the name or description | 14 of 85: 11 in the name ("Fixed Research Evidence Synthesis"), 3 in the description ("Freeze the accepted Part A evidence … for Part B consumption") | a neutral `summary`, which may not name stages, workflows, tasks or other capsules |

## How a plan is put together and run (per sprint)

| # | Stage | Owner | What the schema supplies or records |
|---|---|---|---|
| 1 | write the plan | the planner | Plan steps: typed inputs and outputs, allowed effects, task type, `depends_on`, optional fan-out. No capsule names, as today (`elastic_planner.py:1328-1329`). The planner sees the library only as the set of port types available |
| 2 | repair against supply | the planner, from a code defect | a node no capsule chain can implement comes back as `CAPABILITY_IMPLEMENTATION_MISMATCH` (`:4137-4146`): supply reshapes the plan only through types |
| 3 | expand by composition | code | derived Plan steps (`derived_from`), each matched on its own; one capsule may fill several |
| 4 | offer and choose | the capsule layer's filter, then models | chapter "Pick": declared criteria first, then a choice from `summary` and `ports` |
| 5 | freeze | code | one Binding per step: `bound[]` (primary, context, dependency), fallbacks, overlays, all by hash |
| 6 | schedule | **the workflow's scheduler, not CC** | constraints only: declared write scopes, `resources` modes, and the gate's `parallel_safe` flag. The scheduler keeps topological order (`graph_scheduler.py:2179-2215`), its cap of 8, conflict hold-backs (`:3203`), worker leases and the step's retry count |
| 7 | dispatch | code | one **invocation** per actual run: predicates on fresh state, live hash equal to the pin, and a fallback run when the primary cannot run |
| 8 | gates and delivery | the workflow | each claim keeps the invocation that produced it |

**The planner never holds a list of capsules to schedule.** It says what a node needs; the offer, the freeze and
dispatch fill it. Registered workflows that name capsules per stage today (`allowed_capsules`) keep that as
`restrict_to[]` on the Plan step: a choice on the demand side, never stored on the capsule.

## Real multiplicity

| Relation | Cardinality |
|---|---|
| name to Declarations | 1 : N versions over time; 1 : 1 within a sprint (its snapshot); concurrent sprints may run different versions |
| Plan step to Binding | 1 : 1 per sprint |
| Binding to capsules | 1 : N: one primary, any context capsules, closed dependencies, pre-approved fallbacks |
| Declaration to Bindings | 1 : N: one capsule serves many steps, plans and sprints |
| Binding to invocations | 1 : N: fan-out items × attempts × fallbacks |
| composite to members | 1 : N, keyed by role; one Declaration may fill several roles |

**Fan-out.** A Plan step may declare `over: {input, max_parallel}` and `gather: {mode: all | best_effort, min_items}`. The capsule's port takes one
item; each item is one invocation with an `item_key`. **The capsule never knows it is mapped.** Items run in parallel
up to the smallest of `max_parallel`, the sprint's cap and the free workers, and one at a time if the capsule is not
`parallel_safe`. Effect scopes may use `{instance}`, so parallel items never write the same place. A capsule whose
port takes a whole collection is bound without `over`: the types decide. Today there is no fan-out: a `many` output
is one run writing a directory (`elastic_planner.py:1366-1378`). When items fail, `gather.mode` decides: `all` (the
default) fails the step, `best_effort` passes the successes and lists the failures, down to `min_items`. The step's
gate checks the gathered manifest in code before anything downstream reads it.

**Still six records.** The Binding is written by the freeze; its `invocations[]` are appended by dispatch. Today
attempts overwrite a mutable state file that keeps the last 20 (`task_lifecycle.py:54-56`), and frozen fallbacks are
never read at run time.

## Where it lives in openJiuwen

CC adds records and checks, and uses openJiuwen's own layers and names for everything else. **Reuse comes first:**
what CC adds new is only the Declaration format, the records, one shared predicate evaluator, the admission gate, judge
standing and the tree index. The structure is the one
recorded in the tundle obby vault; the full table is `merged/SCHEMA.md` §4.17a.

| CC part | The openJiuwen piece it uses | How it fits |
|---|---|---|
| **Declaration** | the **Card** side of openJiuwen's Card-versus-Config rule (`ToolCard`, `AgentCard`, `WorkflowCard`; `.claude/rules/architecture.md`) | a Card is static, serialisable identity, and putting a session id or runner in one is an anti-pattern. Invariant 12 is the same rule: the Declaration is card-like and every use lives in run records. It adds what cards lack: preconditions, effects, trust |
| **loading a capability** | `AbilityManager` and `Runner.resource_mgr` for core abilities (tools, workflows, agents, MCP); `harness/extension_binder` for harness extensions; `create_harness(manifest, provider=...)` for agent templates | the same registration paths, fed from CC's hashed store |
| **Plan steps, scheduling, fan-out** | whichever engine runs the AI4Research plan: today its own graph scheduler; on openJiuwen a core workflow graph (Pregel), Agent Teams tasks, or a Swarmflow script with parallel and pipeline operators (agent-core `agent_teams/workflow`, surfaced by jiuwenswarm) | CC does not change with the engine; fan-out is Swarmflow's parallel operator or a workflow loop |
| **invocation** | the harness protocol: a capsule run as an agent is one **Turn** (exactly one start and one terminal event; `TurnResult` with usage and exact cost); a tool capsule's call is one provider **item** (`ItemLifecycleEvent`) | one invocation per Turn or item. A pause and resume stays one invocation, since `PAUSED` and `RESUMED` keep the same Turn; a retry after a terminal event is a new one (**design**, following the one-terminal-event rule). `observed_cost` comes from `TurnResult`; the event sequence and correlation ids are its trace |
| **trajectories** | `agent_evolving`'s canonical OTLP `Trajectory`, and Symphony's trajectory v2 evidence format | consumed, not redesigned: `trajectory_ref` points at one |
| **durable records** | `TrajectoryStore` and `LoadRecord` (in memory); jiuwenswarm's hash-chained Eternal Conversation history where a session opts in; checkpointers (`core/session/checkpointer`, Redis in `extensions`), which resume a run after a crash but do not record what ran; openJiuwen's pluggable stores in `extensions` (DB, KV, vector) | a capsule-layer rail writes Bindings and invocations durably, into openJiuwen's own stores rather than a new database |
| **judges** | the harness's built-in `verification` subagent (spec S_18); `agent_evolving`'s evaluators; Symphony's evaluation metrics (six of nine are model judges, off by default); AI4Research's 20 semantic registry checks and its default `llm_eval` gate | each is a judge with a standing per model and artifact type (§4.5c): it gates from day one, spot checks calibrate it, and only a measured one certifies (**design**) |
| **effects and approvals** | the harness `PermissionEngine` (`ALLOW`, `ASK`, `DENY`) with `PermissionInterruptRail`, and jiuwenswarm's policy mapping severity to them; `SysOperation` sandboxes with `SYSTEM`, `SESSION` or `CUSTOM` isolation, such as jiuwenbox | an irreversible, high-severity effect is an `ASK`, and `DENY` on an unattended run; an `{instance}` scope is a per-invocation `SESSION` sandbox. Permissions are off by default in jiuwenswarm, so a CC sprint turns them on |
| **ToolCard flags** | `exposure`, `parallel_safe`, `stateless`, `idempotent` | computed by the gate from the declared effects and `effect_class`, never trusted as written |
| **context taint** | Session VCS: `commit`, `snapshot`, `rewind`, `fork` | a context that held a revoked hash is not reused: the next invocation starts a new session, or forks from a snapshot taken before the capsule loaded (**design**) |
| **generalists** | `harness_providers`: `native`, `claudecode`, `codex`, `dsh`, behind `HarnessProtocol`; Agent Teams' `external_cli` role | each generalist's carrier is an `AgentTemplateSpec` naming a provider; enrolment checks the host capabilities its `HarnessCard` requires |
| **remote bodies** | A2A `AgentCard` (`extensions/a2a`); MCP servers | `remote_fingerprint` hashes the card or the tool listing |
| **overlays** | the experience layer (`evolutions.json`), written through `agent_evolving`'s `EvolutionStore` after preview and approval; the TTSE bank | pinned per sprint, or not loaded |
| **the tree, RSI** | agent-core's `rsi/harness_rsi` and its tree nodes (`RsiTreeNode`, `rsi/schema.py:96-111`), which jiuwenswarm projects for its web view (`agents/harness/common/rsi/models.py:292`); `agent_evolving`'s candidate validation from one snapshot | `builder_ref` joins RSI's tree; RSI's gate is builder evidence, and CC's gate admits |
| **Symphony** | `CapabilityProvider`, `SkillGraphUpdater` (above) | CC decides what Symphony may index |
| **prod-eligibility** | openJiuwen's aim for production use: globally unique identity, effects declared across hosts, admission records others can audit, no assumption that a person is watching | `decl_hash`, `ext:` effects, Verdicts, unattended runs |

**Names.** openJiuwen's vocabulary is `Session > Turn > Step`, with `Round` reserved for multi-agent phases. Three CC
terms sit beside it and must not be confused with it:

| CC term | Means | Not to be confused with |
|---|---|---|
| **Plan step** | one node of the AI4Research plan (`step_id`) | an agent-core **Step**, one cycle of an agent loop |
| **invocation** | one actual run of a capsule for a Plan step: a Turn for an agent capsule, an item for a tool capsule | a Turn or item that is not a capsule run |
| **capability** | anything an agent can call on; openJiuwen calls tools, workflows, agents and MCP servers **abilities**, and a capsule wraps one ability or skill | a Card, which is only its identity |

## Why it is done this way

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| no task, step or neighbour in the Declaration | a use written into a capsule makes it specific, and puts plan facts where the builder, not the planner, writes them (invariant 9, **design**). Today 42 manifests fix their predecessor inside the capsule |
| match on declared contracts and ports, not task labels | filtering on declared preconditions and effects reached 0.980 success at 2,528 tokens a task, a keyword filter 0.620 (Contract2Tool, 2606.07904 Table V) |
| order comes from typed data edges or the plan | typed edges between capabilities repair locally (GraSP, 2604.17870); guessed edges are an observation |
| one invocation per run, with its step identity | a change must invalidate exactly the downstream runs (Execution lineage, 2605.06365 p6-7); fan-out and retries must be counted to judge a capability fairly |
| context capsules recorded per Binding | severe drift rose with the number of skills loaded together (SkillFuzz, 2607.02345 Fig. 6), so what shared a context must be known |
| the scheduler stays the workflow's | CC is a scheme, not a tool (supervisor, 2026-09-21); the workflow already orders, caps and leases (`graph_scheduler.py`), and CC only supplies declared constraints |
