# Paper2Agent-to-CC: M1 change impact and scoped effort

**Working assessment | 16 October 2026**  
**Purpose:** estimate the Paper2Agent-related capsule work as one bounded M2 workstream. This is a planning range, not an approved estimate, task assignment, or full M2 scope.

Related synthesis: [M2 after M1: Paper2Agent and capability capsules](M2-after-M1-paper2agent-capability-capsules.md).

**19 October follow-up:** [Paper2Agent, CCs, and a container runtime proposal](paper2agent-reference/06-paper2agent-cc-container-proposal.md) grounds the connection in the cloned source and distinguishes application containerization from a per-capsule runtime profile. The CC semantic declaration can remain the initial target, but new container profile, binding, launch and evidence agreements are needed before container execution is supported. The follow-up gives an incremental estimate with explicit exclusions and overlap rules; it does not replace the feasibility spike or commit the full M2 scope.

## Decision in brief

The current M1 CC contract is a credible target format for the *output* of a Paper2Agent-style pipeline. It already models immutable implementation pins, typed ports, dependencies, effects, budgets, guarantees/checks, quality evidence, and lineage. The paper’s MCP server can be represented as an MCP/remote CC or as local tool/code CCs exposed through an MCP adapter. No evidence from this paper alone justifies changing the core CC schema.

The gap is mainly a **builder and evidence pipeline**, not a new capability abstraction. Paper2Agent identifies source repositories, reconstructs environments, finds and runs tutorials, extracts reusable tools, tests/refines them, and packages an MCP server. M1 provides capsule authoring, pinned packaging, checks/admission, storage and use boundaries, but does not specify or deliver this general paper-to-tool construction workflow. M2 should add a build record/source manifest and evidence artifact family alongside CCs. Only add declaration fields if a concrete pilot shows necessary provenance cannot be represented in the build record and lineage.

For a narrow, reviewable first slice—one Python paper/repository, one supported environment path, one or two extracted tools, a human-reviewed candidate CC, independent checks, no automatic publication—the planning band is **about 20–35 engineering person-days plus 5–10 domain/reviewer person-days**. This assumes the M1 capsule registry, immutable packaging, runner, evidence storage and admission interfaces exist and are usable. If those M1 foundations are incomplete, add approximately **10–20 engineering person-days** for the missing integration/foundation work. Multi-language support, general paper coverage, robust arbitrary environment repair, and automatic library publication are outside this band.

## What M1 already gives us

| Need | M1 design coverage | Impact |
|---|---|---|
| Stable capability and version | `identity`, carrier/body hashes, local/remote distinction | Reuse unchanged for generated candidate identity and immutable implementation closure. |
| Source/build ancestry | Optional `identity.lineage` including builder, trigger, context and provenance | Reuse for parentage; it is not yet a detailed paper/repository/tutorial manifest. Avoid stuffing long build logs into declaration provenance. |
| Typed reusable interface | `ports`, `needs`, model/service requirements, resource declarations | Reuse; extractor must propose then validate these against implementation and actual examples. |
| Safety and resource limits | Network policy declaration, effects, budgets and enforcement semantics | Reuse, with protected admission/runner checks. Generated declarations never grant permissions. |
| Evidence/check contract | `guarantees.checks`, evaluation suite/metrics/thresholds, held-out/author/runner fields | Reuse for check *definitions*. Persisting complete generated datasets, logs, plots, environment captures and run evidence belongs in artifact/evidence records. |
| Candidate validation/admission | Declaration/integrity/provenance/compatibility/self-test and independent evidence review | Reuse admission path; paper reproduction tests alone cannot satisfy independent generalization or domain-validity claims. |
| Library selection | Human activation in M1; planned protected automatic admission/selectability in M2 | M2 policy decision: make eligible candidate selectable automatically or retain a human publication gate for this new builder path. |
| Execution adapter | M1 supports code/tools, prompt/agent and pinned MCP/A2A interfaces within supported boundaries | MCP packaging can be an adapter. A remote MCP CC pins interface/fingerprint; local extracted functions can be individual code CCs. |

**Likely declaration change:** none for the initial slice. At most, add an optional, versioned source-reference object if the pilot proves paper/repository/source-location references are required for consumers after admission and cannot be held in an immutable linked build manifest. That would be a compatibility-governed schema proposal, not a pre-emptive M2 requirement. Keep extracted source locations, tutorial IDs, environment-lock hash, license review, and builder trajectory in the build manifest/lineage evidence; keep task/run objectives and permissions outside the declaration as M1 already requires.

