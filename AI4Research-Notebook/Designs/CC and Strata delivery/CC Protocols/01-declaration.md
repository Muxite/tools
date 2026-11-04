---
id: cc-v2-01-declaration
status: v2-reference-implementation
source: November 4 CC v2 revision
last_reviewed: 2026-11-04
next_action: Qualify selected adapter and consumer evidence policy
---
# Declare capabilities and bindings

One package contains named capabilities. A call selects one; sharing a package does not execute siblings or share authority.

| Package field | Meaning |
|---|---|
| `cc` | Required string `"2"`. |
| `id`, `version` | Required package identity and `major.minor.patch` version. Release digest fixes exact bytes. |
| `bindings` | Named executable bindings; required normal binding name is `default`. |
| `capabilities` | Nonempty map of names to contracts. |
| `defs` | Optional map of shared port descriptors, default `{}`; reference as `$name`. |

| Capability field | Meaning/default |
|---|---|
| `does` | Required action, interpretation and relevant limitations. |
| `takes`, `gives` | Port-name maps; each defaults to `{}`. |
| `needs` | Required host provisions, default `[]`. |
| `changes` | Declared effect classes, default `[]`. |
| `guarantees` | Requested semantic checks, default `[]`. A name alone proves nothing. |
| `using` | Selected binding name, default `default`. |

Unsupported required semantics are rejected. Releases contain no unresolved choices or fake digests. Use a [request](02-compiler-and-release.md) while implementation remains open.

## Syntax and field validation

Declarations are UTF-8 JSON or YAML mappings. Reject duplicate keys, YAML aliases/anchors/tags, unknown protocol fields and nonfinite numbers. IDs and local names match `[a-z][a-z0-9._-]*`; names are scoped by package and field namespace. Version is a string of three decimal components with no leading zero except zero itself. Port maps and shared-definition maps have string keys. Needs/effects/check lists contain unique strings. Key order has no meaning. Normalization materializes the listed defaults, retains shared-definition references and never merges capability ports.

Required package fields have no default. `does` is nonempty text. A descriptor's `optional` is boolean. Binding command is a nonempty string array; binding agent is a nonempty host registration name. Native/image bindings additionally accept optional `lock`, a bundle-relative file path sealed with the source. This identifies the supplied dependency lock; it does not install dependencies or establish a hermetic environment. JiuwenSwarm bindings accept exactly `kind` and `agent`.

## Four port kinds

Shorthand `"json"`, `"text"`, `"artifact"` or `"handle"` expands to a descriptor with that `kind`:

```json
{"kind":"json","optional":false,"description":"Caller options","schema":{"type":"object"}}
```

`optional` defaults to `false`; `schema`, `description` and `media_type` are optional. Schema applies to JSON/text ports; media type applies to artifacts. External schema references must be bundled. JSON accepts broad JSON unless a useful schema constrains it. Text carries a string; artifact carries a byte reference; handle carries a host-resolved string. Do not force closed domain records onto ordinary options. Media type is metadata, not proof that content was inspected.

```json
{
  "defs":{"report":{"kind":"artifact","media_type":"application/json"}},
  "capabilities":{
    "inspect":{"does":"Inspect supplied data.","takes":{"options":"json"},"gives":{"report":"$report"}}
  }
}
```

This fragment illustrates reuse; add identity and bindings for a complete declaration. Shared definitions do not schedule pipelines. Callers explicitly supply outputs to later inputs.

## Three bindings

| Kind | Descriptor | Owner |
|---|---|---|
| Native | `{"kind":"native","command":["{python}","{bundle}/tool.py"]}` | Team-trusted local process. |
| Image | `{"kind":"image","image":"REGISTRY@sha256:DIGEST","command":["python","/app/tool.py"]}` | Configured container adapter. Use a pinned image digest or local `sha256:` image ID. |
| JiuwenSwarm | `{"kind":"jiuwenswarm","agent":"registered-agent-name"}` | Host-registered native agent adapter. |

Commands are argument vectors, never implicit shell strings. `{python}` selects the host interpreter; `{bundle}` selects sealed source. Host registration fixes the agent provider; arbitrary caller names are not authenticated agents. All adapters share the call/result/receipt boundary. Availability and execution evidence remain separate from declaration validity.

## Requirements and effects

Built-in needs are `workspace`, `python`, `process`, `gpu` and `environment`. Built-in effects are `workspace.read`, `workspace.write`, `process.exec`, `process.attach`, `process.control`, `gpu.use`, `dependency.install`, `network.request`, `model.invoke`, `git.publish` and `deploy`. Common actions need no external rule document. Custom needs/effects/checks require host support; unsupported required meanings are rejected.

The declaration is an authority ceiling. Host grants bind concrete resources and limits. The reference host requires grants for the selected capability’s full declared effect list; it does not silently remove effects. Artifact references and handles do not authorize access. Model invocation is a separate effect, including in coding sessions; dependency installation, publication and deployment are also separate.

`changes: []` expresses no declared external effects. On trusted native execution it cannot establish that arbitrary code was prevented from making them. [03](03-calls-and-receipts.md) distinguishes enforcement from observation.

## Identity and migration

Contract, executable or material changes require a new sealed release. Native sealing hashes the resolved executable and verifies it again at use. Implementation scripts belong in the bundle and use `{bundle}`; absolute external arguments after argv[0] are rejected as `UNSEALED_IMPLEMENTATION`. Version is a compatibility label; release identity is immutable. Preserve original v1 bytes and lineage. Migration reports unsupported rules, profiles and bindings instead of flattening them into empty lists. Translate only when destination behavior preserves source meaning.
