---
id: amendment-ccp-evidence
status: source-snapshot
source: M1 source commit d3d7f565c6c05ccf764fe0780fde149b7dc89b95
last_reviewed: 2026-10-21
next_action: Recheck source receipt at pilot checkout
---
# Portable evidence snapshot

Source excerpts are from M1 source commit `d3d7f565c6c05ccf764fe0780fde149b7dc89b95`; hashes cover complete Git blobs, not excerpt text. This commit is not claimed to be deployed.

## Host dispatch is the narrow seam (`jiuwenswarm/research/runner.py:648-675`)

SHA-256: `affcb51f2c9830b146afafa3321ad35159b56d6bcfe57840f7c5604b564c3998`

```python
handler, pinned = self.registry.resolve(name, version_label, declaration_sha256)
if pinned and tuple(implementation_refs) != pinned: raise carrier_pin_mismatch
produced = await asyncio.wait_for(handler(ctx, inputs), remaining_deadline)
if not isinstance(produced, dict): raise output_invalid
```

Keep this protected path and substitute only one handler implementation through a host-owned adapter. Container process lifecycle, output capture, evaluation and advancement remain host responsibilities.

## Current generated-code boundary (`jiuwenswarm/research/executor.py:212-239`)

SHA-256: `8ef028d328601bb5ac1f7c8218dc1daff916b26b0222016a6f62e4e5b70a9c90`

The existing executor uses bwrap namespace separation, cleared environment, unprivileged UID/GID, capability drop, a single writable POC workspace, and scoped read-only mounts. This is why a container pilot must show measurable improvement instead of duplicating established isolation.

## Whole application boundary (`deploy/m1/compose.yaml:2-50`)

SHA-256: `29e84630ab48ca382e40a12b28752aa910fa8e8a5c07327483f0c76d6725b87a`

The app is already packaged in a whole-application container with protected config, state, account, IPC, POC, input, and executor mounts. A CC worker must not inherit the app's control or account mounts.

## Coder lookup required

Before implementation, inspect the selected deployed checkpoint and current executor/runner tests in its checkout. Do not treat Notebook source receipts or a `docker info` response as proof of a production deployment or of worker confinement.
