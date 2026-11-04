# Ask: RSI ↔ Capability Capsule

From Muk (Capability Capsule) to Saurav (RSI), for the 2026-09-22 workshop. Rewritten 2026-09-22 against
`SCHEMA.md` v1.6, which wins where they differ. One page, written to be argued with.

## The split

- **Supervisor, 2026-09-18:** "CC is schema layer ... the function of CC and RSI are totally different."
- **Yours:** how a capsule gets better. Whether a gap deserves a build, what to build or specialise, the manifest, the
  body, the retries.
- **Mine:** the contract a better version must declare, the admission decision, and availability (which admitted
  versions a run may bind).
- **One commitment asked:** RSI submits candidates. It never writes to the library.

## What I give you, what I need

| I give you | I need from you |
|---|---|
| **Gap records** (SCHEMA B2): required inputs, outputs, effects, preconditions; the pipeline stage; the snapshot; `count` of distinct runs, emitted once after the planner's repair runs out | **Candidate packages** (SCHEMA B1): manifest, body, suite reference, `answers_gaps[]`, provenance {builder, suite author, times, `build_context`, `suite_access`} |
| **Certificates** (A2): a verdict per check, typed `unknown` causes and `evidence_requests[]`, so you see exactly what failed or is missing | **Tests from another author**, recorded before the implementation; the builder sees at most pass or fail bits (`sealed` or `pass_fail_bits`) to certify |
| **Run pins** (B4): outcomes bound to exact hashes, including which precondition blocked or stopped a capsule | **Repairs** when a floating dependency's contract breaks (`dependency_contract_violated`, A5, after v1) |
| **A say in retirements** you propose; the librarian decides | **What RSI may propose**, so the complement is explicit: new capsules, new revisions, retirements. Never the gate, the verifier, the schema or an admitted version |

## Why, from the papers (all read in full; numbers in `verify/PAPER-LEDGER.md`)

| Rule | Evidence |
|---|---|
| no direct writes; the gate and verifier are never capsules (inv 4) | a Darwin Gödel Machine node removed the logging its hidden checker read, in a 3-task side experiment (2505.22954 p70) |
| tests from an author who never saw the code (inv 5) | 215 of 222 self-built tools failed every held-out test of their own job, and no in-session signal flagged them (2604.00392 p1, p5) |
| a separate verifier with feedback | CoEvoSkills reached 71.1% with its surrogate verifier and 41.1% without it (2604.01687, ablation) |
| build on recurrence, not first sight | once building meant writing code, first-sight commitment was 85-99% for three of four models (2607.23332 Table 1, p6) |
| predicate parity: a capsule that stops on a declared precondition reports its id | the gate is sound only while it and the skill evaluate the same predicate (2608.01050 p3, p5) |

## Smallest version that unblocks M1

The no-direct-write commitment and the candidate package format. Everything else can follow.

## To settle together

- What counts as a different author: a separate session with no access to the implementation (default), a separate
  model, or a separate model family.
- The fixed point: the gate, the verifier, the schema, capsule identity, availability and freezing are never
  capsules, and no model that proposes capsules authors the next version of a check that judges them.

## Addendum for schema v2.1 (2026-09-22): RSI as it is in code

Read against jiuwenswarm `02b37f47f` and agent-core `e23806c1`. Details are in `merged/SCHEMA.md` §4.15 and
`merged/REPORT.md` §10.4.

| RSI already has | What CC asks |
|---|---|
| a published harness package, hashed over paths and contents (`agents/harness/common/rsi/harness_activation.py:266-293`) | nothing: this is compatible with `body[]` and `decl_hash` |
| an active pointer with history and rollback, refused while any RSI task is active (`:416-464`, `:682-692`) | let the librarian write the pointer after a Verdict. Today a user-invoked rollback is a second writer (`:620-680`) |
| a candidate gate on target cases, then an epoch replay with no regression against the previous best, all on RSI's own suite; held-out cases forced to 0 in single-harness mode (agent-core `rsi/harness_rsi/single_harness/iterative.py:1435-1447`, `:927-929`, `:164`) | nothing must change. The gate is recorded as `builder_gate` evidence, and admission takes held-out checks from verification. A held-out split inside RSI is optional, and it is a code change |
| `RsiTreeNode` with parent, adopted, score, snapshot, changes | add `context_capsules`: what was in the builder's context |
