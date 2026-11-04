---
id: lab-desired-state-safe-reapply
status: proposed-for-design-approval
source: Sources/Prompts/2026-10-30-idempotent-inspirations.txt
last_reviewed: 2026-10-30
next_action: Approve environment apply semantics before runtime implementation
---
# Lab desired state and safe reapply

> **Current amendment, 2 November:** [Incus whole-lab selection and sources](Incus%20Research%20and%20Decision.md). Central owns the outer instance, and a trusted local adapter owns the private Docker engine. Earlier Compose-boundary/central capsule executor details below are superseded history. Safe reapply and no research replay remain required. No runtime deployment qualification is claimed.


This extends the proposed paired Central/Local Lab Manager design with an Ansible-inspired environment contract. It is a design proposal, not a working manager or an approved implementation. The live presentation has ten slides: complete architecture; capsule images; request/execution/recovery; Ansible; Docker Compose; JiuwenBox; Lor; ArkenOS; Kubernetes; OpenSandbox.

Each lab has a versioned definition: stable ID, selected source base as creation provenance, pinned worker/capsule images, assigned catalog version, mounts, limits, model routes and requested lifecycle state. Native scientific run state remains inside the lab. Central stores environment intent, routing summaries, operation IDs and observed health.

Explicit apply inspects actual owned resources, previews differences and changes only the authorized environment fields. If definition and observed state match, reapply changes zero resources. Use one serialized operation per lab and stable ownership labels. After interruption, inspect the recorded resource/operation before retrying any creation step. A config hash alone does not prove that resources match. Provider previews must identify unsupported or unknown effects rather than claim a complete dry-run.

Lab source is initialized only on creation. Reapply never resets a writable checkout to its base revision, overwrites research state, globally prunes images, or updates a lab just because mother AI4R changed. Image upgrades/rebuilds and disruptive container recreation are explicit updates. Persistent state stays in lab-owned host mounts/volumes; unrecorded in-container package installs may be lost on recreation. Stop/archive retain data; deletion is separate.

Periodic reconciliation observes and reports. Failed labs do not repeatedly restart. Explicit start/repair can apply needed environment changes after checking the existing state. Docker unavailable is unknown/unavailable, not absent. Research submission has separate request/run IDs, queried before retries; applying an environment never launches or replays a research request. Container entrypoints must not automatically replay unfinished work. Unknown submission acceptance stays unresolved for operator review.

The central scoped host executor remains the sole physical lifecycle owner, invoking Compose for fixed services and Docker for dynamic capsule jobs. Local managers relay scoped requests. No Docker socket is mounted into workers or capsules. Code/image transfer into central stores and subsequent merge/publication remain human-approved actions.

Acceptance after approval: create once; same apply changes nothing; repeat after manager restart preserves IDs; partial setup re-checks existing objects; lab source edits and evidence survive; number of native research submissions remains unchanged; unavailable Docker never causes replacement objects; disruptive updates appear in preview.

Ansible supplies state-aware task and check/diff concepts and actual host install/repair playbooks. State-aware modules can skip already-satisfied state, but arbitrary command tasks are not inherently idempotent and preview support varies. Kubernetes supplies ownership/observation/recovery patterns without a deployed cluster. Compose is the actual container foundation. Native AI4R supplies research APIs. JiuwenBox is candidate tool/job reuse, Lor and ArkenOS are methodology references, and OpenSandbox remains an optional replacement execution provider.

Sources: [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html), [Ansible check/diff](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html), [Compose up](https://docs.docker.com/reference/cli/docker/compose/up/), [Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/). Reviewed October 30. The AI4R-specific contract above is our adaptation, not a claim these projects implement it for us.
