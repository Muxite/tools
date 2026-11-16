

> **EARLIER GUIDANCE: superseded for the current demo.** Use [the November 12 expert-streaming prompt](<20261112 Satay Expert Streaming Demo Agent Prompt prepresentation.md>). This file remains a dated technical/history reference; its generic build order, thread-naming emphasis and old pending-result statements do not define the current assignment.

# 20261111 Satay CC Factory Implementation prepresentation

## Assignment and completion boundary

Build a working, iterative inference-engine software factory on the CC-capable JiuwenSwarm branch. Implement real Capability Capsules, an evidence-backed agent loop, durable build execution, a minimal Lab Manager and a demo lab that runs an actual inference image. Deliver a ten-minute demonstration of component CC → skill-guided integration/repair → Builder CC → Manager → real inference and evidence. Finish with an artifact handoff to the RSI presenter. Profiling and their next improvement are outside this presentation and are not prerequisites for accepting it.

This is an implementation assignment, not a request to write another architecture proposal. Inspect sources, then build the smallest complete vertical slice and expand it to meet the acceptance cases below. Continue independent work when Satay’s queue, a pending result or a required local dependency is unavailable. Report those boundaries honestly; do not replace the real inference requirement with a mock result.

The new user direction replaces the fixed plan-then-build control assumption for this feature. An agent must repeatedly inspect evidence, revise hypotheses and choose the next useful action. A plan is a versioned working decision, not a frozen graph for the entire task. Capability permissions and evaluation contracts remain explicit; replanning does not silently widen authority or change the scoring rules.

## Source identities and branch strategy

| Source | Inspected identity | Role |
| --- | --- | --- |
| https://github.com/Stellven/jiuwenswarm | `ai4r_ccv2`, `2889a1d6342e9baa7721648eca196bbce79a31d4` | Implementation donor with verified AI4Research-Main ancestry |
| https://github.com/Muxite/siminfeng | `main` and `jetson/c1`, `682c6377da20d9229ef1fdb705f63a7a751d14cb` | Current unified-memory engine campaign and reusable code |
| Same JiuwenSwarm remote | `AI4Research-Main`, `141c1c401138f916af0a41aca791adf226d814c7` | Confirmed parent lineage and eventual change target; no adapter |

Fetch and record actual tips before implementation. The user selected **AI4Research-Main** and explicitly prefers a major in-branch redesign over an adapter. These are reference pins, not permission to overwrite newer work.

Git ancestry was checked locally: `141c1c401138f916af0a41aca791adf226d814c7` is an ancestor of `2889a1d6342e9baa7721648eca196bbce79a31d4`. CC-v2 already has real AI4R lineage. Its history includes removal of M1 research machinery and addition of the CC-v2 runner. Describe this honestly as a substantial AI4Research runtime redesign using the CC-v2 implementation; do not imply that the old control model remains intact.

Create a feature branch such as `ai4r/iterative-cc-factory` with AI4Research-Main as the target. If the fetched target is still an ancestor of the donor, start at the target and fast-forward the feature branch to the reviewed CC-v2 donor (or create the feature branch at that donor; the ancestry is identical). Preserve the existing donor commits. Do not reset AI4Research-Main itself. If either branch has diverged, inspect the changes and carry forward the CC-v2 implementation and authorized removals in reviewed feature commits that retain the current target as an ancestor. Do not use an unrelated-history merge, fake parentage, wholesale destructive checkout, or a cosmetic name change as proof of integration.

Inspect the whole target-to-feature diff, including removed entrypoints, migrations, credentials/configuration behavior and startup paths. Preserve unrelated changes and the active engine/GPU queue. Do not create an AI4R adapter, compatibility sidecar or parallel legacy pipeline for this task. Publish, merge or update the shared target only under the operator's existing authorization.

Read `AGENTS.md`, `docs/architecture/README.md`, `docs/architecture/ccv2/README.md`, `PROTOCOL-CHANGES.md`, the schemas and the real caller code. Record a feature-scoped architecture amendment in the new branch: the user authorizes an iterative factory controller for this demo, superseding the old prohibition on adding a planner only to that extent. Do not restore the old intention compiler, frozen M1 pipeline, RSI console or benchmark stack. Preserve other rules, including grants, provenance, credentials and the established local web port 5175 if a web UI is used.