## New or expanded components

| Component | What it does | Why M1 is not enough |
|---|---|---|
| 1. Source intake and qualification | Resolve paper version and official repository; capture commit, license, data links, submodules and provenance; report missing/ambiguous sources | M1 can record pins and provenance but has no paper/repository resolution workflow or qualification result. |
| 2. Reproducible environment builder | Provision an isolated environment from supported manifests; capture lock, image/toolchain identity, setup logs and resource limits | M1 pins dependencies but does not reconstruct arbitrary research environments. Scope the first supported path tightly. |
| 3. Tutorial/example scanner and runner | Inventory candidate notebooks/scripts; select approved examples; run them in isolation; capture inputs/outputs/figures and assumptions | M1 checks capabilities and invocations, but does not discover and execute repository tutorials as a build process. |
| 4. Tool extractor / CC authoring assistant | Propose single-purpose wrappers, parameterize examples, generate draft ports/dependencies/effects/budgets/check definitions, and map each wrapper to source locations | This is new builder behavior. Treat outputs as drafts subject to schema/static checks and human review; do not let the model define mandatory acceptance policy. |
| 5. Build evidence bundle | Persist source manifest, environment record, tutorial runs, tool mapping, test results, known failures, and hashes as linked immutable artifacts | Current CC metadata is intentionally concise; the complete construction trail needs a versioned artifact contract and retention/indexing. |
| 6. Independent capsule qualification | Run deterministic contract/safety checks and independent reproduction/held-out cases; create admission evidence under protected policy | Existing admission boundary can be reused, but this pipeline needs case preparation, independence rules and a build-to-admission adapter. |
| 7. MCP packaging (optional thin adapter) | Assemble eligible candidate tools/resources/prompts into an MCP endpoint/manifest, with versioned interface and security defaults | Only needed if the first user-facing workflow must expose MCP. It should not become the CC model or duplicate the registry. |

## Recommended first-slice boundary

**Include:**

- One computational methods paper with a known public repository and a clear runnable tutorial.
- One language/runtime (Python) and one environment strategy selected after inspecting the pilot repository.
- One or two narrowly scoped, single-purpose tool candidates derived from the tutorial, with explicit input/output schemas.
- Isolated environment and execution; exact source, dependency, data and implementation pins; retained logs and output artifacts.
- Candidate CC draft generated from and checked against the current schema, with human approval of interface, effects and license/provenance record.
- Independent deterministic contract/safety tests and a small held-out case set authored or adjudicated outside the extractor.
- Existing M1 admission/evidence interfaces reused where implemented; missing interfaces recorded as dependencies, not silently assumed.
- A CLI/build job and a local MCP adapter only if required to demonstrate downstream invocation.

**Exclude:**

- “Any paper” or arbitrary repository conversion; multiple languages, GPU/hardware profiles, private repositories, complex workflow engines, or autonomous dependency repair.
- Automatic publishing/activation without an explicit M2 policy and evidence gate.
- General-purpose composite capsules or internal CC dispatch (M1 marks these as later work).
- Multi-paper knowledge aggregation, discovery-paper/data-resource agentification, scientific hypothesis generation, and a general co-scientist.
- Online adaptation, mutation of a frozen plan, runtime RSI, or recursive modification of the builder/evaluator.
- Claiming scientific validity from tutorial reproduction or LLM-judged outputs alone.

This boundary makes the first question answerable: can one well-supported computational method become a traceable candidate CC that passes independent checks and can be used under the existing runtime contract?

## Effort range

Person-days are elapsed focused work, not calendar duration. Ranges assume one technical lead can reuse the M1 interfaces and existing codebase; they include implementation and developer-level review but not broad product integration. Reviewer days cover method expert/test-case review, not merely attending demos.

| Work package | Engineering person-days | Domain/reviewer person-days | Main uncertainty |
|---|---:|---:|---|
| Pilot selection, source qualification and detailed contracts | 2–3 | 1–2 | Repository cleanliness, license and tutorial suitability |
| Source manifest and build/evidence record format | 2–4 | 0.5–1 | Whether existing artifact references provide adequate storage/indexing |
| Isolated environment provisioning and reproducible tutorial runner | 4–7 | 1–2 | Dependency/GPU/system-package complexity; highest technical uncertainty |
| Tool extraction and draft CC packaging/validation | 4–6 | 1–2 | Tutorial structure and whether functionality separates cleanly |
| Independent contract, safety and held-out evaluation harness | 3–5 | 2–3 | Domain-specific oracle/tolerance and independent case availability |
| Admission/library handoff and optional thin MCP adapter | 3–5 | 0.5–1 | Readiness of M1 admission, storage and MCP interfaces |
| End-to-end hardening, failure evidence, operator docs and demo | 2–5 | 0.5–1.5 | Integration maturity and attributable failures |
| **Total** | **20–35** | **5–10** | Add **10–20 engineering days** if core M1 registry/runner/evidence/admission foundations are not usable. |

