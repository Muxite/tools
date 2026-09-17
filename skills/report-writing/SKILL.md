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
| § / App. / Fig. / Table references in other files; renumbering | `tundlekit text xref REPORT.md --in FILE[=REPORT]... [--exclude GLOB...] [--renumber OLD=NEW] [--renumber-report REPORT] [--write]` | `text_xref` |
| every cited number located on a page of its paper | `tundlekit claims trace REPORT.md --papers DIR [--ledger LEDGER.md] [--in FILE...]` | `claims_trace` |
| apply exact review edits (dry run first) | `tundlekit text apply-edits EDITS.json FILE [--write]` | `text_apply_edits` |
| hand edits in a .docx vs the source, optionally as an edits file | `tundlekit text docx-diff OLD NEW [--search PATH...] [--emit-edits EDITS.json]` | `docx_diff` |
| snapshot a file into `versions/` before writing it | `tundlekit bundle backup FILE... --reason "CHANGE"` | `bundle_backup` |
| build the .docx from the Markdown (house style, stdlib only) | `tundlekit report build REPORT.md -o OUT.docx [--excerpts DIR] [--author NAME] [--overwrite] [--force-office]` | `report_build` |
| HTML page of the summaries of the papers the report cites | `tundlekit papers page REPORT.md -o paper-summaries.html [--dir PAPERS] [--index INDEX.md] [--title TEXT]` | `papers_page` |

Paths may be files or folders (folders are walked for `*.md` and `*.txt`). Add `--json` for machine-readable
results, `--strict` to fail on warnings. Write Markdown; build the .docx with `tundlekit report build` only at the
end.

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
tundlekit text xref report.md --in deck-src/deck.json notes/presenter-pack.md --exclude "*/versions/*"
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

```powershell
tundlekit text xref report.md --in deck-src/deck.json --renumber "Fig. 9=Fig. 10" "Fig. 10=Fig. 9"
tundlekit text xref report.md --in deck-src/deck.json --renumber "§4.2=§4.3" --write
tundlekit text xref report.md --in deck-src/deck.json --renumber "App. E=App. D" --write
```

Without `--write` it lists the planned edits (path, line, old, new). With it, the report's headings and captions
and every file under `--in` are rewritten. A heading renumber also renumbers the slice markers that quote it
(`between("### 4.2 ...")`, `section("4.2")`), and each reference keeps its spelling (`Fig.9` becomes `Fig.10`,
`Table 07` becomes `Table 08`). Fenced code in the report is never renumbered.

**Appendix cascade.** `--renumber "App. E=App. D"` (or `"Appendix E=Appendix D"`) renames the whole appendix, in
the report and in every paired file, keeping each spelling: the `## Appendix E` heading and every `### E.n`
heading; `App. E`, `App. E.n`, `Appendix E` and `Appendix E.n`; and `Table En`, `Fig. En` and `Figure En`. Use it
after cutting or moving an appendix. If appendix D already exists and is not renamed in the same call, the call
fails; move both at once (`"App. D=App. E" "App. E=App. D"` swaps them).

**Several reports.** With several reports paired, a renumber applies only to the report whose headings or
captions hold the old reference, and to the files paired with that report. When more than 1 report holds it,
the call fails and lists them; pick one with `--renumber-report`:

```powershell
tundlekit text xref report.md --in build_deck.py=report.md build_capsule.py=capsule/REPORT-annotated.md --renumber "§4.2=§4.3" --renumber-report report.md --write
```

The report and every target file are written all or nothing: each new file is staged first, and if any replace
fails the files already replaced are restored (the error says which). A read-only target is refused before
anything is written.

### Pair each file with the report it actually slices

A folder often holds several reports (a general report, a capsule report, an annotated variant), and each build
script or notes file uses 1 of them. Checking every file against 1 report floods the result with false X001s.
Pair each file (or folder) with its own report as `FILE=REPORT`, and drop walked files that belong elsewhere with
`--exclude`:

