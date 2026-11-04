---
id: strata-source-trace
status: proposed-runtime-unverified
source: Sources/Prompts/2026-11-02-cc-image-template.txt
last_reviewed: 2026-11-02
next_action: Capture one matched A/A result before selecting the proposed shared-basis reader
---
# The Strata pilot at commit c62d5e3

Inspection used the top-level Huawei Strata checkout, clean on main at `c62d5e3a15b40ea51c96aae9e8d36928965f53ab`. The fixture’s model revision, two shard sizes and published SHA-256 values are taken from the pinned setup code. These pins were inspected; the large weight files were not downloaded or verified in this design review. [Source setup](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/setup.py)

| Path at that commit | What to reuse | What to change |
|---|---|---|
| `spark/build_engine.sh`, `packaging/build_cuda_linux_aarch64.sh` | The ARM64 CUDA build and native engine packaging recipe. | Run inside a digest-pinned builder, record toolchain and exact inputs, then wrap the produced engine for its target. |
| `packaging/package_engine.py`, `strata_control/engine_component.py` | Native manifest, per-file bytes/hashes, backend, arch and driver checks. Local unsigned packages and compatible fallback may be acceptable to Strata. | Verify the exact requested release after resolution. Unknown driver or substituted engine prevents comparable hardware evidence. [Component specification](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/packaging/ENGINE-COMPONENT.md) |
| `tests/data/native_experts/iq3_s.txt`, `tools/iq_pack.py` | Native index locating gate/up/down data by layer, expert and shard. The fixture has 48 rows × 512 experts and sums to 50,292,326,400 logical expert bytes. | Reference the pinned inputs and generated index digest. Use a logical selector in the CC. Measure actual unique files required at runtime. [Native fixture](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tests/data/native_experts/iq3_s.txt) |
| `src/kernels/cpu/expert_layout.cpp`, `tools/test_iq_pack.py` | Existing v5 Hadamard sidecar for already-rotated weights. Native compatibility checks demonstrate what a valid pack-reader pair means. | A shared basis across routed down projections is a separate proposal. Build a converter and reader, compare selected reconstructed tiles against the original, and verify the GB10 path. [Pack code](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tools/iq_pack.py) |
| `tools/dgx_bench.py` | One arm per invocation, server warmup, per-cell NDJSON, configuration and summary. | Give each attempt its own directory and tag. Capture/replay real request bytes and nonce order. Keep the speed harness distinct from the separately named standard protocol. [Harness](https://github.com/Niko1221/Strata/blob/c62d5e3a15b40ea51c96aae9e8d36928965f53ab/tools/dgx_bench.py) |

**Proposed ontology.** Identify the immutable model and native input pack. Select all routed down projections by logical identity. Bind the converter and its parameter schema. The worked example uses a proposed rank of 32, per-layer shared bases and per-tile residuals. Preserve router weights and top-k, tokenizer, attention/KV precision and unselected projections. Name the generated candidate pack and required reader ABI. The factory binds their actual digests after build. A ranking, kernel or layout change that affects a protected invariant requires a differently scoped comparison.

**Review evidence.** A local run of the upstream pack test module executed three Hadamard metadata tests successfully. Four fixture-building test classes skipped because the checkout lacked llama.cpp’s gguf-py dependency. This tests metadata handling on the current workstation. Spark build, GPU inference, proposed transformation, restoration and performance improvement remain unmeasured.
