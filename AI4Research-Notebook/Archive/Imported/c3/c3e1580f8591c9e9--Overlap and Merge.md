**Status, 2026-09-24: back-burnered for M1.** Composition is possible in the data structure (`members[]`,
`relation: composes`) and has no code until M4 ([[Layer 2 Presentation]]).

**Terminology settled by Muk, 2026-09-23: the non-merge A-B ships first; merging comes later.**

- **Composition** is what this note specifies and what ships: A-B pins its members by hash, their
  internals are locked, and it runs them in order, **unchanged**. `relation: composes`.
- **Merging** (rewriting a block's internals so its members run in one pass) is a later operation.
  `relation: fuses` is reserved in the schema and **not implemented**. See [[Fusion After Merge]].

Read "merge" below as composition unless it says otherwise.

---

**Muk's design, 2026-09-23. A 能力胶囊 holds a set of capabilities; n = 1 is the degenerate case.
Recurring, high-quality structures are merged into bigger blocks so placements can be made at higher
quality — and nothing is ever split.**

Most of the machinery already exists: see [[Symphony Flow]].

## The five beats

1. **Everything starts at n = 1.** Individually declared, individually admitted, individually placed.
2. **Observe.** Evidence accumulates per edge: how often A→B occurs, and how often it succeeds.
3. **The pruning assumption**, stated as an assumption: two capabilities that each fail their
   declarations are assumed to fail together too, in either order — so failing parts are never merged.
   openJiuwen already enforces exactly this.
4. **Propose, gate, place.** A recurring, high-quality structure becomes a candidate merge capsule. It
   gets a Declaration derived from its members, members pinned by hash, A and B recorded as `co_parents`.
   It is tested **as a block**, on the union of its members' suites plus its own, exactly as the
   individuals were. The librarian then decides whether to place it.
5. **A, B and A-B all remain.** Nothing is retired by merging. Bigger blocks make better placements
   available; the chooser picks per node. **Internals are locked** on merge, except §4.11's
   unpin-with-a-written-purpose. **There is no split operation** — build up only.

## The asymmetry (the sharp point of the whole design)

> Two capsules that each **fail** are assumed to fail together, so junk is never merged.
> Two capsules that each **pass** are **not** assumed to pass together — the block earns its own quality
> record or it has none.

Conservative in both directions, and it follows from quality being distributional: a block's quality is
not the product of its members' qualities and cannot be inferred from them. A merged capsule is measured
as a capsule, exactly as an n = 1 capsule is. See [[Quality Not Just Correctness]].

**What would prove the pruning assumption wrong:** a pair that succeeds together while each member fails
alone.

## Why no splitting

Splitting an existing capability is complicated and unnecessary: if every capsule can exist as a set of
one, every combination can be built up, and no further atomisation is needed. Muk's call, and it removes
a whole class of machinery.

## Recurrence when sprints are expensive

Sprints are costly and infrequent, so thresholds tuned for high-frequency systems do not transfer —
Google recommends materialised views over 30 days of query history, task mining over thousands of events.
We will have tens of observations. Three consequences:

1. **Count in sprints, not nodes** — the schema already says this (threshold 2, per sprint). Keep it and
   say why.
2. **Take Microsoft's posture, not Google's.** This is where the two references in
   [[Inspiration from Other Software]] stop being redundant and become a spectrum: Google's rewrite is
   **automatic** because the evidence is enormous; Microsoft's process mining **marks an opportunity for
   a person to approve** because the evidence is thin and expensive. *We are in Microsoft's regime.*
   A merge proposal is surfaced and approved, never applied automatically.
3. **Seed from known structure, not only from observation.** Some chains run every sprint by
   construction — the workflow's shape is already known. Seed the first candidates from that, and use
   observed recurrence for everything else. This also lets the merge system be demonstrated before much
   evidence exists.

## Costs, stated honestly

Merging is not free, and these belong on the slide rather than in an appendix:

- **Scheduler granularity.** A merged block is one node, holds one lease, and takes the *union* of its
  members' write scopes. Better placement quality, **less parallelism inside the block**.
- **Retry.** A failure inside a merged block **retries the whole block**, unless the block declares
  internal retry.
- **Attribution.** A gap inside a merged block is attributed to **the block, not the member** —
  attribution coarsens as blocks grow.

See [[Impacts on the Workflow]].

## The worked example

`intent → IntentIR → faithfulness`, with the **gate drawn outside the block** ([[The Ceiling]]). It is
the highest-recurrence chain in the system and so the first candidate the algorithm would ever propose.

## Composition now, fusion later

What this note specifies is **composition**: members pinned, internals locked, run in order, unchanged.
That buys placement grain and a block-level quality record. It buys **no execution saving** -- if A and B
each iterate N items, the block still iterates twice.

**Fusion** -- rewriting the internals to run in one pass, dropping a check of B that A already guarantees --
is the separate later operation that would make merging pay for itself. Out of scope for v2.9, and no field
is added for it. The rule that would change: *internals are locked* becomes **the contract is locked, the
implementation is free**, with the composite acting as the oracle.

Full analysis, including a pass-by-pass legality map and four spec problems, is in
[[Fusion After Merge]], left by a research session on 2026-09-23. One of its findings was a real bug and is
already fixed: `relation: merge` was used by SCHEMA §4.9a but missing from the §3.1 lineage enum (the value is
now `composes`).
**Its two cited papers (SkillZip, TraceCompiler) are abstract-only and must not be cited until read in
full.**

## When it happens

**M4** on the [[Milestone Ladder]] — it needs a library and accumulated evidence. But because
`symphony/flow` exists, M4 is cheaper than it looks.

Related: [[Versioning and A-prime]], [[Self-Improvement]], [[Capability Capsule]].
