# Topic register

Every topic the Capability Capsule design has covered, where it lives now, and what was dropped and why. Diff every
rewrite against this file; a topic leaves the design only with a row saying why and what would bring it back.
Created 2026-09-22 after an omission check found topics lost across rewrites. Sources: DESIGN.md at commit
`9507938` (deleted later), SCHEMA.md v1.6, `deck/companion.md`, and `alt/` when it lands.

**Status:** *live* = in the current documents; *thin* = mentioned but not explained; *lost* = present before, now
absent, not by decision; *dropped* = removed on purpose, with the reason.

## Function and framing (a)

| Topic | Status | Where now | Note |
|---|---|---|---|
| a scheme, not a tool (supervisor 2026-09-21) | live | SCHEMA layering; companion a | |
| schema first: what it is, where from, who follows, why | live | companion a | |
| declare, admit, make available, compose | live | companion Table 2 | |
| a real manifest, shown early | live | companion a, slide 4 | |
| declared versus observed safety | live | companion a | |
| each tool answers a measured failure | live | companion a | |
| spatiotemporal composability | live | SCHEMA section; companion a | lost from 2026-09-18 to 2026-09-22; Cordis was cited before it was read, then dropped without a re-entry note |
| a schema layer over units of more than one size (DESIGN §1.1) | thin | SCHEMA `capability_type` | not explained anywhere |
| three things a capsule carries (DESIGN §1.2) | lost | none | superseded by manifest plus records; check alt |
| the supervisor's eight components, mapped (DESIGN §1.4) | live | companion backup | |
| self-improvement loop: the slides', the first framing, now (DESIGN §1.4) | lost | none | background for RSI ownership |

## Architecture (b)

| Topic | Status | Where now | Note |
|---|---|---|---|
| invariants | live | SCHEMA; backup | |
| manifest fields, each with its reason | live | SCHEMA A1; backup | |
| records naming the hash (eight) | live | SCHEMA A2-B7; companion b | |
| two levels | live | SCHEMA A1; companion b | replaced three tiers on 2026-09-21 by decision |
| predicate parity | live | SCHEMA section; companion b | |
| imports enter as provisional | live | SCHEMA A6; companion b | |
| floating dependencies | live | SCHEMA A5; backup | |
| the three loops (build, admit, use) and who owns each (DESIGN §2.2) | lost | none | the clearest ownership picture; wanted for the g discussion |
| what changes as the body grows (DESIGN §2.4) | lost | none | composites by kind survive in SCHEMA only |
| hashes and how a capsule reaches a machine (DESIGN §2.3.1) | thin | SCHEMA `components` | |
| three holes stated up front (DESIGN §2.7) | thin | risks backup | |
| a worked example end to end | missing | none | never written |

## Position (c)

| Topic | Status | Where now | Note |
|---|---|---|---|
| where the schema is read in a run | live | companion c | |
| plan steps and dependencies, today and in the schema | live | companion c | |
| agent-core and Symphony hooks, with gaps | live | companion c; asks | |
| composites and the ceiling on them (DESIGN §3.2) | thin | SCHEMA A1 "not admissible in v1" | |
| capsules and openJiuwen skills: an overlap, not a subset (DESIGN §3.4) | lost | none | the first question Symphony and skillhub people will ask |
| pipeline stages as capsules: an extension, not the scope (DESIGN §3.5) | lost | none | |
| two planners, two filter points | live | companion c | |

## Dependencies (d)

| Topic | Status | Where now | Note |
|---|---|---|---|
| one agreed record per neighbour | live | companion d; deps figure | |
| the screening tool as a neighbour | live | companion d | |
| if a dependency is not there yet | live | companion d | |
| staying in its lane (DESIGN §4.4) | lost | none | what CC deliberately does not do for RSI, verification, routing |
| agent-core's five properties H1-H5 | live | SCHEMA terms; companion backup | definition moved into SCHEMA on 2026-09-22 (it had pointed at deleted DESIGN §4.1) |

