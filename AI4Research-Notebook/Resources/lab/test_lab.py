import hashlib, json, tempfile, unittest
from pathlib import Path
import os
import subprocess
from lab import Lab, LabError, Runner, load_manifest

REV='0123456789abcdef0123456789abcdef01234567'
IMAGE='example.test/lab@sha256:'+'a'*64

class Fake:
    def __init__(self): self.calls=[]; self.fail_logs=False; self.fail_inspect=False; self.dirty=False; self.resources={}
    def __call__(self,args,**kw):
        args=[str(x) for x in args]; self.calls.append(args)
        if args[:3]==['git','-C',args[2]] and args[1]=='-C':
            if 'rev-parse' in args:return REV
            if 'status' in args:return ' M file.py' if self.dirty else ''
            return ''
        if args[:2]==['docker','logs'] and self.fail_logs: raise LabError('logs unavailable')
        if args[:2]==['docker','cp']:
            Path(args[-1],'sample.txt').write_text('volume evidence'); return ''
        if args[:2]==['docker','inspect']:
            if self.fail_inspect: raise LabError('daemon unavailable')
            kind=args[args.index('--type')+1]; name=args[-1]
            key=f'{kind}:{name}'
            if key not in self.resources: raise LabError(f'No such {kind}: {name}')
            data=self.resources[key]
            return json.dumps([data])
        if args[:2]==['docker','network'] and args[2]=='create' or args[:2]==['docker','volume'] and args[2]=='create':
            kind=args[1]; name=args[-1]; labels={args[i+1].split('=',1)[0]:args[i+1].split('=',1)[1] for i,x in enumerate(args[:-1]) if x=='--label'}
            self.resources[f'{kind}:{name}']={'Labels':labels,'Internal':'--internal' in args}; return name
        if args[:2]==['docker','run']:
            name=args[args.index('--name')+1]
            labels={args[i+1].split('=',1)[0]:args[i+1].split('=',1)[1] for i,x in enumerate(args[:-1]) if x=='--label'}
            self.resources[f'container:{name}']={'Id':'cid','Config':{'Labels':labels,'Env':['SECRET=value']},'State':{'Running':True}}
            return 'cid'
        if args[:2]==['docker','stop']:
            self.resources[f"container:{args[-1]}"]['State']={'Running':False}; return args[-1]
        if args[:2] in (['docker','rm'],['docker','volume'],['docker','network']) and args[1] in ('rm',):
            self.resources.pop(f'{args[1]}:{args[-1]}',None); return ''
        return 'fake-id'

class LabTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name); self.runner=Fake(); self.lab=Lab(self.base/'state',self.runner)
        self.manifest=self.base/'manifest.json'; self.evidence=self.base/'persistent'; self.repo=self.base/'repo'; self.repo.mkdir()
        self.manifest.write_text(json.dumps({'experiment':'trial','repo':str(self.repo),'revision':REV,'image':IMAGE,
            'evidence_root':str(self.evidence),'command':['true'],'limits':{'memory':'1g','cpus':1,'pids':32}}))
    def edit(self,**changes):
        data=json.loads(self.manifest.read_text()); data.update(changes); self.manifest.write_text(json.dumps(data)); return data
    def create(self): return self.lab.create(self.manifest)
    def test_digest_validation_dry_run_and_all_ops_reject_traversal(self):
        self.lab.create(self.manifest,True); self.assertFalse((self.base/'state').exists()); self.assertEqual([],self.runner.calls)
        self.edit(image='example:latest')
        with self.assertRaises(LabError): self.create()
        for method in ('start','inspect','stop','export','cleanup'):
            with self.subTest(method=method),self.assertRaises(LabError): getattr(self.lab,method)('../trial',True)
    def test_relative_paths_are_pinned_to_manifest_directory(self):
        self.edit(repo='repo',evidence_root='persistent')
        result=load_manifest(self.manifest)
        self.assertEqual(str(self.repo.resolve()),result['repo'])
        self.assertEqual(str(self.evidence.resolve()),result['evidence_root'])
    def test_owner_unique_names_and_isolated_lifecycle_export(self):
        s=self.create();
        # Another state root and owner using the same friendly identifier receives distinct names.
        second=Lab(self.base/'state2',Fake()); other=second.create(self.manifest)
        self.assertNotEqual(s['owner'],other['owner']); self.assertNotEqual(s['container'],other['container'])
        started=self.lab.start('trial'); self.assertEqual('running',started['status'])
        args=next(x for x in self.runner.calls if x[:2]==['docker','run'])
        joined=' '.join(args); self.assertIn('readonly',joined); self.assertNotIn('docker.sock',joined)
        self.assertTrue(any(x[:3]==['docker','inspect','--type'] for x in self.runner.calls))
        with self.assertRaises(LabError): self.lab.cleanup('trial')
        self.lab.stop('trial'); out=self.lab.export('trial'); export=Path(out['export_path'])
        self.assertTrue((export/'artifacts'/'volume'/'sample.txt').is_file())
        self.assertTrue((export/'artifacts'/'bind').is_dir())
        lines=(export/'checksums.sha256').read_text().splitlines()
        for line in lines:
            h,rel=line.split('  ',1); self.assertEqual(hashlib.sha256((export/rel).read_bytes()).hexdigest(),h)
        self.assertFalse((export.parent/'trial'/'export').exists())
        self.lab.cleanup('trial'); self.assertEqual('cleaned',self.lab.read('trial')['status'])
    def test_export_failure_and_inspect_failure_never_unlock_cleanup(self):
        self.create(); self.lab.start('trial'); self.lab.stop('trial'); self.runner.fail_logs=True
        with self.assertRaises(LabError): self.lab.export('trial')
        self.assertFalse(self.lab.read('trial').get('exported',False))
        self.runner.fail_logs=False; self.lab.export('trial'); self.runner.fail_inspect=True
        with self.assertRaises(LabError): self.lab.cleanup('trial')
    def test_cleanup_refuses_dirty_worktree_and_detects_export_tampering(self):
        self.create(); self.lab.start('trial'); self.lab.stop('trial'); out=self.lab.export('trial')
        self.runner.dirty=True
        with self.assertRaisesRegex(LabError,'uncommitted'): self.lab.cleanup('trial')
        self.runner.dirty=False
        (Path(out['export_path'])/'logs.txt').write_text('changed')
        with self.assertRaisesRegex(LabError,'checksum'): self.lab.cleanup('trial')
    def test_inspection_redacts_environment_and_commands(self):
        self.create(); self.lab.start('trial')
        value=self.lab.inspect('trial')['docker_inspect']['Config']
        self.assertNotIn('SECRET=value',json.dumps(value)); self.assertEqual(['<redacted>'],value['Env'])
    def test_inspect_fails_closed_on_daemon_error(self):
        self.create(); self.runner.fail_inspect=True
        with self.assertRaisesRegex(LabError,'daemon unavailable'): self.lab.inspect('trial')
    def test_network_is_internal_and_existing_noninternal_network_fails_closed(self):
        state=self.create()
        self.lab._ensure_network(state)
        create=next(x for x in self.runner.calls if x[:3]==['docker','network','create'])
        self.assertIn('--internal',create)
        self.assertTrue(self.runner.resources[f"network:{state['network']}"]['Internal'])
        self.runner.resources[f"network:{state['network']}"]['Internal']=False
        with self.assertRaisesRegex(LabError,'not internal'):
            self.lab._ensure_network(state)
    def test_real_git_runner_commit_output_and_worktree_pin(self):
        repo=self.base/'real-repo'; repo.mkdir()
        subprocess.run(['git','init',str(repo)],check=True,capture_output=True)
        subprocess.run(['git','-C',str(repo),'config','user.name','Lab Test'],check=True)
        subprocess.run(['git','-C',str(repo),'config','user.email','lab@example.invalid'],check=True)
        (repo/'source.txt').write_text('pinned input')
        subprocess.run(['git','-C',str(repo),'add','source.txt'],check=True)
        subprocess.run(['git','-C',str(repo),'commit','-m','seed'],check=True,capture_output=True)
        sha=Runner()(['git','-C',str(repo),'rev-parse','HEAD'])
        self.assertEqual(40,len(sha)); self.assertFalse(sha.endswith('\n'))
        data=json.loads(self.manifest.read_text()); data['repo']=str(repo); data['revision']=sha
        self.manifest.write_text(json.dumps(data))
        actual=Lab(self.base/'real-state',Runner()); s=actual.create(self.manifest)
        self.assertEqual(sha,s['revision']); actual._verify_revision(s)
    def test_provisioning_reconcile_allows_safe_stop_and_export(self):
        self.create(); self.lab.start('trial')
        s=self.lab.read('trial'); s['status']='provisioning'; self.lab.save('trial',s)
        stopped=self.lab.stop('trial')
        self.assertEqual('stopped',stopped['status'])
        out=self.lab.export('trial')
        self.assertTrue(Path(out['export_path'],'checksums.sha256').is_file())
    def test_export_refuses_dirty_worktree_before_artifact_copy(self):
        self.create(); self.lab.start('trial'); self.lab.stop('trial'); self.runner.dirty=True
        with self.assertRaisesRegex(LabError,'export refused'): self.lab.export('trial')
        self.assertFalse(self.lab.read('trial').get('exported',False))
    def test_missing_container_after_provisioning_can_be_stopped_exported(self):
        self.create(); self.lab.start('trial')
        s=self.lab.read('trial'); s['status']='provisioning'; self.lab.save('trial',s)
        self.runner.resources.pop(f"container:{s['container']}")
        self.assertEqual('stopped',self.lab.stop('trial')['status'])
        self.assertTrue(self.lab.export('trial')['exported'])
    def test_export_rejects_symlink_without_following_target(self):
        if not hasattr(os,'symlink'):
            self.skipTest('symlink creation is unavailable on this platform')
        self.create(); self.lab.start('trial'); self.lab.stop('trial')
        outside=self.base/'outside-secret.txt'; outside.write_text('must not be copied')
        link=Path(self.lab.read('trial')['evidence'])/'escape.txt'
        try: link.symlink_to(outside)
        except (OSError,NotImplementedError) as e: self.skipTest(f'platform does not permit symlink creation: {e}')
        with self.assertRaisesRegex(LabError,'symlink'): self.lab.export('trial')
        self.assertFalse(self.lab.read('trial').get('exported',False))
    def test_exclusive_schedule_conflict_and_one_shot(self):
        self.create(); self.lab.start('trial')
        data=self.edit(experiment='second',scheduling={'exclusive':True})
        other_manifest=self.base/'second.json'; other_manifest.write_text(json.dumps(data))
        self.lab.create(other_manifest)
        with self.assertRaisesRegex(LabError,'exclusive scheduling conflict'): self.lab.start('second')
        self.lab.stop('trial')
        with self.assertRaisesRegex(LabError,'one-shot'): self.lab.start('trial')
    def test_bad_external_paths_and_positive_limits_refused(self):
        self.edit(evidence_root=str(self.lab.root/'inside'))
        with self.assertRaises(LabError): self.create()
        self.edit(evidence_root=str(self.evidence),limits={'memory':'1g','cpus':0,'pids':32})
        with self.assertRaises(LabError): self.create()

if __name__=='__main__': unittest.main()
