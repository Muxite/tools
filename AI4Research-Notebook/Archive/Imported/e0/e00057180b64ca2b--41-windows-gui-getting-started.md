# 41 — Testing the Windows GUI: what exists, what this machine has, how to start

Written 2026-09-16 on the Huawei Windows machine (`C:\Users\m50066326`), against checkout
`C:\Users\m50066326\huawei\stellven\AI4Research`, branch `openJiuwen-Solar`, HEAD `b0bf165f9`.

**Status: the work was carried out.** §§1-6 are the original reconnaissance and plan; everything
from §7 onward is what actually happened — the runtime is installed, `Solar.exe` is built, the
dashboard runs, and ten defects are recorded with reproductions. One product change was made
(§18 Defect 4 / branch `fix/a11y-gate-windows-python`, commit `cdc1e7a56`).

**Report:** https://claude.ai/artifact/Fb1A6UT6DDUwi48r9d6mhf — the English, workbook-shaped write-up
for the supervisor and co-op students: what was done and why, how the components fit together, a
feature matrix using the Phase 22 verdict vocabulary, per-defect reproduction steps (R-01 … R-10),
and the can/must and one-to-many ambiguities that make two readers score the same row differently.
This note is the working record behind it; the report is the shareable artifact.

⚠ This note is new in tundle and not yet released — run `tools/tundle.sh release "..."` to version it.

## 0. Where the notes actually are on this machine

`OneDrive - UBC\reading` **does not exist here.** `HKCU:\Software\Microsoft\OneDrive\Accounts`
lists a `Business1` account but with an empty `UserFolder`, `$env:OneDriveCommercial` is empty,
and `C:\Users\m50066326\OneDrive` holds nothing but `desktop.ini`. The UBC tenant is not synced
on this box.

The notes are in the tundle instead: `C:\Users\m50066326\Downloads\tundle\ai4research\notes\`
(tundle `VERSION` = `2026.09.15.1`), which mirrors the work machine's `report-writing-set/`.
That is the copy this note joins.

## 1. There is no native Windows GUI

Native (non-WSL) Windows is **explicitly out of scope** — `docs/WINDOWS.md` and `USER-GUIDE.md` §8
both say so. Two GUI surfaces exist, and they are the same UI:

| Surface | What it is | Needs |
|---|---|---|
| **Browser dashboard** | `harness/status-server/` serves a React app, **already built** into `static/p0-app/` (`index.html` + `assets/index-*.js`, title "AI4Research"). `status-server.py` binds `127.0.0.1:8765` on mac/Linux, `0.0.0.0` under WSL so the Windows host can reach it; falls back through 8765-8775. | Runtime installed in WSL. **No Node on Windows.** |
| **Electron shell** (`Solar.exe`) | `desktop/` — a native window that spawns/attaches that same backend and renders the same dashboard. `desktop/package.json` `build:win` → `electron-builder --win portable`. Unsigned, so SmartScreen warns once (`desktop/docs/DOWNLOAD.md`). | Node `^20.19 || >=22.12` **on Windows** to build. No prebuilt exe ships in the repo. |

So the dashboard is reachable **without building anything**. The Electron shell is a second,
optional step. `scripts/Start-Solar-Local.ps1` is a dev helper that assumes
`desktop\dist\win-unpacked\Solar.exe` already exists and a distro literally named `SolarUbuntu`;
it is not a getting-started path.

## 2. State of this machine [verified 2026-09-16]

| Thing | State |
|---|---|
| WSL | version 2.7.14.0, kernel 6.18.33.2-2, WSLg present — **the platform works** |
| Distros | **only `docker-desktop` (Stopped, v2)**. No Ubuntu. |
| Node / npm / bun | **none installed** anywhere on Windows |
| Python (Windows) | not installed (Store alias stub only) |
| Git | `C:\Program Files\Git\cmd\git.exe` |
| Docker Desktop | installed |
| Disk C: | 218 GB free |
| RAM / CPU | 15.7 GB, i7-1260P |
| `~/.solar/` | does not exist — Solar has never been installed here |

## 3. The thing that will bite: the Docker distro doesn't count

Both `install.ps1` (`Test-SolarDistroName`) and `desktop/src/runtime-detect.js`
(`INTERNAL_WSL_DISTRO`) deliberately exclude `docker-desktop` / `docker-desktop-data` — they are
implementation distros, never install targets. `Test-WslReady` requires `wsl --status` to succeed
**and** at least one non-Docker distro to be registered.

With only `docker-desktop` present, `install.ps1` therefore takes the `Install-Wsl` branch:
self-elevate → `wsl --install -d Ubuntu-24.04 --no-launch` → copy itself to
`%ProgramData%\OpenSolar` → write an `HKLM` RunOnce → **demand a reboot**.

That reboot is almost certainly unnecessary here: WSL2 is already functional (Docker's v2 distro
proves the platform features are enabled). The reboot exists for machines where `wsl --install`
has to turn the Windows features on.

**Avoid it by installing the distro first**, then running the installer, which then takes the
"WSL present" branch and never reboots:

```powershell
wsl --install -d Ubuntu-24.04        # creates the distro; set a UNIX user + password
wsl -d Ubuntu-24.04 -- echo ok       # confirm it boots
```

## 4. What `install.ps1` will do to this machine

Read before running — three of these change machine state beyond Solar:

1. **`Set-WslMirroredNetworking`** — if `%USERPROFILE%\.wslconfig` is absent it **writes
   `networkingMode=mirrored` and runs `wsl --shutdown`**. That kills running Docker containers,
   and mirrored mode changes Docker's networking. It refuses to override an *existing* explicit
   `networkingMode`. ⚠ **Decide this before running.** Pre-writing a `.wslconfig` with
   `networkingMode=nat` keeps Docker's behavior; the runtime then uses its `0.0.0.0` fallback,
   which per `README.md` forces the API token on — do not expose that port.
2. **`Enable-WindowsAutostart`** — registers a per-user logon task that brings WSL up and starts
   the status-server at login (`desktop/runtime/install-windows-autostart.ps1`).
   `uninstall-windows-autostart.ps1` reverses it.
3. **Default flags** (`Get-ForwardString`): if you pass none, it appends
   `--components kernel,harness,status-daemon --yes --bootstrap-system-deps`. The
   `status-daemon` is required on Windows — a backgrounded runtime dies when `wsl.exe` returns.
   It also `apt-get install`s `git curl ca-certificates python3 python3-venv python3-pip tmux jq`
   and enables systemd in `/etc/wsl.conf` (another `wsl --shutdown`).

It prefers the **bundled `get-solar.sh` sitting next to it** — which in this checkout is the repo's
own `get-solar.sh` — over the network. Only if that can't be mapped does it fall back to
`https://raw.githubusercontent.com/suraj-subrahmanyan/OpenSolar/v1.0.0-rc.9/get-solar.sh`. Running
it from the checkout root therefore installs **this tree's release**, not upstream's.

Everything is transcripted to `%LOCALAPPDATA%\Solar\setup.log`.

## 5. Plan (in order, each stage verifiable)

```powershell
# Stage 0 — distro, so the installer skips the reboot branch
wsl --install -d Ubuntu-24.04

# Stage 0.5 — decide .wslconfig BEFORE the installer writes one (see §4.1)

# Stage 1 — install the runtime inside WSL (from the checkout, so get-solar.sh is bundled)
cd C:\Users\m50066326\huawei\stellven\AI4Research
.\install.ps1 --components kernel,harness,status-daemon

# Stage 2 — verify
wsl -d Ubuntu-24.04 -- ~/.solar/bin/solar doctor --json      # expect verdict ok
wsl -d Ubuntu-24.04 -- ~/.solar/bin/solar status
```

Then the GUI:

```powershell
# port the runtime actually chose (8765 unless taken)
wsl -d Ubuntu-24.04 -- bash -lc "cat ~/.solar/harness/run/status-server.port"
# open http://localhost:<port> in a Windows browser  ← this is the AI4Research GUI
```

Optional Electron shell afterwards (needs Node 20.19+/22.12+ **on Windows**; tundle ships no Node
installer — `winget install OpenJS.NodeJS.LTS`):

```powershell
cd desktop; npm install; npm run build:win     # -> desktop\dist\...\Solar.exe (portable, unsigned)
```

If anything goes wrong: `powershell -ExecutionPolicy Bypass -File scripts\windows-evidence-doctor.ps1`
— read-only, reports WSL state, distro user, networking mode, in-WSL prerequisites, and
Windows↔WSL reachability.

## 6. Expectations to keep honest

- `docs/WINDOWS.md` marks the WSL2 path **experimental**: gated by deterministic tests, but
  "full first-run verification on real Windows hardware is owner-manual." This machine is exactly
  that test. Whatever happens is a real data point — record it here.
- The dashboard being reachable is **not** an end-to-end pass. Per `04-gotchas.md` #5 and #15, a
  submit receipt is not execution success and the last full E2E never reached the Scheduler.
  Running work through the GUI needs an authenticated model CLI (`claude` or `codex`) **inside
  WSL** — `solar harness preflight` lists it as required.
- `~/.solar/harness/` is the installed runtime; the checkout under `huawei/` is source
  (`04-gotchas.md` #4). Editing the repo will not change what the GUI runs.
- `docs/FIRST-SESSION.md` is the walkthrough for what to do once it's up (doctor → preflight →
  `solar harness start <project>` → `intake`).

## 7. What was actually run, and what it proved [2026-09-16]

