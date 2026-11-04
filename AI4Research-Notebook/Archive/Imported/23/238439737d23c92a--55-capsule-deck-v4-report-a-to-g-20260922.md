# 55: Capability Capsule, deck v4 and report rewritten around a clean a to g (2026-09-22, evening)

Builds on note 54 (schema v2.8). Branch `schema-v2.1-overnight` in `capsule-openjiuwen`, commit `ab0bb28`; not pushed.

## What changed

- **Deck v4, written fresh in logical order:** the problem, a to g, the detail, the fit with openJiuwen, a summary of
  how each part serves the tools, and the limits. 28 core slides and 5 backups (was 45). Key numbers on the slides,
  no "thus" strips, bigger figures, no questions slide, advantages on two slides each citing its paper, and "Under
  CC" columns labelled as design not yet built.
- **New slides:** the capsule's records and the run's records (new figure R1: the planner never writes to a capsule;
  the freeze assigns capsules to DAG nodes by hash); what each record holds, with where the hash, parentage and
  provenance live and what a Finding is for; the Declaration's fields by section in `section.field` names; how
  AI4Research selects today, verified in source; how each part serves the tools and AI4Research.
- **Verified:** AI4Research already filters by code first (types, effects both ways, network, proof classes, trust,
  admission status), never on preconditions, then one model call reads the full rows of every node's eligible
  capsules (`elastic_planner.py:4553-4760`).
- **Report rewritten** so chapter 2 answers a to g cleanly, with evidence, the two real examples in (f), and a new
  (h) on how each part serves the tools. The questions chapter is removed.

## Deliverables (tundle copies)

`Capability Capsule Merged Deck - Muk.pptx`, `Capability Capsule Merged Report - Muk.docx` (53 pages),
`Capability Capsule Schema v2.8 - Muk.md`.
