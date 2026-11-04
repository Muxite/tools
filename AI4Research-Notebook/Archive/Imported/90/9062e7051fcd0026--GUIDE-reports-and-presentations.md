# Guide: technical reports (.docx) and presentations (.pptx) for this user

Written 2026-09-14 from the user's feedback during the capsule and workflow deck rework. Grounded in
`report-capsules/deck-src/build_deck.py` (the current best example), `report-general/build/deckkit.py`,
`figures.py`, `palette.py`, `40-style-card.md`, `report-general/HANDOFF.md` §5-§10f and the capsule report text.
Where an older note disagrees with this guide, this guide reflects the later user decision (see §9).

---

## 0. Quick checklist (1 page)

**Before building**
- [ ] Read HANDOFF hard rules (§8 below). Repos read-only. Word and PowerPoint closed
      (`Get-Process WINWORD,POWERPNT -ErrorAction SilentlyContinue`) before writing any Office file
- [ ] Has the user hand-edited the last built .docx/.pptx? Diff it, carry edits into the script, then regenerate
- [ ] Back up the current deliverable to `versions/<name> (before <change> <date>)`
- [ ] Deck and report cover the SAME claims, evidence, design and open questions (list both outlines side by side)
- [ ] Every design choice has a reason or a paper next to it. No orphan choices
- [ ] Every term, system and figure element is defined before it is used
- [ ] Genuine design decisions: ask the user, with a recommended option. Do not guess
- [ ] Every number traced to an opened source (page, table, file:line)

**While building**
- [ ] Order: background → evidence, each followed by its design rule → today's state → design (collects the rules) → evaluation → next → open questions
- [ ] Each research slide: DEMONSTRATED BY <paper title> · <setup>; findings in plain prose with the number inside
- [ ] Each design slide: THUS strip stating the plan that follows
- [ ] Slides carry the script; notes rephrase the slide in first person plus a little extra; IF ASKED allowed; no MUST HIT
- [ ] Diagrams: 1 box per model call; colour = stage; style = actor (MODEL / CODE / record) with a legend
- [ ] Key properties in titles and labels ("Append-only and versioned: …"), not buried in notes
- [ ] Unfamiliar system (e.g. Darwin Gödel Machine) gets its paper figure or a drawn mechanism
- [ ] Report prose in the 40-style-card voice: impersonal, "Thus", lists carry enumeration, no em dashes

**User rules added 2026-09-14 night**
- [ ] Fewer slides; merge a table and a diagram into 1 diagram the presenter can talk over. Rule slides stay
- [ ] Every heading (report) and title (slide) states its point in 1 line, not a topic label
- [ ] Every paper is named by title where it is cited, at least once per section or slide, never only [n] or an id
- [ ] "So what" review: a Sonnet reviewer answers "so what?" for every section, paragraph, bullet, row and slide;
      anything without an answer is cut. It also checks that the slides alone communicate the point and that the
      spoken notes say that and more
- [ ] Both talks fit 45 min comfortably (plan about 35-40 min); there is no server admin in the audience

**After building**
- [ ] `save(deck=...)` output: combined planned time ≤ 40:00 target, 45:00 max; no WARN overflow lines
- [ ] Render every slide and page to PNG, build contact sheets, look at each one (§7)
- [ ] Adversarial review against the flaw classes in §7; for each flaw found, search for every other instance
- [ ] `rg -n "—| we | our |⚠|\[verified\]|\[proposed\]|\[doc\]"` over report text returns nothing
- [ ] Update DECK-PLAN / HANDOFF notes with what changed and where the backup is

---

## 1. Deck and report: 1 argument, 2 formats

