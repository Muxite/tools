---
id: one-cc-migration-03
status: proposed
source: November 3 single CC proposal and pinned Strata checkout
last_reviewed: 2026-11-03
next_action: Replay native and migrated fixtures before qualifying a real release
---
# Which records become a capsule?

Version 0.3 is a proposed design. It has one installable record, [CC](contracts/cc.schema.json). A [factory brief](contracts/factory-brief.schema.json), [product](contracts/product.schema.json) and [evaluation request](contracts/evaluation.schema.json) have their own identities and lifecycle. Publish the CC to a catalogue by immutable release digest. Submitting a brief, returning a candidate or scheduling a test creates no catalogue entry. A factory can deliver zero CCs.

## Reading the fixture

1. Read [the brief](examples/brief.json). The human supplies the baseline, the outcome, a one-Spark budget, protected behavior and frozen policy. Its profile names actual IQ3_S shards. The reader derives baseline logical expert layout with the identified native index producer. This example leaves the transform method, basis rank and projection selector open.
2. The brief points to [one qualified CC](examples/cc-qualified.json) with native pack inspector and benchmark operations and [one desired reader draft](examples/cc-draft.json) it can choose to implement. Draft fields use unknown, suggested or required; unknown fields contain a question. A draft cannot be installed. Each operation of a qualified CC binds to an immutable carrier, declared port names and check IDs. Each operation names its own needs and effects within the package ceilings. The inspector requires its declared native reader ABI and memory, and the benchmark requires the endpoint and GB10 resources. A recipe pins source, build-context archive, base image, environment lock and recipe where an image is unsuitable.
3. [The product](examples/product.json) returns a Git revision, build recipe and engine image with no delivered CCs. Its fixture branch, tree, image and attestations are hypothetical. Source-only products may carry a pinned commit, Git bundle or patch with expected tree; qualification must materialize and verify the runnable product before lab dispatch.
4. [The evaluation](examples/evaluation.json) binds that product and brief to frozen locks, a workload, the target and the [policy](examples/evaluation-policy.json). Missing evidence yields inconclusive. A protected policy reference allows the builder to know the public gates without access to held-out cases. Held-out data and real evidence are absent from these fixtures.
5. Identity-only fixture locators denote externally managed material. Production admission must fetch scoped artifacts, verify digests, signer and authority, cross-check attestation subjects and reproduce required checks. Registry tags, self-asserted qualification and well-formed JSON do not authorize a run.

## Migration crosswalk

| Prior owner | 0.3 placement | Preservation gate |
|---|---|---|
| M1 declaration and carrier | Keep the old reader as the invoked operation, translate typed input/output to takes/gives, preconditions/providers to needs, effect classes to changes and check IDs to guarantees. Keep original bytes by digest. | An old failure on the same inputs still fails with the same meaning. Unmapped assumptions remain draft questions. |
| M2a category package/member capabilities | Package identity and member entrypoints become one CC with multiple operations. OCI execution becomes an image carrier. Native entrypoints use locked recipes where appropriate. The pool indexes purpose, tags, needs and port compatibility. | Bind each operation to its exact ports, carrier and independent check. Before release, include legacy admission, effect ceilings, provider policy, source/license records, dependency/resource ownership lock and evolution protections in the qualification evidence or separate protected policies. Reject elevation if any rule cannot be enforced. |
| M2a checks, receipt, call, research contract, quality assessment, artifact manifest | Preserve the records and their existing enforcement. Guarantees refer to check definitions. Brief/evaluation adapt the research contract, while a call reserves resources and a receipt records a checked outcome. | Verify resolved references and critical fields at their original enforcement points. A qualifying fixture exercises the native checker independently of the writer. |
| Workshop experiment or 0.1 MoE template | Discovery fields and independently reusable calls can project to CCs. Split model/change intent into the brief/profile, candidate deliverables into product and comparison obligations into evaluation. | Frozen baseline, solver freedom, gates and separate evidence receipt survive. Synthetic artifacts remain synthetic. |
| 0.2 change-request / implementation / evaluation forms | Import respectively as brief, product and evaluation. A 0.2 capability-bundle resolves to candidate CC data after qualification. Retain source form and release digest as lineage. | Give companion artifacts no CC discovery identities. A source product must still be buildable even when the factory returns zero CCs. |

This is a migration design. No converter or production admission service is provided. Adapt each real release by replaying native positive and negative fixtures before activation. When an effect, check, protected change boundary, data obligation or identity cannot be preserved, retain the original runtime under its existing admission or leave the new release in draft.

## Offline acceptance

From this folder run `python validate.py` with Python 3.10+, jsonschema 4.x and referencing installed. The validator uses local schema IDs, verifies the bytes of links within this package, rejects unknown mandatory profile readers and checks operation bindings. Its in-process pool demonstration installs an explicitly approved synthetic digest, discovers it by tag, withdraws it and retains the old reference. Production concurrency, authorization, multi-host leases, provenance verification and hardware execution require separate integration tests.

The fixture's actual source commit, Git tree, model revision and shard byte counts/hashes come from the local Strata checkout at c62d5e3a15b40ea51c96aae9e8d36928965f53ab. Model bytes and live hardware were not examined. All fixture values and gate thresholds require real owners and evidence before dispatch.
