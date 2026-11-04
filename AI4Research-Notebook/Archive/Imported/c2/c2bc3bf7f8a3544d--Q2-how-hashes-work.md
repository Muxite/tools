# Q2. How hashes work

Pinned: AI4Research `b0bf165f9`, DSH `c291e7961a`, both confirmed by `git rev-parse HEAD`.
AI4Research paths sit under `harness/lib/`. Rows marked proposed are design notes, not code.

## 1. What a content hash is

A content hash is a fixed-length fingerprint computed from bytes by a public function, here SHA-256,
returning 64 hex characters. It is deterministic: the same bytes give the same fingerprint on any
machine in any year. It is one-way, so the fingerprint cannot be turned back into the content, which
makes it an identifier and not a copy. It is collision-resistant, so two inputs with the same output
have never been produced and a matching hash is treated as proof of identical bytes. It avalanches:
one changed byte, one digit of a node priority, one word of a test, flips about half the output bits.
Structured data needs a canonical form first, because the same object serialises many ways, so
AI4Research sorts keys and drops whitespace (`intent_compiler.py:62-67`). A hash proves one thing,
that these are the bytes that were agreed. It proves nothing about whether those bytes were good.

## 2. Every hash in scope

| Hash | What is hashed | When | Where stored | Where checked | Failure it catches | Source |
|---|---|---|---|---|---|---|
| `contract_sha256` | The frozen contract minus this field | Freeze | `run_contract.frozen.json` | `verify_frozen_execution_chain` | Any edit to the sealed contract | set `elastic_planner.py:7345`, checked `:7987-7990` |
| 12 `*_ref.sha256` | Each upstream artifact, requirement_ir through scheduler_input | Freeze | Same file | Same function, re-hashing each artifact | An artifact swapped after the freeze | set `:7249-7342`, checked `:7984-7986` |
| `execution_authority.sha256` | Per node: each bound capsule's whole manifest plus its transitive guard and resource capsules, each manifest file's own SHA-256, and 21 semantic fields per candidate operator | Scheduler-input compile | Each node of `scheduler_input.json`, so inside the row above | `validate()` on load, `check_operator` at dispatch | A definition edited after the freeze | `execution_authority.py:40`, `:47-69`; `elastic_planner.py:6830-6832` |
| Check-registry seal | Bytes of the frozen contract and `evaluation_check_registry.snapshot.json` | On load | Refs in the graph and contract | `frozen_evaluation_check_ids` | Grading rules swapped at run time | `execution_authority.py:105-135` |
| DSH archive seal | Bytes of each archived Agent Note, as `sha256:<64 hex>` | On archiving | `.agents/notes/archived/manifest.json` | `verify-archived-agent-notes`, against the git baseline | Any edit or deletion in the frozen archive | `scripts/archived-agent-notes.ts:14-16`, `:57-68`, `:172-190` |
| DSH bilingual sidecar | Git blob SHA-1 of each side of a document pair | When a reviewer confirms the pair | `foo.i18n.yaml` | `verify-translation-pairing`, in `doc-sync` and CI | Either side edited without re-confirming | `archived-agent-notes.ts:19-24`, `:161-166`; `docs/i18n/README.md:10-11` |
| `content_hash` (proposed) | The capsule bytes admitted | Admission | Manifest identity block | Nothing today | Admitted bytes replaced | `39-continuous-capsule-design-draft.md:59`; `report-capsules/REPORT.md:585` |

Failure strings, in row order: `frozen.contract_sha256.hash_mismatch`, `frozen.<ref>.hash_mismatch`,
`EXECUTION_AUTHORITY_INVALID` and `FROZEN_OPERATOR_DEFINITION_CHANGED`,
`GRAPH_EVAL_CHECK_REGISTRY_INVALID`, `sealed content hash changed`, a red pairing gate, none.

## 3. Figure spec: one panel, two hashes, two jobs

Lower lane, `STAGE["library"]`: record box `capsule manifest v1.4.0` tagged `content_hash`, arrow to
record box `registry`, drawn as three stacked rows for append-only. Caption: *protects: the bytes
admitted are the bytes loaded*.

