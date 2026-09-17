---
name: deck-builder
description: Write a presentation as a JSON deck spec and build it into an editable PowerPoint (.pptx) with tundlekit deck build, then check it with tundlekit deck lint. Covers the deck structure template, slide-writing rules, speaker-note rules (TIME / SAY / IF ASKED, no MUST HIT, no meta or defensive lines), the timing table and words budget, optional insertion slides, and the rule that a deck and its report carry 1 argument. Use when asked to create, restructure, time or fix a talk, slide deck or .pptx, or when a report needs a matching presentation.
---

# Building a deck from a spec

The deck is generated from a JSON spec, never edited by hand and regenerated over. If someone edited the built
`.pptx`, find their edits with `tundlekit deck diff BUILT.pptx EDITED.pptx --search deck-src`, carry them into the
spec, then rebuild (see "Carrying hand edits back").
Building needs the `office` extra (`pip install -e ".[office]"` in the tundlekit checkout); linting a spec needs nothing.

| Task | CLI | MCP tool |
|---|---|---|
| build a .pptx from a spec | `tundlekit deck build SPEC.json -o OUT.pptx [--inserts shown\|hidden\|off] [--times-file PATH]` | `deck_build` |
| check a spec or a built deck | `tundlekit deck lint SPEC.json` or `tundlekit deck lint DECK.pptx [--times-file PATH --ids ID...]` | `deck_lint` |
| is PowerPoint (or Word, Excel) running? exit 1 if so | `tundlekit office check [--wait SECONDS]` | `office_check` |
| read back any .pptx (texts, notes, times) | `tundlekit deck inspect DECK.pptx` | `deck_inspect` |
| what changed between 2 decks, with where the old text lives in the sources | `tundlekit deck diff OLD.pptx NEW.pptx [--search PATH...]` | `deck_diff` |
| does the deck cover the report, section by section, rule by rule | `tundlekit review coverage REPORT.md DECK.pptx [--cuts cuts.txt]` | `review_coverage` |
| stage colours for `stage` | `tundlekit palette show` | `palette_get` |

Add `--json` for a machine-readable result. Through MCP, pass `spec_path` (a file) or `spec` (an inline object).

## Workflow

1. Outline the argument (below) next to the report outline, if there is a report. Same claims, same evidence,
   same design, same open questions.
2. Write the spec. Every content slide gets a takeaway title, a `source`, a body that carries the point, and
   notes with `time` and `say`.
3. `tundlekit deck lint SPEC.json --json` and fix every error; fix warnings unless there is a stated reason.
4. `tundlekit deck build SPEC.json -o OUT.pptx --json`. Read `warnings` (text overflow, table past the slide
   bottom, strip too long, over budget) and `budget.status`; fix the spec and rebuild until both are clean.
5. `tundlekit deck lint OUT.pptx` on the built file and `tundlekit review coverage REPORT.md OUT.pptx` when there is
   a report; then run the deliverable-review skill (render every
   slide, contact sheets, adversarial pass).

Close PowerPoint before building (an open file can be locked or clobbered): `tundlekit office check` exits 1
while Word, PowerPoint or Excel is running, and `--wait 120` waits for them to close. Then back up the previous
deliverable before **every** write to it (a build, or edits applied to a .pptx/.docx):

```
tundlekit bundle backup deck/talk.pptx --reason "reorder slides"
```

It copies the file to the nearest `versions/` folder as `talk (before reorder slides 2026-09-17).pptx` and refuses
while Office is running (MCP `bundle_backup`; details in the tundle-bundle skill). `--force-office` exists on
`bundle backup` and `text apply-edits`, but the rule is to close Office, not to force.

## Spec format

