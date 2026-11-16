# Two temporary sandboxes, one engine product

The coding sandbox and test sandbox serve different purposes. Neither temporary setup defines the final lab format.

## Coding sandbox

Use a dedicated project/workspace on the development machine and an ordinary development container where useful. Keep source edits/build tools here. Give the coding agent the repositories, model configuration, datasets and documentation it needs. Persist writable source/worktrees, dependency/build caches, tool-call records and outputs independently of container writable layers. Keep reference inputs and weights read-only; separate credentials through the host's secret mechanism.

Build images through a controlled host-side Buildx command/adapter. Do not mount a broad host Docker/Incus socket into the produced engine image. Native trusted build tools are not an OS sandbox for arbitrary hostile source; record that limitation and use an appropriately scoped build host.

## Test sandbox

The lab agent creates/provisions a separate disposable environment that runs the identified engine image. It needs the declared inputs, GPU/runtime capabilities, test client and writable scratch/output locations, but no source-editing workbench or coding-agent credentials. Development may use a temporary deterministic adapter if final lab integration is unavailable; label it clearly.

For current research, size RAM/CPU/PID/storage/shared-memory/trace limits from actual available capacity on Ubuntu 24.04 with 48 GB RAM and an RTX5070Ti. Existing containers remain untouched. The owner grants exclusive GPU use during tests; do not assume exclusive CPU or SSD. The resource profile must allow adequate host/controller reserves, weights/datasets and growing report artifacts. Declared engine expert-cache budgets are different from outer sandbox resource limits.

## External control and data

Controller, logs and accepted evidence live outside the test sandbox. Capture the coding sandbox's operations externally too, so a coding-container restart does not erase engineering history. Paths in our YAML are logical roles to be resolved by the lab team, not fixed host mount paths.

Test CPU preparation in parallel where useful, but serialize GPU correctness, timed runs and profiling. Avoid builds and heavy storage activity during measurements. Incus/Docker/GPU/profiler support remains a target qualification task owned with the lab team; this research does not prove it.
