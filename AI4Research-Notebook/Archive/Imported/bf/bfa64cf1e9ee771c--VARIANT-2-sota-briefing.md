# AI4Research — System Briefing for State-of-the-Art Positioning

**Purpose of this document.** It describes one system's architecture in
neutral, vendor-agnostic terms so that an external researcher with web access
can position it against published literature and competing frameworks. It is
self-contained: you do not need access to the codebase.

**What is wanted back:** for each mechanism in §4, whether it is standard
practice, an uncommon-but-known technique, or genuinely unusual; who else does
it; and what the relevant published work is. Then answers to the questions in
§6. **Please evaluate, do not confirm.** Where a mechanism is ordinary, say so
plainly — that is more useful than agreement.

**Provenance.** Everything in §§1–3 and §5 was verified by direct code
inspection at commit `b0bf165f9`. Analogues suggested in §4 are the briefer's
own guesses offered for checking, not claims from the project.

---

## 1. What the system is

A **local-first multi-agent execution framework** that runs on a developer
workstation. It takes a natural-language goal, compiles it through several
validation stages into a typed execution plan, freezes that plan as an
immutable hash-verified contract, and then executes it as a DAG across
interchangeable back-ends (hosted LLM APIs, CLI coding agents, headless
browsers, and deterministic local Python workers).

It serves two workloads through one control plane:

1. **Software delivery** — implement, debug, test, review code.
2. **Automated scientific research** — literature discovery → paper ingestion →
   method and claim extraction → claim verification → experiment design and
   execution → report planning → report writing.

Research runs are required to emit **structured, schema-validated evidence
artifacts**, not prose answers.

It is explicitly not a hosted service, not multi-tenant, and not a production
control plane. Self-described maturity: release candidate.

### The stated design thesis

> Language models interpret semantics. Deterministic code validates structure,
> maintains references, freezes contracts, and schedules.

Nearly every mechanism below is an instance of that split, and the most useful
comparative question is whether that split is what distinguishes this system
from mainstream agent frameworks, or whether it is now common.

---

## 2. Verified scale

| Quantity | Value |
|---|---|
| Registered capability units ("capsules") | 80 (77 capability, 1 guard, 2 resource) |
| Abstract operator roles ("logical operators") | 45 |
| Concrete executors ("physical operators") | 102 |
| — of which vendor-neutral local workers | 52 |
| — of which model/CLI-backed | 50 (OpenAI 15, Anthropic 11, Google 7, local 5, browser 5, GLM 4, DeepSeek 3) |
| Declared artifact types | 76 |
| Research evidence schemas | 33 |
| Capability dimensions, graded 1–5 | 15 |
| Pipeline stages, intake → delivery | 9 |
| Acceptance ("journey") tests defined | 25 |
| Feature inventory | 142 level-2 features; 1,502 reviewed atomic rows |
| Tracked files | 5,386 |

Languages: Python (control plane), TypeScript/Bun (runtime services), Bash
(orchestration), React (dashboard), Electron (desktop).

---

## 3. The execution pipeline

```
user request
  → intent compilation        (LLM writes meaning; code validates structure)
  → requirement compilation   (LLM writes; a second independent model reviews)
  → planning                  (LLM decides; code validates, binds, and freezes)
  → FREEZE                    (immutable, hash-verified execution contract)
  → scheduling                (deterministic DAG execution)
  → dispatch                  (leased, scoped, idempotent worker invocation)
  → operators and gates       (capability units execute; evaluators judge)
  → delivery                  (plan → draft → review → deliver)
```

Three properties of this pipeline are the substance of the comparison:

**(a) It can refuse.** Intent compilation that fails validation or needs
clarification halts the pipeline; the planner may also answer directly with no
execution graph at all. Refusal and direct answering are first-class outcomes,
not error paths.

**(b) Everything before the freeze is negotiation; everything after is
contract execution.** Repair loops with bounded budgets (a 3-call ceiling at
the requirement stage; a repair cap of 0–4, default 1, at the planning stage)
operate before the freeze. After it, no component may renegotiate.

**(c) Three mechanisms constrain the model from authoring the inputs to its own
verification.** Whether this closes every path is a fair question — the fidelity
reviewer is itself a model, and the requirement-stage review is advisory rather
than blocking. The three verified mechanisms are:
- The intent stage rejects model-authored source coordinates; deterministic
  code re-derives text spans itself.
