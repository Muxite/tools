# AI4Research pipeline: source walkthrough (2026-09-13/14)

Read in source at `b0bf165f9`. Written for whoever explains the system next; every claim
carries a `file:line`. Use with `REPORT.md` v0.3. Repos are read-only.

## 0. The spine

`request → intent → requirement → plan + capsule binding → FREEZE → dispatch (ticks) → operator
execution → gates → delivery`. Left of the freeze: models negotiate inside code-built fences.
Right: no model decides anything; models only execute inside capsules and judge inside gates.

## 1. Intent (`lib/intent_compiler.py`, `lib/intent_gateway.py`)

- 4 artifacts, 4 authors: IntentIR (model) → validation (code) → fidelity (second model) →
  acceptance (code). `run_pipeline` `:1368`.
- IntentIR = goals, outcomes{information|artifact|action}, constraints{category, statement,
  **expression**}, ambiguities{blocking}, conflicts{clarify|reject}, unknowns.
- Expression language: 21 operators with fixed arity/shape (`_OPERATOR_CONTRACTS` `:634`);
  no subset-of/universal quantifier; unexpressible relations stay literals.
- Model emits `source_quotes`; code binds to offsets (`_bind_exact_source_quotes` `:477`):
  not found / ambiguous → repairable errors. Reviewer quotes fail closed (`:555`).
- 7 validation kinds IV1-IV7 (`validate_intent` `:782`).
- Repair budget `SOLAR_INTENT_MAX_REPAIRS` default 1, cap 4. After budget, fidelity errors
  demoted to advisory warnings (`_demote_exhausted_fidelity_findings` `:1230`): "not a second
  admission authority".
- `decide_acceptance` `:1272`: failed | needs_clarification (blocking ambiguity/conflict) |
  accepted. `requirement_handoff` `:1508` re-checks id + SHA-256.

## 2. Requirement contract (`lib/requirement_compiler/`)

- Template trick: `make_template` (`template_contract.py:55`) bakes the Intent ids and the
  registered `bound_output` check ids into the **schema enums** sent to the model. Model
  fills only `values`: requirements, assumptions, discovery, selection_authority,
  delivery_manifest. Program owns everything else (contract v3, `requirement-semantic-contract.v3.json`).
- Requirement row: priority must/should/may, `acceptance{kind, required_values}`, `check`
  (registry id), `semantic_role` ∈ research_scope|process|delivery|outcome|resolution|constraint.
- `semantic_defects` (`semantic.py:47`): `SOURCE_CONSTRAINT_POLARITY_OR_CATEGORY_CHANGED`
  (byte-equal copy of Intent constraints), `SOURCE_COVERAGE_MISMATCH` (every Intent id
  referenced), named-file manifest checks, `UNKNOWN_CHECK`, role/coverage rule.
- Loop: ≤3 model calls, ≤1 structural repair; reviewer is advisory only
  (`admission_authority: deterministic_contract_validation`).
- Checks registry `config/evaluation-checks.v1.json`: 43 entries. ⚠ 2026-09-14, corrected
  from "all `mode: semantic`": 20 `mode: semantic` rubrics (`applies_to.kind: bound_output`)
  and 23 `mode: deterministic` Python gates (`applies_to.kind: artifact_type`, auto-applied,
  e.g. `evaluators.scientific.literature_discovery_gate:evaluate`).

## 3. Plan and capsule binding (`lib/elastic_planner.py`, `lib/apo_plan_compiler.py`)

- Catalog snapshot `build_planning_catalog_snapshot` `:616`: workflows, logical operators,
  capsule summaries (`_capsule_summaries` `:494`: task_types, consumes/produces, effects,
  verification, proof classes, trust_class, reasoning_class, preferred/forbidden ops),
  enabled physical operators; hashed.
- Decision: direct_response | exact_reuse | generate (`compile_planning_decision` `:829`).
- PlanIR: model lists nodes with `depends_on`; edges are that list. `validate_plan_ir`
  `:2696`: `DEPENDENCY_UNKNOWN`, `SELF_DEPENDENCY`, `GRAPH_CYCLE` (`:3136`),
  `ARTIFACT_DEPENDENCY_MISSING` (producer not an ancestor `:3251`), `REQUIREMENTS_UNCOVERED`,
  `VERIFIER_*`, `MULTIPLE_LLM_EVALUATOR_NODES`, workspace-read checks. One repair; second
  failure → `plan_acceptance failed`; sprint `elastic_planner_failed`.
