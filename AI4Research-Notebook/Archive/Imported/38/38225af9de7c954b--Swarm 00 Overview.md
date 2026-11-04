**jiuwenswarm** is openJiuwen's flagship DeepAgent product: a multi-agent assistant that runs on one machine or across a cluster, and that you reach from a browser, a terminal, an IDE or chat apps. Read from commit 02b37f47f, 2026-09-21.

## In their words

> *"an Agent system that makes multi-agent collaboration truly work… drive multi-agent collaboration, Skill self-evolution, and tool invocation through natural language — delivering end-to-end from intent to result."* — `README.md`

The headline features, per the README: Leader-led **multi-agent teams**, a **distributed swarm** across processes and machines, **Swarmflow** (deterministic multi-stage Python workflows), **skill self-evolution**, **Swarm Skills Hub** sharing, **Auto Harness**, and **tool permissions**.

## Shape in one paragraph

Channels and frontends feed a **Gateway** process. The Gateway normalises every message into an **E2A** envelope and sends it over WebSocket to an **AgentServer** process. The AgentServer resolves the session and mode and runs an **adapter**, which builds an agent-core **DeepAgent** or **Agent Team**. Almost all agent behaviour comes from [[Core 00 Overview|agent-core]]: the harness, rails, teams, Symphony, evolution. jiuwenswarm adds the processes, channels, config, UI, sandbox and product-level rails. See [[Swarm 01 Processes and Message Flow]].

## Dependency on agent-core

`openjiuwen @ git+https://gitcode.com/openJiuwen/agent-core.git@b6db2733…`, **pinned to a git commit**, not a release (`pyproject.toml:20`). `uv.lock` records that commit as `openjiuwen` 0.1.18. ⚠ The commit, from 2026-09-20, is on **`origin/release/v0.1.19` only, not on `develop`**, so the agent-core the product runs is slightly different from the `develop` HEAD that the [[Core 00 Overview|Core notes]] were read from (e23806c1). Of the siblings in [[openJiuwen Landscape]], it is the heaviest user of the SDK: it imports from core, harness, agent_teams, rsi, extensions, symphony and agent_evolving.

## Naming, which is inconsistent

- ⚠ The **distribution name in `pyproject.toml` is `workswarm` 0.2.5.beta1**, after the commit *"feat: rename workswarm"* (2026-08-17). The README still says `pip install jiuwenswarm`, and the Python package and all CLI commands are still `jiuwenswarm*`. The unified facade class is `JiuWenSwarm` (it routes to the adapters), and older docs say "JiuwenClaw".
- The website's vocabulary is now in the repo too. "WorkSwarm" is the package name, and "Coordination Engineering" appears in `docs/en/AgentTeam.md` §1.3.

## Read order

[[Swarm 01 Processes and Message Flow]] → [[Swarm 02 Modes, Agents and Teams]] → [[Swarm 03 Skills, Symphony, Self-Evolution]] → [[Swarm 04 Memory and Context]] → [[Swarm 05 Channels, Protocols, Sandbox]]

**Key point: jiuwenswarm is a product shell around agent-core.** To learn how agents work, read [[Core 02 DeepAgent Harness]] and [[Core 04 Multi-Agent and Teams]]. To learn how requests reach agents, read the Swarm notes.

Sources: README.md, pyproject.toml, docs/en/SUMMARY.md, docs/en/AgentTeam.md, .doc_project_maintainer/project/overview.md, `git log -S'name = "workswarm"' -- pyproject.toml`
