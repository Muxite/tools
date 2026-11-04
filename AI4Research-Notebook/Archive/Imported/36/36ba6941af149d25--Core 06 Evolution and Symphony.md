Self-improvement code lives in four places. User documentation is uneven.

| Home | What | User docs |
|---|---|---|
| `harness/rails/evolution/` | **online** rails: skill evolution, team skill evolution, context evolution (`metis_context_evolve_rail`, which the docs call "Metis Task Memory"), TTSE, trajectory capture, Symphony graph evolution | Self Evolution chapter |
| `agent_evolving/` | the machinery: `Trainer`, evaluators, optimisers (llm, tool, memory, skill), `Updater`, the canonical OTLP `Trajectory`, signals, experience lifecycle, checkpointing, offline and online RL (`agent_rl/`) | API docs, Self Evolution |
| `rsi/` | *"Recursive self-improvement for standalone Expert Harnesses"*: `harness_rsi/` (the auto-harness orchestrator, stages, pipelines) and `artifact_rsi/` (`paper_opt` auto-research, and `program_opt`, which builds on the pinned `agentdescent==0.4.6`) | auto-harness: API docs, under the old name `openjiuwen.auto_harness`. ⚠ `artifact_rsi`: **none** |
| `symphony/` | capability assets — see below | ⚠ package README only |

## Three evolution chains (`agent_evolving/AGENTS.md`)

1. **Classic parameter optimisation**: `CaseLoader → Trainer predict/evaluate → Trajectory → Updater → candidate → validation → checkpoint`. Candidates start from the same snapshot, are validated independently, and the best one is restored.
2. **Online skill experience**: `trajectory/review/evaluation → EvolutionSignal → optimiser → local preview → approval → EvolutionStore`. A restricted **review agent** gets read-only evidence tools, and it cannot use the main agent's write tools.
3. **Reinforcement learning**: offline with verl rollouts, or online with rails collecting through a gateway, a judge and a scheduler. An env var enables it (`USE_RL_ONLINE_RAIL=1`).

**Key point: an evolved skill is an experience layer, not a rewrite.** Experience goes into `evolutions.json` under the skill directory, and `SKILL.md` is not edited automatically: only a user-initiated `/evolve_rebuild` archives the skill and rewrites it. Automatically generated experience *"usually"* needs **user confirmation before writeback**. So the documented default is to confirm first, but "usually" is not a guarantee. [[Swarm 03 Skills, Symphony, Self-Evolution]] lists the paths that skip review. — `Self Evolution/Skill-Online-Self-Evolution.md:218-256`

## Symphony: capability assets (`symphony/`)

Symphony is a domain module for **skills, agents and other capabilities**. It covers **fingerprint** (semantic profile, normalised IO and tags, `fingerprint.json`), **retrieval** (a browsable capability tree), **orchestration** (a relation graph with Fast and Beam planners producing execution routes), **experience** distilled from trajectories, and **evaluation** (static and trajectory metrics with evidence). Consumers connect through an **Adapter**, and they keep ownership of install, permissions, sessions and UI. See [[openJiuwen Landscape]].

⚠ **Its status table is stale.** It lists retrieval and the Agent Toolkit as *"to be migrated in"*, but `symphony/retrieval/` already holds about 21k lines and `AgenticSkillRetrievalToolkit` exists (`symphony/agent/retrieval_toolkit.py:154`).

## Other extension points

`extensions/` holds A2A client and server; stores (DB, KV, vector); a Redis checkpointer; sandbox providers (`aio`, `jiuwenbox`, `yuanrong`); a Pulsar message queue; OTel tracing; and vendor adapters. ⚠ `extensions/harness/` is an empty package. `dev_tools/` holds the agent and prompt builders, skill creator and evaluator, and tuning.

Sources: openjiuwen/agent_evolving/AGENTS.md, openjiuwen/rsi/__init__.py, openjiuwen/auto_harness/__init__.py, openjiuwen/symphony/README.md, openjiuwen/symphony/{retrieval,agent,orchestration}/, openjiuwen/harness/rails/evolution/, docs/en/2.Development Guide/Self Evolution/Skill-Online-Self-Evolution.md, openjiuwen/extensions/, pyproject.toml
