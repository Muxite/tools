# 60 GiB C3 versus A+ request I/O and scope review

The ten measured pairs include the final A+ control with authorized build exposure. The timing and I/O comparisons are screening.

| Prompt | Pairs | A+ / C3 TTFT (s) | Paired C3 TTFT added (s) | A+ / C3 decode (tok/s) | Paired C3 decode gain (tok/s) |
|---:|---:|---:|---:|---:|---:|
| 512 | 10 | 47.966 / 23.317 | -24.915 [-28.668, -23.119] | 21.444 / 21.134 | -0.411 [-2.141, +0.473] |
| 2048 | 10 | 156.689 / 65.004 | -90.801 [-100.235, -73.967] | 21.224 / 21.072 | -0.149 [-1.270, +0.334] |

Timing brackets are conditional 95% intervals within the two mirrored launch windows.

## Scope safety

| Arm | Pass | Launch to ready (s) | Peak cap usage (GiB) | Minimum host available (GiB) | memory.events max | OOM events |
|---|---:|---:|---:|---:|---:|---:|
| A+ | 1 | 81.174 | 100.000 | 22.463 | 1,187 | 0 |
| C3 | 1 | 170.284 | 100.000 | 22.436 | 1,022 | 0 |
| C3 | 2 | 176.302 | 100.000 | 22.513 | 1,197 | 0 |
| A+ | 2 | 83.164 | 100.000 | 19.322 | 1,269 | 0 |

All scopes exited normally under the 100 GiB cap with swap disabled and CPU affinity 0–7.

## Ten measured pairs per prompt

| Prompt | Phase | Counter | A+ median [min, max] | C3 median [min, max] | Paired A+ minus C3 median [min, max] |
|---:|---|---|---:|---:|---:|
| 512 | Start to first token | Engine reads (GB) | 14.674 [11.074, 18.433] | 2.768 [2.099, 5.435] | 11.616 [8.451, 15.654] |
| 512 | Start to first token | Engine major faults | 14,649.0 [12,714.0, 18,308.0] | 8,399.5 [6,868.0, 9,910.0] | 7,054.0 [2,804.0, 10,270.0] |
| 512 | First token to stream end | Engine reads (GB) | 0.012 [0.011, 0.012] | 0.012 [0.011, 0.012] | 0.000 [-0.000, 0.001] |
| 512 | First token to stream end | Engine major faults | 29.0 [27.0, 31.0] | 27.0 [26.0, 30.0] | 2.0 [-1.0, 4.0] |
| 2048 | Start to first token | Engine reads (GB) | 40.581 [29.810, 49.055] | 10.091 [6.883, 11.139] | 29.904 [22.927, 41.588] |
| 2048 | Start to first token | Engine major faults | 45,247.0 [37,632.0, 55,163.0] | 26,119.0 [8,498.0, 30,234.0] | 18,510.0 [13,150.0, 29,551.0] |
| 2048 | First token to stream end | Engine reads (GB) | 0.012 [0.011, 0.013] | 0.012 [0.012, 0.013] | -0.000 [-0.001, 0.001] |
| 2048 | First token to stream end | Engine major faults | 29.0 [26.0, 31.0] | 28.0 [27.0, 32.0] | 1.5 [-5.0, 3.0] |

Positive paired values mean fewer reads or faults in C3. Ranges here are observed pair ranges. Process read_bytes counts I/O charged to the engine by Linux. GPU copies and host-wide disk counters have separate accounting.

## Startup after identical source conditioning

