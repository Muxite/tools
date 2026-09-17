---
name: paper-reading
description: Fetch arXiv papers, extract their text, and read them efficiently with tundlekit papers (fetch, list, abs, grep, body), then write a per-paper summary file in a fixed format. Enforces the citation rules - cite by paper title and arXiv id, never by nickname or author names - and traces every number to a page. Use when asked to find, download, read, summarise, compare or cite research papers, to verify a number or quote from a paper, or to build a literature index for a report or deck.
---

# Reading papers

| Task | CLI | MCP tool |
|---|---|---|
| download PDFs and extract text | `tundlekit papers fetch 2604.00392 2604.01687 [--dir papers] [--delay 3]` | `papers_fetch` |
| what is here (pdf, txt, pages, summary file) | `tundlekit papers list [--dir papers]` | `papers_list` |
| the abstract | `tundlekit papers abs 2604.00392 [--chars 2200] [--dir papers]` | `papers_peek` (`mode` = abstract) |
| lines matching a regex, with page numbers | `tundlekit papers grep 2604.00392 "silent rot" [--context 2] [--max-hits 12] [--width 200]` | `papers_peek` (`mode` = grep) |
| the main body, page-marked, up to the references (`--appendix`: to the last page) | `tundlekit papers body 2604.00392 [--start 1] [--end 7] [--max-chars 90000] [--appendix]` | `papers_body` |
| a summary file skeleton (title, authors, pages filled in) | `tundlekit papers summary 2604.00392 [--short NAME] [--write]` | `papers_summary` |
| summaries vs papers vs INDEX.md vs a report's references | `tundlekit papers index-check [--index PATH] [--report REPORT.md]` | `papers_index_check` |

Files live in 1 folder (`--dir`, default the current directory): `{id}.pdf`, `{id}.txt`, and summaries in
`summaries/{id} - {short title}.md`. Old-style ids (`cs/0112017`) are stored with `_` for `/`.
Text extraction uses pymupdf (`pip install -e ".[pdf]"`) or `pdftotext`; without either, the PDF is kept and the
result says `text: false`. `fetch` skips PDFs already present, waits `--delay` seconds between downloads (be
polite to arXiv), and never lets 1 failed id stop the others; check `ok` and each `status`.
`--base-url` or the `TUNDLEKIT_ARXIV_BASE` environment variable points at a mirror. `--reextract` rewrites the
`.txt` from the PDF even when it exists. `papers list` also reports `missing_summary` (ids with no summary file)
and `layout_text` per paper.

**Layout-text trap.** Text made by `pdftotext -layout` keeps the page's columns side by side, so 2-column papers
come out with sentences from both columns interleaved on each line. It reads plausibly and misattributes numbers.
`papers body` and `papers list` flag such files (`layout_text: true`, plus a warning in `body`). Re-extract before
reading or quoting:

```
tundlekit papers fetch 2604.00392 --dir papers --reextract
```

## Reading procedure

1. **Fetch** every paper that will be cited. Never cite a paper that was not opened.
2. **Triage with the abstract**: `tundlekit papers abs ID`. Decide whether the paper matters and what to look for.
3. **Read the body**: `tundlekit papers body ID`. It runs from page 1 to the references page, with each page
   marked `[pN]`, so every statement can be located. Long papers: read in ranges (`--start 1 --end 6`, then
   `--start 7 --end 12`); `truncated: true` means text was cut at `--max-chars`. Appendices sit after the
   references: add `--appendix` (the range then runs to the last page) or give an explicit `--start`.
   Check `warnings` first: a layout-text warning means re-extract (above).
4. **Locate specifics with grep**: `tundlekit papers grep ID "Table 5|held-out"`. Each hit gives `page` and
   `line`, the anchor for a citation. Grep is case-insensitive; widen `--context` to see a whole table row, and
   use `--width 200` to cut each hit to 200 characters around the match when a term occurs many times.
5. **Check every number you will repeat** at its page: the value, the unit, the setup (data, model, n) and what
   exactly was measured. Note the page next to it.
6. **Write the summary file** (format below) before using the paper anywhere else.

## Citation rules

