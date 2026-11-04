**One declared precondition, evaluated by the filter and dispatch with one evaluator, and tested against the capsule's own exit logic.** Long version: `tundle/ai4research/notes/PREDICATE-PARITY.md`. Diagram: `capsule-openjiuwen/merged/figures/parity.png`.

## Where it comes from

*Don't Offer What Can't Be Done* (Wix, 2608.01050, read in full). Its gate evaluates each skill's own exit conditions before the model chooses. A blocked skill could not have completed, which is sound by construction but only while the gate and the skill agree (predicate parity) and both read fresh state.

| Result | Number |
|---|---|
| description tokens removed by the gate after matching | 59.1% |
| with matching, against exposing all ten skills | 90.5% fewer |
| replay without the gate, blocked skill picked | 7.8% of 1,000 risk-enriched conversations |

## In the schema

- **Invariant 8**: eligibility is decided only by the declared predicates, through one evaluator, never by a heuristic. Choosing among eligible capsules stays a model's call.
- Whether a predicate can be evaluated at planning is **computed per step**: only if no upstream step declares an effect on its `state_source`. A block at planning holds only without a relevant state change (2608.01050 p3). Only such predicates are filtered, and only after their parity check passes.
- The Binding pins the evaluator and vocabulary versions, so filter and dispatch provably ran the same code.
- For a capsule whose body is a prompt, parity with the body is measured through a `report_exit` tool, not guaranteed by construction.
- Certification tests the body at the boundary, with state missing and with state stale.
- Any change to exit logic is a new revision and repeats the tests, because parity is a release invariant.
- `on_unavailable` is the explicit fail-open or fail-closed policy; the default is to block.
- The paper's three failure modes (predicate drift, state staleness, backend-contract drift) each map to a record.

## Why not a heuristic

In Contract2Tool, a keyword top-5 filter cut tokens but success fell from 0.775 to 0.620. The contract filter reached 0.980 at 2,528 tokens a task, against 26,172 for all tools. That was a synthetic registry with mocked execution.

## The lesson from AI4Research (archived)

The planner's filter never reads preconditions, and dispatch checks four fixed kinds: two predicate sets, so no parity. Four readers of one precondition gave four answers. That is why M1 has **one** predicate evaluator shared by the planner-binder and dispatch. → [[Position in the Pipeline]], [[Layer 2 Presentation]]
