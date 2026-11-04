# V5 — AI4Research claim verification

Repository: `C:\Users\m50066326\huawei\stellven\AI4Research`
Branch: `openJiuwen-Solar` (confirmed via `git branch --show-current`, up to date with `origin/openJiuwen-Solar`)
HEAD commit: `b0bf165f9ab073aae23e45b3b2796973e5677ee` — "merge: ai4research-main into openJiuwen-Solar", 2026-09-08 16:51:53 -0400
Note: working tree has one pre-existing unstaged modification (`install.ps1`) that was already present when I started; I did not touch it and made no other changes to the repository.

---

### C1. Root README describes request_envelope→requirement_ir→prd/Contracts/task_graph pipeline and itself labels this historical, not current

**Verdict:** VERIFIED

**Evidence:**
`README.md:4-6`:
```
> 当前迁移修复线为 `codex/safety-before-intent-rollback-20260828`，不同于下文历史发布主线。
> 默认 formal 路径是 **Intent Compiler → Requirement Compiler → Elastic Planner → frozen SchedulerInput → Scheduler → Operators/Gates**。
> 下文 PRD/Contracts/task_graph 编译图描述的是历史兼容链，不能用来判断当前 typed 路径。
```
("下文 PRD/Contracts/task_graph 编译图描述的是历史兼容链，不能用来判断当前 typed 路径" = "The PRD/Contracts/task_graph compile graph described below is a historical compatibility chain and cannot be used to judge the current typed path.")

`README.md:54-63` (the pipeline itself, under "核心能力 / 1. Requirement Compiler"):
```
raw request
  └─ request_envelope.json
      └─ requirement_ir.json
          ├─ prd.md
          ├─ Contracts.yaml
          ├─ task_graph.json
          ├─ task_dag.state.json
          └─ closure.json
```
Both halves of the claim are exactly present: the diagram exists further down, and the disclaimer sits near the top (line 6, inside the very first blockquote block).

---

### C2. Current default path GUI/CLI intake → Intent Compiler → Requirement Compiler → Elastic Planner → frozen SchedulerInput → Scheduler → Dispatcher → Operators/Gates, with named entrypoints real

**Verdict:** VERIFIED

**Evidence:** All five files exist with substantial real implementations, not stubs:
- `harness/lib/intent_gateway.py` — 1436 lines, defines `capture()`, `build_requirement_ir()`, `compile_and_evaluate_requirement_bundle()`, `main()` (CLI entrypoint).
- `harness/lib/requirement_compiler/semantic.py` — 292 lines, defines `compile_semantic_requirement_ir()`, `semantic_defects()`.
- `harness/lib/elastic_planner.py` — 8069 lines, defines `compile_and_freeze_execution_bundle()` (see C3) and the whole planning/binding pipeline.
- `harness/lib/scheduler_input.py` — 1073 lines, defines `prepare_runtime_graph()`, `validate()`, `verify_runtime_projection()`.
- `harness/lib/graph_node_dispatcher.py` — 18132 lines, the dispatch/actor-lease/gate runtime.

GUI intake: `harness/status-server/routes/orchestration_routes.py` references `elastic_planner_working`/`elastic_planner_failed` phase state (e.g. lines 993-1027, 2589-2613), i.e. the status-server (GUI backend) reads the same pipeline's phase markers.
CLI intake: `harness/tools/intent_gateway.py`, `harness/tools/pm_dispatch.py`, `harness/tools/codex_pm_router.py` all import/call into `intent_gateway`.

I did not separately verify a file literally named "Scheduler" or "Dispatcher" beyond `graph_node_dispatcher.py`; the scheduling layer also has `harness/lib/graph_scheduler.py` and `harness/lib/dispatch_scheduler.py`, which the claim did not name explicitly, so this is not a discrepancy — just noting the fuller file map.

---

### C3. Elastic Planner performs the freeze itself via `compile_and_freeze_execution_bundle`, producing capsule/physical/evaluation plans + SchedulerInput + frozen run contract; nothing else should call a second authoritative compile

**Verdict:** PARTLY

