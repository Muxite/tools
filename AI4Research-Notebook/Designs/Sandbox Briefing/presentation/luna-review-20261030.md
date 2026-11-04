---
id: sandbox-luna-original-review
status: presentation-review
source: Sources/Prompts/2026-10-30-luna-presentation-review.txt
last_reviewed: 2026-10-30
next_action: Present the proposed design for human approval
---
# Luna review — AI4R Lab Manager design deck

## Presenter walkthrough and audience questions

### Slide 1 — Complete system

**What I would say:** “This is one machine with a central manager coordinating separate project labs. Each lab has its own AI4R worker and Local Lab Manager, its own research state, registry overlay, and capsule instances. The central manager sends work and a read-only catalog snapshot, then receives progress. Labs can reach the model API and internet within policy, but cannot talk to each other. Changes stay local until a person approves central adoption.”

**What a first-time audience may ask:**

- Does the central manager send a request directly to the Local Lab Manager, or does it call AI4R and AI4R route it?
- Which connection carries commands and which carries progress? Are they one request/reply channel?
- Does a Local Lab Manager own its own runtime, or does the Central Lab Manager launch containers in every lab?
- The orange arrows seem to run between Central Lab Manager and lab CC services. Is that a direct runtime control path, and if so why is the Central host executor absent?
- What exactly is “clone base”: source code, an image, a registry snapshot, or a project workspace?
- What can “internet” access reach? Does the same policy also block peer-lab traffic?
- Does “human approval” cover transfer into a review store as well as merge/publish? Who approves and who performs each action?

### Slide 2 — Capsule images and instances

**What I would say:** “A capsule is shipped as a pinned image that carries its dependencies and declared interfaces. The lab’s capsule runtime selects and checks a release for a specific call; a scoped executor starts or connects to the lab-owned job or service. On withdrawal we stop future use and remove the lab’s running instance, while keeping the evidence and the image reference intact. Local edits become private releases. A person must approve any move into the central catalog.”

**What a first-time audience may ask:**

- Who installs and removes the lab-owned instance: the Local Lab Manager, capsule runtime, or Central Lab Manager?
- Is the “scoped host executor” the central manager’s host function from slide 1, or a different controller? The diagram does not show this relationship.
- The green arrow from “Pinned CC image / release” points to the Central Lab Manager, but the next actions appear to install a local instance. Does the manager proxy image bytes, or only authorize/resolve a digest while the lab pulls it?
- What does “bind / guard / check each actual call” mean to an operator? Which checks run before invocation, during effects, and after outputs return?
- “Uninstall / withdraw future use” conflates uninstalling a running instance with withdrawing a release from selection. Which state is removed, and which history remains?
- Does “declared state” include persistent service data, or is that deleted on detach?

### Slide 3 — Research, execution and recovery

**What I would say:** “The central operator creates a stable request ID and sends an outcome to the Central Lab Manager. The task and catalog snapshot go to the Local Lab Manager, which asks the capsule runtime to run a scoped capability. The host executor returns a job handle and observations. The lab checks outputs, records evidence, and reports progress and candidate references. If a reply is lost, we look up the same ID instead of submitting a duplicate. Cancellation first asks the native research run to stop or checkpoint, then stops resources it owns. Candidate work still requires a human-approved export.”

**What a first-time audience may ask:**

- Why does step 3 go from Local Lab Manager to Central host executor when slide 1 says the local manager executes assigned work? Is this executor a central service, a function inside the central manager, or a local adapter?
- Who owns the native AI4R run ID versus the capsule job ID? Which identifier does the user see and use to resume or cancel?
- Step 5 appears as a purple loop at the executor/local boundary, but is described as local output verification. Who checks the result, and what exactly does the loop mean?
- How does the Local Lab Manager return a result to the central manager if the reply is lost? Is “look up the SAME ID” about the native API, the manager protocol, or both?
- What happens if the native API cannot prove that the request was accepted? Can an operator resolve an “unknown delivery” state?
- What does “bounded stop of owned resources” include, and who owns the resource if cancellation races with a restart?

### Slide 4 — Reuse and approval

