# What reading openJiuwen's documents found that searching it did not

Written 2026-09-18 from four agents reading documentation rather than grepping it, plus my own verification of
the load-bearing claims. Reports in `docs-read/D1`–`D4`.

The brief opened with my own mistake — a grep for "admission" and "precondition" over `symphony/` returning
nothing, taken as evidence that no gate existed, while a 2,734-line gate sat in the same directory under
different words. Reading found three more instances of the same pattern, and one of them changes the design.

---

## 1. `ActionSpec` in jiuwensymbiosis is the closest prior art to a capsule manifest, anywhere

Verified in source myself (`jiuwensymbiosis/api/decorators.py:68`, `api/actions.py:648-690`, HEAD `6798f6ed`).

One frozen dataclass declares everything a capability promises:

| Field | What it is |
|---|---|
| `name`, `description` | the action name a plan writes, and **the only text a planner sees** |
| `capability` | the capability gate; `None` means every body has it |
| `params`, `required_params`, `param_schema` | parameters, with per-parameter **JSON Schema** |
| `result` | a `TypedDict` describing result fields, so a later step can read `<bind>.field` and **the validator can reject a field that does not exist** |
| **`requires` / `provides` / `invalidates`** | self-state, **over a closed vocabulary** in `api/state.py` |
| `produces_location` / `consumes_location` / `invalidates_locations` | location freshness |
| `opens_access` / `closes_access` | barriers this action clears or restores |
| `tags` | rail triggers |
| `planner_visible` | whether it enters the planner's vocabulary at all |

Three of its design rules are ones I had been proposing as novel:

> "Body-agnostic, and **the ONLY place these fields are declared** — `ToolMeta` holds a spec rather than copying
> it, so **what a planner reads cannot drift from what the vocabulary promises**."

> "This is the **ONLY text a planner sees**, so it must stay true on every body: an implementation has **no
> channel for adding prose of its own**."

And it is **enforced, not documented**: `ContractViolation(TypeError)` is raised **at import time** when an
implementation's signature cannot satisfy its spec (`api/actions.py:687`, with a unit test at
`tests/unit_tests/api/test_actions.py:148`). Visibility is gated by a capability-set intersection —
`Api.capabilities ∩ Env.effective_capabilities` — so a tool a body cannot support never reaches the planner.

⚠ **The second quote is the shadowing defence, stated as a design rule.** An implementation cannot add prose,
so descriptions cannot drift into distractors. That is a cheaper answer to the 21% shadowing loss than anything
I had proposed, and it costs nothing.

### And the sharpest insight of the day, which is theirs, not mine

**Their preconditions are checkable because the state vocabulary is closed.** `requires` / `provides` /
`invalidates` range over a fixed set in `api/state.py`. Symphony's `applicability` is prose and therefore
uncheckable; jiuwensymbiosis's is a closed enum and therefore mechanical.

That reframes the capsule's hardest open problem. It is not "how do we write preconditions" — it is
**"can a research pipeline close its state vocabulary?"** Robotics can: a gripper is holding something or it is
not. Research is harder: what is the closed vocabulary for "the literature has been surveyed"? If we cannot
close it, our preconditions degrade toward prose and inherit Symphony's problem.

**This should be a design section, and possibly the first question I ask at the workshop after S1.**

### What it does not do, so the capsule still has a job

No versioning or lineage of an `ActionSpec`. No admission — a spec is authored by a person and enforced against
its implementation, never judged as worth keeping. Scope is one robot body's action vocabulary, not a growing
library. And the closed vocabulary is domain-specific and hand-maintained.

---

## 2. A correction: sciencediscovery did not "remove agent-core"

⚠ **My earlier claim was wrong, and it was wrong because of an ambiguous phrase I resolved in my own favour.**

