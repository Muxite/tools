# tundlekit

Agent-agnostic tools and working rules for keeping a transfer bundle ("tundle"), building decks and diagrams,
checking report prose, building the report .docx, rendering deliverables, reading arXiv papers and checking Chinese ↔ English translations.

Every tool is available 3 ways, from the same code:

- a **CLI**, `tundlekit <group> <command>`, for any agent (or person) that can run shell commands;
- an **MCP server**, `tundlekit-mcp` (stdio), for agents that speak the Model Context Protocol;
- **skills** in [`skills/`](skills/), instruction packs in the open Agent Skills format (`skills/<name>/SKILL.md`)
  that say when and how to use the tools.

[AGENTS.md](AGENTS.md) explains how to wire the MCP server and the skills into Claude Code, Codex CLI, Gemini CLI
and other clients. [MANIFEST.md](MANIFEST.md) is the full contract for every command, tool and file format.

## Install

Python 3.10 or newer. From the repository root:

```
pip install -e .[all]
```

The core (CLI, MCP server, bundle, diagram, chart, palette, text, report, papers without text extraction,
translate)
needs only the standard library, so `pip install -e .` is enough for those. Extras:

| Extra | Packages | Needed for |
|---|---|---|
| `office` | python-pptx, Pillow | building, inspecting and packing decks, contact sheets, rendering .pptx |
| `pdf` | pymupdf | rendering PDF pages, extracting paper text |
| `all` | both | everything |
| `dev` | all + pytest | running the tests |

Optional external programs: `git` (bundle commands), LibreOffice or PowerPoint (rendering Office files),
`pdftotext` (paper text without pymupdf), `cairosvg` / `rsvg-convert` / `inkscape` (SVG to PNG).
`tundlekit render backends` shows what is available.

Check the install:

```
tundlekit --version
tundlekit tools
```

## Command overview

Every command accepts `--json` (the tool result as JSON on stdout). Exit codes: 0 success, 1 a check found
errors or the tool failed, 2 usage error. Checkers accept `--strict` (warnings fail too).

| Group | Commands | What for |
|---|---|---|
| `tundlekit bundle ...` | `status`, `release`, `compare`, `prune`, `init`, `lint`, `verify`, `source`, `setup-table`, `backup` | keep a tundle: versioned releases, copy comparison, history clearing, portable names, setup tables, SOURCE.md and per-file `<name>.SOURCE.md` files (1 file, or a whole folder with `source DIR --all`) and checksums, and `versions/` snapshots before an edit (`backup`) |
| `tundlekit deck ...` | `build`, `lint`, `inspect`, `diff`, `pack` | PowerPoint decks from a JSON spec (native single- and multi-series charts, monospace table columns); timing and speaker-note rules, several decks against 1 times file (`lint --ids`); hand edits, cuts, moves and renumbering carried back; presenter packs drafted from a built deck and checked against it after cuts (`pack --check`) |
| `tundlekit diagram ...` | `render`, `validate`, `from-mermaid`, `to-mermaid` | SVG/PNG diagrams (colour = stage, style = actor) from a spec or Mermaid, with group-aware wrapping |
| `tundlekit chart ...` | `bar` | SVG bar charts with a highlighted bar and a takeaway |
| `tundlekit palette ...` | `show` | the stage and outcome colours and the diagram rules |
| `tundlekit text ...` | `lint`, `fignums`, `wordcount`, `xref`, `apply-edits`, `docx-diff` | report style lint, figure/table numbering, words per section, cross-references and renumbering (each file paired with its own report), anchored edits across files, .docx hand edits (`docx-diff --emit-edits` drafts the edits file) |
| `tundlekit report build` | `build` | the house-style .docx from a Markdown report (standard library only), refusing to overwrite hand edits |
| `tundlekit review coverage` | `coverage` | does the deck cover the report, section by section and rule by rule |
| `tundlekit claims trace` | `trace` | is every cited number on a page of the cited paper |
| `tundlekit render ...` | `pdf`, `sheet`, `office`, `backends` | render PDFs and Office files to PNG, contact sheets |
| `tundlekit office check` | `check` | are Word, PowerPoint or Excel running? Run it before any build or render (exit 1 while they are; `--wait` polls) |
| `tundlekit papers ...` | `fetch`, `list`, `abs`, `grep`, `body`, `summary`, `index-check`, `page` | download arXiv papers, read them page by page, keep summaries and their index complete, build a self-contained HTML page of the summaries a report cites |
| `tundlekit translate ...` | `check`, `resources`, `terms` | zh ↔ en translation checks, term carry-over, rules, glossary and prompts |