```powershell
tundlekit text xref report.md --in build_deck.py=report.md build_capsule.py=report-capsules/REPORT-annotated.md notes --exclude "*/versions/*" "*.bak.md"
```

The `FILE=REPORT` examples here are PowerShell. **Git Bash note:** MSYS may rewrite an `A=B` argument whose right
side looks like a path (`notes=/c/work/REPORT.md`). Quote every `FILE=REPORT` and `OLD=NEW` argument
(`"build_deck.py=report.md"`), keep the paths relative, and if a path is still rewritten, prefix the command with
`MSYS2_ARG_CONV_EXCL="*"` or run it from PowerShell.

When every `--in` entry is paired, the positional report may be left out. Other points:

- **Annotated variants.** A build script often slices an annotated copy (`REPORT-annotated.md`) rather than the
  clean report. X002 checks each `between(...)`/`section(...)` marker against the file the call actually reads: a
  `src=NAME` keyword or third argument, or the module-level `.md` path bound to a name (such as
  `SRC = HERE.parents[1] / "report-capsules" / "REPORT-annotated.md"`). Only paths built from string literals and
  `__file__` anchors (`HERE`, `ROOT` with `.parent`/`.parents[k]`) are followed. A `.py` file whose default slice
  source resolves is also checked for X001 against that source, not against the report it is paired with.
- **End markers.** Only a call's first (start) marker must occur exactly once. The second (end) marker needs at
  least 1 occurrence after the start marker, so a repeated `### ` style end marker is fine.
- **X003** (info) means the slice source could not be resolved, so that marker was not checked. It is not a pass:
  open the script, find the file it slices, and check the marker by hand (or pair the script with that file).
- References directly preceded, in the same clause (no `.`, `;` or `:` in between; a comma does not end it), by
  another report's name (`see the capsule report §3`) and citation brackets that start with a number
  (`[5, App. H]`) are skipped. `our report`, `this report`, `the report` and `final report` are never another
  report. The report's own name (its H1 title when that
  ends in "report", else its folder name) is checked normally.

## Tracing numbers to pages (`claims trace`)

**Low priority and unreliable.** `claims trace` is not maintained as a release gate and its results can be
wrong in both directions (numbers missed and numbers matched by coincidence). Use it as a pointer list at most; tracing every number to a page by hand is the real
check.

`tundlekit claims trace REPORT.md --papers DIR [--ledger LEDGER.md] [--in FILE...]` takes every body paragraph that
cites a paper and contains a number, maps the citation to an arXiv id, and searches that paper's text page by page
(`51%` also matches `0.51` and `0.510`). It recognises 2 citation styles only:

- **`[n]` references**: `[3]` or `[3, Table 5]` in the text, with a reference list entry `[3] ... arXiv:2604.00392`
  (or `- [3] ...`).
- **Name + `(pN)` locators**: the paper's name with its arXiv id in the same paragraph, or in a report table row
  that pairs that name with the id, plus a page locator `(pN)`, `(pN, pM)` or `p. N`:
  "Beyond Task Completion (2604.00392) reports 96.8% (p7)".

A number without a citation in its own sentence uses every citation in its paragraph. Numbers after `§`, `Fig.`,
`Table`, `App.`, `Section`, `Eq.`, `Step`, `Phase`, `Level` and rule ids (`R3`), list markers, years and single
digits are not claims. Appendix table rows are checked when the table's caption or header row cites a paper.

**0 claims is not a pass.** If the report uses neither style (author-year citations, bare titles, footnotes),
the result has 0 claims, `ok` stays true, and a **T004** warning says "no citations found". Treat T004 as
"nothing was checked": rewrite the citations into 1 of the 2 styles, or trace the numbers by hand.

Each number gets a status:

