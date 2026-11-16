"""Pinned native Spark build, packaged into an immutable CUDA runtime image."""
import hashlib, json, os, shutil, subprocess, time
from pathlib import Path

ROOT = Path('/home/user2/software-factory-spark-20261113')
SOURCE = ROOT / 'sources/strata-dgx-spark'
DEPS = ROOT / 'sources/strata-ggml'
OUT = Path(os.environ['FACTORY_RESULT_DIR'])
BASE = 'ghcr.io/ggml-org/llama.cpp@sha256:695214dcb4d4062014335702caee98836bbf92c5974b78331c70e152176cbf08'
record = {'phases': [], 'scope': 'Engine build and launch qualification only; no inference performance claim'}

def run(name, args):
    start = time.monotonic()
    print(name, flush=True)
    with (OUT / (name + '.log')).open('w') as log:
        p = subprocess.run([str(a) for a in args], stdout=log, stderr=subprocess.STDOUT)
    record['phases'].append({'name': name, 'seconds': time.monotonic()-start, 'rc': p.returncode})
    if p.returncode:
        raise RuntimeError(name + ': ' + (OUT/(name+'.log')).read_text()[-6000:])
    return (OUT/(name+'.log')).read_text().strip()

def admission():
    """Fail closed on other compute; do not kill unrelated jobs or flush shared caches."""
    mem = {k: int(v.split()[0]) for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
    gpu = run('gpu-admission', ['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'])
    owned = run('container-admission', ['docker','ps','-q','--filter','label=factory.owner=software-factory-spark-20261113'])
    record['admission'] = {'available_kib':mem['MemAvailable'], 'minimum_kib':16*1024*1024, 'gpu_processes':gpu, 'owned_containers':owned}
    if gpu or owned or mem['MemAvailable'] < 16*1024*1024:
        raise RuntimeError('Compute/memory admission failed; no workloads stopped automatically')

start = time.monotonic()
try:
    record['source_commit'] = run('source', ['git','-C',SOURCE,'rev-parse','HEAD'])
    if run('source-clean', ['git','-C',SOURCE,'status','--porcelain']): raise RuntimeError('Dirty source')
    record['dependency_commit'] = run('dependency', ['git','-C',DEPS,'rev-parse','HEAD'])
    if record['dependency_commit'] != '3cf03257f219afbe7334045ff7c6a06ac68c627d': raise RuntimeError('Dependency changed')
    if run('dependency-clean', ['git','-C',DEPS,'status','--porcelain']): raise RuntimeError('Dirty dependency')
    admission()
    flags = ['-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DSTRATA_BUILD_TESTS=OFF','-DCMAKE_CUDA_ARCHITECTURES=121','-DSTRATA_GGML_DIR='+str(DEPS)]
    record['flags'] = flags
    record['nvcc'] = run('nvcc', ['/usr/local/cuda/bin/nvcc','--version'])
    record['gcc'] = run('gcc', ['gcc','--version'])
    key = hashlib.sha256(json.dumps([flags,record['nvcc'],record['gcc']]).encode()).hexdigest()[:20]
    build = ROOT / 'cache' / ('strata-'+key)
    run('configure', ['cmake','-S',SOURCE,'-B',build,*flags])
    run('compile', ['cmake','--build',build,'--parallel','8','--target','strata'])
    context = OUT/'image'; app = context/'app'; app.mkdir(parents=True)
    shutil.copy2(build/'strata', app/'strata')
    record['binary_sha256'] = hashlib.sha256((app/'strata').read_bytes()).hexdigest()
    (context/'Dockerfile').write_text('ARG BASE\nFROM ${BASE}\nUSER root\nRUN rm -rf /app && mkdir /app\nCOPY app/ /app/\nENV LD_LIBRARY_PATH=/app:/usr/local/nvidia/lib:/usr/local/nvidia/lib64\nWORKDIR /app\nENTRYPOINT ["/app/strata"]\n')
    tag = 'factory/strata:ssh-'+os.environ['FACTORY_REQUEST_ID']
    run('package', ['docker','build','--network=none','--build-arg','BASE='+BASE,'--label','factory.owner=software-factory-spark-20261113','--label','factory.source='+record['source_commit'],'-t',tag,context])
    record['image_id'] = run('image-id',['docker','image','inspect','--format','{{.Id}}',tag])
    record['image_tag'] = tag
    # Compilation and packaging have exited before engine admission.
    admission()
    run('launch-smoke',['docker','run','--rm','--gpus','all','--network=none','--read-only','--memory=2g','--memory-swap=2g','--cpus=2','--label','factory.owner=software-factory-spark-20261113',record['image_id'],'--help'])
    record['status'] = 'success'
except Exception as e:
    record.update(status='failed',error=str(e))
    raise
finally:
    record['wall_seconds'] = time.monotonic()-start
    (OUT/'build-record.json').write_text(json.dumps(record,indent=2))
