# HANDOFF: general AI4Research report (read this first)

Written 2026-09-11 by the general-report session. For the next session on **this**
report. The capsule report is a separate deliverable with its own handoff
(`../HANDOFF.md`); the two do not merge.

---

## 1. Read in this order (about 20 minutes)

1. This file
2. `README.md` (this folder): deliverables, decisions, re-runnable checks
3. `REPORT.md` §1-2 and §7: purpose, status and open questions
4. `../40-style-card.md`: the user's voice (required before writing any prose)
5. `review/R1-adversarial.md`: skim the findings so they are not reintroduced
6. `../../papers/summaries/INDEX.md`: what each of the 52 papers says

## 2. What the job is

The user's request (2026-09-11), in their words: work on the general report for the
project; download more documents and find SoTA systems that do what AI4Research does
and how they do it; a big part on the workflow (contract, task DAG, orchestration,
claim extraction, implementation, benchmarking, compiled intent); and what openJiuwen,
which the work is implemented on top of, looks like.

Deliverables: **`.md` first**, then a **`.docx` report** and a **`.pptx` deck**. The deck
is cut from the report, never written separately.

## 3. Where it stands

| Item | State |
|---|---|
| `REPORT.md` | **v0.3 (2026-09-13)**, ~2,600 prose words + 16 tables + 5 figures, 12 pages built (body to p10, App. A-C). 37 papers cited (down from 67). Worked examples: freeze tamper test (§3.2), one claim end to end (§3.4). Corrections table at the top. App. B = reviewer Q&A, App. C = glossary |
| `build/` | `figures.py` (5 greyscale PNGs), `build_report.py` (md → docx), `build_deck.py` (15 slides), `build_summaries.py` (cited-paper page). Outputs in `report-writing-set/general/` |
| `DECK-PLAN.md` | written for the 15-slide deck; slide titles changed in v0.3 to short labels |
| `SOTA-SYSTEMS.md` | evidence register: every figure with a page ref, plus "numbers not to use" |
| `OPENJIUWEN.md` | what openJiuwen is, AI4Research's real relationship to it (branding only, 0 imports), its own `auto_research` pipeline |
| `review/R1-adversarial.md` | adversarial review of v0.1: 41 findings, **all applied** in v0.2 |
| `../../papers/summaries/` | **52 summaries, 1 per paper**, `INDEX.md` grouped by report section |
| `.docx` / `.pptx` | **built** to `general/AI4Research General Report - Muk.docx` and `general/AI4Research General Presentation - Muk.pptx`; regenerate with the build scripts until the user starts editing them in place |
| `general/paper-summaries.html` | cited-paper reading page, published as an artifact 2026-09-13 |

Sweep of 2026-09-13 (4 subagents, 33 new papers read in full, summaries in `papers/summaries/`, INDEX §10-12): corrections applied in v0.3 are listed in the table at the top of `REPORT.md`. arXiv API returns 429 from this machine; discovery via WebSearch, download via `fetch.py` works. |

Waiting on the user: review of v0.2 voice and structure, and answers to Q-G3 to Q-G5.

## 4. Decisions made by the user (do not re-open)

- **Target platform: the DeepSeek Harness (dsh) for now**, "as that's more certain"
- **openJiuwen: add the contract layer to it later**, not port the runtime. openJiuwen
  stays in the report as context and the longer-term home (§5.3)
- **Build with python-docx / python-pptx** (no pandoc on this machine)
- **Write a text summary of every paper** (done)
- **One adversarial-review subagent was approved** and used. It is not standing
  permission: ask before spawning any more. ⚠ That reviewer spawned 2 sub-agents of
  its own; the user has been told

## 5. Hard rules

