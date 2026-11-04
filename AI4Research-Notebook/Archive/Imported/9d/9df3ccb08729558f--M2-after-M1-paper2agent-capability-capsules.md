# M2 after the design package: capability capsules as executable research methods

**Working note | 16 October 2026**  
**Status:** synthesis for M2 PRD and architecture discussion; not a PRD, scope approval, or implementation commitment.

**Scope clarification, 19 October:** Paper2Agent is one possible M2 workstream; the recommendations below do not define the full M2 scope. For the source-grounded connection to CCs and an optional container execution profile, start with [the container proposal](paper2agent-reference/06-paper2agent-cc-container-proposal.md). Its runtime-profile proposal qualifies the original assumption that existing declaration fields alone settle packaging integration.

## Executive reading

The design package has now made the M1 shape concrete: declare reusable capabilities, select and bind them into a fixed plan, execute through governed interfaces, preserve evidence, and keep RSI (Research Self-Improvement) offline. The natural next step is to make the capsule lifecycle work end to end on real research methods, while learning from the M1 baseline. M2 should turn the capsule from a well-specified declaration into a trustworthy, discoverable, versioned, independently checked unit of research work.

The attached paper, *Paper2Agent: Reimagining Research Papers As Interactive and Reliable AI Agents* (Miao et al., arXiv:2509.06917v2, 2025), is a useful pattern for converting a paper and repository into reusable tools: identify the code, provision a pinned environment, execute and audit tutorials, extract parameterized tools, test against reference outputs, and package an MCP interface. The strongest connection is that this pipeline can produce candidate Capability Capsules (CCs), with the CC contract, admission checks, and protected evidence giving it stricter lifecycle semantics than “generate an MCP server.”

**Recommendation:** define M2 around a *paper-to-capsule path plus governed library/planner use*, with independently authored held-out checks and explicit human review at publication. Keep recursive improver self-improvement as a separately gated research track, and keep runtime-plan mutation out of scope until M2 evidence supports a later decision.

## What the paper contributes

Paper2Agent coordinates codebase/environment/tutorial-extraction/testing agents. It records workflow artifacts, executes tutorial examples, turns them into single-purpose functions with explicit inputs/outputs, and assembles MCP tools, resources, and prompts. Its case studies (AlphaGenome, TISSUE, Scanpy) report reproduction and novel-query evaluations. The paper also names important limits: incomplete or poorly documented repositories constrain reliability; its benchmark uses expert-curated examples and manual review; and the best unit may span multiple related papers rather than one paper.

For M2, the valuable contribution is not MCP specifically. It is the staged conversion of research material into executable, tested, documented operations, retaining a trace from source method to tool and observed output. MCP can be one adapter/carrier for a CC, not the capability model itself.

## Connection to the current CC contract

The design package already covers several needs exposed by the paper:

| Paper2Agent concern | Existing capsule/runtime concept | M2 implication |
|---|---|---|
| Method/tool inputs and outputs | Typed `ports`, schema references, `needs` | Generate a *draft* declaration from extracted functions, then validate types and applicability; never infer that a paper’s prose alone guarantees executable I/O. |
| Reproducible environment and code | Pinned carrier/body closure, external dependency pins, remote interface fingerprints | Capture environment lock, data/model/service versions and license/availability as provenance or governed dependency records. |
| Tutorial reproduction and novel use | `guarantees.checks`, evaluation suites, held-out status, runtime evidence | Separate reproduction fixtures from independently authored generalization cases; tutorial success alone is not general capability evidence. |
| MCP tools/resources/prompts | CC execution style, ports, implementation and optional overlays | Treat prompts/resources as pinned implementation or explicit supported overlays; MCP is an adapter. Keep planning and run objectives in protected runtime records. |
| Test/refine loop | Candidate generation and isolated RSI | M2 may produce immutable candidate versions; an independent evaluator/referee controls scoring and admission. Candidate generation cannot own its release decision. |
| Paper/repository lineage | `identity.lineage`, source references, hashes, provenance | Preserve paper version/identifier, repository commit, tutorial/source locations, extracted function mapping, toolchain, and authorship/agent trajectory. |
| Package as reusable capability | Library eligibility/admission and future plan selection | Eligibility must depend on contract validity, safety/dependency closure, evidence profile, and policy—not successful server generation alone. |