**Evidence:**
`harness/lib/elastic_planner.py:6888` — `def compile_and_freeze_execution_bundle(requirement_ir, semantic_result, output_dir, *, sprint_id, ...)`, docstring "Turn admitted semantic planning into a physically feasible frozen graph."

Inside it: `capsule_plan` and `physical_plan` are built via `apo_plan_compiler.compile_whole_request_execution_plan` (line 7051), written to `output_dir / "capsule_plan.json"` and `"physical_plan.json"` (lines 7064, 7066); `scheduler_input = compile_scheduler_input(...)` (line 7228), validated against `SCHEDULER_INPUT_SCHEMA`, written to `output_dir / "scheduler_input.json"` (line 7242); and a `frozen` run contract is asserted against `FROZEN_CONTRACT_SCHEMA` (`run-contract-frozen.v2.schema.json`) at line 7346, returned as `"run_contract_frozen": frozen` (line 7426).

`harness/metadata/NEW-MACHINE-START-HERE.md:48` (dated 2026-08-31, same date the claims were written against) independently states:
```
| 执行合同编译 | `elastic_planner.compile_and_freeze_execution_bundle` | accepted semantic plan → capsule/physical/evaluation plans、SchedulerInput、frozen run contract |
```
This matches the claim's description of outputs almost verbatim.

