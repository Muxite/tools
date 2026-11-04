export async function update({presentation:p}){
 const f=await import('node:fs/promises');await f.writeFile('C:/Users/m50066326/huawei/AI4Research-Notebook/Designs/Sandbox Briefing/presentation/.build-system/before-agent-cc-clarity.json',JSON.stringify(p.toProto()));
 const labels={
  1:{subtitle:'CCs package AI4R agents, skills, tools and workflows; the lab supplies execution and durable state','complete runtime':'Lab AI4R: agents and workflows packaged as CCs\nJiuwenSwarm composition, checks, knowledge and RSI','CC execution':'CC execution\nAgents / workflows'},
  2:{library:'Lab CC library\nAgents + workflows'},
  4:{title:'CC packages: agents, workflows and factory bundles',subtitle:'A CC bundles agent instructions, workflow/tool code, dependencies and declared model access.'},
  5:{'cc client':'Agent / workflow CC\nInjected model client'},
  10:{'AI4R additions':'AI4R lab integration\n\nAgent / workflow CCs\nInstructions + tool code\nPackaged dependencies\nIndependent qualification\nModel and job adapters'}
 };
 for(const [index,names] of Object.entries(labels)){const s=p.slides.getItem(Number(index));for(const q of s.shapes.items)if(names[q.name]!==undefined)q.text=names[q.name];}
 const stack=p.slides.getItem(8).tables.items[0];stack.getCell(2,0).value='CCs: AI4R agents / workflows';stack.getCell(2,1).value='OCI packages agent/skill/tool code and dependencies; Compose hosts services';
 const explanation='\nCCs hold the AI4R agent capabilities: specialist instructions/skills, agent or workflow code, tool implementations, software dependencies and declared model requirements. They can represent one agent, several collaborating agents, a tool or a composite workflow. Research and Factory workflows compose these CCs through native JiuwenSwarm interfaces. The lab provides orchestration, state, scoped execution and model routes around them. Shared model weights remain outside the package unless a lab-private model profile explicitly includes them. A logical CC/bundle is not necessarily one dedicated process or container; deployment follows declared dependencies and isolation needs. This is the intended packaging architecture, not a newly verified runtime result.';
 for(const i of [1,2,4,5,8,10])p.slides.getItem(i).speakerNotes.text+=explanation;
 return {updated:[2,3,5,6,9,11],slides:p.slides.items.length};
}
