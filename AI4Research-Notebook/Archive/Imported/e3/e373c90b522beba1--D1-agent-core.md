# D1 — agent-core (Python Agent SDK)

Scope: `C:\Users\m50066326\huawei\openjiuwen\agent-core`
HEAD commit: `6dfda012193d09dc3908524d5f8ae406811d909f`, committed 2026-09-18 15:41:35 +0800 (same day as this reading).

## Repos and documents read

- Root: `README.md`, `README.zh.md`, `AGENTS.md`, `CLAUDE.md` (full read).
- `.claude/rules/architecture.md`, `git-workflow.md`, `karpathy-principles.md`, `python/coding-style.md` (full read); `.claude/skills/` listing only (python-patterns, python-testing, security-review, verification-loop — not opened, out of scope for doc reading).
- `docs/en/1. Product Overview.md` and `docs/zh/1.产品简介.md` (full read, compared line-for-line).
- `docs/en/2.Development Guide/README.md` (near-empty stub, see "What I could not determine").
- Full recursive directory listing of `docs/en/` (466 files) vs `docs/zh/` (462 files), diffed structurally (see Contradictions section).
- `docs/en/2.Development Guide/Advanced Usage/Agent Skills.md`, `Checkpointer Checkpoint Mechanism.md`.
- `docs/en/2.Development Guide/Advanced Usage/Session/Interruption Resumption.md`, `State Management.md` (partial).
- `docs/en/2.Development Guide/Workflows/Key Concepts.md`, `Overview.md`.
- `docs/en/2.Development Guide/Self Evolution/Agent-Skills-Capture-Your-Expertise.md`, `Skill-Online-Self-Evolution.md`, `Swarm-Skills-Turn-a-Successful-Collaboration-into-Team-Capability.md` (all full read).
- `docs/en/2.Development Guide/API Docs/openjiuwen.core/graph/graph.md` (sample of auto-generated API reference).
- `docs/dev/zh-doc-audit-v0.1.10-16.md` and `docs/dev/zh-doc-fix-summary-v0.1.10-16.md` — internal, dated audit artifacts, not part of the public docs tree but directly relevant to the EN/ZH comparison task (full read).
- `openjiuwen/symphony/README.md` — full read (716 lines, Chinese).
- `openjiuwen/rsi/AGENTS.md` — **does not exist** (confirmed absence); read `rsi/__init__.py`, `rsi/schema.py`, `rsi/events.py`, `rsi/harness_rsi/auto_harness/__init__.py`, `rsi/artifact_rsi/__init__.py` docstrings, and the `rsi/artifact_rsi/paper_opt/auto_research/` directory tree and one prompt file (`modules/manager/prompts/system.md`) instead.
- `openjiuwen/agent_evolving/AGENTS.md` — full read.
- `openjiuwen/harness/AGENTS.md` — full read.
- `openjiuwen/agent_teams/AGENTS.md` — full read (in full, ~430 lines).
- `openjiuwen/extensions/tracer_otel/AGENTS.md` — located but not opened (time budget; noted as the only AGENTS.md anywhere under `extensions/`).
- `openjiuwen/core/`, `core/memory/`, `core/graph/`, `core/workflow/`, `core/session/` — checked for AGENTS.md/README at the package root: **none exist** in any of these five directories (confirmed with `find -maxdepth 1 -iname "*.md"`).
- Code inspected directly (not docs, but necessary to check the symphony status table and the rsi gap): `openjiuwen/symphony/__init__.py`, `openjiuwen/symphony/flow/{__init__,models,review}.py`, directory listings of `symphony/{retrieval,agent,discovery,flow,observation}`, line counts (`wc -l`) of `symphony/flow/*.py`.

## What each thing is for

### openJiuwen Core (root README)

> "openJiuwen Core is a Python SDK for large language model applications, providing a high-performance runtime for agents running on the openJiuwen framework."

Three architecture layers are claimed: SDK interface layer, Agent engine (ReAct + Workflow), and a high-performance execution engine (async parallel graph, streaming, distributed deployment). The license footer is notable and appears **identically** in both language versions:

> "This product serves solely as a workflow orchestration tool and does not embed any AI model capabilities. When users integrate AI models for specific business scenarios, they shall bear full responsibility for compliance obligations under the EU AI Act and other relevant regulatory frameworks."
> ZH: "本产品仅作为流程编排工具，不包含 AI 模型能力；用户在连接 AI 模型用于特定业务场景时，需自行承担欧盟 AI 法案等相关合规义务。"

This is a stated non-goal/boundary at the product level: openJiuwen Core positions itself as orchestration infrastructure, not a model provider, and explicitly pushes AI-Act compliance liability onto the integrator.

### Product Overview (`docs/en/1. Product Overview.md` / `docs/zh/1.产品简介.md`)

Describes three products: **openJiuwen Core** (this repo), **openJiuwen Studio** (low-code visual builder), **openJiuwen Ops** (AgentOps: observability, prompt tuning, evaluation). Only Core is open-sourced today; the architecture diagram explicitly marks unreleased components:

> "The following figure illustrates the openJiuwen architecture (components shown within the grey dashed box will be gradually open-sourced in future releases)"
> ZH: "openJiuwen具体的架构图如下（灰色虚框部分待后期持续开源）"

