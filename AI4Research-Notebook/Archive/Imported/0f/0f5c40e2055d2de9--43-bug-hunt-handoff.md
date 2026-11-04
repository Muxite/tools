# AI4Research bug hunt — handoff (2026-09-17)

**Update 11:40 EDT:** verification stopped at the owner's request after a WSL crash. The next step, adding the verified findings to the workbook, is handed off in **`44-fable-handoff-workbook.md`**. Start there.

Continues `42-windows-gui-handoff.md`. That note covers the Windows GUI test, the workbook and the web report. This one covers:
- the **bug hunt** (undeclared dependencies, Windows-specific errors, circular dependencies);
- the **R-56 fix**;
- the **working method** to use from now on.

## 0. Read this first: how to work (the owner's rules for this hunt)

**Goal (owner, 2026-09-17):**
- Find every error, and at most scope how far each one reaches and where it is (file:line, evidence). Do **not** fix.
- The co-op students will rewrite the whole codebase on a different harness (the supervisor wants to move off Solar). The error list is what carries over.
- Fixes (like R-56) and local workarounds are only there to get far enough to reach the next error.
- Don't write fix proposals or cleanup plans.

The first attempt ran several agents in parallel, and that crashed WSL. Work **sequentially**. Slow is fine; failing is not.

1. **One thing at a time.** One agent, one WSL command, in the foreground. Wait for it to finish before starting the next. No background loops or monitors.
2. **One WSL instance.** Use the existing `Ubuntu-24.04` (user `muk`). Never create distros, VMs or containers.
3. **No repo clones.** The repo history is 2 GB; full clones over `/mnt/c` ran the host out of memory. Run code straight from the existing checkout `/mnt/c/Users/m50066326/huawei/stellven/AI4Research`.
   - Need the exact base content? Use `git show openJiuwen-Solar:<path>`, or `git archive openJiuwen-Solar <dirs>` into a folder under `~`.
4. **Scratch space goes in `~/hunt-tmp/<ID>`**, not `/tmp`, because distro restarts empty `/tmp`. Delete it when the item is done.
5. **Keep reproductions simple:** the smallest check that decides the claim, plus a control that differs in exactly one thing.
6. **Don't prime verifiers.**
   - The reproducer gets only the one-line claim and 1–3 file pointers. It never sees the finder's steps, outputs or reasoning.
   - The reviewer gets the claim, the reproducer's report and its saved files, and tries to break the write-up.
7. **Check memory before each WSL step.** Watch Windows free RAM (`Get-CimInstance Win32_OperatingSystem`) and the size of the `vmmemWSL` process. If free RAM is under ~1.5 GB, stop and wait.
8. **Carried over from note 42:**
   - No model usage and no dashboard task submissions unless the owner asks.
   - Never `solar <cmd> --help`.
   - Never write to `~/.solar` / `~/.claude` (the permission check blocks it anyway; the owner runs those steps).
   - Say "not verified" rather than guess.
   - Verdict-changing code goes on its own branch, staging explicit paths only.
   - Measurement trap: from Git Bash use `MSYS2_ARG_CONV_EXCL='*' wsl.exe -d Ubuntu-24.04 -- bash -s <<'EOF' … EOF`; always pass `-d`.

**Per-bug procedure, in order:**

| Step | Who | Gets | Writes |
|---|---|---|---|
| 1. Claim | lead | finder report | one-line claim + pointers |
| 2. Reproduce | fresh agent | `REPRO.md` (top half) + claim + pointers | `repro/<ID>/` scripts, logs, verdict |
| 3. Review | fresh agent | `REPRO.md` (bottom half) + claim + repro report + `repro/<ID>/` | `repro/<ID>/review/`, verdict, accepted write-up |
| 4. Record | lead | review | `VERDICTS.md` entry; later workbook/report |