**What I would say:** “The architecture is our proposal; the listed systems provide selected building blocks or methods. AI4R keeps scientific run state. Compose and Docker own fixed services and image instances. The capsule runtime checks compatibility and acceptance. JiuwenBox may supply compatible command and job controls, but its adapter still needs qualification. Lor and ArkenOS contribute workflow ideas, not cloud services or code dependencies. The decision today is whether to approve the paired managers, lab isolation, and human-gated central writes. Implementation and compatibility checks come afterward.”

**What a first-time audience may ask:**

- Which rows are already implemented and which are proposals? “Reused design feature” sounds more settled than “proposed interface” in the notes.
- Who owns adapter qualification and what evidence is sufficient to say “compatible”?
- Does the capsule runtime already exist in AI4R, or is the capsule image contract also part of the design being approved?
- What is in scope for this approval: architecture only, or permission to begin implementation?
- Who is the human approver, and does approval happen once per export, per push, per merge, or per publication?

### Slide 5 — JiuwenBox

**What I would say:** “JiuwenBox is a possible source for command, file, and background-job API patterns. It does not provide our image registry, plugin installer, or research planner. We would map its job IDs, paths, and scopes into lab-owned records, leave Docker responsible for capsule instances, and store outputs and receipts ourselves. Isolation, cancellation, and restart recovery are claims we still need to verify in the target setup.”

**What a first-time audience may ask:**

- Is JiuwenBox a required component or an optional adapter candidate?
- Which service sends the structured tool request, and where does the lab scope get enforced?
- Where do stdout/stderr and files go, given the note that defaults are not durable evidence?
- Can it safely operate on a CC container without becoming a second controller?
- What is the acceptance test for cancellation and recovery?

### Slide 6 — Lor methodology

**What I would say:** “Lor is a workflow reference for outcome-based tasks, durable work, visible progress, and stopping an individual worker. We can apply those ideas locally: central assigns an outcome and scope, each lab works independently, and central shows status. The design does not depend on Lor’s cloud or proprietary stack, and we are not targeting hundreds of concurrent agents.”

**What a first-time audience may ask:**

- What does “durable” mean in this design: persisted request, native run, checkpoint, or all three?
- Who observes progress and exposes the stop control: central manager, local manager, or AI4R UI?
- Are the two labs scientifically independent if they share model API, image library, or host resources?
- Is this methodology slide decision-relevant, or would a concrete operational example be more useful?

### Slide 7 — ArkenOS methodology

**What I would say:** “This reference contributes persistent goal context, explicit completion evidence, inexpensive job checks, and inspectable task state. Our adaptation keeps scientific records inside the lab, has central hold a routing summary, and checks job state before waking an agent. The example is a finished job waking the local worker to validate evidence and report status. We are not proposing ArkenOS’s interface or social features.”

**What a first-time audience may ask:**

- Which event source wakes the local worker, and what happens if that event is missed?
- Where is the completion criterion stored, and who can change it while a run is active?
- Does central store only a summary, or also candidate references and audit evidence?
- How is the saved task state backed up and recovered?

### Slide 8 — Infrastructure reuse

**What I would say:** “Compose and Docker are the initial runtime foundation. Kubernetes contributes an ownership and reconciliation pattern, not a cluster we install. Ansible provisions or repairs the host rather than dispatching live research. OpenSandbox is optional and would need a qualified endpoint/auth path; it must not co-control Compose-managed containers. Our remaining integration is the manager protocol, catalog handoff, scoped execution, and approved export. Capsule images pin plugin dependencies and versions; removing an instance should preserve evidence.”

**What a first-time audience may ask:**

- Is OpenSandbox a real candidate in the approval decision, or an appendix alternative? What is the reason to include it if Compose is the baseline?
- Who enforces the lab boundary for network access, mounts, and shared services?
- What is “withdrawal” in operational terms: stop service, detach, remove container, revoke selection, or all of these?
- Which exact bits of evidence persist after instance removal, and who stores them?
- The bold line says images handle plugin dependencies/versions, but who tests that the image runs against this AI4R and host/provider version?

## Prioritized issues and suggested fixes

### P0 — Clarify ownership and redraw the execution path

