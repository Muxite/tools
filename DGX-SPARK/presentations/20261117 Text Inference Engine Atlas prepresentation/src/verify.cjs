const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

async function verifyConstruction(page, roleRecords, jump) {
  const jobs = await page.evaluate(() => constructionJobs);
  const roles = new Set(roleRecords.map(r => r.id));
  const assigned = new Set(jobs.flatMap(job => job.cc));
  for (const role of roleRecords.filter(r => r.essential)) {
    assert(assigned.has(role.id),'No construction order owns essential CC ' + role.id);
  }
  const byID = new Map(jobs.map(job => [job.id,job]));
  assert(jobs.length && byID.size === jobs.length, 'Work orders need unique IDs');
  const visiting = new Set(), complete = new Set();
  function visit(id) {
    if (complete.has(id)) return;
    assert(!visiting.has(id), 'Cycle in work orders at ' + id);
    visiting.add(id);
    const job = byID.get(id);
    assert(job.agent && job.output && job.work && job.lane && job.cc.length, 'Incomplete work order: ' + id);
    for (const cc of job.cc) assert(roles.has(cc), id + ' references missing CC ' + cc);
    for (const [provider,receipt] of job.needs) {
      assert(byID.has(provider) && receipt, id + ' needs a provider and receipt');
      visit(provider);
    }
    visiting.delete(id);
    complete.add(id);
  }
  for (const id of byID.keys()) visit(id);
  await jump('#construction');
  await page.locator('#engine-variations').waitFor({state:'attached'});
  const simulator=page.locator('#ready-jobs');
  const ready=()=>simulator.locator('[data-accept]').evaluateAll(buttons=>buttons.map(b=>b.dataset.accept).sort());
  const accept=id=>simulator.locator('[data-accept="'+id+'"]').click();
  assert.deepEqual(await ready(),['intent']);
  await accept('intent');
  assert.deepEqual(await ready(),['contract']);
  await accept('contract');
  assert.deepEqual(await ready(),['plan']);
  await accept('plan');
  assert.deepEqual(await ready(),['reference','routing','serving','state','weights']);
  await accept('weights');
  assert(!(await ready()).includes('placement'));
  await accept('state');
  assert((await ready()).includes('placement'),'Placement must unlock when weights and state receipts are available');
  await simulator.locator('#undo-build').click();
  assert(!(await ready()).includes('placement') && (await ready()).includes('state'),'Undo must withdraw the downstream placement admission');
  const index = await page.locator('a[data-job]').evaluateAll(links => links.map(a=>[a.dataset.job,a.getAttribute('href')]));
  assert.deepEqual([...new Set(index.map(([id])=>id))].sort(),[...byID.keys()].sort(),'Construction overview misses work orders');
  for (const [id,href] of index) assert.equal(href,'#construction/'+id);
  const detail = page.locator('#work-order');
  const example = jobs.find(job=>job.needs.length);
  assert(example, 'No linked producer/consumer work orders');
  await page.locator('a[data-job="'+example.id+'"]').first().click();
  await detail.waitFor();
  await detail.locator('a[href="#construction/'+example.needs[0][0]+'"]').first().click();
  await page.waitForFunction(id=>location.hash === '#construction/'+id,example.needs[0][0]);
  await page.locator('#page-back').click();
  await page.waitForFunction(id=>location.hash === '#construction/'+id,example.id);
  await page.locator('#page-back').click();
  await page.waitForFunction(()=>location.hash==='#construction');
  for (const job of jobs) {
    await jump('#construction/'+job.id);
    await detail.waitFor();
    const hrefs = new Set(await detail.locator('a[href]').evaluateAll(links=>links.map(a=>a.getAttribute('href'))));
    for (const cc of job.cc) assert(hrefs.has('#cc/'+cc),job.id+' has no working CC link to '+cc);
    for (const [provider,receipt] of job.needs) {
      assert(hrefs.has('#construction/'+provider),job.id+' has no link to '+provider);
      assert((await detail.textContent()).includes(receipt),job.id+' does not identify consumed receipt '+receipt);
    }
    assert((await detail.textContent()).includes(job.output),job.id+' omits its deliverable');
  }
  await jump('#construction/'+example.id);
  const cc = example.cc[0];
  await detail.locator('a[href="#cc/'+cc+'"]').first().click();
  await page.locator('.receipt').first().waitFor();
  await page.locator('#page-back').click();
  await page.waitForFunction(id=>location.hash === '#construction/'+id,example.id);
  return example.id;
}

