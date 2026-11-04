# W4: state of the art, checked and cut (2026-09-15)

## OWNED

- `notes/report-general/REPORT.md` §3.2, §4 (opening, 4.1-4.5, Table 6), Appendix A Table A1
- `notes/report-general/build/build_deck.py` slides 14, 15, 16 (file lines 261-325)
- `notes/report-general/SOTA-SYSTEMS.md`
- `notes/pass2/review/W4-sota.md` (this file)

## TOUCHED

The 3 files above, and nothing else. No figure call was edited. Nothing was committed and no builder was run.

Papers opened this pass, all from `papers/`: 2609.05079, 2608.05179, 2504.08066, 2511.02824, 2606.11926,
2411.14199, 2604.13092, 2503.18813, 2606.19819, 2604.04074, 2603.05912, 2606.12344, 2606.26924, 2502.18864,
2505.13400, 2501.04227, 2606.15497.

## CHANGES

### REPORT.md

| Where | Before | After | Why |
|---|---|---|---|
| §3.2 lead (392) | "The proposed first external test is TruthInsightBench (2609.05079), for 4 reasons" | adds "which sets 40 blind discovery tasks drawn from 40 peer-reviewed studies across 10 scientific domains (p1)" | the result had no n. 2609.05079 p1 |
| §3.2 bullet 2 (396-397) | "(p14, Fig. 7)" | "(p14)" | Fig. 7 is this report's own figure; the paper's figure number was not checked |
| §3.2 bullet 3 (398-399) | "4 coding agents on 1 frozen model score 58.4 to 60.3" | "4 coding agents on 1 frozen base model score 58.4 to 60.3 over the 40 tasks ... (p1, p12)" | p1 says "four coding agents on one frozen base model"; the judge is a separate frozen model, so "base" removes the collision |
| §4 opening (416-425) | 4 rungs, then a paragraph defining a home-made label "exec" | 5 rungs, with V defined as "a threat-to-validity argument or a proxy reward", plus a paragraph citing the survey's own placement of "newest 2026 AI scientists" at rung V, signal "externalized checking apparatus (mixed)" (p76) | the invented label sat in a column of survey rungs and had no source. The survey has a rung for exactly this case (p44) and files these systems there itself (p76). Net shorter |
| §4 opening (new paragraph) | nothing | 4 systems read and left out, with the reason and a locator each: Co-Scientist (2502.18864 p2, p5), Robin (2505.13400 p1), Agent Laboratory (2501.04227 p1-2), "Towards End-to-End Automation of AI Research" (2606.15497 p2) | the first question a supervising engineer asks is "where is Google's co-scientist". Answering it in the report costs no talk time |
| §4.1 (440-442) | "1 scored 6, 7 and 6 (6.33) ... (p2, p9)" | "3 of its manuscripts were submitted blind among the 43 submissions ... 1 scored 6, 6 and 7 (6.33) ... (p9)" | p9 gives "individual scores of 6, 6, and 7" and the 43-submission pool. The p2 locator was carrying only the average |
| §4.1 close (449-450) | "its checking is peer review and model judgment (rungs VI and VIII)" | "its checking is its own execution, peer review and model judgment (rungs V, VI and VIII)" | the prose and Table 6 disagreed on the rung set |
| §4.2 (463-465) | "85.5% of data analysis statements, 82.1% of literature statements and 57.9% of synthesis statements were accurate" | the paper's own 3 verbs: reproducible / validated against primary sources / accurate, and "102 statements were extracted from 3 representative reports" | p4 uses a different verb for each type; flattening them overstates the first two. p2 gives the sample |
| §4.2 close (467-470) | "Kosmos links its evidence but does not gate it ... (exec and rung IV)" | "Kosmos cites every statement and measures accuracy afterwards rather than gating on it during the run ... (rungs IV and V)" | "does not gate it" is an absence the paper never states; what is sourced is that the 79.4% was judged after the fact |
| §4.3 heading (472) | "Arbor: a held-out merge gate with no model, the closest system on checking" | "Arbor: a held-out merge gate the merge tool alone can open, the closest system on checking" | "no model" is listed under "Numbers not to use" in SOTA-SYSTEMS.md and was cut from the body by Q3, but survived in the heading. p28 supports tool-level enforcement; p30 shows a model may supply the metric |
| §4.3 result (486-490) | no setup; 1 limitation in prose | adds "89 shell tasks split into 36 development and 53 held-out test tasks (p8), with Claude Opus 4.6 running both Arbor roles (p9)", and 2 labelled limitations, the second being the p30 secondary LLM call | the headline number had no n and no model. The p30 caveat now sits with the claim it bounds |
| §4.3 close (492-493) | "Its gate is fixed outside the agent" | "Its gate is fixed outside the agent that the gate judges" | "outside the agent" was ambiguous for a reader who has just been told a model may extract the metric |
| §4.4 close (513) | "instead of freezing it per run" | "rather than freezing it per run" | first-time-reader rule bans "instead" |
| Table 6 (520-524) | rung column mixed "exec" with survey rungs; 4 cells worded differently from the slide | rungs V / IV, V / II / V, VIII / IV, V; Plans and Checks cells reworded to match slide 15 exactly | consistency requirement, and every rung now traces to 2608.05179 p44 |
| Table 6 caption (526-528) | "Every result except openJiuwen's is the authors' own measurement" | adds "and openJiuwen's row is read from code at `6ecf8218`" | the row's provenance was only in the deck's IF ASKED |
| §4.5 close (531) | "Arbor shows a held-out gate with no model paying off" | "Arbor shows that a held-out gate only a tool can open pays off" | same "no model" correction |
| App. A lead (721) | "14 sources were read in full" | "18 sources were read in full" | 4 rows added below |
| Table A1 Arbor row (725) | "Held-out merge gate with no model; 77.36 against 71.70" | "Held-out merge gate enforced by the merge tool; 77.36 against 71.70" | same correction |
| Table A1 (new row) | nothing | "Considered, not compared \| 2502.18864, 2505.13400, 2501.04227, 2606.15497 \| Why the comparator set is these 4 systems" | matches the new §4 paragraph |
| Table A1 TruthInsightBench row (736) | "6 dimensions; 58.4 to 60.3 plateau" | "40 blind tasks over 6 dimensions; 58.4 to 60.3 plateau" | matches §3.2 |
| Table A1 caption (738) | "The 14 sources" | "The 18 sources" | count |

