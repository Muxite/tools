import json,subprocess
from pathlib import Path
rows=[]
for name in ('ssh-factory-container-cancel-001','ssh-factory-container-timeout-001'):
    info=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
    assert info['Config']['Labels']['factory.owner']=='software-factory-spark-20261113'
    assert info['Name']=='/'+name and not info['State']['Running']
    subprocess.run(['docker','rm',info['Id']],check=True)
    rows.append({'name':name,'id':info['Id'],'prior_state':info['State'],'removed_after_failed_v1_cleanup':True})
Path('/home/user2/software-factory-spark-20261113/results/v1-container-cleanup-failure.json').write_text(json.dumps(rows,indent=2))
