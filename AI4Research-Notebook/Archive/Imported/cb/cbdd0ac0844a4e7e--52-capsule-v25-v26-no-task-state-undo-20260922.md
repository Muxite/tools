# 52: Capability Capsule schema v2.5 and v2.6 (2026-09-22, afternoon and evening)

Builds on note 51 (the v3 report and deck). Current: **schema v2.6**, report and deck v3 updated with it. Branch
`schema-v2.1-overnight` in `capsule-openjiuwen`; not pushed or merged. Muk's directives: `obby/Directives.md`.

## v2.5: a capsule holds no task; plan, schedule and real multiplicity

- **Invariant 12:** a Declaration describes a capability, never a use. No step, node, sprint, workflow, stage, task
  type, capsule to run with, or worker. `applies_to` removed. Today's manifests write uses in: task types in 85 of 85,
  `requires_after` naming a capsule in 42, a fixed position in 14 names or descriptions.
- **Plan and schedule (§4.3a):** the planner writes Plan steps and never names a capsule (as today); code expands and
  filters, models choose, the freeze writes one Binding per step; the workflow's scheduler keeps order, the cap,
  workers and retries; dispatch appends one invocation per run.
- **Multiplicity (§0.6):** `bound[]` with roles (primary, context, dependency), `invocations[]` per run (fan-out items,
  attempts, fallbacks), fan-out on the Plan step (`over`, `gather` all or best effort, a checked manifest),
  composite members keyed by role. Still six records.

## v2.6: authors answer for state and undo

- **Invariant 13:** the author answers for what the capability does; CC for checking the declaration against what it
  observes. **No numeric trust score** (Muk): a mismatch is a typed reason and a Standing move.
- `changes.effect_class` (pure, idempotent, compensable, irreversible), per-effect `idempotent`, `ws:` and `ext:`
  resources (external effects only compensate or emission).
- §4.5a: checks (idempotence run twice, each undo exercised, remote interface fingerprint at every dispatch),
  composition by class (retry, fan-out, exploration, inputs, approval), context taint (a revoked context capsule
  reaches every invocation it shared a context with).

## Where

| What | Where | Tundle copy |
|---|---|---|
| Schema v2.6 | `merged/SCHEMA.md` (§0.6, §4.3a, §4.5a) | `Capability Capsule Schema v2.6 - Muk.md` |
| Report (40 pages), new chapter 8 "Plan and schedule" | `kb/functions/5-plan-and-schedule.md`, built by `merged/build_report_v3.py` | `Capability Capsule Merged Report - Muk.docx` |
| Deck (34 core slides) | `merged/build_spec.py`: "A capsule holds no task", "How a plan is built and run", "Real multiplicity", "Authors declare state and undo" | `Capability Capsule Merged Deck - Muk.pptx` |
| Reviews (Sonnet) | `verify/V12-v25-v26-20260922.md` | |