| Status | Meaning | Action |
|---|---|---|
| located | found on the listed pages | check the page matches the locator in the text |
| derived | not in the paper, but a ledger row marks it derived | the ledger row must show the arithmetic |
| ledgered | not in the paper, but in a ledger row | the ledger row must give its source |
| untraced | not found in the cited papers (T001) | find the page, fix the number, or cite the right source |
| no_source | no cited paper has a text file (T002) | fetch the paper (`tundlekit papers fetch`) and re-run |

Each claim also carries `pages` (ascending), `stated_pages` (the pages the text gives, possibly empty), `weak` and
`locator_match`:

- **`weak: true`**: an integer below 1000 without `%`, or a number found on 5 or more pages. It was located, but
  it may be there by coincidence (a `12` occurs on most pages). When the text gives a locator (`[3, Table 5]`,
  `[3, p. 4]`, `(p4)`), a match on that page, or on a page holding that table or figure, sets
  `locator_match: true`.
- **T003** (info): a weak location with no locator match. **Check every weak location by hand**: open the page
  and confirm the number means what the sentence says. A weak location with a locator match still deserves a
  glance.

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
dry run prints a unified diff. An empty list is valid and writes nothing.

It also works on a `.docx` (within 1 paragraph, across runs), which keeps the owner's formatting. In a .docx, a
tab inside the text reads as `\t` and a page break as `\f` (so a `\n` edit never touches a page break); tab-stop
settings are never text, and paragraph properties are never edited. Back up first
(`tundlekit bundle backup report.docx --reason "review edits"`) and close Word: `--write` on a .docx, .pptx or
.xlsx is refused while Word, PowerPoint or Excel is running. `--force-office` overrides that, but closing Office
is the rule.

## Carrying hand edits back (`text docx-diff`)

When the owner edited the built `.docx`, compare it with the Markdown source (or with the previous build) before
regenerating:

```
tundlekit text docx-diff report.md edited/report.docx --search report-src
```

Changes are paragraph-level `replace`, `insert` and `delete` operations with a `hint` (`path:line`) where the old
text lives. An in-sync pair gives `changes: []` (image markup, list numbers, `\pagebreak`-style lines and
`{{...}}` placeholders are reduced on both sides first).

Let the tool draft the edits instead of retyping them:

```
tundlekit text docx-diff report.md edited/report.docx --search report-src --emit-edits edits.json
tundlekit text apply-edits edits.json report.md
tundlekit text apply-edits edits.json report.md --write
```

`--emit-edits` writes a `replace` change only when it has exactly 1 hint location and the old paragraph matches a
**whole paragraph** there (a Markdown paragraph with blank lines or the file edge on both sides, or a whole
Python/JSON string literal), and the `find` is at least 12 characters with a letter. Every other replacement is
listed under `not_emitted` (`old_index`, `reason`): carry those by hand. The file is a list of
`{"path": <absolute hint file path>, "edits": [{"find", "replace", "count": 1}]}` objects, 1 per target file; the
result's `edits_written` gives the count. `text apply-edits` accepts that list form and applies each object to its own
`path`, all or nothing across files. Carry `insert` and `delete` changes, and replacements with 0 or several
hints, by hand. Then rebuild and diff again.

When an edit fails, the failure lists the `lines` of every occurrence (paragraph indices in a .docx), and for a
`.py` file a `hint` when the text spans a string-literal split (`"a "` and `"b"` on 2 lines): edit those lines by
hand. A `find` or `replace` holding characters that are illegal in XML is refused before anything is written.

## Building the .docx (`report build`)

`tundlekit report build REPORT.md -o OUT.docx` (`report_build`) writes the house-style `.docx`: US Letter, Calibri
11 pt, Heading1-3, Caption, Quote, Code, ListBullet and ListNumber styles, bordered tables with a shaded header
row, figures 6.5 in wide, and a page-number footer. It needs the standard library only (no python-docx, no Pillow).

```powershell
tundlekit office check
tundlekit bundle backup "build/Report.docx" --reason "rebuild"
tundlekit report build REPORT.md -o "build/Report.docx"
tundlekit text docx-diff REPORT.md "build/Report.docx"
```

