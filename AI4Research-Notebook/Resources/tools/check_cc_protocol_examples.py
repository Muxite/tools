"""Validate active v2 documents/packages and replay local reference tests.
The v1 checker is preserved in review-batches/2026-11-04-cc-v2.
"""
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse, unquote
import yaml
VAULT = Path(__file__).resolve().parents[2]
DOC = VAULT / 'Designs/CC and Strata delivery/CC Protocols'
REFERENCE = DOC / 'reference'
sys.path.insert(0, str(REFERENCE))
from ccv2 import UniqueLoader, load, normalize

def main():
    declarations = 0
    for path in DOC.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if not urlparse(target).scheme:
                target = unquote(target.split('#')[0].strip('<>'))
                if target and not (path.parent / target).exists():
                    raise AssertionError(f'Broken local link: {path}: {target}')
        for language, block in re.findall(r'```(json|yaml)\n(.*?)\n```', text, re.S):
            data = json.loads(block) if language == 'json' else yaml.load(block, Loader=UniqueLoader)
            if isinstance(data, dict) and data.get('cc') == '2' and {'id','version'} <= set(data) and any(k in data for k in ('capabilities','materials','applications')):
                normalize(data); declarations += 1
    packages = 0
    for path in (REFERENCE / 'examples').rglob('*.yaml'):
        if path.name in {'cc.yaml','image.yaml'}:
            load(path); packages += 1
    subprocess.run([sys.executable,'-m','unittest','-q','test_ccv2','test_products','test_source_build','test_unified'],cwd=REFERENCE,check=True)
    print(f'PASS: {declarations} complete embedded v2 declarations, {packages} package declarations, local links and host regression suite.')
    print('SCOPE: structural/local replay; upstream client/task and image execution have separate reports.')

if __name__ == '__main__':
    main()
