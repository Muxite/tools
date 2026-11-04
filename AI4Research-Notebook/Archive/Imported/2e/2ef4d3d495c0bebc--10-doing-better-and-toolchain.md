# 10 — "How to do better": capsule gap register + verified toolchain

Written 2026-09-10 by the **capability-capsule panel** (pts/9 session).

> **Filename ownership note.** This file exists at `10-` rather than as part of
> `07-` because `07-capability-capsules.md` is written by another concurrent
> panel and was overwritten mid-session. Four `claude` sessions were running
> against this directory simultaneously. Treat `07/08/09` as that panel's, and
> `10` as this one's. Do not merge them by overwriting — append.

This note deliberately **does not** restate `07` (capsule anatomy, trust
classes, admission gate, binding chain) or `09` (slide outline, guardrails).
It covers the two things those files don't: the **gap register** that powers the
"how to do better" half of the capsule deliverable, and the **document
toolchain** for producing the report and deck.

---

## Part A — Gap register

Nine observations, each traced to a command run against the checkout. These are
the substance of "how to do better." They are stated as findings, not
accusations — several are ordinary consequences of a fast-moving RC.

### A1. The design doc and the shipped schema are incompatible formats [verified]

`docs/CAPSULE_ARCHITECTURE.md` §2.1 specifies a capsule as:

```yaml
apiVersion: capsule/v1
kind: Capsule
metadata: {...}
interface: {input, output, errors}
permissions: {resources, denies}
guarantees: {timing, idempotency, side_effects, resource_bounds}
risks: {cost, ...}
verification: {...}
evolution: {...}
```

The shipped `harness/schemas/draft/capability-capsule.v1.draft.json` requires:

```
capability_capsule_id, capsule_kind, metadata, applicability, contract,
composition, effects, bindings, verification, operator_compatibility, provenance
```

Overlapping *intent*, incompatible *surface*. `interface`→`contract`,
`permissions`+`guarantees`+`risks`→`effects`, and `evolution` has no shipped
counterpart at all. Nothing in the tree reconciles the two, and the
architecture doc is not marked superseded.

**Do better:** either mark `CAPSULE_ARCHITECTURE.md` as historical design
rationale (like the README already does for its own pipeline section), or write
the mapping table. Right now a newcomer reading the flagship design doc will
author a capsule the loader rejects.

### A2. 74 capsules marked `stable` against a `draft` schema [verified]

`grep -o 'status: [a-z_]*' harness/config/capability-capsules.registry.yaml`
→ 74 `stable`, 6 `draft`. Every one of them has
`schema_ref: schemas/draft/capability-capsule.v1.draft.json`, and the governing
ADR is `Status: Draft`.

Instance stability is being asserted above contract stability. If the draft
schema changes, 74 "stable" capsules change meaning.

**Do better:** promote the schema to `v1` (non-draft) before, not after,
declaring instances stable — or introduce a `stable-against-draft` status so
the claim is honest.

### A3. The entire ecosystem layer is design-only [verified]

`CAPSULE_ECOSYSTEM_DESIGN.md` (1139 lines) specifies a 5-layer protocol stack
(`Spec → Execution → Composition → Trust → Discovery`), `capsule://ns/name@version`
URIs, JSON-RPC 2.0 invocation, a federation layer, trust scoring, and four
governance tiers (`Core → Verified → Community → Experimental`).

None of `capsule://`, JSON-RPC, federation, trust-score, `sys_capsules`,
`v_capsule_health`, `CapsuleProvider`, or `min_scare_score` appears **anywhere
in the repository outside the two design docs** — including tests
[verified by adversarial review, which specifically tried to falsify this and
could not]. Ed25519's only hits are the filename `id_ed25519` in secret-scan
allowlists; there is no signature implementation. What *does* exist is a local
registry + a composition module.

**Do better:** this is the single strongest "future work" section the report can
have — the design is genuinely ambitious and genuinely unbuilt. Present it as
roadmap, never as capability. Also note `CAPSULE_ARCHITECTURE.md` §9 still lists
"implement Capsule Registry / composition engine" as next steps, though both now
exist. The doc has exactly one commit, `aeca9f66f` on **2026-02-12**, and has
never been revised [verified]. (An earlier draft said 2026-02-03 — that date is
the `created:` field of the fictional example capsule inside the file.)

### A4. The token-optimization numbers are unmeasured [verified]

The claimed savings — spec lazy-loading **94%**, index compression **75%** —
appear only in `CAPSULE_ECOSYSTEM_DESIGN.md` — 94% at lines 404, 505, 1120;
75% at line **1121 only**, in the closing summary, with no derivation in §2.2
where index compression is actually specified — and nowhere else in the repo. `benchmarks/` contains exactly one file,
`mlx_quantization_bench.py`, unrelated.

**Do better:** these are design-doc estimates. Either measure them (they are
cheap to measure — count tokens of a dehydrated vs. full registry index) or
present them as targets. A report that quotes "94% token savings" as an
achieved result is the most likely single source of an embarrassing question.

### A5. `cap.research-knowledge-query` does not exist [verified]

`autosci-workflow-map.md` maps the wiki-question-answering stage (`/ask`) to
`cap.research-knowledge-query`, "support-only". That id appears in exactly three
files, all under `docs/integrations/autosci/`. It is not in the registry and has
no manifest.

