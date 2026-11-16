"""Collect final port evidence without starting compute or changing shared data."""
import datetime,hashlib,http.client,json,os,socket,subprocess
from pathlib import Path
ROOT=Path('/home/user2/software-factory-spark-20261113');REPO=ROOT/'sources/cc-dgx-spark'
def cmd(*args):return subprocess.check_output(args,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(name):return json.loads(cmd('docker','image','inspect',name))[0]
class DockerHTTP(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.connect('/var/run/docker.sock')
api=DockerHTTP('localhost',timeout=45);api.request('GET','/system/df');response=api.getresponse()
if response.status!=200:raise RuntimeError('Docker disk accounting unavailable')
disk=json.loads(response.read());api.close()
images={k:inspect(v) for k,v in {'factory':'factory/cli:cc-dgx-spark','validation':'factory/cli-test:cc-dgx-spark','engine':'factory/strata:cc-dgx-spark-deepseek'}.items()}
image_disk={}
for key,info in images.items():
 row=next(v for v in disk['Images'] if v['Id']==info['Id'])
 image_disk[key]=dict(image_id=info['Id'],docker_size_bytes=row['Size'],docker_shared_bytes=row.get('SharedSize'),docker_unique_bytes=row['Size']-row['SharedSize'] if row.get('SharedSize',-1)>=0 else None)
paths=[ROOT/'sources/cc-dgx-spark',ROOT/'sources/strata-deepseek',ROOT/'sources/collector',ROOT/'port-store',ROOT/'port-ccstore',ROOT/'port-ipc']
paths+=list((ROOT/'cache').glob('deepseek-*'))
paths+=[p for p in (ROOT/'notes').glob('port-*') if p.is_file()]
paths+=[p for p in (ROOT/'results').glob('port-*') if p.is_file() and p.name!='port-summary.json']
added=[dict(path=str(p),allocated_bytes=int(cmd('du','-sB1',str(p)).split()[0])) for p in paths]
pack=Path('/home/user2/dev/jiuwenswarm/.git/objects/pack')
git_added=[p for p in pack.glob('pack-59564fc7c802f8c6221839439e3766541a023f23.*')]
added.extend(dict(path=str(p),allocated_bytes=p.stat().st_blocks*512) for p in git_added)
run=ROOT/'port-store/runs/ba12e051ab9f47a68163e70deef40057';smoke=json.loads((run/'smoke-result.json').read_text())
samples=[json.loads(l) for l in (run/'collector/samples.jsonl').read_text().splitlines()]
containers=[]
for path in (ROOT/'port-store').rglob('container.id'):
 cid=path.read_text().strip();p=subprocess.run(['docker','inspect',cid],capture_output=True);containers.append(dict(id=cid,removed=p.returncode!=0))
for path in (ROOT/'port-store/runs').glob('*/smoke-result.json'):
 j=json.loads(path.read_text())
 for block in ('collector','gpu_launch_check'):
  cid=j.get(block,{}).get('container_id')
  if cid:containers.append(dict(id=cid,removed=subprocess.run(['docker','inspect',cid],capture_output=True).returncode!=0))
processes=[]
for path in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  value=path.read_bytes().replace(b'\0',b' ').decode(errors='replace')
  if any((' -m jiuwenswarm.factory.'+name) in value for name in ('bridge','spark_run','spark_probe','build_job')) and int(path.parent.name)!=os.getpid():processes.append(dict(pid=int(path.parent.name),command=value))
 except (OSError,ValueError):pass
states=json.loads((ROOT/'results/port-final-attempts.json').read_text())
summary=dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),overall_status='incomplete_inference',
 branch=cmd('git','-C',str(REPO),'branch','--show-current'),factory_base_commit=cmd('git','-C',str(REPO),'rev-parse','HEAD'),
 source_path=str(REPO),build_attempt_id='f0bbabf3d74d46c3a2978dd5399016ac',
 strata_commit='ffa80d73133ea5c548aefe57889a16e8085a938f',ggml_commit='3cf03257f219afbe7334045ff7c6a06ac68c627d',
 executable_sha256='ca7db6709d76e6b7e5518c381b97c6b9a7e645592132d08c8c82d1206ab2fcc1',build_wall_seconds=158.93931738380343,
 images=image_disk,tests=dict(final_passed=104,log=str(ROOT/'results/port-complete-tests.log'),earlier_failures_preserved=True),
 smoke=dict(attempt_id='ba12e051ab9f47a68163e70deef40057',reason=smoke['status'],generated_tokens=len(smoke['generated_ids']),output=smoke['generated_text'],duration_s=smoke['collector']['duration_s'],exit_code=smoke['collector']['container_exit_code'],oom_killed=smoke['collector']['container_oom_killed'],quiescent=smoke['collector']['quiescent'],container_removed=smoke['container_removed'],gpu_launch_check=smoke['gpu_launch_check']['reason'],memory_bytes=smoke['collector']['memory_bytes'],swap_extra_bytes=0,cpus=8,token_cap=32,timeout_s=3600,
 minimum_observed_host_available_bytes=min(v['host_kib']['MemAvailable']*1024 for v in samples),maximum_observed_cgroup_current_bytes=max(v['cgroup_current'] for v in samples)),
 provenance_limit='Matching model sizes and timestamps do not establish full hash verification. Full model hashes were not recomputed.',
 accounting_limit='GPU unified-memory pressure was not fully charged to the container cgroup; host memory guard stopped loading. No inference success or performance claim.',
 disk=dict(known_added_paths=added,known_added_filesystem_allocated_bytes=sum(v['allocated_bytes'] for v in added),image_accounting=image_disk,shared_build_cache_bytes=disk.get('BuildCache') and sum(v.get('Size',0) for v in disk['BuildCache']),limitation='Known newly created paths and Docker image accounting are measured. A before/after total Docker-cache baseline was not captured; shared BuildKit data was not pruned and cannot all be attributed to this port. Image unique bytes do not include shared layers or cache.'),
 dependencies=dict(production_added={'rfc8785':'0.1.4'},production_inventory=str(ROOT/'results/port-production-dependencies.json'),test_inventory=str(ROOT/'results/port-test-dependencies.json'),host_global_installs=False),
 cleanup=dict(attempts_terminal=all(v['state'] in ('succeeded','failed','cancelled') for v in states),containers=containers,owned_processes_remaining=processes,bridge_stopped=not processes,unrelated_services_preserved=True,temporary_paths_removed=['sources/deepseek-ggml','results/port-test-tmp','results/port-regression-tmp','results/port-builder-tmp','results/port-complete-tmp'],shared_docker_pruning=False,host_cache_flushing=False))
(ROOT/'results/port-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(dict(status=summary['overall_status'],tests=104,allocated_new_filesystem_bytes=summary['disk']['known_added_filesystem_allocated_bytes'],image_disk=image_disk,cleanup=summary['cleanup'])))
