# 49 — Handoff: Capability Capsule after the final pass, 2026-09-22

Read this first for Capability Capsule. It replaces notes 47 and 48 and the old `HANDOFF.md` and `HANDOFF-SHORT.md`
(all deleted 2026-09-22; they remain in git history).

## Where everything is

| What | Where |
|---|---|
| Schema, **v1.6**, the source of truth | `capsule-openjiuwen/SCHEMA.md`; copy `tundle/ai4research/Capability Capsule Schema - Muk.md` |
| Deck, 28 core slides + 10 backups (no time limit, supervisor 2026-09-22) | `capsule-openjiuwen/deck/build_spec.py` → `deck.json` → `.pptx`; copy `Capability Capsule Workshop Deck - Muk.pptx` |
| Companion report, 27 pp including the appendix of paper figures | `capsule-openjiuwen/deck/companion.md` → `.docx`; copy `Capability Capsule Schema Companion - Muk.docx` |
| Every cited paper, read in full, with page-level numbers | `capsule-openjiuwen/verify/PAPER-LEDGER.md` |
| Final-pass log: inventory, review findings and verdicts | `capsule-openjiuwen/verify/V9-final-pass-20260922.md` |
| Asks, one page each | `capsule-openjiuwen/asks/` (RSI, verification, routing, Symphony and agent-core) |
| Build commands | `capsule-openjiuwen/INDEX.md` |

## What the design says now

| Topic | Position |
|---|---|
| Framing | a **schema first**: the contract every capability declares, for the tools the openJiuwen-based AI4Research system needs. Each tool answers a failure a paper measured (companion Table 3) |
| Safety | **declared, not observed**: checks run before any run uses a capsule and have a declared target. A capsule blocked by its own declared precondition could not have completed |
| Composability | spatiotemporal composability is part of the schema and the function: needs declared (space) and each effect's `undo` declared (time), after Cordis (2608.25512). Combinations are screened, not certified: the schema feeds a screener such as SkillFuzz and records findings in composition reports (B7) |
| Predicate parity | one declared precondition, evaluated by the filter and dispatch with one evaluator (invariant 8), and tested against the capsule's own exit logic at certification. See `PREDICATE-PARITY.md` |
| Tokens | a removed capsule is never offered, and its full catalog row shrinks to an exclusion line; the baseline is today's filter. Paper numbers: 59.1% and 90.5% (Don't Offer), 26,172 to 2,528 tokens a task (Contract2Tool). In AI4Research the binding prompt carries every eligible catalog row, on repair too, so it carries over. Measured in M2, not assumed |
| Integration | the capsule layer sits beside Symphony on agent-core: `CapabilityProvider`, `SkillGraphUpdater`, the binder, the tool-call rail, the trajectory store. All exist; each has a gap the capsule layer fills (Symphony's graph takes only skills, subagents and agents; the binder has no hash check; load records live in memory). Preconditions say `evaluable_at` planning or dispatch; only the first kind is filtered, after its parity test |
| Levels | provisional (loads, within effects, one postcondition) and certified (every output, blind tests, audited judge, parity) |

## Rules that saved or cost time in this pass

- **Verify every reviewer in the source.** A paper reader called More Skills' 0.49 and 0.28 unsupported. They are in its Fig. 1, as image text. Several other findings were right: the Blind Curator wording, CAC's unknown→defer, Contract2Tool's weakest field, RelAIBuild's after-the-fact detection.
- **Heredocs mangle `\n` inside Python strings here.** Write scripts with the Write tool and run them. Patch with `read_bytes` and `write_bytes`, asserting that each anchor matches once.
- **Figures:** `figures/figs.py` draws every diagram. `figures/extract_paper_figs.py` crops paper figures, with explicit overrides where the caption heuristic fails. Check every rendered page by eye.
- **Slide rules:** no em dashes, semicolons, contractions or first person. Titles ≤ 58 characters, strips ≤ 90. The paper title *Don't Offer What Can't Be Done* triggers false contraction errors in `tundlekit text lint`.

## Open

1. Length is not a constraint: the supervisor said to focus on quality, logic and flow (2026-09-22).
2. The questions for the room (companion Table 22). Each has a default.
3. Nothing is pushed. `capsule-openjiuwen` is committed on `supervisor-answers-20260918`.
