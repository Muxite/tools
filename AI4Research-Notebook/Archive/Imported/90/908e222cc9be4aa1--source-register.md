# Source and version register

## Current authority

| Label | Source | Use in this dossier |
|---|---|---|
| **[DESIGN AUTHORITY]** | [Current full design package](../../design-package/README.md), especially [phase boundaries](../../design-package/delivery-phases.md), [Capsule lifecycle and verification](../../design-package/capsules.md), [research responsibilities](../../design-package/research-design.md), [Intention Compiler build](../../design-package/builds/intention-compiler/README.md), and [Capsule–model-routing contract](../../design-package/reference/capsule-model-routing.md) | Current architecture, responsibilities, authority, interfaces, and stage exits. The compact package is a matched presentation variant, not a separate authority. |
| **[DESIGN AUTHORITY]** | [Current PRD (4), received October 13](../../../product/received-prds/prd-m1-reviewed-2026-10-13.txt), also identified by [product navigation](../../../product/README.md) | Current M1 product behavior, phase acceptance, and exclusions. The received bytes are preserved; the design's decision process interprets them. |
| **[DESIGN AUTHORITY]** | [Routing-owner source receipt](../../design-package/sources/model-routing/README.md), [received router design](../../design-package/sources/model-routing/received/model-router-design-en-2026-10-13.md), and the shared [Capsule–routing integration](../../design-package/reference/capsule-model-routing.md) | Routing behavior stays with its owner; protected export, binding, dispatch authority, and Capsule integration stay with architecture. Phase 1 static Codex remains the operational baseline; API routing is Phase 3. |
| **[DESIGN AUTHORITY]** | [M1 TASKS registration](../../../tasks/M1/TASKS.md) | Current coding registration is pending. This dossier creates no task identities or runtime acceptance. |

## Pinned implementation evidence

| Label | Exact source | Scope and interpretation |
|---|---|---|
| **[IMPLEMENTATION EVIDENCE]** | [`ai4r_test_with_spec_kit` at `73ed9e867d58a22ac57699913ecbd7f4d3619f2c`](https://github.com/Stellven/jiuwenswarm/tree/73ed9e867d58a22ac57699913ecbd7f4d3619f2c) | Pushed compiler candidate and its task/evidence tree. Do not use a moving branch head when making later comparisons. |
| **[IMPLEMENTATION EVIDENCE]** | [M0-001 task scope](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/TASK.md), [source-baseline receipt](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/source-baseline.json), [task progress and acceptance matrix](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/tasks.md) | Defines the October 8 bounded whole-Intention-Compiler assignment, records its 267-file source closure, work, and current evidence status. |
| **[IMPLEMENTATION EVIDENCE]** | [`standalone/intent_compiler/`](https://github.com/Stellven/jiuwenswarm/tree/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/standalone/intent_compiler) | Implementation, local test suite, deployment instructions, and client surface. This is a compiler slice, not the full M1 Capsule library or whole-workflow implementation. |
| **[IMPLEMENTATION EVIDENCE]** | [R07 outcomes](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/evidence/live-R07/outcomes.json), [R08 outcome](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/evidence/live-R08-reference-resource/outcome.json), and [independent R08 release/export check](https://github.com/Stellven/jiuwenswarm/blob/73ed9e867d58a22ac57699913ecbd7f4d3619f2c/docs/code/Missions/M0/M0-001/evidence/v06-r08-export-independent.json) | Exact live-model sample and distinct resource-input follow-up; interpretation is in the results assessment. |

## Version boundary

- **[IMPLEMENTATION EVIDENCE]** The M0-001 receipt was captured October 8 and task scope names the source files and hashes. Its evidence describes that input set and the exact candidates recorded in each run.
- **[DESIGN AUTHORITY]** The current product input is PRD (4), received October 13. The current design package includes subsequent Capsule/model-routing reconciliation.
- **[OPEN QUESTION]** Before treating old compiler artifacts as current-contract compatibility evidence, compare the task’s recorded source bytes with PRD (4) and the current package’s contracts and decisions. In particular, check any public field-version, source-clause, and model-binding changes. Preserve original receipts and runs.
- **[RECOMMENDATION]** Use evidence only for the behavior it directly establishes; do not relabel it as having been generated under the newer sources.