The top-level design says one Central Lab Manager per machine and one Local Lab Manager in each lab, but the arrows do not make the command/runtime ownership legible. Slide 1 sends orange runtime lines from the central manager into lab CC services, while slide 2 places a “Central Lab Manager / Scoped host executor” between the local worker and local CC instances. Slide 3 then makes the local manager call a “Central host executor.” These readings conflict with the stated rule that the central manager coordinates and the local manager executes, and with the one-controller-per-resource rule.

**Fix:** choose one path and use it consistently across slides 1–3. Show Central Lab Manager → Local Lab Manager for assignment/status. Put the scoped provider/executor inside the Local Lab Manager boundary if it owns lab resources, or explicitly label a central host execution function as the sole owner and show how it is scoped to a lab. Keep capsule runtime as the scientific caller/checker, not a second container controller. Give each arrow a verb and direction; use a legend for “request/status,” “image identity/pull,” and “runtime control.” If image bytes are pulled directly from a registry, draw a thin authorization/digest path to the lab and a separate registry pull path; do not imply the central manager proxies the image.

**Concrete slide edits:** Slide 1: put “scoped provider (owned by Local Manager)” inside each lab, remove the direct central-to-CC orange runtime arrows, and label the central/local blue pair “assign” and “progress/status.” Slide 2: rename its central box “Local scoped provider” (if that is the intended owner) and show the Local Manager requesting lifecycle actions; keep “Central Lab Manager” out of the instance-control path. Slide 3: rename “Central host executor” to the same provider name and place it under the correct owner lane. If instead one central provider truly controls all lab resources, explicitly revise slides 1–2 and show its per-lab authority boundary.

### P0 — Make the human approval gate concrete

Slide 1’s rose arrows are visually ambiguous about whether lab code/data are transferred before approval. The note says candidate references may be submitted for review, but the visible diagram can be read as a lab-to-gate-to-central-source push. Slide 4 says “human-gated central writes,” while its supporting sentence uses “approved export / merge”; it does not say who chooses, approves, transfers, merges, or publishes. The user requirement is stronger: no code or image reaches central maintained/review stores and no merge/publish occurs without approval covering that effect.

**Fix:** label the pre-approval action “submit candidate reference/metadata only” if that is intended. Put “human selects + approves export” before any transfer into central review or maintained storage, then “human-approved push” and “manual merge/publish” as distinct steps. Identify the approver/role and whether approval is per action. Keep no automatic agent merge explicit.

### P1 — Simplify and make the arrows decode without the notes

Slide 1 is dense and the color legend overloads color with several semantic classes. Crossings and bottom return arrows are hard to follow; a cyan line gap is explained only in speaker notes. The orange lines can look like central control of lab-local services, and the purple line on slide 2 is not self-explanatory. Slide 3’s step 5 loop is especially opaque and numbering 1–7 makes this look like a strict pipeline despite the note saying research is adaptive.

**Fix:** remove nonessential crossings, label edges in words, and use separate lanes for control/status, image resolution/pull, runtime execution, and human-approved export. Mark slide 3 “illustrative lifecycle, not fixed stages,” and replace the step-5 loop with a simple local verification box and an explicit return arrow. Do not rely on color alone.

On slide 3 specifically, put “verify scientific outputs / accept or reject” inside the Local AI4R / capsule runtime lane, not beside the Local Manager/executor interaction. The Local Manager can report the result and manage environment lifecycle, but it must not look like the scientific judge. Draw the return as “verified status + evidence refs” from local AI4R through Local Lab Manager to Central Lab Manager. The current bold step 5 sits between executor and manager and reads like an unlabelled callback.

### P1 — Show capsule install, use, and removal as an operator-usable lifecycle

Slide 2 compresses a critical feature into three boxes. “Install / attach,” “use isolated job / declared service,” and “uninstall / withdraw future use” do not say who acts, what object changes, how a pinned version is selected, or what is retained. The image-to-central-manager arrow also suggests the wrong data path. Slide 8 repeats that withdrawal removes instances without erasing evidence, but not what evidence or service state survives.

