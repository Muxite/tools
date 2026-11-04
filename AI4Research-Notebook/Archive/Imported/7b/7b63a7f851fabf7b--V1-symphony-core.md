# V1 — symphony core verification

**Repository:** `C:\Users\m50066326\huawei\openjiuwen\agent-core`
**Scope:** `openjiuwen/symphony/`
**HEAD commit:** `f1d7fd6923a6fadda52621385450ff8fdff0ea3f 2026-09-15`
(command: `git -C C:\Users\m50066326\huawei\openjiuwen\agent-core log -1 --format='%H %ad' --date=short`)

---

### C1. `EvaluationSuite` docstring says the suite never executes a capability, computes an admission decision, or invents an overall composite score
**Verdict:** VERIFIED
**Evidence:** `openjiuwen/symphony/evaluation/suite.py:83-88`
```
class EvaluationSuite:
    """Run registered metrics over fingerprints and caller-supplied traces.

    The suite never executes a capability, computes an admission decision, or
    invents an overall composite score. Model-heavy metrics are opt-in.
    """
```
The sentence is verbatim. Claim said "approximately lines 85-87"; the sentence actually spans lines 86-87 — close enough under "approximately."

---

### C2. `interfaces/graph.py` `SkillGraphUpdater` Protocol, docstring, and three async methods
**Verdict:** VERIFIED
**Evidence:** `openjiuwen/symphony/interfaces/graph.py:13-48`
```
@runtime_checkable
class SkillGraphUpdater(Protocol):
    """Narrow dependency used after an approved Skill asset change."""

    async def add_skills(self, changed_skill_ids: Sequence[str], *, request_id: str, source_revision: str) -> GraphMutationResult: ...
    async def update_skills(self, changed_skill_ids: Sequence[str], *, request_id: str, source_revision: str) -> GraphMutationResult: ...
    async def delete_skills(self, changed_skill_ids: Sequence[str], *, request_id: str, source_revision: str) -> GraphMutationResult: ...
```
Docstring matches exactly, class starts line 14 (claim said "approximately line 15" — the docstring itself is on line 15). Exactly three methods, each with the signature described, no other methods on the Protocol.

---

### C3. Symphony-wide search for `held.?out|holdout|test_suite|golden|regression|precondition|postcondition` returns zero matches; recount ~201 files
**Verdict:** VERIFIED
**Evidence/commands:**
```
find . -name "*.py" | wc -l                                          # -> 201
grep -rEIni "held.?out|holdout|test_suite|golden|regression|precondition|postcondition" --include="*.py" .   # -> 0 lines
```
File count recounted at 201, matching the claim. The zero-match result was checked against a sanity test (the same regex correctly matches a synthetic string containing all six terms, so the pattern itself is not silently broken).

Per protocol I searched further for synonyms under other names before trusting the zero:
- `pre_condition|post_condition` (underscore variants): 0 matches.
- `benchmark|ground.?truth|gold.?standard|baseline|canary|ablation`: 3 hits, all unrelated (`discovery/toolkit.py` "session baseline" for incremental-index bookkeeping; `orchestration/planning/beam.py` `SEED_BASELINE_SCORE`; a CSS `align-items: baseline` in an HTML-generating visualizer).
- `expected_output|reference_output|known.?good`: **3 hits that are relevant** — `evaluation/evaluators.py:81`, `evaluation/evaluators.py:521`, and `models/evaluation.py:133` define/use `expected_output` on `EvaluationCase`. This is the closest thing in the codebase to a "golden" concept, but it is explicitly caller-supplied evidence (see C8), not a Symphony-owned test suite/holdout set, so it does not contradict the claim — see "What else I noticed."
- `testsuite|test.?case|fixture|gold.?data|sample.?data|reference.?output|ground.?truth`: no relevant hits (2 matches were unrelated `_remote_reference` identifiers).

---

### C4. `admission|admit` returns exactly three matches, all denying that admission is performed
**Verdict:** VERIFIED
**Evidence:** `grep -rEIni "admission|admit" --include="*.py" .` → exactly 3 lines:
- `evaluation/evaluators.py:432` — `reason="Latency was observed without applying a target or admission threshold.",`
- `evaluation/suite.py:86` — `The suite never executes a capability, computes an admission decision, or` (the `EvaluationSuite` docstring, same text as C1)
- `evaluation/suite.py:662` — `reason="Raw observations were aggregated without a target or admission threshold.",`

