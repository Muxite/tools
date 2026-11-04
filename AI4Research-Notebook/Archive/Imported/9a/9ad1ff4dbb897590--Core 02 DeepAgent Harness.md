`openjiuwen.harness` is a *"coding-agent framework built on core primitives (`ReActAgent` / `AgentRail` / `Runner` / session)"*. It gives a **deep agent** the full loop: model calls, tool execution, rails, subagents, a task loop, a workspace and a permission engine. It is the engine under [[Swarm 00 Overview]].

⚠ It is **top-level `openjiuwen.harness`**, not part of `core/`. The user guide has no dedicated chapter on it. It appears only in the API page, the *Tool permissions* guide, *DeepAgent Reinforcement Learning* and the LSP-agent guide. The real documentation is `harness/AGENTS.md` plus design specs `S_01`–`S_19` in `harness/docs/specs/`.

## Construction

- `create_deep_agent(model, *, card, system_prompt, tools, mcps, subagents, rails, enable_task_loop, ...)` is the **only** public way to build one. New options go into `DeepAgentConfig`, not into more arguments.
- `DeepAgent` exposes `invoke`, `stream`, `follow_up`, `steer`, `abort`, `run_one_round`, `save_state`, `load_state` and `switch_mode`, plus plugin and template loading. Its config can be hot-reloaded.
- `DeepAgent` subclasses `BaseAgent` and **wraps an inner `ReActAgent`** (`deep_agent.py:51,295`). The DeepAgent adds an outer **task loop** (`task_loop/`) around ReAct iterations.

## Rails: the extension mechanism

A rail is a class of lifecycle hooks. It can register tools, inject prompt sections, rewrite inputs, block execution and feed instructions back in. Each rail's hooks are routed to one of two namespaces:

| Events | Handled by |
|---|---|
| before/after model call, before/after tool call, tool and model exceptions, after ReAct iteration, user message | the inner `ReActAgent` |
| before/after invoke, before/after task iteration | the outer `DeepAgent` |

The built-in rails are in `harness/rails/`: security, interrupt (confirm, ask-user), memory (memory, coding and external memory), context engineering, skills, subagent, task planning, task completion, tool-call resilience, MCP, LSP, heartbeat, and **evolution** (skill evolution, team skill evolution, TTSE, trajectory, the Symphony graph evolution rail). **Most product features are rails, not forks of the loop.**

## Tools and subagents

- **Tools** (`harness/tools/`): filesystem, shell, web, worktree, todo, cron, goal, memory, skills, MCP, LSP, subagent, browser, mobile GUI and tool discovery.
- **Built-in subagents** (`harness/subagents/`): browser, code, explore, plan, research, verification and mobile-GUI.
- **Workspace**: this limits what the agent can read and write.

## Tool permissions

`PermissionLevel` has three tiers: **`ALLOW` / `ASK` / `DENY`** (`harness/security/permission_engine/models.py:19`).

| Piece | Role |
|---|---|
| `PermissionEngine` | holds the policy (`tiered_policy`: per-tool levels, defaults, rules, overrides) and evaluates each call |
| `PermissionInterruptRail` | runs `before_tool_call` on **every** tool. A result of `ask` raises a Confirm interrupt |
| `ToolPermissionHost` | injected by the product: the YAML policy path, hot snapshots, ACP, persistence and workspace |
| `SecurityRail` | adds safety prompts. The docs separate **guardrails**, which cover *content* safety, from **permissions**, which cover *execution* control |

Permissions are **off by default**. The rail is built only when `permissions["enabled"]` is true.

**Key point: the harness decides whether a tool call may run.** It does not keep an attested record of what ran. For that, see [[Core 03 Harness Protocol]].

Sources: openjiuwen/harness/AGENTS.md, openjiuwen/harness/rails/AGENTS.md, openjiuwen/harness/deep_agent.py, openjiuwen/harness/{rails,tools,subagents,security}/, docs/en/2.Development Guide/Tool permissions and host integration.md, .claude/rules/architecture.md
