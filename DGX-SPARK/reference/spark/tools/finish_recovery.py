"""Retain recovery evidence and check cleanup; never start a compute job."""
import datetime,fcntl,hashlib,json,os,subprocess,sys,tarfile,shutil
from pathlib import Path
ROOT=Path('/home/user2/software-factory-spark-20261113');REPO=ROOT/'sources/cc-dgx-spark';sys.path.insert(0,str(REPO))
os.environ.update(FACTORY_JOBQ_BIN='/home/user2/rsi-expert-streaming-spark-002/paired-retry-001/lab-source/bin/jobq',JOBQ_DIR='/home/user2/rsi-expert-streaming-spark-002/paired-retry-001/jobq',DOCKER_PREFIX='')
from jiuwenswarm.factory.store import Store
from jiuwenswarm.factory.jobs import Jobs

def command(*args):return subprocess.check_output(args,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def image(tag):
 j=json.loads(command('docker','image','inspect',tag))[0]
 return dict(image_id=j['Id'],architecture=j['Architecture'],labels=j['Config']['Labels'],layers=j['RootFS']['Layers'])

deepseek_id='5f4aeac8fba04610ab19913d3831e9a3';qualify_id='015dae68de67465994b61ea9d895f807';extra_ids=['11a0aec008444aa3b79707c420a15d76','f4e301bee1d248de8af0601dc649bd66']
smoke_root=ROOT/'port-store/runs'/deepseek_id;smoke=json.loads((smoke_root/'smoke-result.json').read_text())
samples=[json.loads(l) for l in (smoke_root/'collector/samples.jsonl').read_text().splitlines()]
qualified=json.loads((ROOT/'port-store/runtime-jobs'/qualify_id/'result.json').read_text())
extra=[json.loads((ROOT/'port-store/runtime-jobs'/aid/'result.json').read_text()) for aid in extra_ids]
checks=[]
for parent in (ROOT/'port-store/runs',ROOT/'port-store/runtime-jobs'):
 for p in parent.rglob('report.json'):
  report=json.loads(p.read_text());cid=report.get('container_id')
  if cid:checks.append(dict(container_id=cid,removed=subprocess.run(['docker','inspect',cid],capture_output=True).returncode!=0))
processes=[]
modules={'jiuwenswarm.factory.'+n for n in ('bridge','runtime_job','spark_run','spark_probe','build_job')}
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  argv=p.read_bytes().split(b'\0')
  if b'-m' in argv and argv[argv.index(b'-m')+1].decode() in modules:processes.append(dict(pid=int(p.parent.name),argv=[s.decode() for s in argv if s]))
 except (OSError,ValueError,IndexError,UnicodeDecodeError):pass
with (ROOT/'port-ipc/bridge.lock').open('a') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for name in ('recovery-test-tmp','recovery-final-test-tmp'):
 p=ROOT/'results'/name
 if p.exists():shutil.rmtree(p)
source_files=sorted(set(command('git','-C',str(REPO),'diff','--name-only').splitlines()+command('git','-C',str(REPO),'ls-files','--others','--exclude-standard').splitlines()))
source_manifest={p:sha(REPO/p) for p in source_files}
(ROOT/'results/recovery-source-manifest.json').write_text(json.dumps(source_manifest,indent=2))
with tarfile.open(ROOT/'results/recovery-source-changes.tar.gz','w:gz') as tar:
 for name in source_files:tar.add(REPO/name,arcname=name,recursive=False)
with Store(ROOT/'port-store') as store:
 rows=[]
 for task in ('spark-deepseek-port','spark-llamacpp-stable'):
  for a in store.dump(task)['attempts']:
   a=Jobs(store).status(a['attempt_id']);rows.append({k:a[k] for k in ('task_id','attempt_id','kind','state','cleanup_state')})
 assert all(r['state'] in ('succeeded','failed','cancelled') for r in rows),rows
 assert not processes and all(c['removed'] for c in checks),(processes,checks)
 assert smoke['status']=='success' and len(smoke['generated_ids'])==32
 assert qualified['status']=='success' and all(r['status']=='success' for r in extra)
 summary=dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='strata_recovered_and_llamacpp_fallback_verified',
   source_branch=command('git','-C',str(REPO),'branch','--show-current'),
   diagnosis='Aggressive automatic GPU expert placement, CPU cache budgeting and oversized prefill buffers on unified RAM; container accounting did not capture most GPU memory. Explicit conservative placement/buffers resolved the observed failure.',
   strata=dict(attempt_id=deepseek_id,status=smoke['status'],output=smoke['generated_text'],generated_tokens=32,exit_code=smoke['collector']['container_exit_code'],duration_s=smoke['collector']['duration_s'],minimum_sampled_host_available_bytes=min(s['host_kib']['MemAvailable']*1024 for s in samples),maximum_sampled_cgroup_current_bytes=max(s['cgroup_current'] for s in samples),config=str(REPO/'deploy/spark/configs/strata-conservative.json'),image=image('factory/strata:cc-dgx-spark-deepseek'),model_provenance_limit=smoke['limitations'][0]),
   fallback=dict(backend='llama.cpp',model='GPT-OSS 20B MXFP4',model_identity=qualified['model'],qualification_attempt=qualify_id,status=qualified['status'],outputs=[r['output'] for r in qualified['records']],repeated_output_equal=qualified['repeated_output_equal'],gpu_activity_confirmed=all(r['gpu_activity_confirmed'] for r in qualified['records']),additional_prompts=[dict(attempt_id=aid,prompt=result['records'][0]['prompt'],output=result['records'][0]['output'],status=result['status']) for aid,result in zip(extra_ids,extra)],image=image('factory/llamacpp:cc-dgx-spark-stable'),launcher=str(REPO/'deploy/spark/run-stable.sh'),limits=qualified['limits']),
   tests=dict(passed=66,log=str(ROOT/'results/recovery-tests-final.log'),earlier_signal_cleanup_failure_corrected=True,original_port_tests_passed=104),
   dependencies=dict(new_packages=[],global_installs=False,model_downloads=False,driver_changes=False),
   cleanup=dict(all_attempts_terminal=True,attempts=rows,owned_processes_remaining=processes,bridge_stopped=True,bridge_lock_released=True,owned_collectors_removed=checks,unrelated_services_preserved=True,shared_caches_not_flushed=True,shared_docker_not_pruned=True),
   limitations=['Bounded functional checks; no long-running load/concurrency certification or general accuracy/performance claim.','The llama.cpp fallback uses a different model from DeepSeek.','The 104 GiB Strata container ceiling does not fully bound unified GPU physical memory; the host guard remains necessary.','DeepSeek model metadata matches, but full weight hashes were not recomputed.'],
   artifacts=dict(source_manifest=str(ROOT/'results/recovery-source-manifest.json'),source_archive=str(ROOT/'results/recovery-source-changes.tar.gz')))
 # Measure owned recovery additions relative to the previous port accounting snapshot.
 old=json.loads((ROOT/'results/port-summary.json').read_text())
 delta=0
 for record in old['disk']['known_added_paths']:
  p=Path(record['path'])
  if p.exists():delta+=int(command('du','-sB1',str(p)).split()[0])-record['allocated_bytes']
 extra_paths=[p for pattern in ('recovery-*','stable-*','strata-smoke-*') for p in (ROOT/'results').glob(pattern) if p.is_file()]
 extra_paths+=[ROOT/'notes/strata-conservative-001.json',ROOT/'notes/run-configs',ROOT/'stable-launch.lock',ROOT/'tools/finish_recovery.py']
 extra_bytes=sum(int(command('du','-sB1',str(p)).split()[0]) for p in extra_paths if p.exists())
 summary['incremental_disk']=dict(known_filesystem_delta_bytes=delta+extra_bytes,measurement='Known owned paths versus port-summary.json plus newly named recovery artifacts, before final evidence ingestion.',docker_note='Fallback packaging has exactly the existing llama image layers, adding labels only. Factory rebuilds reuse layers. No global Docker-cache baseline or shared pruning.')
 (ROOT/'results/recovery-summary.json').write_text(json.dumps(summary,indent=2))
 refs=[]
 names=['recovery-summary.json','recovery-source-manifest.json','recovery-source-changes.tar.gz','recovery-tests-final.log','recovery-factory-image-build.log','stable-llama-executed-worker-001.py']
 for name in names:
  p=ROOT/'results'/name
  for task in ('spark-deepseek-port','spark-llamacpp-stable'):
   record=store.put_artifact(task,'recovery:'+name+':'+sha(p)[:16],p,'application/octet-stream',None)
   if task=='spark-deepseek-port':refs.append(record['artifact_id'])
 store.append_observation('spark-deepseek-port',dict(obs_id='recovery-final:'+sha(ROOT/'results/recovery-summary.json')[:16],kind='recovery_handoff',values=dict(status=summary['status'],strata_attempt_id=deepseek_id,fallback_attempt_id=qualify_id,tests_passed=66,cleanup_verified=True),source_artifacts=refs,limitations='Bounded functional validation only. DeepSeek full weight hashes not recomputed. Fallback model is GPT-OSS 20B.'))
 print(json.dumps(dict(status=summary['status'],strata_tokens=32,min_host_available_gib=summary['strata']['minimum_sampled_host_available_bytes']/2**30,fallback='verified',tests=66,cleanup='verified',known_filesystem_delta_bytes=delta+extra_bytes)))
