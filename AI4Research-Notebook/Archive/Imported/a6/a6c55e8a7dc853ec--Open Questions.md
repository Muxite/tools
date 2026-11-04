**What is still open, as of 2026-09-25.** Each has a default so none blocks M1. Settled questions are at the
end, with where they were settled.

## Open for M1 (decided in WP0 or by the room)

| Question | With | Default |
|---|---|---|
| `identity.code_id` (the decision notes) or `identity.carrier` + `body[].sha256` (the schema)? | Muk | **`carrier`**, as the schema and the layer 2 deck have it. The notes' name is a mismatch, not a second field |
| The JSON Schema's own description still says "Schema version 2.9" (lines 5 and 624); the text is v2.10b | — | fix in WP0 |
| The JSON and the text disagree field by field: 8 mismatches in M1-required fields, 16 more, and `judge`/`judged` inside the JSON (list in `team/SCHEMA-EXPLAINED.md` §8) | Muk | the JSON wins until WP0; fix the M1 fields first |
| Effect classes: the text lists four, the JSON enum has five (`read_only` added) | Muk | keep `read_only`, since `parse_txt` needs it; update the text |
| `changes.state {kind, scope, reset}` and optional `guarantees.test_aids` (proposed v2.11) | Muk | decided in WP0; see [[Layer 2 Presentation]] |
| Which agent-core line to pin to: jiuwenswarm pins `b6db2733` (09-20), not an ancestor of `e23806c1` | agent-core owners | decide before WP1 |
| Improve by depth or by breadth? | the room | no lean stated |
| Symphony's graph takes only skill, subagent and agent capsules (`orchestration/graph/build.py:161`); M1's `count_spaces` is a tool | Muk | Symphony indexes the M1 capsules without graphing them; the alternative is to make them skills (`team/M1-DESIGN.md` §8) |
| Symphony: a deterministic `plan()` path, a stable provider protocol, an admitted-only provider? | Symphony builders | ports first, Symphony later, so M1 does not wait |

## Open for later rungs

| Question | With | Default |
|---|---|---|
| Are team (Swarm) skills admissible? | supervisor, all | not in v1: their Leader decides roles at run time, which is planning |
| Generalist defaults? | pipeline, RSI | `generalist_fallback: on`, `authoring: propose` until M4, a cap per plan; binds only steps whose outputs all have deterministic or reference gates |
| Exploration quota for inactive capsules? | all | a small share of offers on steps that do not require certified capsules |
| Must evolution overlays (teammate experience, TTSE) pass the gate? | RSI, jiuwenswarm owners | pinned per sprint, or not loaded |
| Should RSI add a held-out split inside its loop? | RSI | optional: admission takes held-out checks from verification either way |
| Who owns the vocabulary? | Symphony | the capsule layer, seeded from Symphony's |
| Fail open or closed when state cannot be read? | each builder | closed: defer or block, stated per predicate |
| What false-pass ceiling counts toward certification? | verification | 0.05 until measured |
| What does a DEFER at dispatch do? | pipeline | wait up to `max_age_s`, then a fallback, then fail with a typed reason |
| Who owns the sandbox and composition screening? | verification, agent-core | the capsule layer; screening open |
| Who acts as librarian? | all, supervisor | capsule-layer code, with a named person for revocations |
| Fusion: when, and does "internals locked" become "contract locked"? | Muk | back-burnered for M1; see [[Fusion After Merge]] |

Also still open: the cost of certification per capsule; latency per step; MCP sandboxing; concurrent sprints with
different pins.

## What cannot be a capsule

Held open at Muk's request on 2026-09-23, and narrowed after the presentation. What is known
([[The Ceiling]], [[Post-Presentation Decisions]]):

- **Never a capsule:** the modules that control the workflow, the gates, and the planner and library that act on
  and verify capsules. A capsule may assess; it never decides.
- **The workflow can never be one, compositionally:** a composite is made only of capsules, the workflow contains
  gates and deciders, so it would need members that cannot be members.
- **Still open:** anything whose effects cannot be declared, and anything needing a run-time choice of *other*
  capabilities.

## Settled

| Question | Settled | Where |
|---|---|---|
| Does a capsule hold code? | **No, it points**, always; leaf xor composite, enforced | 2026-09-23, [[Post-Presentation Decisions]] |
| Who binds capsules to steps at M1? | **our planner-binder**: contract, hard filter, exactly one survivor; Symphony's `plan()` at M3 | 2026-09-24, [[Layer 2 Presentation]] |
| Build on the AI4Research harness? | **No.** M1 is a fresh build on openJiuwen; the harness is an archive | 2026-09-24 |
| Versions at M1 | a linked list; the tree stays in the data | 2026-09-24 |
| Lineage shape | a tree, not a chain | 2026-09-23 |
| M1 planner | **a pass-through**: the contract names the capsule; Symphony indexes it, and there is no selection in M1 | 2026-09-25, [[Directives]], [[Presentation 3 - Architect]] |

→ [[HANDOFF]]
