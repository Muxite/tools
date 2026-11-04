# Deck plan — cut from the report (rev 3)

> **2026-09-15 afternoon, last-quarter cut.** The user's first run-through took about 25 min with all 8 insertion slides
> shown, and everything after the design figure (slide 18) dragged and repeated it. Now **23 core slides, 18:05**
> (19:35 with the 2 remaining insertions 9a and 13a; both talks core 33:20). Cut: the generalist DAG slide, the
> recurrence-and-roles slide, the verify-first table (its first 4 rows, each with its step number, sit on the
> evaluation slide), and the 6 design-half insertions (18a, 19a, 23a, 24a, 26a, 26b). The once-per-sprint count
> moved to the R6 rule slide; the generalist's 3 properties moved into the design slide's notes. Admission,
> selection, lifecycle and next notes shortened; the embeddings proposal, the duplicate check detail, "model weights
> never change" and the questions on research contribution, credentials and multi-tenant runs moved to IF ASKED or
> the report. The user's 3 hand edits in the saved pptx (R3 "must pass", slide 16 "Generalist capsule and gap
> record", slide 19 "due to the DGM lesson") are in the script. Everything cut stands in the report unchanged.
> Backup: `versions/… (before last-quarter cut 2026-09-15).pptx`; presenter pack updated.

> **2026-09-15 overnight.** Now **26 slides, 20:30** (35:55 with the workflow deck at 15:25). Slide 24 rebuilt,
> new slide 25 "What to verify first", slide 26 next/deciding in 3 groups; rule slides carry source footers; slide 9
> states on its face that the 222 tools are not Alita-G's. Reviews and applied/rejected lists:
> `notes/overnight/review/R-capsule-deck.md`, `SOWHAT-capsule.md`. The "27 slides, 19:20" below is superseded.

> **Review pass, 2026-09-14 night.** 4 Sonnet "so what" reviewers (both decks, both reports). Applied: R5 and R6
> swapped so rules appear in ascending order (R5 = independent check, R6 = decide separately) in deck, figure badges
> and report Table 4; sprint, node, trust class, freeze and gap record defined at first use; Cordis and "blast radius"
> removed from slides; G/C legend on the sprint figure; AllocBench lines in 4 colours; axis note on the Beyond Task
> Completion chart; figure pointers and a key for "(exists)" in the report; App. B counts reconciled (74 of 79
> manifests registered); §1 maps the 9 capabilities to Section 4; informative headings; papers named by title.
> Rejected: cutting the user's own "Akin to how people learn" analogy. Not done: redrawing the Alita-G and DGM paper
> figures (small text), splitting the design figure, restyling the workflow deck (its review is the input for that).
> Report edits: `deck-src/edit_report_headings_names.py`, `edit_report_review_fixes.py`, `edit_report_no_admin.py`,
> `edit_report_figs.py`; backups in `versions/`.

> **26-slide cut, 2026-09-14 night (supersedes the slide order below).** User: 38 slides is too long; carry the talk
> with diagrams to talk over. Now **27 slides, 19:20** (35:45 with the workflow deck). Merged into 1 diagram each:
> layers + DSH → `fig-stack`; design figure + rules table → `fig-goal-rules` (R1-R6 badges on the boxes); recurrence +
> roles table → `fig-sprint-roles`; manifest table + gate → `fig-admission` (field → check → rejection code, N tries,
> protected box). Also merged: Alita-G 4 → 2 slides, Beyond Task Completion 2 → 1, outcome table into the R3/R6 rule
> slide, versions + updates, order of work + open questions. The 3 rule slides stay (user). Uncovered report
> sections folded in (user): A2A on the stack slide notes, control group on evaluation, §4.7 "what may change" in the
> admission THUS strip, §4.10 "where it runs" in the questions table. R3 now appears on 1 rule slide only; R6 is 1
> label. Figure fixes that also touch the report (Fig. 4, 8, 10, swapped in by `deck-src/edit_report_figs.py`): design
> figure label placement and "scripts, logs" now from the generalist; gate bullet wrap; versions figure said a
> specialization was "contract changed, so a new id". Selection figure left as is: embedding rank is a model use.
> Backups: `versions/capsule build_deck (before 26-slide cut 2026-09-14).py`, `figures (…).py`, report docx.

