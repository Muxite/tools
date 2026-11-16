# November 10 campaign closeout — preserved evidence and Friday selection

**Jetson evidence update:** [received Jetson findings](../jetson-campaign-closeout-20261110/README.md) and [specific CC design changes](../jetson-campaign-closeout-20261110/cc-design-delta.md) add a per-type graph-dispatch component, existing native builder support and new tool requirements. Earlier Jetson-unreceived statements below describe the prior inspection state.

**New evidence received:** [follow-up verification and corrections](followup-evidence/README.md) confirms up1 MUL_MAT passed and a historical live recovery rehearsal exists. Earlier unresolved statements below record the prior inspection state; do not use them as current negatives. Targeted reuse-hit/alias/graph tests and current integration readiness remain open.

Our objective remains to discover Lab Manager responsibilities and useful build, profiling/test, tool, methodology and engine-component CCs through real inference improvement. Friday demonstrates a few capabilities supported by that work; it does not define the campaign's scope.

**Latest user scope:** one useful tool OR component is sufficient for Friday. The full build/agent/Manager/mock-lab loop is optional. Start with [concrete CC design and verification contracts](next-cc-design.md) and the [self-contained evidence request for the campaign agent](next-agent-evidence-request.md). These refine the earlier pipeline-oriented proposal; no new CC implementation is claimed.

For the underlying findings, read [assessment](assessment.md), [expanded Friday demo plan](friday-demo.md) and [earlier developer handoff](developer-handoff.md). The received documents are [CLOSEOUT](source/CLOSEOUT.md), [START-HERE](source/START-HERE.md) and [artifact manifest](source/ARTIFACT-MANIFEST.tsv).

## What was preserved

- [Original CLOSEOUT.zip](received/CLOSEOUT.zip), moved from Downloads after a second SCP retrieval produced the same SHA256. Its three files exactly match the committed snapshot. SHA256: `22a86aecf415c996a434d6649455722ae5028104cae835de18278726626cedbf`.
- [Committed campaign archive](received/siminfeng-closeout-ecaa4b0-campaign.tar.gz), branch `x86/c2-resume`, commit `ecaa4b0d1ed134d598993ca9f26e21745b0bbd4e`. This commit also matched the host's local `origin/x86/c2-resume` ref at inspection; no fetch or independent remote-ref check was performed. [Expanded source](snapshot/campaign/CLOSEOUT.md): 2,958 regular files. Thirty-six symlinks are retained in the archive and listed in [extraction-links.json](extraction-links.json), without materializing their machine-specific destinations.
- [Runtime evidence archive](received/siminfeng-closeout-runtime-evidence.tar.gz): the host's `lab/export`, profiling and profiler-qualification directories. These were absent from the tracked snapshot. [Expanded export example](runtime-evidence/lab/export/job-85805b616c/att-1/MANIFEST.json).
- [Raw job and overnight logs](received/siminfeng-closeout-raw-job-logs.tar.gz): the host's `lab/jobs` and `artifacts/night/logs`. Separate from the commit snapshot because Git omitted raw stdout/stderr. [Example result](raw-job-logs/lab/jobs/job-85805b616c/att-1/result.json).
- [Acquisition receipt](acquisition.json), [offline record audit](record-audit.json), [audit source](audit_records.py), and [file checksums](checksums.sha256).

The last two archives are live filesystem captures, not Git objects or atomic host snapshots. They preserve paths and original bytes in separate directories. No campaign code was executed. No GPU workload, service stop, branch edit, push, history rewrite or implementation-repository modification was performed. Only temporary export archives were created on the source host. The host working tree had one modified evidence stream; it was not substituted into the committed snapshot.

## Local verification

All four archive hashes checked; the three received handoff files match committed bytes. The offline audit checked 914 referenced stdout/stderr files across 54 saved attempt results, with no missing or mismatched files. Export-manifest checks are in `record-audit.json`. The overnight ledger contains 395 rows. D040's saved benchmark arithmetic recomputes to **+2.1749%** on Granite Q8_0 tg128. Hash agreement establishes internal integrity, not independent provenance or renewed GPU qualification.

## What remains on the source host

This is not a complete backup of the 52 GB campaign directory or external models. Engine image tar (~2.21 GB), model weights (~60 GB), KLD reference logits, component libraries, tensor dumps, ignored source clones and scratch trees were not all transferred. Their reported locations and hashes remain in the received manifest and closeout. Available Nsight `.nsys-rep` and `.ncu-rep` files **were** copied in the runtime archive. Do not delete remote originals. Jetson's branch and its raw measurements were not acquired; UMA findings are relayed claims here.

## Sharing and historical authority

The closeout reports an email in public repository history. These local archives should be treated as research evidence requiring review before public redistribution; no history was downloaded or rewritten. Capture-time privacy control is a concrete Manager requirement. The raw source retains historical contradictions and machine-specific paths. Our assessment is a separate interpretation, not an edit to those records, an adopted final Manager architecture, or evidence of integration with the other team's lab agent.
