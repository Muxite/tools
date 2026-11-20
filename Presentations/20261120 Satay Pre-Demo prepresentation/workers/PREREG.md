# Satay A/B scorer pre-registration

Both arms use these checks against llama.cpp commit `9048bad8d6e3a0f9f1726e238e451181c7e02613`. The scorer takes a work order number and a diff. Arm labels, capsule files, and capsule verifiers are outside its inputs. Freeze the scorer before scoring either arm and verify the SHA-256 manifest below before each scoring batch. If a bug requires a change, preserve the original results, document the new version, and rerun both arms under that version. Do not change thresholds after seeing candidate results.

The original scorer (version 1) manifest was recorded on 2026-11-19 at 23:40:29 UTC. Filesystem creation times show that the existing WO5 C and N diffs were created at 23:30:53 and 23:31:53 UTC, respectively. Only file metadata was inspected. The strict pre-candidate freeze condition requires newly generated candidates for that pair.

Scorer version 2 is the amended version recorded on 2026-11-20 at 00:49:15 UTC. Apply this version uniformly to all past and future candidates. Preserve the original outputs when rescoring. See [AMENDMENTS.md](AMENDMENTS.md) for the evidence and the original scorer hashes.

## Run order

`./score.sh <wo-number> <candidate.diff> <outdir>` writes `score.json` and `score.log` under the specified output directory inside `ab`. A completed verdict exits 0 even when checks fail. `score.json` records `scorer_version`. Each stage has a status, one-line reason, and wall seconds or null when unattempted. `total_passed` counts all passing stages. `done_claimable` requires S1 through S5 to pass. The separately reported `active_reached` is true if either S5 config logged an active line. Its value is null until S5 is evaluated.

S1 failure skips dependent checks. S2 failure still permits S3 and any possible runtime checks. S3 failure skips runtime. S4 or S5 failure still permits subsequent independent checks. WO1 replay needs at least one clean gate-on run to attempt and both clean runs to pass. S6 and S7 are skipped for work orders to which they do not apply. Missing GPU access, loopback bind access, or a valid stock reference leaves applicable runtime stages `pending-run`. The score log prints the exact resume command. Each score invocation creates a fresh source and build directory. Runtime retries retain the prior artifacts and use fresh recorder paths.

On the real shell, run the following once to create `reference.json` from the pinned stock CUDA build. The script also saves the requests' raw responses, server logs, and invocation metadata.

```bash
cd ~/predemo/ab
./make_reference.sh
```

Score each diff with the default arguments. If the score was prepared in the sandbox, resume it from the real shell with the exact `run_checks.sh` command in its score log.

## Checks

