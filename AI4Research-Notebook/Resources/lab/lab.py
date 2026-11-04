"""Single-host, operator-driven Docker experiment lab prototype."""
from __future__ import annotations
import argparse, contextlib, hashlib, json, math, os, re, shutil, subprocess, sys, time, uuid
from pathlib import Path

class LabError(RuntimeError): pass
IDENT=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,47}$')

class Runner:
    def __call__(self,args,*,cwd=None,check=True,capture=True,merge=False):
        p=subprocess.run([str(x) for x in args],cwd=cwd,text=True,stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.STDOUT if capture and merge else (subprocess.PIPE if capture else None),shell=False)
        if check and p.returncode:
            detail=p.stdout if merge else p.stderr
            raise LabError(f"command failed ({p.returncode}): {args[0]} {args[1]}: {detail or ''}")
        if not capture: return ''
        return (p.stdout or '') if merge else (p.stdout or '').strip()

@contextlib.contextmanager
def file_lock(path):
    path.parent.mkdir(parents=True,exist_ok=True); f=open(path,'a+b')
    try:
        if os.name=='nt':
            import msvcrt
            f.seek(0); msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl
            fcntl.flock(f,fcntl.LOCK_EX)
        yield
    finally:
        if os.name=='nt':
            import msvcrt
            f.seek(0); msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
        else: fcntl.flock(f,fcntl.LOCK_UN)
        f.close()

def within(path,base):
    try: Path(path).resolve().relative_to(Path(base).resolve()); return True
    except ValueError: return False

