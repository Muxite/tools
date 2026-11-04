---
id: cc-interchange-family-02
status: proposed-runtime-unverified
source: Sources/Prompts/2026-11-03-cc-forms-and-profiles.txt
last_reviewed: 2026-11-03
next_action: Implement one request-to-source-change-to-qualified-product slice against the existing M2a calls
---
# CCs as a structured software engineering interchange

The request sent to the Software Factory describes the desired change, bounds and evidence, while leaving the builder free to choose an implementation. A candidate can deliver source or an image. A lab dispatch resolves either into an exact, verified runnable product. The MoE ontology is a versioned domain profile supported by the common CC envelope.

Read [the common schema](contracts/cc.schema.json), [the MoE profile](contracts/moe.profile.schema.json), [a request](examples/change-request.json), [a source-change candidate](examples/implementation-patch.json), then [the evaluation](examples/evaluation.json). Run `python validate.py` with Python, jsonschema and referencing installed. Every fixture artifact, candidate commit/tree and numerical threshold is illustrative. The baseline Strata Git commit was inspected. No request in this package is dispatchable.

## One family with explicit forms

| Form | Required meaning | Who consumes it |
|---|---|---|
| change-request | Pinned subject, objectives, measurable goals, constraints, editable scope, protected assets, interfaces to preserve, target profiles, inputs, evidence policy, output expectations, budgets and open questions | A Software Builder validates the request, reports blocking questions and selects its own plan and tools. An image field is unnecessary. |
| implementation | Relation to the exact request, source snapshot, one or more source/image deliveries, build recipe/toolchain, dependencies, builder checks, migrations, limitations and provenance | A materializer obtains the source or image, verifies identity and produces a qualified product lock. A reviewer can inspect the actual source change. |
| evaluation | Exact request, baseline/candidate references, actual workload and request tape, target, frozen gates and evidence policy | Central resolves the product, authorizes a run and delegates its investigation to JiuwenSwarm. Independent checks determine what the evidence establishes. |
| capability-bundle | Digest reference to the existing template and its qualification evidence | Existing admitted operations and typed tools remain available to agents. The new envelope does not redefine their legacy semantics. |

All forms share schema version, logical identity/revision/issuer, purpose, discovery tags, digest-bound relations and profiles. The document's content digest identifies the exact published revision. Publication identity and authorization come from a signed artifact or authenticated policy service, independently of the self-reported issuer string. Permissions, attempt IDs, mutable status and results remain in call/lease/receipt records. IDs and relations form an indexable graph. PostgreSQL and content-addressed JSON artifacts suffice for the pilot.

A request may have many implementations and each implementation many evaluations. A builder can ask a question, test a hypothesis, abandon a branch or issue a better candidate while the research objective persists. Consume actual receipts to reconstruct work. Neither publication order nor a relation such as `implements` requires automatic execution.

## A profile extends meaning without editing the base schema

Each `profiles[]` entry contains a stable profile ID, a schema locator plus content digest, a required/optional flag, required reader/tool IDs and the domain data. Core validation checks the envelope. Profile validation resolves an approved, local, hash-pinned schema and checks the data. Capability negotiation also checks that the selected consumer can interpret that profile. A missing executable transformation is a reason to propose a build task or report a gap; claiming to understand its JSON is insufficient.

For the MoE profile, data contains the model and native index references, logical target, requested intent, preserved invariants, reader policy and optional transform parameters. An outcome-directed request lets the builder investigate storage, loader, cache or kernel changes. A specified transformation additionally requires parameters. Domain contracts can be reusable across projects; a robotics profile can define scene, controller and simulator properties without introducing MoE fields into the base.

Unknown required profiles are refused before work is accepted. Unknown optional profiles may be preserved and ignored only if they carry descriptive metadata and no behavior, acceptance gate or execution dependency relies on them. The semantic validator rejects a change-intent that depends on an optional profile. Two profiles cannot silently disagree about an invariant or threshold. Resolve conflicts explicitly before building or evaluating.

