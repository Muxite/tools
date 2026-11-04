---
id: activity-builder-upgrade-20261023
status: candidate
source: Sources/Prompts/2026-10-23-builder-upgrade.txt
last_reviewed: 2026-10-23
next_action: Qualify an authenticated Codex-to-executor run on the exact upgraded build before merging or claiming runtime readiness
---
# Builder upgrade

Implemented on `builder/bounded-build-test-20261023`, final local commit `79ffb21d4c85c30d5295190e535e2a854832d4c4`. This branch is separate from shared `ai4r_M1` at `60f65abe`. It is not pushed, merged, deployed, newly admitted or runtime-qualified.

The [implementation and design comparison](../../AI4Research-Development/jiuwenswarm-m1-current/docs/capsules/builder-upgrade.md) explains the new flow. Builder now allows an initial candidate plus two repairs. Codex supplies code and a unittest suite through the existing subscription; the protected host provisions the exact offline lock, runs the suite and a separate prediction smoke job, then returns bounded diagnostics. The delivered ZIP still has exactly three files; the suite and raw test evidence remain separate. Maximum Builder work is 600 seconds, each job 30 seconds, with at most six jobs and one MiB per output stream.

Existing Jiuwenswarm components provide model-call custody, lock provisioning, read-only resources, namespace/cgroup execution, durable invocation RPC claims, checks, per-output reviewers and gates. Independent checks join every tested candidate to the protected model response and require the final submitted bytes to equal the final tested bytes. Benchmark still provisions its own experiment environment, runs baseline first and owns private-label scoring; producer tests cannot establish scientific success. No RSI or model-router implementation was added.

## Design amendment and compatibility

The [exact user direction](../Sources/Prompts/2026-10-23-builder-upgrade.txt) explicitly changes the maintained Builder design's no-execution/no-install/no-repair clauses and single tool-using CLI approach. The branch uses bounded subscription text calls plus credential-free generated-code jobs, so it does not need a new API key or remove the old isolated CLI's dedicated-credential requirements. This is an authorized branch amendment candidate, not unchanged compliance or a silent central-design revision.

Builder is `m1-13`; its Benchmark consumer is `m1-6-builder-tests`. Prediction build receipt 3.0.0 records actual development execution and test-report Refs. Core Planner `m1-14` corrects only its description of that host-record contract. Static-plan pins and its five-call Builder allowance include all three edits and both independent reviews; scheduler and recovery readers consume the versioned receipt. PDF and unrelated scientific release pins remain unchanged. This retains the current M1 classification scope, not a generic repository Builder.

## Verification and extent

- Linux/WSL root: **121 passed, 3 deselected** in 61.49 seconds. Controlled model/kernel fixtures exercise loop limits, failure feedback, cancellation, identity/byte substitutions, smoke-output parsing, isolation rejection, durable replay, static pins and protected budgets.
- A fresh Windows checkout of implementation commit `5bc3ca70` passed **15 focused checks**, and verified Builder/Benchmark, core Planner and affected PDF checker pins. The final commit changes only verification documentation. Temporary verification worktree was removed cleanly.
- [JUnit evidence](../../AI4Research-Development/jiuwenswarm-m1-current/docs/capsules/builder-upgrade-linux-checks.xml) and [exact commands and limits](../../AI4Research-Development/jiuwenswarm-m1-current/docs/capsules/builder-upgrade-verification.json) remain in the branch.
- The same three connected scheduler owner-boundary cases remain excluded; they are not passes. No guards were weakened to satisfy them.
- No authenticated Codex-to-executor campaign, actual new Builder namespace/cgroup qualification, target deployment, private-label result or measured improvement was demonstrated. Local WSL lacked `bwrap`. Tests do not establish production readiness.

A Luna agent implemented the bounded host test service and reviewed the integration. The supervisor implemented orchestration/checks and corrected review/fixture assumptions against actual store behavior. Agent assertions were checked against source and executable tests; one alleged manifest-kind defect was disproved because the actual store reads schema-valid JSON blobs.

Five notebook files were backed up byte-for-byte before this update. The exact prompt, SHA-256 capture receipt and pre-edit receipts are retained in [this maintenance batch](../Resources/review-batches/2026-10-23-builder-upgrade/). Earlier final-merge and delivery notes remain intact.
