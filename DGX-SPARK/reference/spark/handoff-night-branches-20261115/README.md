# Spark night CC and branch handoff

This directory is ready to copy: `IMAGE-ARCHIVE-VERIFICATION.json` confirms all7,322 source/evidence files and all22 saved image layers. Verification completed before03:00 Toronto on2026-11-15. It contains a source overlay and raw results plus a separately saved standalone ARM64 agent image. No model weights or credentials are included. The destination has not been selected and no transfer was performed.

- `night-branches.tar.gz`: source, CC packages, tests, experiment contracts, raw outputs, negative attempts, native ARM64 component artifacts and live-agent receipts.
- `agent-arm64.tar`: standalone ARM64 factory-agent runtime; exact identity and qualification are in `agent-image-record.json`.
- `verify-archives.py`: verifies source file sets and SHA256, OCI descriptors, image config and compressed/uncompressed layers without Docker loading.
- `night-branches/verify.py`: verifies extracted source/evidence against its manifest.

Run `python3 verify-archives.py` here before and after transfer. To load the agent on an ARM64 Docker host: `docker load -i agent-arm64.tar`. This does not supply model weights, lab host services or credentials. Consult the included Spark runbook and dependency-cleanup audit for those separate requirements. The source is an overlay for a compatible checkout; SOURCE-STATE.json and MANIFEST.json pin the actual dirty working-tree bytes. Earlier handoffs preserve full ancestry and build environments.

Read `night-branches/source/docs/architecture/factory/NIGHT-BRANCH-RESULTS.md`, `NIGHT-BRANCH-METHODOLOGIES.md`, `EVIDENCE-DIGEST-LAB.md` and `BRANCH-WORKBENCH.md` first. The live mission report and proposed next input are under `night-branches/evidence/jiuwen/`.

RSI should score each CC by its job: reproducible builds, reliable experiments, useful bounded evidence, attributable profiles, falsifiable hypotheses or durable branch decisions. Component checks are not engine acceptance. The observed long-prefill improvement is workload-specific; a different longer-generation workload still has unresolved exact-token divergence.

Cleanup: all20 owned model phase containers were removed; GPU process check was empty. Unrelated ai4r and buildkit containers were left alone. No global dependencies were installed. Native experiment binaries live outside portable CC sources. After verified transfer and RSI import, owned duplicate staging/export archives may be removed individually. Retain raw experiments and failed attempts until their import is confirmed. Do not globally prune Docker images/caches or delete shared environments, model assets or historical source closures. The previous38-CC image export is retained separately under `retained-night-agent38/` for provenance.
