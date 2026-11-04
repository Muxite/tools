# Single-host experiment lab prototype

This standard-library Python CLI demonstrates an operator-driven finite Docker experiment lifecycle. It follows the sidecar boundary: the host owns Docker access, jobs use disposable labeled resources, evidence is retained, and the job container receives no Docker socket or daemon credentials. This remains a prototype rather than the architecture's privileged host executor.

## Requirements and manifest

Python 3.10+, Git and a running Docker daemon are required for real runs. Each manifest pins a full Git commit and image digest (`name@sha256:<64 hex>`), provides a nonempty command argument list, and sets positive Docker memory, CPU and process limits. The `experiment` value must be a simple identifier. Optional `scheduling.exclusive: true` prevents overlap with any other running experiment under the same lab root. Exclusive scheduling is enforced by the root's cross-process file lock and state ledger.

Relative repository, evidence-root, and env-file paths are resolved from the manifest's directory and stored as absolute paths, so later commands can run from another directory. Before removal, the resolved worktree must remain inside this lab's state root; symlink and junction worktrees are refused.

The lab creates a detached worktree per experiment, with one UUID-owned container, network and named volume. Each lab owner gets its own evidence subdirectory, preventing same-named jobs in different lab roots from colliding. The worktree is mounted read-only at `/workspace`. The external persistent evidence directory is mounted at `/evidence`; named-volume contents appear at `/workdata`. GPU access is not implemented. Disk quota, host CPU reservation, deadline supervision and monetary cost enforcement are also outside this prototype.

Credentials may be supplied through `env_file`, an explicit existing path outside the repository, worktree, lab state and evidence mounts. Docker reads that path directly; its contents are never copied into state or exports. Inspection redacts environment and command fields. Runtime logs may contain whatever the job itself writes, so the job command remains responsible for avoiding secret output. Container access to the Docker socket is never configured.

## Example

Copy and edit `example-manifest.json`, replacing the repository, commit, immutable image digest, evidence root and command. Keep any secret env file outside the repository and the evidence tree.

```powershell
python lab.py --root C:/lab/state create C:/lab/job.json
python lab.py --root C:/lab/state start smoke-test
python lab.py --root C:/lab/state inspect smoke-test
python lab.py --root C:/lab/state stop smoke-test
python lab.py --root C:/lab/state export smoke-test
python lab.py --root C:/lab/state cleanup smoke-test
```

All operations support `--dry-run`. The preview does not create the lab root, owner marker, lock, state or Docker resources. Experiments are one-shot: after stopping, create a new experiment identifier for another run. If the host crashes during start, deterministic names and UUID labels let `reconcile` record whether the container is running, stopped or absent. `stop` also reconciles before acting. A found but stopped container blocks retry so the same experiment is never silently replayed. A provisioning job with no container can be explicitly stopped, exported and cleaned up, or explicitly started again.

Export is a separate sibling directory outside the mounted evidence path. It requires the source worktree to remain at its pinned commit with no uncommitted or untracked changes. It snapshots persistent bind output and copies `/workdata` from the stopped container, then hashes and verifies the manifest, logs, provenance and artifacts. Cleanup rechecks those hashes, verifies Docker kind and owner labels, confirms the pinned worktree revision, and refuses a dirty worktree. It removes only resources owned by this lab and preserves the export. A crash mid-cleanup can be retried; already absent resources are accepted only when Docker explicitly reports that resource missing. Other inspection failures stop cleanup.

## Contribution recipe

The pinned `/workspace` checkout is read-only so each experiment keeps its source revision stable. For experimental edits, copy its tracked source into `/workdata/candidate` (leaving `.git` out), make changes and run the relevant tests there. Write test output to `/evidence/tests.txt`, then emit `/evidence/candidate.patch` by diffing `/workspace` against the candidate tree and `/evidence/change-manifest.json` with the pinned base revision, test command/results and patch checksum. Export captures both the evidence files and the full `/workdata` volume, so the patch, change manifest, test output and candidate tree travel together. Reviewers can apply the patch to the recorded base revision as a separate contribution; the prototype never writes edits back into the pinned checkout.

## Verification

Run `python -m unittest -v` in this directory. Tests use a stateful fake Docker runner, temporary paths and a real temporary Git repository. They cover trimmed Git revision output, pin validation, non-mutating previews, path traversal rejection, owner isolation, exclusive scheduling, recovery reconciliation, one-shot behavior, dirty worktree refusal, workdata export and checksums, cleanup safeguards, env/command redaction, and export failures. These tests do not validate real Docker behavior. Docker CLI may be installed while its daemon is unavailable.
