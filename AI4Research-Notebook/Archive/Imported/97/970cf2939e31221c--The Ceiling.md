**What can never be a capsule.** Recorded 2026-09-23, reconciling two of Muk's statements: *"things that
judge and verify cannot be capsules, ever"*, and *"why is faithfulness in intent compilation ruled out?
it doesn't make a decision."*

## The rule

> **A capsule may produce an assessment. A capsule may never be the thing that decides.**

Faithfulness checking the IntentIR emits an assessment; the **gate** decides. So faithfulness is a
capsule and the gate is not. `cap.research-claim-verify` — verifying a scientific claim for the
researcher — is domain work that assesses and decides nothing, so it stays legal.

Muk's ruling on where the rule cuts: **judging the system is barred; domain work is not.**

## It needs no new concept — write access already enforces it

Protected components (§4.16.4, "Never grading itself"): **no capsule may write to the gate, the suites,
the logs admission reads, or the record stores.** A faithfulness capsule emits a Finding; it cannot write
a Verdict or move a Standing. That single rule does all the work, and it is checkable where "is this
judging?" is not.

| Supplied by a capsule | Never a capsule |
|---|---|
| **The work of a stage.** `intent → IntentIR` — input, output, declarable effects, checkable postcondition | **Anything that decides**: the gate's enforcement, admission, the librarian's Standing moves |
| **Assessments**, including of our own artifacts — faithfulness, scoring, domain verification. They emit Findings | **Anything that plans, freezes, admits, schedules or judges capsules** (§4.10's ceiling): the planner's filter and binding, the freeze, dispatch |
| A capsule also **carries and declares** its own verification — checks, acceptance, suites — which is what makes non-deterministic work governable | **The gate's rules and suites** (§4.16.4): never changed by the system; people release new versions and each Verdict records its `policy_epoch` |

## The structural ceiling

A capsule never decides **at run time** which other capabilities to involve. Two structural exceptions
are not run-time choices: a pinned `capsule` dependency, and a composite's `members`.

## The worked example

In `intent → IntentIR → faithfulness → gate`, the **first three are capsules and the gate is the
boundary, not a member**. The merge candidate is `intent → IntentIR → faithfulness`, and the gate then
evaluates that block exactly as it evaluates any node. Drawn this way, the gate sitting visibly outside
the merged block is the clearest single picture of the rule.

## Argued compositionally (after the presentation, 2026-09-23)

A composite is made of capsules and nothing else can be a member. Gates and deciders can never be capsules, or
RSI would be editing its own guards and checks. The workflow contains gates and deciders, so it would need
members that cannot be members. **It is not that the workflow is too big; it cannot be composed at all.**
Stated plainly, never a capsule: the modules that control the workflow, the gates, and the planner and library
that act on and verify capsules. And **no capsule is its own final judge**: internal checks are allowed, never
evidence.

## Still open

**What else cannot be represented as a capsule** stays open, at Muk's instruction: anything whose effects
cannot be declared, and anything needing a run-time choice of other capabilities. See [[Open Questions]].

Related: [[Every Stage Applies Capabilities]], [[Quality Not Just Correctness]], [[Self-Improvement]].
