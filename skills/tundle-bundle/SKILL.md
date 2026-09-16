---
name: tundle-bundle
description: Keep a tundle, a git-backed transfer folder (VERSION + CHANGELOG.md + content) copied between devices, with the tundlekit bundle commands. Covers the latest-only rule, the status, release, compare and copy cycle, clearing git history (when, how, and what is or is not approved to clear), lint and verify, setup/ README tables and SOURCE.md files. Use when creating, updating, checking, comparing, copying or pruning a tundle or any folder that holds VERSION and CHANGELOG.md, or when adding installers under setup/.
---

# Keeping a tundle

A **tundle** is a folder under git that holds `VERSION` (like `2026.09.15.1`: date, then a counter for that
day), a `CHANGELOG.md` with a `<!-- entries -->` marker line, and content (papers, reports, notes, installers).
It is copied whole to other devices (phone, Windows, Linux). It keeps only the **latest version** of each file,
for **reading** and for **setting up**. Real work happens elsewhere.

`tundlekit bundle ...` replaces the old `tools/tundle.sh` / `tools/tundle.ps1` scripts on any OS and keeps the
same on-disk formats, so both can run on the same tundle. All commands find the tundle by walking up from the
current directory to the first folder holding both `VERSION` and `CHANGELOG.md`; pass `--root PATH` to be explicit.
Add `--json` to any command for a machine-readable result.

| Task | CLI | MCP tool |
|---|---|---|
| version, history length, sizes, pending changes, largest files | `tundlekit bundle status` | `bundle_status` |
| stage everything, bump VERSION, add a CHANGELOG entry, commit | `tundlekit bundle release "SUMMARY"` | `bundle_release` |
| which of 2 copies is newer | `tundlekit bundle compare OTHER` | `bundle_compare` |
| keep only the newest KEEP versions (dry run without `--yes`) | `tundlekit bundle prune [KEEP] [--yes]` | `bundle_prune` |
| start a new tundle | `tundlekit bundle init [PATH]` | `bundle_init` |
| names, junk, copies, setup tables, VERSION/CHANGELOG | `tundlekit bundle lint` | `bundle_lint` |
| SOURCE.md checksums | `tundlekit bundle verify` | `bundle_verify` |
| draft a SOURCE.md for an installer (hash, program, version guessed) | `tundlekit bundle source FILE [--url URL] [--install CMD] [--write] [--force]` | `bundle_source` |
| add missing rows to a setup folder's README table | `tundlekit bundle setup-table DIR [--write]` | `bundle_setup_table` |

## Rules

- **Latest only.** Replace a file instead of adding `v2`, `final`, `(new)`, `copy` or `backup` copies. Git keeps
  the last few versions. The only place for older snapshots is a topic's `versions/` folder.
- **Reading and setup material, not work trees.** No caches, build output, virtualenvs or `node_modules`.
- **One device edits at a time.** Before changing anything, check that this copy is the newest (`compare`).
  When done, `release`, then copy the whole folder to the other devices.
- **Filenames must work everywhere.** No `: * ? " < > |`, no trailing space or dot, no Windows reserved names
  (`CON`, `PRN`, `AUX`, `NUL`, `COM1`..`COM9`, `LPT1`..`LPT9`), and keep paths short (lint warns over 160 chars).
- **Each topic is a top-level folder with a `README.md`** that says where to start.
- **Never merge 2 copies by hand**, and never `git pull` between copies. The newer copy replaces the older one.

## The update cycle

1. **Check you are on the newest copy.**
   ```
   tundlekit bundle compare /path/to/other/tundle
   ```
   Result `same`, `this_newer` or `other_newer`. If the other copy is newer, copy it over this one first.
2. **Look at the state.**
   ```
   tundlekit bundle status
   ```
   Shows `version`, `history` (number of versions kept in git), content and `.git` sizes, pending changes and the
   5 largest files. `prune_hint` is true when history is over 10.
3. **Edit** the content (replace files, never add copies).
4. **Lint** before releasing and fix every error:
   ```
   tundlekit bundle lint
   tundlekit bundle verify
   ```
5. **Release** with a 1-line summary of what changed:
   ```
   tundlekit bundle release "Added X; replaced Y"
   ```
   This runs `git add -A`, counts added/modified/removed/renamed files, writes the new `VERSION`
   (`today.1`, or `today.N+1` on the same day; never lower than the old version even if the clock is behind),
   inserts a `## {version}  ({date time})` entry after `<!-- entries -->`, and commits as `tundle {version}: {summary}`.
   It fails with `nothing to release` when nothing changed, and when the marker line is missing.
