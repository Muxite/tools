# Optional future-worker reading route

**Proposal only; not an architecture, checklist, gate, or M1 requirement.** Start with the assigned PRD and maintained design; these remain authoritative. Use only relevant notes to frame a bounded comparison. If the design lacks a relevant seam or M1 capability, report that prerequisite; do not infer or implement behavior. The [optional experiment brief](optional-use-experiment.md) has controls and reporting guidance.

## 1. Consumer value and compatibility — highest information value; can be diagnostic before a full runtime exists

Read [capsule feeds](capsule-feeds.md), [typed selection and abstention](typed-selection.md), and [scientific workflow transfer](scientific-workflow-transfer.md). Probe candidate selection through resolved context to downstream result. Compare no feed, a matched procedure, a similar but incompatible procedure, and (if feasible) length-matched irrelevant context. Inspect consumer use, failure mode, and independent expected outcomes. Without an M1 consumer/trace seam, an offline diagnostic tests retrieval/compatibility only, not runtime benefit.

## 2. Stale or conflicting lessons — next; depends on an advisory feed and identifiable versions

Read [memory lifecycle and composition](memory-lifecycle-and-composition.md) and the scientific-workflow card. Probe lesson retrieval/revalidation against the run’s pinned protocol/environment and observe downstream use. Compare current, superseded, conflicting, unresolved, and no-lesson conditions. Keep gate/permissions fixed; measure valid reuse, stale-use errors, unnecessary rejection, and abstention. Lessons remain advisory. If M1 cannot preserve source/version or show which lesson affected a run, report that observability gap; results cannot separate invalidation from missing provenance.

## 3. Scientific repeatability — only when a real runner, frozen inputs, and outcome checks are available

Read [M2 workflows and tools](m2-workflows-and-tools.md) and [scientific workflow transfer](scientific-workflow-transfer.md). Probe frozen protocol/environment execution, interruption/retry, and result capture at the experiment/runner-to-evidence seam. Include scientifically valid negative outcomes and human assists. Compare repeatability and reconstructed traces against an independent measurement or adjudicator; separate scientific variation from infrastructure failure. Simulation or generated-file import can test those narrower properties but does not establish physical or scientific reproducibility.

These comparisons are optional research questions. Existing papers motivate them but do not set acceptance thresholds or establish that any proposed capability exists in M1. Record unavailable seams and unresolved evidence as findings, not new requirements.
