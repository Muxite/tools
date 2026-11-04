# CC build coverage and checking assignments

**Reading level: human potential.** This is a navigation and responsibility map for the existing ten CC designs. Use the current contracts and shared runner rather than implementing ten different execution or verification setups. No declaration/schema version changes are introduced here.

## Ports and assigned verification

These are semantic ports; [field contracts](reference/other-contracts.md), [Intent/Requirements](reference/intent-and-requirements.md) and [checking records](reference/checking.md) own the serialized meanings. Each output is a candidate until its independent assigned checks and protected release pass. Full accepted input and attributable upstream evidence remain available to each declared consumer.

| CC | Required input | Candidate output | Independent verifier responsibility |
|---|---|---|---|
| Intent | Qualified original request and attributable reference context | Intent IR with scope, constraints, uncertainty and traceability | Check fidelity, coverage, scope and explicit uncertainty against the original input; do not write a replacement intent. |
| Requirement | Accepted Intent, original context, resource references and authorized defaults | Research Brief with obligations, preferences, resources, metrics and evidence requirements | Check preservation, traceability, justified defaults and usability for planning; material unresolved obligations block release. |
| Planner | Accepted Brief, pinned eligible catalogue, supplied resources and protected policy | Proposed finite JSON DAG, dependencies, bindings and suggested checking assignments | Assess Brief coverage and task relevance, required outputs/evidence, declared resource/effect feasibility and unsupported assumptions; detailed context below. |
| Search | Accepted Brief and plan-bound query/scope | Attributed candidate evidence and source references | Check relevance, grounding, citation fidelity, scope and declared coverage; unsupported citations cannot pass. |
| Screening | Attributed candidates and inclusion/exclusion/scoring rules | Decisions, scores and reasons linked to candidates | Check consistent application of criteria, supported scores, constraints and attributable dispositions. |
| Hypothesis | Accepted screened evidence, question and Brief | Testable hypothesis, registered protocol/criteria and uncertainty | Check evidence links, falsifiability, protocol completeness and accepted constraints before build. |
| Builder | Accepted frozen hypothesis/protocol, supplied baseline/resources and permitted tools | Bounded POC/source/build artifacts and execution evidence | Check implementation against the registered protocol, forbidden effects/imports and required reproducibility evidence; environment failures remain explicit. |
| Research Benchmark | Accepted POC, frozen protocol, matched baseline/treatment and validation resources | Measurements, comparison and run records | Check matched conditions, baseline presence, metric provenance and completeness; do not confuse this scientific CC with platform benchmarking. |
| Scientific Evaluation | Accepted registered criteria, measurements and supporting evidence | Scientific verdict with evidence-to-criterion reasoning and limits | Check conclusions against registered criteria and actual measurements; a valid scientific negative is deliverable. |
| Delivery | Accepted scientific outputs, gate outcomes and required disclosures | Packaged report/artifacts with verdict, provenance and limitations | Check consistency with accepted artifacts and outcomes; preserve negative results and disclose missing evidence. |

The CC owner defines per-CC ports and proposes checking duties. The Verification lead owns independently admitted mandatory checking profiles and protected gate behavior; the Benchmark lead owns expected platform labels independently of producer outputs. The protected binder assigns exact profiles and criteria before output review. Capsule-author self-tests support development but cannot certify their own outputs.

## Planner semantic verifier contract

The protected context builder supplies the exact proposed graph and subject identity; accepted Brief including all mandatory outcomes, constraints, resource/evidence obligations and traceability references; pinned eligible catalogue with ports, effects, tools, budgets and evidence requirements; supplied resource bindings; node/subnode contracts; independently assigned profile/criteria and deterministic binder findings. It includes permitted upstream evidence and execution observations. The Planner's narrative and suggested checks are untrusted input, not checking authority. Missing accepted context blocks review.

After deterministic graph/port/cycle/mandatory-assignment checks pass, the independently assigned read-only semantic verifier checks that every mandatory Brief obligation has a justified producing node and evidence path, planned work addresses the objective, dependencies make sense beyond mere type compatibility, required resources/effects are declared and feasible within the supplied bounds, and assumptions do not invent permissions, resources or successful results. It evaluates a finite proposed plan; it does not author a replacement plan, add nodes or repair bindings.

Return the existing verifier Assessment structure: exact subject and review-context references, verdict, one attributable finding per required criterion, evidence references to graph elements/Brief obligations/catalogue or binder records, uncertainties, limitations and any required correction. Unsupported feasibility or missing obligation coverage is a blocking finding. The host validates coverage and subject binding and persists the accepted graph, pins, contracts and assignments before dispatch. No different verifier model or additional verification tier is required.

## One shared build and completion rule

Use the same declaration loader, runner, context builder, evidence capture, deterministic checking, read-only semantic verification and durable gate/store path for each supported CC. Reconcile and adapt the already built compiler and compatible implementations first. A generated module or successful self-test is a candidate implementation. The owning native task records implementation complete only after observed behavior satisfies its assigned cases, connected boundaries and required evidence; limitations and environment blocks remain recorded. Whole-workflow acceptance additionally requires connected end-to-end evidence.

See [capsules](capsules.md), [research ports](research-design.md), [node/subnode contracts](reference/node-execution.md) and [core scope](core-build.md). Human schedules and development-tool skills stay outside the product build package.
