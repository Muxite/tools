---
id: activity-m1-docker-preparation-20261026
status: source-implemented-readonly-live-verified
source: Sources/Prompts/2026-10-26-approved-minimal-m1-plan.txt
last_reviewed: 2026-10-26
next_action: Prepare protected isolated live evaluations, then verify Pi and scientific campaigns with exact frozen resources
---
# M1 Docker development and test preparation

Work began October 25 and this note was captured October 26. The current integration checkout is `AI4Research-Development/jiuwenswarm-m1-reviewed-integration`, branch `m1/all-features-20261025`, at `4b70bb4b37ec4c968d7531698df82dc53dda7ee4` when this note was written. Local `ai4r_M1` is `4b70bb4b37ec4c968d7531698df82dc53dda7ee4`. The local and remote M1 promotion was verified at the same commit after a normal fast-forward push. The preceding remote base is `809351f8993661a9fdc6e4e635d48f3d262f991b`. The integration joins all earlier Planner, utility, deployment and Builder histories; old standalone Builder checkouts are historical candidates.

## User decisions and implemented changes

The exact approved plan, five preceding directions and external-agent/interface and isolated-test questions are preserved in [[Sources/Prompt Register]]. The user explicitly deferred lab sandboxing to M2, selected ordinary processes **inside the app container**, and prioritized the shortest seamless M1 development path. This is a user-authorized amendment to earlier notes requiring nested confinement for every M1 generated job. The maintained design-owner checkout and imported history were not silently rewritten.

OpenJiuwen ReAct owns Builder history, tools, edits, development tests and repairs. Codex supplies fresh governed text completions through the existing ChatGPT subscription bridge. Its tools, subagents, browser/computer use, plugins, hooks and unbounded retries are disabled; unexpected native tool activity fails the turn. No API key is fabricated and no desktop credential profile is copied. Existing login/MFA remains.

Runtime schema 5 explicitly captures `m1_app_process`; it cannot be selected by changing a model output or overriding an existing frozen runtime. Typed jobs run as UID/GID10002 with no-new-privileges, address-space/UID process controls, bounded output, timeouts and process-group cleanup. Docker supplies the app's 4GiB/256-PID envelope. The evidence explicitly reports inherited networking/shared namespaces and never claims per-job cgroup or namespace isolation. Strong hostile-code containment is not established for this M1 mode.

Tested-byte custody, protected edit journals, stale-test invalidation, independent checks, separate verifier calls and immutable Benchmark handoff remain. Benchmark owns correctness/timing and never requests automatic post-submission repair. Current immutable releases: Builder `m1-17`, classification Benchmark `m1-10-agent-pi`, separate Pi Benchmark `pi-m1-4`. New local captures use `local-research-unified-v5`; old captures stay retained.

The normal product launch requires **Docker and a browser**, using existing app and benchmark-runner images on localhost5175. SDK, Node, Python runtime and test dependencies are inside images. Host Python is only an optional managed/SSH launcher. Configuration is captured in the app volume. Runner grants are issued by a short-lived command using the existing authority, not a new service; credentials remain private. The runner's named result volume is writable by UID11001. Root-only references persist in a separate volume inside the same app deployment.

## Verified extent

- **219 focused Docker tests and 4 subtests passed**, covering current capsules, four utilities/composition, classification, Pi, Planner, custody and handoff. No deselection.
- **64 Docker boundary tests passed**, including 5 actual ordinary-process cases, actual packaged Codex feature configuration, controlled-response native OpenJiuwen agent sequences, and completion/provenance cases.
- **31 host/operator tests passed**. These test the optional development/operator tooling and Compose rendering; they do not add a host product dependency. Supplemental overlapping results are not added to these totals.
- The production app and runner images built. The final app served HTTP200 on localhost5175 without host cgroup setup. An actual UID11001 runner wrote to a fresh named result volume. Private benchmark storage was observed as root:root0700.

