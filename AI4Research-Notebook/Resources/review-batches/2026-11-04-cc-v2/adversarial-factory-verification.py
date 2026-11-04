import json,sys,hashlib
from pathlib import Path
r=Path.cwd();batch=r/'AI4Research-Notebook/Resources/review-batches/2026-11-04-cc-v2';ref=r/'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference';sys.path.insert(0,str(ref))
from ccv2 import Host,migrate_v1,normalize,CCError
old=json.loads((batch/'adversarial-factory-evidence.json').read_text());out={'scope':'Independent read-only production-source verification; local probe records only','finding_resolution':{}}
collision=migrate_v1(old['migration_collision']['original']);d=normalize(collision['declaration']);dispatch={k:d['bindings'][v['using']]['command'] for k,v in d['capabilities'].items()}
assert dispatch=={'fit':['/fit'],'default':['/predict']};out['finding_resolution']['FACTORY-01']={'status':'resolved','dispatch':dispatch}
x=migrate_v1({'cc':'1','id':'paper.mutable','version':'1.0.0','carrier':'repo:latest','does':'x','run':'/tool','gives':{'x':'integer'}});assert x['status']=='needs_review' and x['declaration'] is None;out['finding_resolution']['FACTORY-05']={'status':'resolved','result':x}
h=Host(batch/'factory-verification-store')
try:h.seal(batch/'missing-method');raise AssertionError('accepted missing script')
except CCError as e:assert e.code=='MISSING_IMPLEMENTATION';out['finding_resolution']['FACTORY-04']={'status':'resolved','diagnostic':e.record()}
release=h.seal(ref/'examples/mapie');out['release']=release
p=h.call(release,'predict_intervals',{'model':h.put_artifact(batch/'trusted-50pct-model.pkl'),'data':{'x':[[25],[26],[27],[28],[29]]}})
assert p['state']=='succeeded';content=json.loads(h.artifact_path(p['outputs']['intervals']).read_text());assert content['confidence_level']==.5
out['finding_resolution']['FACTORY-02']={'status':'resolved','receipt':p,'observed_confidence':content['confidence_level']}
cases={'broadcast':({'lower':[0,0],'upper':[[1],[10]]},[5,5]),'inverted':({'lower':[10,20],'upper':[0,1]},[5,15]),'empty':({'lower':[],'upper':[]},[]),'nonfinite':({'lower':[0],'upper':[float('inf')]},[.5]),'mismatch':({'lower':[0,0],'upper':[1]},[.5,.5]),'labels_2d':({'lower':[0,0],'upper':[1,1]},[[.5],[.5]])}
result={}
for name,(values,labels) in cases.items():
 path=batch/('verify-'+name+'.json');path.write_text(json.dumps(values));receipt=h.call(release,'evaluate',{'intervals':h.put_artifact(path),'labels':labels});assert receipt['state']=='failed' and receipt['reason']=='MAPIE_ERROR',(name,receipt);result[name]=receipt
out['finding_resolution']['FACTORY-03']={'status':'resolved','rejecting_cases':result}
lock=ref/'examples/mapie/requirements-lock.txt';assert lock.is_file();decl,bundle=h.release(release);assert decl['bindings']['default']['lock']=='requirements-lock.txt';assert (bundle/'requirements-lock.txt').read_bytes()==lock.read_bytes();out['lock']={'status':'bundled_and_hashed','sha256':hashlib.sha256(lock.read_bytes()).hexdigest(),'enforcement_scope':'Sealed lock material; not an automatic package installer or environment admission checker.'}
reports={}
for name in ['mapie-report','mapie-replays-report','mcp-report','native-report','factory-lab-report']:
 data=json.loads((ref/'integrations'/(name+'.json')).read_text());reports[name]={'sha256':hashlib.sha256((ref/'integrations'/(name+'.json')).read_bytes()).hexdigest(),'top_level_keys':list(data)}
out['current_integration_reports']=reports
m=json.loads((ref/'integrations/mapie-report.json').read_text());assert m['fit']['outputs']['model']==m['predict']['provenance']['inputs']['model'];assert m['predict']['outputs']['intervals']==m['evaluate']['provenance']['inputs']['intervals'];out['mapie_lineage']={'model_edge':True,'interval_edge':True,'release_matches_verified':m['release']==release,'metrics':m['evaluate']['outputs']}
f=json.loads((ref/'integrations/factory-lab-report.json').read_text());out['factory_lab']={'scope':f['scope'],'inspection_state':f['inspection_receipt']['state'],'entrypoint_executed':f['inspection_receipt']['outputs']['inspection']['entrypoint_executed'],'inference_measured':f['inspection_receipt']['outputs']['inspection']['inference_measured'],'other_keys':list(f)}
out['unresolved_high_priority']=[]
(batch/'adversarial-factory-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'resolutions':{k:v['status'] for k,v in out['finding_resolution'].items()},'release':release,'lineage':out['mapie_lineage'],'factory_lab':out['factory_lab'],'unresolved_high_priority':[]},indent=2))
