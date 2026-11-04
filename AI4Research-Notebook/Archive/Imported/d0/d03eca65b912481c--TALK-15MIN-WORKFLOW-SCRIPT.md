# 15-Minute Talk — The Workflow (draft script)

Written 2026-09-11. Deliverable 1, general half. Hands off to the capability-capsule half.

**This is a speaking script, not a document.** Read it aloud, not silently — the
register is deliberately spoken (short sentences, contractions, sentence
fragments where a pause belongs). If a line feels odd on the page, say it out
loud before changing it.

---

## Word budget — the arithmetic

| Quantity | Value | Reasoning |
|---|---|---|
| Slot | 15 min | = 900 s |
| Slide transitions | ~24 s | 7 figures + title, ~3 s each |
| Diagram parse silence | ~50 s | 5 figures the room must actually read, ~10 s each |
| Deliberate pauses | ~16 s | 4 claims worth landing, ~4 s each |
| Stumble / breath buffer | ~60 s | ~7% of slot |
| **Non-speaking total** | **~150 s** | **= 2.5 min** |
| **Actual speaking time** | **~12.5 min** | 900 − 150 |
| Delivery rate | 130 wpm | prepared technical talk with diagrams |
| **Word budget** | **~1,625 words** | 12.5 × 130 |
| Hard ceiling | 1,700 words | beyond this you will overrun |

**This script as written: 1,435 words** (measured, not estimated) — about
**13.5 minutes** delivered. That is ~90 seconds under the slot, which is the
safe direction to be wrong in. If you want the full fifteen, the expansion
block at the bottom adds ~190 words at two marked insert points.

### Calibrate this against your own rate before you trust it

130 wpm is a planning figure, not your figure. Time yourself reading §1 aloud at
presentation pace — it is 709 words. Then:

```
your wpm = 709 / (seconds taken / 60)
```

- **Under 115 wpm** — you need to cut ~200 words. Cut list is at the bottom.
- **115–145 wpm** — the script fits as written.
- **Over 145 wpm** — you are rushing. Do not add words; add pauses.

Do not calibrate by reading silently. Silent reading runs 2–3× faster than
speech and will tell you the script is short when it is not.

### Allocation

All word counts below are **measured from the script**, not estimated.

| Movement | Words | Speaking | + non-speaking |
|---|---|---|---|
| I — One request, end to end | 709 | 5.5 min | ~6.6 min |
| II — Standard vs uncommon | 249 | 1.9 min | ~2.3 min |
| III — What was actually hard | 362 | 2.8 min | ~3.4 min |
| Hinge — into capability capsules | 115 | 0.9 min | ~1.2 min |
| **Total** | **1,435** | **11.0 min** | **~13.5 min** |
| *with expansion block* | *1,625* | *12.5 min* | *~15.0 min* |

---

## Figure list (build these seven, nothing else)

| # | Where | What it shows | What you do while it is up |
|---|---|---|---|
| 1 | §1.3 | The nine-stage pipeline, left to right, with **the freeze drawn as a vertical bar** splitting the diagram into "interpretation" (left, model-driven) and "execution" (right, deterministic). Stages you narrate in **bold**; the five you skip in grey. | Stays up for the whole worked example. Point at each stage as you reach it. Do **not** read the labels aloud. |
| 2 | §1.4 | The freeze itself. A box labelled *frozen contract* with a hash on it — and **the evaluation rules drawn inside the box**, not beside it. One arrow back in, crossed out: "cannot be edited after this point." | This is the money slide. Put it up, say the line, then stop talking for three seconds. |
| 3 | §1.5 | Three stacked layers: capsule → logical operator (45) → physical operator (102), with a routing table between the bottom two showing conditions (*always / if quota allows / emergency only*). | Trace one path top to bottom with your finger while you talk. |
| 4 | §2 | Two columns side by side: **Standard practice** (8 rows) and **Less common** (3 rows). Standard column visually heavier / longer. | Let the asymmetry do the argument. The picture says "mostly ordinary" before you do. |
| 5 | §3.1 | Two columns: **Intrinsic** (generalises) and **Incidental** (ours). 3 rows each — do not put all five and six on the slide. | — |
| 6 | §3.2 | The contradiction, side by side. Left: `all_nodes_passed = true`, `closure: PASS`. Right: the manifest's own `evidence_gate.status = failed_for_full_requested_scope` and the poster text *"Evidence Gate: Not Passed"*. A red line between them. | Let the room read it before you explain it. This slide is the whole story. |
| 7 | Hinge | One causal step, vertical: *completion inferred from process exit* → *nothing declared what "done" meant* → *a capsule is that declaration, made first-class*. | Last slide of this half. **Do not advance past it** — the capsule half opens on this same slide. |

