# AI4Research / OpenSolar — Benchmarking, Evaluation & Verification Infrastructure

Scope: benchmarks/, harness/evals/, harness/evaluators/, harness/lib/{eval_runner,evaluation_plan,evaluation_budget,agent_arena_benchmark,capability_fusion_benchmark,capability_certification_suite,capability_activation_proof,activation_proof_vnext,capability_effects}.py, harness/schemas/planning/evaluation-*, tests/journeys/phase22/, tests/platform/phase22/, docs/integrations/autosci/phase-22-*, AGENTS.md, scripts/check-*.sh / smoke-*.sh.

Repo: `/home/muk/work/AI4Research`, branch `openJiuwen-Solar`, HEAD `b0bf165f9`.

Legend: **[VERIFIED]** read directly in code/docs and quoted/cited below. **[DOC-CLAIM]** asserted by project docs but not independently re-executed by this research pass (per instructions, no tests were run). **[INFERRED]** my synthesis across multiple files.

---

## Summary

- **[VERIFIED]** The project runs a documented **three-layer test strategy** (AGENTS.md): journey tests are primary acceptance evidence, "reliable existing tests" are a regression layer, and the 1,502-row atomic feature matrix is a diagnostic layer only — atomic rows no longer gate the journey report.
- **[VERIFIED]** Result vocabulary is a strict **six-state enum** (`PASS`, `PASS_WITH_KNOWN_LIMITATIONS`, `FAIL`, `NOT_TESTED`, `ENVIRONMENT_BLOCKED`, `NOT_AVAILABLE`) with an explicit anti-copy rule: "Never copy a green result to file formats, platforms, providers, failure branches, or other variants that the journey did not use" (AGENTS.md:82-84).
- **[VERIFIED]** Phase 22 defines **25 journeys** (P22-J01…P22-J25); J01-J10 have full narrative task/input/execution/pass-criteria/L2-coverage sections in `journey-test-plan.md` (mojibake-encoded Chinese, decoded below); J11-J25 are documented as a canonical ID→test-file→proof-obligation mapping table.
- **[VERIFIED]** `SOLAR_TEST_MODE=rapid_smoke` is a **trusted-environment-variable** authorization (`elastic_planner_adapter.py::_trusted_test_policy`), explicitly *not* triggerable via prompt text or operator output keywords (NEW-MACHINE-START-HERE.md:62-64), and it zeroes the semantic-evaluation budget while keeping deterministic gates required. Docs explicitly record a case where "a rapid receipt PASS did not prevent an empty-discovery handoff", i.e. a rapid_smoke PASS receipt is not proof every hard gate actually ran.
- **[VERIFIED]** The most recent recorded full unattended E2E run (2026-08-31, product commit `f463b861b`) **FAILED at Planner-stage provider schema validation** (`invalid_json_schema`, missing `cpu_cores_min`/`memory_mb_min`/`gpu_required` in the `required` array of the provider-facing structured schema). All later work referenced from that failure ("89 offline regressions") is explicitly labeled offline/source-only regression, not a re-accepted online E2E: *"离线89项回归通过不等于provider/E2E成功"* — "offline regressions passing does not equal provider/E2E success."

---

## Mermaid: Three-layer test strategy and authority

```mermaid
flowchart TB
    subgraph L1["Layer 1 - Journey tests (PRIMARY ACCEPTANCE)"]
        J["tests/journeys/phase22/code/*.py
25 real-task journeys P22-J01..J25
run production entrypoints, keep user-visible outputs"]
    end
    subgraph L2["Layer 2 - Regression tests (BREAKAGE DETECTION)"]
        R["Existing pytest/unittest suites
(elastic planner, scheduler, requirement compiler, ...)
run before/after journeys"]
    end
    subgraph L3["Layer 3 - Atomic inventory (DIAGNOSTIC ONLY)"]
        A["tests/platform/phase22/atomic_feature_matrix.json
1502 atomic_features across 142 L2 features
+ full report xlsx + brief report (L2-only)"]
    end

    J -- "primary PASS/FAIL/etc verdict for Journey + brief reports" --> Verdict["Journey Result States
(6-state enum, AGENTS.md)"]
    R -- "localizes cause of journey failure; does NOT itself set final verdict" --> J
    A -- "diagnostic work queue; never overrides journey plan, code, or journey evidence" -.-> J
    J -- "old atomic FAIL triaged once (core->FAIL / edge case->PASS_WITH_LIMITS / broken fixture->repair / unexercised->NOT_TESTED)" --> A
```

Authority ranking is explicit in AGENTS.md "Sources of Truth" (1. user instruction, 2. journey plan, 3. current code, 4. journey run evidence, 5. regression tests, 6. full report/atomic matrix, 7. progress log) — the atomic matrix is source-of-truth #6, below journey evidence.

---

## Journey table (P22-J01..J25)

Decoded from `tests/journeys/phase22/journey-test-plan.md` (file is UTF-8 that was previously mis-round-tripped through CP1252, producing mojibake like `çœŸå®ž`; the underlying text is Chinese and decodes cleanly via `text.encode('cp1252').decode('utf-8')` on the raw bytes).

