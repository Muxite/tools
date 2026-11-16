import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from remote import main,find_job,ROOT
checks={}
for rid,expected in [('transport-finish-001','succeeded'),('transport-cancel-001','cancelled'),('transport-timeout-001','timeout')]:
    j=find_job(rid);assert j['state']==expected
    group_live=False
    if j.get('pgid'):
        try:os.killpg(j['pgid'],0);group_live=True
        except ProcessLookupError:pass
    assert not group_live
    checks[rid]={'job_id':j['id'],'state':j['state'],'process_group_absent':True}
request=json.loads((ROOT/'requests/transport-finish-001.json').read_text())
again=main({'operation':'submit','id':'transport-finish-001','request':request})
assert again['id']==checks['transport-finish-001']['job_id']
checks['idempotent_resubmit']=True
for name,a in [('path_escape',{'operation':'stage','path':'../forbidden','data':'','sha256':'0'*64}),('changed_request',{'operation':'submit','id':'transport-finish-001','request':dict(request,timeout_s=99)})]:
    try:main(a)
    except ValueError:checks[name]='rejected'
    else:raise AssertionError(name)
assert 'credential_variable_names": []' in (ROOT/'results/transport-finish-001/output.log').read_text()
checks['probe_credential_environment_empty']=True
(ROOT/'results/transport-review.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks))
