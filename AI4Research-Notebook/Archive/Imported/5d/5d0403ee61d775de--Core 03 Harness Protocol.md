`openjiuwen.harness_protocol` is a **provider-neutral SPI** that lets openJiuwen host a *third-party* agent harness, such as Claude Code, Codex or DeepSeek-harness, as easily as its own DeepAgent. Contract version `1.0`. The package holds only contracts and frozen value objects, and the implementations live in `harness_providers/`.

```text
openJiuwen host / runtime adapter
              |
       HarnessProtocol
              |
Claude Code / Codex / Jiuwen DeepAgent / DeepSeek harness / other
```

## Vocabulary

`Session > Turn > Step`. A **Turn** runs from one external input to a stable external output. A **Step** is one agent-loop cycle. Tool calls, commands, file changes and subagents are **provider items** inside a turn, and are not steps. `Round` is reserved for multi-agent phases.

## Three planes, kept apart

| Plane | Direction | Carries |
|---|---|---|
| **observation** | harness → `events()` → host | an ordered, correlated event stream |
| **interaction** | harness → handler → response | tool approvals, user input, MCP elicitation |
| **hooks** | harness → hook → policy result | lifecycle policy callbacks |

An event consumer never answers anything. Anything that blocks goes through the interaction handler.

## Main types

`HarnessProtocol` covers lifecycle, send (steering is `send` with `DeliveryMode.STEER`), abort/pause/resume, `events()` and `turn_events()`, and checkpoint export. `HarnessProvider` validates config and builds the harness. `HarnessCard` declares identity, protocol version and required host capabilities. `HarnessContext` carries the tools, MCP, hooks, interactions and checkpoint storage that the host injects. `TurnResult` is the typed terminal result, with messages, usage, **exact monetary cost** and timing. `HarnessCheckpoint` is versioned, monotonic and pushed idempotently to a sink.

## Events

The events are defined in `harness_protocol/events.py`:

- `TurnLifecycleEvent`, of kind `TurnEventKind`: **started, paused, resumed, finished, aborted, failed** (`:23`). Every turn emits exactly one `STARTED` and exactly one terminal event.
- `ItemLifecycleEvent`, of kind `ItemEventKind`: **started, updated, completed** *"for a provider item such as a tool call"* (`:101,148`). Its payload keeps the item's native shape.
- Output, usage-updated, state-changed, hook-observed, diagnostic, provider and unknown events.

Every event carries a strictly increasing sequence number, a `correlation_id` and `causation_ids`. Buffers are bounded, and **required events are never dropped**.

⚠ **This bears on H5 in [[Dependencies]].** Turn events cover only the lifecycle, but there are also per-tool-call **item events**, alongside the harness's observability spans. Both are reported by the harness or provider itself. Nothing attests that the record is complete, and neither sees the file writes or network traffic of code a tool runs. So a tool-call-level record exists, while an effect-level or verified record is still ours to build.

## Built-in providers (`harness_providers/`)

Factory names: `native` (DeepAgent), `native_v2` (team-side), `claudecode` (over `claude-agent-sdk`), `codex` (over `openai-codex`) and `dsh` (over deepseek-harness). Every provider subclasses `SerializedTurnHarness`, which owns the state machine and turn queue. `create_harness(manifest, provider=...)` builds one from an AgentTemplate manifest. `HarnessIOAdapter` maps the protocol onto the DeepAgent I/O contract, which is how **Agent Teams run Claude Code and Codex as team members** ([[Core 04 Multi-Agent and Teams]]).

⚠ `docs/dev/harness_protocol_integration.md:9` still says the Claude Code and Codex backends are *"not yet migrated"*, but both already exist as `SerializedTurnHarness` providers.

Sources: openjiuwen/harness_protocol/{README.md,AGENTS.md,events.py}, openjiuwen/harness_providers/AGENTS.md, `ls openjiuwen/harness_providers/`, docs/dev/harness_protocol_integration.md
