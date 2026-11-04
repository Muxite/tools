# R2: adversarial review of REPORT.md §6.1 challenges

Reviewed 2026-09-14 against REPORT.md v0.4 and AI4Research `b0bf165f9` (checked out, clean). Scope:
§6 head, §6.1, §6.2, with §3, §4 and App. B for overlap.

Numbering note: the brief says 28 challenges and "#28". The current REPORT.md has **20**: groups A-C
and E number 1-19, and group F holds language coverage as **#20** (HANDOFF §10b says #28 was renumbered
to #20). The deck has no "Full table of 28" string. Its speaker note says "Full table in report §6.1"
(`build_deck.py:519`). This review uses the current numbers 1-20.

Result: 20 items become 13, in 5 groups (A, B, C, E numbered, D kept as the capsule pointer).

---

## 1. Decision table

| # | Current title | Decision | Target | Reason |
|---|---|---|---|---|
| 1 | No external measurement of anything | KEEP, absorb 15-17 | new 1 | root item. 15-17 are evidence for it, not separate challenges |
| 2 | Provenance is not truth | MERGE with 4 | new 3 | same root: what a literature verdict certifies. §3.8 and App. B already explain it |
| 3 | Claim extraction recall is unmeasured and probably low | KEEP, trim | new 4 | unique gap (misses never reach `unsupported_claims`). Drop "probably low": a hedge on an unmeasured value |
| 4 | The span hash is recorded, not enforced | MERGE into 2 | new 3 | a sub-case of verdict strength. Settle action kept |
| 5 | Rubric gates look deterministic | KEEP | new 2 | unique 20 of 43 count. Grouped with measurement: both concern what a PASS means |
| 6 | 1 repair per stage, then fail | MERGE with 7 | new 6 | same root: the pre-freeze loop has a fixed budget and no blocking reviewer. Wording fix: intent repair is configurable up to 4 |
| 7 | Advisory reviewers cannot block | MERGE into 6 | new 6 | stated in §3.1 and §3.3 limits and App. B. Only the audit action is new |
| 8 | No undefined-branch policy | KEEP | new 8 | unique, deck cites it, §6.2 carries it |
| 9 | A frozen contract is only as good as its compilation | KEEP, reword | new 7 | unique measured number (13 of 22, 59.1%, checked p. 17 Table 6). Evidence now names the open-capability route |
| 10 | No re-planning | MERGE with 11 | new 9 | same root: a wrong or unbindable plan has no recovery path inside the run |
| 11 | No generalist fallback | MERGE into 10 | new 9 | 1 clause. Detail lives in §3.3 and the capsule report |
| 12 | The substrate caused the failures | KEEP, reword | new 10 | overclaim in the title (2 incidents, not "the failures"). The 27.4 pp figure is evidence for §5.1, not a settle action |
| 13 | The CLI-agent path has generality and no trust | KEEP, add 21 of 79 | new 11 | unique trust gap. Takes the 21 of 79 figure from deck notes and §3.9 |
| 14 | Retrieval failure ends the run | KEEP, correct | new 12 | concrete failure, but the evidence conflates 2 runs and the settle action is partly stale (Finding F1) |
| 15 | internal evaluation stricter, external absent | MERGE into 1 | new 1 | restates 1. The 24 journeys and 34 kept failures are in §2 and §3.10 |
| 16 | automated review is weak everywhere | MERGE into 1 | new 1 | field observation that motivates 1. 57% is also in §3.9, §4.1 and §4.5. 11-16% appears only here, so it moves into 1 |
| 17 | human checking is also weak | MERGE into 1 | new 1 | field observation; 60.8% is also in §3.8. "Human review is not the fallback" survives as 1 clause |
| 18 | the differentiator has a shrinking window | MOVE | §6 prose, 1 line after Behind | positioning, not a challenge. "Months, not years" is an unsourced prediction: cut |
| 19 | autonomy needs humans removed that the design needs | KEEP, add evidence | new 13 | real design tension. Add the checked l.815 fact: the clean run needed 6 attached PDFs |
| 20 | Language coverage (English-only text stages) | KEEP, compress | new 5 table row + 4 bullets. Recommendation to §6.2 | keeps every key fact and file:line. Evidence/recommendation/testing/limits block cut from 66 lines to about 10 |

