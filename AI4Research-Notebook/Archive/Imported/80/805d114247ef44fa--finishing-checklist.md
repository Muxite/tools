# Architecture-document finishing checklist

This is a prioritized working list, not an additional acceptance register. Complete each item with evidence and keep unresolved points marked.

| Order | Label | Work | Completion evidence |
|---:|---|---|---|
| 1 | **[RECOMMENDATION]** | Freeze the source crosswalk: exact PRD (4), current full/compact package receipts, router design source, M0-001 October 8 input receipt, and candidate identities. Identify material field/version/clause changes. | Reviewed path/hash/source map; no historical source silently treated as current. |
| 2 | **[RECOMMENDATION]** | Close the compiler-result interpretation: inspect R08 independent verifier code and release/export records; resolve its `invalid_for_product` exception; link current local-suite evidence separately from R07/R08 model samples. | Written explanation and affected checker result; original evidence retained; corrected rerun tied to exact candidate if available. |
| 3 | **[RECOMMENDATION]** | Produce complete M1 stage-to-Capsule inventory, including work CCs, verifier assignments, protected checks/gates, supporting tools/services, Phase 2 target, and Phase 3 modules. | Each current PRD stage/User Story maps to producer, inputs/output, independent checks/verifier, gate, dependencies, owner, phase, and implementation status. |
| 4 | **[RECOMMENDATION]** | Reconcile reusable compiler patterns against current Capsule, node/subnode, checking, and routing integration contracts. Separate transferable behavior from implementation-specific mechanisms. | Field/authority/budget/evidence crosswalk with compatibility notes and explicit open items. |
| 5 | **[RECOMMENDATION]** | Identify proof still required: browser journey, Docker/Compose deployment, repeat semantic samples if feasible, plus full workflow and phase-specific checks outside compiler scope. | Explicit evidence owner/prerequisite/status; no “pass” for unrun or blocked checks. |
| 6 | **[RECOMMENDATION]** | Prepare changes for the maintained architecture: carry forward only decisions confirmed by source reconciliation and owner agreement; synchronize full and compact packages, diagrams, indexes, examples, and portable validators as appropriate. | Reviewable change list with source and decision links; both packages validate and shared contracts match. Do not copy old project-coordination planning material. |
| 7 | **[RECOMMENDATION]** | Hand reconciled implementation work to the native M1 coding workflow. Preserve occupied identities, allocate none in this dossier, and record exact candidate/source/evidence expectations in registered TASK records. | Updated M1 register and native TASK/spec/plan/tasks under current Code SOP; acceptance tied to observed evidence. |

## Stop conditions

- **[DESIGN AUTHORITY]** A required source or contract mismatch blocks dependent claims until reconciled.
- **[DESIGN AUTHORITY]** A missing runtime, browser, model, or container prerequisite remains `BLOCKED` or `UNVERIFIED`, not a documentation pass.
- **[RECOMMENDATION]** Do not merge the Capsule and routing-owner designs into every component document. Keep the shared binding/dispatch contract in one interface reference and link to it from Capsule and routing component pages.
