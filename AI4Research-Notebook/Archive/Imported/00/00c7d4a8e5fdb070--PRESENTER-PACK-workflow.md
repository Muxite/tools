# Presenter pack: workflow talk

Against `notes/overnight/render/general-deck/` (20 slides, 15:25) and `notes/report-general/REPORT.md` §1-§7.

## 1. The talk in 10 lines

1. Goal: a request to checked evidence, the field, then the platform
2. 3 claims: the freeze is the boundary; the field checks weakly; dsh gives the runtime, we add the contract
3. 6 terms: capsule, operator, sprint, node, gate, freeze
4. Above the freeze code checks every model call; below it no model schedules, routes or admits
5. Intent: quotes must be found, ids are enumerations, repair is bounded
6. Binding: code filters, the model picks among survivors, code binds from the manifest
7. The freeze: 8 steps of code, grading rules inside the hash
8. Execution: ticks, contained failures, fixed gates; the CLI-agent path is unobserved
9. Claims: a cue-word rule and a decision table, so the verdict is provenance
10. Internal evidence only; ahead on checking, behind on generating, until the first external score

## 2. One crib line per slide

- 1: request to evidence, the field, the platform
- 2: the 3 claims, then the running order
- 3: 6 terms; capsule is the next talk
- 4: tinted is a model, white is code, purple is the freeze
- 5: quotes must be found; ids are enumerations; "only these 5" caught
- 6: 13 codes filter, the model picks, 8 validate, the manifest binds
- 7: rules exist before sealing; priority 999 fails verification
- 8: T1 to T4: write-scope wait, failed gate, repair, skipped dependents
- 9: the request is trusted, what a node reads is not
- 10: a rubric PASS looks like a deterministic PASS
- 11: no experiment, so it stops at partially supported, 0.85
- 12: hand-written and trusted, or general and unobserved
- 13: end to end, not unattended, never measured outside
- 14: it scores verification; report per dimension
- 15: 4 systems spanning the design space, not a ranking
- 16: the harness moves pass rates almost as much as the model
- 17: no external number; provenance not truth; 1 repair
- 18: a wrong plan has no recovery; every fix is proposed
- 19: 3 ahead, 3 behind, the lead is a design property
- 20: nothing built yet; Q-G4 unblocks the most

## 3. Hard questions and answers

1. **Built or designed?** Built at `b0bf165f9`: intent compile, binding, the freeze and its verification, tick dispatch, the 4 gate kinds, the claim chain, 1 experiment family. Proposed only: the generalist capsule, the dsh move, model-written runners, a schema-bound extractor, a span gate. §6.2 lines 674-687.
2. **What does the freeze hash cover?** The contract itself, 12 upstream artifact references, and per node each bound capsule's manifest plus its guard and resource capsules, with the test policy and evaluator gates inside. Not covered: correctness, an equivalent rewrite, operational state, authorship. It detects an edit, it does not prevent one. `Q2-how-hashes-work.md:22-24`, `:61-65`.
3. **Why no external benchmark, and which first?** There is none; only a Terminal-Bench 2.0 adapter exists. TruthInsightBench is proposed because its scored object is verification, and read per dimension because the measured agents sit on a flat plateau. The choice is still Q-G4. §3.1 line 379, §3.2 lines 392-401.
4. **Why that rung?** Execution of a pre-approved runner plus citation grounding, so rung IV. Not rung II: the gates are frozen, but nothing is held out from the agent. The definitions are the survey's (2608.05179 p44); the assignments are ours, and it classifies checks, not systems (p48). `Q3-sota-verification.md:72-76`.
5. **How does it differ from openJiuwen auto_research?** Same thesis, opposite contract lifetime: 1 per run, frozen, against 1 per round, renegotiated. Our grading rules sit inside the hash; theirs are host rules plus a model rubric, and their host-only claim-status classifier is defined and never called. 0 imports shared. §5.4 Table 8.
6. **What is "provenance, not truth"?** Without an experiment the strongest verdict is a case-insensitive substring match against the cited section, so a wrong, retracted or cherry-picked paper passes. It is recorded in 3 structured fields; whether the prose shows them is unchecked. §2.7 lines 324-327.
7. **What if the contract meets something unforeseen?** Before the freeze, 1 bounded repair, then the sprint fails and the user resubmits; there is no re-planning. After it, an evaluator undefined on its outcome has no defined behavior, and a halt, inconclusive or human policy is proposed. §2.3 lines 170-172, 194; §6.1 line 655.
8. **How many runs have passed, and did the 14-node run pass?** The 14-node run of 2026-09-03 the report describes (log l.793-796) executed all 14 nodes at attempt 1, delivered 8 files and closed with `all_required_gates_passed=true`. Do not quote a run count: the ledger's rule is that passing-flag counts are not a reliable measure, because an earlier 14-node run (2026-09-02, log l.638) recorded a PASS closure while its own manifest declared its evidence gate failed; that conflict is what produced the publication-gate fix. `LEDGER-VERIFIED-NUMBERS.md` run ledger (Runs A, B, C).
9. **Whose 11% to 16% on control testing?** The 4 coding agents TruthInsightBench measured on 1 frozen model, not AI4Research, which has never been scored on it. It argues for running the benchmark, it is not a result from it. §3.2 lines 396-397; 2609.05079 p14.
10. **What does dsh change?** It supplies loading, swapping, reverting, sandboxing and logging, replacing tmux, file inboxes and SQLite. It settles none of the contract: what a run must satisfy, what grades it, what a capability may do. Harness choice is worth 27.4 points at a fixed model, against 29.4 for the model. §5.1-§5.3; 2606.12344 p1.

