The `core/` SDK: two built-in agent types, a workflow engine, and one Runner that executes both.

## Two built-in agents

| Type | Code | Shape |
|---|---|---|
| **ReActAgent** | `core/single_agent/agents/react_agent.py` | *"Thought → Action → Observation"* loop, with tool calls and self-correction |
| **WorkflowAgent** | `core/application/workflow_agent/` | runs predefined workflows and can **switch between several workflows in one session**, resuming an interrupted one from its checkpoint |

Behind them: `BaseAgent` is the root. `ControllerAgent` (`core/single_agent/base.py:290`) is the base for `WorkflowAgent` and a third agent, `LLMAgent`, that the README does not mention. ReActAgent's `max_iterations` defaults to **5**. `core.single_agent` is the current API, and `core.single_agent.legacy` is kept only for compatibility. ⚠ The README quickstart still imports `WorkflowAgentConfig` from `legacy`.

## Card vs Config: the design rule that matters most

- A **Card** (`AgentCard`, `ToolCard`, `WorkflowCard`, `SysOperationCard`) is **static, serialisable identity metadata**, so it can cross process boundaries, including over A2A.
- A **Config** is a process-local runtime object that holds resources and state.
- It is an anti-pattern to put `session_id` or the runner inside a Card. — `.claude/rules/architecture.md`

Tools, workflows, agents and MCP servers are all **abilities**. They register through `AbilityManager` and `Runner.resource_mgr`, which is **process-global shared state**.

## Workflows

A workflow is a graph of components wired by `${node.field}` references:

```
flow.set_start_comp("start", Start(), ...)
flow.add_workflow_comp("llm", LLMComponent(cfg), inputs_schema={"query": "${start.query}"})
flow.set_end_comp("end", End(...), ...)
flow.add_connection("start", "llm"); flow.add_connection("llm", "end")
```

Component families are under `core/workflow/components/`:

| Family | Components |
|---|---|
| `flow/` | start, end, branch, loop |
| `llm/` | LLM call, ReAct, questioner, intent detection |
| `tool/` | tool call, HTTP request |
| `resource/` | memory write and retrieval, knowledge retrieval |
| `condition/` | expression, number and array conditions |

## How a run executes

1. Build cards and configs, then register the workflow or agent with `Runner.resource_mgr`.
2. `await Runner.run_agent(agent, inputs)`, or `run_agent_streaming` (the public `Runner` facade at `core/runner/runner.py:821,849`).
3. The graph runs on a **Pregel-style engine** (`core/graph/pregel/`): components run concurrently, values pass between them as batches or streams, and it can jump dynamically between nodes.
4. State is session-scoped. An interrupt, such as a questioner asking the user something or a tool confirmation, **pauses the run, and a later call on the same session resumes it** from the checkpoint. See [[Core 05 Session, Context, Memory]].

**Key point: agents and workflows share one engine, one Runner and one session model.** That is why a workflow can be a tool and an agent can be a component.

Next: [[Core 02 DeepAgent Harness]], which builds a much richer agent on top of ReActAgent.

Sources: README.md, AGENTS.md, .claude/rules/architecture.md, docs/en/2.Development Guide/{Agents,Workflows}/, docs/en/2.Development Guide/Advanced Usage/WorkflowAgent With Multi-workflow Switching.md, openjiuwen/core/{single_agent,application,workflow,graph,runner}/
