Status: current
Last reviewed: 2026-11-20
Supersedes/related: earlier draft of this brief (now Part B), Satay Pre-Demo Plan, Star CC Authoring Brief

# Spark overnight brief for Codex (lead engineer on <spark-host>)

Read all of it. **Part A is the approved plan and wins any conflict with Part B.** Part B keeps the earlier rules: safety, do-not-build, inputs and evidence. Specifically:
- Part A's factory-native bundles replace rb/1.
- Part A's arm A definition replaces Part B's.
- The orchestrator is a Claude session outside this box. "Stop and report" means: write the stop to `~/predemo-spark/OPS/STATUS.md` and `OPS/BLOCKERS.md`, then wait for a message in this terminal.

Owner priorities, in their own words, summarized:
- **Value first.** Get maximum value overnight, about 8 h continuous, and produce whatever you can.
- **The 5 starred builder CCs and the UI are the core.** The UI lives inside the JiuwenSwarm web app, with replay, live view and launch.
- **Strata is the yardstick.** CCs are component builders whose methodologies are reverse-engineered from Strata. The different code, and so the different results, come from the CCs and the system-ontology differences. We measure the gap and close as much as we can.
- **Revise or add CCs if needed.** If the 5 aren't great, improve them or find other CCs.
- **Have something to show when asked.** Questions like "what's the task contract?" and "what's the system ontology?" need an answer. Don't use the original M1 machinery or methodology.
- **Use subagents.** Hand bounded work to your own subagents. Keep the main thread for decisions.

# Part A: approved plan
## Plan (8 h): 5 builder CCs, Strata gap, JiuwenSwarm UI

## Context
**Friday demo.** We show that builder Capability Capsules (CCs), whose methodologies were reverse-engineered from Strata, let JiuwenSwarm improve stock llama.cpp on DeepSeek V4.1 Flash on the DGX Spark.
- **The yardstick is Strata running the same weights on the same box.** The headline is "gap to Strata closed by CCs", plus inverse TTFT vs stock. Both are targets, not promises.
- **The JiuwenSwarm web UI shows everything, live and as replay.** That covers task contract, system ontology, task graph, CCs, artifacts, diffs, tests, measurements and the report.
- **The demo is served from the Spark over tailscale.** No pixel video.
- **No M1 machinery.** We only need a task contract and a system ontology to show when asked.

Codex (gpt-6.1-sol, `--yolo`) on the Spark is the lead engineer and uses its own subagents. I am the orchestrator: I steer, review, keep the work aligned with the demo, and move commits off the box and push them.

## Facts established (read-only exploration)
**Same weights.** The llama.cpp 6-shard pack (`~/software-factory-spark-20261113/deepseek-v41-upstream-20261119/converted/…-00001-of-00006.gguf`) is a byte-exact conversion of the Strata 4-shard pack, so a fair comparison is possible.

**Strata fair profile** (`direct-engine-comparison-v1/contract.json`):
- `strata-dsv41 --serve --pack ~/strata-baseline/Strata-data/packs/deepseek-v4.1-flash-ist-das-2.00bpw --experts 6 --dspark none --cpu-threads 8 --mmap-experts on --vram-experts 1.0 --reserve-mib 16384 --prefill-chunk 256 --no-expert-cache …`
- Served through `serve/server.py` as an OpenAI API on :8081.
- Client: `tools/dgx_bench.py`.
- Earlier numbers: 79.5 prompt tok/s and 14.4 decode tok/s (fair profile); TTFT 4.6 s at 512 tokens and 17 s at 4096 (default profile).

**llama.cpp.**
- Stock defaults (`-fit`) OOM the box.
- The only run that worked: `--load-mode mmap --lazy-mode on -ngl 99 -ot 'blk\.[0-9]+\.ffn_(gate|up|down)_exps\.weight=CPU' -t 8 -b 512 -ub 512`, under a 96 GiB / 8 CPU cap.
- It gave 11.48 tok/s warm decode, but only on a ~20-token prompt.
- `--moe-cache-mib` has never been run.

**Strata mechanism → stock gap → star CC:**

| Strata mechanism | Stock llama.cpp | Star CC |
|---|---|---|
| Profile-driven hot-expert residency (`expert-profile.bin`) | Only a dynamic MoE cache and per-tensor placement | placement planner, expert weight cache |
| Expert lookahead | Absent | demand predictor |
| Work-split prefill chunking | Partial | batch layout mapper |
| — | — | event recorder (observability) |

