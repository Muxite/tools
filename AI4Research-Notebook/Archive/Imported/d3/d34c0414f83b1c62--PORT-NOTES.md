# Porting `declaration.json` to the current schema (2026-09-29)

This capsule was authored against an earlier shape of `cc.declaration.v1`
(the one `SCHEMA.md`/`capsule-openjiuwen` describes). The schema has since
moved to `jiuwenswarm/docs/architecture/capsule/fields.md`, which is now the
one definition of the Declaration's fields. This note records what changed
and why, the way `EXCEPTIONS.md` records the exception-handling rationale.

## What was non-conformant, and the fix

1. **Both `carrier` and `body` were set.** Current `fields.md`: "Exactly one
   of `carrier`, `body`, `remote` or `members` is set" (policy rule
   `one_code_source`, `SCHEMA_NONCONFORMANT` on violation). This capsule's own
   code is one file (`compile_intent.py`), so `carrier` is correct alone.
   `checks/intent_ir_checks.py` was listed a second time under `body`, but it
   was never orphaned by removing that: every one of the seven
   `guarantees.checks[].runner` entries already pins that same file by its own
   `sha256`, independent of `identity.body`. Removed `body`.
2. **`identity.lineage` used a field name (`parent`) that doesn't exist.**
   Current schema: `identity.lineage.parent_hash` and
   `identity.lineage.relation`, required together, only when the capsule
   actually has a parent version. This one doesn't (it's the first version),
   so the whole optional `lineage` object is omitted rather than filled with
   a non-conformant shape.
3. **`evolution.rsi` was missing.** It is `req`/`checked` in the current
   schema and in the policy's first-epoch `required` list. A Declaration
   without it fails admission's schema check outright. Set to `propose`:
   RSI may submit a child, held as `admitted_inactive` until a person
   activates it. This was a judgment call, not a fact recovered from old
   files, and it has since been confirmed and made concrete (2026-09-29,
   below).
4. **`guarantees.failure_modes` didn't exist, even though `EXCEPTIONS.md`
   already specifies it in full and `capsule.md`'s current "when a call goes
   wrong" section now states the general rule this capsule's `EXCEPTIONS.md`
   proposed.** Added the two reason codes `compile_intent.py` actually raises
   (`INTENT_INPUT_MISSING`, `INTENT_INPUT_NOT_STRING`), each `retriable:
   false` (retrying the same input deterministically fails the same way).

## 2026-09-29: `evolution.may_change` added

The schema grew a second RSI field after this port was first written.
`evolution.rsi` alone used to gate whether RSI could touch a capsule at
all. It now also needs `evolution.may_change`, an allow-list of exactly
which paths and files a child may differ on. Absent or empty, RSI may
change nothing, no matter what `evolution.rsi` says. See `fields.md`'s
evolution section and `rsi.md`'s "RSI permissions: opt-in" section for
the full rule.

Muk's direction for this capsule: the code inside may change, and the
declared effect class and effects may change with it, but the ports are
locked. Set:

```json
"may_change": ["files:compile_intent.py", "changes.effect_class", "changes.effects"]
```

`ports` and `guarantees.checks` are not listed, so both stay fixed for
every RSI child. `rsi_cannot_grant` separately blocks a child from ever
adding `evolution` to its own `may_change`, so this permission can only
narrow over time, never widen itself.

## What is still open, not fixed here

- **`EXCEPTIONS.md` lists a third code, `INTENT_INPUT_ID_MISSING`, that
  `compile_intent.py` never raises.** The carrier never reads or checks
  `raw_intent.raw_intent_id` at all. Left out of `guarantees.failure_modes`
  because declaring a failure mode the code cannot produce would itself be
  wrong. Either the code should gain that check, or `EXCEPTIONS.md` should
  drop the code. Muk's or Xiaoyang's call, not made here.
- **The port types `raw_intent` and `intent_ir` are not yet vocabulary
  entries.** `port-types.md` defines the vocabulary's shape but lists no
  domain types yet beyond the base ones. `b1-design.md`'s Open item 3 says
  the same. This capsule's ports name types that don't formally exist yet.
  Not something this port can fix. It needs the first version of each type,
  as `b1-design.md` says.
- **`decl_hash` and `interface_hash` are still uncomputed.** They're
  computed by the author kit (INV-15, over RFC 8785 canonical JSON with v1.0
  defaults filled in), which doesn't exist yet. `tools/hash_declaration.py`
  only stands in for the per-file `sha256` fields, as before. Unchanged by
  this port.
- **Where this capsule sits in the pipeline is still a live, unresolved
  question**, not a settled one. See the dated note added to `README.md`.
