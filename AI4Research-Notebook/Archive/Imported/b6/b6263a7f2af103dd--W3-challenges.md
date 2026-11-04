# W3: the 6 challenges made defensible, and merged for the talk

Written 2026-09-15 in worktree `w3-challenges`. Code read at AI4Research `b0bf165f9` (clean tree,
`git rev-parse HEAD` confirmed). Nothing committed.

## OWNED

- `notes/report-general/REPORT.md`: §6.1 Tables 9 to 12 and the objection paragraphs under them, §6.2, §7, Appendix B
- `notes/report-general/build/build_deck.py`: slides 17, 18, 19, 20 (file lines 326 to end). No `d.figure(` call touched
- `notes/pass2/review/W3-challenges.md` (this file)

## TOUCHED

Only the 3 files above.

## VERIFICATION (task A, each challenge against source)

| # | Claim checked | Held? | Where |
|---|---|---|---|
| 1 | 43 registered checks split 23 deterministic / 20 semantic | yes | `harness/config/evaluation-checks.v1.json`, counted by `mode` |
| 1 | 24 journey rows | yes | `docs/integrations/autosci/phase-22-journey-test-report.md`, rows P22-J01 to P22-J24 |
| 1 | 0 external scores, adapter exists | yes | `harness/lib/benchmark/terminal_bench.py`, `harness/docs/benchmark/terminal-bench-2.md`; no scorecard output in the tree |
| 1, 3 | **New**: at every risk tier exactly 1 node gets a model evaluator; every other node freezes with `evaluator_gate = {"kind": "none"}` and 0 repair attempts | yes | `harness/lib/evaluation_budget.py:22` (`_RISK_BUDGETS` all 1), `:153-172`, `:228-231` |
| 3 | **New**: a node whose gate kind is none records a policy PASS unless a deterministic scientific artifact gate is required | yes | `harness/lib/contract_gate_executor.py:209`, `:236-238`, `:263-266` (`generation_mode = "evaluator_gate_none"`) |
| 2 | 0.85 `partially_supported` from a case-insensitive substring | yes | `delivery.py:155`, match at `:137` |
| 2 | failed spans dropped silently; `precise_source_span_resolved` read by no gate | yes | `delivery.py:115-132`, `:201`; only other occurrence is `test_action_delivery_operators.py:737` |
| 2 | reportable set filtered on evidence ids, so the unsupported list stays empty | yes | `delivery.py:256-261`, `:667-670`, `:2059`; every claim carries its anchor at `operators.py:1226` |
| 2 | cue-word prefix rule, 30 to 1,000 chars, digit means testable, always typed `result` | yes | `operators.py:1181`, `:1203-1206`, `:1224`, `:1219` |
| 3 | 1 repair by default, capped at 4; fidelity demoted after the budget | yes | `intent_compiler.py:210-217`, `:1230-1265` |
| 4 | `UNSATISFIABLE_CAPSULE` fails the plan at the freeze | yes | `apo_plan_compiler.py:626`, consumed at `elastic_planner.py:7067-7080` (`decision="failed"`) |
| 5 | 21 of 79 capsule manifests declare a trust class | yes | 79 `cap.*.yaml` under `harness/` (39 + 40 in 2 directories), 21 with `trust_class` |
| 5 | coordinator ran code 28 hours older than the file on disk | yes | `harness/BUG5-ROOT-CAUSE.md:36-38`, but dated April 2026 and belonging to the old coordinator |
| 5 | **New**: a node's network rule is spent filtering capsules at planning, not at run time | yes | `elastic_planner.py:4577-4581`; the enabled `autosci-exec-experiment-run-worker` declares `network: forbidden` and `execution_trust: fixture_or_adapter_only` in `physical-operators.json` |
| 6 | 3 runs stopped at literature discovery after HTTP 429, first 2 causes fixed | yes | log l.326-329, l.662-664 (fix in `research_operator_registry_adapter.py:795-806`), l.812-815 |
| 6 | frozen `max_attempts=1 / on_exhausted=fail_run` cancelled 13 downstream nodes | yes | log l.814; the provider failure is recorded as retryable |
| 6 | the run that finished unattended had 6 PDFs attached | yes | log l.793, l.815 |

