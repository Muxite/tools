import {box,route,C} from './system_deck.mjs';
export async function update({presentation:p}){
 const before=await import('node:fs/promises');await before.writeFile('C:/Users/m50066326/huawei/AI4Research-Notebook/Designs/Sandbox Briefing/presentation/.build-system/before-research-outputs.json',JSON.stringify(p.toProto()));
 for(const q of p.slides.getItem(0).shapes.items){if(q.name==='subtitle')q.text='Independent labs produce reports and discoveries, retain knowledge and develop reusable capabilities';if(q.name==='retain')q.text='Retain reports, findings\nand supporting evidence';if(q.name==='contribute')q.text='Discoveries and reports\nReusable CC improvements';}
 const core=p.slides.getItem(1);
 for(const q of core.shapes.items)if(q.name==='persistent state')q.text='Persistent lab data: evidence, reports, findings, CCs, jobs and application state';
 box(core,'research outputs',948,510,284,70,'Research outputs\nReports / discoveries',C.white,C.teal,22);
 route(core,'report delivery',[[848,547],[948,547]],C.teal);
 for(const q of p.slides.getItem(2).shapes.items)if(q.name==='workflow')q.text='Research CC workflow\nInvestigate, report, discover';
 for(const q of p.slides.getItem(3).shapes.items)if(q.name==='learn')q.text='Retain and communicate\nFindings, reports, evidence';
 const context='\nLabs produce research outputs as well as capabilities: reports, discoveries/findings and supporting evidence. Research/reporting CCs assemble these outputs within the recurring research workflow; reporting need not wait until the entire project ends. Preserve them in lab data and expose them through the lab interface or an authorized export. The output box denotes deliverables, not another service or automatic public publication. Findings feed knowledge and subsequent investigations. Reports state the evidence, methods and uncertainty, including useful negative/inconclusive outcomes. A candidate hypothesis or generated report is not automatically a validated discovery. Capability contribution/adoption remains a separate path. All this is proposed output behavior, not a measured discovery result.';
 for(const i of [0,1,2,3])p.slides.getItem(i).speakerNotes.text+=context;
 return {updated:[1,2,3,4],slides:p.slides.items.length};
}
