# CHECKPOINT-1 handoff (2026-11-20 UTC)

User requested a clean pause to resume this same session on gpt-6.2-astra. Read BRIEF.md completely (Part A wins), then OPS/DIRECTIVE-2.md. On resume, lead is orchestrator; use gpt-6.2-sol bounded subagents as owner directs. Do not duplicate external ui-cc/ui-data/ui-story worktrees; merge their branches when orchestrator reports ready. No new jobq/docker infrastructure work.

## Code and app

Worktree: ~/predemo-spark/jiuwenswarm; branch demo/cc-star-ui-20261120. Local commits only; no remote or credential additions. Existing factory auth was copied privately into isolated homes as authorized in BRIEF. Latest commit/state is recorded in STATUS.md checkpoint line and `git status`.

App URL: http://<tailnet-ip>:5173. User systemd spark-demo-{frontend,gateway,agentserver}; frontend tailscale-only, backends loopback. bin/demo-up/down link tracked scripts/spark scripts. Leave these services running. UI lists native bundles/live homes, replay/live/launch, readable/raw evidence, digest badges, measurements. A real bounded read-only inspection session was launched from the browser: web-20261120T072040Z-bdae2ff9. Agent's checkpoint notes give final/pause state.

## Safety and approvals

P0 complete and orchestrator APPROVED in terminal. bin/capped uses systemd 100GiB memory.max, no swap, AllowedCPUs requested, verified CPU affinity0-7 + CPUQuota800% (cpuset not delegated). Reduced128MiB enforcement allocator killed with Result=oom-kill; production smoke and GPU-lock refusal passed. All logs retained in OPS/runs/p0-*.

GB10 driver UMA can escape cgroup accounting. MemAvailable watchdog at8GiB is the real safety backstop. Precheck requires110GiB. Reclaim-only memory.events max is expected and explicitly authorized; stop on oom/oom_kill, systemd Result=oom-kill, or watchdog. Peak cgroup/RSS sampled50ms may miss last interval; min MemAvailable retained. One GPU flock; never load DeepSeek outside wrapper. A+ cache never over61440MiB. S DS4_UMA_HEADROOM_GIB>=16. `--graceful-interrupt` forwards SIGINT with30s bound to keep tuner shutdown counters; watchdog remains immediate kill. Synthetic echo/SIGINT smoke passed.

## Completed model work (reconnaissance only)

No model should be running at checkpoint. A and S completed5 repeats each at512/2048, max_tokens32,temp0,seed1, cache_promptfalse. Exact prompt token IDs confirmed at llama-server; Strata effective dsml fixture template renders identical bytes. Fixed prompts/manifests in ops/spark/prompts. First requests discarded; first A preliminary prompt had510 actualtokens and is explicitly excluded. A's first partial load stopped conservatively on reclaim events, then orchestrator clarified and approved retry.

A = stock `-lm mmap --cpu-moe`, defaults otherwise, service host/port only. Default threads20 on8CPU affinity; default slots4, ctx/slot1048576. A load retry61.71s (prior partial load means not OS-cold). Normal exit0. S = actual fair direct-engine profile, host127.0.0.1:8081, DS4_UMA_HEADROOM_GIB16; engine reported load40.2s. Normal exit0. No OOM/watchdog in model runs. Exact command, engine SHA, outputs, memory trace and start/stop rows in OPS/LEDGER.jsonl and OPS/runs/{a-first-load,a-first-load-retry,s-first-load}.

Median client TTFT:

| Arm |512tokens|2048tokens|decode median approx|
|---|---:|---:|---:|
|A|9.679s|31.562s|2.94/2.92 tok/s|
|S|5.582s|19.184s|15.60/14.30 tok/s|

Within each arm/size all5 greedy output hashes match and cache_n0. Strong A warm-up drift (512 range5.188–24.667,2048 range12.758–34.167). P1 concurrent factory/app activity means reconnaissance; finalP4 must have NO factory agents, pytest, npm/builds. No CC speed claim. OPS/BASELINE.{json,md} links every contributing result digest. P4 ABBA not started.

Strata automatically updates original expert-profile.bin in normal runs. Before/after snapshots and hashes retained in S run. Do not restore/overwrite owner's pack. Subsequent S should use task-owned pinned before copy with explicit --expert-profile + --profile-readonly, recording the bookkeeping deviation to prevent profile drift. Config/provenance in OPS/configs and S run.

## Next GPU work

A+ has NOT started. Native tuner launcher bin/tune-server caps/logs every calibration process, rejects GPU cache>60GiB, requires mmap/CPU MoE, forwards normal shutdown stats. Start only after all CPU compiler work is idle and no model processes remain. Proposed command (unique output; do not reuse tuner directory with different command, upstream deletes entries on mismatch):

```
jiuwenswarm/.venv/bin/python llama.cpp-stock/scripts/moe-cache-tune.py --max-mib 61440 --out OPS/tune-aplus-UNIQUE -- bin/tune-server -m ~/software-factory-spark-20261113/deepseek-v41-upstream-20261119/converted/DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ2_XXS-00001-of-00006.gguf -lm mmap --cpu-moe
```