| Arm | Pass | Position | Tokens | TTFT (s) | Decode (tok/s) | Reads before / after first token (GB) | Major faults before / after |
|---|---:|---:|---:|---:|---:|---:|---:|
| A+ | 1 | 1 | 512 | 50.175 | 1.421 | 59.858 / 15.222 | 13,762 / 6,054 |
| A+ | 1 | 2 | 2048 | 124.916 | 3.731 | 73.010 / 3.610 | 50,582 / 1,559 |
| A+ | 1 | 3 | 512 | 33.903 | 20.550 | 27.862 / 0.012 | 19,653 / 29 |
| A+ | 1 | 4 | 2048 | 134.634 | 20.752 | 43.571 / 0.013 | 50,079 / 29 |
| A+ | 1 | 5 | 2048 | 155.090 | 21.500 | 42.987 / 0.012 | 45,657 / 29 |
| A+ | 1 | 6 | 512 | 48.411 | 20.460 | 18.083 / 0.012 | 15,552 / 30 |
| C3 | 1 | 1 | 512 | 27.844 | 3.739 | 22.423 / 2.762 | 10,752 / 1,133 |
| C3 | 1 | 2 | 2048 | 65.130 | 6.700 | 17.897 / 1.376 | 23,365 / 689 |
| C3 | 1 | 3 | 512 | 28.754 | 20.703 | 9.024 / 0.012 | 11,590 / 30 |
| C3 | 1 | 4 | 2048 | 62.754 | 20.444 | 10.461 / 0.012 | 20,095 / 27 |
| C3 | 1 | 5 | 2048 | 62.453 | 21.483 | 12.517 / 0.012 | 27,642 / 29 |
| C3 | 1 | 6 | 512 | 21.105 | 21.349 | 5.705 / 0.011 | 7,795 / 26 |
| C3 | 2 | 1 | 512 | 29.159 | 3.627 | 22.267 / 2.882 | 10,650 / 1,214 |
| C3 | 2 | 2 | 2048 | 74.783 | 7.585 | 19.599 / 1.482 | 27,250 / 719 |
| C3 | 2 | 3 | 512 | 24.055 | 21.192 | 10.899 / 0.012 | 12,465 / 27 |
| C3 | 2 | 4 | 2048 | 76.383 | 17.789 | 11.449 / 0.012 | 26,800 / 27 |
| C3 | 2 | 5 | 2048 | 55.405 | 18.379 | 7.565 / 0.011 | 18,132 / 25 |
| C3 | 2 | 6 | 512 | 20.421 | 21.251 | 6.268 / 0.011 | 9,879 / 24 |
| A+ | 2 | 1 | 512 | 48.392 | 1.375 | 59.660 / 15.589 | 13,939 / 6,248 |
| A+ | 2 | 2 | 2048 | 130.035 | 3.656 | 72.585 / 3.737 | 49,750 / 1,489 |
| A+ | 2 | 3 | 512 | 45.286 | 21.497 | 23.402 / 0.012 | 16,051 / 28 |
| A+ | 2 | 4 | 2048 | 148.241 | 21.255 | 40.276 / 0.012 | 45,955 / 28 |
| A+ | 2 | 5 | 2048 | 154.440 | 20.814 | 45.035 / 0.012 | 47,934 / 29 |
| A+ | 2 | 6 | 512 | 48.275 | 21.435 | 15.863 / 0.012 | 15,295 / 30 |

## Process I/O in the quiet-only paired subset

| Prompt | Pairs | Phase | Paired C3 reads avoided in GB [min, max] | Paired C3 major faults avoided [min, max] |
|---:|---:|---|---:|---:|
| 512 | 6 | Start to first token | 10.547 [9.454, 12.853] | 6,033.0 [2,804.0, 10,270.0] |
| 512 | 6 | First token to stream end | 0.000 [-0.000, 0.001] | 0.5 [-1.0, 3.0] |
| 2048 | 6 | Start to first token | 27.531 [22.927, 35.797] | 18,030.5 [13,150.0, 29,134.0] |
| 2048 | 6 | First token to stream end | -0.001 [-0.001, 0.001] | -1.5 [-5.0, 3.0] |

## Verified native-bank shutdown counters