Examples:

```
tundlekit bundle status
tundlekit bundle release "Added the September report"
tundlekit bundle source setup --all
tundlekit bundle backup reports/report.docx --reason "cut section 4"
tundlekit office check --wait 60
tundlekit deck lint examples/deck.json
tundlekit deck build examples/deck.json -o build/example.pptx
tundlekit diagram render examples/diagram.json -o build/diagram.svg
tundlekit diagram render examples/flow.mmd -o build/flow.svg
tundlekit chart bar examples/chart.json -o build/chart.svg
tundlekit palette show --json
tundlekit text lint report.md
tundlekit report build report.md -o build/report.docx
tundlekit text docx-diff report.md build/report.docx
tundlekit deck pack build/example.pptx -o notes/PRESENTER-PACK.md
tundlekit deck pack build/example.pptx --check notes/PRESENTER-PACK.md
tundlekit papers page report.md -o build/paper-summaries.html --dir papers
tundlekit render office build/example.pptx -o .review/example
tundlekit papers fetch 2604.00392 --dir papers
tundlekit translate check all source.zh.md translation.en.md --dir zh-en
tundlekit review coverage report.md build/example.pptx
tundlekit claims trace report.md --papers papers
tundlekit deck diff build/example.pptx edited/example.pptx --search examples
tundlekit text docx-diff report.md edited/report.docx --search . --emit-edits edits.json
tundlekit text apply-edits edits.json report.md --write
tundlekit text xref report.md --in build_deck.py=report.md notes --exclude "*/versions/*"
```

Any registered tool can also be run by name with JSON arguments:

```
tundlekit tools --json
tundlekit call palette_get --args '{}'
```

## What each command needs

