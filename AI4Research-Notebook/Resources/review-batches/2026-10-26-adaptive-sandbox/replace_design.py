from pathlib import Path
import hashlib
import json
import subprocess
import importlib.util

V = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
rows = []

def sha(raw): return hashlib.sha256(raw).hexdigest()

def save(rel, content):
    p = V / rel
    if p.exists():
        raw = p.read_bytes()
        target = B / 'before' / (rel.replace('/', '__') + '.snapshot')
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(raw)
            assert sha(target.read_bytes()) == sha(raw)
        if not any(r['path'] == rel for r in rows):
            rows.append({'path': rel, 'before_sha256': sha(target.read_bytes()), 'snapshot': str(target.relative_to(V))})
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')

def meta(identity, title, action, body):
    return f'''---
id: {identity}
status: m2-proposal-runtime-unverified
source: Sources/Prompts/2026-10-26-adaptive-sandbox-replacement.txt; https://chatgpt.com/share/6adf9a5b-2320-83e9-afeb-ff63c4f96671
last_reviewed: 2026-10-26
next_action: {action}
---
# {title}

{body}'''

save('Designs/Sandbox Lab Design.md', meta('sandbox-lab-design-m2', 'Sandbox Lab Design',
    'Review the adaptive research loop and first workload experiment before specifying M2', '''
A sandbox lab is a durable research project in which AI4Research can investigate a goal, learn that its first approach was wrong, and choose better next experiments without losing useful work. The sandbox supplies bounded execution and recovery; AI4R supplies the research decisions; capability capsules supply the tools and specialist work. The design succeeds only if that combination makes our research more useful at an acceptable cost.

The central change is **persistent goals, revisable strategy, and durable execution**. We keep AI4R's capability and checking machinery and change when future work becomes committed. Plan to the next meaningful uncertainty boundary, observe the result, then decide what follows. Several justified independent tasks can still run together.

This replaces the previous sandbox explanation and delivery order. It is the current M2 proposal for discussion, not implemented adaptive execution or an amendment to M1. Start with the [research-loop diagram](Sandbox%20Lab%20Diagrams/04-adaptive-work.png), then the [delivery plan](Lab%20Capsule%20and%20Factory%20Design%20Plan.md). Other deployment/package diagrams are supporting detail.

## The AI4R problem this solves

Our first lab investigates workload profiling and whether historical traces can help predict hardware needs on other machines with limited direct access. Before investigating, AI4R may not know which counters are available, whether traces are comparable, or whether a proposed performance unit transfers. A full experiment DAG commits to answers that research is supposed to discover. Better capsules alone do not remove that mismatch.

At the inspected M1 checkpoint, `Scheduler.run` receives the Compiler Brief, obtains a static or Planner proposal, calls the protected binder's `freeze`, and executes that plan. The bounded planning correction/linked continuation handles specified planning failures; it is not ongoing scientific replanning. The source does **not** establish that initial intent compilation happens after planning. The remaining issue is that a compiled brief cannot contain the findings of investigation that has not yet run. Later clarification may also change the task. [Source evidence](#evidence-and-reuse).

For example, start with “test whether normalized workload features predict memory demand on a held-out machine.” Clarify the data, success measure, budget and web permission. Inspect authorized traces first. If counters have incompatible meanings, replace the planned model-fitting work with a comparability experiment or narrow the claim. Retain unrelated valid measurements. If web access is denied, use supplied material and report the evidence gap. Neither a failed premise nor missing permission should trigger an invented finding.

## Three kinds of state, within the existing runtime

| State | Contains | Changes when |
|---|---|---|
| Research objective | Human direction, completion criteria, authoritative constraints and permissions; separately labelled hypotheses and open questions | The human revises intent, or authorized clarification resolves it; observations update knowledge without becoming user instructions |
| Working strategy | Current explanation of how to reach the goal, assumptions, unresolved subgoals and next investigation boundary | Material evidence changes the approach, a prerequisite fails, or progress stalls |
| Execution record | Concrete CC invocations, inputs, versions, assigned checks, effects, job status and results | The runtime dispatches and records work; a revision creates new work rather than rewriting an executed attempt |

These are records and responsibilities in AI4R, not three new services. The strategy may describe distant work provisionally. Only the next justified batch becomes an executable DAG with fixed invocation contracts. The project objective outlives those batches and individual agent sessions.

![Adaptive research with bounded execution](Sandbox%20Lab%20Diagrams/04-adaptive-work.png)

## How the loop works

1. **Clarify and constrain.** Resolve enough intent, resources, cost and completion criteria to choose useful work. Substantive web investigation waits for permission. Missing information blocks dependent work; unrelated permitted work can continue. In unattended mode, an unanswered required clarification produces a visible waiting state rather than a guessed answer.
2. **Plan a bounded investigation.** Select existing operations and a batch whose relevance follows from current knowledge. State what result would change the strategy. An investigation boundary is explicit: do not invent the downstream experiment before its prerequisite findings exist.
3. **Bind and execute.** Existing protected machinery checks types, required inputs, effects, resources, budgets and mandatory checks. The dispatcher rechecks current permission and resource availability. The infrastructure controller runs the authorized work and retains its outcome.
4. **Assess the result.** Host checks and the selected review profile assess assigned obligations. Acceptance of an artifact does not establish that the research objective is achieved. A negative or inconclusive result can be useful and accepted; a crash or missing artifact remains an operational failure.
5. **Continue or revise.** Routine observations update knowledge without invoking a full planner. Reconsider strategy at a declared investigation boundary, changed user direction/permissions, invalidated assumption, missing prerequisite, unrecoverable failure, or idle work with unmet goals. A bounded no-progress review catches missed triggers. Stop when completion criteria are supported, the budget is spent, or a blocker requires intervention.

Begin with explicit boundaries and deterministic trigger rules. A capability can suggest that a result matters, but its suggestion is an observation, not permission to mutate the plan. Evaluate a semantic staleness detector only if the first trial shows that fixed rules miss valuable changes or cause excessive planning. Planning calls, checks, failures and repair attempts all consume the cumulative project budget. Enforce a revision/no-progress bound and report why work stopped.

Specialists can adjust methods inside their assigned objective, budget and effects. They escalate discoveries that change shared assumptions, completion criteria or another branch. A central planner need not micromanage source selection or every analysis step. Larger composite capabilities remain subject to the same external obligations and limits.

## Revising work without corrupting results

The initial migration is a new bounded batch after a completed investigation, with explicit import of accepted, still-relevant artifacts. This is an extension of current execution, not a claim that the M1 scheduler already accepts arbitrary cross-run outputs. Its same-run proof checks need an explicit M2 transfer contract.

If concurrent research later needs revisions within a running project, the Planner proposes a scoped patch against a specific plan and knowledge revision. The runtime commits it atomically only if that revision is still current, dependencies are acyclic, inputs remain valid, and permissions, checks and cumulative budgets are satisfied. Reject a stale proposal and recompute from current state. Patch validation controls execution legality; it does not prove scientific wisdom.

| Existing work | Revision behavior |
|---|---|
| Unstarted | Withdraw or replace before dispatch; rebind against current state |
| Running and independent | Keep original contract and let it finish; do not change its version in place |
| Running and affected | Fence new dependent work; cancel if necessary and supported, otherwise reconcile completion and quarantine its output from the active strategy |
| Completed and still relevant | Reuse only with accepted artifact identity, compatible scope/assumptions, implementation and check context |
| Completed but premise changed | Preserve the historical result, mark its current use invalid and prevent affected descendants from consuming it |
| Failed or effect uncertain | Retain the attempt; inspect actual job/service state before retrying; never blindly replay an external effect |

An accepted result can become irrelevant without becoming historically false. Cache equality alone cannot establish validity: a prompt can stay unchanged while a dataset, permission, application state or hidden dependency changes. Track the dependencies that matter for reuse, conservatively rerunning affected work when they cannot be established. A revoked permission stops new prohibited dispatch immediately and requests cancellation of affected active work; it cannot undo data already transmitted.

Local qualified CC updates become eligible for new bindings automatically under the lab's compatibility policy. They do not replace active invocations or sessions. A new version is a reason to consider a better method, not a mandatory global replan. The CC factory produces candidates; the RSI owner controls broader improvement and harness changes; independent qualification controls admission. Central AI4R adoption remains separate from local eligibility.

## What the sandbox supplies

A lab retains its own AI4R fork, goal/knowledge records, CC selection, application state and research artifacts. Deployment instances are replaceable. A restart reloads the research state and reconciles outstanding work before dispatch; the planner must not reconstruct everything from conversation alone.

Use one permitted Linux Docker host for the first slice. Compose can host AI4R and any required application service. An existing narrow controller/broker interface owns launch, limits, stop and reconciliation. Agents receive scoped operations and resource handles; the controller owns Docker access and policy. A VM remains an optional outer profile, chosen for a demonstrated isolation or deployment requirement. Spark is optional execution hardware, with build preparation elsewhere where practical.

| Existing responsibility | What this proposal requires | Why it matters to research |
|---|---|---|
| AI4R Planner/runtime | Project state, next-batch selection, progress assessment and revision | New evidence can change the next experiment |
| Binder, dispatcher and checks | Fixed invocation contracts, current authorization, independently assigned checks, accepted artifact transfer | Adaptation cannot bypass the checks that make results usable |
| Lab controller | Resource/deadline limits, scoped files/network, mutable-service leases, external stop and job reconciliation | Runaway or conflicting experiments do not destroy the project |
| Durable storage | Separate project records, accepted artifacts, application checkpoints, scratch and secrets; verified independent backup/restore | A replaced app or failed experiment does not erase accumulated work |
| CC factory and qualification | Candidate construction, fixed independent criteria, compatible future eligibility | Acquire missing functionality only when a real research need justifies it |

Containment targets mistakes, faulty harness changes and runaway experiments. Container names and model instructions do not establish isolation. Qualify effective mounts, network policy, process/resource limits and disk behavior on the selected host. Keep control policy and the stable recovery path outside mutable candidate code. Disk pressure stops growth rather than deleting unique findings. Restore must fence the old writer and verify the required data, not merely restart a process. Measurement jobs need an exclusive slot or an explicit co-running-load limitation.

CC packages can expose several named operations over an embedded tool, batch job or managed/attached application. Bind the selected operation to exact implementation, inputs, effects and application identity. An attached endpoint grants no implicit reset/upgrade authority. Stateful applications declare reset/checkpoint semantics and serialize conflicting commands. A durable job handle represents submission/progress, not scientific acceptance. Robotics can validate this later; a small stateful fixture can test protocol behavior first without claiming simulator integration.

Review payloads follow the selected qualified profile. Historical output-only review remains available; the October 26 checkpoint also has opt-in evidence-aware review, with its own limits. This planning change neither silently broadens reviewer access nor treats an older output-only description as the only current mode. [Current review evidence](../Activities/2026-10-26%20M1%20Reliability%20and%20ML%20Readiness%20Checkpoint.md).

## Evidence and reuse

Source inspected on October 26: our published M1 `ab0d9c7fe8ceadf45c61d04e94e2dd9b44b867a7`, read from Git objects in the reviewed-integration checkout; installed OpenJiuwen SDK source `9e3390195a9ea15235b2b5f7412cb2aa440622cc`; upstream JiuwenSwarm checkout `02b37f47fbefe80a58e4ed88606120818ca44ac3`. Those identities describe different codebases. No runtime compatibility or speedup was tested for this design update.

| Evidence | Supported design inference | Limit |
|---|---|---|
| M1 `research/scheduler.py`: `run`, `binder.freeze`, `_committed_node`; `planning.py`: bounded continuation | Keep existing execution/checking and introduce explicit project/batch boundaries | Current same-run and frozen-plan proofs do not directly permit mutable or cross-batch execution |
| M1 `research/native.py`: tools/subagents disabled, task loop/planning disabled, `enable_swarmflow=False` for the Planner Leader | Narrow orchestration is deliberate in our adapter | It is not a missing upstream capability; simply enabling flags would bypass the integration design |
| Pinned SDK `harness/goal/{schema,manager,store}.py` | Persistent goals and budget/progress state offer a reuse candidate | Its completion assessments are not independent scientific acceptance |
| Pinned SDK `agent_teams/workflow/engine/journal.py`: `call_signature`, `get_cached`; `primitives.py`: `agent`; `runtime.py`: `run_id` | Structural path, content signature and run isolation support selective workflow replay | Prompt/options/schema reuse is not complete research-dependency validation or arbitrary live-DAG patching |
| [JiuwenSwarm release notes](https://github.com/openJiuwen-ai/jiuwenswarm/releases): persistent goals; SwarmFlow modify/replay with unchanged-operator cache | Investigate upstream goal/replay mechanisms before building equivalent machinery | Release descriptions alone do not prove coexistence with independent live branches |
| [Magentic-One](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html): task and progress ledgers, stall-driven revision | Separate enduring task understanding from progress and next action | Frequent orchestration can cost more; no AI4R benefit follows from its benchmarks |
| [SyncPlan](https://arxiv.org/abs/2608.01652) and [Learning When to Plan](https://arxiv.org/abs/2509.03581) | Test selective replanning rather than assuming every result deserves a new plan | Their environments and learned mechanisms do not establish transfer to AI4R research |
| [Temporal workflow messages](https://docs.temporal.io/develop/python/workflows/message-passing) | External events and durable execution have established implementation patterns | A pattern reference; adopting another runtime is not a prerequisite |

The first reuse investigation should exercise the pinned SDK goal/replay paths through a small adapter spike and compare the work needed with extending our existing store and scheduler. Do not replace the framework just to obtain a loop. JiuwenSymbiosis and LangGraph are optional follow-up references; neither is a dependency of this proposal.

## Evidence that would make this valuable

The first demonstration uses workload research with a controlled late discovery: initially comparable-looking traces turn out to have incompatible counter semantics. AI4R should replace the dependent fitting step with a useful comparability investigation or a narrower supported conclusion, preserve an unrelated valid measurement, and respect a no-web policy. Repeat with a user scope change, a failed prerequisite and a process interruption. A driver can test mechanics; only an actual Planner-selected change demonstrates autonomous adaptation.

Compare the same capabilities, task inputs, injected discovery, checking criteria, model configuration and total budget under three planning policies: fixed initial DAG, replanning at every batch boundary, and selective replanning. Use independently assessed research quality, correct responses to changed information, stale-result consumption, reuse of unaffected work, planning/checking cost, total runtime and recovery behavior. Freeze the scoring rules before the runs; report all attempts and a useful negative result if adaptation does not help. Use held-out discovery cases and repeated paired trials before asserting general benefit.

The case for this structure is strongest if selective replanning improves independently verified outcomes on changing-information tasks, preserves static-task quality, and costs less than frequent replanning at comparable quality. Set the acceptable cost and quality tradeoff before measurement. We have not established any of these outcomes yet. One controlled successful revision establishes feasibility only; a short restart trial does not establish day-long autonomy. Hardware-transfer prediction accuracy and CC effectiveness remain separate experiments.

The remaining discussion choices are the first uncertainty boundary, the quality/cost tradeoff, which upstream goal/replay pieces fit our checks, and when concurrent live patches become necessary. The [replacement plan](Lab%20Capsule%20and%20Factory%20Design%20Plan.md) orders the work around those questions. Earlier VM, container and factory notes are implementation references only where compatible with this proposal.
'''))

