# Handoff to a Fable agent: put the verified findings into the Excel workbook (2026-09-17)

**Today's only critical deliverable** is `C:\Users\m50066326\Downloads\tundle\ai4research\AI4Research Windows GUI Test Report - Muk.xlsx`. It is currently missing R-56 to R-58 and all the bug-hunt findings. Your job is to add them truthfully, rebuild the workbook, and have the result survive an adversarial review.

This note continues `43-bug-hunt-handoff.md`. Read §0 of that note for the working rules. Read this note first.

## 0. Rules (owner's, all still in force)

- **Goal:** find and scope errors: symptom, where it lives (file:line), how far it reaches, evidence.
  - **No fixes and no fix proposals.** The co-op students will rewrite the product on another harness.
  - In the workbook, leave the "change needed" / fix columns **empty** for new rows.
- **One thing at a time:** one agent and one WSL command, in the foreground.
  - No repo clones, no new distros.
  - Scratch goes in `~/hunt-tmp/<ID>`.
  - Check Windows free RAM (`Get-CimInstance Win32_OperatingSystem`) before every WSL step. Wait if it is under ~1.5 GB.
- **Do not start the Solar cockpit.** The owner stopped that after incident 2 (below). Never write to `~/.solar` or `~/.claude`. No model-backed tasks.
- **Evidence standard:**
  - Every workbook row must match an accepted write-up in `VERDICTS.md`, or an owner report.
  - Say "not verified" where that is the truth.
  - Plain English, no Chinese.
  - Findings the owner reported don't need verification.
- **Traps:**
  - `wsl.exe … -- bash -c '…$VAR…'` expands `$vars` in an outer shell first. Always use `wsl.exe -d Ubuntu-24.04 -- bash -s <<'EOF' … EOF`.
  - Always pass `-d`, because the default distro is docker-desktop.
  - WSL stops the distro a few seconds after the last `wsl.exe` exits (R-07).

## 1. Machine state at handoff (11:40 EDT)

- **WSL:** Ubuntu-24.04 is **Stopped**.
  - At ~11:33 the second cockpit start was followed by `Wsl/Service/E_UNEXPECTED` ("Catastrophic failure"), with 2.2–2.5 GB free. The cause is unknown (VERDICTS.md "Incident 2").
  - Docker Desktop's distro is running, and three other claude.exe sessions are alive on this machine.
- **R-56 fix:** installed in `~/.solar/harness/lib/multi_task_runner.py`, with a `.bak-20260917-before-frozen-profile-fix` backup.
  - Whether the blocked Alita-G run now dispatches is **not verified**, because the cockpit never stayed up.
- **No keep-alive is running.** If you need WSL up for a while, start one detached through WMI; a plain `Start-Process` from a tool call gets killed when the call ends:
  `Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='C:\Windows\System32\wsl.exe -d Ubuntu-24.04 -- sleep infinity'}`
  Write its PID to `solar-tools\bug-hunt-20260917\wsl-holder.pid`.
- **Repo:** `C:\Users\m50066326\huawei\stellven\AI4Research` is on `fix/frozen-profile-operator-id` (`01ac5aaf3`, not pushed). Do not edit it.

## 2. What goes into the workbook

**Sources:**
- `C:\Users\m50066326\solar-tools\bug-hunt-20260917\VERDICTS.md`: the accepted write-ups. This file is authoritative.
- Note 43 §3–§4.
- `screenshots\INDEX.md`.

**Workbook content:** it lives in `C:\Users\m50066326\solar-tools\report-src\workbook_v2.py`, which has these lists:
- `CHECKLIST`: sections A–H, plus Z for code-only.
- `PROBLEMS_HUMAN`: sections A–H.
- `PROBLEMS_TOOL`, `LEFT_OUT`, `DESIGN`.

The layout is set by `build_workbook_v2.py`. Check the sheet names and row shapes there before editing. Keep the existing style.

### 2a. GUI findings the owner reported (no verification needed)

