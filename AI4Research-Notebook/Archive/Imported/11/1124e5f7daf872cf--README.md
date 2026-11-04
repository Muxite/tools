# Capability Capsule architecture closeout

**Status: working evidence dossier and implementation handoff; not architecture authority.** Updated October 13, 2026.

This folder reconciles the current maintained architecture and PRD with the pushed Intention Compiler implementation and its recorded evidence. It supports continued architecture work outside the full and compact design packages. The maintained package and separately supplied PRD remain authoritative; this dossier allocates no coding TASK, AC, or IF identity.

## Reading order

1. [Source and version register](source-register.md) pins the exact inputs and implementation candidate.
2. [Results assessment](results-assessment.md) distinguishes local checks, live samples, blocked checks, and the R08 evidence-tool discrepancy.
3. [M1 Capsule map](capsule-map.md) separates the implemented compiler slice from the complete M1 capability set.
4. [Architecture reconciliation ledger](reconciliation-ledger.md) records alignments, gaps, and unresolved decisions.
5. [Finishing checklist](finishing-checklist.md) orders the remaining documentation work.
6. [Implementation handoff](implementation-handoff.md) turns the reconciled findings into inputs for the native coding-task workflow.

## Evidence labels

- **[DESIGN AUTHORITY]** Current PRD or maintained design-package requirement.
- **[IMPLEMENTATION EVIDENCE]** Versioned source, task record, or captured artifact from the compiler branch.
- **[MEASURED SAMPLE]** An observed run or test result; its stated sample count and limits apply.
- **[UNVERIFIED]** Required behavior not demonstrated by the referenced evidence.
- **[OPEN QUESTION]** A decision or reconciliation still needed.
- **[RECOMMENDATION]** Proposed next work for architecture review; not an adopted requirement.

The source register identifies every authority boundary. Branch evidence is linked at the immutable commit, and large runtime-state files are referenced rather than copied. Current design-package files are linked in this checkout; this notes folder is Git-ignored by repository policy and is local working material. The completed [routing-integration package receipt](../../experiments/design-package-routing-integration-2026-10-13/README.md) records the maintained-package delivery separately.

## Working boundary

Do not infer full M1 Capsule completion from the compiler slice, treat one live run as a reliability result, or convert implementation-specific settings into architecture-wide requirements. Resolve substantive changes through the maintained design and PRD process, then update the native coding register and TASK records under the Code SOP.
