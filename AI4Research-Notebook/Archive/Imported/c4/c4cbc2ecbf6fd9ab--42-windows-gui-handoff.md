# AI4Research Windows GUI testing — handoff (2026-09-17)

Continues `41-windows-gui-getting-started.md`. §31 there has the detailed log of every finding and correction.

**Update 2026-09-17:** the bug hunt, the R-56 fix and the sequential working method are in `43-bug-hunt-handoff.md`. That note's §1 has the current machine state and overrides the "Repo" and "Cockpit" lines below: the repo is now on `fix/frozen-profile-operator-id`, and the cockpit is down after three distro restarts.

## 1. Where the results are

| What | Where |
|---|---|
| **Excel report (main deliverable, owner-organised)** | `Downloads\tundle\ai4research\AI4Research Windows GUI Test Report - Muk.xlsx` — Summary, Checklist (81 rows, sections A–H + Z), What works, Problems & reproduction (37 user-visible + 6 code-only + left-out list), Design questions |
| Web report (long form, every finding R-01…R-55) | https://claude.ai/artifact/Fb1A6UT6DDUwi48r9d6mhf (Version 24, private). Its own feature table is the older 74-row layout. |
| Report sources and build scripts | `C:\Users\m50066326\solar-tools\report-src\` (HTML source, `workbook_v2.py` = workbook content, `build_workbook_v2.py`, extract/verify scripts) |
| Test/probe scripts (Playwright, no model use) | `C:\Users\m50066326\solar-tools\report-src\probes\` |
| Alita-G run files + reading guide | `C:\Users\m50066326\solar-tools\runs\alita-g-20260916\README.md` |
| Test prompts / fixtures | `solar-tools\pass-probe\` (direct answer, code task), `solar-tools\claim-test\` (+ WSL `~/solar-fixtures/claim-test`) |
| Mock dashboard (fixture data, no model use) | `solar-tools\start-mock-dashboard.ps1` → http://127.0.0.1:8790 (was killed for low memory; restart when needed) |

**Rebuild the workbook** after editing `workbook_v2.py`. Needs openpyxl, which is in the scratch venv `~/.cache/xlsx-venv` in WSL:
```
wsl -d Ubuntu-24.04 -- bash -c '~/.cache/xlsx-venv/bin/python /mnt/c/Users/m50066326/solar-tools/report-src/build_workbook_v2.py "/mnt/c/Users/m50066326/Downloads/AI4RnD Brief Feature Test Report.xlsx" "/mnt/c/Users/m50066326/Downloads/tundle/ai4research/AI4Research Windows GUI Test Report - Muk.xlsx"'
```
The summer workbook is only a style template and is never modified. The layout has **not** been checked in Excel (no Excel or LibreOffice on this machine).

## 2. Machine state (all local, reversible, none committed)

**WSL:** `Ubuntu-24.04`, user `muk`. **Always use `wsl -d Ubuntu-24.04`** — the default distro is docker-desktop (R-22).

**Dashboard service:** systemd user unit `solar-status-server`. The port changes on restart and is currently **8765**; it is recorded in `~/.solar/harness/run/status-server.port`.

**Local workarounds in place:**

| Change | File | Why | Undo |
|---|---|---|---|
| `~/.local/bin` on the service PATH | `~/.config/systemd/user/solar-status-server.service.d/10-local-bin-path.conf` | R-14: the service could not find codex/claude | delete the file, `systemctl --user daemon-reload && systemctl --user restart solar-status-server` |
| Model stages use Claude | `.../20-llm-provider.conf` + `export SOLAR_LLM_PROVIDER=anthropic` in `~/.profile` (marked LOCAL WORKAROUND) | R-43 (Codex out of usage) and R-45 | delete both, restart the service and the cockpit |
| Runtime = claude | `~/.solar/harness/config/solar-user-config.json` (backup `…json.bak-20260916-before-claude`, runtime was codex) | R-45 | Settings → runtime Codex |
| PM pane model = claude-haiku | same file (set by the owner) | R-48 → it actually runs Sonnet | Settings |
| Claude trust + bypass accepted | `~/.claude.json`, `~/.claude/settings.json` (`skipDangerousModePermissionPrompt`) | R-46 | `claude` settings |

**Other state:**
- **Accounts.** Codex is signed in but **out of usage until 2026-10-16 13:20** (R-43). Claude Code 2.1.273 is signed in (claude.ai) and every model stage now uses it, so tasks spend Claude usage.
- **Cockpit.** tmux `solar-harness`, 4 Claude panes (Opus 4.8; PM on Sonnet). Panes run with **permission prompts off and no file fence** (R-47), and every start makes the Planner run a full Opus session on its own (R-54, R-55).
  - Restart it from a WSL login shell: `export PATH="$HOME/.solar/bin:$PATH"; solar harness stop; solar harness start ~/.solar/workspace`
- **Leftovers that affect results.** `~/.solar/workspace/sprints/*.planner-*.md` (written by the Planner pane on its own at cockpit start, R-54) make every run show the Alita-G note as its result. R-54 is now explained, so they can be moved out to get clean deliverable lists. The two Planner transcripts are the evidence; keep them.
- **The installed runtime came from the Windows checkout.** As a result, many files are world-writable and 1,277 Python files have CRLF line endings (R-40).
- **Repo** `C:\Users\m50066326\huawei\stellven\AI4Research`: currently **checked out on `fix/a11y-gate-windows-python`** (one commit `cdc1e7a56`, not pushed; git identity set repo-locally). Switch back with `git checkout openJiuwen-Solar` before other work. No uncommitted changes.

## 3. Runs so far

| Run | Provider | Outcome | Problem |
|---|---|---|---|
| hello.txt `…172130…e3f88bdf` | Codex | planning failed | R-26, R-32 |
| AllocBench + paper `…180422…1b04e202` | Codex | planning failed (worker binding) | R-39 |
| sky blue `…185659…c339d1ab` | Codex | passed; answer hidden | R-44 |
| fish `…185941…77f0f03b` | Codex | failed in 2.5 s (usage limit) | R-43 |
| fish again `…193358…6367eabd` | Claude | finalized | R-44, R-54 |
| Alita-G + paper `…193901…906b3dd8` | Claude | planning failed (no report-plan capability) | R-39 |

## 4. Open items, in suggested order

1. **Owner review of the workbook in Excel.** Row heights are estimated, and some owner judgements are recorded as PASS (intent/requirements quality).
2. **R-54 root cause: found (2026-09-17).** No task was dispatched to the Planner. On every Claude cockpit start it is sent the word `solar` (`lib/persona-config.sh:232`, `pane-launcher.sh:159`). `personas/planner.md` names no run and uses the relative path `sprints/<sid>.planner-*.md`, and the pane runs in `~/.solar/workspace`. The model then searched `.solar-intake-sources`, picked a failed run and wrote notes there; the transcripts are in `~/.claude/projects/-home-muk--solar-workspace/`. Write isn't in its tool list, but permission prompts are off (R-47). The earlier `pm_dispatch.py` write-scope theory was wrong. **Any cockpit restart will probably do this again** (R-55: 12–13k output tokens on Opus per start).
3. **Alita-G workaround test.** Paste the paper text instead of attaching it. If it still fails: branch + change so `literature_discovery` is optional for user-supplied sources (R-39).
4. **Owner's manual test list** (from the chat): approval screen on the mock, reload/deep links, two tabs, narrow window, keyboard-only use, stopping the service mid-page, vague request ("Make it better"), an explicit file path, a sourced question, cancelling, two tasks at once.
5. **Not verified yet.**
   - A public website reading the dashboard (R-30).
   - A Claude pane actually writing outside the workspace (R-47).
   - Whether the code task in `pass-probe\2-code-task.txt` gets past planning.
6. **Fix candidates (each on its own branch; small unless noted).**
   - R-27: phase-name mismatch.
   - R-38: open-button scroll and shared-folder fallback.
   - R-36: de-duplicate by operator_id.
   - R-46: auto-answer prompts by text.
   - R-48: Haiku in the registry, or stop offering it.
   - R-53: path match.
   - R-14: service PATH.
   - R-40: `rsync --chmod`, `*.py eol=lf`.
   - Larger: R-32 clarification flow; R-43 pending list and provider errors.

## 5. Working rules the owner set (keep following)

- Documented install path first; repair only after it fails, and record the failure.
- Every claim needs evidence someone can re-check. Say "not verified" rather than guess, and correct wrong claims openly.
- Code changes that change a verdict go on their own branch with a commit. Stage explicit paths only.
- No Chinese in reports.
- Product-honesty policy: no fake previews; preflight shows real state; no misattributed errors; logs must show where they end.
- Do not probe `solar <cmd> --help` (it can run the command). Do not write to real settings for security tests.
- Model-backed tasks spend the owner's quota; only submit them when asked.
- Screenshots: app window only.
- Measurement traps:
  - From PowerShell, `$` variables get lost on the way to `wsl.exe`; use Git Bash with `MSYS2_ARG_CONV_EXCL='*' wsl.exe -d Ubuntu-24.04 -- bash -s <<'EOF'`.
  - In Git Bash, `python` is the Windows Store stub.
  - The dashboard port moves.
  - Same-page hash navigation keeps page state; use a fresh browser context per case.
