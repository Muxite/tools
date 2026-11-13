# 20261113 Satay Recovery Guide prepresentation

Use the internal Linux filesystem for repositories, live queue state and SQLite. Danta is supplementary storage only; this change does not mount or write it. Keep a remote Git checkpoint and a second verified artifact copy because a flash drive attached to the same host is not independent power-loss protection.

## Queue and reboot behavior

Install or reinstall only while the queue is idle with `python3 ~/tools/TRANSFER/satay-recovery/install_service.py`; it refuses a takeover while jobs are queued/running. The existing queue is supervised by `satay-jobq.service`, a systemd user service. It restarts after a worker crash, with at most five starts per five minutes. Existing runners survive a worker restart; reconciliation occurs before dispatch, without automatically replaying an interrupted job. A host reboot marks old running jobs failed and dependent jobs skipped. Builds and GPU jobs remain mutually exclusive. No inference jobs are started by installation.

New records include boot identity, kernel process-generation ticks and monotonic start time. Reconciliation never signals a process ID from a previous boot or a different recorded generation. Timeouts do not depend on the wall clock, which can jump on Satay. Job state is flushed before atomic replacement; directory entries and event records are flushed too. These reduce loss risk but do not guarantee hardware power-loss durability.

Legacy records that still say running without boot identity block reconciliation for manual inspection. Do not retry them until processes, image builds and labelled containers have been examined. Do not rewrite historical completed evidence.

```sh
systemctl --user status satay-jobq.service
journalctl --user -u satay-jobq.service -n 40 --no-pager
~/projects/siminfeng/bin/jobq list
~/projects/siminfeng/bin/jobq reap-containers --dry-run
```

Stopping the service stops admission, not running commands. Use `jobq cancel JOB_ID` and wait for the recorded terminal state to cancel work. Preview stale containers before removing any. Unknown effects are not permission to rerun.

**Boot prerequisite:** `loginctl show-user muk -p Linger` must say `Linger=yes` for unattended startup without a login. If it says no, an administrator must run `sudo loginctl enable-linger muk`. The user service alone does not establish boot-without-login recovery. Do not reboot the shared machine just to test this during demo preparation.

If the service exhausts its restart limit, inspect the journal and resolve the error, then `systemctl --user reset-failed satay-jobq` and `systemctl --user start satay-jobq`. Do not create an unbounded restart loop.

## Private checkpoint and later supplementary copy

Run `python3 ~/tools/TRANSFER/satay-recovery/checkpoint.py --destination ~/backup/factory-checkpoints` after coherent factory milestones. The helper uses SQLite's online backup API, checks both databases and atomically publishes a checksum manifest. It whitelists `factory.sqlite` and `ccstore/calls.sqlite`; it excludes agent homes, credentials, environment files and sessions. Database contents can still include prompts, paths and user-supplied text. Keep snapshots private and out of Git and public packages.

Each database is internally consistent; the two copies are not a cross-database transaction. Take a final snapshot with the factory idle before a coordinated restore. This is a state checkpoint, not a complete restore: worktrees, artifact files, model/image dependencies and selected job evidence must also be preserved by the portable package or separate verified copies. Never overwrite a live database. Restore into a separate internal-filesystem recovery location, verify hashes and inspect referenced artifacts before resuming.

For a later Danta copy, first identify the intended device by label and UUID with `lsblk -f`; never assume `/dev/sda1`. Have the user mount it, copy only completed snapshot directories and the portable ZIP, then recompute every manifest hash at the destination. Never run a live SQLite database from exFAT. No Danta copy is performed by this helper.

## Milestone source and artifact recovery

Keep changes scoped by repository: queue/lab code in siminfeng, generic checkpoint helpers here, factory/capsule logic in JiuwenSwarm. Review `git status` and explicit paths before committing. Never add queue environment files or agent auth/session directories. Commit a coherent stage, push fast-forward, then verify the remote head. Do not move published tags.

If a push fails, preserve the local commit and a self-contained Git bundle on internal storage, record the intended remote and branch, and retry later with a bounded attempt count. Do not reset or force-push over remote work. A local commit is not an off-machine backup. Keep the previous known-good replay and evidence intact while packaging a replacement.

An interrupted Codex/factory session must resume from recorded task state, observations and source/image identities. Do not assume an absent chat process means an absent build or container. The portable handoff supplies the new session's context; factory resume creates a new agent session with recovery context.

## Verification boundary

Queue tests use isolated temporary queues, lightweight subprocesses and a fake operation wrapper: worker interruption without duplicate execution, runner interruption and subsequent admission, previous-boot PID reuse protection, and a simulated wall-clock jump. These establish queue behavior, not an inference or physical power-cut result. The SQLite helper is checked with temporary fixture databases and a private live snapshot, not by overwriting the current runtime.

### Actual checks on Satay, 2026-11-13

- Queue integration suite: 17 passed in 26.99 seconds, isolated queues only.
- Checkpoint fixture suite: 2 passed; hashes and restored fixture contents match; auth-file exclusion and failed-snapshot cleanup checked.
- One private live snapshot created under `~/backup/factory-checkpoints/`, with both SQLite integrity checks passing. It is not included in Git or the public demo package.
- While the production queue was idle, the service's main worker was killed once. systemd restarted it automatically (restart count 0 to 1), with no jobs dispatched and no tmux sessions stopped.
- Current boot limitation: `Linger=no`; no sudo credentials were available, so boot-without-login startup remains unqualified and needs the one administrator command above.
- No model runs, hardware builds, reboot, Danta writes or tag changes were performed for these checks.
