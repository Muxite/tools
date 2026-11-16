Exported verbatim from immutable observation `obs-final-report`. The agent preserved this report in evidence after two local report-file writes failed. This file was exported by the parent orchestrator.

# Branch exploration report

Task: night-branch-jiuwen-v1. Result: report_inconclusive.
Decision records 1–3 selected and revised the work; terminal decision follows this report.
The fixed task is a CPU branch exploration, separate from engine benchmarking.
No GPU, model launch, job, compilation, native_experiment, source/configuration edit, network command, commit or promotion was performed.

## Branch outcomes

The host suggestion graph began at graph_rev 1. Decision 1 cancelled its five unrelated suggestions; branch work used CAS revisions and readiness/status reads. The final branch graph is revision 13.

| Branch | Reservation (CPU seconds) | Outcome | Evidence |
| --- | ---: | --- | --- |
| scratch-residency | 12 | Qualitative work complete; synthetic payload reuse verified, actual Strata memory benefit unknown | obs-residency-audit |
| prefill-scope | 12 | Qualitative work complete; treatment exposure checked, engine correctness/benefit unresolved | obs-prefill-coverage |
| workflow-batch | 12 | Qualitative work complete; pinned CPU overhead favors cohesive batching, current implementation unmeasured | obs-workflow-costs |
| workflow-release-only | 6 | Pruned: sealed-release reuse alone does not explain most observed workflow reduction; its small measured effect is retained | obs-workflow-costs, operator-extra-3, operator-extra-4 |
| prefill-divergence | 12 | Completed continuation of prefill-scope; original token divergence localized and next reference test designed | obs-prefill-divergence-design |

Reservations total 54 of 60 CPU seconds; 6 remain unallocated. Pruning did not release its reservation. These are accounting reservations, not measured CPU consumption. GPU allocation and use were zero. No branch_measurement was recorded: all branch findings were attached qualitatively. The optional capability lists are references, not evidence every listed operation ran.

Thirteen new analysis calls succeeded: memory_residency_lab plan/verify; strata_budget_workbench verify_startup for retained A/B/C logs and summarize_memory for original speed-cell extrema separately by arm; prefill_chunk coverage for original, later and proposed boundary lengths; cc_workflow_lab analyze_receipts on an explicitly historical fixture; and methodology_transfer_lab design_trial. Their actual receipt outputs are retained in the observations and embedded structured report. No new performance benchmark was run.

## Measurements and their limits

### Original manual engine round — unchanged

Evidence: manual-engine-evidence, manual-engine-analysis, input-native-contract and copied native records.

The frozen exploratory order was A/B/C/C/B/A, two fresh cells per arm. A used a 76,000,000,000-byte resident expert budget and chunk 256; B changed only the budget to 68,000,000,000; C changed only the chunk to 1024. Full six-expert routing was retained. The timing shape was pg512/tg128; startup was excluded and the first request in each process was discarded.

The original operator-reported aggregates remain:

| Arm | Native combined output tokens/s | Native decode tokens/s | Native prefill tokens/s |
| --- | ---: | ---: | ---: |
| A | 8.526531056335056 | 13.889265659333207 | 88.33348189767463 |
| B | 9.244591673126646 | 13.780777967981223 | 112.33900635563779 |
| C | 10.605098180010495 | 13.982601856336048 | 175.6171180956519 |

These are the source's existing aggregates, not a new pooled comparison with later inputs. Original cross-arm speed outputs differ in every listed speed case, although eight zero-shot ARC answers agree. Two cells per arm provide weak uncertainty estimates. Matching sampled answers is not numerical equivalence or acceptance.

The CPU startup parser independently validated requested=effective and sufficient safe budget, all 40 layer placements and aggregate identity on the retained A1, B2 and C3 speed logs. A/C retain 8,843 experts with aggregate 0f85bacd1770a4f9; B retains 7,911 with aggregate 95fe419aa1d98913. These are retained startup facts, not fresh runtime qualification.

Original speed-cell memory extrema were summarized separately by arm:

| Arm | Maximum recorded cgroup kernel peak, bytes | Minimum recorded host MemAvailable, bytes |
| --- | ---: | ---: |
| A | 20,157,755,392 | 35,371,913,216 |
| B | 30,741,258,240 | 43,942,330,368 |
| C | 22,035,554,304 | 36,678,455,296 |

