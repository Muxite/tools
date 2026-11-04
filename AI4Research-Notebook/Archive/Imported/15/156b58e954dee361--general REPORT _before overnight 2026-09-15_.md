# AI4Research: Workflow, State of the Art, and the Target Platform

Draft v0.6 · 14 September 2026

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
| capsule | A contract for 1 capability, written in YAML: its typed inputs and outputs, its effects on the system, its preconditions, postconditions and invariants, and how it is verified. The registry holds 80 entries (77 capabilities, 1 guard and 2 resources), and 74 of the 79 capsule manifests are registered |
| operator | Whatever executes a step. A logical operator is an abstract role with graded requirements, such as architecture reasoning at level 4, and 45 are defined. A physical operator is a concrete executor, such as a model endpoint, a CLI agent or a tool, and 102 are defined, of which 63 are enabled |
| sprint | 1 request carried from compiled intent to closure |
| node | 1 step of a sprint's task graph |
| gate | A check that decides PASS or FAIL for the output of 1 node |
| freeze | The point at which the plan, its capability bindings and its grading rules are hashed into 1 run contract |

*Table 1. The 6 terms the report rests on.*

A research run produces schema-validated evidence artifacts rather than free prose. Section 3 summarizes the run and
test evidence so far.

---

## 2. The workflow: models propose, code checks, and the freeze fixes the rules

A request passes through the stages in Fig. 1, and the freeze divides them in 2. Before the freeze, a model proposes
each artifact, meaning the compiled intent, the requirement contract and the plan, and deterministic code checks it.
At the freeze, code hashes the plan, its capsule bindings and its grading rules into 1 run contract. After the
freeze, no model schedules work, routes it to an operator or admits a result. Models still run inside capsules as
operators and judge inside rubric gates, but the order of work, the choice of operators and the rules that decide
PASS are all fixed.

![Fig. 1. The workflow. Above the freeze, every model call is followed by code that checks it; below it, a frozen contract is executed. Tinted boxes are model calls, white boxes deterministic code, and colour marks the stage.](build/fig/fig-workflow.png)

Each subsection below follows the same order: what the stage does, how code keeps the model in check, the nearest
published work where one exists, and the limits of the stage. Appendix E gives the detail of each stage.

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

Research agents such as AI Scientist-v2 and Kosmos take a topic straight into an agent loop and leave no typed artifact
that a later stage can check against. The closest published design is PlanCompiler (2604.13092), in which the model
only selects typed nodes from a closed registry and static checks validate the resulting graph. It scores 44 of 50 on
schema-trap tasks, against 20 of 50 for GPT-4.1 and 26 of 50 for Claude (p1), but it has not been applied to research
workflows.

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
capsules that wrap frontier CLI agents by default, and composition through registered adapters. The capsule report
proposes a generalist capsule for exactly these nodes.

There are two limitations to this stage:

- Capsules that call models are opaque at planning. The planner sees only their trust class, reasoning class and list
  of operators, not the prompt or its behavior
- The fit reviewer is advisory and may be the same model as the planner, in which case the record states that the
  review was a second pass by the same model

### 2.3 The freeze: the plan and its grading rules are hashed before anything runs

The freeze turns the negotiated plan into a contract. It runs in 8 steps of deterministic code (Appendix E.4), and any
step can fail the sprint. The evaluation budget becomes a test policy first, so the grading rules exist before
anything is sealed, and if any capsule definition changed during planning, the freeze aborts with
`CAPSULE_CHANGED_DURING_PLANNING`.

![Fig. 3. The freeze chain. Each artifact is hashed and linked by reference; thick borders are hashed with the grading rules inside them.](build/fig/fig-freeze.png)

The grading rules are inside the hash. The compiler writes each node's evaluator bindings and the run's test policy
into the scheduler input itself (Appendix D), and the hash is SHA-256 over canonical JSON with sorted keys and no
whitespace. If the grading rules sat outside the hash, a run could be judged by rules chosen after its outputs were
seen. Inside it, changing what counts as success changes the hash, and the run no longer matches its contract.

