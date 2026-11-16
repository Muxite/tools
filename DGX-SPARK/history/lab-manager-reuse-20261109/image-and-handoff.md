# Image production and cross-machine handoff

## Default build path

Reuse BuildKit/Buildx with a versioned Dockerfile and Bake definition. The product image is the inference engine: executable, runtime dependencies and supported launch interface. Model weights/datasets remain separate read-only identified artifacts unless a measured requirement justifies another arrangement. Do not ship the coding sandbox or the coding agent's credentials as the engine image.

For a registry-free first demo, produce a Docker image archive using supported Docker/Buildx export tooling. Record archive SHA-256, byte size, expected platform and Docker config/image ID, plus source commit/tree/patch, base image identity, build arguments, versions and executable hash. A receiver checks the archive hash before controlled load and checks the resulting image/config identity and executable afterward. Do not call a Docker archive an OCI-layout archive.

If an existing registry is used instead, record a pullable repository@manifest-digest reference and the selected platform manifest. Preserve the distinction between an index digest, platform manifest digest, config/image ID and archive-file hash. No registry publication is authorized merely by this recommendation.

Build provenance and exported attestations depend on exporter/image-store behavior. Check the actual artifact; do not assume `--load` or a Docker archive preserves attestations. Sidecar build metadata can be retained without claiming it is an embedded SLSA attestation. [BuildKit dossier](dossiers/buildkit.md).

## Minimal useful interface

The [YAML proposal](examples/engine-lab-handoff.yaml) separates release identity, input artifacts, argv, logical mounts, required capabilities, requested tests and output expectations. It contains no host paths, Incus commands, privileged flags or arbitrary shell scripts for the receiver to run. Requests are capabilities/requirements; the lab agent maps them to a qualified sandbox and returns accepted, rejected or needs-information with reasons.

One engine image is enough. Additional images are named by role only when actually needed, such as a separately versioned diagnostic tool. Do not add a service graph before there is a real multi-service workload.

The YAML is a working interface proposal, not a CC schema, ontology, final product contract or team-agreed API. It remains `draft` while image/model hashes and supported launch/test details are unknown. Dispatch must reject missing identities, incompatible platforms, unapproved runtime controls and unsupported test requirements before expensive staging.

## Useful CC

Start with an engine-delivery CC grouping independently useful inspect/prepare/validate operations. Consume actual Granite configuration and observed image/build evidence. Return a machine-readable report, unresolved requirements and a handoff artifact. Do not infer image internals from agent assertions or pretend metadata inspection validates numerical inference. The engine itself remains a product with its own launch interface, not an engine-as-CC wrapper.

A second clear option is a saved Nsight report-analysis CC. It can reuse shipped report scripts without acquiring the GPU, but requires a real report/tool version and honest coverage limits.
