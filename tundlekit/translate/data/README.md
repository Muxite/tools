# translate/: Chinese ↔ English SWE translation kit

For agents and humans in this workspace who translate technical text between Chinese and English. The main job is **zh→en**: much of AI4Research / OpenSolar is written in Chinese, while the report and deck are English-only (`notes/AUDIENCE.md`). **en→zh** is supported and ready for when it's needed.

**The one idea:** the dangerous translation errors are the *fluent* ones: a term swapped for a near-synonym, "should" turned into "must", "can evolve" turned into "can evolve under version control", a design goal presented as a shipped fact. They read well and pass a skim, and then an expert catches them. This workspace has already shipped several (see [failure-modes.md](failure-modes.md)). How much process a translation gets, a shared glossary, and a separate critic matter far more here than which model does the translating.

## Pick your tier first

| Tier | When | What you do |
|---|---|---|
| **T0** | reading Chinese for your *own* understanding; nothing you write quotes it | keep [zh-en-traps.md](zh-en-traps.md) in mind. No checks. |
| **T1** | a short quote or paraphrase going into a note, report, slide, or a message to another agent | follow [RULES.md](RULES.md); run `tcheck encoding` on the source and `tcheck all` on the pair; use the quoting convention below. If the quote carries a guarantee, requirement, number, or status claim, also run the critic (exceptions A12). |
| **T2** | a full digest or section, anything spec / API / runbook / acceptance criteria, or anything a slide's argument rests on | the full pipeline below |

Anything that leaves your own context is at least T1 (M12).

## T2 pipeline

The orchestrating agent **does not translate T2 text itself**. It hands the text to a translator subagent and then to a separate critic, because a translator reviewing its own work reads what it meant, not what it wrote (M11). If your context forbids subagents without permission (`notes/HANDOFF.md` rule 5), ask first. If you can't, use the cold self-critic fallback in exceptions A14 and label the result `critic: self (no subagent)`.

```bash
K=/home/muk/work/translate/checks/tcheck.py
python3 $K encoding SRC.md                          # 1. garbled input? repair a copy or stop (FM-10)
python3 $K glossary-slice SRC.md --dir zh-en        # 2. terms relevant to this source
# 3. translator subagent: prompts/zh-to-en.md with the slice pasted in; save its output to OUT.md
python3 $K all SRC.md OUT.md --dir zh-en            # 4. mechanical checks (code, spans, banned terms, untranslated text)
# 5. critic subagent, FRESH context: prompts/critic.md with source, translation, and step-4 output
# 6. orchestrator applies the critic's smallest fixes and re-runs step 4. Any other rewording goes back to
#    the critic. Every [AMBIGUOUS] stays visible until a human resolves it; the orchestrator never guesses
# 7. append any pending terms to glossary.tsv (status=pending)
```

For text unrelated to AI4Research, add `--domains general` to `glossary-slice` and `all`, so AI4Research conventions (合同, 算子, …) aren't enforced. `SRC.md` can be `path:START-END` to take a line range (widen it if it cuts a table or fence). If `OUT.md` contains the translator's `<translation>…</translation>` block, only that block is checked.

**`tcheck` passing means "no mechanical damage", not "faithful."** It checks exactly three things: garbled encoding, protected spans (code blocks, inline code, URLs, paths, plus a warning for numbers and a check for untranslated leftovers), and glossary conformance. Modal force, additions, omissions, scope, causality, actors, and status are the critic's job. That split is deliberate: scripts only get the checks they can do reliably.

## Quoting convention (notes, report, deck)

- **English first.** The Chinese original goes in a footnote or appendix, never Chinese-only in the body (AUDIENCE.md).
- **Cite the source** as `path:line`, and **copy the original from the file**, never from memory or from another note (M8: note 14 misquoted its own correction).
- **Label what it is**: "Translated from `path:line`" for a translation, "Summary of §X" for a paraphrase. Quotation marks only ever go around a translation (A7).
- **Markers**: `[AMBIGUOUS: A | B]` where the source is ambiguous and the ambiguity matters; `[TN: …]` for a translator's note that explains a term or a sense and never evaluates (M4).
- **Check record.** One line in the footnote: `tcheck: OK (2 warnings explained) · critic: fresh | self · verdict: faithful`. With no record, the quote counts as unchecked (M12).
- **Translation never upgrades evidence.** A `[repo-claim]` stays a claim; design-doc text stays "the design specifies…", never "the system does…" (FM-9).

## Files

| File | Read it when |
|---|---|
| [RULES.md](RULES.md) | before any T1/T2 translation. The binding MUST/SHOULD rules; §2 is zh→en, §3 is en→zh |
| [failure-modes.md](failure-modes.md) | to understand *why* the rules exist; FM-1..FM-10 with real cases from this workspace |
| [zh-en-traps.md](zh-en-traps.md) | while translating zh→en: modal ladder, tense and status markers, scope, polysemous words (支持, 默认, 实时, 保证…), connectives |
| [en-zh-traps.md](en-zh-traps.md) | while translating en→zh: modal ladder, near-synonym pairs, typography |
| [exceptions-and-misuse.md](exceptions-and-misuse.md) | when a rule doesn't seem to fit (§A exceptions), before reviewing (§B misuse, M1..M13), and before trusting a tcheck result (§C limits) |
| [glossary.tsv](glossary.tsv) | via `glossary-slice`. The single source of truth for terms: approved and banned renderings, domain, evidence |
| [prompts/zh-to-en.md](prompts/zh-to-en.md), [prompts/en-to-zh.md](prompts/en-to-zh.md) | to brief a translator subagent (fill in the `{{slots}}`) |
| [prompts/critic.md](prompts/critic.md) | to brief a critic subagent (fresh context; it reports findings and never rewrites) |
| [checks/tcheck.py](checks/tcheck.py) | stdlib Python; `--help` for usage. Tests: `python3 -m unittest discover -s checks` |

## Glossary rules for agents

- **Append only.** New terms go in as `status=pending`, with evidence (`file:line` for both the Chinese occurrence and any English rendering or code identifier). Never reorder rows, and never flip a row to `approved`. A human does that (M7).
- A row that doesn't fit the sense in front of you is **not** a reason to edit the row. Use the right rendering and add a `[TN]` that names the source term (A2).
- Authority when sources disagree: code identifier > the source's own English gloss > approved row > industry term > pending gloss (A1).
- The shipped glossary is validated by the tests (column counts, statuses, and no two approved rows mapping the same term to different renderings).

## Scope and precedence

- **deepseek-harness doc pairs** (`foo.md ↔ foo.zh.md` inside that repo): that repo's `docs/i18n/` rules, terminology table, and `dsh-translate-docs` workflow win outright (A13). This kit is for translating *into our notes and deliverables*.
- The user-level skill `swe-translate` (`~/.claude/skills/swe-translate/`) points agents here. This directory is the single source; the skill only routes.
