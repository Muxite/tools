# Completed ten-experiment Strata campaign

All ten GPU experiments completed. No throughput improvement was accepted.
The source/evidence archive includes the final report, original failures,
configuration diagnostics, fixed-placement source/build/A/A chain, and the two
final fixed-placement screens. The final factory suite passed1000 tests with1
skipped. No defaults were promoted.

- `spark-broad-campaign.tar.gz`: focused source overlay, sixteen task exports,
  sanitized additional receipts, cleanup inventory and portable verifier.
- `spark-broad-agent-and-engine-images.tar`: refreshed standalone agent and the
  fixed-placement engine images; no model weights or mounted credentials.
- `*.sha256`: archive byte identities.
- `IMAGE-ARCHIVE-VERIFICATION.json`: streaming content, OCI config/blob and
  uncompressed layer digest verification. No Docker load was used for verification.
- `verify-archives.py`: repeatable standard-library archive verification.

Extract the source/evidence archive and run `python3 spark-broad-campaign/verify.py`.
It checks all4248 file hashes and nested evidence manifests. The source is a
working-tree overlay, not a complete standalone Git checkout. Read its README
for workload, quality, warmup and evidence omission limits.

The agent's actual standalone Docker smoke imported the Jiuwen facade and sealed
25 capsules without a source bind. Its OCI image identity is
`sha256:24e9fb3b44ae390b4fc11434050136f4a619ece9a261b385fe50fc5a2ffba0ee`.
The engine identity is
`sha256:a431b930d26d0abb6eacbd56a970f56216367d901f514a898a2197dc9d1d3b24`.
Historical mission image identities are preserved in their original receipts.

The image archive can be imported separately with `docker load --input
spark-broad-agent-and-engine-images.tar`. Loading is not required to inspect or
verify the evidence. Model assets and deployment configuration remain separate.
No shared images, caches, queues or evidence were pruned during packaging.
