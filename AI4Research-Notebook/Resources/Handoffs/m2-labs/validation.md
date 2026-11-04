---
id: m2-handoff-validation
status: acceptance-plan-not-executed
source: source-map.json; Sources/Prompts/2026-10-23-m2-component-handoffs.txt
last_reviewed: 2026-10-23
next_action: Freeze scenario expectations before coding and record evidence by environment
---
# Acceptance and completion reporting

Freeze expectations before coding. Use public synthetic development cases, not
private benchmark tests. Record exact source/image/platform/configuration and
whether each check exercised fixtures, Docker, VMs, models or Spark. Separate
run totals/baselines; document agreement and mocks are not runtime PASS.

| Scenario | Designed outcome / owner |
|---|---|
| Ordinary M1 benchmark startup | No VM/factory/local-model or sudo prerequisite / deployment owner |
| No VM permission/provider | No escalation or host change; provider blocked, independent carrier work continues / lab controller |
| Stop/start and app replacement | Same project data, appropriate new deployment/container identity / lab controller |
| Restore with uncertain old writer | Fence or confirmed shutdown before writes; reject ambiguity / recovery owner |
| Corrupt backup or missing dependencies | No READY/replay claim, preserve current state and report exact gap / recovery owner |
| Capsule completes | Seal exact bytes; independent checks/gates decide acceptance / broker and gate |
| Wrong image/platform or linked/corrupt outputs | Preparation/check failure, no fallback or partial acceptance / broker and checks |
| Cancel, OOM, restart or persistence failure | Confirm/reconcile owned state, retain evidence, no uncertain-effect replay / broker |
| Misleading self-tests/injected instructions | No authority, criterion waiver or self-admission / fixed factory controller and admission owner |
| Changed source/declaration/image | New identity; invalidate affected old PASS / factory and qualification |
| Private producer context given to verifier | Denied; exact declaration and subject output only / binding owner |
| Disk pressure/stale leases | Reject bounded growth, protect data/models/pins, no global prune / storage owner |
| Shared model/build backend | Independent state/jobs/grants/conversations and physical copy accounting / resource and lab owners |
| Candidate exchange/publication | Independent admission and explicit adoption, old runs pinned / release owners |
| Model/platform upgrade | New compatible pins for new runs, retained history and recoverable migrations / lab release owner |

## Implementer return

Return a short functional description per branch, commit/base/dirty-tree identity,
actual commands and configs, evidence locations, passed/failed/skipped/blocked
checks by environment, usable behavior now and remaining connected checks.
Include resource ownership/limits, replay availability and whether independent
qualification/admission/activation actually occurred. Preserve prior failures.

## Exit meanings

- Contract slice: agreed versioned examples and responsibilities, no runtime acceptance.
- Tool carrier: real container through host checks/gates and negative cases, no VM/factory claim.
- Durable lab: real VM lifecycle, fenced replacement restore and project export; second-lab isolation separately proved.
- Manual factory: real source-to-image, independent qualification/admission/invocation and bad-candidate rejection.
- Adaptive factory: bounded authoring over proven lifecycle, recovery and independent repeated-case assessment.
- Spark path: actual ARM64/Spark evidence; AMD64 mocks or source inspection cannot substitute.

This documentation revision checks links, metadata, preserved source hashes and
Mermaid renderings. `source-map.json` records inspected sources;
`validation-receipt.json` records completed document checks. No implementation
or host test is claimed merely because these handoffs were authored.
