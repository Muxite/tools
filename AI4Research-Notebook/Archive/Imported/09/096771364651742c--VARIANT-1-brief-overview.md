# AI4Research in Ten Minutes

*A brief overview for readers new to the system. Assumes you have built or used
LLM agents before; assumes nothing about this codebase.*

---

## 1. The one idea

Most agent systems work like this: give a language model a goal and some tools,
let it plan and act in a loop, and hope it stays on track.

AI4Research refuses that loop. Instead:

> **The language model interprets meaning. Deterministic code validates
> structure, freezes the plan, and runs it.**

The system compiles your request — the way a compiler compiles source code —
through several checked stages into a **frozen execution contract**. Only then
does anything run. After the freeze, no component may renegotiate what was
agreed, and the model is constrained — though not entirely prevented — from certifying its own work.

If you remember one thing: **there is a hard line in the middle of this system.
Before it, the system negotiates with a model. After it, the system executes a
contract.**

---

> **Status in one line, up front:** this is release-candidate software. It has
> completed a full research run end to end — once, with a mid-run fix — and is
> not yet reliably unattended. Details in §7.

## 2. What it is for

It runs on a developer's own machine (not a cloud service) and does two kinds
of work through one pipeline:

- **Software delivery** — write code, fix bugs, run tests, review changes.
- **Automated research** — find papers, read them, extract methods and claims,
  verify those claims, design and run experiments, write a report.

Research runs must produce **structured evidence files**, not a chat answer.
That constraint drives most of the design.

Names you will see used interchangeably: **AI4Research** (the repository),
**OpenSolar** (the packaging), **Solar** (the runtime and CLI). They are one
system. `openJiuwen-Solar` is a *branch name*, not a product.

---

## 3. One request, end to end

Say you ask: *"Do a systematic study of KV-cache efficiency for long-context
LLM inference."*

| # | Stage | What happens |
|---|---|---|
| 1 | **Intake** | Request arrives via web dashboard or CLI. |
| 2 | **Intent compilation** | A model answers *"what did they actually ask for?"* producing a typed record of goals, constraints, ambiguities, and unknowns. Crucially, **the model is not allowed to write the citation coordinates** pointing back at your text — code re-derives those itself. |
| 3 | **Requirement compilation** | A model answers *"what would satisfy this?"* Then a **second, independent model reviews it**. The reviewer can only find fault — it cannot rewrite the answer. The constraints from stage 2 are copied in and locked; the model may interpret beside them but never edit them. |
| 4 | **Planning** | A model decides *how* — which steps, in what order, using which capabilities. It may also decide the honest answer is a direct reply with no execution at all. |
| 5 | **THE FREEZE** | The plan is compiled into an immutable contract, hashed end to end. Included in that hash: **the rules that will be used to judge the run**, so a run cannot later soften its own passing criteria. |
| 6 | **Scheduling** | Deterministic from here. The contract becomes a DAG. Nodes run when dependencies clear. Nodes declaring overlapping file writes are never run concurrently. |
| 7 | **Dispatch** | Each ready node is handed to a worker under a time-limited lease, with a fingerprint check so a retry cannot accidentally re-run expensive work. |
| 8 | **Execution** | Capability units do the work — search literature, ingest papers, extract claims, verify them. Evaluators judge each result against the frozen rules. |
| 9 | **Delivery** | A report plan is produced, then a draft, then review, then delivery. |

Note stages 2–4: **the system can refuse.** A request that fails validation or
needs clarification stops there. That is a designed outcome, not an error.

---

## 4. Capability Capsules — the key abstraction

A **capsule** is a single YAML file describing one unit of capability. Think of
it as a function signature that also declares its side effects and who is
allowed to call it.

Each capsule declares:

- **When it applies** — and, unusually, when it must **not** be chosen.
- **Inputs and outputs**, with schemas.
- **Preconditions and postconditions**.
- **Invariants** — promises it must never break.
- **Effects** on six axes: read, write, execute, network, cost, and **risk**.
- **Composition** — what it is compatible and incompatible with.
- **Who may run it** — including an explicit **forbidden** list.

There are **80 registered capsules**. Registration is a gate, not an index:
five capsule files sit on disk *unregistered* and are therefore inert. Scanning
the directory and auto-activating what you find is forbidden.

Here is a real invariant, from the literature-discovery capsule:

> *"Missing protocol parameters remain explicitly unresolved rather than being
> silently invented."*

And another:

> *"Scientific reliability is not self-certified at discovery; downstream
> ingestion and claim verification decide evidentiary support."*