Further gaps that could become additional CCs if time allows:
- Engram row cache and threads (absent in stock)
- DSpark drafter (absent)
- Worker spin (partial)

**App.** The factory branch `demo/friday-deepseek-20261120` is the owner's lineage and the Friday-demo prep. Problems found:
- The gateway imports the deleted `research_http.py` (`gateway/channel_manager/web/web_channel_app.py:128`), so it crashes until fixed.
- No venv. `factory-env` has openjiuwen at the same pin, and `uv` is at `~/rsi-expert-streaming-001/factory-env/bin/uv`.
- No node. Node 24 is at `~/rsi-native-20261117-setup01/runtime/node-v24.22.3-linux-arm64/bin`.
- No frontend build, and Vite dev mode blocks remote hosts. Serve the built `dist` with `app_web` and `FRONTEND_HOST=<tailnet-ip>`.
- Frontend: React and zustand, no router (`App.tsx` `activeNav`). The template is `features/rsi`. HTTP routes follow `trajectory_http.py`.

**Factory.**
- `jiuwenswarm-factory ask|init|run|story|plan|export`, with one controller per `FACTORY_HOME`.
- Evidence lives in `factory.sqlite` plus `sessions/*.jsonl` and `telemetry/events.jsonl`.
- `export` writes a hashed bundle (`MANIFEST.json`, `records/`, `artifacts/`, `session.jsonl`). The read-only helpers already exist: `story.load_source`, `story.build_events`, `taskgraph.from_records`, `telemetry.read_events`, `monitor.*`, `redact.sanitize`.
- The agent is Codex through `openai-codex-cli-bin` 0.163.0, with its own `CODEX_HOME` per home, which needs a login.
- The bundled tasks and contracts are Jetson-only.

## Key decisions
1. **Bundle format:** use the factory's native `export` bundle and live homes, not my rb/1. That removes a translation layer and a point of failure. Benchmark runs attach their results, logs and command lines as artifacts and records in the same store. The rb/1 viewer code serves only as UI reference.
2. **Arms:** all on the same prompts, under the same cap (100 GiB, 8 CPUs).
   - **S** = Strata fair profile.
   - **A** = stock as documented for oversized MoE: `-lm mmap --cpu-moe`, everything else default. The deviations from pure defaults are recorded.
   - **A+** = A plus `--moe-cache-mib`, chosen with `scripts/moe-cache-tune.py`.
   - **C1–C5** = each star CC's product change.
   - **D** = all five combined.
3. **Metrics:**
   - Primary: client TTFT at 512 and 2048 prompt tokens, `-n 32`, temperature 0, warm, 5 repeats, ABBA order.
   - Gap closed = (TTFT_A − TTFT_X) / (TTFT_A − TTFT_S).
   - Also reported: inverse-TTFT ratio vs A and vs A+, decode tok/s, peak memory, load time.
4. **Who applies the CCs:** JiuwenSwarm runs each star CC as a factory session, in its own `FACTORY_HOME`, starting from the Satay round-1/2 candidates. Bring-up of the Spark factory path (task, contract, auth, build) is time-boxed to 90 minutes. If it misses the box, the lead Codex applies the CCs directly, still following each capsule's method, and imports the result into a factory store so the UI shows it the same way. The fallback is labelled honestly.
5. **Contract and ontology to show:**
   - Contract: `star-deepseek-v1.json`, retargeted from the Satay `star-prefill-v0.json`, plus a one-page readable version.
   - Ontology: the owner's Downloads files, pinned in `inputs/ontology/SHA256SUMS`, plus each capsule's `ONTOLOGY.yaml` slice.
   - Nothing from M1.
6. **Operations source of truth:**
   - On the Spark, `~/predemo-spark/OPS/` holds `STATUS.md` (append-only, UTC), `LEDGER.jsonl` (every run: arm, command, binary sha, result path), `DECISIONS.md` and `BLOCKERS.md`.
   - I mirror a sanitized copy (no IPs, users or paths) to Muxite/tools branch `spark-overnight-20261120`, roughly hourly.
   - Code goes to the jiuwenswarm branch `demo/cc-star-ui-20261120` (worktree `~/predemo-spark/jiuwenswarm`). I pull it with `git bundle` and push from `~/huawei/jiuwenswarm`.