- The requirement stage deep-copies the prior stage's constraint structure and
  guards it with an equality check, so a model may add interpretation beside
  constraints but can never edit them.
- The plan's declared side-effect union, its verification duties, and its list
  of goals it could not satisfy are all computed deterministically from static
  manifests — not emitted by the planner.

---

## 4. Mechanism catalogue

Thirteen mechanisms, described as neutrally as I can manage. For each, the
question is: **is this standard practice, uncommon, or unusual — and who else
does it?**

The suggested analogues are my own guesses, listed *after* each description. If
they anchor you toward a flattering comparison, discard them and search
independently — I would rather you find a closer analogue I missed.

**M1 — Multi-stage compilation of natural language into a typed IR before any
execution graph exists.** Rather than an LLM planning step-by-step at runtime,
the request passes through successive compiler stages, each emitting a
schema-validated intermediate representation. Execution begins only after the
final IR is accepted.
*Suggested analogue to check: compiler front-ends (parse → semantic analysis →
codegen); older task-oriented dialogue pipelines (intent classification → slot
filling → structured query).*

**M2 — Structural validation performed by code that did not generate the
content.** Model output fills designated "meaning" fields; separate
deterministic validators enforce types, references, and invariants. The two are
different code paths by construction.
*Analogue: parser/AST versus type-checker; schema validation layered over
function-calling output.*

**M3 — Independent review artifacts, produced by a different actor than the
generator.** Each stage emits not just its product but separate validation,
fidelity, and acceptance artifacts. The fidelity reviewer is a distinct model
call that **cannot rewrite the artifact** — it may only find fault. Acceptance
is a deterministic gate, and it is checked twice by two different modules
before the next stage may run.
*Analogue: CI "verify" stage separate from "build"; actor-critic separation,
though here the critic is a separate call or rule set, not co-trained.*

**M4 — Immutable, hash-verified execution contract between planning and
execution ("the freeze").** Canonical-JSON SHA-256 digests chain every planning artifact into one frozen
contract. Verification recomputes each stage from its inputs and compares
hashes rather than reading a recorded verdict. The evaluation policy that will
judge the run is included in that hash. The intended effect is that a stale or
altered contract fails verification; whether this is meaningfully stronger than
conventional checksumming, and what it costs when a plan must change mid-run,
are open questions.
*Analogue: package-manager lockfiles; content-addressed build graphs (Bazel
action graphs, Nix derivations).*

**M5 — Capability units declaring effects, pre/postconditions, invariants, and
a trust class.** Each unit is a manifest declaring: applicability signals
(including **negative** signals — when it must *not* be chosen); typed inputs
and outputs; preconditions and postconditions; prose invariants; a six-axis
effect block (`read`, `write`, `execute`, `network`, `cost`, **`risk`**);
composition edges (`compatible_with`, `incompatible_with`, `requires_after`);
required guard and resource units; verification conditions; and which executors
are **preferred** or **forbidden**. A registry gates admission: a manifest
present on disk but unregistered is inert, and directory scanning to
auto-activate is forbidden.
*Analogue: object-capability security; effect systems in PL theory applied to
tool invocation rather than syscalls.*
**Important caveat for assessment:** I have verified that these fields are
*declared*. I have **not** verified that every declared field is *enforced* at
dispatch time — `risk` in particular may be descriptive metadata with no
enforcement path. Treat enforcement as unverified.

**M6 — Trust classes constraining which unit may satisfy which goal.** Units
are classed as performing measured execution, transforming existing evidence,
or being fixture/adapter only. A goal requiring measured evidence cannot be
satisfied by a unit that merely reshapes evidence. The intent is to prevent an
agent claiming it ran an experiment it did not run. This depends on unit
authors classifying honestly, and I found the enforcement differing between two
call sites in ways I could not fully resolve.
*Analogue: provenance/lineage typing; integrity levels in mandatory access
control.*

**M7 — Abstract-role to concrete-executor indirection with graded capability
requirements and conditional failover.** Plans bind abstract roles (with graded
requirements such as `architecture_reasoning: 4`) rather than concrete models.
A routing table maps each role to an ordered candidate list (average 2.75 candidates) with conditions — always available, quota permitting, plugin
present, or emergency only.
*Analogue: service-mesh logical-name-to-endpoint resolution; database logical
versus physical query plans.*