| | Deck | Report |
|---|---|---|
| Content and coverage | same | same |
| Voice | spoken, plain, short sentences | formal, impersonal (40-style-card) |
| Detail | enough to follow without the speaker | full, with limitations lists and appendices |
| Order | strictly build-up: evidence → rule → design | may state the design up front (e.g. Fig. 3 opens §4), then justify each part |
| Uncertainty | "Proposed: nothing here is built or measured yet" divider; "my proposal" in notes | a plain "proposed" sentence plus a labelled limitations list |

- Differences are wording and ordering forced by the format, never content. If the report has a section, the
  deck has a slide (or an explicit cut decided with the user), and the reverse
- 2 argument shapes only: **claim → backup**, or **explain → "thus the plan is X"**. Nothing mysterious, nothing
  referenced before it is introduced

---

## 2. Deck structure template

| # | Section | Slide types | Notes |
|---|---|---|---|
| 1 | Title | title_slide | 1-sentence subtitle that says what the thing is |
| 2 | Goal | 1 slide, stage-coloured | the goal, what already exists, the real question, and the talk plan |
| 3 | Background | 1 slide per concept, short | define protocol/platform/layers the audience will misuse (MCP, DSH) |
| 4 | Divider "The evidence" | divider | "Each result, then the design rule it leads to" |
| 5 | Evidence blocks | per paper: what it is (figure) → how it works + result → where it falls short → (why it does not transfer) | each research slide has DEMONSTRATED BY |
| 6 | Rule slide after each block | `rule_slide` "What this means: …" | numbered rules R1…Rn, 1 line each (+ continuation) |
| 7 | Synthesis (optional) | table across papers | e.g. "Judging only by outcome breaks at every level" |
| 8 | Today | table of gaps in current code | file:line in the footer |
| 9 | Divider "The design" | divider | "Proposed: nothing here is built or measured yet" |
| 10 | Design overview | the full design figure | longest notes of the talk; walk it step by step |
| 11 | Rule collection | table: Rule · In the design · Because (paper) | THUS "every box in the design answers 1 of these rules" |
| 12 | Design parts | 1 slide per mechanism, each with THUS | generalist, DAG, recurrence, roles, manifest, gate, selection, lifecycle, platform mapping |
| 13 | Evaluation | tracks + "what would prove it wrong" | prediction stated in advance |
| 14 | Next | order of work | riskiest assumptions tested early |
| 15 | Open questions | table: For (design / supervisor) · Question; there is no server admin | end on the decision that unblocks most |

**Worked example (capsule deck, current script)**

```
Title → Goal → MCP is a protocol, not a tool → What each layer answers → DeepSeek Harness: everything is a plugin
── The evidence ──
Alita-G ×4 (exists · how + result · where it falls short · why it does not transfer)
  → RULE "2 clocks and a managed library"   R1 separate clocks · R2 pinned versions · R3 validate · R4 no duplicates
Beyond Task Completion ×2 · CoEvoSkills · Darwin Gödel Machine ×2 · "breaks at every level"
  → RULE "an independent check"             R3 held-out tests · R6 separate suite author, code gate, protected components
AllocBench
  → RULE "decide separately, build on repeats"  R5
Today: 79 hand-written capsules, 5 gaps
── The design ──
Design figure → "The design rules, and the evidence behind each" (R1-R6 table) → generalist → frozen DAG
→ recurrence → roles → manifest → gate → selection → append-only → retirement → updates → DSH mapping
→ evaluation → order of work → open questions
```

The earlier version had a single "6 changes" slide at the start of the design act. The user split it: each change
now appears as a rule right after the evidence that motivates it, then all 6 are shown together at the design stage.

**Cutting for time** (in this order): extra papers → SoTA comparisons → challenge lists → background depth.
Never cut a main point, a rule slide, or the design overview.

---

## 3. Slide-writing rules

