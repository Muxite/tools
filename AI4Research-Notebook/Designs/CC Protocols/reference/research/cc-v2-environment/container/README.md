---
id: cc-v2-container-probe
status: blocked-image-native-passed
source: November 4 native and Docker Desktop feasibility probe records
last_reviewed: 2026-11-04
next_action: Restore Docker Desktop engine health, then rerun probe.py and the Host image call.
---
# Portable worker feasibility probe

The same [`tool.py`](../../../examples/portable/tool.py) processes one JSON packet
on stdin and emits one result on stdout. It uses only the Python standard library.
The native declaration is `cc.yaml`; `image.yaml` selects an immutable official
Python registry manifest and runs the worker from the read-only bundle mount.

**Observed on 2026-11-04:** all four direct native cases passed: ASCII trimming,
preserved non-ASCII whitespace, a successful empty output map, and nested JSON
echo. The real Docker run failed before executing the worker. Native/image result
equivalence is **not established**. See [`probe-report.json`](probe-report.json)
for command vectors, packets, outputs, exit codes, and exact stderr.

Docker Desktop was launched hidden. Its backend failed while renaming
`sailor-ingest.sock` to `sailor-ingest.sock.stale` (system could not access the
file). The Linux engine pipe remained absent. The exact startup error is in
[`docker-startup-error.txt`](docker-startup-error.txt). No reset, global
configuration change, or Windows service stop was performed. A supported
`docker desktop restart --timeout 30` attempt hung beyond its timeout. Only the
verified Desktop process tree created by this probe and its hung CLI helpers were
stopped; a second hidden launch failed with the same socket rename error.

The Docker registry was reachable: `docker manifest inspect --verbose
python:3.12-slim` resolved the linux/amd64 manifest to
`sha256:1148dbb014615300fa7e713b2f94f550c0d1c69780c0805f84f093ceee34dd0b`.
[`base-image-manifest.json`](base-image-manifest.json) preserves registry identity,
platform, layers, and config digest. This is registry evidence, not a local pull,
build, or execution receipt. An actual `docker build --platform linux/amd64 -t
cc-v2-portable-probe:local <portable-directory>` was attempted and failed because
the engine pipe was absent; see [`build-attempt.json`](build-attempt.json).
No local image identity was produced.

The pinned [`Dockerfile`](../../../examples/portable/Dockerfile) is ready for a
later local build. `image.yaml` deliberately references the independently resolved
registry image, not a fictitious built image ID. The bundle mount supplies the
same worker bytes for native and image calls.

Run `python probe.py` from this directory after engine recovery. The script
records new observations; it does not repair Docker. Its image command uses no
shell, disables network access, makes the root filesystem read-only, mounts
`/cc/bundle` and `/cc/in` read-only and `/cc/out` read-write, and passes no resource
mounts. The native call is a trusted local process; this probe is not evidence of
native isolation or cross-machine reproducibility.

## Reference Host integration

`host_probe.py <evidence-directory>` seals and calls this worker through `ccv2.Host`,
including an output artifact. Actual Host evidence is stored outside the reference
tree at `C:/Users/m50066326/huawei/research/cc-v2-environment/container/`, including
`host-probe-report.json`, the release/attempt/artifact store, and the second Docker
startup error. Four native capabilities succeeded, and returned artifact UTF-8
bytes and SHA-256 matched. The image Host attempt returned `failed/PROCESS_FAILED`
because Docker did not execute a worker; its attempt stderr preserves the missing
engine pipe error. Host native/image equivalence remains unverified.

The initial artifact attempt exposed Windows newline translation in `write_text`.
The worker now writes explicit UTF-8 bytes; the subsequent actual Host artifact
comparison passed. Both attempt records remain in the evidence store.