**M8 — Filesystem-queue IPC for language-agnostic dispatch.** Workers are
invoked by writing JSON request files to a directory and reading result files
back, guarded by file locks and atomic rename — not by RPC. Any process that
can read and write files can be an operator.
*Analogue: maildir/spool queues; filesystem-backed job queues.*

**M9 — Leases and scoped tokens bounding worker authority.** Dispatched work is
claimed under a time-bounded lease with stale/dead reclaim, so a crashed worker
releases its claim. A separate token type describes file/shell/network/git
allow and deny scopes. *Verified caveat: the token's path-checking method has
no production callers; actual filesystem confinement is enforced by the worker
daemon's allowed-output-roots and staged-publish mechanism. Treat the token
layer as partially wired.*
*Analogue: short-lived cloud IAM session tokens; distributed-lock leases.*

**M10 — Idempotency fingerprinting with deduplication and cooldown.** Before
dispatch, a canonical hash of the request is checked against a dedup ledger and
a per-unit cooldown file, so a scheduler retry cannot re-run an expensive
operation.
*Analogue: idempotency keys in payment APIs; at-least-once consumers
deduplicating on message ID.*

**M11 — DAG scheduling with declared write-scope conflict avoidance and human
gates.** Nodes declare the paths they will write; prefix-overlap detection
prevents co-scheduling conflicting nodes, and an undeclared scope is treated as
exclusive (fail-safe). Readiness is topological; cycles are rejected. Nodes may
block for human approval, and a graph-level policy decides whether dependents
proceed meanwhile.
*Analogue: build-system output-ownership conflict detection; optimistic
concurrency keyed on declared write-sets; CI manual-approval gates.*

**M12 — Evidence-first research pipeline with anti-fabrication invariants.**
Extracted claims carry a citation span bound to a hash of the exact source
text. The intent is to make fabricated citations detectable; I have not
verified how comprehensively this is checked downstream. Verdicts are drawn
from a closed set, and an outcome with no collected results must map to
*inconclusive* — never to *supported*. Discovery units are forbidden from
falling back to fixtures or synthetic candidates, must record a study protocol
(search strategy, selection criteria, time range, inclusion/exclusion), and
must leave unresolved protocol fields **explicitly unresolved rather than
invented**. Discovery is also barred from self-certifying reliability; that is
decided downstream.
*Analogue: FEVER-style claim verification with SUPPORTS/REFUTES/NOT-ENOUGH-INFO;
test frameworks defaulting to inconclusive rather than false pass.*

**M13 — "Activation proof" with negative controls.** A test layer distinguishes
a capability that is *installed* from one that is *actually exercised with
observable effect*, using an append-only event ledger and coverage telemetry.
It includes **negative controls** — confirming that unrelated capabilities are
correctly *not* selected. It explicitly disclaims any ability to prove a
model's private reasoning, asserting only what was visible to the worker, what
was called, and what artifacts resulted.
*Analogue: mutation testing; negative controls in experiment design;
feature-flag exposure logging.*

---

## 5. Honest status, and what is design rather than implementation

An external assessment should not credit the system with more than it has.

**Demonstrated.** A complete 15-node end-to-end research run passed on
2026-09-03 with all required gates passed and closure confirmed. That run
required a mid-run fix and a coordinator reload before completing.

**A caution about pass counts.** Other runs have also recorded
`all_nodes_passed=true`, but at least one was **retracted by the project itself**
after inspection found the delivered manifest declaring its own evidence gate
failed. Treat closure flags in this system as unreliable without content
acceptance — the maintainers do.

**Not demonstrated.** Routine unattended reproducibility. The pre-release
regression suite stood at 606 passed / 34 failed / 8 skipped, with failures
deliberately retained and itemized rather than suppressed.

**Design-only — do not treat as implemented.** Two large design documents
describe a capsule *ecosystem*: URI-addressed capsules, a JSON-RPC invocation
protocol, a federated multi-vendor marketplace, cryptographic signing, and a
numeric trust score. **None of these appear in the code.** The documents also
use terms like "symbolic verification" and "termination analysis" with no
accompanying method. There is **no formal-verification formalism** in this
system: "verification" means schema validation plus string-expression pre/post-
conditions and prose invariants, not machine-checked proof. Any positioning
against formal-methods literature should be on those terms.

