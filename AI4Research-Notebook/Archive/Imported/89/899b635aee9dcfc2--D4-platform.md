# D4 — Platform, protocol and infrastructure (openJiuwen)

Scope: `C:\Users\m50066326\huawei\openjiuwen\` — agent-protocol, skillhub, agent-memory, agent-runtime,
agent-studio (deep reads); agent-infer, agent-tools, agent-dx, relay, CareerSim-BDCI26, agent-core-java
(README-level passes). Read-only, no web/arXiv. Governing question: **what does openJiuwen already provide
that a capability-capsule layer should consume rather than rebuild?**

This report is a synthesis of five parallel document-reading passes (not grep passes — each pass opened and
read whole documents, per the brief's method note about the "admission"/"precondition" grep failure in
`symphony`). Every finding below is traceable to a specific file; I have preserved the sub-readers' distinction
between "the doc claims X" and "X is code-verified" wherever they made it, and flag where I could not verify
it myself.

## Repos and documents read, with commits

| Repo | HEAD commit | Date | Note |
|---|---|---|---|
| agent-protocol | `79201fe4c1bd1c8696f3ef750004969a906ccfcb` | 2026-09-04 | "merge develop into main" |
| skillhub | `236f56c101d94ea3b94ff1d62f4bd28b7d380812` | 2026-09-18 | "!266 merge develop into develop" |
| agent-memory | `9bf45fa4154fc448cbe6a126958c50b9f26a1685` | 2026-09-01 | "fix: version number modify" |
| agent-runtime | `34ed6e86b99fab9b3f07d9f063efc1692ab365d2` | 2026-08-04 | "fix: change readme clone url to github" |
| agent-studio | `31c8d04dfdae4f647ff3653c7b583f8a05df51eb` | 2026-09-18 | "!2344 merge fix-end-dev into studio-2.0-dev" |
| agent-infer | `fefffba9e7142a81658b304efe876eb687a5ead6` | 2026-09-15 | README-level |
| agent-tools | `824a5170517104332d9358721286ce5178125794` | 2026-08-04 | README-level, `openjiuwen_package_design.md` read in full |
| agent-dx | `02f13a57f6893a1e02b190f2f9771f3ccd96bb93` | 2026-09-15 | README-level |
| relay | `9de45970272cc6985334b14da116b9e159a7fce6` | 2026-08-07 | README-level, but `office-claw-skills/BOOTSTRAP.md` also read |
| CareerSim-BDCI26 | `f61c738c72e51b77298cc1c14c7c6ebf4b6c527d` | 2026-08-14 | README-level |
| agent-core-java | `9a244867addb86343b6d1b91fd1744b6bf86d565` | 2026-09-15 | README-level only, by design (repo has ~1,497 docs) |

Deep-dive document lists (non-exhaustive selection, all read in full unless noted):
- **agent-protocol**: root README.md/README_zh.md; A4P/README.md, A4P_PROTOCOL.md, A4P_SDK_DESIGN.md,
  tests/README.md, examples/note_mcp_a4p/README.md; AgentRegistry/README.md,
  README_forAgentTeam.md, README_forDistributed.md, client/README.md, client/README_agentteam.md,
  docs/{a2x_design, architecture_overview, auth_design, register_design, search_design, heartbeat_design,
  cluster_design, build_design}.md. Not read: backend_api.md, environment.md, frontend_design.md, ui/README.md.
- **skillhub**: root README.md/README_zh.md; docs/zh/1. 产品概览.md; docs/zh/5. 开发指南/{Skill与SwarmSkill规范,
  Skill审核机制, Agent资产, 插件包格式}.md; docs/zh/4. 用户指南/{发布Skill, 发布SwarmSkill, 角色与权限,
  场景化指引与FAQ}.md; docs/zh/7. API参考/{ClawHub兼容层, Agent资产列表与下载接口,
  openJiuwen-Agentic-Hub-接口参考}.md; docs/zh/6. 运维指南/README.md; marketplace/dispatch/{README, docs/README,
  retrieval/algorithm, retrieval/doc}.md; marketplace/retrieval/doc.md; CHANGELOG.md; cli/README.md; plus a
  source-level check of `marketplace/skill_review/domain/check_catalog.py` (389 lines) and
  `marketplace/dispatch/indexing/models.py`, because the prose docs only gesture vaguely at what "review" checks.
  Not read in full: 快速开始, 在线体验运行时, 检索系统 docs, 推荐系统, cli sub-READMEs, raw OpenAPI YAML.
- **agent-memory**: README.md/README.zh.md; docs/en/API Docs/{long_term_memory, memory_server, config,
  graph_memory, middle_term_memory}.md; prompt files memory_update_check.md, semantic_validation.md,
  dreaming_extraction.md; a source peek at `config.py` (ForgettingConfig) and `evaluator.py`
  (EbbinghausEvaluator) because the docs describe the forgetting mechanism without giving its formula.
- **agent-runtime**: README.md/README_zh.md; docs/en/{0,1,2,3,4}, docs/zh/{0,2,3,4,5} (5 is ZH-only — see
  Contradictions); one source check of `management/.../models/enums.py` for deployment status states, which
  are undocumented in prose.
- **agent-studio**: README.md/README_zh.md; docs/en (and zh) architecture-overview.md, rest-api-workflow.md,
  rest-api-single-agent.md; docs/en/tutorial/02-user-guide.md §4–§7 (targeted, not the full 6,241 lines);
  docs/FAQ/faq.md; agent_builder/serve/README.md (agent_builder/prompt/README.md is a 17-byte stub — empty).
- **Six brief-pass repos**: root READMEs (EN/ZH where both exist) plus one deeper doc each where flagged
  relevant (agent-tools' `openjiuwen_package_design.md`; relay's `office-claw-skills/BOOTSTRAP.md`;
  agent-dx's cli/README.md and executor/README.md).

---

## What each thing is for

### agent-protocol (highest priority)
Root README, EN and ZH (faithful 1:1 translation, no divergence):
> EN: "**Agent Protocol** is a collection of software development kits (SDKs) for agent interoperability and
> authorization protocols. It helps developers quickly integrate agents, enable agent-to-tool / agent-to-agent
> interoperability, and establish verifiable authorization boundaries across different runtime environments."

Four bundled SDKs: MCP (C++), A2A (C++), an agent registry (A2X), and A4P (Python). The README asserts the
bundling ("agent interoperability and authorization") but never explains architecturally why these four belong
together — no diagram, no cross-references between the sub-projects at root level. As detailed below, A4P and
A2X in particular turn out **not** to reference each other at all despite both being sold under this one
"verifiable authorization boundaries" sentence.

**A4P** ("Agentic Authentication, Authorization and Audit Protocol") — A4P/README.md (Chinese-only; there is
no English A4P doc at all): establishes a cryptographically verifiable record of **human consent** before an
Agent causes a Tool Server to execute a sensitive action. Concretely: "A4P 在 Agent 执行敏感操作前建立用户授权
边界" (A4P establishes a user-authorization boundary before the Agent executes a sensitive operation). It ships
two mandate types (one-time Operation Mandate, reusable Intent Mandate/Token), two user-signature methods
(Ed25519, WebAuthn), and a prepare→complete→verify state machine, with a Python SDK and reference Tool
Server/A4P Server implementations.

**AgentRegistry (A2X)** — a service registry with three retrieval strategies (LLM taxonomy search, vector
search, full-context baseline), heartbeat liveness, and an opt-in gossip cluster. Per `a2x_design.md`: "A2X 可
索引任何带有 `description` 字段的智能体服务" (A2X can index any agent service that has a `description` field) —
i.e. discovery is over free text, not a typed capability contract.

### skillhub
Root README (near-exact EN/ZH translation):
> EN: "**openJiuwen Agentic Hub** is an open-source **Skill hosting and distribution** implementation in the
> openJiuwen ecosystem, intended for self-hosted team deployments."
> ZH: "**openJiuwen Agentic Hub**（本仓库）是 openJiuwen 生态中的 **Skill 托管与分发** 开源实现，供团队在自有
> 环境中部署使用。"

This is the closest thing in the whole scope to an actual admission-gated capability registry: a publish →
(optional AI/rule risk review) → moderation (PENDING/APPROVED/REJECTED) → market-display pipeline, with a real,
if undocumented-in-prose, 30-plus-item security checklist behind it (`check_catalog.py`). "Skill" and
"SwarmSkill" are both single-package artifacts described by a `SKILL.md` frontmatter contract (name,
description, optionally `kind`/`roles`); Agent assets (plugins, connectors, agent-groups) are a second, weaker
admission tier the docs describe with an explicit boundary: "Hub 只做包结构与安全校验，运行时文件是否齐留给
JiuwenSwarm" (Hub only checks package structure & security; whether runtime files are actually complete is
left to JiuwenSwarm — a downstream system outside this repo).

### agent-memory
> EN: "JiuwenMemory is an **AutoGenetic Memory** system... designed specifically for Agents — enabling a
> cognitive leap from 'information storage' to 'autonomous growth' for memory... every memory acts like a
> **gene segment**."
> ZH: "**JiuwenMemory**是...一款专为智能体设计的**自主生长记忆系统（AutoGenetic Memory）**——让记忆从'**信息
> 存储**'向'**自主生长**'进行认知跃迁...每一条记忆都像一段**基因片段**。"

Long-term/mid-term/graph memory with LLM-based extraction, a semantic-conflict admission check before write, an
Ebbinghaus-style decay/forgetting scheduler, and an optional "Dreaming" consolidation pass. The "gene
segment"/"AutoGenetic" language is marketing metaphor over a concrete, verifiable mechanism (scheduled LLM
re-summarization + a scored decay formula) — there is no actual genetic algorithm.

### agent-runtime
> EN: "openJiuwen Agent Runtime (Runtime) is a runtime and deployment system for AI agents. Its goal is to
> move agents reliably from **development** to **production**."
> ZH: "openJiuwen Agent Runtime（简称 Runtime）是面向 AI Agent 的运行时与部署管理系统，核心目标是将智能体
> 从'开发态'稳定地带到'生产态'。"

Deployment/management plane for agent instances (subprocess/Docker/[K8s "coming soon"]), with a thin
request-scoped tenant-injection model rather than verified sandboxing, and a separate, largely undocumented
(ZH-only) control-plane transport-security SDK.

### agent-studio
> EN: "openJiuwen AgentStudio is an all-in-one AI Agent development platform that provides a full-stack
> solution from development to deployment, with low-code / no-code visual design and orchestration tools to
> rapidly build and debug agents and workflows."
> ZH: "openJiuwen AgentStudio 提供一站式 AI Agent 开发平台，为开发者提供从开发到部署的全栈解决方案，采用低代码
> /零代码的可视化设计与编排工具，让开发者快速打造和调试智能体与工作流。"

A visual builder producing a DSL+IR pair per workflow/agent version, executed by `studio-runtime` (which wraps
`agent-runtime`). Faithful EN/ZH parity throughout every doc the sub-reader diffed.

### Brief-pass repos (one line each)
- **agent-infer**: "manages caches and schedules agent workflow requests in or in front of LLM serving
  engines such as vLLM" — inference-serving/scheduling layer, not an orchestration product.
- **agent-tools**: "Code repository for building and managing intelligent agent tools" — in practice a Python
  packaging/entry-point plugin-registration mechanism (`openjiuwentools.components`), build-time composition,
  not runtime admission.
- **agent-dx**: "Agent Distributed Executor (agent-dx) is a distributed execution substrate for agents,
  providing developer tools for agent registration, invocation, and session management" — a CLI/SDK/Executor
  trio on top of Huawei's openYuanrong FaaS platform. "dx" = Distributed Executor, not developer experience.
- **relay**: "Relay is a multi-agent collaboration platform that organizes multiple AI Agents into a real
  team... Most frameworks help you call Agents, Relay helps them work together." Contains an undocumented
  (not mentioned in relay's own README) "OfficeClaw/RelayClaw/JiuwenClaw" subsystem with its own skill catalog
  and a stated pre-install admission gate — see Contradictions.
- **CareerSim-BDCI26**: a CCF BDCI 2026 competition entry ("职场长程生存与晋升挑战"), not a platform component —
  but its submission format (`manifest.json` + `SKILL.md` + `career_sim_runner validate`) is secondary evidence
  of ecosystem-wide capability-package conventions.
- **agent-core-java**: "an independent Java implementation for the openJiuwen framework... a Java software
  development toolkit designed for large language model applications" (EN); ZH says "独立框架实现" (independent
  framework implementation) equally explicitly. No described interop/bridge with the Python agent-core SDK —
  read as a parallel, non-interoperating reimplementation, per the README alone (not verified against source).

---

## Goals and direction

- **agent-runtime** has the clearest explicit roadmap of anything read: both READMEs carry an identical
  "Roadmap" section: "Strengthen Docker / Kubernetes deployment paths; CLI integration; Web UI integration" /
  "完善 Docker / Kubernetes 部署能力；补齐 CLI 接入能力；补齐 WebUI 接入能力." This matches concrete stubs found
  in the docs: K8s deployment is literally "# Kubernetes deployment (coming soon)" / "（待开放）"; high-code
  agent publishing is marked "not yet available."
- **agent-studio**'s CHANGELOG documents a completed architectural migration, stated as a direction already
  substantially executed, not just planned: "架构整改: 移除 Agent Service, Builder 作为独立微服务运行，降低服务
  耦合度、明确职责边界" (removed Agent Service; Builder now runs as an independent microservice, reducing
  coupling) and "支持开发态与运行态分离部署...实现开发与运行生命周期隔离" (dev-state and run-state can be
  deployed independently, achieving lifecycle isolation) — i.e. the stated direction is deployable separation
  of build-time and run-time concerns, with the original Java `studio-service` monolith **already removed**
  from the repo as of this HEAD, split three ways into `studio-manager` (Java, management), `studio-runtime`
  (Python, execution — wraps `agent-runtime`), `studio-builder` (Python, NL2/prompt/model tuning).
- **agent-memory**'s Graph Memory is explicitly a *current-state* limitation, not a stated near-term roadmap
  item — both READMEs and `graph_memory.md`'s own FAQ say it plainly: "当前作为独立模块使用，尚未接入
  `LongTermMemory.add_messages` 主流程" (currently an independent module, not wired into the main pipeline) —
  the doc frames this as a standing architectural fact, without committing to when/whether it will be wired in.
- **A4P**'s own SDK design doc (§10, §12) reads as an explicit, itemized "not yet done" list rather than a
  vague disclaimer: production TLS, inter-service auth between A4P Server and Tool Server, rate limiting,
  **audit persistence**, permission isolation, private-key rotation, multi-keyId rollout windows, and a shared
  pending/credential/usage store for multi-replica deployment are all named as gaps the current single-process,
  in-memory-pending implementation does not cover. This is the single most load-bearing "current implementation
  vs. final design" distinction found in the whole scope, because it is A4P's *audit* half that is admittedly
  unbuilt (see Findings, Evidence and provenance).
- **skillhub**'s CHANGELOG shows a completed product-identity migration ("产品展示名与文档由 SwarmSkillsHub /
  SkillHub / TeamSkillsHub 统一为 openJiuwen Agentic Hub") explicitly **not** propagated to internal identifiers
  ("仓库目录、Docker/K8s 内部名、`swarmskill` 类型与官方域名暂不改" — repo directory, Docker/K8s internal names,
  the `swarmskill` type string, and the official domain were deliberately left unchanged) — a self-acknowledged
  external/internal identity mismatch, directly relevant to how much a capsule's own identity/lineage model
  should trust a product's display name versus its internal type strings.
- **AgentRegistry**'s cluster/heartbeat modules are explicitly designed as strictly optional and
  backward-compatible, stated as a hard design invariant, not just current behavior: all three optional
  modules (auth/heartbeat/cluster) carry a documented "向前兼容承诺" (forward-compatibility promise) that
  behavior with the module un-configured must be byte-equal to behavior with the module entirely absent,
  enforced by named regression tests.

---

## Findings relevant to the capsule

### Capability reuse — skills, tools, plugins, capability assets

- **skillhub is the primary capability-reuse mechanism in this scope.** A Skill is one package: root
  `SKILL.md` with YAML frontmatter (`name`, `description`, optional `display_name`/`author`/`tags`); a
  SwarmSkill adds `kind: swarm-skill` and a non-empty `roles[]` array (≥2 roles, unique `id`s). **Important
  correction to a plausible a-priori reading**: a SwarmSkill is *not* a mechanism for composing multiple
  already-published, independent Skill capsules into a new one — it is a single artifact whose one `SKILL.md`
  declares multiple agent personas/roles and how they coordinate, not a graph referencing other Skills by ID.
  Quote: "SwarmSkill 将多智能体协作中的角色分工、任务流程和协作规则沉淀为可复用的团队级技能" (SwarmSkill
  crystallizes role division, task flow, and collaboration rules from multi-agent collaboration into a
  reusable team-level skill).
- Non-Skill-like package types (`tools`, `mcp-stdio`, `restful-api`, and four Agent-asset types) use a
  `plugin.yaml` manifest instead, with a required field set (`name`, `version`, `display_name`, `description`,
  `runtime.type`, `metadata.author`, `metadata.tags[]`, and, for non-Skill-like types only,
  `compatibility.python` per PEP 440).
- **agent-tools** provides a *different* kind of capability reuse: build-time Python packaging with
  entry-point self-registration (`[project.entry-points.'openjiuwentools.components']`) — sub-packages
  register components/frontends into a shared plugin namespace at wheel-install time. This is composition
  plumbing with **no described verification step, no capability manifest/schema beyond the package
  name+version, and no runtime admission gate** — a useful contrast case for what capability reuse looks like
  *without* a capsule-style admission gate.
- **agent-studio**'s Skill packaging (per `docs/FAQ/faq.md` §4) is a third, file-based format: a folder
  containing exactly one subfolder named to match the Skill name declared in `SKILL.md`, `SKILL.md` at that
  folder's root, package size <10MB. `SkillEntity`/`SkillVersionEntity` exist in agent-studio's own DB schema
  (with `latest_version`, `used_version`, `published_asset` fields) but **there is no REST API reference for
  Skill CRUD** in agent-studio's docs — a documentation gap the sub-reader flagged directly (grepped `rest-api*
  .md` for "skill," zero hits).
- **relay** contains an entire undocumented (not surfaced in relay's own top-level README) skill-catalog
  subsystem — "OfficeClaw/RelayClaw/JiuwenClaw" — bootstrapped from `office-claw-skills/BOOTSTRAP.md`,
  organizing skills into 4 categories via a `manifest.yaml`. See Contradictions for the `skill-vetter` finding.
- **CareerSim-BDCI26**'s submission format (`manifest.json` + `design/skills_design.md` + `skills/<name>/
  SKILL.md`, validated via `career_sim_runner validate --submission solution`) is a fourth independent
  data point for the same `SKILL.md`-as-portable-unit convention recurring across the ecosystem.
- **Cross-cutting negative finding**: across skillhub, agent-studio, and CareerSim, no composition mechanism
  found anywhere verifies its references at admission time. skillhub's own doc states the "专家团"
  (agent-group) asset type is admitted without checking that its declared `agents[]` members or `leader`
  actually exist ("不因缺少 `agents/` 成员目录或 `leader` 拒发"). This is a direct, quotable gap relative to a
  capsule design that wants composition integrity enforced at admission.

### Contracts — inputs, outputs, preconditions, effects, permissions, cost

- **skillhub's Skill/SwarmSkill contract is prose, not typed.** The schema has no `inputs`/`outputs` type
  fields, no declared `permissions`/capabilities-required field, no dependency/version-range declaration, no
  signature/identity field. The contract *is* the free-text `description` field plus a name/version/tags
  envelope. Where a `capabilities[]` array does exist (Agent-asset marketplace API detail response), skillhub
  explicitly does **not** verify it against package contents: "不因文件缺失拒发，不校验 SKILL frontmatter / JSON
  内容" — so even declared capability lists are unverified metadata, not an enforced contract.
- **agent-studio has the most concrete typed input/output contract found anywhere in this scope**, at the
  workflow level: a Start node defines typed parameters (String/Number/Boolean/Object-up-to-5-levels/File/
  Array), each carrying a Parameter Description that is *itself machine-consumed* ("When the workflow is bound
  to an agent, the large model uses this description to decide how to automatically extract information from
  user conversations"), a Required flag, and a Default Value; an End node defines either free-text templated
  output or a "Task feedback" mode returning structured JSON — "upgrading the workflow's return from natural
  language conversation to a programmatically callable standardized data format." At the Agent level, the
  `App` table carries explicit `input_params`/`output_params TEXT` fields separate from internal config. No
  permissions contract was found at the Agent/Workflow level (auth is platform-wide, not per-artifact); Plugin
  artifacts do carry something closer to a formal interface contract (`02-user-guide.md` §7.1.3.2 has
  subsections literally titled "接口契约定义" / Interface Contract Definition, Authentication Configuration,
  Lifecycle and State Control) but this is scoped to Plugins/Tools, not to Agent/Workflow.
- **A4P's Mandate is a contract about one action, not about a capability.** An Operation Mandate pins an exact
  `{action, params}` pair plus a `validTime.until` expiry — it is a single-use authorization for one call, not
  a standing declaration of what a capability can do. Intent Mandates/Tokens generalize this to an action
  whitelist with per-field parameter constraints (exact / `"*"` wildcard / glob) and an optional
  `executionPolicy.maxExecutions` — the closest thing to a "cost" or usage-quota concept found in the whole
  scope.
- **No cost/pricing field was found declared on any capability artifact** across all five deep-dive repos.

### Admission and validation

This is the theme with the most concrete cross-repo evidence, and the one the brief's opening warning is most
directly aimed at — several of these mechanisms are described under vocabulary that would not match a grep for
"admission" or "precondition":

- **skillhub — the most fully worked-out admission gate in the whole scope.** Pipeline (quoted): "发布校验 ->
  审查（可选）-> 审核 -> 市场展示" (publish-time structural validation → optional risk review → moderation →
  market display). Version states are strictly `PENDING`/`APPROVED`/`REJECTED`. The actual checklist behind
  the vague "审查" (review) prose — undocumented anywhere in the prose docs, found only by reading
  `marketplace/skill_review/domain/check_catalog.py` directly — has 30-plus named checks across six categories:
  package spec & auditability, prompt-injection/instruction security, secrets/data exposure, execution/
  side-effect boundary (including path-traversal, shell exec, destructive ops, resource exhaustion), goal-
  consistency & user-consent boundary, and provenance/supply-chain (including typosquatting/impersonation
  detection). Whether every listed check is wired into the live default pipeline was not verified (the
  sub-reader did not trace the runtime call graph) — flagged explicitly as unverified. **There is a real
  bypass**: "携带有效 `X-System-Token` 的发布请求直接 `APPROVED`，跳过审查与审核" (requests carrying a valid
  System Token are auto-approved, skipping both review and moderation) — a genuine trust-boundary hole if such
  tokens leak. Agent-asset admission (plugins/connectors/agent-groups) is a deliberately **weaker second tier**:
  "Hub 只做包结构与安全校验" (Hub only checks package structure & security) — no frontmatter/JSON content
  validation, no requirement that a plugin declare at least one capability component.
- **A4P — an admission gate for actions, described without ever using the word "admission."** The
  prepare→complete→verify state machine functions as a gate: a Tool Server must reconstruct the pending
  operation from the *current* business request and refuse to trust parameters fed back by the Agent or
  Mandate — "Tool Server 必须使用'当前业务请求'重新构造待执行操作，不能直接信任 Agent 或 Mandate 反向提供的业务
  参数." "Fail closed" is used explicitly and repeatedly (e.g., storage unavailable → fail closed).
- **agent-memory — a real semantic admission gate before writing to long-term memory**, again under different
  vocabulary: `MemUpdateChecker` classifies each candidate memory against existing memories into 冗余
  (redundant) / 冲突 (conflicting) / 共存 (coexist) before writing, dropping or flagging redundant/conflicting
  items; a second LLM-mediated check (`semantic_validation.md`) validates explicit user UPDATE/DELETE
  directives against the targeted memory before executing them. There is **no human review step** anywhere in
  the memory pipeline — it is fully LLM-automated, and there is no confidence-threshold admission gate on
  extraction itself (the closest analog, a similarity `threshold`, gates *retrieval*, not *writing*).
- **agent-studio — a single synchronous validation step at publish time**, not a separate review workflow: "在
  发布前自动校验工作流配置的有效性" (automatically validate workflow configuration before publishing), failing
  with a structured 400 error (`error_code`, `error_msg`, `error_reason`, `error_suggestion`, `details`). What
  the validation actually checks is **not documented** anywhere the sub-reader read — only that it exists and
  can fail. A second, cruder admission control exists at import time: a `front_page_block_nodes` config can
  reject import of workflows containing "受限节点" (restricted node types), plus a `STRICT`/`SPACIOUS` import
  mode toggle.
- **relay — a stated but unverified pre-install gate.** `office-claw-skills/BOOTSTRAP.md` names a
  `skill-vetter` skill explicitly as "安全优先的 skill 审核与风险评估，用于安装前审查" (security-first skill
  review and risk assessment, for pre-install review) — a genuine admission-gate *claim*, but the sub-reader
  did not open `skill-vetter/SKILL.md` itself (out of scope for the brief pass), so rigor/automation is
  unverified. This entire subsystem is invisible from relay's own top-level README — a shallow README-only
  read would have missed it entirely, exactly the failure mode the brief opened by warning against.
- **CareerSim-BDCI26** — a documented `career_sim_runner validate --submission solution` step against the
  manifest/skill structure before a submission runs, a narrowly-scoped but concrete admission-validation
  instance.
- **AgentRegistry (A2X) has no content-quality admission gate at all** — registration is upsert-only,
  field-additive, with only a *format*-level check (`FormatValidator` checking `min_version` per service type
  in `register_config.json`) — it checks the registration envelope, not whether the underlying service/agent
  is any good, safe, or does what it claims.

### Versioning, lineage, deprecation

- **skillhub**: multiple versions coexist per asset; the public market card always resolves to the latest
  **APPROVED** version — "待审核版本不会覆盖已公开的稳定版本" (a pending version never overwrites the public
  stable one). **Key negative finding**: there is no soft "deprecated"/"withdrawn" state — only PENDING/
  APPROVED/REJECTED. The only way to remove a live version is a hard, irreversible DELETE (`DELETE /plugins/
  {asset_id}/versions/{version}`, restricted to the publisher or a System Token), with an explicit warning that
  `version=all` "不可逆" (irreversibly) removes every version and its object-storage files. There is no
  npm/crates.io-style "yank" (mark bad, keep resolvable for pinned consumers) — a rejected version can only be
  resurrected by a moderator flipping REJECTED→APPROVED or by shipping a new version. A separate, unrelated
  "撤回/revoke" state machine exists, but it is scoped to *group access grants* (a group's authorization to see
  a Skill), not to the Skill version's own lifecycle — the sub-reader flagged this distinction explicitly to
  avoid conflating the two.
- **A4P**: protocol versioning lives only in the `type` string (`a4p/v1/operation-mandate`, etc.) — a single v1
  epoch, no v2/migration path discussed. A credential store has `schemaVersion: 2` with old-format records
  explicitly rejected. **Key rotation/revocation is an explicitly named, unresolved gap**: "私钥轮换、多个
  keyId 的灰度窗口和旧 token 验证策略" (private key rotation, multi-keyId gradual rollout, old-token
  verification policy) are listed in §10 as not yet designed/tested. No token-revocation HTTP endpoint is
  documented — only expiry (`validTime`/`expireAt`) and per-token execution quotas (`maxExecutions`) limit a
  live mandate/token's life.
- **AgentRegistry**: no per-entry version history at all — updates are upsert-only ("顶层字段 upsert：相同键直接
  替换，新键追加；不删除既有字段"), overwriting the live record with no way to retrieve a prior state. What does
  exist is a *format* version per service type (`min_version` in `register_config.json`) and, in cluster mode,
  a `(updated_at_ms, node_id)` last-write-wins version used purely for node-to-node conflict resolution, not
  exposed to users as entry history.
- **agent-memory**: **no content-level versioning of individual memory units** — `update_mem_by_id` overwrites
  `content` in place, with the old content simply gone (no diff, no history log). What exists instead is a
  reversible **soft-delete/hide** toggle via the Ebbinghaus forgetting mechanism (`blacklisted` true/false) —
  a two-state visibility switch, not a version history; "recall" un-forgets a hidden memory, it does not
  restore a prior edited content state.
- **agent-runtime**: no documented redeploy-in-place or rolling-update mechanism for a deployed agent — the
  doc named for exactly this topic ("3. Agent Deployment.md") is thin, almost entirely about deployment
  *strategy* (subprocess/Docker/K8s startup mechanics) rather than lifecycle *states*; the actual state enum
  (`PENDING`, `RUNNING`, `STOPPED`, `FAILED`, `RUNNING_NOTREADY`) exists only in source code
  (`management/.../models/enums.py`), never quoted in any prose doc.
- **agent-studio**: the most mature versioning model found — explicit draft/published status
  (`AgentVersion.is_online`, `WorkflowEntity.deploy_wf_version`/`last_version_id`), named version history with
  `version_name`+`version_note` per publish, immutable version snapshots of DSL+IR files at publish time,
  reference-counting before deletion (versions shared to the Asset Plaza cannot be deleted until unshared),
  and published-version immutability of global config. True content "rollback" is not directly named for
  Agent/Workflow versions in the docs read (though CHANGELOG confirms "版本回退"/version rollback exists for
  Plugins specifically), but the version-list + snapshot machinery would support it.
- **agent-dx**: not artifact versioning, but a concrete **session-lineage/branching** mechanism worth noting —
  `/fork <turn-id> <new-session-ctx-id>` creates a new session lineage from a specific completed conversation
  turn. This is session lineage, not capability lineage, but it is the only "fork from a point in history"
  primitive found anywhere in this scope.

### Evidence and provenance

- **A4P produces a defined, signed proof-of-authorization artifact (the Mandate), but this is explicitly not
  an audit log.** Quoted Operation Mandate example includes `operationId`, `subject`, `operation`, `validTime`,
  `userAuthorization`, `displayText`, and Ed25519 server+user signatures over a canonicalized JSON payload.
  **But** the pending entry is deleted on successful `complete` ("成功后先消费 pending") — it is consumed, not
  archived — and the SDK explicitly disclaims managing business-side idempotency/result storage: "SDK 不管理；
  demo 用内存字典；业务方负责幂等和结果缓存." **The single most important negative finding of this whole
  report**: despite A4P's full name being the "Agentic Authentication, Authorization, **and Audit** Protocol,"
  the word "审计"/audit occurs only 5 times in the entire A4P directory and **zero times in A4P_PROTOCOL.md**,
  the actual spec document. Every occurrence frames audit as something the *deployment layer*/integrator must
  add externally, never something A4P itself persists: "为 A4P Server 和 Tool Server 之间增加认证、网络保护、
  限流和审计" (add authentication, network protection, rate limiting, **and audit**, between A4P Server and Tool
  Server — listed as an integrator TODO); "把用户拒绝、授权验证、额度消费和业务执行结果写入外部审计系统" (write
  user rejections, authorization verifications, quota consumption, and business execution results into an
  **external** audit system). A4P specifies no audit-log schema, storage, or retention policy of its own.
- **"Verifiable authorization boundary"** — the exact phrase appears only in the *root* agent-protocol README,
  never inside A4P's own docs (A4P's closest phrasing drops "verifiable": "A4P 在 Agent 执行敏感操作前建立用户
  授权边界"). Concretely, "verifiable" attaches to the Mandate/Token artifacts themselves — the User Authorizer
  can cryptographically confirm a mandate came unmodified from a trusted, locally-pinned A4P Server instance —
  not to an abstract audit trail. This is a real, precise mechanism (mandate *integrity/provenance*
  verification), just narrower than the root README's framing implies, and it is not substantiated by A2X at
  all (A2X's registry entries have no cryptographic identity — see below).
- **AgentRegistry keeps its own audit log file** (`auth_data/audit.log`, per `auth_design.md`), but its byte-
  level schema is never documented — only its existence, gitignore status, and a regex-tested constraint that
  plaintext tokens must never appear in it.
- **agent-memory's provenance is uneven by memory type.** Graph Memory has the strongest provenance in this
  entire scope: every write creates an `Episode` storing the original content and every entity/relation
  mentioned in it, giving full traceability back to source. By contrast, the **main flat-memory pipeline**
  (UserProfile/Semantic/Episodic units — the default path) has **no documented source-message backlink** in its
  schema (`mem_id/content/type/timestamp/fields/is_important/blacklisted` — no `source_message_id` or
  `source_session_id`), unlike Graph Memory's Episode linkage or Middle-Term memory's `message_mem_id`. This
  means the default (non-graph) memory path cannot necessarily be traced back to the exact conversational turn
  that produced it — a genuine provenance gap directly relevant to a capsule design that wants lineage on every
  unit of stored knowledge.
- **agent-runtime's ZH-only security module** (`docs/zh/5. 安全模块.md`) provides signing/verification and
  certificate-pinned handshake authentication for control-plane links (Manager↔Gateway↔AgentServer), which
  *could* serve as an evidence primitive for node identity — but this is transport-layer trust for Runtime's
  own internal wiring, not an audit trail of agent actions, and it explicitly does not reference A4P anywhere.

### Composition — how capabilities connect, and whether anything composes systems

- **No mechanism found anywhere in this scope verifies composition references at admission time** (repeated
  above under Admission — restated here because it is the central composition finding): skillhub's
  agent-group asset type is admitted without checking its declared members exist; SwarmSkill composes roles
  within one artifact, not other artifacts by reference.
- **AgentRegistry's A2X search composes *discovery*, not systems**: an LLM navigates a taxonomy tree built over
  free-text `description` fields (name+description+category), never over declared input/output/permission
  contracts. Quoted design principle: "每次 LLM 路由决策只看到当前可见子树...模型只输出可见边界节点的显示名称"
  (every LLM routing decision sees only the current visible subtree; the model only outputs the visible
  boundary nodes' display names) — sophisticated text-relevance routing, not capability-contract matching.
  skillhub's own marketplace dispatch is architecturally similar and equally text-driven: its `CatalogRecord`
  data model has no typed input/output schema and no permission/capability-contract field, only
  `description`/`retrieval_text`/free-form `metadata`; the DB-level keyword endpoint is explicitly non-semantic
  ("`search_keyword` 走数据库关键词匹配，不走语义检索").
- **agent-studio composes workflows as typed node graphs** (`{"nodes": [], "edges": []}`), and an Agent
  artifact bundles typed references to sub-capabilities — `{"nodes": [], "tools": [], "workflows": [],
  "mcp_servers": [], "skills": [], "knowledge_repos": []}` — this is the closest thing in the whole scope to
  "composing a system rather than a function": an Agent is explicitly a typed bundle of workflow/tool/MCP/
  skill/knowledge references. Whether those references are validated to exist/resolve at publish time is not
  documented (only that "workflow configuration" validation happens generally).
- **agent-tools' entry-point registration** composes at Python-package build time (wheel-install-time
  discovery into a shared plugin namespace) — a form of composition, but purely mechanical, with no contract
  or admission layer riding on top of it.

### Research-agent workflows — literature, hypotheses, experiments, reports

Nothing in this scope's five deep-dive repos or six brief-pass repos addresses literature review, hypothesis
tracking, experiment management, or research-report generation directly. The nearest adjacent material:
- **agent-memory**'s Dreaming mechanism performs a bounded "generalize from repeated evidence" inductive step
  with explicit anti-hallucination guardrails, quoted in full because they read like a minimal evidentiary
  standard: "护栏（必须同时满足才输出归纳条目）：(1) 有两处及以上相互独立的佐证；(2) 归纳属于公认常识而非主观
  臆测...；(3) 宁可不归纳，也不要编造" (guardrails, all required to emit a generalized entry: (1) two or more
  independent pieces of evidence; (2) the generalization must be common-sense-level, not speculative; (3)
  prefer not generalizing over fabricating). This is the single closest thing in this whole scope to a
  "claim-to-evidence" discipline, and it lives inside a memory-consolidation prompt, not a research-workflow
  product.
- **CareerSim-BDCI26** ships a "decision_report.md" as part of its submission design docs, but this is a
  competition artifact, not a research-report generation capability of the platform.
- No repo in this scope names literature search, hypothesis generation, or experiment orchestration as a
  stated purpose. (Note: `deepsearch` and `sciencediscovery` exist as sibling repos under
  `openjiuwen/` but were explicitly out of this scope per the brief — another agent's territory.)

### Stated non-goals and boundaries

- **Universal legal boilerplate**, identical (EN/ZH) across every repo read: "This product serves solely as a
  workflow orchestration tool and does not embed any AI model capabilities. When users integrate AI models for
  specific business scenarios, they shall bear full responsibility for compliance obligations under the EU AI
  Act..." / "本产品仅作为流程编排工具，不包含 AI 模型能力；用户在连接 AI 模型用于特定业务场景时，需自行承担
  欧盟 AI 法案等相关合规义务。" — this is a legal template, not an architectural non-goal, but it establishes
  that *nowhere* in this scope does a repo claim to ship or be responsible for the model itself.
- **A4P**, itemized and explicit (§10/§12, quoted above under Goals and direction): not production TLS, not
  inter-service auth, not rate limiting, not audit persistence, not key rotation, not multi-replica shared
  state, not distributed transactionality between authorization-consumption and external business writes
  ("SDK 保证同一进程内一个 pending 最多 complete 成功一次，但不保证授权消费和外部业务写入构成分布式事务").
  Private-key custody is explicitly pushed to the caller: "Ed25519 私钥由调用方的生产密钥系统管理，SDK 不负责
  持久化或解锁."
- **skillhub**: explicitly does not verify Agent-asset runtime-completeness — "运行时文件是否齐留给 JiuwenSwarm"
  (whether runtime files are actually complete is left to JiuwenSwarm, a separate downstream repo/system). Base
  deployment has no LLM/embedding dependency at all — hybrid/semantic retrieval, recommendations, and the
  online-sandbox are all optional add-ons, not core, per §6 部署边界 of the product overview.
- **AgentRegistry**: a hard architectural non-goal, stated and grep-verified per the sub-reader: the core
  `register/` module must never import `auth/`, `heartbeat/`, or `cluster/` — "register 不知道鉴权/心跳/集群
  存在" (register doesn't know auth/heartbeat/cluster exist) — all three are wired in only via callback
  injection, an explicit decoupling non-goal, not an accident.
- **agent-runtime**: K8s deployment, CLI integration, and Web UI integration are all self-declared "not yet
  done" (see Roadmap above) rather than silent gaps.
- **agent-studio**: no dedicated "non-goals" section was found; the closest is the documented build-time/
  run-time module separation, and a scoped, stated limitation that Task Workflows specifically exclude certain
  node types (input, message, questioner, Q&A, object-extraction, Agent nodes).

---

## Contradictions and ambiguities

1. **A4P's name vs. its content.** The protocol's own name promises "Audit" as one of its three pillars, but
   the actual spec document (`A4P_PROTOCOL.md`) never mentions audit at all, and every one of the 5 total
   audit-related sentences in the whole A4P directory frames it as an external/deployment-layer responsibility.
   This is a genuine, quotable contradiction between the product's name/README-level claim and what the
   protocol document itself specifies — not a translation issue, a scope-vs-naming issue.

2. **A4P and A2X are bundled by the root README under one "verifiable authorization boundaries" sentence, but
   share no cross-references, no common identity model, and no common credential format.** A2X's own auth
   module (bearer API keys, `a2x_pat_...`, sha256-hashed at rest, governing who may CRUD the registry) is
   architecturally and cryptographically unrelated to A4P's Ed25519/WebAuthn-signed mandates (which govern
   whether an Agent may cause a specific business action after human consent). Neither doc set mentions the
   other, despite living in the same repo. A2X registry entries also have **no cryptographic identity at
   all** — just a deterministic `sha256(name)[:16]`-derived string ID — in sharp contrast to A4P's signed
   subjects. The root README's claim that this bundle "establishes verifiable authorization boundaries across
   different runtime environments" is substantiated by A4P alone, not by A2X.

3. **The single largest EN/ZH divergence pattern in this scope is not word-level mistranslation — it is
   structural absence.** A4P and AgentRegistry (both inside agent-protocol) have **zero English documentation**
   — README.md, A4P_PROTOCOL.md, A4P_SDK_DESIGN.md, and every AgentRegistry doc are Chinese-only, despite the
   root agent-protocol README existing as a clean, faithful EN/ZH pair. An English-only reader who follows the
   root README's English promise of "verifiable authorization boundaries" hits a documentation wall in both of
   the two subsystems most relevant to that exact claim. Likewise, **skillhub's entire substantive
   documentation tree (docs/zh/) has no English counterpart** — only the root README is EN/ZH paired; the
   product-overview, admission-pipeline, roles/permissions, and API-reference docs exist in Chinese only.
   **agent-runtime** has a narrower but structurally sharper version of the same pattern: `docs/en/SUMMARY.md`
   lists 5 chapters (0–4); `docs/zh/SUMMARY.md` lists 6, adding "5. 安全模块" — the English table of contents
   doesn't even acknowledge the security-module doc exists, so the question "does agent-runtime's security
   model relate to A4P?" is structurally unanswerable from English docs alone.

4. **agent-core-java's README states two different minimum JDK versions.** EN: "Java 17 or higher." ZH:
   "Java 21或更高版本" (Java 21+). These directly contradict each other on the minimum supported JDK — flagged
   by the sub-reader as a genuine, not cosmetic, inconsistency. (A secondary, likely-just-stale divergence: the
   example Maven artifact version differs, 0.1.12 EN vs 0.1.7 ZH.)

5. **skillhub's ZH README claims more than its EN counterpart for the same feature.** ZH Features list: "Skill
   发布与**版本治理**" (publish and *version governance*); EN: "publish and version Skills" — ZH implies
   moderation/governance is part of the headline feature, EN reads flatter. Neither README actually names the
   admission/review subsystem explicitly — both undersell how central it is; the difference is only in degree.

6. **relay's README describes a Node.js/pnpm build toolchain in Quick Start, but its own Architecture section
   says the core engine is Python** — "Relay 是平台的核心引擎，采用 Python 构建" (Relay is the platform's core
   engine, built with Python) — present identically in both EN and ZH, so this is an authoring inconsistency
   within the document, not a translation divergence. Not independently verified against source (out of scope
   for a README-level pass).

7. **relay's own top-level README says nothing about the "OfficeClaw/RelayClaw/JiuwenClaw" skill-catalog and
   admission (`skill-vetter`) subsystem that visibly exists in the repo tree** (`office-claw-skills/`,
   `office-claw-config.json`, `RelayClawAgentService.ts`, `relayclaw-sidecar.ts`,
   `relayclaw-security-proxy.ts`, `OfficeClawHub.tsx`, a `build-jiuwenclaw-wheel.mjs` script). This is
   discoverable only by opening `office-claw-skills/BOOTSTRAP.md`, one directory-level down from what a
   README-only pass would read — precisely the failure mode the brief opened by warning against (the
   `symphony` admission-gate grep miss). Two points worth carrying into the capsule design directly: (a) this
   is a second, independent instance of "ClawHub"/"Claw"-branded naming, alongside skillhub's own "ClawHub
   compatibility layer" (see next point) — whether these are the same external ecosystem or coincidentally
   similar naming was **not** established (no web access in this task); (b) the bootstrap doc names a
   `skill-vetter` skill explicitly as a pre-install security review gate, a genuine admission-gate claim that
   was not verified further (its own `SKILL.md` was not opened, out of scope for the brief pass).

8. **skillhub's "ClawHub compatibility layer"** (`docs/zh/7. API参考/ClawHub兼容层.md`) is framed precisely as
   a protocol-compatibility shim for an *external* CLI ecosystem, not a description of ClawHub as a product:
   "ClawHub CLI 兼容层...协议适配：供 ClawHub CLI 及生态工具无缝接入" (protocol adaptation, for ClawHub CLI and
   ecosystem tools to integrate seamlessly). The response schema it mimics
   (`ClawhubSkillDetail.moderation.{isSuspicious, isMalwareBlocked, verdict, reasonCodes, engineVersion}`) uses
   fields skillhub's own native moderation model doesn't otherwise have (native states are just PENDING/
   APPROVED/REJECTED) — strong circumstantial evidence that ClawHub is a real external skill-registry product
   with its own malware-scanning verdict schema, and skillhub is shimming that shape for drop-in client
   compatibility. **This is inference from API shape, not a confirmed fact** — no web access was available to
   verify what ClawHub actually is, and this report should not assert it as established. It is left open
   whether relay's "OfficeClaw"/"RelayClaw" naming (finding 7) and skillhub's "ClawHub compatibility" concept
   are the same referent.

9. **agent-studio's `agent_builder/serve/` does not serve built agents/workflows**, despite being a plausible
   a-priori reading of the module name (and despite the original task framing assuming it might). Its full
   content is 2 lines: "serve 模块 — 服务化MindSophon中的各模块...当前使用flask作为基础的controller和http服务"
   (the serve module services the various modules within MindSophon [agent_builder's internal codename] as
   Flask-based services) — its actual API surface is NL2-generation, prompt-optimization, and model-tuning
   endpoints, i.e. build-time tooling. The real execution path for a published agent/workflow is
   `studio-manager`'s REST façade calling into `agent-runtime`/`studio-runtime`. Not a doc contradiction
   exactly, but a naming trap worth flagging so it isn't repeated in the capsule design's own reading of this
   repo.

10. **agent-memory's Graph Memory is sold in both READMEs as part of "knowledge accumulation," but is
    documented, in the same repo, as a disconnected code path**: "`LongTermMemory.add_messages` does not
    currently call `GraphMemory.add_memory`" (graph_memory.md FAQ, matching both README's own text). A caller
    must invoke `GraphMemory.add_memory` explicitly; ordinary memory writes never populate the graph. This is
    a documented current-state fact, not something inferred, and not framed anywhere as an imminent roadmap
    item.

---

## What I could not determine

- **Whether A4P has any private-key-rotation or token-revocation code despite the docs flagging it as an
  untested/undesigned gap** — no source was read for A4P beyond `errors.py` and directory listings; "not
  designed per docs" is not the same claim as "definitely absent in code."
- **Whether every check in skillhub's `skill_review/domain/check_catalog.py` (30+ named checks) is actually
  wired into the live default pipeline**, or which are gated by further config not documented anywhere — the
  runtime call graph (`engines/registry.py`, `runtime/runner.py`) was not traced.
- **What ClawHub actually is** (external product, its owner, whether it is the same referent as relay's
  "OfficeClaw"/"RelayClaw" subsystem) — inferred only from API response shape in skillhub's compat layer; no
  web access was available in this task to confirm.
- **Whether agent-studio's exported `.jsonl` DSL, or its IR file, is consumable by anything outside
  agent-studio's own `studio-manager`/`studio-runtime` pair** — e.g., by `agent-core`, by `agent-runtime` used
  as a standalone library, or by skillhub. Not addressed anywhere in agent-studio's docs; a grep for
  "skillhub" across `docs/en/` returned zero hits. This is a doc silence, not a confirmed negative — the
  capsule design should not assume either portability or lock-in here without asking the agent-studio team
  directly.
- **What agent-studio's publish-time workflow validation actually checks** (dangling edges, type mismatches,
  missing required node configs, permission checks on referenced plugins/MCP/knowledge bases) — only that it
  exists and fails with structured errors is documented; the rule-set itself is not, and verifying it would
  require reading `studio-manager-service` source, out of scope for a doc-level pass.
- **The byte-level schema of AgentRegistry's own `auth_data/audit.log`** — existence, gitignore status, and a
  no-plaintext-token constraint are documented; its field format is not.
- **Whether agent-runtime's `docker`/`k8s` deployment modes provide any *deliberate* multi-tenant isolation
  guarantee**, as opposed to an incidental side effect of container/pod boundaries — never stated as a security
  property in any doc read. The default `subprocess` mode has no described isolation mechanism at all beyond
  bare OS process separation, and the docs never discuss that as a security boundary.
- **agent-runtime's full IR JSON manifest schema** (the actual deployable artifact's field list/types) — the
  docs describe how to submit it (multipart upload plus `name`/`mode` query params) but never show its
  internal shape.
- **`agent_builder/prompt/README.md`** is functionally empty (17 bytes, a bare Chinese H1 title with no body)
  — a genuine documentation gap, not a reading-effort shortfall.
- **agent-core-java's relation to the Python SDK beyond the README's bare "independent implementation"
  claim** — per scope instructions this repo's ~1,497 other docs were not read; whether the two share any
  wire-compatible schema, interop bridge, or even design-philosophy documentation was not investigated. A
  pointer surfaced incidentally (via the harness's own project-instruction injection, not sought out): the
  repo's `AGENTS.md` mentions a "Card/Config split" (`AgentCard`, `ToolCard`, `WorkflowCard`,
  `SysOperationCard` for identity/metadata, vs. configs for runtime behavior) that sounds directly relevant to
  a capsule's contract+identity split — flagged only as a candidate for a targeted follow-up read, not as
  verified README content, since it fell outside this pass's explicit README-only scope for this repo.
- **`docs/zh/1. 快速开始.md` (agent-runtime)** was not read in full and not diffed against its EN counterpart
  beyond the SUMMARY-level structural gap already reported (finding 3) — small content divergences there
  cannot be ruled out.
- **The full content of several lower-priority skillhub docs** (快速开始, 在线体验运行时, 检索系统 indexing/
  retriever docs, 推荐系统, 运维指南 sub-docs, both CLI sub-package READMEs, the raw OpenAPI YAML) — deprioritized
  per the brief's own stated ordering; the sub-reader judged the higher-priority docs sufficient for the
  capsule-design questions but flagged the gap rather than omitting it silently.
- **relay's `office-claw-skills/refs/bug-diagnosis-capsule.md`** — the filename itself uses "capsule"
  terminology and was not opened (out of scope for the brief README-level pass); flagged as a candidate for a
  follow-up targeted read if capsule-naming precedent in this codebase matters to the design.
- **AgentRegistry's `backend_api.md`, `environment.md`, `frontend_design.md`, `ui/README.md`** were
  deprioritized and not read; could contain additional schema/versioning detail not captured here.

---

## Capability concern → repo → coverage gap

| Capability concern | Which repo already provides it | What it does not cover |
|---|---|---|
| Package/host a reusable capability (a "Skill") | **skillhub** — `SKILL.md` frontmatter contract, publish→review→moderation pipeline, PENDING/APPROVED/REJECTED versioning | No typed input/output/permission schema (contract is prose `description` + name/version/tags); no composition-reference verification; no deprecation state, only hard delete or moderator reversal; System-Token bypass skips admission entirely |
| Verify a capability is safe/correct before it's trusted | **skillhub** — 30+-item `check_catalog.py` risk checklist (prompt injection, secrets, destructive ops, supply-chain/typosquat) behind the "审查" stage | Checklist is undocumented in prose (code-only); not proven wired into the live default pipeline; Agent-asset (plugin/connector) admission is a deliberately weaker tier that skips content validation entirely |
| Bind a human's consent to a specific sensitive action | **A4P** — signed Operation/Intent Mandates, prepare→complete→verify state machine, Ed25519/WebAuthn | No audit log/trail schema at all (explicitly deferred to an external system, despite "Audit" in the protocol's own name); no key rotation/revocation; single-process/in-memory pending state, not production-multi-replica-ready |
| Discover a capability/agent by capability | **AgentRegistry (A2X)** — LLM taxonomy search, vector search, heartbeat liveness, opt-in cluster | Discovery is over free-text `description`, not a typed contract; entries have no cryptographic identity, just a hashed name string; no content-quality admission, only format/version checks; no cross-reference to A4P despite being bundled together |
| Declare a typed input/output contract on a built artifact | **agent-studio** — typed Start/End node schema on Workflows, `input_params`/`output_params` on Agents | No declared permissions contract at Agent/Workflow level (only Plugins get an "Interface Contract Definition"); validation rule-set behind publish-time checks is undocumented; portability of the DSL/IR pair outside agent-studio's own services is undocumented (doc silence, not a confirmed negative) |
| Version and publish-gate a built artifact, with rollback | **agent-studio** — draft/published status, named version history, immutable DSL+IR snapshots per publish, reference-counted deletion | No explicit "rollback" operation named for Agent/Workflow versions (only confirmed for Plugins); publish-time validation exists but its rule-set is opaque |
| Store and accumulate long-term knowledge, with decay | **agent-memory** — LLM extraction, semantic-conflict admission before write, Ebbinghaus decay/soft-forgetting scheduler, optional Dreaming consolidation, Graph Memory with per-write source Episodes | No content-versioning/rollback (edits overwrite in place); Graph Memory (the one component with strong provenance) is not wired into the default write path; the default flat-memory path has no documented source-message backlink |
| Deploy and run an agent as a service, manage its lifecycle | **agent-runtime** — deploy/list/detail/delete API, subprocess/Docker/(K8s "coming soon") strategies, tenant-context injection | Lifecycle *states* only exist in source, undocumented in prose; no rolling-update/redeploy-in-place documented; "multi-tenant isolation" is asserted as a headline feature but documented only as request-level ID tagging, not verified sandboxing; the one real transport-security SDK it has (control-plane crypto/pinning) is ZH-only-documented and explicitly unrelated to A4P |
| Compose multiple capabilities into a coordinated system | **agent-studio** (typed Agent bundles referencing workflows/tools/MCP/skills/knowledge) and **skillhub's SwarmSkill** (multi-role single-package coordination) | No repo in scope verifies composition references resolve at admission time; SwarmSkill composes roles within one artifact, not other published artifacts by reference; A2X's "search" composes discovery, not systems |
| Package/distribute reusable code/tool logic at build time | **agent-tools** — entry-point plugin registration into a shared Python namespace at wheel-install time | Purely mechanical; no manifest/contract, no verification step, no runtime admission — a contrast case for what reuse looks like without a capsule gate |
| Reproducible research-agent workflows (literature, hypotheses, experiments, reports) | **none of the repos in this scope** | Out of scope for this pass (see `deepsearch`/`sciencediscovery`, explicitly assigned elsewhere); the only adjacent artifact found is agent-memory's Dreaming evidence-guardrail language, which is not a research-workflow product |
