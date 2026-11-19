# Substituting real steps on the DGX Spark

Copy `demo/script.json` to a file under the cockpit directory and use `bin/cockpit up --script demo/spark.json` to select it. The commands below are integration examples. Match the argument names, receipt formats and paths to the deployed factory. Use a fresh run for each baseline contract. Place or copy every event reference under the cockpit directory before emitting it.

| Step | Command or action to substitute | Stage |
| --- | --- | --- |
| s01 Stock inputs | Collect the signed requirements contract, ontology, stock `git rev-parse HEAD` and prior receipts with the Requirements and Evidence Capsule entry points. Emit `plan ok` with the contract reference. | native CC execution |
| s02 Freeze comparison | Have the Requirements Capsule record the baseline definition and claim-to-receipt mapping in the contract. Emit `decision ok`. | native CC execution |
| s03 Cache hypothesis | Run the Task Planner against the contract, ontology, stock revision and prior receipts. Emit `plan ok` with a falsifiable `data.hypothesis`. | native CC execution |
| s04 Expert cache patch | Invoke the Expert Weight Cache’s native entry point against the stock worktree. Save `git diff --color=always` and `git diff --stat`. Emit `cc_apply ok --cc expert_weight_cache` with the diff reference and `data.diff_stat`. | native CC execution |
| s05 Source verification | Run `git diff --check` and the capsule’s source verifier. Emit `verify ok\|fail --cc expert_weight_cache` with the verifier receipt. | native CC execution |
| s06 Inspect patch | Keep the `show` action and select the owning capsule. | native CC execution |
| s07 Image receipt | Run `factory.builder submit` for the pinned source and `factory.builder status` until it seals an immutable image digest. Emit `build ok` with the image receipt when compilation succeeds. | compile |
| s08 Activation marker | Start the sealed image’s `llama-server` against the pinned model. Check readiness, output sanity and the capsule’s marker. Emit `activate ok` with a runtime acceptance receipt and `data.marker`. | runtime acceptance |
| s09 Acceptance gate | Keep the `wait` action for s08’s `activate ok` event. | runtime acceptance |
| s10 Paired ABBA | Use a `quiet_run` action for `factory.lab_client ABBA` with stock and candidate image digests, fixed run parameters and a paired receipt path. The director emits the paired result once quiet ends. | hardware measurement |
| s11 Arm receipts | Have the Evidence Collector materialize the paired result’s arm receipts and emit `result ok` with `data.arm` set to `A` or `B`. | hardware measurement |
| s12 Compare arms | Keep the results view. Use the actual receipt values for narration and update the fixture caption. | hardware measurement |
| s13 Analysis wording | Run the Methodology Capsule against the immutable ABBA and arm receipts. Record the verdict and the reason for a revision. | native CC execution |
| s14 Report and next run | Have the Task Planner emit a decision with the report and reason for the proposed next test. | native CC execution |

Use the stage enum `native`, `compile`, `runtime` or `hardware` in the script and events. For an arm table, each receipt should expose `ttft_ms`, `native_prefill_ms`, `decode_tps`, `memory_mib`, `output_check` and `verdict`. Use `{run}` and `{job}` in the `quiet_run` receipt path for unique, immutable receipts. The shell receives `COCKPIT_RUN`, `COCKPIT_STEP`, `COCKPIT_STAGE` and `COCKPIT_JOB`. Write experiment stdout and stderr normally. Cockpit captures both to disk and displays them after quiet mode.

For a timed demo, spend roughly one minute on stock inputs, three minutes on the capsule and its build, three minutes on output and the paired comparison, and the remaining time on scope and the next decision.
