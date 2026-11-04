from pathlib import Path
import json, hashlib, shutil
root=Path(__file__).resolve().parents[3]
batch=Path(__file__).resolve().parent
receipts=[]
def save(rel,content):
 p=root/rel
 if p.exists():
  old=p.read_bytes(); dst=batch/'before'/(rel.replace('/','__')+'.snapshot'); dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(old)
  receipts.append({'path':rel,'before_sha256':hashlib.sha256(old).hexdigest()})
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding='utf-8',newline='\n')
def edit(rel,fn): save(rel,fn((root/rel).read_text(encoding='utf-8')))
prompt='''make multiple diagrams showing different hings, one should show inside the AI4R box and its components and its linkages to lab interface, the contaienrs coming in etc. persistent lab data looks good. i thinkt he diagram for A looks good right now, so make the slides about a design kinda like A. make sure all design decisions are packed up, and i can flip to other things to reference it and show it clearly (so i dont need to draw on the board). we should explain how shared inference can work, i think the mental model is that local LLMs can be called similarly to any API, this gives us some openness. but if the project is designed to work on model fine tuning, then yes the sandbox can also run the model, but no other sandbox can access it then. we have limited resources so thats why we need some shared services.

Keep VM per lab; use A’s visual style

we should show its more of a cycle and not like doing singular tasks 1 at a time, yes the research breif exists but it doesnt mean the system cant retry or adjust itself as it goes along naturally. this is a good structure for slides but i fear its a bit too short to explain this big concept cuz we gotta make sure people understand. lets not use the workload example. ensure that big diagrams are in the pptx you produce

the goal should be at the very start, whats the purpose of lab operating model? and exactly how its helpful for AI4Research and what value we will provide.

dont forget what i told you earlier, but if you can qoute a major figure in teh AI space near the front or a major concern they have and use it as a reference to lead into a key feature that would be excellent. recent news in ai space is also good. so if i tell you something new that doesnt mean stop adding the big diagrams
'''
rel='Sources/Prompts/2026-10-27-sandbox-system-presentation.txt'
save(rel,prompt)
mf=root/'Sources/capture-manifest.json'; entries=json.loads(mf.read_text(encoding='utf-8-sig'))
entries.append({'path':rel,'sha256':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'capture_method':'Exact visible message texts, separated by blank lines; second item is the visible clarification reply. UTF-8 LF, not a transport export.','captured_date':'2026-10-27'})
save('Sources/capture-manifest.json',json.dumps(entries,indent=2,ensure_ascii=False)+'\n')
edit('Sources/Prompt Register.md',lambda s:s+'\n- [[Sources/Prompts/2026-10-27-sandbox-system-presentation.txt|October 27 sandbox presentation directions]]: VM boundary retained, multiple large diagrams, cyclical research, shared API inference and private model policy, purpose first, sourced quote, PPTX output, no workload example.\n')
edit('Sources/Implementation Intent.md',lambda s:s+'\n## October 27 presentation reconciliation\n\nVM per lab remains selected. “Like A” means its visual style. Each lab owns the full AI4R, factory and RSI. Research is recurring and can overlap independent branches, with scoped retries. Shared inference uses configured API endpoints on the same or another host. Private model training/serving is lab-only with qualified compute and denied cross-lab access. Current explanation and presentation remove the workload example. Large editable system diagrams, an opening purpose/value statement and attributed near-front quote are cumulative requirements. The deck is a design proposal; runtime/benefit claims remain unverified. See [[Designs/Sandbox Briefing/presentation/README]].\n')
def design(s):
 s=s.replace('Qualify the selected VM and JiuwenBox adapter boundaries; prepare the evidence appendix as the next checkpoint','Review the complete system diagrams and acceptance scenarios, then qualify one bounded lab integration')
 a=s.index('Our first lab investigates workload profiling'); b=s.index('At the inspected M1 checkpoint',a)
 s=s[:a]+'A continuing research project discovers assumptions, failures and missing capabilities as it works. Committing every future experiment before those discoveries makes later work depend on guesses. The lab operating model gives each project retained state, independently evolvable AI4R and bounded execution so it can select useful next work, retry locally and overlap independent investigations. These are intended benefits to test, not measured gains.\n\n'+s[b:]
 a=s.index('For example, start with'); b=s.index('## Three kinds of state',a); s=s[:a]+s[b:]
 a=s.index('The first demonstration uses workload research'); b=s.index('Compare the same capabilities',a)
 s=s[:a]+'The first demonstration should contain a material late discovery that invalidates a planned prerequisite. AI4R should revise the dependent next work, retain unrelated valid findings, allow a local retry while independent work continues, and respect the existing scope and budget. Repeat with a scope change, failed prerequisite and process interruption. A driver tests mechanics; only actual Planner-selected changes demonstrate autonomous adaptation.\n\n'+s[b:]
 s=s.replace('Hardware-transfer prediction accuracy and CC effectiveness remain separate experiments.','CC effectiveness and long-duration reliability remain separate evaluations.')
 anchor='### OpenJiuwen compatibility and contributions'
 addition='''## System views and model placement

The [current presentation and diagram index](Sandbox%20Briefing/presentation/README.md) contains the complete deployment, AI4R internals, continuing cycle, overlapping investigations, CC intake, shared inference, private model and recovery views. These supersede the old presentation story and its workload example. The comparison drawings remain historical alternatives.

Shared model inference is a normal configured API service. The lab selects an endpoint profile containing URL, protocol/features, model identity and scoped credentials. A local model server can expose a compatible API on the same or another host. vLLM is a concrete serving candidate, not a mandatory backend. Tool calling, streaming and context behavior need compatibility checks. Sharing reduces duplicated model allocations in principle; real savings, quotas, queues and capacity require measurement. Stopping one lab must leave other clients and shared services available.

For model development or fine-tuning, the lab may run a private model with its own datasets, weights and checkpoints. Other sandboxes receive no endpoint or storage access. Enforce network and authorization boundaries and exclude private endpoints from shared service discovery. A VM does not imply accelerator access: the selected provider must qualify the lab's compute/device allocation. Unsupported hardware profiles remain unavailable. Private sharing requires a separate explicit decision.

'''
 return s.replace(anchor,addition+anchor)
