---
id: lab-progression
status: prototype-smoke-verified
source: Resources/verification/lab-host/host-0d43064b32.json; Resources/lab/validate_host.py
last_reviewed: 2026-10-21
next_action: Qualify an M1 image and operator resources separately, then repeat the lab journey with the real runtime
---
# Lab progression and actual evidence

The lab manager is infrastructure outside experimental AI4Research instances. Each experiment pins a source commit and immutable image, owns a separate worktree, internal Docker network, named volume and evidence directory, and exports evidence before cleanup. Code/CC candidates return through reviewed patches; exports do not activate them.

## Real Docker smoke campaign

On October 21, the [host validation script](../Resources/lab/validate_host.py) ran real synthetic containers against Docker Desktop's Linux daemon (29.8.0, x86_64). The [receipt](../Resources/verification/lab-host/host-0d43064b32.json) contains exact argument-array commands, inspected identities, expected/refused operations and cleanup status. The image was `alpine@sha256:5291449c3df73caf6ed85e649dec1b9e818b39a5d8c871e97afc13e9cd5e8fa8`. A new, one-file synthetic Git repository supplied the source pin; no M1 code or model was executed.

| Scenario | Observed result |
|---|---|
| Two concurrent experiments | Both running, distinct networks/volumes/worktrees and A/B output markers |
| Resource constraints | Inspected 64 MiB memory, 0.25 CPU, 32 PIDs per container |
| Source/effect boundary | Source write denied; no Docker socket mount; internal network with no default route |
| Scheduling | Exclusive run refused during ordinary runs; ordinary run refused while exclusive active |
| Recovery | Simulated manager state-commit interruption recovered the same live container without replay |
| Worker interruption | Forced worker kill reconciled to stopped; evidence still exported |
| Export safety | Running export refused; export hashes checked; tampered export prevented cleanup |
| Cleanup | All four owned experiment containers/networks/volumes/worktrees cleaned; exported evidence retained |

Network creation now uses `--internal`; owned but non-internal networks are refused. A regression test exercises the refusal. This is a concrete strengthening of the earlier prototype. An internal network and absent default route are bounded observations, not an exhaustive proof against every Docker/kernel escape or network channel.

## What remains separate

The manager currently controls named resources and mounts but is not a general adversarial sandbox, a distributed scheduler, or a product authority. The synthetic image ran with its default user and writable image root; M1's application/RestrictedExecutor confinement must be qualified independently. The recovery test simulated the state gap, not a physically crashed desktop/daemon. No native Ubuntu daemon, GPU exposure, GB10 behavior, real scientific workload, model account or CC accuracy was qualified.

Use [[Resources/Lab Host Validation]] for broader negative probes. Actual source/hash and evidence export are retained under `Resources/verification/lab-host`; generated lab control state and synthetic repository remain outside the vault. Never use global Docker cleanup.

## Future-soon per-CC carrier

[[Amendments/Container CC Pilot/README|The container carrier amendment]] preserves host admission, frozen bindings, output capture, checks, verifier assignments and release. Start with one stateless, model-free code carrier. Compare it with the existing in-process or RestrictedExecutor option using identical cases. Pin its image/dependencies; test denial, cancellation, stale/duplicate responses, partial output and overhead. Retain the existing carrier unless separately reviewed evidence supports adoption. This is distinct from the real whole-experiment smoke test above.
