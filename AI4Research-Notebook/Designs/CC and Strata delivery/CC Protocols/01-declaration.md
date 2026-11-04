---
id: cc-v2-01-declaration
status: v2-reference-implementation
source: November 4 unified capability and Lab amendment
last_reviewed: 2026-11-04
next_action: Qualify Incus and additional service transports
---
# Declaration and bindings

## 1. One package, one capability map

A capsule is a versioned package of capabilities and/or materials. A capability provides an action or serves an interface over time. `serves` describes its lifecycle; it does not create another category of software. Native versus image describes execution packaging, independently of finite versus persistent lifetime. Skills/reference-only capsules are valid without any process.

| Package field | Type, requiredness, default and validation |
|---|---|
| `cc` | Required literal string `"2"`. |
| `id` | Required package ID matching `[a-z][a-z0-9._-]*`. |
| `version` | Required `major.minor.patch` string; decimal components have no leading zero except zero itself. |
| `capabilities` | Optional ID-to-contract map, default `{}`. At least one capability or material must exist. |
| `materials` | Optional ID-to-material map. Omitted means none; no generated empty field is needed. |
| `bindings` | ID-to-binding map. Defaults `{}` for passive-only packages; executable capabilities require `default`. |
| `defs` | Optional ID-to-shared-port map, default `{}`; reference as `$name`. |
| `provenance` | Optional nonempty bundle-relative file path to generated build evidence; no default. |

Local names follow the same ID rule and are scoped by package and map. Capabilities share one namespace. Shared descriptions/bindings are defined once; discovery summaries are derived. No package-wide permission or port union is authored.

## 2. Capability fields

| Field | Type, requiredness, default and validation |
|---|---|
| `does` | Required nonempty text: behavior, result interpretation and meaningful limits. |
| `using` | Binding ID; defaults `default`, must resolve. |
| `takes` | Port map; defaults `{}`. Call inputs for a finite action; instance setup inputs for a served capability. |
| `gives` | Port map for finite action outputs; defaults `{}`. Not used with `serves`, whose interface owns business responses. |
| `needs` | Unique string list, defaults `[]`; supported host provisions. |
| `changes` | Unique string list, defaults `[]`; permitted effect classes, under host authorization. |
| `guarantees` | Unique string list, defaults `[]`; checkable commitments, not proof or automatic verifier execution. |
| `serves` | Optional lifecycle/interface object. Absent means ordinary finite call. Native/image process bindings supported by the reference service adapter. |

The terms do not overlap: `takes` is data, `needs` is provision, `changes` is permitted effect, `gives` is returned data and `guarantees` is a checkable commitment. A profiler takes a target and options, needs permission/resources to inspect it, may attach instrumentation, gives a trace and can promise trace coverage. A complete trace can reveal poor performance. Optional guarantees never gate ordinary execution automatically.

## 3. Ports and ordinary configuration

A port is `json`, `text`, `artifact`, `handle`, a `$definition`, or a descriptor:

```json
{"kind":"json","optional":false,"description":"Options","schema":{"type":"object"}}
```

| Descriptor field | Rule |
|---|---|
| `kind` | Required `json`, `text`, `artifact` or `handle`. |
| `optional` | Boolean, defaults false. |
| `description` | Optional text. |
| `schema` | Optional JSON Schema for JSON/text; no external references. Ordinary JSON remains broad unless deliberately constrained. |
| `media_type` | Optional artifact media type; metadata, not inspected-content proof. |

Omitted optional ports differ from present null, empty strings/arrays/objects and empty files. Required output absence is malformed; a valid empty output is success. Null is ordinary JSON if allowed, never an unresolved implementation marker. Large state, source changes, weights and traces belong in artifacts; host-issued handles identify authorized live resources. Possessing a handle/reference is not a permission grant.

Use ordinary named ports or a broad `options: json` to parameterize behavior. For services, start inputs configure the instance; subsequent prompts/requests use its native API. Configuration changes require an explicit reconfiguration capability or new instance/generation. No competing root `parameters` list is needed. Requests/templates list explicit open choices; executable releases contain none.

## 4. Bindings

| Kind | Binding fields | Meaning |
|---|---|---|
| `native` | Required `kind`, nonempty argv `command`; optional bundled `lock` path | Run in the admitted local environment. |
| `image` | Required `kind`, immutable `image`, nonempty argv `command`; optional `lock` | Run an image by digest/local immutable image ID through a qualified provider. |
| `jiuwenswarm` | Required `kind`, registered `agent` name | Delegate a capability through native sessions/tools and parent authority. |

