---
id: cc-v2-format
status: draft-specification
source: November 4 focused protocol plan
last_reviewed: 2026-11-04
next_action: Validate packages against the published schemas
---
# Format and schema

## Authority and layout

The producer MUST supply UTF-8 `cc.yaml`, expressed as YAML or JSON with JSON-compatible values, and its declared files. The [capsule schema](schemas/cc.schema.json) defines structure; this document defines meaning and semantic checks. Consumers MUST reject duplicate keys, YAML aliases/anchors/tags, nonfinite numbers, unknown protocol fields and unresolved mandatory choices. Ordinary domain JSON properties are not protocol fields. Producers MUST quote YAML strings that could be interpreted as booleans, numbers or dates; JSON avoids scalar-resolution ambiguity.

```text
package/
  cc.yaml
  tool.py        # implementation if selected
  SKILL.md       # material if supplied
  api.json       # interface document if referenced
```

Images MAY be pinned references rather than bundled bytes. External runtimes, models and dependencies MUST be available/admitted before execution; they need not all be inside every CC. An archive MAY carry this same relative layout. Optional construction/observation contracts belong in [profiles](profiles/README.md).

## Schema index

| Contract | Machine-readable definition |
|---|---|
| Completed declaration | [cc.schema.json](schemas/cc.schema.json) |
| Request / reusable request template | [request.schema.json](schemas/request.schema.json) |
| Call, process input/result, artifact, error, receipt, instance, release index | [messages.schema.json](schemas/messages.schema.json), named `$defs` |

Schemas use JSON Schema 2020-12 with local cross-schema references. Validators MUST NOT fetch arbitrary remote references. A port's domain schema can use bundled `$defs` and fragment references. Schema validation does not establish file existence, reference resolution, permissions, runtime behavior or scientific correctness; semantic validation MUST check those applicable boundaries separately.

## Package fields

| Field | Type / scope | Required / default | Meaning and validation |
|---|---|---|---|
| `cc` | String; package | Required | Literal `"2"`. |
| `id` | ID; package | Required | Stable capsule name. |
| `version` | String; package | Required | `major.minor.patch`, decimal components without leading zeros. Compatibility label, not byte identity. |
| `capabilities` | ID-to-contract map | Optional / `{}` | Actions and served interfaces. |
| `materials` | ID-to-material map | Optional / absent | Passive files. At least capabilities or materials MUST be nonempty. |
| `bindings` | ID-to-binding map | Optional / `{}` | Every selected binding MUST resolve. |
| `defs` | ID-to-port map | Optional / `{}` | Shared direct descriptors/kind shorthand referenced as `$name`; definitions do not chain through other definitions. |
| `provenance` | Relative file path | Optional / absent | Bundled generated build/evidence record. No mandatory build service. |

IDs match `[a-z][a-z0-9._-]*`, are unique within their map and are scoped by package. Capabilities share one namespace. Authors MUST define shared facts once and reference them. Summaries are derived; neither ports nor permission grants are the package-wide union.

## Capability fields

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `does` | Nonempty text | Required | Behavior, result interpretation and significant limits. |
| `using` | Binding ID | Optional / `default` | Explicitly selected bindings need no unused `default` sibling. |
| `takes` | Port map | Optional / `{}` | Action inputs, or service setup inputs. |
| `gives` | Port map | Optional / `{}` for actions | Action results. MUST NOT accompany `serves`; that native interface owns business responses. |
| `needs` | Unique nonempty strings | Optional / `[]` | Required execution provisions. |
| `changes` | Unique nonempty strings | Optional / `[]` | Permitted effect ceiling, subject to host authorization. |
| `guarantees` | Unique nonempty commitment/check IDs | Optional / `[]` | Checkable commitments, not proof or automatic verifier execution. |
| `serves` | Service descriptor | Optional / absent | Persistent provision through a native interface. |

`takes` is data, `needs` is provision, `changes` is permitted effect, `gives` is returned data and `guarantees` is a checkable commitment. For a profiler: target/options are inputs; admitted inspection resources are prerequisites; attachment is an effect; a trace is output. A complete trace can reveal poor performance.

## Ports and configuration

A port is `json`, `text`, `artifact`, `handle`, `$definition`, or a descriptor:

```json
{"kind":"json","optional":false,"description":"Options","schema":{"type":"object"}}
```

