# 30 — Concurrency: many agents, one mutating library

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
question. Paper claims **[verified]** against the local extractions.

> "What about concurrency? What if two agents are working at the same time —
> surely they could benefit from knowing the MCPs, but also the MCP library is
> getting updated and modified."

**Nothing in notes `17-` … `29-` addresses this, and it is not a detail.** It is
the first requirement that makes several previously-optional pieces mandatory,
and it is the one dimension where capsules have an advantage no other system on
the comparison can offer.

---

## 1. Why this is harder here than ordinary read-write concurrency

A database handles concurrent readers and writers. This is worse in one specific
way: **a read is not a lookup, it is baked into a frozen plan.**

The architecture's central discipline is the freeze — the planner resolves
capabilities and freezes a plan; the scheduler executes only what was frozen and
may not re-derive anything. So a "read" of the library is not momentary. It is
a commitment that has to stay valid for the lifetime of a run, which under
multi-day autonomous operation (`26-`) may be days.

If another agent modifies a capsule in that window, the frozen plan now names a
capability whose behaviour has changed underneath it. **Nothing detects that
today.**

⚠ **This makes the missing `version` field load-bearing.** Note `13-` records
`version` present in only **43 of 85 manifests**, and the evolution contract as
designed-not-implemented. Under single-agent operation that is a tidiness gap.
Under concurrency it is a correctness bug: **a frozen plan must pin capsule
versions, not capsule IDs.** Alita-G, for reference, has no versioning at all —
`version` occurs zero times in the paper (`27-` §1).

**This is the strongest available argument for the evolution contract**, and it
arrived from a direction none of the roadmap items anticipated.

## 2. What the prior art already does — and it converges

Two of the six systems have real concurrency designs, and they landed on the
same discipline independently.

**SkillDAG** [verified, 2606.03056] — a **propose-then-commit** protocol under
three structural invariants: *acyclicity, non-contradiction, append-only
reversibility* (line 83-84). Commits carry a natural-language reason and the
supporting execution trace (line 283). Rollback is by recency or task ID via the
append-only log (line 323, 972). Stale edges get an explicit retraction path —
add, delete, or retype (line 310).

Its correctness property is the one to steal: **online edits expand ground-truth
recall *set-monotonically*** (line 460) — edits "enlarge ground-truth recall
**without evicting prior hits**" (line 38).

**DGM** [verified, 2505.22954] — genuinely parallel: `k` self-improvements run in
parallel per iteration (line 1816), two iterations in parallel for SWE-bench
(line 319), and the archive exists precisely to enable "parallel exploration of
multiple paths" (line 1671). Its conflict-avoidance mechanism is that the
archive is **append-only** — nothing is ever modified in place, so concurrent
writers cannot collide.

**And this is also the DeepSeek Harness's own discipline**, per the dsh panel's
notes: committed generations are never renamed, replaced or deleted; a write
publishes a **version-named successor beside the source**. Three independent
designs, one answer.

> **Concurrency discipline, converged: append-only, versioned, monotone. Never
> modify in place.**

The other four systems have nothing to say here. Alita-G's Box is built offline
and frozen at inference — it has no concurrency story because it has no
concurrent phase. SkillWeaver's transfer result (strong agents' APIs lift weaker
agents) is *sequential* sharing, not concurrent.

## 3. The design that follows

### 3.1 Lifecycle state is the isolation boundary

The cleanest available answer to "does agent B see what agent A just built",
and it needs no new machinery — `19-`'s lifecycle already has the states:

| State | Visibility | Rationale |
|---|---|---|
| `draft` | **private to the generating run** | unproven; sharing it propagates silent rot (`29-`) to a second agent |
| `stable` | **shared, and pinnable by version** | earned promotion on observed evidence |
| `retired` | not selectable; existing pins still resolve | retirement must not break a frozen plan mid-run |

> **Promotion is publication.** That single sentence resolves visibility,
> and it makes the promotion gate (`13-` R6) a concurrency control rather than
> just a quality control.

### 3.2 Pin versions in the frozen plan

The plan freezes `capsule_id@version`, not `capsule_id`. A concurrent admission
publishes a new version beside the old; running plans keep resolving to what
they froze. This is exactly dsh's versioned-successor rule applied to the
registry.

