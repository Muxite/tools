# AI4Research: Workflow, State of the Art, and the Target Platform

Muk Chunpongtong · September 2026

This report covers 3 subjects, in the same order as the presentation:

- How AI4Research turns a research request into checked evidence
- How each stage of that workflow compares with the systems that define the state of the art
- Which platform the work moves to, and what AI4Research adds on top of it

Code claims were read in source at AI4Research `b0bf165f9`, DeepSeek Harness `c291e7961a` and openJiuwen
`agent-core@6ecf8218`, and paper claims were read in the cited paper. The body follows the presentation. Appendix A
lists the sources, Appendix B answers the questions a reviewer is likely to ask, Appendix C gives the code location
behind every code claim, Appendix D holds the code excerpts, and Appendix E holds the workflow details that the
presentation leaves out.

---

## 1. The goal: 3 claims, and the 6 terms they rest on

The report is written for a reader who builds agents but has not seen this codebase. It makes 3 claims, and
Sections 2 to 6 give the evidence for each:

- The workflow has 1 boundary that matters, the freeze, which fixes the plan, the capabilities bound to it and the
  rules that will grade it before anything runs
- The state of the art generates research well and checks it weakly, while AI4Research checks strictly and pays for
  it in code generation, claim recall and external evaluation
- The DeepSeek Harness supplies the runtime that AI4Research built by hand, and the contract layer is what
  AI4Research adds

AI4Research is a local-first multi-agent system. It compiles a natural-language research goal into a typed,
hash-verified contract, then executes that contract as a task graph in which each step runs on an interchangeable
operator: a model, a command-line (CLI) coding agent or a tool. It is packaged as OpenJiuwen Solar, release
`1.0.0-rc.9`.

The project states its target design in 1 sentence, translated here from the Chinese original:

> LLMs interpret semantics; deterministic code validates structure, maintains references, freezes contracts, and
> schedules.

This sentence is a design target, not a measured property. Thus, Section 2 checks, stage by stage, where a model
proposes and where code decides.

6 terms carry the whole report (Table 1).

| Term | Meaning |
|---|---|
| capsule | A contract for 1 capability, written in YAML: its typed inputs and outputs, its effects on the system, its preconditions, postconditions and invariants, and how it is verified. The registry holds 80 entries (77 capabilities, 1 guard and 2 resources), and 74 of the 79 capsule manifests are registered, so 5 manifests are unregistered and 6 registry entries have no manifest |
| operator | Whatever executes a step. A logical operator is an abstract role with graded requirements, such as architecture reasoning at level 4, and 45 are defined. A physical operator is a concrete executor, such as a model endpoint, a CLI agent or a tool, and 102 are defined, of which 63 are enabled |
| sprint | 1 request carried from compiled intent to closure |
| node | 1 step of a sprint's task graph |
| gate | A check that decides PASS or FAIL for the output of 1 node |
| freeze | The point at which the plan, its capability bindings and its grading rules are hashed into 1 run contract |

*Table 1. The 6 terms the report rests on.*

A research run produces schema-validated evidence artifacts rather than free prose.

---

## 2. The workflow: models propose, code checks, and the freeze fixes the rules

A request passes through the stages in Fig. 1, and the freeze divides them in 2. Before the freeze, a model proposes
each artifact, meaning the compiled intent, the requirement contract and the plan, and deterministic code checks it.
At the freeze, code hashes the plan, its capsule bindings and its grading rules into 1 run contract. After the
freeze, no model schedules work, routes it to an operator or admits a result. Models still run inside capsules as
operators and judge inside rubric gates, but the order of work, the choice of operators and the rules that decide
PASS are all fixed.

![Fig. 1. The workflow. Above the freeze, every model call is followed by code that checks it; below it, a frozen contract is executed. Tinted boxes are model calls, white boxes deterministic code, and colour marks the stage.](build/fig/fig-workflow.png)

Appendix E gives the detail of each stage.

### 2.1 Before the plan: code checks every model output

The first 2 stages turn the request into a structured record of what was asked, called the IntentIR, and then into a
requirement contract, which states what would satisfy the request before any stage decides how. Each model output is
checked by code before the next stage reads it (Table 2).

| Step | Author | What it does |
|---|---|---|
| Compile intent | A model | Writes the IntentIR: goals, typed outcomes, constraints, ambiguities, conflicts and unknowns |
| Validate | Deterministic code | Runs 7 kinds of check, and finds every quote the model gives in the request text |
| Fidelity review | A second, independent model call | Checks that the IntentIR reflects the request |
| Accept | A deterministic gate | Accepts, returns a blocking ambiguity or conflict to the user for clarification, or fails |
| Fill requirements | A model | Fills in values only, since the valid Intent ids and check ids are enumerations in the schema |
| Check requirements | Deterministic code | Requires constraints copied byte for byte, every Intent id covered, and only registered checks |

*Table 2. The steps before planning, and who authors each.*

Code keeps the model in check at each of these steps:

- Binding every quotation to the request. The model supplies quotes, and code finds each quote in the request text and
  records its offsets. A quote that is not found, or is found more than once, is a repairable error, so the model
  cannot point at text that is not there
- Bounding repair. The intent is repaired once by default and at most 4 times, because every extra repair is another
  chance to optimize the output against the validator rather than against the request
- Making invented references impossible. The JSON schema sent to the model lists the valid Intent ids and the ids of
  the registered checks as enumerations, meaning fixed lists of allowed values, so a reference to an Intent item or a
  check that does not exist fails schema validation before any other code reads it

The fidelity review has already caught a real error. In the 14-node run of 2026-09-03, the reviewer caught the
compiler strengthening "distinguish 5 evidence statuses" into "only these 5", and 1 bounded repair fixed it before the
intent was accepted.

The checks registry matters for every later gate. It holds 43 checks: 23 deterministic Python gates, applied
automatically to an artifact type, and 20 semantic rubrics, judged by a model for an output that a requirement names.
Thus, 20 of the 43 registered checks are model judgments, and Section 2.6 shows that results do not record which kind
decided.

Research agents such as AI Scientist-v2 (2504.08066) and Kosmos (2511.02824) take a topic straight into an agent loop
and leave no typed artifact that a later stage can check against. The closest published design is PlanCompiler
(2604.13092), in which the model only selects typed nodes from a closed registry and static checks validate the
resulting graph. It scores 44 of 50 on schema-trap tasks, against 20 of 50 for GPT-4.1 and 26 of 50 for Claude (p1),
but it has not been applied to research workflows.

There are two limitations to this stage:

- A fidelity objection is demoted to a warning once the repair budget is spent. This is deliberate, since a review
  model must not become a second admission gate, but it means a meaning-level error the reviewer found can still pass
- Criteria for selecting the literature corpus are not separated from process language in the free text. One run
  filtered its literature search on the words "one-off answer" and emptied its own shortlist

### 2.2 Binding: code narrows the capsules, a model picks, and code binds

The plan says how the request will be met and which capability each step uses (Fig. 2). Before any model sees the
candidates, a hard filter excludes capsules on 13 codes: a mismatched input or output type, an unsatisfiable mandatory
proof class, effects that do not match the node's request in both directions, network rules, a missing verification
contract, an undeclared implementation and unsatisfied execution trust. Matching in both directions means a capsule
must have every effect the node requires and no effect the node did not request. The planner model then picks only
among the capsules that survived, code validates the choice on 8 codes, and a second model reviews the fit, but a
failed review only produces a warning. Finally, the capsule id, proof obligations, artifact types, effect union and
approved physical operators are copied from the manifest, never from the model. Appendix E.3 lists all 8 steps of
planning.

![Fig. 2. Capsule binding: code filters, validates and binds; a planner model selects among the survivors and a second model reviews the fit, advisory only. When no capsule fits, the plan fails at the freeze.](build/fig/fig-binding.png)

There is no generalist fallback today. A node that no capsule and no composition fits raises `UNSATISFIABLE_CAPSULE`,
and the whole plan fails at the freeze. The nearest substitutes are a direct response to the whole request, coding
capsules that wrap frontier CLI agents by default, and composition through registered adapters. The companion report
"Capability Capsule in AI4Research", called the capsule report throughout, proposes a generalist capsule for exactly
these nodes.

There are two limitations to this stage:

- Capsules that call models are opaque at planning. The planner sees only their trust class, reasoning class and list
  of operators, not the prompt or its behavior
- The fit reviewer is advisory and may be the same model as the planner, in which case the record states that the
  review was a second pass by the same model

### 2.3 The freeze: the plan and its grading rules are hashed before anything runs

The freeze turns the negotiated plan into a contract. It runs in 8 steps of deterministic code (Appendix E.4), and any
step can fail the sprint. The evaluation budget becomes a test policy first, so the grading rules exist before
anything is sealed. If any capsule or operator definition changed during planning, the freeze aborts
with `CAPSULE_CHANGED_DURING_PLANNING` or `OPERATOR_CHANGED_DURING_PLANNING`. The check compares the
live definitions against the ones already frozen into the nodes, so it runs only for a plan whose
nodes already carry their capsule bindings and frozen execution candidates (Appendix E.3).

![Fig. 3. The freeze chain. Each artifact is hashed and linked by reference; thick borders are hashed with the grading rules inside them.](build/fig/fig-freeze.png)

The grading rules are inside the hash. The compiler writes each node's evaluator bindings and the run's test policy
into the scheduler input itself (Appendix D), and the hash is SHA-256 over canonical JSON with sorted keys and no
whitespace. If the grading rules sat outside the hash, a run could be judged by rules chosen after its outputs were
seen. Inside it, changing what counts as success changes the hash, and the run no longer matches its contract.

