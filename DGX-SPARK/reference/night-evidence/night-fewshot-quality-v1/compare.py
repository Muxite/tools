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
HERE=ROOT/'night-fewshot-quality-v1'
def build_quality(original):
 from jiuwenswarm.factory import benchmark_data as bd
 def no_network(*args,**kwargs):raise ValueError('Expected already pinned public dataset cache; no new download permitted')
 bd._download=no_network
 cache=ROOT/'benchmark-data/arc-v1/public-source'
 train,train_source=bd.fetch_split(cache,'train');test,test_source=bd.fetch_split(cache,'test')
 expected={v['split']:v['canonical_rows_sha256'] for v in original['provenance']['splits']}
 assert train_source['canonical_rows_sha256']==expected['train'] and test_source['canonical_rows_sha256']==expected['test']
 demos=bd.select_rows(train,8);targets=bd.select_rows(test,16)
 assert not {r['id'] for r in demos}&{r['id'] for r in targets}
 tokenizer=bd.load_tokenizer(ROOT)
 def question(row):
  allowed,answer,choices=bd.normalize_question(row)
  return row['question']+'\n'+'\n'.join(k+'. '+v for k,v in choices)
 prefix='Answer the multiple-choice science question. Reply only with the best answer letter; no explanation. The solved training examples illustrate the format.\n\n'
 prefix+='\n\n'.join('Example '+str(i)+':\n'+question(row)+'\nAnswer: '+bd.normalize_question(row)[1] for i,row in enumerate(demos,1))
 cases=[]
 for row in targets:
  allowed,answer,_=bd.normalize_question(row)
  prompt=bd.CHAT_PREFIX+prefix+'\n\nNow answer this new question:\n'+question(row)+'\nAnswer: '+bd.CHAT_SUFFIX
  ids=tokenizer.encode(prompt,parse_special=True)
  assert tokenizer.decode(ids)==prompt and 256<len(ids)<=2048
  cases.append(dict(id=row['id'],kind='quality',split='test',prompt=prompt,ids=ids,max_new_tokens=8,allowed_letters=allowed,expected_letter=answer,original_answer_key=row['answerKey']))
 d=dict(schema_version=1,quality=cases,provenance=original['provenance'],fewshot=dict(train_ids=[r['id'] for r in demos],test_ids=[r['id'] for r in targets],shots=8,selection='existing SHA256(seed42:id) order',test_answers_in_prompts=False,official_arc_score=False,prompt_tokens=[len(r['ids']) for r in cases],purpose='Expose chunk treatment during correctness checks; earlier zero-shot prompts fit in one256-token chunk'))
 from jiuwenswarm.factory.strata_prefill import coverage
 d['fewshot']['chunk_coverage']=coverage([len(r['ids']) for r in cases],256,1024)
 assert d['fewshot']['chunk_coverage']['predicted_changed_chunk_count_cases']==16
 frozen(HERE/'dataset.json',d);return d

def prepare():
 new=json.loads((ROOT/'fixed-placement-campaign-v1/fixed-aa-contract.json').read_text())
 bm.validate_contract(new);fp.validate_build(new)
 d=json.loads(Path(new['dataset_path']).read_text());assert sha(new['dataset_path'])==new['dataset_sha256']
 d=build_quality(d)
 profiles={a:apply(dict(profile=new['arms']['A'],budget_bytes=b))['profile'] for a,b in [('A',76000000000),('B',68000000000),('C',76000000000)]}
 from jiuwenswarm.factory.strata_prefill import apply as apply_chunk
 profiles['C']=apply_chunk(profiles['C'],1024)['profile']
 pins={k:sha(REPO/'jiuwenswarm/factory'/k) for k in new['execution_sha256']}
 pins.update({k:sha(REPO/'jiuwenswarm/factory'/k) for k in ['strata_prefill.py','strata_components.py']})
 budget_pin=sha(REPO/'jiuwenswarm/factory/ccs/strata_budget_workbench/component.py')
 c=dict(schema_version=1,comparison_id='night-fewshot-quality-001',order=list('ACCA'),profiles=profiles,image=NEW,
  quality_cases=16,speed_cases=0,phase_containers=4,budget_component_sha256=budget_pin,source_pins=pins,orchestrator_sha256=sha(__file__),
  dataset_path=str(HERE/'dataset.json'),dataset_sha256=sha(HERE/'dataset.json'),assets=bm.validate_assets(new),
  hard_stop_utc='2026-11-15T07:20:00Z',promotion_authorized=False,
  scope='Eight-shot ARC-Challenge16 sample, disjoint training demonstrations; prompts exceed256 tokens to expose prefill chunk treatment. Two fresh cells per arm, exact output and per-question quality checks. Not official ARC score.')
 frozen(HERE/'contract.json',c)
 return c,new,d

def analyze(c,cells,d):
 tok=load_decoder(ROOT,d['provenance']['tokenizer']['files']);out=[]
 for cell in cells:
  answers=[]
  for case,row in zip(d['quality'],cell['quality']['requests'],strict=True):
   x=decode_answer(row['ids'],tok,case['allowed_letters'],eos_id=1)
   answers.append(dict(id=case['id'],expected=case['expected_letter'],answer=x['answer'],correct=x['answer']==case['expected_letter'],valid=x['answer'] in case['allowed_letters'],text=x['text']))
  out.append(dict(index=cell['index'],arm=cell['arm'],correct=sum(v['correct'] for v in answers),total=16,answers=answers,placement=cell['quality']['budget_identity'],memory=cell['quality']['memory']))
 exact=[]
 for i,j in [(0,3),(1,2),(0,1),(3,2)]:
  exact.append(dict(cells=[i+1,j+1],different_cases=[x['case_id'] for x,y in zip(cells[i]['quality']['requests'],cells[j]['quality']['requests'],strict=True) if x['ids']!=y['ids'] or x['finish']!=y['finish']]))
 regressions=[]
 for k,case in enumerate(d['quality']):
  counts={arm:sum(r['answers'][k]['correct'] for r in out if r['arm']==arm) for arm in 'AC'}
  if counts['C']<counts['A']:regressions.append(dict(id=case['id'],counts=counts))
 return dict(cells=out,exact_tokens=exact,per_question_regressions=regressions,all_answers_valid=all(v['valid'] for r in out for v in r['answers']),fewshot=d['fewshot'],promotion_authorized=False,limitations=['Adapted8-shot ARC-Challenge16 generation, not official full benchmark or loglikelihood score.','Only16 unique test questions, repeats do not increase population sample size.','Demonstrations selected independently from train; quality compared only within this new fixed prompt protocol.','No population noninferiority or exact whole-engine equivalence is established.'])

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
   for phase in ['quality']:
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
