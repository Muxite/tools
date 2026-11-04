---
id: paper2agent-source-review-2026-10-21
status: reviewed
source: Paper2Agent@8c2d059165ef8cdcb70dbea76655b9c2b55b38e6; repository https://github.com/jmiao24/Paper2Agent
last_reviewed: 2026-10-21
next_action: Recompute source identity and review relevant files at the exact checkout before any future adapter or implementation
---
# Paper2Agent source review

This is a bounded, read-only review supporting [[Designs/Paper2Agent Capability Factory]]. It records what the checked-in instructions and scripts say; it is not an implementation specification from the Paper2Agent authors beyond their paper, nor evidence that the workflow was executed successfully.

The parent review batch's [source receipt](source-receipt.json) records bounded SHA-256 receipts for the selected Paper2Agent and M1 files. The receipt establishes the exact bytes captured for that review scope; it does not make the inspection exhaustive.

## Source identity and method

- Checkout: `C:/Users/m50066326/huawei/Paper2Agent`, branch `main`, clean at inspection (`git status --short --branch` returned `## main...origin/main`).
- Pin: `8c2d059165ef8cdcb70dbea76655b9c2b55b38e6`, dated `2026-09-17T09:56:07-07:00`, commit subject `Add Nature citations`.
- Remote: `https://github.com/jmiao24/Paper2Agent.git`.
- Model used for this source-reading task: `gpt-6-luna`.
- Reviewed README, top-level skill, Paper2Skill and Paper2MCP skills, selected scripts and workflow/runtime/verification/delivery references. No files in the reference checkout were edited. No Paper2Agent scripts, tests, factory/runtime model calls, generated MCP server, benchmark or end-to-end conversion were run; model calls used to author this source review/design note are not evidence about the factory.
- Notebook search excluded `Archive`, `Imported`, migration data and the large imported corpus. At search time, the Notebook had no authored technical Paper2Agent analysis; its source collection indexes the third-party repository in place. This review batch is new authored analysis, not a claim about earlier notes.

The authors' primary publication is [Nature, “Reimagining research papers as interactive and reliable AI agents”](https://www.nature.com/articles/s41586-026-11044-y), DOI `10.1038/s41586-026-11044-y` as cited in the repository README. Local manuscript navigation lives at [`paper2agent-paper/SKILL.md`](../../../../Paper2Agent/skills/paper2agent/paper2agent-paper/SKILL.md); the review here focuses on the skill workflows and code, not a full manuscript reanalysis.

## Short pipeline summary

The top-level skill routes paper sources to Paper2Skill, code repositories to Paper2MCP, and combined requests to both. The two branches have separate work directories and deliverable contracts. Combined output is a paper skill alongside an MCP project. A blocked branch yields a partial combined result. See [`SKILL.md`](../../../../Paper2Agent/skills/paper2agent/SKILL.md), especially the routing and output contract.

Paper2Skill snapshots supplied sources, prepares editable review plans, extracts a fixed package, supports review aids and source-hash-bound review reuse, builds the reading skill and verifies it. Its output includes `SKILL.md`, an index, continuous paper/supplement Markdown, and categorized figures/tables. Review plans, originals and verification evidence stay outside the reading package. The documented CLI stages and their implementation locations are in `paper2skill/scripts/paper_bundle.py`: `prepare` line 226, `extract` 341, `reuse_review` 361, `review_aid` 413, `build` 486, `verify` 508, and CLI setup 513. Parsing helpers are in `paper2skill/scripts/pdf_to_skill.py`.

