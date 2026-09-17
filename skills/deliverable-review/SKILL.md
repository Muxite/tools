---
name: deliverable-review
description: Review a built report (.docx/.pdf) or deck (.pptx) before it goes to anyone - build from the script, render every page and slide to PNG with tundlekit render, make contact sheets, read the slides alone, run an adversarial pass over a fixed table of flaw classes, propagate every fix to all other instances, and record the review. Includes the hard rules (Office closed, checked with tundlekit office check before any build or render, back up first, no markers in deliverables, never overwrite hand edits). Use after building or changing any deliverable document or presentation, before sending or presenting it, or when asked to check, proofread or QA one.
---

# Reviewing a deliverable

| Task | CLI | MCP tool |
|---|---|---|
| are Word, PowerPoint or Excel running? (exit 1 if so; `--wait` polls every 2 s) | `tundlekit office check [--wait SECONDS]` | `office_check` |
| what can render here (PowerPoint, LibreOffice, pymupdf, Pillow, SVG→PNG) | `tundlekit render backends` | `render_backends` |
| render a .pptx/.docx to PNGs (+ notes, contact sheets) | `tundlekit render office FILE.pptx -o DIR [--backend auto\|powerpoint\|libreoffice\|text]` | `render_office` |
| render PDF pages to PNG | `tundlekit render pdf FILE.pdf -o DIR [--dpi 110] [--first N] [--last M]` | `render_pdf` |
| contact sheets from any images | `tundlekit render sheet IMAGE... -o DIR [--cols 4] [--rows 3]` | `render_contact_sheet` |
| read a deck's texts, notes and times | `tundlekit deck inspect DECK.pptx` | `deck_inspect` |
| deck rules | `tundlekit deck lint DECK.pptx` | `deck_lint` |
| report prose and numbering | `tundlekit text lint REPORT.md`, `tundlekit text fignums REPORT.md` | `text_lint`, `text_fignums` |
| report ↔ deck coverage, section by section and rule by rule | `tundlekit review coverage REPORT.md DECK.pptx [--cuts cuts.txt]` | `review_coverage` |
| every cited number located on a page of its paper | `tundlekit claims trace REPORT.md --papers papers [--ledger LEDGER.md] [--in NOTES.md]` | `claims_trace` |
| hand edits in a built deck, with where the old text lives | `tundlekit deck diff BUILT.pptx EDITED.pptx --search deck-src` | `deck_diff` |
| hand edits in a built .docx vs its source, as an edits file | `tundlekit text docx-diff REPORT.md EDITED.docx --search report-src --emit-edits edits.json` | `docx_diff` |
| apply those edits (dry run, then `--write`) | `tundlekit text apply-edits edits.json REPORT.md` | `text_apply_edits` |
| stale § / Fig. / Table references in scripts and notes, each against the report it slices | `tundlekit text xref REPORT.md --in FILE[=REPORT]... [--exclude GLOB...]` | `text_xref` |

## Hard rules

- **Office closed.** Word and PowerPoint must not be running while any script writes or renders an Office file
  (lock files `~$*` are unreliable on synced folders). Run `tundlekit office check` (MCP `office_check`) before
  **every** build and render. It lists running Word, PowerPoint and Excel processes (on Linux and macOS: LibreOffice),
  exits 1 when any is running, and never touches them. Ask the owner to close them and save their work, then
  `tundlekit office check --wait 120` polls every 2 seconds until they are closed or the time is up. Build scripts
  can call `tundlekit.render.office_running()` for the same check. `render office` with the `powerpoint` backend
  also refuses when PowerPoint or Word is open.
- **Back up first.** Before any change, copy the current deliverable to
  `versions/<name> (before <change> <date>).<ext>`.
- **Build from the script only.** Never hand-edit a built file and then regenerate over it. If the owner edited
  the built file, diff it (`tundlekit deck diff BUILT.pptx EDITED.pptx --search deck-src`, or
  `tundlekit text docx-diff REPORT.md EDITED.docx --search report-src --emit-edits edits.json`), carry every change
  into the source (`tundlekit text apply-edits edits.json REPORT.md` applies the list of per-file edits it wrote,
  all or nothing; `insert`, `delete` and ambiguous changes stay manual), then regenerate and diff again.
- **Render into a scratch folder**, never into the source folder, the repository root or the home folder.
  `render office` refuses those, never opens the original (it renders a copy) and empties its output folder
  first, so stale renders never survive.
