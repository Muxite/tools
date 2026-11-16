# 20261113 Spark Research Evidence Index postpresentation

- [Source transfer verification](evidence/source-verification.json): all extracted regular files and archive identity.
- [Transport review](evidence/transport-review.json): recovery, duplicate prevention, changed-input/path rejection and process cleanup.
- [Final qualification review](evidence/qualification-review.json): actual checked scope and remaining gates.
- [Queue review](evidence/queue-review.json): owned job states, process-group and container absence.
- [Factory graph](evidence/factory-graph.json): locally directed task revisions and links to actual evidence and reconciled attempts.
- [Derived build and inference summary](evidence/summary.json): phase timings, capped memory and sampled storage reads.
- [Original failed container cleanup](evidence/v1-container-cleanup-failure.json): preserved failure and narrowly scoped recovery.
- [Export manifest](evidence/export-manifest.json): hashes and sizes of fetched raw records, logs and outputs.

Each run has its own subdirectory in `evidence`. Build records retain source tree, toolchain, flags, runtime and image identities. Inference records retain model hash, arguments, limits, samples, exit status and output hashes. Original records are not relabeled after a fix; a new request ID identifies the corrected run.
