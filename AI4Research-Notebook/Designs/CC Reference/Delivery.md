---
id: m1-cc-delivery-reference
status: historical-source-reference
source: AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/capsules/delivery.py; research/checks/research.py
last_reviewed: 2026-10-23
next_action: Use Current Baseline for later source status; re-review affected role bytes before applying this historical contract
---
# Delivery

**Historical source scope:** this page describes the `98bd9d9` implementation, compared only through `d3d7f56`. This review updates its freshness label and navigation, not the underlying source audit. Use [[Resources/Current Baseline]] for later inspected source and candidate identities; the details below are not a complete reference for `809351f8` or the separate Builder candidate.

`research.delivery` drafts one nine-section Markdown report and a typed delivery manifest from accepted evidence. It must preserve source metric values, criteria and evaluation classifications exactly, copy uncertainty and risk notes, expose unavailable values as null/unavailable, and bind exact evidence refs. Host derives the report artifact ref after receiving the report, then inserts it in the manifest. Delivery does not publish or execute follow-ups.

**Inputs and outputs.** It receives the accepted Brief, candidate set, Screening/opportunity, blueprint, manifest/bundle, benchmark payload/receipt, verdict, gates, raw evidence and run config. Run configuration is filtered from the model payload while refs are retained. Outputs are `research_report` and `delivery_manifest`.

**Model and checks.** One text model call; no tools/network. Host checks report shape and required nine ordered sections/tables, exact values and rule text, verdict/blocker copying, safe relative file paths, role/audience and exact accepted evidence references. The report is prose, so independent scoring checks factual fidelity and completeness beyond structure.

**Failure classes.** Missing report/manifest, absent unique report role, malformed schema, unbound or wrong evidence ref, changed value/classification, omitted limitation, invented evidence, or operational model failure must remain distinct. A correct report blocked by format gate is false rejection; a polished report that changes a scientific FAIL into PASS is false acceptance if it advances.

**Study score.** Use a frozen source matrix with required facts, citations/ref identities, exact metric and verdict values, missingness and risks. Score exactness and critical errors separately from readability. Include negative science cases: `FAIL` and `INCONCLUSIVE` must still be delivered faithfully.

**Evidence.** [[Designs/CC Reference/Source Map]] links the carrier, delivery/stage checks, and focused test files. No publication or user study occurred.
