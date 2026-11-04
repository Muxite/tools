# Knowledge base index

The report and deck are built from these files: `merged/build_report_v3.py` assembles `merged/REPORT.md` from
`report/` and `functions/`, and `merged/build_spec.py` writes the deck. Edit here, then rebuild. The schema itself is
`merged/SCHEMA.md`; the evidence ledgers are `../verify/PAPER-LEDGER.md` and `../alt/READ-LOG.md`.

## Map

| Folder | Holds | Report section |
|---|---|---|
| `materials/` | the assignment (a to g as Muk defines it), Muk's directives (a copy of tundle `obby/Directives.md`), the supervisor's rulings, the 2026-09-15 report, teammates | used throughout |
| `repos/` | the AI4Research workflow and where CC sits (file:line); agent-core and Symphony (what CC runs on); jiuwenswarm | §2c, §2d, §2e |
| `papers/` | one file per paper or pair, read in full: what it measured, pages, limits, which function it supports | cited from `functions/` |
| `functions/` | the foundation, then one file per verb: pick, verify, improve, remove; then plan and schedule. Each says what the schema provides and "we do X because of paper A" | §3 to §8 |
| `report/` | the front (what CC is; a to g), the worked example, today's capsules compared, limits, questions, the appendix | §1, §2, §9 to §12 |

## Which paper supports which function

| Function | Papers |
|---|---|
| Pick | Don't Offer What Can't Be Done; Contract2Tool; More Skills, Worse Agents?; GraSP and SkillDAG; SkillWeaver; Alita-G |
| Verify | Beyond Task Completion; SkillProbe; Cognitive Admission Control; The Blind Curator; Darwin Gödel Machine; CoEvoSkills; Agent Contracts and ABC |
| Improve | When Self-Evolution Backfires; AllocBench; Alita-G; SkillWeaver; Library Drift; Skill Drift Is Contract Violation |
| Remove | Cordis; SkillFuzz; SkillProbe (composition); Execution lineage and RelAIBuild |

## Topic register

Every topic the v2.3 report carried, and where it lives now. A topic may move; it may not disappear silently.

| Topic | Where now |
|---|---|
| What CC is; why the workflow needs it (declare, not observe) | §1; `report/00-front.md` |
| a to g answers | §2; `report/00-front.md` |
| The Declaration's fields, required and optional; how the capability is held (carriers, hashes) | §3; `functions/0-foundation.md` |
| Trust levels (exempt, provisional, certified) and per-claim assurance | §3, §5 |
| Selection: the four stages, the deterministic criteria, predicate parity, why it is cheap | §4; `functions/1-pick.md` |
| Verification: targets, hashes, declared versus observed effects, held-out checks, protected components | §5; `functions/2-verify.md` |
| Self-improvement: three clocks, the generalists (exempt), the capability tree, inherited suites, the cold path's four roles, monotone versions, four update options, lineage, who carries past performance | §6; `functions/3-improve.md` |
| Unpinned capability dependencies with a purpose (cost: stays provisional) | §3, §6 |
| Spatiotemporal composability; composites; composition screening; revocation reach | §7; `functions/4-remove.md` |
| A capsule holds no task; plan assembly and scheduling; ownership; real multiplicity (Bindings with roles, invocations, fan-out) | §8; `functions/5-plan-and-schedule.md` (v2.5) |
| Position in the workflow, with code | §2c; `repos/ai4research-workflow.md` |
| What CC depends on (systems, teams, models, materials) | §2d; `repos/agent-core-and-symphony.md` |
| Symphony fingerprint versus Declaration; other designs; papers | §2e |
| Advantages, each falsifiable | §2f |
| Parts already built; new work; first milestone | §2g |
| Worked example | §9 |
| Today's capsules compared record by record | §10 |
| What the schema does not claim | §11 |
| Questions for the room | §12 |
| The openJiuwen and AI4Research parts CC uses, what each does | Appendix A (`report/98-openjiuwen.md`) |
| Figures from the papers | Appendix B |
| Derivation of v2.1 and later from all evidence | `merged/DERIVATION.md` |

**Moved out of the report into `merged/SCHEMA.md` only** (kept, but not needed to answer a to g):

- `evaluable_at` detail and failure modes as records;
- import rules for ToolCard, MCP, skills, A2A and old manifests (the carrier table stays in §3);
- concurrency and migration rules;
- hooks and their gaps in agent-core, H1 to H5 (summarised in `repos/agent-core-and-symphony.md`).

**Cut from the report as not crucial to a to g** (Muk, 2026-09-22: no filler):

- the tool catalogue and the paper-by-paper motivation (replaced by per-function rationale);
- the three ownership loops, and "what CC deliberately does not do";
- which workflow stages could or must not be capsules;
- the four-arm test and cost estimates (milestones stay as a backup slide).

**Considered and left out of the schema** (unchanged from v2.3): the slide's formal layer (SysML v2 chain), the five
unglossed capsule kinds, signing and key management, a numeric trust score (compensatory scores bypass hard
conditions), admission cost (no paper measures it for this design), and papers in `papers/` not read in full.

**Not yet covered:** the cost of certification per capsule (jiuwenswarm's RSI `Usage` record is the pattern).
