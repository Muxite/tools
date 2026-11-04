# 53: Capability Capsule, final for Muk's review: schema v2.7, report and deck v3 (2026-09-22, night)

Builds on notes 51 (v3 around a to g) and 52 (v2.5, v2.6). Branch `schema-v2.1-overnight` in `capsule-openjiuwen`,
commit `715789d`; not pushed or merged. Directives: `obby/Directives.md`.

## What v2.7 added

- **Node gates** (§4.5b): three parts, three writers (step acceptance from the request, the capsule's own checks,
  artifact-type checks). An admitted capsule very likely passes its own part. A `fit_failure` Finding charges a
  failed step check with passing capsule checks to the fit, not the capsule.
- **Suites travel with the lineage** (§4.7): the Verdict lists every suite; a child (and co-parents) inherit them.
  RSI reads visible suites and adds cases; sealed ones only as pass or fail; a fresh held-out addition each generation.
- **`guarantees.exempt`** (§4.1 step 5, §4.14): generalists are enrolled at level `exempt`, below provisional. Several
  (Codex, Claude), named in the run contract, bound by every plan gate, never supporting a claim.
- **The capability tree** (§4.13a): every Declaration a node, rejected ones included; CC stores and exposes
  (guaranteed from its own records, optional what builders supply); RSI's policy chooses where to branch; no score.
- **Where each part lives in openJiuwen** (§4.17a): Declaration = Card; invocation = harness-protocol Turn or item;
  generalists = harness providers; approvals = `PermissionEngine` `ASK`; trajectories consumed from `agent_evolving`.

## The deliverables

| What | Tundle copy |
|---|---|
| Report, 50 pages: a-to-g answers, then Foundation, Pick, Verify, Improve, Remove, Plan and schedule, example, today, limits, questions | `Capability Capsule Merged Report - Muk.docx` |
| Deck, 39 core slides and 3 backups, 36 minutes planned; a caption on every figure slide | `Capability Capsule Merged Deck - Muk.pptx` |
| Schema v2.7 | `Capability Capsule Schema v2.7 - Muk.md` |

Reviews (Sonnet only) and fixes: `capsule-openjiuwen/verify/V12-v25-v26-20260922.md`.

## Open for Muk

- **Names:** a CC "Plan step" is an AI4Research plan node, not an agent-core "Step" (one agent-loop cycle). Kept, with
  a terminology table; renaming to "Plan node" is possible.
- **Tundle history** is over its limit; pruning waits for approval.