Verification recomputes 3 stages, the composition-selection validation, the evaluation-plan validation and the
scheduler-input compile, and compares the hashes of everything else. An existing test sets a node's priority to 999
in a frozen bundle, and verification fails even though the stored verdict still says PASS; edited acceptance criteria
and an edited composition rationale fail the same way (Appendix E.4). A hash detects an edit after the fact, wherever
something recomputes it; it prevents no edit and authenticates no author. When the freeze fails, the plan is marked
failed with its reasons, partial artifacts and a failure receipt are kept, and the sprint ends. There is no re-planning, so
the user submits a new request.

Other work fixes parts of a run before execution, but none fixes the grading rules with the plan (Appendix E.4
compares them). A targeted search on 2026-09-13 found no reviewed system that seals its own evaluation criteria inside
the run's integrity hash. The survey "Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap"
(2608.05179) recommends exactly this from outside the run, as "a pre-committed task specification that fixes the
metric, the split, and the success threshold before the run" (2608.05179 p28). Thus, the idea is recognized but has not
been built elsewhere.

The freeze has 3 costs:

- Losing plan-level search. Search happens only inside operators, so the plan cannot change when execution shows it
  was wrong
- Handling staleness only before the freeze, by bounded repair
- Fitting execution and grading well and open-ended exploration poorly, where Arbor (2606.11926) and Kosmos re-plan
  every cycle (Section 4)

There are four limitations to the freeze:

- A frozen contract is only as good as its compilation, and plan defects per run are not measured
- An open capability, such as a shell or SQL, routes around typed contracts. PlanCompiler calls this "constraint
  evasion under partial enforcement" (p3), and it causes 13 of its 22 failures (p17)
- A frozen rule carries no branch for an outcome it did not anticipate. At every risk tier the evaluation budget gives
  a model evaluator to 1 node of the graph and freezes every other node with an evaluator gate of kind none, and such a
  node records a policy pass, so the proposed fix is a policy declared in the test policy: halt, return inconclusive,
  or ask a person
- Any change to a capsule definition during planning aborts the freeze, so a library that keeps changing would race
  every plan

### 2.4 Dispatch: a failure stays contained, and gates never move

Execution is tick-based. The scheduler does not plan everything and then run it; it repeatedly picks the nodes that are
ready and dispatches them. The frozen contract is projected into a runtime graph, a separate ledger holds everything
that changes during the run, and every step of a tick is deterministic code (Appendix E.5).

Fig. 4 follows an illustrative graph of 7 nodes through 4 ticks. For every node, the freeze fixes the bound capsule
and its contract hash, the operator candidates, the evaluator gate, the write scope, the repair budget and the failure
policy. Gates are therefore chosen at the freeze and never updated during the run, and the runtime refuses any change
to a frozen field. On each tick the scheduler builds its ready set in 4 steps:

- Ordering the nodes topologically with Kahn's algorithm, with ties broken by id
- Keeping the nodes whose dependencies have all passed
- Ordering those nodes by priority and id and selecting up to 8
- Skipping any node whose write scope or effects conflict with a node already selected in that tick, so that the node
  waits for a later tick rather than failing

A node that fails its gate returns to a ready status and is repaired with the gate's findings. Once its repairs are
spent, it is marked failed, and every node that depends on it is skipped as blocked by a failed dependency. A node
waiting for human review holds its dependents pending instead. The frozen failure policy then stops the node or fails
the run. A passed node never regresses, and work envelopes are fingerprinted, so a retry never repeats a paid call.

![Fig. 4. 1 frozen graph over 4 dispatch ticks: Kahn ready sets, a write-scope conflict, a failed gate with repair, and the skipped dependents of a node whose repairs ran out.](build/fig/fig-dag.png)

The limitation of this stage is its substrate. Work moves through tmux keystroke injection, file inboxes and SQLite,
and that substrate produced failures of its own. One coordinator ran code 28 hours older than the file on disk, and a
run manifest recorded the node statuses a model declared rather than those in the ledger, a defect a deterministic
materializer fixes at `b0bf165f9`.

### 2.5 Operator execution: 1 path is recorded, and the CLI-agent path is not observed

An operator runs a node along 1 of 2 paths, and the paths differ most in what is observed (Appendix E.6). On the
registry path, code re-verifies the graph projection, the frozen operator candidates, the artifact contract, the
capsule binding and the write scope before running, and it keeps the request, schema, response, events and hashes of
each model call. On the CLI-agent path, the agent receives a tmux pane in a git worktree, and its commands, files and
network access are not observed. Its evidence is classed `fixture_or_adapter_only`, which marks evidence that came
from a test fixture or an adapter rather than from a measured execution.

The trust model follows from these 2 paths (Fig. 5):

- The user's request is trusted. The raw intent records its channel and sender, and clarification, the fidelity review
  and the refusal check exist to capture what the user meant, not to defend against the user
- Papers, web pages, tool output, code a model writes and remote agents are untrusted
- The freeze fixes the plan before untrusted content is read, the property CaMeL (2503.18813) enforces for control flow (p1). Planning
  sees uploaded files only as records and paths, and nodes read their contents after the freeze
- The CLI-agent path breaks that separation, since `codex exec` reads papers and data while holding shell, file and
  network access, unobserved. CaMeL gives untrusted text only to a model with no tools
- A fixed plan does not stop untrusted text from steering values, since a sentence planted in a paper passes the
  literature check as partially supported (Section 2.7)
- This trust model holds for 1 user on a local machine, and a shared, unattended server with several users and API
  credentials needs a different one (capsule report, Appendix G.8)

![Fig. 5. Trust boundary: the plan is fixed before untrusted content is read; the CLI-agent path hands that content to an agent with tools.](build/fig/fig-trust.png)

### 2.6 Gates and delivery: code or a model decides, and results do not say which

Every node closes on the evaluators frozen for it, and there are 4 kinds (Table 3).

| Kind | Decides by | Note |
|---|---|---|
| Deterministic command | Exit code, decided by code | Passes on exit code 0; a timeout counts as an infrastructure failure, which cannot flip a node that passed its policy |
| Model evaluation | A separate evaluator actor | A model judgment |
| Code task | A patch, test evidence and a verifier decision | The writer may not be the verifier |
| Scientific gate | The artifact type | Applied according to the artifact type |

*Table 3. The 4 kinds of gate.*

A receipt is not evidence: a node closes only on the chain of result, callback and an evaluator PASS. At the end of
the sprint, a terminal barrier publishes the outputs byte-identical to the working directory and closes the sprint.

The limitation of this stage is that a rubric PASS is a model judgment recorded by code. 20 of the 43 registered checks
are rubrics, and the result vocabulary does not distinguish them from the 23 Python gates. The budget is narrower than
that count suggests. At every risk tier 1 node of the graph carries a model evaluator and every other node is frozen with
an evaluator gate of kind none, which records a policy pass and leaves the node's proof obligations and artifact schema
to decide.

### 2.7 Claims: the check proves where a sentence came from, not that it is true

Claims move through a chain of 6 evidence schemas: literature discovery, research paper, research claims, claim verdict,
scientific report plan and scientific report. No model is called anywhere in claim extraction or in the verdicts.

Extraction uses a cue-word rule rather than a model:

- A sentence of 30 to 1,000 characters becomes a claim if it contains a cue word: show, demonstrate, improve, reduce,
  increase, achieve, outperform, result, found or find. Cue words match by prefix, so "founded" counts as "found"
- A claim is marked testable if it contains any digit, a percent sign, "compared" or "than", so a year qualifies, and
  partially testable otherwise
- Every claim is typed as a result, and claims are taken round-robin across papers, 12 by default and at most 50
- Each claim carries its citation spans: the character offsets into the normalized section text, the quote and the
  SHA-256 hash of the whole section
- If no sentence matches, extraction fails with an error rather than inventing a claim

Verdicts come from a decision table checked from top to bottom (Fig. 6). When a claim has no experiment, the only
evidence is the literature, and the check is a case-insensitive substring match against the cited section, which
yields the class `source_reported`.

![Fig. 6. The claim chain and the verdict decision table, checked top to bottom.](build/fig/fig-claim.png)

Spans are re-verified: the quote must equal both the text at its offsets and the claim text, and the section hash must
match. A span that fails is dropped silently and does not enter the verdict, which reads the substring match alone. A
flag, `precise_source_span_resolved`, turns false only when every span fails, and no gate reads it. The claim verdict
gate refuses 4 things:

- Upgrading evidence that does not support the claim
- A supported verdict with open overclaim risks or a mismatched scope comparison
- A verdict whose only evidence is the claim itself
- Any verdict without limitations

The report lists unsupported claims, but the list filters on the wrong property. A verdict is reportable whenever it
has a non-placeholder evidence id and claim text, whatever its value, and every extracted claim carries its paper anchor
as an evidence id through verification. Thus, an extracted claim judged insufficient or not supported becomes a report
conclusion, marked only by its evidence status, and the list of unsupported claims stays empty.

1 claim from a test fixture shows the whole chain (Table 4).

| Step | "Reranker A improves ranking quality over reranker B." |
|---|---|
| Cue word | "improves" matches |
| Testability | Set to testable in the fixture; the extractor would assign partially testable, since the sentence has no digit, percent sign, "compared" or "than", and "over" is not on the list |
| Span | The whole sentence, in the results section of the reranker paper, with the hash of that section |
| Experiment | None |
| Substring check | Found, case-insensitive |
| Verdict | Partially supported, class `source_reported`, not locally reproduced |
| Gate | No upgrade is possible; the report carries the claim as a conclusion whose evidence status is source-reported and whose tested status is not locally reproduced |
| If the span had failed its re-hash | The verdict would be unchanged; proposed fix: a gate on `precise_source_span_resolved` |

*Table 4. 1 claim from a test fixture, end to end.*

Without an experiment, the strongest verdict certifies only that the sentence occurs in the cited section, so a wrong,
retracted or cherry-picked paper passes. This is provenance, not truth. The system records it in 3 structured fields: a
limitation ("Source-reported exact quotation only"), a verification basis of source-reported exact quote, and the
conclusion's evidence status. Whether the rendered report prose shows those labels has not been checked. Appendix E.7
compares this design with the nearest published alternatives and gives measured rates of citation and claim failure.