| Rule | Why |
|---|---|
| Slides almost ARE the script: a reader with only the slides follows most of the talk | thin slides were the main complaint |
| Title = the takeaway sentence, not a topic label | the audience remembers titles |
| Research slide: `d.measured(s, "<Paper title> (arXiv id)", "<setup: data, model, n>")` | people remember titles, not "Zhang et al."; setup bounds the claim |
| Use the paper's real title, never a nickname | it is "Beyond Task Completion", not "silent rot" |
| Findings in plain prose with the number built in | no "Eq. 5", no "evidence in paper" columns |
| Charts get a 1-2 line bold takeaway under them (`point()`) | the chart must explain itself |
| Design slide: `d.therefore(s, "…")` states the plan | explain → thus |
| Background slides short, but correct (MCP = client-server protocol; a tool is 1 of 3 server primitives) | define before use without bloat |
| Unfamiliar system: reproduce the paper's figure, or draw the mechanism | the DGM slide "made 0 sense" without Fig. 1 |
| Important properties go in the title or figure label | "Append-only and versioned: nothing is edited or deleted" |
| Source footer on every content slide (paper table/figure, report §, file:line) | everything justified |
| Merge or cut low-value slides; no weird ordering | bloat hides the argument |
| Big text: body ≥ 18 pt, tables ≥ 14 pt, figure labels readable at slide width | readable from the back |
| No em dashes, above all in titles; say it as a normal sentence, or use a colon or a full stop | an em-dash title makes the presenter pause instead of reading it out; there is almost always a shorter, more human phrasing |

**Before → after (from the rework)**

| Before | After |
|---|---|
| Title "Silent rot" | "Do self-made tools work beyond the task that made them?" then "96.8% of kept tools fail those tests" |
| "Kaliyev and Maryanskyy measured…" / MEASURED BY strip | `DEMONSTRATED BY  Beyond Task Completion (arXiv 2604.00392) · 99 tasks, Haiku 4.5, 222 kept tools` |
| "Eq. 5 is the only gate" | "It keeps every tool from a run with a correct answer, whether or not that tool helped" |
| "Effective coverage 1.00 → 0.51 (Table 4)" | "It never removes duplicates: as the library grows from 26 to 128 tools, the share of distinct tools falls from 100% to 51% and accuracy stops improving" |
| "Threshold sensitivity: ±16 pp" | "Retrieval is fragile: changing the similarity threshold moves accuracy by 16 points on 25 questions" |
| DGM diff shown alone | Fig. 1 + 3 bullets on how it works, then the diff slide with the task, the 1.67 vs 2.00 scores, and "the checking code was hidden from it" |
| "1 claim, 1 number, 1 picture; detail in the presenter's head" | 4-5 full-sentence bullets or a table that carries the point |
| "6 changes" slide opening the design | R-rules after each evidence block + 1 collection table at the design stage |
| Box "Build" | build-decision agent (MODEL) → suite author (MODEL) → implementation agent (MODEL) → admission gate (CODE) |

---

## 4. Speaker-note rules

Format (built by `d.notes(s, time, say=..., asked=[...])`):

```
TIME 0:45
SAY: <the slide rephrased, first person, conversational, plus a little extra>
IF ASKED:
- <likely question: short answer>
```

- SAY = what the slide says, in the user's speaking voice, plus the connecting sentence to the next slide
- First person, contractions fine ("Here's my recommendation…", "So the loop isn't new. What matters is where it stops working.")
- Walk diagrams step by step in reading order ("Walking the ticks: A, B and F are ready, but F waits because…")
- No MUST HIT section (`hit=` is legacy in deckkit; do not pass it). No "The point of this slide:" meta talk
- **State what happened and what it means.** No announcing what the talk will or won't do, no pre-emptive
  disclaimers, no hedges about fairness. The user deleted these by hand:

  | Deleted (meta / defensive) | Keep instead |
  |---|---|
  | "I'm not going to show the design yet" | (nothing; just go to the evidence) |
  | "So the loop itself isn't new, and I'm not claiming it is. What I care about is where this loop stops working... The next 4 slides are about that." | "So the loop isn't new. What matters is where it stops working." |
  | "For a fixed benchmark that's fine. For a system that runs for weeks, it isn't." | the concrete difference: "It builds its library once for a fixed benchmark and then freezes it. We never stop." |

  Fairness caveats the audience may raise go under IF ASKED, not in SAY
