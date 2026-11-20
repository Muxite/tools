# Selected CC review: DeepSeek versus Granite

2026-11-20 UTC. Read-only source review of the five selections in
`OPS/cc-candidate-index.json` and current 1.1.1 GUIDE/METHOD files. No edits,
builds, model executions or additional output into frozen inputs. Diff references
below use the original patch line numbers, which remain pinned by the index.

The strict A profile does not activate all five current products. Preserve that
baseline and label separate activation controls explicitly; changing slot count,
thread count, batch shape, checkpoint policy or placement together with a CC
would confound a claim of gain attributable to that CC alone.

| Proven constraint or retained evidence | Implication / next evidence |
|---|---|
| A actually initializes **20 threads and 4 slots** under the eight-CPU cgroup ([A log](~/predemo-spark/OPS/runs/a-first-load-retry/stderr.log:7)). Stock auto-slot logic sets 4 ([server.cpp](~/predemo-spark/llama.cpp-stock/tools/server/server.cpp:129)); Linux CPU detection enumerates all physical cores, independently of affinity ([common.cpp](~/predemo-spark/llama.cpp-stock/common/common.cpp:92)). | The cap limits CPU execution, not worker count. Oversubscription is real; its timing cost remains a hypothesis. `-t 8` would be a recorded profile deviation and needs its own matched stock control, not silent replacement of A. |
| Predictor explicitly rejects more than one configured slot ([WO4](~/predemo-spark/inputs/ab/runs-r2/wo4-C/candidate.diff:638)); mapper rejects `n_parallel != 1` ([WO5](~/predemo-spark/inputs/ab/runs-r2/wo5-C/candidate.diff:103)). One occupied slot in a four-slot server does not qualify. | Their strict-A gate-on arms should report inactive fallback. An eligible single-slot profile requires a same-profile stock comparison. Expanding the capsules to multi-slot serving is a semantic change requiring orchestrator review. |
| Mapper also rejects checkpoint-enabled paths ([WO5](~/predemo-spark/inputs/ab/runs-r2/wo5-C/candidate.diff:87)). Stock defaults are 32 checkpoints and `swa_full=false` ([common.h](~/predemo-spark/llama.cpp-stock/common/common.h:600)); this DeepSeek model reports `n_swa=128` ([model log](~/predemo-spark/logs/smoke-a.log:188)); server derives `n_swa` accordingly ([server-context.cpp](~/predemo-spark/llama.cpp-stock/tools/server/server-context.cpp:1445)). | `-np 1` alone is insufficient. A separately frozen eligible control would also need a recorded checkpoint-policy change, e.g. stock's `--ctx-checkpoints 0`. Supporting checkpoint paths instead needs capsule semantic review. No such change was applied. |
| Mapper computes `limit = n_batch - n_batch % n_ubatch` ([WO5](~/predemo-spark/inputs/ab/runs-r2/wo5-C/candidate.diff:29)). Stock defaults are 2048/512 ([common.h](~/predemo-spark/llama.cpp-stock/common/common.h:479)). | At unchanged effective defaults, its cap equals stock's cap: there is no changed cut to attribute a scheduling gain to. GUIDE requires changed-cut evidence; an active marker alone is insufficient. Misaligned widths are acceptance probes, not an unlabelled faster A. |
| Cache and predictor reject native MoE cache: `cparams.moe_cache_size > 0` ([WO2](~/predemo-spark/inputs/ab/runs-r2/wo2-C/candidate.diff:52)) and `has_moe_cache` ([WO4](~/predemo-spark/inputs/ab/runs-r2/wo4-C/candidate.diff:648)). Cache GUIDE explicitly mandates this independent bypass. | A+ is a valid comparator, but these products cannot add an engaged improvement on A+ as currently written. Native-cache coexistence requires capsule semantic review; do not remove the guards by hand. |
| Placement needs both gate `1` and an explicit plan ([WO3](~/predemo-spark/inputs/ab/runs/wo3-C/candidate.diff:29)). It rejects plan matches overlapping existing stock overrides ([WO3](~/predemo-spark/inputs/ab/runs/wo3-C/candidate.diff:283)). A's `--cpu-moe` already overrides expert tensors. Conflict checking follows the attempted planned load ([WO3](~/predemo-spark/inputs/ab/runs/wo3-C/candidate.diff:350)). | An expert plan plus A's broad CPU override is an inactive-fallback case, potentially with a second load. Plan admission must be reasoned before spending a DeepSeek load. An alternate placement profile must have a matched stock `-ot` control and remain capped. Reconciliation/precedence changes require capsule semantic review. |
| Placement `cap_bytes` is CPU device **total memory**, and `peak_bytes` is summed host model-buffer allocation ([WO3](~/predemo-spark/inputs/ab/runs/wo3-C/candidate.diff:323), [readback](~/predemo-spark/inputs/ab/runs/wo3-C/candidate.diff:443)). The patch logs planned/actual buffer names but does not assert equality in the readback loop ([WO3](~/predemo-spark/inputs/ab/runs/wo3-C/candidate.diff:249)). | These fields are not the 100 GiB cgroup budget, RSS peak or a verified whole-run capacity ledger. GUIDE's broader capacity/binding requirements remain unproven. Read back every assignment; do not treat the active marker as proof of capacity safety or exact placement. |
| Selected recorder historical score passes amended v4, but normal S6 has **1151 records / 1152 expected / lost=1** in both configs; S5L has **767 / 768 / lost=1** ([score](~/predemo-spark/inputs/ab/out-r2/wo1-C/score.json)). Recorder GUIDE/METHOD require zero loss for normal full acceptance. | Historical scorer pass is valid under its amendment, but does not establish full capsule acceptance. Find the missing event through the existing capsule method before making a zero-loss claim. No scorer relaxation is justified. Recorder `active` is emitted at output setup, before eligible routes are observed ([WO1](~/predemo-spark/inputs/ab/runs-r2/wo1-C/candidate.diff:346)); require actual JSONL coverage. |

