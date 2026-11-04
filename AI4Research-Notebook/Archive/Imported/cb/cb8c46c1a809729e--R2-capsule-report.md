# R2 capsule report: final editorial pass for a first-time reader

Written 2026-09-15. Worktree `r2-capsule-report`. Nothing committed. No builder or render script run.

## OWNED

- `notes/report-capsules/REPORT.md`, the whole file
- `notes/pass2/review/R2-capsule-report.md`

## TOUCHED

- `notes/report-capsules/REPORT.md`: §1.2, §2.7, §4 lead, §4.3, §5.1, §5.2, §6, App. B
- Read only: `notes/HANDOFF-SHORT.md`, `notes/GUIDE-reports-and-presentations.md` §5 and §8, `notes/40-style-card.md`,
  `notes/pass2/review/W1-capsule-plan.md`, `notes/pass2/review/W2-papers.md`, `notes/pass2/proposals/W5-coverage.md`
  Part 1, `notes/report-capsules/deck-src/build_deck.py`, `notes/report-general/REPORT.md`,
  `C:\Users\mukch\projects\work\AI4Research` at `b0bf165f9` (`harness/lib/execution_authority.py` only, to spot-check
  4 line locators)

## CHANGES

### First-time-reader rewrites

| Where | Before | After | Why |
|---|---|---|---|
| §4.3 `REPORT.md:294` | "as SkillWeaver does before a skill is used [7]" | "as SkillWeaver, a web agent that discovers and hones its own skills, does before a skill is used [7]" | SkillWeaver's first use in the body had no gloss; every other system is defined where it first appears |
| §4.3 `:310` | "the AI4Research sandbox hand takes a list of guarded roots" | "the AI4Research sandbox takes a list of guarded roots" | "hand" is an internal AI4Research term that neither report defines |
| App. B `:643` | "The sandbox hand already records every path" | "The sandbox already records every path" | same term, propagated |
| §5.1 `:374` | 1 sentence with a nested count, "4 parameters, 2 with proposed starting values, 1 stated as a rule and 1 read from the census … and 2 platform assumptions" | split into 2 sentences, so the reader adds 3 + 1 + 3 + 4 + 2 = 13 without unpacking a nested clause | the lead must let a first-time reader check the count against the 13 rows |
| §5.1 `:374` | "All 79 manifests populate consumed and produced types, and step 4 … so exact matching spans all of them" (orphan sentence in the lead) | "The ranking assumption has candidates to rank in every case, since all 79 manifests populate …" | the sentence carried no stated relevance; it now names the assumption it supports |
| §5.2 `:396` | "It is a question for Section 6." | "Section 6 lists it among the values to settle before building starts." | "a question for Section 6" left the reader with nothing to look for |
| §6 `:442` | "For the supervisor, with the proposed default where the report implies 1:" | "Ask the supervisor, with the proposed default where the report implies 1:" | verbless fragment, and now parallel with "Decide before building" and "Test before trusting" |
| §4 `:217`, new sentence before Table 4 | table appeared with no lead-in | "Table 4 collects the 6 rules the results of Section 2 established, and names the part of the design each one produced." | every numbered table takes a 1-sentence lead-in (guide §5) |

### Mistakes

| Where | Before | After | Why |
|---|---|---|---|
| §1.2 `:49` and `:61` | "4 properties of DSH shape the design (Fig. 2)" | pointer removed there and moved to "merge into 1 abstraction via DSH, where everything is a plugin (Fig. 2)" | Fig. 2 draws the 4 layers and the capsule band, not the 4 DSH properties; the pointer sat on the wrong paragraph |
| §6 `:424` | "Three of these steps are smaller or larger than 1 line suggests." | "Four of these steps …" | the paragraph discusses steps 2, 5, 8 and 9 |
| §6 `:426` | "Rows 8 to 11 of Table 7 carry 4 of these" | "Table 7 carries 4 of these as assumptions with a test attached, the recurrence threshold, the gate-try cap, the breaking-change rule and the cap on generalist nodes" | Table 7 has no row-number column, so a reader had to count 11 rows; the column count is unchanged |
| §6 `:438-440` | "(Table 7, row 5)", "(row 6)", "(row 7)" | "(Table 7, practice feedback)", "(Table 7, ranking)", "(Table 7, task scores)" | same defect, same fix |
| App. B `:618` | "85 capsule manifests, of which 79 are capability capsules other than the 3 artifact adapters" | "85 capsule manifests, of which 79 are capability capsules and the other 6 are the 3 artifact adapters, the guard and the 2 resources" | 85 minus 79 is 6 and only 3 were named, so the arithmetic did not close; the 6 are the ones W1 identified |

### Defensibility

| Where | Added | Why |
|---|---|---|
| §2.7 `:181`, new paragraph after Table 2 | "The 3 results come from 3 different models, Claude Haiku 4.5, Claude Opus 4.6 and Claude 3.5 Sonnet, so what carries across them is the pattern rather than any of the rates, and the control for the rates this design would produce is the 79 hand-written capsules of Section 5." | the cross-paper objection "you cannot control for the model" was answered nowhere in either document (W5 Part 1, question 11). Stated in the argument's own voice, and every model name is already sourced in §2.3, §2.4 and §2.5 |
| §6 `:422`, appended to the paragraph after the step list | "Steps 1 to 7 change code that already runs and read records the system already writes, step 8 is the only new subsystem, and step 9 is the only step that needs a running DSH." | "how long does this take, and what is new work?" was answered nowhere (W5 Part 1, question 23). Every clause restates what §3, §4 and App. B already source |