- IF ASKED: bounds and caveats that did not fit on the slide (1 model, same tasks, n = 25)
- Notes never introduce a claim the slide and report do not contain
- Length: TIME × ~2 words/second at most (§6)

**Example (design overview, current script, abridged)**

> SAY: Here's my recommendation for Capability Capsule. When planning can't find a suitable capsule for a step, it
> uses the generalist capsule instead. On that first run we don't build anything, but we store a gap record […]
> When the same gap keeps coming back across sprints, a separate build-decision agent looks at those costs and
> counts and decides whether to build a new capsule, version an existing one, or wait. If it builds, it writes the
> manifest, and a suite author writes the tests from that manifest alone, so the gate is fixed before any
> implementation starts. […] gets a limited number of tries at the gate, hearing only admit or reject with a reason.
> IF ASKED:
> - Why cap the tries: unlimited retries let the builder learn the tests

---

## 5. Report rules

**Voice** (`40-style-card.md`, HANDOFF §6)
- Impersonal: no "we", "our", "I". No em dashes. No hedging verbs. No rhetorical questions in body prose
- Mean sentence ~24 words; triads; "Thus", "Akin to"; numerals for small numbers; slashes for near-synonym sets
- Assert flat, then bound with a labelled list: "There are two limitations to this result:" + bullets
- Lists: parallel, verb- or gerund-first, no terminal punctuation, no sub-bullets
- Status in plain words ("Everything in this section is proposed"), never in markers or softened verbs

**Ordering differences allowed**
- §4 may open with the design figure and a paragraph walking it, then justify each part in subsections
- Evidence sections still end each paper with a "Thus, …" consequence, so the rules exist before the design
- Limitations as lists after each result; full per-paper numbers, inventories, rejection reasons, platform facts,
  dispatch rules go to appendices, referenced from the body

**Deck element → report element**

| Deck | Report |
|---|---|
| Goal slide | §1 opening paragraph + goal statement |
| Background slide (MCP, DSH, layers) | §1 paragraphs + figure; facts in an appendix (App. D, E) |
| DEMONSTRATED BY strip | "In <paper title> [n], …" with the setup in the sentence; locators as [n, Table 5] |
| Plain-prose finding bullet | 1 sentence with the number, then the limitations list |
| Chart + takeaway line | figure with a caption that states the takeaway; table in the appendix |
| Rule slide ("What this means: …") | closing "Thus, the design …" paragraph of that subsection |
| Synthesis table | numbered table with a 1-sentence lead-in |
| "Today" gaps slide | §3 list "Five things the current code does not yet give…" with file:line |
| Divider "Proposed" | §4 opening sentence: "Everything in this section is proposed. None of it is built or measured." |
| Design overview figure + long SAY | §4 opening paragraph + Fig. 3 |
| Rule collection table | §4.1 table of changes, each row with its reason and citation |
| THUS strip | "Thus, …" sentence ending the subsection |
| IF ASKED bullets | limitations lists, or appendix detail |
| Evaluation / prove-wrong slide | §4.11 tracks, prediction, "would be proven wrong by" list |
| Open questions table | §5 lists grouped by owner |

Check: the rule numbering or change list must match between deck and report (same count, same names).

---

## 6. Diagram rules (`palette.py`, `figures.py`)

