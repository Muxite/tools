# 03 — Conventions & Rules (non-negotiable)

Condensed from `CLAUDE.md` and `AGENTS.md`. When these conflict with your
instinct, they win. When a direct user instruction conflicts with these, the
user wins.

## Working rules (`CLAUDE.md`)

- Work on the **branch and scope the owner requested**.
- **One concern per change.**
- **Stage explicit paths only.** Never `git add -A`, never `git add .`.
- Do **not** commit local planning/worklog files unless explicitly asked to
  publish them. ← this is why these notes live outside the repo.
- **Never** run release/orphan-cut commands or push release refs unless the
  owner explicitly approves that specific action.
- Never introduce personal paths, account handles, secrets, tokens, or
  machine-local defaults into tracked files.
- Before touching the GUI under `harness/status-server/react-app`, read
  `DESIGN.md` and follow it **exactly**. Its token front matter is the single
  source of truth — no colors, fonts, shadows, gradients, or progress bars
  outside it.

## Git & safety (`AGENTS.md`)

- Use the currently checked-out branch unless told otherwise.
- **Do not push without explicit approval.**
- Never use destructive resets or history rewrites to clean a shared worktree.
- Keep out of commits: `.codex-tmp/`, rendered inspections, temp spreadsheets,
  Excel `~$` lock files, local envs, credentials.
- **Never touch the real home directory** during install/uninstall tests — use
  sandbox `HOME`.

### The pre-push integration gate

Before pushing `openJiuwen-Solar` to `origin` or `stellven`, all of:

1. Fetch+prune both remotes; verify both current remote tips are **ancestors**
   of the candidate local tip.
2. Keep an explicit ledger of candidate fixes by **immutable commit hash**,
   each classified `accepted` / `superseded` / `obsolete` / `rejected` with a
   reason or replacement hash. Only `accepted` may be integrated, and each must
   be verified reachable via `git merge-base --is-ancestor`.
3. For cherry-picks/squashes: record original + integrated hashes, verify
   reachability, review patch equivalence. **A similar subject line is not
   proof.**
4. `git branch --no-merged` is an **inventory only**. Never bulk-merge. A
   branch existing is not approval to integrate it.
5. Require clean worktree, passing relevant tests, explicit user approval.
6. Push the same verified commit to both remotes, then fetch and verify both
   tips resolve to that exact commit. Never force-push without explicit
   authorization of the specific rewrite.

## Verification / test philosophy — Phase 22

This is the part most agents get wrong. There are **three layers**:

1. **Real-task journey tests** — the *primary acceptance evidence*. Realistic
   inputs, production entrypoints, retained user-visible outputs and logs.
2. **Reliable existing tests** — the *regression layer*. They detect breakage
   and localize failures. They do **not** by themselves establish the product
   verdict.
3. **Atomic inventory** — the *diagnostic layer*. Detailed workbook/matrix.
   Phase 22 no longer requires every atomic row to have an executable selector.

> Do not resume a campaign to complete all atomic bindings unless the user
> explicitly asks.

### Result vocabulary — use these exact words

| State | Meaning |
|---|---|
| `PASS` | Realistic task completed; minimum observable success conditions met. |
| `PASS_WITH_KNOWN_LIMITATIONS` | Core task completed; a real non-core variant / edge case / limitation remains. |
| `FAIL` | An implemented path failed, or the result didn't meet minimum success conditions. |
| `NOT_TESTED` | No accepted journey exercised it. |
| `ENVIRONMENT_BLOCKED` | A *named* platform / hardware / credential / account / permission / provider prevented execution. |
| `NOT_AVAILABLE` | The required product behavior is not implemented. |

**A journey proves only the paths it actually exercised.** Never copy a green
result across file formats, platforms, providers, or failure branches.

**Never pass a journey because a process started or a file exists.** Verify the
intended input was processed and the artifact is non-empty, structurally
usable, and relevant to the request.

### Triaging an old atomic failure against a passing journey

1. Affects a core step, data integrity, privacy, security, or truthfulness of
   the result → journey is `FAIL`.
2. Real edge case / unexercised variant → `PASS_WITH_KNOWN_LIMITATIONS`; keep
   the limitation recorded.
3. Broken fixture / runner / path assumption / wrong expected result →
   **quarantine or repair the test**. Not a product failure.
4. Journey didn't exercise it → `NOT_TESTED`. Never infer a pass.

### Test execution mechanics

- Prefer the repo `.venv` and the existing suite runner.
- Parallel pytest runs need **unique `--basetemp` and cache dirs**.
- **Never redirect logs into the same `--basetemp` dir.**
- Sandbox homes for install/uninstall/privacy/config tests.
- Record exact commands, exit codes, durations, output tails, and
  `repo_head` (`git rev-parse HEAD`).
- An assertion failure is `FAIL`. A broken fixture is repaired and rerun, not
  mislabeled as an environment block.
- A Unix-only path in a cross-platform test is a **test portability defect**
  first, unless the requirement is explicitly platform-specific.
- Live-provider tests need explicit user authorization and must never print,
  archive, or commit credentials.

## Parallel agents & shared artifacts

**This repo commonly has a dirty worktree and concurrent agents.** Preserve
changes outside your assigned scope. Inspect `git status` and current ownership
before editing.

Only the **explicitly assigned integration owner** may edit or regenerate:

- `tests/platform/phase22/atomic_feature_matrix.json`
- the Phase 22 matrix/workbook generators and validators
- `docs/integrations/autosci/phase-22-test-report.xlsx`
- `docs/integrations/autosci/phase-22-progress-log.md`
- `docs/integrations/autosci/phase-22-journey-test-report.md`
- the brief report

Worker agents write **only** their assigned journey tests, fixtures, and
isolated results, at `.codex-tmp/phase22-worker-results/<batch-id>/result.json`.

Every accepted test, status change, report sync, repair, superseded decision,
and remaining blocker gets appended to `phase-22-progress-log.md` — by the
integration owner, after review. **Do not claim a report is synchronized**
unless both the progress-log entry and report validation exist.

## Worker quality gate (before handoff)

- Assigned journey/diagnostic IDs present exactly once
- Tests exercise production behavior with defensible assertions
- All claimed executable tests were **actually run**
- Failures separated into product / test-runner / platform-provider /
  not-implemented causes
- Outputs and limitations recorded truthfully
- `git diff --check` passes
- No credentials, `.env` contents, Excel lock files, local output copies, or
  scratch artifacts staged

Final message must state: what changed, what was run, exact counts, remaining
limitations, isolated result path.

## Verification commands

Match the gate to what you changed:

```bash
git diff --check
bash scripts/check-privacy.sh
bash scripts/check-installed-clean.sh
bash scripts/smoke-install-matrix.sh minimal
bash scripts/release-cut.sh --source HEAD

# harness runtime launch work:
bash scripts/check-harness-plumbing.sh
```

`check-harness-plumbing.sh` is **deterministic plumbing**, not live Claude
behavior. It verifies install/layout/preflight/coordinator and dispatch
artifact plumbing **without consuming Claude quota** — use it freely. Live
panes and real delegation results still need manual verification when auth and
quota are available.

There are ~50 gates in `scripts/`; `check-*.sh` are gates, `smoke-*` are smoke
tests. Worth `ls scripts/` before inventing your own verification.

## Release safety

Before any public cut: release dry run must pass and **gitleaks must actually
run**. The release cut is a **manual owner action** — do not create orphan
branches, push release refs, or publish assets from an ordinary cleanup task.