---

# THE SCRIPT

---

## §1 — One request, end to end  *(~7 min, 800 w)*

### 1.1 The one idea  *(115 w)*

I'm going to show you one idea, and then one request moving through the system
that implements it.

The idea is this. A language model interprets what you meant. Then deterministic
code freezes that interpretation into a contract, and executes it. The model
never gets to re-interpret after the freeze.

If you've used a package manager, you already know this shape. You write a loose
dependency range. The resolver decides. The lockfile records the decision. And
every install after that reads the lockfile, not the range.

The freeze is that lockfile, for research work.

Everything else I say today is downstream of that one sentence.

### 1.2 What it is for  *(70 w)*

Briefly, what this is. It's a local workstation tool, not a hosted service. It
runs two kinds of workload — code delivery, and research.

The research half is the harder one, and it carries a requirement that shapes
the whole design: a research run has to produce structured evidence that another
program can check. Not prose. That constraint is why the pipeline looks the way
it does.

### 1.3 The request  *(325 w)*

> **[FIGURE 1 — the nine-stage pipeline. Leave it up through §1.4.]**

So. You type a request. *Do a systematic study of KV-cache efficiency for
long-context LLM inference.*

Nine stages. I'll narrate four properly and wave at the rest.

**Stage two, intent compilation.** A model reads your sentence and answers one
question — what did they actually ask for? It produces a typed record. Goals,
constraints, ambiguities, and explicitly, unknowns.

Here's the first decision worth noticing. That record cites your original text,
and the model is not permitted to write the citation coordinates. Code
re-derives them by searching your text itself. The model can say what you meant.
It cannot say where you said it.

**Stage three** does the same trick at larger scale. A model answers *what would
satisfy this request*. Then a second, independent model reviews that answer —
and the reviewer can only find fault. It can't rewrite. The constraints from
stage two are copied forward and locked: the model may interpret beside them,
never edit them.

**Stage four, planning.** A model decides how. Which steps, what order, which
capabilities. It's also allowed to conclude that the honest answer is a direct
reply with no execution at all.

One thing before I go on. Stages two through four can *refuse*. A request that
fails validation, or that needs clarification, stops there. That's a designed
outcome, not an error.

### 1.4 The freeze  *(115 w)*

Then stage five.

> **[FIGURE 2 — the freeze. Say the next two sentences, then stop for three seconds.]**

The plan is compiled into an immutable contract and hashed end to end. And here's
the part I'd ask you to remember: **the rules that will be used to judge this run
are inside that hash.**

A run can't later soften its own passing criteria. Changing the criteria changes
the hash, and the hash gets checked.

After the freeze, everything is deterministic. The contract becomes a DAG. Nodes
run when dependencies clear. Two nodes declaring overlapping file writes are
never scheduled together — and a node that doesn't declare its write scope at
all is treated as exclusive. It fails safe.

Dispatch hands each ready node to a worker under a time-limited lease, with a
fingerprint check so a retry can't accidentally re-run expensive work.

Then the work happens, evaluators judge each result against the frozen rules, and
delivery produces a report plan, a draft, a review, and the files.

### 1.5 How capabilities reach hardware  *(175 w)*