save('Designs/Lab Capsule and Factory Design Plan.md', meta('vm-cc-factory-design-plan',
    'M2 sandbox plan: prove adaptive research first', 'Agree the first workload scenario and evidence criteria, then register a bounded implementation slice', '''
The first delivery is one durable workload-research lab that changes its next experiment when new evidence invalidates its approach. Use existing AI4R capsules, checking, storage and OpenJiuwen integration wherever they fit. Expand packaging, factories and deployment only when a demonstrated research need requires them.

This replaces the earlier VM-first, carrier-first and factory-first delivery order. [[Designs/Sandbox Lab Design]] owns the current explanation and evidence; [[Designs/Labs and Capability Capsules]] is the short overview. M2 remains a proposal. M1 runs and its published checkpoint retain their existing contracts.

## 1 Establish the smallest useful change

Agree one workload question, authorized data, no-web/web policy, resource budget, independent success criteria and a discovery that should change the next step. Inspect the target repository's current instructions and native task allocation before implementation. Recheck the current source rather than treating a notebook snapshot as today's code.

The inspected M1 scheduler freezes one run and verifies same-run producer proofs. Its bounded planning continuation is not research adaptation. The pinned OpenJiuwen SDK already contains persistent goals and journal-based selective replay. Exercise those paths in a small compatibility spike: show what our binder/checking/store can reuse, what requires an adapter, and whether cache identity captures the dependencies needed for this case. A different runtime is justified only by a concrete gap and measured integration advantage.

**Exit:** a reviewable mapping of the existing goal, planner, scheduler, checks and store to one objective and two investigation batches; one selected reuse path; explicit handling of accepted artifact transfer. No new generic registry, planning service, VM fleet or factory is required.

## 2 Demonstrate one evidence-driven revision

Implement persistent objective/knowledge/strategy state and a next-batch planning boundary. Begin after clarification and before substantive permitted investigation. Re-enter clarification when needed. Bind each dispatched batch through the existing protected path. Transfer accepted artifacts explicitly between batches with scope, dependency and check validation; do not relax current same-run proofs into arbitrary artifact reads.

Run the workload scenario: inspect traces, discover incompatible counters, revise the future experiment, retain a valid unrelated measurement, and produce a justified next action or narrower finding. Keep user permissions authoritative. A candidate's recommendation or successful process exit cannot make its own result accepted or change the goal's completion criteria.

**Exit:** an actual Planner selects the changed next experiment after observing the result. Retained output and independent assessment show why the change was useful. A controlled driver establishes protocol behavior only. Include a no-web case, missing input, rejected output and a valid scientific negative. Stop at the cumulative cost/revision/no-progress limits with a visible outcome.

## 3 Make that lab survive interruption

Use one permitted Docker host with bounded jobs and an external stop path. Keep project state and accepted artifacts outside replaceable app processes. Reconcile interrupted jobs and uncertain effects before retrying. Test restart and a verified restore into a replacement deployment, fencing the old writer. Exercise timeout/cancel, storage exhaustion and stale artifact rejection. Measurement interference must be controlled or reported.

**Exit:** the lab resumes the intended research state, avoids duplicate effects and preserves usable findings. Check effective access, network and resource limits on the actual host. A fixture-only success is not host isolation evidence. One lab and a small stateful fixture are sufficient; Spark, GPU, robotics and a VM remain optional profiles with separate qualification.

## 4 Decide whether selective planning earns its cost

Compare fixed initial planning, revision at every batch boundary and selective revision. Keep capabilities, model, inputs, discovery schedule, permissions, total budget and evaluation criteria matched. Freeze the acceptable cost/quality tradeoff first. Score outcomes independently; include no-change tasks, scope changes, misleading observations, failed prerequisites and interrupted work. Repeat paired trials on held-out cases; report quality, stale reuse, recovery, planner/checking cost and elapsed time, including failures.

**Exit:** an evidence-based decision to keep, simplify or revise the mechanism. The smallest prototype proves feasibility; repeated controlled comparisons are needed for a value claim, and a representative extended run is needed for long-duration operation. The planner-strength/capability-composition study is separate so it does not confound this planning-policy comparison.

## Expand only where the evidence points

| Observed need | Next extension | Required evidence |
|---|---|---|
| Independent useful work is delayed by global barriers | Scoped patches while unaffected branches continue | Atomic revision conflict rejection, invalidation closure, cancellation/obsolete-output handling, no stale dispatch |
| Missing capability repeatedly blocks useful research | Manual package, then factory-assisted production | Measured integration effort, independent conformance and useful task contribution; compatible local future adoption |
| Stateful domain service is required | Managed/attached application binding | Session leases, reset/checkpoint behavior, recovery and compatible updates |
| A second project or stronger boundary is needed | Second independent lab and optional VM profile | Separate writable state/access, restore, selective contribution and measured resource cost |
| New harness behavior is useful | RSI-owned platform candidate | Evaluation against incumbent behavior; candidate cannot change its own acceptance criteria |

Factories still produce CC candidates, including packages with several operations. Qualification controls eligibility; automatic compatible local updates apply to new bindings only. Whole-harness RSI has its own owner. Central adoption is a separate decision. These responsibilities are retained without making every extension a prerequisite for testing adaptation.

## Decisions for our design walkthrough

Use one worked example to choose the first uncertainty boundary and demonstrate what survives a plan change. Agree how much quality improvement or wasted-work reduction would justify the extra cost. Review the goal/replay reuse spike and artifact-transfer rule before deciding whether live patching is necessary. Then show the objective, current evidence, next batch, revision reason and stop condition in the proposed presentation.

The honest presentation claim today is: our source has governed fixed-plan execution and upstream mechanisms worth reusing; this design proposes testing adaptive research on top. No improvement percentage, generalized day-long autonomy, cross-hardware predictor accuracy or deployed multi-lab factory is established.
'''))