```json
{
  "meta": {"id": "example", "title": "Build tools behind a held-out gate", "inserts": "shown",
           "budget": {"target": "5:00", "max": "6:00"}, "words_per_second": 2.3},
  "slides": [
    {"type": "title", "title": "Build tools behind a held-out gate",
     "subtitle": "Why agents that write their own tools must be tested by someone else",
     "byline": "Research update",
     "notes": {"time": "0:15", "say": "Today's update is about agents that build their own tools, and why every tool they build needs a check they did not write."}},
    {"type": "divider", "title": "The evidence", "subtitle": "Each result, then the design rule it leads to",
     "notes": {"time": "0:05", "say": "So here's the evidence, one result at a time."}},
    {"type": "content", "eyebrow": "Research",
     "title": "96.8% of kept tools fail their held-out tests",
     "stage": "gates", "source": "Beyond Task Completion, Table 5",
     "demonstrated_by": {"paper": "Beyond Task Completion (arXiv 2604.00392)",
                         "setup": "99 tasks, Claude Haiku 4.5, 222 kept tools"},
     "body": {"kind": "chart", "categories": ["One-Shot", "ToolMaker-style", "CREATOR-style", "All 222 tools"],
              "values": [100.0, 100.0, 91.7, 96.8], "highlight": 3, "unit": "%",
              "takeaway": "Tools that run cleanly still return wrong answers on inputs the agent never saw"},
     "notes": {"time": "0:45",
               "say": "This paper replayed every tool that 3 tool-building methods kept against tests of that tool's own capability, on inputs the agent never saw. 215 of 222 tools scored zero. They didn't crash, they just returned wrong answers. The hand-written reference tools pass every suite, so the tests are fair.",
               "asked": ["Are the suites too hard: the reference implementations score 1.00 on all 16 capability suites"]}},
    {"type": "content", "eyebrow": "Research", "insert": true,
     "title": "Unverified self-made skills barely beat none",
     "stage": "gates", "source": "CoEvoSkills, Fig. 4",
     "demonstrated_by": {"paper": "CoEvoSkills (arXiv 2604.01687)", "setup": "SkillsBench, Claude Opus 4.6"},
     "body": {"kind": "table", "rows": [["Condition", "Pass rate"], ["No skills", "30.6%"],
              ["Human-curated skills", "53.5%"], ["Self-generated with a verification loop", "71.1%"]],
              "widths": [8.3, 3.5]},
     "notes": {"time": "0:30",
               "say": "With no skills an agent passes 30.6 percent. Human-curated skills reach 53.5. Self-made skills that go through a verification loop reach 71.1, so the gain comes from checking, not from writing."}},
    {"type": "content", "eyebrow": "Rule", "title": "What this means: the builder never writes its own tests",
     "stage": "gates", "source": "Beyond Task Completion, Table 5; CoEvoSkills, Fig. 4",
     "body": {"kind": "lines", "items": ["R1  A separate suite author writes the tests from the manifest",
                                          "R2  The implementer never sees the held-out tests"]},
     "thus": "every tool enters the library through a gate its builder did not write",
     "phase": {"in": "manifest", "out": "admitted tool"},
     "notes": {"time": "0:35",
               "say": "So here's the rule I take from both results. The agent that builds a tool never writes the tests for it. A separate author writes them from the manifest, before any code exists, and the builder only hears admit or reject."}}
  ]
}
```

A longer version is in the repository at `examples/deck.json`.

Field reference:

- `meta` (all optional): `id` (required with `--times-file`), `title`, `logo` (image path), `inserts`
  (`shown` | `hidden` | `off`), `budget` (`target`/`max` as `M:SS`, default 40:00 / 45:00),
  `words_per_second` (default 2.3). Relative paths resolve against the spec file's folder.
- `type`: `title` (title, subtitle, byline), `divider` (dark; title, subtitle), `content` (default).
- content fields: `eyebrow` (shown upper-case), `title`, `stage` (a palette stage: intent, binding, freeze,
  dispatch, gates, claims, build, library, external), `source` (footer), `insert`, `demonstrated_by`
  (`paper`, `setup`), `phase` (`in`, `out`), `thus`, `body`.
