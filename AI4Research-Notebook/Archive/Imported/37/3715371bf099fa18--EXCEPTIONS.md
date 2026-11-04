# Exception handling for `compile_intent`, and a proposal for every capsule

## The question

A capsule's carrier is ordinary code; ordinary code can raise. The Declaration
says what a capsule promises (`guarantees.checks`) and what must be true
before it runs (`needs.when`), but nothing today says what a capsule must do
when something goes wrong *inside* the call. This capsule needed an answer to
build at all, so this is that answer, scoped to `compile_intent`, plus a
proposal for the general rule (open for sign-off, not a Directive).

## The three cases, and the rule for each

**1. A precondition was supposed to catch this, but didn't.**
`needs.when` declares `raw_text_present` and `raw_text_nonblank`. In a wired
system, the precondition evaluator (`components/run.md#precondition-evaluator`)
runs these before dispatch and never calls the capsule at all if they fail
(INV-8: an unfailed precondition is `defer` or `fail`, never a call). If the
capsule is invoked anyway — a caller bug, a direct test, a future runner with
a bug — `compile_intent` **raises** `IntentCompilerInputError`, a narrow
exception carrying a `reason_code` from a fixed, closed list (below). It never
guesses at a missing or non-string `text`.

**2. The input is shape-valid but hard to read.**
Contradictory instructions, vague references, no clear goal, run-on prose:
`compile_intent` **never raises** for these. It always returns a
structurally valid `IntentIR` (every list present, every check in
`declaration.json` passing) and puts the difficulty *in* the output: an
`ambiguity` with a real question, an `unknown` with the nearest-fitting
`kind`, or a `conflict` whose `resolution` is always `clarify` — never
`reject`, because a rule-based compiler with no judgment cannot conclude a
request is impossible; only a person or a judged capsule may decide that.
This is the design's own rule restated for exceptions: **block for safety,
label for quality** — a weak result ships with a label saying why it is weak,
instead of stopping the pipeline.

**3. Something the capsule cannot recover from at all.**
There is no such case in `compile_intent` today: it is `pure`, touches no
filesystem, network or model, so the only way it fails past case 1 is a bug.
A bug should not be caught and hidden; it propagates as an unhandled
exception, which the runner (once it exists) turns into an Observation with
`outcome: error` and a `Reason`, which the node gate reads as `blocked`
(never `pass` — INV-8 again).

## The closed list of reason codes this capsule uses

| `reason_code` | When | Case |
|---|---|---|
| `INTENT_INPUT_NOT_STRING` | `raw_intent.text` is present but not a `str` | 1 |
| `INTENT_INPUT_MISSING` | `raw_intent.text` is absent, `None`, or empty/whitespace-only | 1 |
| `INTENT_INPUT_ID_MISSING` | `raw_intent.raw_intent_id` is absent or empty | 1 |

These are additive to the policy's `registries.reason_code` list (INV-16: a
new registry value, not a schema change) — the existing codes
(`SCHEMA_NONCONFORMANT`, `HASH_MISMATCH`, ...) are about the Declaration and
admission, not a capsule's own runtime input. `IntentCompilerInputError`
carries the code as `.reason_code` and a plain-language `.message`, matching
`Reason {code, message}` in `cc.common.v1` field for field, so a future
runner can build a `Reason` from it with no translation step.

## The general proposal (open for sign-off, not binding)

Every capsule needs the same three cases, and right now each author would
invent their own. Proposed addition to the Declaration or to `cc.check.v1`
(exact home is Muk's call): a capsule states its own closed list of runtime
`reason_code`s the same way it states checks, e.g. a
`guarantees.failure_modes: list<{reason_code, when, case: 1 | 2 | 3}>` field.
Admission's rule set gains one row: `reason_code` values are unique per
capsule name and are additive only, never removed once admitted (a removed
code silently changing a caller's error handling is the same class of problem
INV-16 already guards against for fields). The runner's contract becomes:
*any* exception a carrier raises that is not one of its own declared
`reason_code`s is wrapped as a generic `CAPSULE_RAISED_UNDECLARED` and always
treated as `blocked`, never `fail` — a capsule may declare a **soft**
failure mode (case 1: bad input, potentially retriable upstream) but may not
declare its way out of case 3 (an undeclared exception is always a bug, and a
bug is always `blocked`, per INV-8).

This is a proposal, not a Directive: it needs Muk's sign-off and probably
Xiaoyang's, since it touches the runner contract in `components/run.md`. It
is written here because `compile_intent` needed a concrete answer today, and
because the next capsule that is built (deterministic or not) will need the
same answer.