6. **Copy** the **whole** folder, including the hidden `.git`, to the other devices, replacing older copies.
   If git reports "dubious ownership" (phone storage, USB drives, copies made by another user):
   ```
   git config --global --add safe.directory "<full path to tundle>"
   ```

The release uses git's configured identity. Set `user.name` and `user.email` first on a fresh device.

## Starting a tundle

```
tundlekit bundle init path/to/new-tundle
```

Creates the folder, runs `git init` on branch `main`, and writes `VERSION` (`today.0`), a `CHANGELOG.md` with
`# Changelog` and the marker, a `.gitignore` with the junk patterns and a `.gitattributes` with `* -text`
(no line-ending conversion). No commit is made. The first release produces `today.1`.

## Clearing git history

Git keeps a full copy of every changed file per version, and PDFs, Office files and installers barely
compress, so `.git` grows by about the size of whatever changed. Keep **the newest 5 versions**.

**Clear when any of these is true**

- `status` shows more than 10 versions (`release` reminds you: `prune_hint`)
- `.git` is bigger than the content (`status` shows both: `git_bytes` vs `content_bytes`)
- the phone or a device is short on space
- a large file (installer, batch of papers) was just removed or replaced; the old copy stays in `.git` until
  history is cleared

**How**

1. Work on the **newest** copy (`tundlekit bundle compare OTHER` if unsure).
2. Release pending changes first. Prune refuses to run with unreleased changes, and with more than 1 branch.
3. Dry run, which lists kept and dropped versions and changes nothing:
   ```
   tundlekit bundle prune
   ```
4. Clear, keeping 5 (or pass a number, e.g. 3; the minimum is 1):
   ```
   tundlekit bundle prune --yes
   tundlekit bundle prune 3 --yes
   ```
   The newest KEEP commits are rebuilt on a new root with the same trees, messages, authors and dates; tags,
   stashes, `refs/original` and reflogs are removed, and `git gc --prune=now` deletes dropped versions for good.
   Files, `VERSION` and `CHANGELOG.md` stay exactly as they are.
5. **Replace every other copy with this one.** Their history no longer matches. Copy the folder over them;
   do not `git pull`.

**Approved for clearing (no need to ask)**

- git history older than the newest 5 versions; fewer (down to 1) is fine when space is tight
- reflog entries, unreachable objects, tags, stashes and leftover `refs/original`
- caches and leftovers matched by `.gitignore`: `__pycache__`, `.pytest_cache`, Office lock files `~$*`,
  `Thumbs.db`, `.DS_Store`
- superseded snapshots in a topic's `versions/` folder, as long as the newest snapshot of each document stays
- an older tundle copy on another device, **after** the newer copy is fully copied there and `compare` confirms it

**Not approved (ask the owner first)**

- any file in the current version: papers, reports, notes, installers
- `VERSION`, or entries in `CHANGELOG.md`
- clearing history on a copy with unreleased changes, or on a copy that is not the newest
- deleting the `.git` folder (it removes version control, and copies can no longer be compared)

## Lint rules (`tundlekit bundle lint`)

Result: `ok`, `findings` (`rule`, `severity`, `path`, `line`, `message`), `counts`, `files`. Exit 1 on errors;
`--strict` also fails on warnings. Options: `--max-path` (default 160), `--large-mb` (default 500).

`--ignore` (repeatable, also on `verify`) drops accepted findings: `--ignore B011` drops a rule everywhere,
`--ignore "B003:ai4research/versions/*"` drops it for paths matching the glob (relative, `/`-separated).
Use it for findings that are deliberate, and say why in the tundle's README, rather than living with noise:

```
tundlekit bundle lint --ignore B011 --ignore "B009:setup/*"
```

Links (symlinks, junctions) are never followed: each counts as 1 entry.