Count and content match the claim exactly: two "target or admission threshold" statements plus the `EvaluationSuite` docstring, all three denying admission is performed. (Note: technically all three lines are physically inside the `evaluation/` directory, since `suite.py` is itself in `evaluation/`; the claim's phrasing distinguishes the docstring one by content, not by location, so this is not a discrepancy.)

---

### C5. `CapabilityFingerprint.version` defaults to `"1.0.0"` and is excluded from the published artifact serializer
**Verdict:** VERIFIED
**Evidence:** `openjiuwen/symphony/models/fingerprint.py:32` — `version: NonEmptyString = "1.0.0"`; and line 141 —
```python
return tuple(item.model_dump(mode=info.mode, exclude={"version", "static_data"}) for item in value)
```
inside `FingerprintArtifact._serialize_public_fingerprints` (a `@field_serializer("fingerprints")`, docstring: "Keep graph-only compatibility fields out of `fingerprint.json`."). The line number (141) matches the claim exactly. Consequence as claimed: `version` is set on every `CapabilityFingerprint` but stripped before the artifact is serialized to `fingerprint.json`.

---

### C6. `evaluation/evaluators.py` defines exactly nine built-in metrics with the listed `metric_id`s
**Verdict:** VERIFIED
**Evidence:** `grep -n "metric_id" evaluators.py` → exactly 9 lines, in order: `structure_conformance` (147), `description_quality` (212), `classification_consistency` (251), `success_rate` (311), `latency` (395), `accuracy` (441), `completeness` (563), `capability_selection` (624), `composition_effectiveness` (649). This set matches `BUILTIN_EVALUATORS` at `evaluators.py:671-681` exactly (9 evaluator classes; `TraceEvaluator` and `LLMTraceEvaluator` at lines 288/299 are intermediate base classes with no `metric_id` of their own and are not in the tuple).

---

### C7. `EvaluationSuite.register()` is a public extension point for caller-supplied evaluators
**Verdict:** VERIFIED
**Evidence:** `evaluation/suite.py:179-194` — `def register(self, evaluator: Evaluator, *, replace: bool = False) -> EvaluationSuite:`. It is a public (non-underscore) method; the `evaluator` parameter is typed against `evaluation/base.py:139` `class Evaluator(Protocol):`, a structural protocol (checked via `_validated_evaluator_metric_id`, which only requires `metric_id`, `scope in {"static","trace"}`, and a callable `evaluate`) — not restricted to the nine built-ins. `EvaluationSuite.__init__` itself calls `self.register(evaluator)` for each built-in, confirming `register` is the general mechanism, usable by any caller.

---

### C8. Symphony never executes a capability during evaluation; trajectories are caller-supplied `EvaluationCase`/`CapabilityCall` objects
**Verdict:** VERIFIED
**Evidence:** `models/evaluation.py:90` — `class CapabilityCall(SymphonyModel): """One capability invocation observed in an evaluation trace."""`; `models/evaluation.py:125` — `class EvaluationCase(SymphonyModel): """Caller-supplied static or runtime evidence for one capability."""`. Both are plain Pydantic data models (fields like `output`, `success`, `latency_ms`, `expected_output`), not executable. Searched `evaluation/*.py` for any execution mechanism (`subprocess|asyncio.create_subprocess|exec\(|importlib|__import__|\.invoke\(|\.execute\(|\.call\(` and `invoke_capability|execute_capability|run_capability|call_capability|capability\.run\(|capability\.execute\(`) — zero hits in either search.

---

### C9. Capability graph artifact directory: immutable `versions/<version>/graph.json`, atomically-switched `current.json` pointer, failed/cancelled build leaves previous version intact
**Verdict:** VERIFIED
**Evidence:** `orchestration/artifacts.py`:
- `GraphArtifactStore.stage()` (lines 84-123) writes the payload into a fresh `run_dir` via `_write_json_atomic`, then does `os.replace(run_dir, version_dir)` (line 118) — an atomic rename into `versions/<version>/graph.json`; if the version directory already exists it refuses to overwrite (`FileExistsError`, line 102) unless explicitly reusing an identical staged mutation.
- `GraphArtifactStore.activate()`/`_activate_unlocked()` (lines 125-130, 192-202) writes `current.json` via `_write_json_atomic` (temp file + `os.replace`, lines 325-328) — a separate, atomic step from staging.
- `_write_json_atomic` (lines 325-328): `temporary.write_text(...); os.replace(temporary, path)`.
- In `orchestration/service.py:129-189`, `build()` calls `stage()` first, then only calls `activate_if_current()` after `prepare_artifact` succeeds (line 181); if the task is cancelled or raises before that point, `current.json` is never touched, so the previous version stays current and readable. Same pattern in `orchestration/mutation_service.py:326-362` (`_publish_payload`): stage, then `activate_if_current`, with the activation step raising/propagating on any failure and never touching `current.json` first.

---

### C10. Batch graph mutation API: one call = one transaction publishing exactly one immutable version; one call carries only one kind of operation; identity (id) change must be delete+add, not update
**Verdict:** PARTLY
**Evidence:**
- `orchestration/mutation_service.py:68-69` — `class GraphMutationCoordinator: """Validate, build, and atomically publish one batch graph mutation."""`; `mutate()` docstring (line 102): `"""Apply one validated all-or-nothing mutation batch."""`
- One-operation-per-call: `orchestration/mutations.py:26` — `MutationOperation = Literal["add", "update", "delete"]`, and `GraphMutationCoordinator.mutate(self, operation: MutationOperation, changed_skill_ids: Sequence[str], ...)` takes a single operation value applied to the whole batch of ids — VERIFIED, a call cannot mix add/update/delete.
- Identity-change-must-be-delete+add: `mutations.py:473-500`, `_validate_update_membership`: `"""Require updated Skills to exist in both current and target inventory."""` — it raises `not_found` if a requested id is missing from the current graph (line 483-491) and raises `change_set_mismatch` if it is missing from the target inventory (line 492-500). Since capability identity is keyed by `capability_id` (`capability_identity("skill", capability_id)`), an id-changing rename cannot satisfy "present in both current and target" under `operation="update"` — the old id would fail the target-membership check and the new id would fail the current-membership check. The code therefore forces a rename to be modeled as delete (old id) + add (new id). This is enforced behavior, not a stated rule in a comment/docstring, but it does hold. VERIFIED (as a necessary consequence of the code).
- **What fails**: "publishing exactly one immutable graph version" is not true for every call. `mutation_service.py:240-265`, `_noop_result`: when `operation == "update"` and the provider inventory shows no actual content change (`not any(state.changes.values())`), the coordinator returns early with `GraphMutationResult(status="noop", previous_version=state.active.current_version, version=state.active.current_version, ...)` — **no new `versions/<version>/graph.json` is written and `current.json` is not touched**. So a no-op `update_skills()` call is a valid, successful call that does *not* publish a new immutable version; it just confirms the existing one. This contradicts the literal "each call... publishes exactly one immutable graph version."

**Note:** Two of the three sub-claims (single operation kind per call; identity change requires delete+add) are verified. The "each call publishes exactly one immutable version" sub-claim is false for no-op update calls, which return `status="noop"` and the *same* previous version rather than a newly published one.

---

### C11. `CapabilityDescriptor` and `CapabilityIO` field sets, no JSON Schema on either
**Verdict:** VERIFIED
**Evidence:** `models/capability.py`:
```python
class CapabilityIO(SymphonyModel):        # lines 15-40
    name: NonEmptyString
    type: NonEmptyString
    description: str = ""
    required: bool | None = None
    default: JsonValue = None
    metadata: JsonObject = Field(default_factory=dict)

class CapabilityDescriptor(SymphonyModel):  # lines 62-78
    capability_id: NonEmptyString
    capability_type: NonEmptyString
    name: NonEmptyString
    description: str = ""
    source: str = ""
    available: bool = True
    inputs: tuple[CapabilityIO, ...] = ()
    outputs: tuple[CapabilityIO, ...] = ()
    classification: str = ""
    tags: tuple[NonEmptyString, ...] = ()
    content_hash: str = ""
    semantic_content: str = Field(default="", exclude=True, repr=False)
    metadata: JsonObject = Field(default_factory=dict)
```
Both field lists match the claim exactly (13 fields on `CapabilityDescriptor`, 6 on `CapabilityIO`, no extras). The shared base class `SymphonyModel` (`models/_base.py:19-40`) adds no fields, only `ConfigDict` and field validators, so nothing is inherited in. `grep -n "schema" capability.py` returns no matches — confirmed no JSON-Schema field on either model.

---

### C12. `retrieval/` is ~97 files / ~21,000 lines, the largest symphony subsystem, despite README marking capability retrieval 待迁入
**Verdict:** VERIFIED
**Evidence (counts):**
```
find retrieval -name "*.py" | wc -l    -> 97
find retrieval -name "*.py" -exec cat {} + | wc -l  -> 21140
```
Per-subsystem comparison (files/lines): `agent` 2/2336, `discovery` 6/3225, `evaluation` 4/2019, `experience` 12/2949, `flow` 11/2734, `interfaces` 4/131, `models` 8/1003, `observation` 5/1160, `orchestration` 29/8369, **`retrieval` 97/21140**, `shared` 20/5333. Retrieval is over twice the size (by lines) of the next-largest subsystem (`orchestration`).

**README status (Chinese quoted, my gloss):**
`README.md:20-23`:
```
| 能力域 | 当前状态 | 说明 |
| --- | --- | --- |
| 能力指纹 | 已实现 | ... |
| 能力检索 | 待迁入 | 最终提供能力树构建、浏览和自然语言检索。 |
```
Gloss: "能力域" = capability domain, "当前状态" = current status, "能力检索" = "capability retrieval", "待迁入" = literally "awaiting migrate-in" — "pending migration in" / "not yet migrated in" (迁 = migrate/move, 入 = in). The row for capability retrieval is marked 待迁入, matching the claim. The same marker appears again in the directory blueprint at `README.md:126`: `├── retrieval                     # 待迁入`.

---

### C13. Retrieval tree "Skill equivalence groups" (Skill 等价群), deterministic merge, `SkillIndexBuildConfig.equivalence_enabled`, disabled by default
**Verdict:** VERIFIED
**Evidence (README, Chinese quoted, my gloss):** `README.md:94-104`:
```
### 检索树中的 Skill 等价群

显式开启等价群后，检索树构建会先在同一分类分支内召回候选 Skill，再逐对判断核心能力是否相同或相近，并用
确定性合并生成等价群节点。...

该能力由 `SkillIndexBuildConfig.equivalence_enabled`（离线构建对应
`BuildConfig.tree_equiv_grouping_enabled`）控制，默认关闭，需要时显式开启。
```
Gloss: "检索树中的 Skill 等价群" = "Skill equivalence groups in the retrieval tree"; "显式开启等价群后" = "once equivalence groups are explicitly turned on"; "确定性合并生成等价群节点" = "deterministic merge produces equivalence-group nodes"; "该能力由 `SkillIndexBuildConfig.equivalence_enabled`...控制，默认关闭，需要时显式开启" = "this feature is controlled by `SkillIndexBuildConfig.equivalence_enabled`..., off by default, turned on explicitly when needed."

**Code:** `agent/retrieval_toolkit.py:75-91`, `class SkillIndexBuildConfig:` ... `equivalence_enabled: bool = False` (line 91). Confirms the field name, the class, and the default value exactly as the README and the claim state.

---

## What else I noticed

- **`expected_output` is the nearest thing to a "golden" concept, and it's caller-owned.** `models/evaluation.py:133` (`EvaluationCase.expected_output: JsonValue = None`) and `evaluation/evaluators.py:521` (`AccuracyEvaluator` compares `case.output == case.expected_output`) let a caller supply an expected value for a static accuracy check. This is consistent with C8/C3 (Symphony doesn't own a test suite or execute anything — the caller hands it both the observed and the expected value), but a reader relying only on the C3 regex would miss that this concept exists under a different name. Worth flagging for anyone assuming "no golden data anywhere" means "no comparison-to-expected-value logic anywhere."