Group D (capsule-library pointer): KEEP unchanged. `build_reading.py:349` replaces group "D" with the
capsule report's items, so the letter must stay D.

---

## 2. Findings

### F1. #14 conflates 2 runs; its fix is partly already in code (MAJOR)

REPORT l.724: "Semantic Scholar HTTP 429 → frozen `fail_run` cancelled 13 downstream nodes (log l.814);
root cause: an empty services mapping dropped the multi-provider search (log l.663)".

The log is `harness/metadata/pre-scheduler-stabilization-log-20260829.md`. It records **3 separate runs**
ending at literature discovery after an HTTP 429, each with a different cause:

| Log | Sprint | Cause recorded | Fixed? |
|---|---|---|---|
| l.326-329 | `...-00e0c11e` | frozen `workspace_reads=[]`: no deterministic source inventory, so the 6 PDFs were never bound | yes, `solar.workspace_source_inventory.v1` (l.329) |
| l.662-664 | `...-e42d821b` | the registry adapter passed an empty services mapping, which removed the `discover_sources` multi-provider service (arXiv, Europe PMC, OpenAlex, Crossref) and left Semantic Scholar alone; 13 remaining nodes cancelled by frozen fail-run | yes, l.664. In source: `harness/tools/research_operator_registry_adapter.py:801-806` returns `None` |
| l.812-815 | `...-e8b71a14` | request had `attachments=[]`, so there was no hash-bound local source to fall back on. The frozen policy was `max_attempts=1 / on_exhausted=fail_run`; 13 downstream nodes cancelled | no; the log records diagnosis only |

Consequences:
- the "root cause" attached to l.814 belongs to the l.663 run and is fixed at `b0bf165f9`
- "a second provider" as the settle action is stale: the multi-provider fan-in exists once the mapping is
  fixed (l.663)
- the recurring cause is structural: a retryable `provider_environment_failure` meets a frozen
  1-attempt `fail_run` policy with no declared local-source fallback
- the deck repeats the conflation: `build_deck.py:529` "resolver dropped fallback providers"

### F2. Unattended claim is narrower than §2 suggests (MINOR, supports new 13)

Log l.815: the earlier "runs end to end without intervention" statement is withdrawn as too broad. The
online evidence covers only a run whose 6 PDFs were attached as request-scoped files. A prompt-only rerun
(0 attachments) ended at discovery (l.814). §2 says "Not yet routinely reproducible unattended", which
is consistent. The new item 13 cites l.815.

### F3. "Below the rule-based baseline" is an unmeasured comparison (MAJOR overclaim)

