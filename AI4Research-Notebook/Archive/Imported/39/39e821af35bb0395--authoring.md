# Authoring and publishing a capability capsule

## Lifecycle

1. **Declare.** State purpose, kind, typed ports, preconditions, dependencies, effects, guarantees, candidate checks, and applicable limits. Keep objectives, node IDs, permissions, verifier assignment, and run policy outside. Declared checks document claims and proposals; they are not the mandatory runtime check bundle.
2. **Choose form.** A leaf points to implementation by locator and hash. A composite pins members and describes its internal graph and wiring. Do not promise unsupported fusion.
3. **Build.** Keep code separate and pin covered files. Preserve the declaration's meaning. A node objective binds one or more admitted CCs under a separate Node Execution Contract; subordinate calls keep their own identity, authority and evidence. A CC assesses; the gate decides and releases.
4. **Verify.** Run applicable tests and characterization checks; retain outputs, check results, and evidence references against the exact declaration and implementation hashes. A passing self-test alone is not admission or approval of mandatory checks.
5. **Associate mandatory checks.** An independent check maintainer authors and versions a deterministic check bundle, records its supported capsule-version compatibility, and associates an exact bundle version with the capsule version. The capsule author cannot approve or change this bundle. Runtime contract and policy checks are added separately by the protected binder.
6. **Admit.** In M1, the existing catalog is default-admitted and usable versions receive the minimal shared trusted host-check association; this bootstrap is not a governed admission decision or a claim of capsule-specific correctness. Once governed admission is available, new and changed versions require its successful review of capsule identity, dependency closure, permissions, and the pinned check bundle. Existing bootstrap-admitted versions are not bulk re-admitted. Unsupported obligations block binding.
7. **Publish and activate.** Store immutable capsule and check-bundle versions and their association. A human-controlled pointer selects eligible capsule/check pairs for future plans. RSI candidates remain inactive until their required admission and human activation. Existing runs retain their pins; reversion changes future selection only.

## Authoring rules

Prefer wrapping a working JiuwenSwarm/OpenJiuwen capability. Keep the summary task-independent. Declare effects and repeat safety; prose grants no permission. Type and check outputs. A composite pins members by hash and exposes only a boundary it can guarantee.

The companion description and schema disagree on requiredness, shapes, and enums. Use [the declaration inventory](declaration.md); Spec Kit must reconcile and version the format before implementation. Do not invent keys.

Protected configuration or the frozen graph assigns runtime criteria. Keep verifiers, gates, check bundles/runners, hidden fixtures, and their behavioral dependency closure outside RSI mutation. Capsule-associated checks do not grant release authority; only the protected gate releases work.

## Change rules

Preserve each version's meaning. Changes to ports, guarantees, effects, implementation, or check compatibility require a new explicit version/association and the applicable admission path. A check-bundle change creates a new bundle version and association; it never silently updates a capsule version or active run. Record lineage where supported. Library changes apply to future freezes; active runs keep pinned versions and checks.