Also re-read for the ledger rule: log l.793-796 is the 2026-09-03 sprint `…-6619dfa8`, 14 nodes at attempt 1,
ledger revision 106, closure `closed`, `all_nodes_passed=true`, `all_required_gates_passed=true`. Table 5 and
Table 6 as drafted are correct and were left alone. No run count is quoted anywhere in my sections.

**Corrections made because the evidence was thinner than the sentence, not the verb:**

1. §6.1 #3 said "an evaluator that is undefined on the outcome it receives has no defined behavior". The code
   defines it: such a node records a policy pass. The row now states that, with the mechanism, so the sentence
   matches what a reader can check.
2. §6.1 #5 led with an April-2026 substrate incident. The row now leads with the CLI-agent path that research
   nodes use today, and marks the coordinator incidents as the older substrate.
3. §6.1 #6 said the third run failed because no sources were attached. The log says the provider failure was
   marked retryable and the frozen 1-attempt policy is what ended the run. The row now says that.
4. Deck slide 17 cited `delivery.py:137` for the 0.85 verdict; the verdict is at `:155` and `:137` is the match.

**Cuts: none.** All 6 challenges survive. Each now carries at least 1 fact a reader can open at the pinned
commit, and each answers the strongest objection in the deliverable rather than in a note.

## Counter-arguments, and where each is answered

| # | The strongest objection a supervising engineer makes | Answered in |
|---|---|---|
| 1 | "Every pre-release system has no external score, and the internal evidence is strong." | §6.1 paragraph under Table 9; App. B row "Every pre-release system lacks an external score"; slide 17 SAY and IF ASKED |
| 2 | "Provenance instead of truth is the honest design, and it says so in its own fields." | §6.1 paragraph under Table 10 (the gap is what the output shows; FactReview returns inconclusive); App. B row |
| 3 | "Bounded repair and advisory reviewers are by design." | §6.1 paragraph under Table 11 (the default evaluator gate is the part that is not); App. B row; slide 18 SAY |
| 4 | "13 of 22 is PlanCompiler's number, and resubmitting is cheap." | Same paragraph: the number bounds the failure mode without measuring this system, and resubmission is cheap only when the plan fails at the freeze |
| 5 | "The stale coordinator is history and dsh fixes it." | §6.1 paragraph under Table 12; App. B row; the row itself leads with the live CLI-agent path |
| 6 | "HTTP 429 is a provider flake. Retry." | Same paragraph and App. B row: the failure was retryable and the frozen policy ended the run; loosening it alone would run with no evidence |

## CHANGES

`notes/report-general/REPORT.md`

