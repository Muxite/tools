# CC package / real agent loop handoff

This review bundle supersedes the earlier review source overlay and adds the
real JiuwenSwarm task spark-agent-improvement-001. The old handoff remains intact.
See source/docs/architecture/factory/SPARK-AGENT-IMPROVEMENT-2026-11-14.md for
implementation, actual negative result and next-work gaps.

The candidate's prefill median was lower, but its first token differed. The agent
rejected it, skipped confirmation, retained evidence and proposed diagnostics.
This is a completed real improvement loop, not an accepted engine speedup.

Extract spark-factory-review.tar.gz, then run python3 spark-factory-review/verify.py.
The bundle contains a focused exact working-tree overlay, not the full repository;
SOURCE-PROVENANCE.json records the base revision and dirty file state. Apply the
overlay to that base on the destination. No external .git worktree pointer, model
weights, credentials, Python environment or shared queue state is copied.

The prior handoff-20261114/spark-arm64-images.tar.gz contains the unchanged Strata
runtime, builder and older agent/CLI images. This handoff adds the new agent image
as spark-agent-cc-packages.tar.gz. Load archives on ARM64; use the exact image IDs
in receipts/final-role-images.json. The role receipt includes existing deployment
paths, so relocate explicit bindings/contracts when migrating and issue NEW test
contracts instead of mutating historical ones. GPUs still require compatible
NVIDIA drivers/runtime. Models remain separately supplied; the existing identity
inventory, pack/tokenizer files and source pins describe the tested input.

The old CLI image remains usable with the source-bind wrapper. The new agent image
has independently passed a source-unmounted facade/package smoke. The actual live
mission used the supervisor's explicit read-only source bind, recorded in proof.

Exported evidence is sanitized and independently hashed; artifacts.json maps original
and exported hashes. No archive was transferred to another machine in this session.
The bundled prior image-archive-verification receipt refers to the OLD four-image
archive. New agent archive verification is supplied beside this bundle.

Cleanliness: no global installs, driver changes, model downloads, shared pruning,
or unrelated-process stopping. Owned test scratch, refreshed agent build context,
new tagged image, logs and archives are the additions. Preserve raw evidence and
source/contract pins before removing scratch/context; do not remove shared images,
model files or the external queue/toolchain merely because this task references them.
