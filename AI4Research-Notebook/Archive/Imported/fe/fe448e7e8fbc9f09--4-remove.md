# Remove: capabilities are easier to remove because of spatiotemporal composability

**Stated plainly first, because it is the part most likely to be challenged.** Composability lets a
capability be installed and uninstalled while the system runs, and lets dependents be notified when one
goes away. It is **not foolproof, and it is not full reversibility.** Registrations come back out;
emissions already sent do not, external state is not rolled back, and a context poisoned by a bad tool
stays poisoned. This is the last milestone, not the first.

The mechanism itself already exists in agent-core: `apply_extension_hot` and `unapply_extension_hot`
bind and unbind tools, MCP servers, rails, prompt sections, skills and subagents, undoing them in
reverse order, and rolling back a partial failure. `_unbind` raises `Unsupported hot unbind` for kinds
it does not handle, so unloading is not universal even at the mechanism level. What this schema adds is
not the unloading. It is the **declaration of whether unloading is safe**.

**No runtime that was checked promises that unloading actually happens.** This is not a limitation of
one implementation; it is what every serious platform says about itself:

| Platform | What it says |
|---|---|
| **POSIX `dlclose`** | unloading is reference-counted, `RTLD_NODELETE` disables it entirely, and "a successful return from `dlclose()` does not guarantee that the symbols associated with handle are removed from the caller's address space" |
| **musl libc** | "`dlclose` is a no-op." Libraries stay loaded for the life of the process, because leftover references can crash after unload and unloading leaks thread-local storage. Both behaviours conform to POSIX |
| **Java (JLS §12.7)** | a class may be unloaded "if and only if its defining class loader may be reclaimed by the garbage collector". Unloading is an optimisation, and programs must not depend on it |
| **.NET collectible `AssemblyLoadContext`** | unload is **cooperative**: `Unload()` "just initiates the unloading", and it completes only when no thread holds the plugin's methods on its stack and no outside reference pins it. Completion has to be checked, not assumed |
| **OSGi** | after an uninstall, wirings still in use are "pending removal" and keep their class loader until dependents are refreshed. One leftover reference pins the whole bundle |
| **Erlang/OTP** | the best-known hot-swap system in existence keeps exactly two versions, current and old. Loading a third purges the old one "and any processes lingering in it are terminated" -- it unloads by **killing** what is still running |
| **Linux kernel** | a forced module unload sets taint flag `R`. The kernel does not treat it as trustworthy |
| **Kubernetes** | retirement is drain then force: remove from endpoints, run `preStop`, `SIGTERM`, a grace period, then `SIGKILL` |

**So the word "uninstall" must mean "no longer routed, and drained".** It must never mean "its code and
memory are gone". That is the honest promise, it is the one every platform above actually makes, and it
is why this milestone is last: the schema's contribution is not the unloading but the **declaration of
whether unloading is safe**, plus the draining discipline around it.

The design follows Kubernetes' shape: **stop offering it, wait for in-flight work to finish, and reclaim
on restart.** Nothing claims the old capability has ceased to exist inside a running process.

**Each capsule declares what it needs and provides (space), and how each of its effects is undone (time). So it can be
added, replaced, reverted or removed without breaking the capsules that depend on it. A revocation reaches exactly the
work it affected, and composition risk is screened.**

## What the schema provides