| Where | Before | After | Why |
|---|---|---|---|
| §6.1 Table 9 evidence | "Inside the run, 20 of 43 registered checks are model-judged rubrics…" | adds "At every risk tier the evaluation budget gives a model evaluator to exactly 1 node of the graph and freezes every other node with no evaluator gate" | answers "the internal evidence is enough" with a checkable fact (`evaluation_budget.py:22`) |
| §6.1 Table 9 settle | "TruthInsightBench end to end, reported per dimension; marking rubric verdicts…; hand-labeling 50 sections" | 3 tests, each with its signal (a dimension score inside the 58.4 to 60.3 band; the count of model-decided PASS values in 1 run; recall against a 50-section hand label) | a direction became a test |
| §6.1 after Table 9 | none | new paragraph answering the 2 objections, and pricing the work (a Terminal-Bench 2.0 adapter exists; TruthInsightBench needs one of the same shape) | the objection is answered in the deliverable |
| §6.1 Table 10 evidence | "…no gate reads the span flag, and claims judged insufficient or not supported still become report conclusions" | names the mechanism: the reportable set filters on evidence ids and every claim carries its paper anchor | the old sentence asserted the effect without its cause |
| §6.1 Table 10 settle | 5 directions | 5 tests with signals (replay the delivery fixture with 1 edited span; count conclusions lost by filtering on the verdict; read a delivered report for the 3 fields; per-language extractor scores) | same |
| §6.1 after Table 10 | none | new paragraph: the structured fields are the reason the design is worth keeping; the gap is the rendered output; FactReview's inconclusive outcome | answers "that is by design" |
| §6.1 Table 11 #3 evidence | "an evaluator that is undefined on the outcome it receives has no defined behavior" | the evaluation-budget and gate-executor mechanism, ending "an unanticipated outcome closes on the node's proof obligations and artifact schema alone" | the old sentence had no source; the new one does |
| §6.1 Table 11 #3, #4 settle | "Measuring the resubmission rate…"; "Counting plan defects per run…" | a freeze-then-contradict test with its signal; a planning-only replay of the 24 journeys reporting defects per plan | a direction became a test |
| §6.1 after Table 11 | none | new paragraph answering "that is by design" and "that is PlanCompiler's number" | same |
| §6.1 Table 12 #5 | led with the old substrate | leads with the CLI-agent path, adds the planning-time network rule and keeps 21 of 79 | the live claim leads; the dated one is marked |
| §6.1 Table 12 #5 settle | "sandbox access logs" | run 1 adapter-path experiment node with an outbound request in the runner and read every retained artifact; the signal is whether any shows it | a direction became a test |
| §6.1 Table 12 #6 | "with no attached sources, the frozen policy … cancelled 13 downstream nodes" | "the provider failure was retryable, and the frozen policy … ended the sprint … because no hash-bound local source was declared" | matches the log's own cause |
| §6.1 Table 12 #6 settle | 2 directions | 2 tests with signals, including a forced 429 rerun | same |
| §6.1 after Table 12 | none | new paragraph answering "that is history" and "just retry" | same |
| §6.2 | "Declaring a policy for undefined outcomes in the frozen contract (challenge 3)" | spells out halt, inconclusive or ask a person rather than recording a policy pass; new bullet on recording the deciding check kind (challenge 1); the fallback bullet names hash-bound and coverage in delivery | §6.2 now mirrors the settle columns |
| §7 heading | "2 decisions taken, 2 questions outstanding" | "2 decisions taken, 3 decisions waiting" | Q-G5 added |
| §7 Table 13 | 3 columns, owner "user" | 4 columns: question, the decision it asks for, owner; Q-G5 added (who owns each challenge, and assign 1 and 4 for the next cycle); owners are presenter or supervisor | every row is now a decision the supervisor can take |
| §7 after Table 13 | none | "Q-G4 unblocks the most…" | matches slide 20 |
| App. B | row "What happens when a frozen rule is undefined on the outcome? Nothing is defined" | the policy-pass mechanism, pointing at §2.3 and §6.1 | corrects a claim the code contradicts |
| App. B | 14 rows | 7 rows added, 1 per counter-argument, each 1 to 3 sentences with a section pointer | task C |
| §6 head (l.629) | "Arbor already runs a held-out gate with no model" | "Arbor already runs a held-out gate that only its merge tool can open" | cross-reference from the SoTA lane: 2606.11926 p30 shows a secondary model call extracts the metric the gate compares, so "no model" is not licensed |

`notes/report-general/build/build_deck.py`