There are four limitations to claim handling:

- AI4Research's own extraction recall is unmeasured. A claim the cue-word rule misses never appears among the
  unsupported claims, so the list looks complete when it is not
- The span hash is recorded but not enforced
- The unsupported list filters on evidence ids rather than verdicts, so weak verdicts reach the conclusions
- Every claim is typed as a result, and multi-clause sentences are not decomposed

### 2.8 Experiments: trusted measurement covers only 1 hand-written family

Experiments are the only place where AI4Research measures rather than cites. `cap.research-experiment-run` is the only
capsule with the trust class `measured_execution`, and its invariants are strict:

- Running only "an exact Python runner and input files whose hashes are bound into the approved plan"
- Using no network and writing only inside the approved scope
- Refusing to claim measured execution "when the process or result contract fails"
- Requiring a hash-bound experiment approval before any run that is not a fixture

Experiment code is written on 1 of 2 paths:

- On the native path, a plan template is filled in and the package comes from a dataset manifest. Only 1 experiment
  family exists, KV-cache quantization for causal language models, and its runner was written by hand
- On the adapter path, the experiment is delegated to `codex exec`, and its evidence is classed
  `fixture_or_adapter_only`

Across the library, only 21 of the 79 manifests declare a trust class at all.

Code generation is at the center of every end-to-end system in Section 4. AI Scientist-v2 (2504.08066) writes and runs
code at every node of a tree search, and its checking missed a 57% overlap between training and test data (Section
4.1).

Thus, the native path cannot fabricate a measurement but cannot test a claim outside 1 family, while the adapter path
has the generality and none of the trust. The proposed direction is for a model to write runners on the native path,
where nothing runs until it is hashed and approved.

---

## 3. Evaluation: 1 internal run executed end to end, and no external score yet

### 3.1 Evidence so far: demonstrated end to end, not yet routinely unattended

The evidence so far comes from the stabilization log and the journey test report (Table 5). Journey tests are the only
acceptance evidence; regression suites locate faults but never decide the verdict (Appendix E.8).

| Evidence | Result |
|---|---|
| 14-node research run, 2026-09-03 | 1 bounded intent repair (Section 2.1), then the requirement contract and the plan were accepted the first time; every node passed on its first attempt and the ledger reached revision 106. The run executed its 14 nodes, delivered the 8 requested files and closed with every required gate passed (log l.793-796) |
| Pre-release regression, 22 affected test files | 606 passed, 34 failed and 8 skipped; the 34 failures are kept as known debt, from old fixtures that the current frozen-plan preflight rejects and from Windows path failures, rather than relaxed away |
| Journey tests | 24 real tasks run through the production entry points, the only acceptance evidence |
| External benchmark scores | None; an adapter for Terminal-Bench 2.0 exists |

*Table 5. Evidence so far.*

Thus, the workflow has been demonstrated end to end, but it is not yet routinely reproducible without a person
attending.

Results use 6 values: PASS, PASS_WITH_KNOWN_LIMITATIONS, FAIL, NOT_TESTED, ENVIRONMENT_BLOCKED and NOT_AVAILABLE. A green
result may not be copied to a variant that no journey exercised, and the journey report states that it is "not a claim
that all 142 Level 2 features passed". No source records the token cost, the money or the wall-clock time of a sprint,
so this report gives no cost figure.

### 3.2 TruthInsightBench: the first external test, reported per dimension

The proposed first external test is TruthInsightBench (2609.05079), which sets 40 blind discovery tasks drawn from 40
peer-reviewed studies across 10 scientific domains (p1). It is the right first test for 4 reasons (Fig. 7):

- Its scored object is verification. It awards 100 points over 6 dimensions: evidence auditability 45, robustness 15,
  control testing 15, cross-dataset generalization 10, novelty 10 and falsifiability 5 (p8)
- The 4 measured agents score 78% to 81% on evidence auditability and 83% to 87% on novelty, against 11% to 16% on
  control testing, the dimension that asks whether a simpler explanation or a no-signal control would have produced
  the same result (p14)
- Its result is a flat plateau, since 4 coding agents on 1 frozen base model score 58.4 to 60.3 over the 40 tasks and no
  pair separates, with the smallest p = 0.118 (p1, p12). Any real gain would be visible
- A frozen model judge applies the rubric to executed artifacts, only the aggregation is deterministic, and no instance
  is graded by a human (p2, p9)

![Fig. 7. TruthInsightBench, range across 4 coding agents per dimension (2609.05079 p3, p14). Red, hatched: dimensions that need the agent to try to break its own result.](build/fig/fig5-benchmarks.png)

Thus, results on this benchmark should be reported per dimension rather than as a total.

---

## 4. The state of the art: 4 reference systems that generate well and check weakly

The 4 systems were chosen to span the design space: generation first (AI Scientist-v2), scale (Kosmos), a mechanical
held-out check (Arbor), and the same thesis as AI4Research inside openJiuwen (auto_research). Each system is placed on
the verification ladder of the survey "Autonomous Research Agents: A Survey of AI Scientists and the Verification
Gap" (2608.05179), introduced in Section 2.3. The survey classifies "checks, not systems", and warns that
"locating a system on the ladder means decomposing its output rather than awarding it a single grade" (p48), so the
placements below are this report's own, and 5 rungs of the ladder are used (p44):

- II: an executable test against held-out ground truth, or a process reward
- IV: grounding in citations
- V: a threat-to-validity argument or a proxy reward, meaning a check the system manufactures for itself when no
  independent oracle exists
- VI: judgment by a human expert
- VIII: the model's own judgment

Rung V carries most of the weight below, because running code the system wrote against tests the system chose is a
proxy reward rather than a held-out test. The survey reaches the same placement from its own corpus, filing the
sub-area "newest 2026 AI scientists" at rung V with the signal "externalized checking apparatus (mixed)" (p76).

4 further end-to-end systems were read and left out of the comparison, since the strongest check each admits is one
AI4Research has no path to: Co-Scientist (2502.18864) ranks hypotheses in a model tournament and validates the
survivors in vitro (p2, p5), Robin (2505.13400) proposes a drug candidate and confirms it in the laboratory (p1),
Agent Laboratory (2501.04227) takes human feedback at every stage and scores higher in that co-pilot mode than
autonomously (p1-2), and "Towards End-to-End Automation of AI Research" (2606.15497) repeats AI Scientist-v2's
workshop experiment with the same generation-first design (p2).

### 4.1 AI Scientist-v2: strong generation, and a review that missed a 57% data overlap

AI Scientist-v2 (2504.08066) generates research first and checks it last. It works in 4 phases:

- Ideation at "grant proposal" level, with Semantic Scholar checked for novelty (p4)
- An experiment progress manager that runs 4 stages with explicit stopping criteria: prototype, hyperparameter tuning,
  research agenda and ablations (p5)
- A tree search inside each stage. At each node the model writes a plan and Python code, the code runs, an error marks
  the node as buggy, and a vision-language model critiques the figures. Expansion debugs buggy nodes or extends the best
  ones, and a model evaluator picks the best node per stage (p5-7)
- Writing in 1 pass followed by a reflection stage (p4), with a vision-language model checking that figures match their
  captions (p8)

3 of its manuscripts were submitted blind among the 43 submissions to an ICLR 2025 workshop, and 1 scored 6, 6 and 7
(6.33), above the acceptance threshold, before being withdrawn by prior agreement (p9). Humans chose 3 ideas from 2
batches of about 20 each, and the best manuscript for each idea (p10).

The checking missed a serious flaw. The authors' own post-review examination found about 57% overlap between training
and test data in the code (p11), while the workshop reviewers raised justification and breadth, not the overlap (p2).

Compared with AI4Research, AI Scientist-v2 searches adaptively at every stage, lets a model evaluator pick the best
node per stage (p5) and a vision-language model review figures and captions (p7), and has no contract. Its last check
before submission was human peer review, not a model. Thus, it is strong at generating, and its checking is its own
execution, peer review and model judgment (rungs V, VI and VIII).

### 4.2 Kosmos: research at scale, least accurate on synthesis at 57.9%

Kosmos (2511.02824) is built for scale, and it works in cycles:

- A scientist supplies an objective and a dataset
- Each cycle launches up to 10 parallel tasks across 2 agent types, 1 for data analysis and 1 for literature search,
  and their outputs are summarized into a shared world model, which is queried to propose the next cycle's tasks (p2)
- A run takes over 200 agent rollouts, writes 42,000 lines of code and reads 1,500 papers (p1-2)
- "Each statement and figure in the report cites either a publication found by the literature search agent or a Jupyter
  notebook created by the data analysis agent" (p2)

102 statements were extracted from 3 representative reports and rated by expert scientists who were not shown the
supporting code or cited papers, and 79.4% were accurate (p2, p4). By type, 85.5% of data analysis statements were
reproducible, 82.1% of literature statements were validated against primary sources, and 57.9% of synthesis
statements were accurate (p4).

Compared with AI4Research, Kosmos cites every statement and measures accuracy afterwards rather than gating on it
during the run, and it re-plans its world model every cycle, the opposite of a frozen contract. The 57.9% on synthesis
supports keeping claims separate from synthesis, as AI4Research does, but it says nothing about AI4Research's own
synthesis. Its checks are citation grounding and its own execution (rungs IV and V).

### 4.3 Arbor: a held-out merge gate the merge tool alone can open, the closest system on checking

Arbor (2606.11926) separates a long-lived coordinator from short-lived executors:

- The coordinator owns a hypothesis tree, and each node of the tree holds a hypothesis, an insight and metadata, which
  carries "an implementation reference such as a git branch or commit" (p6); the schema names it a branch (p31)
