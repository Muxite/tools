**Note for the team leader, 2026-09-23. Proposal from Muk, analysed against the current merge design. Nothing in
the schema, kb or deck has been edited; this note is the only file written.** Status: **design proposal, not
decided.** Update 2026-09-24: the post-presentation deck shows it as design ("Where a section can be fused, and
where it cannot"), and layer 2 back-burners merge, fusion and optimisation for M1: possible in the data
structure, no code. Written by a research session (Sonnet 5); Muk asked for it to be left for the team leader agent.

## The idea (Muk)

A and B are n = 1 capsules and A-B is an accepted common form. Can TensorRT's theory (graph IR, layer fusion,
constant folding, DCE, CSE, kernel/tactic selection, memory planning) be used to optimise A-B into a *new*
capsule? A and B may have had their own pre-gate checks; A-B may remove or modify them. If A and B each iterate
N items, A-B iterates once and applies both. A-B is tested as one unit: A's inputs in, B's outputs out.

## Verdict

**Yes, and it is a different operation from today's merge.** Today's merge ([[Overlap and Merge]], SCHEMA §4.9a)
is **composition**: a block pins A and B by hash, internals locked, runs A then B unchanged. What Muk describes is
**fusion**: a build step that rewrites the internals. Recommended shape: **merge first, then optionally fuse the
merged block.** The fused block is a child of the composite (`relation: fuse`); A, B, A-B and A-B-fused coexist,
nothing is retired, there is still no split. The composite is the **oracle**: the fused block is compared with
A;B on stored inputs and must pass §4.6 replacement compatibility and the §4.5c rule "block a regression against
a known-good version".

## The one rule that changes

"Internals are locked" becomes **"the contract is locked, the implementation is free."** Dropping A's pre-gate
is allowed, but the union-of-suites rule stays, including A's `negative_control` cases: the fused block must
still refuse or mark whatever A refused or marked. That is how a dropped check is shown to have been redundant.
Each dropped check is recorded as kept, subsumed by a named check, or dropped with a reason. Members stop being
pinned internals and become `sources` (provenance and oracle; nothing runs from them).

## Pass map (legality comes from the Declaration)

| TensorRT / compiler pass | Capsule case | Legal when |
|---|---|---|
| vertical fusion | one loop applying A then B per item | both **item-local**; a sort, dedupe or aggregate is a **barrier** |
| horizontal fusion | two capsules over one input, one pass | both read-only on it |
| CSE | one fetch/parse instead of two | `pure` or `idempotent`, same `resource_key` |
| constant folding | shared config resolved at build | inputs declared constant |
| DCE, buffer elision | drop unused output, skip scratch write | the seam has exactly one consumer and is not a declared output or gate input |
| reorder / pushdown | B's filter before A's transform | needs a commutativity declaration; defer |
| tactic selection | pick best candidate fused body | measured on replayed inputs, not live sprints |

Failure behaviour counts as observable: unfused, A failing on item 5 leaves no B effects; fused, items 1-4 already
have B applied. So `compensable` and `irreversible` effects cannot be interleaved unless the block declares its
own atomicity. **`IntentIR` is probably consumed downstream, so the current worked example
(`intent → IntentIR → faithfulness`) is likely not a fusion candidate;** use an N-item list case.

## Where the analogy breaks

- TensorRT fuses from a catalogue of pairs known to give the same result. We have no such catalogue, so
  legality must come from author declarations, and **iteration shape is not in the schema today**.
- Equivalence is exact or comparator-based for deterministic tools, but only a **rate within a tolerance** for
  model-bearing capsules. Our sources do not show TensorRT verifying fused kernels numerically: the oracle test
  is **our design**, not TensorRT's.
- Our sprints are rare, so fusion is proposed and a person approves, as for merges (Microsoft regime).
- TensorRT discards its engine; ours is stored and admitted. NVIDIA: builds "are not strictly bit-deterministic",
  so identity is the hash of the artifact, never of the derivation.
- The fuser is a cold-path builder ([[The Ceiling]] is not crossed): it produces a Declaration, has no write
  access to gates or suites, and the proposer must not be the builder (AllocBench).

## Vocabulary to add

**fusion** (rewrite internals) vs **merge** (declare the block); **composition** (members run unchanged);
**sources**; **seam** (the A→B interface that disappears); **item-local** / **barrier**; **subsumed check**;
**equivalence mode** (exact, comparator, rate within tolerance); **pass** (a named rewrite recorded on the block;
TensorRT names fused layers with `+`); **source map** (block regions traced to sources, diagnostic, not a split).

## Problems found in the current spec

1. SCHEMA §3.1 lineage `relation` lists supersedes, specialises, rollback_of, migrated_from, but **not `merge`**,
   which §4.9a already uses. `fuse` would be a further addition.
2. Suites that assert on the seam cannot run against a fused block. Needs a trace build that exposes the seam in
   tests only, or a rule that compares at the block boundary.
3. Iteration shape would be a new author-side field. Make it optional, default unknown, unknown meaning
   composition only (as `needs.when` already treats unknown).
4. The §4.9a costs (one lease, retry the whole block, coarser attribution) apply more strongly to fusion; a
   source map recovers some attribution.

## Evidence standing

- **Checked on NVIDIA docs:** the builder collapses a recognised pattern into one kernel; fusion removes launch
  overhead and avoids materialising intermediates; tactics are picked by timing at build; the timing cache reuses
  a result for an identical layer configuration; builds are not bit-deterministic.
- **Not checked against TensorRT:** DCE, CSE, folding, pruning (general compiler theory), engine portability,
  intermediate-tensor debugging behaviour.
- **AI-side precedent, not yet in the kb:** SkillZip (2608.05604) gives *legality conditions* (stable interface,
  closed execution, verifier still reachable) for reversible macros; it compresses context, not execution, so it
  is no evidence of a speed-up. TraceCompiler (2608.02680): 34 observed API calls to 11 runtime calls on one
  intent, 15 of 21 leave-one-out folds passing, refuses an under-determined irreversible effect, and measures no
  build cost. Numbers are from the abstracts; read the full text before citing.
- **Citation discipline** ([[Inspiration from Other Software]]): TensorRT is already cited for per-pair
  preconditions. Cite it again only for "what does fusing buy". Oracle SPM already covers "measure before
  trusting"; do not add a second row for tactic selection.

## Recommendation

Present fusion as **why merge pays off** (merge has no measurable benefit today), marked design, placed after M4
on the [[Milestone Ladder]], with the iteration-shape field declared inert from day one. It entered the
post-presentation deck as design and stays a next step after M4.

Related: [[Overlap and Merge]], [[Versioning and A-prime]], [[Quality Not Just Correctness]], [[Symphony Flow]].