| ID | Task (English gloss) | Main user-visible outcome | Default environment |
|---|---|---|---|
| P22-J01 | Install from scratch and check running status | Usable local CLI + status page | Linux/WSL2, local, no live provider |
| P22-J02 | Have Solar actually fix a small code defect | Real code change, tests, and approval evidence | tmux + Codex/Claude, live provider |
| P22-J03 | Run the official platform workflow benchmark | Scores, per-item evidence, auditable report | Installed isolated harness |
| P22-J04 | Import and re-import a local paper | Queryable paper, source, graph and memory evidence | Local PDF/Markdown, default offline |
| P22-J05 | Search literature around a topic + anchor | Deduplicated, sourced candidate literature list | Network / literature provider |
| P22-J06 | Form and filter research ideas from paper evidence | Sourced, falsifiable, rankable idea cards | J04/J05 products, optional live model |
| P22-J07 | Design and actually run a small experiment | Plan, real process result, metrics and status | Local Python, controlled execution permission |
| P22-J08 | Verify one true / one false claim using experiment results | Two traceable, distinguishable verdicts | J07 products, local evaluator |
| P22-J09 | Generate and review a deliverable research report | Report, evidence index, review, and publish package | J04-J08 products, optional compile tool |
| P22-J10 | Backup, uninstall-with-retained-data, restore, then full uninstall | Data recoverable, and finally zero Solar residue | Isolated install directory, local |
| P22-J11 | Resolve and invoke a capability capsule/operator through Solar | Governed runtime evidence for a selected capsule + physical operator | `test_j11_capsule_operator.py` |
| P22-J12 | Recover an interrupted run, retain execution records | Resume preserves prior state, terminal auditable record | `test_j12_failure_recovery_records.py` |
| P22-J13 | Open the local interaction interface via shipped entrypoint | Interface renders usable state, no crash | `test_j13_local_interaction_interface.py` |
| P22-J14 | Receive a WeChat-origin identity event via product channel boundary | Real configured channel/account required; fixtures alone can't pass WeChat/identity L2s | `test_j14_wechat_identity.py` |
| P22-J15 | Execute install/runtime matrix on the named OS | Each OS verdict needs evidence from *that* OS - one platform never proves another | `test_j15_cross_platform_install_matrix.py` |
| P22-J16 | Clarify requirements, compile a bounded repair, verify in tmux | Real diff fixes a failing test through Solar | `test_j16_tmux_requirements_builder.py` |
| P22-J17 | Select capsule/operator/model, persist TaskGraph state, interrupt+recover in tmux | Dispatch/execution/eval/persistence/recovery evidence, same sprint | `test_j17_tmux_capsule_operator_core.py` |
| P22-J18 | Run Linux CLI/status/tmux lifecycle, inspect settings/traces | Real Linux/WSL commands start, report, stop, release resources | `test_j18_real_linux_status_lifecycle.py`, `test_j18_tmux_cli_status_config.py` |
| P22-J19 | Use real dashboard, inspect local account/channel surfaces | Browser UI must render real backend state | `test_j19_real_gui_dashboard.py`, `test_j19_tmux_ui_account_channels.py` |
| P22-J20 | Produce source-backed research synthesis via `autosci_bridge.py research` | Provider sources, synthesis, citations, report, terminal state all usable | `test_j20_research_synthesis.py` |
| P22-J21 | Build and execute an experiment, hand off usable package | Product-built assets execute, satisfy contract, downstream-checker-accepted | `test_j21_experiment_build_handoff.py` |
| P22-J22 | Review supported vs. overbroad claims, record follow-up | Supported evidence passes, overreach fails closed | `test_j22_evidence_review_followup.py` |
| P22-J23 | Route a real model request, retain usage audit evidence | Requested/observed provider-model match, no hidden fallback | `test_j23_model_routing_audit.py` |
| P22-J24 | Export/redact/backup/delete/uninstall sandbox-owned personal data only | All privacy actions in isolated home; owned residue removed, no secrets exposed | `test_j24_privacy_lifecycle.py` |
| P22-J25 | Construct supported Python runtime deliverable, replay durable archive in clean sandbox | Schema-valid, hash-bound, credential-free bundle; replay installs offline and starts real status service | `test_j25_runtime_deliverable_distribution.py` |

**Minimum journey evidence (AGENTS.md:86-99)** every *accepted* journey must record: journey ID + task description; realistic input/fixture; exact production command/entrypoint; required environment/config (no secrets); minimum observable success conditions; L2 features actually exercised; exit code + concise stdout/stderr; generated artifact paths + basic usability checks; Git commit + run ID; final result + known limitations. Quote: "Do not pass a journey merely because a process started or a file exists."

Recommended completion order (journey-test-plan.md, "实现顺序"): finish provider-free J01, J03, J04, J07, J08, J10 first; then network/model-needing J05, J06, J09; finally run J02 on an already-authorized live runtime — to validate runner/sandbox/evidence format first before absorbing provider cost/uncertainty.

---

## Six-state result vocabulary

| State | Meaning (AGENTS.md:67-84) |
|---|---|
| `PASS` | Realistic task completed and its minimum observable success conditions were met. |
| `PASS_WITH_KNOWN_LIMITATIONS` | Core task completed, but a real non-core variant, edge case, or limitation remains. |
| `FAIL` | An implemented path failed, or the produced result did not meet the task's minimum success conditions. |
| `NOT_TESTED` | No accepted journey exercised the feature or variant. |
| `ENVIRONMENT_BLOCKED` | A specifically named platform, hardware, credential, account, permission, or provider prevented execution. |
| `NOT_AVAILABLE` | The required product behavior is not implemented. |

**Exact quote (AGENTS.md:82-84):**
> "A journey may prove only the feature paths that it actually exercised. Never copy a green result to file formats, platforms, providers, failure branches, or other variants that the journey did not use."

**Triage rule for old atomic failures (AGENTS.md:105-119):**
1. Core step / data integrity / privacy / security / truthfulness impact → journey is `FAIL`.
2. Real unexercised edge case → journey may be `PASS_WITH_KNOWN_LIMITATIONS` (retain limitation in full report, summarize in journey report).
3. Broken fixture/runner/path assumption/incorrect expected result → quarantine/repair the *test*, do not record as product failure.
4. Not exercised at all → record as `NOT_TESTED`; "do not infer a pass."

---

## Gate & smoke script inventory (scripts/)

All `check-*` and `smoke-*` scripts install into an isolated sandbox `HOME` (never the real user home) and are structured as deterministic assertions over that sandbox, not live-model journeys. `check-harness-plumbing.sh` explicitly labels itself: **"deterministic harness plumbing smoke, not live runtime behavior"** and installs with `--fake-keys --skip-llm-cli` — quota-free by construction.

