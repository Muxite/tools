---
name: report-writing
description: Draft and check technical report prose in a fixed house voice (the style card) - impersonal, declarative, no hedges, no em dashes, lists carry enumeration, and every claim stated flat then bounded by a labelled limitations list. Covers the report rules, how deck elements map to report elements, and the checkers tundlekit text lint (style), tundlekit text fignums (figure/table numbering and references) and tundlekit text wordcount (section sizes and change against a git baseline). Use when writing, editing or reviewing a report, paper-style note, README-style deliverable or any Markdown prose meant for readers, or when a deck needs its companion report.
---

# Writing a report

| Task | CLI | MCP tool |
|---|---|---|
| style lint (voice, markers, sentence length) | `tundlekit text lint REPORT.md [--rules S001,S002] [--ignore S003] [--max-words 42]` | `text_lint` |
| figure and table numbering, dangling references | `tundlekit text fignums REPORT.md [--refs DECK-NOTES.md]` | `text_fignums` |
| words per section and bucket, change since a git ref or a file | `tundlekit text wordcount REPORT.md [--baseline HEAD~1] [--baseline-file OLD.md] [--no-tables]` | `text_wordcount` |
| § / App. / Fig. / Table references in other files; renumbering | `tundlekit text xref REPORT.md --in FILE... [--renumber OLD=NEW] [--write]` | `text_xref` |
| every cited number located on a page of its paper | `tundlekit claims trace REPORT.md --papers DIR [--ledger LEDGER.md] [--in FILE...]` | `claims_trace` |
| apply exact review edits (dry run first) | `tundlekit text apply-edits EDITS.json FILE [--write]` | `text_apply_edits` |
| hand edits in a .docx vs the source | `tundlekit text docx-diff OLD NEW [--search PATH...]` | `docx_diff` |

Paths may be files or folders (folders are walked for `*.md` and `*.txt`). Add `--json` for machine-readable
results, `--strict` to fail on warnings. Write Markdown; convert to .docx only at the end.

## The style card (the house voice)

Measured from the owner's own drafts. Follow it so the prose reads as theirs.

**Measured**

- Mean prose sentence 20-24 words; work in a 15-25 word band, with at most 1 longer definitional sentence per
  paragraph (lint warns over 42 words)
- No first person: no "we", "our", "I". Describe the system, not the authors
- Zero hedges, zero contractions, zero em dashes, zero semicolons
- Prose states a position; a list does the enumeration

**Habits to reproduce**

- **Lists carry the load.** When something needs enumerating, break to a list rather than extending a sentence.
  Noun-phrase or gerund lists: parallel, verb- or gerund-first, no terminal punctuation, no sub-bullets.
  Full-sentence items end in a period. Term lists read "Term: gloss".
- **Triads** for the 1 point that needs weight ("hand-write, hand-verify, or predict"); do not force one into
  every list.
- **Define by function, never by formalism**: "X is a system that uses A to provide B and allows C."
- **1 analogy, brief, then dropped.** No extended metaphor, no scene-setting, no anecdotal opener.
- **Formal connectives**: "Thus", "Akin to", "Then", "Additionally"; "While" / "When" for subordinate clauses.
  Not "so", not "like".
- **Slashes for near-synonym sets**: "skills/MCPs/tools".
- **Numerals** for technical or measured quantities ("1 abstraction", "83.03%"); spelled-out words for discourse
  quantifiers ("two limitations").
- **High technical density.** The reader builds agents; common terms need no gloss, but project terms are
  defined before use.
- **Open a section with its subject's function or status**, never "This section describes…".
- **Rhetorical questions only in headings**, never in body prose.

## Claim → labelled limitations list

The voice is uniformly assertive, so an unmeasured claim reads exactly like a measured one. Carry uncertainty in
structure, never in the verb.

1. State the claim flat, with the number, the setup and the source in the sentence.
2. Follow at once with a labelled list: "There are two limitations to this result:" plus 1 bullet per bound.
3. Never soften the sentence ("a promising 83.03%, though this may not generalise" is wrong twice: it weakens
   the claim and buries the bound).

> In the GAIA benchmark of real-world tasks, Alita-G reports 83.03% pass@1 with the generated tool library,
> against 75.15% without it. There are two limitations to this result:
> - The tool library is built from the same validation set the score is reported on.
> - GAIA totals are not directly comparable between systems.

Status goes in plain words ("Everything in this section is proposed. None of it is built or measured."), never in
a softened verb and never in a marker.

## Report rules

- **Every heading states its point in 1 line**, not a topic label.
- **Cite papers by title** where they are used, at least once per section: "In Beyond Task Completion [3], …",
  with the setup (data, model, n) in the sentence and locators as "[3, Table 5]". Never only "[n]" or an id,
  never author names or "et al." in body prose (lint S008; reference lists and Appendix A are exempt), never a
  nickname.
