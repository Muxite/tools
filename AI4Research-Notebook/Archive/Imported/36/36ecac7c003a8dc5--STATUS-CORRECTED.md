# ⚠ CORRECTED STATUS — supersedes earlier claims in these notes

**Verified directly against `harness/metadata/pre-scheduler-stabilization-log-20260829.md`
(863 lines, append-only, entries through 2026-09-03) on 2026-09-10.**

## What I got wrong

Notes 04, 08, and 09 — and my earlier statements — said:

> "The last recorded full E2E failed at Planner model-output schema admission
> and never reached the Scheduler. Later fixes are source-only, offline
> validated, never re-accepted online. Do not claim end-to-end passes."

**That is wrong, and it is wrong in an important way.** It was derived from
`migration-handoff-20260831.md`, which is a **mid-arc snapshot**, not the end of
the story. The stabilization log continues for another ~230 lines past that
point, through 2026-09-03.

Two agents independently repeated my error because they were pointed at the
handoff docs. A third agent resolved the append-only timeline properly and
caught it. **Lesson for the report: in an append-only log, the last entry wins
— always read to the end.**

## What is actually true

### The system achieved a full end-to-end pass on 2026-09-03

Sprint `sprint-20260903-072109-intent-conduct-an-end-to-end-system-cf3739f6`,
driven by a real user prompt plus six attachments:

- **15/15 nodes passed**
- `run_status=completed`, projection `passed/scheduler_complete`
- `all_nodes_passed=true`, `all_required_gates_passed=true`
- Closure closed
- final runtime revision **530**

The log's own words (line 863, translated from Chinese):

> "The production sprint `sprint-20260903-072109-...`, driven by the repaired
> code, remains the highest-level acceptable evidence: 15/15 nodes passed,
> Closure closed, `all_nodes_passed=true`, `all_required_gates_passed=true`."

### The honest caveats — state these, don't bury them

This was **not** a pristine untouched run start to finish:

1. **A mid-run intervention occurred.** The run deadlocked at
   `survey-synthesis` with a repeating `missing_deepresearch_quality_gate`
   block. A permanent fix was written, deployed, and the Coordinator was
   reloaded (**PID 779798 → 828727**). The next normal Scheduler tick then
   reused the *original* worker artifacts, the *original* independent PASS
   sidecar, and the *original* frozen plan to advance the node
   `reviewing → passed` (revision 493 → 495).
   The log is explicit that no graph was hand-written, no gate fabricated, no
   model re-invoked, and Solar was not bypassed.
2. **At that moment the log refused to claim the remaining three nodes had
   passed.** The 15/15 figure comes from the later completion at revision 530.
3. **The Session Timeline projection file for that run was manually
   compacted** — but deterministically, from the authoritative gate ledger's
   terminal `status_transition` records, preserving record IDs/times/nodes, and
   tagged `source=gate_ledger_terminal_projection`. Originals were backed up
   with SHA-256 recorded. No execution conclusions were manufactured.
4. **Pre-release regression was NOT green**: `606 passed / 34 failed /
   8 skipped in 992.68s`. The failures were **deliberately retained as known
   regression debt**, itemized by cause (stale report/publication fixtures,
   old Scheduler/Dispatcher fixtures rejected by current frozen-PlanIR
   preflight, composition-registry drift, Windows-path fixtures). The log
   explicitly refuses to relax product gates or fabricate artifacts to reach
   green.

### The deadlock itself is the best story in the whole log

The root cause is *thematically perfect* for this report:

The frozen node declared only
`evaluation_binding.deterministic_gate_ids=[check.scientific.scientific_report_plan.v1]`,
and the frozen EvaluationPlan contained **no** DeepResearch artifact gate. But
the completion-confirmation code **re-inferred** semantics at runtime from
capability/artifact/path text — and the node's `write_scope` contained
`final_report_plan.json`, which a `final_report` substring rule misread as a
final DeepResearch report. So it demanded a gate that the frozen contract never
required, and blocked a product that had already passed its actual frozen gate.

The diagnosis names the boundary exactly:

> "This is a conflict between the frozen contract and the Scheduler's
> post-hoc semantic inference — not a Planner output, model call, schema
> validation, or worker failure."

And the fix is a principle, not a patch:

> "The Scheduler may only execute gate IDs already frozen in the
> EvaluationPlan; it must not re-infer semantics from runtime filenames or
> paths. If a node class genuinely requires a DeepResearch gate, the Elastic
> Planner must add it to the EvaluationPlan **before freezing**, and a
> pre-freeze validator must reject its absence — rather than the Scheduler
> injecting it after the fact."

**This is the freeze thesis defended against its own implementation.** The
system's most serious late-stage bug was a component quietly re-deriving
meaning after the contract was sealed. Use this as the closing example.

## How to state status in the report

> The architecture is built and has demonstrated a complete 15-node end-to-end
> research run (2026-09-03) with all required gates passed. That run required a
> mid-run fix and coordinator reload; the pre-release regression suite retains
> 34 known failures that the maintainers deliberately declined to hide. The
> system is Release Candidate maturity — demonstrated, not yet routinely
> reproducible unattended.

That sentence is defensible to the supervising SWE and fair to the project.

## Files needing this correction applied

- `04-gotchas.md` #15 — rewrite
- `08-workflow-end-to-end.md` "What to be careful claiming" §1 — rewrite
- `09-report-presentation-kit.md` accuracy guardrails + slide 14 — rewrite