| Script | Category | What it verifies |
|---|---|---|
| `check-autosci-install-closure.sh` | Gate (deterministic) | The *installed* CLI carries the AutoSci runtime closure, not just repo-local source. |
| `check-core-imports.sh` | Gate (deterministic) | Static import-resolution over `core/`. |
| `check-daemons-lifecycle.sh` | Gate (deterministic, sandbox install) | Daemons component installs; service file renders to correct path and is structurally valid. |
| `check-daemons-render.sh` | Gate (deterministic) | Both daemon service templates render with sample values; no forbidden token / unresolved `{{`. |
| `check-dry-run.sh` | Gate (deterministic) | `install.sh --dry-run` writes ZERO files anywhere under HOME. |
| `check-harness-plumbing.sh` | Gate (deterministic, quota-free) | Sandbox install + `solar doctor/status --json` + preflight/coordinator/dispatch artifact plumbing, **explicitly not live Claude behavior**. |
| `check-installed-clean.sh` | Gate (privacy) | Installed/shipped payload carries zero personal tokens. |
| `check-installer-contract.sh` | Gate (deterministic, non-TTY) | Installer contract checks; TTY wizard paths are separately in `smoke-installer-wizard-pty.py`. |
| `check-kernel-gen.sh` | Gate (deterministic) | Min/max SOLAR.md kernel assembly; forbidden tokens. |
| `check-privacy.sh` | Gate (privacy) | Repo-wide grep for owner-identifying personal tokens (paths/handles/emails/LAN IPs); real-secret scanning is delegated to CI gitleaks (not run here). |
| `check-release-coherence.sh` | Gate (release) | Version/channel/mode/reference invariants for a cut tag. |
| `check-repo-hygiene.sh` | Gate (deterministic) | Rejects machine-local/generated/raw test-run state in the Git index. |
| `check-solar-harness-front-door.sh` | Gate (deterministic, sandbox) | Front-door harness entrypoint behavior. |
| `check-solar-status.sh` | Gate (deterministic, sandbox) | `solar status` behavior. |
| `check-solar-ui-lite.sh` | Gate (deterministic, sandbox) | UI-lite path. |
| `check-update.sh` | Gate (deterministic, offline) | Fetch-based `solar update` end-to-end, fully offline. |
| `check-safe-staging.py` | Gate (governance, R8 G05) | Safe Git staging check. |
| `check-secret-scan.py` | Gate (governance, R8 G06/S05) | Reproducible secret scan. |
| `check-windows-filenames.py` | Gate (governance, R8) | Detects illegal Windows filenames. |
| `smoke-install-matrix.sh` | Smoke (deterministic, sandbox) | Profile-based install matrix (`minimal`, `full-non-rust`, ...) with dry-run/daemon/dashboard checks. |
| `smoke-install.sh` | Smoke (deterministic, sandbox) | Basic install smoke. |
| `smoke-status-server-e2e.sh` | Smoke (deterministic, sandbox) | Fresh sandbox install -> start installed status-server -> assert HTTP contract -> uninstall residue-free. |
| `smoke-installer-wizard-pty.py` | Smoke (deterministic, PTY) | Interactive installer wizard via pseudo-TTY. |
| `smoke-core-policy.ts` / `smoke-health-monitor.ts` | Smoke (deterministic, bun) | Core policy / health monitor TS smokes. |
| `live-codex-e2e-isolated.sh` / `live-claude-e2e-isolated.sh` | **Live E2E (quota-consuming)** | Not `check-`/`smoke-` prefixed; these explicitly drive real Codex/Claude runtimes and consume model quota — the counterpart to the deterministic gates above. |

**[INFERRED]** The naming convention itself signals the quota boundary: anything named `check-*`/`smoke-*` uses `--fake-keys`/`--skip-llm-cli` or fully offline flows; anything doing real model calls is named `live-*-e2e-isolated.sh` and lives outside the `check-`/`smoke-` prefix set, matching AGENTS.md's rule that "Live-provider tests require explicit user authorization."

---

## Detailed findings by question

### 1. Three-layer test strategy

**[VERIFIED]**, AGENTS.md "Current Objective" (lines 7-25):
1. **Real-task journey tests are the primary acceptance evidence** — "a small set of end-to-end tasks uses realistic inputs, runs production entrypoints, and retains user-visible outputs and logs."
2. **Reliable existing tests are the regression layer** — "run before or after journeys to detect breakage and help localize failures. They do not by themselves establish the final product verdict."
3. **The atomic inventory is the diagnostic layer** — "the full workbook and atomic matrix preserve detailed behavior, test, implementation, platform, and known-limitation evidence. Phase 22 no longer requires every atomic row to have an exact executable selector before the journey report can finish."

Authority: journey evidence > regression tests > atomic matrix/full report (AGENTS.md "Sources of Truth" ordering, §50-65). What each proves: journeys prove real user-observable task completion; regressions prove no breakage / help localize; atomic rows prove (or fail to prove) one independently observable behavior each, but per the matrix's own `review_policy.test_policy`: **"A test record or L2 representative probe is not copied to every atomic child. Only assertion-level defensible selectors are bound."**

### 2. Journey tests / Phase 22 enumeration

See table above. `tests/journeys/phase22/journey-test-plan.md` (463 lines, mojibake Chinese — decode via `.encode('cp1252').decode('utf-8')`) frames the 10 core journeys (J01-J10) as answering "can OpenSolar complete one useful thing for the user, and can they get an inspectable product" rather than substituting for the 1,502 atomic features. Quote (decoded): "These tasks are not a substitute exhaustive proof for the 1,502 atomic features. Below, 'L2 covered' means that L2 must produce observable effect during the flow; only L2s actually supported by evidence get a new positive conclusion. A journey passing does not automatically judge every boundary of every listed L2 as passing."

J11-J25 appear only as a canonical mapping table (lines 433-455) with task/test-file/proof-obligation columns (see table above) — less narrative detail than J01-J10.

Minimum evidence obligations: see AGENTS.md §86-99, quoted above.

### 3. Six-state vocabulary and anti-copy rule

See table + exact quote above (AGENTS.md:67-84). The journey-test-plan.md restates the same six states in Chinese with essentially identical semantics, confirming the vocabulary is used consistently across both documents.

### 4. Atomic feature matrix