A CC is the stronger abstraction because it declares not only *what code can be called*, but ports, prerequisites, effects, guarantees, budgets, evolution constraints, and exact implementation identity. The run still binds objective, artifacts, permissions, verifier assignment, and release outcome outside the declaration. A paper-specific agent is therefore likely a *bundle or collection of CCs plus supporting resources*, not automatically one monolithic CC. Composite execution remains explicitly future context in the package and should not be smuggled into M2 as if already supported.

## Proposed M2 outcome

M2 should answer one practical question: **Can the system turn a selected, reproducible research method into an admitted, findable capsule that a bounded plan can safely use, and can we show why its results deserve trust?**

A small vertical slice could accept a paper/repository pair and produce:

1. A source manifest: paper/version, official repository evidence, commit, license, data availability, and unresolved provenance.
2. A reproducible environment record and tutorial/example execution bundle with captured inputs, outputs, logs, figures, and resource use.
3. One or more single-purpose candidate CC implementations, each with explicit ports, dependencies, effects, budgets, and source traceability.
4. A test/evaluation package distinguishing reproduction examples, contract tests, safety tests, and held-out generalization cases.
5. A human-reviewable capsule candidate and an independent admission report. Failed, unsupported, or inconclusive candidates remain visible as such.
6. Library indexing and bounded Planner selection over *eligible* candidates, followed by deterministic plan validation and graph freeze before dispatch.
7. An evidence report comparing the candidate’s behavior with a manually implemented/reference path on predeclared cases, including cost, latency, reproducibility, and failure modes.

This slices across the November planning sequence already captured locally: integrate the Generalist; generate one candidate and hand it to isolated RSI; automate protected eligibility/admission; improve bounded planning over eligible candidates; then compare bounded MCTS ordering with that planner. The approved plan says December composition is M3; keep composition deferred unless the M2 PRD explicitly changes that boundary.

## M2 boundaries and safety properties

- **Do not call October success M1 completion.** M1 evidence is an artifact-dataset baseline with known limits; M2 entry depends on reviewing it and resolving the PRD/architecture alignment gate.
- **Do not let the extraction agent author its own acceptance policy.** It can propose code, declaration fields, and tests. Protected policy defines mandatory checks; independent cases are not derived solely from the same tutorial or implementation.
- **Do not equate tutorial reproduction with scientific validity.** Reproduction shows agreement on selected fixtures, not correctness on new data, validity of assumptions, or causality.
- **Do not grant a declaration authority.** Declared network, model, file, and external effects remain subject to runner policy and effective permissions.
- **Keep pins immutable per run.** Library updates affect future plan freezes; running tasks retain exact capsule, model, data, environment, verifier and route bindings.
- **Keep RSI offline and isolated.** It may change one authorized implementation surface and emit a candidate. It cannot alter declarations/contracts, check policy, evaluator/referee, admission authority, or activation controls.
- **Keep failed extraction useful.** Missing source, license, data, dependencies, or reproducibility should produce an explicit unsupported/ineligible result with evidence, not fabricated certainty.
- **Avoid premature genericity.** Start with one or two representative computational methods and a narrow supported language/runtime profile; record unsupported method shapes rather than promising any-paper conversion.

## Suggested M2 success measures

Freeze measures and case provenance before the implementation trial. A reasonable initial scorecard:

- **Traceability:** share of generated tool behavior mapped to source code/tutorial and pinned dependency/data/model inputs.
- **Reproduction:** independent agreement with predeclared reference outputs, with numerical tolerances and figure comparison rules appropriate to each method.
- **Contract correctness:** valid and invalid inputs, output schema validity, deterministic rejection of missing prerequisites, declared side effects, and budget enforcement.
- **Transfer:** held-out datasets/tasks tested by reviewers who did not write the extractor or capsule; report both success and unsupported/abstention outcomes.
- **Admission quality:** false eligible rate and false rejection rate on an independently adjudicated candidate set; no producer-authored judge may satisfy a mandatory gate alone.
- **Planning:** eligible-candidate selection and valid-plan rate on fixed feasible and infeasible cases; verify no dispatch occurs for invalid or unfrozen graphs.
- **Operational cost:** end-to-end human effort, model/tool calls, runtime, compute cost, setup failures, and reproducibility across a clean environment.
- **Scientific-use limits:** explicit expert review for claims whose validity cannot be established by software tests; separate method execution correctness from interpretation/claim quality.

