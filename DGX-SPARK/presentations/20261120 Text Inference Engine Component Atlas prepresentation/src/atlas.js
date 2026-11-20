'use strict';
const data = JSON.parse(document.getElementById('records').textContent);
const byId = rows => new Map(rows.map(row => [row.id,row]));
const components = byId(data.components), capsules = byId(data.ccs), actions = byId(data.actions), jobs = byId(data.jobs);
const builders = id => data.builds.filter(pair => pair[1] === id).map(pair => capsules.get(pair[0]));
const capabilityLinks = [...data.builds,...data.factoryCapabilities];
const relatedCCs = id => capabilityLinks.filter(pair=>pair[1]===id).map(pair=>capsules.get(pair[0]));
const targets = id => capabilityLinks.filter(pair => pair[0] === id).map(pair => components.get(pair[1]));
const participants = id => data.serves.filter(pair => pair[1] === id).map(pair => components.get(pair[0]));
const served = id => data.serves.filter(pair => pair[0] === id).map(pair => actions.get(pair[1]));
const groups = ['Weights and residency','Request and generation','Decoder and experts','Execution and state','Factory','Host platform'];
const all = [...components.values()];
const app = document.querySelector('main');
const e = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link = (url,label) => '<a class="pill" href="#'+e(url)+'">'+e(label)+'</a>';
const cmpLink = c => link('component/'+c.id,c.name);
const actLink = a => link('action/'+a.id,a.title);
const ccLink = c => link('cc/'+c.id,c.name);
const readable = value => Array.isArray(value)?'<ul>'+value.map(x=>'<li>'+e(x)+'</li>').join('')+'</ul>':e(value);
const fact = (title,body) => body ? '<div class="fact" data-field="'+e(title)+'"><strong>'+e(title)+'</strong>'+readable(body)+'</div>' : '';
const heading = (k,title,desc) => '<div class="tagline">'+e(k)+'</div><h1>'+e(title)+'</h1><p class="lead">'+e(desc)+'</p>';
const section = (title,body) => '<section class="panel" data-section="'+e(title)+'"><h2>'+e(title)+'</h2>'+body+'</section>';
const pillbox = items => '<div class="pills">'+items.join('')+'</div>';
const scope = c => c.scope === 'Extension' ? 'Conditional extension' : c.scope;
const sorted = rows => rows.slice().sort((a,b)=>a.name.localeCompare(b.name));

