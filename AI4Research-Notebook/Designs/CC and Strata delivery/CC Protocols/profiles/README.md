---
id: cc-v2-optional-profiles
status: draft-companions
source: November 4 focused protocol plan
last_reviewed: 2026-11-04
next_action: Select only profiles needed for a concrete integration
---
# Optional profiles

These companions are not prerequisites for ordinary CC use. A selected profile identifies its version, subject and unsupported requirements explicitly. No core requirement is hidden here.

## Source/build evidence

An optional `cc-source-change/1` artifact contains `format`, `repository`, `base` (full Git commit), `patch` (artifact reference), `tree` (expected Git tree) and `build` (`command` argv, `output` directory, optional `lock`). The Factory reconstructs into a new checkout; it does not patch the caller's working repository implicitly. Binary/untracked files, LFS objects and submodules must be complete or explicitly unsupported.

A `cc-build/1` record identifies actual source, dependency lock, interpreter/build command, payload files and step outputs. Failed build attempts retain logs; timeout can leave descendants active and requires reconciliation before retry. This describes construction, not another executable capsule format. The experimental materializer is outside the core reading set under `reference/source_build.py`.

## Observation

An optional `cc-observation/1` output/artifact has `format`, `subject` (release and call/instance), `source` (emitter ID and runner/tool/observer kind), `coverage` (scope and available/partial/unavailable/not_requested status), optional `signals` (kind, format, retained artifact reference) and optional W3C `trace_context`. Add sampling/loss/perturbation details when known. Use native signal formats such as OTLP; self-reported traces are not independent proof.

No collector or internal SDK is mandatory. Missing or malformed optional observation yields a diagnostic without discarding completed outputs. An explicitly selected acceptance policy can require evidence for a particular claim. The experimental exporter is under `reference/integrations/observation_demo.py`.

## Lab integration

Candidate manifests, models, workload, driver/GPU compatibility, profiling windows and benchmark policy remain domain inputs/artifacts. Incus setup and JiuwenSwarm integration are described in [implementation strategy](../IMPLEMENTATION.md), not required CC fields. A valid negative measurement remains a valid result.

[Optional profile schemas](../schemas/profiles.schema.json) define `sourceChange` and `observation`. They are selected explicitly; ordinary CCs need neither.