| Rule | How |
|---|---|
| Colour = stage | `STAGE`: intent, binding, freeze, dispatch, gates, claims, build, library, external (Okabe-Ito based) |
| Style = actor | model call: tinted fill + MODEL tag; deterministic code: white fill, stage border + CODE tag; record: folded corner; external: grey |
| 1 box per model call or session | never 1 box hiding several model uses; split "Build", "review", "build and check" |
| Legend on every diagram with more than 1 actor | `legend(ax, …)`; add "1 box = 1 model session" |
| Nothing depends on colour alone | every box also has a text label; outcome colours only for node states |
| Big text | labels readable at slide width; render dual size (slide and report) via `dual()` |
| Draw mechanisms people misread | mock DAG over ticks: dependencies, a failure skipping children, write-scope conflict waiting, gates "FIXED AT THE FREEZE" |
| Properties in labels | library cylinder labelled "append-only · versioned"; "PROTECTED" strip on the gate |
| Reuse the paper's figure | when explaining someone else's system (Alita-G Fig. 1, DGM Fig. 1); caption "reproduced from [n, Fig. 1]" |
| Draw your own | for your design, and for mechanisms the paper only describes in text |
| Illustrative content marked | "(illustrative)", "Example servers are illustrative" |
| Charts | native editable PowerPoint charts; grey bars with 1 highlighted bar; data labels on; n in category labels |

---

## 7. Timing

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

- Speaking rate ~140 wpm; leave room for pointing at figures and pauses. The current capsule SAY text averages ~97
  words per planned minute (2,337 words over 24:05), with the design overview at ~135
- Words budget ≈ seconds × 2.3 at the most; aim for ~1.7
- Both talks share 1 slot: **target 40:00, max 45:00**. Current plan (`build/deck-times.json`): workflow 16:25 +
  capsule 24:05 = 40:30. `Deck.save(deck="general"|"capsule")` records and checks the sum
- Over budget: cut papers, SoTA, challenges first (§2)

---

## 7a. Insertion slides (2026-09-15)

Time is controlled by deleting or hiding insertion slides, never by trimming core slides. Rules:

- Built with `d.slide(..., insert=True)`; numbered after the core slide they follow ("9a"), so core numbers never
  shift. The notes open with an INSERT line; `Deck.save()` reports core time and insertion time separately, and
  `deck-times.json` stores both. `DECK_INSERTS=hidden` builds them hidden (skipped in the slideshow), `off` drops them.
- Self-contained: the title carries the point, the face makes it, the SAY says it. No core slide may refer to an
  insertion slide, and an insertion slide may not refer to another insertion slide or say "as we saw" or "next".
- Every claim on an insertion slide already stands in the matching report with its source; nothing new is argued.
- Placed directly after the core slide whose topic it deepens; an insertion between 2 core slides must not break
  the core slide's THUS strip or the SAY hand-off to the next core slide.

## 8. Review procedure

1. **Build** from the script only; never hand-edit then regenerate over it
2. **Render** each slide and page to PNG (export via LibreOffice headless or a PDF of the file, never by opening
   Word/PowerPoint while scripts write), then make contact sheets (e.g. 4×3 per sheet) and a full-size look at every
   figure slide
3. **Read slides alone** without notes: can the talk be followed? If not, move content from notes to the slide
4. **Adversarial pass** against the flaw classes below, as a hostile reader of the user's instructions
5. **Propagate**: for each flaw found, search the script, report and figures for every other instance and fix all
6. **Gaps in the user's own explanation**: cover them and tell the user (e.g. uncapped gate retries would leak the
   held-out tests, so submissions are capped with admit/reject + reason code only)
7. **Record** the review as a table (Flaw class · Found · Fix) in DECK-PLAN or HANDOFF, plus what is left for the user

**Flaw classes**