| Command | Speeds up / improves | Needs | Writes files? |
|---|---|---|---|
| `bundle status`, `compare`, `lint`, `verify` | checking a copy before editing or copying it; catching unportable names, junk, stale PDFs, bad checksums | Python, `git` | no |
| `bundle source`, `bundle setup-table` | drafting SOURCE.md files and setup README rows from file names, existing README rows and hashes instead of typing them (dry run by default); `bundle source DIR --all` drafts every missing SOURCE.md in a folder tree | Python | with `--write` |
| `bundle backup` | snapshotting files into the nearest `versions/` folder as `<stem> (before <reason> <date>)<ext>` before an edit, instead of copying by hand; refuses while Word, PowerPoint or Excel is running (`--force-office` overrides, but closing Office is the rule), never overwrites without `--overwrite`, lists older `(before ...)` snapshots as `superseded` and deletes them with `--prune` | Python | yes (a copy; `--prune` **deletes** older snapshots) |
| `bundle release`, `init` | 1-command versioned release with a CHANGELOG entry | Python, `git`, a git identity | yes (commit) |
| `bundle prune` | clearing old history safely (dry run by default) | Python, `git` | yes (**rewrites history**; needs `--yes`) |
| `deck build`, `deck inspect` | building a timed, rule-following deck from JSON, including native `series` charts (multi-series bar and line, with a legend), `mono_cols` tables and strip-overlap warnings; reading any deck's text and notes | `office` extra | build: yes |
| `deck lint` | speaker-note timing, meta/defensive notes, insert-slide rules; several decks against 1 shared times file (`--ids` when its keys are not the file stems) | spec: nothing; `.pptx`: `office` extra | no |
| `deck pack` | a presenter pack skeleton (crib line per slide, IF ASKED bullets, timing table) from a built deck; `--check PACK.md` finds a stale pack after cuts and reorders (K001-K006: wrong slide count or times, crib keys naming no slide, slides without a crib line, stale titles, poor matches) | `office` extra | with `-o` (never over an existing pack without `--force`); `--check`: no |
| `report build` | building the house-style .docx from the Markdown report (headings, lists, quotes, code, tables, PNG/JPEG figures, excerpts, captions, page-number footer) instead of a per-report script; every Markdown problem listed at once; refuses to replace a .docx with hand edits (`--overwrite` overrides); `text docx-diff REPORT.md OUT.docx` giving `changes: []` is the acceptance check | nothing (standard library only); Word and PowerPoint closed (`--force-office` overrides) | yes (the .docx; back it up first with `bundle backup`) |
| `deck diff` | finding a person's edits, cuts, moves and renumbering in a built deck and the source lines to change, instead of comparing slides by eye | `office` extra | no |
| `office check` | knowing Word, PowerPoint and Excel are closed before a build or render writes an Office file (`--wait SECONDS` polls) | Windows: `tasklist`; elsewhere `ps` (looks for LibreOffice) | no |
| `review coverage` | report ↔ deck coverage and rule-name check in seconds, instead of a side-by-side read | spec: nothing; `.pptx`: `office` extra | no |
| `claims trace` | locating every cited number on a page of its paper, instead of opening each paper by hand | papers' `.txt` files; `[n]` references or name + `(pN)` locators in the report | no |
| `diagram render` / `validate` / `from-mermaid` / `to-mermaid` | consistent stage/actor diagrams with auto layout, group-aware wrapping, `%% rank` / `%% wrap` in Mermaid | nothing (PNG: `cairosvg`, `rsvg-convert` or Inkscape; pymupdf as a limited fallback) | render: yes |
| `chart bar` | a highlighted bar chart with data labels and a takeaway | nothing | with `-o` |
| `palette show` | the shared colour rules | nothing | no |
| `text lint`, `fignums`, `wordcount` | style-card prose checks, numbering, per-section and per-bucket word counts | nothing (`--baseline`: `git`) | no |
| `text xref` | checking § / App. / Fig. / Table references in scripts and notes, each against the report it slices (`--in FILE=REPORT`, `--exclude`), and renumbering them all at once, including whole appendices (`--renumber "App. E=App. D"`; `--renumber-report` when several reports hold the reference) | nothing | with `--write` |
| `text apply-edits` | applying review edits as anchored replacements (fails instead of silently missing), also inside .docx, and a list of per-file edits all or nothing | nothing | with `--write` |
| `text docx-diff` | carrying hand edits in a .docx back into the Markdown source, with source line hints; `--emit-edits` writes them as an edits file for `text apply-edits` | nothing | only the `--emit-edits` file |
| `render pdf`, `render sheet` | page PNGs and contact sheets for eyeballing a deliverable | `pdf` extra / `office` extra | yes |
| `render office` | render a .pptx/.docx from a copy, never the original | text backend: nothing (`.pptx` needs `office`); PNG: PowerPoint + pywin32 on Windows, or LibreOffice | yes (only into a new, empty or earlier render folder) |
| `papers fetch` | download arXiv PDFs and extract page-marked text | network; `pdf` extra or `pdftotext` for text | yes |
| `papers list`, `abs`, `grep`, `body` | reading a paper and tracing a number to its page; flags 2-column layout text | nothing | no |
| `papers page` | a single-file HTML page (no external requests, light/dark, search box) with 1 card per cited paper from its summary, grouped as in INDEX.md, with missing summaries listed | nothing (standard library only) | yes (the .html, overwritten every run) |
| `papers summary`, `papers index-check` | summary skeletons with title, authors and pages filled in; finding missing summaries and index rows | nothing | summary: with `--write` |
| `translate check`, `resources` | mechanical zh ↔ en checks; the glossary, rules and prompts | nothing | `--repair` only |
| `translate terms` | spotting technical terms dropped between a source and its translations, across Chinese hops (`--compare same-language`, glossary renderings as L003, `--no-glossary`) | nothing | no |