**Fix:** depict a local lifecycle: (1) Local Lab Manager resolves an exact digest from its local overlay/catalog; (2) lab pulls the immutable image from the registry; (3) capsule runtime binds a call and checks guards; (4) Local Lab Manager’s scoped provider starts/reuses the declared instance; (5) runtime checks outputs and records receipt/evidence; (6) detach blocks future selection, drains/cancels and removes only that lab’s instance; (7) retain image identity, receipts, artifacts, and explicitly declared persistent service data. Distinguish revoking a release from removing an instance. State that shared image layers are not globally pruned.

### P1 — Separate proposed reuse from established capability

Slide 4’s table and slides 5–8 use present-tense wording that can sound like the reuse path is already integrated. But the notes say the manager/registry interfaces are proposed and runtime/provider compatibility remains unqualified; JiuwenBox is not a complete installer and its logs may not be durable. Lor/ArkenOS are methodology references, not audited implementations. Slide 8 mentions OpenSandbox despite it being optional and having an auth caveat.

**Fix:** label each item “existing in AI4R,” “design pattern only,” “candidate adapter,” or “to build/qualify.” For each candidate adapter, list the specific proof needed (scope enforcement, auth, cancellation, durable receipts, restart recovery). Keep the open-source alternatives in appendix and avoid suggesting they are dependencies. In slide 4, change “Reused design feature” to “Borrowed capability / pattern” and add a status column.

### P2 — Reduce jargon and define visible terms

“CC,” “capsule,” “bind,” “guarded call,” “overlay,” “receipt,” “candidate ref,” “reconcile,” and “native research API” arrive without a plain-language definition. The audience cannot tell whether a CC is a plugin, service, agent, or container. “Image / capability registry” risks being mistaken for a mutable source repository.

**Fix:** define CC once as “capability capsule (CC): versioned plugin image plus interface and checks.” Use “local private catalog” rather than “overlay” on first mention; use “run receipt (inputs, version, status, outputs)” for receipt; and define “bind” as selecting an exact release and allowed inputs/effects. Replace “reconcile” with “look up and resume control of the same job after restart.”

### P2 — Keep the decision deck focused

Slides 5–8 are useful derivation material but add four vendor/tool tours after the decision slide. That risks making the proposal feel like a technology-selection pitch rather than the requested architecture approval. Slide 4 is the apparent approval endpoint, with later slides reopening implementation choices and alternatives.

**Fix:** keep slides 1–4 as the core, with slide 4 as a crisp approval ask and named follow-up qualification work. Move slides 5–8 to appendix and refer to them only when asked. Use one concrete task example in the main flow to make the design testable.

### P2 — Refresh speaker notes to match the eight-slide deck

The notes repeat a long global architecture preamble on every slide, including “Dense four-slide main presentation,” even though this deck has eight visible slides. The repetition makes slide-specific intent hard to find and can cause the presenter to repeat caveats instead of telling the story. Slide 1 notes explain special arrow crossings that are not self-evident in the visual; slide 3 notes call the flow conceptual but the numbered design still looks prescriptive.

**Fix:** keep shared constraints once in a short opening note (or one presenter brief). Give each slide notes only its purpose, what to say, the specific caveat, and the transition. Update the slide-count wording, remove stale/redundant copy, and make notes agree with revised arrow ownership and approval path. Include the scientific-check owner on slide 3 notes and the exact approval scope on slide 1/4 notes.

## Slide-by-slide edit checklist

- **1:** Replace “clone base” with “read-only catalog snapshot”; make no-peer-lab and outbound internet policy explicit in a small boundary note. Remove or relabel the crossing arrows; show candidate reference submission separately from human-approved transfer. Keep exactly one central manager and one local manager per lab visible.
- **2:** Show who resolves a digest, pulls the immutable image, creates/reuses an instance, verifies outputs, and removes the lab-owned instance. Separate “withdraw release from future selection” from “stop/remove this instance.” State what evidence and persistent data survive.
- **3:** Mark the sequence illustrative. Separate request ID, native research run ID, and provider job handle in the labels. Move scientific verification to Local AI4R/capsule runtime; draw evidence/status back through the Local Manager. Add the unknown-delivery recovery actor and lookup boundary.
- **4:** Make the approval ask and the “after approval” work explicit; add a status for each reuse row. Name the approval role and distinguish candidate review reference, approved export/push, and manual merge/publish.
- **5:** Mark JiuwenBox “candidate adapter, qualification required,” and say where durable stdout/stderr, files, and receipts are stored.
- **6–7:** Mark vendor examples “method only”; either move to appendix or keep one short comparison slide. Pair each claimed method with the specific AI4R adaptation and avoid any implication of external cloud dependency.
- **8:** Keep Compose baseline, clearly mark OpenSandbox optional/unqualified, and clarify that the provider owns only its declared objects. Spell out retained state when withdrawing a CC instance.

