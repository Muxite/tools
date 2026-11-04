---
id: spark-benchmark-host-direction
status: current-direction
source: Sources/Prompts/2026-10-22-spark-benchmark-host-direction.txt
last_reviewed: 2026-10-22
next_action: Use this split in future Spark deployment and M2 sandbox prompts; validate transfer paths on the actual host
---
# Spark as a benchmark host

The DGX Spark is primarily benchmark execution hardware. Most application development and image-building should happen on development machines or an appropriate build service. Prepare only the required versioned images and campaign inputs for Spark, run and inspect tasks there, then bring results and observations back to development machines for review.

This updates the operating assumption for future prompts. The already-sent benchmark-runner prompt remains as issued; image transfer or remote-host operation has not been implemented or tested.

## Intended flow

1. Build and identify app and runner images away from Spark where practical. Record source commit, architecture, image tags and immutable digests; verify Spark compatibility.
2. Deliver only required images/dependencies to Spark through a reachable registry or portable OCI archive. Prefer incremental content-addressed transfer; avoid copying full source trees and build caches for routine runs.
3. Stage each campaign's permitted cases and inputs in an owned Spark location. Keep inputs read-only and held-out material access-controlled.
4. Run with isolated workspaces and persistent campaign output. Inspect readiness, live progress, logs, resource observations and artifacts on Spark.
5. Transfer results, observations and provenance to a user-selected development-machine location. Verify manifests, sizes and hashes; support resume and retain Spark data until the receiving copy verifies.
6. Bound storage on both ends. Reclaim only verified owned staging and disposable cache/image data. Never globally prune or implicitly delete source inputs or accepted results.

## Sandbox planning

Plan the complete build-to-execution-to-review lifecycle: image provenance and architecture, authenticated image delivery, campaign input staging, run isolation, host inspection, result export, transfer recovery, ownership and retention. Spark can be a bounded execution host without being the authoritative home for source development or durable project data. Durable lab identity and project state need an explicit storage and backup design separate from disposable benchmark execution state.

The next sandbox design should choose transfer mechanisms, authentication, directory ownership, quotas, resumable copy and evidence-retention rules. Keep the first slice practical: move one image pair and one campaign end-to-end, run it, inspect artifacts, return them with verified integrity and survive container removal.

## Prompt routing

Use [[Designs/Durable Project Labs]] and [[Designs/Spark Shared Services and Storage]] for M2 sandbox planning. Future Spark prompts should include remote image/input staging and result return. Keep [[Resources/Coder Prompts/benchmark-runner]] as the already-sent app-testing handoff; this note does not change its scope or implementation status.