> **Latest, 2026-09-14 evening (superseded above for order). Read `../GUIDE-reports-and-presentations.md` first.**
> The talk builds the system from evidence: background (goal, MCP, layers, DSH) → Alita-G (exists, how it works,
> where it falls short, why it does not transfer) → rule slide R1-R4 → Beyond Task Completion ×2 → CoEvoSkills →
> Darwin Gödel Machine ×2 (paper Fig. 1, then the gaming case) → outcome-only table → rule slide R3/R6 → AllocBench
> → rule slide R5 → today → design diagram (big text) → rules table R1-R6 → generalist → DAG → recurrence → roles →
> manifest → gate → selection → append-only → retirement → updates → DSH → evaluation → order → questions.
> 38 slides, 24:05 (40:30 with the workflow deck). Cut: 3-loops slide, "6 changes", "what remains open", separate
> Alita-G result slide. Slides carry the script; notes = rephrase + a little extra, no MUST HIT; DEMONSTRATED BY
> <paper title>; no em dashes. Report mirrors it (`deck-src/edit_report_evidence.py`): rule paragraphs R1-R6 in §2,
> DGM explained with its figure (report Fig. 3), Table 4 = rules table, papers named by title.

> **Later 2026-09-14, user decisions (supersede the order and design notes below where they differ):**
> - **Research first, then the system.** Title → 1-sentence goal slide → MCP → layers → DSH → Act I → today →
>   Act II opens with the design diagram (Fig. 3 in the report, opening §4) → 6 changes → loops → generalist →
>   DAG → recurrence → roles → manifest → gate → selection → lifecycle ×3 → DSH mapping → evaluation → order → questions.
>   **37 slides, 25:38** (42:03 with the workflow deck; max 45).
> - **The build-decision agent writes the manifest**; the suite author writes the held-out suite from it, so the gate
>   is fixed before implementation. Cold path order: decide + manifest → suite → implement → gate → commit.
> - **Capped gate submissions**: the implementation agent gets only admit/reject + reason code, at most N tries; out of
>   tries or time, the gap returns to the build-decision agent (CoEvoSkills caps its oracle at 5 rounds). N is an open question.
> - Costs and counts go to the build-decision agent; generalist scripts and logs to the implementation agent only.
> - Title subtitle: "Self-improving tool ecosystem for agents, built on DeepSeek Harness, where everything is a plugin".
> - Speaker notes rewritten in the user's own speaking voice (first person, conversational); the design-slide script
>   is the user's own wording, corrected for the 2 decisions above. Report edit: `deck-src/edit_report_goal.py`.

> **Presentation rework, 2026-09-14 (supersedes everything below for order and style).**
> User asks: 1 box per model call; a shared DAG/dispatch figure; MCP explained properly; DSH explained;
> Alita-G explained with a script and why it does not transfer; papers named by title with who measured
> what; append-only/versioned prominent, retirement and updates explained; colour, coded by stage; claim →
> backup or explain → thus; both talks together ~40 min (45 max); cut papers/SoTA/challenges before main points.
> **36 slides, 23:33** (workflow deck 16:25, 39:58 together; `deckkit.save(deck=...)` checks the sum).
> Order: title · goal (Fig. 1, 3 model sessions + code gate) · MCP (Fig. 2) · layers · DSH · Act I: Alita-G ×5
> (exists, how, result, where it stops, why it does not transfer) · Beyond Task Completion ×2 · CoEvoSkills ·
> DGM · 3 levels · AllocBench · what remains open · today (5 gaps) · Act II: 6 changes · 3 loops (Fig. 4) ·
> generalist · frozen DAG with capsules (Fig. 5) · recurrence (Fig. 6) · why separate sessions (Table 5) ·
> manifest (Table 6) · admission gate (Fig. 7) · selection (Fig. 8) · append-only (Fig. 9) · retirement
> (Table 7) · updates (Table 8) · DSH mapping (Table 9) · evaluation · order of work · open questions.
> Style: `palette.py` (colour = stage; tinted box + MODEL tag = model call, white + CODE = code, folded corner
> = record); Act I slides carry `d.measured()`, design slides `d.therefore()`; notes are SAY / MUST HIT / IF ASKED.
> Figures all come from `../report-general/build/figures.py` (`fig_goal.py`, `fig-goal.png`, `fig-loops.png`
> here are superseded). Report edits: `edit_report_rework.py`, `edit_report_move_dag.py` (backup in `versions/`).
> The user's 14:27 hand edit (subtitle "Self-improving tool ecosystems for agents.") is carried into the script.
>
> Adversarial self-review done the same day, against this checklist; fixes applied:
> | Flaw class | Found | Fix |
> |---|---|---|
> | box hides >1 model call | workflow requirement reviewer; loops fit review; sprint "build and check" | split into own boxes |
> | term before definition | generalist on DAG slide; EFFECT_ESCALATION on today slide; DAG para in report §4.1 | generalist slide first; wording; moved to end of §4.3 |
> | paper nickname / measurer unstated | "Silent rot" titles; Act I slides | paper title; MEASURED BY strip; "by X et al." in report §2 |
> | choice without justification | build roles; versions vs new capsule | Table 5; Table 8 + monotone rule |
> | property only in prose | append-only | slide title, figure label, library cylinder |
> | thin script | 19 slides under ~20 spoken words | SAY text extended |
> | DAG lacks capability per node | card had no capsule mapping | "capsule bound per node" block |
> | layout | SoTA table under THUS strip; DAG too small | strip removed, figure enlarged |
> Left for the user: Table 4 header row breaks from its body across a page in Word; the orange italic
> paragraph in §4.4 ("The number of sprints…") predates this pass and was not touched.

