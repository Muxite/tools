---
id: amendments-index
status: proposed-user-authorized-preparation
source: User-authorized amendment preparation, 2026-10-21
last_reviewed: 2026-10-21
next_action: Review package order and authorize a bounded implementation package
---
# Amendment packages

These are portable, proposed preparation packages for design and test work. They do not change the maintained M1 design, accept a product change, admit a candidate, or prove deployment behavior. Each package carries its own manifest, minimal evidence excerpts, hash receipts, acceptance criteria, negative cases, and rollback direction. The shared [template](Template/Amendment%20package%20template.md) is reusable for later packages.

## Reading order

1. [CC Accuracy Verification](CC%20Accuracy%20Verification/README.md) — priority; establish whether proposed work CCs meet held-out accuracy requirements.
2. [Authority Readiness](Authority%20Readiness/README.md) — validate authority, containment, and readiness prerequisites around those experiments.
3. [Planner Capability Gaps](Planner%20Capability%20Gaps/README.md) — map deliberately disabled native planner capabilities without treating them as absent or enabling them by default.
4. [Container CC Pilot](Container%20CC%20Pilot/README.md) — future-soon, one stateless carrier pilot through the existing registry dispatch seam.

Existing M1 `TASK`, `AC`, and `IF` identities remain owned by the maintained design. Package-local identifiers use `AM-*` namespaces and are proposals; they do not rename, supersede, or silently satisfy existing identities. See [lab progression](../Designs/Lab%20Progression.md) for the current prototype, verified local checks, and two-experiment preparation runbook.

## Baseline and review record

The relevant maintained source excerpts and receipts are embedded in each package so a coder can begin from this directory without first reading the large repository. Each excerpt names its source commit and SHA-256. The M1 project snapshot used here is `d3d7f565c6c05ccf764fe0780fde149b7dc89b95`; this is source evidence, not proof that this exact checkpoint is deployed. The OpenJiuwen dependency pin is `9e3390195a9ea15235b2b5f7412cb2aa440622cc`.

The review batch location is [`Resources/review-batches/2026-10-21-amendments`](../Resources/review-batches/2026-10-21-amendments/README.md). No separate Luna review was run during this preparation; the batch record keeps that distinction explicit.