**Partially wired.** The capability-token path scoping (M9). A distributed
peer-to-peer layer exists with service discovery, coordinator election, and a
task-bidding protocol, but its task-assignment callback does not dispatch
anything — it is a decision layer with **no executor connected**. Remote
execution in practice uses a separate, conventional SSH/rsync push mechanism.

**A named, present-tense competitor it does not currently beat.** The project
tracks a real upstream research-agent project called **AutoSci** across 28 native skills, with dedicated parity tooling that expects AutoSci checked
out as a sibling repository. Its own most recent parity audit reports the
migrated runtime as **not at full parity**, with a final runtime verdict of
`failed`: zero stages at native-full runtime, five partial, four gated and
unexecuted, one fixture-only, five schema-only, four failed, four missing. The
project deliberately refuses to mark any capability `full` until non-fixture
runtime evidence justifies it.

This is the most falsifiable comparison available and should weigh heavily in
any assessment. **A head-to-head with AutoSci is more informative than a
comparison against general-purpose agent frameworks.**

**Declared does not mean enforced.** I verified that capability manifests
*declare* effects, risk, preconditions, and trust classes. I did **not** verify
that each declared field is *enforced* at runtime. At least one adjacent
control — a token type describing file/shell/network scopes — turned out to have
no production callers at all. Assume any manifest field may be descriptive
unless stated otherwise, and treat questions about enforcement as open.

**Self-claims, unverified.** The project contains a document scoring itself
against Copilot, Cursor, Windsurf, Claude Code, Devin, Aider, Cline, AutoGPT,
LangGraph/LangChain, CrewAI, and ChatGPT Agent across 12 dimensions. It scores itself 58/60, placing LangGraph at 31/60. It is self-authored and
not independently validated. It should be treated as a
statement of intent, not evidence. Notably it concedes weaker model flexibility
and macOS lock-in.

---

## 6. Research questions

**Please treat question 1 as the primary one.** The rest are subordinate to it.

### The null hypothesis — address this first

1. **Consider the null hypothesis: this is a competently-built conventional
   system with an LLM attached to two or three stages, assembled from software
   engineering practice that predates LLMs — not a novel architecture.** How
   much of §4 survives that framing? Which mechanisms, if any, are actually
   doing something new? A verdict of "mostly conventional, well assembled" is a
   legitimate and useful answer.

### Costs and failure modes of the central design choice

2. Have any frameworks tried compiling natural language into a fixed typed plan
   before execution and then **abandoned** it? What are the documented failure
   modes of staged/frozen planning versus interleaved plan-act loops,
   particularly in dynamic or partially-observable environments?
3. What happens in such designs when a frozen plan becomes wrong or stale
   mid-run — a file it assumed disappears, an API goes down? What recovery
   paths exist, and how do they compare with dynamic replanning?
4. How do systems that separate planning from execution verify the plan at
   execution time — recomputation, recorded verdicts, re-running validators, or
   otherwise? What are the trade-offs, and is recomputation worth its cost?
5. Is including evaluation criteria inside a plan's integrity hash done
   elsewhere? What are the arguments against it?

### Comparison with existing frameworks

6. How do LangGraph, CrewAI, AutoGen, MetaGPT, OpenHands, Semantic Kernel, and
   comparable frameworks structure the boundary between planning and execution?
   Which validate a typed plan before acting?
7. How common is indirection between an abstract operator role and a concrete
   model, with graded requirements and conditional failover? What do production
   systems typically do instead?
8. What IPC do agent frameworks use for workers — RPC, in-process, message
   queue, filesystem? What are the known trade-offs of filesystem queues, and
   why have most systems chosen otherwise?
9. What is current practice for handling schema-invalid LLM output — retry
   budgets, repair prompting, constrained decoding, grammar-constrained
   sampling? How do small fixed ceilings (3–5 calls) compare, and what hit rates
   are reported?
10. Given a project that self-reports "not full parity" against a named similar
    project (AutoSci, §5), what would a rigorous head-to-head evaluation of two
    research-agent systems actually require? Does published methodology exist?

