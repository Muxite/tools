**Muk, 2026-09-23: there must be a diagram somewhere showing what is in a library and what a capsule can
possibly be.** `library.png`. This is the picture that makes "flexible in form" concrete, and it should
sit early — right after the structure slide.

## What the diagram shows

**One shelf, many shapes.** Every item below is a capsule under one schema, so the librarian places them
all by the same rule. What differs is which optional sections are filled in.

| Shape | What it is | Carrier (agent-core) | Notes |
|---|---|---|---|
| **n = 1, tool** | one function | `ToolCard` | the degenerate case, and the base of everything |
| **n = 1, skill** | a `SKILL.md` folder | `SkillSpec` | the 34 bundled jiuwenswarm skills enter here |
| **n = 1, MCP server** | a whole server | `McpServerSpec` | local hashed by files; remote pinned by endpoint and version |
| **n = 1, A2A agent** | a remote agent | the A2A client | card is metadata, never evidence |
| **n = 1, subagent / template** | an agent template | `AgentTemplateSpec` | |
| **n = 1, prompt section** | text | `PromptSectionSpec` | |
| **bundle** | several tools, MCP servers and skills loaded together, hashed as one body | `PluginSpec` | one Declaration, one Verdict. **No rails** — that would put a capsule in reach of the checks |
| **composite / merged block** | members, each independently admitted, plus an internal DAG | each member's carrier | `members[]` + `structure`; built by [[Overlap and Merge]] at M4 |
| **generalist** | the low-trust do-anything capsule | an agent template naming a provider | `exempt`; more than one may exist (a Codex one, a Claude one) |

## What else the library holds, beside the capsules

Drawn as the records attached to each item, each written by exactly one party:
**Declaration** (builder) · **Verdict** (gate) · **Standing** (librarian) · **Binding** + invocations
(the run) · **Finding** (anyone). Plus lineage edges between versions and between parents and children.

## What is *not* in the library

The contrast half of the diagram, and it does a lot of work:

- **judges, gates, the librarian, the planner, the freeze, dispatch** — [[The Ceiling]];
- **ranking and retrieval** — Symphony's, already built ([[Milestone Ladder]]);
- **tasks** — a capsule holds no step, node, sprint, workflow or worker.

## Why it earns a slide

It answers "what can go in a capsule?" visually and in one pass, and it shows the set case and the
degenerate case side by side, which is the thing people get wrong when they first hear the design.

Related: [[Capability Capsule]], [[Overlap and Merge]], [[Quality Not Just Correctness]].
