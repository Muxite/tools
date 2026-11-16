---
id: muse-final-nvtx-engineering-cc-md
status: current-design-proposal
source: November 6 accepted presentation plan and user steering; pinned sources in Evidence
last_reviewed: 2026-11-06
next_action: Use the final deck for design discussion; qualify implementation before claiming results
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

# NVTX engineering: skill plus deterministic helpers

The builder-side tool packages instructions, placement rules, helper code and regression fixtures. It makes repetitive work repeatable without claiming that source names establish semantics.

| Step | Inputs → outputs / checks |
|---|---|
| inspect | exact source + question → existing hooks, symbols/paths, conditional/async/graph sites and unknowns |
| agent placement plan | anchored site, purpose, domain/name/IDs, range/lifetime, expected fixture, participant mapping |
| check_plan | verify base/anchors, nesting/thread ownership, names, duplicate sites and allowed scope |
| apply | checked plan + exact base → idempotent patch/new snapshot + marker manifest; reject stale base |
| check_build | source/recipe/manifest + optional returned lab coverage → build/check record; absent execution evidence stays absent |
| existing build/package | identified snapshot → new engine image + provenance |

The lab runs the submitted image and reports emitted coverage/missing paths. It does not apply patches. The full [[Presentation speaker notes]] and parameterized output specimens retain current typed CC ports; SKILL.md is a material, not a new root schema field.

Push/pop is same-thread nesting; start/end handles support overlap/cross-thread lifetimes; RAII closes ordinary C++ scopes. NVTX is host semantic context, not automatic GPU completion. Do not add synchronization solely to improve a timeline. Fused/batched kernels need participant maps; do not invent separate expert durations. Graph capture/replay and compiled-out/gated hooks need actual path verification. Stable strings/coarse default ranges help avoid marker bloat.

Engine-native cache/miss/queue/state counters remain necessary. Improvements to the rule pack should add executable regression cases (stale base, duplicate edits, exits, wrong thread, disabled path, fusion, graphs), rather than only more prose.

Sources: [NVTX](https://nvidia.github.io/NVTX/), [Systems](https://docs.nvidia.com/nsight-systems/UserGuide/index.html), [[Evidence]].