### Capability declaration, effects, and enforcement

11. Is there published work on capability manifests for LLM agents that declare
    read/write/execute/network/cost/risk up front? How is such a manifest
    typically enforced, if at all?
12. Manifest-based permission systems (Android permissions, Docker
    capabilities, package manifests) have documented histories of developers
    over-declaring defensively, weakening the granularity in practice. What does
    the literature say about manifest-accuracy decay, and would it apply here?
13. Where a manifest declares a `risk` field, does anything typically *gate* on
    it, or is it descriptive metadata? Is there prior art for risk as an
    enforced dispatch input rather than documentation?
14. Has object-capability security or programming-language effect-system theory
    been applied to LLM tool invocation in published work? Key papers?
15. How do tool-selection systems decide when a tool must *not* be used? Is
    declaring negative applicability standard, or is selection universally
    similarity-based?
16. How do systems prevent an agent from claiming it executed something it did
    not? What is current practice in execution attestation for agents?
17. What is current practice for conflict detection between concurrent agents
    editing a shared workspace?

### Scientific research automation

18. What is the state of the art in automated claim extraction from scientific
    literature? Which systems, which benchmarks, what accuracy?
19. What verdict taxonomies are standard in automated claim verification? How
    does FEVER's scheme compare with a four-value supported / partially
    supported / not supported / inconclusive set?
20. What techniques currently exist for detecting or preventing fabricated
    citations? Is binding a citation to a hash of source text used anywhere, and
    what are its limitations?
21. How do The AI Scientist (Sakana), Coscientist, agent-laboratory, and similar
    end-to-end research agents structure their pipelines? Typed evidence
    artifacts or free text? What do their evaluations show?
22. Is requiring a machine-readable study protocol — search strategy, inclusion
    and exclusion criteria, explicitly unresolved fields — standard in automated
    literature review? How does this relate to PRISMA, and does PRISMA
    compliance have automated tooling already?
23. What is the state of the art in automated experiment design and execution
    with measurement attestation?

### Evidence, evaluation, and how much a demo proves

24. Is a single successful 15-node run — achieved with a mid-run fix and a
    service reload — sufficient evidence of anything beyond "the happy path
    executes once under supervision"? What does the field consider a minimum
    credible evidence bar: how many runs, what failure injection, what
    unattended requirement?
25. When systems report passing tests, how often are those tests exercising live
    models and APIs versus fixtures and mocks? What reporting norms exist, and
    how should an outside assessor probe this?
26. How do frameworks distinguish "capability installed" from "capability
    actually exercised"? Is there published work on activation or exposure
    proof, and are such mechanisms **gameable** — could a worker emit ledger
    events resembling genuine activation without meaningful work, as with
    code-coverage gaming?
27. Are negative controls used in agent capability test suites, or is testing
    predominantly positive-path?
28. How do SWE-bench, Terminal-Bench 2.0, GAIA, OSWorld, WebArena, BrowseComp,
    and tau-bench each define success? Which suit a system spanning both
    software delivery and research, and which would this system likely do badly
    on?
29. Does an accepted benchmark exist for end-to-end automated research quality,
    as opposed to component tasks?
30. Is a multi-state result vocabulary distinguishing not-tested,
    environment-blocked, and not-available from failure used elsewhere, or is
    pass/fail the norm? What are the arguments for and against the added
    complexity?

### Architecture

31. What is current practice for local-first, workstation-scale multi-agent
    systems as opposed to cloud orchestration? What are the known limits?
32. How do durable-workflow engines (Temporal, Airflow, Dagster, Prefect) handle
    plan immutability, replay, and mid-run change? What should an agent
    framework borrow, and what does that literature say about the cost of
    immutability?
33. Is provider-neutral operator abstraction — here roughly half of executors
    have no model vendor — common? What do systems typically do about vendor
    lock-in, and is neutrality worth its complexity?

## 7. How to answer

For each mechanism M1–M13 please give: **standard / uncommon / unusual**, the
closest known systems, key citations, and any respect in which the described
approach is *worse* than current practice. Then address §6, flagging any
question resting on a false premise.

Blunt assessment is more valuable than validation. If the honest verdict is
"this is a well-engineered assembly of known techniques," that is a useful
finding and should be stated plainly.