Supervise first cache-enabled load; tuner driver itself only does bounded sequential file warming and launches each model through wrapper. Then use recommendation, record exact settings, discard first request, measure matched warm repeats. Native tuner calibration may be lengthy (first2x2048 decode, later2x512 per calibration), so value/time-box decisions matter.

## P3 factory/CC state

Bringup DEADLINE08:30Z: recorder needs a built diff; otherwise direct-per-capsule-method fallback with native-store import and honest label, keep factory retry in parallel. Source phase already produced clean recorder commit9d0733cba12c164827b646ea86af618ce7b5ca47 through JiuwenSwarm's native source_workbench; complete-diff capsule verify done=true, static gate-unset-silence inconclusive, no runtime acceptance. Diff at factory-runs/star-observability_event_recorder/products/recorder.diff. Source paths/attempt IDs/resume commands in OPS/p3/CHECKPOINT-1.md from factory agent.

Five separate homes under factory-runs/star-{capsule}, isolated source clones with own.git and no remotes, auth private. Generic agent shell fails bwrap loopback EPERM; native source_workbench succeeds, do not widen sandbox or use sudo. First recorder preparation used linked worktree, host rejected safely; retained and replaced by isolated clone. Other four sessions started source-only, no builds/GPU authorized. Their exact paused states are in P3 checkpoint.

Native build first attempt38389509d2114cb3a9eb69e86886d1a9 failed before compile (ninja absent); not performance-eligible. Retry11283a6509ff40b4bc31acd4b33a086d derives exact stock CMake recipe: Makefiles, GGML_NATIVE/OPENMP ON, empty ARM arch, FA_ALL_QUANTS OFF, sm121 release, installed cc/c++. Historical factory image/Strata recipe left unchanged. Current retry result/pause state provided by P3 agent. Do not sink more time into jobq/docker; use minimum native build/run path.

Five source capsules1.1.1 copied via canonical transport migration1.1.2 (historical kind -> roles, source material hashes retained). Spark host guidance/versioned revision per owner; see current manifests and star-transport-migration.json. No finished product diff shipped in capsules. Factory raw/readable contract star-deepseek-v1 and Spark tasks added. No M1 machinery restored.

## Acceptance risks requiring attention

OPS/cc-candidate-index.json indexes selected r2WO1/2/4/5 and r1WO3, exact digests and historical Satay scores. All5 apply cleanly to stock pin. Historical passes are NOT Spark runtime passes. OPS/cc-review.md has source-backed static issues:

- Strict A defaults slots4 make predictor and mapper ineligible. Mapper additionally rejects DeepSeek SWA checkpoints (default n_ctx_checkpoints32), and aligned2048/512 already makes no cut change. A separate matched activation profile or versioned semantic revision is needed; do not silently change A or call fallback a gain.
- Cache and predictor bypass native MoE cache, so activation vs A+ cannot be assumed.
- Expert placement plans conflict with stock --cpu-moe pattern; stock conflict fallback happens after attempted planned load. Need carefully bounded plan/control or capsule revision, not hidden flag change.
- Historical recorder scorer permits accounted loss (e.g.1 lost event), while capsule normal-run method demands zero loss. Preserve narrow scorer pass, don't claim full capsule acceptance.

BRIEF requires stop/report before semantic capsule changes. Directive2 encourages improvement; report concrete needed revision to orchestrator before changing semantics. Host-only Spark guidance edits explicitly authorized. No semantic fixes yet.

## Fixture and scorer correction on resume

IMPORTANT Directive2: owner's authoritative Granite is being copied to ~/models/campaign/gguf/granite-3.1-1b-a400m-instruct-Q8_0.gguf, SHA starts a52205df. At checkpoint it may still be partial; do not hash/use until copy done and full expected digest provided/retained. This differs from downloaded alternative in ~/predemo-spark/models/... (published HF087517...,1422239456bytes), which must NOT be silently substituted for authoritative fixture. Preserve alternative acquisition evidence; no fixture model was run.

tools/spark_demo/scorer_adapter.py and documented platform amendment currently pin the alternative0875 fixture and platform metadata. It imports unchanged digest-pinned frozen scorer stages and adds per-runtime ledger instrumentation, but needs review/update to owner's path/hash as documented path-mapping-only amendment before any reference/runtime use. Original scorer cannot run because derived Satay source/build paths, receipt/tool paths, CUDA87 and reference absent. Frozen failure proof retained. No scorer stages run on Spark except metadata/tests/scope failure. No new stage/predicate changes allowed; new same-host stock reference needed with authoritative fixture. Don't treat existing alternative adapter as final approved scorer.

## Evidence/UI import

ops/spark/import_evidence.py imports immutable hashed artifacts and idempotent observations into factory-runs/spark-direct-evidence (see CLI/help for actual home defaults), includes failed/discarded runs and labels direct lead benchmark work honestly. A10+S10 eligible observations, cold510 excluded, ontology/capsule/contract materials attached; native exports under factory-runs/exports. Display uses median TTFT, full ranges,n,hash counts, sampled cgroup peak + min available, UMA caveat. No fabricated factory claim for direct benchmark imports. Re-import/export unique snapshots after new milestones. External browser tailscale verification by owner remains outstanding.