Verification recomputes 3 stages, the composition-selection validation, the evaluation-plan validation and the
scheduler-input compile, and compares the hashes of everything else. An existing test sets a node's priority to 999
in a frozen bundle, and verification fails even though the stored verdict still says PASS; edited acceptance criteria
and an edited composition rationale fail the same way (Appendix E.4). When the freeze fails, the plan is marked failed
with its reasons, partial artifacts and a failure receipt are kept, and the sprint ends. There is no re-planning, so
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
- Fitting execution and grading well and open-ended exploration poorly, where Arbor and Kosmos re-plan every cycle
  (Section 4)

There are four limitations to the freeze:

- A frozen contract is only as good as its compilation, and plan defects per run are not measured
- An open capability, such as a shell or SQL, routes around typed contracts. PlanCompiler calls this "constraint
  evasion under partial enforcement" (p3), and it causes 13 of its 22 failures (p17)
- A frozen evaluator that is undefined on the outcome it receives has no defined behavior. The proposed fix is a policy
  declared in the test policy: halt, return inconclusive, or ask a human
- Any change to a capsule definition during planning aborts the freeze, so a library that keeps changing would race
  every plan

### 2.4 Dispatch: a failure stays contained, and gates never move

Execution is tick-based. The scheduler does not plan everything and then run it; it repeatedly picks the nodes that are
ready and dispatches them. The frozen contract is projected into a runtime graph, a separate ledger holds everything
that changes during the run, and every step of a tick is deterministic code (Appendix E.5).

Fig. 4 follows an illustrative graph of 7 nodes through 4 ticks. For every node, the freeze fixes the bound capsule
and its contract hash, the operator candidates, the evaluator gate, the write scope, the repair budget and the failure
policy. Gates are therefore chosen at the freeze and never updated during the run, and the runtime refuses any change
to a frozen field. On each tick the scheduler takes 4 steps:

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

The limitation of this stage is its substrate. Work was delivered through tmux keystroke injection, file inboxes and
SQLite, and the substrate produced failures of its own. One coordinator ran code 28 hours older than the file on disk,
and a run manifest recorded the node statuses a model declared rather than those in the ledger, which a deterministic
materializer now fixes.

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
- The freeze fixes the plan before untrusted content is read, the property CaMeL enforces for control flow. Planning
  sees uploaded files only as records and paths, and nodes read their contents after the freeze
- The CLI-agent path breaks that separation, since `codex exec` reads papers and data while holding shell, file and
  network access, unobserved. CaMeL gives untrusted text only to a model with no tools
- A fixed plan does not stop untrusted text from steering values, since a sentence planted in a paper passes the
  literature check as partially supported (Section 2.7)
- The model holds for 1 user on a local machine, and a shared, unattended server with several users and API
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
are rubrics, and the result vocabulary does not distinguish them from the 23 Python gates.

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

## 3. Evaluation: 1 clean internal run, and no external score yet

### 3.1 Evidence so far: demonstrated end to end, not yet routinely unattended

The evidence so far comes from the stabilization log and the journey test report (Table 5). Journey tests are the only
acceptance evidence; regression suites locate faults but never decide the verdict (Appendix E.8).

| Evidence | Result |
|---|---|
| 14-node research run, 2026-09-03 | 1 bounded intent repair (Section 2.1), then the requirement contract and the plan were accepted the first time; every node passed on its first attempt, the ledger reached revision 106, and the sprint closed with all required gates passed, with no manual verdict and no bypass |
| Pre-release regression, 22 affected test files | 606 passed, 34 failed and 8 skipped; the 34 failures are kept as known debt, from old fixtures that the current frozen-plan preflight rejects and from Windows path failures, rather than relaxed away |
| Journey tests | 24 real tasks run through the production entry points, the only acceptance evidence |
| External benchmark scores | None; an adapter for Terminal-Bench 2.0 exists |

*Table 5. Evidence so far.*

Thus, the workflow has been demonstrated end to end, but it is not yet routinely reproducible without a person
attending.

Results use 6 values: PASS, PASS_WITH_KNOWN_LIMITATIONS, FAIL, NOT_TESTED, ENVIRONMENT_BLOCKED and NOT_AVAILABLE. A green
result may not be copied to a variant that no journey exercised, and the journey report states that it is "not a claim
that all 142 Level 2 features passed". **No external score exists**.