- `body.kind`: `bullets` (`items`), `lines` (`items`, optional `mono`), `table` (`rows`, first row is the header,
  equal lengths; optional `widths` in inches, 1 per column), `figure` (`path` to an existing PNG/JPEG, fitted to
  11.8 × 5.3 in), `excerpt` (`text`, optional `caption`; monospace), `chart` (`categories`, `values`, optional
  `highlight` index or category, `unit`, `takeaway`, `"chart_type": "bar"` (default) or `"line"`, `highlight_color` a
  stage or outcome name other than `pending`, default `gates`; a native editable chart, grey bars, 1 highlighted
  bar, data labels on), `point` (`text`: 1 bold 20 pt line, the takeaway under a table or figure).
- **Multi-series charts**: instead of `values`, give `series`, a list of `{"name", "values"}` (each as long as
  `categories`). The chart gets 1 series per entry and a legend; `values` and `series` are mutually exclusive.
  Works for `bar` and `line`:

  ```json
  {"kind": "chart", "chart_type": "bar", "categories": ["One-Shot", "ToolMaker-style", "CREATOR-style"],
   "series": [{"name": "kept", "values": [119, 19, 84]}, {"name": "passed held-out", "values": [0, 0, 7]}],
   "takeaway": "Almost no kept tool passes its held-out tests"}
  ```
- **Monospace columns**: a `table` block takes `mono_cols`, a list of 0-based column indices set in monospace
  (file paths, ids, commands).
- `body` is 1 block or a **list of blocks**. Blocks stack top to bottom in the body area unless a block gives
  `x`, `y`, `w`, `h` (inches); `size` (pt) overrides the text size. Overflow warnings apply per block. A figure
  without `h` shrinks to fit above the THUS strip, so it never runs off the slide. Geometry values must lie in
  0-1000 inches (`w`, `h` at least 0.01). The build warns when a positioned block overlaps a strip (DEMONSTRATED
  BY, IN/OUT or THUS) or a stacked block overlaps a positioned one: move or shrink the block. An excerpt caption
  that does not fit is dropped with a warning.
- Example of a multi-block body (a table with its takeaway, then a figure beside it):

  ```json
  {"type": "content", "eyebrow": "Research", "title": "Unverified self-made skills barely beat none",
   "stage": "gates", "source": "CoEvoSkills, Fig. 4",
   "body": [
     {"kind": "table", "rows": [["Condition", "Pass rate"], ["No skills", "30.6%"], ["With a verification loop", "71.1%"]],
      "x": 0.75, "y": 1.9, "w": 6.0, "h": 2.0},
     {"kind": "point", "text": "The gain comes from checking, not from writing", "x": 0.75, "y": 4.2, "w": 6.0},
     {"kind": "chart", "categories": ["No skills", "Verified"], "values": [30.6, 71.1], "highlight": 1,
      "unit": "%", "highlight_color": "passed", "x": 7.0, "y": 1.9, "w": 5.6, "h": 4.0}
   ],
   "notes": {"time": "0:35", "say": "With no skills an agent passes 30.6 percent. Self-made skills that go through a verification loop reach 71.1, so the gain comes from checking, not from writing it."}}
  ```

  Prefer 1 block per slide; use several when a table or diagram needs its takeaway line, or a table and a small
  chart make 1 point together.
- `notes`: `time` (`M:SS`, required on every slide), `say`, `asked` (list of "question: short answer").
- Strips: `demonstrated_by` renders `DEMONSTRATED BY   {paper}  ·  {setup}`; `thus` renders `THUS   {thus}`;
  `phase` renders `IN   {in}        OUT   {out}`.
- Numbering: content slides show 1, 2, 3…; title and divider slides advance the counter without showing it.
  Validation lists every problem with its JSON path (`slides[3].notes.time: ...`) in 1 error.

## Deck structure template

