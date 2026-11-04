"""Independent lifecycle probes; all packages and processes are temporary."""
import json, pathlib, shutil, sys, tempfile, time
import psutil
ROOT=pathlib.Path(__file__).parents[4]
REF=ROOT/'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference'
sys.path.insert(0,str(REF))
from ccv2 import Host,CCError,file_sha

evidence={}
with tempfile.TemporaryDirectory() as temp:
    root=pathlib.Path(temp)
    host=Host(root/'store',session_grants=['process.exec','network.listen'])
    bundle=root/'http';shutil.copytree(REF/'examples/http_product',bundle)
    import yaml
    declaration=yaml.safe_load((bundle/'cc.yaml').read_text())
    declaration['applications']['api']['takes']={'data':'artifact'}
    (bundle/'cc.yaml').write_text(yaml.safe_dump(declaration))
    release=host.prepare(bundle)
    source=root/'data';source.write_text('input')
    values={'data':{'uri':source.as_uri(),'sha256':file_sha(source)}}
    first=host.start(release,'api',values,key='replay')
    try:
        source.unlink()
        try:
            retry=host.start(release,'api',values,key='replay')
            direct=Host(host.store).lookup_instance('replay')
            import subprocess
            cli=subprocess.run([sys.executable,str(REF/'ccv2.py'),'instance-key','replay','--store',str(host.store)],capture_output=True,text=True)
            evidence['same_key_missing_artifact']={'same_id':retry['id']==first['id'],'lookup_without_grants_same_id':direct['id']==first['id'],'cli_key_lookup_same_id':cli.returncode==0 and json.loads(cli.stdout)['id']==first['id'],'state':retry['state']}
        except CCError as error:
            evidence['same_key_missing_artifact']={'first_id':first['id'],'first_state':first['state'],'retry_error':error.record(),'instance_state':host.inspect_instance(first['id'])['state']}
    finally:host.stop(first['id'])
    launcher=root/'launcher';launcher.mkdir()
    (launcher/'launch.py').write_text("import subprocess,sys,time\np=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\nprint(p.pid,flush=True)\ntime.sleep(0.3)\n")
    declaration={'cc':'2','id':'review.launcher','version':'1.0.0','bindings':{'default':{'kind':'native','command':['{python}','{bundle}/launch.py']}},'applications':{'worker':{'does':'Launch a background worker','changes':['process.exec']}}}
    (launcher/'cc.yaml').write_text(json.dumps(declaration))
    release=host.prepare(launcher)
    started=host.start(release,'worker',key='launcher')
    child=None
    try:
        deadline=time.monotonic()+4
        while time.monotonic()<deadline:
            current=host.inspect_instance(started['id'])
            if current['state']=='exited':break
            time.sleep(.05)
        child=int(pathlib.Path(started['logs']['stdout']).read_text().strip())
        try:
            stopped=host.stop(started['id'])
            evidence['exited_parent_live_child']={'unexpected_stop_state':stopped['state']}
        except CCError as error:
            evidence['exited_parent_live_child']={'observed_before_stop':current['state'],'stop_error':error.record(),'durable_state':host.lookup_instance('launcher')['state'],'child_alive_after_stop':psutil.Process(child).is_running()}
    finally:
        if child and psutil.pid_exists(child):
            p=psutil.Process(child);p.terminate();p.wait(3)
            host.reconcile_instance(started['id'],stopped=True,note='Independent probe terminated identified child and confirmed wait')
    literal=root/'literal';literal.mkdir()
    (literal/'worker.py').write_text('import time; time.sleep(60)')
    declaration={'cc':'2','id':'review.literal','version':'1.0.0','bindings':{'default':{'kind':'native','command':['{python}','{bundle}/worker.py','{input.prompt}']}},'applications':{'worker':{'does':'Use a literal prompt argument','takes':{'prompt':'text'},'changes':['process.exec']}}}
    (literal/'cc.yaml').write_text(json.dumps(declaration))
    release=host.prepare(literal)
    result=host.start(release,'worker',{'prompt':'Explain the token {input.NAME} literally'},key='literal')
    evidence['literal_placeholder']={'state':result['state'],'literal_preserved':result.get('provenance',{}).get('command',[])[-1]=='Explain the token {input.NAME} literally','diagnostics':result['diagnostics']}
    if result['identity']:host.stop(result['id'])
print(json.dumps(evidence,indent=2))
