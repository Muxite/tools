---
id: ai4r-m2a-2-human-relevant-conversion-and-integration
status: proposed-runtime-unverified
source: ai4r_m2a/3-agent-reference/source-manifest.json
last_reviewed: 2026-10-30
next_action: Implement against the acceptance matrix and attach measured evidence
---
# Conversion guide — map a codebase to the target, not the reverse

[Home](../README.md) · [Exact inventory](../3-agent-reference/migration-map.json) · [Source pins](../3-agent-reference/source-manifest.json)

**This is conversion guidance, not the core architecture.** The core describes what a long-running research system must do. This guide describes how an existing implementation can acquire that behavior. Re-inspect a changed checkout before applying file-level advice. Source observations are not runtime integration proof.

## General conversion statements

1. **An existing callable becomes a capability** when it has explicit input/output and effect contracts, a stable entrypoint, required checks, reproducible fixtures and a receipt-producing invocation path. Preserve useful implementation; extract hidden context dependencies into declared providers.
2. **Related capabilities become a CC** when they share a coherent category package, dependency/effect ceiling, versioned manifest, shared checks and discoverable member declarations. Do not equate every legacy stage or every file with a new CC.
3. **A pipeline stage becomes a reusable operation** by replacing implicit upstream-node state with explicit accepted artifact references and provider interfaces. Stage-specific science checks remain where meaningful. Pipeline-order checks become explicit evidence preconditions rather than silently returning “not applicable.”
4. **A legacy declaration becomes a versioned adapter** that maps old IDs/ports to a member contract. Preserve exact old release behavior for pinned callers. New calls resolve the new schema namespace; no alias silently repoints an old version to new semantics.
5. **A planner becomes advisory**: useful planning code is exposed as an optional capability or native agent aid. Remove the requirement that a global graph be complete and frozen before research can proceed. Keep local immutable calls and experiment protocols.
6. **A session becomes a durable investigation** by persisting evidence, protocols, budget reservations and pending-job reconciliation outside model memory. Reuse existing native persistence/job infrastructure when it meets the contract.
7. **A result becomes a deliverable** through sealed artifacts, independent required checks, receipts and atomic publication. Generated prose or a successful worker exit alone is not delivery.
8. **A CC becomes portable** only after a clean external caller executes its members with explicit providers and identical mandatory checks. Replacing internal state with fake AI4R objects or bypassing checks is not conversion.

## Current implementation observations, isolated from core requirements

The inspected AI4R implementation is our modified `AI4Research-Development/jiuwenswarm-agentic`, branch `m1plus/v2`, pinned in the source manifest. It is not upstream JiuwenSwarm. Its SDK dependency is OpenJiuwen commit `9e3390195a9ea15235b2b5f7412cb2aa440622cc`; the separate upstream agent-core checkout has a different commit and is not evidence for that dependency's behavior.

| Current asset | Conversion action | Required proof |
|---|---|---|
| `capsule_runtime` Python/CLI/MCP entrypoints | Keep transport shape where useful; extract portable guarded core from `research` imports | Clean environment imports and executes without private research modules |
| Loader/stage adapter using internal state/store | Replace hidden stage context with explicit artifact/model/executor/retrieval interfaces | External mode enforces the same required evidence checks |
| Process-local admission and bypass flag | Durable release/environment/policy-bound qualification; remove bypass in accepted execution | Restart and alternate transports cannot evade qualification |
| Daemon thread / cooperative timeout paths | Declare cancellation limits; use provider job IDs, containment and reconciliation | Timeout-after-effect injection does not duplicate operation |
| Single-capability declaration schema 1.0.0 | Add category/member schema namespace; keep legacy adapter | Old pinned client fixture and new member fixture both pass |
| Stage source registry and utility extensions | Group into ten categories; retain useful typed checks | Exhaustive old-ID inventory and member tests |
| Native assembly/provider/skill extension seams in our branch | Bind guarded invocations into JiuwenSwarm; preserve native loop and delegation | Trace shows native agent driving calls; raw-tool bypass denied |
| Existing semantic gate (D20 context restriction) | Amend to scoped objective/input/source evidence and independent obligations | Misleading but well-formed result is rejected |
| Stage delivery/report utilities | Return sealed deliverables and machine manifests | Crash-safe release and standalone reproduction |

The inspected upstream `openjiuwen/jiuwenswarm` provides native skill-retrieval adaptation, MCP configuration and session lifecycle. The exact pinned SDK supplies DeepAgent/tool/session mechanisms. Prefer these instead of reproducing a scheduler. The SDK's MCP resource rail is not itself proof of tool-call enforcement: verify the actual tool invocation path. Product-specific assembly/provider helpers are ours, not a guaranteed upstream API. Interface selection is an implementation task with smoke tests at the actual dependency pin.

## Conversion inventory and missing implementations

Seven current stage IDs map as follows: research.search/screening → literature; research.hypothesis → hypothesis; research.builder → build; research.benchmark/evaluation → evaluation; research.delivery → reporting. Intent and requirements compiler aliases remain separate categories. Utility calculate/table-normalize variants map into calculation; markdown/packet/summary utilities map into reporting; research.generalist maps into generalist. Planner operations, rank/summarize-paper and deliver-paper must be assessed as operations to implement or adapt, not counted complete merely because a design names them.

The machine [migration map](../3-agent-reference/migration-map.json) records all initial members and the inspected release manifests/aliases. Re-scan before coding and account for every newly discovered public CC/operation. Retired source versions are historical assets, not additional callable members unless the registry still advertises them. Do not delete old pinned releases needed for reproducibility.

## Implementation handoff

Register a distinct M2a amendment/specification in the owning repository's existing task workflow, preserving current IDs. Map each M2A obligation to native spec/AC IDs rather than creating a competing task system in this library. Resolve M1 freeze and D20 differences explicitly. Implement one bounded wave at a time with demonstrable artifacts and failure tests; carry unresolved failures into the next scoped task.

Do not migrate production runs in place. For an existing run, either complete it under its pinned legacy contract or explicitly fork a new M2a investigation with source artifacts, compatibility checks and a migration receipt. Old accepted findings remain legacy evidence with their original limitations. The new design does not retroactively certify them.

## Container, evidence and lifecycle conversion

Convert each existing category into a digest-pinned image with a locked dependency set, guarded entrypoint and declared host/provider requirements. Move capability-specific dependencies out of shared host environments into capsule ownership; retain explicit shared-provider contracts. Adapt external Python/CLI/MCP/subagent surfaces to that same image. Do not wrap the entire private research pipeline into every image to simulate portability.

Map existing call/admission records to version/environment/workload-specific evidence with origin and scorer identity. Do not manufacture missing history or transfer trust across versions without qualification. Add installation ownership and reference tracking before cleanup, plus protected evolution-policy fields; these describe what may change without requiring automated RSI yet. See [the behavior contract](capsule-packaging-and-trust.md).