async function main() {
  const location = process.argv[2];
  assert(location && path.isAbsolute(location), 'Pass the absolute path of the built HTML site.');
  const url = pathToFileURL(location).href;
  const browser = await chromium.launch({ executablePath: process.env.BROWSER_PATH || undefined });
  try {
    const context = await browser.newContext({ offline: true, viewport: { width: 1440, height: 980 } });
    const page = await context.newPage();
    const errors = [], requests = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('request', r => { if (/^https?:/.test(r.url())) requests.push(r.url()); });
    page.setDefaultTimeout(5000);
    await page.goto(url);
    await page.locator('.ax-engine svg').waitFor();
    const data = await page.locator('#dataset').evaluate(el => JSON.parse(el.textContent));
    for (const role of data.roles) {
      assert(role.title && role.title !== role.id,role.id+' needs a job title');
      assert(role.contents.length >= 2,role.id+' needs a capability mix');
      for (const cap of role.contents) assert(['component','tool','skill','method'].includes(cap.kind) && cap.name && cap.detail);
    }
    const roles = new Set(data.roles.map(r => r.id));
    const layers = [...data.engine, ...data.factory];
    const layerIds = new Set(layers.map(x => x.id));
    const worksites = new Set();
    function edgesAreClosed(rows, ids, group) {
      for (const [from,to,label] of rows) {
        assert(ids.has(from) && ids.has(to) && label.trim(), group + ' has a broken or unlabeled edge: ' + [from,to,label].join(' / '));
      }
    }
    assert.equal(layerIds.size, layers.length);
    assert.equal(data.engine.length, 8);
    assert(![...roles].some(r => r.startsWith('media.')), 'Non-text work in the active catalog');
    edgesAreClosed(data.edges, new Set(data.engine.map(l => l.id)), 'Engine');
    edgesAreClosed(data.factoryEdges, new Set(data.factory.map(l => l.id)), 'Factory');
    for (const l of layers) {
      const ids = new Set(l.ops.map(o => o.id));
      assert.equal(ids.size, l.ops.length);
      edgesAreClosed(l.edges, ids, l.id);
      for (const op of l.ops) {
        for (const cc of op.cc) {
          assert(roles.has(cc), 'Unresolved operation CC at ' + l.id + '/' + op.id + ': ' + cc);
          worksites.add(cc);
        }
      }
    }
    assert.deepEqual([...roles].sort(), [...worksites].sort(), 'A retained CC is missing from the graphs');
    assert.deepEqual([...new Set(data.sources.map(x => x.engine))].sort(), ['SGLang','Strata','ds4','llama.cpp'].sort());
    assert(data.sources.every(s => s.url && s.symbol), 'A source example is missing its citation');
    assert(data.assets.length && data.roles.length);
    for (const t of data.traces) {
      for (const [layer,operation,cc,explanation] of t.steps) {
        assert(layerIds.has(layer), 'Trace references missing layer: ' + layer);
        assert(roles.has(cc), 'Trace references missing CC: ' + cc);
        const target = layers.find(l => l.id === layer).ops.find(o => o.id === operation);
        assert(target && target.cc.includes(cc) && explanation, 'Trace step has no operation/CC binding: ' + t.id);
      }
    }
    const graphNode = id => page.locator('.ax-canvas [data-ax-id="' + id + '"]').first();
    const jump = async hash => {
      await page.evaluate(h => { window.location.hash = h; }, hash);
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    };
    const testAccess = async () => {
      const defects = await page.locator('.ax-canvas .ax-node,.ax-canvas .ax-wire').evaluateAll(els =>
        els.filter(el => el.getAttribute('role') !== 'button' || el.getAttribute('tabindex') !== '0' ||
          !el.getAttribute('aria-label')).map(el => el.outerHTML.slice(0,140)));
      assert.deepEqual(defects, [], 'An interactive graph element has no keyboard or accessible label');
    };
    await testAccess();
    assert.equal(await page.locator('.ax-canvas .ax-wire').count(), data.edges.length, 'Engine overview omits a relationship');
    const firstEdge = page.locator('.ax-canvas .ax-wire').first();
    await firstEdge.focus();
    await page.keyboard.press('Enter');
    await page.getByText('Handoff · ' + data.edges[0][2], { exact:true }).waitFor();
    await graphNode('model').focus();
    await page.keyboard.press('Enter');
    const route = data.engine.find(l => l.id === 'model').ops.find(o => o.id === 'route' && o.cc.includes('model.expert_routing'));
    assert(route, 'Model diagram is missing authoritative routing');
    if (route.group) {
      const group = graphNode('@group/' + route.group);
      await group.waitFor();
      await group.focus();
      await page.keyboard.press('Enter');
    }
    await graphNode(route.id).waitFor();
    await graphNode(route.id).focus();
    await page.keyboard.press('Space');
    await graphNode('model.expert_routing').waitFor();
    await testAccess();
    await graphNode('model.expert_routing').click();
    await page.waitForFunction(() => document.querySelector('main').textContent.includes('model.expert_routing'));
    await jump('#cc/routing.top_k');
    assert((await page.locator('main').innerText()).includes('model.expert_routing'), 'Legacy routing link failed');
    const router = page.locator('#routing-case');
    await router.selectOption('0.08');
    assert((await page.locator('#routing-out').innerText()).includes('E0 and E2'));
    assert((await page.locator('#routing-out').innerText()).includes('0.4286'));
    await router.selectOption('0');
    assert((await page.locator('#routing-out').innerText()).includes('E0 and E1'));
    assert.equal(data.roles.filter(r=>r.kind==='factory').length,6);
    const spec=data.factory.find(layer=>layer.id==='f_spec');
    assert.deepEqual(spec.ops.find(op=>op.id==='intake').cc,['compiler.intent_brief']);
    assert.deepEqual(spec.ops.find(op=>op.id==='freeze').cc,['compiler.engine_contract']);
    for(const [id,title] of [['compiler.intent_brief','Intent Compiler'],['compiler.engine_contract','Contract Compiler']]){
      const cc=data.roles.find(r=>r.id===id);
      assert(cc.essential && cc.title===title);
    }
    for(const r of data.roles.filter(r=>r.kind!=='factory'&&r.target!==false)){
      assert(data.sources.some(s=>s.assigned===r.id&&s.url)||data.muse.byRole[r.id]?.length,r.id);
    }
    await jump('#cc/model.normalization');
    await page.getByRole('heading',{name:'Normalization at a decoder site'}).waitFor();
    await jump('#factory/f_lab');
    assert.equal(await page.locator('.ax-canvas [data-ax-id="factory.controlled_experiment"]').count(),1);
    await graphNode('factory.controlled_experiment').click();
    await page.waitForFunction(()=>location.hash.includes('cc=factory.controlled_experiment'));
    await jump('#factory');
    await page.locator('.ax-factory svg').waitFor();
    assert.equal(await page.locator('.ax-canvas .ax-wire').count(), data.factoryEdges.length, 'Factory overview omits a handoff');
    const first = data.factory[0];
    await graphNode(first.id).click();
    await graphNode(first.ops[0].id).waitFor();
    await jump('#library?q=dequantize_q6_K');
    assert((await page.locator('main').innerText()).includes('weights.decode_blocks'), 'Library misses a source-symbol match');
    await jump('#sources');
    assert(await page.locator('main a[href*="github.com/"]').count() > 0, 'Evidence view contains no upstream source links');
    for(const section of ['paths-section','matrix-section','history-section']){
      await page.locator('button[data-section="'+section+'"]').click();
      assert.equal(await page.evaluate(()=>document.activeElement.id),section);
    }
    for(const trail of await page.locator('#paths-section details').all()){
      await trail.locator('summary').click();
      assert.equal(await trail.locator('ol li').count(),4);
      assert.equal(await trail.locator('ol a[href*="/blob/"]').count(),4);
    }
    const repoNames = ['Strata','llama.cpp','ds4','SGLang'];
    const targetRoles = data.roles.filter(r => r.kind !== 'factory' && r.target !== false);
    const matrix = page.locator('table.matrix');
    assert.deepEqual((await matrix.locator('thead th').allTextContents()).slice(1),repoNames);
    assert.equal(await matrix.locator('tbody tr').count(),targetRoles.length);
    for (const [i,r] of targetRoles.entries()) {
      const row = matrix.locator('tbody tr').nth(i);
      assert.equal(await row.locator('th a').getAttribute('href'),'#cc/'+r.id);
      assert(r.examples.length,'No inspected example for ' + r.id);
      for (const [j,name] of repoNames.entries()) {
        const refs=r.examples.filter(e=>e.engine===name);
        const cell=row.locator('td').nth(j);
        assert.equal(await cell.innerText(),refs.length ? String(refs.length) : '—',r.id+' / '+name);
        if (refs.length) {
          const repo=data.repositories.find(x=>x.engine===name);
          assert(refs.every(e=>e.url.startsWith(repo.base+'/blob/'+repo.pin+'/')&&e.title&&e.detail),r.id+' needs pinned '+name+' evidence');
        }
      }
    }
    for (const name of repoNames) {
      const sample = targetRoles.find(r => r.examples.some(e=>e.engine===name));
      assert(sample,'No matrix sources for '+name);
      await jump('#sources');
      const href = '#sources/'+sample.id+'?engine='+encodeURIComponent(name);
      const pick = page.locator('table.matrix a[href="'+href+'"]');
      await pick.click();
      await page.getByRole('heading',{name:sample.title,exact:true}).waitFor();
      const expected=sample.examples.filter(e=>e.engine===name);
      assert.deepEqual(await page.locator('main .cap-row a').evaluateAll(as=>as.map(a=>a.href)),expected.map(e=>e.url));
    }
    await jump('#library');
    await page.locator('#search').fill('dequantize_q6_K');
    await page.locator('#scope').selectOption('Engine');
    const listHash=await page.evaluate(()=>location.hash);
    await page.locator('#results a[href="#cc/weights.decode_blocks"]').click();
    await page.locator('.receipt').first().waitFor();
    const ccHash=await page.evaluate(()=>location.hash);
    const slice=page.locator('main a[href^="#sources/weights.decode_blocks?engine="]').first();
    const sliceHash=await slice.getAttribute('href');
    await slice.click();
    await page.locator('main .cap-row a').first().waitFor();
    await page.locator('#page-back').click();
    await page.waitForFunction(h=>location.hash===h,ccHash);
    await page.locator('#page-back').click();
    await page.waitForFunction(h=>location.hash===h,listHash);
    assert.equal(await page.locator('#search').inputValue(),'dequantize_q6_K');
    assert.equal(await page.locator('#scope').inputValue(),'Engine');
    await page.goForward();
    await page.waitForFunction(h=>location.hash===h,ccHash);
    await page.goForward();
    await page.waitForFunction(h=>location.hash===h,sliceHash);
    await page.getByRole('link',{name:'Inspect CC and handoff'}).click();
    await page.getByRole('link',{name:'Quantization experiments'}).click();
    await page.getByRole('heading',{name:'Quantization experiments',exact:true}).waitFor();
    assert.equal(await page.locator('.quant-steps article').count(),5);
    assert((await page.locator('main').innerText()).includes('held-out'));
    await page.getByRole('link',{name:'Run the trial'}).click();
    await page.locator('.receipt').first().waitFor();
    assert((await page.locator('.receipt').first().innerText()).includes('RSI decision'));
    for (const r of data.roles) {
      assert(r.handoff.signals.length && r.handoff.artifact && r.handoff.consumer && r.handoff.proof && r.handoff.rsi,r.id+' handoff is incomplete');
      await jump('#cc/'+r.id);
      const receipt=page.locator('.receipt').first();
      await receipt.waitFor();
      assert((await receipt.innerText()).includes(r.handoff.artifact),r.id+' shows an incorrect handoff');
    }
    await jump('#cc/memory.kv_tiering');
    await graphNode('memory.sequence_kv').waitFor();
    await page.getByText('When moving KV pages between tiers',{exact:true}).click();
    assert((await page.locator('main').innerText()).includes(data.roles.find(r=>r.id==='memory.sequence_kv').tierHandoff.proof));
    await jump('#cc/observability.runtime_events');
    await page.getByRole('heading',{name:'Optional NVTX instrumentation'}).waitFor();
    await jump('#engine');
    const walks = page.locator('[data-walk]');
    for (const t of data.traces) {
      const trigger = walks.filter({ hasText:t.title }).first();
      if (await trigger.count()) await trigger.click();
      else await page.locator('[data-walk="' + t.id + '"]').first().click();
      await page.locator('.steps').first().waitFor();
      assert.equal(await page.locator('.steps a').count(),t.steps.length);
      for (const [n,step] of t.steps.entries()) {
        await page.locator('.steps a').nth(n).click();
        await page.locator('.steps a[aria-current="step"]').filter({hasText:(n+1)+'. '}).waitFor();
        await graphNode(step[2]).waitFor();
        assert((await page.locator('main').innerText()).includes(step[3]), 'Trace step is missing its evidence or test');
      }
      await jump('#engine');
    }
    await jump('#construction/designs');
    assert.equal(await page.locator('nav [aria-current="page"]').innerText(),'Compare engines');
    assert.equal(await page.locator('.comparison-group').count(),4);
    assert(await page.locator('.proof-chip.single').count()>0 && await page.locator('.proof-chip.paper').count()>0);
    for(const card of await page.locator('.comparison-group article').all()){
      const ccLinks=await card.locator('a[href^="#cc/"]').evaluateAll(links=>links.map(a=>a.hash.slice(4)));
      assert(ccLinks.length && ccLinks.every(cc=>roles.has(cc)));
      assert(await card.locator('details a[href^="https://"]').count()>0);
    }
    await jump('#construction/trials');
    assert.equal(await page.locator('.spark-trial').count(),8);
    for(const t of await page.evaluate(()=>sparkTrials)){
      assert(roles.has(t.owner)&&t.partners.every(x=>roles.has(x)));
      await jump('#construction/trial-'+t.id);
      assert.equal(await page.locator('main h1').innerText(),t.title);
      assert.equal(await page.locator('.spark-trial').count(),1);
      assert(await page.locator('.spark-trial').innerText().then(text=>text.includes(t.decision)));
    }
    const jobId=await verifyConstruction(page,data.roles,jump);
    await page.setViewportSize({ width:390, height:844 });
    for (const h of ['#engine','#engine/model?op=' + route.id,'#factory','#library','#sources','#quantization','#sources/weights.decode_blocks?engine=Strata','#construction/trials','#construction/designs','#construction','#construction/'+jobId]) {
      await jump(h);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'Horizontal page overflow at ' + h);
    }
    await jump('#engine/model?op=route');
    await graphNode('backend/row').focus();
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => location.hash.includes('engine/backend') && location.hash.includes('op=row'));
    await graphNode('backend.execute_operators').waitFor();
    await jump('#cc/model.expert_routing');
    await page.locator('[data-ax-id="model.expert_routing"].ax-core').waitFor();
    await page.locator('.corekey').waitFor();
    await jump('#cc/engine.expert_streaming');
    await graphNode('engine.expert_streaming').waitFor();
    assert.equal(await page.locator('[data-ax-id="engine.expert_streaming"].ax-core').count(),1);
    for (const legacy of ['experts.routed_forward','experts.shared_forward']) {
      await jump('#cc/'+legacy);
      await graphNode('model.expert_ffn').waitFor();
    }
    await jump('#cc/engine.expert_residency');
    await graphNode('engine.expert_streaming').waitFor();
    for (const [former,current] of [['serving.tool_conversations','serving.request_gateway'],['factory.methodology_ab','factory.controlled_experiment'],['transfer.prefill_handoff','parallel.model_execution']]){
      await jump('#cc/'+former);
      await graphNode(current).waitFor();
      assert(await page.locator('.cap-row .cap-kind').count()>0);
    }
    await jump('#library');
    await page.locator('#captype').selectOption('method');
    for(const card of await page.locator('#results .listing').all())assert(await card.locator('.cap-method').count()>0);
    await jump('#factory/f_plan?op=workorder');
    await page.getByRole('heading',{name:'Example work orders'}).waitFor();
    assert.deepEqual(errors, [], 'Browser exceptions');
    assert.deepEqual(requests, [], 'Site attempted to load network resources');
    const evidenceCount = targetRoles.reduce((n,r)=>n+r.examples.length,0);
    console.log('PASS: ' + layers.length + ' graph regions, ' + layers.reduce((n,l) => n+l.ops.length,0) + ' operations, ' + roles.size + ' CC handoffs, ' + evidenceCount + ' target CC/source pairs across four engines, ' + data.traces.length + ' walkthroughs. Evidence filters, Back/Forward, quantization, keyboard, offline and mobile checks passed.');
  } finally {
    await browser.close();
  }
}
main().catch(err => { console.error(err); process.exitCode = 1; });