| Descriptor field | Required / default | Meaning |
|---|---|---|
| `kind` | Required | `json`, `text`, `artifact`, `handle`. |
| `optional` | Optional / false | Whether the port may be absent. |
| `description` | Optional text | Caller guidance. |
| `schema` | Optional object/boolean | JSON Schema for JSON/text only. Absent means broad JSON or ordinary text. |
| `media_type` | Optional string | Artifact metadata, not inspected-content proof. |

Presence differs from nonempty content. Null is ordinary JSON if allowed, never an unresolved implementation marker. Empty strings, arrays, objects and files are valid values. Required outputs cannot be missing from an `ok` result; a partial result retains available evidence. Large data, state, patches and models SHOULD use artifacts.

Configuration uses ordinary named ports or a broad options object. Service start inputs configure an instance; subsequent requests use its API. Reconfiguration requires an explicit operation or new instance, with effective configuration recorded. There is no competing root parameter list.

Built-in needs: `workspace`, `python`, `process`, `gpu`, `environment`. Built-in effects: `workspace.read`, `workspace.write`, `process.exec`, `process.attach`, `process.control`, `gpu.use`, `dependency.install`, `network.listen`, `network.request`, `model.invoke`, `git.publish`, `deploy`. Unsupported mandatory meanings MUST fail explicitly before dispatch. Other domains need supported profiles, not GPU fields on every CPU tool.

## Binding fields

| Kind | Required fields | Optional fields and meaning |
|---|---|---|
| `native` | `kind`, `command` | `lock`: bundled dependency-lock path. Use admitted local environment. |
| `image` | `kind`, `image` | `command` defaults to `[]` (use pinned image entrypoint/CMD); optional `lock`. Image is `LOCATOR@sha256:HEX` or local `sha256:HEX`; HEX is 64 lowercase characters. |
| `delegate` | `kind`, `agent` | Host-registered delegate name. Framework/session behavior belongs to the adapter. |

`command` is an argv array of nonempty strings. Native commands MUST be nonempty; an absent/empty image command uses the image's pinned entrypoint/CMD. Runners MUST NOT apply implicit shell interpolation. Native `{python}` selects the configured interpreter; `{bundle}` selects staged sealed files. A lock identifies supplied dependencies; it does not authorize installation or prove full environment closure. Bindings grant no authority.

## Service and material descriptors

| Field | Required / default | Meaning |
|---|---|---|
| `serves.interfaces` | Optional / `{}` | ID-to-interface map. |
| `interfaces.ID.protocol` | Required | `http` in the baseline profile; other transports require a specified adapter. |
| `interfaces.ID.port` | Required integer 1..65535 | Internal service/container port. Native `{port.ID}` requests host allocation. |
| `interfaces.ID.path` | Optional / `/` | Origin-relative base path, not a foreign URL. |
| `interfaces.ID.contract` | Optional relative file | Native API description; no duplicate CC business-method list. |
| `serves.ready` | Optional | Object with required `interface` (declared ID) and `path` (origin-relative HTTP GET path). 2xx within startup timeout establishes availability only. |
| `materials.ID.path` | Required relative file | Immutable bytes to read, not automatically execute. |
| `materials.ID.description` | Optional text | Meaning and usage. |
| `materials.ID.media_type` | Optional text | Content format. |

For service launch, `{input.NAME}` inserts literal text or a staged JSON/artifact path. Inserted input text MUST NOT be reparsed. Unresolved placeholders fail. A service keeps its native protocol rather than implementing finite stdin/stdout packets. Container services must listen on the declared port and a reachable internal interface.

## Portable release identity

Referenced files MUST be regular included files inside the package, using relative paths without symlink escapes. A producer MUST reject references to excluded files. Portable index paths use POSIX separators without absolute paths, `.`/`..` segments, backslashes or duplicate normalized paths.

A preparer generates a `cc-release/2` index containing normalized `declaration` and `files`: records of `path`, `sha256`, `size`. Include `cc.yaml` and every packaged implementation/material file; the generated index is outside its own file set. Sort records by UTF-8 path bytes, canonicalize the index using RFC 8785 and SHA-256 the result. The release ID is that 64-character lowercase hex digest. Index/declaration numbers MUST satisfy RFC 8785; encode higher-precision values as strings. File digests cover exact bytes; sizes are nonnegative safe integers. The preparer does not insert current host file modes, executable paths or environment observations into the index. Producer-supplied build/evidence files remain ordinary hashed material. Effective runtime bindings belong to host records.

