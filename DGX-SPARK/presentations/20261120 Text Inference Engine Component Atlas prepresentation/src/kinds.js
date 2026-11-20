// 20261120 edition: CC kinds, tool and analysis CCs, measured evidence and pinned source links.
const kindOrder = ['builder','tool','analysis','factory'];
const ccKind = cc => cc.ccKind || (cc.kind==='factory' ? 'factory' : 'builder');
const kindBadge = cc => { const k=ccKind(cc); return '<span class="kind-badge kind-'+k+'" data-cc-kind="'+k+'">'+e(data.kinds[k].label)+'</span>'; };
const deliveryNames = {builder:'Code delivered',tool:'Receipt delivered',analysis:'Findings delivered',factory:'Artifact delivered on invocation'};
const operators = id => data.operates.filter(([,part])=>part===id).map(([cc])=>capsules.get(cc));
const operated = id => data.operates.filter(([cc])=>cc===id).map(([,part])=>components.get(part));
const measuredFor = id => data.measured.components[id];
function sourceHref(repo, ref) {
  if (repo==='evidence') return ref.path;
  const pin=data.pins[repo];
  return pin.repo+'/blob/'+pin.commit+'/'+ref.path+'#L'+ref.line;
}
function sourceLink(repo, ref) {
  return '<a class="source-link" href="'+e(sourceHref(repo,ref))+'" target="_blank" rel="noopener noreferrer"><b>'+e(repo==='evidence'?'Evidence copy':repo)+'</b> '+e(ref.path)+(ref.symbol?' · '+e(ref.symbol):'')+' ↗</a>';
}
function evidenceLink(path, label) {
  return '<a class="evidence-file" href="'+e(path)+'" target="_blank" rel="noopener">'+e(label||path.split('/').pop())+' ↗</a>';
}
function kindLegend() {
  return '<section class="kind-legend" aria-label="CC kinds"><h2>Four kinds of CC</h2><p>'+e(data.kindNote)+' Counts: '+data.ccs.length+' atlas CCs and '+data.capsuleCatalog.length+' capsule directories in the JiuwenSwarm catalog.</p><dl>'+kindOrder.map(k=>{
    const r=data.kinds[k], n=data.ccs.filter(cc=>ccKind(cc)===k).length, m=data.capsuleCatalog.filter(c=>c.kind===k).length;
    return '<div data-kind-legend="'+k+'"><dt><span class="kind-badge kind-'+k+'">'+e(r.label)+'</span> <small>'+n+' CCs · '+m+' capsules</small></dt><dd><p class="kind-plain" data-kind-plain>'+e(r.plain)+'</p><small>Delivers: '+e(r.delivers)+'. Name rule: '+e(r.naming)+'. Examples: '+r.examples.map(e).join(', ')+'.</small></dd></div>';
  }).join('')+'</dl></section>';
}
function formerNote(row) {
  return row.formerNames?.length ? '<p class="former" data-former>Formerly '+row.formerNames.map(n=>'“'+e(n)+'”').join(', ')+'. Old IDs and links still resolve.</p>' : '';
}
function measuredBlock(id) {
  const m=measuredFor(id); if(!m) return '';
  return '<section class="sheet measured" data-measured="'+e(id)+'"><h2>Measured evidence</h2><p class="caption">'+e(data.measured.context)+'</p>'+
    '<p><span class="tone tone-'+e(m.tone)+'">'+e(m.status)+'</span> '+e(m.summary)+'</p><ul class="measured-rows">'+
    m.rows.map(r=>'<li><span class="tone tone-'+e(r.tone)+'">'+e(r.grade)+'</span><p>'+e(r.result)+'</p>'+evidenceLink(r.link)+'</li>').join('')+'</ul></section>';
}
function measuredChip(id) {
  const m=measuredFor(id);
  return m ? '<div class="measured-chip"><span class="tone tone-'+e(m.tone)+'">'+e(m.status)+'</span> '+evidenceLink(m.rows[0].link,'report')+'</div>' : '';
}
function operatorBlock(id) {
  const rows=operators(id); if(!rows.length) return '';
  return '<section class="sheet" data-operators><h2>Tool and analysis CCs</h2><p>These CCs operate or analyze this component. They return receipts or findings, not component code.</p>'+
    rows.map(cc=>'<article class="operator">'+kindBadge(cc)+' '+ccLink(cc)+'<p>'+e(cc.summary)+'</p></article>').join('')+'</section>';
}
function endpointChildFor(id) {
  for (const p of endpointData.parents) for (const c of p.children) if (c.legacyIds.includes(id)) return c;
}
function sourceBlock(id) {
  const c=endpointChildFor(id); if(!c) return '';
  const rows=[...[c.source,...(c.additionalSources||[])].filter(Boolean).map(r=>['llama.cpp',r]),...(c.strataSources||[]).map(r=>['Strata',r])];
  const local=(c.localSources||[]).map(r=>'<li>'+evidenceLink(r.path,r.label)+' <small>'+e(r.note)+'</small></li>').join('');
  return '<details class="sheet" data-sources><summary>Sources at the pins · '+(rows.length+(c.localSources||[]).length)+'</summary>'+
    '<p class="caption">llama.cpp '+e(data.pins['llama.cpp'].commit.slice(0,8))+' · Strata '+e(data.pins.Strata.commit.slice(0,8))+' · endpoint subcomponent: '+e(c.title)+'</p>'+
    (c.llamaStatus?'<p><b>llama.cpp status.</b> '+e(c.llamaStatus)+'</p>':'')+(c.contractNote?'<p>'+e(c.contractNote)+'</p>':'')+
    '<ul class="source-list">'+rows.map(([repo,r])=>'<li>'+sourceLink(repo,r)+(r.note?' <small>'+e(r.note)+'</small>':'')+'</li>').join('')+local+'</ul></details>';
}
function operatingView(cc) {
  const k=ccKind(cc), parts=operated(cc.id), cap=cc.capsule||{};
  const capsuleText=cap.dir?cap.dir+' (cc.yaml ID '+cap.id+', version '+cap.version+')':'No capsule directory';
  return '<div class="tagline">'+kindBadge(cc)+' '+(k==='tool'?'Operates an existing tool and returns a verified receipt':'Produces findings from retained evidence')+'</div><h1>'+e(cc.name)+'</h1>'+formerNote(cc)+
    '<div data-delivery>'+fact(deliveryNames[k],cc.summary)+'</div>'+
    section(k==='tool'?'Tool job':'Analysis',fact('Inputs',cc.inputs)+fact(k==='tool'?'Receipt contents':'Report contents',cc.outputs)+fact('Method',cc.method)+
      '<div class="fact"><strong>'+(k==='tool'?'Operates on':'Subject components')+'</strong>'+pillbox(parts.map(cmpLink))+'</div>')+
    section('Acceptance evidence',fact('Verifier',cc.verifier)+fact('Helpers and tests',cc.helpers))+
    section('Package',fact('Capsule',capsuleText)+(cap.sha256?fact('Pinned release digest',cap.sha256):'')+fact('Packaging note',cap.note))+
    (cc.findings.length?section('Runs and findings','<ul class="measured-rows">'+cc.findings.map(f=>'<li><p>'+e(f.text)+'</p>'+evidenceLink(f.link)+'</li>').join('')+'</ul>'):'')+
    section('Sources','<ul class="source-list">'+cc.sources.map(r=>'<li>'+sourceLink(r.repo,r)+(r.note?' <small>'+e(r.note)+'</small>':'')+'</li>').join('')+'</ul>'+
      pillbox([link('evidence/'+cc.id,'Inspect references ('+cc.examples.length+')'),link('library?kind='+k,'All '+data.kinds[k].label+' CCs')]));
}
function capsuleTable() {
  return '<details class="sheet capsule-map" id="capsule-map"><summary>Atlas CC IDs and JiuwenSwarm capsule directories · '+data.capsuleMap.length+'</summary><p>'+e(data.capsuleMapNote)+'</p>'+
    '<div class="table-wrap"><table><thead><tr><th>Atlas CC</th><th>Kind</th><th>Capsule directory</th><th>cc.yaml ID</th><th>Version</th><th>Release digest</th></tr></thead><tbody>'+
    data.capsuleMap.map(r=>{const cc=capsules.get(r.atlas);return '<tr data-capsule="'+e(r.dir)+'"><td>'+ccLink(cc)+'<br><code>'+e(r.atlas)+'</code></td><td>'+e(data.kinds[ccKind(cc)].label)+'</td><td><code>'+e(r.dir)+'</code></td><td><code>'+e(r.capsuleId)+'</code></td><td>'+e(r.version)+'</td><td><code title="'+e(r.sha256)+'">'+e(r.sha256.slice(0,12))+'…</code></td></tr>';}).join('')+
    '</tbody></table></div></details>';
}
function capsuleCatalogTable() {
  const rows=data.capsuleCatalog, count=k=>rows.filter(r=>r.kind===k).length;
  return '<section class="sheet capsule-catalog" id="capsule-catalog" aria-label="Capsules in the JiuwenSwarm catalog"><h2>Capsules in the JiuwenSwarm catalog · '+rows.length+'</h2><p>'+e(data.capsuleCatalogNote)+'</p>'+
    '<p class="caption" data-catalog-counts>'+data.ccs.length+' atlas CCs · '+rows.length+' capsule directories ('+kindOrder.map(k=>count(k)+' '+data.kinds[k].label.toLowerCase()).join(', ')+') · '+rows.filter(r=>r.atlas).length+' directories carry an atlas CC.</p>'+
    '<div class="table-wrap"><table><thead><tr><th>Title</th><th>Kind</th><th>Capsule</th><th>What it builds or does</th><th>Related atlas component</th><th>Atlas CC</th></tr></thead><tbody>'+
    rows.map(r=>{const cc=r.atlas&&capsules.get(r.atlas), part=r.relates&&components.get(r.relates);
      return '<tr data-catalog-dir="'+e(r.dir)+'" data-catalog-kind="'+e(r.kind)+'"><td><b data-catalog-title>'+e(r.title)+'</b>'+(r.formerNames?'<br><small>Formerly '+r.formerNames.map(n=>'“'+e(n)+'”').join(', ')+'</small>':'')+'</td><td><span class="kind-badge kind-'+e(r.kind)+'">'+e(data.kinds[r.kind].label)+'</span></td>'+
        '<td><code>'+e(r.dir)+'</code><br><small><code>'+e(r.capsuleId)+'</code></small></td><td>'+e(r.does)+(r.component?'<br><small>Builds: '+e(r.component)+(r.target?' ('+e(r.target)+')':'')+'</small>':'')+'</td>'+
        '<td>'+(part?cmpLink(part):'<small>'+e(r.relatesNote||'None')+'</small>')+'</td><td>'+(cc?ccLink(cc):'<small>Not an atlas CC entry</small>')+'</td></tr>';}).join('')+
    '</tbody></table></div></section>';
}
function catalogCard(cc) {
  const k=ccKind(cc), parts=(k==='tool'||k==='analysis')?operated(cc.id):targets(cc.id);
  return '<a class="listing kind-card kind-'+k+'" href="#cc/'+e(cc.id)+'" data-cc-kind="'+k+'"><div class="kind-row">'+kindBadge(cc)+(cc.added?' <span class="new-tag">New 2026-11-20</span>':'')+'</div><strong>'+e(cc.name)+'</strong>'+
    (cc.requirement?'<p>'+e(cc.requirement)+'</p>':'')+'<div class="caption">'+e(deliveryNames[k])+'</div><p class="cc-summary">'+e(cc.summary)+'</p>'+
    (cc.formerNames?'<p class="former">Formerly '+cc.formerNames.map(n=>'“'+e(n)+'”').join(', ')+'</p>':'')+'<code>'+e(cc.id)+'</code>'+
    '<div class="caption">'+(k==='tool'?'Operates on':k==='analysis'?'Subject':'Component')+': '+parts.map(c=>e(c.name)).join(', ')+'</div></a>';
}
function library(query) {
  const scopes=[['','All CCs'],['builder','Builder CCs'],['tool','Tool CCs'],['analysis','Analysis CCs'],['factory','Factory worker CCs']];
  const older={'Engine':'builder','Software factory':'factory'};
  root.innerHTML='<h1>All CCs</h1><p class="lead">A CC is a packaged tool for agents. An agent can receive several CCs, and several agents can use the same CC. Search by name, former name, component, capsule directory or source symbol.</p>'+actorExample()+kindLegend()+
    '<div class="tools"><input id="search" type="search" aria-label="Search CCs"><select id="scope" aria-label="CC kind">'+scopes.map(([v,l])=>'<option value="'+v+'">'+l+'</option>').join('')+'</select></div><div id="results"></div>'+capsuleCatalogTable()+capsuleTable();
  const input=root.querySelector('#search'), scope=root.querySelector('#scope');
  const wanted=query.get('kind')||older[query.get('scope')]||'';
  input.value=query.get('q')||''; scope.value=scopes.some(([v])=>v===wanted)?wanted:'';
  const capsuleNames=id=>data.capsuleMap.filter(r=>r.atlas===id).flatMap(r=>[r.dir,r.capsuleId]);
  function update() {
    const terms=input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const rows=data.ccs.filter(cc=>{
      const parts=[...targets(cc.id),...operated(cc.id)];
      const hay=[cc.id,cc.legacy,cc.name,cc.summary,cc.requirement,...(cc.formerNames||[]),...parts.flatMap(c=>[c.name,c.id,...(c.formerNames||[])]),
        ...capsuleNames(cc.id),...Object.keys(data.aliases).filter(key=>data.aliases[key]===cc.id),...(cc.examples||[]).map(x=>x.title),...(cc.contents||[]).map(x=>x.name)].join(' ').toLowerCase();
      return (!scope.value||ccKind(cc)===scope.value)&&terms.every(t=>hay.includes(t));
    }).sort((a,b)=>kindOrder.indexOf(ccKind(a))-kindOrder.indexOf(ccKind(b)));
    root.querySelector('#results').innerHTML='<p class="caption">'+rows.length+' CCs</p><div class="cards">'+rows.map(catalogCard).join('')+'</div>';
    history.replaceState(history.state,'',address('library','',{q:input.value,kind:scope.value}));
  }
  input.oninput=update; scope.onchange=update; update();
}
function operatingCoverage() {
  return details('Tool and analysis CCs · '+data.ccs.filter(cc=>['tool','analysis'].includes(ccKind(cc))).length,
    data.ccs.filter(cc=>['tool','analysis'].includes(ccKind(cc))).map(cc=>'<article class="insight"><h3>'+kindBadge(cc)+' '+ccLink(cc)+'</h3>'+fact(deliveryNames[ccKind(cc)],cc.summary)+'<div class="pills">'+operated(cc.id).map(cmpLink).join(' ')+'</div></article>').join(''));
}