This is a direct statement of roadmap/non-current-state: parts of the real architecture are deliberately withheld from this repo, which matters for reasoning about "where openJiuwen is going" versus what agent-core alone can tell us.

### AGENTS.md (root) — module map

States the intended top-level structure:
> "`openjiuwen/core/`: public SDK/runtime for agents, workflows, sessions, memory, retrieval, security, and system operations."
> "`openjiuwen/harness/`: coding-agent framework built on core primitives..."
> "`openjiuwen/extensions/`: optional integrations such as storage, checkpointers, sandbox providers, and vendor-specific adapters."
> "`openjiuwen/agent_evolving/` and `openjiuwen/dev_tools/`: optimization, evaluation, and developer tooling."

**Notably absent from this list**: `symphony/`, `rsi/`, `agent_teams/`, `harness_protocol/`, `harness_providers/`, `auto_harness/` — all of which exist as real, substantial top-level packages under `openjiuwen/` (confirmed by directory listing) and several of which are large, active subsystems (see Findings). The root AGENTS.md's module map is stale/incomplete relative to the actual tree.

### `.claude/rules/architecture.md`

States the Card/Config split as a first-class design law:
> "**Design intent**: Cards are static metadata, serializable and transportable; Configs are runtime objects holding resources and state. This separation enables Cards to cross process boundaries (e.g., A2A protocol) while Configs remain process-local singletons."

This is directly relevant to the capsule's "declared contract + identity" idea — openJiuwen already separates a transportable, serializable identity/metadata object (Card) from a process-local runtime object (Config), and calls out anti-patterns explicitly: "Putting `session_id`, `runner`, or other runtime data in a Card" and "Defining static description fields in a Config."

### `openjiuwen/symphony/` — capability discovery/fingerprint/orchestration

Its own README states its purpose plainly (quoted in full because every clause matters):

> "`openjiuwen.symphony` 是 openJiuwen 的能力资产发现、指纹、评估、检索、编排和经验沉淀领域模块，用于组织 Agent 运行时可用的 `skill`、`agent` 及其他可扩展能力类型。"
> Gloss: "openjiuwen.symphony is openJiuwen's domain module for capability-asset discovery, fingerprinting, evaluation, retrieval, orchestration and experience distillation, used to organize the `skill`, `agent`, and other extensible capability types available to the Agent runtime."

It names six core capability domains: **能力指纹** (capability fingerprinting), **能力检索** (capability retrieval), **能力编排** (capability orchestration), **经验沉淀** (experience distillation), **能力评估** (capability evaluation), **Agent Toolkit**. This is the single most capsule-relevant subsystem found in agent-core — see Findings below for a detailed status check.

### `openjiuwen/rsi/` — recursive self-improvement (undocumented)

No AGENTS.md, no README, no entry in root AGENTS.md, and **zero references in docs/en or docs/zh**. Its own module docstring:

> `rsi/__init__.py`: `"""Recursive self-improvement for standalone Expert Harnesses."""`
> `rsi/harness_rsi/auto_harness/__init__.py`: `"""Auto Harness Agent — 自主优化 harness 框架的编码 agent。"""` ("Auto Harness Agent — a coding agent that autonomously optimizes the harness framework")
> `rsi/artifact_rsi/__init__.py`: `"""Public contracts for program and paper artifact optimization providers."""`

`rsi/schema.py` defines `RsiTaskCreateRequest` with `scenario: RsiScenario` = `Literal["harness", "artifact"]`, `artifact_type: ArtifactType` = `Literal["program", "paper"]`, plus `search_width`, `max_iterations`, `model_refs` — i.e. a tree/beam-search-shaped optimization loop over two scenario kinds: improving a coding harness, or improving a program or **paper** artifact.

`rsi/artifact_rsi/paper_opt/auto_research/` is a full automated-research pipeline with modules `topic_survey/`, `experiment_design/`, `code_implementation/`, `experiment_execution/`, `reflection/`, `paper_scoring/`, `reporting/`, a `manager/` orchestrator, and a `tree_provider/`. The manager agent's own prompt states its control-loop contract:

> "You are the research-loop manager. You own persistent task state and decide the next control signal. You do **not** search the web, read files, write code, run experiments, or call modules yourself." ... "When `original_task.task_mode` is `modify_paper`, `original_task.initial_prompt` is source-grounded baseline-paper evidence. Treat its reported results as prior evidence, not results from this run. Use Topic Survey to investigate its stated limitations or improvement opportunities, and require each new experiment to compare against that baseline explicitly."

This is directly a **research-agent workflow** (literature → hypothesis/design → experiment → reflection → scored report) — one of the "what we care about" bullets — and it exists in real, fairly deep code (reporting has its own skill set: `ts-figure`, `ts-latex`, `ts-plan`, `ts-review`, `ts-write` SKILL.md files) with **no documentation anywhere in the docs tree**. This is a significant finding for the capsule design, discussed further below.

### `openjiuwen/agent_evolving/` — evolution/RL/experience subsystem

Its AGENTS.md opens with an explicit warning about vocabulary collision, which is exactly the trap the reading brief warns about:

> "不同链路都使用 `evolution` 一词，但不共享同一种数据模型、生命周期或持久化语义。"
> Gloss: "Different pipelines all use the word `evolution`, but they do not share the same data model, lifecycle, or persistence semantics."

Three distinct "evolution" pipelines are named: (1) classical parameter optimization (`Trainer`/`Evaluator`/`Optimizer`/`Updater`/`Trajectory`/`EvolveCheckpoint`), (2) online Skill-experience evolution (`Trajectory → EvolutionSignal → optimizer → local preview → approval → EvolutionStore`), (3) reinforcement learning (`agent_rl/offline` and `agent_rl/online`). `agent_evolving` never imports or mentions `symphony` (confirmed: `grep -rl "symphony" rsi agent_evolving` returned nothing) — despite `symphony/flow/` (see below) implementing what looks like a closely related "turn a trajectory into a packaged, versioned, reviewed capability" pipeline. These are two independently-built subsystems for adjacent problems.

### `openjiuwen/harness/` — coding-agent framework ("DeepAgent")

> "`openjiuwen.harness` 编码智能体框架。构建在 core 原语（`ReActAgent` / `AgentRail` / `Runner` / session）之上，为编码场景提供**深度代理**：模型调用、工具执行、rails 行为约束、子代理、任务循环、工作空间、权限引擎的完整闭环。"
> Gloss: "The `openjiuwen.harness` coding-agent framework. Built on core primitives (`ReActAgent` / `AgentRail` / `Runner` / session), it provides a **deep agent** for coding scenarios: a complete closed loop of model invocation, tool execution, rails behavioral constraints, subagents, task loop, workspace, and permission engine."

This is a mature, heavily-specified subsystem: 19 numbered design specs (`S_01` through `S_19`), one per subsystem (public API/construction, DeepAgent architecture, task loop, rails contract, tool contract, prompts/i18n, data models, security engine, workspace, subagent runtime, goals/evaluation, manifest assembly, resources/extensions, LSP, CLI, KV cache/skill state, personal context, subagents/lifecycle, protocol harness providers). Architecture "iron laws" (架构铁律) are stated bluntly, e.g.:

> "**新增 `AgentCallbackEvent` 成员不放进某个集合 = rail 静默失效**（只有一条 logger.warning，回调一次不跑）。"
> Gloss: "Adding a new `AgentCallbackEvent` member without putting it into one of the routing sets = the rail silently fails (only a single `logger.warning`, the callback never runs once)." — an explicitly named footgun, not just a rule.

### `openjiuwen/agent_teams/` — multi-agent team runtime

> "多智能体团队协作子系统。一个 Leader + 若干 Teammate，通过消息总线与任务数据库协同完成复杂任务。"
> Gloss: "Multi-agent team collaboration subsystem. One Leader + several Teammates collaborate via a message bus and a task database to complete complex tasks."

States a strict terminology hierarchy meant to be binding across "new API, events, traces and docs":
> "```\nSession\n└── Turn          一次外部输入 -> 一次稳定外部输出\n    └── Iteration 一次 Agent Loop 控制循环\n        └── Step  一次可观测原子执行动作\n```"
> Gloss: Session → Turn (one external input → one stable external output) → Iteration (one Agent Loop control cycle) → Step (one observable atomic execution action). `Round` is reserved only for multi-agent collaboration/protocol phases and explicitly must not be used for single-agent Turn/Iteration/Step — with a named exception for legacy `round_id`/`on_round` fields that are "pending independent migration" and must not be copied into new interfaces.

Also documents an explicit public-API contraction: "**没有 factory wrapper**——`create_agent_team` / `resume_persistent_team` / `recover_agent_team` 这套已删除，所有 lifecycle 都走 `TeamAgentSpec.build()` + `Runner` facade" — a prior, presumably more ad-hoc construction API was deleted in favor of a single Spec→build()→Runtime path, stated as an architectural iron law: "**Spec → build() → Runtime 是单向流**...想支持热更新？通过 session + resume 路径，而不是反向污染 Spec。" (Spec → build() → Runtime is a one-way flow; for hot-update support, go through session+resume, never write back into the Spec.)

## Goals and direction

### Symphony: current implementation vs. final design (kept explicitly separate by the source document)

The symphony README states its own dual-layer nature directly:

> "本文档同时描述最终设计和当前实现。'当前可运行接口'描述当前可直接导入的能力；'最终 Runtime 与统一接口蓝图'中明确标注为目标形态的代码示例不代表当前已有对应 facade。"
> Gloss: "This document describes both the final design and the current implementation. '当前可运行接口' (Currently runnable interfaces) describes capabilities importable today; code examples explicitly marked as target-state under '最终 Runtime 与统一接口蓝图' (Final Runtime and Unified Interface Blueprint) do **not** mean a corresponding facade exists yet."

Every code block under the "最终 Runtime 与统一接口蓝图（部分尚未接入）" section is prefixed `# 最终目标示例；当前不可运行。` ("Final target example; not runnable currently.") — this labeling is consistent and was honored throughout the section I read (retrieval search API, multi-service `SymphonyRuntime`, `symphony.experience` facade, `symphony.evaluation.evaluate_capabilities`, `symphony.agent_toolkit(...)`). I did not find an unlabeled target-state example presented as current.

