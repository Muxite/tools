"""Validate the current portable reading set, schemas, examples and local links."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse
import yaml
from ccv2 import UniqueLoader, normalize, resolve_request
from schema_tools import validate

ROOT = Path(__file__).resolve().parents[1]
MAINS = ['README.md','FORMAT.md','USAGE.md','EXAMPLES.md','IMPLEMENTATION.md']


def check():
    counts = {'embedded':0, 'packages':0, 'messages':0}
    completed=json.loads((ROOT/'schemas/cc.schema.json').read_bytes())
    request_schema=json.loads((ROOT/'schemas/request.schema.json').read_bytes())
    def partial(value):
        if isinstance(value,list): return [partial(x) for x in value]
        if not isinstance(value,dict): return value
        return {('anyOf' if k=='oneOf' else k):partial(v) for k,v in value.items() if k not in {'required','allOf','anyOf','minProperties'}}
    assert request_schema['$defs']==partial(completed['$defs']), 'Request definitions drifted from completed contract'

    documents = [ROOT/n for n in MAINS]+list((ROOT/'profiles').glob('*.md'))
    for path in documents:
        text = path.read_text(encoding='utf-8')
        for raw in re.findall(r'\]\(([^)]+)\)', text):
            if urlparse(raw).scheme: continue
            target = unquote(raw.split('#')[0].strip('<>'))
            if target and not (path.parent/target).exists():
                raise AssertionError('Broken local link: '+str(path)+': '+target)
        for language, block in re.findall(r'```(json|yaml)\r?\n(.*?)\r?\n```',text,re.S):
            value = json.loads(block) if language=='json' else yaml.load(block, Loader=UniqueLoader)
            if isinstance(value,dict) and value.get('cc')=='2':
                validate('cc.schema.json',value);normalize(value);counts['embedded']+=1
            elif isinstance(value,dict) and value.get('format')=='cc-request/2':
                validate('request.schema.json',value);counts['embedded']+=1
    for path in (ROOT/'examples').rglob('*.yaml'):
        value = yaml.load(path.read_text(encoding='utf-8'),Loader=UniqueLoader)
        validate('cc.schema.json',value);normalize(value);counts['packages']+=1
    request = json.loads((ROOT/'examples/trim-request.json').read_bytes())
    validate('request.schema.json',request)
    result = resolve_request(request,json.loads((ROOT/'examples/trim-answers.json').read_bytes()))
    validate('cc.schema.json',result)
    for path in (ROOT/'examples/messages').glob('*.json'):
        value=json.loads(path.read_bytes())
        validate('messages.schema.json',value,path.stem);counts['messages']+=1
        if path.stem=='artifact':
            import hashlib
            assert hashlib.sha256((path.parent/value['uri']).read_bytes()).hexdigest()==value['sha256']
    print(json.dumps({'status':'passed',**counts,'scope':'Schema/semantic fixtures and current local links; no image, model or hardware claim'}))
    return counts


if __name__=='__main__': check()