### Checked and left alone

- Numbers agree across sections: 79 capsules of 85 manifests, 13 node-level exclusion reasons plus 5 shared,
  Table 7 at 13 rows, §6 at 9 steps, R1-R6 in ascending order, k = 10 sprints, 2 sprints and 5 gate tries as
  proposed starts, 21 of 79 trust classes, 20 of 43 rubric checks, 5 signals in Table 8, 5 rows in Table 3
- Figures 1-13 and G1 appear in order, each referenced from prose; Tables 1-8, A1-A7, C1-C2, D1, G1-G2 likewise.
  Every markdown table has a consistent column count (checked mechanically). No `*Table N.*` or `![Fig. N.` line
  was altered except the Fig. 2 pointer in body prose
- Cross-references into the general report resolve: §2.2 binding, §2.4 dispatch and its Fig. 4, §2.6 for 20 of 43
- Spot-checked 4 code locators at `b0bf165f9`: `execution_authority.py:37` does key captured definitions by bare
  capsule id, `:40` is the manifest SHA-256, `:47-69` is `freeze_node`, `:81-91` is `check_live_definitions`
  raising `CAPSULE_CHANGED_DURING_PLANNING`. All 4 match the report
- W1's hardest-question table: all 12 answers are present in the prose as claimed
- §1.2 and App. D do not contradict on spatiotemporal composability. §1.2 carries the definition in plain words
  once, App. D restates it in Cordis's own terms with the observational-reversal bound, and §4.1, §4.5 and G.2
  each apply 1 half without redefining it. No duplication was cut, because no 2 adjacent paragraphs say the
  same thing twice
- No em dashes, no "we" or "our", no ⚠, TODO, bracketed placeholders or status markers; no doubled words; no
  heading text changed, and `The 5 gaps of Table 3, as read in source:` is untouched
- §2 hands its numbers forward intact: 2 sprints from AllocBench reach §4.2 and Table 7, 5 gate tries from
  CoEvoSkills reach §4.3, Table 7 and §6, Alita-G's harvest plateau reaches §2.2 and G.4, DGM's never-pruned
  archive reaches §4.5

## CROSS-REFS

Deck edits, for the lane that owns `build_deck.py`. None is required for correctness of the deck on its own.

1. **Slide 26 footer**, `deck-src/build_deck.py:611`. Replace `"Capsule report §6; Table 7 rows 8-11"` with
   `"Capsule report §6; Table 7"`. Reason: §6 no longer numbers Table 7's rows, because the table has no row
   numbers on the page.
2. **Slide 24 footer**, `deck-src/build_deck.py:547`. Replace `"Capsule report §5, Table 6; §5.1, Table 7 rows 1-3"`
   with `"Capsule report §5, Table 6; §5.1, Table 7"`. Same reason.
3. **Slide 9, second face point**, `deck-src/build_deck.py:279-280`. Replace
   `"These 222 tools are not Alita-G's; Alita-G's own tools were never tested on new inputs."` with
   `"These 222 tools come from 3 other tool-making methods on 1 model; Alita-G's tools were never tested this way."`
   Reason: the report states the same fact flat in §2.3 ("The 96.8% was measured on tools written by 3 other
   protocols, and Alita-G's own tools were never replayed on held-out inputs"), and the slide states it as a
   rebuttal of a comparison the slide never draws. Same character budget class, 1 line, 0 seconds.
4. **No heading was changed**, in the report or the deck. No figure or table number moved. No new numbered table
   or figure was created.

## DOUBTS

1. **arXiv ids are not inline in the report.** The brief asks for title plus arXiv id at first use; the report's
   settled convention is title or system name plus `[n]`, with the id in the References list, and the deck strips
   carry the ids. Changing it would touch every citation in §2 and App. A. *Settled by:* the user saying whether
   the body should carry ids.
2. **"the 165-question GAIA validation set" is stated flat in §2.1.** The paper never prints 165; App. A.1 gives
   the derivation and §2.1's third limitation repeats the 13 flips out of 165. A hostile reader who has not read
   App. A.1 will take 165 as the paper's own figure. *Settled by:* the user accepting the derivation, or the body
   naming it as derived.
3. **Owners are still absent from §6.** I added effort and novelty ("steps 1 to 7 change code that already runs")
   but no owner, because no source in the worktree assigns one. *Settled by:* the user naming who does each step.
4. **§4's overview lists 3 build outcomes (build, version, wait) and §4.5 lists 4 (the fourth is specialize).**
   The 3 match the user's own design decision in HANDOFF, so I left both. *Settled by:* the user deciding whether
   the overview should name specialization.
5. **"Decide before building" and "Test before trusting" are imperatives**, which address the reader; the style
   card forbids reader address. They are parallel list lead-ins and the third now matches them ("Ask the
   supervisor"). *Settled by:* the user preferring impersonal lead-ins throughout §6.
6. **App. B's 6 non-capsule manifests** are named as the 3 artifact adapters, the guard and the 2 resources on
   W1's reading of the registry, not on my own count of the manifest directories. *Settled by:* listing the 2
   manifest directories at `b0bf165f9`.
7. **Table 7's row-by-name references** assume the reader can find "practice feedback", "ranking" and "task
   scores" in the first cell of the right rows. The wording matches, but the cells are long. *Settled by:* the
   report builder gaining a row-number column, which this pass could not add without changing a column count.
8. **The cross-paper model sentence sits in §2.7 only.** The same objection applies to §2.8's AllocBench models,
   which §2.8 already bounds per model in its own prose. *Settled by:* the user deciding whether §2.8 needs the
   same sentence.