### 3.2 TruthInsightBench: the first external test, reported per dimension

The proposed first external test is TruthInsightBench (2609.05079), for 4 reasons:

- Its scored object is verification. It awards 100 points over 6 dimensions: evidence auditability 45, robustness 15,
  control testing 15, cross-dataset generalization 10, novelty 10 and falsifiability 5 (p8)
- The measured agents do the easy half and not the hard half, scoring only 11% to 16% on control testing (p14,
  Fig. 7)
- Its result is a flat plateau, since 4 coding agents on 1 frozen model score 58.4 to 60.3 and no pair separates, with
  the smallest p = 0.118 (p12). Any real gain would be visible
- A frozen model judge applies the rubric to executed artifacts, only the aggregation is deterministic, and no instance
  is graded by a human (p2, p9)

![Fig. 7. TruthInsightBench, range across 4 coding agents per dimension (2609.05079 p3, p14). Red, hatched: dimensions that need the agent to try to break its own result.](build/fig/fig5-benchmarks.png)

Thus, results on this benchmark should be reported per dimension rather than as a total.

---

## 4. The state of the art: 4 reference systems that generate well and check weakly

The 4 systems were chosen to span the design space: generation first (AI Scientist-v2), scale (Kosmos), a mechanical
held-out check (Arbor), and the same thesis as AI4Research inside openJiuwen (auto_research). Each system is placed on
the verification ladder of the survey "Autonomous Research Agents: A Survey of AI Scientists and the Verification
Gap" (2608.05179), introduced in Section 2.3. The survey ranks research areas rather than
systems, so the placements are this report's own, and 4 rungs of the ladder are used:

- II: an executable test against held-out ground truth
- IV: grounding in citations
- VI: judgment by a human expert
- VIII: the model's own judgment

The label "exec" marks a system that checks by executing code, without a held-out test.

### 4.1 AI Scientist-v2: strong generation, and a review that missed a 57% data overlap

AI Scientist-v2 (2504.08066) generates research first and checks it last. It works in 4 phases:

- Ideation at "grant proposal" level, with Semantic Scholar checked for novelty (p4)
- An experiment progress manager that runs 4 stages with explicit stopping criteria: prototype, hyperparameter tuning,
  research agenda and ablations (p5)
- A tree search inside each stage. At each node the model writes a plan and Python code, the code runs, an error marks
  the node as buggy, and a vision-language model critiques the figures. Expansion debugs buggy nodes or extends the best
  ones, and a model evaluator picks the best node per stage (p5-7)
- Writing in 1 pass followed by reflection, with a vision-language model checking that figures match their captions (p8)

3 of its manuscripts were submitted to an ICLR 2025 workshop, and 1 scored 6, 7 and 6 (6.33), above the acceptance
threshold, before being withdrawn by prior agreement (p2, p9). Humans chose 3 of about 40 generated ideas and the best
manuscript for each idea (p10).

The checking missed a serious flaw. The authors' own post-review examination found about 57% overlap between training
and test data in the code (p11), while the workshop reviewers raised justification and breadth, not the overlap (p2).

Compared with AI4Research, AI Scientist-v2 searches adaptively at every stage, uses a model reviewer as the final check
and has no contract. Thus, it is strong at generating, and its checking is peer review and model judgment (rungs VI and
VIII).

### 4.2 Kosmos: research at scale, least accurate on synthesis at 57.9%

Kosmos (2511.02824) is built for scale, and it works in cycles:

- A scientist supplies an objective and a dataset
- Each cycle runs parallel tasks for 2 agents, 1 for data analysis and 1 for literature search, and their outputs are
  summarized into a shared world model, which is queried to propose the next cycle's tasks (p2)
- A run takes about 200 agent rollouts, writes 42,000 lines of code and reads 1,500 papers (p1-2)
- Every statement in the final report cites the notebook or paper it came from

