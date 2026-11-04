# 2. Changes and diagnosis

**Diagnose before changing expected behavior.** Compare PRD, design, actual behavior and verification expectations. Check fixtures, environment and versions.

## Bugs and issues

| Finding after diagnosis | Action |
|---|---|
| Code follows design but violates the agreed requirement | Open a design issue. Correct design and affected implementation. |
| Code violates a sound design | Open a code issue. Keep expected design behavior and fix code. |
| Check, fixture, environment or verifier is wrong | Correct verification or the prerequisite. Recheck. |
| Requirement or cause is unclear | Record uncertainty. Investigate. Constrain only affected work. |

An issue needs reproduction, expected/observed behavior, code commit, PRD revision, check/verifier evidence, affected modules and next action. Link the design **at its commit**, for example `.../blob/<commit>/path.md#L42`. Name its section. If the relevant draft is uncommitted, attach its exact bytes/hash and say so.

Notify implementation/checking contributors. Include design contributors when design meaning is disputed, and requirement contributors when obligations are disputed. Link issues to existing TASK/specification records.

## Change trace

- Identify the changed source or assumption.
- Trace producers, consumers, permissions, deployment, exports and evidence.
- Update authoritative definitions, versions/migration, summaries and diagrams together.
- Preserve received sources and old runs. Mark affected evidence stale and repeat affected checks.

## Timelines and phases

- Keep targets, forecasts and estimate assumptions distinct. Affected contributors decide changes to team commitments. Date-only moves update planning. Change design when obligations, boundaries or exits change.
- M1 to M2: carry accepted evidence, unfinished work, blockers, decisions and changed assumptions forward.
- Example: late model credentials block live integration evidence. Resequence independent work or revise the target. Mock results cannot satisfy a live-integration exit.

See [phase exits](../delivery-phases.md) and [failure handling](../failure-and-human.md).
