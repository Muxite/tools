# Brief: first-time-reader review

Part of the [review-prompts skill](../SKILL.md). The orchestrator fills in the inputs and passes everything below
the line to a reviewer in a **fresh context**: it must not have seen the project, the notes or earlier drafts,
because it plays a reader who has only the stated background.

## Inputs

| Slot | Content | Produced by |
|---|---|---|
| `{{audience}}` | the reader to play: what they already know and what they do not (for example "CS students who have built LLM agents; know tool calling, DAGs, JSON Schema, git; do not know this codebase, its terms or the papers") | the owner's audience note |
| `{{deck}}` | every slide's title, text, tables and notes, in order | `tundlekit deck inspect DECK.pptx --json` |
| `{{slide_images}}` | slide and page PNGs or contact sheets, for figures | `tundlekit render office DECK.pptx -o .review/deck` |
| `{{report}}` | the report text, in order | the Markdown source |
| `{{protected}}` | elements that stay; confusion there is fixed by adding explanation, not by cutting | the owner |
| `{{time}}` | the talk length and the planned time per slide (from the deck notes) | `tundlekit deck inspect` |

## Protected

Never propose to remove anything in `{{protected}}`. If a protected element confuses, the fix is a definition, a
label, a figure or a sentence placed before it.

---

You are **{{audience}}**, seeing this material for the first time. Read the deck once from the first slide to the
last, **without going back**, then the report once from the start. Stop at every point where you, as this reader,
would be lost, and record it.

You report findings. **You do not rewrite the deliverable.** The Fix cell names the smallest change (a definition
to add, a term to replace, a label to move earlier) with exact text where possible.

## What counts as confusion

- **Term before definition**: an internal name, abbreviation, system or figure element used before it is
  defined, or never defined. Record the first use and where (if anywhere) the definition comes.
- **Jump**: a slide or paragraph that assumes a step the reader has not seen; something referenced before it is
  introduced; "the design" or "our system" before the reader knows what it is.
- **Unread figure**: a figure the reader cannot follow in the time given (too many panels, labels too small,
  a legend that does not explain the shapes or colours, a mechanism shown without the steps).
- **Missing why**: a design choice with no reason or paper next to it.
- **Number without meaning**: a number whose unit, baseline or setup (data, model, n) is missing.
- **Drag**: a slide that carries more than its planned time allows (compare with `{{time}}`), or a section that
  repeats what the reader already has.
- **Unknown system**: a system from a paper explained without its figure or a drawing of how it works.
- **Status unclear**: the reader cannot tell what is built, measured, proposed or aspirational.

## How to work

1. Read in order and write down each confusion when it happens, with the slide number or section and line.
2. At the end of the deck, answer: could the talk be followed from the slides alone? Name the slides where not.
3. At the end of the report, answer: where did the thread get lost, and what was missing?
4. **Propagate.** For each confusion, search the rest of the deck and report for every other instance of the same
   cause (the same undefined term, the same missing setup) and list them in the same row.

## Output format (exactly)

Verdict: 3-5 lines. Whether the talk can be followed from the slides alone, where the reader gets lost, and what
is missing.

| Where | Confusion | Fix |
|---|---|---|
| slide 7 (first use), also slide 2 | "AI4Research" appears as a column header and is never defined | slide 2, bullet 1: "AI4Research, a multi-agent research framework, …" |
| slide 19 | 4 panels, a 7-state legend and a 9 pt card in 45 s | drop 3 card rows, enlarge the rest; point only at the card, T2 and T4 |
| §5.1, Table 7 | `k` is used in rows 2, 3 and 5 but defined only in §5.2 | define `k` in §5.1's lead sentence |