save('Designs/Labs and Capability Capsules.md', meta('labs-and-capability-capsules-overview',
    'AI4Research Labs and Capability Capsules', 'Review one workload journey with a late discovery and a revised next experiment', '''
AI4Research is intended to sustain long research projects across agent sessions. A human sets the direction; a lab investigates hypotheses, analyzes data, writes code, runs experiments and retains useful findings. Each lab has its own AI4R fork, capabilities, applications and project state. Selected improvements can return to central AI4R through separate qualification.

A lab's sandbox bounds execution mistakes and runaway work and preserves the project through interruption. The first research domain is workload profiling and proposed hardware-demand prediction from historical traces. Robotics is a later, non-blocking application. These are research goals, not measured results.

The current design centers on **persistent goals, revisable strategy, and durable execution**. Research can invalidate the assumptions behind its initial plan. AI4R should plan to the next meaningful uncertainty boundary, execute a checked batch, assess the findings and revise what follows. Completed valid work remains available; changed assumptions prevent stale reuse. Permissions and completion criteria do not become editable model guesses.

![Adaptive research loop](Sandbox%20Lab%20Diagrams/04-adaptive-work.png)

CCs package callable tools, specialist agents and workflows with interfaces, effects, limits and checking obligations. A package can expose several related operations. Specialists may choose local methods within their assignment; the Planner selects useful work; protected binding and checks govern execution and acceptance; the lab controller owns resources and recovery. These are existing responsibilities, not a requirement for a new service per box.

The CC factory supplies missing functionality when justified by research, and independent qualification controls eligibility. Compatible local updates apply to future bindings. Active work stays pinned. The RSI owner handles whole-system improvement and harness candidates. Local publication does not update another lab or central AI4R automatically.

Application developers supply their ordinary interfaces, setup requirements, outputs and reset/checkpoint behavior. CC adapters connect those interfaces to research. Time-sensitive simulation or measurement stays in application code. A simulator author need not understand AI4R's entire planning system.

Start with one useful lab and existing capsules. Demonstrate a discovery that changes the next experiment, reuse of unaffected findings, no-web compliance and interruption recovery. Compare fixed, frequent and selective replanning under matched total budgets and independent scoring. Sandbox operation does not prove scientific accuracy; source support for replay does not prove arbitrary live graph mutation.

Read [[Designs/Sandbox Lab Design]] for the full explanation, source evidence and tradeoffs, and [[Designs/Lab Capsule and Factory Design Plan]] for the replacement delivery order. The [seven-view set](Sandbox%20Lab%20Diagrams/README.md) supports the walkthrough. M2 adaptive execution remains unimplemented by this documentation update; [[Resources/Current Baseline]] records M1 evidence separately.
'''))

