---
id: container-cc-initial-design
status: proposed-m2
source: Sources/Prompts/2026-10-21-docker-feasibility-review.txt; Sources/Prompts/2026-10-21-m2-scope-clarification.txt; Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt; Sources/Prompts/2026-10-23-m2-component-handoffs.txt
last_reviewed: 2026-10-26
next_action: Read the current Sandbox Lab Design and reconcile the affected M2 contracts before implementation
---
# M2 container capability capsules

**Current M2 reading route:** [[Designs/Sandbox Lab Design]] and [the seven-view diagram set](Sandbox%20Lab%20Diagrams/README.md) own the current sandbox proposal. Workload profiling is the first validation case; robotics is a non-blocking integration. The proposal separates CC factory ownership from whole-system RSI, supports multi-operation packages and automatic compatible local adoption, and treats VM deployment as a profile. The earlier details below remain useful only where compatible; rolling planning still needs agreement with its owner.

## October 23 implementation handoff

[[Resources/Handoffs/m2-labs/container-capsules|Current scoped handoff]] is the implementation route. Spark is primarily a restricted benchmark host; development/builds happen elsewhere where practical. The existing no-sudo two-image benchmark workflow stays independent. VMs, a registry, shared local inference and a full capacity controller are not bootstrap prerequisites. M2 infrastructure remains unimplemented by this documentation revision. The full target below is retained; first-delivery scope and sequencing follow the handoff.


Parent: [[Designs/Lab Capsule and Factory Design Plan]]. Every executable CC version has an immutable container carrier. Its declaration remains the capability contract; the image packages its implementation and software environment. There is one image per version, not one image build per invocation. Many invocations reuse that image with separate containers and workspaces.

## Spark execution and retention

[[Designs/Spark Shared Services and Storage]] owns physical resource limits. Use ARM64 images on the GB10 Spark. Agent lab CCs use invocation-scoped model IPC. The existing model connection is used first; an optional local relay can forward requests to a qualified shared host inference gateway when local models are needed. Images package code/dependencies rather than weights or complete project repos/datasets. Model revision, quantization and runtime handles are frozen external dependencies. Weight bytes and GPU workers are central; conversation state is request-scoped.

Image identity is immutable but retention is finite. Active/retained-run references protect required artifacts; removing the last local copy changes replay availability unless a verified external copy exists. Per-VM engine stores/builders do not deduplicate across guests. Reserve temporary/import/output space before execution. Development uses the same limits.

## Image identity: four different hashes

| Identity | Use |
|---|---|
| Local image ID/config digest | Exact local build loaded into a lab engine; inspected and executed by ID, never by a mutable candidate tag |
| Registry manifest digest | Distributable `registry/repository@sha256:...` reference; record selected platform and resolved image/config identity |
| Multi-platform index digest | Identifies a set of platform images; also record which child manifest/platform actually ran |
| Export archive SHA-256 | Verifies transferred file bytes; not a substitute for manifest/config identity |

