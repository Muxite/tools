---
id: resource-migration-backup
status: active
source: Resources/tools/migrate.py; Resources/review-batches/personal-collections-and-readiness.md
last_reviewed: 2026-10-20
next_action: Back up the vault and separately retain linked source repositories and large artifacts
---
# Migration and backup

**October 21 refresh:** classification now uses [the explicit source registry](migration/source-collections.json), including both preserved and captured M1 worktrees. Longest directory-boundary prefix wins; unknown sources remain historical/personal. Source roles do not imply approval. [Previous manifests](migration/history) retain earlier receipts; old archive bytes are not removed by refresh. See [[Resources/Library Completeness]] for semantic coverage rather than treating indexing as understanding.

The migration is non-destructive: original files remain in place. [[Resources/Source Collections]] maps each inventoried item to an exact archived copy, an original link, a byte-identical duplicate, an exclusion, or a review condition.

## What is consolidated

Personal notes and selected frozen Office/PDF artifacts are copied byte-for-byte into `Archive/Imported`, identified by content hashes. Maintained code/design sources and large artifacts stay linked. Source files are never moved, renamed, deleted, or rewritten by the migration.

The inventory covers workspace collections outside explicit directory boundaries. Dependencies, caches, private tool state, and reference repositories have boundary records; their descendants are not counted as individually inventoried files. Personal output and feature-list collections inside the archived AI4Research clone receive a separate pass. Potential credential files and detected secret patterns are excluded. Classification is partly rule-based, so a file's `indexed` state is not a claim that its contents were reviewed.

Archived Markdown retains original bytes. Its old relative links may not resolve from a content-addressed snapshot; open its original path or use the source map to find related files. The vault's authored pages provide maintained navigation.

## Migration records

- [Manifest](migration/manifest.jsonl): original relative path, size, modification time, SHA-256, disposition, destination, source role, and review state.
- [Summary](migration/summary.json): totals, collection coverage, and exclusions.
- [[Resources/review-batches/personal-collections-and-readiness|Bounded source review]]: reviewed entrypoints, authority conflicts, candidate versions, and evidence limits.
- [Migration script](tools/migrate.py): deterministic classification rules and byte verification. Run `python Resources/tools/migrate.py` from the vault to refresh; inspect changes before committing. Refresh does not remove old archived bytes.
- [Byte-restoration tool](tools/restore_archive_bytes.py): repairs a changed archive copy only if the original still matches its recorded hash. The initial integrity review found and restored line-ending conversions; originals were unchanged.

Cheap agents operate on bounded named collections, write draft findings to separate owned folders, and do not modify originals. Central review resolves source authority and conflicting interpretations. This implementation used `gpt-6-luna`; no monetary savings amount is asserted.

## Backup and restore

Local Git retains text changes. Attachments, linked repositories, large datasets, and lab state need backup beyond Git. The vault's `.gitignore` excludes runtime state, caches, and binary attachments from text history.

Use [backup.py](tools/backup.py) to produce a ZIP and SHA-256 receipt in a separate local backup directory. The ZIP includes vault text and archive attachments, while excluding local Git internals, transient lab state, caches, and files whose names indicate credentials. Git history remains in the vault's `.git` directory; this ZIP is for a separate file-level restore. It also includes the manifest identifying external linked sources. That manifest is an inventory, not a backup of their contents.

```powershell
python Resources/tools/backup.py --destination D:\Backups\AI4Research
python Resources/tools/backup.py --verify D:\Backups\AI4Research\VAULT_BACKUP.zip
```

Use an actual available destination; the example does not assume a `D:` drive exists. Back up linked repositories and large artifacts separately, including their uncommitted work. For restore, verify the ZIP, extract to a new empty folder, open that folder in Obsidian, and remap linked source paths from the manifest if the workspace location changed. Keep the current vault until the restored copy has been checked.

This setup documents and tests the backup mechanism. It does not claim an off-device backup exists.
