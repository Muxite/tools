---
id: cc-pilot-case-catalog
status: proposed
source: jiuwenswarm/docs/architecture/design-package/README.md; jiuwenswarm/docs/architecture/design-package/2-capability-capsules.md; jiuwenswarm/docs/architecture/design-package/reference/capsules/README.md
last_reviewed: 2026-10-20
next_action: Audit whether a runnable M1 adapter can faithfully execute these tasks; freeze only after audit and custodian split registration.
---
# CC pilot case catalog

> **Proposed and unrun.** Six concrete development cases cover synthetic intent/brief adapters and recurring research work. There are no results. Exact prompts, self-contained fixtures, and development scoring keys are in [[Experiments/Development-Cases/README|Development Cases]]. No held-out prompt or answer material is stored here.

Links: [[Workstreams/CC Effectiveness]] · [[Home]]

| Case | Split | Task family | Fixture and observable deliverable |
|---|---|---|---|
| DEV-01 | Development | Synthetic intent normalization adapter | Two requests (one actionable, one missing a required scope); emit normalized intent JSON and clarification state |
| DEV-02 | Development | Synthetic research-brief adapter | Convert a bounded request and source constraints into a research brief with scope, exclusions, outputs and acceptance criteria |
| DEV-03 | Development | Daily coding | Repair a small Python CSV summarizer against concrete examples and explicit constraints; return patch and test evidence |
| DEV-04 | Development | Experiment design | Design a paired study from supplied synthetic pilot context; include treatment, controls, outcomes, threats and stopping rules |
| DEV-05 | Development | Reporting | Write a concise evidence report from synthetic results, preserving nulls and clearly separating observations from interpretation |
| DEV-06 | Development | Literature synthesis | Synthesize a tiny synthetic evidence packet and distinguish randomized, observational, and protocol-only evidence |
| HOLD-A | Held out | M1 intent/requirements family | Reserved with independent custodian; identity and contents sealed from proposer |
| HOLD-B | Held out | Daily coding/research operation family | Reserved with independent custodian; identity and contents sealed from proposer |
| HOLD-C | Held out | Experiment design/reporting family | Reserved with independent custodian; identity and contents sealed from proposer |

## Split rules

Development case folders separate agent-facing prompts/fixtures from scorer-only keys. The input-only manifest hashes just the prompt and fixture files. Execution adapters must load only the input paths shown in [[Experiments/Development-Cases/README|Development Cases]]. Held-out identities and hashes must be committed to an access-controlled custodian manifest before proposer design or tuning begins. The proposer receives development cases only. Do not create, store, or reveal held-out prompts or keys in this notebook. If a held-out identity or contents leak, the custodian retires it before execution.

The development pilot is 3 paired repetitions per task, randomized and order-balanced. It tunes process and rubric only. Freeze methods before the custodian runs held-out work. Never manufacture or infer held-out results.

See [[Experiments/cc-effectiveness-protocol|CC Effectiveness Protocol]] for the design, [[Experiments/Development-Cases/README|Development Cases]] for prompts/fixtures/keys, and [[Experiments/raw-results-schema|Raw Results Schema]] for records.
