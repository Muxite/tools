---
id: amendment-planner-capability-gaps
status: proposed-user-authorized-preparation
source: User-authorized amendment preparation, 2026-10-21
last_reviewed: 2026-10-21
next_action: Maintain a verified enabled/disabled planner capability matrix
---
# Planner Capability Gaps

**Package ID:** `AM-PCG-001` · **Status:** proposed user-authorized preparation, not product acceptance.

Read this page, [Evidence.md](Evidence.md), and [manifest.json](manifest.json). This package maps which native OpenJiuwen features M1 uses and which it intentionally disables in its governed planner. A disabled feature is not proof that the native runtime lacks that feature.

## Verified baseline and reuse

M1 pins OpenJiuwen `9e3390195a9ea15235b2b5f7412cb2aa440622cc`; `verify_native_pin()` rejects missing or differently pinned runtime. M1 builds a native `TeamAgentSpec` containing `DeepAgentSpec`, then calls native harness `run_once`. It supplies one audited text model client, one call limit, no tools/MCPs/subagents/rails/skills, no task loop or planning, and no bridge/fork/SwarmFlow/team plan. For workflow scheduling M1 reuses the pinned `AgentBackend`/`run_workflow` interface but fixes serial frozen order, cap=1, retries=0, and no journal/resume/WAL.

The exact pinned source provides broader interfaces: `run_workflow` exposes backend, cap, admission gate, journal/resume, budgets, abort and progress hooks; Team/Deep Agent specs build runtime agents; native `run_once` can honor a configured task loop; Symphony has `CapabilityProvider` and atomic snapshot interfaces with capability fingerprints. M1 already has a `jiuwenswarm.symphony.adapter` over those upstream interfaces. Upstream graph construction accepts only skill/subagent/agent types and fingerprints do not establish code isolation or runtime effects. The current planner restriction is a policy choice.

## Proposed amendment

Before extending the planner, capture the actual effective library snapshot, active live-plans entries, explicitly supplied candidates, policy/resource inventory, eligible survivors, proposed graph and binder rejection reasons. Seven stage names alone do not prove a starved planner: compiler/planner/verifier registrations have separate roles, and policy or ports can exclude otherwise present candidates. Synthetic configuration is not a live snapshot.

Keep a small versioned matrix of requested planner behaviors, native interface at pinned revision, M1 setting, M1 policy reason, and a separately proposed test for any change. Do not build a second Leader, scheduler, model bridge, skills layer, or capability registry. Do not enable additional behavior merely because the upstream API offers it. Any proposed capability must be independently authorized and bounded by existing runner and gate policy.

## Acceptance criteria

- `AM-PCG-AC-01`: evidence confirms installed `direct_url.json` matches the exact commit before native planner or workflow use; missing/mismatch remains blocked.
- `AM-PCG-AC-02`: baseline test proves exactly one governed text model call and rejects tool calls, second call, modality expansion, retries, dynamic member dispatch, or unexpected workflow node order.
- `AM-PCG-AC-03`: a capability matrix accurately labels native available, M1 enabled, M1 deliberately disabled, and unknown; it cites exact pin source/API and M1 adapter configuration.
- `AM-PCG-AC-04`: a proposed feature toggle has explicit schema, authority owner, negative tests, rollback, and resource/data limit before any implementation; default behavior remains current single-shot restriction.
- `AM-PCG-AC-05`: Planner never sees hidden fixtures/keys or evidence reserved for evaluation; runtime semantic verifier still receives declaration plus exact output only.
- `AM-PCG-AC-06`: retain a joined candidate-visibility trace with library/policy/resource hashes and stable per-candidate rejection reasons. Distinguish absent, not selectable, incompatible, policy-denied and eligible-but-not-chosen candidates.
- `AM-PCG-AC-07`: a fixture with an eligible optional gate demonstrates visibility and selection; removing or replacing a mandatory checking profile is rejected. New capsule proposals must name the demonstrated reusable gap and overlap with existing carriers before adoption.

## Negative scenarios and evidence

Test runtime pin mismatch; retry or duplicate dispatch; planner asks for a tool or subagent; loop ignores one-call maximum; workflow adds node; journal returns an old result; feature toggles without frozen configuration; planner requests hidden test/answer material; and container worker tries to become planner or alter the gate. Each must be blocked or non-advancing. Retain pin metadata, config hash, exact source receipts, call count, dispatch trace, rejection reason, and test output.

Rollback sets all experimental feature toggles off, reverts to the frozen single-shot native planner and current serial workflow adapter, then confirms new calls satisfy baseline tests. Past records remain immutable.
