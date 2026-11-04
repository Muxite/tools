---
id: required-m1-typed-planner
status: historical-checkpoint-with-later-source-update
source: Sources/Prompts/2026-10-23-required-m1-planner.txt; Sources/Prompts/2026-10-23-catalog-dag-repair.txt; Sources/Prompts/2026-10-23-push-and-adversarial-review.txt; Sources/Prompts/2026-10-23-review-and-fix.txt
last_reviewed: 2026-10-23
next_action: Qualify the integrated Planner and production checks; retain earlier branch evidence
---
# Required M1 typed Planner

**Later source update:** remote `ai4r_M1` at `809351f8` now contains the required Planner and optional capsule source. Statements below about unmerged local features describe the earlier checkpoint and are superseded for that remote baseline. Source merge is not qualification, activation, deployment or runtime acceptance. See [[Resources/Handoffs/m2-labs/README|M2 implementation handoffs]] for current source receipts and scope.


The latest user correction supersedes the optional-Planner framing in
[[Activities/2026-10-23 Capsule Branches and Factory Direction]]. Typed DAG
planning is required M1 work in the existing core `research.planner`. Individual
Generalist and utility releases remain optional and require normal admission.
The earlier note and source captures are retained; this interpretation does not
rewrite the older design or manufacture upstream implementation evidence.

Local `ai4r_M1` was fast-forwarded to `e296d2b`, merging deployment usability
first. Work continues in `AI4Research-Development/jiuwenswarm-m1-current` on
`m1/required-typed-planner`. The feature merges the existing framework but
removes its separate optional Planner. No scientific work capsule is changed.

The core Planner receives complete pinned admitted declarations and assembles
compatible typed graphs, including generic work. Scientific work retains its
mandatory Evaluation/Delivery release path. One invalid structural candidate
can receive one correction using retained public validation diagnostics, within
one work invocation. Final independent checks, semantic verification and gates
remain required. Runtime/authentication failures do not trigger this repair.
Earlier one-shot wording is explicitly amended by the user's latest direction;
D30's one linked new Compiler attempt after final infeasibility remains bounded
separately. Candidates and advisory diagnostics are retained for export.

See implementation `docs/capsules/typed-planner-m1.md` and inspected source
hashes in `typed-planner-sources.json`. The maintained design-owner checkout is
our modified AI4Research, not pristine upstream JiuwenSwarm. New profiles use
versioned captures; old state and accepted plans are not rewritten.

The deployment push was attempted but Git has no usable GitHub HTTPS credential.
Remote `ai4r_M1` remains at `bfc30ba` at the last check. Deployment tests: 26 pass.
Planner validation is in progress; controlled replies establish mechanics, not
live model reasoning or research quality. Docker's Linux engine remains
unavailable; Docker/SSH/ARM64/Spark/live-model checks are not claimed.

## Final local handoff

Deployment usability is now pushed to remote `ai4r_M1` at `e296d2b` using the
existing authenticated SSH connection; the earlier HTTPS blocker is resolved
for this push. The Planner is committed separately as `9d8f21b140119ccec05f1a4f3cd5fa302cc01df5`
on local `m1/required-typed-planner`; that feature was not pushed.

Adversarial review resulted in fixes for generic graph restrictions and
cross-invocation artifact references in Planner attempt events. Checks cover
one correction of a typed cycle, exhausted repairs, independent verifier
rejection, exact source pins, frozen acceptance, retained diagnostics and
sequential source selection. 109 selected Windows checks and 39 Linux checks
pass. New Linux profile capture/repeat capture preserves state. The outdated
trace test now checks current v2 deferred export semantics rather than obsolete
eager copies; its production function is unchanged. One broader finite-run
check cannot pass in the isolated environment without pinned OpenJiuwen.
No live-model, Docker/SSH deployment, ARM64 or Spark success is claimed.

Portable handoff: `AI4Research-Development/ai4r-m1-typed-planner-handoff-20261023`.
The earlier capsule bundle remains historical. The updated core Planner can
consume normally admitted optional capsules after those branches merge; it
requires no hardcoded new workflow choice. Factory-produced declarations
should describe operation preconditions and limitations as well as port types.

Vault validation retains only the two previously missing Paper2Agent presentation
links (`rev9.pptx` and `review-rev9/`); new note/capture links introduce no errors.

Later deployment revision: [[Activities/2026-10-23 No-sudo Benchmark Launch]]
removes automatic host setup and adds the simple existing-image launch command.
