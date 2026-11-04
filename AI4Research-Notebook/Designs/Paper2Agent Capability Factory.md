---
id: design-paper2agent-capability-factory
status: proposed
source: Resources/review-batches/2026-10-21-paper2agent/paper2agent-source-review.md
last_reviewed: 2026-10-21
next_action: Compare this proposed factory DAG with the maintained M1 design before implementation; keep it a candidate until a bounded prototype and acceptance evidence exist
---
# Paper2Agent Capability Factory

**Fast feature entrypoint:** [[Capability Capsule Factory Feature]] defines the proposed feature, M1 boundary, inputs/outputs, affected native owners, and build order in one page. This longer note supplies stage detail and source evidence. Both remain proposals; neither is an admitted or implemented M1 factory.

## Reading summary

Paper2Agent is a useful reference for turning a research paper and/or its code into two different products: a reviewed, retrievable paper skill and a tested MCP server bound to selected upstream scientific code. Its reusable pattern is staged work with explicit handoffs, source-linked evidence, independent checks, runtime validation, and a portable package. The reference is a workflow implemented through coding-agent skills and scripts; it is not itself a general-purpose factory executable.

The proposed AI4Research adaptation is a candidate pipeline, not an implemented M1 feature. It keeps general source discovery and acquisition as a reusable capability separate from Paper2Agent-specific transformation logic. It also distinguishes factory stages from the CCs that produce a user's eventual scientific tools and from resources that preserve versioned source and evidence. A factory does not grant a generated CC permission to run: normal admission and runtime controls still apply.

## Problem and intended outcome

AI4Research needs a repeatable way to derive candidate capabilities from scientific material without confusing a paper's claims, repository code, generated wrappers, or validation evidence. Paper2Agent shows a concrete division between paper reading and code-to-tool construction. The intended outcome is a proposed factory workflow that could produce reviewable, provenance-carrying candidate packages while preserving the existing CC admission boundary.

Success for a future prototype would mean that each output candidate can be traced to pinned inputs, concrete upstream operations, reference executions, implementation changes, independent checks, runtime requirements, and package contents. A candidate remains a candidate until the existing product process admits it. This design has not been implemented or run in M1.

## Context and authority

