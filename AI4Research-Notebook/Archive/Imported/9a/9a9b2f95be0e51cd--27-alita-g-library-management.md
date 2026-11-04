# 27 — Alita-G has no library management, and declines it on purpose

Written 2026-09-10 by the capability-capsule panel (pts/9).
All claims **[verified]** against `/home/muk/work/papers/2510.23601.txt`
(`pdftotext -layout` of arXiv 2510.23601). Line numbers are that file's.

The user asked directly: *"does it make provisions for library management? From
what I've seen it's just making MCPs, thresholding how good each one is using
very basic measurements (TC), then matching the m:n problem to MCP. No
retirement policy, promotion, modification, dedupe, adversarial review."*

**Confirmed, with one correction that makes the point stronger, and one detail
that makes it sharper.** This note exists so the finding is quotable from one
place — it is the strongest single piece of evidence for the report's
contribution claim.

---

## 1. The lexical evidence

Counts of case-insensitive occurrences across the **entire paper** (title page
to references):

| Term | Count | Where, if non-zero |
|---|---|---|
| `retire` | **0** | — |
| `deprecat` | **0** | — |
| `version` | **0** | — |
| `dedup` | **0** | — |
| `prune` | **0** | — |
| `evict` | **0** | — |
| `delete` | **0** | — |
| `remove` | **0** | — |
| `adversarial` | **0** | — |
| `quality score` | **0** | — |
| `replace` | 1 | line 249 — "Replace hard-coded values with configurable parameters", i.e. abstraction, not library replacement |
| `maintain` | 3 | line 262 — "each MCP maintains its original metadata" (preservation, the opposite of modification); lines 302, 545 unrelated |
| `lifecycle` | 1 | line 94 — **in related work**, describing AutoGenesisAgent [18] |
| `test` | 4 | all benchmark testing (lines 353, 395, 452, 541). **No occurrence refers to testing a generated tool** |

⚠ These are zero-hit claims and they age badly if the source changes. Re-run
before publishing:

```bash
cd /home/muk/work/papers
for t in retire deprecat version dedup prune evict delete remove adversarial; do
  echo "$t : $(grep -c -i -- "$t" 2510.23601.txt)"
done
```

**The `lifecycle` hit is the sharpest detail in this note.** The one place the
concept appears is Alita-G's own related-work section, crediting
AutoGenesisAgent with "self-generating capabilities with **lifecycle management**
for multi-agent systems." The concept is present in their literature review and
absent from their system.

## 2. It is a deliberate refusal, not an omission

This is the part that upgrades the finding from "they didn't get to it" to a
design position the report can engage with.

§3.3, verbatim (lines 256-257):

> *"Unlike traditional clustering approaches, our method **preserves the
> diversity of MCP implementations** to maximize coverage of potential task
> variations."*

And Eq. 7 (lines 259-260):

> `B = {MCP_m | m ∈ [M]}`, where `M = |L|`

`L` is the raw pool. `M = |L|` means the Box is modelled as one-to-one with the
abstracted pool — **Eq. 7 specifies no filter**.

⚠ **Narrowed 2026-09-11.** This previously read "There is no filtering step
after abstraction at all." That overstates what is checkable. The prose names a
filtering step **twice** — line 471, *"followed by filtering and abstraction to
construct the accumulated MCP Box"*, and Table 4's caption, *"curated MCPs in the
MCP Box after filtering and abstraction"* — and one pass over the 165-question
validation set yields only 26 MCPs, which an unfiltered pool would not explain.
The defensible claim is **"no filter is specified"**: named twice, defined
nowhere, and with no per-tool quality criterion either way. `grep -i filter` on
the PDF surfaces those two lines immediately, so a supervisor will find them.

So Alita-G considered consolidating near-duplicates, named the standard
technique for it, and **explicitly chose the opposite**, with a stated rationale:
coverage over compactness. That is a defensible engineering call for a fixed
benchmark suite. It is not one that survives a library that grows for a week.

## 3. The correction — there is no per-MCP quality measure at all

⚠ **The brief says "thresholding how good each one is using very basic
measurements (TC)". There is no per-MCP measurement, not even tool correctness.**

