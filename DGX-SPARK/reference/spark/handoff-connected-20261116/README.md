# Connected factory handoff — 2026-11-16

Local source commit: e6099f421. Source overlay, raw evidence and the standalone ARM64 agent runtime are included. Earlier handoffs are unchanged and remain necessary for base checkout/build ancestry and model assets. No model weights or credentials are included.

Verify before extraction/load: `python3 verify-archives.py` checks source member hashes and the saved image config, layer, blob and identity digests. `sha256sum -c development.patch.sha256` verifies the local commit patch. The verifier does not load Docker images. Extract `connected-development.tar.gz` and read `connected-development/source/docs/architecture/factory/CONNECTED-DEVELOPMENT-2026-11-16.md`. Apply development.patch only to its compatible parent checkout; the source overlay is an alternate review format.

Agent image: sha256:39677167fffa99d8c43ee050b26c0d7951b9fbd6e775db1b544631056ecf6085, tag factory/agent:connected-development-20261116. Actual facade import and sealing all40top-level CC packages passed in the read-only, offline container without a source bind mount. Sealing does not imply every capability has independently passed certification. Runtime is ARM64; rebind paths and supply an explicit new campaign before execution elsewhere.

Results:1,229 tests passed, one skipped. Four GPU diagnostic attempts retained (including failures). Final common-history comparison confirms different output50 logits; no new speedup or quality acceptance. The live CPU agent published a report but hit its300-second limit. Its proposals are not execution authority. Connected live-agent-to-GPU recovery and multi-cycle endurance remain acceptance work.

Cleanup: all owned diagnostic containers were removed. Shared services/caches and user dependencies were untouched. These exported archives and copied staging tree are removable duplicates after verified transfer and RSI import; preserve original raw evidence until then. Do not use broad Docker/system pruning.
