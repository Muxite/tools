---
id: resource-lab-host-validation
status: proposed
source: Resources/lab/README.md
last_reviewed: 2026-10-20
next_action: Execute this runbook on a host with a running Linux Docker engine
---
# Validate the lab on a real host

This runbook supplies the missing real-container evidence. Unit tests alone do not demonstrate runtime isolation. Use disposable synthetic inputs and a test repository before connecting the actual M1 candidate.

## Prepare

Select a Linux image available by immutable digest, with `/bin/sh` and standard file utilities. Record the digest and Docker/host versions. Pin a clean test repository commit. Keep lab state, live evidence, and source repository in distinct directories outside this vault. Copy the [example manifest](lab/example-manifest.json) into a job directory and replace every placeholder.

Create two manifests named `isolation-a` and `isolation-b`, each with memory `256m`, CPU `0.5`, and process limit `64`. Use this command array for A, and replace `A` with `B` for B:

```json
["/bin/sh", "-c", "printf 'A' > /evidence/marker.txt; printf 'A' > /workdata/volume-marker.txt; sleep 60"]
```

The shell command is deliberately a synthetic container workload. The manager invokes Docker through argument arrays. No source credentials are needed.

## Run and inspect

Use `python Resources/lab/lab.py --root PATH` followed by each operation. Record exact commands and outputs in an experiment note.

1. `create` both manifests. Confirm different worktrees, container/network/volume names, and evidence directories.
2. `start` both. While both are running, `inspect` each and confirm distinct mounts, resource limits, owner labels, and pinned image identity. Confirm the source mount is read-only and no Docker socket or foreign evidence mount exists.
3. Create a third manifest with `scheduling.exclusive: true`. Starting it while either run is active must fail. After both runs stop, start the exclusive job and verify an ordinary job cannot overlap it.
4. `stop` both initial jobs, `export` each, then verify exported marker values are A and B respectively, including `/workdata` markers. Export manifests, logs, provenance, and checksums must be present.
5. `cleanup` both. Confirm containers, named volumes, networks, and worktrees are gone while both exports remain intact.

## Failure and recovery checks

On new disposable IDs, interrupt the manager after provisioning has begun and use `reconcile` to determine whether a container exists or is running. Reconciliation must not replay a completed job. Stop, export, and clean it explicitly.

Before export, cleanup must refuse. A running container must not export as complete. Alter one exported file and verify cleanup refuses on checksum mismatch. Make a source-worktree edit and verify export/cleanup refuse without deleting the edit. Restore only your intentional test changes, then repeat.

## Evidence and next gate

Store manifest hashes, pinned commits/images, host inventory, command transcripts, redacted inspections, expected versus observed outcomes, and export checksums. Mark each case passed, failed, or unrun. After the synthetic checks pass, repeat lifecycle checks using the reconciled AI4Research image and supported entrypoint.

GPU exposure is not implemented by this prototype. GB10 device access, workload performance, and concurrent GPU attribution require a separate extension and host validation.