def load_manifest(path):
    manifest_path=Path(path).resolve()
    m=json.loads(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(m,dict): raise LabError('manifest must be a JSON object')
    for k in ('experiment','repo','revision','image','evidence_root','command'):
        if k not in m or m[k] in ('',None,[]): raise LabError(f'manifest missing {k}')
    if not isinstance(m['experiment'],str) or not IDENT.fullmatch(m['experiment']): raise LabError('invalid experiment identifier')
    if not re.fullmatch(r'[0-9a-fA-F]{40}',m['revision']): raise LabError('revision must be full git commit SHA')
    if not isinstance(m['image'],str) or not re.search(r'@sha256:[0-9a-f]{64}$',m['image']): raise LabError('image must be pinned by sha256 digest')
    if not isinstance(m['command'],list) or not m['command'] or not all(isinstance(x,str) and x for x in m['command']): raise LabError('command must be a nonempty list of strings')
    lim=m.get('limits',{})
    memory=lim.get('memory')
    try: positive=(not isinstance(lim['cpus'],bool) and math.isfinite(float(lim['cpus'])) and float(lim['cpus'])>0 and
                   not isinstance(lim['pids'],bool) and int(lim['pids'])>0 and str(int(lim['pids']))==str(lim['pids']))
    except (KeyError,TypeError,ValueError): positive=False
    if not isinstance(memory,str) or not re.fullmatch(r'[1-9]\d*(?:\.\d+)?(?:[bkmg])?',memory,re.I) or not positive:
        raise LabError('positive Docker limits.memory, limits.cpus, and limits.pids are required')
    sched=m.get('scheduling',{})
    if not isinstance(sched,dict) or not isinstance(sched.get('exclusive',False),bool): raise LabError('scheduling.exclusive must be boolean')
    if m.get('env_file') is not None and not isinstance(m['env_file'],str): raise LabError('env_file must be a path string')
    for key in ('repo','evidence_root','env_file'):
        if m.get(key) is None: continue
        if not isinstance(m[key],str) or not m[key]: raise LabError(f'{key} must be a path string')
        value=Path(m[key])
        m[key]=str((value if value.is_absolute() else manifest_path.parent/value).resolve())
    return m

class Lab:
    def __init__(self,root,runner=None): self.root=Path(root).resolve(); self.run=runner or Runner()
    def _valid(self,n):
        if not isinstance(n,str) or not IDENT.fullmatch(n): raise LabError('invalid experiment identifier')
    def _owner(self,create=False):
        f=self.root/'.lab-owner'
        if f.exists():
            val=f.read_text().strip()
            if not re.fullmatch(r'[0-9a-f-]{36}',val): raise LabError('invalid lab owner marker')
            return val
        if not create: raise LabError('lab root has no owner marker')
        self.root.mkdir(parents=True,exist_ok=True); val=str(uuid.uuid4()); tmp=f.with_suffix('.tmp'); tmp.write_text(val); os.replace(tmp,f); return val
    def read(self,n):
        self._valid(n); p=self.root/n/'state.json'
        if not within(p,self.root) or not p.is_file(): raise LabError(f'unknown experiment: {n}')
        s=json.loads(p.read_text())
        if s.get('owner')!=self._owner() or s.get('name')!=n: raise LabError('experiment owner mismatch')
        return s
    def save(self,n,s):
        self._valid(n); p=self.root/n/'state.json'
        if not within(p,self.root): raise LabError('state path escapes lab root')
        p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(s,indent=2)); os.replace(tmp,p)
    def _docker(self,args,merge=False): return self.run(['docker',*args],merge=merge)
    def _inspect(self,kind,name,experiment):
        raw=self._docker(['inspect','--type',kind,name]); data=json.loads(raw)
        if not isinstance(data,list) or len(data)!=1: raise LabError(f'cannot verify owned {kind}: {name}')
        item=data[0]; labels=(item.get('Config') or {}).get('Labels') or item.get('Labels') or {}
        if labels.get('lab.owner')!=self._owner() or labels.get('lab.experiment')!=experiment or labels.get('lab.managed')!='true': raise LabError(f'ownership verification failed for {kind}: {name}')
        return item
    def _resource_labels(self,n): return ['--label',f'lab.owner={self._owner()}','--label',f'lab.experiment={n}','--label','lab.managed=true']
    @staticmethod
    def _missing_resource(error):
        msg=str(error).lower()
        return ('no such object' in msg or 'no such volume' in msg or 'no such network' in msg or
                'no such container' in msg or 'not found' in msg or '404' in msg)
    def create(self,manifest,dry=False):
        m=load_manifest(manifest); n=m['experiment']; self._valid(n); d=self.root/n
        owner=self._owner() if (self.root/'.lab-owner').exists() else (str(uuid.uuid4()) if dry else None)
        repo=Path(m['repo']).resolve(); evidence_root=Path(m['evidence_root']).resolve()
        evidence=evidence_root/f"lab-{owner.replace('-','')}"/n if owner else evidence_root/n
        worktree=d/'worktree'
        if within(evidence,self.root) or within(evidence,repo): raise LabError('evidence must be outside lab state and source repository')
        if d.exists(): raise LabError(f'experiment already exists: {n}')
        if dry:return {'worktree':str(worktree),'evidence':str(evidence),'owner':owner}
        with file_lock(self.root/'.schedule.lock'):
            owner=self._owner(create=True)
            evidence=evidence_root/f"lab-{owner.replace('-','')}"/n
            if within(evidence,self.root) or within(evidence,repo): raise LabError('evidence must be outside lab state and source repository')
            if d.exists(): raise LabError(f'experiment already exists: {n}')
            rev=self.run(['git','-C',repo,'rev-parse','--verify',m['revision']+'^{commit}'])
            if rev.lower()!=m['revision'].lower(): raise LabError('resolved revision mismatch')
            if evidence.exists(): raise LabError('owner-scoped evidence directory already exists')
            evidence.mkdir(parents=True,exist_ok=False); evidence=evidence.resolve()
            if within(evidence,self.root) or within(evidence,repo): raise LabError('resolved evidence path overlaps protected path')
            owner_tag=owner.replace('-',''); prefix=f'lab-{owner_tag}-{n}'
            s={'owner':owner,'name':n,'manifest':m,'revision':rev,'created':time.time(),'status':'creating',
               'worktree':str(worktree),'evidence':str(evidence),'container':prefix,'network':prefix,'volume':prefix}
            self.save(n,s)
            try:
                self.run(['git','-C',repo,'worktree','add','--detach',worktree,rev])
                s['status']='created'; self.save(n,s); return s
            except Exception:
                s['status']='create_failed'; self.save(n,s); raise
    def _validate_external(self,s):
        n=s['name']; self._valid(n)
        expected_worktree=self.root/n/'worktree'
        if (not within(expected_worktree,self.root) or expected_worktree.is_symlink() or
                getattr(expected_worktree,'is_junction',lambda:False)() or
                s.get('owner')!=self._owner() or Path(s.get('worktree','')).resolve()!=expected_worktree.resolve()):
            raise LabError('stored path or owner validation failed')
        evidence=Path(s.get('evidence','')).resolve(); repo=Path(s['manifest']['repo']).resolve()
        expected_evidence=Path(s['manifest']['evidence_root']).resolve()/f"lab-{s['owner'].replace('-','')}"/n
        if evidence!=expected_evidence.resolve() or within(evidence,self.root) or within(evidence,repo): raise LabError('evidence overlaps protected path or has unexpected path')
        expected_prefix=f"lab-{s['owner'].replace('-','')}-{n}"
        if any(s.get(k)!=expected_prefix for k in ('container','network','volume')): raise LabError('resource name/owner mismatch')
        m=s['manifest']; ef=m.get('env_file')
        if ef:
            p=Path(ef).resolve()
            if not p.is_file() or within(p,self.root) or within(p,s['worktree']) or within(p,s['evidence']) or within(p,Path(m['repo']).resolve()):
                raise LabError('env_file must exist outside state, worktree, repository, and evidence mounts')
    def _command(self,s):
        m=s['manifest']; self._validate_external(s)
        args=['run','-d','--name',s['container'],'--network',s['network'],*self._resource_labels(s['name']),
              '--memory',m['limits']['memory'],'--cpus',str(m['limits']['cpus']),'--pids-limit',str(m['limits']['pids']),
              '--mount',f"type=bind,src={s['evidence']},dst=/evidence",'--mount',f"type=bind,src={s['worktree']},dst=/workspace,readonly",
              '--mount',f"type=volume,src={s['volume']},dst=/workdata",'--workdir','/workspace']
        if m.get('env_file'): args += ['--env-file',str(Path(m['env_file']).resolve())]
        return ['docker',*args,m['image'],*m['command']]
    def _running(self):
        found=[]
        if not self.root.exists(): return found
        for p in self.root.iterdir():
            sf=p/'state.json'
            if p.is_dir() and sf.is_file():
                try:
                    s=json.loads(sf.read_text())
                    if s.get('owner')==self._owner() and s.get('status') in ('running','provisioning'): found.append(s)
                except (ValueError,OSError): pass
        return found
    def start(self,n,dry=False):
        self._valid(n); s=self.read(n)
        if dry:return self._command(s)
        with file_lock(self.root/'.schedule.lock'):
            s=self.read(n); self._validate_external(s)
            if s['status']=='stopped': raise LabError('one-shot experiments cannot be restarted; create a new experiment identifier')
            if s['status'] not in ('created','provisioning'): raise LabError('experiment is not startable')
            active=[x for x in self._running() if x['name']!=n]
            exclusive=bool(s['manifest'].get('scheduling',{}).get('exclusive',False))
            if active and (exclusive or any(x['manifest'].get('scheduling',{}).get('exclusive',False) for x in active)):
                raise LabError('exclusive scheduling conflict with another running experiment')
            s['status']='provisioning'; self.save(n,s)
            # Idempotent recovery: verify deterministic resources before reuse; never recreate blindly.
            self._ensure_network(s); self._ensure_volume(s)
            try:
                info=self._inspect('container',s['container'],n); state=info.get('State',{})
                if state.get('Running'):
                    s.update(container_id=info.get('Id',s['container']),status='running'); self.save(n,s); return s
                raise LabError('container exists but is not running; inspect/export it before operator recovery')
            except LabError as e:
                if not self._missing_resource(e): raise
            # Existing but stopped containers are never silently restarted: each id names one planned run.
            cmd=self._command(s)
            cid=self._docker(cmd[1:])
            s.update(container_id=cid,status='running',started=time.time()); self.save(n,s); return s
    def _ensure_network(self,s):
        try:
            network=self._inspect('network',s['network'],s['name'])
            if network.get('Internal') is not True:
                raise LabError('owned experiment network is not internal; refusing network-enabled resource')
        except LabError as e:
            if not self._missing_resource(e): raise
            self._docker(['network','create','--internal',*self._resource_labels(s['name']),s['network']])
    def _ensure_volume(self,s):
        try: self._inspect('volume',s['volume'],s['name'])
        except LabError as e:
            if not self._missing_resource(e): raise
            self._docker(['volume','create',*self._resource_labels(s['name']),s['volume']])
    def inspect(self,n,dry=False):
        self._valid(n); s=self.read(n)
        if dry:return {'state':s,'docker':['docker','inspect','--type','container',s['container']]}
        try:
            info=self._inspect('container',s['container'],n)
            if isinstance(info.get('Config'),dict):
                for key in ('Env','Cmd','Entrypoint'):
                    if key in info['Config']: info['Config'][key]=['<redacted>']
            s['docker_inspect']=info
        except LabError as e:
            if s.get('status') not in ('created','creating','create_failed') or not self._missing_resource(e): raise
            s['docker_inspect']=None
        return s
    def stop(self,n,dry=False):
        self._valid(n); s=self.read(n)
        if dry:return ['docker','stop',s['container']] if s['status'] in ('running','provisioning') else s
        with file_lock(self.root/'.schedule.lock'):
            s=self._reconcile_locked(self.read(n))
            if s['status']=='created':
                s.update(status='stopped',stopped=time.time()); self.save(n,s); return s
            if s['status']!='running': return s
            self._inspect('container',s['container'],n); self._docker(['stop',s['container']])
            s.update(status='stopped',stopped=time.time()); self.save(n,s); return s
    def export(self,n,dry=False):
        self._valid(n); s=self.read(n); dest=Path(s['evidence']).with_name(Path(s['evidence']).name+'.export')
        if dry:return {'destination':str(dest),'required':['manifest.json','logs.txt','provenance.json','checksums.sha256','artifacts/']}
        with file_lock(self.root/'.schedule.lock'):
            s=self.read(n); self._validate_external(s); dest=Path(s['evidence']).with_name(Path(s['evidence']).name+'.export')
            if s['status'] in ('running','provisioning','stopped'):
                s=self._reconcile_locked(s)
            if s['status']=='running': raise LabError('stop experiment before export')
            if s['status']=='created': raise LabError('reconcile/stop experiment before export')
            self._verify_revision(s)
            self._verify_clean_worktree(s)
            if dest.exists(): raise LabError('export already exists; exports are retained')
            temp=dest.with_name('export.tmp-'+uuid.uuid4().hex); temp.mkdir(parents=True)
            try:
                (temp/'manifest.json').write_text(json.dumps(s['manifest'],indent=2))
                (temp/'provenance.json').write_text(json.dumps({k:s.get(k) for k in ('owner','name','revision','created','started','stopped','container_id')},indent=2))
                (temp/'logs.txt').write_text(self._docker(['logs',s['container']],merge=True) if s.get('container_id') else '')
                # Snapshot persistent bind output, excluding exports/temp outputs; also retrieve named-volume data.
                artifacts=temp/'artifacts'; artifacts.mkdir()
                bind_artifacts=artifacts/'bind'; bind_artifacts.mkdir()
                evidence=Path(s['evidence'])
                for src in evidence.iterdir():
                    if src.name.endswith('.export') or src.name.startswith('export.tmp-'): continue
                    self._copy_safe(src,bind_artifacts/src.name)
                if s.get('container_id'):
                    target=artifacts/'volume'; target.mkdir()
                    self._docker(['cp',f"{s['container']}:/workdata/.",str(target)])
                    self._reject_links(target)
                self._verify_revision(s)
                files=sorted(x for x in temp.rglob('*') if x.is_file())
                sums=''.join(f"{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(temp).as_posix()}\n" for x in files)
                (temp/'checksums.sha256').write_text(sums)
                for line in sums.splitlines():
                    digest,rel=line.split('  ',1)
                    if hashlib.sha256((temp/rel).read_bytes()).hexdigest()!=digest: raise LabError('evidence checksum verification failed')
                if not all((temp/x).is_file() for x in ('manifest.json','logs.txt','provenance.json','checksums.sha256')): raise LabError('evidence incomplete')
                temp.rename(dest); s.update(exported=True,export_path=str(dest),status='exported'); self.save(n,s); return s
            except Exception: shutil.rmtree(temp,ignore_errors=True); raise
    @staticmethod
    def _is_linklike(path):
        p=Path(path)
        junction=getattr(p,'is_junction',None)
        return p.is_symlink() or (callable(junction) and junction())
    @staticmethod
    def _reject_links(path):
        """Reject symlinks/junctions and special files before reading export contents."""
        p=Path(path)
        if Lab._is_linklike(p): raise LabError(f'evidence contains a symlink or junction: {p}')
        if not p.is_dir(): return
        for child in p.iterdir():
            if Lab._is_linklike(child): raise LabError(f'evidence contains a symlink or junction: {child}')
            if child.is_dir(): Lab._reject_links(child)
            elif not child.is_file(): raise LabError(f'evidence contains a special file: {child}')
    @staticmethod
    def _copy_safe(src,dst):
        Lab._reject_links(src)
        if src.is_dir(): shutil.copytree(src,dst,symlinks=True)
        elif src.is_file(): shutil.copy2(src,dst,follow_symlinks=False)
        else: raise LabError(f'evidence contains a special file: {src}')
    def _verify_revision(self,s):
        head=self.run(['git','-C',s['worktree'],'rev-parse','HEAD']).strip()
        if head.lower()!=s['revision'].lower(): raise LabError('worktree revision changed')
    def _verify_clean_worktree(self,s):
        status=self.run(['git','-C',s['worktree'],'status','--porcelain']).strip()
        if status: raise LabError('worktree has uncommitted or untracked changes; export refused')
    def _reconcile_locked(self,s):
        if s['status'] not in ('provisioning','running','stopped'): return s
        prior=s['status']
        try:
            info=self._inspect('container',s['container'],s['name'])
            running=bool(info.get('State',{}).get('Running'))
            s.update(container_id=info.get('Id',s['container']),status='running' if running else 'stopped')
        except LabError as e:
            if not self._missing_resource(e): raise
            s.update(status='stopped' if prior=='stopped' else 'created',container_id=None)
        self.save(s['name'],s); return s
    def reconcile(self,n,dry=False):
        self._valid(n); s=self.read(n)
        if dry: return {'docker':['docker','inspect','--type','container',s['container']]}
        with file_lock(self.root/'.schedule.lock'):
            return self._reconcile_locked(self.read(n))
    def _verify_export(self,s):
        p=Path(s.get('export_path',''))
        expected=Path(s['evidence']).with_name(Path(s['evidence']).name+'.export')
        if p.resolve()!=expected.resolve(): raise LabError('export path does not match experiment evidence location')
        required=('manifest.json','logs.txt','provenance.json','checksums.sha256')
        if not all((p/x).is_file() for x in required): raise LabError('complete evidence export is required')
        lines=(p/'checksums.sha256').read_text().splitlines()
        if not lines: raise LabError('evidence checksum list is empty')
        for line in lines:
            try: expected,rel=line.split('  ',1)
            except ValueError: raise LabError('invalid evidence checksum list')
            target=(p/rel).resolve()
            if not within(target,p) or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=expected:
                raise LabError(f'evidence checksum verification failed: {rel}')
    def cleanup(self,n,dry=False):
        self._valid(n); s=self.read(n)
        if dry:return {'remove':[s['container'],s['volume'],s['network'],s['worktree']]}
        with file_lock(self.root/'.schedule.lock'):
            s=self.read(n); self._validate_external(s)
            if s['status']=='running' or s['status']=='provisioning': raise LabError('stop/reconcile experiment before cleanup')
            if not s.get('exported'): raise LabError('cleanup refused: complete evidence export is required')
            self._verify_export(s)
            self._verify_revision(s)
            self._verify_clean_worktree(s)
            # Inspect must succeed and owner labels must match. Never treat inspection errors as absence.
            for kind,key,remove in (('container','container',['rm']),('volume','volume',['volume','rm']),('network','network',['network','rm'])):
                try: self._inspect(kind,s[key],n)
                except LabError as e:
                    if self._missing_resource(e): continue
                    raise
                self._docker([*remove,s[key]])
            self.run(['git','-C',s['manifest']['repo'],'worktree','remove',s['worktree']])
            s['status']='cleaned'; s['cleaned']=time.time(); self.save(n,s); return s

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--root',default='.lab-state'); sub=p.add_subparsers(dest='op',required=True)
    c=sub.add_parser('create'); c.add_argument('manifest'); c.add_argument('--dry-run',action='store_true')
    for op in ('start','inspect','stop','reconcile','export','cleanup'):
        q=sub.add_parser(op); q.add_argument('experiment'); q.add_argument('--dry-run',action='store_true')
    a=p.parse_args(argv); lab=Lab(a.root)
    try:
        result=lab.create(a.manifest,a.dry_run) if a.op=='create' else getattr(lab,a.op)(a.experiment,a.dry_run)
        print(json.dumps(result,indent=2,default=str)); return 0
    except (LabError,OSError,ValueError) as e: print(f'lab: {e}',file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
