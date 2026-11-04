# Clearing git history

tundle only needs a short history: **the newest 5 versions**. Every version keeps its own copy
of each changed file inside `.git`, and PDFs, Office files and installers barely compress, so
old versions pile up quickly.

## When to clear

Clear when **any** of these is true:

- `tools/tundle.sh status` shows **more than 10 versions** (`release` reminds you).
- `.git` is **bigger than the content** (`status` shows both).
- The phone or a device is **short on space**.
- You just **removed or replaced a large file**, such as an installer or a batch of papers. The old copy
  stays in `.git` until history is cleared.

## How

1. Work on the **newest** copy. If unsure, run `tools/tundle.sh compare <other copy>`.
2. **Release** any pending changes first: `tools/tundle.sh release "..."`. Prune refuses to
   run while there are unreleased changes.
3. **Dry run**: `tools/tundle.sh prune`. This lists which versions are kept and which are dropped. Nothing changes yet.
4. **Clear**: `tools/tundle.sh prune --yes` keeps 5. Use `prune 3 --yes` to keep 3.
   On Windows: `.\tools\tundle.ps1 prune --yes`.
5. **Replace the other copies** with this one. Their history no longer matches, so copy the
   folder over them. Don't `git pull` between copies.

Prune keeps the files, `VERSION` and `CHANGELOG.md` exactly as they are. It only rewrites the
history behind them, then deletes the dropped versions for good (`git gc`).

## Approved for clearing (no need to ask)

- Git history older than the newest **5** versions. Keeping fewer (down to 1) is fine when space is tight.
- Reflog entries, unreachable objects, tags, stashes and leftover `refs/original`. Prune removes all of these.
- Caches and work leftovers matched by `.gitignore`: `__pycache__`, `.pytest_cache`, Office lock
  files `~$*`, `Thumbs.db`, `.DS_Store`.
- Superseded snapshots in a topic's `versions/` folder, as long as **the newest snapshot of each
  document stays**.
- An older tundle copy on another device, **after** the newer copy has been fully copied there
  and `compare` confirms it.

## Not approved (ask first)

- Any file in the current version: papers, reports, notes, installers.
- `VERSION` or entries in `CHANGELOG.md`.
- Clearing history on a copy that has **unreleased changes**, or on a copy that **isn't the newest**.
- Deleting the `.git` folder. That removes version control entirely, and later copies can no longer be compared by history.
