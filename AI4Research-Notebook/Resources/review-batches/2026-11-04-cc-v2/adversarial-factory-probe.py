import sys, json, pickle
from pathlib import Path
root=Path.cwd()
batch=root/'AI4Research-Notebook/Resources/review-batches/2026-11-04-cc-v2'
ref=root/'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference'
sys.path.insert(0,str(ref))
from ccv2 import Host, normalize, resolve_request, migrate_v1, CCError
import numpy as np
from mapie.regression import SplitConformalRegressor
from sklearn.linear_model import LinearRegression
out={}
host=Host(batch/'factory-probe-store')
release=host.seal(ref/'examples/mapie')
# Supply a valid but incompatible trusted model from a different nominal level.
x=np.arange(30).reshape(-1,1); y=2*x[:,0]+np.sin(x[:,0])
model=SplitConformalRegressor(estimator=LinearRegression(),confidence_level=.5,prefit=False)
model.fit(x[:15], y[:15]); model.conformalize(x[15:25],y[15:25])
p=batch/'trusted-50pct-model.pkl'
with p.open('wb') as f: pickle.dump(model,f)
modelref=host.put_artifact(p)
pred=host.call(release,'predict_intervals',{'model':modelref,'data':{'x':x[25:].tolist()}},key='factory-model-50pct-v1')
out['wrong_confidence_model']={'model_confidence_level':.5,'receipt':pred}
if pred['state']=='succeeded': out['wrong_confidence_model']['interval_content']=json.loads(host.artifact_path(pred['outputs']['intervals']).read_text())
# Structurally valid artifact with nonsensical scientific intervals.
p=batch/'inverted-intervals.json';p.write_text(json.dumps({'lower':[10,20], 'upper':[0,1]}))
out['inverted_intervals']=host.call(release,'evaluate',{'intervals':host.put_artifact(p),'labels':[5,15]},key='factory-inverted-v1')
p=batch/'broadcast-intervals.json';p.write_text(json.dumps({'lower':[0,0], 'upper':[[1],[10]]}))
out['broadcast_intervals']=host.call(release,'evaluate',{'intervals':host.put_artifact(p),'labels':[5,5]},key='factory-broadcast-v1')
# Negative valid scientific result stays successful execution, independent failed assessment.
p=batch/'normal-intervals.json';p.write_text(json.dumps({'lower':[0,0], 'upper':[1,1]}))
out['valid_negative']=host.call(release,'evaluate',{'intervals':host.put_artifact(p),'labels':[5,5]},key='factory-negative-v1')
# Missing script is not discovered when sealing.
b=batch/'missing-method';b.mkdir(exist_ok=True)
(b/'cc.yaml').write_text("cc: '2'\nid: missing.method\nversion: 1.0.0\nbindings:\n  default:\n    kind: native\n    command: ['{python}', '{bundle}/absent.py']\ncapabilities:\n  run:\n    does: Run missing paper source.\n")
r=host.seal(b)
out['missing_code']={'release':r,'call':host.call(r,'run',{},key='factory-missing-v1')}
# Fixed request action is preserved; implementation semantics remain unverified by design.
desired={'cc':'2','id':'paper.method','version':'1.0.0','bindings':{},'capabilities':{'run':{'does':'Use paper method A, no substitutes.','takes':{'data':'json'},'gives':{'score':'json'}}}}
req={'format':'cc-request/2','kind':'request','id':'fixed-method-a','desired':desired,'open':{'/bindings/default':{'owner':'implementer','question':'Supply binding'}}}
out['request_method_mismatch']={'request':req,'resolved':resolve_request(req,{'/bindings/default':{'kind':'native','command':['{python}','-c','print(42)']}})}
# Compatibility declarations reject unknown fields; generic GPU resource alone cannot express GB10 eligibility.
try:
 d=json.loads(json.dumps(out['request_method_mismatch']['resolved']));d['bindings']['default']['platform']='linux/arm64';normalize(d)
except CCError as e: out['arm_requirement']=e.record()
# Existing valid v1 multioperation case with first capability named default.
old={'cc':'1','id':'paper.ops','version':'1.0.0','carrier':'repo@sha256:'+'a'*64,'operations':{'default':{'does':'first','run':'/first','gives':{'x':'integer'}},'later':{'does':'second','run':'/later','gives':{'x':'integer'}}}}
out['migration']=migrate_v1(old)
# Prove primitive null and mutable carrier migrate behavior too.
old={'cc':'1','id':'paper.mutable','version':'1.0.0','carrier':'repo:latest','does':'x','run':'/tool','gives':{'x':'integer'}}
out['invalid_v1_migration']=migrate_v1(old)
try: normalize(out['invalid_v1_migration']['declaration'])
except CCError as e: out['invalid_v1_normalization']=e.record()
(batch/'adversarial-factory-evidence.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:({'state':v['state'],'outputs':v['outputs']} if isinstance(v,dict) and 'state' in v else str(v)[:250]) for k,v in out.items()},indent=2))
