How a request becomes an agent. Everything here runs on agent-core's [[Core 02 DeepAgent Harness]] and [[Core 04 Multi-Agent and Teams]].

## Modes

Mode strings have three segments, `<category>.<profile>.<plan>`: 8 canonical modes, defined in `jiuwenswarm/common/mode_matrix.py`.

| Segment | Values |
|---|---|
| category | `agent` = one agent · `team` = cluster, a Leader plus members |
| profile | `work` = the DeepAgent profile · `code` = the Code adapter, with coding memory and a project directory |
| plan | `normal` = executable · `plan` = read-only planning, where execution needs `exit_plan_mode` approval |

The Web UI mode selector offers **Agent mode** and **Cluster mode** (plus an `auto_harness` mode). ⚠ The README labels Cluster "(default)", but the frontend defaults to **Agent** (`frontend/src/stores/sessionStore.ts:220`). The README also describes two spaces, **Work** and **Code**. IM channels and the TUI use `/mode`. Legacy strings (`agent`, `code.normal`, `code.team`, `team`) are silently mapped to canonical ones (`docs/en/Modes.md`).

## Adapters, where the product meets agent-core

`server/runtime/agent_adapter/`:

- `JiuWenSwarmDeepAdapter` (`interface_deep.py:1787`) is the work profile. It calls agent-core `create_deep_agent(...)` and mounts the product rails.
- `JiuwenSwarmCodeAdapter(JiuWenSwarmDeepAdapter)` (`interface_code.py:502`) is the code profile, which adds `CodingMemoryRail` and code tools.
- Permission dispatch, the output handoff and evolution slash commands live alongside them.

Product-side rails are in `agents/harness/{common,work,code,team}/rails/`: ask-user, avatar, stream events, execution guard, permissions, project memory, eternal conversation, Symphony, skill-retrieval prompt. A warm pool (`agent_warm_pool.py`) pre-creates agents to cut cold-start time.

## Teams (Cluster mode)

- `TeamManager` (`agents/harness/team/team_manager.py`) normalises config and builds an agent-core **`TeamAgentSpec`**. The Leader decomposes the task and assembles members, and the members work and report back.
- **Distributed mode**: `team.runtime.mode: local | distributed`, `team.runtime.role: leader | teammate`, transport `inprocess | pyzmq`. There is no separate binary. Each node is an ordinary AgentServer with a role-specific config. Teammates register idle nodes in an **A2X registry**, and leaders reserve them. ⚠ **The registry is not bundled**: you deploy it yourself from agent-protocol's `feature/Agentregistry` branch. Distributed mode allows **one active team session per channel**. — `docs/en/DistributedTeam.md`
- **Human in the Team (HITT)**: human seats in a team, which people join from Feishu or Xiaoyi with `/join`.
- **Swarmflow**: the Leader runs a **Python workflow script** (`META={…}` plus `async def run(args)`) through `SwarmflowTool`. Scripts get operators such as `agent(...)` (a one-shot worker), parallel and pipeline steps, and `human` HITL nodes, with a team token budget. The engine is in agent-core `agent_teams/workflow/`. A script can be written on the fly by the Leader, packaged as a **Swarm Skill**, or authored offline.

**Key point: Coordination Engineering is the product's framing.** `docs/en/AgentTeam.md` §1.3 contrasts *"Harness Engineering (harnessing a single agent)"* with *"Coordination Engineering (orchestrating collaboration)"*, and the team is what they ship.

Sources: docs/en/{Modes,AgentTeam,DistributedTeam,AgentTeamHumanInTheTeam,TUISwarmFlowGuide}.md, jiuwenswarm/common/mode_matrix.py, jiuwenswarm/server/runtime/{agent_adapter/,agent_manager.py,agent_warm_pool.py}, jiuwenswarm/agents/harness/{team,common,work,code}/
