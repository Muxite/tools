// Role colors and explicit orthogonal routes for the current fifteen-slide deck.
export const P={ink:'#142033',muted:'#475569',bg:'#FFFFFF',rule:'#CBD5E1',research:'#1D4ED8',researchFill:'#EFF6FF',cc:'#6D28D9',ccFill:'#F3EEFF',model:'#0369A1',modelFill:'#E8F6FD',state:'#047857',stateFill:'#EAF8F0',control:'#B45309',controlFill:'#FFF4DF',check:'#334155',checkFill:'#F1F5F9',output:'#BE185D',outputFill:'#FCECF3'};
function raw(s,name,x,y,w,h){return s.shapes.add({name,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});}
function txt(s,name,x,y,w,h,text,size,color=P.ink,bold=false){const q=raw(s,name,x,y,w,h);q.text=text;q.text.style={typeface:'Segoe UI',fontSize:size,color,bold,alignment:'left',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:0};return q;}
function arrow(s,name,points,role='research',dashed=false,headed=true){
 const color=P[role],xs=points.map(v=>v[0]),ys=points.map(v=>v[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(1,Math.max(...xs)-x),h=Math.max(1,Math.max(...ys)-y);
 s.shapes.add({name,geometry:'custom',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:color,width:2.8,style:dashed?'dashed':'solid'},customPaths:[{width:w,height:h,commands:points.map((v,i)=>i?{lineTo:{x:v[0]-x,y:v[1]-y}}:{moveTo:{x:v[0]-x,y:v[1]-y}})}]});
 if(!headed)return;
 const a=points.at(-2),b=points.at(-1),dx=b[0]-a[0],dy=b[1]-a[1];let tri;
 if(Math.abs(dx)>Math.abs(dy)){const z=Math.sign(dx);tri=[[b[0],b[1]],[b[0]-z*12,b[1]-6],[b[0]-z*12,b[1]+6]];}else{const z=Math.sign(dy);tri=[[b[0],b[1]],[b[0]-6,b[1]-z*12],[b[0]+6,b[1]-z*12]];}
 const ax=Math.min(...tri.map(v=>v[0])),ay=Math.min(...tri.map(v=>v[1])),aw=Math.max(1,Math.max(...tri.map(v=>v[0]))-ax),ah=Math.max(1,Math.max(...tri.map(v=>v[1]))-ay);
 s.shapes.add({name:name+' arrow',geometry:'custom',position:{left:ax,top:ay,width:aw,height:ah},fill:color,line:{fill:color,width:0},customPaths:[{width:aw,height:ah,commands:[{moveTo:{x:tri[0][0]-ax,y:tri[0][1]-ay}},...tri.slice(1).map(v=>({lineTo:{x:v[0]-ax,y:v[1]-ay}})),{close:{}}]}]});
}
const categories={
 1:{investigate:'research',retain:'state',contribute:'output'},
 2:{people:'research',UI:'research',outside:'control','complete runtime':'research',supervisor:'control','CC execution':'cc','model routing':'model','persistent state':'state',inference:'model','package sources':'cc','research outputs':'output'},
 3:{interface:'research',objective:'research',planning:'research',workflow:'research',knowledge:'state',checks:'check',growth:'cc',library:'cc',jobs:'control',persistent:'state'},
 4:{goals:'research',strategy:'research',run:'control',observe:'check',learn:'state',adjust:'research'},
 5:{general:'cc',domain:'cc',local:'cc','factory inputs':'research','factory bundle':'cc','ingest CC':'cc','build test CC':'cc','package CC':'cc',qualification:'check','lab library':'cc','local use':'cc',contribution:'cc'},
 6:{'runtime client':'research','cc client':'cc',routing:'model',registry:'model',shared:'model','private route':'model'},
 7:{trainer:'cc',model:'model','private state':'state','other lab':'research','access denied':'control'},
 8:{research:'research',experiment:'control',labstop:'control',outside:'control',data:'state',restore:'state'},
 11:{native:'research','AI4R additions':'cc',upstream:'cc'}
};
const titles={1:'Purpose: sustained research for AI4Research',2:'The complete lab system',3:'Inside the lab’s AI4R',4:'The continuing research cycle',5:'CC agents, workflows and factory bundles',6:'Model routing inside each lab',7:'Private models inside the lab',8:'Persistence, shutdown and recovery',9:'Technology stack and responsibilities',10:'Reference: OpenJiuwen system diagram',11:'Native JiuwenSwarm integration',12:'Evidence and reuse limits',13:'Acceptance scenarios',14:'Tradeoffs and resource limits',15:'JiuwenBox: coverage and integration'};
const takeaways={1:'Durable project state supports continuity; model-weight continual learning remains separate.',2:'Lab VMs share services; writable state and private models remain separate.',4:'Continue until supported completion, a blocker, human pause or the resource limit.',5:'Factory CCs build other CCs; independent checks qualify new versions for future work.',6:'Move endpoints without changing CC code. Model identity and access policy stay explicit.',7:'Private training needs reserved compute; private models stay outside shared discovery.',8:'Control must work when agents hang. Preserve data and reconcile uncertain effects.',9:'First proof: revise research, qualify a CC, stop a runaway job and resume retained work.',11:'Native skills describe guidance and tools; CCs add packaged execution and research contracts.',12:'Compatibility supports contributions; integration and upstream acceptance need evidence.',14:'Shared services reduce duplicate allocations; capacity, quotas and costs need measurement.'};
const changes={
 1:{contribute:'Reports and discoveries\nReusable CC improvements'},
 2:{supervisor:'Execution control\nJiuwenBox reuse','model routing':'Model routing\nAI4R + CC clients','package sources':'CC package sources\nGeneral / domain','persistent state':'Lab data: evidence, reports, findings, CC versions, jobs and app state'},
 3:{workflow:'Research CC workflow\nInvestigate and report',growth:'Factory / RSI CCs\nBuild and improve',jobs:'Execution control\nScoped CC jobs',library:'CC library\nAgents + workflows',knowledge:'Knowledge / context\nEvidence and findings',planning:'Planning\nStrategy and ready work',persistent:'Durable state connects cycles: goals, evidence, reports, attempts and versions.'},
 4:{goals:'Goals and constraints\nBrief + open questions',strategy:'Choose / revise strategy\nHypotheses and next work',run:'Run ready experiments\nIndependent work overlaps',observe:'Check and observe\nResults and uncertainty',learn:'Retain and communicate\nReports + evidence',adjust:'Adapt the next work\nRetry, repair or revise'},
 5:{general:'General / mother AI4R\nSource + image releases',domain:'Domain CC collections\nRepos + artifact stores',local:'Lab-owned CCs\nPrivate repo + image store','build test CC':'Build CC\nRun tests',qualification:'Independent qualification\nChecks + fixed criteria','shared lab plumbing':'Shared lab execution and model routes','lab library':'Eligible CCs / bundles\nNative skill + tool bindings','local use':'Use locally\nResearch / factory workflows'},
 6:{routing:'Stable model interface\nRole / model alias\nResolve route + credentials','runtime client':'AI4R model client','cc client':'Agent / workflow CC\nInjected model client',registry:'Lab model configuration\nAllowed models / routes'},
 7:{trainer:'Training / evaluation CCs\nVendored software',model:'Lab-private model\nServing or direct calls'},
 8:{experiment:'Cancel an experiment\nStop owned processes',data:'Persistent lab data\nEvidence, reports, jobs, source and checkpoints',restore:'Restart / restore: fence old writers, reconcile jobs and validate state',delete:'Deletion is separate\nOther labs and shared services\ncontinue running'},
 11:{upstream:'Contribution paths\n\nLocal role-specific CCs\nMother AI4R review\nGeneric JiuwenSwarm PRs\nReproducible tests\nUpstream maintainer review'}
};
// [name, points, role, dashed, headed]
const routes={
 1:[['value1',[[378,367],[474,367]],'state'],['value2',[[804,367],[900,367]],'output']],
 2:[['people UI',[[228,182],[288,182]],'research'],['interface runtime',[[488,214],[488,233],[820,233],[820,293]],'research'],['runtime execution',[[173,371],[173,415]],'control'],['run CC',[[278,450],[318,450]],'control'],['runtime model',[[713,371],[713,415]],'model'],['CC model',[[538,450],[578,450]],'model'],['shared API',[[848,450],[920,450],[920,332],[948,332]],'model'],['import package',[[948,468],[934,468],[934,390],[828,390],[828,371]],'cc',true],['retained outputs',[[338,485],[338,525]],'state'],['outside stop',[[1090,214],[1090,233],[880,233],[880,277]],'control'],['report delivery',[[848,547],[948,547]],'output']],
 3:[['direction',[[198,208],[198,282]],'research'],['brief plan',[[328,320],[368,320]],'research'],['plan workflow',[[628,320],[668,320]],'research'],['workflow checks',[[808,358],[808,380],[498,380],[498,412]],'check'],['evidence knowledge',[[368,452],[328,452]],'state'],['knowledge planning',[[198,412],[198,384],[340,384],[340,320],[368,320]],'state'],['capability selection',[[1220,452],[1250,452],[1250,274],[618,274],[618,282]],'cc',true],['execution requests',[[628,432],[648,432],[648,392],[985,392],[985,308],[1008,308]],'control'],['job results',[[1220,320],[1240,320],[1240,554],[498,554],[498,492]],'check'],['factory candidate',[[668,472],[628,472]],'cc'],['qualified admission',[[598,492],[598,518],[980,518],[980,472],[1008,472]],'cc']],
 4:[['g-s',[[348,217],[490,217]],'research'],['s-r',[[790,217],[932,217]],'control'],['r-o',[[1082,264],[1082,390]],'check'],['o-l',[[932,437],[790,437]],'state'],['l-a',[[490,437],[348,437]],'research'],['a-g',[[198,390],[198,264]],'research']],
 5:[['general intake',[[218,230],[218,260],[1040,260],[1040,298]],'cc'],['domain intake',[[618,230],[618,260]],'cc',false,false],['local intake',[[1040,230],[1040,260]],'cc',false,false],['requested creation',[[388,347],[399,347],[399,377],[417,377]],'research'],['compose ingest build',[[533,377],[547,377]],'cc'],['compose build package',[[663,377],[677,377]],'cc'],['factory candidate',[[803,377],[848,377]],'cc'],['admission',[[1040,395],[1040,466],[618,466],[618,478]],'cc'],['use admitted CC',[[788,518],[848,518]],'cc'],['propose upstream',[[448,518],[388,518]],'cc',true]],
 6:[['runtime routing',[[323,254],[368,254],[368,279],[416,279]],'model'],['cc routing',[[323,388],[368,388],[368,347],[416,347]],'model'],['shared call',[[816,279],[872,279],[872,244],[922,244]],'model'],['config routing',[[218,480],[218,455],[396,455],[396,406],[616,406],[616,384]],'model',true],['private call',[[760,384],[760,435]],'model']],
 7:[['trainmodel',[[406,268],[514,268]],'model'],['save checkpoint',[[696,315],[696,416]],'state'],['trainingdata',[[241,416],[241,315]],'state']],
 8:[['escalate1',[[343,215],[448,215]],'control',true],['escalate2',[[808,215],[913,215]],'control',true],['emergency escalation',[[1072,258],[1072,330]],'control',true],['restored',[[428,416],[428,496]],'state']],
 11:[['native binding',[[378,325],[448,325]],'cc'],['contribution path',[[808,325],[878,325]],'cc']]
};
const frames=new Set(['lab boundary','ai4r expanded','factory bundle','lab routing boundary','private lab']);
function textStyle(size,color=P.ink,bold=false,center=false,insets=0){return {typeface:'Segoe UI',fontSize:size,color,bold,alignment:center?'center':'left',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets};}
export async function restyle({presentation:p}){
 for(let i=0;i<p.slides.items.length;i++){
  const n=i+1,s=p.slides.getItem(i);s.background.fill=P.bg;
  for(const q of s.shapes.items){
   if(changes[n]?.[q.name]!==undefined)q.text=changes[n][q.name];
   const str=q.text?.toString()||'',role=categories[n]?.[q.name];
   if(role){q.fill=frames.has(q.name)?'none':P[role+'Fill'];q.line={fill:P[role],width:2,style:'solid'};}
   if(frames.has(q.name)){q.line={fill:role?P[role]:'#64748B',width:1.8,style:'solid'};continue;}
   if(q.name==='title'){q.text=titles[n];q.text.style=textStyle(40,P.ink,true);continue;}
   if(q.name==='subtitle'){q.text.style=textStyle(22,P.muted);continue;}
   if(q.name==='source'){q.text.style=textStyle(14,P.muted);continue;}
   if(q.name==='page'){q.text.style={...textStyle(15,P.muted),alignment:'right'};continue;}
   if(q.name==='footer rule'){q.fill=P.rule;continue;}
   if(q.name==='takeaway'){q.fill='#F1F5F9';continue;}
   if(q.name==='takeaway text'){if(takeaways[n])q.text=takeaways[n];q.text.style=textStyle(24,P.ink,true);continue;}
   if(q.name.endsWith(' label')){q.text.style=textStyle(22,role?P[role]:P.ink,true);continue;}
   if(role&&str){let size=24;if(n===1)size=26;if(n===2)size=['people','UI'].includes(q.name)?27:23;if(n===3)size=23;if(n===5)size=['ingest CC','build test CC','package CC'].includes(q.name)?22:24;if(n===6)size=q.name==='routing'||q.name==='private route'||q.name==='shared'?26:24;if(n===7)size=26;if(n===11)size=25;q.text.style=textStyle(size,P.ink,true,true,6);continue;}
   if(str){let size=24,color=P.ink,bold=false,center=false;if(q.name==='goal'){size=35;color=P.research;bold=true;}if(q.name==='quote'){size=26;bold=true;}if(q.name==='quote attribution')size=18;if(q.name==='review independence'){size=20;color=P.check;}if(q.name==='local retry'){size=24;bold=true;center=true;}if(q.name==='shared lab plumbing'){size=20;color=P.muted;}if(q.name==='policy'){size=22;color=P.muted;}if(q.name==='blocked'){size=23;color=P.control;bold=true;center=true;}if(q.name==='delete'){size=23;bold=true;center=true;}if(q.name==='mapping1'){color=P.control;bold=true;}if(q.name==='mapping2'){color=P.research;bold=true;}if(q.name==='mapping3'){color=P.check;bold=true;}q.text.style=textStyle(size,color,bold,center);}
  }
  if(routes[n]){const old=await p.inspect({select:`$.slides[${i}].elements[*]`,include:['id','name']});const texts=new Set(s.shapes.items.filter(q=>q.text?.toString()).map(q=>q.name));p.delete(old.records.filter(v=>!texts.has(v.name)&&!frames.has(v.name)&&!['footer rule','takeaway','quote field'].includes(v.name)).map(v=>v.id));for(const [name,pts,role,dash,head] of routes[n])arrow(s,name,pts,role,dash,head!==false);}
  s.speakerNotes.text+='\nVisual conventions: blue research/orchestration; violet CC packages/composition; cyan model access; green persistent state; amber execution/control; slate checks; rose research outputs. Solid arrows carry requests/results/control/data; dashed arrows show configuration, references, imports, contribution proposals or optional escalation. Arrowheads terminate on the indicated node boundary. Categories express responsibilities, not mandatory separate services.';
 }
 // Geometry and concise labels provide room for the larger type.
 const shapes=n=>p.slides.getItem(n-1).shapes.items;const get=(n,name)=>shapes(n).find(q=>q.name===name);
 get(2,'persistent state').text.style=textStyle(21,P.ink,true,true,5);
 get(2,'outside').text='Host / provider\nIndependent VM stop';get(2,'outside').text.style=textStyle(23,P.ink,true,true,5);
 for(const name of ['library','jobs'])get(3,name).position.width=212;
 get(3,'library').text.style=textStyle(22,P.ink,true,true,6);
 const ri=get(3,'review independence');ri.position.top=566;ri.position.height=24;ri.position.width=1184;
 get(3,'persistent').text.style=textStyle(24,P.ink,true,true,6);
 get(4,'strategy').position.top=170;
 get(8,'restore').text.style=textStyle(24,P.ink,true,true,6);
 txt(p.slides.getItem(7),'emergency condition',913,276,144,43,'If guest\ncontrol fails',20,P.control,true);
 // A small role legend replaces only the core diagram's visible footer; citations stay in notes.
 const core=p.slides.getItem(1),source=get(2,'source');source.text='';
 ['research','cc','model','state','control','check','output'].forEach((role,k)=>txt(core,'color legend '+role,48+k*170,677,164,25,{research:'Research',cc:'CC packages',model:'Models',state:'State',control:'Control',check:'Checks',output:'Outputs'}[role],15,P[role],true));
 // Preserve every native table value while giving its text more vertical space.
 for(const n of [9,12,13,14,15]){
  const s=p.slides.getItem(n-1),old=s.tables.items[0],snap=old.toSnapshot(),vals=[];
  for(let r=0;r<snap.rows;r++){const row=[];for(let c=0;c<snap.cols;c++)row.push(old.getCell(r,c).text.toString());vals.push(row);}
  const found=await p.inspect({select:`$.slides[${n-1}].elements[*]`,include:['id','kind']});p.delete(found.records.filter(v=>v.kind==='table').map(v=>v.id));
  const widths=n===15?[225,440,519]:n===12?[330,854]:[350,834];
  const t=s.tables.add({rows:vals.length,columns:snap.cols,left:48,top:150,width:1184,height:[13,15].includes(n)?448:420,columnWidths:widths,values:vals});
  t.borders.assign({fill:P.rule,width:1,style:'solid'});
  for(let r=0;r<vals.length;r++)for(let c=0;c<snap.cols;c++){const cell=t.getCell(r,c);cell.fill=r===0?'#E8EFF8':r%2===0?'#F8FAFC':'#FFFFFF';cell.text.style={...textStyle(r===0?21:20,P.ink,r===0||c===0,false,8)};}
 }
 p.slides.getItem(2).speakerNotes.text+='\nConnector correction: planning proposes work; binding/checks authorizes execution, job results return to checking, factory candidates pass qualification before library admission, and the library supplies future selection. These edges replace the earlier workflow-to-executor and factory-to-library shortcuts. Checks span pre-dispatch legality and post-execution acceptance; graph arrows indicate responsibility/data flow, not a single linear research script.';
 p.slides.getItem(1).speakerNotes.text+='\nImported CC packages enter the AI4R selection/qualification responsibility before execution; the import edge no longer goes directly into running CCs. The source receipt and detailed factory slide retain the qualification requirements.';
 return {slides:p.slides.items.length,styled:15,roles:7};
}

export async function finalRepairs({presentation:p}){
 const edits={2:{'CC execution':'CC execution\nAgents + flows'},3:{planning:'Planning\nStrategy + next work',library:'CC library\nAgents + flows'},7:{blocked:'Excluded from shared\nmodel discovery','access denied':'Other labs denied\nNo route or access'},8:{delete:'Deletion is separate\nOther labs + shared services\nstay available'}};
 for(const [n,labels] of Object.entries(edits))for(const q of p.slides.getItem(Number(n)-1).shapes.items)if(labels[q.name]!==undefined){q.text=labels[q.name];if(q.name==='access denied')q.text.style=textStyle(24,P.ink,true,true,6);}
 return {repaired:[2,3,7,8]};
}