App image: `sha256:df2ef57055266feb949c4c83a28e7c1206743123f338a476515224ebb42200d1`. Runner image: `sha256:3aa1fb6cb5c84dcef993d6b2dc96ed66444ffb15b9faf76f6771bb4ade293957`. App build identity: `8b15c60f368db82fba4f2f073ca0a3c418791b10c7d48c13164af04c8b2dfc5d`. [Exact source/image receipt and logs](../../AI4Research-Development/jiuwenswarm-m1-reviewed-integration/docs/capsules/verification-20261025/m1-process/verification.json) retain conditions. Tests use a read-only source mount, ephemeral SDK logs and a filter for an upstream dependency's Python SyntaxWarning.

**Scientific live acceptance is still pending.** The user signed in. Runner readiness passed; the first live smoke recorded four authenticated gpt-6.1-sol completions, including separate Intent and Requirements verifier calls. That run halted because the bundled summary case incorrectly selected the static scientific path without its required resources. The example now explicitly selects the planned PDF-summary workflow and supplies a public synthetic PDF. The second run completed Compiler, Planner, Summary and Delivery with 11 completed governed calls (5 workers, 6 verifier calls). A status-reader bug comparing the Planner catalog input with Binder resource inputs was fixed; the completed run was recovered without repeating model calls. Its independently checked archive has 19,769 members and SHA256 ddc425ec2435c99db9ad8b67e209e4e295f03f926319bf089f7bca84554474fa. The original runner campaign stays paused at its old build pin; recovery uses the authenticated client against the repaired build and retains both identities. No accepted live Pi candidate, independent Pi measurement or full scientific research campaign is claimed. Local developer builtins retain visible NOT_RUN model-qualification status. Scientific campaigns also need their exact frozen task, root scoring profile, runtime binding and required activation. The included summary smoke is not a substitute for Builder/Pi or whole-system acceptance.

[The recovered live report](../../AI4Research-Development/m1-live-results/paper_summary.md) preserves the fictional source limitations and contains page citations.

The earlier interrupted broad research suite and legacy dedicated-CLI Builder failures remain in the restart record. They were not converted to passes or silently deleted. No RSI, model-router or M2 lab implementation was added.

## Isolated capsule tests and verifier stop cases

The user requested repeated single-module tests from frozen pipeline boundaries. Existing E3 single-capsule and E2 node-replay execution/scoring mechanisms support immutable inputs, independent checks, separate verifier calls and finite repeated requests. The product local capture has `evaluation_profile_ref=null`; no production authoring command currently prepares the required profile/assets/runtime from a product run. That missing setup is recorded as an implementation gap, not a passing live test or a request to weaken the gates. Controlled-model replay and deterministic capability tests remain distinct from live semantic quality measurement. Malformed evidence must stop at Tier1 before inference; unsupported but well-formed claims require separate live verifier rejection tests. The source operations guide gives isolated Docker test commands. All 8 isolated replay tests passed after restoring the qualified request read ceiling; the new controlled FAIL test verifies a separate recorded verifier call and halt without product acceptance. The finite status fixture also needed a test-only v2-to-v3 brief update; production validation was preserved. The subsequent status run passed its single-node history check but failed the next legacy finite-segment expectation before dispatch; the remaining cases were not run. That unresolved fixture outcome is retained separately, not counted as passing.

## Operation and recovery

Use the [Docker-only operations](../../AI4Research-Development/jiuwenswarm-m1-reviewed-integration/deploy/m1/OPERATIONS.md) and [M1 execution explanation](../../AI4Research-Development/jiuwenswarm-m1-reviewed-integration/docs/capsules/m1-local-process.md). Human steps: start Docker, sign in/MFA, and make existing explicit activation decisions. Builds, setup, scoped grants, invocation and result capture are automated.

The benchmark runner is also the supported external-agent client: authenticated typed HTTP covers intake, uploads, submission, polling, cancellation, reconciliation and verified artifact export. Docker Compose owns app startup; runner has no Docker socket or direct store access.

Seven library files were backed up byte-for-byte before this update. Prompt hashes, validation and the scoped local checkpoint are retained in [the maintenance batch](../Resources/review-batches/2026-10-26-m1-docker-preparation/). Unrelated notebook work and imported archives are preserved. Four scoped `gpt-6-luna` agents handled Codex, Docker setup, process checks and isolated test fixtures; the supervising agent integrated and ran the actual Docker tests and builds.