The reference producer excludes local working-state directories `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `.cc-state`, `.mypy_cache` and `.ruff_cache` before forming the package file set. Declared references to excluded files fail rather than disappear.

Normalization MUST be idempotent and follows these exact steps:

1. Add missing package `bindings`, `capabilities` and `defs` as empty maps. Preserve other optional package fields as absent.
2. Add each capability's `using: default`, `takes: {}`, `needs: []`, `changes: []`, `guarantees: []`; add `gives: {}` only for finite actions.
3. For an existing `serves`, add missing `interfaces: {}` and each interface's missing `path: /`. Do not invent `ready`.
4. Add an absent image `command` as `[]`. Preserve all other binding fields as authored.
5. Preserve port shorthand, inline descriptors, `$definition` references, domain schemas and list ordering exactly. The port `optional: false` default is applied when resolving a port, not inserted into its stored descriptor. JSON Schema default annotations do not mutate input values. Package changes yield new releases; different supplied inputs yield new calls/instances without mutating the package. External assets and images retain their own identities.

## Request CC

```json
{
  "format":"cc-request/2", "id":"request.trim",
  "desired":{"cc":"2","id":"text.trim","version":"1.0.0","bindings":{},"capabilities":{"trim":{"does":"Trim ASCII spaces.","takes":{"text":"text"},"gives":{"trimmed":"text"}}}},
  "open":{"/bindings/default":{"question":"Supply implementation files and binding."}}
}
```

| Field | Required / default | Meaning |
|---|---|---|
| `format` | Required | `cc-request/2`; cannot execute. |
| `id` | Required nonempty text | Request identity, distinct from desired capsule identity. |
| `desired` | Required partial declaration | Fixed known requirements; schema definitions derive from the completed contract. |
| `open` | Required nonempty pointer map | Absent choices relative to `desired`. |
| `open.POINTER.question` | Required nonempty text | Decision to supply. |
| `open.POINTER.owner` | Optional / `implementer` | `requester` or `implementer`. |

Pointers use JSON Pointer escaping, MUST NOT overlap and MUST name absent fields with existing parents. The implementer supplies exactly the named choices and real files; resolution MUST preserve fixed requirements and validate the completed declaration. Null is not an implementation hole. Changed fixed requirements mean a revised request. A template is a reusable request. Runtime-built and prebuilt packages share this same completed format and usage contract.

### Domain ontology as a construction requirement

A requester MAY include an ontology or abstraction model as a material in `desired.materials`: a bundled document or structured file describing the technical method and the system it changes. For an inference engine, this means the technique applied to particular model layers, operations and weights, including how representations, transformations, storage, loading and execution reduce memory. Interfaces and constraints are part of that description, not its whole meaning. Its declared capability contracts specify the externally visible behavior to build; `open` identifies implementation decisions still to resolve. The ontology is construction material, not an extra executable declaration form or an inference-specific root field. Runtime model/configuration values remain ordinary capability inputs.

An inference-technique material SHOULD describe the following where relevant; these are domain guidance, not mandatory fields for every CC:

| Aspect | Description |
|---|---|
| Technique | Algorithm or methodology, its mechanism and source/version. |
| Targets | Model/revision, affected layers, operations and weight groups; excluded parts. |
| Representation | Weight precision, quantization/compression scheme, scales or other metadata, and intermediate-state layout. |
| Execution | Transformations, kernels, weight loading/offloading and memory lifecycle. |
| Requirements | Compatible runtimes/hardware, calibration data, dependencies and assumptions. |
| Goals and tradeoffs | Intended memory reduction, accuracy/performance constraints and measurement conditions; distinguish targets from observations. |
| Open choices | Decisions left to the implementer, explicitly identified in the request. |

The producer SHOULD link the completed package to the requested technique material and record the actual implementation, model/weight identities, configuration and deviations in bundled provenance or referenced evidence. Request-time intent, implemented design and measured results remain distinct. Optional assessment can examine their agreement without becoming a prerequisite for ordinary execution.

The requester SHOULD identify which ontology statements are fixed requirements and which are explanatory context. The implementer MUST retain fixed requirements during resolution or issue a revised request. Supplying an ontology does not prove the implementation conforms: verification remains separately requested, and a consumer MUST NOT treat material instructions as authority to execute or access resources. A domain-specific mandatory interpretation requires an explicitly supported profile; unknown mandatory semantics MUST fail explicitly rather than be silently ignored.

An index consumer MUST check normalization, agreement with the packaged `cc.yaml`, sorted unique portable paths, exact file membership, sizes and digests. Unindexed implementation bytes MUST NOT execute.
