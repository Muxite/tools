import hashlib,json,os,re,subprocess,sys
from pathlib import Path
R=Path('/home/user2/software-factory-spark-20261113');Q=Path('/home/user2/rsi-expert-streaming-spark-002/paired-retry-001/jobq')
sys.path.insert(0,str(R/'sources/factory-fe88a206'))
from jiuwenswarm.factory.store import Store,NotFound
from jiuwenswarm.factory.taskgraph import plan_get
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
jobs=[json.loads(p.read_text()) for p in Q.glob('job-*.json')]
owned=[j for j in jobs if j['name'].startswith('ssh-factory-20261113:')]
assert all(j['state'] not in ('queued','running') for j in owned)
for j in owned:
    if j.get('pgid'):
        try:os.killpg(j['pgid'],0)
        except ProcessLookupError:pass
        else:raise AssertionError('Owned process group remains')
containers=subprocess.check_output(['docker','ps','-aq','--filter','label=factory.owner=software-factory-spark-20261113'],text=True).strip()
assert not containers,'Owned container remains'
for rid in ('container-cancel-001','container-timeout-001'):
    assert json.loads((R/'results'/rid/'cleanup.json').read_text())['remove_rc']==0
projection=[{k:j.get(k) for k in ('id','name','state','class','start','end','rc','pgid','concurrent_jobs')} for j in owned]
(R/'results/queue-review.json').write_text(json.dumps({'owned_jobs':projection,'owned_process_groups_absent':True,'owned_containers_absent':True},indent=2))
base=json.loads((R/'results/build-warm-002/build-record.json').read_text());edit=json.loads((R/'results/build-edit-003/build-record.json').read_text())
assert base['status']==edit['status']=='success'
assert (R/'results/tiny-base-001/stdout.txt').read_bytes()==(R/'results/tiny-edit-001/stdout.txt').read_bytes()
assert 'ssh-build-probe: incremental source executed' in (R/'results/build-edit-003/smoke.log').read_text()
private=[json.loads((R/'results'/rid/'inference-record.json').read_text()) for rid in ('memory-private-8g-003','memory-private-16g-004','memory-private-8g-005')]
assert all(x['status']=='success' for x in private)
assert len({x['stdout_sha256'] for x in private})==1
def reads(s):return sum(int(v) for v in re.findall(r'\brbytes=(\d+)',s.get('io.stat','')))
for a in (private[0],private[2]):
    generated=[s for s in a['samples'] if s['stdout_bytes']>0]
    assert generated and reads(a['samples'][-1])-reads(generated[0])>0
    assert all(int(s['memory.max'])==8*1024**3 for s in a['samples'])
    assert all(int(s.get('memory.swap.current','0'))==0 for s in a['samples'])
review={'status':'bounded-qualification-passed','source':'fe88a20682550603a5d32193403c74cc6e68e8b7','queue_cleanup':True,'tiny_output_agreement':True,'incremental_source_marker':True,'private_budget_output_agreement':True,'ssd_reads_during_output_in_two_8g_runs':True,'limits':['CPU placement for GPT-OSS budget test','tiny GPU smoke only; full GPU allocation accounting not qualified','not a multi-engine benchmark','no inference speed improvement claim','no model larger than physical RAM tested in this stage','no independent remote coding agent','material CCs are candidates, not centrally promoted','cold build launch failed and was corrected; subsequent rebuilds passed']}
(R/'results/qualification-review.json').write_text(json.dumps(review,indent=2))
TASK='spark-ssh-research-20261113'
with Store(R/'factory-store') as store:
    refs=[]
    paths=[R/'results/qualification-review.json',R/'results/queue-review.json']+list((R/'results').glob('*/build-record.json'))+list((R/'results').glob('*/inference-record.json'))
    for p in paths:
        key='evidence-'+sha(p)[:24]
        try:store.read(TASK,key)
        except NotFound:
            art=store.put_artifact(TASK,key+'-file',p,'application/json',None)
            store.append_observation(TASK,{'obs_id':key,'kind':'qualification_record','values':{'relative_path':str(p.relative_to(R))},'source_artifacts':[art['artifact_id']],'limitations':'Scope and exclusions are in the linked raw record.'})
        refs.append(key)
    graph=plan_get(store,TASK)
    if any(n['state']!='done' for n in graph['nodes']):
        updates=[{'node_id':n['node_id'],'state':'done','evidence_ids':refs,'reason':'Accepted only within bounded infrastructure / build iteration / CPU memory-budget method scope; full GPU and physical-RAM scaling remain explicit follow-ups.'} for n in graph['nodes'] if n['state']!='done']
        task=store.get_task(TASK)
        store.advance_decision(TASK,task['current_decision_rev'],{'hypothesis':'Persistent compatible build objects shorten small-edit turnaround. Explicit mmap/no-repack plus owned-file cache control enables a meaningful constrained-memory CPU experiment.','evidence_ids':refs,'action':{'kind':'accept_bounded_methods','promote_central':False},'uncertainty':'Cross-engine comparisons, broader quality, GPU accounting and physical-memory scaling remain unqualified.','reason_for_change':'Retained failed launch, 8GiB repack OOM and shared-cache confound led to measured corrections; no new presentation production.','expected_graph_rev':graph['rev'],'plan_patch':{'update':updates}})
    (R/'results/factory-graph.json').write_text(json.dumps(plan_get(store,TASK),indent=2))
exports={}
for p in (R/'results').rglob('*'):
    if p.is_file() and p.suffix in ('.json','.txt','.log') and 'image' not in p.relative_to(R).parts and p.stat().st_size<16*1024**2:
        exports[str(p.relative_to(R))]={'bytes':p.stat().st_size,'sha256':sha(p)}
(R/'results/evidence-export.json').write_text(json.dumps(exports,indent=2))
print(json.dumps({'review':review,'export_files':len(exports)}))
