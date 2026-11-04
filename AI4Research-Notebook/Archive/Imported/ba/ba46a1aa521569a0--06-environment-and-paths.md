# 06 — Environment, Paths & The Relocation

## The relocation (done 2026-09-10)

```
BEFORE:  /home/muk/projects/AI4Research
AFTER:   /home/muk/work/AI4Research
NOTES:   /home/muk/work/notes/
```

### Why it was safe [verified before moving]

- `git worktree list` showed a **single** worktree — no linked worktrees to
  repoint.
- **No** symlinks escaping the tree.
- **No** `.venv` or `node_modules` at repo root (so no absolute-path-baked
  virtualenv or node bin shims to rebuild).
- `grep -rIl "projects/AI4Research"` over all tracked files: **zero hits.**
  The repo is path-relative by design; `AGENTS.md` states all paths are
  relative to repo root.
- **No** systemd user units under `~/.config/systemd/user/` referenced it.
- Same-filesystem rename, so the 2.0 GB `.git` moved instantly.

Post-move verification: `git status`, `git rev-parse HEAD`, and
`git rev-parse --git-dir` all work; branch `openJiuwen-Solar`, HEAD
`b0bf165f9`, worktree clean.

### The one loose end

```
/home/muk/.claude/projects/-home-muk-projects-AI4Research
```

Claude Code keys session history by working-directory path. Sessions from the
old location stay in that directory; new sessions will create
`-home-muk-work-AI4Research`. Nothing breaks — but **old session history won't
auto-surface** in the new location. Options: leave it (harmless), or rename the
directory to `-home-muk-work-AI4Research` to carry history forward. Not done
automatically, since it's your call.

### Things that could still hold the old path

Not found in this checkout, but worth re-checking if something misbehaves:
shell aliases/functions in `~/.bashrc`, editor workspace files, `~/.solar/`
config (the runtime dir did not exist at move time — Solar was not installed),
tmux session definitions, and any `actor-hosts.json` on remote machines.

## Runtime layout

| Path | What |
|---|---|
| `/home/muk/work/AI4Research` | source checkout |
| `~/.solar/` | Solar runtime state (**did not exist at move time**) |
| `~/.solar/harness/` | installed harness runtime — the `HARNESS_DIR` default |
| `~/.claude/solar/SOLAR.md` | generated runtime kernel (installer output; **not** in this repo) |
| `~/.solar-src/OpenSolar` | `get-solar.sh` keeps its clone here so `solar update` works |

`CLAUDE.md` is explicit: the repo's `CLAUDE.md` is **not** the installed runtime
kernel. The installer generates that separately.

## Key environment variables

| Var | Effect |
|---|---|
| `HARNESS_DIR` / `SOLAR_HARNESS_DIR` | harness root; defaults to `$HOME/.solar/harness` |
| `SOLAR_PANE_RUNTIME` | `claude` \| `codex`. Anything else exits 64. Env wins over dashboard config key `runtime`. |
| `SOLAR_CODEX_EXTRA_FLAGS` | codex launch flags; auto-derived from config `codex.search` / `codex.effort` if unset |
| `SOLAR_PM_DEFAULT_PROVIDERS` | set to `openai` automatically when runtime is codex |
| `SOLAR_MULTI_TASK_DEFAULT_PROVIDERS` | same |
| `SOLAR_TEST_MODE=rapid_smoke` | injects frozen test_policy. **Trusted env only.** Not a quality proof. |
| `SOLAR_INTAKE_COMPAT_MODE=legacy` | keeps the historical intake path. **Do not enable for migration acceptance.** |
| `ANTHROPIC_BASE_URL` | provider abstraction / override point |
| `PYTHONPATH` | forced by `solar-harness.sh` to `$HARNESS_DIR/lib` first |
| `SOLAR_REPO`, `SOLAR_CHANNEL`, `SOLAR_SRC` | `get-solar.sh` bootstrap overrides |

`.env.template` exists at repo root. Never commit `.env` contents.

## Dependencies

### Platform [repo-claim, verified on their test machine]

Primary path: **Linux / Windows WSL2**.
- Python 3.11+ (verified there on 3.12.3)
- Bash 4+ (tested on 5.2.21)
- Git, tmux (3.4), jq (1.7)
- An authenticated model CLI compatible with schema-bound calls

Windows **native** Bash/Python harness is *not* a supported alternative path.
WSL first-install still needs real testing on a new machine.

### Python

Core deps: `requirements/harness.txt` — small and honest:
```
jsonschema>=4.0, pydantic>=2.0, pypdf>=4.0, PyYAML>=6.0, rich>=13.0
```

`requirements/autosci-solar-native-dev.txt` is a **large dev snapshot, not a
cross-platform lockfile**, and contains stale personal cache paths — don't copy
those. Also: **never copy an old venv built with system-site-packages.**

`requirements/mempalace.txt` for the mempalace component.

Test config in `pytest.ini`; prefer the repo `.venv`.

### Node / frontend

The React lockfile's Vite 8 requires Node `^20.19.0 || >=22.12.0`.

⚠ Documented WSL trap: default WSL `PATH` may have **no Linux Node** but *can*
find Windows `npm`, which then fails. Install matching Node/npm **inside the
same Linux/WSL environment**, then `npm ci`. A mixed PATH is not "deps ready".

Frontend dev tests need `tests/harness/status_server/react_app/` from the repo
root — the installer's runtime payload is **not** a full dev checkout.

### Bun / TypeScript

`package.json` requires `bun >= 1.0.0`. Scripts: `bun run dev` / `daemon`
(`core/daemon/server.ts`), `bun run dashboard` (`core/dashboard/server.ts`),
`bun test`. Only runtime dep is `bonjour-service` (mDNS, for HIVE).

## Install

```bash
# curl | bash bootstrap
curl -fsSL <raw get-solar.sh url> | bash -s -- --yes --components kernel,harness

# or from a checkout
./install.sh
```

- `SOLAR_CHANNEL` defaults to a **published tag** (`v1.0.0-rc.9`), kept in
  lockstep with `VERSION` by `scripts/check-release-coherence.sh`. A prior
  mismatch made `solar update` silently *downgrade* fresh installs.
- Default components: `harness,autosci` (pull in `kernel`).
- `--claude-dir` and hooks/MCP registration **modify the user's tool config** —
  confirm before running.
- **Always review the installer dry-run first.**
- Do **not** auto-start the Electron embedded backend, the Vite dev server,
  sample ports, or a second test runtime.
- `install.ps1` + `scripts/Start-Solar-Local.ps1` +
  `scripts/windows-evidence-doctor.ps1` cover Windows.

See `INSTALL.md` (requirements, quick install, unattended/CI, components,
flags, layout, WSL2, verify, lifecycle, troubleshooting) and `docs/UNINSTALL.md`.

## Optional / gated things

Model-and-retrieval networking, auth, external services, GPU/training tooling,
browser deps, and Mac-only integrations must each be checked separately for
whatever feature you enable. Not all optional integrations need to work — but
**never mark an untested one as PASS**.

## Local services

A prior investigation found ~8 localhost services on distinct ports. Known:
- **8765** — status server HTTP control plane, platform-aware binding
- **9876** — HIVE mDNS discovery

Confirm the rest against current config rather than trusting this list.