Each supplied summary row was one original cell's extrema, not an instantaneous sample. The capsule's samples=2 means two cell-summary records; the original monitor counts were A1=113, B2=103, C3=99, C4=100, B5=103, A6=104. Maxima and minima need not be simultaneous. Cgroup accounting/page cache and global host availability are separate and cannot be added or treated as exact GPU/physical memory. The lower resident budget therefore does not establish a measured peak reduction.

### Historical scratch component

Evidence: input-memory-round1, input-memory-examples, obs-residency-audit.

The historical ARM64 native round is explicitly dated 2026-11-15T06:26:40Z. Its lifetimes are synthetic. The current Python plan and independent byte replay reproduce 31,457,280 bytes of independent aligned payload versus a 14,680,064-byte arena: 16,777,216 bytes (16 MiB, 53.33%) saved in this reference. Replay checked 35,651,584 bytes successfully.

Historical native allocation/touch/check times were 17.0482 ms for the baseline and 18.2027 ms for the arena with different checking workloads. They do not establish faster execution. This task did not call native_experiment or build a binary. Actual Strata allocation sizes, asynchronous completion lifetimes, aligned base, persistent buffers and physical residency remain prerequisites.

### Separately pinned later long-prefill evidence

Evidence: operator-extra-1 / inputs/extra-1-analysis.json.

This is pg4096/tg16 in A/C/C/A order, two fresh cells per arm and two measured requests per cell, with startup excluded and one warmup discarded. The retained reported prefill rates are 150.92212274765956 versus 246.21932214546234 tokens/s (ratio 1.6314329381461117). Native combined output rates are 0.5669516779997944 versus 0.903110368553697 tokens/s (ratio 1.5929230013744213). Decode rates are 14.797345726110377 versus 14.801452392516014 tokens/s.

The listed canonical outputs and placement aggregates match in this separate workload. This is descriptive prompt-heavy evidence, not official benchmark execution, cold-storage performance, quality certification or a repair of original pg512/tg128 divergence.

### Separately pinned later quality evidence

Evidence: operator-extra-2 / inputs/extra-2-analysis.json; obs-prefill-coverage.

This is adapted eight-shot ARC-Challenge on 16 unique questions with independently chosen train demonstrations, A/C/C/A order. All cells report 16/16 correct, valid answers and matching output tokens in listed comparisons. It is not an official full ARC score or population noninferiority.

Current coverage calls predict zero changed chunk counts among the original eight prompts of 70–129 tokens: one chunk in both arms. The later 16 prompts of 560–619 tokens predict three baseline chunks versus one candidate chunk in every case. Count coverage is static; it does not itself establish runtime engagement, kernels or correctness. The later quality protocol remains distinct from both timing workloads.

### Separately pinned factory overhead evidence

Evidence: operator-extra-3 / inputs/extra-3-measurements.json; obs-workflow-costs.

The current capsule reanalyzed an explicitly historical 24-invocation qualification fixture across seven packages: total historical elapsed 4.135145907755941 seconds and zero failed rows. This is not the elapsed time of the current analysis, nor a GPU or engine measurement.

Separate pinned actual Host comparisons report:

| CPU workflow comparison | Baseline median seconds | Candidate median seconds | Reported ratio |
| --- | ---: | ---: | ---: |
| Prepare each versus sealed-release reuse | 1.2541592760000002 | 1.1921147625000001 | 1.0520457555360574 |
| Prepare each versus cohesive batching | 1.2411089450000001 | 0.17040512400000002 | 7.283284186923862 |

The baselines belong to separate matched comparisons. They show why release reuse alone was pruned as the principal lever; they do not mean release reuse has zero benefit. Cold seal, warm preparation, direct/instrumented fixture analysis, subprocess and actual Host observations retain their separate original scopes. Linux process lifetime RSS and Python traced allocations are not incremental per-operation memory. No new benchmark_fixture or performance measurement was executed.

Evidence: operator-extra-4 / inputs/extra-4-inventory.json.

