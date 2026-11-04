There are five memory mechanisms plus context compression. Most are switched on separately in `~/.jiuwenswarm/config/config.yaml`. Coding Memory turns on automatically in Code mode. Underneath, agent-core supplies the context engine and the memory rails ([[Core 05 Session, Context, Memory]]).

| Mechanism | What it keeps | How |
|---|---|---|
| **Memory** | persistent facts across sessions, in files | BM25 search by default, with vector and BM25 hybrid when `EMBED_API_KEY` is set. `memory.engine: builtin \| external \| both \| none`. External providers: openJiuwen LTM, Mem0, OpenViking, or a plugin |
| **Auto Memory** | facts **extracted after each conversation**, isolated per project | a post-conversation extraction runner (`agents/harness/common/auto_memory/`) |
| **Task Memory** | lessons from past tasks: retrieve, record, consolidate | `experience_retrieve` and related tools. Retrieval algorithm is `ACE`, `ReasoningBank` or `ReMe` |
| **Coding Memory** | persistent code context in Code mode | turned on automatically in Code mode (`CodingMemoryRail`) |
| **Eternal Conversation** | a complete, durable history of a session, for sessions opted in with `persist_session` | see below |

**Context compression** keeps long conversations inside the model window. It filters selectively, offloads large tool outputs behind `[[OFFLOAD:…]]` markers, and can recall them later. This is agent-core's `ContextProcessorRail` chain, configured by the product.

## Eternal Conversation: the one to know about

`agents/harness/common/rails/eternal_conversation/`, with its flow described in `.doc_project_maintainer/project/flows/eternal-conversation-memory.md`:

- The rail records **the post-ContextProcessor model input, user and task events, tool calls and results, and the final result** into an **append-only, cursor- and hash-chained Raw History**. Large fields are **content-addressed** by a canonical JSON digest, so the exact model input can be reconstructed.
- *"Raw History is authoritative… Any cursor/hash/session divergence fails closed."*
- Two background agents, Extractor and Builder, turn the raw history into structured memory at task boundaries. The working context is replaced only when coverage is exact.
- It is off unless a new Web session sets `persist_session`, and that choice cannot be changed afterwards.

**Key point for H5 ([[Dependencies]]): this is a durable, hash-chained record of tool calls and results.** It fails closed and can be reconstructed, which agent-core's observability spans can't do ([[Core 03 Harness Protocol]]). Like the spans, it records what the agent called, not the file writes or network traffic of code a tool ran. It also lives in the product, not the SDK, it is opt-in per session, and it is a memory feature, not an audit feature.

Sources: docs/en/{Memory,AutoMemory,TaskMemory,CodingMemory,ContextCompression}.md, .doc_project_maintainer/project/{architecture.md,flows/eternal-conversation-memory.md}, jiuwenswarm/agents/harness/common/{memory,auto_memory,rails/eternal_conversation}/
