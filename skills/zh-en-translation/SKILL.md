---
name: zh-en-translation
description: Translate software-engineering text between Chinese and English (mainly zh to en) without the fluent errors experts catch - swapped terms, strengthened modals, added mechanisms, design goals presented as shipped facts. Covers picking a tier (T0 reading, T1 short quotes, T2 full pipeline with a separate translator and a fresh-context critic), the quoting convention, the mechanical checks via tundlekit translate check (encoding, spans, glossary, glossary-slice, all), and the binding rules, glossary and prompts via tundlekit translate resources. Use when reading Chinese sources, quoting or paraphrasing them into English notes, reports or slides, translating docs, specs or code comments in either direction, or reviewing such a translation.
---

# Chinese ↔ English translation

**The one idea:** the dangerous errors are the *fluent* ones: a term swapped for a near-synonym, "should" turned
into "must", "can evolve" turned into "can evolve under version control", a design goal presented as a shipped
fact. They read well, pass a skim, and then an expert catches them. How much process a translation gets, a shared
glossary and a separate critic matter far more than which model translates.

| Task | CLI | MCP tool |
|---|---|---|
| garbled input? (mojibake, U+FFFD); `--repair OUT` fixes a copy | `tundlekit translate check encoding SRC.md` | `translate_check` (`mode` = encoding) |
| glossary terms relevant to a source | `tundlekit translate check glossary-slice SRC.md --dir zh-en` | `translate_check` (`mode` = glossary-slice) |
| protected spans intact (code, inline code, URLs, paths, numbers) | `tundlekit translate check spans SRC.md OUT.md` | `translate_check` (`mode` = spans) |
| glossary conformance (approved and banned renderings) | `tundlekit translate check glossary SRC.md OUT.md --dir zh-en` | `translate_check` (`mode` = glossary) |
| all mechanical checks on a pair | `tundlekit translate check all SRC.md OUT.md --dir zh-en` | `translate_check` (`mode` = all) |
| technical terms (CamelCase, acronyms, English runs in Chinese text) carried into each version | `tundlekit translate terms SRC.md OUT.md [MORE.md...] [--compare same-language] [--no-glossary]` | `translate_terms` |
| list the rules, traps, glossary and prompts | `tundlekit translate resources` | `translate_resources` |
| print one of them | `tundlekit translate resources --name data/RULES.md` | `translate_resources` (`name`) |

`--dir` is `zh-en` (default) or `en-zh`. `--domains general` stops project-specific glossary conventions from
being enforced on unrelated text. `--glossary PATH` uses another TSV. `SRC.md` may be `path:START-END` to take a
line range (widen it if it cuts a table or fence). If `OUT.md` contains a `<translation>…</translation>` block,
only that block is checked. The result has `exit_code`, `ok`, `output` and `errors`.

Resources shipped with tundlekit (read them with `translate resources --name`):

| Name | Read it when |
|---|---|
| `data/RULES.md` | before any T1/T2 translation: the binding MUST/SHOULD rules (§1 shared, §2 zh→en, §3 en→zh) |
| `data/failure-modes.md` | to understand why the rules exist: FM-1..FM-10 with real cases |
| `data/zh-en-traps.md` | while translating zh→en: modal ladder, tense and status markers, scope, polysemous words, connectives |
| `data/en-zh-traps.md` | while translating en→zh: modal ladder, near-synonym pairs, typography |
| `data/exceptions-and-misuse.md` | when a rule does not seem to fit (§A), before reviewing (§B, M1..M13), before trusting a check (§C) |
| `data/glossary.tsv` | via `glossary-slice`: the single source of truth for terms |
| `prompts/zh-to-en.md`, `prompts/en-to-zh.md` | to brief a translator (fill in the `{{slots}}`) |
| `prompts/critic.md` | to brief a critic (fresh context; it reports findings and never rewrites) |

Copies of the 2 trap sheets are next to this skill: [zh-en traps](references/zh-en-traps.md) and
[en-zh traps](references/en-zh-traps.md).

## Pick the tier first

| Tier | When | What to do |
|---|---|---|
| **T0** | reading Chinese for your own understanding; nothing you write quotes it | keep the zh-en traps in mind. No checks |
| **T1** | a short quote or paraphrase going into a note, report, slide, or a message to another agent | follow the rules; run `check encoding` on the source and `check all` on the pair; use the quoting convention. If the quote carries a guarantee, requirement, number or status claim, also run the critic |
| **T2** | a full digest or section; anything spec, API, runbook or acceptance criteria; anything a slide's argument rests on | the full pipeline below |

Anything that leaves your own context is at least T1. Calling a slide quote "T0 reading" is tier-dodging.

## T2 pipeline

