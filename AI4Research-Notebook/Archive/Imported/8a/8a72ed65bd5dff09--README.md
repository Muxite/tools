# tundle

A transfer bundle holding the latest papers, reports, notes and installers. It lives on
the phone and gets copied to any Windows or Linux device. The real work happens on each
machine; tundle only keeps the **latest version**, for **reading** and for **setting up**.

## Which copy is the latest?

Open `VERSION`. It looks like `2026.09.15.1` (date, then a counter for that day), and the higher
number is newer. It's plain text, so a phone can show it. `CHANGELOG.md` lists what changed in each version.

To compare two copies on a computer:

```
tools/tundle.sh compare /path/to/other/tundle          # Linux, or Git Bash on Windows
.\tools\tundle.ps1 compare D:\path\to\other\tundle     # Windows PowerShell
```

## Layout

```
tundle/
├── README.md            this file
├── VERSION              version of this copy
├── CHANGELOG.md         what changed, newest first
├── HISTORY-CLEANUP.md   when and how to clear git history, and what may be cleared
├── tools/               tundle.sh (bash) and tundle.ps1 (Windows wrapper); architecture_sync.py (lint for jiuwenswarm docs/architecture)
├── setup/               installers for setting up a device
│   ├── windows/
│   └── linux/
├── obby/                Obsidian vault: Muk's notes only. Start at README.md, then HANDOFF.md.
│                        The design itself lives only in jiuwenswarm docs/architecture (ai4r_main_branch)
│   ├── Reference/  Parked/  Archive/
├── ai4research/         AI4Research project: reports, decks, notes, papers. Capability Capsule is in
│                        ai4research/capability-capsule/
└── code/                snapshots of the code behind the deliverables, for reference (see below)
    ├── tundlekit/           the kit that builds the decks and keeps this tundle
    └── capsule-openjiuwen/  the Capability Capsule knowledge base, schema, and report and deck builders
```

`obby/` is a reading surface, not a second copy of the work. It holds one short note per idea with the
wiki-links between them, and it opens directly in Obsidian on a phone. The long notes with their file and line
evidence stay under `ai4research/notes/`.

Each topic gets its own top-level folder with a `README.md` that says where to start. Add new
topics next to `ai4research/`.

## Rules

- **Latest only.** Replace a file instead of adding `v2` / `final` / `(new)` copies. Git keeps
  the last few versions if you need to go back.
- **Reading and setup material, not work trees.** No caches, build output, virtualenvs or
  `node_modules`. `.gitignore` already skips the common ones.
- **Code travels as a snapshot.** `code/<name>/` is a read-only copy with a `SNAPSHOT.md` saying where it came
  from and at which commit. Never edit it here. Refresh it from the source with
  `tundlekit bundle snapshot <source> code/<name> --write` (the exact command is in each `SNAPSHOT.md`), then
  `release`. To use tundlekit on a new device, copy `code/tundlekit` out of the tundle first, then
  `pip install -e .[all]` in the copy, so no build files land in the tundle.
- **One device edits at a time.** Before changing anything, check that this copy is the
  newest (`compare`). When you're done, `release`, then copy the folder to the other devices.
- **Filenames must work everywhere.** Don't use `: * ? " < > |`, and keep paths short.

## Updating

```
tools/tundle.sh status                               # version, history length, sizes, pending changes
tools/tundle.sh release "Added X; replaced Y"        # bump VERSION, add a CHANGELOG entry, commit
```

On Windows, use the same commands through `.\tools\tundle.ps1`. It runs the bash script with Git for Windows.

## Copying to another device

Copy the **whole** `tundle` folder, including the hidden `.git` folder. If the device already has a
copy, run `compare` and replace the older one. Don't merge two copies by hand.

If git reports "dubious ownership", which is common on phone storage, USB drives, or a copy
made by another user, run:

```
git config --global --add safe.directory "<full path to tundle>"
```

## Size

Git keeps a copy of every version it remembers, and PDFs, Office files and installers barely
compress. So `.git` is about the size of the content plus whatever changed since.
`status` shows both sizes. [HISTORY-CLEANUP.md](HISTORY-CLEANUP.md) explains how to keep history short (5 versions).