- **Every number traced** to an opened source (page, table, file:line). Never cite a paper that was not opened.
- **Every design choice has a reason or a paper** next to it. Every term, system and figure element is defined
  before use.
- **No markers in the deliverable**: no ⚠, `[verified]`, `[proposed]`, `[doc]`, `[repo-claim]`, `[TODO`,
  `[TBD`, `[footnote`, `TODO:`, `XXX`, and no corrections tables (lint S006). Provenance stays in working notes.
  Gap markers such as `[footnote this def]` are fine while drafting in notes, but none may survive into the
  deliverable.
- **Order**: background → evidence, each paper ending with a "Thus, …" consequence so the rules exist before the
  design → today's state → design → evaluation → next → open questions. The design section may open with its
  full figure and a paragraph walking it, then justify each part in subsections.
- **Detail goes to appendices**: full per-paper numbers, inventories, rejection reasons, platform facts, code
  locations and excerpts, referenced from the body.
- **Figures and tables**: captions `Fig. N. <takeaway sentence>` and `Table N. <takeaway>`, numbered from 1
  without gaps, in order; every mention resolves. Appendix numbering may use a prefix (`Fig. A1.`).
- **"So what" pass**: for every section, paragraph, bullet, row and figure, answer "so what?". Cut anything without
  an answer.

## Deck element → report element

The deck and report carry 1 argument in 2 formats: same content and coverage; the report is formal and fuller and
may reorder. If the report has a section, the deck has a slide (or an agreed cut), and the reverse.

| Deck | Report |
|---|---|
| Goal slide | §1 opening paragraph + goal statement |
| Background slide | §1 paragraphs + figure; facts in an appendix |
| DEMONSTRATED BY strip | "In <paper title> [n], …" with the setup in the sentence; locators as [n, Table 5] |
| Plain-prose finding bullet | 1 sentence with the number, then the limitations list |
| Chart + takeaway line | figure whose caption states the takeaway; the table in an appendix |
| Rule slide ("What this means: …") | closing "Thus, the design …" paragraph of that subsection |
| Synthesis table | numbered table with a 1-sentence lead-in |
| "Today" gaps slide | list "Five things the current code does not yet give…" with file:line |
| "Proposed" divider | design section opening: "Everything in this section is proposed. None of it is built or measured." |
| Design overview figure + long SAY | design section opening paragraph + the design figure |
| Rule collection table | table of changes, each row with its reason and citation |
| THUS strip | "Thus, …" sentence ending the subsection |
| IF ASKED bullets | limitations lists, or appendix detail |
| Evaluation / prove-wrong slide | evaluation tracks, the prediction, and a "would be proven wrong by" list |
| Open questions table | final section: lists grouped by owner |

Check that rule numbering and names match between deck and report (same count, same names).

## Checking

```
tundlekit text lint report.md --band 15,25
tundlekit text fignums report.md --refs deck-notes.md=report.md
tundlekit text xref report.md --in deck-src/deck.json notes/presenter-pack.md
tundlekit claims trace report.md --papers papers --ledger notes/LEDGER.md
tundlekit text wordcount report.md --baseline HEAD
```

`text lint` masks code blocks (also when indented under a list item), inline code, HTML comments, URLs, link targets
and YAML front matter, so they never trigger findings. Suppress a finding on a line and the next with
`<!-- lint-ignore S005 -->` (no ids = all rules). Suppress a rule in a whole file with
`<!-- lint-file-ignore S009 -->` (ids are required), for example in an appendix file of long tables. Use
suppressions sparingly and only with a reason.

| Rule | Severity | Finding | Fix |
|---|---|---|---|
| S001 | error | em dash | a comma, colon or full stop |
| S002 | error | first person (we, our, ours, us, "I …") | describe the system; passive or impersonal |
| S003 | warning | hedge (arguably, seems, perhaps, somewhat, possibly, might, to some extent, it appears; "may" only in "may be/have/well/also/not/help/seem/lead/cause", not the permission sense "a server may use") | state flat, then add the limitations list |
| S004 | error | contraction | spell it out |
| S005 | warning | semicolon in prose (table rows are skipped) | 2 sentences, or a list |
| S006 | error | status marker or placeholder, in prose or headings | plain words; move provenance to notes |
| S007 | warning | question in prose (table rows, and sections whose heading contains "question", are exempt) | a statement; questions only in headings |
| S008 | error | "et al." outside references / Appendix A | cite by title |
| S009 | warning | sentence over `--max-words` words (default 42; table rows skipped) | split it or break to a list |
| S010 | warning | section opening "This section…", "In this section…", "Here we…" | open with the subject's function or status |
| S011 | warning | jargon: "Eq. 5", "pp" outside a citation bracket (`[2, Eq. (5)]` is fine) | say what the equation does; write "points" |
| S012 | info | the file's mean prose sentence length is outside `--band` (default 15,25; needs 5+ sentences) | split long sentences, or join choppy ones |

