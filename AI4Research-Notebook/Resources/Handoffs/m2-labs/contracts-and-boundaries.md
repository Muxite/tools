---
id: m2-handoff-shared-contracts
status: ready-for-bounded-specification
source: source-map.json; Sources/Prompts/2026-10-23-m2-component-handoffs.txt
last_reviewed: 2026-10-23
next_action: Freeze versioned boundary examples in the native interface process
---
# Shared contracts and ownership

| Object | Producer / consumer | Minimum meaning |
|---|---|---|
| Lab manifest | Lab controller / deployment, recovery and broker | Stable lab/project ID, owner, deployment instance, source/app/factory/catalog pins, state schema, model routes, storage envelope and backup refs |
| Base release | Release owner / lab controller | OS/platform/provider compatibility, app/broker/protocol versions, seed capsule/check identities and migrations |
| Candidate package | Factory / qualification and admission | Declaration/source/context/recipe/lock hashes, lineage, image/platform, protocol, needs/effects/budgets, evidence and limitations |
| Frozen invocation | Protected binder/runner / carrier broker | Lab/run/node/attempt, exact eligible capsule, accepted input refs, declared outputs, role/model route, deadline/limits and grants |
| Observation | Broker / host checks | Actual image/container/platform, hashes, start/exit/OOM/cancel/unknown state, logs and measured resource observations |
| Admission | Independent qualification/admission owner / Library | Exact tested subject/criteria, actual findings, failed/blocked/inconclusive outcomes and explicit eligibility/activation |

These are field responsibilities, not competing exhaustive JSON schemas. Freeze
versioned examples in the repository's interface process. Keep artifact refs as
well as hashes: content identity is not authority.

A lab ID survives replacement; a deployment ID does not. A fork gets a new lab ID,
lineage and fresh credentials. Before restoring, enforce a single-writer fence
or confirm the old instance cannot write. Heartbeat expiry alone is insufficient.

## Runtime and custody

An image packages software; its declaration remains the capability contract.
A container is one invocation, not a durable lab. Persist state, resources,
evidence and credentials explicitly. Saved images exclude mounted volumes.
Pass scoped files/refs, never host database/store objects.

Only the infrastructure broker has Docker access. Factory/Planner/model agents
submit typed operations, not arbitrary flags, host paths, devices or shell
commands. No socket in app/capsule containers; invocations are siblings, not
Docker-in-Docker. Docker control and generated builds are powerful inside the
VM; BuildKit on that same daemon is not a hostile-build isolation guarantee.

Local image/config ID, registry manifest digest, multi-platform index digest and
archive SHA-256 have distinct meanings. First use an exact loaded image ID,
platform and verified archive transport; no registry required. Resolve tags
before qualification/freeze. Unknown image/platform blocks preparation; never
rebuild or fallback inside a frozen run.

Bind sources must exist on the daemon host. Mount scoped inputs read-only,
outputs writable and scratch bounded; never mount authoritative lab state.
Validate/import regular output files into separate sealed custody before gates.
Reject traversal, linked/substituted files, missing ports, size/hash changes and
unsupported schemas. A result manifest or exit zero is advisory.

## Planning, checking and release

The Planner assembles compatible contracts into a typed DAG, not a list of fixed
complete workflows. Scientific placement/checking obligations remain. New
capsules enter future plans only through normal qualification/admission/activation.
Containerization preserves exact plan/check/gate meanings and pins.

Host checks may use accepted inputs/runtime evidence. Semantic verifiers receive
only the pinned declaration and exact output (D20/D24), excluding worker inputs,
traces and confidential sources. Private held-out tests remain independent.
Generalist intention-bound checks follow the actual current explicit contract;
never smuggle private inputs into reviewer context or upgrade low trust to truth.

Factory authors cannot waive checks, self-admit or broaden a failed declaration
in place. Changed source/declaration/image is a new candidate. Local eligibility,
exchange, central qualification and lab adoption are separate decisions. Updates
affect future runs; rollback restores a compatible image/catalog/database/source
set and preserves failures. Retain M1 human activation until explicitly changed
by an M2 policy.

## Storage and models

Retain 20% headroom on each measured filesystem. Count peak staging, image
unpacking, intermediate layers, VM overlays, models, clones, output and export
overlap where they physically reside. Separate engines/builders have separate
stores; registry sharing is not cross-VM unpacked-layer deduplication. Never
share writable Docker metadata between daemons.

Use small owned accounting/locks first, not a distributed capacity controller.
Bound heavy-operation concurrency and unknown-size growth. Unattended multi-lab
operation later needs enforceable quotas/reservations and reconciliation; a
ledger alone does not enforce a limit. Uncertain ownership blocks reclamation.

The existing seven-day TTL applies only to explicitly owned inactive temporary
resources. Protect inputs/results/credentials/models/app state, rollback pins,
active/retained dependencies and unknown jobs regardless of age. No global prune.
BuildKit GC is soft collection, separate from hard storage envelopes: existing
10 GB deployment cache and proposed 30 GB M2 per-lab targets are distinct profiles.

Use the configured model connection first. When local inference is required,
share canonical immutable model artifacts and qualified workers, not weight
copies per lab. Pin effective model/runtime/settings per run, isolate sessions
and grants, and switch models only for new runs. Local inference/acquisition
services are not bootstrap dependencies when unused.

Technical references: [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/) and [BuildKit container driver](https://docs.docker.com/build/builders/drivers/docker-container/). These establish mechanics, not tested AI4R compatibility.
