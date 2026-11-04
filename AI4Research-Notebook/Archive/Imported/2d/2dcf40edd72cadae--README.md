# report-general: the general AI4Research report

Started 2026-09-11. Separate from the capsule report (`../report-capsules/`); the two
do not merge (`../HANDOFF.md` §1).

**New session on this report: read `HANDOFF.md` (this folder) first.**

## Deliverables

| Stage | Format | Status |
|---|---|---|
| Working draft | `.md` (this folder) | **v0.3** (2026-09-13): cut to 37 papers, 2 worked examples, 5 figures, Q&A + glossary appendices, 2026 SoTA sweep folded in |
| Report | `.docx` | built: `../../general/AI4Research General Report - Muk.docx` via `build/build_report.py` |
| Deck | `.pptx` | built: `../../general/AI4Research General Presentation - Muk.pptx` via `build/build_deck.py`, 15 slides |
| Reading page | `.html` | `../../general/paper-summaries.html`, one card per cited paper, published as an artifact |

Voice: `../40-style-card.md`. Impersonal, no em dashes, lists carry enumeration,
claims flat with status in markers or a limitations list, never in the verb.

## Files

| File | What |
|---|---|
| `REPORT.md` | ⭐ the draft. §3 is the workflow (7 stages, each against SoTA), §4 SoTA table, §5 openJiuwen |
| `SOTA-SYSTEMS.md` | ⭐ evidence register: 43 papers, every figure with a page ref, plus a numbers-not-to-use table |
| `OPENJIUWEN.md` | what openJiuwen is, AI4Research's actual relationship to it, stage mapping, its own auto_research pipeline |
| `review/R1-adversarial.md` | adversarial review of v0.1: 41 findings; every fix applied in v0.2 |
| `../../papers/summaries/INDEX.md` | ⭐ 52 paper summaries, 1 per paper, grouped by report section |

## Findings this session that change earlier notes

1. ⚠ **jiuwenswarm is real.** `00-orientation.md`, `GLOSSARY.md` and
   `report/VARIANT-3-full-report.md` §1.4 say it "is not a thing". True inside the
   AI4Research tree only; it is openJiuwen's flagship repo. (`OPENJIUWEN.md` §0)
2. ⚠ **openJiuwen is a product name, not only a branch.** Package `openjiuwen-solar`,
   release "OpenJiuwen Solar v1.0.0-rc.9". **Zero** imports of openJiuwen code.
3. ⭐ **Claim extraction is a regex** (`operators.py:1183`) and **claim verification is a
   deterministic decision table** (`delivery.py:41-239`). Without an experiment the
   best verdict is `partially_supported / source_reported`: provenance, not truth.
   `[verified]` this session at `b0bf165f9`.
   ⚠ corrected after R1: the literature verdict comes from a case-insensitive substring
   match (`:133-139`); the SHA-256 span check (`:115-132`) only filters which spans are
   passed on, and no gate reads `precise_source_span_resolved`
4. ⭐ **1 native experiment family**: `causal_lm_kv_cache_quantization.v1`, runner
   hand-written (`kv_cache_experiment.py:27`).
   ⚠ corrected after R1: "no LLM writes experiment code" was wrong. The enabled adapter
   worker `autosci-exec-experiment-run-worker` delegates `$exp-run`/`$exp-design` to
   `codex exec` (trust class fixture_or_adapter_only)
5. ⭐ **openJiuwen has its own research pipeline** with host-validated per-round
   contracts (`agent-core/openjiuwen/rsi/artifact_rsi/paper_opt/auto_research`).
6. `08-workflow-end-to-end.md` "What to be careful claiming" §1 is still stale
   (STATUS-CORRECTED supersedes it). `VARIANT-3` is the corrected workflow source.

## Re-runnable checks

```
# zero openJiuwen imports in AI4Research (expect only branding hits)
rg -i "from openjiuwen|import openjiuwen|agent-core|jiuwenswarm" C:\Users\mukch\projects\work\AI4Research
# the claim regex
rg -n "cue = re.compile" C:\Users\mukch\projects\work\AI4Research\harness\plugins\autosci
# experiment families
rg -n "EXPERIMENT_FAMILY =" C:\Users\mukch\projects\work\AI4Research\harness
```

## Decisions (user, 2026-09-11)

- **Platform: the DeepSeek Harness for now**, "as that's more certain". The report's
  platform section must describe DSH; openJiuwen stays as context and the longer-term home
- **openJiuwen: add a layer**, i.e. contribute the contract layer rather than port the runtime
- **Adversarial review by subagent: approved** (this is the one authorised use)
- **Build tooling: python-docx / python-pptx** for now
- **Paper summaries: write a text summary of every paper** → `../../papers/summaries/`

## Next steps

1. User review of `REPORT.md` v0.2 voice and structure, then answers to Q-G3 to Q-G5
   (Q-G1 and Q-G2 decided)
2. ~~Adversarial review~~ done (R1, 41 findings, all applied); ~~paper summaries~~ done
   (52)
3. Figures: the workflow diagram, the freeze, the verification ladder with systems
   placed on it, the AI4Research vs auto_research contract-scope contrast
4. Build `.docx` and `.pptx` with python-docx / python-pptx. Before writing to OneDrive,
   check for running `WINWORD` / `POWERPNT` processes; `~$` lock files are unreliable