`text fignums` rules: F001 duplicate caption number, F002 gap, F003 sequence not starting at 1, F004 captions out
of order, F005 a mention (`Fig. 3`, `Table A2`) with no matching caption in the checked reports (mentions after
"arXiv" or the word "paper" point into a cited paper and are skipped). Pass deck notes or other documents with
`--refs` so their mentions are checked against the report's captions; `--refs NOTES.md=REPORT.md` resolves that
file against 1 report only, when several reports are checked together.

## Cross-references and renumbering (`text xref`)

`tundlekit text xref REPORT.md --in FILE...` checks every `§N.M`, `App. X.n`, `Fig. N` and `Table N` in the deck
script or spec, presenter packs and notes against the report's headings and captions. X001 is a reference with no
target. X002 is a heading marker that a build script slices on (`between("…")`, `section("4.2")`) and that appears
other than once in the report. To renumber, give all moves in 1 call: they apply simultaneously, so swaps work,
and only whole references change (`Fig. 1` never touches `Fig. 10`):

```
tundlekit text xref report.md --in deck-src/deck.json --renumber "Fig. 9=Fig. 10" "Fig. 10=Fig. 9"
tundlekit text xref report.md --in deck-src/deck.json --renumber "§4.2=§4.3" --write
```

Without `--write` it lists the planned edits (path, line, old, new). With it, the report's headings and captions
and every file under `--in` are rewritten.

## Tracing numbers to pages (`claims trace`)

`tundlekit claims trace REPORT.md --papers DIR [--ledger LEDGER.md] [--in FILE...]` takes every body sentence that
cites `[n]` and contains a number, maps `[n]` to an arXiv id through the reference list (`arXiv:ID` in the entry),
and searches that paper's text page by page (`51%` also matches `0.51`). Each number gets a status:

| Status | Meaning | Action |
|---|---|---|
| located | found on the listed pages | check the page matches the locator in the text |
| derived | not in the paper, but a ledger row marks it derived | the ledger row must show the arithmetic |
| ledgered | not in the paper, but in a ledger row | the ledger row must give its source |
| untraced | not found in the cited papers (T001) | find the page, fix the number, or cite the right source |
| no_source | no cited paper has a text file (T002) | fetch the paper (`tundlekit papers fetch`) and re-run |

`--in` checks deck notes or presenter packs with the report's reference list. A located number can still be the
wrong quantity; the fact-check brief (review-prompts skill) covers meaning.

## Applying review edits (`text apply-edits`)

Apply a reviewer's exact edits as anchored replacements, never by retyping paragraphs:

```json
[
  {"find": "passed 31% to 34% of their verified tasks", "replace": "passed 28.7% to 35.8% of their verified tasks"},
  {"find": "Typed selection is already settled", "replace": "Typed selection is settled once the 2 type vocabularies are normalized", "count": 1}
]
```

```
tundlekit text apply-edits edits.json report.md
tundlekit text apply-edits edits.json report.md --write
```

Each `find` must occur exactly `count` times (default 1), or nothing is written and every failure is listed. The
dry run prints a unified diff. It also works on a `.docx` (within 1 paragraph, across runs), which keeps the
owner's formatting.

## Carrying hand edits back (`text docx-diff`)

When the owner edited the built `.docx`, compare it with the Markdown source (or with the previous build) before
regenerating:

```
tundlekit text docx-diff report.md edited/report.docx --search report-src
```

Changes are paragraph-level `replace`, `insert` and `delete` operations with a `hint` (`path:line`) where the old
text lives. Carry each into the source, rebuild, and diff again.

## Word counts (`text wordcount`)

`text wordcount` lists words per heading (levels 1-3), the total, and `buckets`: `body`, `appendix` (from a level-2
`Appendix` heading) and `references` (from `References` / `Bibliography`), so a body limit can be checked apart from
the appendices. `--baseline GITREF` compares with a git revision and `--baseline-file OLD.md` with another file
(not both); each section gets its change (`"new"` for new headings). `--no-tables` leaves table rows out. Use it to
keep sections balanced and to report what an edit grew or shrank.

## Before handing over

- [ ] `tundlekit text lint` clean (no errors; every warning fixed or explained)
- [ ] `tundlekit text fignums` clean, with the deck notes passed as `--refs`
- [ ] `tundlekit text xref` clean for the deck script and notes; `tundlekit claims trace` has no untraced numbers
- [ ] every paper named by title in each section that uses it; every number traced to a page, table or file:line
- [ ] every claim bounded by a labelled limitations list where it needs one; status stated in plain words
- [ ] coverage matches the deck (`tundlekit review coverage REPORT.md DECK.pptx`); rule names and counts match
- [ ] previous version backed up to `versions/` before overwriting; the rendered document reviewed page by page
  (deliverable-review skill)