**Current-vs-final split, restated in my own words**:
- **Current**: a single `SymphonyRuntime` that only composes `OrchestrationService` (capability-graph build/read/plan, with an online "observation"/evolution feedback loop for edge weights); `FingerprintService` (capability scanning → semantic profile → normalized IO → versioned `fingerprint.json`) usable standalone; `EvaluationSuite` (pluggable static + trajectory evaluators, no composite score, no baked-in admission threshold) usable standalone; `symphony.experience` (trajectory parsing, clustering, distillation, retrieval) usable standalone but **not yet wired into `SymphonyRuntime`**.
- **Final**: a `SymphonyRuntime` that composes `retrieval` (tree-structured, natural-language capability search), `orchestration`, `experience`, and `evaluation` behind one facade, plus an `agent_toolkit(language=...)` that an application wires into its own tool-calling surface. The final design explicitly delegates configuration, asset storage, permissions, and UI to the caller via an `Adapter` protocol — "Symphony 不隐式猜测或扫描应用目录、不读取应用配置、不注册或执行使用方的能力，也不依赖具体使用方代码" ("Symphony does not implicitly guess or scan the application's directories, does not read application config, does not register or execute the caller's capabilities, and does not depend on caller-specific code.").

### Status table — checked against code, found stale beyond the one row the brief flagged

The README's own status table:

| 能力域 | 当前状态 | 说明 |
|---|---|---|
| 能力指纹 | 已实现 (implemented) | ... |
| 能力检索 | **待迁入** (pending migration) | "最终提供能力树构建、浏览和自然语言检索。" |
| 能力编排 | 已实现 | ... |
| 经验沉淀 | 部分实现 (partially implemented) | "独立模块已提供...；尚未接入 `SymphonyRuntime`。" |
| 能力评估 | 已实现 | ... |
| Agent Toolkit | **待迁入** | "最终组合检索和编排，供 Agent 调用。" |
| 公共 `models` | 已实现 | ... |

**How I checked**: I listed `openjiuwen/symphony/` at depth 2 and read `symphony/__init__.py`, `symphony/retrieval/__init__.py`, and `symphony/agent/__init__.py` directly (not just the README).

**Finding 1 — the "能力检索" (capability retrieval) row is stale, in the direction the brief said to expect**: the directory `symphony/retrieval/` exists with real submodules `build/`, `common/`, `llm/`, `search/`, and is lazily importable from the package (`_LAZY_MODULES = frozenset({"agent", "discovery", "flow", "retrieval", "shared"})`). More tellingly, the *same README*, in its "架构总览" (architecture overview) section further down, describes a concrete, present-tense, currently-usable API for it: `AgenticSkillRetrievalToolkit.build_index()`, `SkillIndexBuildConfig.equivalence_enabled` (default off), `SkillIndexBuildConfig.equivalence_min_lexical_similarity` — with worked-through behavior for a "skill equivalence group" feature in the retrieval tree. This is an internal contradiction: the status table says retrieval is not yet migrated in, but a later section of the same document describes a specific, configurable, already-shipped retrieval-tree-building feature in the present tense.

**Finding 2 — "Agent Toolkit" is also further along than "待迁入" suggests**: `symphony/agent/__init__.py` exports `AgenticSkillRetrievalToolkit`, `AgenticRetrievalConfig`, `SkillIndexBuildConfig`, `SkillIndexRuntimeConfig`, `SkillRecord`, `scan_skill_records` — an Agent-facing toolkit already exists for the retrieval slice, even though the unified `agent_toolkit(language=...)` facade described in the "final design" section does not.