- **Office closed.** The build is refused while Word or PowerPoint is running. `--force-office` overrides that,
  but closing Office is the rule.
- **Back up first.** Snapshot the previous build with `tundlekit bundle backup` before every rebuild.
- **Nothing is written until the whole report parses.** Every problem is listed at once as `line N: …`: a missing
  or non-PNG/JPEG figure, a remote image, a missing excerpt, an unknown `{{…}}` placeholder, an unterminated
  fence, a level 4-6 heading, a stray `|` line, a table row with too many cells, list or heading syntax inside a
  quote. Fix the Markdown; these are errors, never noise.
- **Hand-edit guard.** When OUT.docx exists, it is compared with the report first (as `text docx-diff` does). If
  the owner edited it (any change, or an unreadable file), the build stops, names `--overwrite` and gives the
  number of changes. Carry the edits back first (`text docx-diff … --emit-edits`, see above), then rebuild.
  Use `--overwrite` only when the edits are carried or meant to be dropped. An in-sync file is replaced without
  asking.
- **Excerpts.** A whole line `{{excerpt:name|Caption text}}` becomes the text of `EXCERPTS/name.txt` as a small
  code block plus a caption. The folder defaults to `<report dir>/excerpts`, then `<report dir>/build/excerpts`;
  pass `--excerpts DIR` otherwise (the capsule report uses the general report's `build/excerpts`).
- **Author.** `--author NAME`, else the `TUNDLEKIT_AUTHOR` environment variable, else `git config user.name` in the
  report's folder, else empty. The title is the first level-1 heading.
- **Supported Markdown**: headings 1-3, paragraphs, `-`/`*`/`+` and `1.` lists (2 levels), `>` quotes (plain
  text), fenced code, pipe tables, whole-line PNG/JPEG figures `![Caption](fig.png)` (the alt text is the
  caption), paragraphs `*Table N. …*` as captions, `\pagebreak`, bold, italic and inline code. Links become
  plain text, HTML comments and front matter are dropped, and raw HTML stays literal text. Footnotes, math,
  level 4-6 headings, merged cells and alignment are not supported.
- **Warnings** (the build still succeeds): `inline image not embedded` and `table columns squeezed below their
  longest word`.

**Acceptance check.** `tundlekit text docx-diff REPORT.md OUT.docx` gives `changes: []` for a report without
excerpts; with excerpts, only `insert` changes for the excerpt text and its caption. The build does not check
layout (page count, line breaks, figure placement): render it with `tundlekit render office` and read the pages
(deliverable-review skill).

## Reading pages

Private HTML reading pages (a sliced, single-file view of the report per audience) follow the `build_reading.py`
pattern. No tundlekit command builds them: the script keeps its own Markdown renderer, and the pages do not
depend on tundlekit.

- **Source.** Slice the annotated report variant (`REPORT-annotated.md`, the one that keeps anchors and code
  locations), never a copy of it.
- **Fail loudly.** Slice with `between(start, end, src=…)` and `section(num, next)` helpers that exit non-zero and
  name the marker when it is missing. Never publish a stale or half-sliced page. Check counts that must hold
  ("5 gap items") the same way.
- **1 file.** Inline every figure as a `data:image/png;base64,…` URI, and stop when a figure file is missing.
  Expand `{{excerpt:name|caption}}` as a fenced block plus an italic caption.
- **Catch moved markers before building.** Pair the build folder (or the script) with the report it slices, and
  bind the slice source at module level (`SRC = HERE.parent / "REPORT-annotated.md"`), so the check reads the
  right file. Pass the pair to `tundlekit text xref` as `--in FILE=REPORT` (FILE is the script or its folder,
  REPORT the file it slices). PowerShell, from the report's folder:

  ```powershell
  tundlekit text xref --in build\=REPORT-annotated.md
  ```

  X002 means a marker moved or is duplicated: fix the marker or the heading before building. X003 means the
  slice source could not be resolved: check that marker by hand. In Git Bash, write
  `"build/=REPORT-annotated.md"` (quoted, forward slashes; see the Git Bash note above).
- **Rebuild after every report edit**, together with the other outputs: the `.docx` with
  `tundlekit report build` (`report_build`) and the paper-summaries page with `tundlekit papers page`
  (`papers_page`):

  ```powershell
  tundlekit report build REPORT.md -o "build/Report.docx"
  tundlekit papers page REPORT.md -o "build/paper-summaries.html" --dir papers
  python build/build_reading.py
  ```

`papers page` gives 1 card per cited arXiv id that has a `papers/summaries/{id} - *.md` file, grouped by the
numbered sections of `summaries/INDEX.md`, with an "In the report" line from the report's `Used for` table column.
Cited ids without a summary are listed on the page and warned about (`--strict` makes that exit 1): write those
summaries (paper-reading skill).

## Word counts (`text wordcount`)

`text wordcount` lists words per heading (levels 1-3), the total, and `buckets`: `body`, `appendix` (from a level-2
`Appendix` heading) and `references` (from `References` / `Bibliography`), so a body limit can be checked apart from
the appendices. `--baseline GITREF` compares with a git revision and `--baseline-file OLD.md` with another file
(not both); each section gets its change (`"new"` for new headings). `--no-tables` leaves table rows out. Use it to
keep sections balanced and to report what an edit grew or shrank.

## Known noise

Checker output is a starting list to confirm, not a verdict. The remaining false positives per tool:

- `text lint`: S003 still fires on permission "may be" + a participle outside the short irregular list ("may be
  read", "may be sent"); S009 on long definitional sentences that read fine; S011 on "pp" inside quoted text.
- `text fignums`: F005 on a mention of another document's figure or table that is not preceded by "arXiv" or
  "paper" ("the capsule deck's Fig. 2"). Reword it, or resolve the file with `--refs NOTES.md=REPORT.md`.
- `text xref`: X001 on references into another document whose name does not end in "report" ("the design note
  §3"). X003 is a skipped check, never noise to ignore.
- `claims trace`: low priority and unreliable overall (see above). T001 on numbers that are counts or setup details rather than paper results ("12 slides"), and
  on numbers the paper writes in another form (a fraction, a rounded value, a plot reading); add a ledger row.
  Weak locations (T003) may be coincidences. T004 means nothing was checked.
- `text docx-diff`: template text in the .docx (title page, table of contents) shows as `insert`.
- `text wordcount`: no known false positives; headings below level 3 count toward their parent.
- `report build`: none known. Markdown outside the supported list is an error, not noise.

## Before handing over

- [ ] `tundlekit text lint` clean (no errors; every warning fixed or explained)
- [ ] `tundlekit text fignums` clean, with the deck notes passed as `--refs`
- [ ] `tundlekit text xref` clean for the deck script and notes, each paired with the report it slices, and every
  X003 checked by hand
- [ ] if `tundlekit claims trace` was run (optional; unreliable): no untraced numbers and no T004, and every weak location (T003) is checked by
  hand
- [ ] every paper named by title in each section that uses it; every number traced to a page, table or file:line
- [ ] every claim bounded by a labelled limitations list where it needs one; status stated in plain words
- [ ] coverage matches the deck (`tundlekit review coverage REPORT.md DECK.pptx`); rule names and counts match
- [ ] the .docx built with `tundlekit report build`, and `tundlekit text docx-diff REPORT.md OUT.docx` gives
  `changes: []` (only excerpt inserts); reading pages and `tundlekit papers page` rebuilt after the last edit
- [ ] `tundlekit office check` passes before the .docx is built; previous version backed up with
  `tundlekit bundle backup REPORT.docx --reason "CHANGE"` before every write; the rendered document reviewed page by page
  (deliverable-review skill)
