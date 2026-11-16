import json,os,sys,time
from pathlib import Path
print(json.dumps({'pid':os.getpid(),'mode':sys.argv[1],'credential_variable_names':[k for k in os.environ if any(s in k.upper() for s in ('TOKEN','SECRET','PASSWORD','API_KEY'))]}),flush=True)
if sys.argv[1]=='finish': time.sleep(3)
else: time.sleep(90)
Path(os.environ['FACTORY_RESULT_DIR'],'finished.json').write_text(json.dumps({'finished':True,'pid':os.getpid()}))