## DeepSeek-specific activation and timing hypotheses

- **Predictor shape support is plausible, not demonstrated.** DeepSeek is
  `deepseek41`, 40 layers, 384 experts/6 selected; the candidate limits are
  512 layers/1024 experts ([hparams](~/predemo-spark/llama.cpp-stock/src/llama-hparams.h:11)),
  and only GROVEMOE is explicitly excluded. DeepSeek41 has gate/up/down expert
  tensors ([loader](~/predemo-spark/llama.cpp-stock/src/models/deepseek41.cpp:210))
  and uses the shared named MoE graph. Eligible activation still needs mapped
  host projections and actual selected-expert copy callbacks. On mixed GPU/CPU
  graphs it deliberately uses copy observations, not the CPU eval callback
  ([WO4](~/predemo-spark/inputs/ab/runs-r2/wo4-C/candidate.diff:34)).
  CUDA offload thresholds, actual tensor placement, and graph splits can leave
  that path inactive even for a long prompt.
- **Predictor benefit is bounded and presently unattributed.** It hints four
  experts, charges at most 8 MiB per request and sends `MADV_WILLNEED` through a
  worker ([WO4](~/predemo-spark/inputs/ab/runs-r2/wo4-C/candidate.diff:197)).
  DeepSeek selects six experts per token; unions over 512-row batches may be
  much wider. Its teardown prints `bytes_useful_at_consumption=0` literally
  ([WO4](~/predemo-spark/inputs/ab/runs-r2/wo4-C/candidate.diff:621)).
  Hits/lead samples therefore do not prove useful physical I/O or a Strata-sized
  win. Warm, already resident pages may leave little page-fault work to overlap.
- **Cache engagement does not prove aggregate traffic reduction.** It only
  accepts exact CUDA destination representation and verified read-only shared
  GGUF host mappings ([WO2](~/predemo-spark/inputs/ab/runs-r2/wo2-C/candidate.diff:388));
  first fills add a device-to-device staging copy, hits add another device copy,
  and its default total request is 64 MiB. On Spark shared physical memory,
  avoided uploads need not reduce total memory traffic or TTFT. Require positive
  reuse/saved-byte counters and measured time; inspect cap, leases, eviction and
  lifetime behavior on the real mixed backend. A static global pool covers this
  cache, not a combined recorder/predictor/weights/KV admission ledger.
- **Recorder perturbation must be measured.** It installs an eval callback and
  reads selected tensors; preservation of fusion is attempted but is not a
  hardware-overhead measurement. GUIDE's default 3% overhead bound and complete
  route/byte coverage remain pending on DeepSeek.

## Combined D is a composition task

The selected patches independently pass read-only apply checks against stock;
that does not establish composition. Recorder and predictor replace the same
`process_ubatch` compute block and the same server decode closure. Recorder
sets/restores eval and copy callbacks ([WO1](~/predemo-spark/inputs/ab/runs-r2/wo1-C/candidate.diff:545));
predictor installs/restores eval callbacks to `cparams.cb_eval`
([WO4](~/predemo-spark/inputs/ab/runs-r2/wo4-C/candidate.diff:50)).
Cache and predictor insert into the same selected-expert-copy function; recorder
turns that function into a templated implementation. A merge that compiles can
still drop one observer, restore the wrong callback, omit cache-hit byte
accounting, or retire a lease before its last asynchronous reader. CMake/header
conflicts are mechanical; callback composition and lifetime semantics need
explicit review through the capsule methods.

Before D acceptance, answer: which callback owns each ask/read/stop return;
which observer sees original IDs before any remap; how recorder bytes account
for custom-cache hit/fill versus host upload; where cache leases end; and how
all gates unset preserve stock behavior. Require per-component activation,
gate-unset parity, coverage and counters in the same combined run. Native A+
will intentionally bypass the custom cache and predictor; default A will also
bypass mapper/predictor. A combined active profile must be reported separately.

No capsule semantic change was made or proposed as already approved. Supporting
multi-slot/checkpoint/native-cache coexistence or changing placement precedence
would require the orchestrator's semantic-review stop point. Fixing a candidate
that fails its existing requirements should follow the current capsule method,
with regenerated evidence and versioned methodology changes only if needed.

## Directive-2 checkpoint handoff

Read `OPS/DIRECTIVE-2.md` on 2026-11-20 UTC. Owner-provided Granite at
`~/models/campaign/gguf/granite-3.1-1b-a400m-instruct-Q8_0.gguf`, with expected
hash prefix `a52205df`, supersedes the independently downloaded `087517...`
artifact. The local owner-path file was still 397 MiB when inspected; this is
not a completed-copy or digest-verification claim. Do not run it until the copy
completes and the full authoritative digest is verified.

Existing adapter/code/provenance/tests are preserved. On resume, review the
current adapter against the new **path-mapping-only** authorization: its pinned
`087517...` fixture identity and published-size check must not be used as the
owner's fixture, and its prior receipt/toolchain metadata substitutions require
reconciliation with the narrower directive before execution. Preserve the failed
frozen-CLI proof; write no further outputs into frozen inputs. Current prepared
adapter metadata is preparation evidence, not an approved fixture/reference or
an adapted scorer-runtime pass.

Parent is preparing CHECKPOINT-1 and a model-switch pause. No further code,
model, build, test or infrastructure work was performed after this handoff.
