# Spark P4 matched benchmark

Partially build-overlapped screening. Across ten pairs per size, C3 returned the first token 24.92 seconds sooner at 512 tokens and 90.80 seconds sooner at 2048 tokens than same-budget stock A+ by the paired medians.

Every launch passed quiet preflight. Two authorized builds overlapped the final A+ scope. The ten-pair result is descriptive screening. The boundary process checks cannot observe activity that begins and ends between snapshots.

Intervals resample matched request repeats within the two fixed launch windows. They describe those launches and exclude between-launch variation.

The initial reverse C3 launch completed all requests, but its cap monitor lost the final process-exit receipt during cgroup teardown. Its entire window was excluded. A prospectively recorded amendment repeated that C3 position from identical cold conditioning before the final A+ control. The ten pairs use four launches with complete cap receipts. The original window, memory trace and shutdown journals are retained as excluded evidence.

A+ and C3 used the same 61,440 MiB budget, 61,401.18 MiB logged allocation and effective runtime settings.

## 512-token prompts

| Arm | Requests | TTFT median and range (s) | Decode median (tokens/s) | Engine prefill median (ms) | Source expert pages resident at request (median) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A+ | 10 | 47.966 [40.709, 55.721] | 21.444 | 47819.089 | 18.2% |
| C3 | 10 | 23.317 [22.363, 25.957] | 21.134 | 23159.028 | 18.2% |

| Arm | Comparison | Estimate | Observed pair range | Pass medians | Conditional 95% interval |
| --- | --- | ---: | ---: | ---: | ---: |
| A+ | inverse ttft vs Aplus | 1.000 | unavailable | unavailable | 1.000, 1.000 |
| A+ | paired decode tps gained vs Aplus | 0.000 | 0.000, 0.000 | 0.000, 0.000 | 0.000, 0.000 |
| A+ | paired ttft seconds saved vs Aplus | -0.000 | -0.000, -0.000 | -0.000, -0.000 | -0.000, -0.000 |
| C3 | inverse ttft vs Aplus | 2.057 | unavailable | unavailable | 1.943, 2.269 |
| C3 | paired decode tps gained vs Aplus | -0.411 | -2.487, 1.545 | -0.427, 0.818 | -2.141, 0.473 |
| C3 | paired ttft seconds saved vs Aplus | 24.915 | 18.062, 32.316 | 27.652, 22.348 | 23.119, 28.668 |

## 2048-token prompts

| Arm | Requests | TTFT median and range (s) | Decode median (tokens/s) | Engine prefill median (ms) | Source expert pages resident at request (median) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A+ | 10 | 156.689 [134.757, 178.406] | 21.224 | 156545.048 | 18.0% |
| C3 | 10 | 65.004 [52.486, 75.287] | 21.072 | 64874.492 | 18.3% |

| Arm | Comparison | Estimate | Observed pair range | Pass medians | Conditional 95% interval |
| --- | --- | ---: | ---: | ---: | ---: |
| A+ | inverse ttft vs Aplus | 1.000 | unavailable | unavailable | 1.000, 1.000 |
| A+ | paired decode tps gained vs Aplus | 0.000 | 0.000, 0.000 | 0.000, 0.000 | 0.000, 0.000 |
| A+ | paired ttft seconds saved vs Aplus | -0.000 | -0.000, -0.000 | -0.000, -0.000 | -0.000, -0.000 |
| C3 | inverse ttft vs Aplus | 2.410 | unavailable | unavailable | 2.127, 2.697 |
| C3 | paired decode tps gained vs Aplus | -0.149 | -2.270, 1.919 | -0.167, 0.049 | -1.270, 0.334 |
| C3 | paired ttft seconds saved vs Aplus | 90.801 | 71.079, 125.921 | 101.498, 86.386 | 73.967, 100.235 |

## Startup requests by position

Each pass began with the common file-specific source conditioning. Read and fault counts cover the engine process through the first token.