The sole filter is Eq. 5 (line 233):

> `L = { MCP_i,j^(k) | π_master(x_i) = y_i, i ∈ [N], j ∈ [J_k,i], k ∈ [K] }`

The predicate is `π_master(x_i) = y_i` — *did the task produce the right final
answer*. It is **binary, and it ranges over tasks, not tools**. The index `j`
runs over every MCP generated during that task's execution, and all of them are
admitted on the strength of the task's outcome.

Concretely: if a trajectory generates five MCPs and the final answer is correct,
**all five are kept — including any that were never called, called and failed,
or actively unhelpful.** No attribution, no per-tool signal, no threshold.

This makes the user's point stronger than they put it. The gap is not "their
quality measure is basic". It is that **there is no quality measure, and the
proxy they use cannot distinguish a tool that worked from a tool that was
merely present.**

## 4. They built the dedupe test and used it only as a thermometer

§5.2 (lines 470-479) constructs, for the scalability analysis:

> embed each MCP by concatenating description and use-case, ℓ2-normalise, build
> an undirected graph with edges between pairs at cosine similarity ≥ τ = 0.7,
> and count connected components.

**That is a deduplication procedure.** Components of a ≥0.7-similarity graph are
exactly the near-duplicate families a dedupe pass would collapse. Alita-G runs
it, reports the numbers (26 → 128 MCPs against 26 → 65 clusters; effective
coverage 1.00 → 0.51), and uses the result **purely as a diagnostic** to explain
why accuracy plateaus after k=3.

Their own words (lines 529-532): later iterations "predominantly introduce
near-duplicates or narrow variants of existing capabilities", and k=3 "offers a
favorable balance ... while avoiding the redundancy that characterizes further
expansions."

**The mitigation for redundancy is to stop generating.** The measurement exists,
is validated, and is never connected to admission or retirement.

For the report this is the cleanest possible statement of the gap:

> Alita-G can measure its own library's redundancy and chooses not to act on it.
> Its remedy for capability-library rot is to stop growing the library.

## 5. What this licenses the report to claim

Five items, each citable, none requiring a value judgement about Alita-G:

1. **No retirement, promotion, versioning, in-place modification, dedupe,
   adversarial review, or per-tool testing.** *(§1 counts)*
2. **Non-consolidation is a stated design choice**, with coverage as the
   rationale. *(§3.3, lines 256-257)*
3. **The admission predicate is task-level and binary**, so tool quality is
   never assessed. *(Eq. 5)*
4. **The redundancy metric exists and is unwired.** *(§5.2)*
5. **Their remedy for library rot is to stop generating at k=3.** *(§5.2
   conclusion)*

Together these define exactly the surface note `19-`'s lifecycle state machine
and note `17-` §4.3's rejection reasons occupy. The contribution is not "we
thought of library management" — **it is that the closest prior system reached
the point where library management becomes necessary, measured the need, and
stopped.**

## 6. Fairness note — do not overstate this

Two things to keep attached whenever §§1-5 are used, so the report reads as
literate rather than point-scoring:

- **For its setting the choice is reasonable.** A fixed benchmark suite,
  evaluated once, does not need retirement. The absence of lifecycle machinery
  is proportionate to the problem Alita-G set itself, and the paper is candid
  about the plateau rather than hiding it.
- **Their results are strong and stand.** 83.03% pass@1 / 89.09% pass@3 on GAIA
  validation at ~15% fewer mean tokens (Table 1). The critique is about what the
  architecture does not attempt, not about whether it works.

The correct posture: *Alita-G proves the loop is worth building. It also shows
precisely where the loop stops scaling. We are proposing to keep going.*

---

## Cross-references

- `21-` — the full close read; §5 there is now backed by this note.
- `19-` — the lifecycle state machine this gap argues for.
- `17-` §4.3 — the rejection reasons, incl. `DUPLICATE_CAPABILITY`.
- `23-` §4 — the quality ladder Alita-G has no equivalent of.
- `25-` — why retirement matters more over long horizons than short ones.
