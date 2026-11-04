---
id: sandbox-luna-presenter-script
status: presentation-review
source: Sources/Prompts/2026-10-30-luna-presentation-review.txt
last_reviewed: 2026-10-30
next_action: Present the proposed design for human approval
---
# Presenter script

Core design: slides 1–4. Reference explanations: slides 5–8.

## Slide 1

This is one machine, with one Central Lab Manager coordinating independent labs. Each lab has its own writable AI4R copy, a Local Lab Manager, private state and capability capsules, or CCs. A capsule is a versioned plugin image with an interface and checks. Central assigns outcomes and catalog versions through the local manager, which passes commands to its own AI4R and reports progress. The trusted central host executor is the only component that starts and removes container resources, scoped to the requesting lab. Local AI4R makes research decisions and checks results. Labs can reach our model API and the internet, but cannot reach peers. They send candidate references for review; a human must approve code or image transfer into central storage and manually merge or publish.

## Slide 2

A capability capsule is distributed as a pinned image, carrying its dependencies, versions, interface and checks. To install it, enable the exact image digest in the lab catalog. The local runtime selects it and checks the inputs and allowed effects. Through the Local Lab Manager, it asks the central host executor to start or reuse a lab-owned job or service. Image bytes come from our registry through scoped pulls; the manager passes identities and permissions. Local AI4R checks outputs and stores run records. Removal first disables future selection, then drains or cancels and removes only this lab’s instance. We retain the image identity, run receipts, artifacts and declared persistent data. Shared images are not globally deleted. Local edits create new private image versions.

## Slide 3

For example, compare two methods and return a report. Central records a request ID and completion criteria, then assigns the task to the local manager. The lab AI4R selects a capsule and requests execution through its manager. The central host executor returns a job handle and observations. Scientific output verification happens inside the lab AI4R and capsule runtime; the Local Lab Manager only relays status and evidence references. Central links the request ID to the native research run and host job IDs. If a reply is lost, we query the same IDs. If acceptance cannot be proven, the request remains unknown for operator resolution, without blind resubmission. Stop first asks the research run to cancel or checkpoint, then bounds the stop of lab-owned resources. The sequence illustrates one call; research can iterate.

## Slide 4

The decision today is approval of the architecture only. Existing AI4R supplies research APIs. Docker and Compose supply fixed service lifecycle, while one scoped host executor controls dynamic capsule jobs. The capsule image contract and paired-manager protocol are our design work. JiuwenBox is a candidate for reusing tool and job controls. Lor and ArkenOS supply methods, without a dependency on their cloud services. An operator reviews candidate metadata and explicitly approves export or push. A maintainer then reviews, tests and manually merges or publishes; approval must cover each effect. After design approval we qualify authentication, isolation, cancellation, restart recovery and retained evidence. The next four slides are reference material for questions.

## Slide 5

JiuwenBox is an existing Linux command, file and background-job service available in our codebase. We can reuse compatible API shapes and native tool integration, subject to target testing. It does not replace the image registry, capsule installer or research planner. Docker remains the container controller. We must map jobs and paths to the correct lab and persist stdout, stderr, files and run receipts in lab-owned storage, because default logs are not durable evidence. We still need to prove scope enforcement, cancellation and restart recovery in the actual deployment.

## Slide 6

Lor is a workflow reference for outcome-based tasks, durable work, visible progress, and stopping an individual worker. We can apply those ideas locally: central assigns an outcome and scope, each lab works independently, and central shows status. The design does not depend on Lor’s cloud or proprietary stack, and we are not targeting hundreds of concurrent agents. Here durable means persisted request and run records, with checkpoints when supported. It does not mean automatic replay after any failure. Shared services also mean we do not claim independent hardware or scientific reproducibility from isolation alone.

## Slide 7

This reference contributes persistent goal context, explicit completion evidence, inexpensive job checks, and inspectable task state. Our adaptation keeps scientific records inside the lab, has central hold a routing summary, and checks job state before waking an agent. The example is a finished job waking the local worker to validate evidence and report status. We are not proposing ArkenOS’s interface or social features. Local polling checks job status initially, so a missed notification does not lose the run. Completion criteria are recorded with the request and changes must be recorded explicitly. Backup must cover both the lab workspace and application state.

## Slide 8

Compose and Docker are the initial runtime foundation. Kubernetes contributes an ownership and reconciliation pattern, not a cluster we install. Ansible provisions or repairs the host rather than dispatching live research. OpenSandbox is optional and would need a qualified endpoint/auth path; it must not co-control Compose-managed containers. Our remaining integration is the manager protocol, catalog handoff, scoped execution, and approved export. Capsule images pin plugin dependencies and versions; removing an instance should preserve evidence. OpenSandbox would replace a defined provider function rather than control the same containers alongside Compose. It does not understand AI4R research acceptance or deduplication for us. We still own the thin native communication adapter.
