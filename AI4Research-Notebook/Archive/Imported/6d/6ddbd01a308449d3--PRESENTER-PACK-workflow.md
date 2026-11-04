# Presenter pack: AI4Research workflow talk (pass 2)

Verified against `report-general/build/build_deck.py` (read in full, 2026-09-15), not against the old pack.
Updated 2026-09-15 afternoon for the clarity pass: 20 core slides, 16:45, plus 5 optional insertion slides.
Order is now workflow -> what has been shown -> challenges -> state of the art -> platform -> summary; every term
is defined in plain words on the slide where it first appears (target 40 min, max 45, shared with the capsule talk;
both talks core 34:50).
Numbers cross-checked against `report-general/build/figdata.py` and `notes/LEDGER-VERIFIED-NUMBERS.md`.
Ledger rule in force: never quote a run count; the 14-node run of 2026-09-03 (log l.793-796, Run C) passed every
required gate.

## 1. The talk's spine

AI4Research turns a plain-language research request into schema-checked evidence and a report, and the one
boundary that matters is the freeze, where the plan, its bound capabilities, and the rules that will grade it
are hashed together before anything runs. Above the freeze, every model call, compiling intent, filling
requirements, picking capsules, is followed by code that checks it; below the freeze, no model schedules work,
routes it, or admits a result, though models still run inside operators and judge inside rubric gates.
Execution runs in fixed ticks with gates that never move, a failed node repairs once and stays contained, and
the CLI-agent path is the one place nothing observes what the agent actually does. Claims are extracted by a
cue-word rule rather than a model and judged by a decision table that, without a measured experiment, can only
certify that a sentence exists in its cited section, not that it is true. The system has been demonstrated end
to end in 1 logged run that executed every node and closed with every required gate passed, but it has never
been scored by anything outside this repository, and published coding agents score only 11% to 16% on control
testing, the dimension AI4Research would need to prove itself on next. DeepSeek Harness already supplies the
plugin runtime AI4Research built by hand; what AI4Research adds is the contract layer, and moving the workflow
onto that harness is the first proposed step. Overall the system is ahead on checking and behind on generating,
and that lead is a design property that the first external benchmark score will actually test.

## 2. Slide-by-slide

| # | Title (exact) | TIME | Crib line |
|---|---|---|---|
| 1 | AI4Research Workflow (title slide) | 0:25 | This is the AI4Research workflow: how a request becomes checked evidence, what is still hard, how that compares, where it runs next. |
| 2 | 3 claims: the freeze, checking, and the runtime | 1:00 | The talk: workflow, what has been shown, what is still hard, then the other systems and the platform. 3 claims run through it. |
| 3 | What AI4Research is, in 7 terms | 1:05 | Capsule, plan and node, operator, gate, sprint, freeze: each defined in plain words before it is used. |
| 4 | Models propose, code checks, the freeze fixes rules | 1:00 | Above the freeze every model call is checked by code; below it no model decides what runs, where, or whether a result counts. |
| 5 | Before the plan, code checks every model output | 0:55 | The model quotes the request; code finds every quote before the record of the request is accepted. |
| 6 | Code narrows, a model picks, and code checks the pick | 0:55 | Code removes every capsule that cannot do the step; the model picks only among what is left, and code checks the pick. |
| 7 | Grading rules are hashed with the plan | 1:10 | The freeze is 8 steps of code that hash the plan together with the rules that will grade it. |
| 8 | A failure stays contained; gates never move | 1:05 | Execution runs in rounds called ticks; every step is code, and nothing on a node's frozen card can change mid-run. |
| 9 | Nothing watches the coding-agent path | 1:00 | The user's request is trusted; everything a node reads after the freeze, papers and tool output, is not. |
| 10 | A result does not say whether code or a model decided | 0:40 | Some gates decide by exit code, some ask a separate model; a pass from either looks the same in the results. |
| 11 | No model extracts claims, and a verdict proves provenance | 1:00 | Claims are picked out by a word rule, not a model, then judged by a decision table top to bottom. |
| 12 | Experiment code is hand-written or unobserved | 0:40 | Experiments are the only place we measure instead of cite; 1 hand-written script family exists today. |
| 13 | 1 run end to end, and 0 external scores | 0:40 | A 14-node run executed every node first time, delivered 8 files, and closed with every required gate passed. |
| 14 | No outside score, and a verdict that stops at provenance | 0:45 | Nothing outside this repository has ever scored the system, and a verdict without an experiment proves only provenance. |
| 15 | A frozen plan gets 1 repair, and a run needs a person | 0:45 | A frozen plan gets 1 repair before the freeze, then the sprint fails; there is no re-planning after. |
| 16 | First external test: 11% to 16% on control testing | 0:35 | Challenge 1 said nothing has scored the system; this is the first external test worth running, because it scores verification. |
| 17 | 4 reference systems generate well and check weakly | 1:10 | Four systems span the design space; Kosmos shows what checking accuracy after the run leaves behind; AI4Research checks the most and generates the least. |
| 18 | DeepSeek Harness runs it; AI4Research adds the contract | 0:45 | The harness around a model matters almost as much as the model: 27.4 points against 29.4 for the model. |
| 19 | Ahead on checking, behind on generating | 0:40 | We are ahead on checking, sealed grading rules, and behind on generating, 1 experiment family, no benchmark. |
| 20 | DeepSeek Harness comes first, and 3 decisions wait | 0:30 | None of these 5 next steps is built yet; moving onto DeepSeek Harness comes first. |

