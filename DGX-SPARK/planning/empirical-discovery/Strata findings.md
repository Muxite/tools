---
id: inference-factory-strata-findings-20261109
status: source-study-plus-bounded-cpu-evidence
source: research/inference-factory-20261104/Strata at ffa80d73133ea5c548aefe57889a16e8085a938f; research/lab-manager-reuse-20261109/strata-study/source-receipts.json; Sources/Prompts/2026-11-09-continue-strata-research.txt
last_reviewed: 2026-11-09
next_action: Choose discriminating experiments with the active campaign; promote CC/component/Manager needs only with explicit evidence
---

# Strata findings that can reveal useful capabilities

Continue from [[Designs/Inference Factory - Empirical Discovery/README|the current user focus]]. These findings are hypotheses about reusable boundaries, not a required list of packages.

## Actual evidence from this continuation

**23 upstream CPU-only tests passed:** profile generation (7), workload mixing (2), cache-policy simulation (14). A separate state-gate suite was blocked at import by missing `jinja2`; its unittest loader error is not an executed model test. Two small probes demonstrated incomplete-tail trace parsing and limited default identity-helper behavior. [Research status](../../../research/lab-manager-reuse-20261109/strata-study/evidence/research-status.json) and [raw test record](../../../research/lab-manager-reuse-20261109/strata-study/evidence/cpu-study.json).

No model, GPU, Nsight capture, real sandbox crash, or performance improvement was tested here. Source review and independently cross-checked upstream test intentions remain distinct from these CPU observations. The pinned source's tracked state remained unchanged during the 23-test study.

## High-value considerations

| Observation | Candidate capability or Manager implication |
|---|---|
| Default profile construction can preserve a complete base unchanged despite new traces; upstream tests verify the no-op. | Inspect actual artifact/path/config differences before crediting a candidate change. A successful command is insufficient. |
| Profile tools assume 48 layers; Granite has 24. | Geometry/format applicability checks before reusable wrapping or component integration. |
| Raw trace counts and normalized per-request/category weights rank different expert mixtures. | Reusable workload-design methodology with explicit weighting and evaluation split; do not silently optimize the longest trace. |
| Trace collector skips existing nonempty files; two readers accepted a seven-byte incomplete tail as empty data. | Captured/finalized/validated/durably registered are distinct. Partial traces must not silently become completed evidence. |
| Eviction simulator provides fill-only/LRU/LFU-decay/oracle, warm/cold and global/per-layer variants. | Cheap offline policy screen; oracle reads future data, and hit-rate gains still need real overhead/latency/quality validation. |
| Tuning code records candidate diffs, bounds and semantic classes. | Borrow compatibility/methodology patterns, not hardware-specific thresholds or a mandatory single-knob search strategy. |
| Default history identity helper lacks GPU/driver fields, uses sampled model identity, and its reason helper accepts two empty keys. | Complete required-field validation and target environment capture remain ours. Same-build-history comparability is different from a deliberately changed engine A/B comparison. |
| Native engine package verification hashes all payloads only with `full=True`; session fingerprints can be sampled. | Record verification scope; separate artifact integrity, session compatibility and actually loaded configuration. |
| Expert exchange class requires external reader/transfer completion before atomic slot publication. | Component CC needs integration/lifetime/synchronization instructions and tests along with code/binary. Host-array tests do not establish CUDA correctness. |
| Fatal engine output can invalidate a still-living process; restore may fail after partial state mutation. | Health/generation checks, no blind replay, distinguish invalid-before-write from transfer-failed state, and confirmed cleanup before retry. |
| Async save completion and exported-file existence differ; state includes recurrent/indexer/draft/PLE/KV families. | State/reset qualification and export-finalization methods must cover actual engine state, not just similar text output. |
| Atomic rename and JSONL history convenience helpers are not a complete durable transaction/ownership protocol. | Manager still owns durable acknowledgement, concurrent writes, loss accounting, stale ownership and result registration. |

Full source paths, findings, evidence levels and reusable upstream tests are in [the detailed study](../../../research/lab-manager-reuse-20261109/strata-study/README.md). [Experiment ideas](../../../research/lab-manager-reuse-20261109/strata-study/experiment-ideas.md) connect these to real inference experiments without forcing an architecture.

## What to reuse before writing more code

Prefer upstream profile/mixing/replay functions for appropriately qualified inputs; existing package/launch verification patterns; state/lifecycle regression fixtures; BuildKit/Bake for image production; Nsight maintained reports for saved-trace analysis. Keep thin adapters and explicit coverage. Do not turn every function into a CC, import an entire tuning/control platform, or claim a cached expert actually executed solely because it was routed.
