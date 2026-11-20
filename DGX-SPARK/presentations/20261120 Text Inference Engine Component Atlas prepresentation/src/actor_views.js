function actorViewSwitch(base,actionsMode){
  return '<nav class="actor-switch" aria-label="Perspective">'+
    '<a href="#'+base+'" '+(!actionsMode?'aria-current="page"':'')+'>Components</a>'+
    '<a href="#'+base+'/actions" '+(actionsMode?'aria-current="page"':'')+'>Actions</a></nav>';
}
function actorExample(){
  const loader=components.get('weights.checkpoint_reader'),contract=components.get('compiler.contract_compiler'),orchestrator=components.get('factory.workflow_planner');
  const chain=(text,items)=>'<div class="actor-chain"><small>'+e(text)+'</small>'+items.join('<span aria-hidden="true"> → </span>')+'</div>';
  return '<div class="actor-examples">'+
    chain('Builder → component → action performed by code',[ccLink(builders(loader.id)[0]),cmpLink(loader),actLink(actions.get('startup/manifest'))])+
    chain('Reviewed intent and system ontology → contract → agent dispatch',[ccLink(relatedCCs(contract.id)[0]),'<strong>Versioned engine contract</strong>',ccLink(relatedCCs(orchestrator.id)[0]),'<strong>Assigned engine builders</strong>'])+'</div>';
}
function factoryActionOverview(){
  const factoryActions=data.actions.filter(a=>a.id.startsWith('f_'));
  const layers=[...new Set(factoryActions.map(a=>a.layer))];
  root.innerHTML=heading('Software factory','Factory actions','A factory CC performs the assigned work when invoked. Follow the output to see what the next agent receives.')+actorViewSwitch('factory',true)+
    layers.map(layer=>'<section class="sheet"><h2>'+e(layer)+'</h2>'+factoryActions.filter(a=>a.layer===layer).map(a=>
      '<article class="actor-action" data-action-id="'+e(a.id)+'"><div>'+actLink(a)+'</div><div><small>Performed by</small> '+participants(a.id).flatMap(c=>relatedCCs(c.id)).map(ccLink).join(' ')+'</div></article>').join('')+'</section>').join('');
  tabActive('factory');
}
function actionPerformers(a){
  const factory=a.id.startsWith('f_');
  const performerCards=participants(a.id).map(c=>{
    const owners=relatedCCs(c.id),primary=factory?ccLink(owners[0]):cmpLink(c);
    return '<article class="row"><small>'+e(factory?'Factory CC · performs this action on invocation':c.scope==='Host'?'Host provider · supplies this service':scope(c)+' component · performs this action')+'</small>'+
      '<h3>'+primary+'</h3><p>'+e(participationNotes[a.id]?.[c.id]||c.summary)+'</p>'+
      (factory?link('cc/'+owners[0].id,'Inspect the complete capability handoff'):owners.length?'<div>Built or integrated using '+owners.map(ccLink).join(' ')+'</div>':'')+
      (c.scope==='Extension'?fact('Activation',c.when):'')+'</article>';
  });
  return section(factory?'Factory capabilities performing this action':'Components performing this action','<div class="grid">'+performerCards.join('')+'</div>');
}