**[VERIFIED]**, from `tests/platform/phase22/atomic_feature_matrix.json` (48,450 lines) and `README.md`:
- `counts.l2_features` = **142**
- `counts.historical_atomic_rows` = 2,047 -> `counts.reviewed_atomic_features` = **1,502** (net_rows_removed = 545; historical duplicates "remain recoverable from Git commit 012e7a20 and the progress log")
- `test_generation_status` breakdown (of 1,502): `TAGGED_NOT_GENERATED_MANUAL_ORACLE` 909, `CONFIG_RESOLVED_NEEDS_EXACT_BINDING` 179, `BLOCKED_NOT_IMPLEMENTED` 151, `CONFIG_RESOLVED_RELATED_SUITE_FAILED` 39, `PLATFORM_OR_HARDWARE_REQUIRED` 44, `REUSED_L2_REPRESENTATIVE_EXECUTABLE` 120, `GENERATED_EXECUTABLE` 26, `REUSED_EXISTING_EXECUTABLE` 25, `MANUAL_ORACLE_REQUIRED` 9.
- `implementation_status`: `IMPLEMENTED_CURRENT_SUBSET_UNVERIFIED` 1,186, `IMPLEMENTED_EXECUTABLE_EVIDENCE` 165, `NOT_IMPLEMENTED` 151.
- `l2_atomic_rollup_status` (per-L2, 142 total): `FUNCTION_IMPLEMENTED_ALL_ATOMIC_TESTS_PASSED` 2, `FUNCTION_IMPLEMENTED_ATOMIC_TEST_FAILED` 2, `FUNCTION_NOT_IMPLEMENTED_TEST_BLOCKED` 28, `IMPLEMENTED_TEST_GAP_BLOCKED` 110.
- Each atomic feature row (`atomic_feature_id`, e.g. `P22-AF-WF-001-01`) carries: sheet/level_1/level_2, description, `scenario_type`, `review_decision`, `implementation_status`, `test_generation_status`, `coverage_relationship`, `test_binding_id`/`test_selector`/`runner_command`, `mapping_confidence`, `current_result`, `blocker_or_notes`, `code_entrypoints`, `code_limitations` — an unusually rich per-row audit trail.
- Relation to L2/"brief" report: each of the 142 L2 features rolls up from its atomic children (`l2_summary` array, 142 entries) into one `atomic_rollup_status`. The **full report** (`docs/integrations/autosci/phase-22-test-report.xlsx`) is the detailed diagnostic workbook containing all atomic rows; the **brief report** (external path `C:/Users/j50058254/Downloads/AI4RnD Feature List.xlsx`, AGENTS.md:44) is explicitly **Level-2-only, "must never contain atomic rows," and is synchronized from accepted journey results, not used as a source of atomic definitions** (AGENTS.md:46-48).
- Separately, `tests/platform/phase22/README.md` describes a companion **L2 execution matrix** (`l2_execution_matrix.json`) with a 3-class scheme: Class 1 (implementation exists, representative probe passed), Class 2 (implementation exists, probe failed), Class 3 (no implementation, blocked). Audited 2026-07-23 checkout: **142 L2s: 94 class 1, 38 class 2, 10 class 3**; 132 implemented L2s map to 79 unique executable probes (58 passing, 21 failing). Quote: "A passing validator means the design inventory is structurally complete and traceable; it does not mean the underlying L2 capabilities pass." This is a distinct, code-generated cross-check layer from the atomic_feature_matrix's 1,502-row inventory.

### 5. evaluation_plan / evaluation-check-registry / test_policy freezing

**[VERIFIED]** `harness/lib/evaluation_plan.py` (module docstring): "Compile frozen per-node evaluation contracts from admitted Planner artifacts." It:
- Loads and schema-validates the **check registry** (`harness/config/evaluation-checks.v1.json`, schema `harness/schemas/planning/evaluation-check-registry.v1.schema.json`) — each check row has `check_id`, `mode` in {`deterministic`,`semantic`,`deterministic_plus_semantic`}, `applies_to` (either `kind:bound_output` or `kind:artifact_type` with an `artifact_types` list and `auto_apply` flag), `decision`, `deterministic`/`semantic` sub-objects. Deterministic checks must resolve to a real importable callable (`_resolve_callable`) or the registry load raises `EvaluationPlanError` — i.e., you cannot register a deterministic gate pointing at a nonexistent function.
- `compile_evaluation_plan(requirement_ir, plan_ir, capsule_plan, task_graph, registry=...)` binds registry checks to concrete graph nodes: it walks `task_graph["nodes"]`, resolves each node's `semantic_artifact_contract.produces` output types (falling back to the semantic PlanIR node's `_output_contracts`), matches those against `applies_to.artifact_types`, and also honors composition-expanded "support nodes" (`<parent>__<digest>_cNN`) by aggregating `family_outputs` per parent so a requirement's verifier binds correctly even when execution splits one logical node into several physical ones. Requirement-level checks (`_requirement_check`) resolve from `row.get("check")` / `verifier_id` / `verification_method`, defaulting to `"not_machine_checkable"` if nothing is bound.
- Gate policy per node (`_gate_policy`) reads `evaluator_gate.kind`, `on_fail`, and `max_repair_attempts`, clamped to at most 2 repairs.

**`test_policy` and freezing**: `evaluation_budget.py::apply_evaluation_budget(graph, requirement_ir, test_policy=...)` is the risk-bounded semantic-evaluation policy layer that runs "after semantic planning and before plan certification" (module docstring). It computes a `risk_tier` (low/medium/high/critical, budget capped at **1** independent LLM evaluator regardless of tier — `_RISK_BUDGETS = {"low":1,"medium":1,"high":1,"critical":1}`), selects at most that many `semantic_evaluation_node_ids` (preferring the final report node for research requests, or the highest-scoring terminal/report/critique node otherwise), and stamps every node with an `evaluation_policy` record (`policy_id`, `risk_tier`, `semantic_review_required`, `decision_reason`). The **frozen** graph carries `bounded["test_policy"] = policy` and `bounded["evaluation_policy"]["test_policy"] = policy` — i.e. `test_policy` becomes part of the graph payload that gets hashed/frozen downstream in `scheduler_input.py` (which lists `"test_policy"` among the fields projected into the `SchedulerInput` and checks `graph.get("test_policy") != (value.get("test_policy") or {})` as a mismatch/tamper condition, `scheduler_input.py:884`). `policy_allows_none()` cross-checks that a node's `evaluator_gate.kind == "none"` is only legitimate if the node is inside the graph's `deterministic_only_node_ids` under the same `policy_id`, or the graph is already a frozen `solar.scheduler_runtime_projection.v1` (i.e., SchedulerInput is treated as "hash-bound runtime authority" that "carries the certified node policy" even without full planning metadata, `evaluation_budget.py:275-278`).

