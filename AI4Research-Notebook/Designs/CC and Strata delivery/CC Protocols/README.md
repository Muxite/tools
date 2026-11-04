---
id: cc-v2-README
status: v2-reference-implementation
source: November 4 CC v2 revision
last_reviewed: 2026-11-04
next_action: Qualify selected adapter and consumer evidence policy
---
# Capability Capsules  -  v2

A **Capability Capsule (CC)** is a versioned package of **capabilities and/or materials**. A capability provides an action or serves an interface over time. Materials can be skills, methodologies and reference files. A package may contain only materials; no dummy process is required.

An inference engine, an observability service, a coding subagent and a small script can all be capabilities. Native versus containerized describes execution packaging, not what counts as a capability. The runner prepares a sealed release, calls an action or starts a service, and retains the known execution facts. Services keep their native APIs.

```mermaid
flowchart TB
    author["Author / brief"] --> declaration["Declaration or request"]
    declaration --> factory["Software Factory"]
    factory --> source["Exact repository + patch + dependencies"]
    source --> build["Materialize / build"]
    build --> release["Immutable CC release: native payload or pinned image"]
    release --> materials["Optional skills and reference materials"]
    materials --> agent
    release --> catalog["Optional catalog"]
    catalog --> agent["Lab agent"]
    agent --> runner["Runner: prepare and authorize"]
    release --> runner
    runner -->|"call capability"| tool["Outputs + receipt"]
    runner -->|"start service capability"| instance["Instance + endpoints + logs"]
    instance --> measurement["Measurement capability"]
    measurement --> tool
    tool -. identifies .-> release
    instance -. identifies .-> release
    release -. lineage .-> build
    build -. materials .-> source
    tool --> evaluator["Independent evaluation when requested"]
```

The host owns identity, grants, budgets, resource handles and receipts. Optional tool telemetry can link to those facts without being mandatory. Native coding sessions, worktrees and subagent delegation remain native; ordinary internal tools do not each need a capsule.

## Reading route

| Read | Purpose |
|---|---|
| [01  -  Declaration](01-declaration.md) | Author a contract and choose a binding. |
| [03  -  Calls](03-calls-and-receipts.md) | Supply values and interpret effects and receipts. |
| [02  -  Factory](02-compiler-and-release.md) | Materialize requests, seal source and deliver products. |
| [08  -  Coding agents](08-coding-capsule.md) | Direct edits and optional propose/apply workflows. |
| [04  -  Lab and provenance](04-provenance.md) | Connect products to actual execution and measurement. |
| [05  -  Examples and evidence](05-examples-and-conformance.md) | Run examples and understand qualification limits. |
| [12  -  Runner and mistakes](12-runner-and-mistakes.md) | Implement the minimum runner and handle common mistakes. |
| [13  -  Lab and telemetry](13-lab-composition-and-telemetry.md) | Plan the Incus engine/tool pool and optional trace links. |

[06](06-distribution-and-interoperability.md), [07](07-quality-and-improvement.md), [10](10-requests-and-materialization.md) and [11](11-factory-lab-handoff.md) are focused companions. [09](09-upstream-coding-integration.md) retains pinned upstream findings.

## Small declaration

```json
{
  "cc":"2", "id":"text.trim", "version":"1.0.0",
  "bindings":{"default":{"kind":"native","command":["{python}","{bundle}/tool.py"]}},
  "capabilities":{
    "trim":{
      "does":"Remove leading and trailing ASCII spaces; all-space input returns an empty string.",
      "takes":{"text":"text"}, "gives":{"trimmed":"text"}
    }
  }
}
```

The package includes `tool.py`. For all-space input it returns `{"outcome":"ok","outputs":{"trimmed":""}}`. See [calls](03-calls-and-receipts.md) for the packet and artifact rules.

The prepared local experiments can be repeated with one command from this folder:

```text
python reference/run_experiments.py
```

It selects the prepared isolated environment, writes a new report directory, and prints each stage's result. An unavailable container engine is reported separately; native experiments still run. See [environment setup and scope](reference/integrations/README.md).

For ordinary development, run directly from the package folder. The host seals the current source, generates a key, and records its release automatically:

```text
python reference/ccv2.py run reference/examples/portable trim --inputs INPUTS.json --trusted-local
```