The orchestrating agent **does not translate T2 text itself**. It hands the text to a translator (a separate
agent session) and then to a separate **critic in a fresh context**, because a translator reviewing its own work
reads what it meant, not what it wrote. If spawning sub-agents needs permission, ask first.

```
tundlekit translate check encoding SRC.md                       # 1. garbled? repair a copy (--repair FIXED.md) or stop
tundlekit translate check glossary-slice SRC.md --dir zh-en     # 2. terms relevant to this source
tundlekit translate resources --name prompts/zh-to-en.md        # 3. translator brief: fill slots, paste the slice; save output as OUT.md
tundlekit translate check all SRC.md OUT.md --dir zh-en         # 4. mechanical checks
tundlekit translate terms SRC.md OUT.md                         # 4b. terms dropped (L001), changed in count (L002), or rendered per the glossary (L003)
tundlekit translate resources --name prompts/critic.md          # 5. critic brief, FRESH session: source, translation, step-4 output
```

6. The orchestrator applies the critic's **smallest fixes** and re-runs step 4. Any other rewording goes back to
   the critic. Every `[AMBIGUOUS]` stays visible until a human resolves it; the orchestrator never guesses.
7. Append new terms to the glossary as `status=pending`, with evidence (`file:line` for the Chinese occurrence
   and any English rendering or code identifier).

