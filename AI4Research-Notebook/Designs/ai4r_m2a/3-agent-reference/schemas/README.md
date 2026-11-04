---
id: ai4r-m2a-3-agent-reference-schemas-readme
status: proposed-runtime-unverified
source: ai4r_m2a/3-agent-reference/source-manifest.json
last_reviewed: 2026-10-30
next_action: Implement against the acceptance matrix and attach measured evidence
---
# Draft schema boundary

[Agent entrypoint](../README.md)

Schema namespace: `https://ai4r.local/schemas/m2a/`, version `2.0.0-m2a.2`, JSON Schema 2020-12. These identifiers are names, not network dependencies. Local validation registers all schema files. Unknown fields are rejected where objects are closed; explicit context/result payload objects allow domain-specific content.

| Schema | Meaning |
|---|---|
| [package](package.schema.json) | Category release containing multiple declared capability IDs, shared checks/providers and ceilings |
| [capability](capability.schema.json) | Callable member: input/output contracts, effects, check obligations and entrypoint |
| [call](call.schema.json) | Immutable dispatch binding, exact refs, authorization, limits and required check IDs |
| [receipt](receipt.schema.json) | Observed outcome, output refs, required check results, effects and actual usage |
| [artifact manifest](artifact-manifest.schema.json) | Durable delivery with outputs, receipts, project outcome and reproduction level |
| [research contract](research-contract.schema.json) | Versioned question, constraints, deliverables, scientific obligations and escalation policy |
| [check definition](check-definition.schema.json) | Executable check, evidence scope, owner and qualification fixtures |

Schema validation is necessary but insufficient. Cross-record checks require: package membership and effect subsets; immutable digest/file verification; actual input schema and semantic validation; current admission and environment scope; check results matching the prebound obligation set; no accepted receipt unless terminal and every required check passed; provider scope and budget enforcement; manifest/receipt/output integrity; delivery completeness against the project contract. These are runtime invariants, tested under the relevant M2A obligations.

Check IDs resolve to executable definitions in the release or independently protected policy bundle, including stage, applicability rule, evidence requirements and checker digest. Required check lists are fixed before dispatch. All arrays representing identities must be unique; cross-record ID resolution is mandatory. Payload schemas are domain-owned versioned contracts, not arbitrary agent-generated definitions accepted at call time.

Examples intentionally include synthetic digests. Production acceptance requires actual content-addressed bytes and independently trusted qualification; a syntactically valid digest does not prove either.

## Draft .2 additions

[Quality assessment schema](quality-assessment.schema.json) binds scoped trust to release/image/environment, policy, attributed evidence, sample sufficiency and freshness. Package fields now require OCI image-by-digest, dependency lock, resource ownership, history key, quality-policy reference and protected evolution permissions. Runtime must independently recompute policy satisfaction from authenticated evidence; supplied Boolean flags and digest-shaped strings are never authority. A qualified assessment with insufficient samples or stale evidence is invalid. Verify assessment expiry at dispatch, not just at serialization.

The new fields intentionally change the unimplemented draft interface from .1 to .2; preserve an explicit adapter if any experimental caller already uses .1. Synthetic fixtures do not constitute real admission or a default quality threshold.