CC-v2 supplies eight tools, native finite calls, image/native services, passive materials, artifact handles and receipts. Its native execution is trusted-local, not an OS security boundary. Existing synthetic service demonstrations are not inference qualification. The inspected agent-facing finite call uses a 60-second default and blocks during execution; it is unsuitable as the lifetime of a multi-minute build.

For siminfeng, read `c2/STATUS.md`, `c2/METHODS.md`, `c2/MEASUREMENT-GAPS.md`, `cc/build_engine`, `cc/abrun`, `cc/ladder`, `cc/engine_handoff`, `bin/jobq` and their tests. Paths are now rooted at the repository, not `campaign/`. Existing `c2/skills/engine-build` and `engine-ab-experiment` are material to adapt, not automatically current authority: compare their instructions against effective-config fixes, current metric definitions and real preflight behavior. Do not run the codex-delegation skill merely because it is present.

## Satay host preparation before expensive work

**Satay is the user’s Jetson Orin Nano and the implementation, control, native build and demo-lab host.** This corrects the earlier Spark assignment. Do not provision a Spark target or require a second machine. Confirm the actual board, memory, aarch64 architecture, JetPack/L4T, CUDA/toolchain, Docker/NVIDIA runtime, disk, current jobs, model files and existing model-provider login before changing anything. Satay is a human-assigned machine name, not an assumed DNS or SSH address.

Adapt the existing `jetson-orin` Builder target and its native arm64/sm_87 recipe after verifying the local environment. Use the host’s compatible JetPack toolchain; do not copy an x86 or Spark recipe. Keep the pinned OpenJiuwen dependency unless a demonstrated compatibility issue requires a documented change. Use Linux installation paths, and do not install Windows-only `pywin32` from the earlier setup example.

Run the factory controller and deterministic Manager on Satay, with the Builder worker and demo-lab runner outside the tested engine container. Image handoff can use an identified local image via Manager admission; label it a same-host handoff rather than a network transfer. Remote transport is unnecessary for the required demo. Keep the architectural component boundaries even though they share one machine.

Respect Satay’s existing GPU/build queue. Do not overlap builds or inference measurements with queued campaign jobs, stop unrelated processes, upgrade JetPack/drivers, or delete model/image baselines to make room. Check current free memory and peak disk needs rather than trusting the earlier 17 GB estimate. Use an available small model and bounded context for the demo; do not require the pending 35B campaign or new downloads. Record the chosen model, configuration, correctness reference and resource budget. Continue lightweight implementation and offline checks while the queue is occupied.

The coding agent may use the existing approved remote model-provider account; the user has not required the coding LLM itself to run on the Nano. Keep credentials out of evidence. If local prerequisites are missing, report the specific blocker and continue independent code work. Neither old Orin evidence nor this host correction establishes a new runtime pass.

## Runtime design to implement

Use a small `jiuwenswarm/factory/` package (proposed location) with clear controller, store, jobs, manager and provider boundaries. Reuse suitable existing primitives rather than creating a second framework. A single trusted-host service with SQLite and an artifact directory is sufficient; no distributed database, registry service, general lab agent or new planner framework is required.

The JiuwenSwarm agent is the decision maker. The host enforces authorization, durable state, identity and lifecycle. Implement this cycle:

1. Read the objective, constraints, current evidence cursor and unresolved questions from the task record.
2. Retrieve relevant evidence by query/reference. Record the specific evidence IDs considered; do not rely solely on the previous node's prose.
3. Record a decision revision: observations, hypothesis, uncertainty, next bounded action, expected evidence, resource budget and stop condition.
4. Invoke the chosen CC or coding operation with resolved inputs and pinned identities. Submit long work and return promptly.
5. Ingest outputs as immutable artifacts, append observations and reconcile job state. Failed, partial and interrupted attempts remain visible.
6. Choose again: inspect more evidence, integrate, repair, rebuild, rerun, accept, report an inconclusive outcome, or stop for a genuinely missing prerequisite. No predetermined success path or infinite retry loop.