Upper lane, `STAGE["freeze"]`: CODE box `compile scheduler input`, arrow to a wide record box
`scheduler_input.json` holding nested labels `grading rules` and `execution authority`, arrow to
record box `run_contract.frozen.json` tagged `contract_sha256`. Caption: *protects: the plan, its
capsules and its grading rules cannot change after the freeze*. A return arrow feeds a CODE box
`verify_frozen_execution_chain`, labelled `re-hash and compare`, with a failure label in
`OUTCOME["failed"]` reading `hash_mismatch, sprint failed`.

One crossing arrow runs up from `registry` into `execution authority`, labelled `manifest copy +
source_sha256`: the capsule hash is swallowed by the freeze hash. That is the point of the panel.

Matplotlib, per `report-general/build/figures.py`: `node()` with `actor="record"` for the record boxes
and `actor="code"` for the code boxes, `stage=` per lane, `arrow(..., rad=-0.25)` for the crossing
arrow, `RATIO` sizing, a 16 by 7 canvas, lanes at y 0.5 and y 4.0.

## 4. What a hash does not do

- It does not prove the capsule is correct, only that the bytes are unchanged. Beyond Task Completion
  is the counterexample: 96.8% of kept tools failed tests of their own job, and all of them hash fine.
- It does not see a semantically equivalent rewrite as the same. A renamed variable is a different
  hash and identical behaviour. It also weighs nothing: a typo in a comment and a reversed
  conditional both return `hash_mismatch`.
- It does not cover what was left out. Operational state is excluded from the frozen operator
  definition by design (`execution_authority.py:11-16`), so a busy operator is not a contract change.
- It does not stop an edit, only detect one afterwards, and only where something re-computes. Nor does
  it authenticate an author; that needs a signature, absent from shipped code
  (`12-capsule-ecosystem-digest-en.md:32`, `:43-47`).
- It does not make a confirmation sound. The DSH pairing gate says so: a green gate "means the pair
  was confirmed consistent at these exact contents, not that the confirmation was sound"
  (`docs/i18n/README.md:40`).

## 5. IF ASKED

- **Are capsule definitions inside the freeze hash?** Inside, not referenced. `freeze_node` deep-copies
  each bound capsule's whole manifest into the node, adds the manifest file's SHA-256 and walks
  `required_guard_capsules` and `required_resource_capsules` (`execution_authority.py:47-60`).
- **What happens on a mismatch?** Three things, by site. At the freeze, a definition that moved raises
  `CAPSULE_CHANGED_DURING_PLANNING` or `OPERATOR_CHANGED_DURING_PLANNING`
  (`execution_authority.py:81-94`, called `elastic_planner.py:7240-7241`). At verification, mismatches
  become error strings and the sprint returns failed (`:7595-7599`). At dispatch, a changed operator
  demotes that candidate to UNAVAILABLE and the run continues (`multi_task_runner.py:1253-1262`).
- **Is the hash really over the grading rules?** Yes. `evaluation_binding`, `evaluator_gate` and the
  run `test_policy` are written into the scheduler input (`elastic_planner.py:6802-6807`, `:6836`),
  so rules chosen after outputs were seen change `contract_sha256`.
- **Why a git blob hash for DSH document pairs?** It is computable with `git hash-object` on an
  uncommitted file, so a pair is re-recorded in the same pull request (`docs/i18n/README.md:11`).

## 6. Current coverage, and where it is thin

- **General report.** §2.3, lines 152-177, Fig. 3 at 158, App. C rows 780-783. Accurate. Thin: it
  never says capsule manifests are copied whole into the hash, names only the capsule abort and not
  the operator twin, and omits that the live check is skipped when no node carries an execution
  authority (`execution_authority.py:85-86`).
- **Capsule report.** Two mentions. Line 585 lists a content hash in Table C1 with the rejection cell
  blank, and Table C2 (599-611) has no hash reason. Line 678 says a mid-sprint build "would change
  definitions the freeze has already hashed". Lines 190, 209, 321 and 575 name
  `CAPSULE_CHANGED_DURING_PLANNING` without saying a hash detects it. App. D has no DSH hash fact.
- **Decks.** The capsule deck has no occurrence of "hash". The workflow deck covers it: slide 3 at
  line 131, IF ASKED at 146-151.

Patches in `patches/1b-hashes.md`.