| # | Section | Slides |
|---|---|---|
| 1 | Title | title slide; a 1-sentence subtitle that says what the thing is |
| 2 | Goal | 1 slide: the goal, what exists, the real question, the talk plan |
| 3 | Background | 1 short slide per concept the audience would misuse (define before use, but correctly) |
| 4 | Divider "The evidence" | subtitle "Each result, then the design rule it leads to" |
| 5 | Evidence blocks | per paper: what it is (its figure) → how it works + result → where it falls short → why it does not transfer; each with DEMONSTRATED BY |
| 6 | Rule slide after each block | "What this means: …", numbered rules R1…Rn, 1 line each |
| 7 | Synthesis (optional) | 1 table across papers |
| 8 | Today | table of gaps in the current system, with file:line in the footer |
| 9 | Divider "The design" | subtitle "Proposed: nothing here is built or measured yet" (when true) |
| 10 | Design overview | the full design figure; the longest notes of the talk, walked step by step |
| 11 | Rule collection | table Rule · In the design · Because (paper); THUS "every box in the design answers 1 of these rules" |
| 12 | Design parts | 1 slide per mechanism, each with THUS |
| 13 | Evaluation | tracks, plus "what would prove it wrong", stated in advance |
| 14 | Next | order of work; riskiest assumptions tested first |
| 15 | Open questions | table For (owner) · Question; end on the decision that unblocks most |

Only 2 argument shapes: **claim → backup**, or **explain → thus the plan is X**. Nothing is referenced before it
is introduced. Rules appear right after the evidence that motivates them, then all together at the design stage.

**Cutting for time**, in this order: extra papers → state-of-the-art comparisons → challenge lists →
background depth. Never cut a main point, a rule slide or the design overview. Prefer fewer slides: merge a
table and a diagram into 1 diagram the presenter can talk over.

## Slide-writing rules

- Slides almost ARE the script: a reader with only the slides follows most of the talk. No sparse
  "1 claim, 1 number, 1 picture" slides with the content left in the presenter's head.
- Title = the takeaway sentence, not a topic label ("96.8% of kept tools fail held-out tests", not "Silent rot").
  At most 90 characters.
- **No em dashes, above all in titles.** Use a colon, a full stop or a plain sentence.
- Research slide: `demonstrated_by` with the paper's **real title and arXiv id** and the setup (data, model, n).
  Never author names ("Zhang et al.") or nicknames.
- Findings in plain prose with the number built in. No "Eq. 5", "pp", "evidence in paper" columns or internal
  codes without explanation.
- Charts carry a 1-2 line bold `takeaway`; label categories with n where it matters.
- Design slide: `thus` states the plan that follows.
- Key properties go in the title or the figure label ("Append-only and versioned: nothing is edited or deleted"),
  not only in the notes.
- An unfamiliar system gets its paper's figure (`figure` body, caption "reproduced from …") or a drawn mechanism.
- `source` footer on every content slide: paper table/figure, report section, or file:line.
- Every term, system and figure element is defined before it is used. Every design choice has a reason or a
  paper next to it.
- Big text: body ≥ 18 pt, tables ≥ 14 pt. If build warns about overflow, cut words or split the slide.
- Status in plain words: "Proposed: nothing here is built or measured yet". No ⚠, `[verified]`, `[proposed]`
  or bracketed placeholders on slides.

## Speaker notes

The builder writes notes in this format:

```
INSERT: optional slide; delete or hide it and the talk flows unchanged     (insert slides only)
TIME 0:45
SAY: <the slide rephrased, first person, conversational, plus a little extra>
IF ASKED:
- <likely question: short answer>
```

- **SAY** = what the slide says, in the speaker's voice, plus the sentence that hands over to the next slide.
  First person and contractions are fine ("Here's my recommendation…"). Walk diagrams step by step in reading order.
- **IF ASKED** holds bounds and caveats that did not fit on the slide (1 model, same tasks, n = 25), and fairness
  caveats the audience may raise.
- **No MUST HIT section**, and no "The point of this slide:" meta talk (lint D004).
- **No meta or defensive lines** (lint D005). State what happened and what it means. Delete sentences like
  "I'm not going to show the design yet", "I'm not claiming it is", "I'll show…", "this talk will…",
  "for a fixed benchmark that's fine". Replace with the concrete statement, or nothing.