Fresh inventory of 262 distribution rows reports standalone medians 0.090412838 versus 0.032209397 seconds (ratio 2.807032928930647). Its separate actual Host comparison reports 0.170421787 versus 0.1118217855 seconds (ratio 1.5240481650152153). Retained checks report equal outputs/provenance, rejected missing grant, no cache, mutation controls passed, and metadata reads 14 versus 6.

Separate traced Python peaks are 1,260,379 versus 1,260,639 bytes; they are not RSS or child memory. Inventory, batching and release-reuse ratios cannot be multiplied, treated as the same workload or translated into engine speed.

The four extra files were fully read through artifact previews, hash checked against the pinned artifacts, and matched retained observation contents. None contains an explicit measurement timestamp. Those dates remain unknown: task ingestion time is not measurement time. The original engine contract's 2026-11-15 hard stop is likewise not a timestamp for every measurement. The dated historical scratch round remains separate.

## Evidence-driven continuation

Evidence: obs-prefill-coverage, obs-prefill-divergence-design; raw A1/C3 cells and stdin.

The later quality protocol narrows the treatment-exposure gap. It does not resolve the original known full-generation mismatch. The continuation therefore kept the original pg512/tg128 shape rather than selecting only passing short-output workloads.

Actual retained A1 and C3 output IDs first differ at zero-based index 49: the 50th generated token is 10367 versus 32187. Both finish with length and generate 128 tokens. Their first 49 generated tokens agree, but canonical output digests differ. All four request IDs repeat identical stdin, decoding and outputs within each arm; they are not four independent prompts. The raw stdin includes temperature=0, top_p=1, top_k=1, min_p=0, seed=42, spec=0. Actual A/C complete stdin artifacts share SHA256 fa451cb5fbeb0325187a15ce9a4b0aba8a4638b343ad87f9c4063856fe385e77.

The new methodology_transfer_lab design_trial receipt proposes one changed variable, prefill chunk 256 to 1024, with operator_reference_comparison first and balanced 512/128 shape. Its runtime_authorized value is false. Later ABBA advice is not an execution grant.

The supplementary proposed lengths 255,256,257,511,512,513,1023,1024,1025,4096 predict changed counts in eight of ten cases. Lengths 255/256 are negative exposure controls. These are lengths, not authored/tokenized prompts, quality measurements or executed tests.

The next useful bounded experiment is a numerical reference diagnostic on that retained 512-token input. Teacher-force the shared first 49 output tokens and compare the operator/logit state at token 50 while changing only chunk size. Preserve model/tokenizer/image, full six routing, 76e9 budget, decoding, native admission, complete placement and output/finish identity. First locate and bound any mismatch; stop on reference failure, missing engagement/identity or the one-trial budget. Do not reinterpret the original exact-trajectory failure through a later semantic protocol.

This proposal requires an existing numerical reference/observer and separate frozen execution authority. Neither is supplied for current execution. Supplementary long-prefill, decode-heavy or boundary tests need separately frozen workloads and rules; the current task and original contracts remain unchanged.

## Pareto result and stop

Evidence: obs-final-branch-comparison; actual branch_workbench.compare receipt.

Compare returned groups=[] and all five branches in unknown. Throughput, peak memory and quality remain null for current-task branch vectors. No complete vector with an identical scope/key exists, so there is no Pareto winner, accepted engine gain or promotion.

The bounded exploration is complete: distinct branches were reserved, actual CPU receipts were retained and attached, a completed parent was refined using evidence, an unsupported alternative was pruned and unknowns preserved. Numerical correctness, physical memory, broad quality and comparable current-task measurements remain missing. Additional CPU recipes cannot resolve those missing runtime prerequisites.

Two shell input-read commands failed before execution with a bwrap loopback permission error. Evidence/artifact APIs supplied the inputs. An initial evidence query with limit=100 failed validation and was corrected to 50; a separate task-contract evidence read returned NOT_FOUND. These are retained limitations, not successful actions or authority to change the fixed task. No failed receipt was counted as successful.

Local Markdown/JSON report file creation also failed through the file-editing tool, including a retry at the workspace root. No local report path is claimed. This complete report and its structured receipt data are retained as immutable evidence instead.

The final decision is report_inconclusive.

