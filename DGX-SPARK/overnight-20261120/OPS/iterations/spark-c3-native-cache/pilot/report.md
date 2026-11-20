# C3 native cache startup and warm-up pilot

Both 30-GiB launches kept warming across eight request positions, and the cache profile took 33.2 seconds more to become ready than stock.

## Launch and cache admission

| Arm | Launch to ready | Peak cgroup memory | Reclaim max events | Profile seeds | Initial upload |
|---|---:|---:|---:|---:|---:|
| C3-profile-on-speed-30720MiB | 110.343 s | 100.00 GiB | 1218 | 3686 | 31.664 GB |
| Aplus-speed-30720MiB | 77.154 s | 100.00 GiB | 1040 | — | — |

The profile seeds the existing stock bank during startup. Initial seed upload is separate from demand refill traffic.

| Arm | Actual bank | Seed time | Demand upload | Native lookup hits / misses | Large-prefill D2D experts | Evictions |
|---|---:|---:|---:|---:|---:|---:|
| C3-profile-on-speed-30720MiB | 30682.35 MiB | 26.066 s | 44517.30 MiB | 62,705 / 5,414 | 125,607 | 5366 |
| Aplus-speed-30720MiB | 30682.35 MiB | — | 53425.37 MiB | 61,624 / 6,495 | 116,607 | — |

## Request positions after conditioning

| Arm | Position | Prompt tokens | TTFT | Decode tok/s | Process reads / major faults to first token | Process reads / major faults afterward |
|---|---:|---:|---:|---:|---:|---:|
| C3-profile-on-speed-30720MiB | 1 | 512 | 43.479 s | 1.60 | 29.623 GB / 10,444 | 5.321 GB / 3,107 |
| C3-profile-on-speed-30720MiB | 2 | 2048 | 76.151 s | 4.07 | 16.298 GB / 12,146 | 1.687 GB / 940 |
| C3-profile-on-speed-30720MiB | 3 | 512 | 26.745 s | 4.32 | 4.756 GB / 4,908 | 1.632 GB / 907 |
| C3-profile-on-speed-30720MiB | 4 | 2048 | 53.425 s | 5.83 | 2.176 GB / 3,806 | 0.496 GB / 751 |
| C3-profile-on-speed-30720MiB | 5 | 2048 | 35.464 s | 20.88 | 0.180 GB / 311 | 0.007 GB / 6 |
| C3-profile-on-speed-30720MiB | 6 | 512 | 8.582 s | 6.79 | 0.080 GB / 139 | 0.107 GB / 181 |
| C3-profile-on-speed-30720MiB | 7 | 512 | 7.089 s | 20.70 | 0.023 GB / 30 | 0.000 GB / 0 |
| C3-profile-on-speed-30720MiB | 8 | 2048 | 13.843 s | 9.01 | 0.018 GB / 26 | 0.015 GB / 24 |
| Aplus-speed-30720MiB | 1 | 512 | 55.082 s | 1.32 | 44.538 GB / 13,634 | 7.626 GB / 4,103 |
| Aplus-speed-30720MiB | 2 | 2048 | 78.205 s | 4.17 | 23.522 GB / 25,009 | 1.682 GB / 816 |
| Aplus-speed-30720MiB | 3 | 512 | 27.786 s | 4.09 | 4.948 GB / 4,682 | 1.539 GB / 1,048 |
| Aplus-speed-30720MiB | 4 | 2048 | 55.819 s | 4.69 | 1.941 GB / 3,359 | 0.383 GB / 406 |
| Aplus-speed-30720MiB | 5 | 2048 | 39.372 s | 21.59 | 0.395 GB / 1,101 | 0.007 GB / 4 |
| Aplus-speed-30720MiB | 6 | 512 | 9.900 s | 5.55 | 0.190 GB / 304 | 0.460 GB / 667 |
| Aplus-speed-30720MiB | 7 | 512 | 15.662 s | 16.38 | 0.112 GB / 140 | 0.005 GB / 2 |
| Aplus-speed-30720MiB | 8 | 2048 | 26.979 s | 7.14 | 0.101 GB / 88 | 0.021 GB / 24 |

No sampled expert, Engram or dense pages were resident in either pack view immediately before each launch. Launch initialization can change residency before the first request.
Process counters come from one unchanged engine PID per launch. Resource snapshots span client request start to first token and first token to stream completion. The raw analysis retains cgroup file refaults and separate host NVMe counters. Host disk activity includes any other activity on the device.

The cache profile changed launch-to-ready by +33.189 s. Both launches used the same 30-GiB native-bank budget, with one discarded prompt per size and three further positions. Those positions describe the warm-up curve. A separate three-warmup, five-pair lab measures later behavior.

| Matched position | Tokens | TTFT saved | Decode gain | Process reads avoided to first token | Major faults avoided to first token | Greedy parity |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 512 | +11.603 s | +0.28 tok/s | +14.914 GB | +3,190 | matched |
| 2 | 2048 | +2.053 s | -0.09 tok/s | +7.224 GB | +12,863 | matched |
| 3 | 512 | +1.041 s | +0.23 tok/s | +0.192 GB | -226 | matched |
| 4 | 2048 | +2.394 s | +1.13 tok/s | -0.235 GB | -447 | matched |
| 5 | 2048 | +3.908 s | -0.71 tok/s | +0.215 GB | +790 | matched |
| 6 | 512 | +1.318 s | +1.24 tok/s | +0.110 GB | +165 | matched |
| 7 | 512 | +8.573 s | +4.33 tok/s | +0.089 GB | +110 | matched |
| 8 | 2048 | +13.136 s | +1.86 tok/s | +0.083 GB | +62 | matched |

Source, cap, prompt, raw request phases, residency, model identities and build receipts are linked in the iteration record.
Native analysis and exact recomputation used release `91368f73cda8f24a1a5618d721b115ab1602589e6840f89074afa8de107f0d2b`.
