# P1 reference-arm reconnaissance

This historical iteration ran the stock llama.cpp arm A and the Strata fair-profile arm S under the same Spark cap. The direct operator ran the lab before the analysis capsule was available. No builder capsule, candidate diff or A+ timing enters this analysis.

## Lab measurements

| Arm | Prompt tokens | Warm requests | Client TTFT median and range | Engine prefill median | Decode median |
|---|---:|---:|---:|---:|---:|
| A | 512 | 5 | 9.679 s (5.188–24.667 s) | 9.608 s | 2.94 tok/s |
| S | 512 | 5 | 5.582 s (4.341–6.386 s) | 5.566 s | 15.60 tok/s |
| A | 2048 | 5 | 31.562 s (12.758–34.167 s) | 31.487 s | 2.92 tok/s |
| S | 2048 | 5 | 19.184 s (17.321–21.351 s) | 19.166 s | 14.30 tok/s |

The descriptive A−S median TTFT gap was 4.096 s at 512 tokens and 12.378 s at 2048 tokens. The corresponding inverse-TTFT ratios for S vs A were 1.73× and 1.65×.

Greedy output hashes were stable within each arm and size. A and S produced different output hashes. Each request produced 32 tokens with no prompt-cache hits. The first request from each arm is excluded. The preliminary A request used 510 actual tokens and is retained as an exclusion.

The measurements came from contiguous P1 batches with concurrent activity. A showed substantial warm-up drift. There is no quiet ABBA inference, confidence interval or candidate attribution from these observations.

| Arm | Reported load time | Sampled cgroup peak | Minimum host MemAvailable |
|---|---:|---:|---:|
| A | 61.71 s | 95.60 GiB | 79.70 GiB |
| S | 40.20 s | 30.22 GiB | 37.25 GiB |

The first stock load stopped on reclaim-only cap events. The retry was not OS-cold. Both measured scopes exited normally. CUDA UMA can escape cgroup accounting and the sampled peak can omit final teardown.

## Strata stream counters

| Prompt tokens | Native rows | Experts streamed | Layer-cache reuses | Chunks | Compute read wait range | Aggregate I/O worker busy range |
|---|---:|---:|---:|---:|---:|---:|
| 512 | 6 | 3104 | 1012 | 2 | 2.007–4.216 s | 12.639–30.711 s |
| 2048 | 5 | 10894 | 8312 | 8 | 8.327–12.118 s | 47.291–59.864 s |

These are ordinary CUDA0 stream log rows, including the 512-token warmup. I/O worker busy time is aggregate concurrent work and can exceed elapsed prompt time. The counters do not partition wall time or show corresponding stock phases. The larger prompt shows repeat reuse in Strata. This is a mechanism to test on llama.cpp, with a matched gate control and attributed counters.

## Inputs for the next planner

1. Keep P1 as reconnaissance. Re-establish A and S under quiet mirrored launch order using the identical prompt files. Use the retained read-only Strata pre-run profile to control profile drift.
2. Finish A+ native calibration separately. Include A+ in the same mirrored profile if it is accepted.
3. Establish recorder parity and activity before instrumenting quiet measurements. Check candidate-specific activation against the unchanged stock profile. For residency, test reductions in requested and copied expert bytes and wait-at-demand alongside TTFT. Profile traces can explain an effect after a matched uninstrumented comparison.

## Evidence

- Analysis capsule `factory.spark_gap_analysis` version 1.0.0, sealed release `0fa24aee33c49496f380e30ce0b5f1b4f70a5f6e198daa2be9eb258e446ad6a4`.
- Timing analysis `spark-p1-reference-reconnaissance/analysis.json` SHA256 `7bfdf6d99fd9bb99a2e649a6906de9b3f52d082ffa10c33f9b89102a2e6891ea`. It lists every contributing and excluded request and the corresponding server scope and prompt manifest.
- Strata counters `spark-p1-reference-reconnaissance/strata-stream-counters.json` SHA256 `4b6507a9dbff032ae4a0c162c71d3b7e2fb07f5cad948c542094f08d87999f4b`, from `source:OPS/runs/s-first-load/engine.log@sha256:0b754532734af46f7fb7a23ae8cbdfd384dfca4c04fb3aa0cdc6e93bf2ad64d5` SHA256 `0b754532734af46f7fb7a23ae8cbdfd384dfca4c04fb3aa0cdc6e93bf2ad64d5`.
- Initial stock load exclusion `source:OPS/runs/a-first-load/result.json@sha256:9709770a9971304e20eb648db6e5fc9ae628e7a6209020d854caf7d4066c51c6` SHA256 `9709770a9971304e20eb648db6e5fc9ae628e7a6209020d854caf7d4066c51c6`.
