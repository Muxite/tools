"""One explicitly authorized, nonpromoting whole-engine ABBA comparison.
Uses existing recorder and runtime verification without modifying historical policy.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, os, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path('/home/user2/software-factory-spark-20261113')
REPO=ROOT/'sources/cc-dgx-spark'
HERE=ROOT/'direct-engine-comparison-v1'
sys.path.insert(0,str(REPO))
os.environ['PYTHONPATH']=str(REPO)
from jiuwenswarm.factory import benchmark as bm, benchmark_worker as worker, lab_recorder as rec
from jiuwenswarm.factory import fixed_placement_benchmark as fp, broad_benchmark as broad
from jiuwenswarm.factory.lab_lifecycle import atomic_json, recover_run, inspect_owned, load_intent
from jiuwenswarm.factory.benchmark_data import load_decoder, decode_answer
OLD='sha256:c22e5406f9c81f5865a2318712c1f3247a86e2d1b1633a5ad19d1d3a09ffdfb4'
NEW='sha256:a431b930d26d0abb6eacbd56a970f56216367d901f514a898a2197dc9d1d3b24'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frozen(p,x):
 if p.exists():
  if json.loads(p.read_text())!=x: raise ValueError('Frozen artifact differs: '+str(p))
 else: atomic_json(p,x)


from jiuwenswarm.factory.ccs.strata_budget_workbench.component import apply,verify_startup,summarize_memory
HERE=ROOT/'night-branch-engine-v2'
def prepare():
 new=json.loads((ROOT/'fixed-placement-campaign-v1/fixed-aa-contract.json').read_text())
 bm.validate_contract(new);fp.validate_build(new)
 d=json.loads(Path(new['dataset_path']).read_text());assert sha(new['dataset_path'])==new['dataset_sha256']
 d['quality']=d['quality'][:8]
 profiles={a:apply(dict(profile=new['arms']['A'],budget_bytes=b))['profile'] for a,b in [('A',76000000000),('B',68000000000),('C',76000000000)]}
 args=profiles['C']['args'];args[args.index('--prefill-chunk')+1]='1024'
 pins={k:sha(REPO/'jiuwenswarm/factory'/k) for k in new['execution_sha256']}
 budget_pin=sha(REPO/'jiuwenswarm/factory/ccs/strata_budget_workbench/component.py')
 c=dict(schema_version=1,comparison_id='night-branch-engine-001',order=list('ABCCBA'),profiles=profiles,image=NEW,
  quality_cases=8,speed_cases=4,phase_containers=12,budget_component_sha256=budget_pin,source_pins=pins,orchestrator_sha256=sha(__file__),
  dataset_path=new['dataset_path'],dataset_sha256=new['dataset_sha256'],assets=bm.validate_assets(new),
  hard_stop_utc='2026-11-15T07:20:00Z',promotion_authorized=False,
  scope='Single-variable budget or prefill chunk branches against same qualified image; two fresh cells each; exploratory.')
 frozen(HERE/'contract.json',c)
 return c,new,d

def analyze(c,cells,d):
 tok=load_decoder(ROOT,d['provenance']['tokenizer']['files']);out=[]
 for cell in cells:
  rows=cell['speed']['requests'];assert len(rows)==4
  assert all(r['generated_tokens']==128 and r['prompt_tokens']==512 for r in rows)
  pp=sum(r['prefill_ms'] for r in rows[1:]);dt=sum(r['decode_ms'] for r in rows[1:])
  answers=[]
  for case,row in zip(d['quality'],cell['quality']['requests'],strict=True):
   x=decode_answer(row['ids'],tok,case['allowed_letters'],eos_id=1)
   answers.append(dict(id=case['id'],expected=case['expected_letter'],answer=x['answer'],correct=x['answer']==case['expected_letter']))
  out.append(dict(index=cell['index'],arm=cell['arm'],prefill_ms=pp,decode_ms=dt,combined_tps=384000/(pp+dt),decode_tps=384000/dt,quality=answers,memory={p:cell[p]['memory'] for p in ['quality','speed']},placement={p:cell[p]['budget_identity'] for p in ['quality','speed']}))
 pooled={}
 for a in 'ABC':
  arm=[r for r in out if r['arm']==a];pp=sum(r['prefill_ms'] for r in arm);dt=sum(r['decode_ms'] for r in arm)
  pooled[a]=dict(combined_tps=768000/(pp+dt),decode_tps=768000/dt,prefill_tps=3072000/pp,quality_correct=sum(q['correct'] for r in arm for q in r['quality']),quality_total=16)
 for a in 'BC':
  pooled[a]['combined_ratio_to_A']=pooled[a]['combined_tps']/pooled['A']['combined_tps'];pooled[a]['decode_ratio_to_A']=pooled[a]['decode_tps']/pooled['A']['decode_tps']
 exact=[]
 for i,j in [(0,5),(1,4),(2,3),(0,1),(0,2),(5,4),(5,3)]:
  exact.append(dict(cells=[i+1,j+1],phases={p:dict(total=len(cells[i][p]['requests']),different_cases=[x['case_id'] for x,y in zip(cells[i][p]['requests'],cells[j][p]['requests'],strict=True) if x['ids']!=y['ids'] or x['finish']!=y['finish']]) for p in ['quality','speed']}))
 return dict(cells=out,pooled=pooled,exact_tokens=exact,promotion_authorized=False,limitations=['Only eight ARC questions, not benchmark-wide quality certification.','Two cells per arm, no reliable confidence interval.','Native timings exclude startup. First speed request discarded.','Cgroup peak includes accounting/pagecache; host available is global. Neither is exact GPU memory.','Chunk1024 sees a 512-token prompt: tests one versus two prefill chunks, not long-context scaling.'])

def run():
 c,new,d=prepare();output=HERE/'run-001'
 if output.exists():raise ValueError('Run already reserved')
 output.mkdir();atomic_json(output/'contract.json',c)
 started=time.monotonic();cells=[];result=dict(status='partial',cells=cells)
 from datetime import datetime
 hardstop=datetime.fromisoformat(c['hard_stop_utc'].replace('Z','+00:00')).timestamp()
 def stop(n,f):raise SystemExit(128+n)
 for n in [signal.SIGTERM,signal.SIGINT]:signal.signal(n,stop)
 try:
  for index,arm in enumerate(c['order'],1):
   view=copy.deepcopy(new);view['adapter']='strata-benchmark-v2';view['arms']={'A':copy.deepcopy(c['profiles'][arm])}
   cell=dict(index=index,arm=arm);cells.append(cell)
   for phase in ['quality','speed']:
    assert sha(__file__)==c['orchestrator_sha256'];worker.check_source_pins(dict(execution_sha256=c['source_pins']))
    assert sha(REPO/'jiuwenswarm/factory/ccs/strata_budget_workbench/component.py')==c['budget_component_sha256']
    assert sha(c['dataset_path'])==c['dataset_sha256'];assert bm.validate_assets(view)==c['assets']
    cases=d[phase];phasepath=output/f'cell-{index:03d}-{arm}'/phase;phasepath.parent.mkdir(exist_ok=True)
    remaining=hardstop-time.time()
    if remaining<60:raise TimeoutError('Campaign deadline')
    admission=worker.admission(NEW)
    atomic_json(output/'progress.json',dict(index=index,arm=arm,phase=phase,status='running',utc=time.time()))
    print(json.dumps(dict(event='phase_start',index=index,arm=arm,phase=phase,utc=time.time())),flush=True)
    report=rec.run_container(bm.phase_args(view,'A',phase),output=phasepath,image=NEW,mounts=[(v,v) for v in view['workload'].values()],gpu=True,environment=view['arms']['A']['environment'],protocol=bm.protocol(cases,'A',view),timeout_s=min(300,remaining),interval_ms=1000,guard_gib=8,memory_bytes=104*2**30,cpus=8,lease_root=ROOT/'lab-lease')
    if not worker._successful(report):raise RuntimeError('Recorder failed: '+str(report.get('reason')))
    parsed=bm.verify_phase(view,'A',phase,phasepath,cases)
    assert all(r['offered_drafts']==r['accepted_drafts']==r['prefix_reused']==0 for r in parsed['requests'])
    identity=verify_startup(dict(stderr=(phasepath/'stderr.log').read_text(),budget_bytes=int(c['profiles'][arm]['environment']['DS4_EXPERT_BUDGET_BYTES'])))
    samples=[json.loads(v) for v in (phasepath/'samples.jsonl').read_text().splitlines()]
    parsed.update(budget_identity=identity,memory=summarize_memory(dict(samples=samples)),admission=admission);cell[phase]=parsed
    atomic_json(phasepath.parent/(phase+'-result.json'),parsed)
    print(json.dumps(dict(event='phase_complete',index=index,arm=arm,phase=phase,elapsed_s=report.get('elapsed_s'),requests=len(parsed['requests']))),flush=True)
   atomic_json(output/f'cell-{index:03d}-{arm}'/'cell.json',cell)
  atomic_json(output/'analysis.json',analyze(c,cells,d));result.update(status='complete',elapsed_s=time.monotonic()-started)
 except BaseException as exc:
  result['error']=dict(type=type(exc).__name__,message=str(exc));raise
 finally:
  cleanup=[]
  for p in output.glob('cell-*/*/intent.json'):
   if inspect_owned(load_intent(p.parent)) is not None:recover_run(p.parent,reason='night_branch_exit')
   cleanup.append(dict(phase=str(p.parent.relative_to(output)),owned_container_absent=inspect_owned(load_intent(p.parent)) is None))
  atomic_json(output/'cleanup.json',cleanup);atomic_json(output/'campaign.json',result)
  atomic_json(output/'manifest.json',dict(state=result['status'],files={str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*')) if p.is_file() and p!=output/'manifest.json' and not p.name.endswith('.lock')}))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');args=parser.parse_args()
 if args.run:run()
 else:
  c,*_=prepare();print(json.dumps(dict(preflight='passed',contract=str(HERE/'contract.json'),gpu_submitted=False)))