Use a dedicated `profiles[].data` slot instead of blindly appending keys to a closed object. JSON Schema `allOf` validates a value against multiple schemas; it does not merge declarations or override an earlier `additionalProperties: false`. Trusted composed schemas can still validate profile data, and schema resources should resolve offline with bounded reference depth. [JSON Schema composition](https://json-schema.org/understanding-json-schema/reference/combining)

## Delivering source instead of an image

| Delivery | Required pins | Materializer and mismatch behavior |
|---|---|---|
| git-patch | Repository/base commit, patch bytes/hash, exact apply policy and expected result tree | Create a clean worktree at the base, verify hash and run `git apply --check --index`, apply with `git apply --index`, then compare `git write-tree` with the declared result tree. Refuse conflicts, path escapes, mismatched base or result; issue a new candidate after any rebase. |
| git-bundle | Bundle bytes/hash, base prerequisites, desired result commit and tree | Verify bundle and prerequisites, import into a candidate namespace, verify commit and tree, check out a private worktree. Missing prerequisite yields a structured missing-input result. |
| git-commit | Repository, immutable commit and expected tree | Fetch through the approved source mirror, verify the object and exact tree, then materialize the recorded dependency graph. A branch or PR URL is supplementary context. |
| oci-image | Exact image digest and platform | Verify image, provenance, native component and runtime compatibility. Preserve its source snapshot and recipe so accepted work remains reviewable and rebuildable. |

A Git tree covers tracked source and modes. External weights, Git LFS contents, submodule objects and dependency downloads require their own pinned manifests and access checks. This draft uses 40-hex Git object IDs matching the inspected Strata repository. A different object format requires a versioned contract update. A patch may need binary diffs and renames. Do not execute hooks or build recipes with host credentials. The isolated build environment handles untrusted source and dependencies under the existing reviewed-code pilot policy. [Git apply](https://git-scm.com/docs/git-apply) · [Git bundle](https://git-scm.com/docs/git-bundle)

Multiple deliveries in one candidate must resolve to the same source/product lineage. Shape validation cannot prove this; verify it during materialization using tree identities and build provenance. If a source candidate has no image, Central schedules an admitted builder on a compatible node, including an in-lab builder if that provider is explicitly qualified. It produces a new product-lock artifact, records its own receipt and only then permits measurement. Never silently change evaluation inputs when a build fails. Content-addressed caches can reuse an earlier verified build of identical inputs.

The main optimization is independent identity for source change, model pack and executable image. A source-only loader patch can reuse the baseline model pack; a model conversion can reuse the engine when the reader ABI permits it. New image references can reuse registry layers. Keep the CC small by referencing the patch or bundle as an immutable artifact, possibly carried in the same OCI artifact package. [OCI image and artifact manifest](https://github.com/opencontainers/image-spec/blob/v1.1.1/manifest.md)

## The responsibility split

| Owner | Chooses or enforces | Handoff |
|---|---|---|
| Research agent / feature owner | Objective, allowed scope, acceptance gates and protected evidence policy | Change-request CC; clarifications produce a new revision. |
| CC Factory | Form/profile validation, reference resolution, declared capability requirements and publication | Valid candidate record or precise missing-input/profile diagnosis. Publication grants no runtime permission. |
| Software Builder agent | Repository exploration, design, code edits, dependencies, tests and implementation approach within budget | Implementation CC plus source change and honest builder-check results. |
| Isolated build runner / CI | Recorded recipe, source identity, toolchain and output integrity | Verified image/package/model artifacts and provenance; source-only candidates get a materialization receipt. |
| Central Lab Manager / host worker | Admission, placements, effects, resource reservations, lease fencing, gateway and restore | Authorized call and bound product lock for one run/attempt. |
| JiuwenSwarm Lab Agent | Select useful diagnostics, explore behavior and revise a working plan within the assignment | Typed calls, actual observations and reproducible evidence. New code changes return to the builder or a separately admitted build call. |
| Independent checker / feature owner | Frozen evaluation and promotion | Verdict with evidence, followed by reviewed merge and accepted release when justified. |
| RSI | Propose improved factory recipes, build policies and tool selection from prior receipts | New change request or candidate recipe; it cannot lower protected gates to make a failure pass. |

The builder's preflight tests earn readiness for evaluation. They do not establish performance improvement. Report passed, failed, skipped and not-run distinctly. The lab compares real artifacts under matched inputs, records missing evidence and permits research failure without corrupting the build history. Branches and PRs remain the source collaboration layer.

## Gaps and first implementation

The old 0.1 template requires images and callable members. Keep it valid under its own schema and wrap it using `form=capability-bundle`. The 0.2 envelope is a new proposal with a new ID. Before migrating a caller, map its existing package, checks, effect ceiling, call admission and receipt ownership explicitly; adding an envelope cannot replace those enforcement rules.

The new schemas cover declaration shape. The included semantic validator checks profile support, schema byte identity, goal/gate references, required profile use, implementation lineage links and unweakened evaluation gates. It cannot verify source applicability, signatures, real product availability, scientific criteria, cross-profile logical contradictions or actual code quality. These checks need their named owners above.

First implement one request with broad Strata edit scope and an agreed protected test. Have the builder return a real patch plus exact tree. Materialize it in a clean builder, reject a wrong-base case, build from recorded inputs, then ask the JiuwenSwarm lab session to qualify baseline A/A and candidate A/B. Return the negative or positive outcome through the existing call/receipt path. This proves communication and source delivery before adding more profile types. A fixture-valid message with unresolved questions that block lab dispatch stays pending until the owner answers and republishes it.