const participationNotes = {
  'state/weight': {
    'weights.checkpoint_reader':'Supplies the validated tensor identity, shape and byte range used to bind the handle.',
    'placement.weight_placement_planner':'Supplies the storage tier and residency decision for that tensor.'
  },
  'interface/diagnostics': {
    'serving.engine_image_gateway':'Exposes diagnostic access at the image boundary.',
    'observability.runtime_event_recorder':'Produces the correlated events and trace annotations available through those diagnostics.'
  },
  'model/dispatch': {
    'merge.expert_row_dispatcher_and_combiner':'Groups token rows for local expert execution and records their inverse mapping.',
    'parallel.distributed_expert_exchange':'Transfers the grouped rows to the ranks holding their selected experts when the contract spans devices.'
  },
  'model/combine': {
    'merge.expert_row_dispatcher_and_combiner':'Restores token order and accumulates each expert contribution with its original mixture weight.',
    'parallel.distributed_expert_exchange':'Returns contributions to the token-owning rank before local accumulation.'
  },
  'startup/place': {
    'placement.weight_placement_planner':'Assigns weight residency within the available memory budget.',
    'engine.expert_weight_cache':'Supplies the capacity and lifetime requirements for slots holding streamed experts.',
    'parallel.distributed_execution_coordinator':'Assigns work across devices when the contract activates distributed execution.'
  }
};
function actionView(a) {
  const edges=data.cross.filter(([s,t])=>s===a.id||t===a.id);
  return heading(a.layer+' / '+(a.target?'Action':'Conditional action'),a.title,a.detail)+pillbox([link(a.id.startsWith('f_')?'factory/actions':'engine/actions','All '+(a.id.startsWith('f_')?'factory':'engine')+' actions')])+actionPerformers(a)+
    section('Acceptance',fact('Check',a.check)+fact('Measure',a.metric))+
    (edges.length?section('Connected actions',edges.map(([s,t,payload])=>'<div class="trace">'+actLink(actions.get(s))+' → '+actLink(actions.get(t))+'<br><small>'+e(payload)+'</small></div>').join('')):'')+
    (a.id==='model/route'?section('Routing fixture','<p>Scores [0.50, 0.30, 0.20] and ranking biases [0, 0, 0.15] select E0 and E2 for two slots. Normalizing their original scores gives 5/7 and 2/7. A result of 10/17 and 7/17 reveals that ranking bias entered the mixture weights.</p>'):'')+
    (a.id==='model/combine'?section('Row-order fixture','<p>Token A assigns weights 0.25 and 0.75 to expert results 4 and 8. The combined value is 7 in either packed order. Include a second token for the same expert to expose an incorrect inverse permutation.</p>'):'');
}
const deliveryLabel=cc=>cc.kind==='factory'?'Artifact delivered on invocation':'Code delivered';
function dispatchLinks(id){
  if(id==='compiler.contract_compiler')return section('Contract handoff',ccLink(capsules.get('factory.workflow_planner'))+'<p>The orchestrator receives the approved revision and assigns the required builders.</p>');
  if(id!=='factory.workflow_planner')return '';
  return section('Dispatch engine builders',pillbox([link('construction','Component work orders'),link('cc/compiler.contract_compiler','Contract compiler')])+details('Available engine builders',pillbox(data.ccs.filter(cc=>cc.kind==='engine').map(ccLink))));
}
function ccView(cc) {
  if(ccKind(cc)==='tool'||ccKind(cc)==='analysis')return operatingView(cc);
  const factory=cc.kind==='factory', h=cc.handoff;
  const assets=data.assets.filter(a=>a.assigned===cc.id);
  const operating=targets(cc.id).map(c=>'<h3>'+cmpLink(c)+'</h3>'+fact(factory?'How the artifact is used':'What this code does',c.summary)+fact('Consumes',c.inputs)+fact('Provides',c.outputs)+fact('Consumer',c.consumer)+pillbox(served(c.id).map(actLink))).join('');
  const fixtureRoles=new Set(['attention.dense_execution','attention.sparse_execution','dense.feed_forward','model.expert_ffn','model.expert_routing','sequence.recurrent_execution','sampling.select_tokens','weights.decode_blocks']);
  const fixture=fixtureRoles.has(cc.legacy);
  return '<div class="tagline">'+kindBadge(cc)+' '+(factory?'Software factory worker':'Delivers component code')+'</div><h1>'+e(cc.name)+'</h1>'+formerNote(cc)+
    '<div data-delivery>'+fact(deliveryLabel(cc),cc.summary)+'</div>'+endpointOwner(targets(cc.id)[0]?.id)+measuredBlock(targets(cc.id)[0]?.id)+
    (factory?'':section('Component requirement',fact('What the component must do',cc.requirement)+fact('Choices set by the contract',cc.contractChoices)))+
    section(factory?'Invocation':'Integration point',fact(factory?'Where it runs':'Connect the implementation',cc.connection)+operating)+
    dispatchLinks(cc.id)+section('Acceptance evidence',fact('Check',cc.evidence)+(fixture?fact('Reference fixture',h.artifact):'')+fact('Independent comparison',h.proof))+
    details('Engineering detail',(!fixture?fact(factory?'Invocation handoff records':'Companion records for integration and replay',h.artifact):'')+fact('Contract choices',cc.decisions)+(!factory?fact('Implement from scratch',cc.greenfield)+fact('Existing implementations',cc.integration):'')+fact('Measurements',h.signals)+fact('Next decision',h.rsi)+fact('Additional check',cc.check))+
    details('Capability contents',cc.contents.map(x=>fact(x.name+' · '+x.kind,x.detail)).join(''))+
    operatorBlock(targets(cc.id)[0]?.id)+sourceBlock(targets(cc.id)[0]?.id)+
    section('Source evidence',pillbox([link('evidence/'+cc.id,'Inspect references ('+(assets.length+cc.examples.length)+')')]));
}
function evidenceView(cc) {
  const assets=data.assets.filter(a=>a.assigned===cc.id);
  const source=(url,label)=>'<a href="'+e(url)+'" target="_blank" rel="noopener noreferrer">'+e(label)+' ↗</a>';
  return heading('Source evidence',cc.name,'Pinned examples document the inspected implementations. Target performance requires a measured run.')+pillbox([kindBadge(cc),ccLink(cc)])+'<div class="evidence">'+
    assets.map(a=>section(a.name,fact('Inspected asset',a.job)+fact('Evidence status',a.status)+fact('Scope',a.scope)+source(a.source,a.sourceLabel)+(a.evidence?' · '+source(a.evidence,a.evidenceLabel):''))).join('')+
    cc.examples.map(x=>'<article class="panel"><small>'+e(x.engine)+'</small><h3>'+source(x.url,x.title)+'</h3><p>'+e(x.detail)+'</p></article>').join('')+'</div>';
}
