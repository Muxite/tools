# 24 — The local compute envelope, and what it constrains

Written 2026-09-10 by the capability-capsule panel (pts/9), from the user's
design brief. Read with `23-` §4 and `25-` §3.

> "My concern is how much processing power the local user is expected to have.
> This could determine how heavy and how much computation and effort goes into
> curating and searching the MCP library. Alita-G might be relatively simple,
> but beyond-task-completion could take more effort and more memory. How much
> of that memory could have been used to fit better models? Does it take up
> bandwidth on GPUs to move in and out? Does it limit how many MCPs we can hold
> in fast memory?"

⚠ **Framing amended 2026-09-10 — read this first.** The user now expects
**API-based, non-local generation models**, and that **multi-day autonomous runs
belong on a university, company, or cloud server** rather than a workstation
(`26-` §1). That changes what this note is for:

- **§1's conclusion survives and is unaffected** — the *encoder* choice is
  separable from the generation model, and nothing about API-based generation
  makes local embeddings bigger.
- **§2 (index cost) survives** — it was always arithmetic, not hardware.
- **§3 (admission cold-path / selection hot-path) gets *stronger*** — a server
  has idle capacity between runs, which is exactly what conformance checking
  wants.
- **§4 (GPU contention) largely dissolves** under hosted generation, and becomes
  conditional on Q18 rather than assumed.
- **New:** Alita-G's ~15% mean-token reduction stops being a latency footnote and
  becomes a **cost** line item over a multi-day run on metered APIs.

Everything below is therefore conditional on **Q17/Q18** (`§5`), and the
local-first reading applies to the *interactive workstation mode* rather than the
autonomous server mode the design targets. See `26-` for the deployment split and
the threat model that replaces compute as the binding constraint.

---

This was written as a first-class constraint because **AI4Research is presented
as a local workstation tool** — the other panel's report states this as its
framing (`report/VARIANT-1-brief-overview.md` §2). Every design choice in `17-`, `19-`,
`23-` and `25-` spends some part of a budget nobody has yet written down.

---

## 1. The finding that answers most of this [verified]

**The project already runs local embeddings, and they are very small.**

`mempalace/mempalace_init.py:46-49` selects a sentence-transformers encoder by
language:

| Language | Model |
|---|---|
| `en` | `sentence-transformers/all-MiniLM-L6-v2` |
| `zh`, `ja`, other | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

Backed by **ChromaDB** as a persistent local vector store
(`mempalace_init.py:23-24, 84-90`, `chromadb.PersistentClient`), with a
resident daemon that keeps a cached HuggingFace snapshot warm
(`harness/lib/experience/memory_serve_daemon.py:33`,
`memory_serve_wrapper.py:36`). There is also an MCP server in-tree —
`mempalace/mempalace_mcp_server.py` — so the MCP surface is not hypothetical
here either.

**Now compare to Alita-G.** Its headline 83.03% uses OpenAI
`text-embedding-3-large`, hosted, 3072-dimensional (§4.1). Its Table 5 ablation
over encoders, same tasks, library held constant:

| Encoder | Accuracy |
|---|---|
| text-embedding-3-large | **84.0** |
| text-embedding-3-small | 80.0 |
| Qwen3-Embedding-8B | 76.0 |
| NV-Embed-v2 | 72.0 |
| BGE-M3 | 72.0 |

⚠ **Every encoder Alita-G tested is far larger than the one this project
actually runs.** MiniLM-L6-v2 is roughly 22M parameters at 384 dimensions
[unverified — model-card figures from recall; confirm before publishing];
Qwen3-Embedding-8B is 8B. Alita-G's ablation therefore does not bound what
happens at MiniLM scale, but its trend is monotone and downward, and the two
worst encoders it tested already cost **12 accuracy points**.

**The conclusion is concrete and it settles the design question in `23-` §4:**

> On the hardware this system actually targets, embedding similarity is the
> *weakest* signal available, not the strongest. It cannot carry the admission
> decision. It can only rank inside a candidate set that a typed, exact
> contract filter has already made admissible.

That is the same conclusion `23-` §4 reached architecturally, now with a
hardware reason behind it. Two independent arguments for the same stage
ordering is worth stating in the report as such.

## 2. What the index actually costs — the cheap part

The user's worry that the MCP library competes with model weights for fast
memory is worth quantifying, because the answer is reassuring and the *real*
cost is elsewhere.

At 384 dimensions, float32 (arithmetic, not measured):

| Library size | Raw vectors |
|---|---|
| 100 | ~150 KB |
| 1,000 | ~1.5 MB |
| 10,000 | ~15 MB |
| 100,000 | ~150 MB |