- **Repos are read-only.** Never edit anything under `C:\Users\mukch\projects\work\`
- ⚠ Changed 2026-09-14 by the user: **no ⚠ labels, corrections tables, `[verified]` /
  `[doc]` / `[proposed]` markers or bracketed placeholders in the deliverables** (REPORT.md,
  docx, pptx). Verify claims the same way, keep provenance and corrections in notes (this
  file, `PIPELINE-WALKTHROUGH.md`), and say "proposed" in plain words where it matters
- **Never cite a paper that has not been opened.** Page numbers come from the text files
- **Do not read the user's docx files for style.** Use the style card and the notes
- **Shared `notes/`**: several panels write here. Append-only on shared files. This
  panel owns `report-general/`; the capsule panel owns `report-capsules/` and notes 11-39
- **OneDrive files**: before writing any `.docx`/`.pptx`, check for running `WINWORD` /
  `POWERPNT` processes (`Get-Process WINWORD,POWERPNT -ErrorAction SilentlyContinue`).
  `~$` lock files are unreliable on OneDrive. If the user has edited a built file, do not
  regenerate over it

## 6. Voice (from `../40-style-card.md`)

Impersonal: no "we"/"our", no em dashes, no hedging verbs. Lists carry enumeration;
mean sentence about 24 words; triads; "Thus" as a connector; numerals for small numbers.
Status goes in markers or a limitations list, never in the verb. `[footnote …]` marks a
gap. Check before finishing: `rg -n "—| we | our " REPORT.md` should return nothing.

## 7. Paths and pinned commits

Workspace: `C:\Users\mukch\OneDrive - UBC\Reading\report-writing-set\`

| Repo | Path | Commit |
|---|---|---|
| AI4Research | `C:\Users\mukch\projects\work\AI4Research` | `b0bf165f9` |
| DeepSeek Harness | `C:\Users\mukch\projects\work\deepseek-harness` | `c291e7961a` |
| openJiuwen agent-core | `C:\Users\mukch\projects\work\agent-core` | `6ecf8218` (untagged, pkg 0.1.18) |
| openJiuwen jiuwenswarm | `C:\Users\mukch\projects\work\jiuwenswarm` | `b7da9ef98` |
| openJiuwen sciencediscovery | `C:\Users\mukch\projects\work\sciencediscovery` | `537107e` |
| openJiuwen deepsearch | `C:\Users\mukch\projects\work\deepsearch` | `62aa0e3` |

If a clone is missing: `git clone`, then `git checkout <commit>`. jiuwenswarm needs
`GIT_LFS_SKIP_SMUDGE=1` (a missing LFS video breaks the clone), then
`git reset --hard HEAD`.

`[verified]` marks hold only at these commits. If a repo is pulled to a newer commit,
re-check before reusing a line reference.

## 8. Paper tooling (`../../papers/`)

| Script | Use |
|---|---|
| `fetch.py <arxiv-id>...` | download PDF from arXiv, extract text with `===== page N =====` markers |
| `peek.py abs <id>` / `peek.py grep <id> <regex> [ctx] [max]` | abstract, or regex hits with page numbers |
| `body.py <id> [start] [end] [cap]` | compact body text by page; handles both page-marker and form-feed texts |

Traps: the Windows console is cp1252, so set `PYTHONIOENCODING=utf-8` for any script
that prints paper text. Large outputs get persisted to a file; pass a `cap` or read the
saved file. New summary format: citation line, what was read, Summary, How it works,
Results (with pages), Limitations, Relevance. Add each new paper to `INDEX.md`.

## 9. Corrections: do not reintroduce

From R1 (all fixed in v0.2):
- **Claim verification**: the literature verdict (`partially_supported` 0.85) comes from
  a **case-insensitive substring match** (`delivery.py:133-139`). The SHA-256 re-check
  (`:115-132`) only filters which spans are passed on; **no gate reads**
  `precise_source_span_resolved`
- **Experiment code**: an enabled adapter worker (`autosci-exec-experiment-run-worker`)
  delegates `$exp-run`/`$exp-design` to `codex exec`. "No LLM writes experiment code" is
  wrong. Only the native `measured_execution` path is hand-written (1 family, KV-cache
  quantisation). Only **21 of 80** capsules declare a trust class
- **Frozen-chain verification** recomputes **3** stages (composition validation, evaluation
  plan validation, `compile_scheduler_input`) and hash-checks the rest; not "every stage"
- **The governing rule** exists only in Chinese (`NEW-MACHINE-START-HERE.md:21`) and states a
  **target design**; quote the translation as a translation
- **Operators**: 45 logical; 102 physical, 63 enabled, 52 vendor-neutral. 80 capsules
- **DeepResearch Bench** citation range 39.36-94.04 across all 16 systems; 77.96-90.24
  across the 4 deep-research agents
- **PDDL 24-35%** comes from one study (2608.14590 p4), not the 38-study review
- Verification-ladder tiers per system are **this report's assignment**; the survey
  (2608.05179) ranks research areas, not systems
- **Numbers not to use** are listed at the end of `SOTA-SYSTEMS.md`; check it before
  quoting any figure

Found while summarising (not yet in `REPORT.md`, only in the summaries):
- CoEvoSkills: evolution consults the oracle of the same SkillsBench tasks it is scored
  on; no held-out split in the body. Note `../35-` (capsule panel) does not say this
- SkillWeaver: its relative gains disagree between the abstract, text and Table 1; use
  absolute rates
- SkillDAG: baselines quoted, not rerun; online edits add only 2.1 pp held-out

From earlier notes, still true: **jiuwenswarm is real** (openJiuwen's flagship repo,
2,537 commits); older notes saying "it is not a thing" are wrong outside the AI4Research
tree. **AI4Research imports no openJiuwen code**; "OpenJiuwen Solar" is its product name.

## 10. Open questions (`REPORT.md` §7)

| # | Question | Owner |
|---|---|---|
| Q-G3 | Name openJiuwen's own `auto_research` as the closest comparison? | supervisor |
| Q-G4 | Which external benchmark, if any, to run before circulating? | user |
| Q-G5 | Is the capsule a dsh seam or a layer above seams? (capsule report Q48; decides §5.2's capsule row) | design |

## 10a. Session 2026-09-13/14 (after v0.3)

- `PIPELINE-WALKTHROUGH.md` (this folder): source-level explanation of every stage with
  `file:line`, written from reads at `b0bf165f9`. Read it before answering any "how does X
  work" question; it supersedes older workflow notes where they disagree
- App. C glossary removed from `REPORT.md` at the user's request (v0.3 is 11 pages)
- Capsule report edited in place (7 edits, see walkthrough §9); backup in `versions/`
- User's stated preferences this session: shorter, supervisor-facing, lists, technical,
  fewer citations, no AI-sounding prose; "run by me first" was later waived for small edits
- Open: user may want the 8 challenges (chat, 2026-09-13) folded into §6; the capsule
  report frictions (walkthrough §9) folded into its §4.6/§4.9/§4.12

## 10b. Session 2026-09-14: elaboration for 1-hour slots

User: supervisor gave 1 h per presentation; reverse the conciseness cuts, elaborate; later
allowed decks to run longer; cut the SoTA papers for impact; verify the bigger claims.
Roadmap in `C:\Users\mukch\.claude\plans\handoff-written-three-files-idempotent-pnueli.md`.

- `REPORT.md` **v0.4**: every stage explained (§3.1-3.10), 4 reference systems (§4), 27
  challenges (§6.1). **14 papers** (was 37), listed by role in App. A. 17 pages built
- deck: 20 slides, 26:50 planned (cuts 8, 12, 16 → ~24 min). `DECK-PLAN.md` rewritten
- figures 3 and 5 redrawn for the 14-paper set (fig5 is now TruthInsightBench by dimension)
- capsule report docx edited in place (6,906 words, 23 pages): current-code gaps list end of
  §3, fallback note §4.2, restored rev2 material (practice step, reversibility list, full
  Track B, 2 open questions, network default), versioning §4.9, order of work 8 steps, App. B
  counts. Capsule deck rebuilt, greys, 22 slides, 21:35
- backups: `versions/* (before 20-min elaboration 2026-09-14)`
- corrections found by re-verification (all ⚠ in REPORT.md or walkthrough): checks registry is
  23 deterministic + 20 semantic, not all semantic; 21 of **79** manifests declare a trust
  class; 24 journey tests, not 25; `check_live_definitions` compares capsule definitions only;
  "no model decides after the freeze" overstated; Semantic Scholar 429 ended a run via
  `fail_run` (no fallback to local PDFs); "5 task families" unsourced, removed
- checkpoints left for the user: read report §3 and §6.1; click through both decks on a timer
- later the same day: all ⚠ labels, corrections tables and `[verified]`/`[doc]`/`[proposed]`
  markers removed from the deliverables at the user's request (rule change in §5). Capsule
  report: Fig. 2 (3 loops) added; `[decide]` placeholder turned into prose; supervisor-diagram
  placeholder in §1 still open (waiting on the user)
- capsule design agreed with the user: the generalist is a capsule bound at planning, whose work
  seeds new capsules; sprint is the reuse boundary; recurrence counts sprints. Written into the
  capsule report and deck; details in `../report-capsules/DECK-PLAN.md` header note
- redundancy pass (talks back to back, reports sent together): general report §6.1 keeps
  workflow challenges only (19 + F language coverage #20); capsule-library items live in the
  capsule report §3 (now "Five things", model-judgment item and 3 App. B lines removed, binding
  paragraph points to general §3.3). General deck drops the fallback and effects rows; capsule
  deck drops slide 3 and the model-judgment row. Decks: general 20 slides 26:50, capsule 22
  slides 22:00. Backups `versions/* (before redundancy pass 2026-09-14)`
- capsule report: supervisor-diagram line deleted, replaced by a drawn Fig. 1
  (`../report-capsules/deck-src/fig_goal.py`); Alita-G is now Fig. 2, the 3 loops Fig. 3. §4.2
  notes independent clocks, remote cold path, no halting for now (user decision)
- another session added §6.1 F "Language coverage"; renumbered #28 → #20 to match
- **2 private reading pages, maintained from the reports.** Rebuild with
  `python build/build_reading.py` after any change to REPORT.md, the capsule report or the
  summaries, then republish both (same file paths; figures are inlined as data URIs, so no
  `files` map is needed):
  - SoTA reader `general/sota-reader.html` →
    https://claude.ai/code/artifact/8d6e3e57-6e88-4f5b-8575-46fc7c9a737c (replaced the Reading Set)
  - Challenge register `general/challenge-register.html` →
    https://claude.ai/code/artifact/826dc8ce-c276-4a6c-80fd-921958d6fbbe
  The builder slices REPORT.md on literal markers ("Nearest work.", "### 4.1", …) and exits if
  one moves; fix the marker, never publish a stale page
- **figure pass + engineering-style decks (same day).** New build files: `deckkit.py` (shared by
  both decks), `figdata.py` (chart numbers), `excerpts.py` (real code/fixture excerpts, exits if a
  source line moves). `figures.py` adds 7 dual-size diagrams (binding, tick, trust, claim, sprint,
  gate, select). `build_report.py` supports `{{excerpt:name|caption}}` and 6.2 in figures.
  REPORT.md: Figures 1-9 renumbered in order, Listings 1-2 in §3.4; the §3.5 tick list and the §3.8
  verdict table became figures. Capsule report: Fig. 3 sprint timeline, Fig. 5 admission gate,
  Fig. 6 selection funnel (replaced Table 5; DSH table is now Table 5). Decks: general 44 slides
  26:15, capsule 36 slides 22:00. Backups `versions/* (before figure pass 2026-09-14)`
- the repo holds no real run output; `harness/metadata/*` JSON are placeholders (v1 schema, zero
  hashes, `not_executed_metadata_example`) and must not be shown as real artifacts
- another session edited REPORT.md §6 in parallel today (challenges regrouped to A-E, 13 rows);
  the deck's challenge slides follow that grouping

## 10c. Session 2026-09-14: language coverage

- `REPORT.md` §6.1 group F, challenge **28**: text-reading stages are English-only regex
  (intent keyword pass, claim/method/title extraction); recommendation `[proposed]` for a
  schema-bound, grounded model extractor, testable alone on non-English papers with a verified
  claim list. Now 28 challenges. `.docx`/`.pptx` **not rebuilt** for this change
- the user's framing: model reads any language → language-neutral typed fields; not translation

## 10d. Session 2026-09-14: challenge reduction (R2)

- adversarial review `review/R2-challenges.md` (1 reviewer, user-requested): §6.1 cut from 20 to
  **13 items** in groups A-E (D stays the capsule pointer, required by `build_reading.py:349`);
  language coverage is now **#5** with its recommendation in §6.2; §6 head says "cruder than", not
  "below", the CREDENCE baseline; the "months, not years" line removed as unsourced
- corrections applied: #12 no longer conflates the 3 Semantic Scholar 429 runs (log l.327, l.662,
  l.814; the l.662 cause is fixed at `research_operator_registry_adapter.py:805-806`); "every
  remote-agent capsule requires approval" had no source and was replaced by the experiment
  approval gate (`graph_node_dispatcher.py:16814-16838`); #13 cites log l.815 (clean run needed 6
  attached PDFs)
- deck script (slides 18-19 rows and notes, slide 20 behind) and `DECK-PLAN.md` updated; backup
  `versions/REPORT v0.4 (before challenge reduction 2026-09-14).md`. `.docx`/`.pptx` not rebuilt
- ⚠ later the same day: the general `build_deck.py` was rewritten (engineering-style, 44 slides), so
  the R2 §5 line edits no longer apply by line number. Their content was checked against the new
  script: challenge slides follow §6.1 A+B, C, E (13 items); no "remote-agent capsule requires
  approval", "second provider", "months" or "below the baseline"; the Behind row reads
  "English-only regex, recall unmeasured". docx, deck and both reading pages rebuilt after R2

## 10e. Session 2026-09-14: workflow order, define before use

User rule: report and decks run in workflow-phase order; nothing is referenced before its phase.
- REPORT.md: §2 status bullets removed (pointer to §3.10). Fidelity example ("only these 5") now in
  §3.1 after the 4-artifact table; 14-node run + regression 606/34/8 now in §3.10. Trust model moved
  from §3.4 to the end of §3.6 (after both operator paths). Figures: tick = 4, trust = 5. Challenge
  #11 points at §3.6. Backup `versions/REPORT (before workflow reorder …).md`
- general deck: Status slide → "6 Evaluation · Evidence so far"; Trust model after "2 operator
  paths"; `deckkit.phase()` IN/OUT strip on the first slide of each phase (intent, requirement,
  binding, freeze, tick, operators, gates, claims, experiments, evaluation). Still 44 slides, 26:15
- capsule deck: sprint slide moved after the generalist and 2-flags slides. Capsule report: sprint
  figure moved to §4.4 after "Recurrence is counted in sprints"; loops = Fig. 3, sprint = Fig. 4
- rebuilt: general docx, both decks (installed), reading pages (SoTA v5, register v4 republished)

## 10f. Session 2026-09-14: presentation rework (both decks, capsule report)

- plan: `C:\Users\mukch\.claude\plans\for-the-goal-in-lazy-star.md`; details and review table in
  `../report-capsules/DECK-PLAN.md` header
- **colour allowed** now (user): `build/palette.py`, colour = stage, tinted + MODEL tag = model call, white +
  CODE tag = code. **Rule: 1 box per model call** in every figure. `figures.py` rewritten; new diagrams
  `workflow`, `freeze` (dual-size, replace fig1/fig2), `dag`, `dag-capsule`, `goal`, `loops`, `mcp`, `versions`
- **time budget: both talks together ~40 min, 45 max**; general 26 slides 16:25, capsule 36 slides 23:33.
  User prefers cutting papers, SoTA and challenges over missing main points
- `deckkit.py`: `slide(stage=)`, `measured()`, `therefore()`, notes SAY / MUST HIT / IF ASKED,
  `save(deck=)` writes `build/deck-times.json` and checks the combined budget
- REPORT.md: new Figure 5 (frozen DAG over 4 ticks, Kahn order, conflicts, repair, skipped dependents,
  gates fixed at freeze) with a paragraph in §3.5; later figures renumbered to 10. docx, decks and both
  reading pages rebuilt and republished
- capsule report docx edited in place (backup `versions/… (before presentation rework 2026-09-14).docx`):
  DSH and MCP explained in §1 (Fig. 2), Alita-G steps + transfer table (Table 1), "by X et al." in §2,
  "abstraction agent" renamed **build-decision agent**, roles table (Table 5), DAG with capsules at end of
  §4.3 (Fig. 5), §4.9 append-only (Fig. 9) + typed retirement (Table 7) + updates by version/specialization
  (Table 8), App. E (MCP) and F (dispatch rules). Figures 1-9, Tables 1-9 renumbered and checked
- user decision: near-miss gaps may produce a **new version** (same types, no added effects, passes the
  predecessor's regression suite) or a **specialization**; a contract change is a new id

- later the same day (user decisions): capsule talk and report put research before the system (design figure opens
  capsule report §4 as Fig. 3; MCP is Fig. 1, Alita-G Fig. 2); the build-decision agent writes the manifest so the
  gate is fixed before implementation; gate submissions are capped with reason codes only. Capsule deck 37 slides
  25:38, both talks 42:03 (max 45). Speaker notes in the user's own voice. Details: `../report-capsules/DECK-PLAN.md`

## 10g. Session 2026-09-14: challenge #3 checked against code; E merged

- #3 checked at `b0bf165f9` (clean tree). Held: 0.85 substring verdict (`delivery.py:133-159`),
  failing spans dropped (`:115-132`, output `:229-230`), `precise_source_span_resolved` read only by
  a test (`test_action_delivery_operators.py:737`), 1 experiment family (`kv_cache_experiment.py:27`, `:74-78`)
- corrected in §3.8: the gate requires limitations on every verdict (`claim_verdict_gate.py:47-48`), not
  only confidence ≥ 0.8; fixture sets `testability: testable` (`:714`), the extractor would assign
  `partially_testable`; provenance labels already exist in the structured verdict (`:175-178`, `:220`,
  `:2084-2085`), so the #3 fix now asks for them in the prose
- new finding: the reportable set filters on evidence ids, not verdict value (`delivery.py:667-670`);
  extracted claims always carry the paper anchor (`operators.py:1226`), so `insufficient`/`not_supported`
  claims become conclusions and `unsupported_claims` stays empty. Traced in `delivery.py` only; the
  bridge path (`autosci_bridge.py:13474`) is unchecked. §4 summary sentence no longer cites the list
- user asked to merge group E: #10 + #11 → **#10 "Execution is recorded, not observed"**; #12 + #13 →
  **#11 "Unattended runs do not finish"** (the prompt-only rerun of old #13 is the l.814 run of old #12).
  Now 11 general challenges, 16 in the register. §6.2 `(#12)` → `(#11)`; deck challenge table and notes
- backup `versions/REPORT (before claim code check 2026-09-14).md`; register rebuilt and republished;
  deck and docx rebuild status in the session summary

- evening: **`../GUIDE-reports-and-presentations.md`** written (style guide from the user's feedback; read it before
  any deck or report work). Capsule talk restructured as evidence → design rule (R1-R6) → design; slides carry the
  script; notes without MUST HIT; no em dashes. The workflow deck still uses the older note style (hit=)

## 11. What to do next

1. **Get the user's review of `REPORT.md` v0.2.** Apply voice and structure changes in
   the `.md` first
2. **Fold the 3 new summary findings into `REPORT.md`** only where the report cites
   those papers (§3.6, §6), and add them to `SOTA-SYSTEMS.md`
3. **Figures**: the workflow diagram (7 stages around the freeze); the freeze hash
   chain; the verification ladder with systems placed on it; the AI4Research vs
   `auto_research` contract-scope contrast. Native, editable charts where possible
4. **Build the `.docx`** with python-docx from `REPORT.md`. Suggested location, matching
   the capsule report's naming: `report-writing-set/AI4Research General Report - Muk.docx`.
   Confirm the name with the user first
5. **Build the `.pptx`** with python-pptx, cut from the report. Reuse the capsule
   panel's pattern: `../report-capsules/deck-src/build_deck.py` (native charts, speaker
   notes with timings) and its planning doc `../report-capsules/DECK-PLAN.md`
   (1 claim, 1 number, 1 picture per slide). Write a `DECK-PLAN.md` here first
6. Once the user starts editing the built files, stop regenerating: edit them in place

## 12. Memory

The auto-memory entry `general-report-context` points here. Update its "State" line when
the status changes.
