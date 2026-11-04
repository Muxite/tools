---
id: cc-containerization-lab-isolation
status: proposed
source: jiuwenswarm/docs/architecture/design-package/README.md; jiuwenswarm/docs/architecture/design-package/2-capability-capsules.md
last_reviewed: 2026-10-20
next_action: Map the proposed tiered isolation to the actual lab host and document approved mounts and network routes before any live run.
---
# CC containerization and lab isolation

Links: [[Workstreams/Lab Infrastructure]] · [[Workstreams/CC Effectiveness]] · [[Resources/M1 Readiness]]

This is a high-level design proposal for a controlled research-agent lab. It draws on the M1 package's separation of the app, confined executor, sidecar, and RSI workbench. It does not claim that the target lab already implements these controls.

## Two separate decisions

**Per-CC containerization** asks where a single capability capsule executes and what that capsule can access. **Whole-lab isolation** asks how the lab environment is separated from user devices, credentials, networks, and production systems. They are different boundaries. Containerizing every CC does not isolate the lab if containers share sensitive mounts, unrestricted networking, a privileged daemon, or a common writable host path. Conversely, a well-isolated lab may run multiple trusted CCs in one restricted executor if contracts and effect policy permit.

## Proposed lab shape

- A private lab host runs a controller, model bridge, and durable run-record store. Access is through authenticated private routes.
- The controller binds task inputs and limits to immutable CC versions and records the frozen plan.
- A confined executor receives only declared inputs, writes to a per-run workspace, and cannot read credentials, other runs, held-out keys, or controller state.
- A verifier/scorer identity receives only the material needed for assessment. Held-out keys are custodian-controlled and withheld from proposers and execution agents.
- A sidecar may run test and benchmark jobs through a narrow authenticated API. It receives no direct runtime database access.
- Candidate/RSI work occurs in a distinct workbench. Proposed changes enter through an explicit review/admission path; the workbench cannot mutate active runs or versions.
- Backups preserve raw artifacts, manifests, logs, and exact software pins with access controls and retention policy.

## When to containerize an individual CC

Use a separate container per CC where the declared effect is high impact, the CC executes untrusted or generated code, dependencies conflict, network or secret access differs, or stronger resource caps are needed. A lightweight shared executor may be considered for bounded model-only agent CCs that have no secret access and do not execute arbitrary code, provided the runner can enforce per-invocation filesystem, network, tool and budget controls. These are design criteria, not a statement of current implementation.

For either choice, contract and run policy jointly define inputs, outputs, effects, allowed tools, network, secrets-by-name, and enforced limits. Never mount secrets into a general research worker. Never mount the held-out answer store into proposer or agent containers. Restrict outbound network to the frozen source service or approved endpoints when task reproducibility requires it. Record image digests and package locks. Keep immutable outputs and execution evidence for replay and audit.

## Open design questions

1. Which host boundary protects the lab from routine workstation activity and production credentials?
2. Is each run assigned a distinct OS identity and filesystem namespace?
3. Which network egress is required for the benchmark, and how is it logged?
4. Who operates the custodian identity and key escrow for held-out cases?
5. What artifact retention and deletion policy applies to prompts, provider traces, and research data?
6. Which CC effects warrant a dedicated container or separate host?

Resolve these against the real lab before claiming the isolation design is implemented. See [[Experiments/cc-effectiveness-protocol|CC Effectiveness Protocol]] for the matched experiment and [[Designs/skills-to-cc-mapping|Skills to CC Mapping]] for capability packaging.

## Superseding direction

The latest [[Sources/Prompts/2026-10-21-vm-capsule-factory-design-plan.txt|request]] chooses full CC containerization as the design target. Selective/shared-carrier discussion above is earlier rationale. Whole-lab isolation is one VM per lab. [[Designs/Lab Capsule and Factory Design Plan]] and linked briefs define next work; the one-CC pilot remains the first implementation check.