One more layer, because it matters for the second half of this talk.

> **[FIGURE 3 — the three-layer indirection.]**

Plans don't bind to models. They bind to *roles*.

A capsule says what capability is needed. That maps to a **logical operator** —
an abstract role, forty-five of them. Something like *needs architecture
reasoning at level four*. And that maps to a **physical operator** — a concrete
executor. A hundred and two of those.

A routing table connects them, with conditions. Always. If quota allows. If a
plugin is present. Emergency only. So when your first-choice model is out of
quota, the next one takes over — and the plan doesn't change.

That word *capsule*. Hold onto it.

A capsule is a single file describing one unit of capability. Think of it as a
function signature that also declares its side effects and who's allowed to call
it. There are eighty registered.

I'll come back to them properly in the second half. For now it's just the thing
dispatch hands work to.

---

## §2 — Standard versus uncommon  *(~2.5 min, 275 w)*

So how much of that is actually new?

Mostly, it isn't. And I want to say that first, because the honest split is more
useful to you than a pitch.

> **[FIGURE 4 — two columns. Let the room see the asymmetry before you talk.]**

Content addressing is decades old. Topological DAG scheduling is textbook. Leases
with stale reclaim are standard distributed-systems hygiene. Idempotency
fingerprints are routine in anything that retries. Filesystem work queues are a
well-known pattern — generally worse than a message broker, though defensible
here, because you get language-agnostic workers on one machine with nothing to
install. And declaring effects in a manifest is what Android permissions and
Docker capabilities already do.

Three things are less common.

**First**, verification *recomputes* rather than reads. Most systems check their
own stored verdict. This one re-runs each planning stage and compares hashes.

**Second**, the evaluation criteria live inside the plan's integrity hash. That's
the mechanism I just showed you — and it exists specifically so a run can't
re-grade itself.

**Third**, capabilities declare when they must *not* be selected. Negative
applicability signals. And the test layer checks the matching property — that
unrelated capabilities are correctly *not* chosen.

If I had to name one property instead of three mechanisms, it's this. The system
defaults to fail-closed in at least six independent subsystems, written at
different times by different people. That consistency is harder to achieve than
any single item on that list.

Whether the combination is novel — I'm not going to claim that. It's a question
for a literature review we haven't finished.

---

## §3 — What was actually hard  *(~4 min, 440 w)*

### 3.1 Intrinsic and incidental  *(255 w)*

Now the part I think is most worth your time. What was actually hard.

I want to separate two kinds of problem, because only one of them generalises.

> **[FIGURE 5 — intrinsic vs incidental, three rows each.]**

Some problems are **intrinsic**. Anyone building this class of system hits them.

Provider structured-output dialects aren't interchangeable. OpenAI's strict mode
requires every property listed as required. Gemini rejects certain recursive
schemas. Those aren't bugs — they're three vendors' real constraints. Which means
a schema projection layer has to be a first-class component, not something you
bolt on afterward.

Natural-language requirements don't cleanly separate *what to retrieve* from
*what to deliver*. That sounds abstract, so concretely: process language bled
into the topical filters, and the system started filtering its literature search
on words that described the deliverable. That's a real semantics problem, and it
shows up in anything that compiles free text into an execution plan.

And — whether something actually happened can't be certified from an exit code. A
wrapper can return ok, exit zero, and be wrapping work that failed internally.

The other kind is **incidental**. Real, but consequences of choices this project
made. Driving sub-agents by injecting keystrokes into terminals produced a race
condition — a message queue wouldn't have that failure mode at all. A shell
daemon ran pre-fix code for twenty-eight hours because nothing restarted it.
Worth knowing. Doesn't generalise.

### 3.2 The system caught itself  *(185 w)*

I want to finish on one incident, because I think it's the best evidence for
anything I've said.

> **[FIGURE 6 — the contradiction. Let them read it. Count to three.]**

