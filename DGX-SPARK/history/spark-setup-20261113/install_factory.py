"""Install the verified cc-siminfeng snapshot and register actual Spark build evidence."""
import hashlib, json, subprocess, sys, tarfile
from pathlib import Path
ROOT = Path('/home/user2/software-factory-spark-20261113')
archive = ROOT/'incoming/cc-siminfeng-c7891472.tar.gz'
expected = 'bdf1e4327ea21d692b07369618f979d026b98fe08cad703d0b056e4815421cc7'
with archive.open('rb') as f:
    if hashlib.file_digest(f,'sha256').hexdigest() != expected:
        raise RuntimeError('Source transfer hash mismatch')
source = ROOT/'sources/cc-siminfeng-c7891472'
source.mkdir(exist_ok=False)
with tarfile.open(archive) as tar:
    tar.extractall(source, filter='data')
sys.path.insert(0,str(source))
from jiuwenswarm.factory.store import Store
task = 'spark-strata-fork-20261113'
with Store(ROOT/'factory-store') as store:
    store.create_task({'task_id':task,'objective':'Qualify the named Strata DGX Spark fork through SSH, preserving llama.cpp as a control baseline','target':{'profile':'spark-gb10'},'allowed_effects':['process.exec'],'constraints':{'agent_location':'Windows','no_remote_provider_credentials':True,'build_inference_exclusive':True}})
    path = ROOT/'results/strata-fork-build-001/build-record.json'
    record = json.loads(path.read_text())
    artifact = store.put_artifact(task,'strata-fork-build-001',path.read_bytes(),'application/json',None)
    store.append_observation(task,{'obs_id':'strata-fork-build-001','kind':'ssh_build_result','values':{'status':record['status'],'image_id':record['image_id'],'wall_seconds':record['wall_seconds']},'source_artifacts':[artifact['artifact_id']],'host_run':{'request_id':'strata-fork-build-001'},'limitations':'Imported actual SSH execution evidence, locally directed. Launch help only; no model inference or performance claim.'})
manifest = {'factory_branch':'cc-siminfeng','factory_commit':'c7891472b399aecba42735df19b8c80451231355','archive_sha256':expected,'source_path':str(source),'task_id':task,'strata':record,'lifecycle':{'reasoning':'local Windows agent','remote_controller_running':False,'queue_worker':'retained for durable execution, about 7 MiB RSS at inspection','handoff':'build processes exit before launch; GPU-process, owned-container and available-memory admission checked','limitation':'No automatic shutdown of an independently started factory controller is implemented; shared unrelated services preserved'}}
(ROOT/'results/strata-fork-setup.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'factory_source':str(source),'task_id':task,'registered':True}))