### 3.3 Monotonic admission as a checkable invariant

SkillDAG's set-monotonicity generalises into something the admission gate can
actually enforce:

> **A concurrent admission must never invalidate a plan already frozen.**

Admissions add; they never remove or redefine. Retirement marks a capsule
unselectable *for future planning* and leaves existing pins resolvable. That is
a mechanical property, testable, and it belongs in the gate's rejection reasons
as something like `NON_MONOTONIC_ADMISSION`.

### 3.4 Gap leases — the thundering herd

Two agents hit the same capability gap simultaneously, both search, both find
nothing, both generate. The result is two near-identical capsules — Alita-G's
measured duplication problem (`27-` §4), arriving faster.

Mitigation, in order of cost:

1. **Claim the gap before building.** Agent A registers an intent to build
   capability X; B either waits on it or proceeds without. Standard single-flight
   / cache-stampede handling.
2. **`DUPLICATE_CAPABILITY` at admission** (`17-` §4.3) catches what slips
   through — necessary anyway, but it wastes the generation that lost the race.
3. The repo's `capsule-cooldown.json` rate-limits generation but does **not**
   deduplicate concurrent intent; it is related machinery, not a substitute.

### 3.5 Index coherence

The selection stack (`23-` §4) has a typed filter, a quality floor and an
embedding index. Under concurrency the index must move with the registry:

- a capsule admitted but not yet indexed **exists and is unfindable**;
- a capsule retired but still indexed **is selectable and shouldn't be**.

Both are silent failures. The registry and its index need to advance together,
or the index needs to be derived from the registry at query time rather than
maintained alongside it.

## 4. The part that is genuinely ours

Everything above is defensive. This is the upside, and **no system on the
comparison can offer it**:

> **Declared effects make concurrent capability use statically analysable.**

If two agents' planned capabilities declare their `write` scopes and `network`
reach up front, then **write-scope collisions between concurrent runs are
detectable before either is scheduled** — not discovered as corruption
afterwards. Effect declaration stops being only an admission-time safety check
and becomes a *scheduling* input.

None of the six papers can do this, for the same reason none of them gates on
effects: their tools do not say what they touch. It is the concurrency-specific
version of the argument the whole report makes.

⚠ **And this is the Cordis dimension note `20-` skipped.** That note read Cordis
for **temporal** composability — reversible effects, retirement ordering. But
Cordis's abstract gives equal weight to **spatial** composability, and its
unifying result is explicitly about interleaving:

> *"the mediation induces an observational equivalence up to which the effects of
> distinct components interleave without disturbing one another."*

**Non-interference between concurrently active components is the formal frame
for §4**, and it is already in the paper underlying the harness this work
targets. Note `20-` should be extended, or a companion note written, covering
the spatial half — it is the more relevant half for this question.

## 5. The upside worth stating

Concurrency is not only a hazard. The quality ladder (`23-` §4) needs invocation
evidence, and `13-` R6 records that capsules currently have no feedback loop at
all. **N concurrent agents generate N times the evidence**, so promotion and
demotion decisions get better faster, and the cold-start problem (`23-` §6)
shrinks. A shared library under concurrency is the *reason* a quality ladder
becomes measurable rather than theoretical.

The condition is that evidence be attributed per capsule *version*, or the
signal from two versions blurs together — which brings §3.2 back around.

## 6. Open questions

- **Q28 — What is the concurrency model?** Multiple agents in one process, one
  machine, or across machines? Decides whether this is a lock, a lease, or a
  distributed consensus problem.
- **Q29 — Is the registry single-writer?** A single admission service serialising
  writes removes most of §3 at the cost of a bottleneck, and is very likely the
  right first answer.
- **Q30 — May agent B use agent A's `draft` capsule?** §3.1 says no. Worth
  confirming, because "yes" would be much faster and much more dangerous.
- **Q31 — What happens to a running plan when its pinned capsule is retired
  mid-run** for cause (e.g. it was found to be silently rotten)? Finish, or abort?
  This is a genuine safety-vs-liveness trade and the answer differs for a
  correctness retirement versus a routine one.
- **Q32 — Is evidence attributed per version or per capsule ID?** §5.