Paper2MCP has six gated stages: environment and tool selection; source execution/reference results; implementation then independent verification; MCP integration; runtime installation validation; documentation and ZIP delivery. The workflow and non-negotiable source-binding/verification rules are in [`paper2mcp/SKILL.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/SKILL.md). Its final artifact is `dist/<repo>-mcp.zip` with recipient-facing usage instructions and runtime dependencies. Client registration is only done when requested.

## Detailed routes and evidence

### Top-level routing and product shape

[`Paper2Agent/skills/paper2agent/SKILL.md`](../../../../Paper2Agent/skills/paper2agent/SKILL.md) routes by supplied inputs: paper and supplementary PDFs/files use Paper2Skill; Python/R/CLI code uses Paper2MCP; both use both workflows. Combined layout is `dist/<project>-agent/skill/<paper-name>/` plus `mcp/<repository-name>-mcp/`. It requires each component's own instructions and separate working directories. README lines 13-33 give the general Quick Start; lines 36-96 show task/tutorial filters and environment-based credentials. The README describes the project as “automatic” and “minimal human input,” but stage instructions show extensive agent-run review and explicit evidence gates. The headline alone is not evidence of autonomous correctness.

### Paper to reading resource

[`paper2skill/SKILL.md`](../../../../Paper2Agent/skills/paper2agent/paper2skill/SKILL.md) requires `paper_bundle.py` for conversion and explicitly states that paper content is not executed. The normal deliverable is `<identifier>-paper/` with `SKILL.md`, `references/index.md`, `references/paper.md`, `references/supplement.md`, and `assets/{figure,supp_figs,table,supp_table}`. Original sources, review plans, previews, contact sheets, metadata and verification reports remain in the work directory.

Documented path:

1. `prepare` inventories sources and creates editable `bundle.json`; the reviewer routes source role/title/asset names and tables.
2. `extract` creates page/source evidence; `review-aid` compiles contact sheets and a queue of unreviewed pages, extractor warnings, margin furniture, possible joins and verification diagnostics.
3. Reviewers inspect every page and supplied image, correct reading order, hierarchy, cross-page text, equations, code, figures, captions and table relationships, and record page/source review notes. Multiple agents may handle exclusive pages; the coordinator reconciles shared decisions and a fresh verifier compares the result to visible originals.
4. Build the package, inspect representative text/tables/captions and the smallest labels, answer a retrieval question using only the package, then run strict verification.

`paper_bundle.py` defines source handling and commands (`paper_bundle.py:83-207,226-360,361-485,486-571`). Workbook tables are read from OOXML. Hidden rows/columns, merges, cached formula values and metadata are retained; formulas are never executed (`paper_bundle.py:83-87,144-168`). Formula caches can be stale, and cells without cached values export formula text with a warning (`:149-153`). The verification rereads workbook snapshots and checks exported CSV coordinates (`:175-207`).

Paper2Skill has explicit results: `mechanical_failure`, `unreviewed`, `unresolved_discrepancies`, `reviewed_with_limitations`, and `reviewed`; strict mode fails on the first three (`paper2skill/SKILL.md:98-109`, code `paper_bundle.py:508-571`). It requires source/page inspection; this does not mean only humans may interpret sources. Work can be assigned to reviewers/agents under the specified review protocol.

### Repository to candidate MCP package

[`paper2mcp/SKILL.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/SKILL.md) describes a six-stage coordinator/specialist workflow with completion markers. The orchestrator instructions specify workspace setup, assignments, handoffs, retries, and resume behavior. The reference assumes a host able to spawn agents. Python is the default stage route, with separate R and CLI routes. Its main boundaries:

1. **Select useful tasks.** Begin with tutorials, then inspect README, public API/CLI, official examples and tests. Bind each candidate to actual pinned source code and a defensible verification source. Record task/I/O, implementation symbol/path, evidence, decision and owner. Match explicit user scope; do not broaden an unmatched filter.
2. **Execute source first.** Run upstream operations with traceable inputs before writing wrappers. Preserve native numerical/structural results, figures, metadata and reproducibility settings.
3. **Implement narrowly.** Prefer direct upstream API, intended CLI, or attributed tutorial extraction when no callable implementation exists. Do not invent scientific algorithms. Keep necessary input-contract checks, supported parameters, upstream defaults and error semantics. Do not move benchmark recomputation into production wrappers.
4. **Verify independently.** After implementation work completes, use fresh agents distinct from implementers. Trace every wrapper to source, independently run upstream references, compare original and changed inputs, test relevant errors/composition and review for duplicated or changed scientific logic.
5. **Integrate and validate runtime.** Mount only verified operations; install the pinned project/runtime, launch MCP, compare expected tool inventory and input schemas, and execute positive calls for each tool.
6. **Document and deliver.** Include `USAGE.md`, runtime assets and fixed dependencies; create a ZIP, extract at another path, install from the package, and run real calls against the extracted server. Keep scientific reports outside the default package.

Important local references:

