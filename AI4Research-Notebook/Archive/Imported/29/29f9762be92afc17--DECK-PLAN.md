# Deck plan: the general (workflow) talk

> **Presentation rework, 2026-09-14 (supersedes the counts and rules below).** 26 slides, 16:25 planned; the
> capsule deck plans 23:33, 39:58 together (target 40, max 45). Colour by stage (`build/palette.py`), 1 box per
> model call, notes SAY / MUST HIT / IF ASKED, design slides end in a THUS strip, external results carry a
> MEASURED BY strip. Order: title · 3 claims · 6 terms · pipeline (Figure 1, 6 model calls before the freeze,
> each followed by code) · intent · requirement (+ checks registry) · binding figure · no capsule fits · freeze
> order · hash chain · tamper test · dispatch tick · **frozen DAG over 4 ticks (Figure 5)** · trust (2 operator
> paths) · gates · claims figure · 1 claim end to end · experiment code · evidence so far · TruthInsightBench ·
> 4 reference systems in 1 table · DSH mapping · challenges ×2 · ahead/behind · next and open questions.
> Cut to notes: hard-filter codes, SchedulerInput node, sealed-rules nearest work, harness chart, failure-rates
> chart, 3 of 4 SoTA slides. Review checklist and results: `../report-capsules/DECK-PLAN.md` header.

Rewritten 2026-09-14 for the engineering-style rebuild. Source of truth: `REPORT.md` v0.4.
Built by `build/build_deck.py` on the shared kit `build/deckkit.py` (also used by the capsule
deck). Black and white only. **44 slides, 26:15 planned.** Capsule talk follows directly.

## Slide rules (both decks)

- breadcrumb eyebrow (section) + short label title; no assertion-sentence titles
- body = 1 of: table (≤ 6 rows, ≤ 4 columns), figure, code excerpt, or ≤ 5 short bullets
- source line in the footer (`file:line` or arXiv id + page); every on-slide number is in the report
- detail in speaker notes, which start `TIME m:ss`
- dense slides are split, not shrunk (body ≥ 20 pt, tables ≥ 16 pt, excerpts ≥ 14 pt)

## Sections

| # | Section | Slides | Visuals |
|---|---|---|---|
| 1 | System | title, scope, what it is, terms, status | 2 tables |
| 2 | Workflow | pipeline, intent ×2, requirement ×2, binding ×3 | Figure 1, binding figure, 3 tables |
| 3 | Freeze | order, hash chain, grading-rules excerpt, real SchedulerInput node, tamper test, nearest work, trust model, costs | freeze chain, trust boundary, 3 code excerpts |
| 4 | Execution | dispatch tick, dispatch rules, 14-node ledger, 2 operator paths, gates | tick figure, 4 tables |
| 5 | Claims | pipeline, extraction rule, 1 claim end to end, measured rates | claim figure, regex excerpt, failure-rate figure |
| 6 | Experiments, evaluation | who writes code, first external test | TruthInsightBench figure |
| 7 | State of the art | AI Scientist-v2, Kosmos, Arbor, auto_research | 4 tables |
| 8 | Platform | harness effect, dsh mapping | harness figure |
| 9 | Challenges | report §6.1 A+B, C, E | 3 tables |
| 10 | Summary | ahead/behind, next, open questions | |

Cut candidates if over time: "A real SchedulerInput node", "Sealed grading rules: nearest work"
(about 75 s).

## Visual sources

- drawn figures: `build/figures.py`; new diagrams rendered at 2 sizes (`fig/`, `fig/slide/`)
- chart data: `build/figdata.py`
- code and fixture excerpts: `build/excerpts.py` → `build/excerpts/*.txt`; exits if a source line moved.
  No real run output exists in the repo; the `harness/metadata` examples are placeholders and are
  not used. The SchedulerInput node comes from `tests/harness/fixtures/scheduler-input-live-two-node.json`

## Claims the deck must not make

- "AI4Research verifies claims": without an experiment it certifies provenance
- "No model decides after the freeze": no model schedules, routes or admits; 20 of 43 checks are rubrics
- "No LLM writes experiment code": the adapter path uses `codex exec`
- "The frozen chain is fully recomputed": 3 stages recomputed, the rest hash-compared
- "AI4Research beats system X": no external score
- "There is a generalist fallback": `UNSATISFIABLE_CAPSULE` fails the plan
