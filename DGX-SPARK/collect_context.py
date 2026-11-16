from pathlib import Path
import subprocess, tarfile, io, json
stage=Path(r'C:/Users/m50066326/huawei/outputs/dgx-spark-context-20261115')
stage.mkdir(exist_ok=True)
remote=r'''
from pathlib import Path
import subprocess,json,tarfile,io,hashlib,sys,datetime
root=Path('/home/user2/software-factory-spark-20261113')
src=root/'sources/cc-dgx-spark'
picked={}; omitted=[]
def add(p,arc):
 if p.is_symlink() or not p.is_file(): return
 if p.stat().st_size>1500000:
  omitted.append({'path':str(p),'reason':'over 1.5 MB','bytes':p.stat().st_size}); return
 if p.suffix.lower() not in {'.md','.json','.jsonl','.yaml','.yml','.py','.sh','.csv','.txt','.toml','.patch','.sha256'} and p.name not in {'Dockerfile','LICENSE'}: return
 if any(x in p.parts for x in ['.git','__pycache__','.venv','venv','node_modules','sessions','agent-data','agent-workspace']): return
 if any(x in p.name.lower() for x in ['credential','auth.json','token-cache','.env']): return
 picked[arc]=p
for sub in ['docs/architecture/factory','jiuwenswarm/factory','tests/factory','deploy/spark']:
 for p in (src/sub).rglob('*'): add(p,'factory-source/'+p.relative_to(src).as_posix())
for p in (src/'scripts').glob('*factory*'): add(p,'factory-source/'+p.relative_to(src).as_posix())
for p in (src/'tools').glob('*.py'): add(p,'factory-source/'+p.relative_to(src).as_posix())
for sub in ['AGENTS.md','pyproject.toml','LICENSE']:
 add(src/sub,'factory-source/'+sub)
for sub in ['notes','tools','requests','capsules']:
 for p in (root/sub).rglob('*'): add(p,'spark/'+p.relative_to(root).as_posix())
for p in (root/'results').glob('*.json'): add(p,'spark/'+p.relative_to(root).as_posix())
for sub in ['night-branch-analysis-v1','night-long-prefill-v1','night-fewshot-quality-v1','night-branch-engine-v2','night-branch-jiuwen-v1','development-numerical-analysis-001','development-numerical-analysis-002','development-cpu-mission-001','cc-workflow-efficiency-002','cc-native-inventory-once-002']:
 for p in (root/sub).rglob('*'):
  rel=p.relative_to(root/sub)
  if any(x in rel.parts for x in ['admitted-source','execution-source','runtime','factory','source-copies','ccstore','baseline-ccstore','candidate-ccstore','controller-attempts']): continue
  add(p,'spark/'+p.relative_to(root).as_posix())
for p in root.glob('handoff-*/*'):
 if p.is_file(): add(p,'spark/'+p.relative_to(root).as_posix())
for p in (root/'handoff-night-branches-20261115/night-branches/evidence').rglob('*'):
 if any(x in p.parts for x in ['ccstore','baseline-ccstore','candidate-ccstore','releases','runtime','source-copies']): continue
 add(p,'night-evidence/'+p.relative_to(root/'handoff-night-branches-20261115/night-branches/evidence').as_posix())
def git(*args): return subprocess.run(['git','-C',str(src),*args],capture_output=True,text=True).stdout
meta={'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'factory_head':git('rev-parse','HEAD').strip(),'branch':git('branch','--show-current').strip(),'status_porcelain':git('status','--porcelain'),'snapshot_kind':'selected working-tree files, including uncommitted development; not a complete restorable checkout','omitted':omitted,'files':[]}
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as tar:
 for arc,p in sorted(picked.items()):
  b=p.read_bytes(); meta['files'].append({'path':arc,'source':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  t=tarfile.TarInfo(arc); t.size=len(b);tar.addfile(t,io.BytesIO(b))
 b=json.dumps(meta,indent=2).encode();t=tarfile.TarInfo('REMOTE-SNAPSHOT.json');t.size=len(b);tar.addfile(t,io.BytesIO(b))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','user2@100.105.127.48','python3 -'],input=remote.encode(),capture_output=True,timeout=180)
if r.returncode: raise RuntimeError(r.stderr.decode())
with tarfile.open(fileobj=io.BytesIO(r.stdout),mode='r:gz') as t:t.extractall('\\\\?\\'+str(stage),filter='data')
print(json.dumps({'stage':str(stage),'transfer_bytes':len(r.stdout),'files':len(json.loads((stage/'REMOTE-SNAPSHOT.json').read_text())['files'])}))