save('Workstreams/Lab Infrastructure.md', meta('workstream-lab', 'Lab infrastructure',
    'Prove one useful adaptive workload lab before expanding infrastructure', '''
The current direction is [[Designs/Sandbox Lab Design]] with the delivery order in [[Designs/Lab Capsule and Factory Design Plan]]. A durable sandbox exists to support useful research that can change course as evidence arrives. The first slice is one workload lab, a permitted investigation, a changed next experiment and retained valid findings.

Keep AI4R's existing capsules, governed execution and checks. Investigate pinned OpenJiuwen goals and selective replay for reuse. Add project continuity and explicit next-batch planning/accepted artifact transfer before considering live graph patches. Measure whether selective replanning improves independently assessed research quality at an acceptable total cost.

One permitted Docker host is sufficient for the initial deployment profile. Qualify actual limits, access, stop/recovery and backup/restore. VMs, Spark, local inference, robotics, factories and additional labs enter when the chosen research or isolation needs justify them. Existing M1 app/runner deployment remains independent.

[[Designs/Lab Progression]] retains bounded synthetic evidence; it does not establish actual M2 or day-long research acceptance. [[Resources/Handoffs/m2-labs/README]] contains older implementation references that require reconciliation with the replacement plan. Detailed VM/container/factory and Spark notes remain optional profiles, not the current delivery sequence.
'''))