- **No markers in deliverables**: no ⚠, corrections tables, `[verified]` / `[proposed]` / `[doc]` markers or
  bracketed placeholders. Provenance stays in notes.
- **Verify every claim against an opened source.** Never cite an unopened paper.
- Source repositories are read-only. Ask before spawning reviewer subagents if the context requires it.

## Procedure

0. **Office closed**: `tundlekit office check` must exit 0 (use `--wait SECONDS` while the owner closes files).
   Repeat it before every later build or render.
1. **Build** the deck and report from their scripts or specs (`tundlekit deck build SPEC.json -o OUT.pptx`).
   Fix every build warning (overflow, table past the bottom, strip too long, a block overlapping a strip, over
   budget).
2. **Lint** mechanically: `tundlekit deck lint OUT.pptx`, `tundlekit text lint REPORT.md`,
   `tundlekit text fignums REPORT.md --refs NOTES.md`, and `text xref` with each script paired with the report it
   actually slices:
   ```
   tundlekit text xref REPORT.md --in deck-src/deck.json NOTES.md build_deck.py=REPORT.md build_capsule.py=capsule/REPORT-annotated.md --exclude "*/versions/*"
   ```
   Each `--in` entry may be written `FILE=REPORT` (a file or folder paired with its own report, for example
   `--in build/=REPORT-annotated.md`); `--exclude GLOB...` drops walked files that belong to another report.
   A build script that slices an annotated variant (`REPORT-annotated.md`) must be checked against that variant,
   or every marker looks missing. X003 (info) means the script's slice source could not be resolved and the
   marker was not checked: check it by hand.
   Also search the report text for em dashes, first person and markers; nothing may remain.
   Then the 2 checks that replace most of a manual cross-read:
   ```
   tundlekit review coverage REPORT.md build/deck.pptx --cuts cuts.txt
   tundlekit claims trace REPORT.md --papers papers --ledger LEDGER.md --in NOTES.md
   ```
   `review coverage` lists report sections with no slide (C001), slides with no section (C002), footers citing
   missing sections (C003) and rule names that differ between the 2 (C004-C006); agreed cuts go in `cuts.txt`.
   `claims trace` marks every cited number as located (with pages), derived, ledgered, untraced or no_source;
   every untraced number is a must-fix until its page is found. A T004 warning (0 claims: the report uses neither
   `[n]` references nor name + `(pN)` locators) means nothing was traced, not that everything passed. Every weak
   location (T003) needs a look at its page.
3. **Render** every slide and page:
   ```
   tundlekit office check
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
   below, for every slide, section, figure and table. Better: hand the briefs in the review-prompts skill to
   reviewers in a fresh context (fact-check, adversarial flaw classes, so-what, first-time reader), with the
   outputs of steps 2-3 as their inputs, and merge their tables.
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
alone carry the point and that the notes say that and more. The so-what brief in the review-prompts skill is the
ready-made instruction for it, with a fixed `Element · So what · Verdict` table.

Apply the accepted edits with `tundlekit text apply-edits EDITS.json FILE` (dry run, then `--write`), so every
replacement is anchored and a missing anchor fails instead of silently doing nothing.

## Known noise

The checkers give a starting list for a person or agent to confirm. The remaining false positives per tool:

- `review coverage`: unnumbered headings and slides without a `§` footer are matched by title only, so a
  reworded title gives a false C001/C002 pair. Cite the section in the footer, or record the cut in `cuts.txt`.
- `claims trace`: T001 on counts and setup details that are not paper results, and on numbers the paper writes in
  another form; weak locations (T003) may be coincidences; T004 means nothing was checked.
- `text xref`: X001 on references into another document whose name does not end in "report"; X003 is a skipped
  check, not noise.
- `deck lint`: D005 on a meta phrase used in a real statement; D009 on built decks whose footer sits high on the
  slide; D013 when deck ids are not the file stems (pass `--ids`).
- `deck diff`: a slide whose title was rewritten beyond recognition (similarity below 0.4) shows as `removed` plus
  `added`, not as a title change.
- `text docx-diff`: template text in the .docx (title page, table of contents) shows as `insert`.
- `render office`: the "renders under 10 KB" warning can also fire on genuinely sparse slides; look before acting.
- `office check`: it sees only Word, PowerPoint and Excel (LibreOffice elsewhere); another program holding the
  file open is not detected.

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