**Finding 3 — the table omits three real, substantial code trees entirely**: `discovery/` (config.py, directory_toolkit.py 1407 lines, models.py 466 lines, skillfs.py 902 lines, toolkit.py — a "skill filesystem" discovery layer), `observation/` (contracts.py, identity.py, service.py, store.py — this is the backing implementation for the "动态 observation"/`submit_observation()`/graph-evolution feedback loop that the README *does* describe in prose under orchestration, and that `harness/rails/evolution/symphony_edge_evaluator.py` etc. wire into — but it has no row in the status table and is not in the README's "最终目录蓝图" (final directory blueprint) tree at all), and **`flow/`**.

**Finding 4 — `symphony/flow/` is, by my reading, the concrete instance of the exact trap this reading brief opens with.** It totals **2,734 lines** (`wc -l flow/*.py` = 2734), it has no row in the status table, no mention in the "最终目录蓝图" tree, and its own docstring names it plainly:

> `flow/review.py`: `"""PackageReviewGate：确定性静态评审（结构/依赖/安全/完整性）。"""` — "PackageReviewGate: deterministic static review (structure/dependency/security/integrity)."

It defines `VERDICT_APPROVED`, `VERDICT_REJECTED`, `VERDICT_NEEDS_HUMAN_REVIEW`; a `PackageReviewAgent` Protocol restricted to `review(package) -> verdict` with no tool/filesystem/sysop access ("Restricted model reviewer with no tool, filesystem, or sysop surface"); forbidden-code-token and forbidden-permission checks (`_FORBIDDEN_CODE_TOKENS = ("import os", "import sys", "subprocess", "eval(", "exec(")`, `_FORBIDDEN_PERMISSIONS = frozenset({"credential_access", "filesystem_write", "process", "shell"})`); a license allowlist; and a full recipe/package lifecycle (`ExperienceRecipe`, `RECIPE_STATUS_DRAFT/ACTIVE/DEPRECATED`, `RECIPE_GRADE_CANDIDATE/VERIFIED`, `CapabilityPackager`, `SkillAdapter`/`render_package`, `FlowStore`, schema versions `RECIPE_SCHEMA_VERSION`/`PACKAGE_SCHEMA_VERSION`/`REVIEW_SCHEMA_VERSION`). This is exactly the capsule's "verified admission" and "identity and lineage" concept, already built, under the vocabulary "flow / recipe / package / review gate / verdict" — not "admission" or "precondition." I confirmed this is not documentation vaporware by reading the actual `.py` source, not just the README.

I connected this code to product-facing prose: `docs/en/2.Development Guide/Self Evolution/Swarm-Skills-Turn-a-Successful-Collaboration-into-Team-Capability.md` describes, in user-facing terms, exactly this pipeline's purpose (turning a successful multi-agent team trajectory into a reusable, packaged "Swarm Skill" via `swarmskill-creator`), and `symphony/flow/__init__.py` exports `LLMPackageReviewAgent`/`PackageReviewGate`/`CombinationCandidate` that read as the backing implementation — but neither document cross-references the other by name. I could not fully confirm the wiring between `swarmskill-creator` (described as a "companion Agent Skill") and `symphony/flow` in the time available; this is a plausible but unconfirmed connection (see "What I could not determine").

**How thoroughly did I check for other stale rows?** I verified all seven rows against an actual directory listing and two `__init__.py` files, and inspected line counts of `flow/`. I did **not** exhaustively read every file under `orchestration/`, `evaluation/`, or `experience/` to verify those three "已实现"/"部分实现" rows line-by-line; I take the "已实现" rows on lighter trust than the two "待迁入" rows and the omitted `flow/`/`observation/`/`discovery/` trees, which I positively confirmed contain real, non-trivial code.

### Skill lifecycle: capture → evolve → rebuild/rollback (well-documented, cross-file consistent)

`Skill-Online-Self-Evolution.md` describes a two-layer model that is directly relevant to "versioning, lineage, deprecation":

> "Skill definition\n  └── SKILL.md, roles/, workflow.md, scripts/, and other base files\n\nEvolution experience layer\n  └── experience records in evolutions.json"

Each experience record is versioned/scored (`id`, `source`, `timestamp`, `context`, `change`, `score`, `usage_stats`, `applied`), gated by user confirmation before writeback ("there is usually user confirmation between automatic experience generation and actual writeback"), and lifecycle-managed via explicit commands: `/evolve`, `/evolve_list`, `/evolve_simplify` (DELETE/MERGE/REFINE/KEEP actions), `/evolve_rebuild` (archives old `SKILL.md` + `evolutions.json` before regenerating), `/evolve_rollback <skill_name> [version]`. The document is explicit that this is not silent self-modification:

> "openJiuwen's self-evolution is a transparent, manageable feedback loop with confirmation for important changes and rollback for important versions." ... "**there is usually user confirmation between automatic experience generation and actual writeback**"

Confirmation behavior is stated to differ by command (worth noting precisely, since it's a real nuance, not uniform):
> "New experience generated by automatic signal detection usually asks the user to accept or reject. A normal Skill's `/evolve_simplify` usually shows the cleanup actions first and then asks whether to execute them. The cleanup path for Team / Swarm Skills may execute directly and return results in the current version. `/evolve_rebuild` is a user-initiated rebuild task; it archives the old version first... `/evolve_rollback` is a user-initiated rollback command and does not show an extra confirmation prompt."

## Findings relevant to the capsule

**Capability reuse (skills, tools, plugins, capability assets)**: Agent Skills are a folder format (`SKILL.md` + optional `scripts/`/`references/`/`assets/`), discovered by name+description metadata only at startup ("progressive disclosure": ~100 tokens of metadata → full body on trigger → referenced files on demand), installable from a local directory or downloaded from a GitHub tree via `agent.register_remote_skills(skills_dir, github_tree=GitHubTree(repo_owner=..., repo_name=..., tree_ref=..., directory=...), token=...)`. Swarm Skills extend the same `SKILL.md`-rooted format to multi-role teams (`roles/`, `workflow.md`, `bind.md`, `dependencies.yaml`, optional `scripts/workflow.py`). Symphony's `flow/` and `discovery/` packages appear to be the lower-level capability-asset machinery (packaging, review-gating, filesystem scanning) underneath this user-facing story, though I could not fully confirm the wiring (see above).

**Contracts (declared inputs/outputs/preconditions/effects/permissions/cost)**: The Card/Config split (`.claude/rules/architecture.md`) is the closest thing to a general "declared contract" primitive in agent-core: `AgentCard`, `ToolCard`, `WorkflowCard`, `SysOperationCard` are serializable identity/metadata, explicitly designed to cross process boundaries (the rule names A2A protocol as the reason). Symphony's `CapabilityFingerprint`/`CapabilityDescriptor`/`CapabilityIO` model is a second, adjacent contract vocabulary (semantic profile, normalized input/output, tags) purpose-built for retrieval/orchestration matching rather than process-boundary transport — these are two different "contract" ideas serving different purposes (identity/transport vs. semantic matching), and I did not find a document that unifies them. `symphony/flow/review.py`'s `PackageReviewGate` forbidden-token/forbidden-permission lists are the clearest example of a **declared permission/effect boundary enforced at admission time** anywhere in this repo.

**Admission and validation**: `symphony/flow/review.py` (`PackageReviewGate`, verdicts APPROVED/REJECTED/NEEDS_HUMAN_REVIEW, deterministic static checks + a permission-and-tool-restricted `LLMPackageReviewAgent`) is the strongest concrete admission-gate implementation found. Skill online self-evolution's "generate candidate → user confirmation → writeback" loop is a second, lighter-weight admission gate for incremental changes to an existing capability. Symphony's `EvaluationSuite` explicitly disclaims setting admission thresholds itself: "默认不生成跨指标 composite score，也不固化准入阈值" ("by default it does not generate a cross-metric composite score, and does not bake in an admission threshold") — evaluation is deliberately separated from the admit/reject decision, which is left to the caller (or to `PackageReviewGate` for the packaging path specifically).

**Versioning, lineage, deprecation**: Skill evolution's archive-before-rebuild + numbered rollback versions is the clearest lineage mechanism for skills. `symphony/flow/models.py` has explicit schema versions (`RECIPE_SCHEMA_VERSION = "symphony.experience_recipe.v1"`, similarly for package/review) and a recipe status machine (`draft`/`active`/`deprecated`) plus a grade (`candidate`/`verified`) — this is a genuine capability-lineage model, separate from the Skill-experience lineage model, and (as far as I could tell) not cross-referenced with it. Checkpointer artifact versioning (`graph_artifact_root/versions/<version>/graph.json`, atomic `current.json` pointer, never-overwrite-last-good-on-failure) is a third, independent versioning mechanism, for execution-graph state rather than capability definitions.

**Evidence and provenance**: Symphony's evaluation `MetricResult` carries `status`, an optional `[0,1]` score, `reason`, redacted `evidence`, `failure`, and `suggestion` per metric — evidence is redacted/length-limited by design (`脱敏` = de-identified/redacted appears repeatedly). The graph-evolution ("observation") path is explicit about evidentiary strength requirements: "只有强验证成功，或带明确 evidence reference 且归因于 `orchestration` 的边级失败，才更新权重；弱证据、外部服务错误、权限错误、网络错误和截断轨迹仅留作审计。" ("Only strong verification success, or edge-level failure with explicit evidence reference attributed to `orchestration`, updates weights; weak evidence, external service errors, permission errors, network errors, and truncated trajectories are kept for audit only.") — a genuine claim-to-evidence discipline, with an append-only `evidence.sqlite3` log described as canonical.

**Composition (do capabilities connect; does anything compose systems, not just functions)**: Symphony's orchestration graph composes *capabilities* into an executable plan (`planned_graph`, a minimal JGF v2 single graph with `can_feed` edges). Whether anything composes *systems* (i.e., whole agents/pipelines, not individual skills/tools) is less clear: `agent_teams` composes whole agents (Leader + Teammates) but via a different mechanism (message bus + task DB, not symphony's capability graph), and Swarm Skills capture *collaboration patterns* as reusable artifacts, but the execution engine for that (`SwarmFlow`) is described only at the product-doc level in what I read — I did not locate or read its implementation, so I cannot say whether it reuses the workflow engine, the symphony orchestration graph, both, or neither.

**Research-agent workflows (literature, hypotheses, experiments, reports)**: `rsi/artifact_rsi/paper_opt/auto_research/` is a real, structured pipeline (topic_survey → experiment_design → code_implementation → experiment_execution → reflection → paper_scoring → reporting, with a manager agent enforcing a strict "manager decides, does not act" control-loop contract, and a `modify_paper` task mode that treats a baseline paper's reported results as prior evidence rather than current-run results). This is the single most relevant piece of code in agent-core to a research-agent capsule design, and it is **entirely undocumented** — not mentioned in README, AGENTS.md, or any file under `docs/`. This is a significant gap worth flagging to Muk directly: the capsule work should probably look at this code, not just the documented subsystems.

**Stated non-goals and boundaries**: (1) The root README's AI-Act liability disclaimer (product-level non-goal: "does not embed any AI model capabilities"). (2) Symphony's Adapter boundary — "不隐式猜测或扫描应用目录、不读取应用配置、不注册或执行使用方的能力" (does not implicitly scan app directories, read app config, or register/execute the caller's capabilities) and "`SkillFolderScanner` 只扫描调用方显式传入的根目录" (only scans caller-supplied roots, no symlink/junction traversal). (3) `agent_teams`'s explicit statement that `coordinator` makes no decisions: "**coordinator 不做决策** ... 不要把业务逻辑塞到 loop 里" (the coordinator does not decide; do not put business logic in the loop). (4) `harness`'s single-construction-path law and manifest-only extension law, both phrased as things not to do rather than things to do.

## Contradictions and ambiguities

**Symphony status table vs. its own architecture-overview section** (already detailed above under Goals and direction): the table marks 能力检索 (capability retrieval) as "待迁入" (pending migration), while the "架构总览" section of the *same document* describes `AgenticSkillRetrievalToolkit.build_index()` and `SkillIndexBuildConfig.equivalence_enabled` in the present tense as a configurable, shipped feature. Both readings are drawn from the same file; I am confident this is a genuine internal inconsistency, not a misreading on my part, because I additionally verified the `retrieval/` and `agent/` packages exist and export exactly those names.

**Symphony's status table also omits real code** (`flow/`, `observation/`, `discovery/` — 2,734 + ~1,300 + ~2,800 lines respectively by rough count) rather than mis-stating it. This is a different kind of staleness from the retrieval row (omission vs. wrong label), and I flag it separately because the brief specifically warned that vocabulary (not just table rows) can hide a real subsystem — `flow/` is that case.

**Root AGENTS.md module map is incomplete**: it documents `core/`, `harness/`, `harness_protocol/`, `harness_providers/`, `extensions/`, `agent_evolving/`, `dev_tools/`, but not `symphony/`, `rsi/`, `agent_teams/`, or `auto_harness/`, all of which are real top-level packages with their own substantial code and (for `agent_teams`, `agent_evolving`, `harness`) their own detailed AGENTS.md files. Whether this is an oversight or reflects that these are newer/less-stable additions, I could not determine from the text alone.

**EN/ZH divergence — human-authored docs (`docs/en/2.Development Guide/` vs `docs/zh/2.开发指南/`)**: I diffed the full directory trees. Structurally, the human-authored guide sections (`Advanced Usage`/`高阶用法`, `Agent Teams`/`智能体团队`, `Self Evolution`/`自演进`, `Agents`/`智能体`, `Multi-Agent`/`多智能体`, `Workflows`/`工作流`, `Basic Functions`/`基础功能`) have **matching file counts and matching topic-for-topic translated filenames** — I found no missing or extra human-authored topic file in either direction. The root `1. Product Overview.md` / `1.产品简介.md` pair is a faithful, essentially line-for-line translation (I read both in full).

**EN/ZH divergence — auto-generated API reference docs** (`docs/en/2.Development Guide/API Docs/` vs `docs/zh/.../API文档/`): here real gaps exist. Diffing the two trees:
- `openjiuwen.agent_teams.README.md` exists as a flat top-level file in EN only; ZH has only the nested `openjiuwen.agent_teams/README.md` (the content likely exists, just not duplicated at the flat path — a minor structural asymmetry, not a content gap).
- `openjiuwen.core/retrieval/indexing/processor/extractor/ontology_triple_extractor.md` exists in EN only — **no ZH counterpart at all**.
- `openjiuwen.core/workflow/components/flow/execute_single_component.md` exists in EN only — **no ZH counterpart at all**.
- Three files are simply translated-filename equivalents, not gaps: `a2a/client.md`↔`a2a/客户端.md`, `a2a/server.md`↔`a2a/服务端.md`, `harness/subagents/browser_agent.md`↔`harness/subagents/浏览器子智能体.md`, `harness/tools/browser_tools.md`↔`harness/tools/浏览器子智能体工具.md`.

**EN/ZH divergence — confirmed by the repo's own internal audit** (`docs/dev/zh-doc-audit-v0.1.10-16.md`, dated 2026-07-29, anchored to tag `v0.1.16.post1` / commit `b28b4f3a6`, roughly seven weeks before this repo's HEAD): this is a self-produced, methodologically explicit audit (41 tracked issues, later reduced to 39 unique after dedup) comparing `docs/zh/` against source code. It is evidence, not my own finding, but it is strong evidence and I quote it because it independently corroborates the kind of drift this reading exercise is meant to surface. Two examples with direct EN/ZH bearing:
- **HAR-04**: "文档写 `from openjiuwen.core.skills import GitHubTree`，实际模块路径为 `openjiuwen.core.single_agent.skills`。导入路径错误致示例不可运行。" (The [ZH] doc writes `from openjiuwen.core.skills import GitHubTree`, but the actual module path is `openjiuwen.core.single_agent.skills`. The wrong import path makes the example non-runnable.) I confirm the **English** doc I read (`Agent Skills.md`) already uses the correct path `from openjiuwen.core.single_agent.skills import GitHubTree` throughout — so at the time of that audit, EN was correct and ZH was wrong on this exact point. The companion fix-summary document (`zh-doc-fix-summary-v0.1.10-16.md`) confirms this was subsequently corrected in ZH ("HAR-04 | High | Agent Skills.md:87、:283 | 导入路径修正：`from openjiuwen.core.skills` → `from openjiuwen.core.single_agent.skills`").
- **TE-02/TE-03/TE-04**: at audit time, ZH had "零概念覆盖" (zero conceptual coverage) for HITT (Human-In-The-Team), Team permission guardrails, and OTEL team-level tracing. The fix-summary explicitly states these were **not** in scope for that fix pass: "多智能体团队项（TE-02/03/04、AS-07/08/09/10、AS-13、AS-17）：非杨泽渠职责，不在本次修复范围。" (Agent-team items ... were not this person's responsibility, out of scope for this fix pass.) Yet the **current** `docs/zh/2.开发指南/智能体团队/` directory (which I listed directly) now contains `HITT人机交互团队模式.md`, `OTEL团队级追踪.md`, and `Team权限护栏.md` — i.e., these specific gaps have since been closed, presumably by a separate, later effort not captured in either audit document I read. I flag this as a **resolved-since-audit** case rather than a live contradiction, but it means the audit documents themselves are now partially stale artifacts (which is expected and stated as historical — they're timestamped — but worth knowing before trusting them as current status).
- The fix-summary also documents the audit **correcting itself**: item AS-06 was marked "跳过" (skipped) because "前提错误：`memory/external/lakebase_memory_provider.md`（512 行）已存在，与 RET-05 交叉。非真实缺失。" (False premise: the doc already exists at 512 lines, overlapping with RET-05. Not a real gap.) — i.e. the original audit had at least one false positive, later caught during the fix pass, not by me.

**"Team Skill" vs. "Swarm Skill" naming**: `Swarm-Skills-Turn-a-Successful-Collaboration-into-Team-Capability.md` states directly: "In openJiuwen code and some historical docs, you may also see the name `Team Skill`. For user understanding, you can treat them as the same kind of capability... This document uses the product term `Swarm Skill` consistently." This is the document flagging its own internal naming drift — old code/docs say "Team Skill," current product docs say "Swarm Skill." I did not verify how much code still uses `TeamSkill*` naming (the audit's TE-01 item independently found a related class-name mismatch: docs called a class `TeamSkillExperienceOptimizer`, source code actually names it `SkillExperienceOptimizer`, in `agent_evolving/optimizer/skill_call/experience_optimizer.py`).

## What I could not determine

- **`docs/en/2.Development Guide/README.md`** is a one-line stub (`# Development Guide`) — no overview content beyond the heading. I could not determine whether the ZH counterpart (`docs/zh/2.开发指南/README.md`, not opened) carries more content; given the pattern found elsewhere (topic-for-topic parity), I'd guess it's equally minimal, but this is a guess, not a finding.
- **Whether `symphony/flow/` is actually the execution backend for `swarmskill-creator`/`skill-creator`** described in the product docs. The vocabulary and shape line up strongly (trajectory → recipe → package → review gate → verdict → render into `SKILL.md`-shaped output), but I did not find an explicit cross-reference in either direction, and I did not trace the actual call graph (e.g., from a `skill-creator`/`swarmskill-creator` prompt or tool definition into `symphony.flow`). This should be verified before being relied on as fact.
- **Whether `SwarmFlow`'s execution engine reuses the core workflow engine (`core/workflow/`), the symphony orchestration graph, or neither.** The product docs describe SwarmFlow only behaviorally ("orchestration is handled by the system"); I did not locate or read its implementation module.
- **How much of the "已实现" (implemented) status in symphony's table I can trust beyond a directory-existence check.** I verified `orchestration`, `evaluation`, and `experience` have real, sized code directories and that `__init__.py` exports match the README's described API surface, but I did not read enough of `orchestration/graph/`, `evaluation/evaluators.py`, or `experience/*.py` line-by-line to independently confirm behavior matches the prose (as I did for `flow/review.py`). Treat "已实现" rows as directory-confirmed, not behavior-confirmed.
- **`core/graph/`, `core/session/`, `core/workflow/` design-level documentation.** These three packages — explicitly named in this task's scope as "the execution substrate" — have **no AGENTS.md, no README, and no conceptual design doc** anywhere I found; the only documentation is auto-generated API reference (e.g. `docs/en/.../API Docs/openjiuwen.core/graph/graph.md`, which is a class-by-class docstring dump of `Graph.start_node()`/`end_node()`/etc., not an architecture explanation). Checkpointing, resume, and parallelism *are* well documented, but at the usage-guide level (`Checkpointer Checkpoint Mechanism.md`, `Session/Interruption Resumption.md`, `Workflows/Overview.md`'s "Parallel Branching" section) rather than the design/substrate level the task asked about. I could not find a document explaining, e.g., how the graph executor schedules concurrent branches, how checkpoint granularity interacts with parallel branches, or what "long-horizon execution" guarantees (if any) exist beyond per-component retry/timeout config (`max_retries`/`timeout`/`exception_config` on `add_workflow_comp`, mentioned only in the audit's WF-03 entry, not in the primary docs I read).
- **`openjiuwen/extensions/tracer_otel/AGENTS.md`** — located (it's the only AGENTS.md under all of `extensions/`) but not opened, due to time budget after the depth spent on symphony/rsi/harness/agent_teams. A gap in my own coverage, not a claim about the repo.
- **`.claude/skills/`** (python-patterns, python-testing, security-review, verification-loop) — listed but not read; these looked like coding-standard skills rather than architecture/product documents, so I judged them out of scope for this pass, but I did not verify that judgment by opening them.
- I did not read `docs/dev/harness_protocol_integration.md`, `docs/dev/online-rl-service-operations.md`, or `docs/dev/session/vcs_design_cn.md` (the latter is explicitly Chinese and title suggests "session version-control design" — directly relevant to lineage/versioning of session state, and I flag it as a likely-valuable document I did not get to).
