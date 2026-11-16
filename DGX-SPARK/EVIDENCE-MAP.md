# Evidence and provenance map

## Included layers

| Directory/file | Purpose and authority |
|---|---|
| README/INTENT/CURRENT-STATE/FACTORY-LOOP/NEXT-AGENT | New synthesis for this handoff; separates current user direction from inspected historical claims |
| REMOTE-SNAPSHOT.json | UTC capture time, live source HEAD/branch/dirty paths, selected file hashes and size omissions |
| reference/factory-source/docs/architecture/factory | Detailed current architecture, runbooks, research, measured reports and caveats |
| reference/factory-source/jiuwenswarm/factory | Selected actual implementation and CC library, including captured uncommitted development |
| reference/factory-source/tests/factory | Existing regression/acceptance source, not newly executed results |
| reference/factory-source/deploy/spark and scripts | Deployment/mission source with external dependencies; historical deadlines require fresh contracts |
| reference/spark/results | Top-level retained structured proofs, summaries, identities and failure records |
| reference/spark/night-* and development-* | Selected experiment/analysis/agent output records |
| reference/night-evidence | Exported night handoff evidence, with duplicate installed stores excluded |
| reference/spark/handoff-* | Archive/image manifests, qualification and cleanup records, not bulk images |
| history | Jetson/x86 closeout lessons, lab research, Muse handbook, earlier Spark setup and Windows handoff |
| SOURCE-INDEX.json | Every imported file's original path, digest, bytes and packaged path |
| MANIFEST.json | Integrity hashes for all delivered files except itself |

## Key reading routes

- **Latest changes and unresolved work:** CONNECTED-DEVELOPMENT-2026-11-16.md, DEVELOPMENT-REVIEW-2026-11-16.md, CPU-CAMPAIGN-SPEC.md.
- **Engine results and contradictions:** NIGHT-BRANCH-RESULTS.md, SPARK-FACTORY-EXPERIMENTS-2026-11-14.md, SPARK-BROAD-CAMPAIGN-RSI-RESULTS.md, GPU-COMPONENT-EXPERIMENTS.md.
- **Agent operation:** CONTROLLER.md, TASK-GRAPH.md, BRANCH-WORKBENCH.md, SPARK-AGENT-IMPROVEMENT-2026-11-14.md, INFERENCE-FACTORY-LOOP.md.
- **CC semantics and RSI:** CCV2-REVISION.md, CC-JOB-PACKAGES.md, CC-PACKAGE-VERIFICATION-ALIGNMENT.md, RSI-HANDOFF.md, NIGHT-BRANCH-METHODOLOGIES.md, EVIDENCE-DIGEST-LAB.md.
- **Migration:** REPOS.md, LINEAGE.md, MIGRATION.md, Jetson branch record, historical closeout assessments.

These filenames are under reference/factory-source/docs/architecture/factory unless a different path is given. Historical source links may point to the full original checkout or omitted evidence; do not treat them as bundled merely because a narrative links them.

## Collection limits

This is a selected readable source/evidence package, not a disk image or complete campaign export. Per-file collection cap is1.5MB. Included formats are source, Markdown, JSON/JSONL, YAML, CSV, text, patches and checksum records. Installed/runtime stores, credential state, environments, model weights and bulk binary/image archives are excluded. The original export receipts identify larger transfer packages. REMOTE-SNAPSHOT lists size-based omissions; directory/format exclusions are defined by collect_context.py.

Files were read from a live machine and individually hashed. This is not an atomic filesystem snapshot; verify live changes before resuming. No runtime database was copied and no live experiment was started/stopped. Historical exported files can overlap current source; source paths distinguish them. The final selected factory source is clean at the recorded commit; the earlier collection saw development in progress and was refreshed after it was committed. External run artifacts still require their own hashes and do not follow from the code commit.

Thread provenance for explicit November13 decisions: Codex chat “Build DGX Spark software factory”, id01a1d70d-28db-7253-aa06-c9ffc188eaa4. Current intent: November15 “Package DGX Spark work context”. Full chat dumps and unrelated personal content are not published. Newer scientific facts come from inspected Spark source/evidence rather than that older chat.