## Safety notes

- `bundle` commands only ever act on the tundle root. Git environment variables such as `GIT_DIR` are ignored,
  and a root that is not the top folder of its own git repository is refused.
- `bundle prune --yes` deletes every ref except the current branch and garbage-collects the dropped versions.
  Copy the result over the other copies afterwards (see the `tundle-bundle` skill).
- `render office` refuses output folders that are a filesystem root, the home folder, the current folder, the
  source's folder, any ancestor of those, or a folder containing `.git`. It only empties a folder that is new,
  empty, or marked by an earlier render (`.tundlekit-render`).
- The MCP server never exits on bad input, and tool output never reaches its stdout.

## Known limits

- `render office` makes PNGs only with PowerPoint (Windows, pywin32) or LibreOffice. Without them it produces text
  dumps.
- Text made by `pdftotext -layout` interleaves 2-column pages. `papers body` and `papers list` flag it
  (`layout_text`); re-extract with `tundlekit papers fetch ID --reextract` (needs pymupdf for reading-order text).
- `review coverage` matches sections by their numbers (`§2.3` in slide footers) or by title similarity; unnumbered
  headings and slides without a footer are matched only by title, so cite the report section in every footer.
- `claims trace` is deliberately low priority and is **not reliable**: it is not a release gate, it misses
  numbers and it matches numbers by coincidence. Do not treat its output as a check; trace numbers by hand. In
  detail: it finds numbers as written (plus percent ↔ decimal). A number the paper states in another form
  (a fraction, a rounded value, a figure read off a plot) shows as untraced until it has a ledger row, and a located
  number may still be the wrong quantity. Only references with an arXiv id are traced, and only `[n]` references
  or a paper name with its id plus a `(pN)` locator count as citations. A report with neither gives 0 claims and a
  T004 warning: that is not a pass. Small integers and numbers found on many pages are marked `weak` (T003 when no
  stated page or table matches) and need a check by hand.
- `papers summary` writes a scaffold, not a summary: the title, authors and page counts are guessed from the first
  page (check them), and every section still needs a person to read the paper and write it.
- `report build` supports a fixed Markdown subset (headings 1-3, paragraphs, lists 2 levels deep, plain quotes,
  fenced code, pipe tables, whole-line PNG/JPEG figures, `{{excerpt:name|caption}}`, page breaks). Anything else
  (level 4-6 headings, footnotes, math, remote images, merged cells) is an error; links become plain text and raw
  HTML stays literal. It does not check layout: render the .docx and read the pages.
- `deck pack --check` compares crib lines with slides by shared key words; a hand-written crib line that
  paraphrases its slide (dividers especially) can give a false K005.
- `text xref` resolves a build script's slice source only from string literals and `__file__`-based anchors;
  anything else gives X003 (info) and that marker is not checked. References to another document whose name does
  not end in "report" are still checked against the paired report.
- `deck diff` pairs slides only while their titles stay at least 0.4 similar; a slide retitled beyond that shows as
  `removed` plus `added`.
- `deck build` overflow warnings come from a characters-per-line estimate; the rendered slide decides.
- The pymupdf PNG fallback of `diagram render` keeps arrowheads (drawn as paths) and dashes, and names anything
  else it cannot reproduce in `warnings`. Use `cairosvg`, `rsvg-convert` or Inkscape for exact PNGs.
- `office check` sees Word, PowerPoint and Excel (LibreOffice outside Windows) only; it does not detect other
  programs holding a file open, and on non-Windows systems without LibreOffice running it always reports `ok`.
- `bundle backup` prefixes a snapshot with its folder label (`notes-report-capsules REPORT (before …).md`) when
  the file sits below the folder holding `versions/`, so same-named files from different folders never collide.
  A snapshot `--prune` could not delete is listed under `not_pruned` (never `pruned`) and the command exits 1.
- `bundle source` and `bundle setup-table` guess program names and versions from file names (or reuse an existing
  README row); check them. Junk files and names with a backtick or `|` are listed as `skipped`, never added.