### 6. SOLAR_TEST_MODE=rapid_smoke

**[VERIFIED]**:
- Authorization point: `harness/tools/elastic_planner_adapter.py::_trusted_test_policy()` reads `os.environ.get("SOLAR_TEST_MODE", "")`; any nonempty value other than exactly `"rapid_smoke"` raises `ValueError(f"unsupported SOLAR_TEST_MODE: {mode!r}")`. This is a Python-process environment variable read at adapter startup — not user-prompt text, not operator/worker output.
- Doc confirmation, `NEW-MACHINE-START-HERE.md` (decoded): "Rapid smoke injects a frozen test_policy through the trusted environment `SOLAR_TEST_MODE=rapid_smoke`; it is not authorized by keywords in the user prompt or operator output. It reduces the cost of executing semantic evaluation; it cannot be used to prove scientific quality; one rapid receipt PASS did not prevent an empty discovery handoff, so a receipt alone cannot claim all hard gates actually executed successfully." Also `MIGRATION-CODEX-PROMPT-20260831.md`: "使用受信任 rapid_smoke 环境，不是 prompt 关键词" ("use the trusted rapid_smoke environment, not prompt keywords").
- Effect: `evaluation_budget.apply_evaluation_budget()` — when `policy.mode == "rapid_smoke"`, forces `semantic_evaluation_budget=0`, `deterministic_gates_required=True`, sets `semantic_node_ids=[]` (no LLM evaluator selected at all), and for every node either preserves an existing `deterministic_command` gate (reason `rapid_smoke_deterministic_gate_retained`) or sets `evaluator_gate={"kind":"none","on_fail":"fail","test_policy_mode":"rapid_smoke"}` (reason `rapid_smoke_bypass`). `contract_gate_executor.py:239-270` reads `gate.get("test_policy_mode") == "rapid_smoke"` to decide whether the executor's decision reason is `rapid_smoke_bypass` vs `evaluator_gate_none`.
- What it does NOT prove: it skips semantic (LLM-judged) evaluation entirely; deterministic gates still run. Docs are explicit that a rapid_smoke PASS is not scientific-quality proof.
- **The documented empty-discovery incident**: `migration-handoff-20260830.md` "Historical defect and follow-up" section, run `sprint-20260830-194438-...`, final state `failed/scheduler_failed`: "discovery passed, ingestion failed, five later nodes cancelled. Ingestion error: `Discovery evidence contains no candidates`." Root cause chain: a negative-literal constraint (`deliverable_mode not_equals "one-off answer"`) was compiled by `lib/requirement_compiler/compiler.py::_expression_values` into a *positive* required_value (dropping the negation), which then got folded into the Discovery node's objective text by `lib/elastic_planner.py::_preserve_discovery_requirement_scope`; providers returned 11 candidates, relevance kept 3, but an over-broad topic-coverage check "demanded workflow phrasing" and emptied the shortlist to zero. Exact quote: **"The rapid receipt used rapid_smoke_bypass; it is not proof that all hard gates actually executed. Ingestion rejected the empty artifact as it should."** — i.e., the deterministic ingestion gate correctly caught the empty handoff even though the upstream discovery step had a rapid_smoke PASS receipt; the case is presented as a *positive* proof that rapid_smoke's remaining deterministic gates work, while cautioning readers never to treat the rapid_smoke evaluator PASS itself as end-to-end proof.

### 7. Capability ACTIVATION PROOF

**[VERIFIED]** `harness/lib/capability_activation_proof.py` (871 lines). Module docstring states the four conceptual checks directly:
1. "Default dispatch text contains intent/capability context."
2. "DAG graph-node dispatch receives the same context."
3. "Real runtimes produce observable artifacts."
4. "Negative controls do not falsely select unrelated capabilities."

These four are expanded into **13 concrete proof functions** run by `main()`: `proof_dispatch_activation`, `proof_graph_dispatch_activation`, `proof_use_effect_telemetry`, `proof_runtime_effect`, `proof_ruflo_runtime_effect`, `proof_model_call_runtime_projection`, `proof_disposable_sandbox_runtime_lifecycle`, `proof_sandbox_write_guard_blocks_host_write`, `proof_mirage_exec_routes_through_sandbox`, `proof_qmd_search_routes_through_sandbox`, `proof_pdftotext_extract_routes_through_sandbox`, `proof_status_ui_capability_health_projection`, `proof_negative_control` — passed/total scored, both JSON and rendered Markdown reports written under `reports/capability-activation-evidence/latest/`.

**Negative control** (`proof_negative_control`, lines 777-802): injects a deliberately capability-irrelevant dispatch file (`"# Negative\n\nCompute 2 + 2 only.\n"`) through the real `solar_skills.py inject` pipeline, then asserts the resulting injected text does **not** contain any of a fixed unrelated-capability marker list: `["Browser-use MCP", "MarkItDown", "Ruflo", "Empirical Research", "gstack"]`. Passing means no capability was falsely auto-injected for an irrelevant task — a check specifically against over-eager/false-positive capability activation. There is also a second negative-style check, `proof_sandbox_write_guard_blocks_host_write`, which asserts a disallowed host write is actually blocked (writes evidence to `sandbox-write-guard-negative.json`).

**Self-stated boundary (exact quote, lines 11-12 and rendered report, lines 824-828):**
> "Boundary: no benchmark can prove an LLM's private reasoning. We prove the worker-visible prompt/context, runtime calls, and produced artifacts."

Rendered-report Chinese equivalent: "能证明：默认 prompt/dispatch 已带能力、真实 runtime 已执行、产物已生成、负例不误触发。不能证明：LLM 私有思考过程一定按某个 skill 思考；只能证明 worker 可见输入和可观察输出。" ("Can prove: default prompt/dispatch already carries the capability, the real runtime executed, artifacts were produced, negative cases don't falsely trigger. Cannot prove: that the LLM's private reasoning process definitely 'thought' via a given skill — only the worker-visible input and observable output.")

`activation_proof_vnext.py` (389 lines) is a **separate, additive coverage extension** (explicitly documented as not mutating the base module: "The base module (`activation_proof.py`) is imported and consumed read-only; this file does NOT mutate it") that adds three broker/verifier/artifact-registry FSM coverage metrics via a deterministic in-process broker drive into an isolated `EventLedger` (no production state, no network) — it targets a newer S03 broker component, distinct from the capability-activation proofs above, and outputs `verdict: PASS|FAIL` against coverage `thresholds`.