That is the stated design philosophy: **admit what you do not know, and do not
grade your own work.** The code mostly honours it — with real exceptions. When
the intent stage runs out of its repair budget, the harness *demotes* its own
independent reviewer's objections to advisory warnings
(`_demote_exhausted_fidelity_findings()`), and the requirement-stage review is
advisory by design. The principle is genuine; the enforcement has gaps.

---

## 5. How capabilities reach hardware

```
Capsule            what capability is needed
   ↓
Logical operator   an abstract role (45 of them), e.g. "needs architecture
                   reasoning at level 4"
   ↓
Physical operator  a concrete executor (102 of them)
```

Plans bind to *roles*, not to models. A routing table maps each role to an
ordered list of candidates with conditions — *always*, *if quota allows*, *if a
plugin is present*, *emergency only*. If the first choice is out of quota, the
next takes over without changing the plan.

Of 102 executors, **52 declare no model provider at all** — local workers rather
than hosted models. Two caveats: only 63 of the 102 are enabled, and only 18 of
the 52 carry the full vendor-neutral field set, so treat 52 as an upper bound on
vendor independence rather than a headline.

---

## 6. Three things worth noticing

**It refuses to treat an attempt as an outcome** — and it once enforced that
against itself. In September 2026 a run executed all 14 nodes, delivered all
eight requested files, and its closure flag recorded `all_nodes_passed=true`.
Then someone read the delivered files: the run's own manifest declared
`evidence_gate.status = failed_for_full_requested_scope`, and the poster said
"Evidence Gate: Not Passed". **The project retracted its own passing run**,
concluding it proved file delivery but not a genuine end-to-end pass, and
changed the gate so a self-declared failed manifest can never publish.

The same refusal appears at three other boundaries:
- A dispatch *receipt* is not proof of execution — only a result plus an
  evaluator verdict is.
- Contract verification **recomputes** each planning stage and compares hashes,
  rather than trusting the recorded "pass".
- Delivery distinguishes *finished* from *accepted*; acceptance needs an
  external evaluator verdict.

**Claims are hash-bound to their sources.** An extracted claim carries a
citation span tied to a **hash of the exact source text**. A fabricated
citation is therefore structurally detectable, not merely improbable.

**Its tests use negative controls.** The capability test layer checks not only
that the right capability is selected, but that *unrelated capabilities are
correctly not selected*. It also states its own limit honestly: it cannot prove
what a model "reasoned", only what the worker saw, what was called, and what
files resulted.

---

## 7. Where it actually stands

Being accurate here matters more than being impressive.

**It works, demonstrably, under supervision.** More than one run has finished
with every gate reporting passed. The project's own highest-level accepted
evidence is a 15-node run on 2026-09-03 — which required a mid-run hotfix and a
coordinator restart before it completed. Read that as "the happy path completes
when someone is watching," not "the system runs itself."

**It is not yet routinely reproducible unattended.** The pre-release test suite
stood at **606 passed, 34 failed, 8 skipped** — and the maintainers
deliberately kept those failures itemized rather than quietly making them pass.

**Some documentation describes a system that does not exist.** Two large design
documents describe a capsule marketplace with cryptographic signing, URI
addressing, and trust scores. None of that is implemented. There is also **no
formal verification** despite the vocabulary: "verification" here means schema
checks and written invariants, not machine-checked proofs.

Maturity is **release candidate**: suitable for local trial and controlled
experiments, not production.

---

## 8. The bug that explains the whole system

Late in development a run deadlocked. A node had passed its actual quality gate
— the work was done and independently marked PASS — yet the scheduler refused
to accept it, blocking every minute.

The cause: the scheduler was **re-inferring meaning at runtime from a
filename**. The file was called `final_report_plan.json`, a substring rule
matched `final_report`, and the scheduler concluded this must be a final
research report requiring an extra gate — a gate the frozen contract had never
required.

The maintainers' diagnosis names the boundary exactly:

> *"This is a conflict between the frozen contract and the Scheduler's post-hoc
> semantic inference — not a Planner output, model call, schema validation, or
> worker failure."*

And the fix was a principle, not a patch: **the scheduler may only run gates
already frozen into the plan; it must never re-derive meaning from runtime
filenames.**

That is the thesis meeting its own implementation. The most serious late bug was
a component deciding for itself what something meant after the contract was
sealed. Worth knowing: the same pattern — inferring behaviour from filename text
rather than reading the frozen declaration — still appears elsewhere in the
codebase, so this is a lesson learned rather than a problem closed.

---

## Where to go next

- **Longer overview** — mechanism-by-mechanism, written for external comparison.
- **Full report** — every stage with code citations, the complete challenge
  history, and anticipated questions.
- **Glossary** — every term above, defined.
