---
id: amendment-authority-readiness
status: proposed-user-authorized-preparation
source: User-authorized amendment preparation, 2026-10-21
last_reviewed: 2026-10-21
next_action: Convert negative scenarios into readiness probes for the isolated lab
---
# Authority Readiness

**Package ID:** `AM-AR-001` · **Status:** proposed user-authorized preparation, not product acceptance.

Read this overview, [Evidence.md](Evidence.md), and [manifest.json](manifest.json). This package organizes preflight and denial evidence for the existing M1 boundaries. It does not add credentials, host control, APIs, or a new acceptance decision.

## Baseline and compatibility

M1 already runs as one application container with a read-only root, dropped capabilities, no-new-privileges, seccomp, a private network, protected config, IPC and state mounts. Generated code uses the protected `RestrictedExecutor` with an unprivileged identity, cleared environment, unshared namespaces, a job workspace and declared read-only assets. The executor is not a Docker socket proxy. See the embedded excerpts for source receipts.

Compatibility rules: keep protected host admission, immutable bindings, finite model bridge, protected evidence, deterministic checks, semantic-verifier disclosure limit, and `ProtectedGate`. Preserve maintained `TASK`/`AC`/`IF` identities. Add only `AM-AR-AC-*` preparation criteria. `docker info` success is host readiness evidence only; it does not establish a secure worker or product acceptance.

## Proposed readiness experiment

First reconcile source authority: the captured M1 branch's AGENTS/product navigation still describe older PRD/scope and pending registration, while its actual `docs/code/Missions/M1/TASKS.md` is r45, populated, and allocated against October 15 V10. The maintained design checkout identifies V10, but the captured implementation's top-level receipt identifies October 13. Preserve both receipts and the native task identities. The register's integrated NOT_BUILT/final NOT_RUN fields must not be overwritten by a narrower build/deployed-checkpoint or component regression result.

Collect a preflight record for the exact machine/image/runtime, Linux isolation prerequisites, cgroup/resource limits, worktree revision, image digest, model bridge ownership, available hardware, credential presence without value disclosure, and evidence storage availability. The worker receives only the authorized input/output envelope and effect handles needed for the declared call. It receives no Docker socket, host home, account token, direct provider credential, hidden-fixture mount, or direct gate/store authority.

If a mandatory boundary is unavailable, record `blocked` before candidate execution. An operator may authorize protected preparation of a missing platform dependency; that preparation is recorded separately and does not count as a pass. Never silently substitute a mock, local unrestricted process, broad mount, or host-side model proxy.

## Acceptance criteria

- `AM-AR-AC-01`: readiness record identifies host, image digest, code revision, active limits, isolation mechanism and probe versions without recording secret values.
- `AM-AR-AC-02`: negative probes for secret, control state, hidden fixtures, unrelated artifacts, undeclared network, Docker socket, and arbitrary executable fail from the worker identity.
- `AM-AR-AC-03`: missing kernel, cgroup, image, bridge, or evidence prerequisite produces a stable blocked reason before a paid/model or candidate side effect.
- `AM-AR-AC-04`: every effect travels through the host-owned bounded capability path; malformed requests, replay, undeclared operation, or mismatched invocation identity are denied and recorded.
- `AM-AR-AC-05`: host output checks, deterministic gates, exact-output verifier assignment, and release commit remain the only path to advancement.
- `AM-AR-AC-06`: revocation or worker failure stops new dispatch, preserves prior records, and supports a reviewed rollback to the prior binding.
- `AM-AR-AC-07`: the owning source record resolves or explicitly blocks the conflicting October 13 top-level receipt versus October 15 V10 task allocation, recording exact source bytes and authorized scope. A terminal-LF difference is recorded separately from a semantic requirement change.
- `AM-AR-AC-08`: reconcile candidate build identity, component evidence, system evidence and accepted deviations individually; a page load, test count or child deployment note cannot advance unrelated ACs or final system acceptance.
- `AM-AR-AC-09`: update stale navigation through the native owning process without reallocating existing TASK/AC/IF identities or overwriting historical source/evidence.

## Observable negative scenarios

Probe attempts to read `/var/run/docker.sock`, account/session files, run-state, hidden fixture paths, undeclared parent/sibling inputs, and host home. Attempt DNS/TCP and Unix socket egress; request an unlisted tool; forge a different invocation ID; replay a previous envelope; remove a mandatory probe; and kill the worker during output transfer. Each must deny, block, or produce an explicit non-advancing outcome with a host-side record.

## Evidence and rollback

Retain image and source digests, protected readiness manifest, exact probe sources/results, effective UID/GID, namespace/cgroup observations, denied-path outcomes, network probe outputs, bridge protocol version, invocation correlation, raw worker logs, output hashes, failure reason, and export checksum. Keep credentials out of evidence and sanitize user-controlled logs before sharing.

Rollback revokes the experimental binding, routes new plans to the prior admitted binding, and verifies that no worker remains active. Keep all evidence and mark any uncertain containment as a stop requiring operator review.