The prompt templates and rules are in `C:\Users\m50066326\solar-tools\bug-hunt-20260917\` (`BRIEF.md`, `REPRO.md`), already updated for these rules.

## 1. Machine state right now (checked 10:16 EDT)

- **Distro restarts.** `Ubuntu-24.04` restarted **three times** today: 10:07:36, 10:09:58 and 10:16:31 EDT. The first two were caused by our clones; the third was very likely our own 10:16 check command followed by R-07 (see §3c).
  - **Cockpit and coordinator are down** (no tmux session), so nothing is advancing runs.
  - The **status service** is active on port **8765**.
- **Blocked Alita-G run** `sprint-20260917-134155-…-b67894fe` (pasted-text version of test C): it got past planning (R-39 workaround works), then was blocked by R-56. Its status is still `active / graph_dispatch_active`, last updated 14:03:48 UTC.
- **Repo:** `C:\Users\m50066326\huawei\stellven\AI4Research` is on **`fix/frozen-profile-operator-id`** (commit `01ac5aaf3`, not pushed).
  - The earlier fix branch `fix/a11y-gate-windows-python` (`cdc1e7a56`) still exists.
  - Run `git checkout openJiuwen-Solar` before unrelated work.
- **Scratch left in WSL:** `~/fixwork/{base,patched,base.failed}`, needed for step 2a below; delete after. Agent scratch in `/tmp` was wiped by the restarts.
- **All local workarounds from note 42 §2 are still in place.**

## 2. Owner actions

**Done 2026-09-17 at the owner's request:**
- **2a applied at 11:21 EDT:** printed `applied`. The backup is `~/.solar/harness/lib/multi_task_runner.py.bak-20260917-before-frozen-profile-fix`, and the new file parses.
- **2b done at 11:22 EDT:** tmux `solar-harness` is running with 4 Claude panes, coordinator PID 1833 and watchdog PID 1956. The preflight is all OK, with claude 2.1.274 (it auto-updated at 09:47).
- **Measurement trap found on the way:** `wsl.exe … -- bash -c '…$VAR…'` and `bash -lc '…'` have their `$vars` expanded by an outer shell before bash runs. That silently produced `PATH` without `~/.local/bin`, so preflight said "claude runtime CLI not found". Use `wsl.exe -d Ubuntu-24.04 -- bash -l -s <<'EOF' … EOF`.
- **Still to check:** whether the blocked Alita-G run now dispatches to `mini-claude-sonnet-builder-2` (§3).
- **The cockpit did not survive:**
  - The 11:22 cockpit died at 11:22:41. The first keep-alive (started with `Start-Process` from the tool) had already exited, so WSL stopped. A keep-alive started through WMI (`Invoke-CimMethod Win32_Process Create`) does survive.
  - A second start at ~11:33 was followed by **`Wsl/Service/E_UNEXPECTED`**: Ubuntu stopped, and the keep-alive died with it. 2.2–2.5 GB was free and the cause is unknown (VERDICTS.md "Incident 2").
  - **State now:** R-56 fix installed, cockpit down, Ubuntu stopped. Whether the Alita-G run dispatches is still unverified.

The original instructions follow.

### 2a. Apply the R-56 fix to the installed runtime

This backs up the installed file, checks it matches the base version, then copies in the fixed one:

```
MSYS2_ARG_CONV_EXCL='*' wsl.exe -d Ubuntu-24.04 -- bash -c 'L=~/.solar/harness/lib/multi_task_runner.py; diff -q <(tr -d "\r" < $L) <(tr -d "\r" < ~/fixwork/base/harness/lib/multi_task_runner.py) && cp -p $L $L.bak-20260917-before-frozen-profile-fix && cp ~/fixwork/patched/harness/lib/multi_task_runner.py $L && echo applied'
```

To undo, copy the `.bak-20260917-before-frozen-profile-fix` file back.

### 2b. Restart the cockpit (spends Claude usage)

From a WSL login shell:

```
export PATH="$HOME/.solar/bin:$PATH"; solar harness start ~/.solar/workspace
```

This has two effects:
- The Planner pane will run its own Opus session and may write another notes file into `~/.solar/workspace/sprints/` (R-54/R-55).
- The coordinator's next check should dispatch the Alita-G step to `mini-claude-sonnet-builder-2` (Sonnet). This is **not verified live**.

### 2c. Decide whether to keep the Planner notes

The notes in `~/.solar/workspace/sprints/` still make every run show the Alita-G note as its result (R-38/R-54).

## 3. R-56: a run is blocked by "unknown multi-task profile"

- **Symptom:** the run page shows `node blocked: frozen_scheduler_preflight_unavailable:unknown multi-task profile: mini-claude-sonnet-evaluator-print`. Every recovery button is disabled, and the coordinator fails the same check every ~15 s without calling a model.
- **Cause:**
  1. The planner bundled `cap.requirement-compiler-verification` into the answer step.
  2. That capability's `default_operator_profile` is a **worker id**, not a profile (`capability-capsules.registry.yaml:94`).
  3. `_frozen_default_operator_profile` (`harness/lib/multi_task_runner.py`) only ignores worker ids that are among the step's own candidates. Here the candidates are 3 builders, so the evaluator id was treated as a profile, and `select_profile` raised the error.
  4. 63 enabled workers have no profile, so other capabilities can hit the same thing.
- **Fix** (`01ac5aaf3`): ignore any value that names a registered worker and is not also a profile. It reads the registry directly, because `load_physical_operators()` prunes blocks and would write to disk.
- **Tests:** 2 new tests pass. The 16 other failures in `tests/harness/runtime/test_multi_task_runner_submit_path.py` (`plan_validator_dispatch_refused`) are **identical on the unmodified base**, so they are pre-existing and unrelated.
- **Offline check on the live run's frozen step:**
  - **Before:** raised the error above.
  - **After:** profile `builder`, backend `claude-cli`, model `sonnet`, worker `mini-claude-sonnet-builder-2`.
  - This needs `~/.local/bin` on PATH. Without it, the next check reports all three builders as `backend_cli_unavailable`.
- **Evidence:** `solar-tools\bug-hunt-20260917\r54-r56-scripts\blk1-4.sh`.
- **Side finding:** the shipped `harness/config/physical-operators.json` contains another developer's path, `/mnt/c/Users/j50058254/Desktop/Github repo/OpenSolar-Canonical/…`, plus "Mac mini" operators with `/opt/homebrew/bin/codex`.
- **Still to do:** add R-56 to the workbook and web report once the live run confirms or refutes the fix.

## 3b. R-57 (GUI): the POC preview says "Preparing" on a blocked run

- **Reported by the owner** on 2026-09-17 (10:16 EDT page refresh) on the blocked Alita-G run `sprint-20260917-134155-…-b67894fe`.
- **What the page shows at the same time:**
  - Header: **Paused**, `node blocked: frozen_scheduler_preflight_unavailable:unknown multi-task profile: …` (R-56); every recovery button disabled.
  - Plan panel: "0/1 steps · blocked at a capability gate", but the only step's chip says **queued**.
  - **Dynamic POC preview:** title **"Preparing"**, phase "graph dispatch active", **0%**, 0 passed / 1 total / 0 failed, "Repair results will appear here as the plan stabilizes.", "The preview will appear when a POC artifact is produced." Nothing says the run is blocked or waiting on the owner, so the panel reads as "not passed, not failed, about to start".
- **Cause (code reading):**
  - `harness/status-server/react-app/src/App.tsx:1549-1555`: the title has only four states: "Completed with failures", "POC ready", "Building now", "Preparing". Anything not terminal and with no active node falls to "Preparing".
  - `harness/status-server/react-app/src/pocPreview.ts:70-83`: the model has no blocked or paused count and never reads `status_counts.blocked` or the node block reason.
  - `pocPreview.ts:59-60`: `terminal` is true only for `passed|completed|done`, so a failed or blocked run is never terminal. That keeps the "…as the plan stabilizes" text forever and makes "Completed with failures" reachable only when the run status is itself `passed`.
- **Relation to earlier findings:** same family as R-27 ("Preparing"/spinner in every state) and R-52 (preview not useful; spinner stays after the run ends). R-57 is the blocked-run case, where the page elsewhere already knows the node is blocked. Product-honesty rule: the preview must show the real state.
- **Status:** owner-observed plus code reading. Not independently reproduced (a mock projection with one blocked node would decide it without model usage). Not yet in the workbook or web report.
- **Addendum (owner, 10:4x EDT): the loading spinner never stops.** `App.tsx:1639` is `<Loader2 className={model.terminal ? "" : "spin"} />` in the preview window. Because `terminal` is false for blocked and failed runs (above), the spinner spins forever on them. This is a pure frontend condition: it does not depend on the backend or on any exception.

## 3c. The backend "died": R-07 again, reproduced live on 2026-09-17

- **Symptom (owner):** the dashboard stopped answering; the page shows "reconnecting" and "Failed to fetch".
- **Evidence:**
  - At 10:45 EDT `wsl -l -v` showed `Ubuntu-24.04` **Stopped** with 4.7 GB free on Windows, so this was not the earlier out-of-memory crash.
  - `journalctl --user -u solar-status-server`: every start today ended within 16–66 s with a **clean** stop ("Reached target shutdown.target / Exit the Session"), with no traceback or error lines: 10:09:35→10:09:51, 10:10:00→10:11:06, 10:16:33→10:16:49.
  - **Live repeat:** my diagnostic `wsl.exe` command started the distro at 10:45:23 (service active, port 8765). Seconds after the command ended, `wsl -l --running` no longer listed Ubuntu-24.04 and `/healthz` refused the connection.
- **Cause:** R-07 / note 41 §12. WSL stops the distro once no `wsl.exe` session is attached; systemd units and linger don't keep it up. Earlier today the owner's open WSL terminal (the cockpit shell) held it up; that was lost in the 10:07/10:09 restarts.
- **Correction to §1:** the 10:16 restart is **very likely ours**. The §1 state check at 10:16 started the distro, and it stopped when that command ended (the same pattern as the live repeat). The service being "back on 8765" at 10:16 lasted 16 s.
- **To keep the backend up:** keep a WSL terminal open, or run a hidden holder such as `wsl.exe -d Ubuntu-24.04 -- sleep infinity` (the control used in note 41 §12). This is the owner's decision because it is a long-running background process.
- **Done (owner asked, 2026-09-17 ~11:15 EDT):** a hidden holder `wsl.exe -d Ubuntu-24.04 -- sleep infinity` is running (Windows PID in `solar-tools\bug-hunt-20260917\wsl-holder.pid`). The distro stays up, and `/healthz` on 8765 answers 200. To stop it: `Stop-Process -Id (Get-Content …\wsl-holder.pid)`. A reboot or `wsl --shutdown` also ends it. The cockpit and coordinator are still not running (§2b).

## 3d. R-58 (GUI): "reconnecting" forever, never "offline"

- **Symptom:** with the backend gone, the stream chip stays on "reconnecting", and the rest of the page keeps its last state ("Paused", "graph dispatch active", "Preparing"). The only other sign is "Failed to fetch" in the sessions list.
- **Cause (code reading):** `App.tsx:1244` and `:1296` set `retrying` on every EventSource error. Nothing ever moves to `off`/"offline" after repeated failures (`off` is set only when EventSource is missing or no run is selected, `:1246`, `:1263`, `:1299`). The 20 s refresh (`:1247-1253`) keeps failing, and no banner says the service is unreachable. If the service comes back on a different port (R-24), the page retries the old port indefinitely (not verified live).
- **Honesty rule:** the page must say the backend is unreachable, rather than showing stale run state as current.

## 3e. Owner hypothesis: frontend issues come from swallowed exceptions

- **Count** (Windows-side `Select-String` over `harness/**/*.py`, excluding `tests/`, `node_modules/`, `.packaging/`):
  - **2,446** `except:` / `except Exception[ as e]:` handlers in 447 files.
  - **973** of them are followed directly by `pass`, `continue` or a bare/empty `return`.
  - Heuristic: this checks only the next line, so handlers that swallow after a log line or a longer body are not counted.
  - Only 15 are in `status-server/` itself (10 in `routes/orchestration_routes.py`).
- **Verdict for today's symptoms: not the cause.**
  - The spinner (§3b) and "reconnecting" (§3d) are frontend conditions.
  - The backend stop (§3c) was a clean systemd shutdown with no errors.
- **Still a real risk:** swallowed exceptions hide evidence. NEW-01 (session-end save fails silently, `|| true`) is the same pattern in shell. A backend failure hidden this way would show up only as wrong or stale state, never as an error. This is recorded as a scoping finding (proposed **NEW-04**), not a cleanup task. It marks where errors can hide. When a later symptom looks like stale or wrong state, check the handlers on that path first.

## 4. Bug-hunt status

The full text of every verdict is in `bug-hunt-20260917\VERDICTS.md`. The finders' reports are in `findings\D1.md` and `findings\C_and_W.md`. Scripts and logs are in `repro\<ID>\`.

### Done (reproduced and reviewed)

| ID | Finding | Severity | Verdict |
|---|---|---|---|
| D1-01 | No pip on a fresh Ubuntu 24.04. The installer skips the Python requirements, then fails with "requirements … not importable" (no mention of pip) and leaves a half-done install. `--bootstrap-system-deps` doesn't help on Python ≥3.11. | high | stands with corrections |
| D1-02 | INSTALL.md says the `sqlite3` CLI is not required. The kernel's SessionStart hook exits 127, with no output, on every session without it. Stock 24.04 lacks it; it was hand-installed here on 09-16. | medium | stands with corrections |
| D1-03 | `solar doctor` lists tmux, jq and the model CLI as MISSING but says `Verdict: ok`, exit 0. The docs and release checklist treat that as a pass; launch preflight still blocks the start. | medium | stands with corrections |
| D1-04 | Without curl, `status-server start` kills a server that is answering after ~8 s and says only "did not become ready" (`harness/solar-harness.sh:4148-4163`). curl is undocumented and never installed or checked. Hits git clone + install.sh and pipx on curl-less Linux. | medium | stands with corrections |
| D1-05 | Without jq, the kernel safety hooks `pre-bash.sh`/`pre-edit.sh` exit 0 (no decision) for `rm -rf /`, `mkfs`, `.env`/`*.key` edits (`jq … 2>/dev/null`, pre-bash.sh:5-8). Solar panes run in bypass mode (R-47), so nothing guards them. jq is never checked for installs without harness, and only warned about by default. | high (bypass) / medium | stands with corrections |
| NEW-03 (from D1-06, whose own claim was wrong) | `install.sh` exits 1 with **zero output** when a Python name tried before the first suitable one is missing, e.g. an old `python3` with no `python`, even if python3.12 exists (`common.sh:95` + `set -e` at `:104/:115/:121`). Its own "needs Python 3.11+" message never prints. Stock Ubuntu 24.04 is unaffected; older distros (general knowledge) are. | medium-high | stands with corrections |
| D1-07 | A Codex pane exits 78 without `codex-code-mode-host` (on PATH or next to codex) or without kernel Landlock (`pane-launcher.sh:621-658`, `:492-603`). Launch preflight, `solar harness doctor` and `solar doctor` check neither; doctor calls the panes `manual_pending` and blames "trust/auth/quota prompts". The developers' own log (2026-08-29) records the same failure. | medium | stands with corrections |

### Reproduced or partly reproduced, review still needed (next in queue)

| ID | Where it stands | What the review must do |
|---|---|---|

### New findings from the reproductions (need their own reproduce → review)

- **NEW-01:** `hooks/session-end-save.sh:40` writes to table `evo_memory_semantic`, which the installer never creates. The error is swallowed, and nothing is saved.
- **NEW-02:** `hooks/pre-bash.sh:27` puts the pattern in quotes, so `curl … | sh` is never blocked, even with jq. The block messages are Chinese-only.
- **NEW-03:** see D1-06 above.

### Candidates not yet reproduced (suggested order)

1. **W-01:** `install.ps1:184` passes `wslpath` a path whose backslashes are stripped, and PS 5.1 then throws, so the bundled installer aborts. Hidden today by R-02.
2. **W-05:** the desktop app caches the default distro and never re-checks after installing into Ubuntu-24.04 (a mock test exists in `windows\stale-cache.cjs`).
3. **W-07:** `main.js:1118-1124` puts `awk '{print $1}'` in a command where the outer shell eats `$1`, so the WSL-IP fallback breaks on VMs with several IP addresses.
4. **W-08:** the documented `./install.ps1` is blocked by the default execution policy.
5. **C-01:** the desktop app requires `codex login status` before showing the dashboard, but the first-time login is only offered inside the dashboard. It is also hard-coded to Codex.
6. **C-02:** the desktop app copies its bundled harness before checking whether Solar is installed, so the real installer (tmux, jq, pip, systemd) is never offered.
7. **C-03:** an `auth_expired` worker block survives re-login and the suggested `clear-override`, so intake stays blocked for 6 h, or forever for browser workers. (It was checked offline with `circ\run_authblock.sh`.)
8. **C-08:** `solar doctor` is itself written in Python, so it can't report "python3 missing" (exit 127).
9. **W-02:** the RunOnce resume command is 726–830 characters, over the documented 260-character limit, and HKLM RunOnce runs only for admins.
10. **W-04, W-06:** Docker-only WSL forces an admin prompt and a reboot; an existing older or Rancher distro is picked and then fails with Python <3.11.
11. **Low priority:** D1-08 (`requests` not declared), D1-09 (developer-machine operators), D1-10 (fixed `/tmp/solar.sock`), C-04 (port file deleted; related to R-24), C-05 (reboot loop, unverified), C-06 (`repair`/`update` point at each other), C-07 (= R-34), W-03 (non-admin users), W-09 (apostrophe in path; same mechanism as R-02).

Checked and found clean: systemd ordering, Python import cycles, bash `source` cycles, installer component order, repo symlinks, case collisions, reserved names.

## 5. Files

| What | Where |
|---|---|
| Hunt workspace (rules, templates, verdicts, findings, scripts) | `C:\Users\m50066326\solar-tools\bug-hunt-20260917\` |
| Rules for every agent | `…\BRIEF.md` |
| Reproduce / review prompt templates | `…\REPRO.md` |
| Verdicts and accepted write-ups | `…\VERDICTS.md` |
| Finder reports | `…\findings\D1.md`, `…\findings\C_and_W.md` |
| Per-bug scripts and logs | `…\repro\<ID>\` (+ `review\`) |
| Finder scripts | `…\d1\`, `…\circ\`, `…\windows\` |
| R-54/R-55/R-56 investigation scripts | `…\r54-r56-scripts\` |
| R-56 fix | branch `fix/frozen-profile-operator-id`, commit `01ac5aaf3` |

## 6. What changed today in the report (already published)

- **R-54 rewritten:** the Planner starts on its own at every cockpit start, because it is sent the start-up word `solar`, uses relative paths, and is given no run. The earlier dispatcher theory was wrong.
- **R-55 measured:** 12–13k output tokens and 0.5–0.8M cached input tokens on Opus per start.
- **R-47 corrected.**
- **Published:** workbook rebuilt; web report Version 24; note 42 updated.
- **Not yet in the web report:** R-56, R-57 (§3b), the R-07 live repeat (§3c), R-58 (§3d), NEW-04 (§3e) and the bug-hunt findings. They are in the workbook (next item).
- **Workbook updated (2026-09-17, afternoon):** rebuilt from `workbook_v2.py` with the note 44 content.
  - **Added:** R-56, R-57, R-58 (section E), the R-07 live repeat, a new section I with D1-01 to D1-05, D1-07 and NEW-03 (checklist and problems, with reach and not-tested caveats), and a "Candidates: NOT yet reproduced" block (NEW-01, NEW-02, NEW-04, W-xx, C-xx). D1-06 is under "Left out".
  - **Style changes asked for the same day:** no "owner" wording ("Hands-on use" instead), no em or en dashes, American spelling, hands-on failures first in each section, failed rows say what happened plus "What was changed or tried", steps described instead of links to repro folders, font 10 with wider evidence columns.
  - **Checks:** `report-src/xl_verify_v2.py` passes (90 checklist rows: 50 fail, 19 pass, 11 pass with limits, 6 works after change, 4 not available; 40 + 7 + 6 problems; 14 candidates). Visual layout not checked (no Excel on this machine).
  - **Adversarial review:** one fresh agent, given only the workbook dump, `VERDICTS.md` and `screenshots/INDEX.md`: 4 must-fix, 17 should-fix, 11 nits. All must-fix and should-fix items were applied and the workbook rebuilt. Details it could not check against VERDICTS (R-56 backend/model, R-58 extra line numbers, NEW-04 file count) come from §3 to §3e of this note. The corrected build was not reviewed a second time.
  - **Not done:** the web report and the tundle release are unchanged.
- **R-59 added (2026-09-17 ~13:10 EDT), workbook rebuilt and re-verified (91 checklist rows, 41 + 7 + 6 problems):**
  - **Symptom:** run `sprint-20260917-163342-…-9fe56c01` ("Is the file I uploaded empty…", CaMeL.md, 2640 bytes). The single step `inspect_uploaded_file` was dispatched to `mini-claude-sonnet-builder-2` at 12:34:41 and finished correctly at 12:35:36 ("contains text", hash equals the upload). At 12:35:49 the harness raised `graph_eval_integrity_escalated_to_human` / `eval_artifact_snapshot_invalid` and set the run to `needs_human_review`; 44 idle scheduler ticks followed, then nothing.
  - **Cause (code reading + the run's snapshot file):** 2 violations `DECLARED_EVAL_BYTES_OUTSIDE_ROOT` for the declared inputs `artifact.requirement_ir` and `artifact.task_graph_node`, which are logical names but were looked up as files under `workdir/` (`graph_node_dispatcher.py:1482`, `:1572`, `:1622`, escalation `:15955`). The other 6 snapshot rows exist with matching hashes. Seen on 1 run; not repeated.
  - **Page (live screenshots, `screenshots\sorted\R-59\`):** still "IN PROGRESS / Agents are working…", Builder "NOW", 0%, preview "Preparing"; only a small step chip says "needs human review"; no action, no answer; "Open deliverable" opens the Alita-G Planner note (R-54).
  - **R-56 rows updated:** the blocked run was never retried (harness stop marked it `interrupted`, which the coordinator treats as finished; the page kept the 10:03 block text). The R-59 run did dispatch to `mini-claude-sonnet-builder-2` with the patch installed, but with a different capability, so the patch is still not verified on the blocked step.
  - **Seen the same afternoon, not in the workbook yet:** R-46 recurs when the cockpit is started from an untrusted folder (`solar harness start` with no path uses `$(pwd)`, here `/home/muk`); `solar` is not on PATH after install (installer only prints a hint, `lib/installer/main.sh:134-135`). The R-59 rows were not adversarially reviewed.