The only in-repo call sites of `compile_and_freeze_execution_bundle` are: `elastic_planner.py:7585` (inside the planner's own wrapper pipeline function, in the same file) and `harness/tests/test_capability_contract_authority.py:419` (a test). No other module in `harness/lib` or `harness/tools` calls it. `apo_plan_compiler.build_physical_plan_ir` (used to build the physical plan) is itself called only from inside `compile_and_freeze_execution_bundle` (`elastic_planner.py:7051`), i.e. it is an internal helper, not a competing compiler.

**Note:** The function name and its outputs (capsule/physical/evaluation plans, SchedulerInput, frozen run contract) are verified. However, I could not find an explicit stated *rule* anywhere ("do not call a second authoritative compile", "single authoritative freeze", etc.) in code comments or docs — I searched for "authoritative compile", "second compile", "single source of freeze", "do not call... freeze", "idempotent freeze" and found no matches outside noise. The rule is only inferable structurally (single call site), not documented as a stated rule. Marking PARTLY because the described mechanism is real and verified, but the "claimed rule" half of the sentence has no textual source I could find — it is an inference from code structure, not a quoted rule.

---

### C4. `harness/config/capability-capsules.registry.yaml` exists and registers 68 capsule manifests

**Verdict:** REFUTED (stale count)

**Evidence:** File exists (`harness/config/capability-capsules.registry.yaml`, 950 lines). Counted registry entries with `grep -c "^  - capability_capsule_id:" harness/config/capability-capsules.registry.yaml` → **80**, cross-checked by `grep -c "manifest_path:"` → also 80, and by section: `grep -n "^  [a-zA-Z_]*:$"` shows three sections — `capability:` (line 4), `guard:` (line 913), `resource:` (line 926) — with `grep -o "capsule_kind: [a-zA-Z_]*" | sort | uniq -c` giving `77 capability + 1 guard + 2 resource = 80`.

Crucially, `harness/metadata/NEW-MACHINE-START-HERE.md:101` — the same document that is dated **2026-08-31** (the exact date the claims were written against, per its own header at line 3: "核对日期：2026-08-31") — says:
```
本次核对：68 个注册 manifest 都在 Git 内。不要扫描目录后自动激活未注册 capsule。
```
("This check: 68 registered manifests are all in Git. Do not scan a directory and then auto-activate an unregistered capsule.")

This is almost certainly the exact source of the "68" figure in the claim. `git log --oneline -- harness/config/capability-capsules.registry.yaml` shows the file was touched by several commits after that date (e.g. `cab32f937 fix(harness): pipeline repairs, reasoning capsules, and credential presence`, `3f534a0a9 fix(harness): persist end-to-end research pipeline repairs`, `e9fbafdf7 feat(planner): expand composable research lifecycle`), consistent with growth from 68 to 80.

**Note:** The claim is a textbook case of staleness flagged in the prompt: correct as of 2026-08-31, wrong as of current HEAD (80, not 68).

**Registry entry fields** (from `RegistryEntry` dataclass, `harness/lib/capability_capsules.py:269-291`, and confirmed by reading raw YAML entries, e.g. `harness/config/capability-capsules.registry.yaml:7-15`):
`capability_capsule_id`, `version`, `capsule_kind` (capability|guard|resource), `status`, `schema_ref`, `manifest_path`, `tags` (list), `owner`, and optional `default_operator_profile`. That's it — the registry entry is a thin pointer/index record; it does not itself carry contract/effects/preconditions data (those live in the manifest file it points to — see C8).

---

### C5. `logical-operators.json` and `physical-operators.json` exist; logical = capability-based routing, physical = role-based dispatch, with a binding router

**Verdict:** VERIFIED

**Evidence:**
- `harness/config/logical-operators.json` exists (52,747 bytes). Entry example (lines 5-18): `"DeepArchitect": {"operator_type": "DeepArchitect", "primary_role": "planner", "required_capabilities": {"architecture_reasoning": 4, "long_context": 3, "multi_agent_coordination": 3}, ...}` — keyed by required capability levels, i.e. capability-based.
- `harness/config/physical-operators.json` exists (192,914 bytes). Entry example (lines 4-27): `"solar-elastic-planner": {"role": "elastic-planner", "roles": ["elastic-planner"], "backend": "command", "command": "python3 \"$HARNESS_DIR/tools/elastic_planner_operator.py\" ...", "task_classes": ["elastic_planning"], ...}` — keyed by role/roles and dispatch command, i.e. role-based.
- Binding router: `harness/lib/apo_plan_compiler.py:1105` `build_physical_plan_for_capsule_node(...)` calls, at line 1127, `enumerate_physical_candidate_decisions(role=..., task_type=..., logical_operator=str(capsule_plan_node.get("logical_operator") or ""), ...)` — this is the function that maps a logical operator/role to a set of physical-operator candidates, i.e. the logical→physical binding router.

---

### C6. Rule: never scan a directory and auto-activate an unregistered capsule; capsules must be registered

**Verdict:** VERIFIED — stated in docs AND enforced in code

**Evidence (documented):** `harness/metadata/NEW-MACHINE-START-HERE.md:101`: "不要扫描目录后自动激活未注册 capsule。" ("Do not scan a directory and then auto-activate an unregistered capsule.")

**Evidence (enforced in code):**
- `harness/lib/plan_validator.py:485-486`: `wc.ERROR_CAPSULE_NOT_REGISTERED, node_id, f"node {node_id} references capsule {capsule_id} which is not in the capsule registry"` — raised when a task-graph node references a capsule id absent from `capsule_registry`.
- `harness/lib/workflow_contract.py:118` defines `ERROR_CAPSULE_NOT_REGISTERED = "CAPSULE_NOT_REGISTERED"`, used at `workflow_contract.py:806-807` with the same "not in the capsule registry" message for workflow stages.
- `harness/lib/apo_plan_compiler.py:633-648`: when `_capsule_manifest(capsule_id, registry_path=registry_path)` returns nothing, the node is marked `"selected": False`, `"unsatisfiable": {"code": "UNSATISFIABLE_CAPSULE", "message": "The declared capability capsule is not registered."}` — i.e. unregistered capsules cannot be selected for execution.
- The capsule loader itself, `harness/lib/capability_capsules.py`, has no `iterdir`/`glob`/`listdir`/`os.walk` calls; `_flatten_registry()` (lines 311-344) only iterates the three fixed sections (`capability`, `guard`, `resource`) of the registry YAML and resolves each `manifest_path` explicitly — there is no directory-scan code path to auto-discover capsules.
- Corroborating find: `harness/config/capability-capsules/` contains 46 `.yaml` files but only 41 of the registry's 80 entries point into that directory (39 point into a separate `harness/capability-capsules/` directory used for research/scientific capsules). Diffing directory contents against registered filenames (`comm -23` on sorted basenames) shows **5 manifest files present on disk but not registered**: `cap.advanced-optimization-reference-worker.yaml`, `cap.chatgpt-browser-agent.yaml`, `cap.gemini-enhanced-search.yaml`, `cap.notebooklm-enrichment.yaml`, `cap.research-report-draft.yaml`. Since the loader is registry-driven (not directory-scanning), these five are inert — good real-world confirmation that the rule holds in practice, not just in the two enforcement points above.

---

### C7. Capability selection is a result of the Planner's binding/composition step, not something a user hand-writes into a plan

**Verdict:** VERIFIED

**Evidence:** `harness/metadata/NEW-MACHINE-START-HERE.md:98`: "选中哪些 capability 不是用户必须手写的架构步骤，而是 Planner 的绑定/组合结果。" ("Which capability is selected is not an architecture step the user must hand-write; it is the result of the Planner's binding/composition.")

Structural confirmation: `capability_capsule_id` does not appear anywhere in the user-facing intake code `harness/lib/intent_gateway.py` or `harness/lib/requirement_compiler/semantic.py` — it only appears in planning/execution-stage schemas (`harness/schemas/planning/capsule-plan.v1.schema.json`, `physical-plan.v2.schema.json`, `scheduler-input.v1.schema.json`, `harness/schemas/executable-node.v1.json`). In `elastic_planner.py`, capsule binding is computed by `run_generated_capsule_binding(...)` (line 6953) or `run_generated_composition_binding(...)` (line 6965), and admitted only via `validate_composition_selection(...)` (line 6933) — an independent-reviewer-model-gated selection process, not a field a human fills in on a submitted plan.

---

### C8. Capsule manifest structure — actual fields, including preconditions/postconditions/effects/write scope/version/predecessor

**Verdict:** PARTLY (manifests have preconditions, postconditions, effects incl. a write list, and version — but no field resembling "predecessor")

**Evidence:** Read three manifests in full: `harness/config/capability-capsules/cap.requirement-compiler-implementation.yaml`, `cap.chatgpt-browser-agent.yaml`, `guard.secret-leak-guard.yaml`. All three share one schema shape. Full text of `cap.requirement-compiler-implementation.yaml`:

```yaml
capability_capsule_id: cap.requirement-compiler-implementation
version: 0.1.0
capsule_kind: capability
metadata: {name, description}
applicability: {task_types, positive_signals, negative_signals}
contract:
  inputs: {required: [{name, type}], optional: [...]}
  outputs: {required: [...], optional: [...]}
  preconditions:
    - check: task_type_in
      values: [implementation, debugging, refactor]
  postconditions:
    - check: output_present
      field: patch_diff
    - check: output_present
      field: handoff_md
  invariants: [free-text strings]
composition:
  consumes: [{type: artifact.requirement_ir}, ...]
  produces: [{type: artifact.patch_diff}, ...]
  compatible_with: [guard.secret-leak-guard, resource.repo-workspace]
  incompatible_with: [cap.auto-merge-without-review]
  requires_after: [cap.requirement-compiler-verification]
effects:
  read: [repo.read, requirement.artifacts]
  write: [repo.worktree, artifacts.handoff]
  execute: [shell.pytest]
  network: []
  cost: [medium_model_quota]
  risk: [patch_scope_drift]
bindings: {skills, mcp_capabilities, data_refs, secret_refs, required_guard_capsules, required_resource_capsules}
verification: {self_check, external_verifier: {required, preferred_capsules}, pass_conditions}
operator_compatibility: {preferred, forbidden}
provenance: {owner, created_at}
```
(Full listing: `cap.requirement-compiler-implementation.yaml:1-113`.)

Directly answering the "in particular" questions:
- **preconditions**: yes — `contract.preconditions` (e.g. `check: task_type_in`).
- **postconditions**: yes — `contract.postconditions` (e.g. `check: output_present, field: patch_diff`).
- **effects on the world**: yes — a dedicated top-level `effects:` block with `read`, `write`, `execute`, `network`, `cost`, `risk` sub-lists.
- **a write scope**: `effects.write` is a list of coarse-grained write targets (e.g. `repo.worktree`, `artifacts.handoff`) — this is the closest thing to a "write scope" at the manifest level, but note the literal token `write_scope` does not appear anywhere in `harness/config/capability-capsules/*.yaml` (checked with grep across the directory, 0 hits); `write_scope` as a term is used elsewhere in the system at the task-graph-node level (README bullet: "read/write scope 必须可解析并位于允许的 artifact roots"), not inside the capsule manifest schema itself.
- **a version**: yes — top-level `version: 0.1.0`.
- **a predecessor**: no such field found. `grep -rn "predecessor" harness/config/capability-capsules/*.yaml` returned zero matches across all 46 files in that directory. The nearest analogous concept is `composition.requires_after`, which names another *capsule id* that must run after this one (an ordering/dependency declaration between capsule types), not a "predecessor" field on a manifest version lineage.

Marked PARTLY rather than VERIFIED only because the claim bundles several sub-questions and one of them (predecessor) is answered negatively, and "write scope" is present only as a coarser `effects.write` list rather than a literally-named field.

---

### C9. Execution evidence and gate verdicts governed by JSON Schemas under `harness/schemas/`, with directories for compiler, planning, evidence

**Verdict:** VERIFIED

**Evidence:** `ls harness/schemas/` confirms these are real directories, not files: `compiler`, `draft`, `evidence`, `influence`, `planning`, `training` (alongside many top-level `.json`/`.yaml` schema files).
- `harness/schemas/compiler/` contains e.g. `intent-ir.v3.schema.json`, `requirement-semantic-contract.v3.json`, `requirement-semantics.v2.schema.json`.
- `harness/schemas/planning/` contains e.g. `capsule-plan.v1.schema.json`, `physical-plan.v2.schema.json`, `scheduler-input.v1.schema.json`, `run-contract-frozen.v2.schema.json` (this is the schema `elastic_planner.py` asserts the frozen run contract against — `FROZEN_CONTRACT_SCHEMA = SCHEMA_DIR / "run-contract-frozen.v2.schema.json"`, `elastic_planner.py:80`, resolving into `harness/schemas/planning/`).
- `harness/schemas/evidence/` contains e.g. `claim_verdict.v1.schema.json`, `experiment_result.v1.schema.json`, `artifact_review.v1.schema.json`, and a `fixtures` subdirectory.

One nuance worth flagging: not every verdict/evidence schema lives inside `evidence/` — e.g. `acceptance-verdict.schema.json` sits at the top level of `harness/schemas/` rather than inside `evidence/`. The claim only asserts that directories for compiler/planning/evidence exist (true) and does not claim exclusivity, so this is not a refutation, just a precision note.

---

## What else I noticed

- **The claim author's own source document is in the repo and dated exactly 2026-08-31**: `harness/metadata/NEW-MACHINE-START-HERE.md` (header: "核对日期：2026-08-31") independently states nearly every one of C3/C4/C6/C7's assertions almost verbatim, including the stale "68" capsule count. This strongly suggests the claims were derived directly from that file rather than from re-reading code at the time, which is exactly the kind of thing that goes stale as the registry grows (68 → 80 in this case).
- **Unregistered manifest files sitting on disk** (5 of them, listed under C6) are a concrete, checkable instance of the "must not auto-activate" scenario the rule exists to prevent — worth knowing about if someone is auditing capsule inventory by listing the directory rather than the registry, since a directory listing will overcount by these 5 (plus the split between `harness/config/capability-capsules/` and the separate `harness/capability-capsules/` directory for research/scientific capsules — two directories feed one registry, which is easy to miss).
- **`NEW-MACHINE-START-HERE.md`** itself is explicit that the last full E2E test did not reach the Scheduler ("最后测试在 Planner 模型输出 schema 准入失败，未到 Scheduler") and cautions against treating "architecture goals" as "accepted behavior" — i.e. the document that best describes the current pipeline shape also states that shape has not been end-to-end verified as of that date. Anyone building on top of this should treat the pipeline topology (C1-C3) as more solid than any specific claim of it having been run end-to-end successfully.
- **`run_contract_frozen` / `capsule_plan` / `physical_plan` can legitimately be `None`** in the return of `compile_and_freeze_execution_bundle` on several early-exit paths (e.g. `elastic_planner.py:7034`, `7094`, `7132`, `7182`, `7224` all set `"run_contract_frozen": None`) — the freeze function has multiple rejection/failure branches before reaching an actual frozen contract, which is consistent with "gates before execution" but means "the Elastic Planner performs the freeze" should not be read as "the Elastic Planner always successfully produces a frozen contract."

**Tally:** VERIFIED: 6 (C1, C2, C5, C6, C7, C9) · REFUTED: 1 (C4) · PARTLY: 2 (C3, C8) · IMPRECISE: 0 · CANNOT-CHECK: 0

---

## Part 2 — Characterisation of Paper2Agent (not claim-checking)

Repository: `C:\Users\m50066326\huawei\Paper2Agent` (read-only, third-party, unrelated to Stellven/AI4Research).

**What it does.** Per `README.md` ("📖 Overview"): "`Paper2Agent` is a multi-agent AI system that automatically transforms research papers into interactive AI agents with minimal human input... Paper2Agent coordinates parallel specialist agents to turn scientific papers into reliable MCP servers and skills." Concretely it is a *skill* (`skills/paper2agent/SKILL.md`) that a coding-agent host (Claude Code, Codex, Gemini CLI) loads, then runs a workflow that reads a paper/repository and produces a working MCP server exposing that paper's methods as callable tools, plus an optional "paper skill." Its own description line: "Convert research papers and associated files, research code, or both into a reviewed paper skill and tested MCP server."

**Unit of packaging.** The deliverable is `dist/<repo-name>-mcp.zip` — quote from `skills/paper2agent/paper2mcp/references/output-delivery.md:3`: "A completed conversion provides `dist/<repo-name>-mcp.zip`: a usable MCP server project for the selected, verified tools." The ZIP contains a `USAGE.md`, the MCP server entry point and tool modules, pinned Python runtime requirements, and (per that file's "Package contents" section) "the original scientific implementation... with provenance and relevant notices, or document and test installation from a fixed version/commit." Combined-mode output additionally nests a `skill/<paper-name>/` alongside `mcp/<repository-name>-mcp/` (`SKILL.md:14-17`).

**Does it version that unit?** No semantic version number is assigned to the packaged agent/MCP server itself. Instead, identity and reproducibility are tracked by content hash and pinned upstream provenance, not a version field on the Paper2Agent output: "Record the ZIP SHA-256 and a file/hash inventory outside the package" and "document and test installation from a fixed version/commit" for the wrapped scientific implementation (`output-delivery.md`, "Validate the ZIP itself" step 1, and "Package contents" bullet 3). Dependency versions are "pinned" (`output-delivery.md:2`: "Pin its Python runtime dependency closure or tested lockfile") but that is dependency pinning, not a version identifier for the produced unit.

**Does anything validate a unit before it is published or installed?** Yes, explicitly and in detail. Two scripted checks are named in `skills/paper2agent/paper2mcp/SKILL.md:41-42`:
- `scripts/verify_workflow.py` — "checks recorded assignments, agent separation, phase order, and artifact hashes."
- `scripts/verify_mcp_server.py` — "launches the server over stdio and checks inventory, input schemas, and saved acceptance calls. Run it in the project and a fresh runtime."

`output-delivery.md`'s "Validate the ZIP itself" section (5 numbered steps) requires: extracting the ZIP into a fresh directory (including a path with spaces), creating a clean runtime environment there, checking executable permissions survive extraction, starting the server from that clean extraction, and — step 4 — "Give an independent verifier the extracted package... Run real MCP calls for every delivered tool, check input schemas, compare scientific results/artifact contents." Step 5 requires retaining `reports/delivery-validation.json` with the archive SHA-256, packaged file hashes, and actual call/comparison outcomes. The workflow table in `paper2mcp/SKILL.md:17-26` lists "Runtime installation validation" and "Documentation and ZIP delivery" as required stages with their own completion markers (`runtime_validation_done`, `delivery_done`), and `SKILL.md:45` states: "Write stage success markers only after their evidence and workflow gate pass. Worker completion alone does not establish success. Final delivery requires runtime validation, recipient-facing `USAGE.md`, and a ZIP that passes installation and real calls after extraction at a new location." So publication/delivery is gated on a documented, scripted, independent-verifier validation pass, not merely on the coordinator's own say-so.
