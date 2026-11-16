"""Bounded inference qualification; cgroup and I/O evidence, no cache-clearing."""
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
R=Path('/home/user2/software-factory-spark-20261113'); OUT=Path(os.environ['FACTORY_RESULT_DIR'])
mode=sys.argv[1];mem=sys.argv[2]
assert mode in ('tiny','gptoss') and mem in ('2g','8g','16g')
model=Path('/home/user2/rsi-expert-streaming-spark-002/probe-model/stories15M-q8_0.gguf' if mode=='tiny' else '/home/user2/ai4r-data/inference-v3/models/gptoss20/gpt-oss-20b-MXFP4.gguf')
image=json.loads((R/'results'/sys.argv[3]/'build-record.json').read_text())['image_id']
name='ssh-factory-'+os.environ['FACTORY_REQUEST_ID'];created=False
record={'model_path':str(model),'model_bytes':model.stat().st_size,'image_id':image,'memory_limit':mem,'swap_allowed':False,'samples':[],'status':'started','scope':'functional and memory-accounting qualification, not a general accuracy or speed comparison'}
def cmd(a):return subprocess.check_output(a,text=True).strip()
def save(): (OUT/'inference-record.json').write_text(json.dumps(record,indent=2))
def stop(*args):raise KeyboardInterrupt('queue cancellation')
signal.signal(signal.SIGTERM,stop)
try:
    # Full hashing establishes exact local artifact identity but also warms pages outside the container.
    # Record this explicitly rather than mislabel subsequent measurements as cold SSD reads.
    with model.open('rb') as f:record['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
    if mode=='gptoss':
        original=model
        private=R/'cache/owned-model/gptoss20.gguf';private.parent.mkdir(parents=True,exist_ok=True)
        if not private.exists():
            tmp=private.with_suffix('.partial')
            h=hashlib.sha256()
            with original.open('rb') as src,tmp.open('xb') as dst:
                for block in iter(lambda:src.read(8*1024*1024),b''):
                    dst.write(block);h.update(block)
                dst.flush();os.fsync(dst.fileno())
            assert h.hexdigest()==record['model_sha256']
            tmp.rename(private)
        else:
            with private.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==record['model_sha256']
        with private.open('rb') as f:os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
        model=private
        record['private_test_copy']=str(private)
        record['cache_condition']='Owned byte-verified model inode; fsync then POSIX_FADV_DONTNEED on this owned file only before run. Advice is not a guarantee: cgroup I/O observations determine physical reads.'
    argv=['/app/llama-completion','-m','/model.gguf','-p','The three main parts of a computer are','-n','64','-c','512','--temp','0','-s','1','-t','8','-ngl','99' if mode=='tiny' else '0','-no-cnv','--no-display-prompt','--no-repack','-lm','mmap']
    record['argv']=argv
    cmd(['docker','create','--name',name,'--label','factory.owner=software-factory-spark-20261113','--gpus','all','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--cpus=8','--pids-limit=512','--memory='+mem,'--memory-swap='+mem,'--tmpfs','/tmp:rw,size=128m','--mount','type=bind,src='+str(model)+',dst=/model.gguf,readonly','--entrypoint',argv[0],image,*argv[1:]])
    created=True;start=time.monotonic()
    with (OUT/'stdout.txt').open('wb') as stdout,(OUT/'stderr.txt').open('wb') as stderr:
        process=subprocess.Popen(['docker','start','-a',name],stdout=stdout,stderr=stderr)
        cgroup=None
        while process.poll() is None:
            if time.monotonic()-start>300: raise TimeoutError('Inference exceeded 300 seconds')
            state=json.loads(cmd(['docker','inspect','--format','{{json .State}}',name]));pid=state.get('Pid')
            if pid and Path('/proc/'+str(pid)+'/cgroup').exists():
                rel=Path('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::')[-1]
                cgroup=Path('/sys/fs/cgroup')/rel.lstrip('/')
                sample={'seconds':time.monotonic()-start,'stdout_bytes':(OUT/'stdout.txt').stat().st_size}
                for field in ('memory.current','memory.peak','memory.max','memory.swap.current','memory.events','memory.stat','io.stat'):
                    p=cgroup/field
                    if p.exists():sample[field]=p.read_text()
                record['samples'].append(sample)
            save();time.sleep(0.5)
    record.update(wall_seconds=time.monotonic()-start,rc=process.returncode,state=json.loads(cmd(['docker','inspect','--format','{{json .State}}',name])))
    record['stdout_sha256']=hashlib.sha256((OUT/'stdout.txt').read_bytes()).hexdigest()
    record['status']='success' if process.returncode==0 else 'failed'
except BaseException as e:
    record.update(status='failed',error=str(e))
finally:
    if created:
        subprocess.run(['docker','stop','-t','3',name],capture_output=True)
        subprocess.run(['docker','rm',name],capture_output=True)
    save()
print(json.dumps({k:v for k,v in record.items() if k!='samples'}))
sys.exit(0 if record['status']=='success' else 1)