Unknown fields/bindings are rejected. Commands are argument vectors with no implicit shell. Native `{python}` selects the configured interpreter; `{bundle}` resolves sealed source. Native execution is explicitly trusted-local and provides no OS isolation. Locks identify supplied dependencies; installation and full environment closure are separate setup/provider concerns. Images do not replace external model, workload, architecture or GPU-driver identities.

## 5. Served capabilities

```yaml
cc: '2'
id: example.service
version: 1.0.0
bindings:
  default:
    kind: native
    command: ['{python}', '{bundle}/server.py', '--port', '{port.api}']
capabilities:
  engine:
    does: Serve the documented inference API; readiness establishes availability only.
    changes: [process.exec, network.listen]
    serves:
      interfaces:
        api: {protocol: http, port: 8080, contract: api.json}
      ready: {interface: api, path: /health}
```

This is a complete declaration; its package must contain real `server.py` and `api.json`. The runnable synthetic version is [http_product](reference/examples/http_product/cc.yaml).

| `serves` field | Rule |
|---|---|
| `interfaces` | Optional ID-to-interface map, defaults `{}`. |
| `interfaces.ID.protocol` | Required `http` in the reference profile; other transports need a qualified provider. An HTTP interface may carry an existing native API, including a separately supported MCP server. |
| `interfaces.ID.port` | Required integer 1..65535; service/container port. Native `{port.ID}` requests host allocation instead. |
| `interfaces.ID.path` | Origin-relative base path, defaults `/`; not a foreign URL. |
| `interfaces.ID.contract` | Optional bundled API document path. Owns request/result semantics. |
| `ready` | Optional object, no default probe. Required `interface` is a declared interface ID; required `path` is an origin-relative HTTP GET path. 2xx within the startup timeout establishes availability only. |

Launch argv supports `{input.NAME}` and `{port.ID}`. Text becomes literal argv text; JSON/artifacts become staged file paths. Inserted values are never reparsed as placeholders. Omitted optional input cannot satisfy a placeholder. The reference service profile rejects live/device handles until a provider qualifies them. Image services must listen on the declared container port and a container-reachable interface, typically `0.0.0.0`; host publication is loopback in the current adapter.

Services are capabilities, but a process lifetime is not a finite tool result. `start` manages the provider; clients use the published interface. A gateway may expose supported service methods as tools without changing the package model. The current generated MCP bridge exposes finite calls only; it does not guess arbitrary service methods from prose.

## 6. Materials and skills

```yaml
cc: '2'
id: paper.methodology
version: 1.0.0
materials:
  method:
    path: SKILL.md
    description: Methodology, assumptions and references for a coding agent.
    media_type: text/markdown
```

A material has required nonempty relative `path`, optional text `description` and optional text `media_type`. It names a sealed file; multiple files use named entries or an existing archive format. No extra capability or dummy binding is required. Preparation checks referenced files are actually included in the sealed bundle, not merely present under ignored directories. Absolute paths, escapes, symlinks and missing/excluded materials are rejected. `Host.material(release, id)` returns the selected immutable artifact and descriptor. Skills are supplied context; loading them does not execute code or grant authority.

An active search library is a capability with inputs/results and declared network effects if needed. A passive library is material. Neither requires a new package kind or a mandatory search/database technology.

## 7. Authority and compatibility

Built-in needs: `workspace`, `python`, `process`, `gpu`, `environment`. Built-in effects: `workspace.read`, `workspace.write`, `process.exec`, `process.attach`, `process.control`, `gpu.use`, `dependency.install`, `network.listen`, `network.request`, `model.invoke`, `git.publish`, `deploy`. Unsupported mandatory requirements/effects are rejected. CPU tools need no GPU fields.

Session authorization is reused and limited to the selected capability. Explicit grants can narrow the session, never widen it. The trusted-native reference requires authorization for the selected entry's full declared effect ceiling; it cannot selectively contain arbitrary native code. Native/image packaging does not itself authorize attachment, publication or installation. A basic Docker bridge requiring egress rejects listen-only admission unless an enforcing provider supplies it.

Declarations reject duplicate keys, YAML aliases/anchors/tags, unknown protocol fields and nonfinite numbers. JSON payloads remain open data. Normalize defaults without merging sibling ports or permissions. Changing bundled source, contracts or default configuration produces a new sealed release. Changing supplied call/setup inputs produces a new bound call/instance identity without changing the package release. Version labels express compatibility, while digests fix bytes.

The preceding unpublished `applications` draft is an import-only compatibility form: the validator converts each entry into `capabilities.ID.serves`, rejects ID collisions and emits only the canonical map. New declarations use `capabilities`. Old tool-only normalized declarations retain their prior model. V1 still requires explicit migration; unsupported meanings are reported, never weakened. Older v2 runners must reject new unsupported fields rather than discard them. See [13](13-lab-composition-and-telemetry.md) for optional telemetry and the planned Incus adapter.