`INPUTS.json` contains `{"text":"   "}`. State is stored under `.cc-state` by default; use `--store` to choose another location. No semantic checker runs, even if the capability advertises guarantees. JSON payloads stay open unless their author supplies a schema.

Optional advisory checking adds `--check core.complete`. Add `--require-checks` only when completeness should gate acceptance. `core.complete` checks completeness, not semantic correctness. Host applications can register domain checkers and select them through `Host.call(..., checks=["check-id"])`.

For reproducible callers that already manage releases, the lower-level interface remains:

```text
python reference/ccv2.py validate PACKAGE/cc.yaml
python reference/ccv2.py seal PACKAGE --store STORE
python reference/ccv2.py call RELEASE trim --inputs INPUTS.json --store STORE --trusted-local
```

Replace uppercase placeholders with real paths/identity. `INPUTS.json` contains plain values, such as `{"text":"   "}`. [The runtime](reference/ccv2.py) owns executable behavior and help. Sealing copies and hashes source so later working-directory edits do not alter a release. Native `--trusted-local` runs team-trusted arbitrary code and provides **no OS isolation**.

## What to do with a received CC

1. Inspect `cc.yaml`: choose a capability to call/start or material to read. Read its behavior, required ports, prerequisites and effects.
2. Prepare under a supported environment. Pin images; seal native files and interpreter. Install dependencies only through an authorized setup step.
3. Supply plain inputs and authorize the selected entry through the host session. Call an action, or start a served capability and use its published interface.
4. Keep the receipt or instance ID. Inspect logs and outputs; stop owned services when finished. A lost reply requires lookup using the original key.

Inputs and outputs belong to each capability. Service setup inputs belong to the selected capability; ongoing traffic follows its API contract. `defs` shares descriptors without merging ports or permissions.

[The hybrid example](reference/examples/http_product/cc.yaml) provides an HTTP service capability and a finite inspection capability. Run its actual source-to-product demonstration:

```text
python reference/integrations/product_demo.py --directory NEW_DIRECTORY --report REPORT.json
```

Use a new directory. This creates an isolated synthetic repository, applies a bound patch, builds a native payload, starts it, calls its HTTP API and stops it. Git and the reference requirements are needed; no model, registry or GPU is used.

## Flexible packaging; optional observation

Use the image for a deployable engine and keep exact source/diff/dependency linkage for rebuilding it. Native scripts are sufficient for small tools. Skills/reference-only packages need only identity/version and `materials`; see [01](01-declaration.md). No image, registry, mandatory telemetry SDK or semantic verifier is required for every CC.

The proposed Incus Lab pulls the engine image, admits selected pool CCs, connects tool/observer capabilities to its identified instance and runs an independent benchmark. Container cleanup is an optional deployment policy; removing a container cannot undo external writes or shared-volume changes. [13](13-lab-composition-and-telemetry.md) gives the plan and separates implemented native behavior from unexecuted Incus integration.

## Meaning of success

Execution, completeness and semantic assessment are separate. A test runner can execute successfully and report failing tests. Empty semantic checks mean `not_requested`. Hashes establish byte identity, not correctness. Declared, granted, observed and enforced effects are separate facts.

Semantic verification is **only on request**. Missing or crashing advisory checkers preserve successful execution and its outputs. Missing explicitly required checkers block before execution. A failing post-execution check reports failed assessment while preserving the completed result. See [quality and defaults](07-quality-and-improvement.md) and the [result-first example](reference/integrations/ease_of_use_demo.py).

This route replaces active v1 syntax. Migration reports unsupported semantics rather than discarding them. Local reference checks do not establish deployed JiuwenSwarm, remote recovery, GB10 measurements or enterprise isolation. Run evidence belongs in [05](05-examples-and-conformance.md).

[The previous draft](history/README.md) is preserved with byte hashes. [The final experiment summary](reference/integrations/final-run-summary.json) distinguishes the passing local/upstream paths from the blocked image experiment.

### Foreground application boundary

The reference native application must keep its foreground leader alive for the lifetime of its work. Daemonizing launchers need a qualified service supervisor/provider. If the leader disappears, `stop` reports `STOP_UNCONFIRMED` and retains `unknown` instead of claiming its children stopped. Inspect descendants and reconcile the original instance; do not start another copy automatically. This is separate from OS isolation.
