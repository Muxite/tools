## Expert-copy replay and the next planner decision

Reconstructing copy geometry from the original mapped GGUF offsets matched the recorder's 52,689,716,736 submitted bytes. The replay issued 10,674 host-to-device calls across 40 groups on the NVIDIA GB10, driver 580.178.04. All positive groups were for one 507-row prefill microbatch across 40 layers. The other two prefill microbatches (1 and 4 rows) and all decode events submitted zero bytes at the observed hook.

The capped replay used the original pageable file mappings, one CUDA stream, a reused destination buffer and synchronization after each nonempty group. No model kernels ran alongside the replay.

| Replay pass | Elapsed time | Effective submitted bytes/s |
|---|---:|---:|
| 0 | 21.347 s | 2.468 GB/s |
| 1 | 42.993 s | 1.226 GB/s |
| 2 | 1.001 s | 52.621 GB/s |
| 3 | 1.000 s | 52.712 GB/s |

The analysis capsule used the measured later-pass median of 52.621 GB/s. Dividing 52.690 GB by that rate gives **1.001 s** of serialized replay-equivalent copy time, or **1.84%** of the single C1 gate-on request's 54.367 s TTFT. For scale only, 1.001 s is **10.3%** of the historical warm A median of 9.679 s. The same-prompt historical A repeat used for output parity took 5.188 s. C1 gate-off and gate-on were separate first requests, at 49.815 s and 54.367 s. Those times cannot isolate recorder overhead or a treatment effect.

The earlier replay passes had uncontrolled file residency and were much slower. Page faults, residency and synchronization are hypotheses for the spread. The replay does not measure the duration of C1's actual copies, their overlap with model kernels, critical-path stalls, or speedup from removing them. The recorder can change synchronization to capture routes, which adds uncertainty when applying these observations to stock. The relative 512-token replay numbers should not be transferred to 2048-token prompts without measurement.

1. Prioritize the expert weight cache and placement planner. Measure actual gate-on and gate-off bytes by path, unique expert demand, wait at first demand, cap headroom, parity and warm TTFT under the matched stock control. For CPU-expert placement conflicts, use an explicitly matched placement control. Check whether an effect remains against A+ once native calibration is complete. The replay motivates a residency and copy experiment without assuming raw transfer speed explains the entire TTFT gap.
2. Then test the batch layout mapper. At 512, the two small groups contained no expert copy bytes and there were no repeated large-copy dispatches per layer to deduplicate. At 2048, demonstrate changed cuts under an eligible matched profile and measure repeated expert copies across microbatches. Keep that activation profile distinguishable from strict A.
3. Use quiet mirrored launches for timing attribution. Compare two warmed launch windows per arm. The original C1 probe establishes functional parity and trace activity, with the independent authoritative Granite scorer still pending.

### Added evidence

- Exact copy replay `spark-c1-functional/copy-replay/bandwidth.json`, SHA256 `b86230e2c85e7bb4775e0c830b38d89bbcb2ca175fb37a529b9c3304ad45007e`.
- Verified copy timing analysis `routing-copy-timing-analysis-report.json`, SHA256 `a39424ca7b57e6e7f2ea6fc68b22b2b74d8359f685fe819c219647d670c4f209`, from `analysis.expert_routing_profile` v1.2.0, release `b7fa53d5c91345807b1372df359850a4c49d5f3c4b2d7bbdfaf0bfa3c1a454fa`.
- Replay plan `spark-c1-functional/copy-replay/c1-copy-replay-plan.json`, SHA256 `b4f9f69a8b121129d9fdb7e787ab2cf508df96a8954ff9e0c7eb34325c0e8456`; capped stop `spark-c1-functional/copy-replay/result.json`, SHA256 `569c8c08fcc42445c0819bd8e306d9c1b06b16d23fb882fb97f42128a9ef50d0`.
- Functional lab `spark-recorder-deepseek-01/lab.json`, SHA256 `bf2f9db6f3f187ff53072baa7b9b07f35a2c11530f7accf6202169c5a5a7c376`; its source references include both C1 requests, the historical parity request and the original trace.
- Historical A measurements and sources in the [P1 reference report](../spark-p1-reference-reconnaissance/report.md), SHA256 `71c3a2f25cfb217efaf4614101163a5c52aa5bab14a3add8ff8e8a6ba15ea115`.