Require an observed replan in the demonstration: use a clearly labeled, controlled invalid configuration or incompatible CLI flag. The agent sees the actual rejection, records a revised decision, repairs the request and resumes. Do not secretly inject a failure into another person's run or hard-code the repaired result.

Tasks can use multiple agents later, but the demo needs only one real JiuwenSwarm agent with these tools. Persistent conversation and durable task state must survive individual tool calls. Budget exhaustion yields a partial result with pending work, never a fabricated pass.

## Shared evidence rather than direct node handoffs

The factory store is the source of task state and evidence. A worker publishes artifacts through a scoped ingestion API; another actor queries the store. Messages and scheduling edges may carry task/job/artifact IDs and short notifications, but producer prose must not become the sole authoritative input to the next actor. File bytes may travel via an authorized artifact resolver; never require copying a growing transcript between nodes.

Minimum records:

- Task: objective, constraints, allowed effects, target, revision, current decision and evidence cursor.
- Artifact: ID, digest, byte size, media type, producer attempt, task scope, durable location and completeness state.
- Observation: source artifact references, observed values or errors, host/run identities, confidence/limitations. Keep observations separate from agent interpretations.
- Decision: revision, parent revision, evidence IDs, hypothesis, chosen action, reason for change and next checks.
- Attempt/job: logical request fingerprint, unique attempt ID, state, timestamps, owned process/container identity, resource use, result references and cleanup state.
- Evaluation: versioned contract and exact inputs; execution outcome, correctness assessment and evidence completeness are separate fields.

Use append-only observations and immutable artifacts. A task's current-decision pointer may advance with an expected-revision check. Two writers must not silently overwrite one another. Verify referenced hashes and ownership on read/ingest; cross-task reads require explicit authorization. A local trusted process can bypass application controls, so do not claim strong isolation without an enforcing provider.

Lab evidence must go through Lab Manager. Manager checks task/lab/run identity, persists the objects, and acknowledges durable receipt. If persistence fails, no successful upload acknowledgment is emitted; the lab retains a retryable spool. Idempotent repeat uploads acknowledge the same bytes; same identity with conflicting bytes is an error. Keep lab working files outside the tested container.

## Capsules to build and demonstrate

Package these as ordinary CC-v2 releases. The actual `cc.yaml` schema is authoritative. Do not introduce unsupported top-level fields such as `kind: skill`, `timeout`, `dependencies` or `component`. Put domain-specific component/build manifests in declared material files, validate them separately, and record their hashes in receipts/evidence. Extend the declaration schema only if a demonstrated requirement cannot be represented otherwise, with a version/migration strategy and tests.

| Capsule ID proposed for this feature | Form and job | Required outputs |
| --- | --- | --- |
| `factory.engine_component` | Passive code/patch materials plus component manifest. Prefer a bounded current expert-fill/pregate change after inspecting the existing engine; older Q4_K unfusion is fallback only. | Exact base, patch/file hashes, supported host/dtype/shape assumptions, configuration, engagement checks, correctness obligations and rollback |
| `factory.integration_skill` | Passive workflow material read with `cc_material`; adapt current engine-build/experiment guidance. | Integration and repair procedure, exact preflight, effective-config validation, evidence publication and instructions to reconsider contradicted assumptions |
| `factory.engine_inspector` | Finite tool. Inspect source/build/host compatibility and the exact binary's supported flags; verify requested versus effective settings. | Structured readiness result, evidence artifact, missing inputs and explicit invalid-input error |
| `factory.builder` | Finite `submit`, `status`, `cancel`, `result` capabilities backed by durable jobs. Fetch pinned dependencies, build identified source and export/locate the image. | Job handle immediately; eventually dependency/source/patch/toolchain identities, logs, image transport reference and build receipt |
| `factory.lab_client` | Finite capabilities invoking deterministic Manager submit/status/cancel/result. | Lab job handle, image admission/transfer result, inference/correctness evidence and durable Manager acknowledgment |
| `factory.evidence` | Finite scoped query/read/publish operations over the task store. | Immutable evidence handles and provenance, not unbounded log dumps |

