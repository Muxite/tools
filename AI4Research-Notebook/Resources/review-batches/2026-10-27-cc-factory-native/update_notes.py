from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[3];batch=Path(__file__).resolve().parent
backups=[]
def save(rel,text):
 p=root/rel
 if p.exists():
  data=p.read_bytes();b=batch/'before'/(rel.replace('/','__')+'.snapshot');b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(data);backups.append({'path':rel,'before_sha256':hashlib.sha256(data).hexdigest()})
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def edit(rel,fn):save(rel,fn((root/rel).read_text(encoding='utf-8-sig')))
prompt='''for the containers-bring-reusable-capability into the lab slide, i reccommend showing the source of the CC packages. theres many places where they are stored, cuz some are domain specific, some are general. each are stored differently. some are made by each lab for their roles. if good they can be merged upstream as part of the mother AI4R. otherwise they stay locally as tools. they will often be made by the Capability Capsule Factory that allows users or the AI to take an issue they have and produce verified functional capsules to do the job and package the caapbilities accordingly. CC factories can be drive by many things, they can ingest data/repos/papers to make capabilities (like paper2agent), or they can ingest "mental models" to produce skills that replicate how certain people think and view problems to provide new perspectives and analysis and methodologies, or they can check for gaps in planning that have repeated or are critical, and make a new specialist to replace the old pure generalist to do the task better. It can also upgrade capsules. can we adjsut to be more like or easier to utilize jiuwenswarm, cuz our goal is to use that as best as we can and be compatible so we can merge back to them with our best ideas. try to reduce slide count if possible. the most important thing is the overall system diagram must be very clear.
'''
rel='Sources/Prompts/2026-10-27-cc-sources-factory-native.txt';save(rel,prompt)
mf='Sources/capture-manifest.json';rows=json.loads((root/mf).read_text(encoding='utf-8-sig'));rows.append({'path':rel,'sha256':hashlib.sha256(prompt.encode()).hexdigest(),'capture_method':'Exact visible user message captured as UTF-8 LF; not a transport export','captured_date':'2026-10-27'});save(mf,json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
edit('Sources/Prompt Register.md',lambda s:s+'\n- [[Sources/Prompts/2026-10-27-cc-sources-factory-native.txt|CC sources, factory and native JiuwenSwarm alignment]]: diverse storage/origins, lab creation/upgrades, separate contribution paths, native reuse and a shorter clear system presentation.\n')
section='''## CC sources, factory and native JiuwenSwarm integration

The CC Factory is a normal lab-local capability-growth mechanism. A user or AI can request a capsule for a concrete problem, repair or upgrade. Inputs may be data, repositories or papers (Paper2Agent-style executable capability), documented mental models/methods (perspective Skills), or repeated/critical gaps in planning that justify a specialist. A factory can improve existing CCs as well as create new ones. A specialist replaces the generalist for a task only when matched task evidence supports that choice. Perspective Skills implement source-inspired methods; usefulness and fidelity require evaluation rather than assuming they reproduce a person's cognition.

| Origin | Possible storage / distribution | Lab use |
|---|---|---|
| Mother AI4R / general capabilities | Versioned source releases and OCI registries | Import selected compatible packages |
| Domain collections | Domain/team repos, registries or artifact stores | Select role-appropriate dependencies and operations |
| Lab-created or upgraded CCs | Lab repo, private registry or local image store | Qualify and retain as local tools/specialists |

These are logical sources with different storage backends, not a requirement to build a central registry. Selected source/image versions enter the lab's working capability selection. Native JiuwenSwarm can still use one physical local Skill library and metadata-based per-role visibility. External distribution and local installation are separate concerns.

Use JiuwenSwarm's native Skill discovery/install, scoped visibility, tools/MCP, teams/workflows and skill creation/evolution hooks wherever they fit. The factory emits compatible native guidance/tool bindings plus the implementation and dependencies packaged for execution. `SKILL.md` guidance/assets are not equivalent to an OCI CC; the package connects native interfaces to its pinned execution unit and AI4R contract. Containerize dependency-bearing software; do not create a redundant service merely to expose guidance. Prefer a narrow adapter to a second skill manager or parallel generic evolution framework.

Factory flow: user/AI need and source material, create or upgrade, executable functional checks and task tests, independent qualification, local eligibility, native invocation. Functional verification covers the declared tasks, effects, compatibility and failure behavior. Broader scientific or performance benefit remains a separate measured result. The candidate cannot change its own acceptance criteria. Regression-test upgrades and apply them to future bindings while active work keeps its pins. Model routes remain injected into both AI4R and CC containers.

Locally useful CCs may stay local indefinitely. Strong reusable changes may be proposed to mother AI4R release review. Generic interfaces, fixes and reusable mechanisms may separately be proposed upstream to JiuwenSwarm with reproducible tests. Local qualification, mother AI4R adoption and upstream maintainer acceptance are different decisions. This work performs no publication or merge.

Pinned upstream `02b37f47fbefe80a58e4ed88606120818ca44ac3` source checked: `jiuwenswarm/agents/swarm/providers/{skills,tools,evolution_rails}.py`, `jiuwenswarm/server/runtime/skill/skill_manager.py`, and `docs/en/MCPConfiguration.md`. Skills use one local library plus role visibility; tool providers and MCP connect callable operations; evolution providers wrap native create/evolution rails. These are source-backed integration points, not a tested AI4R packaging result. Existing M1 Planner restrictions remain deliberate until a bounded M2 adapter is qualified. [Official project](https://github.com/openJiuwen-ai/jiuwenswarm).

'''
edit('Designs/Sandbox Lab Design.md',lambda s:s.replace('## Evidence and reuse',section+'## Evidence and reuse').replace('Appendix slide 17 gives','Appendix slide 15 gives'))
edit('Sources/Implementation Intent.md',lambda s:s+'\n## October 27 CC sources and native factory alignment\n\nCCs originate in general mother-AI4R releases, domain collections and lab-owned storage. Factories create/upgrade from user or AI needs, data/repos/papers, mental models and repeated/critical planning gaps. Qualify functional behavior independently, keep locally useful tools local, and separate mother AI4R adoption from generic JiuwenSwarm contributions. Prefer native Skill management, scoped visibility, tool/MCP and evolution hooks with thin CC execution adapters. The overall diagram is primary. Presentation shortened from 17 to 15 slides, nine main and six appendix; runtime implementation remains unverified.\n')
def plan(s):
 s=s.replace('Use existing AI4R capsules, checking, storage and OpenJiuwen integration wherever they fit.','Use native JiuwenSwarm skills, tools/MCP, role visibility and creation/evolution hooks with existing AI4R checking and storage wherever they fit.')
 s=s.replace('Expand packaging, factories and deployment only when a demonstrated research need requires them.','Exercise one bounded factory-created or upgraded capsule as part of the lab slice, rather than adding a competing generic skill framework.')
 s=s.replace('one selected reuse path; explicit handling of accepted artifact transfer.','one selected native reuse path; explicit handling of accepted artifact transfer, multi-source CC intake and one factory candidate.')
 s=s.replace('**Exit:** an actual Planner selects the changed next experiment after observing the result.','**Exit:** an actual Planner selects the changed next experiment after observing the result. One created or upgraded CC passes executable functional/task checks, independent qualification and native Skill/tool invocation. A specialist-vs-generalist improvement claim needs a matched comparison.')
 s=s.replace('Manual package, then factory-assisted production','Native create/evolution hooks plus the factory packaging adapter')
 return s+'\nFactory inputs include explicit user/AI requests, data/repos/papers, mental models/methods and repeated or critical gaps. General, domain and lab-owned package storage stay distinct. Qualified packages become local tools; upstream mother-AI4R adoption and generic JiuwenSwarm contributions follow separate review paths. [[Designs/Sandbox Lab Design]] owns this native integration contract.\n'
edit('Designs/Lab Capsule and Factory Design Plan.md',plan)
edit('Designs/Labs and Capability Capsules.md',lambda s:s+'\n## Native capability growth\n\nGeneral mother-AI4R packages, domain collections and lab-generated CCs may use different source/image storage. A lab selects pinned packages and uses native JiuwenSwarm Skill/tool bindings. Its CC Factory creates or upgrades from user/AI needs, papers/repos/data, mental models or critical/repeated gaps. Independent task-level qualification controls local eligibility; useful changes may be proposed separately to mother AI4R and generic JiuwenSwarm upstream review. See [[Designs/Sandbox Lab Design#CC sources, factory and native JiuwenSwarm integration]].\n')
titles=['Purpose and AI4R value','The complete lab system','Inside the lab AI4R','Continuing research cycle','CC sources, factory and local reuse','Model routing for AI4R and CCs','Private models','Persistence, stop and recovery','Technology stack','Original OpenJiuwen system diagram','Native JiuwenSwarm integration','Evidence and reuse limits','Acceptance scenarios','Tradeoffs and resource limits','JiuwenBox requirements fit']
pres='Designs/Sandbox Briefing/presentation/'
readme='''---
id: sandbox-design-presentation
status: design-proposal-rendered-runtime-unverified
source: Sources/Prompts/2026-10-27-cc-sources-factory-native.txt; Designs/Sandbox Lab Design
last_reviewed: 2026-10-27
next_action: Review the overall diagram and factory/native integration boundaries before implementing the bounded slice
---
# Sandbox design presentation

[PowerPoint: AI4Research Sandbox Design rev5](output/AI4Research%20Sandbox%20Design%20rev5.pptx). [Live editable deck](page://page_7a233186a3548191869c85106fc552b4).

Nine main slides and six hidden appendix slides, reduced from seventeen total. The complete lab system is the primary diagram. The source/factory view now shows general, domain and lab-owned storage; user/AI and source-driven factory creation/upgrades; independent qualification; local use; and separately reviewed contributions. Native JiuwenSwarm Skill/tool/evolution mechanisms are the preferred integration surface.

The purpose-first opening, attributed Karpathy quote, recurring research cycle, lab VM ownership, private/shared model policy and independent stop paths remain. The workload example remains removed. Parallel work and scoped retry are folded into the cycle; the dedicated navigation slide is removed. The upstream original figure and our native integration mapping remain adjacent for comparison.

| Slide | Content |
|---|---|
'''+''.join(f'| {i+1} | {t} |\n' for i,t in enumerate(titles))+'''
## Core diagram previews

'''+''.join(f'### {titles[i-1]}\n\n![{titles[i-1]}](review-rev5/slide-{i}.png)\n\n' for i in [2,3,4,5,6,7,8])+'''## Native integration and evidence

JiuwenSwarm source pin `02b37f47fbefe80a58e4ed88606120818ca44ac3` provides Skill discovery/install, a local library with role visibility, config/tool/MCP integration and native skill create/evolution rails. The factory should emit compatible guidance and tool bindings with packaged implementation. A Skill is not an OCI image; a CC adds pinned execution and AI4R obligations. Qualify these adapters rather than introducing a parallel skill manager. Detailed source scope and limits are on slides 11–15 and in notes.

Mental-model Skills provide source-inspired perspectives and methods. Claims of faithful person emulation or superior decisions require evidence. Functional qualification covers specified task behavior, compatibility and regression criteria. It does not establish general research benefit. A specialist replaces a generalist only after a matched assessment supports it. Local usefulness does not automatically publish a CC. Mother AI4R release adoption and generic JiuwenSwarm upstream contribution are separate review paths.

Both AI4R and CCs use injected model routing. Endpoint relocation can preserve code and model identity; model substitution follows explicit policy. Private models remain lab-scoped. JiuwenBox offers execution, stop and proxy mechanisms; Docker owns OCI and the provider owns VM power control. Integration, actual termination, privacy, GPU support and research improvements remain unverified.

- JiuwenSwarm: https://github.com/openJiuwen-ai/jiuwenswarm . Exact source paths are retained in notes and the dated source receipt.
- JiuwenBox: https://github.com/openJiuwen-ai/jiuwenswarm/blob/develop/jiuwenbox/README.md . Graceful shutdown and signal escalation are source-backed, not a deployment test.
- Karpathy publisher transcript: https://www.dwarkesh.com/p/andrej-karpathy , October 17, 2025. Persistent external state addresses continuity, not weight-level continual learning.
- OpenJiuwen Figure 2: https://arxiv.org/html/2608.27969v1 , August 28, 2026. The original diagram is reproduced with attribution; similarity does not validate our complete deployment.
- Stable-interface precedent: https://www.anthropic.com/research/managed-agents , April 8, 2026.
- Serving/routing precedents: https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/ and https://docs.litellm.ai/docs/proxy/model_management . No gateway product is newly selected.
- Host controls: https://docs.docker.com/engine/security/ , https://docs.docker.com/engine/containers/resource_constraints/ and https://libvirt.org/manpages/virsh.html . Effective configuration requires qualification.

## Reusable source

`cc_factory_native.mjs` contains the current diagram/native integration callbacks and one-time compaction of the prior seventeen-slide deck. Do not rerun `compact` against an already compacted deck. It uses native helpers from `system_deck.mjs`. Earlier callbacks describe the previous ordering and should not be replayed over the current deck. `export_native.mjs` exports the reviewed saved state to PowerPoint and embeds the attributed original image. The external live session supports PNG previews but not direct PPTX export. Current renders are in `review-rev5/`; earlier renders and exports remain as revision history. Page ID: `page_7a233186a3548191869c85106fc552b4`.
'''
save(pres+'README.md',readme)
edit('Home.md',lambda s:s.replace('ten main slides, seven hidden appendix references','nine main slides, six hidden appendix references').replace('large editable system diagrams and a local PowerPoint.','clear overall-system and CC source/factory diagrams, native JiuwenSwarm integration and a local PowerPoint.'))
edit('Presentation Library/Deck Catalog.md',lambda s:s.replace('Ten main slides and seven hidden appendix references','Nine main slides and six hidden appendix references'))
renders=Path('C:/Users/m50066326/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Roaming/Codex/web/Codex/artifact-sessions/exports/latest/e91be6b1fafe6d85492b7271ed7d3473f685aa0efa44c444b2b4a3768bc2c6e9')
dest=root/pres/'review-rev5';dest.mkdir(exist_ok=True)
for i in range(1,16):
 for ext in ['png','layout.json']:shutil.copy2(renders/f'slide-{i}.{ext}',dest/f'slide-{i}.{ext}')
sources=[]
for rel in ['README.md','docs/en/MCPConfiguration.md','jiuwenswarm/agents/swarm/providers/skills.py','jiuwenswarm/agents/swarm/providers/tools.py','jiuwenswarm/agents/swarm/providers/evolution_rails.py','jiuwenswarm/server/runtime/skill/skill_manager.py']:
 p=root.parent/'openjiuwen/jiuwenswarm'/rel;sources.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(batch/'source-and-note-receipt.json').write_text(json.dumps({'revision':'02b37f47fbefe80a58e4ed88606120818ca44ac3','scope':'source inspected; no runtime compatibility or factory effectiveness tests','sources':sources,'backups':backups},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'notes_updated':len(backups),'slides':15,'main':9,'appendix':6,'source_files':len(sources)}))