- Each executor tests 1 hypothesis in its own isolated git worktree (Alg. 1, p7). An executor may repair the
  implementation but not change the hypothesis, since otherwise "the returned score would no longer be evidence about
  the assigned node" (p8)
- The coordinator loops through 6 steps: observe, ideate, select, dispatch, backpropagate and decide (p7)
- A held-out merge gate evaluates the best-scoring candidate on the test evaluator in a fresh worktree, and merges it
  into the best artifact only if it improves on it (p8). The merge tool "is the only path through which a candidate
  branch can be promoted", so the gate is enforced by the tool rather than by the coordinator (p28)

On Terminal-Bench 2.0, whose 89 shell tasks are split into 36 development and 53 held-out test tasks (p8), with Claude
Opus 4.6 running both Arbor roles (p9), Claude Code has the best development score (75.00) and drops to 71.70 on the
held-out tasks, while Arbor scores lower on development (72.22) and best on the held-out tasks (77.36) (p10). There are
2 limitations to this result:

- How often the test evaluator runs is unreconciled. Algorithm 1 calls it on the best candidate every cycle (p7), the
  reported protocol evaluates the test set "only once after the search completes" (p33), and the implementation fires
  the gate only past a 5% development-score threshold (p26, p29)
- The gate compares a number a model may have produced. When the command output holds no valid JSON block, "a
  secondary LLM call reads the full command output and extracts the primary metric as a percentage" (p30). The
  comparison is mechanical, and the measurement it compares need not be

Compared with AI4Research, Arbor is the closest system on checking. Its gate is fixed outside the agent that the gate
judges, but the gate is not hashed with a plan, and the plan changes every cycle (rung II).

### 4.4 openJiuwen auto_research: the same thesis, with the contract renegotiated every round

openJiuwen's agent-core at `6ecf8218` contains an automated research package, auto_research, built from 6 parts
(App. C):

- A module chain from topic survey through experiment design, code implementation, experiment execution and reflection
  to reporting in LaTeX, plus standalone paper scoring
- An LLM manager that emits 1 decision each round: execute a subtask under a contract, done, or blocked
- Host-side validation that rejects illegal moves in code, such as execution without a ready implementation,
  re-execution before repair, or declaring done while requirements are pending
- Budgets in the shipped config of 50 rounds, 4 code retries, 6 design revisions and 4 execution retries; the code
  defaults behind them are lower, at 30, 4, 5 and 3
- A claim-status classifier that is "pure, host-only ... no model call", comparing this run's numbers against a prior
  paper's. It is defined but not called anywhere in the package
- Paper scoring by a dual rubric sampled 5 times at temperature 0

The repository publishes no evaluation of the package: no results, benchmark or evaluation document exists anywhere
under `paper_opt/`.

Compared with AI4Research, auto_research shares the design thesis that the model decides and the host validates, but
it renegotiates the contract every round rather than freezing it per run. Thus, it is the sharpest contrast in this
report.

### 4.5 Side by side: AI4Research checks the most and generates the least

| System | Plans how | Checks with | Rung | Headline result |
|---|---|---|---|---|
| AI Scientist-v2 | Tree search per stage | Execution; model and vision-language reviewers | V, VI, VIII | 1 of 3 workshop papers above threshold; 57% overlap missed |
| Kosmos | World model, re-planned each cycle | Citation to a notebook or a source | IV, V | 79.4% of statements accurate; 57.9% on synthesis |
| Arbor | Coordinator-owned hypothesis tree | Held-out merge gate, enforced by the merge tool | II | Terminal-Bench 2.0 held out: 77.36 against 71.70 for Claude Code |
| openJiuwen auto_research | Manager with a contract per round | Host validation each round; rubric scoring | V, VIII | No published evaluation |
| **AI4Research** | **Compiled, frozen contract** | **Grading rules hashed with the plan; 23 code gates, 20 rubrics** | **IV, V** | **14 nodes executed and 8 files delivered with every required gate passed; no external score** |

*Table 6. The 4 reference systems and AI4Research side by side. Every result except openJiuwen's is the authors' own
measurement, and openJiuwen's row is read from code at `6ecf8218`. The rung column is this report's own: the survey
classifies checks rather than systems (2608.05179 p48), and names none of these 5 systems.*

The field is ahead on autonomy, scale and generality. Kosmos reads 1,500 papers in a run, AI Scientist-v2 writes and runs
its own experiments, and Arbor shows that a held-out gate only a tool can open pays off. AI4Research's claims are
auditable, through frozen gates, retained spans, and a verdict and evidence status on every conclusion, but they have
not been checked externally.

---

## 5. The target platform: the DeepSeek Harness supplies the runtime, not the contract

The platform decision was made on 2026-09-11: the DeepSeek Harness (dsh) for now, chosen as the more certain of the 2
candidates and already the target of the capsule report. Sections 5.1 to 5.3 give the evidence for it, and Section 5.4
explains why the other candidate, openJiuwen, comes later.

### 5.1 Why the harness matters: it moves pass rates almost as much as the model

![Fig. 8. At a fixed model, harness choice moves pass rates about as much as model choice (Claw-SWE-Bench, 2606.12344 p11-13).](build/fig/fig4-harness.png)

Claw-SWE-Bench (2606.12344) measured how much the harness around a model matters on coding tasks (Fig. 8):

- At a fixed model, the choice of harness moves the pass rate by 27.4 percentage points, against 29.4 points for the
  choice of model at a fixed harness (p1)
- The biggest single lever is the output contract. With the same model, having the model write a diff passes 19.1% of
  tasks, while having the model edit files and the runner export the diff passes 73.4% (p1, p11)

There are three limitations to this result:

- The effect shrinks as the model gets stronger, from 27.4 points on Qwen 3.6-flash to 12.5 on GLM 5.1 (p3)
- It covers coding benchmarks only
- No harness-controlled measurement exists for research work

### 5.2 What dsh is: a plugin harness with no privileged core

dsh is a plugin harness. In its own words, "There is no privileged core to patch: you extend dsh by mounting a plugin
beside the others, and registrations are effects that unwind when their plugin unloads." The model adapter, tool
registry, session log and agent loop are all plugins on a shared context called Cordis. dsh is a developer preview at
version `0.1.5-rc.2`, and 4 of its properties matter for AI4Research:

- Substitutability. A swappable service boundary is made of 3 roles, a service definition, a provider and a consumer,
  and is "complete, never one role"
- Replayability. "Model-visible means logged. Anything that reaches a model request must be reconstructable from the
  log"
- Immutable data. Committed session generations are never renamed or deleted, and a write publishes a version-named
  successor
- Containment. A sandbox service keeps policy separate from mechanism, beside services for approval, authorization and
  credentials

### 5.3 Stage mapping: what dsh provides at each stage, and what AI4Research adds

Table 7 puts each stage of the workflow beside the dsh mechanism that would carry it. Nothing in its third column is
built.

| AI4Research stage | dsh mechanism | What AI4Research would add |
|---|---|---|
| Compiled intent and contract | An agent pre-step; typed session events | The intermediate artifacts and their deterministic validation |
| Freeze | Immutable versioned successors; history derived from the log | The plan hash with the grading rules inside |
| Task graph | Jobs, subagents and agent teams | The frozen graph, write-scope conflicts and the projection check |
| Orchestration | Swappable services in place of the file inbox; a token meter | Logical and physical operator routing as service providers |
| Capsules | A per-tool catalog of required services and written events | Declared effects checked before admission (capsule report) |
| Gates | Invariants and an approval service | Frozen evaluators and the result vocabulary |
| Claims | The session log as an evidence store | Evidence schemas, verdict gates and the unsupported-claims list |
| Security | Sandbox policy and backends | Declared effects, which turn a sandbox policy from a guess into a declaration |

*Table 7. What dsh provides at each stage, and what AI4Research would add.*

Thus, dsh settles loading, swapping, reverting, sandboxing and logging. It does not settle the contract: what a run must
satisfy, what grades it, and what a capability may do.

### 5.4 openJiuwen: the longer-term home for the contract layer, not the runtime

The second decision of 2026-09-11 was to add the contract layer to openJiuwen later rather than port the runtime.
AI4Research carries the openJiuwen name (as openjiuwen-solar) but shares none of its code: 0 imports at `b0bf165f9`.
The 2 systems differ on every axis that the contract layer touches (Table 8).

| | AI4Research | openJiuwen auto_research |
|---|---|---|
| Contract scope | 1 per run, frozen | 1 per round, renegotiated |
| Grading rules | Inside the frozen hash | Host rules in code; paper scoring by a model rubric |
| Adaptation | Bounded repair before the freeze | Every round |
| Code generation | Pre-built runners on the native path | A model coder with retries |
| Claims | Cue-word extraction and verbatim grounding | Host-only numeric claim status against prior papers |

*Table 8. AI4Research and openJiuwen auto_research compared.*

---

## 6. Where this leaves AI4Research: ahead on checking, behind on generating

AI4Research is ahead of the reviewed systems in 3 ways, all of them design properties rather than measured results:

- Sealing the grading rules inside the run's integrity hash, which the survey recommends and no other reviewed system
  implements
- Refusing to raise a claim above insufficient when its text is not found in the cited retained section
- Keeping an honest result vocabulary, in which not-tested and environment-blocked are not failures

It is behind in 3 ways:

- Experiment code on the trusted path covers 1 hand-built family
- Claim extraction is an English-only cue-word rule, cruder than the rule-only baseline of CREDENCE (2606.19819,
  Appendix E.7), with recall unmeasured
- There are no external benchmark results

The lead is a design property, not a result, since Rel(AI)Build (2606.26924) already content-hashes its specification at
approval and Arbor already runs a held-out gate that only its merge tool can open (Appendix E.4 and Section 4.3). Thus, the first external result decides whether the lead holds.

