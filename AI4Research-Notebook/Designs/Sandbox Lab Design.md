---
id: sandbox-lab-design-m2
status: design-awaiting-approval
source: Sources/Prompts/2026-10-29-design-approval-adapter.txt; Sources/Prompts/2026-10-29-lab-manager-implementation.txt; Sources/Prompts/2026-10-30-central-local-managers.txt
last_reviewed: 2026-10-30
next_action: Approve the design and the AI4R adapter boundary before further implementation
---
# Sandbox Lab Design

> **Current amendment, 2 November:** [Incus whole-lab selection and sources](Sandbox%20Briefing/Incus%20Research%20and%20Decision.md). Central owns the outer instance, and a trusted local adapter owns the private Docker engine. Earlier Compose-boundary/central capsule executor details below are superseded history. Safe reapply and no research replay remain required. No runtime deployment qualification is claimed.


**Latest hierarchy:** one Central Lab Manager per machine is the command/communication hub; every lab AI4R worker contains a Local Lab Manager. Central hands down scoped commands and versioned registry snapshots. Labs return progress through their manager pairing, never contact peer labs, may access permitted internet services, and may modify private CCs. Any central push/export, merge or image publication requires human approval. See [Central–Local coordination](../../AI4Research-Development/jiuwenswarm-m1-current/docs/architecture/lab-manager/central-local-coordination.md).

**October 30 clarification:** lead with the goals and lab design, then feature derivations. A lab is a project with its AI4R worker and sibling CC containers. [Capsule support](../../AI4Research-Development/jiuwenswarm-m1-current/docs/architecture/lab-manager/capsule-support.md) explains immutable images, per-lab instances, clean dependency removal, preserved evidence and the scoped host execution interface. The in-progress [[Designs/ai4r_m2a/README]] remains the capability-design owner and is unchanged by this work. Hardware capacity/cost slides are removed.

**Latest clarification:** design approval comes first; no more Lab Manager code is needed now. The existing experimental implementation is retained as reference. [The adapter design](../../AI4Research-Development/jiuwenswarm-m1-current/docs/architecture/lab-manager/communication-adapter.md) explains what OpenSandbox can reuse and what stays AI4R-specific. Its endpoint discovery is useful; the inspected server proxy filters native bearer authentication, so direct native HTTP remains the proposed research path. Compose is the baseline candidate, and OpenSandbox is an alternative lifecycle owner, never a second controller over the same containers.

**Selected October 29:** a small host-side Lab Manager over Docker Compose. Each lab owns an independent writable AI4R Git clone and persistent research state. This explicitly supersedes the October 27 VM-per-lab selection. The exact previous document is preserved in [the history snapshot](../Resources/review-batches/2026-10-29-lab-manager/prior-Sandbox-Lab-Design.md.txt); its SHA-256 is recorded in the adjacent source receipt.

The maintained design and implementation live together in [the code repository](../../AI4Research-Development/jiuwenswarm-m1-current/docs/architecture/lab-manager/README.md). [The operator guide](../../AI4Research-Development/jiuwenswarm-m1-current/lab-manager/README.md) explains setup, requests, GPU recovery and manual exports. This notebook is a navigation and decision record, not another runtime specification.

## Responsibility boundaries

- Mother AI4R owns maintained releases. Labs clone a selected committed revision and do not mount mother's writable files or Git metadata.
- The host manager owns lab lifecycle, requested/observed state, routing summaries, exclusive GPU admission and selected export. It runs independently of mother and labs.
- Each lab's existing AI4R owns research decisions, run records, scientific checks and cancellation. CC names and model selections recorded by the manager are metadata; the native operator configuration enables the actual capabilities and model routes.
- Shared inference stays outside lab projects. Private serving/training and mutable checkpoints belong to a lab. One GPU uses explicit planning, drain, private script and inference restoration phases.
- A human reviews and applies exports on a separate mother review branch. No merge agent, automatic adoption or automatic update propagation is included.

## Reuse decisions

Compose supplies actual grouped lifecycle and ordinary container boundaries. Existing AI4R Docker stages and native request/status/cancel APIs are reused. The previous lab CLI informs ownership labels, finite reconciliation and checksum/export patterns. Compatible JiuwenBox tools remain inside a lab without requiring a second isolation layer around every CC.

Kubernetes inspires stable IDs, ownership labels and requested/observed reconciliation; no cluster is deployed. Ansible installs the host service and stays outside live operations. Lor contributes outcome-based campaigns, separated workers and visible controls. ArkenOS contributes persistent workspaces/goals, completion criteria, task inspection and cheap event checks. Their public documentation supports methodology reuse; no unavailable public core implementation is claimed as code-audited. [[Designs/Lab Design Comparison]] retains the option investigation as supporting evidence, with its older selection superseded here.

## Delivery and evidence

The [updated presentation](https://chatgpt.com/space/page_7a233186a3548191869c85106fc552b4) presents the Compose decision, Lor/ArkenOS methods, writable lab anatomy, relay, GPU phases, manual contribution and reuse. Prior VM slides are hidden historical material; comparison graphs remain supporting slides with estimated effort clearly distinguished from benchmarks.

[Implementation evidence](../../AI4Research-Development/jiuwenswarm-m1-current/docs/code/Missions/LAB/LAB-001/evidence.md) separates unit/HTTP fixtures, actual Docker checks, lab-image build and editable-source bootstrap from actual model/GPU qualification. These checks do not establish scientific quality, deployment readiness on DGX Spark, or completion of the separate M2a research-runtime program.

The exact approved user plan and capture hash are preserved in [[Sources/Prompts/2026-10-29-lab-manager-implementation.txt]] and [the receipt](../Resources/review-batches/2026-10-29-lab-manager/source-receipt.json). All execution remains on our infrastructure.
