# Q3. Verification of REPORT.md §4 "The state of the art"

Sources opened tonight: `papers/2504.08066.txt`, `2511.02824.txt`,
`2606.11926.txt`, `2608.05179.txt`; `notes/LEDGER-VERIFIED-NUMBERS.md`;
`agent-core` at `6ecf82184f5b9d5706b35015720f7b931869de56` (confirmed by
`git rev-parse HEAD`). Patches: `patches/2b-sota.md`.

## Claim table

Agent-core paths are relative to `openjiuwen/rsi/artifact_rsi/paper_opt/`.

| Claim (REPORT.md line) | Source | Status | Note |
|---|---|---|---|
| §4.4 "A module chain from topic survey ... to reporting in LaTeX, plus standalone paper scoring" (489) | `auto_research/modules/manager/schemas.py:26-33`; `paper_scoring/scorer.py:49` "LaTeX-in / dual-rubric scoresheet-out" | verified | Scoring is standalone because it is absent from `ModuleId` and from `configs/pipeline.default.yaml:38-44` |
| §4.4 "An LLM manager that emits 1 decision each round: execute ... done, or blocked" (491) | `manager/schemas.py:22` `ControlSignal = Literal["EXECUTE", "DONE", "BLOCKED"]`; `extensions/tools/submit_manager_decision.py:14` "Accept exactly one validated ManagerDecision per routing round" | verified | `:69` "may be called only once per round" |
| §4.4 "Host-side validation that rejects illegal moves" (492-493) | `pipeline/transitions.py:427` "execution requires a ready implementation"; `:458` "execution requires a newer ready implementation"; `:602` "DONE rejected" with `:614` "pending requirements" | verified | All 3 named moves land |
| §4.4 "Budgets of 50 rounds, 4 code retries, 6 design revisions and 4 execution retries" (494) | `configs/pipeline.default.yaml:28,30,31,32` | verified (qualify) | These are shipped-config values. Code defaults at `manager/schemas.py:156-161` are 30 / 4 / 5 / 3 |
| §4.4 "A claim status computed on the host with no model" (495) | `reporting/evidence.py:153-156` "Pure, host-only classification ... no model call"; `:24` `EvidenceSource = Literal["prior_paper", "current_run"]` | corrected | `classify_numeric_status` has **no caller anywhere in agent-core**. Defined, never computed. "Phase 1 of that design" (`:3`) |
| §4.4 "Paper scoring by a dual rubric sampled 5 times at temperature 0" (496) | `paper_scoring/scorer.py:49`, `:169`, `:177`, `:197`; `configs/pipeline.default.yaml:196-197` | verified (qualify) | Schema default is temperature 0.1 (`paper_scoring/schemas.py:282`); 0 comes from the shipped config |
| §4.4 "No published evaluation" (497) | No results, benchmark or evaluation document under `paper_opt/` | verified as absence | Bound it to the repo at `6ecf8218`; `docs/reporting_iteration_design.md`, cited by `evidence.py:2`, does not exist |
| §4.2 "Every statement in the final report cites the notebook or paper it came from" (454) | 2511.02824 p2 §2.1: "Each statement and figure in the report cites either a publication found by the literature search agent or a Jupyter notebook created by the data analysis agent" | verified | Locator was missing; add (p2) |
| §4.2 "about 200 agent rollouts" (453) | 2511.02824 p1: "over 200 agent rollouts" | corrected | 42,000 lines and 1,500 papers verified |
| §4.2 "parallel tasks for 2 agents" (451) | 2511.02824 p2: "up to ten literature search and analysis tasks" per cycle | corrected | 2 agent *types*, up to 10 tasks |
| §4.2 "79.4% of 102 statements ... 57.9% synthesis" (456-457) | 2511.02824 p4 (percentages); p2 (the 102-statement sample and the no-evidence condition) | verified | Split the page cite |
| §4.1 ideation, 4 stages, tree search (427-432) | 2504.08066 p4, p5, p5-7 | verified | Stage 1's name is "Preliminary Investigation"; "prototype" is its stopping criterion |
| §4.1 "Writing in 1 pass followed by reflection ... (p8)" (433) | 2504.08066 p4 (single-pass writing); p8 (VLM caption check) | corrected | Page split |
| §4.1 "uses a model reviewer as the final check" (442-443) | 2504.08066: AI reviewer is figure/caption-scoped (p7) and node-scoped (p5) | not found -> cut | No model reviews the finished manuscript. The last check was human peer review |
| §4.1 "57% overlap"; 6/7/6 = 6.33; 3 of ~40 ideas (435-440) | 2504.08066 p11, p9, p10 | verified | "~40" = "around twenty" + "roughly twenty"; never one number |
| §4.3 "each node ... holds a hypothesis, an insight and a git commit reference" (468-469) | 2606.11926 p6: the 3rd field is **Metadata**, holding "an implementation reference such as a git branch or commit"; p31 schema says branch | corrected | |
| §4.3 "6 steps: observe, ideate, select, dispatch, backpropagate and decide" (473) | 2606.11926 p7 | verified | The appendix prompt lists 7 differently-named steps (p23-24); do not cite it |
| §4.3 "No model decides the merge" (475) | Nearest is p28 (tool-level enforcement); p30 records "a secondary LLM call reads the full command output and extracts the primary metric" | not found -> cut | Replace with the tool-level claim |
| §4.3 "the held-out score is itself selected over many test calls" (479-480) | Alg. 1 p7 supports the per-cycle call, but p26/p29 gate it at 5% and p33 says the test set "is evaluated only once after the search completes" | not found -> cut | Report the unreconciled tension instead |
| Table 6, Arbor: 77.36 vs 71.70 (509) | 2606.11926 p10, Table 2 | verified | Name it Terminal-Bench 2.0 |
| Table 6, AI4Research: "1 clean 14-node run" (511) | `LEDGER-VERIFIED-NUMBERS.md:96`, `:99`, `:103-105`, `:118` | corrected | See below |
| Table 6, "no external score" (511) | `SOTA-SYSTEMS.md:97` | verified | |
| Ladder rungs II / IV / VI / VIII (416-419) | 2608.05179 Table 8, p44 | verified | Numbers, labels and strongest-first order are right. Rung II also covers process rewards |
| "The survey ranks research areas rather than systems" (413-414) | 2608.05179 p48: "The ladder classifies checks, not systems" | corrected | The survey's objection is stronger than the report's disclaimer |
| The "exec" label (421) | Not in 2608.05179 | not found -> flag | The survey puts a self-manufactured check at rung V, "proxy reward" (p44) |

