# Native CC workflow integration

Updated 2026-11-16. Source implementation is committed and pushed to
[Stellven/jiuwenswarm integration/native-cc-workflows](https://github.com/Stellven/jiuwenswarm/tree/integration/native-cc-workflows),
implementation commit `abcc4af85` and live campaign record `fb57d6592`.

The merge incorporates Spark source through `eea97929c` and the incoming
`dynamical-workflow` branch through `73da54106`. Read the maintained
[native workflow guide](https://github.com/Stellven/jiuwenswarm/blob/integration/native-cc-workflows/docs/architecture/factory/NATIVE-WORKFLOWS.md)
and [validation record](https://github.com/Stellven/jiuwenswarm/blob/integration/native-cc-workflows/docs/architecture/factory/WORKFLOW-INTEGRATION-VALIDATION.md).

The workflow team owns multiworkflow composition, adaptive graph orchestration
and replay presentation. Our side owns CC v2 semantics, Lab Manager admission,
budgets, resource lifecycle and independent evidence. The application remains
an iterative inference-engine factory on DGX Spark with STRATA as its baseline.
Ascend is an incoming example, not our acceptance target.

Implemented: native sealed-CC leaves, reusable recursive subworkflows, durable
graph revisions and invocation intents, recovery without duplicate calls,
task/attempt identity checks, scoped lab status/result/cancellation, standard
benchmark cancellation, graph/evidence UI and read-only replay. Existing CC
packages remain authoritative; there is no permanent Stage-to-CC executable adapter.
Old scheduler operations cannot silently become unsupervised workflow leaves.

Validation: 1572 broad Linux tests passed (13 skipped, one unrelated Docker demo
excluded); 105 targeted follow-up tests passed; frontend build and 18 runtime unit
tests passed. Real CC/browser and source-write/local-commit workflows were exercised.
Fault-injected transport tests are labeled separately. These checks do not establish
a new GPU speedup, full-model qualification or live CUDA vector capture.

Spark integration checkout:
`/home/user2/software-factory-spark-20261113/sources/native-workflow-integration-20261116`.
The existing `sources/cc-dgx-spark` checkout and live stores have not been migrated.
Use a fresh admitted task and bounded campaign for hardware qualification; do not
revive expired campaign authority or bypass independent source/build lineage checks.

Update, 2026-11-16: native GPU execution qualification passed and the factory
console is now active on Spark loopback port 5175 as `native-cc-factory.service`.
A fresh ARM64/CUDA build ran the real full six-expert DeepSeek model. The frozen
1471-token prompt and 16-token continuation matched exactly across four requests
in two fresh GPU processes. Wrong-image rejection, running-GPU cancellation,
container cleanup, service restart and read-only browser replay passed. The GPU
check exposed and fixed terminal cleanup reconciliation for Strata and native
build containers. An additional 55 focused checks and the service access/restart
check passed.

See the [service runbook](https://github.com/Stellven/jiuwenswarm/blob/integration/native-cc-workflows/docs/architecture/factory/SPARK-NATIVE-SERVICE.md)
and [small qualification record](https://github.com/Stellven/jiuwenswarm/blob/integration/native-cc-workflows/docs/architecture/factory/qualifications/20261116-spark-native.json).
The initial console task used `spark-native-e2e`. The old `ai4r-spark-ai4r-1` container and
its volumes are retained for rollback. That qualification task was bounded to three
build/four lab attempts and a four-hour workflow deadline; future campaigns need
fresh task authority. No model accuracy, long-context validation, live numerical
oracle qualification or speedup is claimed. Independent baseline/candidate
optimization campaigns remain separate scientific acceptance work.

Subsequent live agent campaign, 2026-11-16: the real JiuwenSwarm/Codex controller
accepted a request for at least 10% higher decode tokens/s on our fixed-placement
STRATA modification. It searched historical evidence, planned native workflow
`throughput-goal`, revised it to revision 18, tested three candidates and authored
and built a real ARM64 source change. Prefetch regressed 7.09%; six CPU workers
measured -0.37%; reducing ARM64 idle spin from 20ms to 200us measured 15.3268 versus
13.9698 tokens/s (+9.71%). Exact tokens, finish reasons and placement passed.
The 10% gate was missed; no ABBA confirmation or candidate promotion occurred.
The result is exploratory, not an accepted speedup. All eight GPU processes and
the native build completed; cleanup and independent raw-evidence rechecks passed.

The persistent experiment library holds 578 snapshots from 15 admitted stores,
including failures and current measurements. Search refreshes it, preserves
changed snapshots and returns source/task/record/hash provenance. The live console
now loads `throughput-goal`, task `native-throughput-goal-001`, from
`native-throughput-goal-20261116`. Its graph is explicitly agent-stopped
(`cancelled`), with all 18 nodes completed and no cleanup pending. Read-only browser
replay passed. A future campaign needs a fresh budget; its first steps should
measure CPU scheduling/quota behavior, then qualify a candidate without relaxing
the target. The existing engine baseline remains active.

See the [agent campaign guide and results](https://github.com/Stellven/jiuwenswarm/blob/integration/native-cc-workflows/docs/architecture/factory/NATIVE-THROUGHPUT-AGENT.md)
and [actual agent report](https://github.com/Stellven/jiuwenswarm/blob/integration/native-cc-workflows/docs/architecture/factory/qualifications/20261116-throughput-agent-report.md).
The guide links the small provenance record and unpromoted source patch. Runtime
integration and history/throughput admission checks passed 57 distinct focused
Python cases; this count is separate from the earlier integration validation.

Keep models, transfer ZIPs, mutable databases and large run artifacts outside Git.
