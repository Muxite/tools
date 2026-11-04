"""Read-only review probes; all capsule/store outputs are temporary."""
import copy, json, pathlib, sys, tempfile
from unittest.mock import patch

REF = pathlib.Path(__file__).parents[3] / 'Designs/CC and Strata delivery/CC Protocols/reference'
sys.path.insert(0, str(REF))
from ccv2 import Host, normalize
from mcp_server import tool_schema

evidence = {}
with tempfile.TemporaryDirectory() as temp:
    root = pathlib.Path(temp)
    bundle = root / 'bundle'; bundle.mkdir()
    host = Host(root / 'store')
    base = {'cc':'2','id':'review.example','version':'1.0.0',
            'bindings':{'default':{'kind':'native','command':['{python}','{bundle}/tool.py']}},
            'capabilities':{'run':{'does':'Return a JSON value.', 'gives':{'value':'json'}}}}
    def seal(decl, source):
        (bundle/'cc.yaml').write_text(json.dumps(decl), encoding='utf-8')
        (bundle/'tool.py').write_text(source, encoding='utf-8')
        return host.seal(bundle)
    d = copy.deepcopy(base)
    d['capabilities']['run']['takes'] = {'options': {'kind':'json','schema':True}}
    normalized = normalize(d)
    try: tool_schema(normalized['capabilities']['run'], normalized['defs'])
    except Exception as e: evidence['boolean_schema'] = {'normalizes':True,'exception':repr(e)}
    release = seal(base, "print('{\"outcome\":\"partial\",\"reason\":\"Only first 10 of 100 pages scanned\",\"outputs\":{\"value\":10}}')")
    r = host.call(release,'run',{},key='partial')
    evidence['partial_reason'] = r
    outside = root/'external.py'
    outside.write_text("print('{\"outcome\":\"ok\",\"outputs\":{\"value\":1}}')")
    d = copy.deepcopy(base); d['bindings']['default']['command']=['{python}',str(outside)]
    release = seal(d, '# unused bundled file')
    a = host.call(release,'run',{},key='external1')
    outside.write_text("print('{\"outcome\":\"ok\",\"outputs\":{\"value\":2}}')")
    b = host.call(release,'run',{},key='external2')
    evidence['external_source']={'release':release,'first':a,'second':b}
    d=copy.deepcopy(base); d['bindings']['default']={'kind':'image','image':'sha256:'+'a'*64,'command':['python','{bundle}/tool.py']};d['capabilities']['run']['changes']=['model.invoke']
    release=seal(d,'# image command mocked to inspect adapter construction')
    commands=[]
    def fake_run(command,**kwargs):
        commands.append(command)
        return type('Completed',(),{'stdout':b'{"outcome":"ok","outputs":{"value":1}}','stderr':b'','returncode':0})()
    with patch('ccv2.subprocess.run', fake_run):
        r=host.call(release,'run',{},key='image-network',grants=['model.invoke'])
    evidence['model_network']={'command':commands[0],'receipt':r,'note':'Adapter construction only; no Docker execution claimed'}
    workspace=root/'workspace';workspace.mkdir(); (workspace/'data').write_text('x')
    host.resources={'work':{'kind':'workspace','path':str(workspace)}}
    d=copy.deepcopy(base);d['bindings']['default']={'kind':'jiuwenswarm','agent':'coder'}
    d['capabilities']['run'].update(takes={'workspace':'handle'},changes=['workspace.read','workspace.write'])
    import ctypes
    kernel = ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
    kernel.CreateFileW.restype=ctypes.c_void_p
    locks=[]
    def delegate(packet,context):
        # A legitimate Windows process can keep a newly produced file exclusively open.
        handle=kernel.CreateFileW(str(workspace/'data'),0x80000000,0,None,3,0,None)
        assert handle not in (None,ctypes.c_void_p(-1).value),ctypes.get_last_error()
        locks.append(handle)
        return {'outcome':'ok','outputs':{'value':1}}
    host.delegates={'coder':delegate}
    release=seal(d,'# unused')
    try:
        r=host.call(release,'run',{'workspace':'work'},key='workspace-replace',grants=['workspace.read','workspace.write'])
        evidence['workspace_finally']={'returned':r,'status':host.status('workspace-replace')}
    except Exception as e:
        evidence['workspace_finally']={'exception':repr(e),'status':host.status('workspace-replace')}
    finally:
        kernel.CloseHandle.argtypes=[ctypes.c_void_p]
        for handle in locks: kernel.CloseHandle(handle)
print(json.dumps(evidence, indent=2))
