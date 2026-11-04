---
id: activity-reliability-reproduction-20261026
status: verified-development-checks
source: Sources/Prompts/2026-10-26-reliability-and-reproduction.txt
last_reviewed: 2026-10-26
next_action: Prepare protected live isolated evaluation captures, then complete Pi and scientific acceptance
---
# Reliability fixes and reproducible checks

Current integration source `e1ca360c087cf612f34056a3f137c86300a79e5f` on `m1/all-features-20261025`; local M1 `e1ca360c087cf612f34056a3f137c86300a79e5f`. The verification source is `176a0ae864250053b1921e7e5fcd94741b81ad8c`. This extends [[Activities/2026-10-26 M1 Docker Development and Test Preparation]] and supersedes its pending legacy status-fixture result. Exact logs, JUnit, manifests and commands are retained in [the verification receipt](../../AI4Research-Development/jiuwenswarm-m1-reviewed-integration/docs/capsules/verification-20261026/reliability/summary.json).

## What changed

An adversarial test exposed an interrupted-status custody gap: after recovery recorded an interrupted dispatch, a substituted child-contract assignment escaped the reader's older open-attempt validation. The reader now joins interrupted attempts to their original parent, assigned template, declaration, admission and checking profile. The existing corruption test still requires rejection. No acceptance or source-integrity check was relaxed.

The stale test interceptor now stops the actual workflow before its first callback, preserving pending nodes. The controlled Hypothesis fixture generates the currently registered metrics and rules, leaving the historical source fixture unchanged. Recovery assertions require durable interrupted records and Failed lifecycle state, with no fabricated completion time/output/containment. These fixture corrections are not new live scientific results.

The PowerShell launcher runs named isolated groups inside the existing Docker verification target. It resolves the immutable image ID, uses read-only source, disables networking, bounds memory/PIDs/time, preserves failures and refuses evidence overwrite. It hashes source before and after tests; changes invalidate a passing exit. Repeats receive separate containers and receipts. No host Python, API key, credential import or new service is required.

## Passing extent and reproduction

| Group in the combined run | Passed | Failures/errors | Skipped |
| --- | --- | --- | --- |
| capabilities | 38 | 0 | 0 |
| replay | 8 | 0 | 0 |
| status | 31 | 0 | 0 |
| planner | 26 | 0 | 0 |
| builder | 42 | 0 | 0 |
| benchmark | 32 | 0 | 0 |
| completion | 28 | 0 | 0 |
| executor | 10 | 0 | 0 |

Combined: **215 passed**, **0 failures**, **0 errors**, **0 skips**. Earlier capability repetitions each passed 38 checks on identical captured source bytes; they are not 76 unique cases. The deliberately short timeout returned 124 and retained evidence. The source-change negative control is recorded separately; neither is counted as a passing capsule run.

From the integration repository root in PowerShell:

```powershell
./deploy/m1/check-capsules.ps1 -Group all -Build
./deploy/m1/check-capsules.ps1 -Group capabilities -RepeatCount 2
./deploy/m1/check-capsules.ps1 -Group replay -Case tests/unit_tests/research/test_evaluation_replay.py::test_actual_verifier_rejection_halts_valid_replay_with_call_evidence
```

Use a fresh `-Output C:/Temp/my-new-check` to select a destination. The recorded run used `-Image ai4r-verify:20261025` at `sha256:09979a044c9eace8e3ef17cd142eb26a27306e14ea80939c0628356eaca2e97a` with the current source mounted read-only. Each run retains `launch.json`, `source-manifest.json`, `pytest.log`, `junit.xml` and `result.json`. Compare image ID, source manifest and selected targets before treating a reproduction as equivalent. Overlapping earlier suites are not added to this total. [Detailed reproduction guide](../../AI4Research-Development/jiuwenswarm-m1-reviewed-integration/docs/capsules/reliability-reproduction.md).

## Runtime and limits

Rebuilt app image: `sha256:973d0b5c9e5b68c174e38fd66527edc238889807555f89f698edbc9afaba53c8`. Build identity: `d0e550ed55098aad805262be36b57468d2416041e282eec57831dc67e63b5680`. Authenticated runner readiness and status access to the previously completed PDF run were checked after restart. This did not repeat its 11 model calls or establish a new research result. Existing ChatGPT sign-in was retained; scoped credentials were refreshed only within the private Docker volume.

The development tests use controlled model replies, actual capsule/check code and native SDK mechanics. They establish verifier-stop mechanics, not live semantic judgment quality. Live E2/E3 evaluation still needs protected profile/assets/runtime authoring; the product has no evaluation profile. Accepted live Pi artifacts, independent Pi timings and full scientific acceptance remain pending. Earlier failed/interrupted attempts remain historical evidence. No RSI, model-router or M2 lab work was added.

## Maintenance custody

Seven library files were backed up byte-for-byte as `.snapshot` files with SHA256 receipts. The exact request and capture hash are preserved. Validation and the scoped Git checkpoint are retained in [the maintenance batch](../Resources/review-batches/2026-10-26-reliability-reproduction/). Imported archives and unrelated notebook work were preserved.