## Phases (start about 01:30 local, continuous about 8 h)
**P0 Safety and setup (0:00–0:45, no model loads)**
- `bin/capped`:
  - `systemd-run --user --scope -p MemoryMax=100G -p MemorySwapMax=0`, with CPUs limited to 8 via `AllowedCPUs`
  - a pre-check that refuses to start under 110 GiB MemAvailable
  - a watchdog that kills under 8 GiB
  - `flock gpu.lock`, and a peak-memory log
- An enforcement test: an allocation that must be killed.
- `bin/quiet`.
- The OPS folder, and the git worktree and branch.
- **Stop point:** I review `bin/capped` before the first DeepSeek load.

**P1 Reference arms (0:45–2:30, GPU lane)**
- Run S, A and A+ on fixed prompts. The prompt files and token counts are recorded, and the same chat template is checked.
- The first load of each engine is supervised. The first request is discarded and the cold load is recorded.
- Output: a baseline table with the gap.

**P2 App and UI (0:30–5:00, CPU lane, a Codex subagent, in parallel)**
- Get the app running:
  - Fix the `research_http` import.
  - Create a venv with `uv venv` plus `uv sync`, or `pip install -e`.
  - Build with npm using the box's node.
  - Write `bin/demo-up` and `bin/demo-down`.
