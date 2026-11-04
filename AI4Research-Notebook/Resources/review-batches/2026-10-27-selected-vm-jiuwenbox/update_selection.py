"""Checkpoint 2: reconcile selected architecture in notes, without deck/runtime edits."""
from pathlib import Path
import hashlib,json

B=Path(__file__).resolve().parent
V=B.parents[2]
rows=[]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(rel,text):
    p=V/rel
    if p.exists():
        raw=p.read_bytes();dest=B/'before'/(rel.replace('/','__')+'.snapshot')
        dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists()
        dest.write_bytes(raw);assert digest(raw)==digest(dest.read_bytes())
        rows.append({'path':rel,'before_sha256':digest(raw),'snapshot':dest.relative_to(V).as_posix()})
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes((text.strip()+'\n').encode('utf-8'))
def replace(text,old,new):
    assert old in text,old
    return text.replace(old,new,1)
def read(rel):return (V/rel).read_text('utf-8')

prompt='we will use VM-per-lab and selective jiuwenbox reuse. that is what i intended for the design to look like. we are meant to be compatible with openjiuwen stuff as in theory we will contribute to it when we have good findings.'
prompt_rel='Sources/Prompts/2026-10-27-select-vm-jiuwenbox-upstream.txt'
save(prompt_rel,prompt)
manifest=json.loads(read('Sources/capture-manifest.json'))
manifest.append({'path':prompt_rel,'sha256':digest((prompt+'\n').encode()),'capture_method':'exact visible user message, UTF-8 LF','captured_date':'2026-10-27'})
save('Sources/capture-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))

rel='Designs/Sandbox Lab Design.md';t=read(rel)
t=replace(t,'status: m2-proposal-runtime-unverified','status: selected-architecture-runtime-unverified')
t=replace(t,'last_reviewed: 2026-10-26','last_reviewed: 2026-10-27')
t=replace(t,'next_action: Review the adaptive research loop and first workload experiment before specifying M2','next_action: Qualify the selected VM and JiuwenBox adapter boundaries; prepare the evidence appendix as the next checkpoint')
heading='# Sandbox Lab Design'
selection='''
**Selected October 27:** one VM per lab with selective JiuwenBox reuse. This is the user-selected M2 architecture, not a deployed or compatibility-qualified system. [[Designs/Lab Design Comparison]] retains the alternatives and source evidence.

![Selected VM-per-lab deployment](Lab%20Design%20Comparison/02-vm-per-lab.png)

[Scalable deployment view](Lab%20Design%20Comparison/02-vm-per-lab.svg). This is the selected deployment view; earlier optional-VM or shared-host-only placement is superseded. The comparison drawing shows the boundary and lifecycle, while the reuse allocation below identifies the selected software roles.

| Layer | Selected direction |
|---|---|
| Lab boundary | A Linux VM per lab, its own guest environment and Docker Engine; people primarily connect to their lab interface and may directly administer their guest |
| Research runtime | The lab's complete independently versioned AI4R, including research, planning, checking, memory, capability library, factory and RSI |
| Capability execution | Vendored OCI/container CCs include their tool implementations and software dependencies; a stable supervisor owns scoped execution and Engine access |
| JiuwenBox reuse | Reuse compatible tool/sandbox lifecycle and job-control mechanisms through an adapter; its bubblewrap sandbox is distinct from our OCI carrier and outer VM |
| Shared services | Inference and other configured services have authenticated network endpoints; they may be co-located or remote and survive one lab stopping |
| Outside control | Host/provider VM start, shutdown and forced stop remain available independently of the guest's AI4R; project deletion remains separate |

### OpenJiuwen compatibility and contributions

OpenJiuwen compatibility is an explicit engineering target. Start from its supported extension/provider interfaces and the actual dependency pin. Keep AI4R-specific contracts behind narrow adapters, document necessary extensions, and avoid coupling the research loop to a workspace platform's choices. Selective reuse permits replacing an unsuitable implementation while retaining compatible interfaces where practical. It does not imply that every upstream backend already satisfies our containment, persistence or acceptance requirements.

Compatibility must be demonstrated for the selected versions: tool I/O and failures, job cancellation and actual termination, retained state/restart, and scoped access. Source presence or a no-op base lifecycle method is not a passing integration result. Do not inherit destructive default teardown as the durable lab's stop behavior.

Useful generic fixes, adapters, reusable components and research findings can become contribution candidates for upstream OpenJiuwen, with reproducible examples/tests and the required dependency information. Adoption into our central AI4R release and acceptance by upstream OpenJiuwen are separate processes. This direction authorizes neither publishing a contribution nor claiming upstream endorsement or tested compatibility.
'''
t=replace(t,heading,heading+'\n\n'+selection)
t=replace(t,'It is the current M2 proposal for discussion, not implemented adaptive execution or an amendment to M1.','The deployment boundary and selective JiuwenBox reuse are selected; detailed M2 mechanisms remain proposals, not implemented adaptive execution or an amendment to M1.')
t=replace(t,'Use one permitted Linux Docker host for the first slice. Compose can host AI4R and any required application service. An existing narrow controller/broker interface owns launch, limits, stop and reconciliation. Agents receive scoped operations and resource handles; the controller owns Docker access and policy. A VM remains an optional outer profile, chosen for a demonstrated isolation or deployment requirement. Spark is optional execution hardware, with build preparation elsewhere where practical.','Use one permitted Linux lab VM for the first slice, with its own Docker Engine. Compose hosts the lab AI4R and required application services. A stable VM-local controller owns scoped launch, limits, stop and reconciliation, selectively adapting JiuwenBox where compatible. Agents receive scoped operations and resource handles; the controller owns Engine access and policy. Host/provider control can stop the entire VM if guest control fails. The VM is the selected lab boundary; provider support and any accelerator access still require qualification. Spark remains optional hardware, with preparation elsewhere where practical.')
t=replace(t,'No runtime compatibility or speedup was tested for this design update.','No runtime compatibility or speedup was tested for that source review or this architecture-selection update.')
save(rel,t)

rel='Designs/Lab Capsule and Factory Design Plan.md';t=read(rel)
t=replace(t,'last_reviewed: 2026-10-26','last_reviewed: 2026-10-27')
t=replace(t,'# M2 sandbox plan: prove adaptive research first','# M2 sandbox plan: prove adaptive research first\n\n**Selected deployment:** one VM per lab and selective JiuwenBox reuse, with OpenJiuwen compatibility and upstream contribution potential as explicit targets. The complete AI4R, including RSI and factory, belongs to each lab. [[Designs/Sandbox Lab Design]] owns the selected placement and adapter boundaries; checkpoint 1 remains the comparison history. No deployment or compatibility result is implied.')
t=replace(t,'M2 remains a proposal.','The lab boundary and reuse direction are selected; detailed M2 integration remains a proposal.')
t=replace(t,'Use one permitted Docker host with bounded jobs and an external stop path.','Use one permitted Linux lab VM with its own Docker Engine, bounded jobs and a host/provider stop path independent of guest AI4R. Selectively reuse JiuwenBox behind an adapter while keeping OCI package execution and whole-VM control distinct.')
t=replace(t,'One lab and a small stateful fixture are sufficient; Spark, GPU, robotics and a VM remain optional profiles with separate qualification.','One VM lab and a small stateful fixture are sufficient; Spark, GPU and robotics remain optional profiles with separate qualification. Verify supported OpenJiuwen tool/provider behavior, actual cancellation/termination and retained-state restart at the selected pins. Preserve reproducible generic findings for possible upstream contributions.')
t=replace(t,'| A second project or stronger boundary is needed | Second independent lab and optional VM profile |','| A second project is needed | Second independent lab VM |')
save(rel,t)

rel='Designs/Labs and Capability Capsules.md';t=read(rel)
t=replace(t,'status: m2-proposal-runtime-unverified','status: selected-architecture-runtime-unverified')
t=replace(t,'last_reviewed: 2026-10-26','last_reviewed: 2026-10-27')
t=replace(t,'A human sets the direction;','People set the direction;')
t=replace(t,"Each lab has its own AI4R fork, capabilities, applications and project state. Selected improvements can return to central AI4R through separate qualification.","Each lab VM contains its own complete AI4R version, including RSI, factory, capabilities, applications and project state. People primarily use its lab interface and may administer the VM directly. Selective JiuwenBox reuse and compatibility with OpenJiuwen are selected design directions. Selected improvements can return to central AI4R through qualification; useful generic findings and components can separately become upstream OpenJiuwen contribution candidates.")
t=replace(t,"A lab's sandbox bounds execution mistakes and runaway work and preserves the project through interruption.","The selected lab boundary is a VM with containerized CCs inside it. A stable local supervisor selectively reuses JiuwenBox for compatible execution/lifecycle functions; external host/provider control can stop the VM if AI4R hangs. Normal stop preserves data and remains separate from deletion. Shared inference and other configured services can be on another machine. These controls are designed to bound execution mistakes and preserve the project through interruption; they still need runtime qualification.")
save(rel,t)

rel='Designs/Lab Design Comparison.md';t=read(rel)
t=replace(t,'status: comparison-for-discussion-not-selected','status: comparison-complete-option-b-selected')
t=replace(t,'next_action: Discuss the lab boundary and reuse choice before changing the current architecture or deck','next_action: Use the selected Sandbox Lab Design; retain this note as the checkpoint 1 comparison')
t=replace(t,'# Lab designs: which boundary fits our work?','# Lab designs: which boundary fits our work?\n\n**Subsequent decision, October 27:** the user selected option B, VM per lab, with selective JiuwenBox reuse and OpenJiuwen compatibility/contribution goals. [[Designs/Sandbox Lab Design]] now owns that selected architecture. The comparison and original recommendation below remain checkpoint 1 evidence, not a deployment result.')
save(rel,t)

rel='Designs/Sandbox Lab Diagrams/README.md';t=read(rel)
t=replace(t,'# Sandbox Lab Diagrams','# Sandbox Lab Diagrams\n\n**October 27 deployment selection:** use [the selected VM-per-lab view](../Lab%20Design%20Comparison/02-vm-per-lab.svg) and [[Designs/Sandbox Lab Design]] for current placement and selective JiuwenBox reuse. View 2 below retains the earlier optional-VM/shared-host proposal and is superseded for deployment choice. The other views remain supporting logical diagrams, not runtime evidence.')
save(rel,t)

rel='Decisions/Decision Register.md';t=read(rel)
t=replace(t,'| Decision | State | Evidence |\n|---|---|---|','| Decision | State | Evidence |\n|---|---|---|\n| VM per lab, selective JiuwenBox reuse, OpenJiuwen compatibility and contribution target | Selected by user October 27; runtime qualification pending | [[Sources/Prompts/2026-10-27-select-vm-jiuwenbox-upstream.txt]] · [[Designs/Sandbox Lab Design]] |')
save(rel,t)

for rel,old,new in [
 ('Home.md','[[Designs/Lab Design Comparison|Lab design comparison: checkpoint 1]] — matched diagrams, pros/cons, OpenJiuwen reuse and shutdown paths; boundary selection remains open.','[[Designs/Lab Design Comparison|Lab design comparison: checkpoint 1]] — matched diagrams and pros/cons. **Selected:** VM per lab with selective JiuwenBox reuse; [[Designs/Sandbox Lab Design]] records checkpoint 2 and OpenJiuwen compatibility/contribution goals.'),
 ('Sources/Implementation Intent.md','# Current intent and working requirements','# Current intent and working requirements\n\n**Selected October 27:** VM per lab and selective JiuwenBox reuse. Each VM contains its complete independently versioned AI4R. OpenJiuwen-compatible interfaces and potential upstream contributions are explicit targets. [[Designs/Sandbox Lab Design]] records the selection and remaining qualification; [[Designs/Lab Design Comparison]] preserves the prior comparison. Architecture notes are updated as checkpoint 2; presentation evidence is still checkpoint 3.'),
 ('Designs/Design Library.md','It does not replace the current proposal or expand the deck.','The user subsequently selected VM per lab and selective JiuwenBox reuse. [[Designs/Sandbox Lab Design]] owns checkpoint 2; the deck has not yet been reconciled.'),
 ('Workstreams/Lab Infrastructure.md','One permitted Docker host is sufficient for the initial deployment profile. Qualify actual limits, access, stop/recovery and backup/restore. VMs, Spark, local inference, robotics, factories and additional labs enter when the chosen research or isolation needs justify them.','The selected initial deployment is one permitted lab VM with its own Docker Engine and selective JiuwenBox reuse. Qualify actual limits, guest access, experiment/lab stop, independent host/provider VM stop and backup/restore. OpenJiuwen-compatible interfaces and potential upstream contributions are explicit targets. Spark, local inference, robotics and additional labs enter when needed.'),
 ('Designs/Sandbox Briefing/presentation/README.md','# Sandbox design presentation','# Sandbox design presentation\n\n**October 27 freshness notice:** the user selected VM per lab, selective JiuwenBox reuse and an OpenJiuwen compatibility/contribution target. [[Designs/Sandbox Lab Design]] contains checkpoint 2. This deck remains the October 26 presentation; its placement and reuse explanation needs checkpoint 3 reconciliation before presenting it as the selected architecture.'),
]:
    t=read(rel);save(rel,replace(t,old,new))

rel='Sources/Prompt Register.md'
save(rel,read(rel)+'\n\n- [[Sources/Prompts/2026-10-27-select-vm-jiuwenbox-upstream.txt]] — selects VM per lab and selective JiuwenBox reuse, targeting OpenJiuwen compatibility and future contributions; recorded in [[Designs/Sandbox Lab Design]].')

(B/'receipt.json').write_bytes((json.dumps({'checkpoint':2,'date':'2026-10-27','scope':'Selected architecture, reuse allocation, delivery-plan and notebook reconciliation only; deck/runtime unchanged','before':rows,'runtime_validation':'NOT_RUN; selection is not compatibility acceptance'},indent=2)+'\n').encode())
print('Selected architecture recorded and notes reconciled; deck/runtime unchanged.')
