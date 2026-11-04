---
id: amendment-container-cc-pilot
status: proposed-user-authorized-preparation
source: User-authorized amendment preparation, 2026-10-21
last_reviewed: 2026-10-21
next_action: Keep as future-soon pilot until authority and accuracy packages clear their gates
---
# Container CC Pilot

**Package ID:** `AM-CCP-001` · **Timing:** future-soon, after readiness and accuracy preparation · **Status:** proposed preparation, not product acceptance.

Read this page, [Evidence.md](Evidence.md), and [manifest.json](manifest.json). This proposal tests one stateless code carrier behind the existing exact-pinned registry dispatch. It does not containerize each CC, rebuild CapsuleRunner, replace the native planner or application container, or give a container Docker control.

## Baseline and smallest pilot

M1 already has one application container and a protected `CapsuleRunner` that resolves the exact CC name/version/declaration hash, verifies implementation references, invokes the handler, captures typed outputs, runs checks/verifier, and commits advancement through the protected gate. Generated POC code already runs through `RestrictedExecutor` with bwrap and resource limits. These boundaries remain authoritative.

Pilot only one named, stateless code carrier with no model/tools/network/secret needs. A host-owned adapter serializes the frozen invocation identity, declared input bytes or scoped read handles, and explicit output schema to an isolated worker. The worker receives a scratch workspace, pinned implementation/environment, and no host store credentials, gate APIs, Docker socket, provider credentials, hidden fixtures, or unrelated input. All effects requiring authority go through a host broker that checks invocation identity and capability limits. Host validates response, captures exact bytes, runs existing checks, and alone asks the protected gate to advance.

If the target can run within existing `RestrictedExecutor` at lower cost and adequate quality, keep using it. Container isolation requires evidence that it improves isolation, dependency control, or repeatability enough to justify lifecycle and IPC cost.

## Compatibility and readiness

Do not change existing `TASK`/`AC`/`IF` identifiers. Add `AM-CCP-AC-*`. Preserve exact native runtime pin and planner single-shot settings. The candidate worker cannot alter declaration, registry, deterministic checks, verifier profile, hidden test data, evidence store, or gate. Runtime verifier still receives only declaration plus exact output and pinned criteria/instructions. Docker daemon access is host-only; worker gets no socket or orchestration credentials. `--network none` unless a separately authorized brokered effect is essential. GPU is unsupported by the lab prototype and must block a GPU-required carrier rather than silently omit access.

## Acceptance criteria

- `AM-CCP-AC-01`: pilot selects exactly one stateless handler by immutable declaration and implementation pins; mismatches refuse dispatch.
- `AM-CCP-AC-02`: the host runner retains the full current path for invocation, output capture, deterministic validation, verifier binding, evidence, and release. Worker cannot call `ProtectedGate` or write host state.
- `AM-CCP-AC-03`: worker receives no Docker socket, credentials, host home, hidden fixture/key, unrelated input, or direct provider/model client. Denial is demonstrated by in-worker probes.
- `AM-CCP-AC-04`: timeout, worker death, malformed/oversized output, duplicate response, stale invocation ID, or partial artifact transfer yields non-advancing state and preserved evidence; no automatic replay.
- `AM-CCP-AC-05`: read-only pinned source and immutable image digest, resource limits, network policy, environment lock, hardware requirements, logs and output hashes are recorded and reproducible.
- `AM-CCP-AC-06`: compare the isolated carrier against the same baseline cases using predeclared quality, latency, resource, and operational cost measures; adopt only if a separately reviewed decision shows a net improvement.
- `AM-CCP-AC-07`: rollback switches the exact binding to the previous in-process/restricted-executor handler and confirms no future dispatch targets the container.

## Negative scenarios and evidence

Probe the socket, env, host home, store, gate, hidden paths, sibling input, undeclared network, GPU device, and a second invocation. Tamper image digest or code pin; exceed CPU/memory/PID/output budgets; crash before and after output commit; resend a prior response. All failures stop advancement, preserve local evidence, and never trigger hidden data leakage or retries.

Retain image digest/build provenance, source and environment hashes, frozen contract and invocation IDs, effective limits, network/mount/identity observations, test suite and scorer pins, raw output bytes and digest, stdout/stderr, timeout/failure, host gate decision, and checksums. Rollback keeps all experiment evidence and uses the previously admitted binding for future runs.
