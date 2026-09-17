# Layout recipes and legibility

Companion to the diagram-maker skill. The skill says what the visual code means (colour = stage, style = actor,
1 box per model call). This file says **how to lay a figure out** and **how to make it readable at the size it
will actually be shown**.

Both came out of building 19 diagrams for 2 reports and 2 talks, where the recurring defects were never colour
mistakes: they were figures that showed a component map instead of a mechanism, and figures that were legible on
a slide and unreadable on the page.

---

## 1. Pick the recipe before opening the spec

Ask what the figure has to teach, then take the matching layout. Starting from a blank canvas is what produces
component maps.

| The point is… | Recipe | In a spec |
|---|---|---|
| the order of steps | linear pipeline | nodes in order, `direction` LR |
| a long pipeline with named phases | stage bands | 1 group per phase, each labelled with a claim |
| a boundary that splits before from after | full-width divider | a node spanning the width, or a group holding everything on each side |
| 2 loops running on different clocks | 2 regions | 2 groups, edges crossing between them |
| what changes over time | small multiples | 1 figure per step, rendered separately |
| the shape of a record | spec card | a `record` node whose label lists the fields |
| a rule that is an if/elif chain | decision table | condition nodes on the left, verdict nodes on the right |
| what a checker declares, checks and rejects | 3-column matrix | 3 ranks, 1 row per field |
| elimination down to a choice | funnel | 4-5 ranks, each stage a question |
| what was true when | lane timeline | needs a drawing tool, not the spec |
| what sits on what | layer stack | 1 rank per layer, or 1 group per layer |
| a protocol people misread | topology | a group for the host, `external` nodes outside it |
| who can influence what | trust boundary | 2 groups, a dashed edge crossing into the trusted one |
| a store and its properties | datastore | a `record` node labelled `library\nappend-only · versioned` |

**Rank and wrap.** `rank` pins a node to a column (LR) or row (TB): use it to line up nodes that belong together
and to put a feedback target where the reader expects it. `wrap` caps ranks per row, so a long pipeline becomes
2 readable rows instead of 1 strip too wide to read on a slide. Reach for `wrap` before shrinking anything.

**What the spec cannot express.** Small multiples over time, lane timelines, funnels whose *width* carries the
elimination, and figures with free-floating annotation blocks are not layouts the automatic renderer produces.
For those, either render each step as its own diagram and place them side by side on the slide, or draw the
figure in a plotting library and place the result with a `figure` body. Do not contort a spec into them.

---

## 2. Legibility: the same drawing at 2 sizes

A figure is usually shown twice: about 12 inches wide on a slide, about 6.5 inches wide in a report. Scaling one
drawing down makes its labels unreadable. Drawing it twice makes the 2 versions drift.

**The rule that solves it: fix text size as a ratio of the physical width, not in absolute points.**

- Draw on a resolution-free canvas (percentages of width), with one base text size passed in, and every label a
  multiple of that base.
- Set the base from the output width: `base = width_in_inches × ratio`. The same `ratio` at both widths means the
  text occupies the same fraction of the picture in both, so the slide and the page show the identical drawing,
  one simply printed larger.
- A ratio of about 1.5 puts a full-size label near 9.6 pt on the page and 18 pt on the slide. Useful range: 1.4
  to 1.65.
- Choose the ratio per figure: the largest value that does not overflow, checked by eye.

**The report is the binding case.** At 6.5 inches text is half the size it is on a slide, so a figure that reads
on screen can be illegible on the page. Judge legibility from the report render; the slide takes care of itself.
Keep the smallest annotation at roughly 6.5 pt at report width.

**When something overflows, widen the box or shorten the label. Never lower the ratio.** Lowering the ratio fixes
one collision by making every label in the figure smaller.

For SVG output the same logic applies through the box sizes: boxes widen to fit their longest line and lines are
never truncated, so a figure gets wider rather than smaller. If the result is too wide for a slide, use `wrap`,
split the figure, or cut words from labels.

---

## 3. Labelling

These are what turn a correct diagram into one that explains itself.

- **Every arrow carries the thing that travels it**: `manifest`, `draft`, `held-out tests`, `admit or reject +
  reason`. An unlabelled arrow says only "related".
- **Headings and group labels are claims, not nouns.** `EXECUTION: no model schedules, routes or admits` beats
  `Execution`. The negative form is often the most informative: `no model decides`, `warns only`, `never builds`.
- **Properties live in labels**: `append-only · versioned`, `FIXED AT THE FREEZE`, `PROTECTED`, `fixed before the
  build`. Anything said twice in the talk belongs inside the figure.
- **A role node states what it sees, what it never sees, and what it hears.** Three lines replace a table.
- **Counts and identifiers in the `sub` line** (`13 reasons`, `7 checks`, `≤ N tries`) make a figure auditable
  against its source without adding a sentence.
- **Mark illustrative or proposed content inside the canvas** with `note`. The first question from a senior
  reader is what is real.
- **Keep the legend.** `"legend": "auto"` adds it whenever more than 1 actor appears, with `1 box = 1 model
  session` when a model node is present.

---

## 4. Style modifiers, one meaning each

Reserve each visual variation for exactly one meaning across the whole document set:

| Modifier | Means |
|---|---|
| dashed node | optional, planned, or not built yet |
| dashed edge | advisory or informational, not the main path |
| thick border | sealed, protected, or the subject of the figure |
| an edge in the `failed` outcome colour | a rejection or failure path; something going backwards |
| `external` actor | outside the system boundary |

Outcome colours mark node states only. Never use them for stages.

---

## 5. Checking a figure

```
tundlekit diagram validate fig-build.json
tundlekit diagram render fig-build.json -o fig-build.svg --png fig-build.png
tundlekit palette show
```

Then look at it at the size it will be shown. After the figure is placed in a deliverable, the render step is
what catches the defects no validator sees:

```
tundlekit render office build/deck.pptx -o .review/deck
tundlekit render office build/report.docx -o .review/report
```

Every layout defect that ever shipped from this material was invisible to the automated checks and obvious in a
render: a strip covering a table, an arrow ending in empty space, a figure too small to read, a stale figure
number in a footer.

**Renumbering.** Inserting a figure shifts every later number. Renumber the report and the deck footers in one
operation, never separately:

```
tundlekit text xref report.md --in deck-src/deck.json --renumber "Fig. 9=Fig. 10" "Fig. 10=Fig. 9"
tundlekit text fignums report.md --refs notes.md
```

---

## 6. Checklist

- [ ] the figure shows a mechanism, not a component map
- [ ] it matches one of the recipes in §1, and uses `rank` / `wrap` instead of shrinking
- [ ] 1 box per model call; the MODEL box count matches the prose
- [ ] every edge is labelled with what travels it
- [ ] group and section labels state claims, not topics
- [ ] key properties are in labels; illustrative or proposed content is marked
- [ ] each style modifier carries only its one meaning
- [ ] legend present when more than 1 actor appears
- [ ] every distinction survives greyscale: text, outline and fill, not colour alone
- [ ] rendered and read **at report width**, with the smallest label still legible
- [ ] numbers in the figure match the report table and the source