| ID | Where | Content (from note 43 §3, §3b, §3d and VERDICTS.md) |
|---|---|---|
| R-56 | PROBLEMS_HUMAN, section E (Session page and run status) | Run paused with `node blocked: frozen_scheduler_preflight_unavailable:unknown multi-task profile: mini-claude-sonnet-evaluator-print`. Every recovery button is disabled, and the coordinator retries every ~15 s without calling a model. Cause: a capability's `default_operator_profile` is a worker id, not a profile (`capability-capsules.registry.yaml:94`, `_frozen_default_operator_profile` in `harness/lib/multi_task_runner.py`). Offline check: before the fix it raised; after it returns builder/sonnet/`mini-claude-sonnet-builder-2`. **Live effect not verified.** The fix exists only so testing can continue; don't present it as a recommendation. |
| R-57 | PROBLEMS_HUMAN E; also update the CHECKLIST row that cites R-52 (POC preview) | On a blocked run the POC preview says "Preparing", phase "graph dispatch active", 0% and 0/1/0, with no mention of the block. On a **failed** run it says "Preparing" with a spinner that never stops, next to "1 failed". On a mock blocked run the header says PAUSED/node blocked while the preview says "Building now". Cause: `react-app/src/App.tsx:1549-1555` (only 4 titles), `:1639` (spins while not terminal), `pocPreview.ts:59-60` (only passed/completed/done count as terminal), `pocPreview.ts:70-83` (no blocked count). Screenshots: `screenshots\sorted\R-57\` (mock dashboard: real server and frontend, fixture data). Related to R-27 and R-52. |
| R-58 | PROBLEMS_HUMAN E | With the backend gone, the connection chip says "reconnecting" forever and never "offline". There is no unreachable banner, the sidebar shows "Failed to fetch", and the run view shows stale state as current. Demonstrated at +30/+90/+180 s. Cause: `App.tsx:1244`, `:1296`; nothing ever sets `off` after failures. Screenshots: `screenshots\sorted\R-58\`. |
| R-07 (update the existing row) | PROBLEMS_HUMAN A | Add today's live repeat: every status-server start ended 16–66 s after the last `wsl.exe` exited, as a clean systemd shutdown with no errors. The owner saw "the backend died". |

### 2b. Bug-hunt findings: reproduced by one agent and survived review by another

Keep their hunt IDs (D1-01 …, NEW-03). Suggested placement: a new clearly labelled section, **"Fresh machine and Linux install (bug hunt, reproduced + reviewed)"**, in the problems sheet, or in `PROBLEMS_TOOL` if that fits the builder better. Also add matching CHECKLIST rows (result `IMPLEMENTED_AND_FAIL`) only where a user-facing feature row makes sense. Use the **accepted write-up** text from VERDICTS.md, shortened, without changing the meaning.

| ID | One line | Severity (from the review) |
|---|---|---|
| D1-01 | No pip on fresh Ubuntu 24.04. The install fails with a non-pip error and leaves a half-done install; `--bootstrap-system-deps` doesn't help. | high |
| D1-02 | INSTALL.md says the sqlite3 CLI isn't needed, but the kernel SessionStart hook exits 127 silently without it. | medium |
| D1-03 | `solar doctor` says "Verdict: ok" (exit 0) with tmux, jq and the model CLI missing. | medium |
| D1-04 | Without curl, `solar harness status-server start` kills a healthy server after ~8 s and says only "did not become ready". | medium |
| D1-05 | Without jq, the kernel safety hooks stop blocking `rm -rf /`, `mkfs` and `.env`/`*.key` edits. Unguarded in bypass mode (Solar panes, R-47). | high (bypass) / medium |
| D1-07 | A Codex pane exits 78 without `codex-code-mode-host` or kernel Landlock. No check covers either; doctor blames "trust/auth/quota prompts". | medium |
| NEW-03 | `install.sh` exits 1 with **zero output** when an earlier Python candidate name is missing (e.g. an old python3 and no `python`). The "needs 3.11+" message never prints. | medium-high |

Each VERDICTS entry also carries **reach** and **not-tested** caveats. Keep those in the row (the observed/limitations column); they are what makes the rows survive review.

### 2c. Not verified: list them only as such, or leave them out

The owner has not decided whether unverified candidates belong in the workbook. Default: put them in `LEFT_OUT` (or a small "Candidates not yet verified" block) with the words **"not yet reproduced"**, never as failures.
- **NEW-01:** `hooks/session-end-save.sh:40` writes to the missing table `evo_memory_semantic`, and the error is swallowed.
- **NEW-02:** `hooks/pre-bash.sh:27` quoting means `curl … | sh` is never blocked.
- **NEW-04:** 2,446 broad `except` handlers in the harness, 973 of them followed directly by pass/continue/return. This is a scoping note on where errors can hide, not a defect.
- **W-01, W-05, W-07, W-08, C-01, C-02, C-03, C-08, W-02, W-04, W-06**, and the low-priority list: see note 43 §4.

### 2d. Leave out

- Incident 1 and incident 2 (the WSL crashes) are test-harness and machine events, not product defects.
- The keep-alive mistake.
- The measurement traps.

## 3. Steps

1. **Read.** Read `VERDICTS.md`, note 43 §3–§4, `workbook_v2.py` and `build_workbook_v2.py`.
2. **Edit `workbook_v2.py` only.** Change `build_workbook_v2.py` only if a new section needs it. **First back it up** to `workbook_v2.py.bak-20260917-before-bughunt`.
3. **Update the Summary.** The builder counts rows itself; confirm that it does, and fix any hard-coded totals or text, e.g. "R-01…R-55".
4. **Rebuild.** This is one WSL command. Check memory first. Ubuntu is stopped, and this command will start it.
   ```
   MSYS2_ARG_CONV_EXCL='*' wsl.exe -d Ubuntu-24.04 -- bash -s <<'EOF'
   ~/.cache/xlsx-venv/bin/python /mnt/c/Users/m50066326/solar-tools/report-src/build_workbook_v2.py "/mnt/c/Users/m50066326/Downloads/AI4RnD Brief Feature Test Report.xlsx" "/mnt/c/Users/m50066326/Downloads/tundle/ai4research/AI4Research Windows GUI Test Report - Muk.xlsx"
   EOF
   ```
   - **Back up first:** copy the current .xlsx to `…- Muk.bak-20260917-before-bughunt.xlsx`.
   - **If WSL fails again** (`E_UNEXPECTED`): do not retry in a loop. Wait a few minutes and try once more. If it still fails, ask the owner whether to `pip install --user openpyxl` into Windows Python 3.12 (`C:\Users\m50066326\AppData\Local\Programs\Python\Python312\python.exe`) and build from Windows instead.
5. **Verify mechanically** with a small openpyxl script (`xl_verify.py` targets the old layout, so write a new one for v2). Check that:
   - the sheet names are as expected;
   - every ID from §2a/§2b appears exactly where intended;
   - no row presents a §2c item as a failure;
   - there are no CJK characters and no empty result cells;
   - the Summary totals equal the row counts.
   There is no Excel or LibreOffice on this machine, so the visual layout can't be checked; say so.
6. **Adversarial review** (one fresh agent, after the build). Give it only the rebuilt workbook, `VERDICTS.md` and `screenshots\INDEX.md`. Its job is to find any row that:
   - overclaims beyond the accepted write-up;
   - drops a reach or "not tested" caveat;
   - cites a wrong file:line;
   - counts an unverified item as a failure;
   - contains a fix proposal;
   - reads badly.
   Apply its corrections, rebuild, and re-verify.
7. **Record.**
   - Add a short "Workbook updated" line to note 43 §6, including what was added and the review verdict.
   - Update the memory file `windows-gui-testing-handoff.md` (IDs are now R-01…R-58 plus the hunt IDs).
   - Do **not** cut a tundle release and do not update the web report unless the owner asks.
8. **Report to the owner.** Include what changed, the review verdict, and what remains unverified.

## 4. Optional, only if the owner asks after the workbook is done

Reproduce and then review NEW-01 and NEW-02, the same way as the others (templates in `bug-hunt-20260917\REPRO.md`, rules in `BRIEF.md`). Then work through the candidate list in note 43 §4.