### 6.1 Challenges: 6 open problems, each with what would settle it

The challenges are grouped by area, with the evidence for each and what would settle it.

A. Measurement and judgment

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 1 | Nothing is measured externally | Every strength above is a design property read in source: the 24 journey tests and the 14-node run are internal, and there are 0 benchmark scores. At every risk tier exactly 1 node of the graph gets a model evaluator, and the result vocabulary does not separate the 20 model-judged rubrics from the 23 Python gates (Section 2.6). Claim recall is unmeasured, since the cue-word rule matches by prefix and decomposes nothing, so missed claims never reach the unsupported list (Section 2.7). In DeepFact (2603.05912), PhD-level experts working unassisted judge verifiable claims correctly 60.8% of the time (p5), so human review is no substitute | Running TruthInsightBench end to end on 1 frozen model and reading the 6 dimension scores rather than the total, where an evidence-auditability rate inside the published 78% to 81% band puts the auditability claim with the field rather than ahead of it (Section 3.2); recording the deciding check kind on every verdict and counting, for 1 finished run, how many PASS values a model decided; hand-labeling the claims of 50 paper sections and reporting the cue-word rule's recall against that list |

*Table 9. Challenges in measurement and judgment.*

Every pre-release system lacks an external score, and the internal evidence cannot stand in for one: a graph gets
1 model-evaluated node at any risk tier, and a reader of a delivered report cannot tell which verdicts a model
decided. The work itself is small, since a Terminal-Bench 2.0 adapter already sits in the repository and
TruthInsightBench needs an adapter of the same shape.

B. Claims

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 2 | Claims carry provenance, not truth, and only in English | Without an experiment, the strongest verdict is partially supported at 0.85, the confidence Fig. 6 attaches to a case-insensitive substring match against the cited section. Spans that fail their re-hash are dropped silently, no gate reads the span flag, and the reportable set is filtered on evidence ids rather than verdicts, so claims judged insufficient or not supported become report conclusions and the unsupported list stays empty (Section 2.7). The typed fields between stages are language-neutral, so the English rules sit at 2 boundaries, the request and the papers: negation cues and clause breaks on one side, claim cues, testability patterns and a 30 to 1,000 character length on the other. The repository's own operating documents are in Chinese | Adding a gate that fails a claim whose span fails its re-hash, then replaying the delivery fixture with 1 span edited, where the signal is whether the node fails rather than passing with the span dropped; filtering the reportable set on the verdict and counting how many conclusions 1 finished run loses; reading a delivered report and recording whether the 3 provenance fields reach its prose; running a schema-bound model extractor against a hand-verified claim list per language, reported as precision, recall and unbound-quote rate (Section 6.2) |

*Table 10. Challenges in claim handling.*

The system does say that its verdicts are provenance verdicts, in a limitation, a verification basis and a
per-conclusion evidence status, and those fields are the reason the design is worth keeping. The gap is what a
reader of the output sees: a claim the workflow judged insufficient arrives as a conclusion, the list of unsupported
claims is empty whatever the verdicts were, and no check requires the 3 fields to survive into the rendered prose.
FactReview (2604.04074) shows the alternative inside the same design: a closed set of 4 outcomes in which a claim
whose link to its evidence cannot be established is returned as inconclusive rather than carried forward
(Appendix E.7). Per-language work has started at the relevance gate, where Chinese character pairs were added by
hand, and that is the shape the rest of the rules would have to take.

C. Planning and the freeze

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 3 | The freeze cannot handle what it did not foresee | Intent, requirement, plan graph and capsule selection get 1 repair by default, then the sprint fails, and the requirement and capsule-fit reviewers are advisory from the start, so a meaning error a reviewer found can pass (Sections 2.1 and 2.2). The frozen rules carry no branch for an outcome they did not anticipate: every node but the single model-evaluated one is frozen with an evaluator gate of kind none and 0 repair attempts, and such a node records a policy pass unless a deterministic scientific artifact gate is required for it (Section 2.3) | Freezing a graph, then delivering for a node whose evaluator gate is none an output that validates against its schema and contradicts its acceptance criterion, where the signal is the verdict recorded for that node and the mode it names: a policy pass measures the gap, a failure closes it; declaring halt, inconclusive or human in the test policy and repeating that test; counting resubmitted requests over 20 runs and how many carried an advisory warning before the run failed |
| 4 | A contract is only as good as its compilation, and a wrong plan has no recovery | Plan defects per run are unmeasured, and an open capability such as a shell or SQL routes around typed contracts, the cause of 13 of PlanCompiler's 22 failures (Section 2.3). There is no re-planning: when execution shows the plan was wrong, the run fails and the user resubmits, and a node no capsule fits raises `UNSATISFIABLE_CAPSULE` so the plan fails at the freeze (Section 2.2) | Replaying the 24 journey requests through planning alone at 1 frozen model and counting, per plan, the nodes that raise `UNSATISFIABLE_CAPSULE` and the frozen nodes whose bound capsule cannot produce the artifact the node is asked for, so the signal is defects per plan against the 0 the freeze assumes; keeping the freeze and documenting its cost against Arbor and Kosmos; the generalist capsule proposed in the capsule report (Section 4.1 there) |

*Table 11. Challenges in planning and the freeze.*

A bounded pre-freeze loop is the point of the design, and the advisory reviewers and the single repair are
deliberate. What is not deliberate is what the freeze does with an outcome nobody wrote a rule for: the node closes
as a recorded pass. 13 of 22 is PlanCompiler's number, which bounds the failure mode without measuring this system,
and that missing measurement is the challenge. Resubmission is cheap when a plan fails at the freeze, before any
work runs, and expensive when a plan freezes cleanly and execution shows it was wrong, because the whole run is
discarded.

D. Capsule library. Trust classes, declared versus observed effects, versioning, gap records, protected paths and the 2
type vocabularies are covered in the capsule report (Section 3 there), so this group adds no numbered challenge here.

E. Execution and autonomy

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 5 | Execution is recorded, not observed | On the CLI-agent path, enabled today, only the git worktree bounds the agent: its commands, files and network access are not observed, its evidence is classed `fixture_or_adapter_only`, and untrusted paper text reaches it through that shell (Section 2.5). A node's network rule is spent at planning, filtering which capsules the planner may pick from, and nothing watches the network once the node runs (Section 2.2). Only 21 of 79 capsule manifests declare a trust class at all. The coordinator substrate of tmux keystroke injection, file inboxes and SQLite, which the move to dsh replaces, produced failures of its own: 1 coordinator ran code 28 hours older than the file on disk, and a run manifest recorded the statuses a model declared (Section 2.4) | Running 1 experiment node on the adapter path with an outbound request placed in the runner and reading every artifact the run retains, where the signal is whether any of them shows the call; the move to dsh, whose sandbox service and session log make that access recordable (Section 5); model-written runners under hash-and-approve on the native path |
| 6 | Unattended runs do not finish | 3 logged runs stopped at literature discovery after Semantic Scholar returned HTTP 429, each from a different cause, and the first 2 causes are fixed. The third was a prompt-only rerun: the provider failure was retryable, and the frozen policy of 1 attempt and then failing the run ended the sprint and cancelled 13 downstream nodes, because no hash-bound local source was declared to continue on. The run that finished without intervention did so only with 6 PDFs attached, and an experiment that is not a fixture waits for a hash-bound approval, so an unattended run must defer any plan that needs one (Section 2.8) | An unattended journey test from a prompt with no attachments and a fallback to hash-bound local sources declared in the frozen contract, where the signal is that the run reaches closure and delivery states the source coverage it used; the same prompt with the provider forced to return HTTP 429, where the signal is whether the run continues on local sources or cancels its downstream nodes |

*Table 12. Challenges in execution and autonomy.*

The coordinator incidents belong to a substrate the move to dsh replaces, and the row separates them from the live
part, the CLI-agent path that research nodes use today. An HTTP 429 is not answered by a retry alone: the provider
failure was already marked retryable, and the frozen failure policy of 1 attempt ended the run, so loosening that
policy would let a run continue with no evidence behind it. The fallback has to be a hash-bound local source declared
inside the contract.

### 6.2 Directions (proposed): the next step each challenge points to

The directions below follow from the challenges, and none is built yet:

- Moving the workflow onto dsh, keeping the contract layer as the contribution, and offering it to openJiuwen later
  (challenge 5)
- Having a model write experiment runners under hash-and-approve (challenge 5)
- Counting plan defects per run before deciding whether the freeze keeps its cost (challenge 4)
- Adding a schema-bound model extractor at both text boundaries, in which every typed field carries a verbatim quote
  in the source language that code binds to offsets and hashes, so no translated text becomes evidence (challenges 1
  and 2)
- Keeping deterministic checks after the extractor, and adding a gate that fails unverified spans, each tested per
  language against a hand-verified claim list (challenge 2)
- Declaring in the test policy what a node does when its frozen rules do not cover the outcome it received, so that a
  node with no evaluator gate halts, returns inconclusive or asks a person rather than recording a policy pass
  (challenge 3)
- Recording on every verdict which kind of check decided it, so that a rubric PASS and a Python-gate PASS are
  distinguishable in results and in the delivered report (challenge 1)
- Declaring a local-source fallback for retrieval nodes, hash-bound inside the frozen contract, with the coverage it
  used stated in delivery (challenge 6)
- Running 1 external benchmark end to end before making any comparative claim (challenge 1)

## 7. Open questions: 2 decisions taken, 3 decisions waiting

Every row of Table 13 names the decision it asks for, so a reader can act on it rather than agree with it.