Stage 0 done: `wsl --install -d Ubuntu-24.04 --no-launch` registered the distro (no reboot needed —
WSL2 was already functional, as Docker's v2 distro proved). `--no-launch` skips OOBE, so the default
user was **root**; a normal user `muk` was created with passwordless sudo (required: `install.ps1`
runs `sudo apt-get` through `wsl.exe` with no tty, so a password prompt would hang), and
`/etc/wsl.conf` was pre-written with `[user] default=muk` and `[boot] systemd=true`.

**The GUI serves from the checkout with no install at all.** Running
`python3 harness/lib/symphony/status-server.py` with `HARNESS_DIR` set to the repo's `harness/`
(exactly what `desktop/verify.js` does) gave `/healthz` → 200 and the built dashboard HTML at
`/static/p0-app/index.html` → 200. `status-server.py` is **pure stdlib** — the only `import mermaid`
is inside a JavaScript template string, not Python. `harness/run/` is gitignored, so this leaves the
worktree clean (`git status` empty afterwards).

**Networking, measured.** Under NAT with no `.wslconfig`, the Windows host reached the WSL server on
**both** `127.0.0.1:<port>` and the WSL IP — `healthz` 200 both ways. But `/` returned **403** from
Windows, because `_default_bind_host()` picks `0.0.0.0` under NAT, and `TOKEN_ENFORCED` is
`BIND_HOST not in ("127.0.0.1","::1","localhost")`. Under **mirrored** mode the bind becomes
`127.0.0.1`, the token is still issued and injected into the dashboard HTML
(`window.__SOLAR_TOKEN__`) but **not enforced** — so the browser GUI works normally. Mirrored is
therefore the right choice for GUI testing, not merely a preference. Escape hatches if NAT is kept:
`SOLAR_REQUIRE_TOKEN=0`, or pass the token as `?token=` / `X-Solar-Token` (both accepted by
`_client_token`). Static assets and `/healthz` are exempt; the dashboard HTML deliberately is **not**.

## 8. Three defects found on the documented Windows path

All three are in the shipped tree at `b0bf165f9`, and all three are on the path a new Windows user
follows. Together they mean **`install.ps1` cannot currently succeed on this machine.**

1. **The documented quick-start command cannot work.** `docs/WINDOWS.md` and `USER-GUIDE.md` §8 say
   to run `./install.ps1 --yes --components kernel,harness`. `install.ps1` declares `-Distro`,
   `-BootstrapUrl`, `-RepoUrl` as positional `[string]`s, so unnamed args bind to those first, and
   the comma in `kernel,harness` makes PowerShell build an **array**, which cannot convert to
   `[string]`. Verified: `Cannot process argument transformation on parameter 'RepoUrl'`. The
   working form is `.\install.ps1 -ForwardArgs @('--yes','--components','kernel,harness')`.
2. **`Install-WslPrerequisite` is malformed.** Its `$sh` string contains an inner double-quoted
   `echo "[solar] non-apt distro; skipping prerequisite install (installer will report any gaps)"`
   nested inside the outer double-quoted command. The quoting collapses and bash reports
   ``syntax error near unexpected token `('``, exit 2, which the script turns into a fatal throw.
   It runs **unconditionally before everything else**, so it fails even when every prerequisite is
   already present — `install.ps1` is unusable on any apt distro until this is fixed.
3. **`scripts\windows-evidence-doctor.ps1` always reports `prereqs_missing : (none)`.** Ground truth
   on this box was `jq`, `pip3` and `sqlite3` missing, and the installer's own dry-run agreed it
   would install `jq`; the doctor still said `(none)`, twice. Its prereq loop returns zero output
   when passed through the PowerShell→`wsl.exe` argument boundary (the same loop works correctly
   when fed via `bash -s` on stdin); an empty `$b` makes `command -v` exit 0 on every iteration, so
   nothing is ever reported. **Do not trust that line** — it is the one line a bug reporter would
   quote. Every other field it printed was accurate.

Also worth noting: `install.ps1 --dry-run` is **not** dry. `Install-WslPrerequisite`,
`Set-WslMirroredNetworking` and `Enable-WindowsAutostart` all run before `Invoke-LinuxInstaller`, so
the apt install, the `.wslconfig` rewrite and the `wsl --shutdown` happen regardless. The notes' rule
"always review the installer dry-run first" has to be applied at `install.sh`, not `install.ps1`.
Driven there (`bash install.sh --dry-run --yes --components kernel,harness,status-daemon`) the
dry-run is honest and readable, and correctly reported the missing `jq`.

## 9. Open, for the next session

- Whether to file/fix the three defects in §8, or just record them. They are real and reproducible.
- Whether to build `Solar.exe` at all, or stay on the browser dashboard for the test.
- The Phase 22 L2 test matrix (`Downloads\AI4RnD Brief Feature Test Report.xlsx`, 142 items:
  26 PASS, 66 PASS_WITH_KNOWN_LIMITATIONS, 22 IMPLEMENTED_AND_FAIL, 28 NOT_AVAILABLE) is the
  register of what to exercise. Not yet mapped onto what the GUI can actually reach.
## 10. The runtime is installed and the GUI is up [2026-09-16]

`install.ps1` was bypassed (§8.2 makes it unusable) and its steps were done by hand, in its own order:

1. `apt-get install git curl ca-certificates python3 python3-venv python3-pip tmux jq sqlite3` — the
   step that fails inside `Install-WslPrerequisite`.
2. `%USERPROFILE%\.wslconfig` written with `[wsl2] networkingMode=mirrored`, then `wsl --shutdown`.
   Confirmed after restart: `wslinfo --networking-mode` → `mirrored`. Docker was not running, so the
   shutdown cost nothing.
3. `bash install.sh --yes --components kernel,harness,status-daemon --bootstrap-system-deps`, run
   **from the checkout** — deliberately not the bundled `get-solar.sh`, which clones upstream
   `v1.0.0-rc.9` from GitHub instead of testing this tree. Exit 0.

Result: `solar doctor` → **Verdict: ok** (python3 3.12.3, yaml/jsonschema/pydantic/rich, tmux, jq,
bash>=4 all ok). Layout is the documented one: `~/.solar`, `~/.solar/harness`, `~/.solar/bin`,
`~/.claude/solar`. The `status-daemon` systemd user unit is **enabled and running**.

**The dashboard is reachable from Windows at `http://127.0.0.1:8765/` — HTTP 200.** Under mirrored
mode `BIND_HOST` is `127.0.0.1`, so the token is issued but not enforced and the browser needs no
header. This is the GUI.

Two reporting inconsistencies seen at first light, both cosmetic but confusing:

- `solar status` prints `Daemon | component: not-installed | detail: core-runtime/daemons component
  not installed` even though `components: kernel,harness,status-daemon` and the status-server unit
  is enabled and serving. That Daemon section tracks the **`daemons`** component, not
  `status-daemon`; read it as "no core-runtime daemon", not "no status server".
- `version: 1.0.0-rc.8-583-gb0bf165f9` while `channel: v1.0.0-rc.9` and root `VERSION` says
  `1.0.0-rc.9`. The git-describe version trails the declared release.

Known gap, not a defect: `runtime CLI/auth: missing/unauthenticated`. The selected pane runtime is
**codex**, and no `codex` (or `claude`) CLI exists inside WSL, so panes cannot launch yet. Windows
has `claude.exe` 2.1.273 but that is the **Windows** binary and does not satisfy the WSL preflight.
Per `04-gotchas.md` #5/#15, nothing end-to-end can be claimed until that is resolved.

## 11. `Solar.exe` builds — the "Windows App" verdict is stale [2026-09-16, verified]

With Node v24.19.0 / npm 11.17.0 on Windows (`winget install OpenJS.NodeJS.LTS`), in `desktop/`:

```powershell
npm install --no-audit --no-fund
npm run build:win
```

Exit 0. Produced, with electron-builder 26.15.3 / electron 42.6.1, win32 x64:

| Artifact | Size |
|---|---|
| `desktop\dist\Solar 1.0.0-rc.9.exe` (portable) | 95,336,391 B |
| `desktop\dist\win-unpacked\Solar.exe` | 232,713,728 B |

The pipeline ran clean end to end: `build-renderer` → 4 assets + `index.html`; `prepackage-check`
→ "harness contains no symlinks"; `prepare-package-resources` → `.packaging/harness`; then
`@electron/rebuild`, packaging, asar integrity, and signtool (self-signed, so SmartScreen will still
warn — expected per `desktop/docs/DOWNLOAD.md`).

This directly contradicts the Phase 22 row `Installer & CLI & Webapp / 1. Windows App` =
**NOT_AVAILABLE**, "This feature is not implemented in the current product, so it could not be
tested." It **is** implemented and it **does** build. The defensible verdict is not NOT_AVAILABLE;
it is "implemented, builds, and needs its runtime path exercised" — subject to §12.

## 12. Why the Windows dashboard keeps disappearing [root cause proven]

Symptom: the dashboard answers 200 from Windows, then becomes unreachable (`curl` exit 7, code 000)
within ~25-45 s.

Ruled out, each by direct observation:

- **Not linger.** `loginctl show-user muk` printed `State=lingering / Linger=yes` *before* any fix
  was applied — `components.d/status-daemon/component.sh:54` already runs `enable-linger`.
- **Not a dead service.** `systemctl --user is-active solar-status-server.service` → `active`, with
  `status-server.py` alive as PID 308, at the moment the host could not reach it.
- **Not the idle timeout.** `[wsl2] vmIdleTimeout=86400000` (24 h) in `.wslconfig` + `wsl --shutdown`
  changed nothing: still "no running distributions" and 000 at t+45 s.
- **Not the failed prewarm.** The prewarm does fail (§13), but the status-server was running anyway.

**Proven cause:** WSL2 terminates the VM once no `wsl.exe` session is attached. A background
process, an active systemd user unit and linger do **not** hold it open. Control test: launching
`wsl.exe -d Ubuntu-24.04 -- sleep 3600` hidden and detached kept `wsl -l --running` reporting
`Ubuntu-24.04`, and the dashboard answered **200 at t+50 s**.

**Consequence for the product:** `desktop/runtime/start-solar-wsl.vbs` calls
`sh.Run(..., 0, False)` — asynchronous, returns immediately — so it never holds a session. The
logon task therefore cannot keep the dashboard alive, and it only fires at logon anyway. Note this
step never runs on a normal install regardless, because `install.ps1` dies at §8.2 first.

Caveat for anyone re-testing: the dashboard HTML at `/` is a **559-byte SPA bootstrap** that
contains `window.__SOLAR_TOKEN__` but none of the UI text. Asserting "What do you want done?" or
"Settings" against raw HTML will always fail; the UI is client-rendered, which is why
`desktop/verify.js` drives a real browser instead.

## 13. Two corrections, recorded so they are not re-derived

**The status-server port is not stable.** After a VM teardown and restart the service came back on
**8766**, not 8765 (`ss -ltnp` → `127.0.0.1:8766 python3 pid=626`; `run/status-server.port` → `8766`).
A host-side check hardcoding 8765 will report a false "dashboard down". Always read
`~/.solar/harness/run/status-server.port` first — `Start-Solar-Local.ps1` and the desktop app both do.
`status-server.py` falls back through 8765-8775 when the primary is taken.

This means one earlier "unreachable" reading was a **port change, not a teardown**. The §12 teardown
finding is unaffected: that test recorded `wsl -l --running` → "There are no running distributions"
*together with* a 000 response, which the port explanation cannot account for.

**Do not screenshot the full screen to evidence the GUI.** It captures whatever the operator has in
front of them, not the app, and on a machine in use that is both useless as evidence and a privacy
problem. Use `desktop/verify.js`, which drives headless chromium against an isolated `HARNESS_DIR`
and writes `gate-dashboard.png`.

## 14. Faking a runtime-CLI pass for prewarm [verified]

There is **no first-class mock** for a codex/claude pass. There are three seams, in decreasing
honesty:

1. **`SOLAR_CODEX_BIN` / `SOLAR_CLAUDE_BIN`** (`solar-harness.sh:556-566`). `pane_runtime_cli_path()`
   prefers these over `command -v`, and validates only with `[[ -x "$c" ]]` — no version probe, no
   auth check. An executable stub at that path satisfies the preflight gate at
   `solar-harness.sh:797-803`. This is the seam to use for exercising launch plumbing without a
   real CLI.

   Verified on this machine, `solar harness preflight`, same command twice:

   ```
   BEFORE:  required fail: codex runtime CLI not found
            preflight failed: 1 required launch check(s) failed

   AFTER:   required ok: codex path=/home/muk/.solar-test/bin/codex
            manual-pending: live codex pane behavior is not verified by preflight; ...
   ```

   The stub was a 43-byte `#!/bin/bash; echo "codex-stub 0.0.0"; exit 0` at
   `~/.solar-test/bin/codex`, `chmod +x`, with `SOLAR_CODEX_BIN` pointing at it. Nothing else
   changed, and no repo file was touched. Note the gate's own wording concedes the limit:
   "live codex pane behavior is not verified by preflight".
2. **`DISPATCH_MOCK`** (`coordinator.sh:2056-2065`) short-circuits dispatch, appending
   `attempted`/`acked` ledger entries with `{"dry_run":true}`. Dispatch-level, not preflight.
3. **`--skip-llm-cli` / `--fake-keys`** — installer flags only, documented in
   `harness/docker/smoke-test.sh:8-9`. They affect install-time checks, not launch preflight.

There is **no** env var that skips the preflight CLI check itself; the only skip in
`solar-harness.sh` is `SOLAR_SKIP_DOCTOR` (set by `--skip-doctor`), which skips **doctor**, not
preflight.

⚠ A stubbed pass proves the launch path, and nothing else. `04-gotchas.md` #5 and #6 apply directly:
a submit receipt is not execution success, and a mode that cuts real model calls cannot be cited as
evidence of quality. Anything exercised this way must be labelled as stub-backed in the report, and
must never be recorded as PASS for a feature whose success condition requires real model work.

## 15. Gates run on Windows [evidence]

Toolchain used: Node v24.19.0, npm 11.17.0 (`winget OpenJS.NodeJS.LTS`), Python 3.12.10
(`winget Python.Python.3.12`, at `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`).

**`desktop/contract.js` — CONTRACT PASS, exit 0.** The backend-contract gate spawns its own
status-server on an isolated `HARNESS_DIR` and asserts the HTTP contract the desktop shell depends
on. All seven assertions passed:

```
PASS  GET /healthz == 200
PASS  OPTIONS /status == 204 (CORS preflight, was 501)
PASS  OPTIONS sends Access-Control-Allow-Origin
PASS  HEAD /status == 200 (was 501)
PASS  GET /runtime-info == 200
PASS  GET /auth/status == 200
PASS  /auth/status leaks no token-shaped value
```

Worth noting against the "native Windows is out of scope" line in `docs/WINDOWS.md`: this gate ran
**entirely on Windows**, and `status-server.py` started under **native Windows Python** — no WSL
involved. `verify.js` and `contract.js` both default `PYTHON` to `python` on `win32`, so the repo
clearly intends the status-server to run natively for gate purposes. "Out of scope" applies to the
harness/runtime, not to the status-server process.

**`desktop/verify.js` — could not run at first attempt.** It started its backend fine
(`backend=http://127.0.0.1:8765/`) but failed with
`browserType.launch: Executable doesn't exist ... chrome-headless-shell.exe` — Playwright's browser
binary is not downloaded by `npm install`. `npx playwright install chromium` is a required extra
step before any visual/accessibility gate. Record this as a prerequisite, not a product defect.

## 16. The Windows GUI path, proven end to end [2026-09-16]

**`desktop/verify.js` — GATE PASS, exit 0.** Headless chromium against an isolated backend:

```
backend=http://127.0.0.1:8765/ asserted=[What do you want done?, Settings] of [What do you want done?, Settings]
GATE PASS
```

Both required UI strings were found **in the rendered DOM**, not in raw HTML (§13 explains why that
distinction matters). Screenshot written to `desktop/gate-dashboard.png`, 64,333 bytes.

**`npx electron .` with `SOLAR_DESKTOP_SELFTEST=1` — SELFTEST OK, exit 0.** The packaged shell's own
verdict, in order:

```
[solar-desktop] attached to already-running runtime http://127.0.0.1:8766/
[solar-desktop] Windows runtime prewarm ready
[solar-desktop] loading runtime dashboard: http://127.0.0.1:8766/
[solar-desktop] LOADED http://127.0.0.1:8766/
[solar-desktop] SELFTEST OK {"verdict":{"ok":true,"reasons":[],
  "expectedOrigin":"http://127.0.0.1:8766","actualOrigin":"http://127.0.0.1:8766",
  "readyState":"complete","rootChildCount":1,"bodyTextLength":344,
  "matchedContract":"dashboard","targetMarkers":{"homeLanding":true,
  "taskInputAccessibleName":"What do you want done?"},
  "rendererErrors":[],"fallbackUsed":false}}
```

So the whole Windows chain works: **build → launch → attach to the WSL runtime on the right port →
prewarm → load → render the home landing**, with no renderer errors and no fallback.

⚠ **STUB CONTAMINATION — read before citing any later PASS.** The selftest only reaches OK because a
**stub** `codex` sits at `~/.local/bin/codex` inside WSL (§14). Without it the same command gives
`SELFTEST FAIL {"reason":"runtime_dependency_check_failed","failures":["runtime-prewarm"]}`. Both
runs are recorded above and the only difference is the stub. What is proven is the **launch and
render plumbing**; nothing about real model work is proven, and no feature whose success condition
needs a real model may be marked PASS from this. Remove it with
`rm ~/.local/bin/codex ~/.solar-test/bin/codex` before any run that must be stub-free.

Other Windows gate results, same toolchain:

| Gate | Result |
|---|---|
| `desktop/contract.js` | **PASS** (7/7, §15) |
| `desktop/verify.js` | **PASS** |
| `desktop/runtime-sync.test.cjs` | PASS |
| `desktop/package-private-state.test.cjs` | PASS |
| `desktop/safe-output.test.js` | PASS |
| 7 × `tests/harness/status_server/react_app/*.mjs` | **all PASS** — intake-api retry, nodeActor (19 cases), planNodeLabel, pocPreview, runPipeline, runUsage, statusColors (5.95:1 on white) |
| `desktop/accessibility.test.js` | **did not run** — root cause found, see below. A startup failure, **not** an accessibility verdict. |

### Defect 4: `accessibility.test.js` cannot run on Windows [verified]

The gate fails with `status server did not become healthy` (`accessibility.test.js:49`) because it
spawns the backend with a **hardcoded `"python3"`** at `accessibility.test.js:64`, while its two
sibling gates resolve the interpreter per platform:

```
verify.js:9-10        process.env.PYTHON || (process.platform === "win32" ? "python" : "python3")
contract.js:19-21     process.env.SOLAR_PYTHON || (process.platform === "win32" ? "python" : "python3")
accessibility.test.js:64   spawn("python3", [statusServer], { ... })      <-- no win32 branch
```

On Windows `python3` resolves to
`%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe`, the Microsoft Store **alias stub**, which prints
"Python was not found..." and exits without starting anything — so `waitForPort` can only ever time
out. Nothing about accessibility is being measured. It is a one-line inconsistency, not an a11y bug.

⚠ **PATH hazard worth knowing.** In a shell that has not picked up the installer's PATH update,
*both* `python` and `python3` resolve to the WindowsApps stubs. The real interpreter is
`%LOCALAPPDATA%\Programs\Python\Python312\python.exe`. `verify.js` and `contract.js` passed because
their shells had the refreshed PATH, where the real `python` precedes the alias. When reproducing
any of this, check `(Get-Command python).Source` first.

**Fixed, on branch `fix/a11y-gate-windows-python`** (branched from `openJiuwen-Solar` @ `b0bf165f9`;
one file, `desktop/accessibility.test.js`, staged by explicit path):

```diff
-  const backend = spawn("python3", [statusServer], {
+  const python =
+    process.env.PYTHON || (process.platform === "win32" ? "python" : "python3");
+  const backend = spawn(python, [statusServer], {
```

Result — the gate now runs and **passes** on Windows:

```
ACCESSIBILITY AUDIT PASS (axe serious/critical 0 + keyboard focus reachable)   exit 0
  violations: []        incomplete: []
  keyboard: "New task" button focus_visible, Enter opens dialog, Escape closes,
            focus_restored_to_trigger: true
  accessible name: textbox "What do you want done?" via aria-labelledby=home-task-heading
```

No behavior change off Windows: the non-`win32` branch is still `python3`, and `PYTHON` still
overrides. This is the one verdict in these notes that moved because of a code change, and it has
its own commit so the before/after is traceable without re-deriving it.

## 17. Dashboard routes and error screens, exercised [evidence]

Driven with Playwright against the **live WSL runtime** (port 8766), `waitUntil: "domcontentloaded"`.
⚠ Do **not** use `networkidle`: the dashboard polls continuously, so network idle never arrives and
navigation times out. That is a test-harness trap, not a product defect — `verify.js` avoids it.

| Route | Result |
|---|---|
| `/#/` | Home landing, 357 chars. Controls: `New task`, `Attach files`, `Crew`, `Start work`. Text: "AI4Research Multi-agent runtime", "SESSIONS / No sessions yet", "Settings", "What do you want done?", "Describe a task. AI4Research routes it through PM, Planner, Builder, and Evaluator agents — and tells you plainly when it stalls.", "Starts a real intake via the existing CLI". |
| `/#/settings` | Settings, 700 chars. Tabs: **Credentials, Default crew, Usage & limits, Activity, About**. Controls: `Reload`, `Save` ×4, `Save configuration`. Notice: "Saves update the local config and local secrets only; restart the cockpit to apply changes to running panes. Provider keys are stored only on this m…" |
| `/#/garbage-not-a-route` | **Redirects to `/#/`** — unknown-route fallback confirmed. |

`pageErrors=[]` across all three. Session views could not be exercised: "No sessions yet", and
creating one needs a real run (§14 caveat).

**Error-screen taxonomy**, from `SOLAR_DESKTOP_SELFTEST=1` with `SOLAR_BACKEND_URL` pointed at bad
backends. Three distinct verdicts observed so far:

| Induced condition | Verdict |
|---|---|
| No runtime CLI (stub removed) | `SELFTEST FAIL {"reason":"runtime_dependency_check_failed","failures":["runtime-prewarm"]}` |
| Backend on a Chromium-blocked port (`:9`) | `FAIL-LOAD -312 ERR_UNSAFE_PORT` → `{"reason":"runtime_dashboard_load_failed","code":-312}` |
| Backend on a legal dead port (`:59999`) | `FAIL-LOAD -102 ERR_CONNECTION_REFUSED` → `{"reason":"runtime_dashboard_load_failed","code":-102}` |
| Healthy runtime + stub CLI | `SELFTEST OK` (§16) |

So load failures collapse to one `reason` and are distinguished by Chromium's `code`/`description`.
Note that in **attach mode** (`SOLAR_BACKEND_URL` set) the shell still runs and reports "Windows
runtime prewarm ready" before attempting the load — attach does not skip prewarm.

Not exercised on Windows: the application menu and **Help → Copy diagnostics**. Electron menus are
not reachable from Playwright, so this needs a human click or a dedicated harness. Record it as
untested, not as passing.

Two further route facts, both confirmed against the live runtime:

- **`GET /sessions/<sid>` 302-redirects to the hash route.** Verified:
  `status=302 redirect=http://127.0.0.1:8766/#/sessions/test-abc-123`. So deep links from outside
  the SPA resolve correctly.
- **`/runtime-info` proves which runtime the GUI is bound to:**
  `{"ok":true,"pid":626,"port":8766,"bind_host":"127.0.0.1","python":"/usr/bin/python3","harness_dir":"/home/muk/.solar/harness"}`.
  `bind_host` `127.0.0.1` is the mirrored-mode path from §7, and `harness_dir` is the **WSL** install —
  useful when you need to prove the Windows browser is talking to the WSL runtime and not a stray
  Windows-side server spawned by a gate. `/auth/status` and `/status` both return 200.

## 18. CLI surface: `--help` is not safe on every verb [verified]

Run inside WSL against the installed runtime. Two defects and one trap.

**Defect 5 — `solar update --help` starts updating instead of printing help.** It printed
`fetching https://github.com/suraj-subrahmanyan/OpenSolar.git (channel: v1.0.0-rc.9) updating
b0bf165f9 -> fd15…` — a network fetch plus an in-place runtime update, from a `--help` invocation.
A user typing `--help` to find out what a command does should never mutate their install.

Impact here, checked rather than assumed: the installed runtime was **not** swapped. `solar status`
still reports `version: 1.0.0-rc.8-583-gb0bf165f9`, `git: b0bf165f9`, the receipt still carries its
original 09:56:36 timestamp, and the status-server is still the same process (PID 626) used for
every measurement above. What *did* happen is a clone of upstream into `~/.solar-src/OpenSolar` at
HEAD `fd15753`. The update appears to have been cut short only because the command was piped into
`head`, which closed the pipe. Do not read this as "update is harmless" — read it as "the guard is
luck, not design".

**Defect 6 — `solar uninstall --help` is rejected**: `unknown uninstall option: --help`. Every other
listed verb accepts it in some form; this one errors on its own documented flag.

**Trap — several verbs silently ignore `--help` and run the command.** `solar harness status --help`
printed live harness status; `solar doctor --help` ran the doctor; `solar harness intake --help`
printed usage in Chinese. This is the likely substance behind the Phase 22 note on
`UI / 1. CLI` ("some secondary help commands still failed on Windows"), though what is observable
here is broader than "failed": some of them *execute*.

⚠ **Methodology correction, recorded so no one re-derives a wrong number.** My first pass captured
`$?` after piping each command into `head`, so the exit codes measured `head`, not `solar`. Those
values are meaningless and are **not** reported here. Only the printed output above is evidence. Any
future CLI exit-code claim must capture `${PIPESTATUS[0]}` or avoid the pipe entirely.

For reference, `solar --help` itself works and lists the full verb set: `version, status, doctor,
update, repair, backup, restore, identity, privacy, channel, advanced, ui, harness, uninstall,
components`. Note `solar identity` and `solar privacy` exist as CLI verbs — relevant to the Phase 22
`Account management` rows recorded as NOT_AVAILABLE, which deserve their own re-check.

## 19. The TUI opens on Windows — Phase 22's FAIL is not reproduced [verified]

Phase 22 records `UI / 3. TUI` as **FAIL**: *"The interactive terminal interface did not open on
Windows because it uses an unsupported signal."* On this machine it opens and renders.

`solar harness monitor tui` → rc 0, `monitor tui 已在独立窗口打开`. The session is real:

```
solar-harness: 2 windows (created Wed Sep 16 10:12:32 2026)
  0: Product Delivery- (4 panes)
  1: monitor* (1 panes) (active)
```

`tmux capture-pane` on window 1 returns a live, populated interface — a "当前无 Sprint" empty state
with suggested next actions, coordinator status, recent dispatch, and a shortcut menu
(`n) 新建 Sprint   s) 查看全局状态   r) 刷新   l) 调度日志   c) 查看检查点   q) 退出   k) 关闭 Harness   w) Webhook 管理`).
Separately `solar ui --once --no-color` (a different surface — "Solar UI-lite", self-described as
"deterministic local dashboard; not live Codex behavior") also ran clean at rc 0.

**Three caveats, all of which a reviewer will ask about:**

1. This is **WSL2**, which `docs/WINDOWS.md` defines as *the* Windows runtime path — but it is not
   native Win32. If Phase 22's claim was about a native Win32 console, this does not contradict it.
   The claim as written says "on Windows", and on the supported Windows path it opens.
2. The tmux session exists only because the **stub** CLI (§14) let prewarm build the cockpit. The TUI
   itself needs no model, but its host session was created under stub conditions.
3. The TUI is **Chinese-only**, which matters directly for the English-document goal.

**Bonus defect — the TUI contradicts itself.** The same captured frame shows both
`○ 协调器未运行` ("coordinator not running") and `⚠ coordinator 已在运行 (PID=1470, etime=07:57)`
("coordinator already running"). One frame, two opposite claims about the same process. A live
coordinator was in fact running at PID 1470.

## 20. `Account management` looks stale too — same pattern as Windows App [static evidence]

Phase 22 records three `Account management` rows as **NOT_AVAILABLE**, "This feature is not
implemented in the current product, so it could not be tested":
`1. Account Registration`, `2. Authentication & Session Security`, `3. User Profile Management`
(the third adds "no real user profile feature was found for identity, role, research preferences,
notifications, or accessibility").

The product ships a CLI surface and a 500-line module for exactly these:

| Evidence | Where |
|---|---|
| `solar identity register / login / session / logout / profile get\|set` | `bin/solar:104-108`, dispatched at `bin/solar:1509-1510, 1535` |
| `solar privacy export \| delete \| redact` | `bin/solar:109-110`, dispatched at `bin/solar:1513-1514, 1536` |
| Implementation | `harness/lib/local_identity.py` (500 lines) |
| Module's own summary | "Local-only identity, session, profile, and privacy controls for Solar … with a sandboxable account store, hashed passwords, hashed session tokens, expiry, logout, redacted export, and delete." (`local_identity.py:2-6`) |
| Password hashing | `HASH_ALGORITHM = "pbkdf2_sha256"` (`:26`), `_hash_password` (`:132`), `_verify_password` (`:143`) |
| Session security | `_issue_session` (`:168`), `_token_hash` (`:156`), `_session_for_token` (`:186`), `_purge_expired_sessions` (`:160`) with `expires_at` checks |
| Credential hygiene | `SENSITIVE_KEY_PARTS = ("password","secret","token","credential","api_key","apikey")` (`:33`), `redact_value` (`:207`); token read from **stdin** so it never enters argv (`:116-128`) |
| Dedicated tests exist | `tests/vertical/account_management/test_local_identity_privacy_channel_security.py`, `tests/repairs/identity_privacy_channels/test_identity_privacy_channel_service.py` |
| Uninstall treats it as user data | `SOLAR_DATA_PATHS="install-receipt.json config.env .env db identity"` (`bin/solar:139`), preserved by `--keep-data` (`:1383-1390`) |

So "not implemented" is not supportable as written. The honest distinction is **local-only** identity
(no remote account service, no email verification, no OAuth) versus *absent*. Rows 1 and 2 describe
capabilities that exist in local-only form; row 3's specific claim about profile fields needs
checking against `identity profile set` before it is re-verdicted either way.

**The repo's own tests for this area pass on this machine — `6 passed in 7.36s`, rc 0**, covering
`test_local_identity_privacy_channel_security.py` and `test_identity_privacy_channel_service.py`.
So the capability is not merely present in source; its shipped tests execute and pass here. That
makes NOT_AVAILABLE ("not implemented … could not be tested") untenable for rows 1 and 2: it both
*is* implemented and *can* be tested.

Test-runner note for reproduction: **`pytest` is absent from the WSL runtime**
(`/usr/bin/python3: No module named pytest`) — the installer ships the harness deps but no test
runner. Use a contained venv (`python3 -m venv ~/.solar-test/venv`, then
`pip install pytest -r requirements/harness.txt`, giving pytest 9.1.1) rather than
`pip install --break-system-packages`, since Ubuntu 24.04 is PEP 668 externally-managed.

⚠ **Do not re-check these rows by invoking the CLI.** Defect 5 showed `--help` can execute the verb,
and `solar privacy delete` is destructive. Read the code or run the tests; do not probe with
`--help`.

## 21. Two Windows testing traps that cost real time

**Trap A — `git status` disagrees between Windows and WSL on the same checkout.** Running the repo
from `/mnt/c` under WSL made `git status` report **4,609 modified files**, including every
`.agents/skills/*/SKILL.md`, with diffs showing whole files rewritten. Nothing had been modified.

```
Windows git:  modified: 0      core.filemode=false  core.autocrlf=true
WSL git:      modified: 4609   core.filemode=false  core.autocrlf=(unset)
```

Git stores LF; Windows git checks out CRLF and normalizes it back, so it sees a clean tree. WSL git
has no `autocrlf`, so it compares CRLF working files against an LF index and calls every line
changed. **Always run `git status` from the same side you intend to commit from.** I nearly
"restored" 4,609 untouched files over this. Commit `cdc1e7a56` was verified intact from the Windows
side afterwards.

**Trap B — `tests/vertical/` is partly Windows-only and cannot be judged from WSL.**
`tests/vertical/installer_cli_webapp/test_cli_provider_onboarding_behavior.py:11` hardcodes
`BASH = Path(r"C:\Program Files\Git\bin\bash.exe")` — it deliberately drives the **shipped CLI**
through Git for Windows, with a fake `HOME` and a `python3` shim. Run from inside WSL it dies with
`FileNotFoundError: 'C:\Program Files\Git\bin\bash.exe'`, which says nothing about the product. The
test has no skip guard or fallback for non-Windows hosts, so it fails rather than skipping.

Suite result from WSL: **1 failed, 8 passed, 1 skipped** — but that single failure is this
portability artifact, so the honest reading is 8 passed / 1 skipped / 1 not-applicable-here.

Re-run **from Windows**, where that bash does exist (`Test-Path` → `True`, pytest 9.1.1 on Python
3.12.10), it still fails — but for a different and more interesting reason:
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. Bash was found and the
fixture ran; `solar doctor --json` simply returned nothing parseable. That is a genuine
Windows-path datapoint about the shipped CLI and is being characterized separately — do **not**
record it as either a pass or a product defect until the cause is known.

## 22. Fork lineage — and why the installer points somewhere surprising

Corrected by the owner on 2026-09-16, and it matches the remotes exactly:

```
lisihao/Solar                    the original            -> our `upstream` remote
  └─ Stellven/AI4Research        fork of Solar           -> our `origin` (this repo)
       └─ suraj-subrahmanyan/OpenSolar   fork of AI4Research, by a co-op student
```

So "Solar", "AI4Research" and "OpenSolar" are **three repositories in a fork chain**, not three names
for one repo — while *within* this tree the words are also used as layer names (Solar = runtime/CLI,
`~/.solar`; AI4Research = product/UI title; OpenSolar = contributor-doc and installer identity). Both
things are true at once, which is exactly why the naming reads as inconsistent.

**The consequence is not cosmetic.** `get-solar.sh:22` and `install.ps1:50-51` pin the bootstrap to
`https://github.com/suraj-subrahmanyan/OpenSolar.git` at tag `v1.0.0-rc.9`. So on a stock install the
runtime is fetched from the **downstream co-op fork**, not from `Stellven/AI4Research`. That is what
`solar update --help` (Defect 5) was observed fetching, and it is why installing from the checkout
(`bash install.sh`) rather than via `get-solar.sh` matters if you intend to test *this* tree.

## 23. Why `solar doctor --json` returned nothing on Windows [root cause]

The Windows run of `test_cli_provider_onboarding_behavior.py` failed with
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. Cause, reproduced
directly:

```
$ "/c/Program Files/Git/bin/bash.exe" -lc './bin/solar doctor --json'
Python was not found; run without arguments to install from the Microsoft Store, ...
[rc=49]      stdout bytes=0
```

Git-Bash's `PATH` reaches the **WindowsApps `python` alias stub** before the real interpreter, so the
CLI's Python call dies and `doctor --json` emits **nothing at all** on stdout. Same root hazard as
Defect 4 (§15).

Two separable observations, and they should be recorded as different rows:

1. **Environment:** Git-Bash inherits the alias-stub PATH. Not a product defect.
2. **Product weakness:** a command documented to emit JSON exited **49 with empty stdout** and put its
   only explanation on stderr. Any caller doing `json.loads(stdout)` — including the repo's own test —
   gets an unhelpful decode error instead of the real cause. A contract-bearing `--json` verb should
   emit a JSON error object or fail with a diagnosable message on stdout.

## 24. Defect 7 — the installer pulls from a DOWNSTREAM fork [owner-flagged, verified]

`Stellven/AI4Research` installs its runtime from `suraj-subrahmanyan/OpenSolar`, which is a **fork of
itself** (§22). This is not a naming curiosity; it is a provenance inversion and it should be fixed.

```
get-solar.sh:22     SOLAR_REPO=https://github.com/suraj-subrahmanyan/OpenSolar.git
install.ps1:50-51   -BootstrapUrl https://raw.githubusercontent.com/suraj-subrahmanyan/
                                  OpenSolar/v1.0.0-rc.9/get-solar.sh
                    -RepoUrl      https://github.com/suraj-subrahmanyan/OpenSolar.git
```

Observed, not inferred: `solar update` fetched from that URL and left a clone at
`~/.solar-src/OpenSolar` with `HEAD = fd15753`, while this checkout is `b0bf165f9`. So the runtime a
stock install would have received is a tree this repository did not produce and does not track.

**The round-trip problem (the owner's point).** A change made here does not reach this project's own
users directly. It reaches them only if and when the downstream fork merges it, and it comes back
through that fork — so what ships is whatever the fork owner's tree contains at that moment, not
what was written here. A fix can therefore return altered, bundled with unrelated downstream
commits, or not at all. The upstream cannot ship to its own users without a third party acting, and
cannot be sure that what arrives is what it sent.

**Why this is close to untestable, which is its own cost.** The installed artifact depends on another
repository's state at fetch time, so:

- Two installs a week apart can differ with **zero commits in this repo**, and a bug can appear or
  vanish with nothing here to bisect against.
- `v1.0.0-rc.9` is a **tag in the fork**, and tags are mutable by the fork owner. Pinning a tag in a
  repository you do not control is not a pin.
- Nothing verifies that the fetched tree corresponds to any commit here — no hash check, no
  signature, no comparison against `origin`. Divergence is silent.
- `scripts/check-release-coherence.sh` keeps `VERSION` and the channel in lockstep *within this
  repo*; it cannot detect that the channel points somewhere else entirely.

**Security framing, stated plainly:** every install and every `solar update` executes code fetched
from an account outside this project's control. Whoever holds write access to that fork controls
what installing users run. That is a supply-chain exposure independent of anyone's intent, and it
compounds Defect 5, where `--help` alone was enough to trigger a fetch.

**Suggested fix:** point `SOLAR_REPO` / `-RepoUrl` / `-BootstrapUrl` at `Stellven/AI4Research`, pin a
commit rather than a mutable tag, and have the installer record the resolved commit in
`install-receipt.json` so an install can be traced to a known tree. Until then, install from a
checkout (`bash install.sh ...`), which is what every result in these notes used.

## 25. Web dashboard findings — ALL platforms, not Windows-specific [2026-09-16]

Raised by the owner after using the dashboard at `http://127.0.0.1:8766/`, then driven with Playwright.
The dashboard is the same React bundle on every OS, so none of these are Windows gripes.

**What the owner hit:** typed a task, pressed Start work, got the bare string
`intent_compilation_failed` and nothing else. Two attempts ("what more info do you need",
"who is huawei"), plus two labelled Playwright probes, all failed identically.

**Cause — and a correction.** I first suspected the stub `codex` from §14. **Wrong.** Every attempt
recorded, in `~/.solar/harness/intents/<id>/intent/intent_acceptance.json`:

```
"decision": "failed", "reasons": ["openai transport failed (FileNotFoundError)"]
```

The status-server runs as a systemd user unit whose `PATH` is
`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin`.
The unit file sets no `PATH`. No `codex`, `claude` or `openai` is reachable from it, stub or real.
`/auth/status` agrees: `codex: missing-cli, claude: missing-cli, glm: missing-key`.

### D8 — preflight and intake resolve the model binary differently (the important one)

`solar-harness.sh` preflight (`pane_runtime_cli_path`, :556-566) honours `SOLAR_CODEX_BIN` and probes
`~/.local/bin/codex`. `harness/lib/intent_compiler.py` references neither — it runs bare
`command = ["codex", ...]` (:258) off `PATH`. So **preflight can pass while every intake fails**, which
is exactly what happened: the desktop selftest reported "Windows runtime prewarm ready" (§16) and
dashboard intake still died. Worse, a **real** `codex` installed to `~/.local/bin` — a location
preflight *explicitly checks* — would still fail from the dashboard, because the systemd unit's
`PATH` lacks it. A green preflight is not evidence that intake works. Re-read §16 in that light.

### D9 — the failure reason is recorded, then thrown away twice, and misnamed

- The reason exists on disk (above).
- The server response (`status-server.py:1422-1441`) returns `intent_id`, `returncode: 3`, `command`,
  and only the *path* to `intent_acceptance.json` — never its `reasons`.
- The UI renders `response.error` verbatim (`App.tsx:249`): the literal code, nothing else. It stays
  on `/#/`.
- The recorded reason says **"openai transport"** while the binary actually missing is **`codex`**.
- The response also hands the browser an absolute server path (`/home/muk/.solar/...`).

### D10 — the dashboard accepts tasks it provably cannot run

`AuthGate` (`App.tsx:318-345`) blocks only on exactly `"unauth"` — "Degrade OPEN: only a definite
unauth blocks; detection gaps never trap the user." But `missing-cli` is not a detection gap; it is a
definite negative. With **zero** usable providers the composer renders and accepts work. The desktop
shell has a real pre-dashboard dependency check (§16); **the browser path has none.**

### D11 — the crew picker looks functional and is not

- `MODEL_OPTIONS` is a hardcoded array (`App.tsx:4107`); presets hardcode role models (:4218-4236).
  Availability is never consulted — all six models offered while every provider is unavailable.
- **Where the pre-selection comes from — corrected.** I first claimed the silent fallback
  `role_models?.[role]?.model || MODEL_OPTIONS[0]` (`App.tsx:5126`) produced it. **Wrong for this
  machine:** `GET /settings` returns `role_models` with all four roles = `claude-opus-4.x`
  (alias `opus`, source `solar-user-config.json`), so the fallback never fired. The fallback does
  exist, and on a runtime that returns no models it would silently pick `codex-gpt-5.5`. Neither
  path checks availability.
- **The default config contradicts itself:** `runtime.value = codex` (the launch runtime) while every
  role model is `claude-opus-4.x`. A Claude crew on a Codex launch runtime — and both CLIs are missing.
- The picker is **not wired to runs** — its own popover says "Staged preview — the crew and build
  panes you set here aren't wired to the run yet". A control that changes nothing should not look
  like one that does.
- "Parallel build workers · up to 102": `maxPanes = res.physical_operators?.count` (:5130, fallback
  4) — confirmed, `GET /settings` → `physical_operators.count = 102`. That is the number of
  *registered* operators presented as capacity; usable parallelism here is 0.
- Settings → Default crew pre-selects **Codex CLI** as launch runtime while it is missing.

### D12 — smaller issues

- **Brand mark.** Not a copy of Huawei's logo — `App.tsx:275-277` says "Original lotus mark … Not a
  reproduction of any existing trademark" — but the palette is explicitly "Huawei-derived" with
  "Huawei red #CF0A2C (PANTONE 186 C)" (`styles.css:32,44`). A red petal fan in that exact red reads
  as Huawei's mark. The comment says **five** petals; the array draws **seven** (:285-291).
- **Token in URLs.** The SPA's event stream requests `/events?stream=1&...&token=<token>` —
  `EventSource` cannot send headers — partly undoing the desktop shell's header-only navigation.
- **Settings → Credentials** shows three key rows, all `UNCHANGED`, and never says the CLIs are
  absent. The page where the problem is fixed does not name the problem.
- **Settings → Activity** says "Busiest day: 2026-06-25 (0)" — a zero-session "busiest" day three
  months before this install existed.
- **Failed intakes are invisible.** Four failures, and both the sidebar and Activity show 0.
- **Orphaned uploads.** Attachments persist even when the request fails.

### Attachments go into WSL — verified, and correctly designed

The browser reads the file with the File API, base64-encodes it as `content_base64` (`api.ts:302`),
and POSTs JSON over loopback to the status-server **inside WSL**, which writes it with
`_persist_intake_attachments` (`status-server.py:1156`):

```
Windows : scratchpad\solar-attach-probe-7f3a.txt                                        sha256 ecffd417...2c1f
WSL     : ~/.solar/harness/run/intake-uploads/<request_id>/solar-attach-probe-7f3a.txt   sha256 ecffd417...2c1f
```

Byte-identical, Unicode (`café 😀`) intact. **There is no Windows-side worker and no Windows helper.**
The only Windows→WSL file bridge in the product is `runtime-sync.js`, which copies program code, not
user data. Limits: 8 files, 20 MiB each, 64 MiB total decoded — all in one JSON body, and base64
inflates the wire size by about a third.

Probe hygiene: my first attachment check printed `hasBase64Field=false` because its regex did not
match the key `content_base64`. The code is the evidence; that line was wrong.

Probes created four intake records, all labelled `[playwright probe]` in their task text.

## 26. Owner's product-honesty policy — and where the dashboard breaks it

Stated by the owner on 2026-09-16. It is the standard every UI finding above is judged against.

1. **No non-functional previews.** This is a local app. It must not make claims, collect input, and
   then fail to act on it. A "LARP app" is a defect even if every component behind it is fine.
2. **Preflight must show state before asking for input** — which checks passed, which failed, and
   what is not usable — so nobody types a task into something that cannot run it.
3. **No false attribution.** An error must name the real cause and its real owner. The anti-pattern
   is a SaaS error page dressed as a Cloudflare error so the blame lands elsewhere.

| Policy | Where the dashboard breaks it | Evidence |
|---|---|---|
| 1 | Crew picker is a staged preview wired to nothing | its own popover text; D11 |
| 1 | "Parallel build workers · up to 102" — a capacity claim with zero usable workers | `physical_operators.count = 102`; `/auth/status` all unavailable |
| 1 | Composer accepts and submits work with no runnable provider | D10; four failed intakes |
| 2 | Browser path has **no** preflight at all | D10 |
| 2 | `AuthGate` treats a definite `missing-cli` as a "detection gap" and opens | `App.tsx:340` |
| 2 | Credentials tab never says the CLIs are missing | Settings sweep |
| 2 | The desktop preflight that *does* exist checks the wrong thing — green while intake fails | D8 |
| 3 | **`"openai transport failed"`** blames a remote provider's transport for a **local** binary missing from the service `PATH` | `intent_acceptance.json`; `intent_compiler.py:258` runs `codex` |
| 3 | `intent_compilation_failed` frames it as the *user's intent* failing, when nothing ran | D9 |
| 3 | Hero copy promises it "tells you plainly when it stalls"; the failure is a bare code | the landing page itself |
| 3 | "Busiest day: 2026-06-25 (0)" asserts a fact that is not one | Settings → Activity |

**Scoring rule adopted from this policy:** a feature that accepts input and cannot act on it is
`IMPLEMENTED_AND_FAIL`, even when each component individually "works", because the contract the user
actually sees is broken. And an error message that points at the wrong owner is a defect in its own
right, separate from whatever caused the error.

## 27. Retraction, the first stub-free app launch, and multi-account [2026-09-16]

**Retraction.** §§16-17 and the published report (up to Version 4) said the packaged `Solar.exe` hit
Defect 2 on first launch, citing `%LOCALAPPDATA%\Solar\setup.log`. **That log is mine, not the app's**:
`Start time 20260916095224`, `End time 20260916095228` — my manual `install.ps1 -ForwardArgs` run,
twelve minutes before `Solar.exe` was built (10:04). WSL and the runtime were already present when the
app ran, so it never offered setup. What *is* verified, by code and hash:

```
sha256 install.ps1                                   59a608853303741af30e15059fc8023e95f58154b43cbea2fe8c0e8f0d6ea807
sha256 desktop/dist/win-unpacked/resources/install.ps1   (identical)
bundled copy line 172: the defective nested-quote echo
main.js:289  Start-Process -FilePath 'powershell.exe' -Verb RunAs ...
```

So the app's setup path is **expected** to hit Defect 2 but is **NOT_TESTED**. To observe it:
`$env:SOLAR_SIMULATE='wsl-missing'`, launch, click *Install WSL2 now* (UAC prompt).

**Stub removed** (`~/.local/bin/codex` and `~/.solar-test/bin/codex`) before the owner installs a real
Codex — preflight's candidate list checks `~/.local/bin/codex` *before* `~/.npm-global/bin/codex`, so
a leftover stub would have shadowed a real install and produced a false green. Preflight now reports
`required fail: codex runtime CLI not found`. The stub-era cockpit was stopped with
`solar harness kill`. A WSL holder (`wsl -- sleep infinity`, Windows PID 1796) keeps the VM up for the
review — stop it with `Stop-Process -Id 1796`.

**First stub-free launch of the portable build** (`Solar 1.0.0-rc.9.exe`), window "Solar":

```
attached to already-running runtime http://127.0.0.1:8766/
Windows runtime prewarm failed: ... required fail: codex runtime CLI not found
  install hint: Install the Codex CLI and confirm 'codex --version' works before launching panes
prewarm start failed
```

No `loading runtime dashboard` line follows, unlike the stub-backed run. Under the owner's policy this
is the **desired** behaviour — real state before input — so the desktop preflight row is reframed: it
still fails, but only for D8 (false green), not for stopping here.

### D13 — multiple accounts per provider: not supported, and crossable

- One Codex sign-in check, fixed path `$HOME/.codex/auth.json` (`auth-helpers.sh:26,46`).
- One key per provider in `~/.solar/secrets/solar-user-secrets.env` (`status-server.py:1910-1932`).
- No selector anywhere (the `account_identifier` hits in `harness/lib/browser/` are for the browser
  operator, unrelated).
- `CODEX_HOME` is the only switch: honoured by the cockpit (`solar-harness.sh:4115`), sandboxed per
  pane (`pane-launcher.sh:537`), unset from tmux global env (`:612`). **Ignored** by the dashboard's
  sign-in check, and not inherited by the systemd status-server — so cockpit and dashboard can use
  different accounts, and the dashboard can bill tasks to the default one.
- **`cmd_reuse_host_creds`** (`auth-helpers.sh:65-100`) copies Windows `.codex/auth.json` (or
  `.claude/.credentials.json`) into WSL, **replacing** a different existing WSL sign-in
  (`"replaced": true`). Work-on-one-side / personal-on-the-other → silent account swap.
- Fallback when the Windows profile cannot be resolved: glob `/mnt/c/Users/*/`, first non-shared
  profile holding a sign-in. On a multi-user PC it could pick another person's credential if readable
  from WSL. Code review only.
- This is also the answer to "is there a Windows-side tool that streams data into WSL": **for
  sign-ins, yes (this helper); for user files, no** — attachments go over HTTP.
- Workaround (untested): one `CODEX_HOME` per account, the same value set on the service via a systemd
  drop-in, restart both; never use sign-in reuse across different accounts. Confirm Codex's own
  handling with `codex --help` after install.

Report updated: new matrix row `Account management / 2` = NOT_AVAILABLE, reproduction R-18, counts now
9 PASS / 5 limited / 15 FAIL / 1 NOT_AVAILABLE / 2 NOT_TESTED = 32 rows.

## 28. Copy diagnostics is truncated, and OpenRouter is only half-integrated [2026-09-16]

### D14 — Copy diagnostics silently stops at `wsl --status:` [root cause proven]

The owner used the app's **Copy diagnostics** (the menu path automation could not reach) and pasted:

```
=== Solar desktop diagnostics (local, no telemetry) ===
time: 2026-09-16T15:27:40.562Z
app: 1.0.0-rc.9  electron: 42.6.1  platform: win32 10.0.26200
HARNESS_DIR: C:\Users\m50066326\.solar\harness
wsl distro: Ubuntu-24.04  state: up
wsl --status:
D
```

Mechanism, reproduced with the same call in Node:

```
spawnSync("wsl.exe", ["--status"], { encoding: "utf8" })
chars: 116   NUL count: 58
first chars: "D\u0000e\u0000f\u0000a\u0000u\u0000l\u0000t\u0000 ..."
a NUL-terminated consumer keeps: "D"                         <- exactly where the paste stops
NULs stripped: "Default Distribution: docker-desktop\r\nDefault Version: 2\r\n"
```

`wsl.exe` writes UTF-16LE. `collectDiagnostics()` (`main.js:1320-1324`) decodes it as UTF-8 and appends
it unmodified; `clipboard.writeText` (`:1421` screen action, `:1741` menu) hands it to the Windows
clipboard, whose text ends at the first NUL. **Everything after it is lost** — port, in-app log ring,
`desktop.log` tail, WSL journald, service status. The fix already exists in the repo:
`runtime-detect.js:23,36` strips NULs with `.replace(/\x00/g, "")`; the collector does not reuse it.
Same pattern as D8 — two code paths treating one input differently.

**Save diagnostics…** writes with `fs.writeFileSync` (`:1750`), which does not stop at NUL, so the saved
file should hold the full report with NULs interleaved in that one section. Inference — not tested.

**Correction to the owner's reading:** the logs were not deliberately removed. The collector includes
them; truncation dropped them. "(local, no telemetry)" means nothing is sent off-machine, not that
anything was stripped.

**No end-of-report marker.** The collector ends `return redact(parts.join("\n"))` with no terminator, so
a truncated copy is indistinguishable from a complete one. Owner's rule 4 (§26 / memory): output that
can be cut off must say that it ended.

**`HARNESS_DIR` in the report does not exist.** It prints `C:\Users\m50066326\.solar\harness`; on this
machine `C:\Users\m50066326\.solar\` contains only `logs`. On Windows the app reports its own default
(`path.join(os.homedir(), ".solar", "harness")`), while the harness lives in WSL at
`/home/muk/.solar/harness`. The first path a support reader sees points at nothing.

**Copy does not copy what is displayed — and removes it from view.** The owner expected the button to
copy the screen's content, and reported that clicking it "removed the log stuff". Confirmed:

- The `runtime-dependency-missing` screen (`main.js:1205-1218`) displays the preflight output in a
  `<pre>` block (`d.output`, :1211), with actions *Open install guidance*, *Retry*, *Copy diagnostics*.
- `runAction("copy-diagnostics")` (:1420-1425) copies `collectDiagnostics()` — a different report —
  then **immediately** `win.loadURL(SCREENS.loading("Diagnostics copied to clipboard. Retrying…"))`,
  replacing the screen and starting an unrequested retry.
- Net effect: the displayed output is on neither the screen nor the clipboard. The owner's reading was
  closer to right than my first correction allowed.
- "Diagnostics copied to clipboard" is shown regardless of truncation — a false success message.

**Over-redaction — tested in isolation.** `redact()` (`main.js:1302-1309`) has two rules: blank values
after `*TOKEN|KEY|SECRET|CREDENTIAL*` (correct), and replace **any** `\b[A-Za-z0-9_\-]{32,}\b` with
`[REDACTED-LONG]`. Exact copy of the function run against this session's values:

```
REDACTED  OPENAI_API_KEY=sk-live-abc123                 -> OPENAI_API_KEY=[REDACTED]      (correct)
REDACTED  intent-20260916-151347-f03e9c01a5             -> [REDACTED-LONG]
REDACTED  webapp-intake-8a76f565-5a61-4ed2-...           -> [REDACTED-LONG]
REDACTED  sha256 ecffd417...2c1f (real file hash)        -> [REDACTED-LONG]
REDACTED  40-hex commit-shaped value (synthetic sample)  -> [REDACTED-LONG]
kept      "required fail: codex runtime CLI not found"
kept      /home/muk/.solar/harness/lib/symphony/status-server.py
```

Hyphens are in the character class, so dashed IDs are swallowed whole. Even with the NUL bug fixed, a
copied report would hide the exact identifiers needed to find a failed task. The commit value was a
made-up 40-hex string used only to test the pattern.

Report updated as R-19 (diagnostics) and R-20 (OpenRouter), plus a new Diagnostics group (3 FAIL rows)
and a Model providers row (NOT_AVAILABLE). Owner's rule 4 added. Counts: 9 / 5 / 18 / 2 / 2 = 36.

### D15 — OpenRouter: supported in AutoSci only, absent everywhere else

**Correction first:** I initially said this branch had zero OpenRouter code. Wrong — my search piped
through `head -15` and doc hits filled every line. `git grep -il openrouter HEAD` → **41 files**,
including code:

```
harness/plugins/autosci/services/production_research.py
harness/plugins/autosci/services/codex_research.py
harness/plugins/autosci/services/claude_research.py
harness/plugins/autosci/backends/artifact_review.py
harness/plugins/autosci/bin/autosci_skill_executor.py
harness/plugins/autosci/bin/autosci_skill_shim.py
harness/plugins/autosci/bin/fixed_research_node_adapter.py
harness/lib/webwright_adapter.py
harness/tests/research_unit/test_review_provider_independence.py
harness/config/workflows/research.evidence_to_poc.v1.workflow.json
```

Docs [repo-claim, not re-run here]: P22-J23 PASS — a real OpenRouter `gpt-5.5` request through the
production AutoSci review entrypoint; commit `9d8eb1d4` made OpenRouter the **default when both keys
exist**, default model `deepseek/deepseek-v3.2`, OpenAI only via `AUTOSCI_RESEARCH_LLM_PROVIDER=openai`
(`phase-22-progress-log.md:1764-1782`). `origin/ai4research-main` carries 33 non-doc hits.

**Not integrated anywhere else** [verified]:
- Dashboard provider table `_PROVIDER_KEY_ENV` (`status-server.py:1927-1934`): anthropic, zhipu/glm,
  deepseek, openai, serper — **no `OPENROUTER_API_KEY`**, so the Credentials page cannot store one.
- Crew picker `MODEL_OPTIONS` (`App.tsx:4107`): no OpenRouter route.
- Pane runtimes and the intent compiler run only the `codex` / `claude` CLIs.

So a user can have OpenRouter configured for research review and still be unable to start any task
(this machine). Owner's direction: OpenRouter should be a first-class, system-wide provider — a natural
fit for the best-model-per-task routing a colleague is building.

## 29. Plain `wsl` opens Docker's distro — and the report is now split in two [2026-09-16]

### D16 — `wsl` with no arguments lands in `docker-desktop`

The owner tried to install Codex and got:

```
PS> wsl
bluemuk:/mnt/host/c/Users/m50066326# curl -fsSL https://chatgpt.com/codex/install.sh | sh
-sh: curl: not found            (sudo: not found, apt: not found — also under `wsl -u root`)
```

`wsl -l -v` → `* docker-desktop  Running 2` (default) and `Ubuntu-24.04  Running 2`. The `-sh` prompt,
`/mnt/host/c` mount and missing package manager are Docker Desktop's internal distro. Ubuntu is fine:
as `muk` it has `/usr/bin/curl` and passwordless sudo.

- No `--set-default` anywhere in `install.ps1`, `desktop/src/` or `scripts/`, although the product's
  own code calls Docker's distros implementation-only and never a Solar target.
- `docs/WINDOWS.md:33` says "inside WSL run: `loginctl enable-linger $USER`" without naming the
  distro; only :53 uses `-d Ubuntu-24.04`.
- `windows-evidence-doctor.ps1` prints `Default Distribution: docker-desktop` but does not flag it.
- Fix for the owner: `wsl -d Ubuntu-24.04` (or `wsl --set-default Ubuntu-24.04`, undo with
  `--set-default docker-desktop`). **Install Codex as `muk`, not root** — as root it lands in `/root`
  and Solar (running as `muk`) never sees it. `sudo apt-get curl` should be `sudo apt-get install -y curl`.
- After installing, check where it went (`which codex`) against R-14: the dashboard service's PATH does
  not include `~/.local/bin` or an npm global bin, so preflight can pass while dashboard tasks fail.

### Report restructured

Owner asked for one file with two sections. Published as Version 6:

- **Part 1 · Windows** — 16 rows (4 PASS / 2 limited / 9 FAIL / 1 NOT_TESTED); reproductions R-01,
  R-02, R-03, R-06, R-07, R-08, R-09, R-10, R-19, R-22.
- **Part 2 · Every platform** — 21 rows (5 / 3 / 10 / 2 NOT_AVAILABLE / 1 NOT_TESTED); reproductions
  R-04, R-05, R-11, R-12 to R-18, R-20, R-21.
- Total 37: 9 / 5 / 19 / 2 / 2 — counted per part from the file, and every R-link checked to resolve.
- Diagnostics split: **R-19** (Windows — NUL truncation, nonexistent `HARNESS_DIR`) and **R-21** (all —
  copies the wrong content, clears the screen, false success, no end marker, over-redaction).
- Classification rules: the Linux installer run and the accessibility verdict sit in Part 2 (same
  script / same dashboard everywhere); the Windows-only gate fix stays in R-09. Part 2 was observed on
  Windows only and is classed as cross-platform from the code — stated in the report's limits.

## 30. Automated testing, a real task, and a mock dashboard [2026-09-16, report Version 7]

Owner signed in to Codex 0.154.0 (official installer → `~/.local/bin/codex`, a symlink into
`~/.codex/packages/standalone/releases/`). Stub removed first so it could not shadow the real one.

**Tools (scratchpad):** `solar-e2e.js` (Playwright `_electron` against the packaged app: sim / real /
twin / cold / stale), `edge.js`, `edge2.js` (upload intercepted), `edge3.js` (fresh context per case),
`run-real.js`, `make-mock.js` → `mock-dashboard.cjs` (repo fixture seeding from
`tests/desktop/overhaul-visual.test.cjs` lines 1-500 + a completed session; real status-server on
port 8790 with a temp data dir; Ctrl+C deletes it).

**Local workaround applied (still in place):**
`~/.config/systemd/user/solar-status-server.service.d/10-local-bin-path.conf` adds `%h/.local/bin` to
the service PATH. Dashboard tasks now reach Codex and spend quota. Remove + restart to undo.

**New defects (report R-23 … R-31):**
- R-23 Install WSL2 button: `Start-Process -ArgumentList` splits paths with spaces. Replica: plain ✓,
  `o'brien` ✓, `with space` ✗, `Jane Doe's files` ✗, silently.
- R-24 Wrong port file → app deletes pid/port/token (`main.js:565`, `:1010`) of a healthy server and
  waits forever; timer resets. Keep waiting / Retry / Reconnect are the same code
  (`main.js:1471`: `clearPortCache(); reload()`). Recovery: restart the service. Service journal showed
  no restarts during the test.
- R-25 Status screens: `data:text/html,` without charset (`main.js:1152`) → `â€"`, `â€¦`;
  unknown screen → `[object Object]`.
- R-26 **Real task "Create a file named hello.txt containing the word hello." failed at execution
  planning**: `OBLIGATION_UNSATISFIABLE_FOR_NODE_KIND … check.patch_within_scope … node_kind='artifact'`.
  Semantic plan accepted, execution plan rejected; both generations carried the obligation, which is a
  required check in `cap.requirement-compiler-implementation.yaml:96`. Reason not shown anywhere on the
  session page. Intent ~61 s, failure at ~2 min.
- R-27 Session screen: planning failure described as a failed step with evaluation evidence;
  "Plan compiling…" under RUN FAILED; preview panel "Building now"/"Preparing"/spinner in every state
  (real failed run + mock blocked/gate/failed/done); internal chips; "…bdfRequest:" run-together.
- R-28 Attachments: 0-byte → `attachment_content_missing` (empty base64 treated as missing); 100-char
  Chinese name → `attachment_write_failed` (ext4 255-byte limit, name cut at 140 *chars*); long names
  lose extension; 9 files → all dropped; 21 MB → clear message (good).
- R-29 12,001 chars accepted with no counter → bare `task_too_long`; connection loss → "Failed to
  fetch". Whitespace-only blocked and double Ctrl+Enter deduplicated (good).
- R-30 **Security:** ACAO `*` on all JSON; token not enforced on loopback; body parsed regardless of
  content type; keys written with `json.dumps` and `source`d by `model-config.sh:24`. Isolated test:
  trailing space kept, `\n` literal, `$HOME` expanded, backtick executed. Browser completion not tested;
  nothing written to real settings.
- R-31 Repo visual gate RED (2 fails): `.plan-card-role` removed in `3f534a0a9`, test last changed
  2026-08-07. Not Windows.

**Passes / nuances:** cold start from `wsl --shutdown` → dashboard in ~14 s; with the app open the VM
stayed up 90 s (R-07 mainly hits browser-only use); two instances both worked (no lock); Save
diagnostics writes the full report (11,846 B, 58 NULs, no end marker, 4 redactions); menu has
DevTools and no About; the Playwright-only preload error never appears in normal launches.

**Corrections recorded this round:** stub was NOT the cause of the owner's failures (service PATH);
first pre-selection explanation wrong (config, not fallback); attachment "wrong error" was leftover
page state (same-document hash navigation) — re-tested cleanly; "port file missing after cold start"
was a PowerShell→wsl `$`-stripping artifact; "something holds 8765" was just port instability.
**Rule for next time:** never pass `$`-containing commands from PowerShell to `wsl.exe`; use
`wsl.exe … bash -s` with a heredoc from Git Bash.

## 31. hello.txt, worker boundary, claim capabilities, colours [2026-09-16, report Version 8]

- **hello.txt run** `sprint-20260916-172130-…-e3f88bdf`: FAILED at execution planning (R-26), not stuck.
  Intent accepted with `clarification_questions: []`, `ambiguities: []`. Requirements pass with
  `assumptions: []`, `relative_path "hello.txt"`, `output_root "."`. Workspace authority root is
  `/home/muk/.solar/workspace` (still empty). The location was defaulted silently → **R-32**.
- **Worker boundary** (`pane-launcher.sh run_codex_with_filesystem_scope`). The default on Linux is
  the harness's own Landlock wrapper, and Codex runs with its sandbox bypassed. Read-only: system
  folders. Read-write: `~/.solar/harness`, the task directory, the worker's state and temp folders.
  Probe with `tools/landlock_exec.py`, no model: blocked `/mnt/c`, `~`, `~/.codex/auth.json`, `/tmp`;
  ALLOWED workspace, the harness folder including its scripts, and all sprint records.
  `~/.solar/harness` and `bin/` are `drwxrwxrwx` → **R-33**. Planning stages run Codex with
  `--sandbox read-only`. `SOLAR_CODEX_PANE_FS_ISOLATION=codex` switches to Codex `workspace-write`.
- **Capabilities.** The 8 claim capsules are stable and their files exist (checked with the repo's
  loader; my earlier "manifest NO" was a path mistake). The registry test fails 1/2:
  `cap.research-report-draft` is in `autosci/manifest.yaml:34` but not in the registry → **R-34**.
- **Claim fixture** `C:\Users\m50066326\solar-tools\claim-test\` (+ `~/.solar/workspace/claim-test/`):
  `cache-pilot-notes.txt` (S1–S6) and `prompt.txt`. Regex results → **R-35**. The backend flags S1,
  S2 and an unrelated "40%" (S5). The lifecycle cue also flags S3 ("improvements"), S4 ("improving")
  and S6 ("did not improve"). Offline `solar harness research init/add-source/extract/ledger` works;
  extract stores the whole source as ONE item (confidence 0.7); `check` needs a compiled report.
- `solar` is not on PATH in WSL. README.md:375 documents `export PATH="$HOME/.solar/bin:$PATH"`,
  so this is not a defect.
- **"Workers: N configured · N ready"** is a count of registry rows, and "ready" is inferred from
  labels → **R-36**.
- **Colours** (owner): working = brand red, danger = the same `#a60822` as working text, a failed
  load shows amber, and green appears despite DESIGN.md saying "NO green" → **R-37**.
- **Owner's real run** `…180422…1b04e202` (AllocBench question + attached .md): failed at execution
  planning, `report_draft: UNSATISFIABLE_BINDING`. 0 of 102 workers fit
  (`ScientificReportDrafter` needs `evidence_transform` trust) → **R-39**. This is NOT R-34 (I briefly
  assumed it was; the node uses `cap.scientific-report-synthesize`).
- The same page listed MY fixture (written 14:03:20, run created 14:04:22) as the run's primary
  result. Cause: `_discover_sprint_deliverables` scans the shared `~/.solar/workspace` with a cutoff
  of `created_at − 300 s` → **R-38**. Open, new tab and download all worked in Chromium and in the
  desktop app from a fresh page. The OWNER then found the real repro: with any file already open in
  the panel, the red button swaps the panel off-screen and never scrolls (focus-on-mount effect,
  App.tsx:3370). Reproduced with `open-probe3.js`.
  "State transition" entries have empty `from` and a dispatch key as `to` → added to R-27.
- **Output policy (R-38, extended).** The fixture was moved to `~/solar-fixtures/claim-test/` (run list
  74→72 items, output rows 2→0). The folder comes from `raw_intent.context.cwd` (shared workspace;
  no per-run `workdir`). The result is picked by 11 name/size/time tiers (a process file with
  "accepted" in its name wins). Stage is a substring match on the full path ("dagmar"→task_graph).
  Four page areas pick the output differently (the preview box prefers any .html or poster.html).
  Verified with `deliv_policy_probe.py` and `poc_pick_probe.mts` (scratchpad).
- **Pipeline vs UI (report "Where each problem lives").** Both real runs failed in the pipeline
  (R-26, R-39). The SERVER then reports `plan_governance.state "compiling"` with no codes:
  `orchestration_routes.py:2750` only knows `plan_compile_failed` (the pipeline now writes
  `planning_failed`) and reads codes from a `<run>.plan-compile-errors.json` that nobody writes.
  The server says the credential-less Claude worker is "ready/configured". The PAGE drops 102
  workers to 56 (de-duplicates by pane_id; 47 share `solar-harness-multi-task:*`).
- **Windows-specific, new.** R-40: installing from the Windows checkout copies with `rsync -a`,
  so 2576/3495 files are world-writable. `core.autocrlf=true` leaves 1277 .py files with CRLF,
  and 481 executable CRLF-shebang files fail if run directly (the task path uses
  `python3 file.py`, so nothing seen broken). This explains R-33's 777. R-41: no Windows-path
  translation anywhere, and no drop handling (NOT_TESTED; the owner should try a real drag).
  WSL clock was in sync (no drift seen).
- **Causes and fix distance (report V13, cheap scoping).** Most code arrived in bulk import
  `523040fb2` (2026-07-21), so the "why" is not in this repo.
  - R-27/R-13: `23e50e1a0` (08-28) writes phase `planning_failed` (coordinator.sh:3820), but the
    server knows only `elastic_planner_failed` (:993) and `plan_compile_failed` (:2750). The
    adapter never copies `plan_acceptance.reasons`. SMALL.
  - R-39: `cab32f937` (09-08) `cap.scientific-report-synthesize` requires trust_class
    evidence_transform, prefers builders with unset trust, and forbids autosci-report-worker (the
    only one with that trust). Self-contradictory. SMALL config; unknown after.
  - R-26: impl capsule obligation (05-24) vs the newer node-kind checker. SMALL–MEDIUM.
  - R-38: by design, runs use an isolated `sprints/<sid>/workdir` and publish later (project log,
    08-29). The server falls back to the shared cwd while that folder does not exist (planning or
    early failure). SMALL to drop the fallback.
  - R-32: the server passes `clarification_questions`, but the page never renders them. Recording
    the assumption is SMALL; the ask/answer flow is LARGE.
  - Drag-and-drop: the owner tested it; nothing happens. Now NOT_AVAILABLE (a nit).
- Totals by script: 67 rows. Part 1 has 25 (6/4/12/1 not available/2 not tested). Part 2 has 42
  (5/7/28/2 not available). Report Version 13.
- **Excel version** `tundle/ai4research/AI4Research Windows GUI Test Report - Muk.xlsx`, in the
  summer workbook's format and built with that file as the style template (the template was not
  modified). Sheets: Test Summary, Windows GUI Features, Cross-Platform Features, Problem
  Reproduction, Where Problems Live, Fix Scoping, Ambiguities. Built by `report_extract.py` +
  `build_xlsx.py` (scratchpad; openpyxl in `~/.cache/xlsx-venv` in WSL). Verified: counts match,
  verdict→colour matches, no CJK. Not visually checked (no Excel or LibreOffice installed).
- **Pass probes** `C:\Users\m50066326\solar-tools\pass-probe\`.
  1. A direct answer ("Why is the sky blue?", the example used in
     tests/harness/test_direct_answer_runtime.py). A RequirementIR with
     `request_type direct_answer` and the matching hints forces `direct_response`
     (elastic_planner.py:846), then tools/direct_answer_runtime.py writes
     `sprints/<sid>/workdir/workspace/direct_response/answer.md`. The model resolves offline to
     codex_cli `--model gpt-5.5`; whether the account can use gpt-5.5 is unverified.
  2. A code task (hello_py/ with a test). Code targets should avoid R-26's artifact-node
     rejection; less certain.
- **R-42 (from code, not run).** The direct answer is `codex exec --sandbox read-only
  --ignore-user-config --model gpt-5.5` (structured_model.py:145), with no `--search`, so it
  answers from model memory. The answer schema allows only answer, requirement_ids and
  limitations: no sources. The review is the same model ("same_model_second_pass"), yet the
  status note says "passed one independent review". Citable answers live in the research
  subsystem, whose full-plan route fails at report_draft (R-39). Report V14: 68 rows (Part 2
  43, 1 not tested); the xlsx was rebuilt and verified.
- **First PASS: sky run** `…185659…c339d1ab`, 39 s. The requirement compiler set NO request_type,
  so the planner's own strategy call chose direct_response and wrote the answer inside planning
  (Codex default model, `planning/semantic/direct_response.json`). The worker route and gpt-5.5
  were NOT used (corrected in R-42). The review was a same_model_second_pass. The page shows
  "Run complete" with all 4 roles green and NO answer anywhere; the server marks no result among
  39 items → **R-44**.
- **Fish run** `…185941…77f0f03b` failed at the planner's first call (exit 1, 2.5 s, same schema
  as the passing calls). stderr is discarded (structured_model.py:163). One replay showed:
  "You've hit your usage limit … try again at Oct 16th, 2026 1:20 PM". `/auth/status` still says
  codex ok. Intake took 35 s with only a "Starting" button, no pending entry, and a navigation
  jump after clicking away → **R-43**. ALL model-backed testing is blocked until 2026-10-16 13:20
  unless Plus or another provider.
- Report V15: 71 rows (Part 2 46: 5/8/31/2). The xlsx was rebuilt (71, R-01..R-44, no CJK).
- **Switched to Claude (R-45; local config, no repo change).** The Settings runtime selector only
  changes worker panes; model stages read `SOLAR_LLM_PROVIDER` (structured_model.py:265). Done:
  - installed Claude Code 2.1.273 (official installer, `~/.local/bin/claude`; all harness flags
    supported);
  - `POST /settings {"runtime":"claude"}` (backup `config/solar-user-config.json.bak-20260916-before-claude`);
  - systemd drop-in `20-llm-provider.conf` plus a `~/.profile` export, both `SOLAR_LLM_PROVIDER=anthropic`;
  - `solar harness stop`, a service restart, and `solar harness start ~/.solar/workspace`.

  Verified: both processes have the variable; 4 Claude panes; every stage resolves to
  anthropic/claude_cli (offline). PENDING: the owner runs `claude auth login` in WSL; then
  restart the cockpit; then test. To revert: delete the drop-in and the profile lines, set the
  runtime to codex, restart. Report V16: 72 rows.
- **R-46 (owner).** After the switch, the cockpit panes open on Claude's first-run screens:
  the theme picker in PM/Planner/Evaluator and the sign-in screen in Builder
  (`~/.claude.json` hasCompletedOnboarding unset). The startup check still says
  LIVE-CHILD-PRESENT. Fix: run `claude` once in a normal WSL terminal (theme, sign in, exit),
  then `solar harness stop; solar harness start ~/.solar/workspace`. Report V17: 73 rows; the
  xlsx was rebuilt (R-01..R-46, 0 CJK — one quoted pane title was translated).
- **Trust-prompt loop (added to R-46).** Onboarding was done from `/mnt/c/Users/m50066326`, so
  only that folder is trusted. The panes in `~/.solar/workspace` hit "Quick safety check".
  `pane-launcher.sh:150-151` auto-sends "1"+Enter; in Claude Code 2.1.273, option 1 = "No, exit"
  → exit 1 → respawn: 15 exits 19:19:58–19:21:36 (pane-exit.jsonl). The launcher also
  auto-accepts the bypass-permissions warning (":124" sends "2"). Workaround: `cd
  ~/.solar/workspace && claude`, choose "Yes, I trust this folder", exit, restart the cockpit. A
  real fix (match options by text, or pre-check trust) would be a repo change → own branch.
  Report V18.
- **Second prompt: the bypass-permissions warning** (owner; log shows exit 1 at 19:25:31–47 for
  all four panes). Correction: both menus are UNNUMBERED with "❯ No, exit" pre-selected, so the
  typed digit ("1" for trust, "2" for bypass) does nothing and Enter declines. 50 exits
  19:15–19:26:20. The owner accepted both by hand (`skipDangerousModePermissionPrompt: true`);
  at 19:27 all 4 panes were idle, "bypass permissions on".
- **R-47.** Claude panes get NO Landlock (the wrapper is on the codex branch only,
  pane-launcher.sh:703). They run `--dangerously-skip-permissions --model claude-opus-4-8
  --allowedTools Read Bash Grep Glob Write`, and the settings file holds only event hooks, so
  they can write anywhere, including /mnt/c. The startup token makes panes generate immediately
  (Planner used 1.5k tokens at start), so a cockpit start costs quota.
- **Why 4 panes.** `EXPECTED_PRODUCT_DELIVERY_PANES=4` (solar-harness.sh:81); `start_harness`
  splits one window into a 2x2 grid (:1191-1195), one pane per role: PM, Planner, Builder,
  Evaluator. There is an optional separate "lab" session with 4 more builder panes (:1568-1570),
  not running. Report V19: 74 rows.
- **xlsx made minimal (owner request)**: 3 sheets like the summer file (Test Summary, Windows GUI
  Features, Cross-Platform Features) and 8 columns. The summary has only the verdict table, the
  total (74) and one line saying R-numbers refer to the web report. Build with `MINIMAL=1
  build_xlsx.py`; without it, the full 7-sheet version is produced. Verified: 25 + 49 rows, 0 CJK;
  the template is unchanged (09:47).
- **Problem Reproduction sheet restored, curated** (`repro_curated.py`). Scope: GUI, GUI↔backend and
  Windows setup; verified items only. It has 32 rows (21 owner-reported) and a "Not listed" block:
  R-05/06/08/31/34/35 out of scope; R-09/10 not product problems; R-18 unverified; R-20 feature
  request; R-33 covered by R-47; R-41/42 minor/merged.
- **Re-verified for it** (`verify-probe.js`, `settings-recheck.js`, no model use):
  - R-43: intake mocked in the browser. No sidebar entry while pending; after clicking away, the
    page jumped to the new run when it finished (hello×8→SKY×6).
  - R-30: a page on 127.0.0.1:8799 read /auth/status, /settings (213 KB) and a deliverables list.
  - R-16: 11 failed intake jobs, none in the sidebar; credential rows only "UNCHANGED". The
    "busiest day" and "runtime preset Codex" claims were dropped (not re-observable).
- **New owner runs on Claude.**
  - Alita-G (+paper): all 7 model calls on claude_cli passed, then NO_FEASIBLE_CAPSULE_COMPOSITION
    (plan_answer_report: REQUIRED_INPUT_UNAVAILABLE). Added to R-39; this also confirms R-45 works.
  - The fish question re-run on Claude: finalized.
  - The dashboard port is now 8765 (it changes on service restart).
  - Web report V20.
- **Workbook reorganised (owner round 3).** Built by `workbook_v2.py` + `build_workbook_v2.py`.
  - Sheets: Summary, Checklist (81 rows in sections A–H, Z = code-only), What works, Problems &
    reproduction (37 user-visible, then 6 code-only, then a left-out list), Design questions.
  - New result WORKS_AFTER_CHANGE (yellow). Totals: 19 pass / 11 limits / 6 after change /
    41 fail / 4 NA.
- **New owner findings, verified** (web report V23):
  - R-48: Haiku in Settings runs Sonnet. The registry has no haiku; persona-config.sh:79 falls
    back to sonnet.
  - R-49: desktop app takes 6.1–6.4 s to a usable dashboard vs 0.3 s for the page in an open
    browser (`startup-timing.js`).
  - R-50: no live chip on home (App.tsx:4048).
  - R-51: the chip dashes are connector lines (styles.css:4568); chips are keyword-mapped.
  - R-52: POC preview not useful; spinner stays after the run ends.
  - R-53: the approval Review file link opens the file list (mock, `approval-probe2.js`); an
    absolute Windows path doesn't match.
  - R-54: the Claude Planner pane wrote planner-requirements/handoff for AllocBench (15:28) and
    Alita-G (16:12) into ~/.solar/workspace/sprints; every run now shows the Alita-G file as its
    result (fish showed AllocBench earlier). The write path looks resolved relative to the
    workspace (pm_dispatch write_scope_resolution); not fully traced.
  - R-55: the startup token spends ~1.5k tokens.
- **Getting past the Alita-G gap.** No code: paste the paper text instead of attaching it, or
  also ask for a literature search. Code (own branch): make literature_discovery optional for
  user-supplied sources, or synthesize a discovery record from the attachment.

## 32. Open, for the next session

- Whether to file/fix the three defects in §8, or just record them. They are real and reproducible.
- Installing a model CLI **inside WSL** before any pipeline work can be exercised.
- Building `Solar.exe` (needs Node on Windows) to test the Electron shell and its WSL bootstrap.
- The Phase 22 L2 test matrix (`Downloads\AI4RnD Brief Feature Test Report.xlsx`, 142 items:
  26 PASS, 66 PASS_WITH_KNOWN_LIMITATIONS, 22 FAIL, 28 NOT_AVAILABLE) is the register of what to
  exercise. Note its sheets say `FAIL` where the summary sheet says `IMPLEMENTED_AND_FAIL`.
- **`Installer & CLI & Webapp / 1. Windows App` is recorded NOT_AVAILABLE — "not implemented in the
  current product".** That verdict looks stale: `desktop/` implements it (`build:win` →
  `electron-builder --win portable`), plus `install.ps1`, `docs/WINDOWS.md`, WSL runtime detection
  and logon-autostart. It was never packaged and exercised, which is a different verdict. Correcting
  this with evidence from this machine is the point of the new English document.