## 3. Hard questions

1. **Built or only designed?** Built and read in source at commit b0bf165f9: intent compilation, binding, the freeze and its verification, tick-based execution, all 4 gate kinds, the claims chain, and 1 hand-written experiment runner family. Proposed and not built: moving onto DeepSeek Harness, model-written experiment runners, a schema-bound claim extractor with a span gate, and a deciding-check label on every verdict. Source: slide 20; Report §6.2.
2. **What exactly does the freeze hash cover, and what does it not?** It hashes the bound plan together with the grading rules for that run: the test policy and every node's frozen evaluator gates, plus the manifest of each bound capsule and its guard/resource capsules. It does not cover correctness, an equivalent rewrite of the same logic, runtime state, or who made the edit; a hash detects that something changed after the fact, it does not prevent the change. Source: slide 7; Report §2.3.
3. **Why no external benchmark yet, and which one first?** None has been run; only a Terminal-Bench 2.0 adapter exists, with no score attached. TruthInsightBench is proposed first because it specifically scores verification, not task completion, and should be read per dimension since the 4 measured agents sit within 2 points of each other overall. Source: slide 16; slide 20 (Q-G4); Report §3.1-3.2; arXiv 2609.05079 p12.
4. **How does AI4Research differ from openJiuwen auto_research?** Both share the thesis of contract-checked generation, but the contract lifetimes differ: AI4Research freezes 1 contract per run before execution starts, while auto_research renegotiates a contract every round. AI4Research's grading rules sit inside the run hash; auto_research relies on host validation each round plus a rubric, and it publishes no evaluation. Source: slide 17; Report §5.4, §4.5 Table 6.
5. **What does "provenance, not truth" mean for a claim verdict?** Without a measured experiment, the strongest verdict a claim can get is that its cited span was found, case-insensitively, inside the section it points to, capped at 0.85, partially supported. That only proves the sentence exists where cited, not that it is correct, so a wrong or retracted paper can still pass. Source: slide 11; Report §2.7.
6. **What happens if the frozen plan meets something it didn't anticipate?** Before the freeze, the intent stage gets 1 bounded repair by default and then the sprint fails and the user resubmits; there is no re-planning once the freeze is sealed. After the freeze, a node with no defined evaluator behavior for an unforeseen outcome can record a pass by default; a halt, inconclusive, or ask-a-person policy is proposed but not built. Source: slides 17-18; Report §6.1, §2.1, §2.3.
7. **How many runs have passed, and did the 14-node run pass?** Do not quote a run count. The 14-node run of 2026-09-03 (log l.793-796, Run C in the ledger) executed all 14 nodes at attempt 1, delivered 8 files, and closed with every required gate passed; that is the run this talk and the report describe. A separate, earlier run on 2026-09-02 recorded a PASS closure while its own manifest declared its evidence gate failed, which is why the ledger bars quoting any run count as a reliability measure. Source: slide 13; `notes/LEDGER-VERIFIED-NUMBERS.md` run ledger, Run C.
8. **Whose 11% to 16% on control testing is that?** It belongs to the 4 coding agents TruthInsightBench measured against 1 frozen judge model; AI4Research has never been run on that benchmark. It is cited as the argument for running it next, not as a result AI4Research produced. Source: slide 16; arXiv 2609.05079 p14.
9. **What does moving to DeepSeek Harness actually change?** It supplies plugin loading, swapping, reverting, sandboxing, and logging that AI4Research today builds by hand; it settles none of the contract layer, meaning what a run must satisfy, what grades it, and what a capability may do. The harness choice alone is worth 27.4 points of pass-rate at a fixed model in Claw-SWE-Bench, against 29.4 points for changing the model itself. Source: slide 18; arXiv 2606.12344 p1, p11.
10. **Why does the freeze trade away re-planning that Arbor and Kosmos both do?** Arbor and Kosmos re-plan every cycle so they can react to what execution reveals; AI4Research fixes the plan and its grading rules before any node runs, so no one can change what counts as success after seeing the outputs. This buys a sealed, auditable contract at the cost of correcting a plan execution shows was wrong; the only recovery today is a fresh resubmission. Source: slides 7, 18 (IF ASKED); Report §2.3.
11. **Does a result say whether code or a model decided it passed?** No. Of the 43 registered checks, 23 are deterministic Python gates and 20 are model-judged rubrics, but a node's closure does not mark which kind produced a given PASS, so a rubric pass reads identically to a deterministic one. Source: slide 10; Report §2.6 Table 3.
12. **What is the state of experiment code, and why does it matter?** Only 1 experiment family, KV-cache quantisation, runs on a hand-written runner whose code and inputs are hashed into the approved plan before it runs, so it cannot fabricate a measurement; everything else goes through the CLI-agent adapter path, which is general but entirely unobserved. Only 21 of the 79 capsule manifests declare a trust class at all, so most evidence a run produces today carries no declared trust class. Source: slide 12; Report §2.8.

