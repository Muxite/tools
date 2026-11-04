"""Focused portable-boundary probes. Runtime scratch stays on D:."""
import json,pathlib,shutil,sys,tempfile,threading
import rfc8785
ROOT=pathlib.Path(__file__).parents[4]
REF=ROOT/'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference'
sys.path.insert(0,str(REF))
from ccv2 import Host,normalize,resolve_request,sha
from schema_tools import validate
scratch=pathlib.Path('D:/cc-focused-protocol-scratch');scratch.mkdir(exist_ok=True)
evidence={}
with tempfile.TemporaryDirectory(dir=scratch) as temp:
    root=pathlib.Path(temp);bundle=root/'bundle';bundle.mkdir()
    declaration={'cc':'2','id':'review.example','version':'1.0.0','bindings':{'worker':{'kind':'native','command':['{python}','{bundle}/tool.py']}},'capabilities':{'run':{'does':'Return value','using':'worker','gives':{'value':'json'}}}}
    (bundle/'cc.yaml').write_text(json.dumps(declaration))
    (bundle/'tool.py').write_text("print('{\"outcome\":\"ok\",\"outputs\":{\"value\":1}}')")
    host=Host(root/'store');original=host.prepare(bundle)
    source=host.store/'releases'/original
    manifest=json.loads((source/'manifest.json').read_bytes())
    manifest['files']=[r for r in manifest['files'] if r['path']!='tool.py']
    imported=sha(rfc8785.dumps(manifest));target=host.store/'releases'/imported
    shutil.copytree(source,target)
    (target/'manifest.json').write_bytes(rfc8785.dumps(manifest))
    first=host.call(imported,'run',{},key='import-one')
    (target/'bundle/tool.py').write_text("print('{\"outcome\":\"ok\",\"outputs\":{\"value\":2}}')")
    second=host.call(imported,'run',{},key='import-two')
    evidence['unindexed_implementation']={'release':imported,'indexed_paths':[r['path'] for r in manifest['files']],'first_state':first['state'],'first_reason':first['reason'],'first_outputs':first['outputs'],'second_state':second['state'],'second_reason':second['reason'],'second_outputs':second['outputs']}
    request={'format':'cc-request/2','id':'review.request','desired':{'cc':'2','id':'review.requested','version':'1.0.0','bindings':{'default':{}},'capabilities':{'run':{'does':'Run'}}},'open':{'/bindings/default/kind':{'question':'Choose runtime'},'/bindings/default/command':{'question':'Supply argv'}}}
    try:
        resolved=resolve_request(request,{'/bindings/default/kind':'native','/bindings/default/command':['{python}','{bundle}/tool.py']})
        evidence['partial_binding_request']={'resolved':True}
    except Exception as error:evidence['partial_binding_request']={'resolved':False,'exception':type(error).__name__,'message':str(error)[:450]}
    started,finish=threading.Event(),threading.Event()
    delegate=root/'delegate';delegate.mkdir()
    (delegate/'cc.yaml').write_text(json.dumps({'cc':'2','id':'review.delegate','version':'1.0.0','bindings':{'default':{'kind':'delegate','agent':'worker'}},'capabilities':{'run':{'does':'Wait then return'}}}))
    def callback(packet,context):
        started.set();finish.wait(5)
        return {'outcome':'ok','outputs':{}}
    host.delegates={'worker':callback};release=host.prepare(delegate)
    worker=threading.Thread(target=lambda:host.call(release,'run',{},key='pending',checks=['core.complete']))
    worker.start();started.wait(3)
    receipt=host.status('pending')
    try:
        validate('messages.schema.json',receipt,'receipt')
        evidence['running_assessment']={'valid':True,'assessment':receipt['assessment']}
    except Exception as error:evidence['running_assessment']={'valid':False,'assessment':receipt['assessment'],'exception':type(error).__name__,'message':str(error)[:300]}
    finally:finish.set();worker.join(5)
print(json.dumps(evidence,indent=2))