> **Rebuilt 2026-09-14 in the engineering style (supersedes the notes below for layout):**
> `deck-src/build_deck.py` now uses the shared kit `../report-general/build/deckkit.py` and chart
> data `figdata.py`; same slide rules as the general deck (breadcrumb + short title, 1 table /
> figure / excerpt / ≤ 5 bullets, source footer, detail in notes). **36 slides, 22:00.** Act I:
> goal figure, 4 layers, Alita-G ×3 (native coverage chart), silent rot ×2 (native bar), CoEvoSkills
> (native column), DGM diff, 3 levels, AllocBench (native line), what remains open. Today: inventory,
> what the code lacks. Act II: sprint timeline, 3 loops, generalist ×4, builder roles, manifest,
> admission gate figure, rejection reasons, protected components, selection funnel, lifecycle, where
> it runs, capsules on DSH, evaluation ×2, order of work, open questions. Figures: `fig-goal.png`,
> `image1.png` (Alita-G), `fig-loops.png` here; sprint, gate, select from `../report-general/build/fig/slide/`.

> ⚠ **Rebuilt 2026-09-14** (general-report session, 20-minute elaboration pass): 22 slides,
> 21:35 planned. Changes: palette converted to greys (black-and-white rule of 2026-09-13);
> new slide 14 *What the current code does not yet give a library that agents extend*
> (versioning, gap signal, protected paths, observation, trust 21 of 79, model judgment 20 of
> 43), each row read in source at b0bf165f9; hot-path box marked "(new)" because no generalist
> fallback exists today (`UNSATISFIABLE_CAPSULE` fails the plan); order of work now 8 steps
> (versioning, gap record, deny list first); slide 13 notes add the binding layer. Former cut
> candidates 3, 18, 19 kept in. Report docx edited in place the same day; backups in
> `versions/… (before 20-min elaboration 2026-09-14)`.
>
> **Later 2026-09-14, generalist capsule (user-agreed design):** 23 slides, 23:05. New slide 17
> *The generalist is a capsule whose work can seed new capsules*: bound at planning to nodes no
> capsule or composition fits; judged by gates fixed at planning; lowest trust; leaves a gap
> record and trajectory; never writes to the library. 2 flags in the frozen run contract
> (`generalist_fallback`, `capability_authoring`). **Sprint** = 1 request from intent to
> closure (1 planning snapshot, 1 run contract, 1 ledger) and is the reuse boundary.
> Recurrence counts sprints, not nodes (5 parallel generalist nodes = 1 sighting, 5 examples).
> Trajectories go to the implementer only; generalist outputs never become expected results.
> Slide 16 hot path redrawn; slide 23 order of work and asks updated. Report: §4.1 sprint,
> §4.2-4.4 rewritten, §4.9, §4.11, §4.12 Table 6 (capsule concerns onto DSH), §5 questions.
> Backups `versions/… (before generalist capsule 2026-09-14)`.
>
> **Redundancy pass, later 2026-09-14** (this talk follows the workflow talk): slide 3 *Runs of
> days and weeks…* removed; "Model judgment" row dropped from the code-lacks slide (a reminder
> sits in its notes); slide 13 binding notes cut to 1 line. Hot-path notes add independent
> clocks, cold path on another server, no halting for now. **22 slides, 22:00.**

