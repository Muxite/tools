"""Independent offline browser checks for the endpoint and retained atlas routes."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

HERE = Path(__file__).resolve().parent
EDGE = Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')

def check(ok, message):
    if not ok:
        raise AssertionError(message)

def go(page, route):
    page.evaluate("h => location.hash = h", '#' + route)
    page.wait_for_timeout(80)

def retained(page):
    # Routes and source identities survive the endpoint redesign.
    for route, marker in [('component/engine.expert_weight_cache', 'Expert weight cache'),
                          ('action/model/route', '5/7'),
                          ('assembly/decoder/layer/routed', 'Routed'),
                          ('trace/cold/0', 'expert'),
                          ('quantization', 'Quantization')]:
        go(page, route)
        expect(page.locator('main')).to_contain_text(marker, ignore_case=True)
    go(page, 'component/engine.expert_weight_cache')
    cc = page.locator('main a[href^="#cc/"]').first
    check(cc.count() == 1, 'Cache component lost its builder link')
    cc.focus()
    page.keyboard.press('Enter')
    expect(page).to_have_url(__import__('re').compile(r'#cc/'))
    expect(page.locator('main')).to_contain_text('Expert weight cache', ignore_case=True)

PINNED = Path(__import__('os').environ.get('LLAMA_CPP_PIN_DIR', 'llama.cpp'))
STRATA = Path.home() / 'huawei' / 'Strata'

def endpoint(page):
    import subprocess
    model = page.evaluate("() => endpointData")
    parents = model['parents']
    check(len(parents) == 8 and len({p['id'] for p in parents}) == 8, 'Expected eight unique endpoint groups')
    children = [c for parent in parents for c in parent['children']]
    ids = [identity for child in children for identity in child['legacyIds']]
    check(len(ids) == 36 and len(set(ids)) == 36, 'Expected 36 uniquely assigned engine component IDs')
    inventory = page.evaluate("() => JSON.parse(document.querySelector('#records').textContent).components.filter(c => c.scope !== 'Factory' && c.scope !== 'Host').map(c => c.id)")
    check(set(ids) == set(inventory), 'Endpoint IDs do not match engine and extension inventory')
    placement = {identity: p['id'] for p in parents for c in p['children'] for identity in c['legacyIds']}
    for identity, owner in {'engine.expert_weight_cache':'weight-residency', 'placement.weight_placement_planner':'weight-residency',
                            'routing.expert_demand_predictor':'weight-residency', 'memory.sequence_kv_cache':'sequence-state',
                            'memory.prefix_state_cache':'sequence-state', 'sequence.recurrent_state_operator':'sequence-state',
                            'weights.weight_pack_compiler':'preparation', 'weights.weight_block_decoder':'backend',
                            'model.expert_router':'model', 'backend.quantized_matmul_kernel':'backend',
                            'backend.cpu_weight_repack':'backend', 'weights.engram_row_cache':'weight-residency',
                            'engine.host_expert_store':'weight-residency'}.items():
        check(placement[identity] == owner, 'Incorrect component placement: ' + identity)
    revision = subprocess.check_output(['git', '-C', str(PINNED), 'rev-parse', 'HEAD'], text=True).strip()
    check(revision == model['revision'], 'Source checkout differs from the recorded pinned revision')
    refs = [ref for item in children + model['boundaries'] + model['scenarios']
            for ref in [item.get('source'), *item.get('additionalSources', [])] if ref]
    for ref in refs:
        path = (PINNED / ref['path']).resolve()
        check(path.is_relative_to(PINNED.resolve()) and path.is_file(), 'Invalid source path: ' + str(ref))
        contents = path.read_text(encoding='utf-8', errors='replace')
        check(1 <= ref['line'] <= len(contents.splitlines()), 'Invalid source line: ' + str(ref))
        lines = contents.splitlines()
        vicinity = '\n'.join(lines[max(0, ref['line'] - 21):ref['line'] + 20])
        check(ref['symbol'] in vicinity, 'Source symbol not near cited line: ' + str(ref))
    # Strata anchors: each path exists at the pinned commit and its symbol is near the cited line.
    strata_refs = [ref for item in children for ref in item.get('strataSources', [])]
    check(len(strata_refs) >= 20, 'Strata evidence missing from endpoint records')
    for ref in strata_refs:
        text = subprocess.check_output(['git', '-C', str(STRATA), 'show', model['strataRevision'] + ':' + ref['path']],
                                       text=True, encoding='utf-8', errors='replace')
        lines = text.splitlines()
        check(1 <= ref['line'] <= len(lines), 'Invalid Strata line: ' + str(ref))
        vicinity = '\n'.join(lines[max(0, ref['line'] - 21):ref['line'] + 20])
        check(ref['symbol'] in vicinity, 'Strata symbol not near cited line: ' + str(ref))
    # Tool and analysis CC sources use the same pins.
    records = page.evaluate("() => JSON.parse(document.querySelector('#records').textContent)")
    for cc in [c for c in records['ccs'] if c.get('ccKind') in ('tool', 'analysis')]:
        check(cc['sources'], 'Operating CC lacks sources: ' + cc['id'])
        for ref in cc['sources']:
            if ref['repo'] == 'evidence':
                check((HTML_DIR / ref['path']).is_file(), 'Missing evidence source: ' + ref['path'])
                continue
            if ref['repo'] == 'Strata':
                text = subprocess.check_output(['git', '-C', str(STRATA), 'show', model['strataRevision'] + ':' + ref['path']], text=True, encoding='utf-8', errors='replace')
            else:
                text = (PINNED / ref['path']).read_text(encoding='utf-8', errors='replace')
            lines = text.splitlines()
            check(1 <= ref['line'] <= len(lines) and ref['symbol'] in '\n'.join(lines[max(0, ref['line'] - 21):ref['line'] + 20]),
                  'Operating CC source symbol not near line: ' + cc['id'] + ' ' + str(ref))
    for child in children:
        for local in child.get('localSources', []):
            check((HTML_DIR / local['path']).is_file(), 'Missing local evidence copy: ' + local['path'])
    for identity in ['quantized_matmul', 'cpu_expert_lane', 'engram_row_cache', 'host_expert_store']:
        child = next(c for c in children if c['id'] == identity)
        check(child.get('source') and child.get('strataSources') and child.get('llamaStatus'), 'New subcomponent lacks sources or status: ' + identity)
    go(page, 'endpoint/parent/backend')
    for title in ['Quantized matmul kernels', 'CPU expert lane kernels and weight repack']:
        expect(page.locator('main')).to_contain_text(title)
    expect(page.locator('main')).to_contain_text('No IQ2_XXS repack path exists at this pin')
    go(page, 'endpoint/parent/weight-residency')
    for title in ['Engram row cache', 'Expert store and admission policy (host expert tier)']:
        expect(page.locator('main')).to_contain_text(title)
    for marker in ['--ssd-policy', 'DS4_ENGRAM_CACHE_MB', 'lazy_read']:
        expect(page.locator('main')).to_contain_text(marker)
    check(page.locator('main [data-measured]').count() >= 3, 'Measured evidence missing from weight residency')
    go(page, 'endpoint/parent/runtime')
    expect(page.locator('main')).to_contain_text('--dspark')
    go(page, 'endpoint/parent/sequence-state')
    expect(page.locator('main')).to_contain_text('STRATA_DS4_REUSE')
    go(page, 'endpoint/parent/preparation')
    expect(page.locator('main')).to_contain_text('hotness-aware mixed precision')
    check(page.locator('main a[href="evidence/pack-conversion/convert_ds41_upstream.py"]').count() == 1, 'Pack converter precedent missing')
    go(page, 'endpoint/measured')
    check(page.locator('main article[data-measured]').count() == 5, 'Measured view lists five components')
    go(page, 'endpoint/campaign')
    check(page.locator('main [data-campaign-builders] tr[data-campaign-cc]').count() == 5, 'Campaign view lists five builder CCs')
    check(page.locator('.ep-nav a[href="#endpoint/campaign"][aria-current]').count() == 1, 'Campaign view missing from the Engine nav')
    for href in page.locator('main a[href^="evidence/"]').evaluate_all('as => as.map(a => a.getAttribute("href"))'):
        check((HTML_DIR / href).is_file(), 'Broken campaign evidence link: ' + href)
    for href in page.locator('main a[href^="evidence/"]').evaluate_all('as => as.map(a => a.getAttribute("href"))'):
        check((HTML_DIR / href).is_file(), 'Broken evidence link: ' + href)
    page.goto(page.url.split('#')[0])
    check(page.locator('.ep-map-node').count() == 8, 'Default route must show eight endpoint groups')
    go(page, 'engine')
    check(page.locator('.ep-map-node').count() == 8, 'Overview must show eight groups')
    check(page.locator('.ep-map-canvas svg path').count() >= 8, 'Diagram connections are missing')
    check(page.locator('.ep-budget-wire').count() == 1, 'Shared-budget constraint missing from diagram')
    expect(page.locator('.ep-budget-relation')).to_contain_text('not a data handoff')
    for identity in ['sequence-state', 'weight-residency']:
        check(page.locator(f'a.ep-map-node[href="#endpoint/parent/{identity}"]').count() == 1,
              'Split memory group missing from map: ' + identity)
    first = page.locator('a.ep-parent[href^="#endpoint/parent/"]').first
    check(first.count() == 1, 'Parent link missing')
    first.focus()
    page.keyboard.press('Enter')
    expect(page).to_have_url(__import__('re').compile(r'#endpoint/parent/'))
    expect(page.locator('.ep-detail')).to_be_visible()
    go(page, 'endpoint/parent/memory')
    for identity in ['sequence-state', 'weight-residency']:
        check(page.locator(f'main a[href="#endpoint/parent/{identity}"]').count() == 1,
              'Former memory route must link to ' + identity)
    go(page, 'endpoint/ranks')
    check(page.locator('.ep-rank').count() == 10, 'Expected ten ranked entries')
    check(page.locator('.ep-star.is-starred').count() == 5, 'Expected five starred entries')
    starred = page.locator('.ep-rank:has(.ep-star.is-starred) h2').all_text_contents()
    check(starred == ['Expert weight cache', 'Expert router', 'Weight placement planner',
                      'Quantization and weight-pack preparation', 'Expert demand predictor'], 'Starred priorities changed')
    go(page, 'endpoint/coverage')
    expect(page.locator('main')).to_contain_text('What earns a component boundary?')
    for card, family in zip(page.locator('.ep-stack > .ep-detail').all(), model['boundaries']):
        expect(card).to_contain_text(family['title'])
        for key in ['status', 'detail', 'caller', 'acceptance', 'integrationStatus', 'qualificationStatus']:
            if family.get(key):
                expect(card).to_contain_text(family[key])
        for path in family.get('reviewedPaths', []):
            expect(card).to_contain_text(path)
        for cc in family.get('implementingCCs', []) + family.get('collaboratingCCs', []):
            check(card.locator(f'a[href="#cc/{cc}"]').count() > 0, 'Family CC omitted: ' + cc)
        if family.get('source'):
            expect(card).to_contain_text(family['source']['path'])
    go(page, 'endpoint/changes')
    check(page.locator('.ep-detail').count() == 7, 'Expected seven change scenarios')
    for card, scenario in zip(page.locator('.ep-detail').all(), model['scenarios']):
        check(card.locator('a[href^="#cc/"]').count() > 0, 'Scenario lacks implementing CC link')
        check(card.locator('.ep-source').count() > 0, 'Scenario lacks source attribution')
        expect(card).to_contain_text(scenario['source']['path'])
        expect(card).to_contain_text(scenario['source']['symbol'])
    go(page, 'endpoint/walks')
    expect(page.locator('.ep-walks')).to_be_visible()
    check(page.locator('.ep-walks > .ep-detail').count() == 2, 'Expected two walkthroughs')
    check(page.locator('.ep-walks .ep-steps li').count() >= 4, 'Walkthrough handoffs missing')
    go(page, 'endpoint/demo')
    expect(page.locator('.ep-metrics')).to_be_visible()
    budget = page.locator('.ep-budget')
    expect(budget).to_contain_text('96 GiB')
    budget_cards = budget.locator('.budget-examples article')
    check(budget_cards.count() == 2, 'Expected two budget examples')
    expect(budget_cards.nth(0)).to_contain_text('8 GiB sequence reservation')
    expect(budget_cards.nth(0)).to_contain_text('24 GiB available for expert slots')
    expect(budget_cards.nth(1)).to_contain_text('16 GiB sequence reservation')
    expect(budget_cards.nth(1)).to_contain_text('16 GiB available for expert slots')
    expect(page.locator('main')).to_contain_text('Set one memory cap for both owners')
    expect(page.locator('main')).to_contain_text('Cancel one of two active requests')
    expect(page.locator('main')).to_contain_text('no endpoint speed measurement', ignore_case=True)
    check(page.locator('main a[href^="#cc/"]').count() > 0, 'Demo lacks CC attribution')
    check(page.locator('main a[href^="#evidence/"]').count() > 0, 'Demo lacks evidence attribution')
    cc_href = page.locator('main a[href^="#cc/"]').first.get_attribute('href')
    evidence_href = page.locator('main a[href^="#evidence/"]').first.get_attribute('href')
    page.locator('main a[href^="#cc/"]').first.click()
    expect(page).to_have_url(__import__('re').compile(__import__('re').escape(cc_href) + '$'))
    go(page, 'endpoint/demo')
    page.locator('main a[href^="#evidence/"]').first.click()
    expect(page).to_have_url(__import__('re').compile(__import__('re').escape(evidence_href) + '$'))
    for width, height in [(1440, 900), (390, 844)]:
        page.set_viewport_size({'width': width, 'height': height})
        for route in ['engine', 'assemblies', 'endpoint/parent/service', 'endpoint/parent/model', 'endpoint/parent/memory', 'endpoint/parent/sequence-state', 'endpoint/parent/weight-residency', 'endpoint/parent/backend', 'endpoint/ranks', 'endpoint/changes', 'endpoint/walks', 'endpoint/demo', 'endpoint/measured', 'endpoint/campaign', 'endpoint/coverage', 'library']:
            go(page, route)
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),
                  f'{width}px horizontal overflow on {route}')
            if route == 'engine':
                rects = page.locator('.ep-map-node').evaluate_all('els => els.map(e => {const r=e.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom]})')
                for index, (left, top, right, bottom) in enumerate(rects):
                    for other in rects[:index]:
                        check(min(right, other[2]) <= max(left, other[0]) + 1 or
                              min(bottom, other[3]) <= max(top, other[1]) + 1,
                              f'{width}px map cards overlap')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('html', type=Path)
    parser.add_argument('--legacy', type=Path, help='Old component HTML to check retained routes')
    args = parser.parse_args()
    global HTML_DIR
    HTML_DIR = args.html.resolve().parent
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EDGE) if EDGE.exists() else None, headless=True)
        for path, is_legacy in [(args.html, False)] + ([(args.legacy, True)] if args.legacy else []):
            check(path.is_file(), 'HTML not found: ' + str(path))
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, offline=True)
            page = context.new_page()
            errors, requests = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda req: requests.append(req.url) if req.url.startswith(('http:', 'https:')) else None)
            page.goto(path.resolve().as_uri())
            retained(page)
            if not is_legacy:
                endpoint(page)
            check(not errors, 'Browser errors: ' + repr(errors))
            check(not requests, 'Network requests while offline: ' + repr(requests))
            context.close()
        browser.close()
    print('PASS: endpoint and retained routes, offline, keyboard and narrow viewport')

if __name__ == '__main__':
    main()