| Class | Test |
|---|---|
| Box hides >1 model call | count model sessions in the prose; count MODEL boxes |
| Term before definition | first use of every term vs its defining slide/section |
| Paper nickname or author names | every paper reference is its title (+ arXiv id) |
| Setup unstated | every result says data, model, n |
| Choice without justification | every design element maps to a rule or stated reason |
| Property only in prose | key properties appear in a title or figure label |
| Thin slide | slide text alone carries the point; SAY ≥ ~20 words |
| Jargon | "Eq.", "pp", internal codes on slides without explanation |
| Coverage mismatch | report sections vs deck slides, 1:1 or agreed cut |
| Ordering | nothing used before introduced; research before system |
| Layout | text overflow WARNs, strips overlapping tables, small figures |
| Over-claim | "proposed" stated; bounds (1 model, same tasks) present |
| Legacy notes | no MUST HIT, notes in first person |
| Meta / defensive notes | no "I'll show…", "I'm not claiming…", "that's fine for X, but…" in SAY |

**Hard rules (HANDOFF §5)**
- Repos under `C:\Users\mukch\projects\work\` are read-only
- Verify every claim against an opened source; never cite an unopened paper
- No ⚠, corrections tables, `[verified]`/`[doc]`/`[proposed]` markers or bracketed placeholders in deliverables;
  provenance stays in notes
- Word and PowerPoint closed before writing Office files (`~$` lock files are unreliable on OneDrive)
- If the user edited a built file: diff it, carry the edits into the script, then regenerate
- Back up to `versions/` before every change
- Ask before spawning review subagents

**Past mistakes not to repeat**
- Sparse "1 claim, 1 number, 1 picture" slides with the content left in the presenter's head
- Author names ("Qiu et al.") and nicknames ("Silent rot") instead of paper titles
- "Eq. 5", "coverage ratio", "evidence in paper" columns in place of plain findings
- A DGM slide with no picture of how DGM works
- "Build" as 1 box; "requirement reviewer" and "build and check" hiding model calls
- The generalist used on the DAG slide before its own slide; EFFECT_ESCALATION used before definition
- "6 changes" presented at the start of the design with no evidence in front of them
- "Append-only" only in prose; retirement and updates unexplained
- 19 slides with under ~20 spoken words; MUST HIT lists instead of a script
- Meta and defensive note sentences ("I'm not going to show the design yet", "and I'm not claiming it is",
  "For a fixed benchmark that's fine…")
- Uncapped gate retries (tests leak); generalist outputs as expected results (suite admits repeated mistakes)
- MCP described as a tool; DSH never explained
- A THUS strip placed over a table; a DAG figure too small to read

---

## 9. Where existing files disagree with this guide

- `deckkit.py` docstring still says "black and white", "exactly 1 body … ≤ 5 bullets", "Detail goes in the notes",
  and `notes()` still accepts `hit=` (MUST HIT)
- `report-general/build/build_deck.py` (workflow deck) passes `hit=` on most slides and its SAY text is terse and
  impersonal ("The point of this slide: …")
- `DECK-PLAN.md` "Design principles" (presenter-led sparse slides) and the rework note ("MEASURED BY strip",
  "notes are SAY / MUST HIT / IF ASKED", "6 changes" slide, "what remains open" slide) are superseded
- `HANDOFF.md` §10f still lists notes as SAY / MUST HIT / IF ASKED
- `40-style-card.md` recommends `[proposed]` status markers and `[footnote …]` gap markers; HANDOFF §5 bans markers
  in deliverables (use plain "proposed" and limitations lists)
- Capsule `build_deck.py`: the goal slide SAY still announces the talk ("I'm not going to pitch the idea itself.
  Instead I'll go through the research…"); the 96.8% and rules-table notes still say "silent rot" as a name for the
  paper; R3 appears on 2 rule slides and "R6" labels 3 lines of 1 slide
- Capsule report vs deck: the report names authors ("built and measured by Qiu et al.", 2 different "Zhang et al.")
  rather than leading with titles; §4.1 Table 4 is "6 changes" while the deck says R1-R6 (check names match);
  §2.7 "What remains open", §3 control group and A2A, §4.7 reversibility list and §4.10 "Where it runs" have no deck
  slide (coverage gap, or an agreed cut to record)
