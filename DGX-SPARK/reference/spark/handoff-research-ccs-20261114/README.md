# RSI-ready research CC handoff

Seven new self-contained job packages, 24 native capabilities. Quick validation:
59 focused tests passed; all seven local verifiers and 24 real Host capability
examples passed. Refreshed standalone agent smoke imported Jiuwen and sealed
32 top-level capsules. These are CPU-verified prototypes, not integrated GPU
optimizations or proof of an inference speedup.

- `research-cc-starter-kit.tar.gz`: 110 files containing packages, skills,
  methodologies, primary-source provenance, focused tests and release-bound
  receipts. Extract and run `python3 research-cc-starter-kit/verify.py`.
- `research-agent-image.tar`: optional refreshed ARM64 agent image. Import with
  `docker load --input research-agent-image.tar` on a compatible host. Models,
  native builder and Strata engine remain separate from this agent image.
- `verify-archives.py` and `IMAGE-ARCHIVE-VERIFICATION.json`: independent archive,
  OCI config/blob and uncompressed-layer verification without Docker loading.
- `*.sha256`: archive checksums.

The image is `sha256:20fe65639494b328c74738e76e88d8e5a16924fe4b535aa8822cab32aa2ef1d6`.
Read the kit's `docs/architecture/factory/RESEARCH-CC-STARTER-KIT.md` for methods,
implementation directions and RSI workflow. Each CC has `EXAMPLES.json` with
complete native inputs and a standalone `verification.py`.

No new model inference, model download, global package install, engine patch,
shared-cache deletion or unrelated service interruption was performed for this
kit. Previous handoffs remain unchanged. Copy these owned archives off Spark;
verify before deleting any owned transfer staging. Do not prune shared Docker
layers, model weights, queues or build caches.