- **Cite by title and arXiv id**: "Beyond Task Completion (arXiv 2604.00392)". People remember titles.
- **Never by nickname** (a paper's catchy concept is not its name: it is "Beyond Task Completion", not "silent rot")
  and **never by author names** ("Zhang et al."). In report prose, name the paper by title at least once per
  section where it is used; numeric references ([n]) come in addition, not instead.
- **Use the paper's own terms** and quote them exactly when the wording matters. Copy quotes from the text file,
  never from memory or from another note.
- **State the setup with every result**: data, model, n ("99 tasks, Claude Haiku 4.5, 222 kept tools").
- **Keep the paper's scope**: a result on 1 model, 1 benchmark or the same tasks it was tuned on is bounded that
  way; put the bound in a limitations list, not in a hedge.
- **Trace every number to a page** (and table or figure). A number without a page is not used.
- **Do not inflate**: if a paper says "on par", do not write a number read off a plot; if the headline number
  and a figure disagree, cite the headline and do not present the other as the same quantity.
- **Correct yourself visibly in notes**: when an earlier note got a paper wrong, record the correction where the
  error was, with the page that settles it. Deliverables carry only the corrected statement.
- Mentions that point into a cited paper ("arXiv 2604.00392 Table 5", "the paper's Fig. 1") are fine;
  `tundlekit text fignums` skips them.

## Summary file format

One file per paper: `summaries/{id} - {short title}.md`. `tundlekit papers list` shows which papers have one.
Start from the generated skeleton rather than a blank file; it fills in the title, authors and page counts from the
text and refuses to overwrite an existing summary:

```
tundlekit papers summary 2604.00392 --dir papers                       # preview
tundlekit papers summary 2604.00392 --dir papers --short "Beyond Task Completion" --write
```

Then fill in every section from the pages actually read.

```markdown
# 2604.00392 · Beyond Task Completion: <full title as printed>

<Authors> · <affiliations> · arXiv <version> <date> (<venue if any>) · <N> pp (<M> body)
Read: <pages actually read, e.g. body p1-7; appendix B p10-11>; results from <pages or "abstract only">

## Summary
3-6 sentences: what the paper does, the main mechanism, and the headline result with its number.

## How it works (p2-3)
- the setup: data, tasks, model(s), seeds, n
- the mechanism, in the paper's own terms (bold the terms that will be reused)

## Results (p4-6)
- each result with its number, its table or figure, and the page
- what the paper claims the result shows, and what it does not show

## Limitations (stated, p6)
- limitations the paper states
- limitations it does not state, marked as the reader's own observation

## Relevance
- where this paper is used (report section, deck slide, design rule) and for which claim
- what must not be claimed from it
```

Rules for the file:

- Every section heading that makes claims carries the pages it came from.
- "Read:" is honest: if only the abstract and introduction were read, say so, and do not summarise results from
  pages not read.
- Mark caveats the paper does not state as your own, so no one later cites them as the paper's.
- Keep an `INDEX.md` next to the summaries (check it with `papers index-check`, below): groups that follow the report's structure, 1 table per group with
  columns Paper (`id` + short title) and One line (the finding that matters, with its number).

## Checking the collection

```
tundlekit papers index-check --dir papers --report report.md
```

| Rule | Finding | Fix |
|---|---|---|
| P001 | a paper with no summary file | write one (`papers summary`) or remove the paper |
| P002 | a summary not mentioned in INDEX.md | add its row |
| P003 | INDEX.md's "N summaries" count is wrong | update the count |
| P004 | a summary missing `## Summary`, `## How it works` (any `## How ...` heading counts), `## Results`, `## Limitations` or `## Relevance` | add the section, or give that summary its own heading list with `--profile` |
| P005 | an arXiv id cited in the report (a reference list entry, or a paper name with its id) with no summary | read the paper and summarise it before citing it |
| P006 | no INDEX.md (a warning) | create it |
| P007 | (info) the report has no citations the tool can resolve | P005 checked nothing: cite as `[n]` with `arXiv:ID`, or name + id |

`--profile JSON` maps a summary id to its required headings, for summaries of a different kind (a benchmark or a
survey).

To check that each number a report cites is on a page of its source, use `tundlekit claims trace REPORT.md --papers papers`
(report-writing skill). It needs `[n]` references or name + `(pN)` locators; 0 claims (T004) is not a pass.

## Known noise

`papers index-check` and the text tools give a starting list to confirm. The remaining false positives:

- `papers index-check`: P002 when INDEX.md names a paper by a title variant without its id; P004 on a summary that
  deliberately uses other headings (use `--profile`).
- `papers summary`: the title can still pick up a venue line or stop early on an unusual first page, and small-caps
  names may be split oddly; check the title and authors before `--write`.
- `papers body`, `papers list`: the `layout_text` flag on a 1-column paper with wide tables.

## Numbers ledger

For a report or talk, keep a ledger file: every number, count, percentage, version or date that appears in the
deliverable has a row with its value, its source (paper id + page + table, or file:line, or the command that
produced it) and any trap next to the correction ("not 75%: that is the round-5 curve; the headline is 71.1%").
A trap printed beside its correction is not reintroduced by the next drafter. No number goes into the deliverable
without a ledger row.

## Example session

```
tundlekit papers fetch 2604.00392 --dir papers
tundlekit papers abs 2604.00392 --dir papers
tundlekit papers grep 2604.00392 "silent rot" --dir papers --context 3
tundlekit papers body 2604.00392 --dir papers --start 1 --end 7
tundlekit papers list --dir papers --json
```

Through MCP: `papers_fetch` with `{"ids": ["2604.00392"], "dir": "papers"}`, then `papers_peek` with
`{"id": "2604.00392", "mode": "grep", "pattern": "silent rot", "dir": "papers"}`.