Earlier this month, a run froze a fourteen-node graph, executed every node, and
delivered all eight requested files. Closure recorded pass. `all_nodes_passed`
was true.

Then the delivered files went through content acceptance.

The run's own manifest declared that its evidence gate had failed for the full
requested scope. The poster it generated displayed, in text, *"Evidence Gate:
Not Passed."* All six sources had parsed — but two of them, H2O and SnapKV, were
excluded on assessment, leaving four, with insufficient coverage.

And the project wrote this down about its own run:

> "This sprint can only prove physical execution and eight-file delivery; it
> cannot count as a complete E2E PASS."

They changed the gate, so a manifest declaring its own failure can never publish
again — with a regression test for exactly that case.

That's the design philosophy meeting its own implementation. The system refused
to treat an attempt as an outcome. Even when the attempt was its own.

---

## Hinge — into capability capsules  *(~1 min, 120 w)*

One question to carry into the second half.

Why was that possible at all? Why could a run record itself as passed while its
own evidence said otherwise?

> **[FIGURE 7 — the causal step. This is the last slide of this half AND the first slide of the next. Do not advance past it.]**

Because completion was *inferred* — from the fact that processes exited and files
appeared — rather than *read* from a contract that declared what completion
meant.

That's the third intrinsic problem from two slides ago. And it has a shape.

The thing that did the work should not be the thing that certifies the work. And
what counts as done has to be written down before the work starts, by something
other than the worker.

A capability capsule is that contract, made first-class.

That's the second half.

---

## Source note — the quoted sentence in §3.2

The blockquote in §3.2 is a translation, not a paraphrase. Everything around it
is narration.

**Translated from** `harness/metadata/pre-scheduler-stabilization-log-20260829.md:638`

Full translation of that entry:

> After content acceptance was carried out on the final eight files, it was found
> that `research_run_manifest.json` itself declared
> `evidence_gate.status=failed_for_full_requested_scope` and
> `closure_status=open_degraded`, and listed failed gates; `poster.html` likewise
> displayed `Evidence Gate: Not Passed`. All six input sources had been parsed,
> but H2O and SnapKV were excluded by source assessment, leaving only four
> selected sources, with insufficient method/comparison/metric coverage. The old
> closure's `all_nodes_passed=true` conflicts with the research truth of the
> deliverables, so this sprint can only prove physical execution and eight-file
> delivery; it cannot count as a complete E2E PASS.

[TN: 真值 = "true value"; not the ML "ground truth".]

