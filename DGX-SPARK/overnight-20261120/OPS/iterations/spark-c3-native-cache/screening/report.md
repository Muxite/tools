# C3 60-GiB interim screening

At 60 GiB, C3 decoded 6.8× and 7.1× as fast as A-matched at 512 and 2048 tokens, while median time to first token rose to 5.2× and 5.3×.

- At 512 prompt tokens, C3 read a median 2.813 GB and recorded 8,044 engine major faults before the first token.
- At 2048 prompt tokens, C3 read a median 9.519 GB and recorded 24,703 engine major faults before the first token.

C3 took 167.276 s to become ready versus 75.132 s for A-matched, with 86.294 s in profile seeding and 63.875 GB in initial upload.

C3 logged 1.150 TB of aggregate large-prefill device-to-device copies across all 16 requests. This counter measures device-local copies. The request-phase tables separately show process reads and faults.

Host page pressure is one possible contributor to the first-token regression. The paired A-matched comparison includes the standing native bank and the seeding policy. The pending same-budget 60-GiB A+ arm is the control for separating the profile from the stock bank.

## Launch and cache admission

| Arm | Launch to ready | Peak cgroup memory | Reclaim max events | Profile seeds | Initial upload |
|---|---:|---:|---:|---:|---:|
| A-matched-speed-30720MiB | 75.132 s | 100.00 GiB | 1039 | — | — |
| C3-profile-on-speed-61440MiB | 167.276 s | 100.00 GiB | 1241 | 7432 | 63.875 GB |
| S-fair-steady | 42.055 s | 22.25 GiB | 0 | — | — |

The profile seeds the existing stock bank during startup. Initial seed upload is separate from demand refill traffic.

| Arm | Actual bank | Seed time | Demand upload | Native lookup hits / misses | Large-prefill D2D experts | Evictions |
|---|---:|---:|---:|---:|---:|---:|
| C3-profile-on-speed-61440MiB | 61401.18 MiB | 86.294 s | 12784.57 MiB | 133,944 / 1,559 | 396,975 | 1511 |

## Request positions after conditioning

| Arm | Position | Prompt tokens | TTFT | Decode tok/s | Process reads / major faults to first token | Process reads / major faults afterward |
|---|---:|---:|---:|---:|---:|---:|
| A-matched-speed-30720MiB | 1 | 512 | 49.649 s | 2.71 | 30,794.727 MiB / 90,175 | 4,889.555 MiB / 25,287 |
| A-matched-speed-30720MiB | 2 | 2048 | 75.476 s | 2.75 | 4,118.836 MiB / 5,899 | 3,292.707 MiB / 39,973 |
| A-matched-speed-30720MiB | 3 | 512 | 31.853 s | 2.85 | 1,012.613 MiB / 3,000 | 1,341.738 MiB / 8,379 |
| A-matched-speed-30720MiB | 4 | 2048 | 18.976 s | 2.95 | 2.035 MiB / 3 | 3.949 MiB / 38 |
| A-matched-speed-30720MiB | 5 | 2048 | 12.092 s | 3.02 | 0.062 MiB / 1 | 0.000 MiB / 0 |
| A-matched-speed-30720MiB | 6 | 512 | 4.706 s | 3.00 | 0.000 MiB / 0 | 0.125 MiB / 1 |
| C3-profile-on-speed-61440MiB | 1 | 512 | 28.751 s | 3.50 | 21,339.000 MiB / 10,730 | 2,870.012 MiB / 1,591 |
| C3-profile-on-speed-61440MiB | 2 | 2048 | 75.111 s | 6.88 | 22,679.711 MiB / 33,590 | 1,345.848 MiB / 703 |
| C3-profile-on-speed-61440MiB | 3 | 512 | 22.972 s | 18.32 | 9,659.121 MiB / 11,847 | 11.762 MiB / 30 |
| C3-profile-on-speed-61440MiB | 4 | 2048 | 69.359 s | 21.27 | 11,262.422 MiB / 27,420 | 11.879 MiB / 28 |
| C3-profile-on-speed-61440MiB | 5 | 2048 | 60.909 s | 20.03 | 9,686.949 MiB / 26,585 | 11.879 MiB / 28 |
| C3-profile-on-speed-61440MiB | 6 | 512 | 23.667 s | 18.01 | 5,258.109 MiB / 9,942 | 11.617 MiB / 28 |
| S-fair-steady | 1 | 512 | 5.299 s | 9.80 | 7,152.832 MiB / 48 | 1,377.832 MiB / 10,956 |
| S-fair-steady | 2 | 2048 | 18.330 s | 14.80 | 7,955.207 MiB / 0 | 224.742 MiB / 1,833 |
| S-fair-steady | 3 | 512 | 7.302 s | 17.10 | 6,111.539 MiB / 0 | 1.449 MiB / 14 |
| S-fair-steady | 4 | 2048 | 22.584 s | 16.90 | 8,183.410 MiB / 0 | 1.781 MiB / 5 |
| S-fair-steady | 5 | 2048 | 25.069 s | 17.00 | 8,293.738 MiB / 0 | 0.270 MiB / 0 |
| S-fair-steady | 6 | 512 | 9.785 s | 17.00 | 6,343.242 MiB / 0 | 0.145 MiB / 2 |