## 4. Numbers to have ready

| Number | What it is | Source |
|---|---|---|
| 80 / 79 / 74 / 5 | Registry entries / cap.*.yaml manifests on disk / registered / unregistered | slide 3; Report §1 |
| 45 / 102 / 63 | Logical operators / physical operators / physical operators enabled | slide 3 |
| 43 = 23 + 20 | Registered checks: deterministic Python gates + model-judged rubrics | slide 4 (IF ASKED); slide 10 table |
| 21 of 79 | Manifests declaring a trust class | slide 12; Report §2.8 |
| 606 / 34 / 8 | Regression suite: passed / failed / skipped, 22 files, 992.68s | slide 13; log l.862 |
| 24 / 0 | Journey tests (the only acceptance evidence) / external benchmark scores | slide 13; Report §3.1 Table 5 |
| 58.4 to 60.3, p = 0.118 | TruthInsightBench totals, no agent pair separates | slide 16; arXiv 2609.05079 p12 |
| 11% to 16% | Control-testing share of points earned, 4 coding agents | slide 16; figdata.py `TRUTHINSIGHT`; arXiv 2609.05079 p3, p8, p14 |
| 79.4% / 57.9% | Kosmos statements rated accurate, overall / synthesis-only | slide 17; arXiv 2511.02824 p2, p4 |
| 77.36 vs 71.70 | Arbor vs Claude Code, Terminal-Bench 2.0 held-out half | slide 17; arXiv 2606.11926 p10 |
| 27.4 vs 29.4 | Pass-rate spread from changing the harness vs the model, Claw-SWE-Bench | slide 18; figdata.py `HARNESS`; arXiv 2606.12344 p1, p11 |
| 14 nodes, 8 files, all required gates passed | The 2026-09-03 run (Run C) this talk describes | slide 13; ledger run table |