The component is not a callable service merely because it is packaged as a CC. The skill does not grant authority. The coding agent edits an owned checkout using its existing permitted coding tools, guided by those materials. The Builder must compile the integrated component, not only emit a manifest or return an old unrelated image. A pre-existing integrated component must be demonstrated against a defined pre-integration source or explicitly as a recorded integration; do not apply it twice.

At least one real agent must discover these packages, read the component/skill, invoke the executable CCs and inspect their receipt states. A Python script that directly calls functions is useful testing but does not satisfy live-agent acceptance. Preserve the existing eight tools and replay semantics. Use `cc_artifact`/handles consistently; do not pass workstation absolute paths to a remote provider as if they were portable resources.

## Long-running jobs, build dependencies and retries

Choose asynchronous submit/status/result as the main path. A finite CC call acknowledges submission, not build success. Keep its short request deadline separate from the job's operator-approved execution deadline. A host-owned durable supervisor runs the job outside the per-session MCP lifetime; reconnecting the agent must recover the same job. Adapt `bin/jobq` where it meets the contract, otherwise wrap the required lifecycle rather than reimplementing the entire campaign.

Use explicit states `queued`, `running`, `succeeded`, `failed`, `cancel_requested`, `cancelled`, `unknown`. Cleanup is separate. Submission with the same idempotency key and identical logical request returns the same job; the same key with changed inputs is a conflict. An explicit retry creates a new attempt after reconciling prior work. Failed results do not qualify as successful reusable fit/build results. A changed argv, image, model, environment, watchdog or evaluation protocol invalidates incompatible reuse.

Persist identity before launching; use owned process groups/container IDs and start-generation identity. After restart reconcile actual execution before dispatch. Never infer termination from a timed-out caller or use process-name grep as ownership. Cancellation first records intent, then action, then observed stop; do not launch replacement work until the prior attempt is stopped/fenced. Disconnect/cancellation of an agent session must not orphan an untracked build.

The old Jetson builder assumes host tools exist and installs no packages. Implement actual pinned dependency acquisition in a prepared build environment or explicit dependency step. Record cache hits honestly. A clean-environment build must establish the preparation works; a cached rehearsal can shorten the talk. Do not upgrade host drivers/JetPack as a routine demo dependency step. Check peak disk needs before downloading or building, and retain required baseline/rollback artifacts.

Source commit, dirty-tree/patch identity, target/toolchain, base image, dependency lock/recipe, build flags and actual image identity travel together. Local image ID, registry digest and archive checksum are distinct. For remote delivery supply a usable pull reference or archive; verify bytes and loaded image identity at the destination. A local-only image handle is acceptable only when labeled as a same-host handoff.

## Demo lab and acceptance authority

Implement a deterministic Manager and fixed runner, not the eventual autonomous Lab Agent. The runner is outside the tested container. It admits the declared target/image, mounts model/input read-only, runs a fixed small workload, captures actual output/effective configuration and applies a predeclared correctness check. Report failed measurement separately from failed candidate. Preserve logs and cleanup on every exit.

The operator supplies or approves an identified correctness reference/tolerance before evaluating the candidate. A successful text response is a smoke result, not proof of full model accuracy. The agent may improve development checks after learning more, but a changed scored evaluation contract creates a new revision and a new comparable run set; it cannot retroactively turn a failed score into a pass.

For this talk require real integration, build and inference correctness at the declared scope. A positive speedup, the model ladder, J-OM12, KL experiments and an RSI optimization are not required. If speed is shown, use compatible unprofiled evidence and clear sample counts. Do not use the 9B single smoke result as a final benchmark, the predicted IQ3_S 2.5 tok/s as measured, or 70-question and 140-question scores as directly comparable. The existing GPU queue must not be preempted by this assignment.

## Major AI4Research revision with one execution model

Implement this directly as the new factory execution path in the AI4Research lineage. Use the CC-v2 runner and preserved JiuwenSwarm/Codex integration as working code, not as a second service connected through an AI4R adapter. The agent, capsule execution, durable jobs, Manager and evidence store must work together in the resulting feature checkout.

Replace the old fixed compiler/planner flow for this factory use case. Inventory its startup hooks, imports, task records, configuration and UI/CLI entrypoints; retire or redirect the affected ones explicitly. Update AGENTS and architecture/start instructions to the authorized iterative model so the next coder does not restore obsolete assumptions. Keep historical decisions and run evidence labeled historical. Keep independent framework features intact unless the change requires their migration.

