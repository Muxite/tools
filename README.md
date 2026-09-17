# tundlekit

Agent-agnostic tools and working rules for keeping a transfer bundle ("tundle"), building decks and diagrams,
checking report prose, rendering deliverables, reading arXiv papers and checking Chinese ↔ English translations.

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

The core (CLI, MCP server, bundle, diagram, chart, palette, text, papers without text extraction, translate)
needs only the standard library, so `pip install -e .` is enough for those. Extras:

| Extra | Packages | Needed for |
|---|---|---|
| `office` | python-pptx, Pillow | building and inspecting decks, contact sheets, rendering .pptx |
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
| `tundlekit bundle ...` | `status`, `release`, `compare`, `prune`, `init`, `lint`, `verify`, `source`, `setup-table` | keep a tundle: versioned releases, copy comparison, history clearing, portable names, setup tables, SOURCE.md files and checksums |
| `tundlekit deck ...` | `build`, `lint`, `inspect`, `diff` | PowerPoint decks from a JSON spec; timing and speaker-note rules; hand edits carried back |
| `tundlekit diagram ...` | `render`, `validate`, `from-mermaid`, `to-mermaid` | SVG/PNG diagrams (colour = stage, style = actor) from a spec or Mermaid |
| `tundlekit chart ...` | `bar` | SVG bar charts with a highlighted bar and a takeaway |
| `tundlekit palette ...` | `show` | the stage and outcome colours and the diagram rules |
| `tundlekit text ...` | `lint`, `fignums`, `wordcount`, `xref`, `apply-edits`, `docx-diff` | report style lint, figure/table numbering, words per section, cross-references and renumbering, anchored edits, .docx hand edits |
| `tundlekit review coverage` | `coverage` | does the deck cover the report, section by section and rule by rule |
| `tundlekit claims trace` | `trace` | is every cited number on a page of the cited paper |
| `tundlekit render ...` | `pdf`, `sheet`, `office`, `backends` | render PDFs and Office files to PNG, contact sheets |
| `tundlekit papers ...` | `fetch`, `list`, `abs`, `grep`, `body`, `summary`, `index-check` | download arXiv papers, read them page by page, keep summaries and their index complete |
| `tundlekit translate ...` | `check`, `resources`, `terms` | zh ↔ en translation checks, term carry-over, rules, glossary and prompts |

Examples:

```
tundlekit bundle status
tundlekit bundle release "Added the September report"
tundlekit deck lint examples/deck.json
tundlekit deck build examples/deck.json -o build/example.pptx
tundlekit diagram render examples/diagram.json -o build/diagram.svg
tundlekit diagram render examples/flow.mmd -o build/flow.svg
tundlekit chart bar examples/chart.json -o build/chart.svg
tundlekit palette show --json
tundlekit text lint report.md
tundlekit render office build/example.pptx -o .review/example
tundlekit papers fetch 2604.00392 --dir papers
tundlekit translate check all source.zh.md translation.en.md --dir zh-en
tundlekit review coverage report.md build/example.pptx
tundlekit claims trace report.md --papers papers
tundlekit deck diff build/example.pptx edited/example.pptx --search examples
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
| `bundle source`, `bundle setup-table` | drafting SOURCE.md files and setup README rows from file names and hashes instead of typing them (dry run by default) | Python | with `--write` |
| `bundle release`, `init` | 1-command versioned release with a CHANGELOG entry | Python, `git`, a git identity | yes (commit) |
| `bundle prune` | clearing old history safely (dry run by default) | Python, `git` | yes (**rewrites history**; needs `--yes`) |
| `deck build`, `deck inspect` | building a timed, rule-following deck from JSON; reading any deck's text and notes | `office` extra | build: yes |
| `deck lint` | speaker-note timing, meta/defensive notes, insert-slide rules; several decks against 1 shared times file | spec: nothing; `.pptx`: `office` extra | no |
| `deck diff` | finding a person's edits in a built deck and the source lines to change, instead of comparing slides by eye | `office` extra | no |
| `review coverage` | report ↔ deck coverage and rule-name check in seconds, instead of a side-by-side read | spec: nothing; `.pptx`: `office` extra | no |
| `claims trace` | locating every cited number on a page of its paper, instead of opening each paper by hand | papers' `.txt` files | no |
| `diagram render` / `validate` / `from-mermaid` / `to-mermaid` | consistent stage/actor diagrams with auto layout | nothing (PNG: `cairosvg`, `rsvg-convert` or Inkscape) | render: yes |
| `chart bar` | a highlighted bar chart with data labels and a takeaway | nothing | with `-o` |
| `palette show` | the shared colour rules | nothing | no |
| `text lint`, `fignums`, `wordcount` | style-card prose checks, numbering, per-section and per-bucket word counts | nothing (`--baseline`: `git`) | no |
| `text xref` | checking § / App. / Fig. / Table references in scripts and notes, and renumbering them all at once | nothing | with `--write` |
| `text apply-edits` | applying review edits as anchored replacements (fails instead of silently missing), also inside .docx | nothing | with `--write` |
| `text docx-diff` | carrying hand edits in a .docx back into the Markdown source, with source line hints | nothing | no |
| `render pdf`, `render sheet` | page PNGs and contact sheets for eyeballing a deliverable | `pdf` extra / `office` extra | yes |
| `render office` | render a .pptx/.docx from a copy, never the original | text backend: nothing (`.pptx` needs `office`); PNG: PowerPoint + pywin32 on Windows, or LibreOffice | yes (only into a new, empty or earlier render folder) |
| `papers fetch` | download arXiv PDFs and extract page-marked text | network; `pdf` extra or `pdftotext` for text | yes |
| `papers list`, `abs`, `grep`, `body` | reading a paper and tracing a number to its page; flags 2-column layout text | nothing | no |
| `papers summary`, `papers index-check` | summary skeletons with title, authors and pages filled in; finding missing summaries and index rows | nothing | summary: with `--write` |
| `translate check`, `resources` | mechanical zh ↔ en checks; the glossary, rules and prompts | nothing | `--repair` only |
| `translate terms` | spotting technical terms dropped between a source and its translations | nothing | no |

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
- `claims trace` finds numbers as written (plus percent ↔ decimal). A number the paper states in another form
  (a fraction, a rounded value, a figure read off a plot) shows as untraced until it has a ledger row, and a located
  number may still be the wrong quantity. Only references with an arXiv id are traced.
- `bundle source` and `bundle setup-table` guess program names and versions from file names; check them.
- `translate check` and `translate terms` find mechanical damage only. Faithfulness needs the critic step
  (`zh-en-translation` skill).
- `text apply-edits` on a .docx edits text within 1 paragraph; it does not add or remove paragraphs.

## How the tools are built

[MANIFEST.md](MANIFEST.md) is the contract. For each change, one agent writes tests from the manifest: a visible
suite (in `tests/`) and a held-out suite that the implementer never sees. A separate agent implements from the
manifest and the visible tests only. The change is accepted when both suites pass. Adversarial reviews then look
for defects and usefulness gaps on real material, and their findings become new manifest sections (§13, §14),
with tests first. The [`held-out-build-gate`](skills/held-out-build-gate/SKILL.md) skill describes the method.

## MCP server

```
tundlekit-mcp [--root PATH]
python -m tundlekit.mcp_server
```

It speaks MCP over stdio (1 JSON-RPC message per line) and exposes every tool listed by `tundlekit tools`, with
the same names (`bundle_status`, `deck_build`, `diagram_render`, `text_lint`, `review_coverage`, `claims_trace`,
`papers_fetch`, …). `--root` sets
the default tundle for the bundle tools. Configuration snippets for common agents are in [AGENTS.md](AGENTS.md).

## Skills

| Skill | Use it for |
|---|---|
| [`tundle-bundle`](skills/tundle-bundle/SKILL.md) | keeping a tundle: release cycle, copying, history clearing, lint, setup tables, SOURCE.md |
| [`deck-builder`](skills/deck-builder/SKILL.md) | writing and building a deck spec; slide, note and timing rules; insertion slides |
| [`diagram-maker`](skills/diagram-maker/SKILL.md) | diagrams by the stage/actor rules, the Mermaid subset, bar charts |
| [`report-writing`](skills/report-writing/SKILL.md) | the style card voice, claim → limitations lists, report rules, text checks |
| [`deliverable-review`](skills/deliverable-review/SKILL.md) | render, contact sheets, adversarial review against flaw classes |
| [`deliverable-production`](skills/deliverable-production/SKILL.md) | running the whole project: production order, reading it aloud early, lanes for several agents, the hand-back package |
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
