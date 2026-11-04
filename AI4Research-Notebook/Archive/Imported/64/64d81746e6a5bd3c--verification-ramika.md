# Ask: Verification ↔ Capability Capsule

From Muk (Capability Capsule) to Ramika (Verification), for the 2026-09-22 workshop. Rewritten 2026-09-22 against
`SCHEMA.md` v1.6, which wins where they differ. One page, written to be argued with.

## The split

- **Supervisor, 2026-09-21:** verification covers system-level and capability-level verification, runs at each
  sprint, and "CC is more of a scheme, and verifier is a tool. CC can use tools, but CC is not a tool."
- **Yours:** how checks run, and how the verifier's own error is measured.
- **Mine:** what is checked (the declared pre- and postconditions), the admission rule over your verdicts, and the
  records they land in. You measure, the capsule layer decides.

## What I give you, what I need

| I give you | I need from you |
|---|---|
| **The targets**: each capsule's postconditions, anchored deterministic, reference or judged; its preconditions, with `state_source` and `on_unavailable` | **A verdict per check** against the exact `content_hash`: satisfied, violated or unknown, with the missing evidence named for unknown |
| **Parity fixtures to run**: each precondition at its boundary, with state missing and with state stale (certified level) | **Precondition parity results** (`precondition_parity[]`): does the capsule's own exit logic agree with its declaration |
| **Run pins**: every binding, exit and gate verdict, so a sprint failure maps to exact capsule versions | **Sprint-level failures naming the step**, which the run pin turns into `revalidation_pending` on those hashes |
| **Observed effects** at tool-call level from agent-core's rail | **A verifier audit** (A4): false-pass and false-fail rates per anchor kind, on a stated corpus |

## Why, from the papers (all read in full; numbers in `verify/PAPER-LEDGER.md`)

| Rule | Evidence |
|---|---|
| audited error rates on every certificate; a false-pass ceiling for certification (default 0.05, `design`) | false-pass bias injected on a grader stopped retirement by the contribution rule (0 to 0.3, against 1.3 clean), while raw deprecations never reached zero and hid it (The Blind Curator, 2607.07436 Table 1, p6) |
| deterministic checks and a judge both have a place | they were complementary: checks missed semantic defects the judge flagged, and the judge's score barely moved on structural defects (2607.07436 Fig. 2) |
| `unknown` defers with an evidence request; only a violated check rejects | Cognitive Admission Control (2609.16313 p5, p8); rejecting on unknown lost 30 of 120 completions in its ablation (p10) |
| running without error is never evidence | 215 of 222 self-built tools ran and failed every held-out test of their own job (2604.00392 p5) |
| parity is tested at boundary, missing and stale state | the release fixtures of Don't Offer What Can't Be Done (2608.01050 p5 §6.1) |

## Smallest version that unblocks M3

The verdict format (per check, per hash, typed unknown) and one audit number per anchor kind.

## To settle together

- The false-pass ceiling: 0.05 until measured.
- What a sprint-level failure sends: run id and step id by default.
- The owner of the observing sandbox for effects below tool-call level.
- Ground Truth: verification curates reference answers, pinned as data dependencies.
