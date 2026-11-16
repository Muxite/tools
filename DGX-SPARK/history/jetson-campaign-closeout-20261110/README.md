# Jetson closeout — evidence received and compared

The original [jetson-closeout.zip](received/jetson-closeout.zip) is preserved intact after moving it from this workstation's Downloads. SHA256: `dc264ae20bff66451aeac581dae3412375353a6b83c6a9bb5a01e067da076435`. It contains two documents: [CLOSEOUT](source/CLOSEOUT.md) and [START-HERE](source/START-HERE.md), not all underlying results.

To study the referenced implementation and measurements, we also acquired the [committed campaign archive](received/jetson-campaign-73484492.tar.gz) through the existing x86 SSH connection. Both the remote Git branch query and x86's local `origin/jetson/c1` resolved to **`73484492c67cbf5b38d2cd8522f7f780975907aa`**, the final closeout commit. The ZIP's two documents exactly match that snapshot. The earlier `01fa56c` in the draft identity table is superseded by this observed final commit.

Start with [findings and evidence limits](assessment.md), then [specific CC and demo implications](cc-design-delta.md). The central goal remains discovering useful Manager/CC designs through engine improvement. One useful tool OR component is enough for Friday; the whole orchestration loop remains optional.

## What is locally checked

- Archive hashes and safe extraction; 2,357 regular files in the committed snapshot. Twenty-five special/link members remain in the original tar and are listed in [extraction-links.json](extraction-links.json), not materialized locally.
- [Offline arithmetic audit](record-audit.json) of J-E007 raw benchmark samples: BF16 **+19.2118%**, mixE4K/Q4_K **+23.6409%**, Q8_0 **−6.2146%**. These use the lane's declared rule: discard sample one of each five-sample invocation, average the remaining samples, then average the two invocations per arm. They are not fresh measurements or cross-host speed comparisons.
- mixE4K greedy output files have equal full hashes; printed PPL/KLD/top-1 summaries match between the two dispatch arms. Those KLD values are against the saved BF16 reference, not a direct zero-KLD comparison of candidate versus baseline and not raw-logit parity.
- SPEC2 saved per-request records recompute to **+63.14% rewrite** and **+96.81% repeat**. Stored output hashes are matching 12-hex prefixes. No broad chat/task-quality conclusion follows; the chat arm was invalid.

## Important limits

The committed snapshot omits **376 stdout/stderr files referenced by lab attempt results**, including Jetson-local jobs. None of those referenced raw lab files could be hash-verified from this snapshot. This contradicts a blanket reading of “all raw logs committed”; experiment-level JSON, text and telemetry files do exist and support the checks above. Missing files are listed in the audit. Do not call this a complete lab-evidence backup.

Images, model weights, source clones, build caches and some profiling/base-logit artifacts remain on Jetson. This package is a read-only evidence snapshot, not a runnable deployment or full host backup. The source has historical contradictions and stale subheadings; our interpretation is separate. No Jetson SSH access change, build, test execution, profiler capture, GPU operation, service change or push was performed. Source-host state is reported by the closeout, not freshly observed here.

Receipts: [acquisition](acquisition.json), [validation](validation.json), [checksums](checksums.sha256). The [x86 evidence package](../inference-campaign-closeout-20261110/README.md) remains separate: different commits, model hashes, memory systems and decision-number namespaces.
