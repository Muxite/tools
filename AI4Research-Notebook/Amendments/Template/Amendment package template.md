---
id: amendment-package-template
status: template
source: Local authored template
last_reviewed: 2026-10-21
next_action: Copy into a new package and assign new AM identifiers
---
# [Package title]

**Package ID:** `AM-[DOMAIN]-NNN`
**Status:** `proposed-user-authorized-preparation`
**Priority / phase:** [priority; preparation only or future-soon]
**Owner:** [role]
**Rollback owner:** [role]

## Purpose and reading order

State the proposed question, why this package improves quality/testability/effort, and the exact order to read its local evidence. Keep it self-contained; list only external sources required for implementation and mark them `coder lookup required`.

## Baseline and compatibility

Record source commit, runtime pin, current behavior and evidence excerpt with SHA-256 receipt. Preserve existing `TASK`/`AC`/`IF` identities. Define new criteria under package-local `AM-*` IDs. State interface compatibility and what this package explicitly leaves unchanged.

## Proposed amendment

Describe smallest useful change, authority owner, data flow, readiness blockers and explicit exceptions. State whether proposed preparation is already user-authorized. Preparation does not imply product acceptance or deployment authorization.

## Acceptance criteria

Use observable outcomes with a test or evidence source for each. Include positive, negative, failure, cancellation and recovery cases as applicable. A missing mandatory check is `blocked`, never a pass.

## Required evidence

List source/runtime pins, case or run identities, config and resource limits, raw outputs, hashes, evaluator versions, failures, logs and custody needed to reproduce and review results. Separate measured evidence from authored claims.

## Rollback

Describe the prior binding/configuration, how to restore it, which evidence remains, and how to prove no subsequent dispatch uses the candidate. Never delete evidence as rollback.

## Manifest

Include a machine-readable `manifest.json` with package ID, proposed status, source/runtime receipts, interfaces, acceptance IDs, and rollback reference. Update status only with evidence; never label preparation as product acceptance.
