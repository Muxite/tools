# 14. What the schema does not claim

- **It does not claim that declared capsules are correct.** It claims that what was checked is recorded, and that what
  was not checked is labelled.
- **It does not claim safety in combination.** Screening reduces composition risk. Nothing certifies a set.
- **It does not undo emissions or external state.** It only controls when they are allowed, and checks a declared
  compensation once. What a capability does behind its interface is its author's (invariant 13).
- **It does not see a remote body change its behaviour behind an unchanged interface.** It catches a changed
  interface at dispatch, and changed behaviour only by observation, so such effects are at most `audited`.
- **It does not clean a poisoned context.** It traces and marks stale the claims a revoked context capsule touched,
  and never reuses that context. Influence that leaves no claim cannot be traced.
- **It does not fix degradation at scale on its own.** Much of it is the agent using no skill at all, which a
  filter cannot fix (2605.24050 Table 2).
- **It does not promise identical replays.** A model behind an API changes; sprints are recoverable, not
  byte-identical.
- **It does not promise task success.** Passing the filter means no declared exit holds, not that the capsule
  will succeed or was the right choice.
- **It does not make token budgets hard.**
- **It does not verify Cordis-style inverses** unless a check exercises them.
- **The design has not been measured as a whole.**
  - The numbers cited are the papers' own, in their own narrow setups.
  - None of them tested this design.
  - The worked example's findings, hashes and error rates are illustrative.
- **It does not claim that a model judge is trustworthy.** It claims that every judge's standing is recorded, that a
  pass from an unmeasured judge is labelled rather than trusted, and that only a measured judge counts toward
  certification or retirement **(design)**.
- **It does not claim that labelled results are right.** Softening lets more work run; the labels say how much of it
  is backed. A reader who ignores the labels gets today's trust level, not CC's.
- **It does not settle ownership, the ceiling, or the default thresholds.** The ceiling is proposed (SCHEMA §4.10). The
  recurrence threshold of 2, the overlap policy and the risk ceilings are all **(design)**.
- **It does not describe a system that exists.** The capsule layer is a proposal. Only the code cited as "today" and
  the openJiuwen sources exist.

## The question deliberately held open

**What cannot be represented as a capsule at all** is left open on purpose, rather than answered and
later retracted.

What *is* settled is the boundary. A capsule may produce an **assessment**; it may never be the thing
that **decides**. So a faithfulness check or a domain verifier is a capsule -- it emits a Finding and
something else acts on it -- while the gate, admission, the librarian's Standing moves, the planner's
filter, the freeze and dispatch never are. The schema enforces this by write access rather than by
classifying intent: no capsule may write to the gate, the suites, the logs admission reads, or the
record stores.

Candidates for the rest of the answer: anything whose effects cannot be declared, and anything that
needs to choose *other capabilities* at run time. Naming the boundary we know is stronger than an answer
that would have to be withdrawn.
