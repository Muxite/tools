---
id: cc-v2-implementation
status: implementation-strategy
source: November 4 focused protocol plan
last_reviewed: 2026-11-04
next_action: Qualify adapters separately from the standalone protocol
---
# Implementation strategy and experimental reference

## Separation from the protocol

The other four main documents define/explain CC. This file describes tooling strategy and qualification; no core requirement exists only here. The prototype is experimental evidence, not a compatibility authority or production certification. Previous drafts (optional checkout history) and historical reports retain their actual bytes, source hashes and evidence scope.

## Implementation order

1. **Authoring and validation:** schemas, semantic references, included-file checks, normalized defaults and portable release indexes. Reject obsolete aliases; this draft needs no migration machinery.
2. **Standalone local access:** read passive material and execute a finite native action offline using only core dependencies. Require no registry/account/framework/collector. Authorize the host session once.
3. **State and services:** keyed calls, durable artifacts, generation-aware instances, lookup/inspect/stop/reconciliation. Preserve unknown effects. The reference native service requires its foreground leader to remain alive; daemonizing launchers need a supervisor/provider.
4. **Adapters:** pinned images and generic delegates. JiuwenSwarm retains native sessions/tools/permissions through `delegate`. MCP/A2A are integrations, not mandatory dependencies. Native MCP services supply their own discovery rather than duplicate CC method lists.
5. **Factory and Lab:** exact source/base/patch/tree/dependency reconstruction or a pinned executable/image. Keep Strata's component manifest as its domain authority. Qualify an actual Incus host, engine generation, external model and frozen workload before inference claims.
6. **Optional observation and cleanup:** join signals to subject/source/coverage; qualify owned-resource removal. Missing optional observation preserves results. Container removal does not undo remote effects or borrowed-volume changes.

## Reference setup

```text
python -m pip install -r reference/requirements.txt
python reference/ccv2.py run examples/trim trim --inputs examples/trim/inputs.json --trusted-local
python reference/check_package.py
```

Core dependencies are YAML parsing, JSON Schema validation and RFC 8785 canonicalization. `requirements-services.txt` adds process inspection; `requirements-mcp.txt` adds MCP. `requirements-test.txt` installs both optional groups. Native trusted-local provides no OS isolation. Installing a runner does not authorize arbitrary received code.

The reference APIs are `Host.prepare`, `describe`, `material`, `run`, `call`, `start`, `lookup_instance`, `inspect_instance`, `stop` and `reconcile_instance`. Local `binding.json` records resolved executables outside the portable release digest. Another host prepares identical files with its own admitted environment. Environment eligibility and package identity are separate.

## Evidence and next trials

Validate schemas, semantic fixtures and local examples first, then optional service/delegate/MCP tests. Repeat the exact pinned scientific/upstream trials before claiming those integrations passed after format changes. Keep declaration validation, fixture replay, actual host invocation, live-agent behavior and hardware measurement distinct.

Earlier evidence includes native MAPIE and actual pinned upstream deterministic calls. It does not prove this revised format's complete deployment, live models, working image execution or hardware measurements. The earlier Docker attempt failed before worker startup. Incus, GPU/SOL trials, distributed recovery, tenant isolation, automatic OTLP propagation and general clean-uninstall providers require separate qualification.

A first Incus trial selects a supported image/provider, records its operation/instance identities, verifies the actual loaded engine generation, invokes one benchmark client, compares observation disabled/enabled, loses a reply to exercise lookup, and stops/optionally removes only owned resources. Preserve failures and gaps.

## Packaging and maintenance

The portable reading set is the five main documents plus `schemas/`, `examples/` and `profiles/`. It requires no checkout files outside that set or installed environment. The runner can be carried separately under `reference/`. Historical notes/results stay outside the main route. Change schemas, semantic validation and examples together; verify local links and render Mermaid diagrams before publication.

Standards reused: [JSON Schema](https://json-schema.org/draft/2020-12), [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785), [MCP](https://modelcontextprotocol.io/specification/2025-11-25), [A2A](https://a2a-protocol.org/v1.0.1/specification/), [W3C Trace Context](https://www.w3.org/TR/trace-context/), [OpenTelemetry](https://opentelemetry.io/docs/concepts/context-propagation/) and [Incus](https://linuxcontainers.org/incus/docs/main/explanation/instances/). CC does not redefine their internals.

## Focused draft verification

The current local suite covers structural/semantic schemas, portable identity, native services, request resolution, partial/error outputs and recovery. A fresh core-only environment exercises native/material access without MCP, agent frameworks or process-inspection packages. Independent review reproduced and closed index-coverage, partial-request and running-receipt schema defects. Exact results/source hashes are recorded in the transfer revision, rather than treated as protocol requirements. No image, live model, Incus or hardware pass follows from those checks.