The inspected reference checkout is [Paper2Agent](../../Paper2Agent/README.md) at `8c2d059165ef8cdcb70dbea76655b9c2b55b38e6` (`main`, clean at inspection; `origin` is `https://github.com/jmiao24/Paper2Agent.git`). The exact inspection scope, model, and evidence limitations are recorded in the [source review](../Resources/review-batches/2026-10-21-paper2agent/paper2agent-source-review.md). The authors describe the system in the [Nature paper](https://www.nature.com/articles/s41586-026-11044-y); the local clone includes a paper-reading skill and manuscript files under `Paper2Agent/skills/paper2agent/paper2agent-paper/`.

The reference's top-level skill routes paper inputs to Paper2Skill, code repositories to Paper2MCP, or both to both, and defines a combined output layout ([top-level skill](../../Paper2Agent/skills/paper2agent/SKILL.md)). Paper2Skill builds a compact reading package after page/source review ([Paper2Skill workflow](../../Paper2Agent/skills/paper2agent/paper2skill/SKILL.md)); Paper2MCP selects upstream operations, executes them for reference results, wraps them, verifies independently, validates the runtime, and packages a ZIP ([Paper2MCP workflow](../../Paper2Agent/skills/paper2agent/paper2mcp/SKILL.md)). The repository's normative instructions and scripts are primary evidence for this design; README marketing language is not treated as proof of autonomous operation or scientific reliability.

This note proposes how selected patterns might map to the maintained M1 architecture. It does not change the architecture or claim a factory implementation. The present M1 inventory has no composite/factory CC that performs this workflow. The existing Intention Compiler, Requirements, Planner, semantic Verifier, and runtime CCs remain governed by their maintained contracts; this note is not a substitute for them.

## Proposed behavior and boundaries

### Three kinds of things

Keep these identities explicit throughout the workflow:

1. **Factory CCs and stage CCs** are product-side capabilities that perform bounded work such as source inventory, task selection, wrapper construction, or verification. A factory may coordinate stages, but each stage has a declared input/output contract and evidence obligations. Whether these become individual CCs, one composite, or host orchestration is an open implementation choice.
2. **Generated product CCs** are candidate scientific tools produced for a paper/repository task. They bind to named upstream operations and inherit ordinary review, policy, admission, and runtime requirements. Generation is not admission, activation, or permission to execute.
3. **Resources** are versioned data and evidence: source snapshots or pinned references, paper reading packages, repository manifests, fixtures, tutorial outputs, verification reports, environment locks, and package inventories. They are not arbitrary executable CCs. A resource may contain code as source material, but execution requires an explicit, governed capability that consumes it.

The distinction prevents a source bundle, an agent prompt, or a generated package from being silently treated as an executable capability. It also lets multiple products reuse the same reviewed resources while tracking their exact versions.

### Candidate dependency graph

The candidate factory has two input branches and a convergent product path:

- **Paper branch:** paper and supplied supplementary sources → reviewed, navigable paper resources (text, tables, figures, source maps and review state).
- **Repository branch:** repository locator → general source discovery/acquisition capability → pinned source snapshot and license/availability assessment → environment and reference executions → selected upstream operations and reference outputs.
- **Convergence:** paper resources and/or repository evidence inform task selection. For code-backed tasks, implementation produces thin candidate wrappers tied to selected upstream calls. The runtime stage assembles and tests the candidate package. A separate input-dependent verifier compares behavior with reference executions, changed inputs and relevant failures. An output-only semantic verifier may separately review declarations and exact candidate output for contract/meaning checks; its evidence must not be conflated with input-dependent scientific comparison.

Paper-only work can produce a reviewed reading resource without claiming runnable scientific tools. Repository-only work can produce candidate tools if the paper is unavailable, while recording that limitation. A combined request can share provenance across both branches. A missing dependency, license, credential, dataset, hardware resource, or defensible reference execution blocks or narrows the affected candidate; the workflow records the gap instead of implying success.

### Keep source discovery general

Repository discovery and acquisition should be a general reusable capability, not embedded in Paper2Agent-specific rules. This is a proposed separate, explicitly authorized preparation workflow, not permission for M1 intake or Builder execution to fetch arbitrary sources. Current M1 PRD §3.1.2 accepts a user-supplied local project/code directory and excludes live scraping and direct GitHub cloning during intake ([PRD §3.1.2](../../jiuwenswarm/docs/product/received-prds/prd-m1-v10-2026-10-15.txt)). R5 restricts dependency selection to a protected, reviewed lock catalog; generated code does not resolve/install packages ([R5](../../jiuwenswarm/docs/architecture/design-package/method/decisions.md#r5)). D45 runs Builder tool commands with network disabled ([D45](../../jiuwenswarm/docs/architecture/design-package/method/decisions.md#d45)). Any future acquisition capability therefore needs its own approved scope, authority, execution boundary, provenance and handoff into qualified local resources. Given such authorization, it could identify repository identity/revision, tree and license signals, capture provenance, and expose a stable source snapshot. It must report inaccessible or ambiguous sources and must not infer a license grant from public availability. Paper2Agent-specific selection, extraction, review and wrapper policy then consumes that prepared snapshot. This boundary permits reuse without inheriting Paper2Agent's paper-to-skill/MCP algorithm or weakening current M1 restrictions.

### Candidate stage responsibilities

| Stage candidate | Main responsibility | Evidence/resource output |
|---|---|---|
| Source discovery and acquisition | Resolve user-authorized sources; capture identity, revision, availability and license metadata | Immutable source references/snapshot manifest, source hashes, license and access findings |
| Paper reading preparation | Inventory paper, supplement, tables and figures; extract and organize content for review | Editable review plans, page/source review records, compact paper skill and asset index |
| Task and operation selection | Translate user tasks into useful operations; inspect tutorials plus APIs, scripts, tests and examples; bind each candidate to a concrete upstream implementation | Selection inventory with task/I/O, callable symbol/path, reference source, ownership, decision and blockers |
| Environment and reference execution | Prepare supported runtime and run upstream examples/operations on traceable inputs before wrapping | Pinned environment facts, execution records, input/output provenance and native reference results |
| Candidate wrapper construction | Implement minimal adaptation around the existing upstream operation; retain parameters, defaults and meaningful errors | Candidate product CC/source, source binding, changed-file manifest and wrapper-specific contract |
| Input-dependent independent verification | A fresh verifier compares wrapper with direct upstream results on original and changed inputs, failures and composition where relevant | Independent comparison report, test cases/fixtures, observed deviations and unresolved limits |
| Runtime integration and delivery | Mount only verified candidates; install runtime, run real MCP calls, package and validate from an extracted location | Tool inventory, runtime reports, USAGE, ZIP hash/file manifest and extraction acceptance report |
| Output-only semantic review (separate) | Review the declared capability and exact output against semantic/contract requirements where that is the intended verifier role | Declaration/output review result and rationale, with no claim of rerunning scientific computation |

Paper2Agent's **fresh source-reading verifier** is not the same role as AI4Research's **semantic Verifier**. Paper2Agent requires a verifier to trace wrappers back to source code, independently obtain upstream expected results, and exercise changed inputs and relevant failures (`Paper2Agent/skills/paper2agent/paper2mcp/references/tool-selection-and-wrapping.md`). AI4Research's semantic Verifier is an output-only reviewer of declaration plus exact output. Reuse its contract only for that output-only check; implement the source-reading and input-dependent comparisons as separately specified verification work, with explicit inputs and evidence.

### Gate and failure behavior

Every stage should publish a completion state only when its contract and evidence are present. Worker completion alone is not stage success. Keep selected, merged, internal, deferred and excluded tasks visible with reasons. Do not let easy-to-wrap tasks silently replace requested scope. The Paper2Agent workflow helper itself checks recorded assignment/order/hash consistency but leaves scientific selection and result interpretation to people/agents (`paper2mcp/references/workflow-state.md`).

Treat the final ZIP as a candidate artifact. Its delivery record should bind to the exact package hash, extraction location, runtime identity, installed dependencies, actual tool calls, comparison results and remaining external requirements. Passing selected-tool checks does not establish whole-repository correctness; packaging checks do not establish scientific validity. Admission remains a separate decision under current AI4Research governance.

## Reusable patterns and caveats

The most reusable reference patterns are: source-bound task selection; execution of upstream code before wrapper construction; minimal wrappers; independent verification after all implementation is complete; explicit handoff markers and artifact hashes; fresh-install and real-call validation; and keeping development evidence separate from deliverables. For paper material, useful patterns include editable page review plans, image/contact-sheet review aids, source-hash-bound review reuse, workbook coordinate checks, and strict verification with recorded limitations.

Several limits matter for adaptation:

- Paper2Skill requires inspection of every page and supplied image and does not execute methods or code quoted in the paper. Review can be assigned to agents; the requirement is inspection and evidence, not necessarily human-only interpretation.
- Workbook formula values use cached workbook values; caches may be stale, formulas are not executed, and formula metadata is retained. This needs to remain visible in any derived table resource.
- Paper2MCP assumes a coding-agent host with agent spawning plus Python/Git and may require R, native commands, data, API access or GPUs. Its orchestration instructions are not a host-independent runtime.
- MCP inventory acceptance checks do not compare scientific artifact contents by themselves. The reference separately requires scientific comparisons and actual calls. Its own instructions say selected-tool validation does not prove the whole source repository correct.
- Credentials must be supplied at runtime, and unavailable licenses, dependencies, data, models or hardware can leave a candidate incomplete. A public repository or a successfully assembled ZIP alone does not prove redistribution rights or portability.
- The inspected clone contains skills, scripts, prompts and reference material that depend on a host agent to orchestrate; this review did not run the factory, its scripts, tests, models, or any generated tools. No performance, accuracy, or end-to-end success claim follows from this design.

## Alternatives and open choices

The factory might be one composite coordinating stage capabilities, a host-level workflow over several CCs, or a mixture with non-agent scripts for deterministic packaging and checks. Preserve stage contracts and evidence regardless of the orchestration form. A second choice is whether to make paper review a prerequisite for code-backed candidates or an optional parallel branch; the reference supports paper-only, code-only and combined routes, so the candidate design keeps those branches independently useful.

Before implementation, decide how general source acquisition interacts with credential policy, license assessment, and immutable snapshots; whether resources are content-addressed or revision-addressed; which stages can resume safely; what status marks partial output; and which existing admission gate consumes candidate packages. Settle these choices against the maintained M1 contracts and an actual bounded prototype, not from the reference workflow alone.

## Validation and adoption

This is a proposal only. No M1 implementation, model call, benchmark, MCP conversion, or Paper2Agent end-to-end run was performed for this note. Before adoption, map the proposed stages to existing CC interfaces and gates, identify composites missing from M1, and implement only after the maintained design accepts the change. Validate with source fixtures at a pinned revision, independent upstream/wrapper comparisons, relevant changed inputs and failures, resource/permission checks, clean runtime installation, extracted-package calls, and evidence that no candidate is admitted or executed without normal authorization. Record actual model/runtime identities, exact source and package hashes, skipped checks, and unresolved external requirements.