| Stage | Pass condition |
| --- | --- |
| S1 Apply | Fresh `cp -a` copy with reflinks when available. Verify the pin and a clean tree including ignored files, refresh the copied index, run `git apply --check --index`, then `git apply --index`. The default Git empty-input rejection applies. |
| S2 Scope | All touched paths satisfy the table below. Use the staged name/status with rename detection disabled and supplement it with patch numstat paths. A rename checks the removal and addition. |
| S3 Build | Configure from the pinned stock receipt and build target `llama-server` using Ninja, Release, CUDA 12.6, architecture 87, `GGML_NATIVE=ON`, `GGML_CUDA_FA_ALL_QUANTS=OFF`, and the compiler/launcher paths in the receipt. Use at most three jobs. Substitute source and build paths and set `LLAMA_USE_PREBUILT_UI=OFF` to suppress optional fetching. The stock receipt's build log shows zero embedded UI assets. Configure and build share 90 minutes of execution time, with up to 30 seconds of termination grace. A shared build lock serializes scorers. Stage wall time includes any lock wait. Count build log lines containing compiler-style warning diagnostics without failing on them. The hit-rate denominator is direct hits + preprocessed hits + misses, using the private build's ccache stats log. The rate is null when there are no such events. |
| S4 Default-off | In both C1 and C2, complete a clean server lifecycle with the gate unset and require the config's stock token hash and zero occurrences of the work order's marker prefix at the start of a log message. |
| S5 Gate-on | In both C1 and C2, complete a clean server lifecycle with the gate set and require the config's stock token hash. Each log must have exactly one status line, either `<name>: active …` or `<name>: inactive (reason)`, and at least one `<name>: stats …` line with the required decimal counters after the pre-shutdown log checkpoint. Strip standard time, level and ANSI color decoration. Require the specified active fields or effective settings and use the last qualifying shutdown stats line for the counters. Allow other prefixed lines and record their count and first five in `extra_marker_lines`. Report activity per config and in the summary. |
| S6 WO1 replay | For each clean gate-on config, ignore blank JSONL lines and accept a single optional object of type `summary` or `stats`. Every other line must be an event object with phase `prefill` or `decode`, with type `event` or the type field omitted. With a summary, require the event count to equal `expected - lost` from that summary. Without a summary, warn and require zero loss in the stats log and an event count of `24 × total microbatches`. For this single, uncached request, derive prefill microbatches as ceil(`timings.prompt_n / n_ubatch`) and decode microbatches as `timings.predicted_n - 1` because the first token is sampled from prefill logits. Report total and per-phase event counts, distinct layers and phase-scoped microbatches seen when IDs are available, lost, incomplete, overflow, and summary presence. |
| S6 WO3 placement | Use `-ngl 99 -lm mmap` with the same request and shared flags and omit `-cmoe` for this extra comparison. Write a version-1 plan with a single CPU override for `^blk\.[0-9]+\.ffn_down_exps\.weight$`. Compare the candidate using `--placement-plan` with the stock run using `-ot` for that regex. Require an exact token hash, active and shutdown stats showing 24 assigned tensors, and identical logged model buffer names and sizes. The reference generator also runs stock without the override and requires increased CPU-side model buffer allocation with stock `-ot`. |
| S7 WO5 mapper | In both configs, compare fresh gate-off and gate-on sessions at 1, 31, 32, 33, 127, 128, 129, 511, 512, 513, and 1023 input tokens. Use raw IDs from repeating the one stock Granite token for ` the`, without adding special tokens. Validate exact evaluated prompt length and zero cache reuse. Generate up to 8 greedy tokens per case. If the stock C1 pilot demonstrates positive cache reuse, repeat 33, 129, and 513 tokens in separate cache-enabled sessions. Prime the first length minus 16 tokens with one generated token and require positive cache reuse of at least the primed length and less than the full prompt. For each length within each mode, require gate-off/on token hash equality and equal `cache_n`. Require clean shutdown for each session. Record `cached_vs_cold_differs` on each cached result for the same gate and length for information only. Record cached cases as skipped when the stock pilot reports no reuse. |

## Gates and allowed paths

| WO | Gate when enabled | Marker | Allowed paths besides the CMake list below |
| --- | --- | --- | --- |
| 1 | `LLAMA_EVENT_REC=<absolute path to fresh JSONL file>` | `runtime_event_recorder` | `src/**`, `tools/server/server-context.cpp`, `tools/server/server-context.h` |
| 2 | `LLAMA_EXPERT_CACHE=1` | `expert_weight_cache` | `src/**`, `ggml/src/ggml-backend.cpp`, `ggml/include/ggml-backend.h` |
| 3 | `LLAMA_PLACEMENT_PLAN=1` | `weight_placement_planner` | `src/**`, `common/arg.cpp`, `common/common.h`, `common/common.cpp` |
| 4 | `LLAMA_EXPERT_PREDICT=1` | `expert_demand_predictor` | `src/**`, `tools/server/server-context.cpp` |
| 5 | `LLAMA_BATCH_LAYOUT=1` | `batch_layout_mapper` | Newly added `src/llama-batch-layout.h`, `tools/server/server-context.cpp` |

For every WO, reserve `src/llama-sampler*`, `src/llama-model*`, `src/models/**`, `src/llama-graph.*`, and `src/llama-arch.*` for stock sampling, model, graph/router and architecture code. None of the WOs names one of these files as an explicit exception. The allowed standalone CMake files are the root and `src/CMakeLists.txt` for all WOs, plus `tools/server/CMakeLists.txt` for WOs 1, 4 and 5, `ggml/src/CMakeLists.txt` for WO2, and `common/CMakeLists.txt` for WO3. Paths under a WO's broad `src/**` allowance follow the same source tree rule for new files. S2 enforces file boundaries. Whether a permitted CMake edit or the optional WO2 backend hook was necessary requires source review.

The two runtime configurations are C1 `-ngl 0 -lm mmap` and C2 `-ngl 99 -cmoe -lm mmap`. Shared flags are `-c 2048 -np 1 --temp 0 --seed 1 -lv 4`, a fixed localhost port, and `--no-cache-prompt` except for deliberate cached-prefix cases. Use `~/models/campaign/gguf/granite-3.1-1b-a400m-instruct-Q8_0.gguf`. S4, S5 and the WO3 comparisons use the one-shot prompt below at temperature 0, seed 1, `n_predict=48`, with `return_tokens=true`.

