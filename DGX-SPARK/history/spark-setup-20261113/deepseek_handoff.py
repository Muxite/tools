"""Record selected DeepSeek target and verify existing pack metadata without loading it."""
import hashlib, json, subprocess
from pathlib import Path
root=Path('/home/user2/software-factory-spark-20261113')
source=Path('/home/user2/strata-baseline/Strata')
pack=Path('/home/user2/strata-baseline/Strata-data/packs/deepseek-v4.1-flash-ist-das-2.00bpw')
manifest=json.loads((pack/'pack-source.json').read_text())
checks=[]
for name,(size,mtime) in manifest['files'].items():
    p=(Path(manifest['model_dir'])/name).resolve()
    s=p.stat()
    checks.append({'path':str(p),'bytes':s.st_size,'size_matches':s.st_size==size,'mtime_matches':s.st_mtime_ns==mtime})
if not all(c['size_matches'] and c['mtime_matches'] for c in checks):
    raise RuntimeError('Existing model pack metadata mismatch')
engine=source/'build-spark-dsv41/strata-dsv41'
record={
    'selected_target':'Existing DeepSeek assets with newer Strata',
    'user_direction':'Finish main setup and end local turn; Codex is now available on Spark',
    'source':str(source),
    'commit':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),
    'engine':str(engine),
    'engine_version':subprocess.check_output([str(engine),'--version'],text=True).strip(),
    'engine_sha256':hashlib.sha256(engine.read_bytes()).hexdigest(),
    'pack':str(pack),'model_checks':checks,
    'verification_limit':'Sizes and nanosecond mtimes match existing pack provenance; full model hashes were not recomputed in this turn.',
    'factory_source':str(root/'sources/cc-siminfeng-c7891472'),
    'ssh_adapter':str(root/'tools/remote_v3.py'),
    'shared_queue':'/home/user2/rsi-expert-streaming-spark-002/paired-retry-001/jobq',
    'inference_started':False,
    'next_action':'Submit one bounded DeepSeek smoke through the shared GPU queue, record output and cleanup. Read the source AGENTS.md and existing collector before execution.',
    'existing_configuration':str(source/'strata-deepseek-v4.1-flash-ist-das-2.00bpw.json'),
    'qualified_collector_reference':'/home/user2/strata-rsi-engine-capability-004-20261112/controller/lab_driver_v7.py',
    'resource_rules':['No simultaneous build and inference jobs','Keep reasoning local or checkpoint and exit owned remote controller before inference','Retain the small queue worker','Check unrelated compute and available host memory before admission','Stop only explicitly owned processes and containers; do not flush shared host caches','Bound memory, swap, runtime and output; verify container cleanup after run'],
    'caveats':['The newly built shi3z fork image targets Qwen and is not the DeepSeek executable','Historical experiments used modified binaries; do not label them the unmodified current baseline','No autonomous remote controller shutdown implemented yet','No new model inference or performance result in this handoff']
}
path=root/'notes/deepseek-next-run.json'
path.write_text(json.dumps(record,indent=2))
print(json.dumps({'handoff':str(path),'files_verified':len(checks),'total_bytes':sum(c['bytes'] for c in checks),'version':record['engine_version'],'inference_started':False}))
