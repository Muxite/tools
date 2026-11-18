const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

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
    const outputs = new Set();
    for (const choice of ['5 routed','6 routed','5 routed + 1 shared']) {
      await router.selectOption({label:choice});
      outputs.add(await page.locator('#routing-out').innerText());
    }
    assert.equal(outputs.size, 3, 'Changing the routing contract must change its visible explanation');
    for (const repository of data.repositories) {
      await jump('#engine/model?op=' + route.id + '&overlay=' + encodeURIComponent(repository.engine));
      await graphNode('model.expert_routing').waitFor();
      assert((await page.locator('main').innerText()).includes(repository.engine), 'Missing source overlay for ' + repository.engine);
    }
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
    await page.setViewportSize({ width:390, height:844 });
    for (const h of ['#engine','#engine/model?op=' + route.id,'#factory','#library','#sources']) {
      await jump(h);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'Horizontal page overflow at ' + h);
    }
    await jump('#engine/model?op=route');
    await graphNode('backend/row').focus();
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => location.hash.includes('engine/backend') && location.hash.includes('op=row'));
    assert(await graphNode('backend.execute_operators').count(), 'Kernel worksite has no backend CC');
    assert.deepEqual(errors, [], 'Browser exceptions');
    assert.deepEqual(requests, [], 'Site attempted to load network resources');
    console.log('PASS: ' + layers.length + ' graph regions, ' + layers.reduce((n,l) => n+l.ops.length,0) + ' operations, ' + roles.size + ' reachable CCs, ' + data.sources.length + ' source examples and ' + data.traces.length + ' walkthroughs. Keyboard, offline and mobile checks passed.');
  } finally {
    await browser.close();
  }
}
main().catch(err => { console.error(err); process.exitCode = 1; });