# Reconcile entrypoints without replacing other active M1 work.
for rel, old, new in [
 ('Home.md', 'current October 27 proposal route, with workload profiling first and robotics non-blocking.', 'current proposal: persistent goals, revisable strategy and durable execution; see [[Designs/Lab Capsule and Factory Design Plan|the replacement delivery plan]].'),
 ('Designs/Design Library.md', 'implementation agreements remain open.', 'the replacement [[Designs/Lab Capsule and Factory Design Plan|delivery plan]] prioritizes evidence-driven research adaptation before infrastructure expansion. Implementation agreements remain open.'),
 ('Resources/Handoffs/m2-labs/README.md', 'status: ready-for-bounded-specification', 'status: historical-handoff-requires-reconciliation'),
 ('Resources/Handoffs/m2-labs/README.md', 'next_action: Select one component and implement its first bounded slice', 'next_action: Follow the replacement adaptive research plan before selecting compatible implementation details'),
]:
    p=V/rel
    text=p.read_text('utf-8')
    assert old in text, (rel, old)
    save(rel, text.replace(old,new,1))

# Explicit entrypoint updates (preserve complete existing body).
notes = {
 'Active Stage.md': ('# CC effectiveness and a personal research lab', '**Current sandbox design:** [[Designs/Sandbox Lab Design]] and [[Designs/Lab Capsule and Factory Design Plan]] replace the infrastructure-first proposal with persistent goals, revisable strategy and checked execution batches. Prove a useful change of experiment and measure its value first. This design work does not change the separate M1 live ML priority below.'),
 'Sources/Implementation Intent.md': ('# Current intent and working requirements', '**October 26 replacement direction:** Replace the sandbox explanation and delivery plan with persistent goals, provisional strategy, fixed dispatched attempts and selective evidence-driven revision. Prioritize measurable research value and reuse existing AI4R/OpenJiuwen. [[Designs/Sandbox Lab Design]] and [[Designs/Lab Capsule and Factory Design Plan]] supersede incompatible earlier notebook interpretations and the infrastructure-first order. This is design preparation, not implementation or deployment of M2.'),
 'Designs/Agent Reading and Freshness.md': ('# Agent reading route and source freshness', '**Current replacement route:** [[Designs/Labs and Capability Capsules]] → [[Designs/Sandbox Lab Design]] → [[Designs/Lab Capsule and Factory Design Plan]]. Start with the adaptive loop and source evidence. The first value test is a changed experiment after new findings, preserving valid work. Older VM/factory handoffs are implementation references, not the current delivery order.'),
 'Project Overview.md': ('# AI4Research: what we are building and why', '**Current sandbox proposal:** Research goals persist while strategy changes with evidence. [[Designs/Sandbox Lab Design]] proposes next-batch planning with durable checked execution, reusing AI4R and pinned OpenJiuwen where suitable. [[Designs/Lab Capsule and Factory Design Plan]] replaces the infrastructure-first order with one useful adaptive workload experiment and a controlled value comparison. M2 behavior remains unverified.'),
}
for rel,(heading,note) in notes.items():
    t=(V/rel).read_text('utf-8')
    save(rel,t.replace(heading,heading+'\n\n'+note,1))