- [`tool-selection-and-wrapping.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/references/tool-selection-and-wrapping.md): source-grounded operation selection, wrapper rules and fresh independent verifier requirements.
- [`orchestration.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/references/orchestration.md): host-provided agents, concurrency, environment ownership, limits and handoffs.
- [`runtime.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/references/runtime.md): environment and execution evidence rules; FastMCP baseline and route requirements.
- [`runtime-verification.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/references/runtime-verification.md): acceptance cases, tool inventory, schemas, actual calls and limits of the helper.
- [`workflow-state.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/references/workflow-state.md): assignments, hashes, markers and gates.
- [`output-delivery.md`](../../../../Paper2Agent/skills/paper2agent/paper2mcp/references/output-delivery.md): ZIP structure, relocation acceptance and completion evidence.

### Candidate factory concepts for AI4Research

This is an interpretation proposed in the linked design note, not a feature found in M1 or a claim that Paper2Agent uses AI4Research's architecture.

- Keep general repository source discovery/acquisition independently reusable: resolve an authorized source locator, pin identity/revision, retain provenance and source/license/availability findings, and hand a stable versioned source resource downstream. Paper2Agent-specific extraction and tool selection consume that resource.
- Keep factory/stage CCs distinct from generated scientific product CCs. A factory produces candidates and evidence; it does not admit, activate, or grant run permission to a candidate.
- Treat source snapshots, reading packages, environment locks, tutorial outputs and reports as versioned resources/data. Their contents are not arbitrary executable CCs. Execution must happen through an explicitly governed capability.
- Preserve parallel provenance branches: paper → reviewed paper resources; repository → environment/reference execution → selected upstream operations → candidate wrappers → runtime-validated package. Independent comparisons depend on inputs and reference results; an output-only semantic review remains a separate role.
- Paper2Agent's verifier is richer in a particular direction: it reads source implementations and independently runs calls to compare wrapper behavior. AI4Research's semantic Verifier checks declaration plus exact output as an output-only review. These roles should not be merged or claimed equivalent.

The proposed separate source-discovery/acquisition capability must respect the current M1 boundary. PRD v10 §3.1.2 (lines 873-887) accepts user-supplied local project/code directories and explicitly excludes live web scraping and direct GitHub cloning during intake. R5 says dependency selection comes from a protected, reviewed lock catalog; generated code declares dependencies but does not resolve or install packages (`jiuwenswarm/docs/architecture/design-package/method/decisions.md:23-25`). D45 confines the Builder CLI to the POC workspace with `workspace-write`, network disabled for tool commands, approvals never, and a dedicated budget-limited revocable credential (`.../decisions.md:184-186`). Thus source acquisition here means a future separately authorized preparation path whose permitted reads, identity, environment, provenance, and transfer into qualified local resources are designed and reviewed independently. It does not authorize an intake clone, Builder network access, arbitrary dependency resolution, or a change to M1 execution policy.

### Constraints and evidence boundaries

- **Host/runtime:** README prerequisites include a coding-agent host with skill support, shell and parallel subagent spawning, plus Python/Git; selected repositories may require R, native CLI, data, API access or GPU (`README.md:99-102`). Orchestration is host-assisted, not a host-independent application runtime.
- **Source/license/resources:** Runtime instructions require importing the requested project and verifying module origin and version (`runtime.md:7-11`). The package must carry or document the upstream implementation and relevant notices; credentials stay external. A public URL does not establish source availability, redistribution rights, or dataset/model access.
- **Paper extraction:** Review remains necessary for every page and image. The paper skill does not execute methods or paper code. Image-only content and workbook formula caches retain limits even after mechanical checks.
- **Verification:** `verify_mcp_server.py` checks inventory, schemas, and saved MCP calls; its helper does not inspect scientific values in produced files. Those require independent scientific checks (`runtime-verification.md:40-46`). Workflow hashes/order are bookkeeping controls, not reruns of scientific cases or numerical interpretation (`workflow-state.md:132-144`).
- **Scope:** The instructions explicitly state selected-tool validation is not whole-repository correctness (`paper2mcp/SKILL.md:47`). The ZIP/runtime route can remain incomplete where external credentials, datasets, models, GPU or native software are unavailable (`output-delivery.md:17,33`).
- **This review:** Documentation/script inspection only. No Paper2Agent pipeline, paper bundle, MCP server, generated tool, tests or benchmark was executed. Nothing here demonstrates adapter fidelity, effective runtime/model route, semantic accuracy, actual cost, portability, or deployment isolation.

## Source map

The exact pinned tree is available under [`Paper2Agent`](../../../../Paper2Agent/README.md). Key paths at that pin:

| Role | Path |
|---|---|
| README / user-facing overview | `Paper2Agent/README.md` |
| Overall route / combined contract | `Paper2Agent/skills/paper2agent/SKILL.md` |
| Paper workflow and review protocol | `Paper2Agent/skills/paper2agent/paper2skill/SKILL.md` |
| Paper bundle commands / workbook handling | `Paper2Agent/skills/paper2agent/paper2skill/scripts/paper_bundle.py` |
| PDF extraction and verification | `Paper2Agent/skills/paper2agent/paper2skill/scripts/pdf_to_skill.py` |
| Paper bundle behavioral tests (inspected, not run) | `Paper2Agent/skills/paper2agent/paper2skill/scripts/test_paper_bundle.py` |
| Repository-to-MCP workflow | `Paper2Agent/skills/paper2agent/paper2mcp/SKILL.md` |
| Source selection, wrappers and independent verification | `Paper2Agent/skills/paper2agent/paper2mcp/references/tool-selection-and-wrapping.md` |
| Runtime acceptance boundaries | `Paper2Agent/skills/paper2agent/paper2mcp/references/runtime-verification.md` |
| ZIP/package delivery contract | `Paper2Agent/skills/paper2agent/paper2mcp/references/output-delivery.md` |
