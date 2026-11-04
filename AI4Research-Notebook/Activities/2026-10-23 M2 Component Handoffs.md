---
id: m2-component-handoffs-20261023
status: design-handoffs-not-runtime-implementation
source: Sources/Prompts/2026-10-23-m2-component-handoffs.txt; Resources/Handoffs/m2-labs/source-map.json
last_reviewed: 2026-10-23
next_action: Use the scoped handoffs to specify one carrier and one durable lab on permitted development infrastructure
---
# M2 VM, container capsule and factory handoffs

Created [[Resources/Handoffs/m2-labs/README|a portable handoff package]] with
separate VM-lab, container-capsule and local-factory instructions, common
identity/protocol/custody/resource rules, current source status and shared
acceptance scenarios. This is documentation for bounded implementation, not an
implemented VM/factory/container runtime. No new VM, host service, model,
build, Docker invocation or Spark acceptance test was run for this revision.

The VM handoff begins with one permitted provider/preprovisioned guest, durable
lab identity/state and fenced restore. Missing VM permission does not trigger
sudo or block independent carrier work. The carrier handoff begins with one
real stateless tool using immutable image identity and staged files through
unchanged host checks/gates. The factory handoff uses a fixed durable lifecycle
with bounded adaptive agents, proving the manual source-to-image path first.
Factory proposals do not self-admit or patch frozen plans.

Reconciled eight linked design owners and reading routes. Spark is primarily
benchmark hardware; develop/build elsewhere where practical. First delivery does
not depend on a VM host on Spark, registry, full capacity controller or local
inference server. Keep 20% measured filesystem headroom, count cache/image copies
where they physically exist, protect retained state/evidence/models and use the
existing model connection until a selected task needs local inference. The
10 GB deployed builder cache and proposed 30 GB M2 lab-builder target are distinct
profiles, not conflicting global defaults. Normal benchmark startup remains
no-sudo and separate from privileged VM infrastructure.

Read-only Git inspection discovered a later remote M1 integration at
`809351f8993661a9fdc6e4e635d48f3d262f991b`. The required Planner and optional
capsule source are now integrated; earlier separate-branch notes were retained
and marked superseded on that point. The inspected integration report's test
results belong to that other revision/run, not this documentation task. Source
merge still establishes no image build, eligibility, deployment or model quality.
The existing M1 app/runner commands were not changed by this revision.

Exact request/hash, pre-edit snapshots, source receipts and document-validation
results are retained under `Resources/review-batches/2026-10-23-m2-handoffs`.
The package's own `source-map.json` records source/primary-reference provenance;
all required handoff prose is inside the portable folder. Mermaid renderings
support diagram review, not runtime validation. Received PRD/design source and
archived notes were not rewritten. No new native TASK/AC/IF IDs were invented.

Start with the package README, select one component, and send that component
with the shared-contract/status/validation files to the coding agent. A verified
ZIP companion makes the same reading package portable.
