---
id: amendment-ar-evidence
status: source-snapshot
source: M1 source commit d3d7f565c6c05ccf764fe0780fde149b7dc89b95
last_reviewed: 2026-10-21
next_action: Recheck receipts at coding checkout
---
# Portable evidence snapshot

Source excerpts are from M1 source commit `d3d7f565c6c05ccf764fe0780fde149b7dc89b95`, not a deployment claim. SHA-256 covers each complete source blob.

## Restricted executor (`jiuwenswarm/research/executor.py:212-239`)

SHA-256: `8ef028d328601bb5ac1f7c8218dc1daff916b26b0222016a6f62e4e5b70a9c90`

```python
command = [bwrap, "--unshare-all", "--unshare-user", "--die-with-parent", "--new-session", "--clearenv",
           "--uid", str(uid), "--gid", str(gid), "--cap-drop", "ALL",
           "--ro-bind", "/usr", "/usr", "--ro-bind", "/usr/local", "/usr/local",
           "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
           "--bind", str(work), "/workspace/poc", "--chdir", "/workspace/poc"]
```

The complete source also constrains executable, resource mounts and verified environment; read the source at the recorded commit when implementing.

## Application container (`deploy/m1/compose.yaml:2-15,28-44`)

SHA-256: `29e84630ab48ca382e40a12b28752aa910fa8e8a5c07327483f0c76d6725b87a`

```yaml
app:
  read_only: true
  cap_drop: [ALL]
  cap_add: [SETUID, SETGID, CHOWN, FOWNER, DAC_OVERRIDE, KILL]
  security_opt: [no-new-privileges:true, seccomp=...]
  ports: [{target: 5173, published: '5173', host_ip: 127.0.0.1}]
  volumes: [protected config:ro, state, accounts, ipc, poc, inputs, executor]
```

M1 is already packaged as a whole application container. This proposal scopes any additional container experiment to a single stateless carrier and does not create one app container per CC.