| # | Question | The decision it asks for | Owner |
|---|---|---|---|
| Q-G1 | Which platform the workflow runs on | Taken: the DeepSeek Harness for now, as the more certain of the 2 candidates (Section 5) | presenter |
| Q-G2 | Whether to port the runtime to openJiuwen or add the contract layer to it later | Taken: add the layer later, and keep the workflow on the DeepSeek Harness (Section 5.4) | presenter |
| Q-G3 | Whether openJiuwen's auto_research is named as the closest comparison | Approve naming it in anything that leaves the team, or refuse and let Arbor stand as the closest comparison on checking (Sections 4.3 and 4.4) | supervisor |
| Q-G4 | Which external benchmark comes before circulating | Approve TruthInsightBench and the adapter work it needs, or name a benchmark the existing Terminal-Bench 2.0 adapter already reaches, and set the date it runs (Section 3.2) | supervisor |
| Q-G5 | Who owns each challenge, and in what order they are taken | Assign challenges 1 and 4 for the next cycle, since both are measurements rather than builds and both gate the comparative claims (Section 6.1) | supervisor |

*Table 13. Open questions, the decision each asks for, and its owner.*

Q-G4 unblocks the most, since every comparative claim in Sections 4 and 6 rests on a design property until an external
result exists.

---

\pagebreak

## Appendix A. Sources

AI4Research at `b0bf165f9`: `harness/lib/intent_gateway.py`, `intent_compiler.py`, `requirement_compiler/`,
`elastic_planner.py`, `apo_plan_compiler.py`, `execution_authority.py`, `graph_node_dispatcher.py`,
`graph_scheduler.py`, `contract_gate_executor.py`, `harness/tools/research_operator_registry_adapter.py`,
`harness/plugins/autosci/operators/scientific_lifecycle/evidence/operators.py`, `…/action/delivery.py`,
`harness/evaluators/scientific/claim_verdict_gate.py`, `harness/config/evaluation-checks.v1.json`,
`physical-operators.json`, `logical-operators.json`, `capability-capsules.registry.yaml`,
`harness/capability-capsules/cap.research-experiment-run.yaml`,
`harness/metadata/pre-scheduler-stabilization-log-20260829.md`, `harness/BUG5-ROOT-CAUSE.md`,
`docs/integrations/autosci/phase-22-journey-test-report.md`, `tests/harness/test_elastic_planner.py`,
`tests/plugins/autosci/scientific_lifecycle_action_operators/test_action_delivery_operators.py`. DeepSeek Harness at
`c291e7961a`: `docs/architecture.md`, `AGENTS.md`. openJiuwen: `agent-core@6ecf8218`. The companion report cited as the
capsule report is "Capability Capsule in AI4Research", draft of 14 September 2026.

18 sources were read in full, and each is used for 1 job (Table A1).

| Role | Source | Used for |
|---|---|---|
| Reference system | 2504.08066 AI Scientist-v2 | Generation-first design; 57% overlap missed by review |
| Reference system | 2511.02824 Kosmos | Scale; 79.4% and 57.9% statement accuracy |
| Reference system | 2606.11926 Arbor | Held-out merge gate enforced by the merge tool; 77.36 against 71.70 |
| Reference system | openJiuwen auto_research (source code, no paper) | Per-round contract |
| Considered, not compared | 2502.18864 Co-Scientist, 2505.13400 Robin, 2501.04227 Agent Laboratory, 2606.15497 Towards End-to-End Automation of AI Research | Why the comparator set is these 4 systems |
| Mechanism | 2604.13092 PlanCompiler | Typed plan compilation; 44/50 against 20/50; constraint evasion |
| Mechanism | 2503.18813 CaMeL | Control flow fixed before data; 77% against 84% |
| Mechanism | 2606.26924 Rel(AI)Build | Specification hashed; test linkage cooperative |
| Mechanism | 2606.19819 CREDENCE | Price of rule-based extraction, 0.811 against 0.88 to 0.91 |
| Mechanism | 2604.04074 FactReview | Closest verdict design; 79.7% recall; 17.0% |
| Measurement | 2608.05179 verification-gap survey | Ladder rungs; pre-committed specification |
| Measurement | 2411.14199 OpenScholar | 78% to 90% fabricated citations |
| Measurement | 2603.05912 DeepFact | 27.0% unsupported; experts 60.8%; 83.4% |
| Measurement | 2606.12344 Claw-SWE-Bench | Harness 27.4 against model 29.4 points; 19.1% against 73.4% |
| Benchmark | 2609.05079 TruthInsightBench | 40 blind tasks over 6 dimensions; 58.4 to 60.3 plateau |

*Table A1. The 18 sources read in full, and what each is used for.*

## Appendix B. Questions a reviewer will ask

| Question | Answer | Section |
|---|---|---|
| Does it verify claims? | Without an experiment, no. It certifies that the sentence occurs in the cited section (partially supported, 0.85) and records that limitation | 2.7 |
| Is the span hash enforced? | Spans are re-hashed and filtered, but no gate fails a claim whose span fails. A gate on the span flag is proposed | 2.7 |
| Does a model decide anything after the freeze? | Not scheduling, routing or admission. Models execute inside capsules, and 20 of 43 registered checks are model-judged rubrics | 2.4, 2.6 |
| Can the model overrule a rejection? | No. A fidelity objection is demoted to a warning once the 1-repair budget is spent, by design, so a review model never becomes a second admission gate | 2.1 |
| What happens when no capsule fits? | `UNSATISFIABLE_CAPSULE`, and the plan fails at the freeze. There is no generalist fallback today, and the capsule report proposes a generalist capsule | 2.2 |
| Does an LLM write experiment code? | Yes, on the adapter path through `codex exec`, classed `fixture_or_adapter_only`. The trusted path has 1 hand-written family | 2.8 |
| Is there any external benchmark? | None. TruthInsightBench comes first, reported per dimension | 3.2 |
| Does any other system seal its grading rules inside the run hash? | None of the reviewed systems does, after a targeted search on 2026-09-13. Rel(AI)Build hashes its specification, but its test linkage is cooperative and checked after the fact | 2.3 |
| Does the hash stop tampering? | No. It detects an edit after the fact, wherever something recomputes it, and it authenticates no author | 2.3 |
| What does the freeze cost? | No re-planning when execution shows the plan was wrong, and search only inside operators. It fits execution and grading, not exploration | 2.3 |
| Is the frozen chain fully recomputed? | 3 stages are recomputed, and the rest are compared by hash | 2.3 |
| What happens when a frozen rule is undefined on the outcome? | The node closes as a recorded policy pass. At every risk tier 1 node of the graph carries a model evaluator, every other node is frozen with an evaluator gate of kind none, and such a node passes on its proof obligations and artifact schema alone. A halt, inconclusive or human policy in the test policy is proposed | 2.3, 6.1 |
| Every pre-release system lacks an external score. Why does it matter here? | Because the argument is a design comparison, so until 1 external result exists no quantity can be set beside Arbor or Kosmos. The internal evidence cannot stand in: a graph gets 1 model-evaluated node, and a report reader cannot tell which verdicts a model decided | 6.1, 2.6 |
| Provenance rather than truth is deliberate. Where is the problem? | In what the output shows. A claim judged insufficient arrives as a conclusion, the unsupported-claims list is empty whatever the verdicts were, and no check requires the 3 provenance fields to reach the rendered prose. FactReview returns such a claim as inconclusive instead | 2.7, 6.1, E.7 |
| Bounded repair and advisory reviewers are by design. What is left? | The default evaluator gate. A node outside the single evaluated node is frozen with no evaluator gate and 0 repair attempts, so an outcome nobody wrote a rule for closes as a pass | 2.3, 6.1 |
| 13 of 22 is PlanCompiler's number. Why does it count here? | It bounds the failure mode without measuring this system, and that missing measurement is the challenge. Plan defects per run are counted by nobody today | 2.3, 6.1 |
| The stale coordinator is an old incident. Is that challenge still live? | The dated incidents belong to the coordinator substrate the move to dsh replaces. The live part is the CLI-agent path used today, whose network rule is spent on filtering capsules at planning and observed nowhere at run time | 2.2, 2.5, 6.1 |
| HTTP 429 is a provider flake. Why not retry? | The provider failure was marked retryable; the frozen policy of 1 attempt ended the run and cancelled 13 downstream nodes. Loosening that policy alone would let a run continue with no evidence behind it, so the fallback has to be a hash-bound local source declared in the contract | 6.1 |
| Why move platforms? | Harness choice moves pass rates by 27.4 points at a fixed model, and the current substrate produced a coordinator running 28-hour-old code | 5.1 |
| Why not openJiuwen now? | No code is shared today, and its auto_research renegotiates its contract every round. The decision is to contribute the layer later | 5.4 |
| Is the 1-sentence design rule measured? | No. It is a translated target statement from a Chinese source | 1 |
| What does a run cost, and which models does it use? | No source records the token cost, money or wall-clock time of a sprint, and no model is named for AI4Research anywhere in this report. 102 physical operators are defined and 63 enabled | 1, 3.1 |

*Table B1. Questions a reviewer is likely to ask, with short answers.*

## Appendix C. Code locations

Every location is in AI4Research at `b0bf165f9` unless stated, with paths under `harness/lib/` unless a directory is
given. "Log" means `harness/metadata/pre-scheduler-stabilization-log-20260829.md`.

