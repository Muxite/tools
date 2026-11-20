## Direct seed mechanism and source-page coverage

On pass 2, 38.36% of sampled seeded-class file pages were resident after direct startup and 38.47% after stock A+ startup, before either server received a prompt.

| Arm | Pass | Load to ready s | Expert seed upload GiB | Direct read GiB | Direct ledger s |
|---|---:|---:|---:|---:|---:|
| A+ | 1 | 82.243 | — | — | — |
| C3-direct | 1 | 86.142 | 29.489 | 29.494 | 12.416 |
| C3-direct | 2 | 87.145 | 29.489 | 29.494 | 12.517 |
| A+ | 2 | 76.147 | — | — | — |

Both witnessed direct ledgers completed without failure or fallback. The source-page populations use the same actual seed IDs.

| Pass 2 after ready | Seeded class | Other expert class | Excluded boundary draws |
|---|---:|---:|---:|
| A+ | 38.47% (1,844 draws) | 39.30% (6,020 draws) | 11 |
| C3-direct | 38.36% (1,844 draws) | 39.20% (6,020 draws) | 11 |

Each launch supplies a post-conditioning capture, three after-warmup-pair captures and ten before-steady-request captures. The pass-2 post-ready sample is the only after-load comparison.

| Arm | Tokens | Before-request seeded / other median | Engine read MiB to first token, median [range] | Major faults to first, median [range] | Engine read MiB after first, median [range] |
|---|---:|---:|---:|---:|---:|
| A+ | 512 | 45.28% / 42.18% | 0.154 [0.000, 19.160] | 0 [0, 16] | 2.070 [0.000, 6.293] |
| A+ | 2048 | 45.30% / 42.12% | 2.006 [0.000, 25.031] | 5 [0, 13] | 0.123 [0.000, 40.914] |
| C3-direct | 512 | 43.92% / 42.36% | 4.451 [0.000, 48.855] | 6 [0, 38] | 0.000 [0.000, 80.539] |
| C3-direct | 2048 | 43.95% / 42.43% | 1.004 [0.000, 147.719] | 4 [0, 175] | 2.986 [0.000, 29.973] |

The analysis attachment retains both request phases, all individual timings, cgroup refaults and host NVMe deltas.

Post-ready was captured on pass 2 only, before any request in those scopes. The pass 1 warmup-pair samples start later.
A+ uses the comparison classes from actual C3-direct admissions. It has no startup profile seed.
Each stratum contributes one deterministic mincore observation. Weight estimates source file-cache occupancy. Pages with slice or tensor boundary overlap are excluded.
Device bank membership can change after startup. Phase reads are engine-process counters, with cgroup file refault and host NVMe activity retained separately.
This candidate/control comparison changes both profile seeding and its read path. A same-ELF mmap-seed comparison is needed to isolate O_DIRECT from profile admission.
