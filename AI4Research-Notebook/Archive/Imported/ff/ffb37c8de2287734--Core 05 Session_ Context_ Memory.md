Four separate concerns: session state, the model's context window, long-term memory, and where tools actually execute.

## Session and checkpoints (`core/session/`)

- Each run has a session that carries state, streaming, interrupts and tracing. The docs cover State Management, Interruption Resumption, Streaming Output and Tracing.
- **Checkpointers** save state at key execution points so a run can resume after an interrupt or a crash. The in-memory and persistent ones are in `core/session/checkpointer/`, and Redis is in `extensions/checkpointer/redis`.
- **Session VCS** (`core/session/vcs/`): version control for the **LLM context itself**. It keeps a message-level, append-only WAL, and supports `commit`, `snapshot`, `restore`, `rewind` and `fork` (`vcs/manager.py:104-185`). `rewind` overwrites in place on the same session. `fork` is the only operation that creates a new session id. It is JSON-only, and it was built *"without modifying any existing code"* on top of the pickle-overwrite checkpointer. The model it copies is Claude Code's `fork_session`. — `docs/dev/session/vcs_design_cn.md`

**Key point: Session VCS is the nearest thing agent-core has to a replayable history.** It records *context and state*, not an attested account of tool effects. See [[Core 03 Harness Protocol]] for that gap.

## Context engine (`core/context_engine/`)

`ContextEngine` is held by each agent and builds the **model input**: history messages as short-term memory with window cropping, token counting and window control, and several concurrent context IDs in one session, for parallel subtasks. The harness adds its default processor chain through `ContextProcessorRail`: a message-summary offloader followed by dialogue, current-round and round-level compressors, with a session-memory compressor that is off by default. ⚠ The Context Engine doc lists a `ReasoningToolLoopCompactProcessor`, and no class by that name exists in the code.

## Long-term memory (`core/memory/`)

`LongTermMemory` covers conversation messages, variable memories and long-term user profiles, **scoped by `scope_id`**. It sits over pluggable KV, vector and DB stores. Since v0.1.4 the API has been `LongTermMemory + MemoryEngineConfig + MemoryScopeConfig + AgentMemoryConfig`, and older docs that use `MemoryEngine` are stale. The code also has `dreaming/`, `graph/` and `lite/` variants. The separate **agent-memory** repo is a larger product ([[openJiuwen Landscape]]). *Metis Task Memory* is documented under Self Evolution.

## System operation and sandbox (`core/sys_operation/`)

Filesystem, shell and code execution go through `SysOperation`, in `local/` or `sandbox/` mode. The docs mark this area **security-sensitive**. Sandbox mode sends operations to an isolated environment, with isolation at the **SYSTEM, SESSION or CUSTOM** level. Its lifecycle is managed by a gateway, and providers and launchers can be plugged in (`extensions/sys_operation/sandbox`).

Sources: docs/en/2.Development Guide/Advanced Usage/{Session/,Checkpointer Checkpoint Mechanism.md,Context Engine.md,Memory Engine.md,Sandbox.md}, docs/dev/session/vcs_design_cn.md, openjiuwen/core/{session,context_engine,memory,sys_operation}/, openjiuwen/extensions/{checkpointer,sys_operation}/
