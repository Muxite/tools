---
name: held-out-build-gate
description: Build a new capability (tool, skill, module, capsule) safely with an independent check - write a manifest first; have a separate suite author write visible and held-out tests from the manifest alone; have an implementer who never sees the held-out tests build against the visible ones; admit through a code gate with a capped number of attempts that reveals only admit/reject plus a reason code; run an adversarial review when attempts run out. Use when an agent or team is about to create or extend a tool or library entry that others will rely on, when orchestrating several agents to build software, or when designing how self-built capabilities get admitted.
---

# Building behind a held-out gate

## Why

Outcome checks do not certify artifacts. When the builder's work is judged only by whether the task in front of it
passed, broken tools get kept:

- In Beyond Task Completion (arXiv 2604.00392), 215 of 222 tools kept by 3 tool-building methods (96.8%) score
  zero correctness on held-out tests of their own capability, while they run cleanly and nothing in the session
  flags them (99 tasks, Claude Haiku 4.5). Reference implementations pass all 16 suites, so the suites are fair.
- In CoEvoSkills (arXiv 2604.01687), 3 ways of letting an agent write its own skills without verification score
  30.7-34.1% against 30.6% with no skills; with a verification loop the same agent's skills reach 71.1%, above
  human-curated skills at 53.5% (SkillsBench, Claude Opus 4.6). The gain comes from the verification loop.
- A self-improving coding agent (Darwin Gödel Machine, arXiv 2505.22954) gamed its objective even with the
  checking functions hidden from it. Hiding is not enough: the gate must be mechanical and protected.

Thus: tests are fixed before the implementation exists, by someone who is not the builder, and the builder cannot
learn the held-out tests through the gate.

## Roles

Each role is a separate agent session (or person). Never merge 2 roles into 1 session.

| Role | Writes | Reads | Never reads |
|---|---|---|---|
| Owner / build decider | the manifest | the need: gap records, costs, how often the gap recurs | test code |
| Suite author | visible tests, held-out tests | the manifest only | any implementation |
| Implementer | the implementation | the manifest, the visible tests, gate verdicts | held-out tests, suite author's notes |
| Gate (code, not a model) | admit / reject + reason code | everything | n/a: it is deterministic and protected |
| Adversarial reviewer | findings | manifest, implementation, both suites, the attempt log | n/a |

The deciding agent does not build. Build only when a need repeats; a one-off need is served by the general path
and recorded as a gap.

## Procedure

### 1. Manifest first

Write the contract before any test or code. It is the only input the suite author gets, so it must be complete:

- purpose and scope: what the capability does, and what it explicitly does not do
- interface: commands, functions or tools, argument names and types, result shapes, error behaviour and messages
- file formats read and written, byte-exact where it matters
- side effects: files, network, subprocesses, what is never touched
- invariants and edge cases: empty input, missing files, invalid values, ordering, determinism
- dependencies: required vs optional, and behaviour when an optional one is missing
- where the manifest is silent, the implementation may choose and tests must not assume

Freeze the manifest (commit it, record its hash). A contract change is a new manifest version, and the suite is
rewritten from it. If this manifest and a test disagree, the manifest wins.

### 2. Suite author writes tests from the manifest alone

- **Visible tests**: cover the main paths and error cases; handed to the implementer as its working check.
- **Held-out tests**: different inputs for the same contract (variants, compositions, adversarial and edge
  cases, regressions), generated from the contract, never from the implementer's work or a past trajectory.
  They live where the implementer cannot read them.
- Every test cites the manifest clause it checks. A test that needs something the manifest does not say is a
  manifest gap: report it to the owner, do not guess.
- Calibrate: a reference or hand-written solution (or a careful dry run against the manifest) must be able to
  pass every test, so a failure means the artifact, not the suite. Tests that need an optional dependency skip
  when it is missing.
- The suite is fixed before implementation starts. After admission it becomes the permanent regression suite.

### 3. Implementer builds against the visible tests

- Gets the manifest and the visible tests. It must not search for, read or run held-out tests, or read the suite
  author's notes, even if it could find them on disk.
- Implements to the manifest, not to the visible tests: passing visible tests is necessary, not sufficient.
- Runs the visible suite locally as often as it likes.

### 4. The gate: capped attempts, minimal feedback

- The gate is deterministic code: it runs visible + held-out tests (plus static checks such as declared effects,
  schema conformance, duplicates) and returns **admit** or **reject plus a reason code** (for example
  `SCHEMA_NONCONFORMANT`, `EFFECT_UNDECLARED`, `INVARIANT_VIOLATED`, `DUPLICATE_CAPABILITY`, or the failing
  manifest section).
- It never returns held-out test names, inputs, expected values, diffs or tracebacks. Unlimited retries or rich
  feedback let the builder learn the held-out tests, which turns them into visible ones.
- **Cap the attempts** (for example 3-5). Log every attempt with its verdict.
- Stage it when checks are expensive: a cheap structural screen on every attempt, the full held-out suite only
  for candidates that pass it.
- The gate and the suites are protected: the implementer cannot modify them, and the gate is never a model that
  reads content the implementer controls (prompt injection through the artifact is the threat).

### 5. When attempts run out: adversarial review

Do not raise the cap and do not show the held-out tests. Instead a reviewer who is neither the implementer nor
the suite author examines the manifest, the implementation, both suites and the attempt log, as a hostile reader:

- Is the manifest ambiguous or incomplete at the failing clause? Then fix the manifest (new version), and have the
  suite author update the tests from it.
- Is a test wrong, or does it assume something the manifest does not say? Then fix the test, with the manifest
  clause cited.
- Is the implementation wrong? Then report the flaw class in manifest terms (not the test content) and return
  the gap to the build decider: retry with a fresh attempt budget, version an existing capability, or wait.
- For each flaw found, search for every other instance of the same class and fix all of them.

Record the outcome: what failed, which role fixed what, and the new manifest or suite version.

### 6. Admission and after

- Admitted artifacts enter an append-only, versioned library; nothing is edited in place. New versions must
  pass the previous version's suite. A contract change means a new id.
- Re-run the suites between releases; retire artifacts that stop passing rather than patching them silently.

## Running this with several agents

- Give each role its own session and its own working directory; pass only the files the table above allows.
- The orchestrator keeps the held-out tests outside every implementer-visible path (a separate folder or
  temporary location the implementer is told never to read) and runs the gate itself.
- Tell the implementer in its brief: the manifest path, the visible test paths, the attempt cap, that hidden
  tests exist and must not be looked for, and that feedback will be admit/reject plus a reason.
- Tell the suite author: write tests from the manifest alone; do not read the implementation; report manifest
  gaps instead of guessing.
- Tests run with the project's normal runner (for example `python -m pytest`); a missing implementation makes
  tests fail, which is expected before the build.

## Checklist

- [ ] manifest written, frozen and versioned before tests or code
- [ ] suite author saw only the manifest; every test cites a clause; suites calibrated
- [ ] held-out tests stored where the implementer cannot read them
- [ ] implementer saw only the manifest and visible tests
- [ ] gate is code, protected, returns admit/reject + reason only, attempts capped and logged
- [ ] exhausted attempts went to an adversarial review, not to a higher cap or leaked tests
- [ ] admitted artifact versioned; its suite kept as the regression suite