| Rule | Severity | Meaning and fix |
|---|---|---|
| B001 | error | name not portable (`: * ? " < > \|`, control chars, trailing space/dot, reserved name). Rename |
| B002 | warning | relative path too long. Shorten folder or file names |
| B003 | warning | copy/version marker in a name (`report v2.docx`, `x (1).pdf`, `y - Copy.txt`, `final`, `old`, `backup`) outside `versions/`. Replace the original instead |
| B004 | info | several snapshots of 1 document in `versions/`. Older ones may be cleared; keep the newest |
| B005 | warning | junk: `__pycache__`, `.pytest_cache`, `.venv`, `venv`, `node_modules`, `.ipynb_checkpoints`, `*.pyc`, `*.tmp`, `~$*`, `Thumbs.db`, `desktop.ini`, `.DS_Store`, `._*`. Delete. Reported as info when `.gitignore` already skips it: git ignores it, but a copied folder still carries it |
| B006 | error | a file or folder in `setup/<dir>/` missing from that folder's `README.md` table. Add a row |
| B007 | error | a `setup/<dir>/README.md` row naming something that does not exist. Fix or remove the row |
| B008 | warning | top-level folder without `README.md` |
| B009 | warning | `X.pdf` older than its `X.docx`/`X.pptx` source. Re-export the PDF |
| B010 | error | `VERSION` or `CHANGELOG.md` missing/malformed, or the newest entry does not match VERSION |
| B011 | info | very large file. Consider whether it belongs, and clear history after replacing it |
| B012 | error | `SOURCE.md` checksum mismatch |
| B013 | warning | `SOURCE.md` whose hash or target file cannot be determined, or whose `- File:` points outside the tundle |
| B014 | info | number of installers under `setup/<dir>/` with no `SOURCE.md` next to them. Draft them with `bundle source` |

## setup/: installers, tables and SOURCE.md

```
setup/windows/    Windows installers (.exe, .msi)
setup/linux/      Linux installers, tarballs and ISOs (.run, .tar.gz, .deb, .iso)
setup/any/        runs on both: scripts, Python wheels, portable archives (create when needed)
```

- Put the installer straight in the OS folder, named with its version (`python-3.13.5-amd64.exe`). A program
  that needs several files gets a folder `<program>-<version>/`.
- **List every file and subfolder in that folder's `README.md` table** (`tundlekit bundle setup-table DIR` drafts
  the missing rows, see below). The first cell names the entry in
  backticks; a folder is written with a trailing slash:
  ```
  | File | Installs | Notes |
  |---|---|---|
  | `python-3.13.5-amd64.exe` | Python 3.13.5 x64 | offline |
  | `ChromeSetup.exe` | Google Chrome (stub) | ⚠ downloads at install time |
  | `tool-1.2/` | Tool 1.2, installer plus licence | see SOURCE.md inside |
  ```
- Prefer offline installers; mark stub installers with ⚠. Match the architecture (x64 / arm64).
- Latest version only: replace the old installer, then clear history when convenient.
- Watch the size: a 3 GB ISO costs about 3 GB again in `.git` while its version stays in history.
- For licensed software, or a download worth verifying again, add a `SOURCE.md` next to it:
  ```
  # <program> <version>
  - Source:     <official download URL>
  - Downloaded: YYYY-MM-DD
  - SHA-256:    <64 hex characters>
  - File:       <file name, needed when the folder holds more than 1 file>
  - Install:    <steps, or the silent/unattended command>
  ```
  Draft it instead of typing the hash: `tundlekit bundle source FILE` prints the text (program and version guessed
  from the file name, architecture tokens such as `x64` removed, SHA-256 and download date filled in); add
  `--url URL --install "CMD" --write` to write it (`--force` to overwrite an existing one). Check the guessed program
  and version, and replace any `<official download URL>` or `<steps>` placeholder. By hand, get the hash with
  `Get-FileHash <file>` (Windows) or `sha256sum <file>` (Linux). Then check it:
  ```
  tundlekit bundle verify
  ```
  `verify` compares every recorded hash with the file (case-insensitive). Without a `- File:` line, the target
  is the only other file in the folder besides `README.md` and `SOURCE.md`. A placeholder like `<hash>` is
  reported as "no hash recorded" (B013).

## Filling in a setup folder quickly

```
tundlekit bundle lint                                   # B006 lists unlisted files, B014 counts missing SOURCE.md
tundlekit bundle setup-table setup/windows              # dry run: the rows it would add
tundlekit bundle setup-table setup/windows --write      # append them to setup/windows/README.md
tundlekit bundle source setup/windows/python-3.13.5-amd64.exe --url https://www.python.org/downloads/ --write
tundlekit bundle verify
```

`setup-table` adds 1 row per unlisted entry (`` | `name` | {program} {version} | ``) after the last row of the
first table, or creates the table; existing rows are untouched. Stub installers (a name with `Setup`, `Installer`,
`Loader` or `latest` and no version) get "⚠ check: may download during install". Edit the guessed descriptions
afterwards; they come from the file name only.

## Checklist before handing a copy on

- [ ] `tundlekit bundle compare OTHER` says this copy is newest (or same)
- [ ] `tundlekit bundle lint` and `tundlekit bundle verify` report no errors
- [ ] `tundlekit bundle release "..."` done; `status` shows `changes: none`
- [ ] history ≤ 10 versions, or pruned per the rules above
- [ ] the whole folder, including `.git`, copied over the older copies
