---
id: ai4r-m2a-packaging-trust
status: proposed-runtime-unverified
source: ai4r_m2a/3-agent-reference/sources/cc-packaging-request.txt
last_reviewed: 2026-10-30
next_action: Implement the declared packaging and qualification contracts, then attach measured evidence
---
# Capsule packaging, evidence-based trust and controlled evolution

[Home](../README.md) · [CC overview](../1-human-required/02-capsules.md) · [How to explain this design](capability-capsule-positioning.md)

## The agent and its capability space

The JiuwenSwarm agent lives in a sandbox with persistent project state and can investigate, write programs, run experiments, analyze data and ask questions. CCs supply a deliberately qualified capability space for that broad activity. A CC groups tools, skills, MCP operations, bounded subagents or data operations with declared effects, guards, gates, dedicated verifiers, traceability and a pinned environment. Ordinary tools can also have excellent tests; the distinction is that this packaging contract makes those requirements explicit and enforced across the supported invocation surfaces.

## Containerized releases and dependency ownership

Every CC release supplies an OCI-compatible image pinned by digest and a dependency lock, plus supported platform and host/provider requirements. Pin the base image and dependency artifacts; retain a build recipe and provenance. The receipt records the resolved platform image digest, not only a mutable tag or multi-platform label. Images make the shipped software environment repeatable; they do not make live external data, models, kernels, drivers or stochastic computation identical. Record those separately and use the existing reproduction-level contract.

Python, CLI, MCP and subagent adapters invoke the same guarded containerized release. They are reusable interfaces, not a requirement to install AI4R. A thin external adapter can start/reuse a compatible container with explicit providers. A reference qualification run must use the image, even if developers also run local unit tests. An external MCP/model service remains an explicitly declared provider with independently recorded identity and limits; the image pins the adapter and local checks, not an uncontrolled remote service.

The agent sandbox and CC containers have different jobs: the former bounds the investigation, while the latter isolate capability dependencies and execution. The host enforces filesystem, network, credential and resource permissions before effects. Do not grant broad host mounts or a container-engine socket merely to make a package start. Containers are not by themselves a complete security boundary; retain the lab's host/VM and provider controls.

## Clean addition and removal now

Installation resolves the image and dependency lock, checks host compatibility, qualifies the declared scope, registers members and publishes eligibility atomically. An interrupted install must not leave a half-registered callable. Capsule-owned dependencies stay within the image or explicitly owned resources, without mutating the host's global package environment.

Removal first disables new selection and dispatch. Drain or cancel existing jobs according to policy, detach adapters/credentials/mounts and reclaim only unreferenced capsule-owned runtime resources. Shared image layers, providers or resources must not be removed while another capsule or job uses them. Retained evidence and reproduction images/snapshots follow retention policy; removing a capability from active use is not deleting its history. If retained images occupy disk, report that plainly rather than claiming complete disk reclamation. Reinstallation of the pinned release must reproduce the demonstrated local setup.

Broader spatiotemporal composition—automatically composing/changing capabilities across contexts and time—is a deferred research direction for months later, with no promised delivery date. It is not an M2a or Stage 1 acceptance requirement. Basic explicit contracts, coexistence of pinned versions and clean add/remove are required now. Do not claim they already implement the broader composition model.

## Quality thresholds and trust from evidence

Keep append-only attributable history for each capability and its release, checker/policy versions, resolved image, provider environment and workload scope. Include success/failure counts, rejected and blocked calls, severity, false acceptance/rejection where independently scored, scientific negatives, costs, latency and sample freshness. A worker's claimed success is not independent performance evidence. Separate qualification fixtures from live-use evidence and keep imported history's origin and verification status.

An independently owned quality policy defines the minimum evidence, sample scope/window, freshness rules, correctness and critical-failure thresholds and required evaluators before qualification. Thresholds are task-specific; there is no universal unexplained trust percentage. The current assessment records the policy and evidence references, denominator, uncertainty/limitations and scope. Insufficient or stale evidence is an explicit result, not a pass. New releases can enter evaluation-only scope using qualification fixtures; they cannot inherit unrestricted trust from an older release or a different workload.

Trust levels are `evaluation_only`, `qualified_for_scope`, `restricted` and `blocked`. They describe policy-derived eligibility, not intrinsic intelligence or permission to skip verification. The compatibility filter also requires the task's minimum trust level and matching qualification scope. A task needing qualified evidence excludes evaluation-only candidates. Qualification may narrow or expire as evidence changes. Authorization remains the intersection of caller/host/package/member scopes even for a highly trusted capability.

Immutable package metadata carries a stable history key and quality-policy reference. The changing performance history and current assessment live in a durable external registry/evidence store; rewriting history must not silently change an image or release digest. A standalone distribution can carry an attributed evidence snapshot and resolve updates through an explicit provider. External hosts may distrust or requalify imported evidence. Confidential task inputs do not become public history by default.

## Evidence-guided RSI boundaries

The package declares allowed optimization targets, objectives and immutable constraints, with a protected evolution-policy reference. History can justify proposing an optimization—for example reducing latency on a verified workload while holding correctness and effect limits fixed. It cannot itself authorize edits. A policy owner decides what may change: worker code, prompts, dependencies or another named component. Verifiers, held-out fixtures, permissions, quality thresholds and release authority are protected by default; changing them requires separately authorized, independently evaluated work.

Every RSI candidate is a new pinned release/image. Compare it with the incumbent under matched workloads, correctness floors, budgets and held-out evaluation, retaining failures and regression evidence. Promotion requires independent admission; rollback keeps the previous release available. Never let a cost objective reward weakening checks or suppressing failed-call history. M2a supplies these interfaces, records and deny-by-default permissions; automating the complete RSI loop remains later work.

## Testable delivery

Stage 1 demonstrates both CC images on a clean compatible host and a remove/reinstall cycle while another capsule remains functional. Verify that disabling a member prevents new dispatch, rejected/valid outcomes remain in history, and loss of required evidence blocks acceptance. Later lifecycle qualification adds concurrent jobs, shared dependency retention, stale/untrusted history, scoped trust downgrade and a denied unauthorized RSI edit. A policy fixture with insufficient samples must not become qualified. These extend existing M2A obligations 02, 03, 05, 09, 10 and 13; they do not waive their existing requirements.

The tradeoff is higher upfront engineering and maintenance: environment packaging, checks, qualification data, effect policies and evidence storage. The intended return is more dependable reuse and reproducible setup. Its magnitude must be measured; no general CC performance advantage is asserted here.