What the repository actually says: there is **zero literal occurrence of "agent-core"** in the current tree, and
the only mention in git history is a PR description recording a deliberate decision **not to adopt it** —
*"不引入 openJiuwen agent-core、DeerFlow Python 进程或新的跨进程协议"* ("do not introduce openJiuwen agent-core,
the DeerFlow Python process, or a new cross-process protocol").

What they *removed* was a different thing: a Python gateway running LangChain's `create_agent` plus a
`deer-flow` dependency, replaced by a self-built TypeScript agent loop with "no LangChain or LangGraph". The
phrase I read as meaning agent-core — "the vendor harness dependency and the submodule it came from" — referred
to that.

So the accurate statement is **"declined to adopt it", not "had it and deleted it"**. Arguably stronger
evidence, and I should have checked rather than resolved an ambiguity toward the more dramatic reading. Note 11
and the vault are corrected.

## 3. sciencediscovery has a skill-library admission pipeline — in Chinese-only design docs

Reported by D3, not independently verified by me. Its shape:

```
propose → dry-run-only validation (diff · diagnostics · conflicts)
        → human permission-gated publish → versioned head pointer → rollback
```

Staged as an MVP through M1.6, with M2 and M3 explicitly roadmap-only. It exists **only in Chinese internal
design documents with no English counterpart**, and `CONTRIBUTING.md` states that **Chinese docs are
authoritative for architecture**.

⚠ Two things follow. First, this is the closest thing to a working capsule admission gate found in the survey,
and an English-only reader would never find it. Second, **any future review of openJiuwen must read the Chinese
documents**, because the authoritative architecture is not in English.

## 4. `rsi/` is a real research pipeline with no documentation at all

D1's most useful find. `openjiuwen/rsi/` has **no README, no AGENTS.md, no entry in the root module map, and
zero mentions anywhere in `docs/en` or `docs/zh`** — yet `rsi/artifact_rsi/paper_opt/auto_research/` implements
a structured research-agent pipeline:

> topic survey → experiment design → code implementation → experiment execution → reflection → paper scoring →
> reporting

That is AI4Research's own workflow, already built, inside the platform we are told to build on, and invisible to
anyone reading the docs. It matters for requirement 2 of the brief and for Saurav's RSI seam, and neither of us
would have found it from documentation.

## 5. Two more vocabulary traps, both flagged by the repos themselves

- **`agent_evolving/AGENTS.md` warns that "evolution" means three different, non-interoperable things** across
  its own subpackages. Their maintainers hit the same trap and wrote a warning.
- **`symphony/flow/` appears nowhere in symphony's status table or its "final directory blueprint"** — which is
  precisely why I missed it. The subsystem is not merely undocumented; it is absent from the document that
  purports to list the subsystems.

## 6. Status-table staleness is worse than one row

D1 checked by reading `__init__.py` files and directory listings rather than trusting the README. Beyond the
retrieval row I already knew about, **"Agent Toolkit" is also marked pending** while a retrieval-scoped agent
toolkit already exists and is exported.

**Treat symphony's implementation-status table as unreliable in both directions** — it under-reports what
exists and omits `flow/` entirely.

## 7. The substrate we plan to depend on has no design documentation

`core/graph/`, `core/session/` and `core/workflow/` have **no design documents at all** — only auto-generated
API reference. Checkpointing, resume and parallelism are documented at usage level, never at the
substrate or scheduling level.

Combined with `symphony` being the least-commented subsystem in the repo (0.69% inline comments), and a
four-month turnover on two of our four models: **whatever we learn about this platform has to be written down as
we learn it.** That is what the vault is for, and it is now a project requirement rather than a habit.

## 8. One documentation bug worth reporting upstream

jiuwenswarm's Swarm Skill docs are internally inconsistent about a **validator-checked** field: frontmatter says
`kind: swarm-skill`, one section says `--type teamskills`, another says `--type swarmskills`. Following the
documentation literally can fail validation. Small, but it is the kind of thing that costs a newcomer an hour
and is free to fix.

---

## 9. A4P does not do audit, which corrects something I wrote

⚠ I recorded that A4P gives us "authority **and** audit trail — two things a capsule admission record would
otherwise have to invent". **The second half is false.**

The word "audit" appears **zero times in `A4P_PROTOCOL.md`**, the actual specification, and five times in the
whole A4P directory — every occurrence deferring audit to an external, unbuilt deployment-layer system. A4P
does produce a real signed evidence artifact, an Ed25519-signed Mandate/Intent Token over canonical JSON, but it
is **consumed on successful completion rather than archived**. No persisted audit-trail schema exists.

So **the capsule layer does have to own its admission record**, and the prod-eligibility constraint "admission
records must be auditable by someone else" has no platform support to lean on. That makes the admission
certificate more important, not less.

Also: **A4P and the A2X registry do not reference each other at all** — different credential models (signed
mandates versus plain bearer API keys), no cross-reference, and neither has any English documentation despite
the root `agent-protocol` README being a clean EN/ZH pair.

## 10. skillhub has the most complete admission gate in the organisation, and a bypass

The fourth instance of the pattern, and the most operationally interesting.

Documented flow: **publish → optional AI/rule review → moderation (`PENDING` / `APPROVED` / `REJECTED`) →
market display.** Behind the vague Chinese prose for "审查" (review) sits a checklist of **30+ named checks** —
prompt injection, secrets exposure, destructive operations, path traversal, typosquatting and impersonation —
which exists **only in source** (`marketplace/skill_review/domain/check_catalog.py`) and in no prose document
anywhere.

⚠ And there is a real bypass: **requests carrying a valid `X-System-Token` are auto-`APPROVED`**, skipping
review and moderation entirely. Agent-asset admission (plugins, connectors) is a deliberately weaker second tier
that skips content validation.

That is worth saying carefully at the workshop. It is not a criticism of skillhub — every gate needs a
privileged path — but it is a concrete example of the thing the capsule design is about: **a gate whose
threshold is real, undocumented, and bypassable is a gate whose guarantees nobody can state.**

## 11. Nobody verifies composition references at admission time

Checked across the whole platform scope: **no repository verifies, at admission, that a composite's declared
parts exist.** skillhub will admit an "agent-group" asset without checking that its declared members are real.

That is empirical confirmation of the compositional hole in DESIGN.md §2.7, from the other direction: it is not
merely that safety may not compose — **nobody currently checks even the cheapest compositional property**,
which is referential integrity.

One correction from the same finding: a SwarmSkill composes multiple agent *roles within one package*, not
other published Skills by reference. So skillhub's unit is self-contained, which is why the question has not
bitten them yet.

## 12. Two more things worth taking, and one claim to stop repeating

**Take:** `agent-memory`'s `MemUpdateChecker` classifies a candidate memory as **redundant / conflicting /
coexisting** before writing — an admission gate under yet another vocabulary. Its consolidation step requires
**at least two independent pieces of evidence** and states the rule plainly: *"宁可不归纳，也不要编造"* — better
not to generalise than to fabricate. That is a good evidence threshold and a better slogan than anything in my
draft.

**Take:** `agent-studio` represents a built agent as a **typed bundle** of `{nodes, tools, workflows,
mcp_servers, skills, knowledge_repos}`, with workflow Start/End nodes declaring typed inputs and structured
JSON output. Whether that artifact is portable outside agent-studio is undocumented — a silence, not a denial.

**Stop repeating:** `agent-runtime`'s "multi-tenant resource isolation" is thin. It is documented as
**request-level tenant-ID injection**, not verified sandboxing, and the default `subprocess` deployment mode has
no described isolation mechanism at all. I used their multi-tenancy as the justification for a prod-eligibility
constraint; the constraint still stands on its own merits, but **not on the claim that they have solved it**.

⚠ Also note `agent-memory` has **no content-level versioning** — edits overwrite in place. Its Graph Memory has
the best provenance in the platform (per-write source episodes) and is **explicitly not wired into the default
write path**.

---

## What this changes

| | Change |
|---|---|
| **§5.1 prior art** | rewrite around `ActionSpec` — it is closer than `skill-creator-normal` or Symphony's `flow/` |
| **§2.3 manifest** | adopt `requires`/`provides`/`invalidates` over a closed vocabulary, typed `result`, and `planner_visible` |
| **§2.5 selection** | adopt "the implementation has no channel for adding prose" as a rule — it is the cheapest shadowing defence available |
| **new open question** | **can a research pipeline close its state vocabulary?** If not, preconditions degrade to prose |
| **note 11 / vault** | correct the sciencediscovery claim |
| **method** | Chinese docs are authoritative for architecture. Any future survey reads them first |
| **§4.1 dependencies** | A4P gives authorization, **not** audit — the capsule owns its admission record |
| **§2.7 holes** | referential integrity of composites is unchecked platform-wide, not just unsafe |
| **prod-eligibility** | stop citing openJiuwen's multi-tenancy as solved; it is tenant-ID injection |