> ⚠ **Superseded by the built deck, 2026-09-11:**
> `../../AI4Research Capability Capsule Presentation - Muk.pptx`, 21 slides, ~18.5 min
> planned (timings in each slide's speaker notes). Same audience as the report.
> Changes from the plan below: added slide 13 *AI4Research already has hand-written
> capsules* and slide 16 *what a capsule declares* (pulled from Appendices B and C);
> AllocBench chart shows all 4 models; CoEvoSkills chart adds the background-only bar.
> Cut candidates if over time: 3, 18, 19 (~2.3 min). Charts are native, editable
> PowerPoint charts. Build script in `deck-src/` (regenerating overwrites manual
> edits in PowerPoint; edit the pptx directly once you start polishing).

Written 2026-09-11. **First sketch, for discussion.** Source of truth is the report
docx (rev 3, ~4,700-word body + Appendices A–D). The deck is **cut from it**, never
written separately (HANDOFF §1, reframe 3).

## Design principles

1. **Presenter-led, sparse slides.** The presenter knows the papers and has notes on
   most of them, so a slide carries **1 claim, 1 number, 1 picture**. The detail lives
   in the presenter's head and in the report appendices, not on the slide.
2. **Assertion titles.** Every slide title is the sentence the audience should
   remember ("Tools judged only by task outcome are broken"), not a topic label
   ("Silent rot").
3. **The wall.** Act I = measured by other people. Act II = proposed, not measured.
   A full-bleed divider slide separates them, exactly as the report's Section 4 opener does.
4. **Three levels is the spine.** Tools / skills / agents: outcome-only judgment
   breaks at every level. Each paper slide in Act I is one row of that table, and
   the table itself is the climax of Act I.
5. **DGM does double duty.** In Act I it is the *agents* row. In Act II node 114 is
   the justification for protected components (report §4.8). Show the same image
   twice so the audience makes the connection.

## Slide order — 20 minutes, 17 slides (cuts for 15 min marked ✂)

| # | Assertion title | Visual | Report § | Presenter carries |
|---|---|---|---|---|
| 1 | Capability Capsule in AI4Research | title | — | — |
| 2 | The goal: an AI that improves itself by keeping a library of its tools | self-extension ring: gap → build → check → install → reuse | 1 | This is the supervisor's premise, given not argued. Point at their diagram |
| 3 | Long runs need more abilities than humans can write, check or predict | the 9 capabilities grouped into 3: deciding · building · managing | 1 | "Days and weeks" is the whole difference from prior work |
| 4 | A capsule answers the question MCP and A2A leave open: may this run, and what will it do? | 4 stacked layers + capsule band | 1 | Layering, not rivalry. MCP tools-only on DSH; A2A only planned (App. D) |
| **ACT I — MEASURED** | | | | |
| 5 | The loop already works: Alita-G, 75.15% → 83.03% on GAIA with 15.5% fewer tokens | Alita-G Fig. 1 (already in report) | 2.1 | Same agent, with vs without the box. Harvested from the eval set |
| 6 | But it keeps a tool on 1 signal: did the final answer come out right | Fig. 1 again, Eq. 5 boxed as the only gate; coverage 1.00 → 0.51 inset | 2.1, A.1 | Fairness: proportionate for a fixed benchmark; dedup declined on purpose |
| 7 | Tools judged only by task outcome are broken: 215 of 222 score zero | bar chart by protocol, n on every bar | 2.2, A.2 | "The verifier scores task outputs, not tools." 1 model, 1 harness — say it before they ask |
| 8 ✂ | Unverified skills are worth almost nothing; verified ones beat humans | 4-bar: 30.6 · 30.7–34.1 · 53.5 · 71.1 | 2.3, A.3 | Oracle = the task's own reward; background alone = 42.4 |
| 9 | An agent judged only by its score games the score | node 114 diff: the 3 `TOOL_*_MARKER` lines deleted; 1.67 vs 2.00 | 2.4 | Checking functions were hidden from it. It changed what the check *reads* |
| 10 | Outcome-only judgment breaks at every level | the 3-row table (report Table 1) | 2.4 | **Climax of Act I. Pause.** |
| 11 ✂ | The builder should not decide what to build | 4% → 92% (Opus 4.8), one arrow | 2.5, A.5 | Share of commitments on first sight; price check was 1 model |
| 12 | What remains open is narrow | 1 sentence, large: *check what agent-written capabilities declare against what they do, mechanically, before admission* | 2.6 | Declaring isn't new (DSH catalog, our 79 manifests). Freezing a checker isn't new (DGM) |
| **THE WALL** | *Everything after this is proposed. Nothing is built or measured.* | full-bleed | 4 opener | ~5 s silence |
| **ACT II — PROPOSED** | | | | |
| 13 | 3 loops around 1 library: the hot path never waits for the cold path | loop diagram (report §4.1 figure — still to draw) | 4.1–4.3 | Gap recurs → abstraction agent decides → implementer builds → separate suite author |
| 14 | Admission is mechanical, and a capsule may never touch what the check reads | gate on the "install" edge + 4 protected components; node 114 image reused small | 4.5, 4.8 | Protection by write access, not secrecy. Declared effects make it checkable; sandbox enforces it |
| 15 ✂ | Embeddings rank; they never admit | 4-stage funnel | 4.6 | Skill bridge already does stages 1–2 for skills |
| 16 | Admission, not containment — and unattended runs lose the gated routes | 2-column: workstation vs shared server | 4.10 | For the server admin in the room |
| 17 | What we build first, and what we need you to decide | numbered order of work (5) + open questions by owner | 4.12, 5 | End on the asks: seam or layer; autonomous target; permission to execute capsules |

15-minute version: drop ✂ slides (8, 11, 15) → 14 slides + wall.

## Figures to make

| Figure | Status | How |
|---|---|---|
| Self-extension ring (2, reused in 13) | to draw | simple SVG / PowerPoint shapes |
| Alita-G Fig. 1 (5, 6) | **have it** — embedded in the report | reuse; add Eq. 5 highlight box for 6 |
| Silent-rot bar (7) | to make | from report Table A1; label every n |
| CoEvoSkills bars (8) | to make | from Table A2 |
| Node 114 diff (9, 14) | to make | the 3 marker lines from DGM App. H, struck through |
| 3-level table (10) | have it | report Table 1, set large |
| 3-loop diagram (13) | to draw | also fills the report's orange `[figure]` marker — make once, use twice |
| Gate + protected components (14) | to draw | ring from slide 2 with a gate on the install edge |
| 4-stage funnel (15) | to draw | from report Table 3 |

## Numbers said aloud — every one is in the report

75.15 → 83.03 · −15.5% tokens · coverage 1.00 → 0.51 · 215/222 = 96.8% · refs 1.00 on
16 suites · 30.6 / 30.7–34.1 / 53.5 / 71.1 (bg 42.4) · node 96 = 1.67, node 114 = 2.00 ·
4% → 92% · 79 manifests · 28 routes / 15 capabilities / 11 gated.

## Claims the deck must not make

Everything in `OUTLINE.md`'s "will not make" table, plus the corrections in HANDOFF §0a.
The live risks on slides, where compression tempts overstatement:
- Slide 7: not "outcome-*gated* admission" — tools **judged only through task outcome**.
- Slide 8: not "agents beat humans" unqualified — only **with verification**.
- Slide 9/14: not "DGM proposes our referee" — the quote is from its safety discussion;
  the novelty is **enforcement through declared effects**, not the idea of protection.
- Slide 11: the price result is **1 model**.
- Slide 12: not "this is novel" — "what remains open".

## Open before building it

- Slot length and audience (supervisor + co-op students as before? server admin present?)
- Format: PowerPoint (python-pptx, editable) or Marp (text-first, exports pptx/pdf)
- Where the presenter's own paper notes live, so speaker notes can point at them
  instead of repeating them
