# 51: Handoff. Capability Capsule v3: report and deck rebuilt around a to g (2026-09-22)

**Current: schema v2.4, report and deck v3.** Branch `schema-v2.1-overnight` in `capsule-openjiuwen`; not pushed or
merged. The obby vault (`tundle/obby/HANDOFF.md`, then `obby/Directives.md`) holds the current state. This note
records why v3 exists and where it is. It builds on note 50 (v2.1 to v2.3).

## Why v3

Muk rejected the v2.3 organisation. His corrections are binding and are recorded in `obby/Directives.md`:

- **The function (a):** CC makes capabilities easier to **pick** (inputs and outputs known; deterministic finding on
  declared requirements cuts out most options, then semantic choice), **verify** (everything declared, so checks have
  a target), **improve** (performance, trust and lineage logged), and **remove** (spatiotemporal composability).
- **Thesis:** others observe (Symphony's fingerprint, Skill Drift, Alita-G); CC declares, because a declaration can be
  checked and found wrong before a sprint relies on it.
- **(c)** planning, freeze and dispatch, with code; CC is upstream of Symphony. **(d)** what CC itself depends on, not
  a capability's own dependencies. **(e)** Symphony first. **(f)** why better. **(g)** built before, never combined.
- Rationale per function, never per paper. Key slides answer a to g first, the body elaborates. No filler.

## What was built

| What | Where | Tundle copy |
|---|---|---|
| Knowledge base, the source of both deliverables | `capsule-openjiuwen/kb/` (`INDEX.md` first: map and topic register) | |
| Report v3, 37 pages, 19 figures | `merged/build_report_v3.py` → `merged/REPORT.md` → `.docx` | `Capability Capsule Merged Report - Muk.docx` |
| Deck v3, 30 core slides and 3 backups, a-g key slides first | `merged/build_spec.py` → `deck.json` → `.pptx` | `Capability Capsule Merged Deck - Muk.pptx` |
| Schema v2.4: §0 reference by function (fields required or optional, carriers, stage-1 criteria, position) | `merged/SCHEMA.md` | `Capability Capsule Schema v2.4 - Muk.md` |
| New papers read in full: SkillProbe (2603.21019), SkillWeaver (2504.07079) | `kb/papers/`, `verify/PAPER-LEDGER.md` | |
| Reviews (Sonnet only) | `verify/V11-v3-review-20260922.md` | |

v2.3 stays in git and as `merged/REPORT-v2.3.md` and `merged/build_spec_v2.py`.

## To change anything

Edit `kb/`, then run `python merged/build_report_v3.py` and `python merged/build_spec.py` plus
`tundlekit deck build merged/deck.json -o "merged/Capability Capsule - Merged Workshop.pptx"`. PowerPoint must be
closed for the docx build. Figures: `merged/figures/figs_v3.py` (P1, D1, V1).
