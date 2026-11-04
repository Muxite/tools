---
type: example
tags: [process]
---

# [module] cc.evaluator: run a precondition against a state and answer pass, fail or defer

*Reference, not for review: an example filled from the [issue template](issue-template.md), section B, pending Xiaoyang's template.*

**Component:** [Precondition evaluator](../components/run.md#precondition-evaluator)  ·  **Build step:** B1  ·  **Size:** S **Schemas it depends on (signed):** [`cc.declaration.v1`](../schemas/declaration.md) (`needs.when`), [`cc.run_contract.v1`](../schemas/run-contract.md) (Binding `predicates[]`), [`cc.observation.v1`](../schemas/observation.md) (`predicates[]`) **Blocked by:** sign-off of `cc.declaration.v1`, `cc.run_contract.v1` and `cc.observation.v1`

## Why
Each Default DAG step must re-check its preconditions on fresh state before it runs (B1), and the planner must check the same ones at planning (B2). One evaluator used by both is what stops the two from disagreeing.

## Work order (not a Declaration)

```yaml
identity:
  name: cc.evaluator
  code: cc/evaluator.py:evaluate
  summary: Evaluate one declared precondition against a state; answer pass, fail or defer.
ports:
  inputs:
    - {name: predicate, type: "cc.declaration.v1 needs.when[] entry"}
    - {name: state, type: "object: {inputs: {...}, observed_at: ISO 8601 time}"}
    - {name: now, type: "ISO 8601 time"}
  outputs:
    - {name: result, type: "string: pass | fail | defer"}
needs:
  signed_schemas: [cc.declaration.v1, cc.run_contract.v1, cc.observation.v1]
  issues_merged: []
  external: []
changes:
  writes: []            # pure: the caller records the result in the Observation
guarantees:
  checks:
    - {id: truth_table, verified_by: builder,
       description: "each of the 11 ops gives the right answer on a present value, one case per op"}
    - {id: unknown_never_passes, verified_by: builder,
       description: "a missing path gives defer, or fail when on_unknown is fail (the policy default, or the predicate ext override); never pass"}
    - {id: stale_is_unknown, verified_by: builder,
       description: "state older than max_age_s is treated as missing"}
    - {id: no_side_effects, verified_by: reviewer,
       description: "the state object is unchanged after the call; no I/O"}
    - {id: parity_with_planning, verified_by: reviewer,
       description: "the same predicate and state give the same answer called from dispatch and from a planning stub"}
estimate: half a day
```

## Out of scope
- Fetching state. The caller passes it in.
- Writing the Observation. The caller records the result.
- `state_source` (B2).

## For the coder
- Build only what the work order says. Do not edit anything under `schemas/`.
- Write a test for every `builder` check, named by its check id.
- Run them and paste the command and its output under "Evidence".
- A schema is wrong or unclear: stop and comment here.

## Evidence (coder fills in)

## Review (architect fills in)
- [ ] every `builder` check re-run and passes
- [ ] every `reviewer` check run and passes
- [ ] writes nothing outside `changes.writes`, and no field outside the schemas it names
- [ ] merged