## 5. Things not to say

- Never quote a run count. Passing-flag counts are not a reliable measure here, and neither the report nor this pack offers one.
- Never name the 14-node run (Run C, 2026-09-03, log l.793-796) and the 15/15 run (Run B, log l.863) in the same sentence without the ledger's run table in view; they are 2 different sprints with different evidence-gate outcomes.
- Don't say "1 clean run": describe it by its log record instead, 14 nodes at attempt 1, 8 files, every required gate passed, log l.795. "Clean" invites the question of how many runs failed.
- Don't say "the last recorded full E2E failed at Planner schema admission": superseded; that claim is stale per the ledger.
- Don't say "52 vendor-neutral operators" unqualified: 52 declare no provider, only 18 carry the full vendor-neutral triple.
- Don't say "68 capsules": the verified count is 79 manifests on disk, 80 registered.
- Don't say "version 3.0.0": the verified version is 1.0.0-rc.9.
- Don't say "198 duplicated filenames": the reproducible figure is 179 shared filenames, 120 byte-identical; it is not load-bearing for this talk and can be omitted.
- Don't say "15 scientific-* roles": the verified figure is 21 `Scientific*` logical roles, 20 bound.
- Don't say AI Scientist-v2's final check was "a model reviewer": it was human peer review (slide 17 IF ASKED).
- Don't say "no model decides Arbor's merge" or that Arbor's held-out score was "selected over many test calls": a secondary model call extracts the metric, and the held-out test set is evaluated once, not searched over (slide 17 IF ASKED).

## 6. Insertion slides

Optional slides, built by `d.slide(..., insert=True)` and numbered after the core slide they follow, so core numbers
never move. Show them when time allows; delete or hide them (`DECK_INSERTS=hidden` or `off`) and the talk flows
unchanged. 5 slides, 4:05 in total.

| # | Title | TIME | Crib line | Cut first if short |
|---|---|---|---|---|
| 7a | Other work fixes the plan, never the rules that grade it | 0:45 | CaMeL fixes control flow, PlanCompiler a typed graph, Rel(AI)Build a hashed specification; none of them fixes what will grade the run. | 3 |
| 15a | What would settle each challenge, and what to read | 0:55 | 1 test per challenge with the signal to read: TruthInsightBench per dimension, the quote gate, the contradicting output, defects per plan, the outbound request, the forced rate-limit error. | 2 |
| 17a | Kosmos cites everything, checks accuracy afterwards | 1:00 | Over 200 rollouts, 42,000 lines of code, 1,500 papers; experts rated 79.4% of 102 statements accurate and 57.9% of the synthesis ones. So what: checked afterwards, 4 in 10 synthesis statements were wrong; AI4Research gates claims during the run and keeps them apart from synthesis. | 4 |
| 17b | openJiuwen renegotiates its contract every round | 0:45 | 6 parts, a manager emitting 1 decision a round, host code rejecting illegal moves, and no published evaluation under `paper_opt/`. | 1 |
| 17c | 4 systems left out: a lab or a person does the checking | 0:40 | Co-Scientist in vitro, Robin in the laboratory, Agent Laboratory with a person at every stage, and one repeat of AI Scientist-v2's experiment. | 5 |

Removed on 2026-09-15 afternoon (user): the "strongest objection to each challenge" slide. Its content is report §6.1
(the paragraph under each table) and App. B Table B1. The verification-ladder rungs were removed from the Kosmos slide
because the talk never defines the ladder; the report defines it in §4 and keeps its rung column in Table 6.