| Arm | Pass | Request position | Prompt tokens | Load to ready (s) | TTFT (s) | Decode (tokens/s) | Reads (GB) | Major faults |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A+ | 1 | 1 | 512 | 81.17 | 50.175 | 1.42 | 59.858 | 13,762 |
| A+ | 1 | 2 | 2048 | 81.17 | 124.916 | 3.73 | 73.010 | 50,582 |
| A+ | 1 | 3 | 512 | 81.17 | 33.903 | 20.55 | 27.862 | 19,653 |
| A+ | 1 | 4 | 2048 | 81.17 | 134.634 | 20.75 | 43.571 | 50,079 |
| A+ | 1 | 5 | 2048 | 81.17 | 155.090 | 21.50 | 42.987 | 45,657 |
| A+ | 1 | 6 | 512 | 81.17 | 48.411 | 20.46 | 18.083 | 15,552 |
| C3 | 1 | 1 | 512 | 170.28 | 27.844 | 3.74 | 22.423 | 10,752 |
| C3 | 1 | 2 | 2048 | 170.28 | 65.130 | 6.70 | 17.897 | 23,365 |
| C3 | 1 | 3 | 512 | 170.28 | 28.754 | 20.70 | 9.024 | 11,590 |
| C3 | 1 | 4 | 2048 | 170.28 | 62.754 | 20.44 | 10.461 | 20,095 |
| C3 | 1 | 5 | 2048 | 170.28 | 62.453 | 21.48 | 12.517 | 27,642 |
| C3 | 1 | 6 | 512 | 170.28 | 21.105 | 21.35 | 5.705 | 7,795 |
| C3 | 2 | 1 | 512 | 176.30 | 29.159 | 3.63 | 22.267 | 10,650 |
| C3 | 2 | 2 | 2048 | 176.30 | 74.783 | 7.59 | 19.599 | 27,250 |
| C3 | 2 | 3 | 512 | 176.30 | 24.055 | 21.19 | 10.899 | 12,465 |
| C3 | 2 | 4 | 2048 | 176.30 | 76.383 | 17.79 | 11.449 | 26,800 |
| C3 | 2 | 5 | 2048 | 176.30 | 55.405 | 18.38 | 7.565 | 18,132 |
| C3 | 2 | 6 | 512 | 176.30 | 20.421 | 21.25 | 6.268 | 9,879 |
| A+ | 2 | 1 | 512 | 83.16 | 48.392 | 1.38 | 59.660 | 13,939 |
| A+ | 2 | 2 | 2048 | 83.16 | 130.035 | 3.66 | 72.585 | 49,750 |
| A+ | 2 | 3 | 512 | 83.16 | 45.286 | 21.50 | 23.402 | 16,051 |
| A+ | 2 | 4 | 2048 | 83.16 | 148.241 | 21.25 | 40.276 | 45,955 |
| A+ | 2 | 5 | 2048 | 83.16 | 154.440 | 20.81 | 45.035 | 47,934 |
| A+ | 2 | 6 | 512 | 83.16 | 48.275 | 21.43 | 15.863 | 15,295 |

## Change within each measured launch

Last minus first measured position shows residual movement inside each launch. Exact request samples are retained.

| Arm | Pass | Prompt tokens | TTFT change (s) | Decode change (tokens/s) |
| --- | ---: | ---: | ---: | ---: |
| A+ | 1 | 512 | -2.621 | +0.578 |
| A+ | 1 | 2048 | -11.895 | -0.883 |
| C3 | 1 | 512 | -0.683 | +0.024 |
| C3 | 1 | 2048 | +12.528 | -0.148 |
| C3 | 2 | 512 | +0.284 | +2.148 |
| C3 | 2 | 2048 | +4.505 | -0.637 |
| A+ | 2 | 512 | -4.815 | -1.884 |
| A+ | 2 | 2048 | -23.387 | -2.506 |

## Load and memory by launch

| Arm | Pass | Load to ready (s) | Scope peak (GiB) | Host minimum available (GiB) |
| --- | ---: | ---: | ---: | ---: |
| A+ | 1 | 81.174 | 100.000 | 22.463 |
| C3 | 1 | 170.284 | 100.000 | 22.436 |
| C3 | 2 | 176.302 | 100.000 | 22.513 |
| A+ | 2 | 83.164 | 100.000 | 19.322 |

Source-page residency describes the external inode cache. Scope memory and GPU residency are separate quantities.

Native analysis `factory.spark_gap_analysis` version `1.8.0`, release `70ec6d82fffde1a81ab5a50ca0e2479f42d77678bb3b8c32e844fa8839dd833d`.

## Build exposure and quiet-only pairs

- `spark-owner-d-cpu.service` retained CPUs 12–19, nice 19 and idle I/O in its systemd properties.
- `spark-owner-c2-cpu.service` retained CPUs 12–19, nice 19 and idle I/O in its systemd properties.