- Notes never introduce a claim that the slide and the report do not contain.
- A core content slide needs at least ~20 SAY words (lint D002).

## Timing and words budget

Words budget: SAY words ≤ seconds × 2.3 (lint D001, an error); aim for about 1.7 words per second. Speaking rate
is about 140 wpm, minus time for pointing and pauses.

| Slide type | Seconds | SAY words (max) |
|---|---|---|
| Title, divider | 5-20 | 10-20 |
| Background concept | 35-45 | 60-80 |
| Paper intro / figure | 30-45 | 50-75 |
| Paper result (chart) | 35 | 50-60 |
| Rule slide | 30-40 | 40-80 |
| Synthesis table | 30 | 35-50 |
| Design overview figure | 90 | ~200 |
| Design part (figure or table + THUS) | 35-45 | 50-95 |
| Next / open questions | 25-30 | 15-30 |

- The build result reports `core_time`, `total_time` and `budget.status` (`ok`, `over target`, `OVER BUDGET`).
  Plan about 10% under the slot (a 45:00 slot: target 40:00, max 45:00).
- Several talks sharing 1 slot: give each spec a `meta.id` and build all with the same
  `--times-file deck-times.json`. The result's `ledger` sums the core times of every deck and checks the sum.
- Check the built decks against that file together, so a deck rebuilt without updating the file is caught:
  ```
  tundlekit deck lint workflow.pptx capsule.pptx --times-file deck-times.json
  ```
  Each deck's id is its file stem. When the times file uses other keys (the spec's `meta.id`), give them in deck
  order with `--ids`:
  ```
  tundlekit deck lint build/workflow-v3.pptx build/capsule-final.pptx --times-file deck-times.json --ids workflow capsule
  ```
  D013 flags a deck whose measured core time differs from its entry. When an id is missing from the file, the
  D013 message lists the keys that are present and suggests `--ids`. D008 then checks the **combined** core time
  of all decks against the budget.
- Over budget: hide or drop insertion slides first, then cut in the order above.

## Insertion slides

Time is controlled by hiding or deleting insertion slides, never by trimming core slides.

- Mark with `"insert": true` on a content slide placed directly after the core slide it deepens. It is numbered
  after that slide (`4a`, `4b`), so core numbers never shift; its notes open with the INSERT line.
- `--inserts shown` (normal), `hidden` (in the file, skipped in the slideshow), `off` (left out). The result
  reports core and insert time separately.
- Self-contained: its title carries the point, its face makes it, its SAY says it. It never says "as we saw",
  "as I said", "as mentioned", "next slide" or "coming up" (lint D006).
- No core slide refers to an insertion slide by number ("see slide 4a", lint D007), and no insertion slide
  refers to another.
- Every claim on it already stands in the matching report with its source. Nothing new is argued.
- It must not break the THUS strip or the SAY hand-off of the core slide before it.

## Deck and report: 1 argument, 2 formats

| | Deck | Report |
|---|---|---|
| Content and coverage | same | same |
| Voice | spoken, plain, short sentences | formal, impersonal (style card) |
| Detail | enough to follow without the speaker | full, with limitations lists and appendices |
| Order | strictly build-up: evidence → rule → design | may state the design up front, then justify each part |
| Uncertainty | "Proposed" divider; "my proposal" in notes | a plain "proposed" sentence plus a labelled limitations list |

If the report has a section, the deck has a slide, or an explicit cut agreed with the owner, and the reverse.
Rule numbering and names match between deck and report. The report-writing skill has the element mapping.

Check it mechanically before the review:

```
tundlekit review coverage report.md build/deck.pptx --cuts cuts.txt
```

A section is covered when a slide's source footer cites it (`Report §2.3`) or the slide title is close to the
heading. C001 lists report sections with no slide, C002 slides that cover no section, C003 footers citing a
section that does not exist, C004-C006 rules (`R1`…) missing on one side, named differently, or repeated on
several slides. Record agreed cuts in `cuts.txt`, 1 per line (`§2.7`, `slide 12`, `#` for comments), so they stop
being reported. Cite the report section in every content slide's `source` to make coverage exact.