Translator brief slots: `{{source_path}}` (path + line range), `{{genre}}` (design doc, shipped user doc,
spec / API, runbook, test plan, log, code comment, chat message), `{{status}}` (what the claims are: "design,
largely unbuilt", "describes shipped behaviour as of <date>", "an agent's self-report"), `{{purpose}}`,
`{{glossary}}`, `{{source}}`. The critic also gets `{{direction}}`, `{{tcheck_output}}` and `{{translation}}`,
infers genre and status itself, and answers in a fixed format: a verdict (faithful, faithful-with-fixes or
unfaithful), then a findings table (Location · FM/M · Severity · Source span · Translation span · Problem ·
Smallest fix). An empty findings table is a valid result.

The prompts name the rule files by their original paths; give the translator and critic the texts of the
matching `data/` resources instead.

**No sub-agents allowed?** Do a cold self-critic: put the translation aside; reread the source alone and list its
claims, 1 line per clause, with force, scope and status; only then read the translation and tick each claim;
list every English clause with no source claim; run the critic checklist; label the result
`critic: self (no subagent)`. It is a fallback, not an equivalent.

**A passing check means "no mechanical damage", not "faithful".** `translate check` covers garbled encoding,
protected spans (plus warnings for numbers and untranslated leftovers) and glossary conformance. Modal force,
additions, omissions, scope, causality, actors and status are the critic's job.

## Core rules (the full text is `data/RULES.md`)

- **Say exactly what the source says.** Nothing added (guarantees, prerequisites, warnings, examples,
  qualifiers), nothing dropped. Fluency never justifies either.
- **Preserve force**: requirement, recommendation, permission, possibility, prediction, observation. Use the
  modal ladder. When unsure, choose the **weaker** claim: under-claiming is recoverable.
- **Preserve scope** (all / some / one / none; negation), **causality** (sequence is not cause; 然后 / 再 are
  sequential, only 因为 / 因此 / 所以 / 从而 / 导致 are causal), and **status** ("the design specifies X" never
  becomes "the system does X"; 将 / 会 in a design doc is usually "is intended to").
- **Never invent an actor or tense.** Subject-less Chinese: use the actor from context, else passive, else
  `[TN: actor unstated]`. 了 / 已 / 完成 mark completion in the narrative, not "shipped".
- **Hedges survive**: 一般 / 通常 / 基本 / 原则上 are not dropped and never become "always".
- **Standards-style specs**: 应 = shall (a requirement), not "should". Decide the genre first.
- **Glossary exactly** where an approved row applies; never a banned rendering; never a near-synonym for a
  technical term. An unlisted term with no established equivalent keeps the source term with a short gloss,
  `自闭环 (self-contained closed loop)`, and becomes a pending row.
- **Protected spans survive byte for byte**: code blocks (including their comments; translate those in a
  `*Translated comments:*` list under the block), inline code, identifiers, commands, flags, env vars, JSON/YAML
  keys, paths, URLs, versions, numbers and units, product names. Value-preserving format changes are allowed
  (三 → 3, 2026年9月10日 → 2026-09-10).
- **Keep structure**: heading levels, list kinds and counts, table shape, emphasis.
- **Ambiguity that matters is never resolved by guessing**: keep it, or mark `[AMBIGUOUS: reading A | reading B]`.
- **Damaged input is not translated** as if meaningful: repair a copy first, or report it.
- **Process**: translate 1 semantic unit at a time; verify clause by clause (added? dropped? force? scope? actor?
  tense? connective? term? spans?); reread the English alone and fix phrasing only; run `check all`, fix every
  hard failure, and explain or fix every warning.
- **en→zh**: keep the English modal force (may ≠ 必须, should ≠ 必须, can ≠ 保证); natural technical Chinese with
  explicit actors; half-width space between CJK and Latin/digits, full-width punctuation, 顿号 for enumerations,
  你 not 您; keep the English term on first use for unsettled jargon: `背压（backpressure）`.

## Term carry-over (`translate terms`)

`tundlekit translate terms SRC TGT [TGT...] [--compare previous|same-language] [--no-glossary]` finds the
technical terms in the source (CamelCase words, words of 2+ capitals such as `MCP`, terms with an inner slash
such as `CI/CD`, and runs of 2-4 ASCII words embedded in Chinese text; inline code, URLs, paths, list markers and
English-only lines excluded) and counts each one, case-insensitively, in every following file. A term inside a
longer term at the same place is not counted separately.

- **L001** (warning): a term present before and absent now. Usually a dropped clause or a term translated away;
  check it against the glossary, and restore it or record why it is gone.
- **L002** (info): the count changed. Often harmless (a pronoun replaced a repeat), sometimes a dropped or added
  mention; look at each.
- **L003** (info): the term is absent, but the target is mostly Chinese (over 30% CJK letters) and the tundlekit
  glossary's approved Chinese rendering appears instead ("rendered as ..."). This is the expected result of a
  correct en→zh hop, not a loss.

**Chinese hops.** In a chain `EN.md ZH.md EN2.md`, English terms legitimately disappear in the Chinese file.
With the glossary on (the default), a term with an approved `zh` rendering that appears there gives L003, not
L001. An L001 on a Chinese file therefore means either the term has no approved rendering yet (check the rendering
used, then add a `pending` glossary row) or the term really was dropped. `--no-glossary` turns this off and reports
every missing term as L001, which is the strict view for a file that must keep the English terms (a zh doc that
quotes identifiers).

**Comparing across the hop.** By default (`--compare previous`) each file is compared with the one before it, so
a chain `SRC DRAFT FINAL` shows where a term was lost. With `--compare same-language`, each file is compared with
the nearest earlier file of the same dominant script (Chinese vs Latin), which catches English drift across a
Chinese hop (`EN.md` → `ZH.md` → `EN2.md`: `EN2.md` is compared with `EN.md`). A file with no earlier file of its
script gives no findings.

```
tundlekit translate terms spec.en.md spec.zh.md spec.en2.md
tundlekit translate terms spec.en.md spec.zh.md spec.en2.md --compare same-language
```

It complements `check all`: that checks protected spans and the glossary, this checks identifiers and English terms
that no glossary row lists. Neither judges faithfulness; the critic does.

## Known noise

The checks give a starting list to confirm, never a verdict. The remaining false positives per tool:

- `translate terms`: L001 on a term correctly translated into Chinese when the glossary has no approved `zh` row
  for it (or with `--no-glossary`); L002 when a pronoun or a heading change alters a count; 2-4 word English runs
  in Chinese text that are ordinary words, not terms (a product tagline).
- `translate check`: number and untranslated-leftover warnings on value-preserving changes (三 → 3, a product name
  kept in English); glossary findings from project conventions on unrelated text (use `--domains general`).

## Quoting convention (notes, reports, decks)

- **English first.** The Chinese original goes in a footnote or appendix, never Chinese-only in the body.
- **Cite the source** as `path:line`, and **copy the original from the file**, never from memory or another note.
- **Label what it is**: "Translated from `path:line`" for a translation, "Summary of §X" for a paraphrase.
  Quotation marks only ever go around a translation, never around a paraphrase.
- **Markers**: `[AMBIGUOUS: A | B]` where an ambiguity matters; `[TN: …]` for a translator's note that explains a
  term or sense and never evaluates the source.
- **Check record**, 1 line in the footnote:
  `tcheck: OK (2 warnings explained) · critic: fresh | self · verdict: faithful`. A quote with no record counts
  as unchecked.
- **Translation never upgrades evidence.** A claim stays a claim; design-doc text stays "the design specifies…".

## Glossary rules

- **Append only.** New terms go in as `status=pending` with evidence. Never reorder rows, never flip a row to
  `approved`: a human does that.
- A row that does not fit the sense in front of you is not a reason to edit it. Use the right rendering and add a
  `[TN]` naming the source term at its first occurrence. The override covers the whole document, so check it
  holds at every occurrence.
- Authority when sources disagree: code identifier > the source's own English gloss > approved row > industry
  term > pending gloss.
- A repository with its own translation rules and terminology for its own doc pairs wins outright there.

## Done means

A bilingual engineer reading only the translation gets the same facts, caveats, force and status as a reader of
the source, and nothing extra. All check failures are fixed, every warning is explained, every `[AMBIGUOUS]` is
resolved by a human or left visible, and every pending term is recorded.
