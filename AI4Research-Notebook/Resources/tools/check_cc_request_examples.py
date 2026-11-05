from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]/'Designs/CC Protocols'
sys.path.insert(0,str(ROOT/'reference'))
from ccv2 import resolve_request
from schema_tools import validate
request=json.loads((ROOT/'examples/trim-request.json').read_bytes())
answers=json.loads((ROOT/'examples/trim-answers.json').read_bytes())
validate('request.schema.json',request)
validate('cc.schema.json',resolve_request(request,answers))
print('PASS: current request schema, exact choices and completed contract')