| Operation | What the schema declares or records | Rule |
|---|---|---|
| **add** | `injects` (services it needs), `provides` (services it installs), each with an interface version | admitted only if every needed service has an admitted provider, and there are no cycles |
| **replace** | a new version: new hash, new Verdict | monotone, and compatible: outputs still cover every port a dependent consumes, and `provides` still covers every key a dependent injects. No new write, delete or emission without re-screening |
| **revert** | Standing history (`previous[]`) | back to an earlier hash that still has a valid Verdict |
| **remove** | Standing moves: deprecated, then retired | stop offering it first; retire only when no admitted capsule relies on a service only it provides; agent-core unloads its registrations in reverse order |
| **undo effects** | `effects[].reversibility`: inverse, scoped (a child context thrown away), compensate, or emission (crosses the system boundary) | an emission is never "undone"; it is withheld until the freeze allows it, or compensated |
| **revoke** | the reason sets the policy | superseded: running steps finish. Conformance failed: running steps finish, and downstream claims go stale. Effect violation: running steps abort, and the capsule is quarantined. Revoked provenance: running steps abort, and every capsule built with it in context becomes suspect |
| **trace the damage** | each invocation's step identity (hash of the capsule, its inputs and its predecessors), and its claims | a change invalidates exactly the downstream steps and claims |
| **composites** | members pinned by hash | a composite is offered only while every member is still admitted |
| **screen combinations** | effects (the modifies set), invariants, the Binding's `context` capsules, `load_mode`, `injects`/`provides` | sets are screened, never certified; a confirmed harmful set is never co-loaded |

**Change happens between sprints, not within one.** A sprint keeps the hashes it pinned.

## What composability does not undo, and what the schema does instead

Removing a capsule undoes its registrations, not what it did. Two things stay:

- **External state.** A capability over a live database changes it. Effects on `ext:` resources can only be
  `compensate` or `emission`, and the author must say which, per effect, with `idempotent` and the capability's
  `effect_class`.
- **The context.** A capsule loaded into an agent's context shaped every later decision there. So a context capsule
  counts like the primary for revocation: every invocation it shared a context with is traced and its claims go stale,
  and a context that held a revoked hash is never reused.

**What composition may do depends on the declared class:**

| | pure | idempotent | compensable | irreversible |
|---|---|---|---|---|
| automatic retry | yes | yes | after the compensation ran and was checked | no, a named person decides |
| fan-out in parallel | if parallel safe | if parallel safe | if parallel safe, each item's undo recorded | one item at a time |
| exploration, speculative runs | yes | yes | no | no |
| inputs it may act on | any | any | any | supported claims only |
| approval | none | none | none | the step and the run's effect ceiling must allow it; high severity needs a named person, and an unattended run blocks |

Undeclared behaviour counts as irreversible until an audit says otherwise.

## Why it is done this way

Each row pairs a rule with the measured failure, or the stated design reason, that makes it necessary.

| We do this | Because |
|---|---|
| declare needs and provided services, and each effect's undo | Cordis defines spatiotemporal composability: components added, replaced, reverted and removed without breaking dependents, with the runtime guaranteeing providers outlive consumers (2608.25512 Thm 70, p47), and add, remove and undo reaching the same state as a fresh load (Thm 80) |
| treat emissions as a policy, not a promise | "a message already sent stays sent": Cordis cannot revert what crosses its boundary (2608.25512 p47, p70-71) |
| remove in two steps | Cordis unloads a provider only when nothing relies on it (2608.25512 p36, Alg. 5) |
| version interfaces and pin dependencies | Cordis leaves structural typing of keys and versioning open (2608.25512 p75) |
| compute step identities, so a change invalidates exactly its downstream | with DAG replay, untouched work stayed identical (3 of 3 runs), while loop agents regenerated and contaminated it (Execution lineage, 2605.06365 Table 1; n = 3) |
| screen sets, not only single capsules | severe drift was rare with one skill loaded and rose fourteen-fold to 66.5% with five (p9); 80.6% of high-risk flags were confirmed in execution (SkillFuzz, 2607.02345 Fig. 6, Table II). SkillProbe found the high-risk skills form one connected risk network (2603.21019 p12-13) |
| undo is keyed to a declared class, and external changes are never called reversible | Cordis's guarantees hold only inside its boundary, up to an observational equivalence, and an inverse's correctness is the author's obligation, unchecked by its runtime (2608.25512 p58-59, p70-71) |
| a context capsule counts like the primary when revoked | severe drift rose with the number of skills loaded together (SkillFuzz, 2607.02345 Fig. 6): what shares a context shapes the run |
| gate composites on their members, by hash | jiuwenswarm's SkillPacks already disable a pack when a member is disabled, but reference members by name, so a *changed* member goes unnoticed |