79.4% of 102 statements were judged accurate by experts who did not see Kosmos's evidence. By type, 85.5% of data
analysis statements, 82.1% of literature statements and **57.9% of synthesis statements** were accurate (p4).

Compared with AI4Research, Kosmos links its evidence but does not gate it, and it re-plans its world model every cycle,
the opposite of a frozen contract. The 57.9% on synthesis supports keeping claims separate from synthesis, as
AI4Research does, but it says nothing about AI4Research's own synthesis. Its checks are execution and citation
grounding (exec and rung IV).

### 4.3 Arbor: a held-out merge gate with no model, the closest system on checking

Arbor (2606.11926) separates a long-lived coordinator from short-lived executors:

- The coordinator owns a hypothesis tree, and each node of the tree holds a hypothesis, an insight and a git commit
  reference (p6)
- Each executor tests 1 hypothesis in its own isolated git worktree (Alg. 1, p7). An executor may repair the
  implementation but not change the hypothesis, since otherwise "the returned score would no longer be evidence about
  the assigned node" (p8)
- The coordinator loops through 6 steps: observe, ideate, select, dispatch, backpropagate and decide (p7)
- A held-out merge gate evaluates each candidate on the test evaluator in a fresh worktree, and merges it into the best
  artifact only if it improves on it. No model decides the merge (p8)

On Terminal-Bench 2.0, Claude Code has the best development score (75.00) and drops to 71.70 on held-out tasks, while
Arbor scores lower on development (72.22) and best on held-out tasks (77.36) (p10). The limitation of this result is
that the test evaluator is called on the best candidate every cycle (Alg. 1, p7), so the held-out score is itself
selected over many test calls.

Compared with AI4Research, Arbor is the closest system on checking. Its gate is fixed outside the agent, but the gate is
not hashed with a plan, and the plan changes every cycle (rung II).

### 4.4 openJiuwen auto_research: the same thesis, with the contract renegotiated every round

openJiuwen's agent-core contains an automated research package, auto_research, with 7 parts:

- A module chain from topic survey through experiment design, code implementation, experiment execution and reflection
  to reporting in LaTeX, plus standalone paper scoring
- An LLM manager that emits 1 decision each round: execute a subtask under a contract, done, or blocked
- Host-side validation that rejects illegal moves in code, such as execution without a ready implementation,
  re-execution before repair, or declaring done while requirements are pending
- Budgets of 50 rounds, 4 code retries, 6 design revisions and 4 execution retries
- A claim status computed on the host with no model, which classifies new numbers against prior papers
- Paper scoring by a dual rubric sampled 5 times at temperature 0
- No published evaluation

Compared with AI4Research, auto_research shares the design thesis that the model decides and the host validates, but
it renegotiates the contract every round instead of freezing it per run. Thus, it is the sharpest contrast in this
report.

### 4.5 Side by side: AI4Research checks the most and generates the least

| System | Plans how | Checks with | Rung | Headline result |
|---|---|---|---|---|
| AI Scientist-v2 | Tree search per stage | Execution; model and vision-language reviewers | exec, VI, VIII | 1 of 3 workshop papers above threshold; 57% overlap missed |
| Kosmos | World model, re-planned per cycle | Citation to a notebook or source | exec, IV | 79.4% of statements accurate; 57.9% on synthesis |
| Arbor | Coordinator-owned hypothesis tree | Held-out executable merge gate, no model | II | Terminal-Bench held out: 77.36 against 71.70 for Claude Code |
| openJiuwen auto_research | Manager with a per-round, host-validated contract | Execution; rubric scoring | exec, VIII | No published evaluation |
| **AI4Research** | **Compiled, frozen contract** | **Frozen gates; verbatim grounding** | **exec of a pre-approved runner, IV** | **1 clean 14-node run; no external score** |

*Table 6. The 4 reference systems and AI4Research side by side. Every result except openJiuwen's is the authors' own measurement.*

The field is ahead on autonomy, scale and generality. Kosmos reads 1,500 papers in a run, AI Scientist-v2 writes and runs
its own experiments, and Arbor shows a held-out gate with no model paying off. AI4Research's claims are auditable,
through frozen gates, retained spans, and a verdict and evidence status on every conclusion, but they have not been
checked externally.