No sampled expert, Engram or dense pages were resident in either pack view immediately before each launch. Launch initialization can change residency before the first request.
Process counters come from one unchanged engine PID per launch. Resource snapshots span client request start to first token and first token to stream completion. The raw analysis retains cgroup file refaults and separate host NVMe counters. Host disk activity includes any other activity on the device.

## Cold positions matched by ordinal

| Candidate and control | Position | Tokens | TTFT saved | Decode gain | Reads / major faults avoided to first token | Greedy parity |
|---|---:|---:|---:|---:|---:|---|
| 60-GiB profile and bank versus stock without a native bank | 1 | 512 | +20.899 s | +0.79 tok/s | +9.915 GB / +79,445 | diverged |
| 60-GiB profile and bank versus stock without a native bank | 2 | 2048 | +0.365 s | +4.12 tok/s | -19.462 GB / -27,691 | diverged |
| 60-GiB profile and bank versus stock without a native bank | 3 | 512 | +8.881 s | +15.47 tok/s | -9.067 GB / -8,847 | diverged |
| 60-GiB profile and bank versus stock without a native bank | 4 | 2048 | -50.383 s | +18.33 tok/s | -11.807 GB / -27,417 | diverged |
| 60-GiB profile and bank versus stock without a native bank | 5 | 2048 | -48.817 s | +17.01 tok/s | -10.157 GB / -26,584 | diverged |
| 60-GiB profile and bank versus stock without a native bank | 6 | 512 | -18.961 s | +15.01 tok/s | -5.514 GB / -9,942 | diverged |
| 60-GiB profile versus fair Strata engine and pack | 1 | 512 | -23.452 s | -6.30 tok/s | -14.875 GB / -10,682 | diverged |
| 60-GiB profile versus fair Strata engine and pack | 2 | 2048 | -56.781 s | -7.92 tok/s | -15.440 GB / -33,590 | diverged |
| 60-GiB profile versus fair Strata engine and pack | 3 | 512 | -15.670 s | +1.22 tok/s | -3.720 GB / -11,847 | diverged |
| 60-GiB profile versus fair Strata engine and pack | 4 | 2048 | -46.775 s | +4.37 tok/s | -3.229 GB / -27,420 | diverged |
| 60-GiB profile versus fair Strata engine and pack | 5 | 2048 | -35.841 s | +3.03 tok/s | -1.461 GB / -26,585 | diverged |
| 60-GiB profile versus fair Strata engine and pack | 6 | 512 | -13.882 s | +1.01 tok/s | +1.138 GB / -9,942 | diverged |

## Five post-warmup pairs

| Arm | Tokens | TTFT median [min, max] s | Decode median [min, max] tok/s | Last minus first TTFT / decode |
|---|---:|---:|---:|---:|
| A-matched-speed-30720MiB | 2048 | 12.051 [12.010, 12.548] | 3.011 [2.998, 3.030] | +0.497 s / +0.008 tok/s |
| A-matched-speed-30720MiB | 512 | 4.557 [4.550, 4.607] | 3.002 [2.997, 3.031] | -0.056 s / -0.033 tok/s |
| C3-profile-on-speed-61440MiB | 2048 | 63.520 [49.839, 69.472] | 21.262 [20.520, 21.479] | +19.633 s / -0.674 tok/s |
| C3-profile-on-speed-61440MiB | 512 | 23.886 [21.480, 27.926] | 20.364 [16.303, 21.356] | +6.446 s / -0.037 tok/s |
| S-fair-steady | 2048 | 26.807 [21.864, 30.614] | 17.100 [17.000, 17.200] | +8.750 s / +0.100 tok/s |
| S-fair-steady | 512 | 12.313 [10.175, 13.041] | 17.200 [13.400, 17.300] | +2.138 s / +3.800 tok/s |