Do not set numeric thresholds from Paper2Agent’s reported scores; its tasks, baselines, sample sizes, methods, and human grading do not establish thresholds for AI4Research.

## M2 decisions the PRD must settle

1. What is the M2 product claim: one reproducible capsule pipeline, a usable capsule library/planner, or both as one vertical slice?
2. Which method domains, repositories, languages, environment managers, and external services are supported in the first slice?
3. What exact evidence makes a candidate selectable, and which requirements need human/domain-expert review?
4. Who controls held-out data, independent test authorship, evaluator/referee, admission, publication, and rollback?
5. Does M2 include a separate human activation step, or may eligible candidates become selectable automatically under policy? The local November plan proposes future selectability but says the aligned M2 PRD/design must confirm it.
6. What M1 completion and alignment evidence is a hard entry gate, and which unmet items can be explicitly waived by the product owner?
7. Is the research-improver itself a target in M2? If yes, define editable components, isolated environment, held-out rotation, candidate comparison, and immutable control plane before any recursive loop.
8. Is any execution-time adaptation desired? If yes, define it as a separately authorized runtime capability with a fixed-plan invariant and safety case; otherwise defer it.
9. What is the intended relation between one paper and one CC: one method per CC, a paper bundle of CCs/resources, or multi-paper method families?

## Sequencing proposal

**Gate 0 — M1 evidence review and PRD alignment (Nov 2–3 window):** review actual trial outputs and limits; product owner supplies aligned M2 PRD; architecture freezes only with required interfaces and decisions resolved.

**M2-A — Thin vertical slice (planned Nov 4–13 windows):** integrate Generalist/interfaces; generate one bounded candidate; package and independently evaluate it; implement policy-backed eligibility/admission; retain all evidence. A blocked or no-gain outcome is still valid evidence, but does not satisfy a positive capability claim.

**M2-B — Planner selection (planned Nov 16–20 windows):** compare bounded planner improvements and MCTS ordering on the same fixed feasible/invalid set; exact pins, graph checks, freeze and protected dispatch remain authoritative.

**M2-C — Regression/readiness (planned Nov 23–30 windows):** publish case-level evidence, known limits and a go/no-go recommendation for December M3. Keep composition and broader self-improvement out of M2 unless the PRD explicitly pulls them in and budgets/evidence are revised.

The local schedule is a planning proposal, not evidence that dates, owners, or acceptance thresholds have been confirmed. Its conditional gate should remain real.

## Reading references

- Miao et al., *Paper2Agent: Reimagining Research Papers As Interactive and Reliable AI Agents*, arXiv:2509.06917v2 (attached PDF), especially the workflow and limitations sections (paper pp. 4–8, 14–15, 18–19).
- Current M1 design: `RSI Design Docs/DESIGN - RSI M1 v0.2.md`, particularly scope and the M2 boundary (Section 15). It explicitly says runtime and recursive improvement need later scope decisions.
- Current CC field/lifecycle contract: `outputs/m1-core-review-2026-10-14/design-package-compact/capsule/declaration.md` and `capsule/authoring.md`.
- Local sequencing and decisions: `AI4Research_private_planning/cc-plan-approved-revision-2026-10-14-r2/plan.md` and `decisions.md`.
- Meeting direction: `AI4Research_private_planning/2026-10-13-meeting-decisions.md`.

## Follow-up: change impact and effort

A focused assessment of what the current M1 CC already supports, the builder/evidence components a Paper2Agent path adds, a first-slice boundary, and a provisional person-day range is in [Paper2Agent-to-CC change impact and effort](Paper2Agent-to-CC-change-impact-and-effort.md).
