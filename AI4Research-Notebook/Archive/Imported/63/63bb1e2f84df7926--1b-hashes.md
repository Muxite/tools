# Patch set 1b: hashes

Proposed edits only. Nothing applied. Anchors are verbatim at the file state of 2026-09-14.
Evidence and reasoning are in `../Q2-how-hashes-work.md`.

Target: `notes/report-capsules/REPORT.md` (patches 1 to 4).
Optional: `notes/report-general/REPORT.md` (patch 5).

---

## Patch 1. Table C1, identity row gets a rejection reason (line 585)

Table C2 was read first. No existing reason fits: `PROVENANCE_UNVERIFIED` covers a missing record of
the generating model, prompt or trajectory, not a mismatch between recorded and actual bytes, and no
other reason concerns identity. A new reason is therefore needed, and `HASH_MISMATCH` matches the
string AI4Research already emits at the freeze (`elastic_planner.py:7986`, `:7990`).

ANCHOR (old, verbatim)

```
| Identity | Id, semantic version, content hash | Plans pin the exact version admitted | |
```

NEW

```
| Identity | Id, semantic version, content hash | Plans pin the exact version admitted, and the hash makes that pin checkable | `HASH_MISMATCH` |
```

## Patch 2. Table C2 gains the matching row (after line 609)

ANCHOR (old, verbatim)

```
| `PROVENANCE_UNVERIFIED` | The generating model, prompt or trajectory is not recorded |
```

NEW

```
| `PROVENANCE_UNVERIFIED` | The generating model, prompt or trajectory is not recorded |
| `HASH_MISMATCH` | The capsule's files do not hash to the content hash recorded in its manifest, so the bytes being loaded are not the bytes that passed admission |
```

Table C2's caption needs no change: it already reads "in addition to the 5 already documented."

## Patch 3. Appendix D gains 3 sentences on DSH hashes (after line 620)

ANCHOR (old, verbatim)

```
- Durable data is published as a version-named successor beside the unchanged source, and committed generations are never renamed, replaced or deleted
```

NEW

```
- Durable data is published as a version-named successor beside the unchanged source, and committed generations are never renamed, replaced or deleted
- The frozen archive of Agent Notes is sealed by an append-only manifest, `.agents/notes/archived/manifest.json`, that records a SHA-256 of each archived file's bytes, and its verifier refuses any sealed entry whose hash changed or went missing (`scripts/archived-agent-notes.ts:14-16`, `:57-68`, `:172-190`)
- Each bilingual document pair carries a sidecar record, `foo.i18n.yaml`, holding the git blob hash of each side as of the last time a reviewer confirmed the two say the same thing (`docs/i18n/README.md:10-11`)
- The pairing gate states its own limit: a green gate "means the pair was confirmed consistent at these exact contents, not that the confirmation was sound", and it "cannot judge whether the two sides say the same thing" (`docs/i18n/README.md:40`)
```

## Patch 4. Section 4.5 gains 2 sentences on what makes the pin verifiable (line 321)

ANCHOR (old, verbatim)

```
Versioning is the first of these to build, because the current freeze assumes a library that does not change. Pinning `capsule_id@version` in the registry, the planning snapshot and each node's execution authority turns today's `CAPSULE_CHANGED_DURING_PLANNING` abort into a lookup of the version the plan bound. Admission takes effect at the next sprint's planning snapshot, never inside a running sprint.
```

NEW

```
Versioning is the first of these to build, because the current freeze assumes a library that does not change. Pinning `capsule_id@version` in the registry, the planning snapshot and each node's execution authority turns today's `CAPSULE_CHANGED_DURING_PLANNING` abort into a lookup of the version the plan bound. Admission takes effect at the next sprint's planning snapshot, never inside a running sprint. The pin names a version; the content hash is what makes the pin checkable, because the freeze already copies each bound capsule's whole manifest and a SHA-256 of its manifest file into the node's execution authority, and hashes that into the run contract (`execution_authority.py:40`, `:47-69`; `elastic_planner.py:6830-6832`, `:7339-7345`). A capsule admitted mid-sprint therefore cannot be substituted into a running plan without changing that hash, which is what turns "used from the next sprint" from a convention into a property verification can test (`elastic_planner.py:7984-7990`).
```

## Patch 5 (optional). General report section 2.3, freeze-abort sentence (lines 154-157)

The description is imprecise rather than wrong. Two gaps: the same check also raises
`OPERATOR_CHANGED_DURING_PLANNING` for a changed operator definition
(`execution_authority.py:92-94`), and the check returns early and does nothing when no node carries
an execution authority, which happens when the planning catalog snapshot has no execution
definitions (`execution_authority.py:85-86`, guarded at `elastic_planner.py:6829-6832`).

The inaccurate sentence, quoted: "The evaluation budget becomes a test policy first, so the grading
rules exist before anything is sealed, and if any capsule definition changed during planning, the
freeze aborts with `CAPSULE_CHANGED_DURING_PLANNING`."

ANCHOR (old, verbatim)

```
anything is sealed, and if any capsule definition changed during planning, the freeze aborts with
`CAPSULE_CHANGED_DURING_PLANNING`.
```

NEW

```
anything is sealed, and if any capsule or operator definition changed during planning, the freeze
aborts with `CAPSULE_CHANGED_DURING_PLANNING` or `OPERATOR_CHANGED_DURING_PLANNING`. The check
compares the live definitions against the ones already frozen into the nodes, so it runs only for a
plan whose nodes carry a frozen execution authority.
```

If the second sentence is judged too much detail for section 2.3, apply only the first sentence and
leave the caveat to Appendix C.