| Arm | Pass | Small ubatch ≤8 hits | Small ubatch misses | CPU misses | Demand upload MiB | Large batch cache copies | Large batch device-to-device MiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| A+ | 1 | 131,427 | 4,076 | 0 | 33,451.44 | 261,903 | 723,372.54 |
| C3 | 1 | 133,944 | 1,559 | 0 | 12,784.57 | 396,975 | 1,096,775.24 |
| C3 | 2 | 133,944 | 1,559 | 0 | 12,784.57 | 396,975 | 1,096,775.24 |
| A+ | 2 | 131,427 | 4,076 | 0 | 33,451.44 | 261,903 | 723,372.54 |

Counters cover the whole launch, including warmups. The small-ubatch category can include prefill and decode. Large-batch cache copies are device-local. Process read and fault counters use separate boundaries.

## Host file pages associated with actual C3 startup seeds


Both C3 passes admitted the same 7,432 experts and uploaded 63.875 GB at startup. The A+ comparison applies the same layer and expert IDs to its source pages.

| Arm | Pass | Post-ready seeded pages | Post-ready other expert pages | Excluded boundary draws |
|---|---:|---:|---:|---:|
| A+ | 1 | 16.54% (3,715 draws) | 18.13% (4,149 draws) | 11 |
| C3 | 1 | 34.06% (3,715 draws) | 5.11% (4,149 draws) | 11 |
| C3 | 2 | 33.83% (3,715 draws) | 4.87% (4,149 draws) | 11 |
| A+ | 2 | 16.66% (3,715 draws) | 18.32% (4,149 draws) | 11 |

| Arm | Prompt | Seeded before-request median [min, max] | Other before-request median [min, max] |
|---|---:|---:|---:|
| A+ | 512 | 18.35% [15.39%, 19.19%] (3,715 draws) | 17.82% [15.75%, 18.59%] (4,149 draws) |
| A+ | 2048 | 18.40% [15.95%, 18.81%] (3,715 draws) | 17.69% [15.67%, 18.54%] (4,149 draws) |
| C3 | 512 | 8.86% [8.31%, 9.30%] (3,715 draws) | 26.56% [25.92%, 26.93%] (4,149 draws) |
| C3 | 2048 | 9.05% [8.38%, 9.44%] (3,715 draws) | 26.55% [25.63%, 27.34%] (4,149 draws) |

The same deterministic page draws are weighted by their original stratum size and exclude slice-boundary pages. The JSON supplement retains all three post-warmup-pair observations per launch and separate cgroup/host evidence references. These estimates describe host file pages by startup admission class. Later evictions can change device-bank membership. Per-expert cache-hit causation remains unmeasured.


## Prospective scope replacement

The operator excluded `OPS/runs/p4-cache60-c3-pass-2-01` and named `OPS/runs/p4-cache60-c3-pass-2-retry-01` before its fresh launch.
Cap monitor read ENODEV as the cgroup vanished at shutdown. The process return code was not retained. Exclude the whole scope. The paired results use the fresh verified scope.
Amendment `spark-p4-cache60-build-overlap/raw/OPS/p4/cache-abba-60g-amendment.json@cb072674e5927e56b9a503a96ff4cef7b76b0f17ebe1002ed8297e09af6ed248` SHA256 `cb072674e5927e56b9a503a96ff4cef7b76b0f17ebe1002ed8297e09af6ed248`.


## Original native DO and build

Factory source task `spark-cache-residency-do-01` used original commit `ad2130b0126ad0c8f7ac33d966f828fc17f4528c`, source verifier call `c7981f3a-1d5b-4bbc-acb5-97326aeaec2a` and build attempt `32b595d1a67b489eb2fc8bc12ed985d5`.
The revision links the exact source decision, diff, verifier receipt, ELF manifest, and build receipts.


Native report `spark-p4-cache60-build-overlap/report.md` SHA256 `90341d85316b2df43f1edac3a76d3133ebc9d99d8ceb585c2dc7e2d7a780486a`.
Native verifier `spark-p4-cache60-build-overlap/verify-receipt.json` SHA256 `fdb49f102ad5b38ec320300329fac0268731944d5cae0118d4c75e6534fc989e`.
