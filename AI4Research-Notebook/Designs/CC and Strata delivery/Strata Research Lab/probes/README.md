---
id: one-cc-lab-probes
status: proposed-runtime-unverified
source: Sources/Prompts/2026-11-03-one-cc-implementation.txt
last_reviewed: 2026-11-03
next_action: Follow the linked evidence and qualify remaining target-machine checks
---
# Strata source and expert-layout probes

The recorded probe used Python 3.12 and Git on Windows with Strata at commit `c62d5e3a15b40ea51c96aae9e8d36928965f53ab`. Python uses its standard library and imports the GGUF v3 reader from the supplied trusted checkout. Supply the local checkout path as the first argument. The replay makes a disposable local clone inside this folder and releases it after the source-only check. It needs writable temporary space and local Git history containing the base and its parent.

```text
python -B run_probes.py <trusted-Strata-checkout> --receipt probe-result.json
python -B inspect_projection.py <trusted-Strata-checkout> --layer 0 --expert 0 --projection down
```

For a real Qwen GGUF shard and its matching Strata native v3/v4 layout, add `--layout <native_experts.txt> --gguf <shard-file>`. The reader verifies the projection’s GGUF tensor name, encoding, expert count, start, block geometry and file bounds before reading and hashing the selected expert’s bytes. Supply a previously authenticated shard. This inspector covers one projection and does not verify model signatures, other shards, reader ABI, execution quality or per-role byte layout in optional `experts.bin`.

## Evidence

- The checked-in IQ3_S layout yields 48 layers, 512 routed expert slots per layer and 50,292,326,400 logical expert bytes. Its header and rows identify the layer 0 down tensor at shard offset 913,711,104. These are native fixture declarations. They do not establish the physical size of a deployed model or the per-expert projection length.
- Strata ships a readable 483,520-byte GGUF control vector with 47 F32 tensors. Its bytes and bounds were checked; it cannot satisfy a request for a routed expert tensor. The Huawei workspace inventory found only this control vector and two DeepSeek header fixtures in each of the two Strata copies. The full IQ3_S shard was unavailable.
- A generated two-expert F32 GGUF exercised the actual slice path, selected the expected 16 bytes from expert 1, and rejected a one-byte truncation. This is explicitly synthetic data.
- The replay starts at the exact base, checks the patch and preimage digests, applies and stages a single source change in a clean temporary checkout, and verifies the postimage and resulting Git tree. The change turns off `STRATA_PF_FUSED` in the engine’s SM121 defaults. The previous Git commit was rejected before applying any changes. This is a control ablation for source materialization, independent of the MoE storage experiment.
- No engine binary, model reply, GPU checkpoint, compressed model, or throughput/quality measurement was produced. To reproduce just the source candidate, the patch, descriptor, full pinned Git tree and SHA-256 checks are sufficient; qualifying an actual engine still requires a build and a target-hardware test.

Pinned upstream implementation: [native pack writer](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tools/iq_pack.py), [GGUF reader](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tools/gguf_reader.py), [native expert fixture](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tests/data/native_experts/iq3_s.txt), [device defaults](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/src/core/nv_defaults.cpp).