Registry-published releases use digest references; archive-distributed releases retain verified transport hashes plus inspected local image/platform identities, with no registry requirement. Unpublished local candidates can run by full local image ID under explicit local admission. This refines the earlier assumption that every build immediately has a usable registry digest. Publishing creates an additional distribution record; it never rewrites a frozen local invocation. Inspect local IDs and repository digests separately. [Image inspection](https://docs.docker.com/reference/cli/docker/image/inspect/), [digest pulls](https://docs.docker.com/reference/cli/docker/image/pull/).

## Package and invocation boundary

| Object | Contents and owner |
|---|---|
| Candidate package | Declaration/source hashes, parent lineage, build-context hash, Dockerfile/locks, image identity/platform, protocol version, needs/effects and evidence references; factory produces |
| Eligible version record | Exact package/image/check/profile pins and allowed usage; admission owner decides |
| Frozen invocation | Attempt/node, eligible version, accepted artifact refs, grants/budgets, scoped model route, lab release revision; protected binder/runner produces |
| Result manifest | Output port/file/schema/media information and completion status; capsule proposes |
| Sealed observations and gate result | Actual image, inputs/outputs, logs, resource/failure evidence and independent assessment; host owns |

The current candidate implementation passes Python callables scoped artifact helpers. M2 must serialize accepted bytes and provenance into an invocation workspace, reconstruct only the required capability in the CC entrypoint, then import outputs into host custody. No runtime database/store handle crosses into the container. Adapt one real CC before inventing a universal transport for all current helpers.

Proposed protocol v1: `/inputs/invocation.json` plus read-only artifact files; `/outputs/result.json` plus output files; bounded `/tmp`; image-baked entrypoint. Record logical refs and hashes alongside files so existing host checks can trace accepted inputs. Invoke with an argument array, not an agent-generated shell command. Current in-memory model/artifact adapters need explicit implementation equivalents.

## What a Docker invocation actually looks like

Illustrative Linux operator shape only. Broker implementation derives every value from policy, creates/pre-owns directories and resolves the admitted image first. Placeholder values below must not be copied as a working release configuration.

```bash
docker create --name ai4r-attempt-a1 \
  --label ai4r.lab=lab-a --label ai4r.attempt=a1 \
  --pull=never --restart=no --init \
  --user 10001:10001 --read-only --network none \
  --cap-drop ALL --security-opt no-new-privileges:true \
  --memory 512m --cpus 1 --pids-limit 128 \
  --mount type=bind,src=/srv/ai4r/jobs/a1/inputs,dst=/inputs,readonly \
  --mount type=bind,src=/srv/ai4r/jobs/a1/outputs,dst=/outputs \
  --tmpfs /tmp:rw,nosuid,nodev,size=64m \
  "${CC_IMAGE_ID}" --invocation /inputs/invocation.json
```

Broker persists creation intent, records returned container ID, starts it, supervises deadline/cancellation, captures exit/OOM state and logs, imports outputs and only later removes owned resources. No automatic remove/restart obscures failures. Numbers are example test limits, not resource requirements. [Container run/create options](https://docs.docker.com/reference/cli/docker/container/run/).

Bind sources must exist on the Docker daemon's VM host, not merely inside the app container. Broker resolves refs to allowlisted real paths, rejects traversal/symlink escapes and unexpected output file types/sizes, and never mounts the entire lab state. Host copies validated output bytes into a different sealed location; it does not grant the capsule write access to authoritative evidence. Input ownership and output UID mapping are qualification checks. [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).

## Agents, checks and nesting

Tool CCs use `network none` initially. Agent CCs receive an invocation-scoped Unix socket to the VM model relay; access is budgeted/revocable and tied to the frozen role/model request. The relay forwards to host inference without exposing acquisition/provider credentials or Docker control. Qualify socket ownership, gateway authorization and cancellation against the actual bridge adapter; the proposal does not assume its existing in-process API works unchanged.

Verifier CCs receive only the pinned work declaration and exact output in their input manifest. Producer task/source files and model traces are excluded. Protected host checks retain input/runtime access separately. The gate host alone accepts or halts. Container exit zero or a factory self-test never accepts an output.

Full CC containerization includes agent and verifier carriers; deterministic protected host code need not become a CC. A CC cannot create child containers by mounting Docker. Future composed CCs ask the governed scheduler to dispatch pinned members. Builder emits source/bundles; factory image construction is a separate broker operation. Benchmark execution profiles need explicit code/device/resource grants, not implicit Docker-in-Docker.

Start with one short-lived container per invocation. A persistent service carrier later requires reset, concurrency, state and per-request isolation semantics. A coherent multi-operation capability may share one image/declaration. A remote-service adapter image does not freeze the remote server.

## Failure and reproducibility

Missing image/platform fails preparation; no fallback/rebuild under a frozen run. Cancellation terminates the owned container, seals partial observations and leaves incomplete outputs unaccepted. On broker restart, reconcile IDs and ownership before taking action. A new attempt gets a new identity; never replay an uncertain non-idempotent effect automatically. Host output-storage failure prevents acceptance even if computation succeeded.

Record input/data hashes, source/build recipe, effective image/platform, model identity/settings/seeds where possible, host kernel and relevant GPU/driver/runtime versions. Distinguish rerunning an existing image, rebuilding software and reproducing scientific results within tolerances. Do not claim Docker guarantees identical provider responses or floating-point results across hardware.

Weights/data remain separately pinned resources. Retain image artifacts or rebuild dependencies needed for replay; a lockfile cannot preserve vanished packages. Shared immutable layers reduce per-version storage, but each VM has its own engine store. Measure build/pull/startup, execution, checks, disk and total journey separately. Full containerization remains the M2 target.

Conversion order: stateless tool, agent via scoped bridge, verifier with payload-negative checks, then resource-intensive research stages. Compare real carrier outputs/failures against the current contract. Include corrupt outputs, denied mounts/network, unavailable dependencies, timeout/OOM/cancel and host persistence failure. Gate equivalence is infrastructure evidence; CC accuracy remains a distinct experiment.
