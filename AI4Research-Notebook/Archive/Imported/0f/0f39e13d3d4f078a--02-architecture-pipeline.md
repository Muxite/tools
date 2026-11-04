# 02 — Architecture & The Real Pipeline

> Source: `harness/metadata/NEW-MACHINE-START-HERE.md` (checked 2026-08-31) plus
> direct inspection of `harness/lib/`. Marked [repo-claim] where I did not run it.

## ⚠ The single most important fact

The root `README.md` describes a pipeline of
`request_envelope → requirement_ir → prd.md + Contracts.yaml + task_graph.json`.

**That is the HISTORICAL compatibility chain. It is not the current path.**
The README says so itself, in a banner at the very top. Agents that skim the
README and implement against PRD/Contracts/task_graph will be building on a
dead architecture.

## The current default ("formal") path

```
GUI / CLI
  → Intent Compiler
    → Requirement Compiler
      → Elastic Planner
        → frozen SchedulerInput
          → Scheduler
            → Dispatcher
              → Operators / Gates
                → final delivery
```

| Stage | Real entrypoint | In → Out |
|---|---|---|
| GUI/CLI intake | `harness/lib/symphony/status-server.py`, `harness/solar-harness.sh` | user request + attachment refs → intent request; returns session/intake status |
| Intent Compiler | `harness/lib/intent_gateway.py` → `intent_compiler.run_pipeline` | normalized input → IntentIR, validation, independent fidelity, acceptance. **On failure or clarification-needed, it must not continue.** |
| Requirement Compiler | `harness/lib/requirement_compiler/semantic.py` + `evaluator.py` | accepted IntentIR → LLM values + independent second-model semantic review. ⚠ Budget corrected 2026-09-10: the docs say "1 structural + 1 semantic repair, ≤5 calls" (split counters, blocking review, commit `f463b861b`), but **current HEAD** merged them back to **one shared counter, 3-call ceiling, advisory-only review** (commit `5ade9d9f3`). Code and tests agree; `semantic-retrieval-contract.md` is stale. |
| Planner entry | `harness/lib/intent_consumer.py` → `harness/tools/elastic_planner_adapter.py` | accepted RequirementIR → semantic/execution bundle. **The adapter itself writes no lifecycle state.** |
| Elastic Planner | `harness/lib/elastic_planner.py::run_elastic_planning_request` | LLM decision, PlanIR, fidelity + binding review; deterministic validation/acceptance; bounded repairs |
| Execution contract compile | `elastic_planner.compile_and_freeze_execution_bundle` | accepted semantic plan → capsule/physical/evaluation plans, SchedulerInput, frozen run contract |
| Scheduler | `harness/lib/scheduler_input.py`, `multi_task_runner.py`, `graph_scheduler.py` | validated frozen bundle → runtime graph projection + separate mutable `task_graph_state`; ticks by dependency |
| Dispatcher | `harness/lib/graph_node_dispatcher.py`, `operator_runtime.py` | ready node + contract/lease → operator request, submit/accept/result evidence. **A submit receipt is not proof of successful execution.** |
| Operators & gates | `harness/plugins/autosci/`, `harness/evaluators/scientific/` | declared artifact routes → domain evidence; verdicts per bound evaluator/test_policy |
| Delivery | selected report-plan / report-draft operators + Scheduler/Coordinator closeout | research evidence → report plan → structured report + `report.md`. Must check topic relevance, evidence, and title. |

## Rules that fall out of this design

These are stated as hard constraints [repo-claim]:

1. **Even simple queries go through Intent → Requirement → Planner.** The
   Planner may choose `direct_response`, in which case no Scheduler/worker
   starts. Do **not** hand-build a multi-node DAG just to answer something
   simple.
2. **Complex queries cannot bypass the compile chain** by carrying an epic tag.
3. **The Elastic Planner freezes internally.** Do not also call
   `static_execution_compiler.compile_bundle` — that would be a second
   authoritative compile.
4. **Legacy mode exists but is off-limits for acceptance.**
   `SOLAR_INTAKE_COMPAT_MODE=legacy` keeps the old path alive; do not enable it
   when validating a migration.
5. **Compile-time semantic review ≠ runtime bundled evaluator.** Different
   boundaries, don't conflate them.
6. **Capability selection is the Planner's binding/composition result**, not an
   architecture step the user hand-writes. Registry entry point is
   `harness/config/capability-capsules.registry.yaml`, pointing at concrete
   capsules, with `logical-operators.json` and `physical-operators.json`
   alongside. 68 registered manifests, all in git. **Never scan the directory
   and auto-activate an unregistered capsule.**

## `SOLAR_TEST_MODE=rapid_smoke`