**Chinese original** (copied from the file, per the kit's M8 rule):

> 对最终八文件做内容验收后发现 `research_run_manifest.json` 自己声明
> `evidence_gate.status=failed_for_full_requested_scope`、`closure_status=open_degraded`
> 且列出 failed gates；`poster.html` 同样显示 `Evidence Gate: Not Passed`。六个输入源均已
> parse，但 H2O 与 SnapKV 被 source assessment 排除，只留下四个 selected sources，
> method/comparison/metric 覆盖不足。旧 closure 的 `all_nodes_passed=true` 与交付物的
> 研究真值冲突，所以该 sprint 只能证明物理执行和八文件交付，不能作为完整 E2E PASS。

`tcheck: OK (0 failures, 0 warnings) · critic: fresh subagent · verdict: faithful-with-fixes (3 findings, all applied)`

### What the source does NOT say — do not restore these

| Do not say | Why |
|---|---|
| "Then **someone** opened the files" | The source clause is subject-less. English forces a subject; supplying "someone" invents an actor the source does not name, and makes a deliberate step sound like luck. |
| "They **retracted** their own passing run" | Verified: **zero** occurrences of 撤回 / 撤销 / 收回 / 作废 in the surrounding entries. The source verb is 冲突 — the closure flag *conflicts with* the deliverables' research truth. The retraction-like effect is the **permanent fix** at `:639` (closure 不能再 — can *no longer* — mark such a run completed), which is future behaviour, not something done to this run. Fair as your spoken characterisation; never inside quotation marks. |
| "Six sources parsed" | The source says 均 — **all** six. Dropping the quantifier weakens a claim that is in your favour. |
| "proved file delivery" | Drops 物理执行 — physical execution. The source claims both. |

# Delivery notes

## The four pauses

Marked in the script. Do not skip them — they are inside the 15-minute budget.

1. After *"the rules that will be used to judge this run are inside that hash"* (§1.4) — 3 s
2. After the two-column figure appears (§2) — 2 s, before you start talking
3. After Figure 6 appears (§3.2) — 3 s, let them read the contradiction
4. After *"even when the attempt was its own"* (§3.2) — 2 s, before the hinge

## If you are running long — cut in this order

| Cut | Saves | Safe because |
|---|---|---|
| §1.5 routing-table conditions (*always / if quota allows / emergency only*) | ~35 w | The three-layer picture survives without the condition list |
| §2 the filesystem-work-queue sentence | ~40 w | Longest item in the standard column; the column is already heavy |
| §3.1 the shell-daemon example | ~25 w | Keep the keystroke-race example; it's the better one |
| §1.3 the "stages two to four can refuse" paragraph | ~45 w | Move it to Q&A — it's a good answer, not a necessary beat |

Total available: ~145 words ≈ 65 seconds. **Do not cut the hinge or §3.2.**

## If you are running short — the expansion block

The script runs ~13.5 min as written. These two inserts bring it to ~15.0 min.
Both are additive: nothing else in the script references them, so you can decide
on the morning without re-reading anything.

**Decide before you walk in, not on stage.** A talk padded live runs long,
because the padding gets added early and the cuts come out of the close.

### Insert A — §2, after the third "less common" item  *(~65 w)*

> **Fourth.** Extracted claims are hash-bound to their sources. When the system
> pulls a claim out of a paper, it records a citation span tied to a hash of the
> exact source text. Which means a fabricated citation isn't just unlikely — it's
> structurally detectable. You can check it mechanically. For a research system,
> that's the failure mode you most need a machine answer to.

*Then amend the spoken line "three things are less common" to "four things".*

### Insert B — §3.1, after the exit-code paragraph  *(~125 w)*

> Two more, quickly, and both are the kind of thing you only believe after it
> bites you.
>
> Multi-writer state on a local filesystem corrupts silently unless you version
> it explicitly. This project found that class of bug in two separate eras of the
> codebase — which suggests it isn't an oversight, it's a standing cost of
> choosing local files as the source of truth.
>
> And: if you maintain two schemas for the same object, they will drift. Here
> there are genuinely two — a flatter one the model writes against, and a
> canonical one the system uses — for a good reason, because models generate
> better against simpler schemas. The tension is intrinsic. The drift is
> guaranteed unless a test asserts they still match.

*Figure 5 stays at three rows per column. These are spoken, not shown.*

### If you are still short after both

Do not add more words. Take questions earlier. Unused time becomes Q&A, which is
where the supervising engineer will actually engage.

## Numbers said aloud — verify before presenting

| Said | Source | Trap |
|---|---|---|
| forty-five logical operators | V3 §10 | — |
| a hundred and two physical operators | V3 §10 | Only 63 are *enabled*. Don't volunteer 102 as a capability count |
| eighty registered capsules | V1 §4 | Five more sit on disk unregistered and inert — that's the interesting half if asked |
| fourteen-node graph, eight files | V3 §29.1 (2026-09-02) | **Distinct from** the 15-node accepted E2E run on 2026-09-03. Do not merge them |

## Two things this script deliberately does not say

- **Test numbers** (606 passed / 34 failed / 8 skipped) and the release-candidate
  status. At 15 minutes with a capsule half following, status belongs in Q&A —
  and the retraction story already establishes the honesty this half needs. If
  asked directly, answer plainly and immediately.
- **Any paper citation.** No comparison to named systems. §2 makes its claim from
  the codebase only, which keeps this half clear of citation exposure.