§6 Behind (l.692): "an English-only cue regex, below even the rule-based baseline CREDENCE measures".
Deck `build_deck.py:549`: "regex below the rule-based baseline". AI4Research's extraction recall is
unmeasured (§3.8 Limits, #3). CREDENCE's 0.811 is for spaCy sentence segmentation, a different method.
§3.8 says "cruder than that baseline", a design comparison, which is defensible. "Below" states a score
that was never measured. Replace with "cruder than" (see §4 and §5).

### F4. "1 repair per stage" is the default, not a fixed rule (MINOR)

#6 says every stage gets "1 bounded repair; a second defect fails the sprint". For intent,
`SOLAR_INTENT_MAX_REPAIRS` defaults to 1 and is capped at 4 (`intent_gateway.py:210-217`, per §3.1). The
new item 6 says "1 by default".

### F5. "The substrate caused the failures" overclaims (MINOR)

#12's evidence is 2 incidents: the 28-hour-stale coordinator and model-declared manifest statuses (§3.5).
F1 shows other run failures came from contract and adapter bugs, not the substrate. The new title is
"The substrate produced failures of its own".

### F6. #18 contains an unsourced prediction (MINOR)

"Months, not years, without an external result" has no source. Cut. The checked facts (Arbor's non-LLM
held-out gate §4.3, Rel(AI)Build's hashed spec §3.4, the survey's pre-committed specification §3.4) move
to 1 line under Behind.

### F7. #20 detail checked, 2 small precision notes (no change needed in the compressed text)

All checked at `b0bf165f9`:
- `intent_gateway.py:240-243`: Chinese action markers `改造`, `迁移`, `设计`, `优化`
- `:246-250`: `_NEGATION_CUE` is English only. The report's list is abbreviated; the source also has
  `do not`, `rather than` and contractions. No Chinese negation
- `:251`: `_HARD_CLAUSE_BREAK` `[.!?;:\n]|but|however|yet`. No `，。；`
- `:339`: `[a-z0-9_]+` word count
- `evidence/operators.py:1183` cue regex; `:1206` bound `30 <= len <= 1_000`; `:1224` testability
  `\d|%|compared|than`; `:1380-1390` method cues ("we used", ...)
- `action/delivery.py:995-1011` English method-name patterns; `:1648` CJK bigram loop
- `autosci_bridge.py:12875-12885` "report named/titled" title patterns
- `graph_node_dispatcher.py:2690` `DEEPRESEARCH_GATE_ARTIFACT_RE`

Paths in the report are short names. Full paths: `harness/plugins/autosci/operators/scientific_lifecycle/evidence/operators.py`,
`.../action/delivery.py`, `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/lib/intent_gateway.py`,
`harness/lib/graph_node_dispatcher.py`.

### F8. #19's approval claim not confirmed in a spot-check (OPEN)

"gated routes and every remote-agent capsule require approval" did not match in a grep of `harness/lib`,
`harness/tools` or the capsule YAML for remote-agent approval. `actor_runtime.py:296-307` gates only
`login`, `external_write`, `form_submit` and `account_action`. The claim is kept in the draft because it
is existing report text. Re-check its source before circulating.

### Checked and correct

- PlanCompiler constraint evasion: 13 of 22 failures, 59.1% (`2604.13092.txt:847`, Table 6, and `:1056`)
- TruthInsightBench control testing 11-16% (`2609.05079.txt:868`, p. 14)
- log l.814: `max_attempts=1 / on_exhausted=fail_run`, 13 downstream nodes cancelled
- `precise_source_span_resolved` unread, 20 of 43 rubric checks, 21 of 79 trust classes: consistent
  with §3.7, §3.8, §3.9 and HANDOFF §10b

### Builder constraints for the replacement

`build_reading.py:279-329` parses §6.1:
- group headers `X. Name` or `X. Name: note`
- table rows `| n | title | evidence | settle |`
- list items `- n title: detail`
- the prose form (`n Title...` plus `Recommendation (proposed):`)

The replacement uses table rows only, so the prose branch (`:291-316`) becomes unused, which is harmless.
Unnumbered bullets under a table are ignored by the register, so the language file:line list appears in
the report but not in the register. Group D must stay D (`:349`).

---

## 3. Drop-in replacement for §6.1

Paste from `### 6.1 Challenges` up to, not including, `### 6.2`.

```markdown
### 6.1 Challenges

A. Measurement and judgment

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 1 | No external measurement | every strength above is a design property read in source; 24 journey tests and 1 clean 14-node run are internal; 0 benchmark scores. Checking is weak across the field too: AI Scientist-v2's accepted paper carried ~57% train/test overlap, measured agents score 11-16% on TruthInsightBench control testing, experts judge verifiable claims correctly 60.8% of the time, so human review is not the fallback | TruthInsightBench end to end, dimension-level rates (§3.10) |
| 2 | Rubric verdicts look deterministic | 20 of 43 registered checks are model-judged rubrics; the result vocabulary does not separate them from the 23 Python gates (§3.7) | mark rubric verdicts as such in results and reports |

B. Claims

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 3 | Provenance, not truth | without an experiment the strongest verdict is `partially_supported` 0.85: a case-insensitive substring of the cited section, so a sentence planted in a paper passes; spans that fail re-hash are dropped silently and no gate reads `precise_source_span_resolved` (§3.8) | experiments beyond 1 family (§3.9); literature-only verdicts labelled as provenance; a gate that fails a claim whose span fails |
| 4 | Claim recall is unmeasured | cue-word regex, prefix-anchored, any digit counts as testable, every claim typed `result`, no decomposition; misses never reach `unsupported_claims`, so the list looks complete; the regex is cruder than CREDENCE's rule-only baseline, which reaches 0.811 F1 | hand-label 50 sections; a schema-bound model extractor behind the same span hash and gate (§6.2) |
| 5 | Text stages read English only | the typed fields between stages are language-neutral, so the English rules sit at 2 boundaries, reading the request and reading papers, while the repository's own operating documents are in Chinese | a schema-bound model extractor, tested alone on non-English papers (§6.2) |

Where the rules for #5 are English:

- intent: negation cues and clause breaks `.!?;:` `but|however|yet` are English (`intent_gateway.py:246-251`); Chinese action markers `改造`, `迁移`, `设计`, `优化` exist (`:240`), Chinese negation and `，。；` do not
- claims, testability, methods, report title: English patterns (`operators.py:1183`, `:1224`, `:1380-1390`; `delivery.py:995-1011`; `autosci_bridge.py:12875-12885`)
- length: a claim must be 30-1,000 characters (`operators.py:1206`); a character carries more text in Chinese, so the bound selects different sentences per language
- per-language patching has started: the relevance gate adds CJK bigrams by hand (`delivery.py:1648`)

C. Planning and the freeze

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 6 | Pre-freeze negotiation is bounded and advisory | intent, requirement, PlanIR and capsule selection get 1 repair by default, then the sprint fails; the fidelity objection is demoted after the budget and the requirement and capsule-fit reviewers are advisory from the start, so a meaning error a reviewer found can pass (§3.1-3.3) | measure the resubmission rate and how often a warning preceded a failed run; decide whether a human-approved second repair is acceptable |
| 7 | A frozen contract is only as good as its compilation | plan defects per run are unmeasured; an open capability (shell, SQL) routes around typed contracts, the cause of 13 of PlanCompiler's 22 failures (§3.4) | count plan defects per run |
| 8 | No undefined-branch policy | a frozen evaluator undefined on the outcome it receives has no defined behaviour (§3.4) | a policy (halt, inconclusive, human) declared in `test_policy` |
| 9 | A wrong plan has no recovery path | no re-planning: when execution shows the plan was wrong the run fails and the user resubmits; a node no capsule fits raises `UNSATISFIABLE_CAPSULE` and the plan fails at the freeze (§3.3, §3.4) | keep the freeze and document the cost against Arbor and Kosmos; the generalist capsule proposed in the capsule report |

D. Capsule library: trust classes, declared versus observed effects, versioning, gap records,
protected paths and the 2 type vocabularies are covered in the capsule report (§3).

E. Execution and autonomy

| # | Challenge | Evidence | What would settle it |
|---|---|---|---|
| 10 | The substrate produced failures of its own | tmux keystroke injection, file inboxes, SQLite; a coordinator ran code 28 hours older than the file on disk; a run manifest recorded model-declared statuses (§3.5) | the move to dsh (§5) |
| 11 | The CLI-agent path has generality and no trust | `codex exec` in a worktree; commands, files and network unobserved; evidence `fixture_or_adapter_only`; untrusted paper text reaches an agent holding shell, file and network access (§3.4, §3.6); 21 of 79 manifests declare a trust class | model-written runners under hash-and-approve on the native path; sandbox access logs |
| 12 | A provider failure ends the run | 3 logged runs stopped at literature discovery after Semantic Scholar HTTP 429, each from a different cause (no source inventory, an empty services mapping that dropped the multi-provider search, no attached sources); the first 2 are fixed. Each time the frozen failure policy ended the run; at l.814 `max_attempts=1 / on_exhausted=fail_run` cancelled 13 downstream nodes (log l.327, l.662, l.814) | a declared fallback to hash-bound local sources inside the frozen contract; coverage stated in delivery |
| 13 | Autonomy removes the humans the design needs | gated routes and every remote-agent capsule require approval, so an unattended run must defer any plan that needs one; the clean run finished without intervention only with 6 PDFs attached, and a prompt-only rerun ended at discovery (log l.815) | an unattended journey test from a prompt alone |
```

---

## 4. Replacements for the §6 head and §6.2

### §6 head (replaces l.679-693)

```markdown
## 6. Where this leaves AI4Research

Ahead:

- grading rules sealed in the run's integrity hash; recommended by the survey, implemented
  nowhere else reviewed
- literature verdicts refused for quotes not found in the retained source; only re-verified
  spans reach the report
- honest result vocabulary: not-tested and environment-blocked are not failure

Behind:

- experiment code on the trusted path: 1 hand-built family
- claim extraction: an English-only cue regex, cruder than the rule-based baseline CREDENCE
  measures, recall unmeasured
- external benchmarks: none

The lead is a design property, not a result: Rel(AI)Build already hashes its spec and Arbor runs a
non-LLM held-out gate (§3.4, §4.3). Thus the first external result decides whether it holds.
```

### §6.2 (replaces l.812-820)

```markdown
### 6.2 Directions (proposed)

- workflow onto dsh seams; contract layer stays the contribution; offer it to openJiuwen later
- a model writes experiment runners under hash-and-approve
- a schema-bound model extractor at both text boundaries (#4, #5): it reads the source language
  and emits typed fields (claim type, polarity, hedge level, requested and excluded outcomes,
  title), each with a verbatim source-language quote that code binds to offsets and hashes, as
  `_bind_exact_source_quotes` does for intent; no translated text becomes evidence
- the deterministic checks stay after the extractor: quote found, enum valid, the no-upgrade
  verdict gate, and a new gate that fails unverified spans (#3). Tested alone: precision, recall
  and unbound-quote rate per language against a hand-verified claim list, with the current regex
  on English papers and CREDENCE's 0.811 F1 as baselines
- an undefined-branch policy for the frozen contract (#8)
- a declared local-source fallback for retrieval nodes (#12)
- 1 external benchmark end to end before any comparative claim (#1)
```

Material cut from old #20 and where it went:
- "Why a model fits": cut. Its argument is carried by the §6.2 bullet
- extractor limits (run-to-run variation hashed per node, no tools for untrusted text, cost, local-model
  quality unmeasured, `DEEPRESEARCH_GATE_ARTIFACT_RE` at `graph_node_dispatcher.py:2690`): cut from the
  report. If the author wants 1 of them, the untrusted-text point belongs in §3.4 Trust model as
  "an extractor reading papers runs without tools"
- NFKC normalisation detail: cut (implementation detail)

---

## 5. Cross-reference changes

### REPORT.md

| Line | Old text | New text |
|---|---|---|
| 692 | `- claim extraction: an English-only cue regex, below even the rule-based baseline CREDENCE measures` | see §4 head replacement (`cruder than ... recall unmeasured`) |
| 703 | `hand-label 50 sections; a parser or schema-bound model extractor behind the same span hash and gate (#20)` | `hand-label 50 sections; a schema-bound model extractor behind the same span hash and gate (§6.2)` (now in new row 4) |
| 695-810 | whole §6.1 | §3 above |
| 816-818 | `... a model extractor also removes the English-only rules at intent and extraction (#20)` | §4 §6.2 replacement (`#4, #5`) |
| App. B 876 | `Gate on precise_source_span_resolved proposed` | unchanged (no number) |
| App. B | none | optional new row: `Does it read non-English papers? \| Not at the text boundaries: intent cues and claim, method and title patterns are English regex. A schema-bound model extractor is proposed \| 6.1, 6.2` |

App. B carries no challenge numbers, so no row breaks. §3 carries none either.

### build_deck.py

| Line | Old text | New text |
|---|---|---|
| 513 | `['No external measurement', 'every strength is a design property read in source', 'TruthInsightBench end to end'],` | `['No external measurement', 'every strength is a design property; checking is weak elsewhere too: 11-16% control testing, experts 60.8%', 'TruthInsightBench end to end'],` |
| 514 | `['Provenance is not truth', 'strongest literature-only verdict: the sentence exists in the cited section', ...]` | `['Provenance, not truth', 'strongest literature-only verdict: the sentence exists in the cited section; failed spans dropped silently', 'experiments beyond 1 family; a gate on failed spans'],` |
| 515 | `['Claim recall unmeasured', 'cue regex, no decomposition; misses never reach unsupported_claims', 'hand-label 50 sections; parser or model extractor behind the same gate'],` | `['Claim recall unmeasured, English only', 'cue regex, no decomposition, English patterns; misses never reach unsupported_claims', 'hand-label 50 sections; schema-bound model extractor with grounded quotes'],` |
| 516 | `['Rubric gates look deterministic', ...]` | `['Rubric verdicts look deterministic', '20 of 43 checks are model rubrics, unmarked in results', 'mark rubric verdicts as such'],` |
| 519-521 | `'TIME 1:45\n- Full table in report §6.1. No generalist fallback and the capsule-library challenges are left to the capsule talk.\n- Not on the slide: 1 repair per stage then fail (resubmission rate unmeasured); advisory reviewers cannot block; no re-planning; span hash recorded, not enforced.'` | `'TIME 1:45\n- Full table in report §6.1 (13 items). Capsule-library challenges are left to the capsule talk.\n- Not on the slide: pre-freeze repair bounded and reviewers advisory (#6); compilation quality unmeasured, 13 of PlanCompiler\'s 22 failures from constraint evasion (#7); no recovery path for a wrong plan (#9).'` |
| 524 | `s = slide('What is hard 2/2: execution and positioning')` | `s = slide('What is hard 2/2: execution and autonomy')` |
| 527 | `['The substrate caused the failures', ...]` | `['The substrate produced failures', 'tmux, file inboxes, SQLite; coordinator 28 h stale; model-declared manifest', 'the move to dsh'],` |
| 529 | `['Retrieval failure ends the run', 'Semantic Scholar 429 → fail_run cancelled 13 nodes; resolver dropped fallback providers', 'a second provider; coverage stated in delivery'],` | `['A provider failure ends the run', 'Semantic Scholar 429 in 3 runs; frozen 1-attempt fail_run cancelled 13 nodes', 'hash-bound local-source fallback; coverage stated in delivery'],` |
| 530 | `['Humans check badly too', 'experts 60.8% on verifiable claims; reviewers missed a 57% overlap', 'do not rely on human review as the fallback'],` | `['Unattended runs not yet shown', 'approvals defer plans; clean run needed 6 attached PDFs', 'an unattended journey test from a prompt alone'],` |
| 531 | `['The window is shrinking', 'Arbor runs a non-LLM held-out gate; Rel(AI)Build hashes its spec', 'an external result within months'],` | `['The lead is a design property', 'Arbor runs a non-LLM held-out gate; Rel(AI)Build hashes its spec', 'the first external result'],` |
| 533-536 | `'TIME 1:45\n- 21 of 79 manifests declare a trust class.\n- Autonomy: gated routes and every remote-agent capsule need approval, so an unattended run must defer any plan that needs one.\n- Capsule-library challenges ...'` | `'TIME 1:45\n- 21 of 79 manifests declare a trust class.\n- Humans are no fallback: experts 60.8% on verifiable claims; AI Scientist-v2 reviewers missed a 57% overlap.\n- Capsule-library challenges (versioning, gap records, protected paths) are in the capsule talk.'` |
| 549 | `'claim extraction: regex below the rule-based baseline',` | `'claim extraction: English-only regex, recall unmeasured',` |

Slide 18's CLI-path row (l.528) and undefined-branch row (l.517) need no change.

### Other files (notes, not deliverables)

- `DECK-PLAN.md:42` `6.1 A-B` → `6.1 A-C`; `:43` `6.1 C, E` → `6.1 E, 6`
- `build_reading.py:281` comment `# a prose challenge, e.g. "20 The stages that read..."`: stale but
  harmless. Rebuild the challenge register and republish after pasting (HANDOFF §10b)
- `HANDOFF.md` §10b/§10c: "27 challenges", "challenge 28", "#20" and "Now 28 challenges" become
  historical. Add a line: §6.1 reduced to 13 items (R2)