Every other Table A1 "used for" entry was re-checked against §2-§4 and holds: PlanCompiler is used in §2.1 for the
typed-node comparison and in §2.3 for constraint evasion; CaMeL in §2.4; Rel(AI)Build in §6 and App. E.3; CREDENCE in
§6.1; FactReview, OpenScholar and DeepFact in App. E.7 and §6.1; Claw-SWE-Bench in §5.1; the survey in §2.3 and §4.

### build_deck.py

| Where | Before | After | Why |
|---|---|---|---|
| 262 | footer "2609.05079 p3, p8, p12, p14" | "p1, p3, p8, p12, p14" | the n comes from p1 |
| 263 | setup "4 coding agents, 1 frozen model, 6 dimensions" | "40 blind tasks, 4 coding agents, 1 base model" | setup needs n; kept under the strip's 109-character limit |
| 267-275 | TIME 0:40, 72-word SAY, 2 IF ASKED | TIME 0:30, 66-word SAY, 3 IF ASKED | 10 s saved. The dropped sentence repeated the numbers already printed in `point()` under the chart |
| 279 | footer "2606.11926 p7-10" | "2511.02824 p2-4, 2606.11926 p8-10, p28" | the merge-tool claim is p28 |
| 280-290 | 4 table cells worded differently from Table 6; "VLM" undefined on the deck; "not gated"; "held-out merge gate, no model"; AI4Research result "no external score" | every row now matches Table 6, including the AI4Research row "14 nodes executed and 8 files delivered with every required gate passed; no external score"; headers "Plans how / Checks with / Headline result" | consistency requirement, the "no model" correction, and no undefined acronym on a slide face |
| 292 | THUS "...; no result here is external" | "AI4Research checks the most and generates the least, and has no external score" | "no result here is external" read as if the 4 papers' results were internal |
| 293-303 | TIME 1:00, 108-word SAY naming all 4 systems, 3 IF ASKED | TIME 0:40, 83-word SAY naming Arbor (checking) and AI Scientist-v2 (generating), 6 IF ASKED | 20 s saved. Kosmos and auto_research stay on the slide, in Table 6, and in IF ASKED; the co-scientist question is now answerable |
| 316-317 | SAY opened "Why the harness matters:" | "The harness around a model matters almost as much as the model." | label-then-point fragment; TIME unchanged |

