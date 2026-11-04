import {route,C} from './system_deck.mjs';
export async function update({presentation:p}){
 const s=p.slides.getItem(5);
 for(const q of s.shapes.items){
  if(q.name==='lab routing boundary')q.position.height=420;
  if(q.name==='private route'){q.position.left=448;q.position.top=435;q.position.width=368;q.position.height=110;}
  if(q.name==='registry'){q.position.left=68;q.position.top=480;q.position.width=300;q.position.height=75;q.text='Lab model configuration\nAllowed models / routes';}
 }
 const old=await p.inspect({select:'$.slides[5].elements[*]',include:['id','name']});
 p.delete(old.records.filter(x=>['config routing','config routing arrow','private call','private call arrow'].includes(x.name)).map(x=>x.id));
 route(s,'config routing',[[218,480],[218,455],[396,455],[396,406],[616,406],[616,384]],C.teal,true);
 route(s,'private call',[[760,384],[760,435]],C.amber);
 s.speakerNotes.text+='\nPlacement correction: the private model process and lab model configuration are explicitly inside the lab VM boundary. Shared inference remains outside and can be co-located or remote. Private serving access remains restricted to this lab.';
 return {updated:[6],slides:p.slides.items.length};
}