---

## 5. The target platform: the DeepSeek Harness supplies the runtime, not the contract

The platform decision was made on 2026-09-11: the DeepSeek Harness (dsh) for now, chosen as the more certain of the 2
candidates and already the target of the capsule report. Sections 5.1 to 5.3 give the evidence for it, and Section 5.4
explains why the other candidate, openJiuwen, comes later.

### 5.1 Why the harness matters: it moves pass rates almost as much as the model

![Fig. 8. At a fixed model, harness choice moves pass rates about as much as model choice (Claw-SWE-Bench, 2606.12344 p11-13).](build/fig/fig4-harness.png)

Claw-SWE-Bench (2606.12344) measured how much the harness around a model matters on coding tasks:

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

| AI4Research stage | dsh mechanism | What AI4Research would add (proposed) |
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

| | AI4Research | openJiuwen auto_research |
|---|---|---|
| Contract scope | 1 per run, frozen | 1 per round, renegotiated |
| Grading rules | Inside the frozen hash | Host rules in code; paper scoring by a model rubric |
| Adaptation | Bounded repair before the freeze | Every round |
| Code generation | Pre-built runners on the native path | A model coder with retries |
| Claims | Cue-word extraction and verbatim grounding | Host-only numeric claim status against prior papers |
| Code shared today | 0 imports | |

*Table 8. AI4Research and openJiuwen auto_research compared.*

---

## 6. Where this leaves AI4Research: ahead on checking, behind on generating

AI4Research is ahead of the reviewed systems in 3 ways, all of them design properties rather than measured results:

- Sealing the grading rules inside the run's integrity hash, which the survey recommends and no other reviewed system
  implements
- Refusing literature verdicts for quotes not found in the retained source, so only re-verified spans reach the report
- Keeping an honest result vocabulary, in which not-tested and environment-blocked are not failures

It is behind in 3 ways:

- Experiment code on the trusted path covers 1 hand-built family
- Claim extraction is an English-only cue-word rule, cruder than the rule-based baseline CREDENCE measures, with recall
  unmeasured
- There are no external benchmark results

The lead is a design property, not a result, since Rel(AI)Build already hashes its specification and Arbor already runs a
held-out gate with no model (Sections 2.3 and 4.3). Thus, the first external result decides whether the lead holds.

### 6.1 Challenges: 11 open problems, each with what would settle it

The challenges are grouped by area, and each comes with the evidence for it and what would settle it.

A. Measurement and judgment

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 1 | No external measurement | Every strength above is a design property read in source; the 24 journey tests and the 1 clean 14-node run are internal, and there are 0 benchmark scores. Checking is weak elsewhere too: AI Scientist-v2's accepted paper carried about 57% train/test overlap, measured agents score 11% to 16% on control testing, and experts judge verifiable claims correctly 60.8% of the time, so human review is not the fallback | TruthInsightBench end to end, reported per dimension (Section 3.2) |
| 2 | Rubric verdicts look deterministic | 20 of 43 registered checks are model-judged rubrics, and the result vocabulary does not separate them from the 23 Python gates (Section 2.6) | Marking rubric verdicts as such in results and reports |

*Table 9. Challenges in measurement and judgment.*

B. Claims

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 3 | Provenance, not truth | Without an experiment, the strongest verdict is partially supported at 0.85, a case-insensitive substring of the cited section; spans that fail their re-hash are dropped silently and never enter the verdict, and no gate reads the span flag; claims judged insufficient or not supported still become report conclusions, so the unsupported list stays empty (Section 2.7) | Experiments beyond 1 family (Section 2.8); showing in the report prose the provenance labels already in the structured verdict; a gate that fails a claim whose span fails; a reportable set filtered on the verdict |
| 4 | Claim recall is unmeasured | The cue-word rule matches by prefix, counts any digit as testable, types every claim as a result and decomposes nothing; missed claims never reach the unsupported list, so the list looks complete | Hand-labeling 50 sections; a schema-bound model extractor behind the same span hash and gate (Section 6.2) |
| 5 | Text stages read English only | The typed fields between stages are language-neutral, so the English rules sit at 2 boundaries, reading the request and reading papers, while the repository's own operating documents are in Chinese | A schema-bound model extractor, tested on its own on non-English papers (Section 6.2) |

