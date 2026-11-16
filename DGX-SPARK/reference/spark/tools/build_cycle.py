"""Bounded Spark native build experiment with persistent, configuration-keyed objects."""
import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/user2/software-factory-spark-20261113')
SOURCE=ROOT/'sources/llama.cpp'
BASE='ghcr.io/ggml-org/llama.cpp@sha256:695214dcb4d4062014335702caee98836bbf92c5974b78331c70e152176cbf08'
TOOLS=['llama-completion','llama-bench','llama-server']
FLAGS=['-DCMAKE_BUILD_TYPE=Release','-DGGML_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=121','-DGGML_NATIVE=OFF','-DBUILD_SHARED_LIBS=ON','-DLLAMA_BUILD_TESTS=OFF','-DLLAMA_CURL=OFF','-DLLAMA_BUILD_UI=OFF','-DLLAMA_USE_PREBUILT_UI=OFF','-DLLAMA_OPENSSL=OFF','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
OUT=Path(os.environ['FACTORY_RESULT_DIR'])
record={'phases':[],'flags':FLAGS,'tools':TOOLS,'base_runtime':BASE,'compiler_workers':8,'candidate_scope':'build pipeline qualification, no model performance claim'}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(phase,args):
    start=time.monotonic(); print(phase, ' '.join(map(str,args)),flush=True)
    p=subprocess.run(list(map(str,args)),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (OUT/(phase+'.log')).write_text(p.stdout)
    record['phases'].append({'phase':phase,'seconds':time.monotonic()-start,'rc':p.returncode,'children_maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss})
    (OUT/'build-record.json').write_text(json.dumps(record,indent=2))
    if p.returncode: print(p.stdout[-10000:]);raise RuntimeError(phase+' failed')
    return p.stdout.strip()
start=time.monotonic()
try:
    if not SOURCE.exists():
        run('clone',['git','clone','--no-hardlinks','--no-checkout','/home/user2/rsi-expert-streaming-001/llama-source',SOURCE])
        run('checkout',['git','-C',SOURCE,'checkout','--detach','cf34d311332e362198f0a410c466d1e940287d02'])
    commit=run('source-id',['git','-C',SOURCE,'rev-parse','HEAD'])
    if run('source-status',['git','-C',SOURCE,'status','--porcelain']):raise ValueError('Dirty source')
    record['source_commit']=commit
    record['source_tree']=run('source-tree',['git','-C',SOURCE,'rev-parse','HEAD^{tree}'])
    record['nvcc']=run('nvcc',['/usr/local/cuda/bin/nvcc','--version'])
    record['gcc']=run('gcc',['gcc','--version'])
    record['cmake']=run('cmake-version',['cmake','--version'])
    key=hashlib.sha256(json.dumps([FLAGS,record['nvcc'],record['gcc'],record['cmake']]).encode()).hexdigest()[:20]
    compiled=ROOT/'cache'/('build-'+key)
    record['cache_key']=key;record['existing_objects']=compiled.exists()
    run('configure',['cmake','-S',SOURCE,'-B',compiled,*FLAGS])
    run('compile',['cmake','--build',compiled,'--parallel','8','--target',*TOOLS])
    record['compile_commands_sha256']=sha(compiled/'compile_commands.json')
    context=OUT/'image';app=context/'app';app.mkdir(parents=True,exist_ok=False)
    for name in TOOLS:shutil.copy2(compiled/'bin'/name,app/name)
    for p in (compiled/'bin').glob('*.so*'):shutil.copy2(p,app/p.name,follow_symlinks=False)
    record['binary_hashes']={p.name:sha(p) for p in app.iterdir() if p.is_file()}
    # Clear inherited /app to prevent old libraries or tools entering this artifact.
    (context/'Dockerfile').write_text('ARG BASE_RUNTIME\nFROM ${BASE_RUNTIME}\nUSER root\nRUN rm -rf /app && mkdir /app\nCOPY app/ /app/\nENV LD_LIBRARY_PATH=/app:/usr/local/nvidia/lib:/usr/local/nvidia/lib64\nWORKDIR /app\nENTRYPOINT []\n')
    tag='factory/llamacpp:ssh-'+os.environ['FACTORY_REQUEST_ID']
    run('package',['docker','build','--network=none','--build-arg','BASE_RUNTIME='+BASE,'--label','factory.owner=software-factory-spark-20261113','--label','factory.source='+commit,'-t',tag,context])
    image=run('image-id',['docker','image','inspect','--format','{{.Id}}',tag]);record['image_id']=image
    run('smoke',['docker','run','--rm','--network=none','--read-only','--entrypoint','/app/llama-completion',image,'--version'])
    record['status']='success'
except Exception as e:
    record.update(status='failed',error=str(e));raise
finally:
    record['wall_seconds']=time.monotonic()-start
    (OUT/'build-record.json').write_text(json.dumps(record,indent=2))