- `translate check` and `translate terms` find mechanical damage only. Faithfulness needs the critic step
  (`zh-en-translation` skill). `translate terms` downgrades a missing term to L003 only when the glossary has an
  approved Chinese rendering and the file is mostly Chinese.
- `text apply-edits` on a .docx edits text within 1 paragraph; it does not add or remove paragraphs.
  `docx-diff --emit-edits` covers only `replace` changes with exactly 1 source location whose old text is a whole
  paragraph there (a Markdown paragraph or a whole string literal) and at least 12 characters; the rest are listed
  under `not_emitted` for manual work. `--write` on an Office file is refused while Office is running
  (`--force-office` overrides).
- `FILE=REPORT` and `OLD=NEW` arguments are shown in PowerShell form. Git Bash (MSYS) may rewrite an `A=B`
  argument whose right side looks like an absolute path; keep such paths relative, quote the argument, or set
  `MSYS2_ARG_CONV_EXCL="*"`, or use PowerShell.
- `translate terms` reports the line (`line`) in the compared file (`compared`), not in the flagged file (`path`). Use
  `--compare same-language` for round trips (zh → en → zh), or the back-translation is compared with the middle
  hop.
- Every checker's output is a starting list to confirm. Each skill lists the known remaining false positives
  (noise) of the tools it runs.

## How the tools are built

[MANIFEST.md](MANIFEST.md) is the contract. For each change, one agent writes tests from the manifest: a visible
suite (in `tests/`) and a held-out suite that the implementer never sees. A separate agent implements from the
manifest and the visible tests only. The change is accepted when both suites pass. Adversarial reviews then look
for defects and usefulness gaps on real material, and their findings become new manifest sections (§13 to §16),
with tests first. The [`held-out-build-gate`](skills/held-out-build-gate/SKILL.md) skill describes the method.

## MCP server

```
tundlekit-mcp [--root PATH]
python -m tundlekit.mcp_server
```

It speaks MCP over stdio (1 JSON-RPC message per line) and exposes every tool listed by `tundlekit tools`, with
the same names (`bundle_status`, `deck_build`, `diagram_render`, `text_lint`, `review_coverage`, `claims_trace`,
`report_build`, `deck_pack`, `papers_page`, `papers_fetch`, …). `--root` sets
the default tundle for the bundle tools. Configuration snippets for common agents are in [AGENTS.md](AGENTS.md).

## Skills

| Skill | Use it for |
|---|---|
| [`tundle-bundle`](skills/tundle-bundle/SKILL.md) | keeping a tundle: release cycle, copying, history clearing, lint, setup tables, SOURCE.md |
| [`deck-builder`](skills/deck-builder/SKILL.md) | writing and building a deck spec; slide, note and timing rules; insertion slides |
| [`diagram-maker`](skills/diagram-maker/SKILL.md) | diagrams by the stage/actor rules, the Mermaid subset, bar charts |
| [`report-writing`](skills/report-writing/SKILL.md) | the style card voice, claim → limitations lists, report rules, text checks, building the .docx, reading pages |
| [`deliverable-review`](skills/deliverable-review/SKILL.md) | render, contact sheets, adversarial review against flaw classes |
| [`paper-reading`](skills/paper-reading/SKILL.md) | fetching and reading papers, citation rules, summary files |
| [`zh-en-translation`](skills/zh-en-translation/SKILL.md) | translation tiers, the translator + critic pipeline, checks |
| [`held-out-build-gate`](skills/held-out-build-gate/SKILL.md) | building a capability behind a manifest, held-out tests and a capped gate |
| [`review-prompts`](skills/review-prompts/SKILL.md) | ready briefs for fresh-context reviewers: so-what, first-time reader, adversarial flaw classes, fact-check |

Example inputs are in [`examples/`](examples/): a deck spec, a diagram spec, a Mermaid flowchart and a chart spec.

## Tests

```
python -m pytest
```

Tests that need an optional package or program skip when it is missing.