## End-to-end coherence check: one task and one CC

**Scenario:** An operator asks Lab A to compare two analysis methods and report a result. Lab A uses CC image `registry.example/analysis:2.4.1` (illustrative pinned release) in an isolated job. The task produces a report and a private candidate CC change. Lab B must remain unaffected.

1. **Create request:** Central AI4R/operator records outcome, completion criteria, and a stable request ID. The Central Lab Manager assigns Lab A. The slides show these concepts, but do not say where the request record lives, who can change criteria, or what the operator sees.
2. **Handoff:** Central sends the task plus a versioned, read-only catalog snapshot to Lab A’s Local Lab Manager. This is specified in the notes but the diagram labels “clone base,” which implies a code/workspace clone rather than a catalog snapshot. Lab A’s private overlay must remain writable only by Lab A.
3. **Resolve CC:** The local capsule runtime selects the exact image digest and checks declarations, guards, inputs, and required provider. Current slide says “select / bind / check” but omits who authorizes the pull and where the digest is recorded. Image bytes should flow from a scoped registry endpoint, not through the manager unless proxying is intentional.
4. **Install/launch:** Local Lab Manager/provider creates a Lab A-owned job from the pinned image. This is where current diagrams contradict: central is called the host executor and appears to control lab instances. The Local Lab Manager should be named as the sole lab-resource lifecycle owner if that is the intended architecture.
5. **Call and observe:** Capsule runtime calls the CC through its guarded interface. Provider returns a stable job handle and execution observations. The local AI4R/capsule runtime checks scientific output and stores a receipt/artifact record; the Local Lab Manager only reports status and manages owned resources. The notes state the right split, but slide 3 compresses verification into the manager/executor area and visually obscures it.
6. **Return result:** Local AI4R reports status, report artifact reference, native run ID, CC release digest, and evidence through Local Lab Manager → Central Lab Manager. Candidate CC changes remain in Lab A’s private registry. Slide 3 has this path abstractly, but the identity relationship is not explicit enough to distinguish native run ID, manager request ID, and container job handle.
7. **Recovery/cancel:** After a lost reply, the same manager request ID is queried; do not submit a second native run. Cancellation asks native AI4R to checkpoint/cancel, then Local Lab Manager stops only the job/service it owns. The deck states the principle but omits the user-visible unknown-delivery resolution and restart owner.
8. **Withdraw CC:** Lab A disables future selection of that release, drains/cancels the service, removes only its own instance and retains evidence, artifacts, release identity, and declared persistent service data. Slides 2 and 8 assert retention but do not specify the retained objects or distinguish release withdrawal from instance uninstall. Shared image layers must not be pruned if another lab uses them.
9. **Propose central adoption:** Lab A emits a candidate reference and summary, not a code/image transfer into central storage. A named human reviews and explicitly approves the transfer/push, then separately approves or performs merge/publication. The notes require this but the visible rose arrows make the order ambiguous. Lab B receives no direct message and no writable shared state.

**Result:** the task is coherent as an architecture intent, but the deck is not yet operationally unambiguous. The main blocker is the owner of lab execution resources (central versus local); next are the exact approval boundary and the image/instance lifecycle. Resolve these and the same task can be traced consistently from request through recovery and human adoption.

## Overall review

The deck is visually clean and the 8-slide count fits the requested limit. It puts the complete topology first, keeps reuse after architecture, and avoids the prohibited M2a naming. The strong points are the explicit no-peer-lab rule, human approval intent, stable-identity/recovery concern, and separation of research acceptance from process success. Before this becomes an approval deck, fix the cross-slide execution ownership contradiction, clarify exactly what crosses the human gate, and make the CC lifecycle concrete enough to answer “who installs, runs, and removes this instance?” without consulting the notes.