Record the old-to-new mapping: how a task is submitted, how the agent chooses actions, where evidence lives, how long jobs are tracked, how cancellation/restart works, and how results are returned. Existing run records are historical evidence; do not deserialize them as live new-format tasks unless an explicit tested migration exists. Unsupported legacy configurations must produce a clear migration error rather than silently invoke the old pipeline. Document a rollback revision/configuration path; rollback does not rewrite evidence created by the new system.

Acceptance requires actual target ancestry, a reviewed migration/removal diff, a working native JiuwenSwarm entrypoint and a real end-to-end factory run in the resulting branch. There is no separate adapter milestone. Report `cc_demo_ready` and `ai4r_lineage_and_migration_verified`; the latter is not permission to merge and does not imply the shared AI4Research-Main has been changed.

## Implementation order and acceptance cases

1. **T01 source/host intake:** pin sources, inspect target and existing queue; record the authorized scope amendment and unresolved host/model inputs. Exit: executable target choice or a precisely bounded external blocker, with independent work continuing. The AI4R branch is resolved.
2. **T02 evidence store:** implement task/observation/artifact/decision records, scoped APIs, atomic persistence and revision guards. Exit: evidence round-trip, conflicting write rejection, failed-ingest retry, no cross-task leakage.
3. **T03 jobs and Builder:** adapt durable execution and dependency preparation. Exit: a real build beyond 60 seconds survives client reconnect; duplicate submit does not duplicate work; changed request cannot reuse old success; cancellation is observed.
4. **T04 capsules:** package component and skill plus inspector/builder/evidence tools. Exit: schemas and material paths validate; operator grants constrain tools; actual agent discovery and receipt handling work.
5. **T05 adaptive loop:** connect real JiuwenSwarm decisions to the store and CCs. Exit: a controlled actual rejection causes a recorded revised decision and corrected attempt using queried evidence; historical failure remains visible.
6. **T06 Manager/lab:** implement image transfer/admission and real inference. Exit: exact image/model/config identity links build → lab → persisted report; bad digest, unsupported target, failed correctness, upload failure and cancellation take truthful paths.
7. **T07 AI4R lineage and migration:** preserve AI4Research-Main ancestry, review the CC-v2 donor changes, update native startup/configuration/docs and remove obsolete factory control paths. Exit: ancestry check, migration/error-path tests, clean affected imports and a real factory run in the resulting feature branch; no adapter.
8. **T08 rehearsal/export:** retain real transcript, source diff, capsule releases, build/dependency records, image identity and lab report; produce a short recording and runbook. Exit: a ten-minute CC-only rehearsal, plus lineage and migration status.

Run existing CC-v2 regression tests and targeted tests for modified boundaries. Verify the real preflight route: dry-run alone does not execute it. Test budget exhaustion, stale/changed request, process restart, duplicate submission, grant denial, invalid settings, unsupported CLI flag, wrong target/image and durable-upload failure. Synthetic fixtures are labeled test evidence and never substituted for the live inference result.

## Deliverables and ten-minute screen sequence

Deliver working code on the feature branch, six actual capsule packages, reproducible setup/start commands, machine-readable task and job examples, acceptance receipts and the evidence bundle. Include a small progress view or CLI that exposes current objective, latest decision/reason for change, active job, artifacts and readiness; a new polished UI is not required. Record source revision and uncommitted patch identity accurately if no commit is authorized.

Screen sequence: 0–1 CC roles; 1–2 baseline/component; 2–4:30 skill-guided integration/repair; 4:30–6:30 real Builder evidence; 6:30–8:45 Manager and real lab run; 8:45–9:30 artifact chain; 9:30–10 evidence handoff to RSI. Use labeled recordings for operations too long for the slot. Do not spend this time on profiling or the RSI person's next improvement.

Return a concise completion report: implemented modules/capsules, source and environment pins, actual commands/results, live versus recorded versus fixture evidence, remaining blockers and the two separate readiness statuses. The attached task manifest is a work contract, not an already implemented runner configuration. No code or live execution is claimed by this handoff package.