*Table 10. Challenges in claim handling.*

The English-only rules behind challenge 5 sit in 4 places:

- Reading the request, where the negation cues and the clause breaks (. ! ? ; : and but, however, yet) are English. Some
  Chinese action markers exist (改造, 迁移, 设计, 优化), but Chinese negation and Chinese punctuation (，。；) do not
- Reading papers, where the claim cues, testability, methods and report title use English patterns
- Claim length, where a claim must be 30 to 1,000 characters, and a Chinese character carries more text than an English
  one, so the bound selects different sentences in each language
- The relevance gate, where per-language patching has started with Chinese character pairs added by hand

C. Planning and the freeze

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 6 | Pre-freeze negotiation is bounded and advisory | Intent, requirement, plan graph and capsule selection get 1 repair by default, then the sprint fails; the fidelity objection is demoted after the budget, and the requirement and capsule-fit reviewers are advisory from the start, so a meaning error a reviewer found can pass (Sections 2.1 and 2.2) | Measuring the resubmission rate and how often a warning preceded a failed run; deciding whether a human-approved second repair is acceptable |
| 7 | A frozen contract is only as good as its compilation | Plan defects per run are unmeasured, and an open capability such as a shell or SQL routes around typed contracts, the cause of 13 of PlanCompiler's 22 failures (Section 2.3) | Counting plan defects per run |
| 8 | No policy for undefined outcomes | A frozen evaluator that is undefined on the outcome it receives has no defined behavior (Section 2.3) | A policy of halt, inconclusive or human, declared in the test policy |
| 9 | A wrong plan has no recovery path | There is no re-planning: when execution shows the plan was wrong, the run fails and the user resubmits, and a node no capsule fits raises `UNSATISFIABLE_CAPSULE` so the plan fails at the freeze (Section 2.2) | Keeping the freeze and documenting its cost against Arbor and Kosmos; the generalist capsule proposed in the capsule report (Section 4.1 there) |

*Table 11. Challenges in planning and the freeze.*

D. Capsule library. Trust classes, declared versus observed effects, versioning, gap records, protected paths and the 2
type vocabularies are covered in the capsule report (Section 3 there), so this group adds no numbered challenge here.

E. Execution and autonomy

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 10 | Execution is recorded, not observed | The old substrate used tmux keystroke injection, file inboxes and SQLite; a coordinator ran code 28 hours older than the file on disk, and a run manifest recorded model-declared statuses (Section 2.4). On the CLI-agent path, only the worktree bounds the agent, commands, files and network are unobserved, evidence is `fixture_or_adapter_only`, and untrusted paper text reaches an agent that can act (Section 2.5); only 21 of 79 manifests declare a trust class | The move to dsh (Section 5); model-written runners under hash-and-approve on the native path; sandbox access logs |
| 11 | Unattended runs do not finish | 3 logged runs stopped at literature discovery after Semantic Scholar returned HTTP 429, each from a different cause, and the first 2 causes (no source inventory and an empty services mapping) are fixed. The third was a prompt-only rerun: with no attached sources, the frozen policy of 1 attempt and then failing the run cancelled 13 downstream nodes. The clean run finished without intervention only with 6 PDFs attached, and an experiment that is not a fixture waits for a hash-bound approval, so an unattended run must defer any plan that needs one (Section 2.8) | A declared fallback to hash-bound local sources inside the frozen contract, with coverage stated in delivery; an unattended journey test from a prompt alone |

*Table 12. Challenges in execution and autonomy.*

### 6.2 Directions (proposed): the next step each challenge points to

The directions below follow from the challenges, and none is built yet:

- Moving the workflow onto dsh, keeping the contract layer as the contribution, and offering it to openJiuwen later
- Having a model write experiment runners under hash-and-approve
- Adding a schema-bound model extractor at both text boundaries (challenges 4 and 5), in which every typed field carries
  a verbatim quote in the source language that code binds to offsets and hashes, so no translated text becomes evidence