| Build service invocation | Start UTC | Stop UTC in this run | Attempt |
|---|---|---|---|
| spark-owner-d-cpu.service | 2026-11-20T13:45:31.550698+00:00 | 2026-11-20T13:45:31.640578+00:00 | Preflight only |
| spark-owner-d-cpu.service | 2026-11-20T13:46:26.681790+00:00 | 2026-11-20T13:46:30.621806+00:00 | 51b98e442f1b4ba69cc7e879eb5b95c6 |
| spark-owner-d-cpu.service | 2026-11-20T13:48:29.851831+00:00 | Still active at GPU close | 87ecc8bf665f43729dd3a375a88699e3 |
| spark-owner-c2-cpu.service | 2026-11-20T13:46:07.028118+00:00 | 2026-11-20T13:46:11.413119+00:00 | 6e73a022cdac4b2ebd505b40c4a1acfb |
| spark-owner-c2-cpu.service | 2026-11-20T13:48:08.957594+00:00 | Still active at GPU close | ce1eef65da2341f59846b0c6bb7711a7 |
| spark-c2-placement-tier-build.service | 2026-11-20T13:45:29.860678+00:00 | 2026-11-20T13:45:34.025936+00:00 | 9f533251884a4a2eb9088d235398af91 |

The quiet-only subset ends at the first authorized preflight or build activity at 2026-11-20T13:45:29.860678+00:00. A request whose after-boundary crosses that cutoff stays in the screening set, including later gaps. The journal identifies active-service intervals. Boundary snapshots separately record visible compiler processes.

| Final A+ prompt | Repeat | Before UTC | After UTC | Intersecting service intervals | Compiler observed at boundary |
|---:|---:|---|---|---|---|
| 2048 | 7 | 2026-11-20T13:43:53.725005+00:00 | 2026-11-20T13:46:41.906715+00:00 | spark-c2-placement-tier-build.service, spark-owner-c2-cpu.service, spark-owner-d-cpu.service | None observed |
| 512 | 7 | 2026-11-20T13:46:41.982223+00:00 | 2026-11-20T13:47:30.394762+00:00 | None | None observed |
| 512 | 8 | 2026-11-20T13:47:30.467916+00:00 | 2026-11-20T13:48:25.424377+00:00 | spark-owner-c2-cpu.service | spark-owner-c2-cpu.service |
| 2048 | 8 | 2026-11-20T13:48:25.517402+00:00 | 2026-11-20T13:50:49.988538+00:00 | spark-owner-c2-cpu.service, spark-owner-d-cpu.service | spark-owner-c2-cpu.service, spark-owner-d-cpu.service |
| 2048 | 9 | 2026-11-20T13:50:50.060157+00:00 | 2026-11-20T13:53:15.776989+00:00 | spark-owner-c2-cpu.service, spark-owner-d-cpu.service | spark-owner-c2-cpu.service, spark-owner-d-cpu.service |
| 512 | 9 | 2026-11-20T13:53:15.858694+00:00 | 2026-11-20T13:54:01.788679+00:00 | spark-owner-c2-cpu.service, spark-owner-d-cpu.service | spark-owner-c2-cpu.service, spark-owner-d-cpu.service |
| 512 | 10 | 2026-11-20T13:54:01.864982+00:00 | 2026-11-20T13:54:44.890771+00:00 | spark-owner-c2-cpu.service, spark-owner-d-cpu.service | spark-owner-c2-cpu.service, spark-owner-d-cpu.service |
| 2048 | 10 | 2026-11-20T13:54:44.968216+00:00 | 2026-11-20T13:57:02.086020+00:00 | spark-owner-c2-cpu.service, spark-owner-d-cpu.service | spark-owner-c2-cpu.service, spark-owner-d-cpu.service |

| Prompt | Quiet-only repeat labels | Paired C3 TTFT saved s (range) | Paired C3 decode gained tok/s (range) |
|---:|---|---:|---:|
| 512 | 1, 2, 3, 4, 5, 6 | +26.796 [+23.160, +32.316] | -0.448 [-2.487, +0.127] |
| 2048 | 1, 2, 3, 4, 5, 6 | +100.235 [+73.967, +125.921] | -0.149 [-1.270, +0.605] |

Quiet-only rows give observed ranges. The ten-pair conditional bootstrap includes the build-overlapped reverse control and describes these run windows.

A separate agent reported a read-only text search lasting about 10 seconds within 13:48:23–13:51:25 UTC. That period is already in the screened portion. Its shared-I/O effect was not measured.