edit('Designs/Sandbox Lab Design.md',design)
def plan(s):
 s=s.replace('Agree the first workload scenario and evidence criteria, then register a bounded implementation slice','Review the system diagrams and bounded integration criteria before runtime implementation')
 s=s.replace('one durable workload-research lab','one durable research lab').replace('Agree one workload question,','Agree one bounded research objective,')
 s=s.replace('Run the workload scenario: inspect traces, discover incompatible counters, revise the future experiment, retain a valid unrelated measurement, and produce a justified next action or narrower finding.','Exercise a material late discovery: revise the dependent future experiment, retain unrelated valid findings, permit scoped local retry while independent work continues, and produce a supported next action or narrower conclusion.')
 s=s.replace('Use one worked example to choose the first uncertainty boundary and demonstrate what survives a plan change.','Use the full deployment, internals, cycle, CC, inference and recovery diagrams to agree the first integration boundary. The presentation excludes a workload example.')
 return s+'\nShared API inference may be co-located or remote. The bounded integration must also check per-lab limits, shared-service survival after lab stop, and denied cross-lab access to private model endpoints and checkpoints. See [[Designs/Sandbox Briefing/presentation/README]] for checkpoint 3 and the reference appendix.\n'
edit('Designs/Lab Capsule and Factory Design Plan.md',plan)
pres='Designs/Sandbox Briefing/presentation/'
titles=['Purpose and intended AI4R value','Complete environment in each lab VM','Inside the lab AI4R','Continuing research cycle','Overlapping investigations and local retry','Vendored container CC intake and use','Shared inference API, local or remote','Private models and fine-tuning','Persistence, stop and recovery','Technology stack and first proof','Appendix navigation','Original OpenJiuwen Figure 2','Corresponding AI4R responsibilities','Evidence and reuse limits','Acceptance scenarios','Tradeoffs and resource constraints']
readme='''---
id: sandbox-design-presentation
status: design-proposal-rendered-runtime-unverified
source: Sources/Prompts/2026-10-27-sandbox-system-presentation.txt; Designs/Sandbox Lab Design
last_reviewed: 2026-10-27
next_action: Review the ten main slides and use the appendix to settle the bounded integration criteria
---
# Sandbox design presentation

[PowerPoint: AI4Research Sandbox Design rev2](output/AI4Research%20Sandbox%20Design%20rev2.pptx). [Live editable deck](page://page_7a233186a3548191869c85106fc552b4).

Ten main slides explain the complete system; six hidden appendix slides support questions. The goal and intended AI4R value come first. The near-front Karpathy quotation motivates retained project state while explicitly distinguishing it from continual learning in model weights. The workload example is removed. VM per lab remains selected, using the comparison's visual style. Research is cyclical, with local retries and overlapping independent work.

The large diagrams are embedded as editable PowerPoint objects. The upstream Figure 2 is an attributed original image. All slides include source/limit notes. The diagrams below are previews of the same slide content, not replacements for the editable diagrams in the PPTX.

| Slide | Content |
|---|---|
'''+''.join(f'| {i+1} | {t} |\n' for i,t in enumerate(titles))+'''
## Diagram previews

'''+''.join(f'### {titles[i-1]}\n\n![{titles[i-1]}](review-system/slide-{i}.png)\n\n' for i in range(2,10))+'''## Evidence and limits

- Karpathy publisher transcript, October 17, 2025: https://www.dwarkesh.com/p/andrej-karpathy . The exact short quotation concerns memory/continual learning. Durable external state addresses continuity only.
- OpenJiuwen paper, August 28, 2026: https://arxiv.org/html/2608.27969v1 . Slides 12 and 13 enable an adjacent visual comparison. Similarity supplies precedent, not proof of our VM, packaging or privacy.
- Anthropic, April 8, 2026: https://www.anthropic.com/research/managed-agents . Stable interfaces and separated state/execution support implementation flexibility as a design precedent.
- vLLM official API serving: https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/ . Candidate interface with feature/capacity checks still required.
- Docker security/resource controls: https://docs.docker.com/engine/security/ and https://docs.docker.com/engine/containers/resource_constraints/ . Effective configuration requires verification.
- VM lifecycle: https://libvirt.org/manpages/virsh.html . Shutdown, force-off and storage deletion have distinct semantics.

Pinned source review separates our M1 `ab0d9c7`, SDK `9e339019` and upstream JiuwenSwarm `02b37f47`. JiuwenBox source supplies sandbox/job mechanisms, not an integrated OCI/whole-VM guarantee. OpenJiuwen compatibility and possible contributions remain targets. Current M1 freezes a run; accepted-result transfer and adaptive cross-batch execution remain explicit integration work.

This is ready for a design discussion. No integrated runtime, termination, privacy, GPU access, long-duration reliability or research improvement result is implied. Slide 15 states observations required before those claims. Resource savings and research value remain hypotheses to measure.

## Reusable source

`system_deck.mjs` is the current native slide source; `export_system.mjs` exports the reviewed live state for local PowerPoint because this external session supports inspection and PNG previews only. `build_slides.mjs` and `review/` retain the previous story. Current renders are in `review-system/`; the full original upstream figure is in `references/`. Page ID: `page_7a233186a3548191869c85106fc552b4`. Reconnect that page for future live edits.
'''
save(pres+'README.md',readme)
edit('Home.md',lambda s:s.replace('six main slides, two hidden backups, a workload example, source evidence and explicit implementation decisions.','ten main slides, six hidden appendix references, large editable system diagrams and a local PowerPoint. Purpose first, recurring research, shared/private inference and stop/recovery.').replace('last_reviewed: 2026-10-26','last_reviewed: 2026-10-27'))
edit('Presentation Library/Deck Catalog.md',lambda s:s.replace('[six-slide story, sources and remaining decisions]','[system diagrams, sources and remaining decisions]').replace('Six main slides and two hidden backups, reviewed as a design proposal on October 26.','Ten main slides and six hidden appendix references, reviewed as a design proposal on October 27. Local PPTX is linked from the presentation note.'))
renders=Path('C:/Users/m50066326/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Roaming/Codex/web/Codex/artifact-sessions/exports/latest/e91be6b1fafe6d85492b7271ed7d3473f685aa0efa44c444b2b4a3768bc2c6e9')
dest=root/pres/'review-system';dest.mkdir(exist_ok=True)
for n in range(1,17):
 for ext in ['png','layout.json']:shutil.copy2(renders/f'slide-{n}.{ext}',dest/f'slide-{n}.{ext}')
(batch/'note-edit-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'notes_updated':len(receipts),'renders':16,'prompt_sha256':entries[-1]['sha256']}))