- Keeping deterministic checks after the extractor: the quote is found, the enumerations are valid, no verdict is
  upgraded, and a new gate fails unverified spans (challenge 3), each tested on its own per language against a
  hand-verified claim list
- Declaring a policy for undefined outcomes in the frozen contract (challenge 8)
- Declaring a local-source fallback for retrieval nodes (challenge 11)
- Running 1 external benchmark end to end before making any comparative claim (challenge 1)

## 7. Open questions: 4 questions, 2 already decided

| # | Question | Owner |
|---|---|---|
| Q-G1 | Target platform: decided, dsh for now | user |
| Q-G2 | Port the runtime or add a layer: decided, add the layer to openJiuwen later | user |
| Q-G3 | Should openJiuwen's auto_research be named as the closest comparison? | supervisor |
| Q-G4 | Which external benchmark comes before circulating? TruthInsightBench is proposed | user |

*Table 13. Open questions and their owners.*

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
`c291e7961a`: `docs/architecture.md`, `AGENTS.md`. openJiuwen: `agent-core@6ecf8218`.

14 sources were read in full, and each is used for 1 job (Table A1).

| Role | Source | Used for |
|---|---|---|
| Reference system | 2504.08066 AI Scientist-v2 | Generation-first design; 57% overlap missed by review |
| Reference system | 2511.02824 Kosmos | Scale; 79.4% and 57.9% statement accuracy |
| Reference system | 2606.11926 Arbor | Held-out merge gate with no model; 77.36 against 71.70 |
| Reference system | openJiuwen auto_research (source code, no paper) | Per-round contract |
| Mechanism | 2604.13092 PlanCompiler | Typed plan compilation; 44/50 against 20/50; constraint evasion |
| Mechanism | 2503.18813 CaMeL | Control flow fixed before data; 77% against 84% |
| Mechanism | 2606.26924 Rel(AI)Build | Specification hashed; test linkage cooperative |
| Mechanism | 2606.19819 CREDENCE | Price of rule-based extraction, 0.811 against 0.88 to 0.91 |
| Mechanism | 2604.04074 FactReview | Closest verdict design; 79.7% recall; 17.0% |
| Measurement | 2608.05179 verification-gap survey | Ladder rungs; pre-committed specification |
| Measurement | 2411.14199 OpenScholar | 78% to 90% fabricated citations |
| Measurement | 2603.05912 DeepFact | 27.0% unsupported; experts 60.8%; 83.4% |
| Measurement | 2606.12344 Claw-SWE-Bench | Harness 27.4 against model 29.4 points; 19.1% against 73.4% |
| Benchmark | 2609.05079 TruthInsightBench | 6 dimensions; 58.4 to 60.3 plateau |