## Carrying hand edits back

When the owner edited a built deck, never rebuild over it until their edits are in the spec:

```
tundlekit deck diff build/deck.pptx edited/deck.pptx --search deck-src
```

Each change names the slide, the field (`title`, `text`, `notes`, `hidden`, `number`, `added`, `removed`,
`moved`), the old and new text with a unified diff, and `hint`: up to 3 `path:line` places under `--search` where
the old text occurs, which is usually the line of the spec to edit. Apply every change to the spec (for many small
text edits, `tundlekit text apply-edits EDITS.json deck.json` applies anchored replacements and fails if an anchor
is not unique), back up, rebuild, and diff again: the result should list only changes you chose not to carry.

**After cuts and reorders.** The owner often deletes, inserts and reorders slides, which renumbers everything
after them. Deck diff pairs slides by title first (exact, then similarity ≥ 0.8), then by number text, then by
position (both only when titles are still ≥ 0.4 similar), so a renumbered or moved slide is still paired with its
old self:

- `slide` is always a string label: the new slide's number text (`"7"`, `"4a"`), or `"#3"` (its position) when
  the slide shows no number. For `removed` it is the old slide's label.
- `number` (`old`, `new` are number texts): the same slide now shows another number. Usually a side effect of a
  cut or insertion before it; nothing to carry unless the spec numbers slides by hand.
- `moved` (`old`, `new` are 1-based positions): the slide changed order relative to the others, beyond what
  insertions and removals explain. Reorder the spec's `slides` list to match.
- `removed` / `added`: cut or new slides. A cut goes into the spec (and into `cuts.txt` for `review coverage`);
  a heavily retitled slide can also show up as a `removed` plus `added` pair, so compare the 2 before deleting.
- A table gives at most 1 `text` change, with a row-by-row diff (cells joined with ` | `).

## Lint rules (`tundlekit deck lint`)

| Rule | Severity | Finding |
|---|---|---|
| D001 | error | SAY words > seconds × words per second |
| D002 | warning | core content slide with fewer than 20 SAY words |
| D003 | error | em dash in a title |
| D004 | error | notes with `MUST HIT` or "The point of this slide" |
| D005 | warning | meta/defensive SAY ("I'm not going to", "I'm not claiming", "I'll show", "I'll go through", "I'm going to show", "Instead I'll", "this talk will", "that's fine for") |
| D006 | error | insert slide that says "as we saw", "as I said", "as mentioned", "next slide", "coming up" |
| D007 | error | non-insert slide that mentions an insert slide by number |
| D008 | error / warning | core total over max / over target |
| D009 | warning | content slide with no source footer (built decks: no text low on the slide besides the number) |
| D010 | warning | `et al.` or "Eq. N" on the slide face |
| D011 | warning | title longer than 90 characters |
| D012 | error | slide without TIME (built decks) |
| D013 | error | a deck's core time differs from its entry in `--times-file` |
| D014 | warning | em dash, a stray double period, or a double space mid-sentence in slide text or SAY |

Tool arguments `words_per_second`, `target` and `max` override the spec meta; `--strict` makes warnings fail too. A spec run and a .pptx run
should both be clean before review.

## Known noise

Lint and diff output is a starting list to confirm. The remaining false positives per tool:

- `deck lint`: D005 on a listed phrase used in a real statement ("I'll show the numbers from the second run" can be
  fine; rephrase if in doubt); D009 on built decks whose footer sits high on the slide; D013 when deck ids are not
  the file stems (pass `--ids`); D002 on short core slides that are deliberately brief (a quote slide).
- `deck build`: overflow warnings use a characters-per-line estimate, so a warning on text that visibly fits (or
  none on text that does not) is possible; the rendered slide decides.
- `deck diff`: a heavily retitled slide shows as `removed` plus `added`; `hint` may point at a spec line holding the
  same text on another slide.
- `review coverage`: slides without a `§` footer are matched by title only, so a reworded title gives a false
  C001/C002 pair.
