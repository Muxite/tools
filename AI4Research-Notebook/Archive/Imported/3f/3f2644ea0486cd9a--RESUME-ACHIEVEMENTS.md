# Resume achievements: Capability Capsule schema (Huawei, AI4Research, Sep 2026)

Short, factual lines for the resume writer library. Every figure below can be traced to a file in this repo.

## One-line summary

Designed the Capability Capsule schema, the declarative contract that every capability in Huawei's openJiuwen-based
AI4Research system declares, grounded it in 21 research papers read in full, and checked every integration claim
against source code.

## Achievements

- **Designed a schema, not a tool.** Wrote the Capability Capsule schema (v1.6, then a merged v2.0): a hashed manifest
  plus admission, standing, binding and finding records, with 8 to 11 invariants, used by the planner, verifier,
  screener, router and self-improvement (RSI) teams.
- **Made safety declarative.** Replaced heuristic candidate filtering with *predicate parity*: the planner's filter, the
  dispatch check and the capability's own exit logic evaluate one declared predicate, tested on boundary, missing and
  stale state before it may filter.
- **Grounded every design choice in research.** Read 21 papers in full and built a page-level evidence ledger; each
  schema field names the tool that reads it and the paper that motivates it.
- **Quantified the token case.** Scoped published savings (59.1% and 90.5% of selection-description tokens; 26,172 to
  2,528 tokens a task in another study) to the AI4Research workflow, and designed the measurement against today's
  filter rather than assuming it.
- **Designed for safe composition without overclaiming.** Mapped the schema's fields onto a composition screener's
  inputs (SkillFuzz, 80.6% of high-risk flags confirmed in execution), and added spatiotemporal composability
  (add, replace, revert, remove) from the Cordis model.
- **Verified integration in source.** Traced hooks and gaps across agent-core, Symphony, skillhub, ScienceDiscovery and
  the existing AI4Research harness to file and line, e.g. that the extension binder loads by name with no hash check.
- **Derived the schema from evidence and code.** Built a derivation matrix from each source finding, through the
  requirement it sets, to a schema element: 20 directives, 21 papers, the pipeline code, agent-core, and jiuwenswarm's
  34-skill corpus. It showed that none of those skills declares inputs, outputs or effects, and that the RSI loop
  accepts candidates only on cases it was optimised on. Both findings shaped schema v2.1.
- **Ran staged adversarial review.** Put the deliverables through independent reviewers (Haiku, then Sonnet, then
  Opus) plus my own pass, verified every finding in the paper or code before acting, and logged each verdict.
- **Explored an alternative design and merged the best of both.** Commissioned an independent design written without
  sight of the first, compared them row by row, and merged them into one schema.
- **Delivered the workshop package.** A 28-slide deck with 10 backups, a companion report, an independent report
  (36 pages), purpose-drawn diagrams, paper-figure appendix, a topic register to prevent silent loss, and handoff notes.

## Skills shown

Schema and API contract design · agent systems and tool/skill registries · verification and safety engineering ·
research synthesis · source-code auditing (Python) · technical writing and presentation · review process design ·
Python tooling (matplotlib, PyMuPDF, docx and pptx builds).
