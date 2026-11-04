**A lesson from the archive.** Since 2026-09-24 the AI4Research harness is archived and M1 is a fresh build on
openJiuwen, so these capsules are evidence for the design, not something to convert. Measured that day
(`merged/fleet_report.py`): **0 of 85** manifests satisfy M1; the carrier is `SkillSpec` for 83; no precondition has
`op`, `path` or `evaluable_at`; 85 have postconditions and none has an id; nothing has a hash.

**Today's AI4Research capsules are strict on shape and lenient on meaning. The schema keeps the instinct to declare
everything, and makes each declaration evaluable, owned and pinned.** Report §3. Code: AI4Research `b0bf165f9`.

## Today, counted

The registry holds 80 capsules (74 stable, 6 draft), with 85 manifests in two folders: `harness/config/capability-capsules/`
(46) and `harness/capability-capsules/` (39).

| Part | What code does with it today |
|---|---|
| preconditions | four kinds are checked at dispatch, for capability-native envelopes only (`operator_runtime.py:796-808`); **any other kind passes silently**; the filter never reads them (`capability_capsules.py:1220-1242`) |
| postconditions | file presence, after the node (`graph_node_dispatcher.py:8034`) |
| invariants | prose, **judged by a model** after the node, with no measured error (`static_execution_compiler.py:560-566`) |
| applicability | a negative keyword excludes a capsule, positive keywords score it (`capability_capsules.py:1041-1052`): keywords decide eligibility today |
| admission | only `stable` is admitted, but **a missing status counts as stable** (`capability_admission.py:14`); only the manifest file is hashed |
| the library | lookups resolve by bare id, so a change during planning aborts the freeze; a step nothing fits fails the plan |

## Record by record

| Record | Stricter or looser | Evidence |
|---|---|---|
| Declaration: inputs, outputs | stricter: one vocabulary, each output with its check | Contract2Tool |
| Declaration: preconditions | stricter: one evaluable predicate for filter and dispatch, with parity | Don't Offer |
| Declaration: invariants | stricter: a check with a runner, or marked `declared` | The Blind Curator, RelAIBuild |
| Declaration: effects | stricter: scope, reversibility, assurance | Cordis, SkillFuzz |
| Declaration: applicability | **looser, on purpose**: keywords dropped | a keyword filter cut success to 0.620 (Contract2Tool) |
| Declaration: dependencies | pinned by default; unpinned only with a written purpose | Skill Drift: 10% to 78% repair |
| Verdict | stricter: typed, runner hashes, measured judges; **looser**: provisional admission, only where outputs are checked downstream | Beyond Task Completion |
| Standing, Finding | new | The Blind Curator, SkillFuzz |
| Plan step, Binding | stricter: declared ports; exact hashes; fallbacks kept | GraSP, Execution lineage |
| the library | versioned, append-only, monotone; three clocks; the generalist | the 2026-09-15 report, AllocBench |

→ [[Capability Capsule]], [[Self-Improvement]]
