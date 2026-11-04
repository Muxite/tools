# Verification report: openjiuwen/symphony/flow/ and orchestration/config.py

Repository: `C:\Users\m50066326\huawei\openjiuwen\agent-core`

HEAD commit (checked first, per protocol):
```
$ git -C C:\Users\m50066326\huawei\openjiuwen\agent-core log -1 --format='%H %ad' --date=short
f1d7fd6923a6fadda52621385450ff8fdff0ea3f 2026-09-15
```

---

### C1. `flow/` has 11 `.py` files, ~2,734 lines, implements a capability-creation pipeline
**Verdict:** VERIFIED
**Evidence:** Counted with `wc -l *.py` in `openjiuwen/symphony/flow/`:
```
    79 __init__.py
   128 codegen.py
   447 distill.py
   537 engine.py
   290 models.py
   164 narrative.py
   188 packager.py
    76 privacy.py
   108 render.py
   342 review.py
   375 store.py
  2734 total
```
11 files, exactly 2,734 lines. Pipeline shape confirmed by module docstrings, e.g.
`flow/engine.py:56` — `"""经验沉淀与能力包安装准备；不执行用户任务，也不做本地安装。"""`
(gloss: "Experience distillation and capability-package install-preparation; it does not execute user tasks, nor does it perform local installation.") — evidence ingestion → recipe distillation → packaging → static/LLM review → skill rendering.

### C2. `models.py` schema version constants
**Verdict:** VERIFIED
**Evidence:** `flow/models.py:11-13`
```
RECIPE_SCHEMA_VERSION = "symphony.experience_recipe.v1"
PACKAGE_SCHEMA_VERSION = "symphony.capability_package.v1"
REVIEW_SCHEMA_VERSION = "symphony.package_review.v1"
```
Exact match.

### C3. `models.py` status/grade/verdict enums
**Verdict:** VERIFIED
**Evidence:** `flow/models.py:15-22` (`RECIPE_STATUS_DRAFT/ACTIVE/DEPRECATED` = `"draft"/"active"/"deprecated"`), `:24-26` (`RECIPE_GRADE_CANDIDATE/VERIFIED` = `"candidate"/"verified"`), `:37-40` (`VERDICT_APPROVED/REJECTED/NEEDS_HUMAN_REVIEW` = `"approved"/"rejected"/"needs_human_review"`). All three value sets match exactly.

### C4. `ExperienceRecipe` dataclass fields
**Verdict:** VERIFIED
**Evidence:** `flow/models.py:117-130`
```python
@dataclass
class ExperienceRecipe:
    recipe_id: str
    version: int
    status: str
    grade: str
    applicability: dict[str, Any]
    combination_structure: dict[str, Any]
    execution_narrative: str
    quality: dict[str, Any]
    provenance: dict[str, Any]
    schema_version: str = RECIPE_SCHEMA_VERSION
```
Field list and `version: int` typing match exactly.

### C5. `review_static()` runs exactly ten named static checks; none executes the candidate
**Verdict:** VERIFIED
**Evidence:** `flow/review.py:142-151` calls, in order: `_check_structure`, `_check_dependencies`, `_check_code_safety`, `_check_secrets`, `_check_artifact_paths`, `_check_integrity`, `_check_meta_naming`, `_check_materials`, `_check_permissions`, `_check_license` — exactly the ten named, no more, no fewer.

I read every check body (`review.py:177-323`):
- `_check_structure`/`_check_dependencies`/`_check_materials`/`_check_permissions`/`_check_license`: pure dict/string inspection (`package.get(...)`, membership tests).
- `_check_code_safety` (`:217-230`): calls `validate_generated_script(script)` (`codegen.py:104-128`), which does `ast.parse(source)` then `ast.walk(tree)` checking `ImportFrom`/`Import`/`Call` node types against a whitelist — pure static AST analysis, no `exec`/`eval`/`compile(...,"exec")`/subprocess.
- `_check_secrets` (`:233-241`): compares `redact_private_json(package) != package` — pure text/regex redaction (`privacy.py`), no execution.
- `_check_artifact_paths` (`:244-254`): string `".."` containment check on a path.
- `_check_integrity` (`:257-265`): calls `CapabilityPackager.verify_package_integrity`, which recomputes a sha256 over `materials` and string-compares to `package["integrity"]` (`packager.py:78-84`) — pure hashing.
- `_check_meta_naming` (`:268-277`): regex match via `validate_meta_name` (`codegen.py:100-101`).