- **The graph mutation no-op path (see C10) is a real design point**, not just an edge case worth a footnote: `preserve_previous_index_on_failure: bool = True` and `strict_failure: bool = False` also exist as retrieval-side config defaults (`agent/retrieval_toolkit.py:108-109`), echoing the same "don't destroy a working artifact on an ambiguous/failed build" philosophy seen in the graph artifact store (C9).

- **`retrieval/` is not just large, it's already wired into the public package surface**, just not into `SymphonyRuntime`: `openjiuwen/symphony/__init__.py` lazily exports `retrieval` (`_LAZY_MODULES = frozenset({"agent", "discovery", "flow", "retrieval", "shared"})`, line 92, and `from openjiuwen.symphony import retrieval as retrieval`, line 87). So "待迁入" in the README's implementation-status table appears to specifically mean "not yet composed into the unified `SymphonyRuntime` facade," not "the code doesn't exist yet" — the README's own preamble (`README.md:17-18`) makes this distinction explicit ("当前可运行接口" describes what's importable now; the "final Runtime" blueprint's code samples are aspirational). Unlike `experience/`, which has an `experience/API.md` documenting its standalone use, `retrieval/` has no equivalent doc file — it is large, importable, and functional-looking code, but the README does not present it as a supported standalone entry point the way it does `experience`.

- **Evaluators are explicitly LLM-judge-based for several metrics** (`DescriptionQualityEvaluator`, `ClassificationConsistencyEvaluator`, `AccuracyEvaluator`, `CompletenessEvaluator`, `CapabilitySelectionEvaluator`, `CompositionEffectivenessEvaluator` all subclass `LLMJudgeEvaluator`/`LLMTraceEvaluator` per `evaluation/evaluators.py:209-649`), and `EvaluationSuite.__init__` takes `enable_llm: bool = False` — model-heavy metrics are opt-in, matching the "Model-heavy metrics are opt-in" line quoted in C1.

## Tally

VERIFIED: 12
REFUTED: 0
PARTLY: 1 (C10)
IMPRECISE: 0
CANNOT-CHECK: 0
