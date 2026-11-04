---
id: final-m1-merge-20261023
status: merged-pushed-with-explicit-runtime-limits
source: Sources/Prompts/2026-10-23-authorize-final-merges.txt; Resources/review-batches/2026-10-23-final-merge/final-receipt.json
last_reviewed: 2026-10-23
next_action: Qualify connected execution and run a real authenticated campaign on the merged source
---
# Final M1 merge

**Merged and pushed to `ai4r_M1` at `60f65abe`.** The new upstream AI4R at `125dafc5` now includes our deployment workflow, required core typed Planner, four optional capsule candidates and development guidance. This supersedes the separate-candidate next step in [[Activities/2026-10-23 Supervised M1 Integration]]. All eleven original source/rehearsal branch heads are now ancestors of final M1, including the retained utility-composition test. Feature branches and the earlier deployment-pause history are preserved; no force push was used.

The [current repository status](../../AI4Research-Development/jiuwenswarm-m1-current/deploy/m1/INTEGRATION-STATUS.md) records source scope and remaining work. The [exact receipt](../Resources/review-batches/2026-10-23-final-merge/final-receipt.json) pins commits and verification. There is one final shared version; historical branches are provenance, not competing maintained implementations.

## What was reconciled

Kept the incoming Brief v3 target comparisons, historical v2 reads, output-specific assessments, exact contract exports and safe retained-upload reuse. The merged core Planner is a new `m1-13` release; PDF work keeps upstream `paper-m1-5`, while its affected Planner is `paper-m1-9`. New profile captures use `local-research-unified-v3`. Static remains the D39 default; planned execution is selected explicitly before a run, with no silent failure fallback.

Resolved eight source/document/catalog conflicts and verified the combined checker closures. Seven narrow EOL rules reproduce upstream CRLF-pinned bytes without repinning its compiler/scientific/PDF work releases. Updated stale current-release test inputs and version assertions while retaining historical fixture files and protected rejection behavior. A final real-Factory regression exposed and fixed the legacy PDF Planner catalog-port mismatch: the coordinator now follows its admitted declaration rather than a hardcoded core name, so both Planner paths bind their required inputs before dispatch. This regression does not claim a live PDF model run. Optional code is present, but no candidate was automatically qualified, admitted or activated.

## Verification and actual extent

- Fresh Windows checkout: **225 passed, 4 deselected, 3 subtests passed in 67.78 seconds**. [Command](../Resources/review-batches/2026-10-23-final-merge/fresh-checks-command.json), [log](../Resources/review-batches/2026-10-23-final-merge/fresh-checks.log), [JUnit](../Resources/review-batches/2026-10-23-final-merge/fresh-checks.xml).
- The retained utility-composition test passed separately and is also included in the final 225-check run; it exercises the actual utility modules and registered deterministic checks while preserving the original packet and low-trust label. This is narrower than real governed Scheduler execution.
- Fresh Windows and main-checkout pin checks pass: all seven scientific, three paper and four optional candidate entries reproduce their exact catalogs. Planner/PDF checker release pins verify.
- Independently materialized Linux source subset also verifies the final m1-13/paper-m1-9 pins and catalogs; a fresh/repeated development profile capture preserved the same binding and static source. [Method and limits](../Resources/review-batches/2026-10-23-final-merge/linux-pin-verification.json). The full-history clone attempt from the local partial repository failed on a missing promisor object; it is not a successful Linux clone or application run.
- The same four explicit exclusions remain: three connected scheduler cases and one previously reproduced Windows routing-custody fixture. A separate shared-fixture run passed 26 checks and failed one connected private-measurement test with `audit_unavailable`; its [JUnit](../Resources/review-batches/2026-10-23-final-merge/shared-fixture-checks.xml) is retained. No audit/custody guard was weakened. The three partial-output security cases now pass with a valid current Brief input.

A live authenticated campaign, full generic dynamic execution/delivery, production checking-asset qualification, actual SSH deployment, ARM64/Spark and scientific execution remain unverified. This is completed source integration, not full M1 runtime acceptance or measured CC benefit. RSI and model-router implementation remain with their owners.

Luna agents completed scoped reviews and named-file fixes. The supervisor corrected an actor-shadowing mistake and an overbroad EOL recommendation before final verification. An additional final Luna review hit a workspace credit limit and did not complete; the supervisor performed the final source/conflict review directly. Agent claims were not treated as acceptance evidence.

## Recovery and next step

Nine notebook files were backed up with exact hashes before this update. Earlier notes and prompts remain intact, with current navigation pointing here. The [verified Git bundle](../../AI4Research-Development/ai4r-m1-final-integration-60f65abe-20261023.bundle) and receipt retain source history; the bundle requires base `bfc30ba`. Use the [runbook](../../AI4Research-Development/jiuwenswarm-m1-current/deploy/m1/OPERATIONS.md) with matching images, qualify a deliberate new configuration/release on the actual execution environment, and retain one real campaign's inputs, outputs, plan, checks, gates and observations before claiming runtime readiness.
