# Predicate parity, on one page

**Source:** Ashkenazi, Kloz, Ulianchenko (Wix), *Don't Offer What Can't Be Done: Deterministic Executability Gating
for LLM Skill Selection at Scale*, arXiv 2608.01050, 7 pp, read in full. **Used in:** `SCHEMA.md` v1.6, section
*Predicate parity* and invariant 8.

## The idea

- A skill can match the topic and still be impossible to run in the current state: the account lacks an
  entitlement, or the thing already exists.
- The paper's gate removes such a skill **before the model chooses** by evaluating the skill's **own exit
  conditions** against authoritative state. The paper calls this exit-condition inversion.
- Because the gate and the skill evaluate the **same predicate**, a blocked skill could not have completed. It is
  sound by construction, but only while **predicate parity** holds and both read fresh state.
- The guarantee is one-sided. Passing the gate does not mean the skill will succeed or that the user wants it.

## What it measured (Wix Helpmate, ten skills, 9 June to 10 July 2026)

| Result | Number | Caveat |
|---|---|---|
| description tokens removed by the gate after semantic matching | 59.1% (59.4% of pairs) | description tokens only, not billed cost or latency |
| with semantic matching, against exposing all ten skills | 90.5% fewer | same |
| replay without the gate: the model picked a blocked skill | 78 of 1,000 (7.8%) | risk-enriched cohort, replayed once, selection only |

## Keeping parity (the paper's release lifecycle, p5-6)

1. Change the skill's exit condition.
2. Change the gate predicate and the state it reads.
3. Run parity regression tests on boundary, missing-state and stale-state fixtures.
4. Serve only after they pass, with versioning and rollback.

Parity is a **release invariant**, not a one-time check. Three failure modes: predicate drift (gate and skill
disagree), state staleness, and backend-contract drift (a state field changes meaning).

## How the schema uses it

| Paper | Schema |
|---|---|
| gate predicate = the skill's exit condition | one declared precondition per condition, as data: check {path, operator, value}, `state_source` |
| gate before the model | the planner's filter evaluates it before any model sees the candidate, but only preconditions `evaluable_at: planning`, and only after their parity test passes; the rest wait for dispatch, because a frozen plan binds steps before upstream outputs exist |
| parity with the skill | filter and dispatch share one evaluator (inv 8). The body is tested against the declaration at certification (`precondition_parity[]`) |
| regression fixtures | boundary, missing state, stale state: required for certified |
| release invariant | any change to exit logic or a precondition is a new revision and repeats the tests |
| explicit unavailable-state policy | `on_unavailable`, block by default |
| three failure modes | run pin `exit` and `blocked[]`, certificate, `dependency_contract_violated` |
| not a substitute for access control | passing a precondition grants no right to any effect |

## Why not a heuristic filter

In Contract2Tool (2606.07904 Table V, p8), a keyword top-5 filter cut tokens from 26,172 to 4,482 a task, but success
fell from 0.775 to 0.620. Filtering on preconditions and effects exposed one tool, used 2,528 tokens, and succeeded
0.980 of the time. That was a synthetic 100-tool registry with mocked execution. A filter that guesses removes the
wrong things; a filter on the capsule's own declared predicate removes only what cannot run.

## Where AI4Research stands today (code, `b0bf165f9`)

- The planner's candidate filter uses its own compatibility logic and never reads preconditions (`elastic_planner.py:4553-4648`).
- Dispatch checks four fixed kinds against the task envelope (`capability_capsules.py:1220-1242`).
- These are two predicate sets, so there is no parity. The binding prompt carries every eligible candidate's full
  catalog row, and repeats it on repair (`elastic_planner.py:4678-4724`, `:4949`).
