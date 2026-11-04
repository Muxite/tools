# Verification report — jiuwenswarm / skillhub

**Repositories under test and HEAD commits (confirmed first, per protocol):**

- `jiuwenswarm`: `e12bcb31cf6b85a2f6d9ae9c192e75ae50752ed5` — "fix(rsi): keep task deletion resilient when cleanup is blocked" (2026-09-15 21:03:25 +0800)
- `skillhub`: `ff9c37f7a216471929fbbba102553e34e281aaff` — "!262 merge develop into develop" (2026-09-15 14:46:44 +0800)

Verified with `git rev-parse HEAD` / `git log -1` in each repo.

---

### C1. ~765 lines mention `symphony`; three integration shapes (Rails, tools, adapter layer)
**Verdict:** VERIFIED
**Evidence:**
Command: `cd jiuwenswarm && grep -r "symphony" --include="*.py" . | wc -l` → **765** (case-sensitive, lowercase `symphony`, exact match to the claim). For reference: case-insensitive count is 1117, `grep -r "Symphony"` (capitalized) is 323, `-riw` (word-boundary, case-insensitive) is 459 — the claim's number matches only the case-sensitive lowercase count exactly, which is a defensible reading of "mention symphony."

Three shapes confirmed present:
- Rails: `jiuwenswarm/agents/harness/common/rails/symphony/orchestration_rail.py`, `retrieval_context_processor.py`, `tool_stream_events.py`, `__init__.py`
- Tools: `jiuwenswarm/agents/harness/common/tools/symphony_toolkits.py`, `.../skill_retrieval_toolkits.py`
- Adapter layer: `jiuwenswarm/symphony/adapter.py`, `build.py`, `graph_state.py`, `graph_storage.py` (also present in that directory but not named in the claim: `config.py`, `llm.py`, `service.py`, `__init__.py`)