### 8. capability_effects.py — use->effect telemetry

**[VERIFIED]** Module docstring (`harness/lib/capability_effects.py`): "Use->effect evidence updater for Solar capability injection. This module connects three observable artifacts: 1. dispatch `.intent.json` says what Solar made visible to the worker. 2. handoff/eval files say what the worker/evaluator actually cited. 3. sys_resource_usage records the use/effect telemetry for audit and evolution. It does not claim access to private model reasoning."

Mechanism: `_evidence_matches(capabilities, evidence_text)` case-insensitively substring-matches each registered capability's provider/capability/scorecard terms (`_terms_for_capability`, sorted longest-first to avoid short-token false positives) against the text of handoff/eval files, producing `matched_terms` per provider. `_verdict_from()` extracts a PASS/FAIL verdict from an eval JSON's `verdict`/`status` field, or falls back to a regex search for `\b(PASS|FAIL|FAILED|PASSED)\b` in free text. `scan_effect()` (function begins ~line 90, only partially read in this pass) is presumably the orchestrator tying dispatch-declared capabilities to what evidence actually cites, then calling `resource_telemetry.record_usage()` to log the correlation (import wrapped in try/except, "fail-open in copied test fixtures"). This is the "dispatch declared X -> worker cited X -> sys_resource_usage recorded X" correlation loop referenced in the task brief.

### 9. Benchmarks: agent_arena, capability_fusion, others

