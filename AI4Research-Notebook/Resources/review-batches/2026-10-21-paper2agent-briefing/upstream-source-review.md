---
id: paper2agent-briefing-upstream-source-review
status: source-review
source: Local Git checkouts and source at the revisions recorded below; Planner Capability Gaps evidence snapshot
last_reviewed: 2026-10-21
next_action: Recheck exact source blobs at implementation checkout before relying on interface claims
---
# Upstream source review: agent architecture

Read-only source inspection; no runtime execution. This record distinguishes actual upstream repositories, the AI4Research modified checkout, and the OpenJiuwen pin used by captured M1.

| Source | Identity and revision | Use in this review |
|---|---|---|
| Modified AI4Research `jiuwenswarm/` | Remote `Stellven/jiuwenswarm`; branch `ai4r_muk`; HEAD `889682f0afc3d06c2ad88e71534483a31d2eb560`; working tree has modifications/untracked files | Design work only; not original upstream |
| Captured M1 implementation | `AI4Research-Development/jiuwenswarm-m1-review-d3d7f56`; remote `Stellven/jiuwenswarm`; detached HEAD `d3d7f565c6c05ccf764fe0780fde149b7dc89b95` | Evidence for current M1 adapter settings |
| Actual upstream JiuwenSwarm checkout | Remote `openJiuwen-ai/jiuwenswarm`; clean `develop`; HEAD `02b37f47fbefe80a58e4ed88606120818ca44ac3` | Source inspection only; team assembly/provider design |
| OpenJiuwen agent-core current checkout | Remote `openJiuwen-ai/agent-core`; clean `develop`; HEAD `e23806c1073275780dced2b71ddd592ffb0a21fd` | Current local checkout; differs from M1 reviewed pin |
| OpenJiuwen agent-core reviewed pin | `9e3390195a9ea15235b2b5f7412cb2aa440622cc`, commit object present locally; identified as M1 pin in amendment evidence | Pin-specific interface evidence; do not substitute current `develop` |

## Native interface evidence at the reviewed pin

The notebook's [Planner Capability Gaps evidence](../../../Amendments/Planner%20Capability%20Gaps/Evidence.md) records pin-specific source blob hashes and line references. It identifies `openjiuwen/agent_teams/harness/native_harness.py:288-297` for `LeaderHarness.run_once`: it bypasses the supervisor and invokes the Deep Agent; `DeepAgentSpec.enable_task_loop` determines whether that invocation performs one ReAct round or self-drives its task loop. This is an invocation interface, not proof of durable coordinator state across separate user requests.

At the same pin, `openjiuwen/agent_teams/workflow/engine/backends/base.py:39-47,118-135` defines the `AgentBackend.run(...)` seam, while `engine/runner.py:294-312` exposes `run_workflow` controls for backend, cap, admission, resume/journal/WAL, budgets, abort and progress. M1 reuses this for a deliberately serial frozen workflow. It is the better existing seam for bounded DAG episodes, not an outer goal loop.

The pinned `openjiuwen/symphony/interfaces/capability.py:13-34` defines `CapabilityProvider` and `AtomicCapabilityProvider` inventory/snapshot interfaces. Capability descriptors/fingerprints provide source identity and graph semantics, but are not effect isolation or authority. At the reviewed pin, F37 (`agent_teams/docs/features/F_37_swarmflow-stateful-sessions-and-human.md`) describes stable session context/checkpoint recovery; it explicitly leaves cross-process/restart persistent checkpointer wiring unresolved. F38 (`F_38_swarmflow-journal-persistence.md`) adds a separate workflow execution journal; it does not itself persist the user's goal or hypotheses. The Team `SessionManager` in `agent_teams/agent/session_manager.py` binds session lifecycle and checkpoint state. These pin-supported pieces are useful substrates, but do not constitute the proposed user-facing coordinator. Actual upstream JiuwenSwarm HEAD contains provider-based team assembly in `jiuwenswarm/agents/swarm/assembly.py`; agent-core also has managed subagent lifecycles under `openjiuwen/harness/subagent_runtime/`.

## M1 configuration evidence

In the captured implementation `jiuwenswarm/research/native.py`, lines 16-28 pin-check installed `openjiuwen` `direct_url.json` against `9e3390195a9ea15235b2b5f7412cb2aa440622cc`. Lines 41-77 adapt `run_workflow` to a frozen serial order, cap one, zero retries, and no resume/journal/WAL. Lines 80-114 implement an audited text-only bridge allowing one model invocation and rejecting tool calls and other modalities. Lines 117 onward build `TeamAgentSpec` with `DeepAgentSpec`; tools, MCPs, subagents, rails, and skills are empty, task loop and planning are disabled, and subagent runtime/async subagents and skill discovery are disabled. These are explicit M1 restrictions. They do not show that the upstream native runtime lacks these interfaces.

Do not generalize the Planner's restrictions to all agents. The current M1 Builder design uses one synchronous Codex CLI invocation per CC call, with a bounded internal tool loop (40 calls), confined POC workspace, and network disabled for tool commands. See the modified design checkout's [D43/D45 record](../../../../jiuwenswarm/docs/architecture/design-package/method/decisions.md#d43). This Builder loop is its own governed CC action, not arbitrary nested CC dispatch or a persistent coordinator.

## Design consequence and limit

Reuse the pin guard, governed bridge, `AgentBackend` workflow seam, and capability snapshot concepts. For the coordinator, add a separate host-managed goal/session record and invoke its turn between completed episodes or bounded individual actions. Preserve host ownership of policy, grants, binding, dispatch, budgets, checking, and release. Native APIs do not establish safe effects, hidden-call mediation, durable goal semantics, or product acceptance. This review is source-level only.

The [source receipt](source-receipt.json) separately records our two modified checkouts, the original upstream checkout, current agent-core HEAD, nine selected working-source hashes, and five exact Git blobs at the M1 dependency pin. Source hashes identify the inspected material, not runtime acceptance. Bulk reading/writing used `gpt-6-luna`; the coordinator/restructuring assessment used `gpt-6.1-sol`.
