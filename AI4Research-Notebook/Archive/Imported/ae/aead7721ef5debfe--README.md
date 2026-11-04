# `compile_intent` — a standalone Capability Capsule

Deterministic, no-model replacement for the semantic-authoring half of
AI4Research's old `intent_compiler.py`. It turns a `RawIntent` (a request's
raw text) into an `IntentIR` (goals, outcomes, constraints, ambiguities,
conflicts, unknowns, each citing an exact source span) using fixed rules and
zero network or model calls.

This package is self-contained on purpose: it can be run and tested with no
CC runner, no jiuwenswarm, no agent-core. It is built to be dropped into
`cc/capsules/compile_intent/` inside the jiuwenswarm `ai4r_*` branches once
that scaffolding exists — see "Integration seam" below.

## Where this sits in the design

Per `ai4research-design/schemas/intent.md` and `components/request-to-contract.md`:
intent compilation is a **B2, parallel-track** capability (the M1/B1 path
uses template mapping in control code, with no IntentIR). This capsule is
built now, unblocked, against the same fixture-style pattern the PRD uses for
the Planner and RSI tracks: it produces real `IntentIR` values today, off the
main path, so the Leader Agent test, the gates and RSI can all be developed
and tested against it before B2 wiring exists.

It replaces only `normalize_input` + `compile_candidate` + `validate_intent`
from the old system — the parts that decide *what the IntentIR says*. It does
**not** include `review_fidelity` (an independent model judge) or
`decide_acceptance` (a gate, which is control code, never a capsule). Those
stay separate, per the 2026-09-25 Directive ("M1 keeps intent compilation
lean: two capsules, `compile_intent` ... and `review_fidelity`; the
deterministic checks sit inside the `decide_acceptance` gate").

## Files

| File | What it is | Who wrote it |
|---|---|---|
| `declaration.json` | The capsule's `cc.declaration.v1` Declaration | architect (this session) |
| `compile_intent.py` | The carrier: `compile_intent(raw_intent: dict) -> dict` | implementer subagent, blind to `tests/` |
| `checks/intent_ir_checks.py` | The seven `guarantees.checks` runners, run independently of the extraction logic | architect (checks are never written by the builder — INV-10) |
| `tests/test_compile_intent.py` | Black-box tests against the Declaration's contract, not the implementation | tester subagent, blind to `compile_intent.py` |
| `run_checks.py` | A standalone harness: compiles one `RawIntent`, runs every check, folds a verdict the way a node gate would | architect (this session) |
| `fixtures/` | Sample `RawIntent` JSON files for manual runs | architect + tester |
| `EXCEPTIONS.md` | The exception-handling contract this capsule follows, proposed as a general rule for every capsule | architect (this session) |

## Running it

```bash
pip install pytest   # only dependency; the capsule itself is stdlib-only
python -m pytest tests/ -v
python run_checks.py fixtures/plain_goal.json
python run_checks.py --text "Compare 4-bit and 8-bit quantisation; the report must cover both."
```

## What "deterministic" buys, and what it costs

The old compiler called a model twice (semantic authoring, then an
independent fidelity reviewer) and used deterministic code only to bind
source spans and validate structure. This capsule keeps the deterministic
half and replaces the model half with an explicit, inspectable rule set (see
`compile_intent.py`'s module docstring for the exact cues). That trades away
the old system's semantic depth — it will not infer an implicit goal a
request never states in recognisable form — for:

- **No model dependency.** It runs with no network, no Codex quota, and no
  non-determinism, so it is safe as an always-available first pass and as a
  test fixture generator for every other B2/B3 capsule that reads an
  `IntentIR`.
- **Full auditability.** Every classification traces to one of a fixed list
  of cue phrases in the module docstring; there is no hidden model judgment
  to explain.
- **Conservative defaults**, matching the design's "fail closed" and "block
  for safety, label for quality" rules: it never decides a conflict is
  `reject` (only a human or a judged capsule may conclude that), and
  anything it cannot classify with confidence becomes an `unknown` or a
  non-blocking `ambiguity` rather than being silently dropped or guessed at.

## Known limitations (found while testing, not fixed further)

These make the output noisier in specific cases; none of them break the
Declaration's contract — every check still passes for all of them, because
the checks test structure, not classification accuracy.

- **Placeholder detection over-fires on bare comparisons and HTML-like tags.**
  `a < b and c > d` and `<b>bold</b>` each produce a spurious `unknown`, because
  the placeholder regex (`<...>` / `[...]`) cannot distinguish "a filled-in
  slot" from "an angle bracket used for something else." Reliably telling
  these apart needs more context than a regex can carry; left as a known gap
  rather than adding a second heuristic layer with its own new edge cases.
- **`\bonly\b` fires on ordinary prose** ("this is the *only* option"), tagging
  it as a `scope` constraint even with no real scope boundary stated.
- **The bare cue `format` also matches "information" and "formatting."**
- **First-match-wins can drop a sentence's goal.** "Compare vendors, and the
  report must be in markdown." is classified only as a `constraint`; the
  comparison goal in the same sentence is not separately recorded. Splitting
  a sentence into more than one classified item was out of scope for v1.
- **Cross-sentence conflicts are not detected.** Only a single sentence with
  both a contrast marker and two constraint cues is flagged; "must use X" in
  one sentence contradicted by "never use X" in another goes unnoticed.

## 2026-09-29: the placement claim above predates `b1-design.md`

The "Where this sits in the design" section above says the M1/B1 hot path
uses template mapping in control code, with no IntentIR, and that intent
compilation is a B2/parallel-track capability. That was written against an
earlier design. The current `jiuwenswarm/docs/architecture/b1-design.md`
(itself marked "preliminary, open to change") puts a model-calling
`compile_intent` directly on the B1 hot path, as the pipeline's first node,
producing a real IntentIR — which this deterministic, no-model capsule is
not. Whether this capsule is: (a) superseded by a different, model-backed
`compile_intent` on the hot path, (b) usable as B1's `compile_intent` node
outright (dropping the "model" requirement), or (c) correctly a fixture
generator kept off the hot path as originally intended, is open again. See
`b1-design.md`'s node table and its Open item 2. Declaration-level schema
drift from the intervening changes is ported in `PORT-NOTES.md`; this
placement question is not something a schema port can resolve.

## Integration seam

When `cc/` exists in the jiuwenswarm `ai4r_*` branches:
1. Move this directory to `cc/capsules/compile_intent/` unchanged; the
   `carrier.ref` and `body[].path` in `declaration.json` are already relative
   to the capsule's own root, per `cc.declaration.v1`.
2. Recompute `decl_hash` and `interface_hash` through the author kit once it
   exists (today, `identity.carrier.sha256` etc. are computed by
   `tools/hash_declaration.py` in this directory, standing in for it).
3. Submit it to admission as a Candidate with `tests/test_compile_intent.py`'s
   cases as its test suite (`lineage.parent: null`, `submitter_kind: author`).
4. Nothing here calls the runner, the Artifact store, or Observations: the
   carrier takes and returns plain dict values matching `cc.intent.raw.v1`
   and `cc.intent.ir.v1`. Wrapping the input/output in Artifacts and writing
   the Observation is the runner's job, unchanged by this capsule.
