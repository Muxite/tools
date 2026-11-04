# AI4Research

Reports, decks, notes and papers from the AI4Research work. The work happens on each machine; this folder holds
the latest copy. `notes/` mirrors the work machine's `report-writing-set/` folder, so relative links inside the
notes still resolve.

**Status, 2026-09-25.** Capability Capsule (CC) was presented on 2026-09-23. Its milestone M1 is a fresh build on
openJiuwen (agent-core and Symphony). The old AI4Research harness is an **archive**: its tools and
`capability_capsules.py` appear only as lessons, never as a build target.

## Start here

| What | Where |
|---|---|
| **Block 1: Capability Capsule and the schemas** | `../obby/Block 1 - CC and Schemas/`, a folder in the obby Obsidian vault, kept as reference: Capability Capsule, the workflow in six parts, every schema and how they relate, where CC connects to agent-core and jiuwenswarm, what the PRD needs. Start at `Design/README.md` |
| **Capability Capsule, current** | `capability-capsule/` (see its README): the presented deck, the post-presentation deck and its Part A, the layer 2 deck, schema v2.10b with its JSON Schema, M1 policy and validator |
| Capability Capsule reasoning and decisions | the Obsidian vault, `../obby/`. Start at `HANDOFF.md` |
| Capability Capsule session records | `notes/57-capsule-v6-merge-quality-scope-20260923.md` is the newest; 49 to 56 are the history before it |
| Capability Capsule, older deliverables | `capability-capsule/older/` |
| The code the decks and schema were built with | `../code/capsule-openjiuwen/` and `../code/tundlekit/` (snapshots for reading) |
| General workflow report and deck | `general/AI4Research General Report - Muk.docx` (`.pdf` for phones), `general/AI4Research General Presentation - Muk.pptx` |
| Reading pages | `general/sota-reader.html`, `general/paper-summaries.html`, `general/challenge-register.html` |
| Paper summaries | `papers/summaries/INDEX.md`. PDFs and extracted text are in `papers/` (see `papers/TITLES.md` for the two names each paper has) |
| Chinese ↔ English translation rules | `translate/README.md` |
| Windows GUI testing | `AI4Research Windows GUI Test Report - Muk.xlsx` and `AI4Research Windows GUI Tests Muk.xlsx`. Both are live and they are different documents. Start from `notes/44-fable-handoff-workbook.md` |
| The supervisor's slides and answers, 2026-09-18 | the four `.jpg` files in `notes/`, transcribed in `notes/45-` and `notes/46-` |
| Slide and page images of the 2026-09-15 deliverables | `notes/overnight/render/<deck-or-report>/` |
| Older snapshots | `versions/`: the newest pre-git snapshot of each document, plus the reports annotated with code locations |

## Notes on this copy

- The notes say to back up into `versions/` before every Office edit. That still applies on the work
  machine. In tundle, git history covers old versions (see `../HISTORY-CLEANUP.md`).
- Numbered notes are session records and are not rewritten afterwards. When one disagrees with the vault, the
  vault (`../obby/`) is current.
- The PDFs were rendered from the `.docx` files on 2026-09-15. If a report changes, re-render or remove its PDF
  so the two don't disagree.