None of the ten checks imports `subprocess`, calls `exec`/`eval`, spawns a process, or invokes the generated `swarmflow/run.py` script. A repo-wide grep of `flow/` for `subprocess|Popen|exec\(|eval\(|compile\(|importlib|sandbox|shell=True|os\.system|__import__` returned zero real hits (only `_FORBIDDEN_CODE_TOKENS = (..., "subprocess", "eval(", "exec(")` in `review.py:31`, which is itself a static *blacklist* the code-safety check searches for inside candidate scripts — it never calls these itself). The claimed consequence holds.

### C6. `review()` short-circuits on non-approved static result; three `needs_human_review` paths
**Verdict:** VERIFIED
**Evidence:** `flow/review.py:96-131`.
Short-circuit: `:102-104` — `result = self.review_static(...); if result.verdict != VERDICT_APPROVED: return result`.
(a) No agent configured: `:105-115` — `if self._review_agent is None: result.verdict = VERDICT_NEEDS_HUMAN_REVIEW`.
(b) Agent raises: `:116-119` — `try: verdict = await self._review_agent.review(...) except Exception: verdict = VERDICT_NEEDS_HUMAN_REVIEW`.
(c) Agent returns an unrecognised verdict: `:120-121` — `if verdict not in {VERDICT_APPROVED, VERDICT_REJECTED, VERDICT_NEEDS_HUMAN_REVIEW}: verdict = VERDICT_NEEDS_HUMAN_REVIEW`.
All three distinct paths confirmed exactly as described.