- Candidate catalog `_hard_capsule_candidate_row` `:4553`, code only, 13 exclusion codes:
  I/O type mismatch, `MANDATORY_PROOF_CLASS_UNSATISFIABLE`, `REQUIRED/UNREQUESTED_*_EFFECT`
  (effects must match node request **both ways**), `NETWORK_*`, `VERIFICATION_CONTRACT_MISSING`,
  `IMPLEMENTATION_UNDECLARED`, `EXECUTION_TRUST_UNSATISFIED`.
- Selection `compile_capsule_selection` `:4727`: model picks only from eligible; code derives
  `dispatch_task_type`. `validate_capsule_selection` `:4815`: 8 codes. `review_capsule_fit`
  `:5685`: second model, **fail→warning** (advisory). One repair.
- Composition fallback `run_generated_composition_binding` `:5544`: chain capsules +
  registered adapters; `validate_capsule_bindings` `:6361` rejects
  `UNREGISTERED_ADAPTER_COERCION`.
- Node binding `:6270-6320`: `capability_capsule_id`, `proof_obligations`, `artifact_types`,
  `effect_union`, `approved_physical_operator_ids` copied from manifest, never from model.
- Physical plan `build_physical_plan_ir` (`apo_plan_compiler.py:1192`): frozen
  `execution_candidates` per node; exclusions `ROLE_MISMATCH`, `TASK_CLASS_MISMATCH`,
  `CAPSULE_FORBIDDEN`, `PROVIDER_UNAUTHENTICATED`, `RUNTIME_NOT_IDLE`, trust codes.
- Model-calling capsules at planning: visible only via `trust_class`, `reasoning_class`
  (`_capsule_reasoning_class` `:433`, deterministic is the fail-closed default; synthesis
  checks need a reasoning capsule), and physical enumeration.
- **No generalist fallback.** Node with no capsule → `UNSATISFIABLE_CAPSULE`
  (`apo_plan_compiler.py:624`) → plan fails. Nearest substitutes: `direct_response`
  (whole request), static-default coding capsules wrapping frontier CLI agents
  (`capability_capsules.py:1145-1180`, `static_default_fallback`), composition.
  `legacy_uncontracted` graphs are refused dispatch (`plan_validator.py:1528`).

## 4. Freeze (`compile_and_freeze_execution_bundle` `:6888`)

Order, each a fail point: evaluation budget → `test_policy` (`evaluation_budget.py:175`,
risk tier, 1 semantic-evaluator node, or rapid_smoke = 0) · capsule + physical plans ·
adapter validation · merge into graph · `plan_validator.validate_plan` + `stamp_plan_certificate`
("never a participation trophy") · `compile_evaluation_plan` (`evaluation_plan.py:198`) +
validation · `compile_scheduler_input` `:6662` (contains `test_policy` `:6842`, per node
`evaluation_binding`/`evaluator_gate`/`evaluation_policy` `:6802-6808`, `contract_sha256`,
`execution_authority`) · `check_live_definitions` (`execution_authority.py:81`,
`CAPSULE_CHANGED_DURING_PLANNING`) · `run_contract.frozen.v2` with every ref + `plan_certificate`,
self-sealed `contract_sha256` (`:7260-7345`) · `plan_acceptance accepted, runtime_handoff_allowed`.

Hash = SHA-256 over canonical JSON (`intent_compiler.py:62-67`).
`verify_frozen_execution_chain` `:7748-8052`: 14 checks; recomputes 3 (composition validation,
evaluation-plan validation, SchedulerInput compile), hash-compares the rest. Test
`tests/harness/test_elastic_planner.py:4697-4718` (priority=999, edited criteria, edited rationale).

Freeze failure: `plan_acceptance failed` + reasons, partial artifacts kept, failure receipt,
sprint `failed/elastic_planner_failed` (`elastic_planner_runtime.py:262-310`). No re-plan;
new request.

