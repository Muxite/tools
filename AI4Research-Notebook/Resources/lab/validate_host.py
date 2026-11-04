"""Run an opt-in real Docker smoke campaign using only disposable owned resources.

No model, account, application instance or user repository is executed. Evidence is retained.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import uuid
from lab import Lab, LabError, Runner

VAULT=Path(__file__).resolve().parents[2]

class RecordedRunner(Runner):
    def __init__(self): self.commands=[]
    def __call__(self,args,**kwargs):
        entry={'argv':[str(a) for a in args]}; self.commands.append(entry)
        try:
            result=super().__call__(args,**kwargs)
            entry['output']=result
            return result
        except Exception as error:
            entry['error']=str(error)
            raise

def main():
    run=RecordedRunner()
    campaign=VAULT.parent/'AI4Research-Lab-Validation'/('host-'+uuid.uuid4().hex[:10])
    campaign.mkdir(parents=True,exist_ok=False)
    receipt_dir=VAULT/'Resources/verification/lab-host'; receipt_dir.mkdir(parents=True,exist_ok=True)
    receipt=receipt_dir/(campaign.name+'.json')
    report={'kind':'real Docker synthetic lab smoke, not M1 or CC accuracy evidence',
            'capture_date':'2026-10-21','campaign':str(campaign),'checks':{},'commands':run.commands}
    lab=Lab(campaign/'state',run)
    names=[]
    def expect_denied(key,call):
        try: call()
        except LabError as error:
            report['checks'][key]={'passed':True,'reason':str(error)}
        else: raise AssertionError('Expected refusal: '+key)
    try:
        image=json.loads(run(['docker','image','inspect','alpine:3.22']))[0]
        pin=next(x for x in image['RepoDigests'] if x.startswith('alpine@sha256:'))
        report['image']=pin
        info=json.loads(run(['docker','info','--format','{{json .}}']))
        report['host']={k:info.get(k) for k in ('ServerVersion','OSType','Architecture','NCPU','MemTotal')}
        # Do not retain unrelated daemon information or global container inventories.
        run.commands[-1]['output']=json.dumps(report['host'])
        repo=campaign/'fixture';repo.mkdir()
        run(['git','init',str(repo)])
        run(['git','-C',str(repo),'config','user.name','Notebook Lab Fixture'])
        run(['git','-C',str(repo),'config','user.email','fixture@example.invalid'])
        (repo/'source.txt').write_text('immutable fixture\n',encoding='utf-8')
        run(['git','-C',str(repo),'add','source.txt'])
        run(['git','-C',str(repo),'commit','-m','Synthetic lab fixture'])
        revision=run(['git','-C',str(repo),'rev-parse','HEAD'])
        report['fixture_revision']=revision
        for name,marker,exclusive in [('isolation-a','A',False),('isolation-b','B',False),('exclusive','E',True),('ordinary','O',False)]:
            command=['/bin/sh','-c',
                "printf '%s' '"+marker+"' > /evidence/marker.txt; printf '%s' '"+marker+"' > /workdata/volume-marker.txt; "
                "if (printf bad >> /workspace/source.txt) 2>/dev/null; then printf BAD > /evidence/source-check.txt; else printf READ_ONLY > /evidence/source-check.txt; fi; "
                "test ! -e /var/run/docker.sock && printf NO_SOCKET > /evidence/socket-check.txt; "
                "ip route > /evidence/routes.txt; echo ready; trap 'exit 0' TERM; while :; do sleep 1; done"]
            manifest={'experiment':name,'repo':str(repo),'revision':revision,'image':pin,
                      'evidence_root':str(receipt_dir/campaign.name),'command':command,
                      'limits':{'memory':'64m','cpus':0.25,'pids':32},'scheduling':{'exclusive':exclusive}}
            path=campaign/(name+'.json');path.write_text(json.dumps(manifest),encoding='utf-8')
            lab.create(path);names.append(name)
        a=lab.start('isolation-a');b=lab.start('isolation-b')
        time.sleep(2)
        states=[lab.inspect(n) for n in ('isolation-a','isolation-b')]
        assert all(s['docker_inspect']['State']['Running'] for s in states)
        assert a['network']!=b['network'] and a['volume']!=b['volume'] and a['worktree']!=b['worktree']
        for s in states:
            inspected=s['docker_inspect']; mounts={m['Destination']:m for m in inspected['Mounts']}
            assert not mounts['/workspace']['RW'] and '/var/run/docker.sock' not in mounts
            assert inspected['HostConfig']['Memory']==64*1024*1024
            assert inspected['HostConfig']['PidsLimit']==32
            assert inspected['HostConfig']['NanoCpus']==250000000
            network=json.loads(run(['docker','network','inspect',s['network']]))[0]
            assert network['Internal'] is True
        report['checks']['two_simultaneous_isolated_limited_runs']={'passed':True}
        expect_denied('running_export',lambda:lab.export('isolation-a'))
        expect_denied('cleanup_before_export',lambda:lab.cleanup('isolation-a'))
        expect_denied('exclusive_cannot_overlap',lambda:lab.start('exclusive'))
        # Simulate a coordinator crash after container creation but before state commit.
        state=lab.read('isolation-a'); cid=state['container_id'];state['status']='provisioning';lab.save('isolation-a',state)
        recovered=Lab(campaign/'state',run).start('isolation-a')
        assert recovered['container_id']==cid
        report['checks']['provisioning_recovery_no_replay']={'passed':True,'container_id':cid}
        run(['docker','kill','--signal','KILL',a['container']])
        assert lab.reconcile('isolation-a')['status']=='stopped'
        lab.stop('isolation-b')
        report['checks']['forced_worker_interruption_reconciled']={'passed':True}
        exports={}
        for name,marker in [('isolation-a','A'),('isolation-b','B')]:
            state=lab.export(name); path=Path(state['export_path']);exports[name]=str(path)
            assert (path/'artifacts/bind/marker.txt').read_text()==marker
            assert (path/'artifacts/volume/volume-marker.txt').read_text()==marker
            assert (path/'artifacts/bind/source-check.txt').read_text()=='READ_ONLY'
            assert (path/'artifacts/bind/socket-check.txt').read_text()=='NO_SOCKET'
            assert 'default' not in (path/'artifacts/bind/routes.txt').read_text()
            # Verify cleanup refuses tampered evidence, then restore the exact bytes.
            target=path/'artifacts/bind/marker.txt'; original=target.read_bytes();target.write_bytes(b'tampered')
            expect_denied(name+'_tampered_export',lambda:lab.cleanup(name))
            target.write_bytes(original)
            lab.cleanup(name)
            assert path.exists() and not Path(state['worktree']).exists()
            for kind,key in [('container','container'),('network','network'),('volume','volume')]:
                result=subprocess.run(['docker','inspect','--type',kind,state[key]],capture_output=True)
                assert result.returncode!=0
        report['checks']['export_markers_readonly_no_socket_no_default_route_cleanup_preserves_evidence']={'passed':True}
        report['exports']=exports
        lab.start('exclusive');expect_denied('ordinary_cannot_overlap_exclusive',lambda:lab.start('ordinary'))
        lab.stop('exclusive');lab.export('exclusive');lab.cleanup('exclusive')
        lab.stop('ordinary');lab.export('ordinary');lab.cleanup('ordinary')
        report['result']='passed'
    except Exception as error:
        report['result']='failed';report['error']=repr(error)
    finally:
        report['cleanup']={}
        for name in names:
            try:
                state=lab.read(name)
                if state['status']!='cleaned':
                    lab.stop(name)
                    if not lab.read(name).get('exported'): lab.export(name)
                    lab.cleanup(name)
                report['cleanup'][name]=lab.read(name)['status']
            except Exception as error: report['cleanup'][name]='requires inspection: '+str(error)
        report['lab_source_sha256']=hashlib.sha256((VAULT/'Resources/lab/lab.py').read_bytes()).hexdigest()
        receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'result':report['result'],'receipt':str(receipt),'checks':report['checks'],'cleanup':report['cleanup']},indent=2))
    return report['result']!='passed'

if __name__=='__main__': raise SystemExit(main())
