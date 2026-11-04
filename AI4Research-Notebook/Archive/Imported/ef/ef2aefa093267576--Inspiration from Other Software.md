**Muk's rule: a shipped product outranks a paper, and the framing is "inspiration from other software" —
which is a good look at Huawei. Second rule, 2026-09-23: spread the references across the whole
presentation; do not condense the corporate connection into one slide.**

Nearly every hard decision in this design has already been made by a company shipping at scale. Each
reference belongs **where the decision is made**, not bunched at the end.

## Citation rules

- **One row, one question.** No two rows cited for the same point — a reader should be able to delete any
  row and lose exactly one answer.
- **The biggest company that actually ships the mechanism.** Do not stack six vendors behind one idea.
- Cite each only for what it demonstrably does. A company may recur across unrelated products.

## The map

✅ verified in source during the 2026-09-23 session · ⚠️ candidate anchor, **verify before it ships**

| Where it is used | Company | The one question it answers | |
|---|---|---|---|
| (b) Structure: one schema, optional parts, added to over time | **Google** — Protocol Buffers | *How does one schema survive fields being added for years?* Optional by default, reserved fields, old readers keep working | ⚠️ |
| Declared vs observed | **Google** — Kubernetes `spec` vs `status` | *Where does what you declare live, versus what is observed of it?* Two sections of one object, written by different parties — our Declaration versus Verdict and Standing | ⚠️ |
| Admission: nothing runs unadmitted | **Google** — Kubernetes admission control | *Can a declarative check run before anything is allowed to exist?* | ⚠️ |
| Declared effects and permissions | **Apple** — App Store entitlements and privacy labels | *Can a component be made to declare what it touches before anyone installs it?* | ⚠️ |
| Admission gate with a human route | **Apple** — App Review | *Does a gate with static checks plus a human route work at scale?* | ⚠️ |
| Progressive activation (M1–M5) | **Meta** — Gatekeeper feature gating | *Can a system ship with parts inert and be switched on progressively?* | ⚠️ |
| Judges calibrated by spot checks | **Amazon** — Mechanical Turk gold-standard questions | *How do you trust a judge you cannot fully verify?* | ⚠️ |
| Merge: keep both forms | **Google** — BigQuery materialized-view recommender | *When a pattern recurs, do you replace the parts or keep both?* **Keep both** — the base table stays and the optimiser redirects | ✅ |
| Merge: who approves | **Microsoft** — Power Automate Process Mining | *Who decides a merge is worth making?* The system marks the opportunity; a person acts | ✅ |
| Merge: which pairs may merge | **NVIDIA** — TensorRT layer fusion | *May any adjacent pair be merged?* **No** — a published catalogue of admissible fusions, checked before fusing | ✅ |
| A block with its own graph | **Amazon** — Step Functions nested workflows | *How is a block containing its own graph handled?* As one unit, with monotone integer versions | ✅ |
| Pinned internals, A′ handling | **Google** — Bazel | *How do you stop a merged block drifting?* Pin inputs by content-addressable checksum; reuse only on exact match; rebuild on demand | ✅ |

**Do not overclaim TensorRT**: cite layer fusion for the *pattern* (a catalogue of admissible fusions,
not every adjacent pair). The sources do not show numerical verification of fused kernels.

**A reference that turns out not to work the way claimed is worse than no reference** — drop it rather
than soften it.

## Where research is still cited

Second, and only where industry does not cover it: **AllocBench** (2607.23332) for *why* the proposer
must not be the builder, and **Cordis** (2608.25512) for composability's boundary. See [[Evidence]].

Related: [[Overlap and Merge]], [[Versioning and A-prime]], [[Quality Not Just Correctness]].

---

## Second pass, 2026-09-23: three agents, non-AI software only

Full map and sourcing: `capsule-openjiuwen/kb/materials/inspiration.md`.

**Verified anchors replaced the weak ones.** Out: Apple App Review and entitlements (Apple's pages do
not say whether review is human), Meta Gatekeeper, Amazon Mechanical Turk. In: Chrome extension manifest
permissions, Kubernetes admission control and `spec`/`status`, Chrome Web Store hybrid review, OCI
digests, Protocol Buffers, PyPI/npm/crates.io immutability, Amazon Redshift AutoMV, Akamai
cache-on-second-hit, Oracle query rewrite and SQL Plan Management, Intel macro-op fusion, Microsoft
Azure SQL auto-tuning, Bazel, AWS Step Functions.

**Five findings changed the design, not just its citations:**

1. **Uninstall means drained, not gone.** No runtime promises unloading happens -- POSIX `dlclose`,
   musl, Java §12.7, .NET cooperative unload, OSGi pending-removal wirings, Erlang purging by killing
   processes, Linux taint on forced unload. M5's promise was rewritten to match, and
   [[Quality Not Just Correctness]] and the M5 figure follow Kubernetes' drain-then-force shape.
2. **Block a regression, label a capsule with no better replacement.** The loose "label for quality" is
   the minority position (SRE error budgets, AWS alarm rollback, Kayenta). But all of those block a *new
   change* while a known-good version keeps serving, and **Envoy's panic threshold** shows the other
   side: with too few healthy hosts it disregards health status entirely, because over-excluding is
   worse. Kubernetes readiness versus liveness gives the deprecate/revoke split.
3. **A failing judge is removed, not labelled.** Crowdsourcing removes a worker below the accuracy
   threshold on hidden test questions and discards their judgments. The labelling rule stops at the
   judge.
4. **Nothing is retired *by merging*** -- but a block is an ordinary member afterwards. Redshift drops
   unused automated views and Azure SQL drops unhelpful indexes, so "all three coexist forever" was too
   strong.
5. **Required-ness lives in the gate.** Protocol Buffers removed `required` on purpose. The schema marks
   nothing required; the `policy_epoch` decides, versioned and relaxable.

**Corrected claim:** a minimum observation count before a *quality claim* is standard (Envoy's
`success_rate_request_volume`, SonarQube's 20-line floor, Kayenta's no-data class). The departure is a
minimum before *merging*. An earlier draft of the deck said there was no precedent at all, which was
wrong.

**No precedent found for "build up, never split"** -- LLVM splits hot from cold, Oracle dissolves views
by inlining. It is presented as [[Overlap and Merge]]'s design choice, defended as one.

**Still unverified, must not ship:** Appen's thresholds (404 pages), the OSGi classloader-leak reading,
Kubernetes pod-shutdown ordering, Optimizely's mSPRT.

## Links embedded in the deck, and how they are checked

The decks carry clickable links from a checked registry: `LINKS` in `merged/build_deck_v6.py` (the post
deck) and in `merged/layer2/build_deck_l2.py` (layer 2, which adds the post deck's entries). Each entry records the
URL, the page title that actually loaded, and the sentence confirmed on it. The build post-processes the `.pptx`
so any run carrying the marker `↗ ` becomes a real hyperlink. Since 2026-09-25 tundlekit does the same step
(`tundlekit deck links DECK.pptx --links links.json`), and it fails on any marked text with no checked entry.

**Every URL was fetched and read before it went on a slide**, and what the page *actually resolves to* is
recorded beside it, not what the URL suggests. Two did not land where the URL implies:

- `man7.org/.../dlclose.3.html` lands on the **dlopen(3)** manual page. The claim is there, so the link
  text says dlopen(3).
- `kubernetes.io/.../admission-controllers/` is titled **"Admission Control in Kubernetes"**.

Nothing goes on a slide unless the quoted claim was found on the page that actually loads. **Re-check the
whole registry before any future workshop** -- vendor documentation moves, and a dead or changed link on
screen is worse than no link.