- Serve at `http://<tailnet-ip>:5173`. Bind to the tailscale IP only. Gateway and agentserver stay on localhost.
- Add a **Factory runs** feature (`src/features/factoryRuns/`, a new nav key) with backend `gateway/channel_manager/web/factory_http.py`, which reuses the story, taskgraph, telemetry, monitor and redact helpers, confines paths to an allowed root, and copies SQLite before reading.
  - **Views:** list (bundles and live homes), replay (scrubber over story events), live (poll `story?since=`), launch (POST that starts a detached `jiuwenswarm-factory run` subprocess in a new home).
  - **Panels:** contract (readable plus raw), ontology (slice plus links to the owner's files), task graph, CCs (`cc.yaml`, verifier result, pinned digests, artifacts), diffs with scorer stage chips, tests and scores, measurement table (arms, gap chart), terminal/session log, report. Each file gets a digest badge.
- Test with a factory export bundle that already exists, for example `~/software-factory-spark-20261113/exports/factory-loop-v1/*`.

**P3 Apply the 5 CCs (1:00–5:00)**
- Spark task template and contract (`target: spark-gb10`, DeepSeek paths, a native build for sm_121 instead of the Jetson docker image).
- Apply `inputs/factory-satay/factory-{slice-loader,component-spec}.diff`.
- Copy Codex auth from `~/.codex` into each home's codex-home. If that fails, ask the owner for a single `jiuwenswarm-factory login`.
- Per CC: run the factory session, then capsule `verify`, scorer S1–S5 plus S5L on the small fixture, then DeepSeek gate-unset parity and gate-set activation under `bin/capped`.
- Order: recorder → placement → cache → predictor → mapper. Builds run in parallel on the CPU; GPU checks run one at a time.
- If a candidate fails, Codex revises the capsule (versioned 1.1.2…), never the diff by hand.
- Then build D, the combined change.

**P4 Profile (4:00–7:00, GPU lane, quiet machine)**
- Run A, A+, C1–C5, D and S, ABBA ordered.
- Every run writes a ledger row and an artifact.
- Per-CC attribution from the recorder's activation counters.

**P5 Improve (whenever results arrive, in parallel)**
- If a CC shows no gain, look at the Strata mechanism behind it. The likeliest win is profile-driven per-expert hot residency (Strata's `expert-profile.bin`), applied through the placement planner and cache CCs.
- Optional extra builder CCs, only if the five are done:
  - Engram row cache
  - work-split prefill chunking
- **No-gain CCs:** if a CC gives no gain, report it honestly. Its value can still be correctness or observability.

**P6 Report and demo readiness (7:00–8:00)**
- `report.md` plus the final factory export bundle, shown in the UI.
- A rehearsal pass: open the UI over tailscale, replay a run, start a short live session.
- Final commit; I push both branches.

## How I supervise
- I launch tmux `muk` window `codex` with `codex --yolo` and an opening prompt to read `BRIEF.md` (updated with this plan) and start P0.
- A background poller wakes me when `OPS/STATUS.md` changes, plus a fallback check about every 20 minutes. At each wake I review:
  - commits and diffs, against the "do not build" list
  - memory events
  - the arm results
- I send corrections with `tmux send-keys`.
- About hourly I mirror OPS and code off the box and push.
- Hard stops are memory events and anything that needs sudo or deleting other people's files. The RSI owner's material may be cleared if disk or processes get in the way, but it isn't needed: 1.7 TB is free.

## Files I'll prepare before launch
- `~/predemo-spark/BRIEF.md`, rewritten to this plan, adding the Strata arm, gap metric, factory-native bundles, app recipe and fallback rule.
- `~/predemo-spark/OPS/` skeleton.
- The prompt files: 512 and 2048 tokens of fixed text.
- The tmux window `muk:codex` and the launch.

## Verification
- **P0:** the cap test kills at the limit, and `bin/capped` logs peak memory.
- **P1:** S, A and A+ each give 5 warm repeats with TTFT; outputs at temperature 0 are recorded and matched across repeats.
- **P2:** from my machine, the URL over tailscale loads. Factory runs lists a real export bundle, replay scrubs, live view follows a running session, launch starts a session, and digest badges are verified.
- **P3:**
  - Each CC: capsule verify passes, scorer passes, gate-unset output hash matches stock, and the activation line appears when the gate is set.
  - D builds and passes parity.
- **P4:** a ledger row for every number, and an attribution table with confidence intervals.
- **Overall:** the final report states verified vs inferred and what was not measured.

# Part B: earlier brief (rules and inputs)
# Spark overnight brief for Codex (lead agent on <spark-host>)

You are the lead engineer on the DGX Spark tonight. An orchestrator (Claude) steers from outside and reviews your output. Use your own subagents for bounded pieces; keep the main thread for decisions. Work in `~/predemo-spark`. Commit often on the branch below. Write a short status line to `~/predemo-spark/STATUS.md` after every milestone (UTC time, what finished, what is next, blockers).

## 1. What the demo must show (the only goal)

Five **builder Capability Capsules (CCs)** are applied by JiuwenSwarm to stock llama.cpp. Each produces a reviewed diff that builds, passes its capsule verifier and the independent scorer, and is profiled on the Spark running DeepSeek V4.1 Flash (232 GB) in 128 GB. The JiuwenSwarm UI shows the whole thing, live and as replay, so nobody records a pixel video. It shows the contract, task graph, each CC, its artifacts, diffs, test results, measurements and the final report.

- A CC is a builder. It ships methodology, samples, helpers, tests, acceptance criteria and a verifier with pinned hashes. It never ships the finished diff. The diff is produced during the task.
- We compare **code with vs without each CC's product change**. We do not compare agents with vs without a capsule.
- Speed targets are targets, not promises. 1.30x inverse TTFT is the goal and 1.50x is the stretch. A modest, attributed improvement with every CC working is a successful demo.

The five starred builder CCs (capsule 1.1.1, in `inputs/ccs/`):
1. `observability_event_recorder`: runtime event recorder (JSONL)
2. `expert_weight_cache`: GPU cache for host-resident expert weights
3. `weight_placement_planner`: per-tensor placement plan (buffer overrides)
4. `expert_demand_predictor`: router-driven next-layer expert prefetch hints
5. `batch_layout_mapper`: batch/microbatch layout for MoE prefill

## 2. Do not build (out of scope tonight)

- No new tuning CCs and no hand-tuning beyond the arms below.
- No Strata work, and nothing for the RSI loop. Don't recover or extend other people's experiments.
- No ontology or contract redesign. Use what exists.
- No new scorer stages. Use the frozen scorer plus its amendment log. Add an amendment only for a defect proven by logs, apply it to all candidates, and record it.
- No pixel recording, tmux choreography or replay "director".
- No polish beyond what the UI needs to show the items in section 1 clearly.

## 3. Safety rules (hard; an earlier load OOM-hung this box)

- Never load DeepSeek outside the wrapper `bin/capped` (you write it first). It must:
  - use `systemd-run --user --scope -p MemoryMax=100G -p MemorySwapMax=0`
  - check `MemAvailable` before start, and refuse if it is under 110 GiB
  - run a watchdog that kills the job if `MemAvailable` drops under 8 GiB
  - take a single GPU job lock (`flock ~/predemo-spark/gpu.lock`)
  - log the start, stop and peak RSS to the run bundle
- Verify the cap really enforces before the first DeepSeek load. Run a small allocation test that must be killed at the limit.
- Always use `-lm mmap` for DeepSeek (load_mode auto resolves to `none` and pins host RAM).
- Only one model process at a time. Timed runs only on a quiet machine: load under 1.0 and no builds running.
- No sudo is available. Don't try.

## 4. Inputs (already on the box)

- **Stock:** `llama.cpp-stock` at pin `9048bad8d6e3a0f9f1726e238e451181c7e02613`, built in `build-stock-cuda121` (sm_121, clean tree). Receipt facts: `llama-server` sha256 `0340c6cc...8aa44`.
- **Model (llama.cpp format, six shards incl. Engram):** `~/software-factory-spark-20261113/deepseek-v41-upstream-20261119/converted/DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ2_XXS-00001-of-00006.gguf`. The Strata 4-shard pack under `strata-baseline` uses different GGUF keys and will not load. Don't use it.
- **CCs, work orders and scorer:** `inputs/` (copied from Satay)
  - capsules 1.1.1: `inputs/ccs/*`
  - work orders: `inputs/ab/wo/WO1-5.md`
  - scorer v4: `inputs/ab/scorer.py`, `scorer_runtime.py`, `PREREG.md`, `AMENDMENTS.md`, `selftest/`
  - Satay candidate diffs and scores: `inputs/ab/runs*`, `inputs/ab/out*`
  - On Satay, round-1 candidates for 4 of 5 work orders passed every scorer stage. The mapper failed the gate-unset silence rule, which capsule 1.1.1 addresses.
- **Run bundle format and viewer:** `inputs/run-viewer/` (SPEC.md rb/1, adapters, validator, prototype `viewer.html`).
- **Factory:** the JiuwenSwarm branch `demo/friday-deepseek-20261120` in `~/software-factory-spark-20261113/sources/factory-friday-deepseek-20261120`. It descends from `ai4r_M1`, `ai4r_M1plus` and `ai4r/demo`. Create the work branch `demo/cc-star-ui-20261120` from its HEAD in a new worktree at `~/predemo-spark/jiuwenswarm`. The web UI is at `jiuwenswarm/channels/web/frontend` (React/Vite), and the factory code is at `jiuwenswarm/factory`.

- **System ontology (use as given, no redesign):** `inputs/ontology/`, pinned in `SHA256SUMS`:
  - `system-ontology-design.en.md` is the design: Given, Engine, Knowledge; engine regions.
  - `unified-dictionary.md` holds the terms.
  - `metadata-alignment.md` and `term-alignment-for-review.md` are the alignment notes.
  - `EXAMPLE.md` is a worked example.
  - `20261117 Unified overview prepresentation.mmd` is the overview diagram.

  Each capsule's `ONTOLOGY.yaml` is a small slice written against these. The ontology is part of the contract, and the UI's contract panel shows the task's slice with links to these files. If a slice uses a term that is missing from the dictionary, note it in the report. Don't edit the ontology files.

- **Contract, task graph and planner: use the factory as it is.**
  - **Code:** `jiuwenswarm/factory/contract.py`, `contracts/`, `taskgraph.py`, `controller.py`, `ontology.py`, plus the Codex decision agent.
  - **Star contract and tasks:** in `inputs/factory-satay/`. That folder holds `star-prefill-v0.json` with its NOTES, `tasks/star-*.json`, and two factory patches. `factory-slice-loader.diff` adds capsule ONTOLOGY.yaml slice loading. `factory-component-spec.diff` adds the `builder_spec` component kind, so builder CCs don't need a shipped patch.
  - **Retarget:** apply both patches, then retarget the star contract from Granite on Satay to DeepSeek on the Spark.
  - **Lineage:** the contract lineage is the M1 Research Brief, translated into the factory contract JSON. The M1 intent and IR design survives as documents in `docs/code/Missions/M0/source/Architecture_context/design-package/` (for example `Intent_IR.json` and `Intention_Node_Contract.json`). Show that lineage in the UI's contract panel by linking those documents.
  - **Don't re-implement the M1 intent compiler.**

## 4b. Branch, serving and push

- **Lineage:** `demo/friday-deepseek-20261120` is the project owner's own lineage, which is the Friday demo prep:
  - `ai4r/demo`
  - the owner's Jetson demo console and `ask` commits (11-13)
  - the Codex and Spark Factory Agent CC, lab and factory commits (11-15 to 11-19)
- **Reference only:** the Satay worktree at `fe88a206` is an ancestor.
- **Previous demo console:** `jiuwenswarm/factory/demo.html`, `monitor.html` and `views/` are the previous demo's console. Reuse its pieces, but the new UI lives inside the JiuwenSwarm web app, not as a separate page.
- **No GitHub auth here.** Commit locally only. Don't add remotes or credentials. The orchestrator pulls commits off the box with `git bundle` and pushes them.
- **Serving:** the demo is shown in a browser on another machine over tailscale. Run the JiuwenSwarm app (gateway and web frontend production build) on the Spark, bound to a port reachable on the tailscale interface. Write the start/stop commands to `bin/demo-up` and `bin/demo-down`, and the URL to STATUS.md. The app must survive the browser reloading. Live view must work while a factory session runs.

## 5. Work plan (in order; replan freely within the goal)

**M0 Safety (about 30 min).** `bin/capped`, a cap enforcement test, `bin/quiet` (load and process check), and the GPU lock.

**M1 Stock reference arms on DeepSeek (first capped load is supervised: stop and report after it).**
- **A (stock as documented):** defaults (`-fit on`, `-ngl auto`, `-b 2048` default) plus only `-lm mmap`, which is needed to load at all. Record that as a deviation.
- **A+:** A plus the documented native MoE cache, `--moe-cache-mib` chosen with `scripts/moe-cache-tune.py` as documented.
- **Workload:** fixed prompts at 512 and 2048 tokens, `-n 32`, temp 0, 5 repeats, server mode. The primary metric is client-observed TTFT. Also record prompt t/s, decode t/s, peak RSS and load time. Record cold vs warm separately.

**M2 Apply the five CCs to the pin.**
- Start from the Satay round-1/2 candidates. For each work order, rebase the best scoring candidate onto `llama.cpp-stock` in its own worktree and build for sm_121.
- Run that capsule's `verify`, then scorer stages S1–S5 and S5L on the small fixture model (`inputs/` notes say which), then a DeepSeek gate-unset parity and gate-set activation check under `bin/capped`.
- If a candidate fails, fix the capsule or verifier first (capsule edits are allowed and versioned, e.g. 1.1.2), then regenerate. Never hand-patch the product diff outside the capsule method.
- Produce a combined branch D with all five changes.

**M3 Profile.**
- **Arms:** A, A+, each CC alone (C1–C5, gate on) and D (all five).
- **Order and repeats:** ABBA-ordered, 5 repeats, same prompts and settings.
- **Report:** inverse TTFT ratio vs A and vs A+ with a 95% CI, per CC attribution, and activation counters from the recorder.
- **No-gain CCs:** If a CC gives no gain, say so. Its value can still be correctness or observability.

**M4 JiuwenSwarm run and UI (in parallel with M2/M3 via a subagent; no GPU needed).**
- **Bundles:** factory runs emit rb/1 run bundles (events.jsonl plus a hashed manifest and files). Add a recorder hook in the factory, reusing the adapters in `inputs/run-viewer/adapter`.
- **UI:** add a "Factory runs" feature to the JiuwenSwarm web frontend.
  - (a) **Replay:** an rb/1 bundle with a scrubber.
  - (b) **Live view:** tail events of a running session through the existing gateway or factory API, using polling or websocket.
  - (c) **Launch:** a new factory session from a task and contract with the five star CCs.
  - **Panels:** contract and ontology, task graph, CCs (bundle, verifier result, pinned hashes, artifacts), diffs with scorer stage chips, tests and scores, measurements (arm table), terminal log and final report.
  - **Integrity:** digest badges. Never hide a mismatch.
- **Pilot:** drive one CC (the recorder) end to end through JiuwenSwarm with the UI live, then the other four.
- **Bundle every run:** every M1–M3 run also writes a bundle so it appears in the UI.

**M5 Report (by 08:00 local).**
- A `report.md` inside the final bundle and an HTML view in the UI.
- **Contents:** what each CC built, its verification, measured effect, the honest limits, and what was not measured.

## 6. Evidence rules

- Every number links to a bundle file with a sha256.
- Record exact command lines, the binary sha256, the model shard digests (reuse the existing receipts where present), git commits and the capsule digests.
- Keep failed runs. Label them; don't delete them.
- Separate verified from inferred in every summary.

## 7. When to stop and report to the orchestrator

- After M0, and after the first capped DeepSeek load.
- After any unexpected memory event.
- When a capsule needs a semantic change rather than a wording fix.
- If M1 shows A cannot load under the cap.
- When anything would require sudo, deleting others' files, or a network push outside the work branch.
