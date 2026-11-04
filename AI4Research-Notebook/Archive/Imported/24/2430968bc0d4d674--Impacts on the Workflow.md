**Answer (d) has been too narrow.** It covered RSI, verification and model routing and stopped. Muk,
2026-09-23: show impacts on the *other parts of the workflow* too, not just the teammate features. Those
are what a reviewer will probe.

## Half one: the teammate features

| Consumer | Reads from the Declaration | Attaches to | Activates |
|---|---|---|---|
| **Verifier** (largest) | `guarantees.checks[]`, `acceptance`, `ports.outputs[].check`, `changes.effects[]`; then Verdict and inherited suites | `EvaluationSuite` (`symphony/evaluation/suite.py:83`), `GoalEvaluator.should_spot_check()` (`harness/goal/evaluation.py:264`), `PackageReviewGate` | M1 for one check, M3 for suites, judges and quality |
| **RSI** | `identity.lineage`, Standing, the suites a parent passed | join CC's tree to RSI's by `builder_ref` (`RsiTreeNode.parent_id`). **CC exposes, RSI chooses** | M4 |
| **Model routing** | `needs.model`, `budget` | `ModelAllocator` (`agent_teams/models/allocator.py:88`), `IntelliRouterModelClient` — neither reads anything about the capability today | M3 |

The verifier gets the most space. The point to land: **every check needs a target, and today there is
none** — nothing on a carrier says what a capability is supposed to do, so a test can only be written
about a task. See [[Quality Not Just Correctness]].

## Half two: the rest of the workflow

The "Today" column is the **archived** AI4Research harness: it shows what each part does now, and M1 builds its
own planner-binder, freeze, runner and gate on openJiuwen rather than changing these files
([[Layer 2 Presentation]]). The impacts hold for whichever code fills each part.

| Workflow part | Today | Impact |
|---|---|---|
| Planner | hard filter `elastic_planner.py:4553-4648`; selection call `:4678-4760` reads full rows for every node | filter gains declared preconditions; the model reads only `summary` and `ports` |
| Freeze | `execution_authority.freeze_node`, `check_live_definitions` | pins `decl_hash`, Verdict **and every member's hash** — a merged capsule's freeze is larger |
| **Scheduler** | ready nodes topologically, ≤8 parallel, write-scope conflicts held back (`graph_scheduler.py:3203`), one lease per operator | shape unchanged, but **merging changes granularity**: a merged block is one node, holds one lease, takes the *union* of its members' write scopes. Better placement quality, **less parallelism inside the block** |
| Dispatch | four hard-coded precondition kinds (`operator_runtime.py:796-808`) | one evaluator on fresh state; live hash equals pinned hash |
| **Retry and fallback** | per node | a failure inside a merged block **retries the whole block** unless the block declares internal retry |
| Node gates / evaluation plan | compiled from requirement checks and manifest claims (`evaluation_plan.py:277-356`) | three parts with named writers; judges carry a Standing |
| **Findings and attribution** | per node | a gap inside a merged block is attributed to **the block, not the member** — attribution coarsens as blocks grow |
| Delivery and claims | invariants judged as prose | each claim keeps the invocation that produced it, plus a status |
| Gap handling | `UNSATISFIABLE_CAPSULE` fails the plan (`apo_plan_compiler.py:626`) | generalist fallback per the run contract, plus a gap Finding |
| Intake, intent, requirements | no capabilities today | **now supplied by capsules too** — [[Every Stage Applies Capabilities]] |

The three bolded rows are the honest costs of merging. They belong on the merge slides, not an appendix.

Related: [[Dependencies]], [[Overlap and Merge]], [[Position in the Pipeline]], [[Where It Attaches]].