*Table A1. The 14 sources read in full, and what each is used for.*

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
| Is "nobody seals grading rules" still true? | Yes, after a targeted search on 2026-09-13. Rel(AI)Build hashes its specification, but its test linkage is cooperative and checked after the fact | 2.3 |
| What does the freeze cost? | No re-planning when execution shows the plan was wrong, and search only inside operators. It fits execution and grading, not exploration | 2.3 |
| Is the frozen chain fully recomputed? | 3 stages are recomputed, and the rest are compared by hash | 2.3 |
| What happens when a frozen rule is undefined on the outcome? | Nothing is defined. A policy is proposed | 2.3 |
| Why move platforms? | Harness choice moves pass rates by 27.4 points at a fixed model, and the current substrate produced a coordinator running 28-hour-old code | 5.1 |
| Why not openJiuwen now? | No code is shared today, and its auto_research renegotiates its contract every round. The decision is to contribute the layer later | 5.4 |
| Is the 1-sentence design rule measured? | No. It is a translated target statement from a Chinese source | 1 |

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
| 2.2 | Same-model review record; physical plan; unsatisfiable node; CLI coding capsules | `elastic_planner.py:482`; `apo_plan_compiler.py:1192`, `:626`; `capability_capsules.py:1145-1180` |
| 2.3 | Freeze order; scheduler input; live definitions | `elastic_planner.py`: `compile_and_freeze_execution_bundle` :6888, `compile_scheduler_input` :6662; `execution_authority.py:81-91` |
| 2.3 | Grading rules written into the scheduler input; canonical hash | `elastic_planner.py:6802-6842`; `intent_compiler.py:62-67` |
| 2.3 | Verification and its 3 recomputed stages | `elastic_planner.py`: `verify_frozen_execution_chain` :7748-8052, stages :7871-7884, :7919-7929, :7930-7951 |
| 2.3 | Tamper test; failure handling | `tests/harness/test_elastic_planner.py:4697-4718`; `elastic_planner_runtime.py:262-310` |
| 2.4 | Dispatch tick; reconciling dispatches | `graph_node_dispatcher.py`: `_dispatch_ready_unlocked` :16772, `_reconcile_existing_dispatches` :5774 |
| 2.4 | Ready set, assignment, admission | `graph_scheduler.py`: `enqueue_ready` :4100, `assign_ready` :3131 and :3200-3209, `node_admission_status` :2103, `topo_order` :2008, `ready_nodes` :2179 |
| 2.4 | Write conflicts; monotonic progress; skipped dependents; human review; statuses | `graph_scheduler.py`: `write_scope_conflict` :2237, `mark_node_result` :3736, `terminalize_dependency_blocked_nodes` :3979, :3633, :48-53 |
| 2.4 | Projection check; ledger | `scheduler_input.py:849`; `task_graph_state.json` |
| 2.4 | Stale coordinator code; model-declared statuses | `harness/BUG5-ROOT-CAUSE.md:38`; log l.786-787 |
| 2.5 | Registry path checks; CLI-agent path | `harness/tools/research_operator_registry_adapter.py`: `_verified_dispatch_authority` :268, `_validated_binding` :357; `multi_task_runner.py` |
| 2.5 | Request channel and sender; files seen at planning | `intent_compiler.py:386-400`; `elastic_planner.py:1389-1392` |
| 2.6 | Gate kinds; code-task verification | `contract_gate_executor.py`; `verification_gate.py:13` |
| 2.7 | Extraction; cue words; testability; length; evidence id; error | `…/evidence/operators.py`: :1180-1265, :1183, :1224, :1206, :1226, :1264 |
| 2.7 | Verdict table; substring match; span re-verification; span flag | `…/action/delivery.py`: :145-166, :137, :114-132, :201 |
| 2.7 | Verdict gate; reportable set; evidence id kept; limitation and basis; conclusion fields | `harness/evaluators/scientific/claim_verdict_gate.py:29-69`; `delivery.py`: :667-670, :2059, :167-172, :175-178, :220, :2084-2085 |
| 2.7 | Claim example | `tests/plugins/autosci/scientific_lifecycle_action_operators/test_action_delivery_operators.py:689-742` |
| 2.8 | Experiment capsule; hand-written runner | `harness/capability-capsules/cap.research-experiment-run.yaml`; `kv_cache_quantization_runner.py` |
| 3.1 | 14-node run; regression; journey report | Log l.793-795, l.862; `docs/integrations/autosci/phase-22-journey-test-report.md:65` |
| 4.4 | auto_research package; illegal-move checks | agent-core: `openjiuwen/rsi/artifact_rsi/paper_opt/auto_research/`, `pipeline/transitions.py:602`, `:614` |
| 5.2 | Plugin quote; replayability quote; service roles | dsh at `c291e7961a`: `docs/architecture.md:13`, `:121`; `AGENTS.md:113` |
| 6.1 #5 | English rules in intent and papers | `intent_gateway.py:240`, `:246-251`; `operators.py:1183`, `:1224`, `:1206`, `:1380-1390`; `delivery.py:995-1011`, `:1648`; `autosci_bridge.py:12875-12885` |
| 6.1 #11 | Semantic Scholar stops; prompt-only rerun; PDFs attached | Log l.327, l.662, l.814, l.815 |

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
   `CAPSULE_CHANGED_DURING_PLANNING`
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
| Research agents | AI Scientist-v2, Kosmos, Arbor, openJiuwen auto_research | Nothing global; plans evolve every cycle or round | |

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