Even at 100× the current 80-capsule registry, the vector index is **noise**
next to the encoder itself, and far below anything that would displace a model.
Chroma adds overhead for metadata and its HNSW graph, but not an order of
magnitude at these sizes.

**So the answer to "does it limit how many MCPs we can hold in fast memory" is:
not the embeddings.** The cost lives in three other places, and they should be
budgeted explicitly:

1. **The resident encoder** — a fixed cost, paid once, already being paid by
   `memory_serve_daemon`. Adding capsule search to an already-warm encoder is
   close to free.
2. **Conformance checking at admission** — the genuinely new cost. Static
   effect analysis, schema validation, invariant checks on a verification
   corpus, negative controls, and duplicate detection are per-admission work.
   This is what the brief means by "beyond-task-completion could take more
   effort and more memory."
3. **Observability and evidence** — `23-` §7.1 notes Alita-G stores nothing
   about invocation history. Storing it is what makes the quality ladder
   (`23-` §4) possible, and it grows with *use*, not with library size. This is
   the one that grows without bound over a week-long run.

## 3. The asymmetry that makes this affordable

The important structural point, and a good one for the report:

> **Admission is expensive and rare. Selection is cheap and constant.**

Conformance checking runs once per candidate capability, at admission time,
off the critical path — it can be slow, batched, and even deferred, because a
capsule sits in `draft` until it passes. Selection runs on every planning
decision and must be fast.

Alita-G has the opposite shape: its curation is cheap (keep what succeeded) and
its selection carries all the weight (one embedding pass and a threshold, per
task). **We are proposing to move cost from the hot path to the cold path.**

That reframes the brief's concern. The question is not "can the local machine
afford conformance checking" in the abstract — it is *how much cold-path
compute is available between runs*, which for a workstation running a week-long
job is substantial and currently idle.

## 4. The GPU-bandwidth question

The brief asks whether moving capabilities in and out consumes GPU bandwidth.
On the current stack, largely **no**, and for a specific reason: MiniLM-class
encoders run acceptably on CPU, and ChromaDB is a CPU-side store. Nothing in
the capsule path needs to be resident on an accelerator.

That is a property worth *protecting* rather than assuming. It becomes false
the moment either of these is adopted:

- a large local embedding model, to close the gap in §1 — which would put the
  encoder on the GPU and into competition with the generation model;
- any generalist weight update (`25-` §3, Q13) — which is the expensive,
  irreversible option that note argues against on separate grounds.

**Both of the tempting "make it better" moves are the ones that consume the
accelerator.** The design that keeps the GPU free for the model that actually
reasons is: small local encoder, typed exact matching doing the discriminative
work, conformance checking on CPU on the cold path. The compute argument and
the architecture argument point the same way, which is the sort of coincidence
worth pointing out in a report.

## 5. What is not known, and should be asked

None of this can be settled without a number nobody has stated. These belong on
the report's open-questions slide, and they are the kind a supervisor can
actually answer:

- **Q17 — What is the target machine?** RAM, VRAM, whether a GPU is assumed at
  all. Everything above is conditional on it.
- **Q18 — Is the generation model local or hosted?** If hosted, the local
  budget is almost entirely free and this whole section relaxes. If local, the
  encoder and the model are in direct competition and §4 becomes binding.
- **Q19 — What is the cold-path budget?** How much compute may be spent between
  runs on curation, conformance checking, and duplicate detection?
- **Q20 — What is the retention policy for observability?** Invocation history
  is what feeds the quality ladder and is the only store that grows with use.
  Unbounded retention is not an option over a week-long run.
- **Q21 — Is a larger local encoder worth its footprint?** Alita-G's Table 5
  quantifies the accuracy at stake (up to 12 points) but on hardware unlike
  ours, and only as a *single-stage* selector. Under the staged design in
  `23-` §4 the marginal value of a bigger encoder is much lower — it only
  reorders an already-admissible set. **This is a measurable question and a
  good candidate for a small experiment.**

## 6. One paragraph for the report

> Alita-G's results rest on a hosted 3072-dimensional embedding model, and its
> own ablation shows twelve accuracy points separating that from open-source
> encoders. This project runs `all-MiniLM-L6-v2` locally, against a persistent
> Chroma store — smaller than anything in that ablation. On this hardware,
> similarity is the weakest signal available, which is precisely why the
> discriminative work belongs in exact contract matching over declared types
> and effects, with embeddings only ranking what is already admissible. The
> expensive part of our design — conformance checking — runs once per
> capability at admission, on the cold path, rather than on every task. We are
> moving cost off the hot path and off the accelerator, and the local-first
> constraint is what makes that the right trade rather than merely a defensible
> one.