| Section | Claim | Location |
|---|---|---|
| 1 | Target design sentence | `NEW-MACHINE-START-HERE.md:21` |
| 2.1 | Intent pipeline; validation; acceptance | `intent_compiler.py`: `run_pipeline` :1368, `validate_intent` :782, `decide_acceptance` :1272 |
| 2.1 | Expression language; quote binding; repair budget; fidelity demotion | `intent_compiler.py`: `_OPERATOR_CONTRACTS` :636, `_bind_exact_source_quotes` :477, `SOLAR_INTENT_MAX_REPAIRS` :210-217, `_demote_exhausted_fidelity_findings` :1230-1265 |
| 2.1 | Refusal checked twice | `intent_gateway.py`: `capture()` :976, `requirement_handoff()` :1508 |
| 2.1 | Fidelity example ("only these 5") | Log l.793 |
| 2.1 | Template enums; semantic defects; checks registry | `requirement_compiler/template_contract.py:55`, `requirement_compiler/semantic.py:47`, `harness/config/evaluation-checks.v1.json` |
| 2.2 | Catalog snapshot; planning decision; plan validation | `elastic_planner.py`: :616, :829, `validate_plan_ir` :2696 |
| 2.2 | Hard filter; selection; its validation; fit review; composition; node binding | `elastic_planner.py`: :4553, :4727, :4815, :5685, :5544, :6270-6320 |
| 2.2 | Same-model review record; physical plan; unsatisfiable node fails the plan; CLI coding capsules | `elastic_planner.py:482`, `:7067-7080`; `apo_plan_compiler.py:1192`, `:626`; `capability_capsules.py:1145-1180` |
| 2.2 | The node's network rule filters capsules at planning | `elastic_planner.py:4577-4581` |
| 2.3 | Freeze order; scheduler input; live definitions | `elastic_planner.py`: `compile_and_freeze_execution_bundle` :6888, `compile_scheduler_input` :6662; `execution_authority.py:81-91` |
| 2.3 | Grading rules written into the scheduler input; canonical hash | `elastic_planner.py:6802-6842`; `intent_compiler.py:62-67` |
| 2.3 | Verification and its 3 recomputed stages | `elastic_planner.py`: `verify_frozen_execution_chain` :7748-8052, stages :7871-7884, :7919-7929, :7930-7951 |
| 2.3 | Tamper test; failure handling | `tests/harness/test_elastic_planner.py:4697-4718`; `elastic_planner_runtime.py:262-310` |
| 2.3 | Semantic budget: 1 model-evaluator node per graph at every risk tier; every other node frozen with an evaluator gate of kind none and 0 repair attempts | `evaluation_budget.py`: `_RISK_BUDGETS` :22, `select_semantic_targets` :153-172, :228-231 |
| 2.4 | Dispatch tick; reconciling dispatches | `graph_node_dispatcher.py`: `_dispatch_ready_unlocked` :16772, `_reconcile_existing_dispatches` :5774 |
| 2.4 | Ready set, assignment, admission | `graph_scheduler.py`: `enqueue_ready` :4100, `assign_ready` :3131 and :3200-3209, `node_admission_status` :2103, `topo_order` :2008, `ready_nodes` :2179 |
| 2.4 | Write conflicts; monotonic progress; skipped dependents; human review; statuses | `graph_scheduler.py`: `write_scope_conflict` :2237, `mark_node_result` :3736, `terminalize_dependency_blocked_nodes` :3979, :3633, :48-53 |
| 2.4 | Projection check; ledger | `scheduler_input.py:849`; `task_graph_state.json` |
| 2.4 | Stale coordinator code; model-declared statuses | `harness/BUG5-ROOT-CAUSE.md:38`; log l.786-787 |
| 2.5 | Registry path checks; CLI-agent path | `harness/tools/research_operator_registry_adapter.py`: `_verified_dispatch_authority` :268, `_validated_binding` :357; `multi_task_runner.py` |
| 2.5 | Request channel and sender; files seen at planning | `intent_compiler.py:386-400`; `elastic_planner.py:1389-1392` |
| 2.5 | Experiment adapter operator: enabled, `execution_trust: fixture_or_adapter_only`, `network: forbidden` | `harness/config/physical-operators.json`, `autosci-exec-experiment-run-worker` |
| 2.6 | Gate kinds; code-task verification | `contract_gate_executor.py`; `verification_gate.py:13` |
| 2.6 | A node whose evaluator gate is none records a policy pass unless a deterministic scientific artifact gate is required | `contract_gate_executor.py`: `execute_gate` :187, :209, :236-238, :263-266 |
| 2.7 | Extraction; cue words; testability; length; evidence id; error | `…/evidence/operators.py`: :1180-1265, :1183, :1224, :1206, :1226, :1264 |
| 2.7 | Verdict table; substring match; span re-verification; span flag | `…/action/delivery.py`: :133-166 (0.85 at :155), :137, :115-132, :201 |
| 2.7 | Reportable set, and the unsupported list built from its complement | `delivery.py`: `_grounded_evidence_ids` :256-261, :667-670, :2059 |
| 2.7 | Verdict gate; reportable set; evidence id kept; limitation and basis; conclusion fields | `harness/evaluators/scientific/claim_verdict_gate.py:29-69`; `delivery.py`: :667-670, :2059, :167-172, :175-178, :220, :2084-2085 |
| 2.7 | Claim example | `tests/plugins/autosci/scientific_lifecycle_action_operators/test_action_delivery_operators.py:689-742` |
| 2.8 | Experiment capsule; hand-written runner | `harness/capability-capsules/cap.research-experiment-run.yaml`; `kv_cache_quantization_runner.py` |
| 2.8 | 21 of the 79 capsule manifests declare a trust class | 79 `cap.*.yaml` under `harness/capability-capsules/` (39) and `harness/config/capability-capsules/` (40) |
| 3.1 | 14-node run; regression; journey report | Log l.793-796, l.862; `docs/integrations/autosci/phase-22-journey-test-report.md:65` |
| 3.1 | 24 journey rows | `docs/integrations/autosci/phase-22-journey-test-report.md`, rows P22-J01 to P22-J24 |
| 3.1 | Terminal-Bench 2.0 adapter exists; no scores recorded | `harness/lib/benchmark/terminal_bench.py`; `harness/docs/benchmark/terminal-bench-2.md` |
| 4.4 | Module chain; standalone scoring | agent-core at `6ecf8218`, under `openjiuwen/rsi/artifact_rsi/paper_opt/`: `auto_research/modules/manager/schemas.py:26-33`; `auto_research/modules/reporting/latex.py`; `auto_research/modules/paper_scoring/scorer.py:49` |
| 4.4 | 1 decision per round; its 3 signals | `auto_research/modules/manager/schemas.py:22`; `auto_research/extensions/tools/submit_manager_decision.py:14`, `:69` |
| 4.4 | Illegal-move checks: execution without a ready implementation; re-execution before repair; done while pending | `auto_research/pipeline/transitions.py:427`, `:458`, `:602` with `:614` |
| 4.4 | Budgets (shipped config; code defaults at `modules/manager/schemas.py:156-161`) | `configs/pipeline.default.yaml:28`, `:30`, `:31`, `:32` |
| 4.4 | Claim status, host-only, no model; prior-paper source; never called | `auto_research/modules/reporting/evidence.py:150`, `:153-156`, `:24`; no caller in the repo |
| 4.4 | Dual rubric, 5 samples, temperature 0 | `auto_research/modules/paper_scoring/scorer.py:49`, `:169`, `:177`, `:197`; `configs/pipeline.default.yaml:196-197` |
| 4.4 | No published evaluation | No results, benchmark or evaluation document under `paper_opt/` |
| 5.2 | Plugin quote; replayability quote; service roles | dsh at `c291e7961a`: `docs/architecture.md:13`, `:121`; `AGENTS.md:113` |
| 5.2 | Developer preview; version `0.1.5-rc.2` | dsh at `c291e7961a`: `README.md:11-13`; `apps/cli/package.json:4` |
| 6.1 #2 | English rules in intent and papers | `intent_gateway.py:240`, `:246-251`; `operators.py:1183`, `:1224`, `:1206`, `:1380-1390`; `delivery.py:995-1011`, `:1648`; `autosci_bridge.py:12875-12885` |
| 6.1 #6 | Semantic Scholar stops; the retryable failure meeting a frozen 1-attempt policy; PDFs attached | Log l.327, l.662, l.814, l.815; fix at `research_operator_registry_adapter.py:795-806` |

*Table C1. The code location behind each code claim.*

## Appendix D. Code excerpts

The compiler writes the grading rules into the scheduler input, so they are inside the frozen hash (Section 2.3):

{{excerpt:sched_code|Listing 1. The compiler writes the grading rules into the hashed SchedulerInput (`harness/lib/elastic_planner.py`).}}

A real node from a test fixture carries the bound capsule's contract hash and its evaluators:

{{excerpt:sched_node|Listing 2. 1 node of a 2-node SchedulerInput (`tests/harness/fixtures/scheduler-input-live-two-node.json`, hash shortened). This fixture does not carry the later `evaluator_gate` and `test_policy` fields.}}

The tamper test edits a frozen bundle and expects verification to fail (Section 2.3):

{{excerpt:tamper_test|Listing 3. The tamper test (`tests/harness/test_elastic_planner.py:4697-4705`).}}

## Appendix E. Workflow details

### E.1 Compiled intent

The first stage produces 4 artifacts, and each has a different author (Table E1).

| Artifact | Question it answers | Author |
|---|---|---|
| IntentIR | What was asked? | A model |
| Validation | Is it structurally sound? | Deterministic code, with 7 kinds of check |
| Fidelity review | Does it reflect the request? | A second, independent model call |
| Acceptance | May the run proceed? | A deterministic gate |

*Table E1. The artifacts of the intent stage.*

The IntentIR records 6 things:

- The goals
- The outcomes, each typed as information, an artifact or an action
- The constraints, each with a category, a statement and a machine-readable expression
- The ambiguities, each marked as blocking or not
- The conflicts, each marked for clarification or rejection
- The unknowns

Besides binding quotes and bounding repair (Section 2.1), code keeps the model in check in 2 more ways:

- Limiting the expression language to 21 operators with a fixed arity and shape. There is no subset-of operator and no
  universal quantifier, so a relation the language cannot express stays a literal string
- Checking a refusal twice. The intake stops the pipeline, and the handoff to the requirement stage re-verifies the
  decision id and its SHA-256 hash

The stage ends in 1 of 3 outcomes: accepted, needs clarification, where a blocking ambiguity or conflict goes back to
the user, or failed.

