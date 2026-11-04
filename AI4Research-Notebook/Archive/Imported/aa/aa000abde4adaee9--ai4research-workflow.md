# The AI4Research workflow, and where CC sits in it

The AI4Research harness is at `stellven/AI4Research/harness/lib`, commit `b0bf165f9`. The new system moves this
workflow onto openJiuwen agent-core; the stages stay. The file:line references below are verified. **CC lives at three
stages, planning, freeze and dispatch**, plus the in-run gates that check outputs.

**Corrected 2026-09-23.** The previous sentence here -- that intake, intent and requirement compilation
never see capabilities -- is **superseded**. Every stage that does work picks, binds and runs a capsule;
the work of `intent -> IntentIR` is itself a capability. Planning, the freeze and dispatch remain special
only in that they are where CC's *control* acts. The workflow does not become a capsule: what is never a
capsule is anything that decides.

## The stages

A sprint is one accepted request, carried from compiled intent through planning, the freeze and execution to closure.
It owns one planning snapshot, one run contract and one ledger.

| Stage | What happens today (code) | What CC changes there |
|---|---|---|
| **Planning** | `compile_and_freeze_execution_bundle` (`elastic_planner.py:6888`) runs, in order: | the filter reads the **declared** requirements (see "Pick" below). Preconditions that can be read at planning enter it; the rest wait for dispatch. The binding model reads only `summary` and `ports`. If nothing fits, the step binds a generalist the run contract names, or records a gap |
| | 1. a hard filter, one candidate row per capsule, on artifact types, effects in both directions, network, trust class and verification presence (`_hard_capsule_candidate_row`, `:4553-4648`) | |
| | 2. a binding model that sees the full catalog row of each eligible capsule (`_capsule_selection_prompt`, `:4678-4724`) | |
| | 3. a fit review by a second model (`review_capsule_fit`, `:4980`), with one bounded repair; then failure with `UNSATISFIABLE_CAPSULE` (`apo_plan_compiler.py:626`) | |
| **Freeze** | `freeze_node` (`execution_authority.py:47-69`) copies each bound capsule's manifest, and the guard and resource capsules it requires, into the node's execution authority, and hashes it. Only `stable` capsules are admitted, and a missing status counts as stable (`capability_admission.py:14`). `check_live_definitions` (`:81-94`) aborts the sprint if a definition changed during planning | the Binding pins exact hashes (every body file, not only the manifest), the Verdict, the pinned overlays and the pre-approved fallbacks. It checks the sprint's snapshot, so an admission during planning no longer aborts the sprint |
| **Dispatch** | for capability-native envelopes, the capsule is resolved and the frozen authority is checked (`operator_runtime.py:796-815`). Four precondition kinds are checked against the task envelope (`capability_capsules.py:1220-1242`) | the **same declared predicates** as the filter are re-evaluated on fresh state, by the same evaluator (predicate parity). The live hash must equal the pinned one. A DEFER waits, then falls back, then fails with a typed reason |
| **In-run gates** | `output_present` postconditions are checked after the node (`graph_node_dispatcher.py:8034`). Each prose invariant becomes a `semantic_review` item judged by a model (`static_execution_compiler.py:560-566`). Frozen evaluation checks are enforced (`graph_node_dispatcher.py:11713`) | outputs are checked by the capsule's declared checks. Observed effects are compared with declared effects. Claims record their Binding and a status |

## How the plan is built and scheduled today (read 2026-09-22)

- **Plan.** A model writes the PlanIR (nodes, `depends_on`, `consumes`, `produces`) and may not name a capsule, model
  or operator (`elastic_planner.py:1328-1329`). It is given the capsules' port catalog (`capability_capsule_abis`,
  `:1431`). If no capsule chain implements a node, `CAPABILITY_IMPLEMENTATION_MISMATCH` goes back to the model as a
  defect (`:4137-4146`). So the DAG comes first, and supply reshapes it only through the repair loop.
- **Composition** expands a node into a chain of capsule steps, with ids `<parent>__<sha8>_cNN`
  (`_composition_support_node_id`, `:5914-5919`; `_generated_composition_task_graph_proposal`, `:5922`). A capsule
  appears at most once in a chain (`capsule_composition.py:340`, `:559`).
- **Schedule.** `graph_scheduler.ready_nodes` returns ready nodes in topological order (`:2179-2215`). At most 8 run
  in parallel (`graph_node_dispatcher.py:2391-2399`); nodes whose write scopes or effects conflict are held back
  (`graph_scheduler.py:3203`); one active lease per operator (`operator_runtime.py:504-515`). Retries follow the node's
  `failure_policy.max_attempts`, default 1 (`graph_node_dispatcher.py:5658-5662`).
- **Runs.** Each dispatch gets `dispatch_id = graph-{sid}-{node}-{ts}` (`graph_scheduler.py:4149`). Attempts are kept
  in a mutable state file, the last 20 (`task_lifecycle.py:54-56`). `approved_fallback_capsule_ids` is frozen
  (`elastic_planner.py:5886`) but read by no runtime file.
- **Multiplicity.** One primary capsule per node, plus guard, resource and verifier stages. The same capsule may serve
  several nodes. No fan-out: a `many` output is one run writing a directory (`elastic_planner.py:1366-1378`).
- **Uses written into capsules.** No manifest holds a step, node or sprint id. But all 85 hold
  `applicability.task_types`; 46 hold `composition.requires_after`, 42 of them naming another `cap.*`; 14 names or descriptions (11 names, 3 descriptions)
  fix a workflow position; `operator_compatibility.preferred` names workers. Registered workflows name capsules per
  stage (`allowed_capsules`, `config/workflows/*.workflow.json`).

## Why capabilities must be right here

A frozen plan chains steps. Each capability's output is the next node's input, so a wrong capability propagates its
error to every downstream node and into delivered claims. The frozen plan cannot swap a capsule mid-sprint, except to a
pre-approved fallback (`elastic_planner.py:5886-5888`).

## Today's capsule library, counted

- The registry has **80 capsules: 74 stable, 6 draft** (`config/capability-capsules.registry.yaml`).
- There are 85 manifests in two folders: `harness/config/capability-capsules/` (46) and `harness/capability-capsules/`
  (39).
- **A static default per logical operator** is the fallback when goal classification finds nothing
  (`capability_capsules.py:54-75`, `:1174-1179`).
- **Keywords decide eligibility today.** A negative keyword excludes a capsule, and positive keywords score it
  (`capability_capsules.py:1041-1052`).