**Do better:** the stage-mapping table has drifted from the registry. A
registry-vs-map consistency check is a ~20-line script and would be a concrete,
creditable improvement to propose.

### A6. Two parallel capsule directories, no documented rule [verified]

- `harness/capability-capsules/` — 39 manifests (research/scientific lifecycle)
- `harness/config/capability-capsules/` — 46 manifests (adapters, requirement
  compiler, external/PoC research variants)

The registry's `manifest_path` resolves both. No doc states which directory a
new capsule belongs in.

**Do better:** trivial to fix, easy to justify, and a good example of the
"conventions should be enforced, not remembered" argument that the capsule
concept itself makes.

### A7. The deprecated alias has no removal deadline [verified]

The ADR (2026-05-24) accepts `execution_capsule_id` "for one migration cycle at
the loader boundary only," and `execution-capsule.v1.draft.json` is literally
titled *"Solar Execution Capsule v1 (Deprecated Alias)"*. Still present.
No date, no ticket, no cycle definition.

**Do better:** "one migration cycle" is unmeasurable. Deprecations need a
version number to expire at.

### A8. No AutoSci route ever reached `full` coverage [verified against the
2026-07-02 entry in `unification-status.md`; re-check before publishing]

28 routes: 17 `partial`, 11 `gated`, 0 `full`. Gated:
`/daily-arxiv /edit /exp-pilot-run /exp-run /paper-compile /poster /prefill
/refine /reset /setup /visualize`. The status log records "No route was promoted
to `full`."

**Do better:** pick *one* route and drive it to `full` as a demonstration. A
single fully-accepted route is worth more, rhetorically and technically, than 17
partial ones.

### A9. ~~Capability scoring exists but is structurally silent~~ — SUPERSEDED

This item was **wrong twice over**, and the second error was found only by
adversarial review:

1. `capability-scorer.sh` and `harness/needs-improvement.md` do not report on
   capsules — correct.
2. But they do **not** report on `plugin_capabilities` either.
   `capability-scorer.sh` contains zero references to `plugin_capabilities`,
   `state.db`, or `sqlite` [verified]; it scrapes capability names out of sprint
   `eval.md` files into `capability-graph.jsonl`. It is a **third** system.

The correct finding is stronger: capsules have **no quality feedback loop at
all** — no scorecard, no health status, no promotion/demotion path. See
`13-capsule-roadmap-and-open-questions.md` R6 for the verified version.

## Part B — Report/presentation toolchain

Installed and verified this session. Every command below was run end-to-end on
Chinese sample text taken from `CAPSULE_ARCHITECTURE.md`, with CJK glyphs
confirmed present in the output via `pdftotext`. This matters: both flagship
capsule docs are in Chinese.

**Installed:** `pandoc` 3.1.3 (apt), `@marp-team/marp-cli` 4.5.1 (global npm),
`texlive-xetex`, `texlive-lang-chinese`.
**Already present:** `pdflatex`, `lualatex`, `weasyprint`, `libreoffice`,
`google-chrome` (marp's export backend), 38 Noto CJK fonts, `pdftotext`.

### Reports — pandoc

```bash
pandoc report.md -o report.docx                          # Word, CJK verified
pandoc report.md -o report.pptx                          # plain outline deck
pandoc report.md -o report.pdf --pdf-engine=weasyprint   # CSS-styled, fast
pandoc report.md -o report.pdf --pdf-engine=xelatex \
       -V CJKmainfont="Noto Serif CJK SC"                # typeset, best for CJK
```

`--pdf-engine=lualatex` is **broken on this machine** (luaotfload font-database
error, fails at `\familydefault`). Use `xelatex` or `weasyprint`.
`xelatex` requires `-V CJKmainfont=...`; without `texlive-lang-chinese` it dies
with `! Emergency stop` at `\setCJKmainfont`.

### Slides — marp

```bash
marp deck.md -o deck.html    </dev/null
marp deck.md --pdf  -o deck.pdf   </dev/null
marp deck.md --pptx -o deck.pptx  </dev/null
```

**The `</dev/null` is mandatory.** Without it marp blocks forever on
`Reading stdin stream...` and never exits — it cost a 300-second timeout before
being diagnosed. Front-matter must include `marp: true`.

A harmless `ERR_MODULE_NOT_FOUND` appears under `DEBUG='marp-cli*'` while marp
resolves its default engine; it falls back correctly and the output is fine.

### Choosing an output

| Need | Use |
|---|---|
| Report colleagues will edit | `pandoc -o .docx` |
| Report as polished PDF with Chinese | `pandoc --pdf-engine=xelatex` |
| Presentation authored as Markdown | `marp` — much better-looking slides |
| Presentation as editable PowerPoint | `marp --pptx`; `pandoc -o .pptx` for a plain outline |

Mermaid diagrams (used in `08-workflow-end-to-end.md`) do **not** render in
pandoc or marp by default. Options: pre-render with `mmdc`
(`npm i -g @mermaid-js/mermaid-cli`) to SVG and include the image, or paste the
diagram into a marp HTML slide with the mermaid script. Not yet installed.
