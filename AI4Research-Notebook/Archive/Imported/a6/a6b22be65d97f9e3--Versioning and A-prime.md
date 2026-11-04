**The hardest question in the merge design: A, B and A-B exist, then A is revised to A′. What happens to
A-B?** Answered from what other companies do, 2026-09-23.

| Question | Answer | Precedent |
|---|---|---|
| Does A-B break? | **No.** A-B pinned member A by hash and keeps running on that hash. Frozen sprints keep what they pinned (inv 3) | **Amazon** Step Functions: a new child version does not change a parent until the parent's reference moves |
| Does A-B silently become A′-B? | **Never.** A merged block's internals are locked; a member change is a new block, not an edit | **Google** Bazel: change an input's checksum and the cached output is simply not reused — nothing is mutated in place |
| Is A-B now wrong? | **Stale, not invalid.** Marked stale against A′ and still usable. If A is *revoked* rather than superseded, A-B goes `suspect` with `MEMBER_UNAVAILABLE` — the cascade the schema already has, and jiuwenswarm already ships for SkillPacks | **Google** BigQuery: a materialised view refreshes when its base changes compatibly, and is *invalidated* when it does not |
| Do we automatically build and test A′-B? | **No — lazily, on demand.** A′-B becomes a candidate only when A′ passes §4.6 replacement compatibility against A (outputs cover every consumed port, no new powers) **and** something actually asks for the pair again | **Google** Bazel: rebuild on demand when inputs no longer match, never eagerly on every change |
| What if A′ is strictly better? | Still no automatic rebuild. The librarian may *promote* A′-B as a candidate, but A-B is not retired — nothing is retired by merging or by revision | **Google** BigQuery: the base table always remains |

## The rule in one line

> **Pinned members never move; a changed member makes a candidate, not an edit; and candidates are built
> when asked for, not when changed.**

This matters doubly given that sprints are expensive ([[Overlap and Merge]]): eager rebuilding of every
A′-B combination would spend the budget on blocks nobody asked for.

Related: [[Overlap and Merge]], [[Inspiration from Other Software]], [[Symphony Flow]].