| Arm | Tokens | Process reads to first token (MiB) | Major faults to first token | Process reads afterward (MiB) | Major faults afterward |
|---|---:|---:|---:|---:|---:|
| A-matched-speed-30720MiB | 2048 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| A-matched-speed-30720MiB | 512 | 0.000 [0.000, 0.188] | 0.000 [0.000, 2.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| C3-profile-on-speed-61440MiB | 2048 | 9077.891 [6260.219, 11529.289] | 24703.000 [8310.000, 27309.000] | 11.371 [10.980, 11.941] | 27.000 [27.000, 29.000] |
| C3-profile-on-speed-61440MiB | 512 | 2682.957 [2354.750, 5524.754] | 8044.000 [7938.000, 9116.000] | 11.234 [11.172, 12.484] | 27.000 [27.000, 34.000] |
| S-fair-steady | 2048 | 8560.609 [8555.277, 8560.766] | 0.000 [0.000, 0.000] | 0.199 [0.000, 3.355] | 0.000 [0.000, 0.000] |
| S-fair-steady | 512 | 6360.496 [6360.059, 6360.660] | 0.000 [0.000, 0.000] | 0.027 [0.000, 0.180] | 0.000 [0.000, 1.000] |

| Candidate and control | Tokens | TTFT saved s | Decode gain tok/s | Greedy parity |
|---|---:|---:|---:|---|
| 60-GiB profile and bank versus stock without a native bank | 512 | -19.329 [-23.374, -16.873] | 17.362 [13.300, 18.325] | diverged |
| 60-GiB profile and bank versus stock without a native bank | 2048 | -51.488 [-56.924, -37.788] | 18.232 [17.521, 18.474] | diverged |
| 60-GiB profile versus fair Strata engine and pack | 512 | -12.219 [-15.613, -9.363] | 3.264 [-0.997, 7.956] | diverged |
| 60-GiB profile versus fair Strata engine and pack | 2048 | -36.422 [-41.381, -27.975] | 4.162 [3.520, 4.379] | diverged |

Ranges summarize the five observed paired positions within one launch per arm. Persistent movement across positions indicates residual warming or drift. Comparisons across cache budgets or Strata packs describe the named settings and engine differences. Greedy parity is reported separately. Retain mirrored launch replication for a causal performance decision.

## Greedy output checks

| Arm | Prompt tokens | Within-arm content and reasoning stability | Content SHA256 prefix |
|---|---:|---|---|
| A-matched-speed-30720MiB | 2048 | stable | `fbcc592f6770` |
| A-matched-speed-30720MiB | 512 | stable | `e7d866c0639c` |
| C3-profile-on-speed-61440MiB | 2048 | stable | `b2881b1b899a` |
| C3-profile-on-speed-61440MiB | 512 | stable | `ca9f89c46a40` |
| S-fair-steady | 2048 | stable | `ad42523685cf` |
| S-fair-steady | 512 | stable | `1dc4cb2ce81c` |

Cross-arm equality is shown in the paired tables. Timing comparisons use the actual generated sequences. Accuracy remains unmeasured.

The C3 60-GiB content and reasoning hashes also match the earlier A+ 30-GiB warm-up pilot at 2048 tokens, 512 tokens. That historical hash check uses a different cache budget.

## Strata engine prefill counters

Native engine log `spark-c3-native-cache/screening/scopes/strata-steady-fair-01/engine.log` and parsed prefill counters `spark-c3-native-cache/screening/scopes/strata-steady-fair-01/prefill-streaming.json` are retained separately from request process and NVMe snapshots.

The final logged 2048-token CUDA0 prefill streamed 1,530 experts from files and 4,547 from the layer cache. The engine reported 8.9 GB unbuffered and 4.4 GB through page cache, with 20365 ms of compute wait for reads.
I/O workers accumulated 119645 ms of activity across threads.

Worker times can overlap one another and other prefill work. The engine counters have their own boundaries and remain separate from client TTFT, process reads and GPU copies.

Source, cap, prompt, raw request phases, residency, model identities and build receipts are linked in the iteration record.
Native analysis and exact recomputation used release `4c486958fd4f149f194eebd642ef2a464adc7332a933ecc3d8179e532eb67309`.
