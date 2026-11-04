---
id: activity-agentic-builder-pi-20261023
status: candidate
source: Sources/Prompts/2026-10-23-agentic-builder-plan.txt
last_reviewed: 2026-10-23
next_action: Qualify the authenticated Linux Builder and independent Pi benchmark before reviewing M1 integration
---
# Agentic Builder and Pi benchmark

Implemented as a **separate source candidate** on `builder/bounded-build-test-20261023`. Tested implementation commit: `2890421cf6990eb624591b5d330e657d324d91a0`. Documentation/evidence checkout head at this update: `db34c50d1398870f356e6cc65b35c58a61c9436b`. Shared local `ai4r_M1` remains `60f65abe64eb8294f6de6b0413dfb032e2cf86b9`; this upgrade was not merged, deployed or activated in an installed library.

**Live completion is blocked.** No authenticated Codex-built Pi candidate, actual protected candidate execution, separate live verifier assessments or measured Pi improvement was produced. Fixture timings are not performance results. The [recorded preflight](../../AI4Research-Development/jiuwenswarm-m1-current/docs/capsules/agentic-builder-live-preflight.json) found missing governed Linux model/executor sockets and no installed VCS-qualified SDK distribution. Bubblewrap and cgroup v2 are present; presence does not establish full runtime qualification. A separate Windows Docker probe could not connect to its Linux engine. No API key was requested or fabricated.

## What changed

Builder `m1-15` uses the real OpenJiuwen ReAct framework at `9e3390195a9ea15235b2b5f7412cb2aa440622cc`, the framework beneath Jiuwenswarm's code harness. The scoped native client calls the existing governed Codex subscription bridge, preserving protected call identity. It serializes native messages and tool definitions; no separate credential-bearing coding process or SDK-local shell fallback is added.

The agent chooses inspection, hash-guarded edits and patches, compilation, unittest selection, smoke checks, log inspection, repair, submission or a blocked result. Its workspace and conversation persist for that invocation. Limits are 600 seconds, 20 model calls, 40 tool operations and 12 generated development jobs, each at most 30 seconds. Compilation does not execute code. Infrastructure failure and cancellation stop the native invocation before another model call; this required an explicit guard because the SDK can turn tool errors into conversational feedback.

Tests belong to an exact four-file development snapshot. Edits or a subsequent failed check invalidate passing status. Submission packages only `requirements.txt`, `poc_patch.py` and `run_benchmark.py`; `tests.py` stays separate evidence. Receipt 4.0.0 links protected actions, model outputs, revisions, tests and the submitted archive. Independent replay checks, separate per-output verifier calls and protected gates remain. Builder tests do not decide scientific success, and Benchmark never sends a submitted program back for automatic repair.

The classification Benchmark consumer is `m1-7-agent-pi`, with its existing output contract preserved for Evaluation. Pi is a separately pinned `research.benchmark` release, `pi-m1-1`, requiring separate admission. Both use the seven roles: hypothesis blueprint, POC manifest, POC archive, build receipt, baseline resource, validation resource and environment lock. The static Builder allowance reserves 22 calls: 20 work calls and both independent output reviews.

The prepared Pi task supplies interface requirements, public cases and a captured standard-library baseline without claiming Search or Screening occurred. The candidate chooses its algorithm. Independent reference generation uses Decimal Gauss–Legendre and integer Chudnovsky binary splitting; they agree at 100000 places. Reference bytes stay outside Builder tools and candidate mounts. The protocol measures five fresh baseline and candidate processes separately at 10000 and 100000 places, then checks three frozen unseen precisions and four boundary cases. It uses the executor clock, full-prefix correctness, captured hardware and effective CPU affinity. A slower correct candidate is a valid negative result. These checks strengthen resistance to hardcoding; they do not prove every possible program genuinely computes Pi.

## Verification and exact extent

- **62 focused tests passed**, including the real pinned native runtime with controlled model responses. They cover action sequences, failure feedback, targeted repair, stale tests, premature submission, budgets, scopes, cancellation, custody and Pi protocol cases.
- **129 regressions passed; 3 previously excluded scheduler qualification cases remain excluded.** The run includes classification/build receipt, execution, scheduler, release-pin, Planner and independent-review budget checks.
- The committed source was checked in a clean detached checkout. Builder, both Benchmark releases, core Planner and affected PDF checker pins were verified. [Commands, source fingerprints, versions and JUnit receipts](../../AI4Research-Development/jiuwenswarm-m1-current/docs/capsules/agentic-builder-verification.json) retain the exact conditions. Native tests used pinned SDK source imports; they do not qualify the complete installed SDK distribution or the Linux services.
- Earlier candidate `m1-14` at `8e096ef9` and scripted `m1-13` at `79ffb21d` remain historical checkpoints. Their reports are not substituted for this revision's evidence. See [[Activities/2026-10-23 Builder Upgrade]] for the older three-candidate controller.

Three scoped Luna agents (`gpt-6-luna`) implemented components and checks; the supervisor integrated the protected broker, scoring and release paths and ran the actual SDK and regression tests. Source inspection and executable checks corrected agent assumptions, including reference rounding/formatting, native message serialization, artifact joins, and SDK tool-error continuation. No RSI or model-router implementation is included.

## Design amendment and recovery

The [exact approved plan](../Sources/Prompts/2026-10-23-agentic-builder-plan.txt) authorizes this branch amendment to the maintained Builder design's no-execution, no-repair and single coding-process clauses. The design-owner source was reviewed at `889682f0afc3d06c2ad88e71534483a31d2eb560`; document hashes are in the verification receipt. The maintained design repository and historical imported notes were not silently rewritten.

Seven library files were backed up byte-for-byte. The prompt hash, pre-edit receipts, vault validation and local checkpoint status are retained in [the maintenance batch](../Resources/review-batches/2026-10-23-agentic-builder/). Existing unrelated notebook changes are preserved; no remote checkpoint push is performed.
