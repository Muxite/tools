"""Replay active v2 request and fixed-field regression checks."""
from pathlib import Path
import json
import re
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'Designs/CC and Strata delivery/CC Protocols'
REFERENCE = DOC / 'reference'
sys.path.insert(0,str(REFERENCE))
from ccv2 import normalize,resolve_request

def main():
    blocks = [json.loads(b) for b in re.findall(r'```json\n(.*?)\n```',(DOC/'02-compiler-and-release.md').read_text(encoding='utf-8'),re.S)]
    requests = [b for b in blocks if isinstance(b,dict) and b.get('format')=='cc-request/2']
    assert requests, 'Missing worked request'
    for request in requests:
        answers = {p:{'kind':'native','command':['{python}','{bundle}/tool.py']} for p in request['open']}
        normalize(resolve_request(request,answers))
    subprocess.run([sys.executable,'-m','unittest','-q','test_ccv2.HostTests.test_request_resolution_and_migration','test_ccv2.HostTests.test_migration_binding_name_collision'],cwd=REFERENCE,check=True)
    print(f'PASS: {len(requests)} embedded v2 request, fixed-field preservation and migration dispatch fixtures.')

if __name__ == '__main__':
    main()