**Note (minor, doesn't change verdict):** these three shapes are not the *only* places symphony is referenced — `grep -rl "symphony" --include="*.py" . | grep -v /tests/` also turns up `server/runtime/agent_adapter/` (3 files), `gateway/channel_manager/` (2), `agents/swarm/providers/` (2), `symphony/skill_retrieval/`, `common/recommendation/`, `common/prompt/`, etc. Inspection of `server/runtime/agent_adapter/interface_deep.py` and `interface_code.py` shows these are wiring/glue code that imports and registers the three named shapes (e.g. `from jiuwenswarm.agents.harness.common.rails.symphony.retrieval_context_processor import ...`, `self._sync_symphony_tools_for_runtime`), not a fourth architecturally distinct integration surface, so the claim's framing holds.

---

### C2. `symphony/evolution/` ~2,821 lines / 8 files; evolves edge weights from plan outcomes, never authors a capability
**Verdict:** PARTLY
**Evidence:** `find jiuwenswarm/symphony/evolution -name "*.py" | xargs wc -l` → exactly **2821 total** across 8 files: `aggregate.py` (458), `models.py` (118), `pack_adapter.py` (96), `pack_store.py` (53), `service.py` (498), `session_consumer.py` (1484), `store.py` (101), `__init__.py` (13).

The dominant mechanism matches the claim exactly. `aggregate.py:36-155` (`build_overlay_from_events`) consumes `plan.outcome` events and produces an overlay of `edges`/`nodes`/`paths` stats keyed by existing skill ids, computing a bounded `runtime_weight` (`aggregate.py:391-407`, `_runtime_weight`, docstring: "SkillGraph reinforces a successful path with a fixed additive step. Symphony applies the same public step size symmetrically to explicitly attributed failures.") — this is pure edge-weight/statistics evolution over an existing graph; no new skill/capability id is ever minted here.

**Note — why PARTLY:** `service.py:358-452` (`_try_distill_skill_packs`) is a second, optional pathway in the same module that goes beyond edge weights. When `config.evolution.enabled` and `config.evolution.flow.enabled` are both true (flow defaults to `True`, but evolution itself defaults to `False` — `jiuwenswarm/symphony/config.py:23-26`: `DEFAULT_SYMPHONY_ENABLED = False`, `DEFAULT_EVOLUTION_ENABLED = False`, `DEFAULT_FLOW_ENABLED = True`) and an external dependency (`openjiuwen.symphony.flow.distill`, which lives in the separate `agent-core` repo at `openjiuwen/symphony/flow/distill.py`) is importable, it groups qualified successful edge-sequences and calls `distill_group` to synthesize a **new "skill pack" artifact** — a named recipe (`pack_id`, `member_ids`, `grade`, `task_description`, `execution_narrative`) — and persists it via `write_packs` (`pack_store.py`). `jiuwenswarm/symphony/service.py:704-740` then surfaces each pack as its own graph node (`"type": "skill_pack"`, `pack_node_id = f"pack:{pack_id}"`) with `"contains"` edges to its member skills, added to `result_graph["pack_nodes"]`/`["pack_edges"]` alongside (but separate from) the main capability graph.

This does not literally author a new tool/capability (every `member_id` references a pre-existing skill id already in the graph, and the pack node lives on a separate `pack_nodes`/`pack_edges` key, not folded into the routing graph's `edges`), so "capability" in the narrowest sense (new executable skill) still holds. But it is more than edge-weight evolution: it synthesizes and persists a new, LLM-narrated composite artifact. The fallback narrative generator even uses "能力" (capability) to describe the constituent skills: `service.py:490` `f"基于 {len(order)} 个能力协作完成的任务（{' → '.join(order)}）"` — gloss: "A task accomplished through the collaboration of {N} capabilities ({chain})" — confirming the packs are compositions of existing capabilities, not new ones, but they are still a new authored unit (a recipe/grouping) that the pure-edge-weight framing omits.

---

### C3. `models.py` schema versions, event names, outcomes, relation, failure-attribution modes
**Verdict:** VERIFIED
**Evidence:** `jiuwenswarm/symphony/evolution/models.py:7-23`:
```
OVERLAY_SCHEMA_VERSION = "symphony.dynamic_overlay.v3"
EVENT_SCHEMA_VERSION = "symphony.evolution_event.v2"
PLAN_CREATED = "plan.created"
PLAN_OUTCOME = "plan.outcome"
OUTCOME_SUCCESS = "success"
OUTCOME_FAILURE = "failure"
OUTCOME_NO_PLAN = "no_plan"
OUTCOME_NEEDS_INPUT = "needs_input"
CAN_FEED = "can_feed"
ATTRIBUTION_ALL_EDGES = "all_edges"
ATTRIBUTION_TERMINAL_EDGE = "terminal_edge"
ATTRIBUTION_EXPLICIT = "explicit"
ATTRIBUTION_SUCCESS_ONLY = "success_only"
```
Every name and value in the claim matches exactly, including that `can_feed` is the sole relation constant defined in the file.

---

### C4. `add_skills|update_skills|delete_skills` — only one call, in a test file, no production caller
**Verdict:** VERIFIED
**Evidence:** `grep -rn -E "add_skills|update_skills|delete_skills" --include="*.py" .` from the jiuwenswarm root returns exactly one match to the batch graph API: `tests/unit_tests/symphony/test_fingerprint_adapter.py:281`:
```python
result = await runtime.graph_engine.add_skills(
    ["translator"],
    request_id="consumer-full-build-add",
    source_revision=target_artifact.source_snapshot.snapshot_id,
)
```
(There is also `_update_skills_state_for_builtin` in `jiuwenswarm/common/utils.py:560,804,862` — an unrelated function about installing/state-tracking builtin skill directories, not the Symphony graph-mutation API; it does not match `update_skills` as a whole word or as the Symphony method.)

Further checks run before confirming the negative:
- `grep -rn "graph_engine" --include="*.py" .` repo-wide → only the two lines in that same test file (`:281`, `:286`). No other file references `graph_engine` at all.
- Grepped `jiuwenswarm/symphony/adapter.py`, `build.py`, `service.py` for any wrapping call (`add_skill`, `remove_skill`, `.skills(`, `getattr(...skills...)`) — none found. `grep -noE "runtime\.[a-zA-Z_]+|identity_runtime\.[a-zA-Z_]+" build.py service.py` shows production code only ever touches `.orchestration` and (via an unrelated import path, not an attribute access) `.skill` module import — never `.graph_engine`.
- The actual `add_skills`/`update_skills`/`delete_skills` methods are defined outside jiuwenswarm entirely, in the separate `agent-core` repo: `openjiuwen/symphony/graph_engine.py:45,61,77` and `openjiuwen/symphony/interfaces/graph.py:17,28,39`. jiuwenswarm only consumes `SymphonyRuntime` from `openjiuwen.symphony` (imported in `jiuwenswarm/symphony/build.py`, `service.py`, and the test file) — the batch mutation surface is external, and jiuwenswarm's own codebase never calls it outside the one test.

---

### C5. `skill-creator-normal/` contents: SKILL.md ~619 lines, 3 sub-agents, listed scripts, HTML eval viewer
**Verdict:** VERIFIED
**Evidence:** `wc -l jiuwenswarm/resources/agent/workspace/skills/skill-creator-normal/SKILL.md` → **619** (exact match).
`find .../skill-creator-normal -type f`:
- `agents/analyzer.md`, `agents/comparator.md`, `agents/grader.md` — all three present.
- `scripts/run_eval.py`, `scripts/run_loop.py`, `scripts/aggregate_benchmark.py`, `scripts/quick_validate.py`, `scripts/package_skill.py`, `scripts/improve_description.py` — all present (plus `scripts/generate_report.py`, `scripts/utils.py`, `scripts/__init__.py`, not named in the claim).
- HTML eval viewer: `eval-viewer/viewer.html` and `assets/eval_review.html` both present, plus `eval-viewer/generate_review.py`.

---

### C6. Test cases are optional and the user decides
**Verdict:** VERIFIED
**Evidence:** `SKILL.md:55`:
> "4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide."

Exact match to the claim's paraphrase.

---

### C7. grader.md: "A passing grade on a weak assertion is worse than useless — it creates false confidence."
**Verdict:** VERIFIED
**Evidence:** `agents/grader.md:9`:
> "You have two jobs: grade the outputs, and critique the evals themselves. A passing grade on a weak assertion is worse than useless — it creates false confidence. When you notice an assertion that's trivially satisfied, or an important outcome that no assertion checks, say so."

Exact quote match.

---

### C8. Consequence: one-session authoring loop, no held-out split, no author/grader separation, loop ends on user satisfaction not threshold
**Verdict:** PARTLY
**Evidence:**
- **User-satisfaction termination — confirmed.** `SKILL.md:20`: "Repeat until you're satisfied." And the explicit iteration-loop stop condition at `SKILL.md:432-437`: "Keep going until: The user says they're happy / The feedback is all empty (everything looks good) / You're not making meaningful progress." No numeric threshold anywhere in this loop.
- **No separation of test-author from implementer — confirmed for the main functional loop.** `SKILL.md:262-264`: "After writing the skill draft, come up with 2-3 realistic test prompts... Save test cases to `evals/evals.json`." `SKILL.md:300-304` (Step 2): "While runs are in progress, draft assertions... Draft quantitative assertions for each test case." The same session that writes the skill draft also writes the prompts and the assertions; grading is done by a `grader` sub-agent spawned within that same session/workspace, not an independently authored, pre-registered eval.
- **"No held-out split" — imprecise.** The SKILL.md *does* describe a genuine train/held-out-test split, but for a different sub-process: description/trigger optimization, not functional correctness grading. `SKILL.md:521`: "It splits the eval set into 60% train and 40% held-out test, evaluates the current description..., then calls Claude to propose improvements based on what failed. It re-evaluates each new description on both train and test, iterating up to 5 times... selected by test score rather than train score to avoid overfitting." This is `scripts/improve_description.py`'s optimization loop for the skill's triggering description, not for whether the skill's outputs are correct — so C8's "no held-out split" is true of the quality-grading loop but not true of the description-optimization loop that the same document documents in detail.
- There is also a "Blind comparison" advanced mode (`SKILL.md:444-446`, `agents/comparator.md:1-7`) where "you give two outputs to an independent agent without telling it which is which" — but this blinds the *grading agent* to which skill *version* produced an output for A/B comparison purposes; it does not blind the grader to the test cases/assertions, nor separate the test-author from the implementer — the same user/session still designed both skill versions and the test prompts, and `agents/analyzer.md:7` explicitly "unblinds" the results afterward. This nuance doesn't overturn the main "no separation" claim, but it means "no held-out split" as a blanket statement over the whole document is not accurate.

**Judgment:** the claim's characterization is correct for the core skill-quality loop (grading is one-session, satisfaction-driven, no independent test authorship), but overstates uniformity — the same SKILL.md separately documents a genuine held-out train/test split used for a different purpose (description triggering), which a reader of C8 as written would not expect to exist.

---

### C9. `agent-core/openjiuwen/harness/skills/library_state.py` — skills_state.json, no versions/lifecycle/retirement, fails open
**Verdict:** VERIFIED
**Evidence:** (File confirmed to live in `agent-core`, not `jiuwenswarm`, as the claim itself notes.) `library_state.py:6-13`:
> "A Skill library keeps a library-wide kill switch in ``skills_state.json``, written next to the Skills themselves by the install / marketplace flow::
>
>     {
>       "skill_configs": {
>         "gamma": {"enabled": false}
>       }
>     }"

Matches the claimed shape `{"skill_configs": {"<name>": {"enabled": false}}}` exactly.

Fail-open behavior, explicit in both docstring and code — `library_state.py:21-23`:
> "The format is read defensively on purpose. A missing, unreadable or malformed state file means 'nothing is switched off', because a corrupted file must not silently blank out an agent's whole Skill view."

And in code, `library_state.py:50-60`:
```python
state_path = Path(skills_dir) / SKILLS_STATE_FILENAME
if not state_path.is_file():
    continue
try:
    data = json.loads(state_path.read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError, UnicodeDecodeError):
    logger.warning(...)
    continue
```
Missing file → `continue` (skipped, nothing added to `disabled`). Unreadable/malformed → caught exception → logged warning → `continue`. Either way the function returns fewer/no disabled names, i.e. more skills stay enabled — fails open. The entire module (76 lines) has exactly one concept, `enabled: false`; no version field, lifecycle-state field, or retirement-reason field appears anywhere in the file.

---

### C10. `jiuwenswarm/resources/agent/workspace/skills/` ~33 built-in skills, including the 7 named authoring skills
**Verdict:** VERIFIED
**Evidence:** `ls -1 jiuwenswarm/resources/agent/workspace/skills/ | wc -l` → **34** directories (claim says "about 33" — off by one, within the stated approximation). All 34 entries are directories and all 34 contain a `SKILL.md` (verified with a loop checking for `SKILL.md` in each; no missing).

Full list: `advanced-daily-report, agent-creator, agent-group-creator, akg-agents, ascend-moe-optimizer-auto-trace, ascend-moe-optimizer-trace-analyzer, baoyu-image-gen, cross-channel-history-retrieval, deepep-to-cam-converter, delayed-restart-app, doc-update, docx-pro, dynamic-memory-cli, financial-document-parser, gitcode-api, harmonyos-dev-suite, huawei-cloud-maas-setup, llm-wiki, local-doc-ocr, openJiuwen-DeepSearch, pdf-extraction, plugin-creator, ppt-creation, pptx-generator, project-maintainer, rsi-program-dataset-creator, skill-creator, skill-creator-normal, skill-gen-4-enterprise-doc, skill-omni-creation, skvm-general, skvm-jit, swarmskill-creator, xlsx`.

All 7 named authoring skills present: `skill-creator`, `skill-creator-normal`, `skill-omni-creation`, `swarmskill-creator`, `agent-creator`, `plugin-creator`, `rsi-program-dataset-creator`. Note: `agent-group-creator` is an additional authoring-adjacent skill (creates groups of agents) not mentioned in the claim's list — see "What else I noticed."

---

### C11. `skillhub` = "openJiuwen Agentic Hub"; marketplace supports publish + versioning; optional ClawHub-compatible API
**Verdict:** VERIFIED
**Evidence:** `skillhub/README.md:1,9,11,26`:
> "# openJiuwen Agentic Hub"
> "**openJiuwen Agentic Hub** is an open-source **Skill hosting and distribution** implementation in the openJiuwen ecosystem, intended for self-hosted team deployments."
> "**ClawHub compatibility** can be enabled so existing ClawHub-oriented CLIs and tools can integrate..."
> "**Marketplace service**: publish and version Skills, list/detail, presigned downloads; optional **ClawHub-compatible** API surface."

Chinese counterpart, `skillhub/README_zh.md:9,23`:
> "**openJiuwen Agentic Hub**（本仓库）是 openJiuwen 生态中的 **Skill 托管与分发** 开源实现，供团队在自有环境中部署使用。" — gloss: "openJiuwen Agentic Hub (this repository) is an open-source Skill hosting and distribution implementation within the openJiuwen ecosystem, for teams to deploy within their own environment."
> "**市场服务（marketplace）**：Skill 发布与版本治理、列表与详情、预签名下载；可按需启用 **ClawHub 兼容协议**，便于对接既有 CLI 与生态工具。" — gloss: "Marketplace service: Skill publishing and version governance, list/detail views, presigned downloads; the ClawHub-compatible protocol can be enabled as needed, to interoperate with existing CLI and ecosystem tools."

---

### C12. `priority_registry.py` defines SKILL_CREATION_GUIDANCE / NUDGE / TEAM_* priorities
**Verdict:** VERIFIED
**Evidence:** `jiuwenswarm/agents/harness/common/prompt/priority_registry.py:73-76`:
```python
SKILL_CREATION_GUIDANCE = 106
SKILL_CREATION_NUDGE = 107
TEAM_SKILL_CREATION_GUIDANCE = 108
TEAM_SKILL_CREATION_NUDGE = 109
```
and lines 113-116 map the corresponding lowercase string keys to these enum members. All four names present exactly as claimed, confirming skill-creation is steered by prompt-priority guidance/nudge entries rather than a separate platform gate (consistent with — though not by itself proof of — the claim's broader framing that skill creation in jiuwenswarm is agent-prompting-driven).

---

## What else I noticed

- **Evolution is off by default.** `jiuwenswarm/symphony/config.py:23-24`: `DEFAULT_SYMPHONY_ENABLED = False`, `DEFAULT_EVOLUTION_ENABLED = False`. Anyone designing on top of the evolution/overlay system (C2, C3) should know none of it runs unless explicitly turned on in config — the entire dynamic-overlay/edge-weight/skill-pack machinery is dormant by default.
- **The skill-pack distillation pathway (C2) depends on a cross-repo import that can silently no-op.** `service.py:369-377` wraps `from openjiuwen.symphony.flow.distill import ...` in `try/except ImportError: return []`. That module lives only in the separate `agent-core` repo (`openjiuwen/symphony/flow/distill.py`, alongside `codegen.py`, `packager.py`, `review.py` — names suggestive of more automated skill-authoring machinery than jiuwenswarm's own `evolution/` module contains). If `agent-core` isn't installed as a dependency where jiuwenswarm runs, this whole pathway is inert and C2's simple "only evolves edge weights" description becomes accurate in practice — but that's an environment/packaging fact, not something guaranteed by the jiuwenswarm code itself.
- **The Symphony batch-mutation API (C4) is entirely external.** `add_skills`/`update_skills`/`delete_skills` are defined in `agent-core/openjiuwen/symphony/graph_engine.py:45,61,77` and `.../interfaces/graph.py:17,28,39`, not in jiuwenswarm. jiuwenswarm imports `SymphonyRuntime` from `openjiuwen.symphony` as a dependency and never calls the mutation methods except in one test — meaning production skill-graph mutation (if it happens at all) happens entirely inside agent-core or its callers, which this task did not scope in.
- **`library_state.py` (C9) is read-only from jiuwenswarm's perspective** — jiuwenswarm never reads/writes `skills_state.json` directly in the files inspected; the consuming logic lives in `agent-core`'s harness rails. Worth flagging if someone assumes jiuwenswarm owns skill enable/disable state — it doesn't; agent-core does.
- **`skill-creator-normal/SKILL.md` explicitly warns about a Windows/npx bug** (line 88): "On Windows, running `npx skills find` *without* the `powershell -Command "..."` wrapper will silently produce empty output — this is a Windows/npx compatibility bug, not a sign that no skills exist." Given this session runs on Windows, this is directly relevant if anyone exercises that skill's reference-discovery step here.
- **`agent-group-creator`** exists alongside the seven authoring skills named in C10 and was not mentioned in the claim — another skill-creation-adjacent tool in the same directory.

---

## Tally

VERIFIED: 9 (C1, C3, C4, C5, C6, C7, C9, C11, C12)
PARTLY: 2 (C2, C8)
REFUTED: 0
IMPRECISE: 0
CANNOT-CHECK: 0
