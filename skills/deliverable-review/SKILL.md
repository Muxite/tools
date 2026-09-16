---
name: deliverable-review
description: Review a built report (.docx/.pdf) or deck (.pptx) before it goes to anyone - build from the script, render every page and slide to PNG with tundlekit render, make contact sheets, read the slides alone, run an adversarial pass over a fixed table of flaw classes, propagate every fix to all other instances, and record the review. Includes the hard rules (Office closed, back up first, no markers in deliverables, never overwrite hand edits). Use after building or changing any deliverable document or presentation, before sending or presenting it, or when asked to check, proofread or QA one.
---

# Reviewing a deliverable

| Task | CLI | MCP tool |
|---|---|---|
| what can render here (PowerPoint, LibreOffice, pymupdf, Pillow, SVG→PNG) | `tundlekit render backends` | `render_backends` |
| render a .pptx/.docx to PNGs (+ notes, contact sheets) | `tundlekit render office FILE.pptx -o DIR [--backend auto\|powerpoint\|libreoffice\|text]` | `render_office` |
| render PDF pages to PNG | `tundlekit render pdf FILE.pdf -o DIR [--dpi 110] [--first N] [--last M]` | `render_pdf` |
| contact sheets from any images | `tundlekit render sheet IMAGE... -o DIR [--cols 4] [--rows 3]` | `render_contact_sheet` |
| read a deck's texts, notes and times | `tundlekit deck inspect DECK.pptx` | `deck_inspect` |
| deck rules | `tundlekit deck lint DECK.pptx` | `deck_lint` |
| report prose and numbering | `tundlekit text lint REPORT.md`, `tundlekit text fignums REPORT.md` | `text_lint`, `text_fignums` |

## Hard rules

- **Office closed.** Word and PowerPoint must not be running while any script writes or renders an Office file
  (lock files `~$*` are unreliable on synced folders). `render office` with the `powerpoint` backend refuses when
  PowerPoint or Word is open. Check first (Windows: `Get-Process WINWORD,POWERPNT -ErrorAction SilentlyContinue`).
- **Back up first.** Before any change, copy the current deliverable to
  `versions/<name> (before <change> <date>).<ext>`.
- **Build from the script only.** Never hand-edit a built file and then regenerate over it. If the owner edited
  the built file, diff it (`tundlekit deck inspect`, or the text backend of `render office`), carry the edits into
  the source, then regenerate.
- **Render into a scratch folder**, never into the source folder, the repository root or the home folder.
  `render office` refuses those, never opens the original (it renders a copy) and empties its output folder
  first, so stale renders never survive.
- **No markers in deliverables**: no ⚠, corrections tables, `[verified]` / `[proposed]` / `[doc]` markers or
  bracketed placeholders. Provenance stays in notes.
- **Verify every claim against an opened source.** Never cite an unopened paper.
- Source repositories are read-only. Ask before spawning reviewer subagents if the context requires it.

## Procedure

1. **Build** the deck and report from their scripts or specs (`tundlekit deck build SPEC.json -o OUT.pptx`).
   Fix every build warning (overflow, table past the bottom, strip too long, over budget).
2. **Lint** mechanically: `tundlekit deck lint OUT.pptx`, `tundlekit text lint REPORT.md`,
   `tundlekit text fignums REPORT.md --refs NOTES.md`. Also search the report text for em dashes, first person
   and markers; nothing may remain.
3. **Render** every slide and page:
   ```
   tundlekit render backends
   tundlekit render office build/deck.pptx -o .review/deck
   tundlekit render office build/report.docx -o .review/report
   ```
   `auto` picks PowerPoint, then LibreOffice (headless), then a text dump. Slides become `slide-NN.png`
   (1600 × 900) with `notes-NN.txt`; documents become `page-NNN.png`; contact sheets `contact-NN.png` (4 × 3)
   are made when Pillow is installed. A warning "renders under 10 KB" means blank or failed renders: investigate.
   With only the `text` backend, review the text dumps and say that no visual check was possible.
   For a PDF: `tundlekit render pdf report.pdf -o .review/pdf`, then
   `tundlekit render sheet .review/pdf/page-001.png .review/pdf/page-002.png -o .review/pdf-sheets`.
4. **Look at every contact sheet**, then every figure slide and figure page at full size. Check overflow,
   overlaps (strips over tables), tiny figures, unreadable labels, empty or cut-off slides.
5. **Read the slides alone**, without notes. Can the talk be followed? If not, move content from the notes onto
   the slide. Then read the notes: they say what the slide says, plus a little more, in first person.
6. **Adversarial pass.** Act as a hostile reader of the owner's instructions and go through every flaw class
   below, for every slide, section, figure and table.
7. **Propagate.** For each flaw found, search the script, report, figures and notes for every other instance of
   the same class and fix all of them, not just the one spotted.
8. **Cover gaps in the owner's own explanation** and tell the owner (for example: uncapped gate retries would leak
   held-out tests, so the design caps them with admit/reject plus a reason only).
9. **Rebuild, re-render, re-check** until the pass finds nothing new.
10. **Record** the review as a table in the plan or handoff notes, plus what is left for the owner:

    | Flaw class | Found | Fix |
    |---|---|---|
    | Paper nickname | slide 7 title, report §2.3 | replaced with "Beyond Task Completion (arXiv 2604.00392)" |

    Note the backup path and what changed.

## Flaw classes

| Class | Test |
|---|---|
| Box hides >1 model call | count model sessions in the prose; count MODEL boxes |
| Term before definition | first use of every term vs its defining slide or section |
| Paper nickname or author names | every paper reference is its title (+ arXiv id) |
| Setup unstated | every result says data, model, n |
| Choice without justification | every design element maps to a rule or a stated reason |
| Property only in prose | key properties appear in a title or figure label |
| Thin slide | slide text alone carries the point; SAY ≥ ~20 words |
| Jargon | "Eq.", "pp", internal codes on slides without explanation |
| Coverage mismatch | report sections vs deck slides, 1:1 or an agreed cut |
| Ordering | nothing used before introduced; research before the system |
| Layout | overflow warnings, strips overlapping tables, small figures |
| Over-claim | "proposed" stated; bounds (1 model, same tasks) present |
| Legacy notes | no MUST HIT; notes in first person |
| Meta / defensive notes | no "I'll show…", "I'm not claiming…", "that's fine for X, but…" in SAY |
| Heading/title is a topic label | every title and heading states its point in 1 line |
| Untraced number | every number has a page, table or file:line behind it |
| Em dash / markers | none in titles, report prose or anywhere in the deliverable |
| Time | core time within the target; combined time for shared slots within the max |

## "So what" review

For every section, paragraph, bullet, table row and slide, answer "so what?". Anything without an answer is cut.
A separate reviewer (a fresh session that did not write the text) does this best; it also checks that the slides
alone carry the point and that the notes say that and more.

## Past mistakes not to repeat

- sparse slides with the content left in the presenter's head
- author names and nicknames instead of paper titles
- "Eq. 5", "coverage ratio", "evidence in paper" columns instead of plain findings
- an unfamiliar system shown without a picture of how it works
- "Build" as 1 box; reviewer boxes hiding model calls
- a concept used on a slide before its own slide
- design changes presented before the evidence for them
- key properties only in prose; lifecycle steps unexplained
- many slides with under ~20 spoken words; MUST HIT lists instead of a script
- meta and defensive note sentences
- a THUS strip placed over a table; a figure too small to read