## 5. Dispatch (`lib/graph_node_dispatcher.py`, `lib/graph_scheduler.py`)

Interleaved, tick-based; not schedule-all-then-run. Tick (`_dispatch_ready_unlocked` `:16772`):
graph lock → refusals (`runtime_handoff_forbidden`, contract guard, validator guard) →
`_reconcile_existing_dispatches` `:5774` (consume result/eval sidecars, reopen recovered,
terminalise blocked) → approval gate → terminal barrier (publish + close) → workers →
`enqueue_ready` `:4100` → `assign_ready` `:3131` (`verify_runtime_projection`, Kahn ready set,
priority, `write_scope_conflict` `:2237` / `effect_conflict`, `max_parallel` 8) →
`node_admission_status` `:2103` → lease → queue item → `drain_queue` → envelope in
`run/pm-inbox/<op>/<dispatch_id>/` → save ledger (revision++) → status sync.

Statuses `:48-53`: ready {pending, queued, blocked, worker_blocked, failed_review}; active
{assigned, dispatched, in_progress, running, reviewing}; terminal {passed, failed, skipped,
cancelled, skipped_parent_passed}; `needs_human_review`.
Failure: eval FAIL → `failed_review` (ready) → repair with findings ≤ `max_repair_attempts`
→ exhausted: `on_failure_exhausted` stop|fail_run → `terminalize_dependency_blocked_nodes`
`:3979` marks dependents `skipped`; reopenable only if scheduler-authored.
Passed nodes never regress (`mark_node_result` `:3736`).

## 6. Operator execution (between ticks)

- Registry path (`tools/research_operator_registry_adapter.py`): `_verified_dispatch_authority`
  `:268` re-verifies graph projection, layout, operator in frozen candidates, exact
  `artifact_contract/routes/capsule_binding/write_scope`, routes inside workdir or exact input
  bindings; `_validated_binding` `:357` allowlists registry + node kind + implementation id.
  `run_physical_operator` (`lib/physical_operator_worker.py:54`) always writes a typed
  `result.json`. Model calls via `RegistryResearchModelService` (`services/registry_research.py`)
  leave request/schema/response/events + hashes per invocation.
- CLI path (`lib/multi_task_runner.py`): tmux pane, worktree `.worktrees/<slot>`, dispatch
  text + DeepResearch hard rules (`dispatch_prompt_injector.py`), exit code → `result.json`.
  No observation of commands/network. Trust `fixture_or_adapter_only`.

## 7. Gates and delivery

`contract_gate_executor.py`: `deterministic_command` exit 0 → PASS, nonzero → FAIL content,
timeout → FAIL infrastructure (cannot flip a policy-passed node). `llm_eval` → separate
evaluator actor. `VerificationGate.check_code_task` (`verification_gate.py:13`): patch + test
evidence + verifier decision + writer≠verifier. Scientific gates in `evaluators/scientific/`.
Terminal barrier publishes outputs byte-identical to workdir; sprint closes.

## 8. Claims (unchanged from REPORT.md §3.4)

Regex `operators.py:1183`; testable `:1224`; section-hash spans `:886`; verdict table
`delivery.py:145-166`; substring `:137`; span re-verify `:114-132` dropped silently;
`precise_source_span_resolved` written `:201`, never gated; gate `claim_verdict_gate.py:29-69`.

## 9. Capsule report fit (applied 2026-09-13, backup `versions/Report rev4 …`)

Added to the capsule report: binding-layer paragraph (§3), adapter crossing sentence, runtime
admission gate wording, §2.7 novelty sharpened (declared-vs-requested exists; declared-vs-observed
does not), §4.8 corrected (Stage 0 + most of Stage 3 exist; Stage 2 is a planner model; Stage 1
absent), §4.12 item 1, Table 3 rows Trust class + Reasoning class.
Frictions still open for the design: `capsule_id@version` (live-definition check vs changing
library); gap records (today a gap fails the plan at freeze); protected-path deny list in the
hard filter; no effect observation point; advisory reviewer circularity for rubric suites.
Suggested order: versioning → gap_record.v1 → EFFECT_ESCALATION deny list → suite runner →
sandbox access log.
