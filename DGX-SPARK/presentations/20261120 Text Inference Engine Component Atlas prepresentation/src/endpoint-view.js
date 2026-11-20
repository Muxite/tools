(function () {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const list = value => Array.isArray(value) ? value : value == null ? [] : [value];
  const prose = value => Array.isArray(value) ? '<ul>'+value.map(v=>'<li>'+esc(v)+'</li>').join('')+'</ul>' : '<p>'+esc(value)+'</p>';
  const field = (label, value) => value == null || value === '' ? '' : '<div class="ep-field"><strong>'+esc(label)+'</strong>'+prose(value)+'</div>';
  const records = JSON.parse(document.getElementById('records').textContent);
  const ccName = id => { const rows=records.ccs || []; const cc=rows.find(c=>c.id===id||c.legacy===id); return cc?cc.name:id; };
  const links = ids => list(ids).length ? '<div class="ep-links">'+list(ids).map(id=>'<a href="#cc/'+encodeURIComponent(id)+'">'+esc(ccName(id))+' ↗</a>').join('')+'</div>' : '';
  const workerGroups = row => [['Implementing CCs',row.implementingCCs],['Collaborating CCs',row.collaboratingCCs]].filter(([,ids])=>ids?.length).map(([label,ids])=>'<div class="ep-source"><strong>'+label+'</strong>'+links(ids)+'</div>').join('');
  const pins = records.pins || {};
  const strata = s => '<a target="_blank" rel="noopener noreferrer" href="'+esc(pins.Strata.repo)+'/blob/'+esc(pins.Strata.commit)+'/'+esc(s.path)+'#L'+esc(s.line)+'">Strata · '+esc(s.path)+(s.symbol?' · '+esc(s.symbol):'')+' ↗</a>';
  const kindLabel = id => { const cc=(records.ccs||[]).find(c=>c.id===id); const k=cc&&cc.ccKind; return k&&records.kinds?'<span class="kind-badge kind-'+esc(k)+'">'+esc(records.kinds[k].label)+'</span> ':''; };
  const measuredLine = ids => list(ids).map(id=>{ const m=((records.measured||{}).components||{})[id]; return m?'<div class="ep-measured-line" data-measured="'+esc(id)+'"><strong>Measured 2026-11-20</strong> <span class="tone tone-'+esc(m.tone)+'">'+esc(m.status)+'</span> '+esc(m.summary)+' <a href="'+esc(m.rows[0].link)+'" target="_blank" rel="noopener">'+esc(m.rows[0].link.split('/').pop())+' ↗</a></div>':''; }).join('');
  const childSources = c => {
    const extra = list(c.additionalSources).map(x=>'<li>'+source(x)+(x.note?' <small>'+esc(x.note)+'</small>':'')+'</li>').join('');
    const st = list(c.strataSources).map(x=>'<li>'+strata(x)+(x.note?' <small>'+esc(x.note)+'</small>':'')+'</li>').join('');
    const local = list(c.localSources).map(x=>'<li><a href="'+esc(x.path)+'" target="_blank" rel="noopener">'+esc(x.label)+' ↗</a> <small>'+esc(x.note)+'</small></li>').join('');
    return (c.llamaStatus?'<p class="ep-status-note"><strong>llama.cpp status</strong> '+esc(c.llamaStatus)+'</p>':'')+(c.contractNote?'<p>'+esc(c.contractNote)+'</p>':'')+
      (extra||st||local?'<ul class="source-list">'+extra+st+local+'</ul>':'');
  };
  const operating = ids => list(ids).length ? '<div class="ep-source"><strong>Tool and analysis CCs</strong><div class="ep-links">'+list(ids).map(id=>'<a href="#cc/'+encodeURIComponent(id)+'">'+kindLabel(id)+esc(ccName(id))+' ↗</a>').join('')+'</div></div>' : '';
  const source = s => s && s.path ? '<a target="_blank" rel="noopener noreferrer" href="https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/'+esc(s.path)+'#L'+esc(s.line)+'">'+esc(s.path)+(s.symbol?' · '+esc(s.symbol):'')+' ↗</a>' : '';
  const sources = rows => list(rows).map(s=>'<a target="_blank" rel="noopener noreferrer" href="'+esc(s.url)+'">'+esc(s.label)+' ↗</a>').join(' · ');
  const componentLinks = ids => list(ids).length ? '<div class="ep-links">'+list(ids).map(id=>{const c=(records.components||[]).find(x=>x.id===id);return '<a href="#component/'+encodeURIComponent(id)+'">'+esc(c?c.name:id)+' ↗</a>';}).join('')+'</div>' : '';
  const button = (view, label, active) => '<a href="'+(view==='map'?'#engine':'#endpoint/'+view)+'"'+(active?' aria-current="page"':'')+'>'+esc(label)+'</a>';
  const panel = (label, title, text) => '<div class="ep-heading"><span class="ep-eyebrow">'+esc(label)+'</span><h1>'+esc(title)+'</h1><p>'+esc(text)+'</p></div>';
  function coverage(d){const n=list(d.parents).reduce((a,p)=>a+list(p.children).length,0),m=list(d.parents).reduce((a,p)=>a+list(p.children).reduce((b,c)=>b+list(c.legacyIds).length,0),0);return panel('Scope and source coverage','What this map includes','The '+m+' engine and extension records are grouped into '+n+' subcomponents. Six factory and four host records remain in the original atlas. llama.cpp anchors are at '+String(d.revision).slice(0,8)+'; Strata anchors are at '+String(d.strataRevision||'').slice(0,8)+'.')+boundaryGuide()+'<p>Source anchors are examples at revision '+esc(d.revision)+', not proof that every target behavior is implemented.</p><div class="ep-stack">'+list(d.boundaries).map(b=>'<article class="ep-detail"><span class="ep-eyebrow">'+esc(b.status)+'</span><h2>'+esc(b.title)+'</h2>'+prose(b.detail)+'<div class="ep-fields">'+field('Caller',b.caller)+field('Acceptance',b.acceptance)+field('Reviewed paths',b.reviewedPaths)+field('Integration',b.integrationStatus)+field('Qualification',b.qualificationStatus)+'</div>'+(b.source?'<div class="ep-source">'+source(b.source)+'</div>':'')+workerGroups(b)+'</article>').join('')+'</div>';}
  function parent(d,id) {
    if(id==='memory')return panel('Component index','Inference memory','This former group now has two owners. They draw on the same machine memory budget.')+
      '<div class="ep-links"><a href="#endpoint/parent/sequence-state">Sequence state · KV pages, recurrent state and prefix reuse</a><a href="#endpoint/parent/weight-residency">Weight residency · placement, expert slots and prefetch</a><a href="#endpoint/demo">Compare the memory budgets in the demo</a></div>';
    const p=(d.parents||[]).find(x=>x.id===id); if(!p)return endpointRelationshipMap(d);
    return '<a class="ep-back" href="#engine">← All components</a>'+panel('Component',p.title,p.summary)+
      '<div class="ep-stack">'+list(p.children).map(c=>'<article class="ep-detail"><div class="ep-detail-head"><div><span class="ep-eyebrow">Responsibility</span><h2>'+esc(c.title)+'</h2></div><span class="ep-status">'+esc(c.status||'Contract')+'</span></div><div class="ep-fields">'+field('Caller',c.caller)+field('Action',c.action)+field('Acceptance evidence',c.acceptance)+'</div>'+(c.source?'<div class="ep-source"><strong>Source</strong> '+source(c.source)+'</div>':'')+childSources(c)+measuredLine(c.legacyIds)+componentLinks(c.legacyIds)+links(c.builderIds)+operating(c.operatingCCs)+'</article>').join('')+'</div>';
  }
  function ranks(s) { return panel('Priorities','Engineering focus for the constrained-memory MoE demo','Ten responsibilities ranked by their relevance to a correct, measurable speedup. The five starred entries are the focus of the experiment.')+'<div class="ep-ranks">'+list(s.rankings).map((r,i)=>'<article class="ep-rank"><span class="ep-ranknum">'+String(i+1).padStart(2,'0')+'</span><div><h2>'+esc(r.title)+'</h2>'+prose(r.summary)+links(r.legacyIds)+'</div>'+(r.star?'<span class="ep-star is-starred" aria-label="Starred priority">★</span>':'')+'</article>').join('')+'</div>'; }
  function changes(d) { const name=id=>(list(d.parents).find(p=>p.id===id)||{}).title||id; const parentLink=id=>'<a href="#endpoint/parent/'+encodeURIComponent(id)+'">'+esc(name(id))+'</a>'; return panel('Change ownership','What would I change?','Each scenario names an accountable owner, the collaborators and the evidence needed to accept the change.')+'<div class="ep-stack">'+list(d.scenarios).map(c=>'<article class="ep-detail"><span class="ep-eyebrow">Change scenario</span><h2>'+esc(c.title)+'</h2><div class="ep-fields"><div class="ep-field"><strong>Owner</strong><p>'+parentLink(c.owner)+'</p></div><div class="ep-field"><strong>Collaborators</strong><p>'+list(c.collaborators).map(parentLink).join(', ')+'</p></div>'+field('Inputs',c.inputs)+field('Output',c.output)+field('Acceptance',c.acceptance)+'</div>'+(c.source?'<div class="ep-source"><strong>Source example</strong> '+source(c.source)+list(c.additionalSources).map(x=>' · '+source(x)).join('')+'</div>':'')+workerGroups(c)+operating(c.operatingCCs)+'</article>').join('')+'</div>'; }
  function walks(s) { return panel('Walkthroughs','Follow the handoffs','Trace a request and a model pack through the components and their interfaces.')+'<div class="ep-walks">'+list(s.walkthroughs).map(w=>'<article class="ep-detail"><span class="ep-eyebrow">Guided path</span><h2>'+esc(w.title)+'</h2>'+prose(w.summary)+'<ol class="ep-steps">'+list(w.steps).map(t=>'<li><strong>'+esc(t.title)+'</strong>'+prose(t.body)+links(t.legacyIds)+sources(t.sources)+'</li>').join('')+'</ol></article>').join('')+'</div>'; }
  function demo(s) { const d=s.demo||{}; return panel('Performance experiment',d.title||'Predictor demonstration',d.summary||'')+'<div class="ep-callout">'+field('Baseline',d.baseline)+'</div>'+budgetComparison()+'<div class="ep-metrics">'+list(d.metrics).map(m=>'<div><strong>'+esc(m.label)+'</strong><span>'+esc(m.value)+'</span></div>').join('')+'</div><div class="ep-detail"><h2>How to run the comparison</h2><ol class="ep-steps">'+list(d.steps).map(t=>'<li><strong>'+esc(t.title)+'</strong>'+prose(t.body)+links(t.legacyIds)+list(t.legacyIds).map(id=>'<a href="#evidence/'+encodeURIComponent(id)+'">'+esc(ccName(id))+' evidence ↗</a>').join(' · ')+(t.sources?.length?' · '+sources(t.sources):'')+'</li>').join('')+'</ol>'+field('Limits of the evidence',d.limitations)+'</div>'; }
  function measured() {
    const m=records.measured||{components:{}}, rows=Object.entries(m.components);
    const name=id=>((records.components||[]).find(c=>c.id===id)||{}).name||id;
    const local=path=>{const x=String(path).match(/OPS\/iterations\/([^/]+)\/(report(?:-v\d+)?)\.md$/);return x?'evidence/reports/'+x[1]+'--'+x[2]+'.md':null;};
    const available=new Set(rows.flatMap(([,r])=>r.rows.map(x=>x.link)).concat(records.localReports||[]));
    const headline=(records.headlines||{rows:[]}).rows.map(r=>{const src=(r.sources||[])[0]||{},path=local(src.path);
      return '<tr><td>'+esc(r.arm)+'</td><td>'+esc(r.grade)+'</td><td>'+esc(r.ttft)+'</td><td>'+esc(r.decode)+'</td><td>'+esc(r.summary)+'</td><td>'+(path&&available.has(path)?'<a href="'+esc(path)+'" target="_blank" rel="noopener">'+esc(path.split('/').pop())+' ↗</a>':'<code>'+esc(src.path||'')+'</code>')+'</td></tr>';}).join('');
    return panel('Measured evidence','What the 2026-11-20 runs showed per component',m.context||'')+
      '<div class="ep-stack">'+rows.map(([id,r])=>'<article class="ep-detail" data-measured="'+esc(id)+'"><div class="ep-detail-head"><div><span class="ep-eyebrow">Component</span><h2><a href="#component/'+encodeURIComponent(id)+'">'+esc(name(id))+'</a></h2></div><span class="tone tone-'+esc(r.tone)+'">'+esc(r.status)+'</span></div><p>'+esc(r.summary)+'</p><ul class="measured-rows">'+
        r.rows.map(x=>'<li><span class="tone tone-'+esc(x.tone)+'">'+esc(x.grade)+'</span><p>'+esc(x.result)+'</p><a href="'+esc(x.link)+'" target="_blank" rel="noopener">'+esc(x.link.split('/').pop())+' ↗</a></li>').join('')+'</ul></article>').join('')+'</div>'+
      '<section class="ep-detail"><h2>Headline rows as staged</h2><p>Copied from <a href="evidence/final-headlines.json" target="_blank" rel="noopener">final-headlines.json ↗</a>. Its 60 GiB row is the report-v2 screening result; report-v3 (quiet ABBA, 27.08 / 92.07 s saved) supersedes it above. Rows without a local report copy keep their Spark path.</p><div class="table-wrap"><table><thead><tr><th>Arm</th><th>Grade</th><th>TTFT</th><th>Decode</th><th>Summary</th><th>Report</th></tr></thead><tbody>'+headline+'</tbody></table></div></section>';
  }
  function campaign() {
    const c=records.campaign||{}, meas=(records.measured||{}).components||{};
    const cmpName=id=>((records.components||[]).find(x=>x.id===id)||{}).name||id;
    const ccRow=id=>(records.ccs||[]).find(x=>x.id===id)||{};
    const report=path=>'<a href="'+esc(path)+'" target="_blank" rel="noopener">'+esc(path.split('/').pop())+' ↗</a>';
    const builders=list(c.builders).map(b=>{const m=meas[b.component]||{};return '<tr data-campaign-cc="'+esc(b.cc)+'"><td><b>'+esc(b.arm)+'</b></td><td>'+kindLabel(b.cc)+'<a href="#cc/'+encodeURIComponent(b.cc)+'">'+esc(ccName(b.cc))+'</a><br><small>Component: <a href="#component/'+encodeURIComponent(b.component)+'">'+esc(cmpName(b.component))+'</a></small></td><td>'+esc(b.built)+'</td><td>'+esc(b.build)+'</td><td>'+esc(b.lab)+'</td><td><span class="tone tone-'+esc(m.tone)+'">'+esc(m.status)+'</span><br>'+report(b.link)+'</td></tr>';}).join('');
    const d=c.combined||{};
    const combined=d.arm?'<tr data-campaign-combined><td><b>'+esc(d.arm)+'</b></td><td>'+esc(d.title)+'</td><td colspan="3">'+esc(d.result)+'</td><td><span class="tone tone-'+esc(d.tone)+'">'+esc(d.status)+'</span><br>'+report(d.link)+'</td></tr>':'';
    const operating=list(c.operating).map(id=>{const cc=ccRow(id), f=list(cc.findings)[0];return '<tr data-campaign-cc="'+esc(id)+'"><td>'+kindLabel(id)+'<a href="#cc/'+encodeURIComponent(id)+'">'+esc(ccName(id))+'</a></td><td>'+esc(cc.summary)+'</td><td>'+(f?esc(f.text)+'<br>'+report(f.link):'')+'</td></tr>';}).join('');
    return panel('Spark campaign 2026-11-20',c.title||'Spark campaign 2026-11-20',c.context||'')+
      '<div class="ep-callout" data-campaign-contrast><p>'+esc(c.contrast)+'</p></div>'+
      '<div class="ep-metrics ep-counts" data-campaign-counts>'+list(c.counts).map(n=>'<div><strong>'+esc(n.value)+'</strong><span>'+esc(n.label)+'</span></div>').join('')+'</div><p class="caption">'+esc(c.countsSource)+'</p>'+
      '<section class="ep-detail" data-campaign-builders><h2>Builder CCs applied on the target</h2><p>Each builder CC wrote the source code for one engine component. Results compare the built engine with same-budget stock llama.cpp with its native MoE cache (A+).</p><div class="table-wrap"><table><thead><tr><th>Arm</th><th>CC</th><th>What it built</th><th>Build and verify</th><th>Lab outcome</th><th>Result label</th></tr></thead><tbody>'+builders+combined+'</tbody></table></div></section>'+
      '<section class="ep-detail" data-campaign-operating><h2>Tool and analysis CCs that ran, built and read the evidence</h2><div class="table-wrap"><table><thead><tr><th>CC</th><th>What it does</th><th>Campaign finding</th></tr></thead><tbody>'+operating+'</tbody></table></div></section>';
  }
  function budgetComparison() {
    const cap = 96, fixed = 52, workspace = 8, headroom = 4;
    const cards = [['Shorter context', 8], ['Longer context', 16]].map(([label, sequence]) => {
      const expert = cap - fixed - workspace - headroom - sequence;
      return '<article><h3>'+label+'</h3><div class="budget-bar" aria-hidden="true">'+
        [[fixed+workspace+headroom,'base'],[sequence,'seq'],[expert,'expert']].map(([amount,kind])=>
          '<span class="'+kind+'" style="width:'+100*amount/cap+'%"></span>').join('')+'</div>'+
        '<p><b>'+sequence+' GiB</b> sequence reservation<br><b>'+expert+' GiB</b> available for expert slots</p></article>';
    }).join('');
    return '<section class="ep-budget"><h2>One memory budget, two owners</h2><p>Illustrative configurations with the same 96 GiB cap. Both reserve 52 GiB for fixed allocations (including resident weights), 8 GiB for workspace and 4 GiB of headroom. Each physical allocation counts once.</p><div class="budget-examples">'+cards+'</div>'+
      '<p>Increasing the <a href="#endpoint/parent/sequence-state">Sequence state</a> reservation by 8 GiB leaves <a href="#endpoint/parent/weight-residency">Weight residency</a> 8 GiB less for expert slots. This is a planning comparison between server configurations. Measure the actual allocations and peak on the target.</p></section>';
  }
  window.renderEndpoint = function (container) {
    const d=window.endpointData || (typeof endpointData !== 'undefined' ? endpointData : {}), s=window.endpointStory || (typeof endpointStory !== 'undefined' ? endpointStory : {});
    const route=location.hash.replace(/^#endpoint\/?/,'').split('/');
    let view=location.hash==='#engine'?'map':(route[0]||'map'), selected=decodeURIComponent(route[1]||'');
    function draw() {
      container.classList.add('endpoint');
      const nav='<nav class="ep-nav" aria-label="Architecture views">'+[['map','Component map'],['ranks','Priorities'],['changes','What would I change?'],['walks','Walkthroughs'],['demo','Performance demo'],['campaign','Spark campaign 2026-11-20'],['measured','Measured evidence'],['coverage','Source coverage']].map(([id,label])=>button(id,label,view===id||(id==='map'&&view==='parent'))).join('')+'</nav>';
      container.innerHTML=nav+'<div class="ep-content">'+(view==='parent'?parent(d,selected):view==='ranks'?ranks(s):view==='changes'?changes(d):view==='walks'?walks(s):view==='demo'?demo(s):view==='measured'?measured():view==='campaign'?campaign():view==='coverage'?coverage(d):endpointRelationshipMap(d))+'</div>';
    }
    draw();
  };
})();
