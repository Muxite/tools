"""Current-code verification. Creates only temporary capsule files."""
import json, os, pathlib, shutil, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parents[3]/'Designs/CC and Strata delivery/CC Protocols/reference'))
from ccv2 import Host, file_sha

with tempfile.TemporaryDirectory() as temp:
    root=pathlib.Path(temp)
    a,b,bundle=(root/n for n in ('a','b','bundle'))
    for directory in (a,b,bundle): directory.mkdir()
    for directory in (a,b): shutil.copyfile(sys.executable,directory/'reviewpython.exe')
    with (b/'reviewpython.exe').open('ab') as stream: stream.write(b'changed-executable-overlay')
    declaration={'cc':'2','id':'review.path','version':'1.0.0',
        'bindings':{'default':{'kind':'native','command':['reviewpython.exe','-c','print(\'{"outcome":"ok","outputs":{}}\')']}},
        'capabilities':{'run':{'does':'Emit empty success'}}}
    (bundle/'cc.yaml').write_text(json.dumps(declaration))
    old_path=os.environ['PATH']
    os.environ['PATH']=str(a)+os.pathsep+old_path
    host=Host(root/'store'); release=host.seal(bundle)
    manifest=json.loads((host.store/'releases'/release/'manifest.json').read_text())
    os.environ['PATH']=str(b)+os.pathsep+old_path
    os.environ['PYTHONHOME']=sys.prefix
    receipt=host.call(release,'run',{},key='path-change')
    print(json.dumps({'sealed_executable':manifest['executables']['default'],
        'current_resolution':shutil.which('reviewpython.exe'),
        'current_resolution_sha256':file_sha(b/'reviewpython.exe'),
        'receipt_state':receipt['state'],'receipt_reason':receipt['reason'],
        'receipt_command':receipt['provenance']['command']},indent=2))