### E.2 Requirement contract

The model fills in the requirements, assumptions, discovery plan, selection authority and delivery manifest. Each
requirement row carries 4 fields:

- A priority: must, should or may
- An acceptance rule, with its kind and required values
- A check, named by its id in the checks registry
- A semantic role: research scope, process, delivery, outcome, resolution or constraint

Deterministic code then looks for defects, including 3 kinds:

- A changed constraint. Intent constraints must be copied byte for byte, so a model that flips "must not" to "must" is
  caught as `SOURCE_CONSTRAINT_POLARITY_OR_CATEGORY_CHANGED`
- Missing coverage. Every Intent id must be referenced by some requirement, or the contract fails as
  `SOURCE_COVERAGE_MISMATCH`
- An unknown check, together with rules on named-file checks, roles and coverage

The stage makes at most 3 model calls and 1 structural repair. A requirement reviewer comments on the contract, but its
comments are advisory, and the admission authority is recorded as deterministic contract validation. The checks
registry holds 2 kinds of check (Table E2).

| Kind | Count | Applies to | Decided by |
|---|---|---|---|
| Deterministic | 23 | An artifact type, applied automatically | A Python gate |
| Semantic | 20 | An output that a requirement names | A rubric, judged by a model |

*Table E2. The 2 kinds of registered check.*

### E.3 Plan and capsule binding

The plan is built in 8 steps:

1. Catalog snapshot. Code takes a snapshot of the workflows, logical operators, capsule summaries and enabled
   physical operators and hashes it, so the plan records exactly what it was allowed to choose from
2. Planning decision. The planner chooses between a direct response, exact reuse of a known workflow, or a new plan
3. Plan graph. The model lists the nodes and the dependencies of each, and the edges of the graph are exactly that
   list. Code rejects unknown dependencies, self-dependencies, cycles, a node that reads an artifact whose producer is
   not an ancestor, requirements no node covers, and more than 1 model-evaluator node. 1 repair is allowed, and a
   second failure fails the sprint
4. Hard capsule filter. Before any model sees the candidates, code excludes capsules on 13 codes
5. Selection. The model picks only among the capsules that survived the filter, and code derives the dispatch type and
   validates the choice on 8 codes. A second model reviews the fit, but a failed review only produces a warning. 1
   repair is allowed
6. Composition. When no single capsule fits, capsules may be chained, but only through registered adapters
7. Node binding. The capsule id, proof obligations, artifact types, effect union and approved physical operators are
   copied from the manifest, never from the model
8. Physical plan. Each node receives frozen execution candidates, excluding operators with the wrong role or task
   class, operators the capsule forbids, and providers that are unauthenticated or not idle

### E.4 The freeze

The freeze runs in 8 steps of deterministic code, and any step can fail the sprint:

1. The evaluation budget becomes a test policy, which sets the risk tier and the number of model-evaluator nodes, 1 or,
   for a rapid smoke run, 0
2. The capsule plan and the physical plan are validated with their adapters and merged into 1 graph
3. The plan is validated and stamped with a certificate
4. The evaluation plan is compiled and validated
5. The scheduler input, meaning the exact graph the scheduler will run, is compiled
6. The live capsule definitions are checked, and if any definition changed during planning, the freeze aborts with
   `CAPSULE_CHANGED_DURING_PLANNING`. The same check on operator definitions aborts with
   `OPERATOR_CHANGED_DURING_PLANNING`
7. The frozen run contract is written with a reference to every upstream artifact and sealed with its own hash
8. The plan is accepted and handed to the runtime

An existing test tampers with a frozen bundle in 3 ways, and verification catches each one (Table E3).

| Tamper | Caught by | Error |
|---|---|---|
| Set a node's priority to 999 in the scheduler input | Recompute | `scheduler_input.recomputed_mismatch` |
| Edit the acceptance criteria in the evaluation plan | Reference hash | `frozen.evaluation_plan_ref.hash_mismatch` |
| Edit the rationale in the composition selection | Reference hash | `frozen.composition_selection_ref.hash_mismatch` |

*Table E3. The 3 tampers the existing test applies, and how verification catches each.*

Plan nodes also have no half-bound state: a selected node must carry its capsule, dispatch type, role, artifact types,
effect union and proof obligations, and an unselected node must be marked unsatisfiable with no stages.

Other work fixes parts of a run before execution, but none fixes the grading rules with the plan (Table E4).

| Family | Example | Fixed before execution | Not fixed |
|---|---|---|---|
| Plan-then-execute security | CaMeL (2503.18813) | Control flow, before untrusted data is read; 77% of AgentDojo tasks solved with provable security against 84% undefended (p1) | Success criteria |
| Compiled pipelines | PlanCompiler (2604.13092) | A statically validated typed graph | Evaluation policy |
| Deterministic control planes | Rel(AI)Build (2606.26924) | The specification, content-hashed at approval, plus install gates, blocklists and phase transitions | Which files and tests satisfy each criterion, which the agent declares during implementation, "cooperative and auditable post-hoc, not pre-execution enforced" (p1, p20) |
| Research agents | AI Scientist-v2, Kosmos, Arbor, openJiuwen auto_research | Nothing global; plans evolve every cycle or round | The plan and the rules that grade it |

*Table E4. What other work fixes before execution.*

### E.5 Dispatch

1 tick of the dispatcher takes 6 steps (Fig. E1):

1. Taking the graph lock, and stopping if the runtime handoff is forbidden or a guard fails
2. Reconciling the dispatches of earlier ticks
3. Applying the approval gate and the terminal barrier, which closes a finished sprint
4. Verifying the runtime projection, meaning that every frozen field of the runtime graph still matches the contract,
   and computing the set of ready nodes
5. Admitting and leasing the selected nodes, and writing a work envelope into each operator's inbox
6. Saving the ledger with its revision increased by 1

![Fig. E1. 1 dispatch tick around the ledger, the only mutable state.](build/fig/fig-tick.png)

The rules a tick enforces are fixed for the whole run (Table E5).

| Mechanism | Rule |
|---|---|
| Scheduling | Kahn topological order; a cycle is an error |
| Write safety | Nodes with overlapping declared write scopes never run together, and a node that declares no write scope is treated as an exclusive writer |
| Projection check | Every frozen field is compared with the runtime node, and only keys on a 54-name allowlist may change |
| Failure | A failed evaluation leads to repair with the findings, up to the repair budget, and then to stopping the node or failing the run; dependents are skipped |
| Monotonic progress | A passed node never regresses |
| Paid work | Work envelopes are fingerprinted, so a retry never repeats a paid call |
| Evidence | A receipt is not evidence; a node closes only on the chain of result, callback and an evaluator PASS |

*Table E5. The dispatch mechanisms and their rules.*

Node statuses fall into 3 groups, plus a separate status for nodes that need human review. Ready statuses are pending,
queued, blocked, worker-blocked and failed review. Active statuses are assigned, dispatched, in progress, running and
reviewing. Terminal statuses are passed, failed, skipped, cancelled, and skipped because a parent passed.

### E.6 Operator execution paths

The 2 paths carry the same node contract and differ most in what is observed (Table E6).

| | Registry path | CLI-agent path |
|---|---|---|
| Before running | Code re-verifies the graph projection, that the operator is among the frozen candidates, the exact artifact contract, the routes, the capsule binding and the write scope, and checks the registry, node kind and implementation against an allowlist | The agent receives a tmux pane in a git worktree, the dispatch text and injected research rules |
| Model calls | The request, schema, response, events and hashes of each call are kept | Whatever the CLI agent does |
| Output | A typed result file, always | The exit code, converted into a result file |
| Observed | Inputs, outputs and model calls | Nothing: commands, files and network access are not observed |
| Trust class | Set per capsule | `fixture_or_adapter_only` |

*Table E6. The 2 operator paths compared.*

### E.7 Claim handling compared with published work

2 published systems show the price of this design and the nearest alternative:

- CREDENCE (2606.19819) prices rule-based extraction. Its rule-only baseline, spaCy sentence segmentation, reaches 0.811
  Semantic-F1 against 0.88 to 0.91 for model decomposition, loses no entities, and leaves atomicity violations near
  their maximum at 0.52 to 0.56, because "rule-based splitting cannot resolve complex multi-clause structures"
  (p22-23). AI4Research's cue-word rule is cruder than that baseline
- FactReview (2604.04074) is the closest verdict design, with a closed set of 4 outcomes, supported, partially
  supported, in conflict and inconclusive, and an inconclusive verdict whenever the link between claim and evidence
  cannot be established (p2). It extracts claims with a model, at 79.7% recall and 84.3% F1 (p5), and removing execution
  evidence changes 17.0% of claim statuses, more than removing any other source (p1, p6)

Grounding matters because ungrounded claims are common, and human checking is a weak fallback (Fig. E2):

- OpenScholar (2411.14199) reports that GPT-4o fabricates citations 78% to 90% of the time without retrieval (p1)
- DeepFact (2603.05912) finds that 27.0% of claims in deep-research reports are unsupported (p8)
- In DeepFact, PhD-level experts working unassisted judge verifiable claims correctly 60.8% of the time (p5), while the
  best automated checker reaches 83.4% and earlier fact-checking pipelines at most 58.5% (p9)

![Fig. E2. Red, hatched: measured failure rates. Open: measured checker and extractor capability.](build/fig/fig3-citation-failures.png)

### E.8 Testing layers

AI4Research separates 3 layers of testing, and only 1 decides acceptance (Table E7).

| Layer | Content | Authority |
|---|---|---|
| Journey tests | 24 real tasks run through the production entry points | The only acceptance evidence |
| Regression suites | The existing tests | Locate faults, never decide the verdict |
| Atomic matrix | 1,502 reviewed rows over 142 Level-2 features | Diagnostic |

*Table E7. The 3 layers of testing.*