| Where | Before | After | Why |
|---|---|---|---|
| slide 17 | title "No external number, and provenance is not truth"; 3 rows (#1, #2, #3) at 0:45 | title "No number from outside, and a verdict that stops at provenance"; 2 rows (#1, #2), `row_h` 1.65, size 16, widths `[0.5, 2.5, 5.0, 2.8]`; first column headed `§6.1` | fewer things to say; each row carries its own evidence and locator |
| slide 17 notes | 5-sentence SAY, 3 IF ASKED | SAY 86 words for 0:45 (cap 103), 4 IF ASKED including the Terminal-Bench adapter answer | says what the slide says plus the reason it matters |
| slide 18 | title "A wrong plan fails, and the run is not watched"; 3 rows (#4, #5, #6) | title "A frozen plan gets 1 repair, and a run needs a person"; 2 rows, labelled "3, 4" and "5, 6" | 6 report challenges become 4 slide rows |
| slide 18 notes | SAY, 3 IF ASKED | SAY 95 words for 0:45, 4 IF ASKED (28-hour coordinator, the planning-time network rule, PlanCompiler's number, the freeze trade) | the dated incident moves off the face into IF ASKED |
| slide 19 | "no verdict for a quote not in the source"; "a check that did not run is not a failure (NOT_TESTED)" | "a claim not found in its cited section never rises above insufficient"; "a check that did not run is recorded as NOT_TESTED, never as a pass" | both now state what the code does |
| slide 19 notes | SAY 76 words | SAY 76 words, matching the 2 changed cells | slide and note agree |
| slide 20 | 4 next bullets at size 21; 2-row question table at y 5.05 | 5 bullets at size 20 (adds the deciding-check-kind direction), y 2.30; 3-row table at y 4.80, `row_h` 0.52, header "The decision it asks for" | deck matches §6.2 and the new Table 13; the layout absorbs the extra rows above the footer |
| slide 20 notes | SAY 52 words | SAY 52 words naming the 3 decisions | matches the table |

Checked mechanically after editing: `check_forbidden` terms absent from `REPORT.md`; `build_deck.py` parses;
every SAY on slides 17 to 20 is between 20 words and TIME x 2.3; the `build_reading.py` §6.1 parser still
returns 5 groups, 6 numbered items, 3 cells each; group D unchanged; the markers `### 6.1 Challenges` and
`### 6.2` each appear once.

## CROSS-REFS

### App. C rows to add or change (not my lane)

| Section | Claim | Location |
|---|---|---|
| 2.3 (change) | Semantic budget: 1 model-evaluator node per graph at every risk tier; every other node frozen with an evaluator gate of kind none and 0 repair attempts | `evaluation_budget.py`: `_RISK_BUDGETS` :22, `select_semantic_targets` :153-172, :228-231 |
| 2.6 (add) | A node whose evaluator gate is none records a policy pass unless a deterministic scientific artifact gate is required | `contract_gate_executor.py`: `execute_gate` :187, :209, :236-238, :263-266 |
| 2.2 (add) | The node's network rule filters capsules at planning | `elastic_planner.py:4577-4581` |
| 2.5 (add) | Experiment adapter operator: enabled, `execution_trust: fixture_or_adapter_only`, `network: forbidden` | `harness/config/physical-operators.json`, `autosci-exec-experiment-run-worker` |
| 2.7 (change) | Verdict table; substring match; span re-verification; span flag | `…/action/delivery.py`: :133-166 (0.85 at :155), :137, :115-132, :201 |
| 2.7 (add) | Reportable set and the unsupported list built from its complement | `delivery.py`: `_grounded_evidence_ids` :256-261, :667-670, :2059 |
| 2.8 (change) | 21 of 79 manifests declare a trust class | 79 `cap.*.yaml` under `harness/capability-capsules/` (39) and `harness/config/capability-capsules/` (40) |
| 3.1 (add) | 24 journey rows | `docs/integrations/autosci/phase-22-journey-test-report.md`, rows P22-J01 to P22-J24 |
| 3.1 (add) | Terminal-Bench 2.0 adapter exists; no scores recorded | `harness/lib/benchmark/terminal_bench.py`; `harness/docs/benchmark/terminal-bench-2.md` |
| 2.2 (change) | Unsatisfiable node fails the plan | `apo_plan_compiler.py:626`; `elastic_planner.py:7067-7080` |
| 6.1 #6 (change) | Semantic Scholar stops; the retryable failure meeting a frozen 1-attempt policy; PDFs attached | Log l.327, l.662, l.814, l.815; fix at `research_operator_registry_adapter.py:795-806` |

### Sentences for other lanes

`§2.3`, replacing "A frozen evaluator that is undefined on the outcome it receives has no defined behavior. The
proposed fix is a policy declared in the test policy: halt, return inconclusive, or ask a human." (4th bullet of
"There are four limitations to the freeze"):

> A frozen rule carries no branch for an outcome it did not anticipate. At every risk tier the evaluation budget
> gives a model evaluator to 1 node of the graph and freezes every other node with an evaluator gate of kind
> none, and such a node records a policy pass, so the proposed fix is a policy declared in the test policy:
> halt, return inconclusive, or ask a person.

`§2.6`, to add after "20 of the 43 registered checks are rubrics, and the result vocabulary does not distinguish
them from the 23 Python gates.":

> The budget is narrower than that count suggests. At every risk tier 1 node of the graph carries a model
> evaluator and every other node is frozen with an evaluator gate of kind none, which records a policy pass and
> leaves the node's proof obligations and artifact schema to decide.

`App. E.4 step 1` already says the test policy sets 1 model-evaluator node, or 0 for a rapid smoke run, so it
needs no change.

Two "no model" descriptions of Arbor's gate survive outside my lane and need the same wording as §6 l.629:
`REPORT.md:531` ("Arbor shows a held-out gate with no model paying off") and `REPORT.md:766` (Table A1, "Held-out
merge gate with no model"). Deck `build_deck.py:285` and `:298` (slide 15) carry it too. All 4 belong to the SoTA
lane.

`PRESENTER-PACK-workflow.md` §5, hard question 8 ("Why is the 14-node run not a pass?") describes Run A while
the report describes the 2026-09-03 run at log l.793-796, which passed every required gate. The pack contradicts
the report and the ledger's Run C row; the pack's owner should reword or drop it.

### Deck to report numbering map

| Slide | Row label | Report |
|---|---|---|
| 17 | 1 | §6.1 group A, challenge 1, Table 9 |
| 17 | 2 | §6.1 group B, challenge 2, Table 10 |
| 18 | 3, 4 | §6.1 group C, challenges 3 and 4, Table 11 |
| 18 | 5, 6 | §6.1 group E, challenges 5 and 6, Table 12 |

Group D stays the capsule-report pointer and has no slide row, as before.

### TIME deltas

None. Slides 17, 18, 19, 20 keep 0:45, 0:45, 0:35, 0:30, so the workflow deck stays at 15:25 and
`deck-times.json` needs no change. Net change across my slides: 0:00.

## DOUBTS

1. Table 10's evidence cell is 170 words and its settle cell 95. The review `R-general-report.md` finding 17
   already called these cells paragraphs wearing table borders, and my additions did not shrink them. Settled by
   looking at the rendered page: if the cell runs past a page, split group B into 2 rows, provenance and
   language, which the register parser accepts.
2. "An unanticipated outcome closes on the node's proof obligations and artifact schema alone" is read from
   `contract_gate_executor.execute_gate` and `capsule_execution_gate.validate_proof_obligations`. I did not
   trace every caller of `mark_node_result`, so a fourth check may exist. Settled by running the freeze-then-
   contradict test in Table 11, which is the settle action itself.
3. The share of nodes in a real run whose scientific artifact gate is required is unknown, so "every other node
   records a policy pass" is the worst case rather than the measured case. Settled by reading the 14 nodes of
   the 2026-09-03 run for their `generation_mode` values.
4. The journey suite has 24 rows, but its last full run is recorded as 15 passed and 11 skipped, which does not
   add to 24. The report only uses the count, so nothing I wrote depends on it. Settled by opening the final
   journey run record named in the report.
5. `network: forbidden` on the experiment adapter operator is read as a planning-time filter. I did not search
   the dsh-side or OS-level sandbox for a second enforcement point. Settled by the adapter-path outbound-request
   test in Table 12.
6. Table 9 says a TruthInsightBench evidence-auditability score inside 58.4 to 60.3 puts AI4Research with the
   field. That band is the paper's total across 4 coding agents, not its per-dimension range, so the threshold
   is a proxy. Settled by reading 2609.05079 p12 and p14 for the per-dimension spread and restating the number.
7. Q-G5 changes the §7 heading from "2 questions outstanding" to "3 decisions waiting". No builder slices §7,
   but the docx, the deck and `HANDOFF.md` §10 all quote the old count. Settled by a rebuild and a grep.
8. Slides 17 and 18 now carry 2 rows of about 45 words each at 16 pt with `row_h` 1.65. I did not render them.
   Settled by `render.py` and a look at slides 17, 18 and 20, where the question table moved up to y 4.80.
