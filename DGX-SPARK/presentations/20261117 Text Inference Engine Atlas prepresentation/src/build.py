"""Generate the standalone atlas with Python's standard library."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
def read(name):
    return json.loads((HERE/name).read_text('utf-8-sig'))

def assemble():
    evidence = read('evidence.json')
    taxonomy = read('text_factory.json')
    architecture = read('architecture.json')
    engine = read('text_engine.json')
    merged, removed = taxonomy['merge'], set(taxonomy['remove'])
    def current(key):
        visited = set()
        while key in merged:
            if key in visited:
                raise ValueError(f"Cyclic CC alias at {key}")
            visited.add(key)
            key = merged[key]
        return key
    old = {r['id']:r for r in evidence['roles']}
    old.update(taxonomy.get('definitions', {}))
    aliases = {k:current(v) for k,v in evidence['aliases'].items()}
    aliases.update({k:current(k) for k in old})
    aliases.update(taxonomy.get('aliasOverrides', {}))
    roles = {k:r for k,r in old.items() if k not in merged and k not in removed}
    for k,r in roles.items():
        r['why'] = taxonomy['rationale'][k]
        r['when'] = taxonomy['conditional'].get(k,'Required when this operation is present in the target engine or workflow.')
        r.update(taxonomy.get('responsibilities', {}).get(k, {}))
        r['variantJobs'] = []
    for former in merged:
        survivor=current(former)
        roles[survivor]['variantJobs'].append({k:old[former][k] for k in ['id','reason','check','capabilities']})
        for field in ['ex','reuse','capabilities']:
            roles[survivor][field]=list(dict.fromkeys(roles[survivor][field]+old[former][field]))
    catalog=read('capability_catalog.json')
    for key,role in roles.items():
        role['title']=catalog[key]['title']
        role['contents']=list(catalog[key]['capabilities'])
    for key,entry in catalog.items():
        if key in merged and current(key) not in {'factory.controlled_experiment','model.expert_ffn','serving.request_gateway'}:
            roles[current(key)]['contents'].extend(entry['capabilities'])
    for role in roles.values():
        for cap in role['contents']:
            assert cap['kind'] in {'component','tool','skill','method'} and cap['name'] and cap['detail']
    factory = taxonomy['layers']
    sites = {k:[] for k in roles}
    for layer in engine+factory:
        ids = {o['id'] for o in layer['ops']}
        assert len(ids)==len(layer['ops']),layer['id']
        for a,b,*rest in layer['edges']:
            assert a in ids and b in ids and rest[0],(layer['id'],a,b)
        for op in layer['ops']:
            operation=layer['id']+'/'+op['id']
            op['target']=operation not in taxonomy['nonTargetOperations']
            op['cc']=taxonomy.get('operationOwners',{}).get(operation,op['cc'])
            op['cc']=list(dict.fromkeys(current(k) for k in op['cc']))
            for k in op['cc']:
                assert k in roles,(op,k)
                sites[k].append([layer['id'],op['id']])
    for k,places in sites.items():
        assert places,'Unreachable CC '+k
        roles[k]['sites']=places
    sources = []
    for row in evidence['sources']:
        row['assigned']=current(taxonomy.get('sourceOwnerByPrevious',{}).get(row['previous'],row['assigned']))
        row['target']=row['assigned'] not in taxonomy['nonTargetRoles'] and row['previous']!='experts.shared_forward'
        if row['assigned'] in roles:sources.append(row)
    for asset in evidence['assets']:
        asset['assigned']=current(asset['assigned'])
    paths={l['id']:{o['id'] for o in l['ops']} for l in engine+factory}
    cross = read('text_cross.json')
    for a,b,label,kind in cross:
        for endpoint in [a,b]:
            lid,oid=endpoint.split('/')
            assert oid in paths[lid] and label and kind
    for a,b,*_ in architecture['edges']+taxonomy['edges']:
        assert a in paths and b in paths
    for tr in architecture['traces']:
        for item in tr['steps']:
            lay,k,note=item[:3]
            k=current(k)
            if lay not in paths:lay=sites[k][0][0]
            where=next(((l,o) for l,o in sites[k] if l==lay),sites[k][0])
            if len(item)>3:
                assert item[3] in paths[lay]
                where=(lay,item[3])
            assert where in [tuple(site) for site in sites[k]],(tr['id'],where,k)
            assert '/'.join(where) not in taxonomy['nonTargetOperations'],(tr['id'],where)
            item[:]=[*where,k,note]
    baseline=read('essential.json')
    assert set(baseline['roles']) <= roles.keys()
    for lid,ops in baseline['operations'].items():
        assert set(ops) <= paths[lid]
    for l in engine+factory:
        for op in l['ops']:
            op['essential']=op['id'] in baseline['operations'][l['id']]
    for k,r in roles.items():
        r['target']=k not in taxonomy['nonTargetRoles']
        r['essential']=k in baseline['roles']
        if r['target'] and r.get('kind')!='factory':
            assert any(s['assigned']==k and s.get('url','').startswith('https://github.com/') and '/blob/' in s['url'] for s in sources), 'No pinned source for '+k
        if r['essential']:
            assert r['target'],k
    review=read('ownership_review.json')
    handoffs=read('handoffs.json')
    muse=read('muse_evidence.json')
    for key,r in roles.items():
        r['review']=review[key]
        assert review[key]['site'].split('/') in r['sites'], key
        r['handoff']=handoffs[key]
        r['examples']=[]
    roles['memory.sequence_kv']['tierHandoff']=handoffs['memory.kv_tiering']
    def example(key, row):
        bucket=roles[current(key)]['examples']
        if not any(x['url']==row['url'] for x in bucket):
            bucket.append(row)
    for name in ['evidence_runtime.json','evidence_math.json','evidence_peers.json','evidence_ds4_deep.json','evidence_strata_deep.json','evidence_variants.json']:
        for key,rows in read(name).items():
            for row in rows:
                example(key,row)
    for key,rows in muse['byRole'].items():
        for row in rows:
            for repo in evidence['repositories']:
                if row['url'].startswith(repo['base']+'/blob/'+repo['pin']+'/'):
                    example(key,dict(row,engine=repo['engine']))
    for row in sources:
        example(row['assigned'], dict(engine=row['engine'],title=row['symbol'],url=row['url'],detail=row['detail']))
    assert len([r for r in roles.values() if r.get('kind')=='factory'])==6
    return dict(muse=read('muse_evidence.json'),baseline=baseline['description'],cross=cross,engine=engine,factory=factory,edges=architecture['edges'],factoryEdges=taxonomy['edges'],roles=list(roles.values()),aliases=aliases,excluded=sorted(removed),sources=sources,assets=evidence['assets'],repositories=evidence['repositories'],traces=architecture['traces'],transfers=evidence['transfers'],mergers=merged)

if __name__=='__main__':
    data=assemble()
    page=(HERE/'site.html').read_text('utf-8')
    for token,names in [('/*GRAPH_JS*/',['text_graph.js']),('/*SITE_JS*/',['site.js','experiments.js','construction_options.js','spark_trials.js','variations.js','construction.js','integration.js','navigation.js']),('/*SITE_CSS*/',['site.css','text_graph.css'])]:
        page=page.replace(token,'\n'.join((HERE/n).read_text('utf-8') for n in names))
    page=page.replace('__ATLAS__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    out=HERE.parent/'20261117 Text Inference Engine Atlas prepresentation.html'
    out.write_bytes(page.encode('utf-8'))
    print(f"{len(data['roles'])} CCs, {sum(len(l['ops']) for l in data['engine'])} engine operations, {len(data['sources'])} source bindings.")
