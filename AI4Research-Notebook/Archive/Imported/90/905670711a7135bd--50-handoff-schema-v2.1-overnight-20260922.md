# 50: Handoff. Capability Capsule schema v2.1 to v2.3 (2026-09-22)

**Current: v2.3, the version to present** (Muk, 2026-09-22). Branch `schema-v2.1-overnight`, commit `3858111`; not pushed
or merged. The obby vault (`tundle/obby/HANDOFF.md`) holds the current state. This note records how it got there.

| Version | What changed |
|---|---|
| v2.1 | derived from all the evidence; jiuwenswarm and RSI read in code; overlays pinned; RSI's gate counted as evidence only |
| v2.2 | self-improvement restored from the 2026-09-15 report: three clocks, the generalist, cold-path roles, monotone versions, protected components, the audit loop. Report §3 compares today's capsules record by record. Unpinned dependencies need a written purpose |
| v2.3 | a consistency pass after an Opus review: one Standing writer; the generalist only on gated outputs; the freeze checks the snapshot; `contract_hash`; one version rule and one running-plan policy; the run contract, claim status and Finding visibility recorded; unattended runs covered in full; an exploration quota |

**Rules since:** record important things in the obby vault; reviews use Haiku, then Sonnet, never Opus unless asked.


Read this first for Capability Capsule. It builds on note 49, the v1.6 workshop baseline, and does not replace it.
v1.6 is still what the committed workshop deck shows. v2.1 is the merged and revised version, on its own branch for
Muk to accept or reject.

## Where everything is

| What | Where |
|---|---|
| **Schema v2.1**, merged | `capsule-openjiuwen/merged/SCHEMA.md` (branch `schema-v2.1-overnight`); copy `Capability Capsule Schema v2.1 - Muk.md` |
| How the evidence gives the schema | `merged/DERIVATION.md`; copy `Capability Capsule Schema Derivation - Muk.md` |
| Report, 64 pp | `merged/REPORT.md` → `.docx`; copy `Capability Capsule Merged Report - Muk.docx` |
| Deck, 41 core and 10 backups | `merged/build_spec.py` → `.pptx`; copy `Capability Capsule Merged Deck - Muk.pptx` |
| Review log (Haiku, Sonnet, Opus) | `capsule-openjiuwen/verify/V10-overnight-20260922.md` |
| Resume lines | `capsule-openjiuwen/RESUME-ACHIEVEMENTS.md`; copy `Resume Achievements - Capability Capsule - Muk.md` |
| Unchanged, for comparison | v1.6: `SCHEMA.md`, `deck/`. Independent version: `alt/` |

## The question, and the answer

**Question.** Taken together, what do these say the schema must be?

- the 21 papers;
- the AI4Research workflow;
- agent-core;
- jiuwenswarm.

**Answer.** Six records, each written by one party: Declaration, Verdict, Standing, Plan step, Binding and Finding.

- **Authority.** Only a checked declaration grants authority; observation can only withdraw it.
- **Predicate parity.** Eligibility is decided by declared predicates through one evaluator.
- **Pinning.** Everything a sprint loads is pinned by hash. That includes overlays and composite members.

a to g in one line each: `merged/REPORT.md` §2.

## What the jiuwenswarm reading added

| Finding (jiuwenswarm `02b37f47f`, agent-core `e23806c1`) | Consequence in v2.1 |
|---|---|
| 34 bundled skills: 33 declare only a name and description. None declares inputs, outputs, preconditions or effects. 25 ship scripts | imports enter as provisional, and a person confirms the effects |
| agent-core's skill loader reads only `description`, so `allowed_tools` is not enforced | frontmatter is a proposal, never enforcement |
| SkillPacks name their members, and a disabled member disables the pack (since `6f4eaa1b6`, 2026-09-17) | composites pin members by hash; a withdrawn member suspends the composite |
| Swarm Skills declare dependencies and limits as prose, and their Leader decides roles at run time | not admissible in v1: the Leader plans, which is above the ceiling |
| Teammate experience saves automatically. TTSE injects tips with no approval dialog. SkillUseRail adds experience text by skill name | **overlays**, hashed and pinned per sprint, or not loaded |
| RSI accepts candidates only on its own suite, with held-out cases forced to 0 in single-harness mode | RSI's result is `builder_gate` evidence. Admission uses held-out checks from verification, so RSI needs no change |
| RSI hashes its packages and keeps a pointer with rollback, blocked while tasks run | compatible; the librarian writes the pointer; the rollback guard becomes the concurrency rule |

## What review changed (details in V10)

- **Sonnet** found the SkillPack cascade dated to the wrong commit: it came with `6f4eaa1b6`, not `02b37f47f`. It
  also found two path slips, and a contradiction in AutoHarness's own documentation. It confirmed every corpus count.
- **Opus** changed five positions:
  - team skills stay out of v1;
  - RSI's held-out split inside RSI is a code change, so CC does not depend on it;
  - a tool-call rail enforces the tool set, not the effects, which are enforced only in the sandbox;
  - Bindings carry pre-approved fallbacks, as today's freeze does;
  - planning-time evaluability is computed from upstream effects, not declared.

  It also caught a misreading of *More Skills, Worse Agents?* and an overclaim about observation.
- **Haiku**'s length findings were false (checked by measurement).

## Questions for Muk (not decided overnight)

1. ~~Present v1.6 or v2.1?~~ Answered: the newest version, now v2.3 (Muk, 2026-09-22).
2. Is it acceptable that team skills stay out of v1? The supervisor may want them in.
3. Overlays pinned per sprint means teammate experience and TTSE are either pinned or not loaded in AI4Research
   sprints. Does that need the jiuwenswarm owners' agreement first?
4. Merge `schema-v2.1-overnight` into `supervisor-answers-20260918`? Nothing is pushed.

## Rules that saved time

- `git checkout` writes CRLF here. Normalise to LF before patching multi-line anchors.
- A block replacement must stop at the next list item, not the next blank line, or it swallows neighbouring bullets.
- Check every reviewer claim in source first. Reviewers this pass were wrong on title lengths (Haiku) and on a
  missing script (Sonnet), and right about a commit date that the author had assumed from a commit message.