> Write a short note about mixture of experts models and why memory bandwidth matters. Then list three facts.

The token hash is the full SHA-256 of the compact JSON integer array followed by one LF, matching the input to `sha256sum` in `one_shot.sh`. Require a successful response and a nonempty token array. Compare each hash to the same-config stock hash. Record stock binary and model hashes and all gate definitions in `reference.json`. The WO1 gate value in that file is a path template resolved to an unused absolute file path per scored run. Reference generation refuses to replace an existing file. Candidate runs verify the recipe and the model digest against that file.

## Threats to validity

- **Marker spelling and timing.** Match the written WO names without aliases and check message counts, fields, and shutdown timing. For WO4, an active line followed by an inactive line fails S5 under the specified one-status-line rule.
- **Activation.** Inactive is a valid S5 outcome in either config. WO3 S5 sets the gate with no plan, and its S6 exercises an actual override. WO1 needs records to pass S6. A candidate can pass S1–S5 with a marker-only change. Interpret `done_claimable` alongside activity, extra stages and source review.
- **Coverage.** Exact token equality for these requests samples public behavior. It cannot establish all router IDs, mixture weights, memory caps, scheduling invariants, thread safety, or performance. The WO3 readback compares assigned counts and aggregate buffers, which can miss per-tensor differences. WO5 uses one slot, one token pattern, the stock batch limits, and three verified prefix cases.
- **Build or cache effects.** Both arms use the same receipt and a shared local ccache directory. `CCACHE_BASEDIR` is each candidate's source/build parent, `CCACHE_NOHASHDIR=1`, and `CCACHE_TEMPDIR` is under the candidate directory. Timing and hit rate can vary with run order, cache warmth and concurrent load. They are descriptive, apart from the shared build time limit. Warn-only diagnostics and omitted optional UI assets do not change the completion checks.
- **Runtime and state leakage.** Remove inherited `LLAMA_*` and `GGML_*` options and CUDA device-selection overrides, and set the binary library path explicitly. Use distinct C1/C2 ports derived from the candidate diff hash and reuse them sequentially. Reference ports are 20990 and 20991. Serialize scorer-owned runtime sessions. Check loopback bind availability, wait up to 120 seconds for health and allow 300 seconds of HTTP socket timeout. Terminate only the spawned server PID, wait 30 seconds for a normal exit, then force-stop that PID if needed. Use `pgrep -x llama-server` for port conflict diagnostics. Candidate code runs as the operator, so use trusted local diffs. The runtime runner is not a sandbox.
- **Reference drift.** Record the stock baseline on Satay once and use that same reference file for both arms. The scorer pins the stock receipt SHA-256 and reference generation validates the stock executable against it. It checks the model digest before runtime scoring and records the reference file digest in each run. Run the arms on the same host and compare the recorded reference digests.

## Amended SHA-256 manifest (scorer version 2)

Run `sha256sum -c` against the manifest lines in this block from `~/predemo/ab`.

```text
018f87b7009cafb789e13d9aa113eeb29093ce027e9c7caa01e1eee5552f4992  score.sh
670add07f7d997a4264fd2504d14df3999103309c762f44e772ed3b2b50d38bf  run_checks.sh
d1d49fd48bcc191382dc82fd8669fc4187104deceaad74218da76215fc8822d1  make_reference.sh
c3550c744395c8dd4fe86b4d32f692685940d3d674f54363cd60485df5506891  scorer.py
559fa1943d87f29bd565b134c368549438416f71f8588f4640feb2ce45098160  scorer_runtime.py
9de48e961435ff5f0c7c631067b2240557dcb565fd9c07fb6bdc5860110c80da  work-orders.md
1fa79f3c49e2a03dcabfc405d8e435c9d88c266ea311623c1312df73feb1b704  wo/WO1.md
9e7ec7fd06be3763c4d1d19a8af8c38d0655230c0c20c6ea508412d45aebf9ea  wo/WO2.md
bf1a21a51dc3a2c87c8306e3f90fc1992bdc1ae0558f38f3f27f090ad43c3543  wo/WO3.md
7946dccb3891584699cd609955357708e90d1c97984563b44b01d65adbbf2b81  wo/WO4.md
346fc41856f2fd680196f4b6ef2bb2c4cf45cdb83fe560e722d39b0c71ee649b  wo/WO5.md
```