## 4. Numbers to have ready

| Number | What it is | Source |
|---|---|---|
| 80 / 79 / 74 / 5 | Registry entries, manifests, registered, unregistered | §1 line 48 |
| 45 / 102 / 63 | Logical operators, physical, enabled | §1 line 49 |
| 43 = 23 + 20 | Registered checks: Python gates, rubrics | §2.1 lines 106-108 |
| 13 / 8 | Hard-filter codes, then validation codes | §2.2 lines 127-131 |
| 8 / 3 | Freeze steps; stages recomputed | §2.3 lines 153, 168 |
| 21 of 79 | Manifests declaring a trust class | §2.8 line 355 |
| 606 / 34 / 8 · 24 · 0 | Regression pass, fail, skip; journeys; external scores | §3.1 Table 5 |
| 58.4 to 60.3, p = 0.118 | TruthInsightBench totals, no pair separates | 2609.05079 p12 |
| 79.4% / 57.9% | Kosmos statements accurate, overall and synthesis | 2511.02824 p2, p4 |
| 77.36 vs 71.70 | Arbor and Claude Code, Terminal-Bench 2.0 held out | 2606.11926 p10 |

## 5. Things not to say

- Never name the 14-node run and the 15/15 run in one sentence, and never quote a run count. The 14-node run on slide 13 is Run C (2026-09-03, log l.795), which did pass every required gate; the 15/15 run (Run B, log l.863) is the project's own highest-level evidence
- Never quote a run count. One recorded pass was later retracted, so passing-flag counts are not reliable and this report offers none
- "1 clean run": say "1 run end to end" and describe it by its log record (14 nodes, attempt 1 each, 8 files, every required gate passed, log l.795). "Clean" invites the question of how many runs failed, and passing-flag counts are not a reliable measure
- "The last recorded full E2E failed at Planner schema admission": superseded; the 2 kit files repeating it are stale
- Swaps: "52 vendor-neutral operators" to 52 declare no provider, 18 carry the full triple; "68 capsules" to 80; "2.8 candidates" to 2.75; "3.0.0" to `1.0.0-rc.9`; "198 duplicated filenames" to 179 shared, 120 byte-identical; "15 scientific-* roles" to 21 `Scientific*` roles, 20 bound
- 3 sentences cut as inferences the papers do not make: AI Scientist-v2's "model reviewer as the final check" (it was human peer review); Arbor's "no model decides the merge" (a secondary model call extracts the metric, p30); Arbor's held-out score "selected over many test calls" (the protocol evaluates the test set once, p33), still live in slide 15's IF ASKED
- "About 40 ideas" as 1 number: the paper says 2 batches, around twenty plus roughly twenty