## Similar designs (e)

| Topic | Status | Where now | Note |
|---|---|---|---|
| where each approach gets its reference for correct | live | companion e | |
| Symphony fingerprint versus manifest, field by field (DESIGN §5.4) | thin | one row in e; schemas backup | Muk wants this central |
| skills, skillhub, ScienceDiscovery compared | thin | e table; backup | |
| outside agents: where the idea lives (DESIGN §5.3) | lost | none | |

## Advantages, feasibility, questions (f, g)

| Topic | Status | Where now | Note |
|---|---|---|---|
| falsifiable advantages | live | companion f | |
| selection safety and tokens | live | companion f | |
| what is not claimed | live | companion f | |
| composition screening, B7 | live | SCHEMA; companion a, d, f | |
| parts built somewhere | live | companion g | |
| milestones | live | companion g | |
| ownership for discussion | live | companion g | trimmed on 2026-09-22 by decision |
| risks, four-arm test | live | backups | moved on 2026-09-22 by decision |
| questions for the room | live | companion | |

## Never covered (candidates)

| Topic | Why it may matter |
|---|---|
| admitted `description` as a prompt-injection path | models read it at selection |
| several runs using or changing the library at once | append-only and pinned runs cover it, but nothing says so |
| migrating a manifest between schema versions | `schema_version` exists with no migration rule |
| cost of certification per capsule | feasibility, when ownership is decided |

## Dropped on purpose

| Topic | When | Why | Would return if |
|---|---|---|---|
| three tiers | 2026-09-21 | two levels match the evidence's one line | evidence for a middle level |
| exposure, routing ranks capsules | 2026-09-21 | routing picks models only (supervisor) | the supervisor changes it |
| DeepSeek Harness as platform | 2026-09-18 | agent-core chosen | |
| papers not read in full | ongoing | evidence rule | the paper is read in full |

## Merged version (2026-09-22)

`merged/REPORT.md` and `merged/SCHEMA.md` v2.0 merge the companion (v1.6) and the independent version (`alt/`). Its
own register (§20) maps every topic. The topics marked *lost* or *thin* above now live there:

| Topic | Where in `merged/REPORT.md` |
|---|---|
| three loops and who owns each | §10.9 |
| capsules and skills: an overlap, not a subset | §9.7 |
| pipeline stages as capsules | §11.3 |
| composites and the ceiling | §11.1-11.2 |
| staying in its lane | §15 |
| Symphony fingerprint versus Declaration, field by field | §9.1 |
| skills, skillhub, ScienceDiscovery compared | §9.3-9.5 |
| a worked example end to end | §14 |
| the supervisor's components, with Ground Truth | §4.2 |

The four *never covered* topics are listed in the merged register as not yet covered.

## v2.2 (2026-09-22): self-improvement restored

The self-improvement loop, marked *lost* above, is live again in `merged/`. Its source is the 2026-09-15 capsule report
(§4, App. G).

| Topic | Where |
|---|---|
| goals, including self-improvement | REPORT §1-2; SCHEMA §1 |
| three clocks (hot, cold, audit), the sprint as the reuse boundary | REPORT §9.6; SCHEMA §4.0 |
| the generalist capsule and its run-contract flags | REPORT §9.7; SCHEMA §4.14, §3.4 |
| the cold path's four roles, the build budget | REPORT §9.6; SCHEMA §4.12 |
| monotone versions, four update options, retirement policy | REPORT §9.8; SCHEMA §4.7, §4.13 |
| protected components, what the system may change, unattended runs | REPORT §9.9; SCHEMA §4.1, §4.15-4.16 |
| today's capsules compared record by record | REPORT §3 |
| unpinned dependencies with a written purpose | REPORT §9.5; SCHEMA §4.11 |

**Rule added:** every derivation reads the earlier capsule reports as a named source (`merged/DERIVATION.md` stream
E), not only the papers, the code and the current session.
