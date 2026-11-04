---
id: one-cc-factory-overview
status: proposed-runtime-unverified
source: Sources/Prompts/2026-11-03-one-cc-implementation.txt
last_reviewed: 2026-11-03
next_action: Replay the shared contract checks and qualify the inspector and benchmark carriers on one Spark
---
# CC and Software Factory

**Read the human brief first.** It asks the factory to reduce the serving footprint of pinned Strata IQ3_S on a Spark. It supplies two different attachments. `available_ccs` identifies software the builder may use. `requested_ccs` describes behavior the researcher would like the builder to deliver. The same package can occupy either role on different jobs. [Worked factory brief](../shared/examples/brief.json)

| Record | Read it for | Owner |
|---|---|---|
| [Available release](../shared/examples/cc-qualified.json) | A package with inspect and measure operations, carrier bindings, effects, check IDs and qualification. | CC Factory authors a candidate. Independent admission activates a specific release. |
| [Requested reader](../shared/examples/cc-draft.json) | Required and suggested port declarations, open prerequisite and guarantee questions. | Requester sets obligations. The builder resolves unknowns or returns a blocking question. |
| [Product](../shared/examples/product.json) | Reviewable source and build inputs. The example can deliver a modified engine with an empty list of reusable CCs. | Software Factory owns the repository change. Isolated CI owns the verified build record. |
| [Evaluation](../shared/examples/evaluation.json) | Baseline and candidate locks, workload and independently owned policy. | Central allocates a lab. JiuwenSwarm explores within scope. The independent evaluator scores the result. |

The example release is a design fixture. Its qualification and image references must be replaced with real independently verified artifacts before admission. The baseline Strata commit, model revision and shard pins derive from inspected upstream source. No fabricated artifact is a usable software release.

## The single CC contract

The original v2.10b guide assigns Muk ownership of the schema and describes what a capability takes, gives, needs, changes and guarantees. Retain those semantics and the separation between declaration and pinned implementation. M2a contributes package membership, trust and qualification scope. In the new model a package has one identity and version. Each member binds named ports, needs, effects, checks and a carrier. References carry the implementation bytes, test definitions and their provenance. A closed schema governs shape and the validator checks cross-record meaning. [Single CC schema](../shared/contracts/cc.schema.json) · [Compatibility and migration](../shared/Migration.md)

**Profile negotiation.** The shared brief includes actual model pins and an outcome-directed MoE profile. Resolve the namespaced profile schema by pinned bytes and verify the required reader. A missing required reader blocks work. Optional display metadata may be ignored only when execution and acceptance do not depend on it. Outcome mode leaves the tensor selector and algorithm open. An exact transformation supplies its required selector and parameters. [MoE profile](../shared/contracts/profiles/moe.schema.json)

**Build or pull.** The package can refer to an existing image or a source recipe. Freeze build context, base image, source, dependency lock, target platform and actual output digest. A session binds the operation to a specific resolved carrier. A Git change or image that modifies Strata is a factory product; expose selected behavior as a CC only when another harness can install and invoke it independently.

**Papers and projects.** Intake preserves source revision, license, method, fixtures and assumptions. Review native calls and failure modes, wrap the smallest useful operations, compare wrapper behavior with native behavior, then test installation and withdrawal. A paper without executable evidence can yield a draft declaration. The Software Factory operates at repository scope and may use these capsules to modify the packer, loader, kernels and packaging under the worked brief.

## What agents and reviewers can change

The qualification gate verifies carrier provenance and accessible public fixtures. An independent evaluator controls protected cases, check policy and thresholds. Builders and RSI can improve an implementation, create a source diff or capture a changed environment. Promote only after a reproducible rebuild and scoped qualification. An extended declaration that requests additional effects gets a new review. A released image does not establish scientific quality.

Read [the live catalog method](Discovery%20and%20installation.md), then run `python -B shared/validate.py` from the attachment root with Python, jsonschema and referencing installed. Use the separate Strata Research Lab attachment to test source materialization and recovery. Both attachments include byte-identical worked contracts.