prompt='''[https://chatgpt.com/share/6adf9a5b-2320-83e9-afeb-ff63c4f96671](https://chatgpt.com/share/6adf9a5b-2320-83e9-afeb-ff63c4f96671)

work on integrating this into ai4research and updating our sandbox. this is a replacement task, dont think of it as "i gotta record prevnenace and add blah blah and more components". just update and replace the sandbox explanation and plan with these better ideas and get up to speed on ai4r, and then we can go through what the design will look like so we can present it later. we dont wanna overlciam and we always wanna have proof or evidence for why this is a good design and why we wanna structure it this way. it must have veyr high value to our project'''
save('Sources/Prompts/2026-10-26-adaptive-sandbox-replacement.txt',prompt)
manifest=json.loads((V/'Sources/capture-manifest.json').read_text('utf-8'))
manifest.append({'path':'Sources/Prompts/2026-10-26-adaptive-sandbox-replacement.txt','sha256':sha((prompt+'\n').encode()),'capture_method':'exact visible user message, UTF-8 LF; linked discussion read in browser, not a chat export','captured_date':'2026-10-26'})
save('Sources/capture-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
register=(V/'Sources/Prompt Register.md').read_text('utf-8')
save('Sources/Prompt Register.md',register+'\n\n- [[Sources/Prompts/2026-10-26-adaptive-sandbox-replacement.txt]] — replace the sandbox explanation and plan with evidence-led adaptive research; current interpretation in [[Designs/Sandbox Lab Design]].\n')

# Save the changed visual and render only its replacement, preserving the other six.
stem='04-adaptive-work'
for ext in ['mmd','svg','png']:
    p=V/'Designs/Sandbox Lab Diagrams'/f'{stem}.{ext}'
    raw=p.read_bytes(); target=B/'before'/f'{stem}.{ext}.snapshot'
    target.write_bytes(raw); assert sha(target.read_bytes())==sha(raw)
    rows.append({'path':str(p.relative_to(V)), 'before_sha256':sha(raw),'snapshot':str(target.relative_to(V))})

source='''flowchart TB
    GOAL["Persistent research goal<br/>Human constraints and completion criteria"]
    KNOW["Research knowledge<br/>Findings, hypotheses and open questions"]
    STRATEGY["Revisable strategy<br/>Plan to the next uncertainty boundary"]
    BIND["Protected binding and current authorization<br/>Next justified execution batch"]
    EXEC["Execute pinned CC invocations<br/>Bounded jobs and durable records"]
    CHECK["Assigned checks and qualified review<br/>Protected acceptance decision"]
    OBS["Retain results and observations<br/>Failure and uncertainty stay visible"]
    CHANGE{"Material change or<br/>investigation boundary?"}
    FINISH["Complete, wait or stop<br/>Criteria, blocker and budget visible"]
    GOAL --> STRATEGY
    KNOW --> STRATEGY
    STRATEGY --> BIND
    BIND --> EXEC
    EXEC --> CHECK
    CHECK --> OBS
    OBS --> KNOW
    OBS --> CHANGE
    CHANGE -->|"revise future work; keep valid results"| STRATEGY
    CHANGE -->|"no; batch still justified"| BIND
    CHANGE -->|"goal met, blocked or budget spent"| FINISH
    GOAL -.->|"authoritative limits"| BIND
    class GOAL,BIND,FINISH control
    class STRATEGY,EXEC work
    class CHECK qualify
    class KNOW,OBS,CHANGE data
'''
spec=importlib.util.spec_from_file_location('existing_renderer',V/'Resources/review-batches/2026-10-26-sandbox-design-refresh/build_diagrams.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
item=module.render((stem,'Persistent goals, revisable strategy and durable execution',source))
p=V/'Designs/Sandbox Lab Diagrams/manifest.json'
dm=json.loads(p.read_text('utf-8'))
dm['diagrams']=[item if r['stem']==stem else r for r in dm['diagrams']]
save(str(p.relative_to(V)),json.dumps(dm,indent=2))
p=V/'Designs/Sandbox Lab Diagrams/README.md'
t=p.read_text('utf-8').replace('Seven views of the [M2 sandbox design](../Sandbox%20Lab%20Design.md), prepared for the October 27 proposal.', 'Seven supporting views of the [M2 sandbox design](../Sandbox%20Lab%20Design.md). Start with view 4: persistent goals, revisable strategy and durable execution. The [replacement delivery plan](../Lab%20Capsule%20and%20Factory%20Design%20Plan.md) prioritizes a useful adaptive workload experiment.').replace('What can change during research and what remains fixed?', 'How do new findings revise future work while execution stays checked?')
save(str(p.relative_to(V)),t)

(B/'receipt.json').write_text(json.dumps({'scope':'Replacement of sandbox explanation and delivery plan; documentation and one visual only','source_m1':'ab0d9c7fe8ceadf45c61d04e94e2dd9b44b867a7','source_sdk':'9e3390195a9ea15235b2b5f7412cb2aa440622cc','upstream_jiuwenswarm':'02b37f47fbefe80a58e4ed88606120818ca44ac3','before':rows,'runtime_tests':'NOT_RUN; no adaptive implementation or scientific gain claimed'},indent=2)+'\n',encoding='utf-8')
print('Replaced sandbox design, delivery plan, overview and affected reading routes; rendered adaptive-loop diagram.')
