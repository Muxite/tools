# Muse/Spark procedures and preliminary CC handbook

Start with [HANDBOOK.md](HANDBOOK.md), the complete portable handoff. Its focus is Muse Spark Open inference on one 128 GB DGX Spark. The RTX/Jetson campaigns are supporting evidence, not target qualification. No hardware experiments, model-weight downloads or implementation-repository changes occurred in this task.

## What is here

- Executive summary, six Mermaid diagrams with text fallbacks, eleven named procedures, readable capability cards and multi-CC node toolkit assignments.
- Twelve tool candidates, four component families, Field Guide methodology and a conditional Specialist agent role. These are preliminary reference entries, not eighteen mandatory finalized packages.
- Three worked examples and an eight-item backlog with owners, reusable starting points and acceptance checks. Friday's one-tool demonstration precedes a detailed evidence/source appendix.
- Three GPT-6.1 Sol contributions and second-pass cross-reviews: [methods](reviews/methods.md), [CC construction](reviews/cc.md), [lab and Manager](reviews/lab.md).
- [Source receipts](source-receipts.json): captured official pages/pinned reference files, hashes of local source evidence and installed-versus-pinned Muse comparison. One independent capture of NVIDIA's memory-reporting support page returned HTTP 429; the reviewer consulted it through web access. Do not imply all linked references were downloaded afresh.
- [Validation](validation.json) and [notebook validation](vault-validation.json), which check documentation/navigation/integrity, not runtime correctness.

## Lead reconciliation

**Illustrated revision:** [first edition](history/first-edition/HANDBOOK.md) is preserved. Two GPT-6.1 Sol follow-up reviewers assessed the attached campaign interpretation, planner/recording boundaries and recovery example. The lead added Configuration Planner and Campaign Notebook as bounded proposals; retained host observation/calibration in Resource Watch; and kept routing instrumentation separate from read-only analysis. Command-recording patterns do not grant the Notebook arbitrary execution authority. Damaged attachment figures were not reconstructed. See [revision review receipt](revision/review-receipt.json).

Cross-review found no blocking ownership or mechanism contradiction. Incorporated requested/effective cache accounting; mandatory memory headroom; Muse-specific operator boundaries; one-shot/chunked state equivalence; continuous measurement eligibility; bounded allocation-accounting probes; content-bound idempotency and stale-attempt fencing; acknowledged export coverage; current MCP deadline limitation; and the narrow first NCU CSV backend.

The CC review's categorical “engine outside CC” wording is interpreted as independent engine identity and **no requirement** for a whole-engine wrapper, not a universal prohibition on representing an engine capability through a CC. The handbook states the chosen project boundary. Four component rows are research families until a real integration boundary justifies a release.

Preserved the distinction between three retained Q8 samples per arm and 24 completed jobs in the broader x86 comparison. No change to historical result bytes or component acceptance was made.

## Current notes and delivery

Current-focus notes prioritize Muse/Spark and explain multi-CC nodes. Visible focus/implementation messages and the original attachment are captured with SHA-256 receipts. Before-bytes are retained in the original review batch and `AI4Research-Notebook/Resources/review-batches/2026-11-10-muse-handbook-illustrated` relative to the workspace root. No historical campaign result was rewritten.

Send the single output file `outputs/Muse-Spark-CC-Handbook-20261110.md`. It contains the decisions and evidence limits; companion review/source files remain available for audit. `maintain_notes.py` is a one-time maintenance record with an overwrite guard; do not rerun it as a general updater.