### C7. LLM reviewer can only downgrade a statically-approved package, never rescue a failed one
**Verdict:** VERIFIED
**Evidence:** Because of the early return at `review.py:103-104`, the review agent (`self._review_agent.review(...)`, line 117) is only ever invoked when `review_static()` already returned `VERDICT_APPROVED`. When static review fails (`rejected` or the single-failure `needs_human_review` case — see review_static's verdict logic at `:153-162`), `review()` returns immediately and the agent is never consulted, so it cannot change that outcome. When static review passes, the agent can only leave the verdict `approved` or move it to `rejected`/`needs_human_review` (`:120-129`) — never back to a rescued `approved` from a static failure, because that branch is unreachable in that case. Code fully supports the claim.

### C8. `resolve_status_grade` promotes to (active, verified)
**Verdict:** VERIFIED
**Evidence:** `flow/distill.py:377-390`
```python
def resolve_status_grade(...):
    success_count = int(quality.get("success_count") or 0)
    pack_success_rate = float(quality.get("pack_success_rate") or 0.0)
    if success_count >= min_successes_verified and pack_success_rate >= min_pack_success_rate_verified:
        return RECIPE_STATUS_ACTIVE, RECIPE_GRADE_VERIFIED
    ...
```
Exact match to the claimed condition (AND of both thresholds).

### C9. `orchestration/config.py` defaults
**Verdict:** VERIFIED
**Evidence:** `openjiuwen/symphony/orchestration/config.py:7-12`
```python
DEFAULT_FLOW_ENABLED = True
DEFAULT_FLOW_MIN_EDGE_SUPPORT = 1
DEFAULT_FLOW_MIN_EDGE_SUCCESS_RATE = 0.8
DEFAULT_FLOW_MIN_SUCCESSES_CANDIDATE = 1
DEFAULT_FLOW_MIN_SUCCESSES_VERIFIED = 1
DEFAULT_FLOW_MIN_PACK_SUCCESS_RATE_VERIFIED = 0.8
```
All six values match exactly (there is also `DEFAULT_FLOW_MAX_NARRATIVE_EXAMPLES = 5`, not part of the claim, which is fine).

### C10. With shipped defaults, one successful execution is enough to promote a recipe to `verified`
**Verdict:** VERIFIED (traced end to end; one real caveat noted below, which the claim's own wording already accommodates)
**Evidence / trace:**
1. `SymphonyFlowConfig` (`orchestration/config.py:42-52`) defaults every threshold field to the `DEFAULT_FLOW_*` constants from C9, and `SymphonyFlowEngine.__init__` (`engine.py:69`) does `self.config = config or SymphonyFlowConfig()` — so unless a caller explicitly passes a `config`, these are the live values.
2. `engine.ingest()` (`:84-92`) requires top-level `payload["outcome"] == "success"` and a valid graph; `store.append_evidence` is idempotent per `trace_id`.
3. `engine.distill()` (`:215-257`) reads all `outcome == "success"` records, then:
   - `qualified_edges(records, min_edge_support=config.min_edge_support, min_edge_success_rate=config.min_edge_success_rate)` (`:225-229`) computes per-edge `support`/`success_rate` over *all* evidence (`distill.py:217-227`) and keeps edges meeting both thresholds.
   - For a single execution whose graph has one edge marked `metadata.success = True`, that edge gets `support = 1`, `success_rate = 1.0`. With defaults `min_edge_support=1` and `min_edge_success_rate=0.8`, this edge is immediately "qualified" — the very first observation already clears the bar.
   - `group_by_structure` (`distill.py:191-214`) puts this lone trace into a new structure group keyed on its own qualified edge(s).
   - `distill_group` → `compute_quality` (`distill.py:356-374`): `execution_count = 1`, `success_count = 1`, `pack_success_rate = 1/1 = 1.0`.
   - `resolve_status_grade(quality, min_successes_verified=1, min_pack_success_rate_verified=0.8)`: `1 >= 1` and `1.0 >= 0.8` → `(RECIPE_STATUS_ACTIVE, RECIPE_GRADE_VERIFIED)`.
4. This recipe is then saved via `_save_recipe_versioned` and immediately satisfies `get_candidate`'s exposure condition `recipe.status == "active" and recipe.grade == "verified"` (`engine.py:457`), i.e. it is offered onward as a `CombinationCandidate`.

So the claim holds: **one execution graph, containing at least one successful capability-to-capability edge, is sufficient** under shipped defaults to reach `(active, verified)` in the very same `distill()` pass that ingests it.

**Caveats the claim's literal wording should carry (not refutations, but scope notes):**
- A "successful execution" here must produce a graph with **at least one edge** between two capability nodes with `metadata.success = True`. A single-capability, no-edge execution never enters `group_by_structure` (`distill.py:206`, `if not key_edges: continue`) and produces no recipe at all — the flow subsystem is inherently about *combinations*, so this is consistent with, not a violation of, the claim's intent.
- `min_edge_support`/`min_edge_success_rate` are real gates, but at `n=1` with the shipped defaults (`1` and `0.8`) they are trivially satisfied by any single successful edge observation — they do not add a practical barrier at this default configuration.
- Reaching grade `verified` is **not** the same as the capability being installed/published. `CapabilityPackager.build_package` requires `status == active` and `grade == verified` (`packager.py:38-45`) to even attempt packaging, and actual publication still requires an explicit `review_and_prepare_install()` call that runs the full ten-check `PackageReviewGate` (C5/C6) plus optional LLM review before `_publish_approved_package` runs. The claim is specifically about grade promotion, not installation, so this doesn't refute it — but it is an important adjacent fact (see "what else I noticed").
- **Are these the defaults actually used at runtime?** Within `agent-core` itself: yes, for any caller that doesn't override `config`. `SymphonyFlowEngine` is only ever constructed with a non-default config inside `tests/unit_tests/symphony/test_capability_flow.py`. Production code in this repo (`openjiuwen/symphony/runtime.py:58,73`) takes an already-constructed `flow_engine: SymphonyFlowEngine | None` as a dependency-injected parameter — the repo itself never builds one with a custom `SymphonyFlowConfig` for production use. Whether some *external* host application overrides these thresholds before handing in the engine is outside what this repository's code can show — flagged as a scope limit, not a refutation.

### C11. `engine.py` pipeline surface
**Verdict:** VERIFIED
**Evidence:**
- `ingest()` — `engine.py:84-92`, appends evidence via `self.store.append_evidence(evidence)`.
- `distill()` — `engine.py:215-257`, produces `ExperienceRecipe`s.
- `_save_recipe_versioned()` — `engine.py:293-304`, called from inside `distill()`'s loop (`:251`), persists via `self.store.save_recipe(recipe)` with version files (`store.py:137-147`, `v{version}.json`).
- `review_and_prepare_install()` — `engine.py:308-387`, calls `self.gate.review(package, artifact_dir=artifact_dir)` (`:357`).
- `_publish_approved_package()` — `engine.py:404-441`, called from `review_and_prepare_install` (`:370`) on approval; renders and atomically replaces the artifact directory.
- `review_history(package_id)` — `engine.py:481-484`:
```python
def review_history(self, package_id: str) -> list[ReviewResult]:
    """评审结果按包存储；v1 返回最近一次（幂等输入 → 幂等评审）。"""
    return [ReviewResult.from_dict(value) for value in self.store.read_reviews(package_id)]
```
returns past `ReviewResult`s as claimed. (Note: its own docstring says v1 returns only the most recent one, but `store.read_reviews` — `store.py:245-261` — actually globs and returns *every* `reviews/<package_id>/*.json` file; see "what else I noticed".)

### C12. `applicability` is LLM-distilled with template fallback, not structured/machine-checkable
**Verdict:** VERIFIED
**Evidence:** `flow/narrative.py:1` — `"""叙事蒸馏：任务描述与执行过程文本（LLM 优先，模板降级）。"""` (gloss: "Narrative distillation: task description and execution-process text (LLM-first, template fallback)."). `distill_texts()` (`:50-79`): if `llm_client is not None`, tries `_distill_with_llm` and on **any** exception (`except Exception: pass`, `:77-78`) falls through to `_template_texts`. Both paths return `{"applicability": {"task_description": ..., "trigger_conditions": ..., "example_requests": [...]}, "execution_narrative": ..., "narrative_source": "llm"|"template"}` (`:130-141`, `:156-164`). `applicability["task_description"]` and `["trigger_conditions"]` are free-form strings (LLM JSON output, `sanitize_distilled_text`-ed) or, in the template path, hand-built Chinese sentence templates (`:151-152`) — not a structured/machine-checkable condition object.

### C13. Nothing in `flow/` executes the candidate capability
**Verdict:** VERIFIED (negative claim — searched hard, see below)
**Evidence:**
- Explicit design statement: `engine.py:56` — `"""经验沉淀与能力包安装准备；不执行用户任务，也不做本地安装。"""` ("...does not execute user tasks, nor does it perform local installation.")
- Ran `grep -n -iE "subprocess|Popen|exec\(|eval\(|compile\(|importlib|sandbox|shell=True|os\.system|__import__|sys\.exec|sandboxed|dry.?run|trial" *.py` across all 11 files in `flow/`. The only hits were: regex patterns in `privacy.py` (credential detection, unrelated), `review.py:31`'s `_FORBIDDEN_CODE_TOKENS` tuple (a blacklist the static code-safety check searches *for* inside the candidate script text — it never itself calls these), and unrelated regex/id-pattern definitions in `store.py`/`codegen.py`.
- Manually read all 11 files end to end (`models.py`, `codegen.py`, `distill.py`, `engine.py`, `narrative.py`, `packager.py`, `privacy.py`, `render.py`, `review.py`, `store.py`, `__init__.py`). The generated "execution" code (`codegen.generate_swarmflow_script`) is built purely as a **string template** (`codegen.py:82-96`, list of `.append()` lines joined at the end) — it is written to a file by `render.py`'s `SkillAdapter.render` (`render.py:39-40`, `run_path.write_text(run_py, ...)`), never `exec`'d or imported.
- `codegen.validate_generated_script` (`codegen.py:104-128`) only does `ast.parse` + `ast.walk` — parsing, not executing.
- `packager.CapabilityPackager.verify_package_integrity` only recomputes and compares a sha256 hash (`packager.py:78-84`).
- The only "invoke" calls anywhere in `flow/` are `self._llm.invoke(...)` in `review.py:71` (`LLMPackageReviewAgent`) and `llm_client.invoke(...)`/`complete_json_async(...)` in `narrative.py:100,108` — both are calls to an LLM for text generation/judgment, not execution of the candidate capability itself.
- Admission genuinely rests on (a) the ten static `review_static()` checks (C5) plus optional LLM judgment over redacted package contents, and (b) success statistics accumulated purely from evidence the *host application* reports back via `ingest()`/`submit()` from its own production runs — `flow/` itself never runs the capability to generate that evidence.

---

## What else I noticed

- **`review_history` docstring vs. behaviour mismatch.** `engine.py:482` says `"""评审结果按包存储；v1 返回最近一次（幂等输入 → 幂等评审）。"""` ("...v1 returns the most recent one"), but the implementation (`store.py:245-261`, `read_reviews`) globs and returns **every** `reviews/<package_id>/*.json` file that exists, sorted by filename — not just the latest. Since each review's filename is a content hash of its verdict+checks (`review.py:334-342`), identical re-reviews collapse to the same file (making it *look* idempotent), but a package reviewed twice with a different outcome (e.g. LLM agent added/changed between calls) would leave multiple files and `review_history` would return all of them, contradicting the docstring's "returns only the most recent" claim. This wasn't one of the claims under test but is a real, verifiable inconsistency in this subsystem.

- **`verified` grade ≠ installed.** As noted under C10, reaching `(active, verified)` only makes a recipe *packageable* (`packager.py:38-45` gates on exactly these two fields) and offerable as a `CombinationCandidate` — it still has to pass the full ten-check static gate plus optional LLM review via an explicit `review_and_prepare_install()` call before anything is published to disk. Anyone reasoning about "how fast can a bad capability reach production" from C10 alone should know this second gate exists and is separate.

- **The edge-quality gate (`min_edge_support`, `min_edge_success_rate`) is currently vacuous at n=1.** Because the shipped defaults are `1` and `0.8`, the very first successful edge observation always self-qualifies. These knobs only start doing real work once there is more than one trace over the same edge (e.g. a `support=2` requirement, or contradictory evidence pulling `success_rate` below `0.8`). Someone designing on top of this code should not assume the edge-quality filter provides any protection against a single lucky/adversarial run under default config — it doesn't, by construction.

- **`SymphonyFlowConfig` is entirely caller-supplied.** Nothing in `agent-core` itself wires a non-default `SymphonyFlowConfig` into a `SymphonyFlowEngine` for production use — the only non-default construction sites are unit tests. `flow_engine` is a plain dependency-injection parameter into `SymphonyRuntime` (`openjiuwen/symphony/runtime.py:58`), constructed by whatever code calls it, which is outside this repository. Anyone wanting to know "what thresholds does production actually run with" needs to look at the host application, not this repo.

- **`_FORBIDDEN_CODE_TOKENS` and `_FORBIDDEN_PERMISSIONS` are static blacklists, not sandboxing.** `_check_code_safety` does a case-insensitive substring search for tokens like `"subprocess"`/`"eval("`/`"exec("` in the generated script text (`review.py:31`, `:219-225`), and `_check_permissions` rejects a small fixed set of permission strings (`review.py:33`, `:296-309`) if present in `materials.permissions` — but nothing enforces that the generated `swarmflow/run.py` (built purely from a `from swarmflow import agent` whitelist, `codegen.py:14-15,116-127`) doesn't misbehave once it actually runs under the host's own SwarmFlow runtime later. The safety guarantee here is entirely about the *shape* of the generated script at packaging time, not about anything happening at runtime after install — consistent with, and reinforcing, C13.

## Selected Chinese docstrings and glosses

- `models.py:1` — `"""Symphony flow 数据模型：经验配方、能力包与评审结论。"""`
  Gloss: "Symphony flow data models: experience recipe, capability package, and review verdict."
- `models.py:171` (`content_identity`) — `"""用于变更检测：内容（非计数）发生变化时才产生新版本。"""`
  Gloss: "Used for change detection: a new version is produced only when content (not counts) changes."
- `review.py:1` — `"""PackageReviewGate：确定性静态评审（结构/依赖/安全/完整性）。"""`
  Gloss: "PackageReviewGate: deterministic static review (structure/dependencies/security/integrity)."
- `distill.py:1` — `"""确定性结构蒸馏：从执行证据提取 skill pack 与质量统计。"""`
  Gloss: "Deterministic structural distillation: extract a skill pack and quality statistics from execution evidence."
- `distill.py:142-148` (`StructureGroup`) — `"""按"合格成功边结构"聚类的一组证据。键 = 轨迹【成功边】∩ 全局合格边。失败边不参与分组键（它不是任务实际走通的路径），但参与全局边质量统计。组内每条轨迹都完整走过 pack 的全部边，因此组合级统计（execution_count / success_count / pack_success_rate）的归因天然严格。"""`
  Gloss: "A group of evidence clustered by 'qualified successful-edge structure'. Key = trace's [successful edges] ∩ globally qualified edges. Failed edges don't participate in the grouping key (they're not the path actually taken), but do feed global edge-quality stats. Every trace in a group walks the pack's full edge set, so combination-level statistics are inherently strictly attributed."
- `engine.py:56` (`SymphonyFlowEngine` class) — `"""经验沉淀与能力包安装准备；不执行用户任务，也不做本地安装。"""`
  Gloss: "Experience distillation and capability-package install-preparation; it does not execute user tasks, nor does it perform local installation." (directly bears on C13)
- `engine.py:216-220` (`distill`) — `"""批处理蒸馏：全局边统计 → 结构分组 → 叙事 → 版本化落盘。分组键 = 轨迹【成功边】∩ 全局合格边（失败边只参与边质量统计、不参与分组）；组内每条轨迹都完整走过 pack 全部边，组合级统计归因严格——靠被剔边成功的轨迹不会给新 pack 虚增成功经验。"""`
  Gloss: "Batch distillation: global edge statistics → structural grouping → narrative → versioned persistence. Grouping key = trace's [successful edges] ∩ globally qualified edges (failed edges feed edge-quality stats only, not grouping); every trace in a group walks the pack's full edge set, so combination-level statistics are strictly attributed — a trace that only succeeded via a pruned-out edge can't inflate a new pack's apparent success experience."
- `engine.py:482` (`review_history`) — `"""评审结果按包存储；v1 返回最近一次（幂等输入 → 幂等评审）。"""`
  Gloss: "Review results are stored per package; v1 returns the most recent one (idempotent input → idempotent review)." (see docstring/behaviour mismatch noted above)
- `narrative.py:1` — `"""叙事蒸馏：任务描述与执行过程文本（LLM 优先，模板降级）。"""`
  Gloss: "Narrative distillation: task description and execution-process text (LLM-first, template fallback)." (directly bears on C12)
- `codegen.py:55-58` (`generate_swarmflow_script`) — `"""把 skill pack 机械翻译为 SwarmFlow Python 脚本。仅允许白名单算子 from swarmflow import agent；分支边在 v1 中按拓扑序线性化（多前驱用字符串拼接传递）。"""`
  Gloss: "Mechanically translate the skill pack into a SwarmFlow Python script. Only the whitelisted operator 'from swarmflow import agent' is allowed; in v1, branching edges are linearized by topological order (multiple predecessors passed via string concatenation)."
- `packager.py:1` — `"""CapabilityPackager：把 active+verified recipe 冻结为统一能力包。"""`
  Gloss: "CapabilityPackager: freezes an active+verified recipe into a unified capability package."

---

## Tally

VERIFIED: 13 (C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13)
REFUTED: 0
PARTLY: 0
IMPRECISE: 0
CANNOT-CHECK: 0

All 13 claims verified as stated. C10 (the load-bearing claim) is verified with substantial supporting trace and several scope caveats recorded above; none of the caveats contradict the claim as worded. One genuine subsystem inconsistency was found outside the claim set: `review_history`'s docstring ("v1 returns the most recent one") does not match `FlowStore.read_reviews`'s actual behaviour (returns all stored review files for a package).