**[VERIFIED]**:
- **`agent_arena_benchmark.py`** (1,135 lines): "Agent Arena — reproducible cross-agent benchmark harness." Explicitly evidence-first: "It does not claim Solar-Harness is on an external leaderboard unless the public benchmark adapter is actually configured and run." Ships a `PUBLIC_BENCHMARKS` registry (SWE-bench Pro, SWE-bench Verified, and per the docstring also Terminal-Bench/OSWorld/GAIA/WebArena/tau-bench) where each entry has an `adapter_env` (e.g. `SWE_BENCH_PRO_CMD`), a `default_binary`, and a `score_contract` ("runner must write JSON score to `SOLAR_ARENA_SCORE_FILE`"). This means public-benchmark adapters are **env-var-gated and optional** — the benchmark only actually runs the external suite if the operator sets the corresponding command env var; otherwise it presumably runs only the built-in "local Solar smoke suite that proves orchestration capabilities." Also references a vendored `hermes-agent` (cloned from `nousresearch/hermes-agent`) run via `uv`.
- **`capability_fusion_benchmark.py`** (492 lines): "Benchmark whether external capabilities are fused into Solar-Harness... not a micro-performance benchmark. It measures integration quality: manifest validity, capability registry exposure, health visibility, dispatch auto-injection, local runtime smoke, and pane-level availability." Uses a weighted score across `WEIGHTS = {"manifest":15,"registry":20,"health":15,"dispatch":20,"runtime":20,"pane":10}` (sums to 100) over named `SCENARIOS` (e.g. "empirical-research" plugin with capabilities `["research.empirical_pipeline","research.literature_review","analysis.causal_inference"]`).
- **`capability_certification_suite.py`** (412 lines): the "top-level proof runner" answering "Are Solar/Solar-Harness capabilities complete, automatic, default-on, usable, and effective?" It composes existing E2E tests and benchmarks plus "anti-false-positive checks," and explicitly separates `fast` from `full`/`heavy` certification because "some real runtime probes load browsers, local embedding models, or external agent runtimes." Six named `DIMENSIONS`: complete / default / automatic / usable / effective / evidence (Chinese descriptions map to: capability listing coverage; default dispatch injects context; no manual skill-picking needed; CLI/scripts/runtime/pane actually run; positive hits land and negative hits don't, with benchmark scores; every judgment has JSON/Markdown/command-output evidence).
- **`benchmarks/mlx_quantization_bench.py`**: an unrelated, standalone MLX (Apple Silicon ML framework) FP16/INT8/INT4 transformer-block latency micro-benchmark — not part of the Solar capability-verification stack; appears to be a separate performance-engineering artifact at repo root.
- Wired/runnable: **[VERIFIED]** `harness/solar-harness.sh` (lines ~4312-4390, ~4487-4488) wires `capability_fusion_benchmark.py`, `agent_arena_benchmark.py`, `capability_certification_suite.py`, and `capability_activation_proof.py` as CLI subcommands, each with an existence guard (`[[ -f "$_x" ]] || { err "... not found"; exit 1; }`) — i.e. these are first-class `solar-harness.sh` subcommands, not orphaned scripts. Journey **P22-J03** ("run official platform workflow benchmark") is explicitly built to exercise this benchmark path.
- `harness/lib/eval_runner.py` (84 lines) is a smaller, generic "run small Solar eval packs with explicit command gates" runner: loads a YAML/JSON pack (`harness/evals/packs/{plugin-health,skill-coverage,s5-basic,skill-healthcheck-evolution}`), runs each `checks[].cmd` via `subprocess.run(shell=True, ...)`, and compares `exit_code` to `expect_exit`. This is distinct from the certification suite — a lighter-weight, pack-based deterministic-command runner used for skills/plugin health rather than capability-activation proof.
- `harness/evals/skills/*.eval.yaml` (browse/plan/ship/review/retro) and `harness/evaluators/scientific/*.py` (30 files: idea_gate, method_gate, claims_gate, experiment_*_gate, report*_gate, publication_gate, etc.) form the **scientific evidence gate layer** consumed by the Requirement/Planner pipeline's `evaluation-check-registry` — out of this agent's primary scope (claim/evidence schemas) but confirmed present and organizationally adjacent.

### 10. Scripts categorization

See the Gate & Smoke inventory table above. Summary: 19 `check-*` scripts (deterministic gates: privacy/secrets, install/dry-run/hygiene, kernel-gen, daemons render/lifecycle, front-door/status/ui-lite smokes, update, governance/staging/filename checks), 6 `smoke-*` scripts (install-matrix, install, status-server-e2e, installer-wizard-pty, plus two `.ts` bun smokes for core-policy/health-monitor). All of these operate against a sandboxed `HOME`/temp dir and, where they touch model CLIs at all, use `--fake-keys`/`--skip-llm-cli` to remain deterministic and quota-free — `check-harness-plumbing.sh` states this explicitly ("deterministic harness plumbing smoke, not live runtime behavior... It can verify install/layout/preflight/coordinator and dispatch artifact plumbing without consuming Claude quota. Live Claude panes and real delegation results must be verified manually when Claude auth/quota is available," per AGENTS.md's own Verification section). The **quota-consuming counterparts** are `scripts/live-codex-e2e-isolated.sh` and `scripts/live-claude-e2e-isolated.sh`, named outside the `check-`/`smoke-` convention specifically because they drive real provider calls.

### 11. Current verification status (honest)

**[VERIFIED]** Chain of evidence, most recent first:

- `harness/metadata/migration-handoff-20260831.md` (§1, "当前结论" / Current conclusion): **"最后测试 FAIL，不是完整 E2E PASS"** ("the last test is FAIL, not a complete E2E PASS"). Product commit under test: `f463b861bf47bddff46cc2ce3de151dcd8d78992`. Entry point: locked backend's `POST /intake` via `tools/contract_smoke.py`, `rapid_smoke`, one submission, zero manual intervention. "HTTP 200 / intake CLI 0 / 193.239 秒仅表示 intake 成功" ("only means intake succeeded"). Intent passed round 1; Requirement passed after one built-in semantic repair (4 total Requirement model calls); **Planner decision was `generate`, and the DAG-generation model call was rejected by the provider interface.** Final state: `failed/planning_failed` — no SchedulerInput, no frozen execution bundle, no Scheduler, no worker, no report.
- §2 root cause (exact evidence quoted in the doc): the model-facing schema `planning/semantic/generation-0/plan_call/model_output.schema.json` has `$defs/operator_requirements/properties` containing `cpu_cores_min`, `memory_mb_min`, `gpu_required`, but its `required` array does **not** include them; the provider returned `HTTP 400 / invalid_json_schema` reporting `Missing 'cpu_cores_min'`, and no PlanIR was generated. Source of the defect: `harness/schemas/planning/plan-ir.semantic.structured.v2.schema.json`; the compatibility shim `harness/lib/intent_compiler.py::codex_compatible_schema` does not currently reconcile optional-property fields against this stricter provider-side schema requirement. The doc explicitly disclaims alternate explanations: **"不是 LLM 智力退化、旧 Requirement 输出、CPU 资源不足或服务容量错误"** ("not LLM capability degradation, stale Requirement output, insufficient CPU resources, or service capacity error") — "离线 JSON Schema 合法性检查没有覆盖 provider 的更窄约束" ("the offline JSON Schema validity check did not cover the provider's narrower constraint").
- `MIGRATION-CODEX-PROMPT-20260831.md` (the actual handoff prompt for the next agent) restates this and adds: **"本轮修复已提交...离线89项回归通过不等于provider/E2E成功"** ("this round's fixes are committed... 89 offline regressions passing does not equal provider/E2E success"). It explicitly forbids the next agent from resuming repairs without user authorization: "你不得擅自重试或修复" ("you must not retry or repair on your own authority").
- §4 of migration-handoff-20260831.md: "新机安装、认证、Linux 前端构建、唯一 backend readiness 和 E2E 均为 NOT_TESTED" — "new-machine install, auth, Linux frontend build, sole backend readiness, and E2E are all NOT_TESTED."

**What HAS been demonstrated (per these docs):** Intent Compiler and Requirement Compiler pipeline stages pass live, provider-backed calls (with one built-in semantic repair) against the exact original research prompt; hundreds of offline/source-level regression tests pass against the same code (`46 passed` Requirement-final, `43 passed` Planner/Scheduler regression, `13 passed` migration unittest, `410`/`412` broad regression counts referenced in the earlier stabilization log); schema/contract closure audits pass (173 assets / 145 JSON Schemas tracked); static repo-wide audits (AST parse, shell syntax, `git diff --check`) pass.

**What has NOT been demonstrated:** a complete unattended live E2E from prompt submission through Planner -> Scheduler -> worker -> final report. The last attempt at that specific claim failed at Planner-stage provider schema admission. All fixes committed after that failure are, by the docs' own framing, **source-only / offline-validated** — schema JSON validity, regression suites, static audits — and have **not been re-accepted by an online, live-provider E2E run**. The docs are unusually careful never to claim otherwise, repeatedly using phrasing like "does not establish... final E2E acceptance" and "not proof that all hard gates actually executed."

**[INFERRED]** This is consistent with (and a specific, dated instance of) the general AGENTS.md discipline against inferring PASS from partial or offline evidence, and against copying a green regression result onto an unexercised live-provider variant.

---

## Key references (file:line)

- `AGENTS.md:7-25` (three-layer strategy), `:67-84` (six states + anti-copy rule), `:86-99` (minimum journey evidence), `:105-119` (atomic-failure triage), `:141-155` (test execution rules), `:184-201` (worker quality gate).
- `tests/journeys/phase22/journey-test-plan.md:1-463` (mojibake Chinese; task overview table lines 29-42; J01 detail lines 44-79; J11-J25 mapping table lines 433-455; execution order line 463).
- `tests/platform/phase22/atomic_feature_matrix.json` (48,450 lines; `schema="phase22.atomic_feature_matrix.v1"`; `counts`, `l2_summary` [142 entries], `atomic_features` [1,502 entries], `review_policy`).
- `tests/platform/phase22/README.md:1-33` (L2 execution matrix, 3-class scheme, 142 L2s: 94/38/10).
- `harness/lib/evaluation_plan.py:1` (docstring), `:27` (`EvaluationPlanError`), `:69-98` (`load_evaluation_check_registry`), `:190-260` (`compile_evaluation_plan`).
- `harness/schemas/planning/evaluation-check-registry.v1.schema.json` (87 lines; `check_id`/`mode`/`applies_to`/`decision`/`deterministic`/`semantic`).
- `harness/lib/evaluation_budget.py:1-22` (module docstring + `_RISK_BUDGETS` capped at 1), `:175-256` (`apply_evaluation_budget`), `:259-278` (`policy_allows_none`).
- `harness/tools/elastic_planner_adapter.py:29-38` (`_trusted_test_policy`, the `SOLAR_TEST_MODE` gate).
- `harness/lib/contract_gate_executor.py:239-270` (`test_policy_mode == "rapid_smoke"` handling).
- `harness/lib/scheduler_input.py:103` (`test_policy` in frozen-field list), `:884` (test_policy mismatch check).
- `harness/metadata/NEW-MACHINE-START-HERE.md:62-64` (rapid_smoke trusted-env quote).
- `harness/metadata/migration-handoff-20260830.md:148-180` (empty-discovery historical defect, rapid_smoke_bypass quote).
- `harness/metadata/migration-handoff-20260831.md:1-30` (last E2E FAIL, Planner schema root cause, offline-vs-E2E distinction).
- `harness/metadata/MIGRATION-CODEX-PROMPT-20260831.md:20-22` (handoff framing of the same failure; "89 offline regressions != E2E success").
- `harness/lib/capability_activation_proof.py:1-12` (four checks + boundary docstring), `:777-802` (`proof_negative_control`), `:805-829` (rendered report + boundary text), `:832-868` (`main`, 13 proofs).
- `harness/lib/activation_proof_vnext.py:1-38` (coverage-extension docstring; read-only over base module).
- `harness/lib/capability_effects.py:1-10` (use->effect docstring), `:49-84` (`_terms_for_capability`, `_evidence_matches`), `:77-84` (`_verdict_from`).
- `harness/lib/agent_arena_benchmark.py:1-8` (evidence-first docstring), `:24-46` (`PUBLIC_BENCHMARKS` registry entries, env-var-gated adapters).
- `harness/lib/capability_fusion_benchmark.py:1-7` (docstring), `:33-40` (`WEIGHTS`).
- `harness/lib/capability_certification_suite.py:1-13` (docstring), `:30-38` (`DIMENSIONS`).
- `harness/solar-harness.sh:4312-4390,4487-4488` (CLI wiring of the four benchmark/proof scripts).
- `scripts/check-harness-plumbing.sh:1-19` ("deterministic... not live runtime behavior", `--fake-keys --skip-llm-cli`).
- `docs/integrations/autosci/phase-22-journey-test-report.md:1-100+` (2026-08-14 addendum; L2 status counts 30 PASS / 86 PASS_WITH_KNOWN_LIMITATIONS / 0 FAIL / 0 ENVIRONMENT_BLOCKED / 25 NOT_AVAILABLE / 1 NOT_TESTED, of 142 total — a snapshot **predating** the 2026-08-30/31 Planner-schema-failure findings above, so it must not be read as the current status).

---

## Notable quotes (verbatim)

1. AGENTS.md: "Never copy a green result to file formats, platforms, providers, failure branches, or other variants that the journey did not use."
2. AGENTS.md: "Do not pass a journey merely because a process started or a file exists."
3. `atomic_feature_matrix.json.review_policy.test_policy`: "A test record or L2 representative probe is not copied to every atomic child. Only assertion-level defensible selectors are bound."
4. `tests/platform/phase22/README.md`: "A passing validator means the design inventory is structurally complete and traceable; it does not mean the underlying L2 capabilities pass."
5. `NEW-MACHINE-START-HERE.md` (decoded): "Rapid smoke injects a frozen test_policy through the trusted environment SOLAR_TEST_MODE=rapid_smoke; it is not authorized by keywords in the user prompt or operator output... one rapid receipt PASS did not prevent an empty discovery handoff, so a receipt alone cannot claim all hard gates actually executed successfully."
6. `migration-handoff-20260830.md`: "The rapid receipt used rapid_smoke_bypass; it is not proof that all hard gates actually executed. Ingestion rejected the empty artifact as it should."
7. `capability_activation_proof.py`: "Boundary: no benchmark can prove an LLM's private reasoning. We prove the worker-visible prompt/context, runtime calls, and produced artifacts."
8. `agent_arena_benchmark.py`: "This runner is intentionally evidence-first. It does not claim Solar-Harness is on an external leaderboard unless the public benchmark adapter is actually configured and run."
9. `migration-handoff-20260831.md`: "最后测试 FAIL，不是完整 E2E PASS" ("the last test is FAIL, not a complete E2E PASS").
10. `MIGRATION-CODEX-PROMPT-20260831.md`: "离线89项回归通过不等于provider/E2E成功" ("89 offline regressions passing does not equal provider/E2E success").

---

## Open questions

1. `harness/lib/capability_effects.py::scan_effect()` body was only read up to line ~90; the full correlation/telemetry-writing logic (how it calls `resource_telemetry.record_usage`) should be read in full for a complete use->effect trace if the report needs implementation-level precision beyond "connects three artifacts."
2. `activation_proof_vnext.py` targets a "new S03 broker" not otherwise covered by this pass — worth checking whether that broker is claim/evidence-schema territory (the other agent's scope) or genuinely benchmark/verification territory.
3. Whether `agent_arena_benchmark.py`'s public-benchmark adapters (SWE-bench, Terminal-Bench, OSWorld, GAIA, WebArena, tau-bench) have ever actually been run with their env vars set is not evidenced anywhere I found — the code supports it, but no run artifact/report was located confirming an actual external-leaderboard submission.
4. The `phase-22-journey-test-report.md` (2026-08-14, 142-L2 snapshot: 30 PASS / 86 PASS_WITH_KNOWN_LIMITATIONS / 25 NOT_AVAILABLE / 1 NOT_TESTED / 0 FAIL) predates the Planner-schema-admission failure discovered in the 2026-08-29/30/31 metadata logs. It is unclear whether that report has been (or should be) revised downward given the later-discovered E2E failure — this repo area's progress-log (`docs/integrations/autosci/phase-22-progress-log.md`, 4000+ lines) likely has the reconciling entry but was not fully read end-to-end in this pass; only its tail (dated 2026-08-27) was sampled.
5. `harness/schemas/planning/evaluation-plan.v1.schema.json` and `evaluation-plan-validation.v1.schema.json` (98 and 17 lines) were located but not fully rendered/quoted field-by-field in this report — worth a follow-up read if the formal report needs the exact evaluation-plan output shape.