Injects a frozen `test_policy` via a **trusted environment variable** — never
via a keyword in a user prompt or in operator output. It reduces evaluation
cost. It does **not** prove scientific quality: there is a recorded case where
a rapid receipt returned PASS and still handed off an empty discovery. Don't
conclude "all hard gates ran" from a receipt alone.

## Schema / contract locations

Executable JSON Schema dirs:
- `harness/schemas/compiler/` — Intent + Requirement
- `harness/schemas/planning/` — Planner + Scheduler
- `harness/schemas/evidence/` — Scientific Evidence ABI

**Not every stage has its own JSON Schema.** Some boundaries are enforced by
code, some by templates. Key ones:

| Boundary | Authority | Type |
|---|---|---|
| raw request / `input.json` | `intent_compiler.py::normalize_input` | code normalization + design examples — **not** a JSON Schema |
| `intent_ir.json` | `compiler/intent-ir.v3.schema.json`; model body `intent-ir.semantic.v1.schema.json` | JSON Schema + source/reference checks |
| Intent validation/fidelity/acceptance | `intent-validation.v1`, `intent-fidelity.review.v1`, `intent-fidelity.v1`, `intent-acceptance.v1` | separate structural / semantic / admission contracts |
| `requirement_ir.json` v2 | `requirement-semantics.v2.schema.json` + `evaluator.py`; envelope template in `harness/metadata/3-requirements compiler output/` | template + semantic_contract; constraint AST preserved exactly |
| Requirement shared template / review | `requirement-semantic-contract.v2.json`, `requirement-semantic-review.v2.schema.json` | v1 historical contracts do **not** cover this |
| Retrieval contract | `retrieval-contract.v1.schema.json` | Planner refs it via `retrieval_contract_ref`; Scheduler freezes it. **Discovery must not guess topic from the objective.** |
| plan_ir / validation / fidelity / binding / acceptance | `plan-ir.v2`, `plan-validation.v2`, `plan-fidelity.v1`, `binding-trace.v2`, `plan-acceptance.v1` | model semantic body separated from mechanical envelope |
| capsule / physical / evaluation plans | `capsule-plan.v1`, `physical-plan.v2`, `evaluation-check-registry.v1`, `evaluation-plan.v1`, `evaluation-plan-validation.v1` | |
| scheduler_input / frozen contract | `scheduler-input.v1`, `run-contract-frozen.v2` | immutable execution authority; full-chain hash verified before projection |
| runtime projection / task_graph_state | `scheduler_input.py::verify_runtime_projection`, `graph_scheduler.py` | code-enforced. `harness/schemas/task-graph-state.schema.json` exists but was **not observed being loaded on this path** — do not claim its field constraints are enforced. |
| dispatch / lease / worker envelope | `graph_node_dispatcher.py`, `operator_runtime.py`, `tools/operatord.py` | code protocol. The stage-7/8 envelopes in `metadata/` are **design examples**, not enforced schemas. |
| Discovery → ingestion → methods/claims | `evidence/literature_discovery.v1`, `research_paper.v1`, `research_method.v1`, `research_claims.v1`, `claim_verdict.v1` | current Scientific Evidence ABI |
| report plan / report | `scientific_report_plan.v1`, `scientific_report.v1` | different schemas. Markdown is the human deliverable and does **not** replace structured evidence. |

Full schema file hash manifest: `harness/metadata/migration-closure-20260830.json`.

## Operator / dispatch model (from prior investigation)

- **Physical operators** — a fleet with role-based dispatch.
- **Logical operators** — capability-based routing; a binding router maps
  logical → physical.
- **Backend decoupling** — Claude vs Codex is abstracted; provider swap partly
  via `ANTHROPIC_BASE_URL` override.
- **`operatord` daemon** — file-inbox dispatch model. The `operator-inbox`
  filesystem queue is the language-agnostic IPC seam (and the precedent for
  `codex-bridge`'s TS↔Python file-based coordination).
- **Task envelopes + leases** — submission and lease management guard
  concurrency and write scope.
- **tmux panes** — pane lease system renders terminal UI; `pane-lease.sh`,
  `pane-launcher.sh`.

## Runtime selector: claude | codex

`harness/solar-harness.sh` reads `SOLAR_PANE_RUNTIME` (env wins, else the
dashboard-persisted config key `runtime`, else `claude`). Choosing `codex`
routes the whole DAG surface toward OpenAI by default —
`SOLAR_PM_DEFAULT_PROVIDERS`, `SOLAR_MULTI_TASK_DEFAULT_PROVIDERS` — and
supplies `--search` plus `model_reasoning_effort` flags from config keys
`codex.search` / `codex.effort`. [verified in source]

There's an instructive comment there: without `--search`, codex panes launch
with no web search and **research stalls on the human-search gate**. That class
of "config default silently disables a stage" bug is common in this repo.
