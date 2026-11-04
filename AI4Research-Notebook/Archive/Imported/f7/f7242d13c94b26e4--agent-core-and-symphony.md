# openJiuwen agent-core, with Symphony: what CC runs on

agent-core commit `e23806c1`, paths under `openjiuwen/`. CC is built on agent-core (settled by consensus; see
`tundle/obby/openJiuwen Landscape.md`). Needing nothing changed in agent-core is a requirement of the supervisor
(2026-09-18). Each hook below exists today, and each has a gap that the capsule layer's own code fills.

## What CC uses from agent-core (for d: what CC depends on)

| agent-core part | What it is | What CC uses it for | Gap the capsule layer fills |
|---|---|---|---|
| **Carrier specs:** `ToolCard` (`core/foundation/tool/base.py:78`), `McpServerSpec`, `SkillSpec`, `PluginSpec` (`harness/schema/extension_spec.py:146-164`), agent templates | how agent-core describes a loadable capability | **how the schema holds the capability itself**: the Declaration names the carrier spec, and agent-core loads it unchanged | the specs have no needs, effects, version or hash; those live in the Declaration |
| **Binder:** `apply_extension_hot` (`harness/extension_binder.py:27-60`) | loads carriers into an agent; undoes registrations in reverse order on failure or unload | loading a bound capsule; unloading on removal. Reversible registration is the one platform property agent-core fully provides (H1) | loads by name with no hash check, so the capsule layer checks hashes and loads from its immutable store |
| **Skill rail:** `SkillUseRail(enabled_skills=...)` (`harness/rails/skills/skill_use_rail.py:78`, `:95`) | limits which skills an agent may use | applying the offer for skills | it adds evolution-experience text by skill name, and a `max_total_chars` cap drops skills by keyword. Both must be pinned or switched off. The loader reads only `description` from frontmatter (`:946-958`) |
| **Tool rails:** `before_tool_call` (`harness/observability/rail.py:888`); `VerificationRail` (`harness/rails/subagent/verification_rail.py:166-220`) | observe or restrict tool calls | comparing tool calls with declared effects; restricting the tool set a capsule may call | `bash` reaches any path and `mcp__*` passes through, so file, network and execute effects are enforced only in a sandbox. What code does inside a tool is invisible (H5) |
| **Trajectory store** (`TrajectoryStore`); `LoadRecord` | the record of what ran | storing Bindings | load records live in memory (`harness/deep_agent.py:314`), so a capsule-layer rail persists Bindings |
| **RSI module:** `RsiTreeNode` (`rsi/schema.py:96-110`); harness RSI (`rsi/harness_rsi/`) | the self-improvement search tree | lineage for built capsules (`parent_id`, `adopted`, `snapshot_artifact_id`, `changes`) | RSI's candidate gate scores on its own suite, with held-out cases forced to 0 in single-harness mode (`iterative.py:1435-1447`, `:164`), so its result counts as builder evidence only |

## Symphony: agent-core's capability retrieval and orchestration

**What Symphony is.** Symphony is a package inside agent-core that turns an inventory of capabilities into a
retrieval index and a skill graph:

- a **fingerprint** per capability, derived by `FingerprintService` from the provider's descriptor, partly by a
  model, and carrying quality accumulated from use (`symphony/models/fingerprint.py:29-44`);
- a **graph** of `can_feed` edges, proposed by a model at confidence 0.7 or more (`orchestration/graph/build.py:122`),
  which admits only skills, subagents and agents (`:161`);
- a **fast planner** that picks capabilities from id, name and description, and handles I/O compatibility after the
  plan (`orchestration/planning/fast.py:32-44`).

**Where CC sits relative to Symphony.** CC is not *beside* Symphony. It is **upstream of Symphony's inventory**:

- CC's provider implements Symphony's `CapabilityProvider` (`symphony/interfaces/capability.py:13`) and lists **only
  admitted capsules**.
- Each carries `content_hash = decl_hash`, and I/O taken from the declared ports, which Symphony's extractor prefers
  over model output (`shared/fingerprint/extractor.py:151`, `:195-202`).
- Every change to a capsule's Standing is pushed through `SkillGraphUpdater` (`symphony/interfaces/graph.py:14`).
- Symphony then **retrieves and ranks within what CC admitted.** Its quality results stay observations: they can feed
  `use_outcome` Findings and never admit anything.

**How the two relate:**

| | Symphony fingerprint | CC Declaration |
|---|---|---|
| written by | derived by the service, partly by a model | written by the builder, checked by a gate |
| commits to | nothing: it describes | needs, effects, guarantees, budget |
| quality | inside the same object | in separate records (Verdict, Findings, Bindings) |
| identity | a hash of the descriptor | a hash of the Declaration and every body file |
| preconditions and effects | not represented | evaluated by code before a model chooses |

## openJiuwen skills and MCP

- **Skills** are folders with `SKILL.md`. The loader reads only `description`, so anything else a skill declares has
  no runtime effect today (`skill_use_rail.py:946-958`).
- **MCP:** agent-core's client keeps only name, description and input schema (`core/foundation/tool/mcp/client/sse_client.py:331-338`).
  An MCP server's hints and output schemas never reach the runtime.

## Corrections, 2026-09-23 (verified in source at agent-core `e23806c1`)

1. **`symphony/flow/` exists and is not recorded anywhere in these notes.** It is a complete
   distil-to-install pipeline for capability *sets*: `ExperienceRecipe.combination_structure` is a
   capability set with its own DAG (`nodes`, `edges`, `direction`, `loop_guards`); `qualified_edges`
   admits an A-to-B edge only on **both** enough support and a high enough success rate;
   `distill()` groups on a trajectory's **successful** edges only, so failing edges never enter a group;
   `resolve_status_grade` grades a pack `candidate` or `verified`; `content_identity()` versions on real
   change rather than on counts; `CapabilityPackager` content-hashes materials into a `cap-` package id;
   `PackageReviewGate.review_static()` runs ten deterministic checks before an isolated reviewer with no
   tools or filesystem sees a redacted copy; `FlowStore` keeps immutable `vN.json` with a `current`
   pointer. This is the largest single reusable asset for the design.
2. **"The loader reads only `description`" is true of the rail, not of Symphony.**
   `SkillManifestParser` (`symphony/shared/fingerprint/parser.py`) already reads `capability_id`,
   `name`, `description`, `capability_type`, **`inputs`**, **`outputs`**, `category`, `tags`, `version`
   and `available` from `SKILL.md` frontmatter, with diagnostics and budget limits. Only `SkillUseRail`
   is blind to them, so declared ports already have a reader on the Symphony side.
3. **The Symphony README's status table is stale.** It lists retrieval as 待迁入; it is implemented
   (`symphony/retrieval/`, `symphony/agent/retrieval_toolkit.py`). Trust the code, not the README.
