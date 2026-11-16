# Start here: discover the Manager and CCs through inference improvements

This is a portable research package, collected November 9, 2026. It contains official documentation snapshots, commit-pinned source examples/tests and original paper PDFs. The initial collection was source-only. A subsequent [Strata study](strata-study/README.md) passed 23 upstream CPU-only fixtures, ran two bounded probes, and recorded an additional suite blocked by a missing dependency. No target GPU, Incus, Docker, inference, crash or profiling qualification ran here.

## Latest user boundary

**Two-machine extension:** the Ryzen7/RTX5070Ti host drives existing-campaign recovery and full-engine integration; Jetson Orin Nano 8 GB drives native ARM/shared-memory/telemetry/state and selected real inference work. Both have Opus leads with bounded Codex and Sonnet/Haiku workers. [Current complete shared prompt](two-machine/ORCHESTRATOR-PROMPT.md) and [platform rationale](two-machine/PLATFORM-NOTES.md) preserve the reported unfinished x86 work and unknown Jetson qualification.

**Primary objective:** improve real inference through broad, evidence-led engineering, and use that work to determine the Lab Manager design and initially needed build, profiling/test, tool, methodology and component CCs. Friday's demo shows a few proven capabilities; it does not define or limit the campaign. [Campaign discovery brief](campaign-discovery.md) records the current interpretation.

1. The coding agent works in a coding sandbox.
2. The builder produces the runnable inference-engine image.
3. The image is sent to our lab and runs in a separate test sandbox.
4. The test sandbox can crash; the external controller and durable evidence must survive it.
5. The other team owns the lab agent and final sandbox choice/provisioning. We choose the image-build method and useful builder-side tools/CCs.
6. Record all work, tests and major operations carefully. Engine source changes occur in the coding sandbox and yield another image.

The earlier broad Lab Manager research remains useful, but does not assign us the other team's lab-agent implementation. Incus remains a researched target; the temporary development/testing setup is not a final deployment format.

## Reading route

- [Current single file to send both Opus leads](two-machine/ORCHESTRATOR-PROMPT.md) — complete two-machine assignments, campaign state, agent hierarchy, references and coordination/evidence requirements; no separate research bundle needed.
- [Earlier general single-file research handoff](AGENT-HANDOFF.md) — retained detailed research background; current machine allocation is in the newer shared prompt.
- [Campaign discovery and completion criteria](campaign-discovery.md).
- [Recommendation and ownership](recommendation.md).
- [Image-making and handoff](image-and-handoff.md).
- [Crash and evidence rules](crash-and-evidence.md).
- [Temporary coding and test sandboxes](temporary-sandboxes.md).
- [Demo specification](demo.md).
- [Coder-agent prompt](coder-agent-prompt.md).
- [Illustrative handoff YAML](examples/engine-lab-handoff.yaml) — deliberately incomplete, not dispatchable or an agreed team API.
- [27 software dossiers](dossiers/README.md) and [13 paper assessments](paper-dossiers/README.md).
- [Prioritized capability backlog](tool-backlog.md).
- [Continued Strata study](strata-study/README.md), [source/CPU evidence status](strata-study/evidence/research-status.json) and [optional experiment ideas](strata-study/experiment-ideas.md).

## Evidence navigation

[Evidence register](evidence-register.csv) records URL, access time, HTTP outcome, source commit and byte hash. [Repository pins](repository-pins.json), [paper register](paper-register.json), and [acquisition limitations](acquisition-summary.json) identify what was actually collected.

`documents/` contains timestamped official HTML/JSON snapshots. `derived/` contains searchable text derived from documents/PDFs. `repositories/` contains selected source and tests with their license files, commit metadata and path inventories; these are not complete source mirrors. `papers/` preserves original PDFs. `context/` preserves exact historical bytes and their original locations/hashes.

Upstream links inside raw snapshots/source files are retained unchanged; they are optional historical/external references, not the package's required reading graph. Authored navigation is self-contained. Public source/technical documentation does not grant blanket redistribution rights: licenses and original terms remain applicable. No weights, credentials, NVIDIA executables or private runtime state are included.

## Validation limits

Hash, archive, PDF readability and authored-link validation establish package integrity and portability, not runtime correctness or experiment acceptance. See `validation.json` after running the package validator.