## What changed and why

1. **Table 6's AI4Research headline is the important one.** "1 clean 14-node
   run" fails twice against the ledger. Run A's own manifest recorded
   `evidence_gate.status=failed_for_full_requested_scope` and
   `closure_status=open_degraded`, and the log's conclusion is that it "cannot
   count as a complete E2E PASS" (`:99`) - so it was not clean. And `:103-105`
   records 2 further 14-node passes with the instruction not to quote a run
   count, which `:118` lists as a forbidden phrase. Replaced with what the run
   did deliver, without a count.
2. **3 cuts, all in §4.1 and §4.3**: AI Scientist-v2's "model reviewer as the
   final check", Arbor's "No model decides the merge", and Arbor's "selected
   over many test calls". Each is an inference the paper does not make, and the
   last is contradicted by the paper's own protocol.
3. **The ladder framing is rebuilt on the survey's own words.** The survey
   names none of the 5 systems and refuses per-system grades, so Table 6's rung
   column needs that said in its footnote.
4. **All 7 openJiuwen bullets are now sourced**, none cut. 2 needed qualifying:
   the budgets are shipped-config values that differ from the code defaults,
   and the claim-status classifier is never called.

## If asked

- **Why these 4 systems?** They span the design space, not a ranking:
  generation-first (AI Scientist-v2), scale (Kosmos), a mechanical held-out
  gate (Arbor), and the same design thesis as AI4Research (openJiuwen). None
  was chosen for its score.
- **Why is openJiuwen in the table with no result?** It is the sharpest
  architectural contrast, not an empirical comparator. Its row is read from
  code at a pinned commit; no evaluation exists in the repository, and the row
  says so rather than leaving it blank.
- **What rung is AI4Research on, and why?** Execution of a pre-approved runner
  plus citation grounding (rung IV). Not rung II: the gates are frozen, but
  nothing is held out from the agent.
- **Are the rungs the survey's?** The rung *definitions* are (p44). The
  *assignments* are this report's. The survey classifies checks rather than
  systems (p48) and never names these 5 systems.
- **Does the survey disagree anywhere?** It places mechanical end-to-end AI
  scientist loops at rung V, "proxy reward" (Fig. 3 p43; Table 17 p76), and
  codes AI Scientist-v2 as metric-driven rather than judge-driven (Table 15
  p75). This report's "exec, VI, VIII" for that system is its own reading.
- **Is Arbor's 77.36 safe to quote?** Yes, at p10, as a held-out score on
  Terminal-Bench 2.0. What is not safe is the claim that the gate excludes
  models: the metric it compares can come from an LLM extraction step (p30).
