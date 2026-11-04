---
type: capsule
status: proposed
tags: [capsule, open-question]
---

# Exception handling for a capsule

*Proposed 2026-09-28, while building `compile_intent` as the first non-`search_capsule`
Declaration. Open for sign-off; not a Directive. Full working version, with the concrete
case this was built against: `capsules-build/compile_intent/EXCEPTIONS.md`.*

## The gap

The Declaration says what a capsule promises ([`guarantees.checks`](../schemas/declaration.md))
and what must hold before it runs ([`needs.when`](../schemas/declaration.md)). Nothing
says what a capsule's carrier must do when something goes wrong *inside* the call. Every
author would otherwise invent their own answer.

## Three cases, one rule each

1. **A precondition should have caught this, but the capsule was called anyway** (a caller
   bug, a direct test, a future runner bug). The carrier **raises** a narrow, typed
   exception carrying a `reason_code` from a closed list it declares for itself. It never
   guesses at malformed input.
2. **The input is valid in shape but hard to interpret** (vague, contradictory, incomplete).
   The carrier **never raises**. It returns a structurally valid output and puts the
   difficulty *in* the output — an ambiguity, an unknown, a conflict whose resolution can
   only ever defer to a person or a judged capsule, never conclude on its own that
   something is impossible. This is "block for safety, label for quality"
   ([invariants](../schemas/invariants.md)) restated for exceptions.
3. **A bug**, i.e. nothing the capsule's own contract anticipated. It is not caught or
   hidden: it propagates, the runner wraps it into an Observation with `outcome: error`
   and a `Reason`, and the node gate reads that as `blocked` — never `pass` (INV-8).

## Proposed schema change

A capsule states its own closed list of runtime failure modes the same way it states
checks: a new optional field, e.g. `guarantees.failure_modes: list<{reason_code, when,
case: 1 | 2 | 3}>`. Admission's rules gain one row: a capsule's `reason_code` values are
unique to it and additive only — never removed once admitted, for the same reason INV-16
protects fields (a removed code silently changes what a caller must handle for). The
runner's contract: any exception that is *not* one of a capsule's declared `reason_code`s
is wrapped as a generic `CAPSULE_RAISED_UNDECLARED` and is always `blocked`, never `fail`
— a capsule may declare its way into case 1 (a soft, potentially-retriable input problem)
but never into case 3 (an undeclared exception is always a bug, and a bug is always
`blocked`).

This needs Muk's and Xiaoyang's sign-off — it touches the runner contract on
[run](../components/run.md#runner). It exists here because `compile_intent` needed a
concrete answer to be built at all, and the next capsule will need the same one.

## Read next

- [What each field is for](fields.md)
- [The tools that serve CC](tools.md)
- [`compile_intent`'s own version of this, worked through end to end](../../capsules-build/compile_intent/EXCEPTIONS.md)
