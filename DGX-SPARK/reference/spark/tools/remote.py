"""Owned SSH execution adapter; no model-provider authentication required."""
import base64, fcntl, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path('/home/user2/software-factory-spark-20261113')
QUEUE = Path('/home/user2/rsi-expert-streaming-spark-002/paired-retry-001/jobq')
JOBQ = QUEUE.parent / 'lab-source/bin/jobq'
ENV = {'HOME':str(ROOT), 'PATH':'/usr/local/cuda/bin:/usr/bin:/bin', 'LANG':'C.UTF-8', 'JOBQ_DIR':str(QUEUE)}
PREFIX = 'ssh-factory-20261113:'

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def owned(relative):
    p=(ROOT/relative).resolve()
    if not p.is_relative_to(ROOT) or p==ROOT: raise ValueError('Path outside owned workspace')
    return p

def atomic(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix('.tmp'); t.write_text(json.dumps(obj,indent=2)); t.replace(p)

def q(*args):
    return subprocess.check_output(['/usr/bin/python3',str(JOBQ),*args],env=ENV,cwd=ROOT,text=True).strip()

def find_job(rid):
    matches=[]
    for p in QUEUE.glob('job-*.json'):
        j=json.loads(p.read_text())
        if j['name']==PREFIX+rid: matches.append(j)
    if len(matches)>1: raise RuntimeError('Duplicate request jobs; manual reconciliation required')
    return matches[0] if matches else None

def public(j):
    return {k:j.get(k) for k in ('id','name','state','class','start','end','rc','pid','pgid','runner_pid','timeout','concurrent_jobs')}

def main(a):
    op=a['operation']
    if op=='inspect':
        jobs=[json.loads(p.read_text()) for p in QUEUE.glob('job-*.json')]
        return {'host':os.uname().nodename,'root':str(ROOT),'queue':str(QUEUE),
                'memory':Path('/proc/meminfo').read_text(),
                'active_jobs':[public(j) for j in jobs if j['state'] in ('running','queued')],
                'owned_jobs':[public(j) for j in jobs if j['name'].startswith(PREFIX)]}
    if op=='stage':
        p=owned(a['path']); data=base64.b64decode(a['data'],validate=True)
        if hashlib.sha256(data).hexdigest()!=a['sha256']: raise ValueError('Transfer hash mismatch')
        if p.exists() and digest(p)!=a['sha256']: raise ValueError('Refuse overwrite of differing file')
        p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            with p.open('xb') as f: f.write(data)
        return {'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size}
    if op=='fetch':
        p=owned(a['path'])
        if p.stat().st_size>16*1024*1024: raise ValueError('Use chunked transfer for files over 16 MiB')
        return {'sha256':digest(p),'data':base64.b64encode(p.read_bytes()).decode()}
    rid=a['id']
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,70}',rid): raise ValueError('Invalid request ID')
    reqpath=owned('requests/'+rid+'.json')
    with (ROOT/'requests.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if op=='submit':
            request=a['request']
            if request['class'] not in ('cpu','build','gpu'): raise ValueError('Invalid job class')
            if not 0<float(request['timeout_s'])<=5400: raise ValueError('Timeout outside bounds')
            script=owned(request['script'])
            if digest(script)!=request['script_sha256']: raise ValueError('Script changed')
            if not isinstance(request.get('args',[]),list) or not all(isinstance(v,str) for v in request.get('args',[])): raise ValueError('Invalid arguments')
            if reqpath.exists() and json.loads(reqpath.read_text())!=request: raise ValueError('ID already names different inputs')
            if not reqpath.exists(): atomic(reqpath,request)
            j=find_job(rid)
            if j is None:
                q('submit','--class',request['class'],'--name',PREFIX+rid,'--timeout',str(request['timeout_s']), '--grace','5','--','/usr/bin/python3',str(ROOT/'tools/remote.py'),'execute',rid)
                j=find_job(rid)
            return public(j)
        j=find_job(rid)
        if j is None: raise ValueError('No owned job for request')
        if op=='cancel': q('cancel',j['id']); return public(find_job(rid))
        if op=='status': return public(j)
        if op=='logs':
            p=owned('results/'+rid+'/output.log')
            if not p.exists(): return {'text':'','state':j['state']}
            with p.open('rb') as f:
                f.seek(max(0,p.stat().st_size-min(int(a.get('bytes',16000)),65536)))
                return {'text':f.read().decode(errors='replace'),'state':j['state']}
        raise ValueError('Unknown operation')

def execute(rid):
    request=json.loads(owned('requests/'+rid+'.json').read_text())
    script=owned(request['script'])
    if digest(script)!=request['script_sha256']: raise ValueError('Queued script changed')
    for relative,expected in request.get('input_hashes',{}).items():
        if digest(owned(relative))!=expected: raise ValueError('Input changed: '+relative)
    out=owned('results/'+rid); out.mkdir(parents=True,exist_ok=True)
    env=dict(ENV,FACTORY_RESULT_DIR=str(out),FACTORY_REQUEST_ID=rid,BUILD_JOBS='8',PYTHONUNBUFFERED='1')
    start=time.time()
    with (out/'output.log').open('wb') as log:
        rc=subprocess.call(['/usr/bin/python3',str(script),*request.get('args',[])],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    atomic(out/'receipt.json',{'id':rid,'request':request,'started':start,'ended':time.time(),'rc':rc,'output_sha256':digest(out/'output.log')})
    return rc

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='execute': sys.exit(execute(sys.argv[2]))
    try: print(json.dumps(main(json.load(sys.stdin))))
    except Exception as e:
        print(json.dumps({'error':type(e).__name__,'detail':str(e)})); sys.exit(1)
