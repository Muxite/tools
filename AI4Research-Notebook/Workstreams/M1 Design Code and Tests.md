---
id: workstream-m1
status: active
source: Resources/M1 Readiness; Sources/Research Intent
last_reviewed: 2026-10-23
next_action: Check exact source identities in Current Baseline, then qualify connected execution on the selected candidate
---
# M1 design code and tests

## October 23 implementation progress

[[Resources/Current Baseline]] is the current source-status route. The previously inspected M1 source integrates typed planning and optional capsule code; the local Builder branch is a separate candidate. [[Activities/2026-10-23 Delivery and Verification Status]] preserves the earlier separate-branch checkpoint. Neither source integration nor historical local tests establish a completed live campaign or full M1 acceptance.


**Problem:** the next research stage needs usable code and trustworthy test evidence. A coherent design package does not prove that its implementation exists or matches the current contracts.

Use [[Resources/M1 Readiness]] for the audited starting point and [[Designs/Design Library]] for current versus historical sources. Preserve exact candidate commits, local changes, test commands, fixtures, environments, and observed outcomes.

## Current coder handoff

The user reports working M1 code on another machine; that is not a locally inspected runtime result. [[Resources/Coder Prompts/benchmark-runner]] requests development tooling in our AI4Research branch of JiuwenSwarm, operating above isolated targets. It runs queued cases sequentially as a control/data runner and exports a human-review matrix. Authorized implementation edits belong in our branch; benchmark execution must not overwrite user files, mutate their original checkout or alter live state. Developers and their delegated agents are permitted callers. Humans judge the tasks.

This supersedes the earlier sidecar-only/automatic-referee handoff. Existing M1 product/client contracts remain context; the runner integrates through supported APIs/CLI or reports gaps. M2 lab/factory construction is not a prerequisite.

## Immediate work

- Reconcile current compiler candidates with the maintained M1 design and PRD receipt.
- Identify which CC tasks can actually execute before enrolling them in the pilot.
- Record source changes and interface impacts in the repository's existing coding process.
- Keep historical test reports attached to their original candidates; rerun affected checks for a changed candidate.

The meeting prioritizes test reports and code work. Its “this week” and “as fast as possible” wording is retained in [[Sources/Research Intent]], with no invented deadline. Presentation preparation follows concrete evidence rather than replacing this work.

Research experiments in this vault are separate from official M1 TASK/AC/IF registration and acceptance. Existing source records retain their identities and authority.