## CROSS-REFS

Sentences for other lanes, and checks for the builder.

1. **§6 (line 645), another lane.** "Arbor already runs a held-out gate with no model (Appendix E.4 and Section 4.3)"
   carries the claim this pass removed everywhere else. Replace with: "Arbor already runs a held-out gate that only
   its merge tool can open (Appendix E.4 and Section 4.3)."
2. **Appendix E.7 (line 1020), another lane.** "OpenScholar (2411.14199) reports that GPT-4o fabricates citations 78%
   to 90% of the time without retrieval (p1)" names the wrong model. The paper says GPT-4 (p1, "GPT-4 fabricated
   citations in 78-90% of cases"). Replace "GPT-4o" with "GPT-4".
3. **Appendix E.4, another lane.** If it repeats "no model" for Arbor's gate, apply the same replacement.
4. **Heading changed** (listed as required): §4.3 now reads "Arbor: a held-out merge gate the merge tool alone can
   open, the closest system on checking". `build_reading.py` slices on the literal `### 4.3`, not on the title text,
   so the SoTA reader page still builds; the title it prints changes with the heading.
5. **§4 heading text unchanged**, so the `## 4. The state of the art` and `### 4.1`-`### 4.5` markers all still match
   `build_reading.py:180-183`.
6. **TIME deltas.** Slide 14 0:40 to 0:30, slide 15 1:00 to 0:40, slide 16 unchanged at 0:45.
   **Net -30 s**, workflow deck 15:25 to 14:55, both talks 35:55 to 35:25.
7. **Render check for whoever builds next.** Slide 15's table grew by 1 line in the AI4Research row. The estimator in
   `deckkit.table` puts its bottom at 6.17 in against a THUS strip at 6.38 in, so no warning fires, but this is the
   tightest table in the deck. Look at `slide-15.png` after the next render.
8. **Appendix A source count** moved from 14 to 18. Any other section that says "14 papers" or "14 sources" needs the
   same change; `HANDOFF.md` §10b says "14 papers (was 37)" and is a history note, so leave it.

## DOUBTS

1. **Rung V for AI4Research.** Its gates are frozen and hashed, which is stronger than an ordinary proxy reward, but
   nothing is held out from the agent, so II is not available. V plus IV is the honest reading. A supervisor may push
   for a footnote saying the freeze is a stronger V than the others in the column.
2. **Kosmos at rung V.** The paper never claims an executable check on its own analyses; the 79.4% was judged by
   experts afterwards. If that post-hoc expert judgment is what should be graded, Kosmos is IV and VI, not IV and V.
   Worth 1 decision from the user.
3. **openJiuwen's rung.** V, VIII rests on a code read, not a paper. It is the only row in Table 6 whose rung has no
   published artifact behind it.
4. **§4.1 "checks it last".** AI Scientist-v2 checks continuously inside the tree search; what comes last is the
   external check. The sentence is defensible but a careful reader may object.
5. **Missing systems, arXiv ids for the user to fetch if wanted.** None is needed for the argument, and all 4 named
   in §4 are already in `papers/`. The only genuinely absent family is a Kosmos successor; no successor paper was
   found in `papers/` and none is proposed rather than guessed at an id.
6. **DeepScientist (2509.26603) and InternAgent-1.5 (2602.08990)** are in `papers/` and are the 2 strongest candidates
   for a 5th comparator, since both claim a mechanical in-loop check. Both were left out because the brief is to cut
   SoTA, not add it. InternAgent-1.5 was only read at abstract level, so it cannot be cited today.
7. **Q-G3 is still open** (name auto_research as the closest comparison?). It sits in slide 15's IF ASKED and §7. It
   changes §4.4's closing sentence if the supervisor says yes.
8. **Slide 15 has no rung column** while Table 6 does. That is deliberate, since a rung column would need spoken
   explanation and the brief is to cut spoken SoTA. If the supervisor wants the ladder on the slide, it costs about
   20 s back.
