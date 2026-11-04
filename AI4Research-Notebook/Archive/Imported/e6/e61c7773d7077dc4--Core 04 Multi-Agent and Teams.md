There are two separate mechanisms, and they are easy to conflate. The Runner's team facade can run either one. It defaults to Agent Teams, and `base=True` selects a multi-agent `BaseTeam` (`core/runner/team_runner.py:12-15`). A `BaseTeam` can also be called directly with `team.invoke()` or `team.stream()`.

| | **Multi-Agent** (`core/multi_agent/`) | **Agent Teams** (`agent_teams/`) |
|---|---|---|
| Abstraction | `TeamRuntime` for communication, plus `BaseTeam` | a **Leader** and **Teammates**, built with `TeamAgentSpec(...).build()` |
| Messaging | in-process `MessageBus`: point-to-point and pub-sub. `CommunicableAgent` mixin adds `send`, `publish`, `subscribe` | a message bus plus a **task database**. Transport is `inprocess` or `pyzmq`, so it can span processes and hosts |
| State | in process, over `TeamRuntime`. The docs describe no persistence layer | persisted to `sqlite`, `postgresql` or `memory`: team, tasks, messages |
| Lifetime | not documented | temporary, or **persistent** with standby, resume and crash recovery |
| Patterns | handoff, hierarchical-via-tools, hierarchical-via-msgbus (`SupervisorAgent`), and **Agent as Tool** | leader decomposes → teammates claim tasks → leader reviews |

## Agent Teams in outline

- The **Leader** decomposes the task, assigns work, approves results and manages member lifecycles. **Teammates** execute and report through messaging.
- **Execution modes**: *Plan*, where the leader must approve before a teammate completes, and *Build*, the default, with no approval.
- **Spawn modes**: *Process*, the default, where each teammate is a subprocess, and *Inprocess*, with asyncio coroutines. The leader health-checks teammates and restarts them.
- Users can `@member` a teammate directly. Members can be predefined to skip dynamic spawning.

`TeamRole` has **seven** values (`agent_teams/schema/team.py:81`): `leader`, `teammate`, `human_agent` and `passive_human` for humans in the team (HITT), `bridge_agent` (paired with a remote agent over a pure-text protocol), `worker` (single-shot and stateless, for swarmflow), and `external_cli` (a Claude CLI or Codex CLI subprocess as a full teammate). ⚠ The Chinese architecture design doc in `agent_teams/docs/` lists only the first three.

**Key point: Agent Teams is where heterogeneous harnesses meet.** Through [[Core 03 Harness Protocol]], a team can mix DeepAgents, Claude Code and Codex members under one leader. **Team Skill Evolution** turns a successful collaboration into a reusable team skill, covered in [[Core 06 Evolution and Symphony]].

Terminology, `agent_teams/AGENTS.md`: `Session > Turn > Iteration > Step`, where `Round` is a multi-agent phase that contains several agents' turns.

Sources: docs/en/2.Development Guide/Multi-Agent/{Overview,Preset Collaboration Patterns}.md, docs/en/2.Development Guide/Agent Teams/Overview.md, openjiuwen/agent_teams/AGENTS.md, openjiuwen/agent_teams/schema/team.py, openjiuwen/core/multi_agent/{team.py,team_runtime/,teams/}