The lower end assumes the chosen repository already runs in a conventional environment, examples are small, and M1 interfaces are implemented. The upper end assumes some dependency/environment repair and adapter work, but still one repository and one language. A second repository should be estimated after the first, because it tests transfer and generality rather than just adding another instance; budget roughly **5–12 additional engineering days plus 2–4 reviewer days** if it uses the same stack, with more if it changes environment/tooling assumptions.

The existing local November plan allocates 15 human-days to a broader sequence of integration, one capsule candidate, protected admission, planner improvements, MCTS comparison and regression. These are different units and scopes: the 20–35 engineering-day estimate includes builder implementation, while the 5–10 reviewer days are distinct domain/review effort. Do not treat the earlier 15-day plan as an estimate for this full paper-to-capsule pipeline; reconcile the plan and owners after the M2 PRD chooses the slice.

## Suggested staged gates

1. **Feasibility spike (3–5 engineering days, 1 reviewer day).** Select one paper/repository; prove clean environment setup and successful tutorial run; identify license/data blockers; draft one candidate CC and evidence map. Stop if sources cannot be qualified or the reference method cannot run reproducibly.
2. **Minimum builder path (8–14 engineering days, 2–4 reviewer days).** Build source manifest, isolated run capture, one/two wrappers, draft declaration validation and independent cases. Deliver an immutable candidate plus complete build evidence, even if ineligible.
3. **Governed admission and reuse (6–10 engineering days, 1–3 reviewer days).** Connect to protected admission/library and demonstrate future-plan selection or record the deliberate human gate. Add thin MCP exposure only if it is a required consumer adapter.
4. **Hardening and decision (3–6 engineering days, 1–2 reviewer days).** Exercise negative/blocked paths, reproduce in a clean environment, publish case-level evidence, and decide whether a second repository is justified.

The stage ranges overlap with the package estimate and should not be added to it. Gate 1 is the cheapest way to reduce uncertainty before committing to the full slice.

## Decisions needed before committing effort

1. Which single pilot paper/repository is authorized and suitable (license, data access, runnable examples, domain reviewer)?
2. Is the deliverable a candidate CC and evidence bundle, or must it also be admitted, discoverable and invokable from a plan in the same slice?
3. Is MCP exposure a requirement or merely the paper’s chosen packaging example?
4. What clean-environment target and compute budget are supported? Are GPUs or external APIs allowed?
5. Who owns independent test cases and scientific interpretation review? Which claims require expert judgement?
6. Does protected automatic admission/selectability apply to generated candidates, or does M2 retain explicit human publication approval?
7. Which M1 contracts/services are actually implemented and available to this workstream? The design documents specify interfaces but do not prove implementation readiness.
8. Is the total resourcing budget engineering person-days, human effort, or both, and which named people are available?

## Recommendation

Approve only the **3–5 day feasibility spike** as the next sizing step, then re-estimate from the selected repository and actual M1 readiness. Keep the CC schema unchanged during the spike. Require a concrete schema change proposal only if the pilot demonstrates a consumer-facing need that cannot be represented by a linked immutable build/evidence manifest. This prevents the paper conversion feature from expanding into a capsule-format redesign or an implied commitment to general paper agentification.

## Basis in current artifacts

- M1 CC field reference and schema: `outputs/m1-core-review-2026-10-14/design-package-compact/capsule/declaration.md` and `reference/schemas/capsule-declaration.schema.json`.
- CC lifecycle and boundaries: `outputs/m1-core-review-2026-10-14/design-package-compact/capsules.md` and `capsule/authoring.md`.
- M1 RSI scope and explicit M2 boundary: `RSI Design Docs/DESIGN - RSI M1 v0.2.md`, Sections 1 and 15.
- Existing planning sequence and admission decision: `AI4Research_private_planning/cc-plan-approved-revision-2026-10-14-r2/plan.md` and `decisions.md`.
- Paper2Agent pipeline and limitations: attached `2509.06917v2.pdf`, especially its workflow/methods (pp. 4–8, 18–19) and limitations (pp. 14–15).
