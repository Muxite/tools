"""Validate this portable documentation graph; no runtime acceptance implied."""
from pathlib import Path
from urllib.parse import unquote, urlparse
import hashlib
import json
import re

REQUIRED = {'README.md', 'implementation-status.md', 'contracts-and-boundaries.md',
            'vm-labs.md', 'container-capsules.md', 'local-factories.md', 'validation.md'}
OWNERS = {'durable_lab', 'container_carrier', 'local_factory', 'storage_and_models',
          'independent_assurance', 'restricted_spark_and_m1_separation'}


def validate(folder, *, manifest=False):
    folder = Path(folder).resolve()
    for name in REQUIRED | {'source-map.json'}:
        assert (folder / name).is_file(), 'Missing required file: ' + name
    source = json.loads((folder / 'source-map.json').read_text('utf-8'))
    mapping = source['responsibility_map']
    assert set(mapping) == OWNERS, 'Missing/unknown responsibility mapping'
    for files in mapping.values():
        assert files and len(files) == len(set(files)), 'Empty/duplicate ownership coverage'
        assert set(files) <= REQUIRED, 'Ownership refers outside required reading graph'
    links = 0
    for name in REQUIRED:
        raw = (folder / name).read_text('utf-8')
        for key in ('id', 'status', 'source', 'last_reviewed', 'next_action'):
            assert re.search(r'^' + key + r':\s*\S', raw, re.M), 'Missing metadata: ' + name
        text = re.sub(r'```.*?```', '', raw, flags=re.S)
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if urlparse(target).scheme or target.startswith('#'):
                continue
            target = unquote(target.split('#')[0])
            resolved = (folder / target).resolve()
            assert resolved.is_relative_to(folder), 'Required reading escapes package'
            assert resolved.exists(), 'Broken package link: ' + target
            links += 1
        if '```mermaid' in raw:
            diagrams = re.findall(r'```mermaid\n(.*?)```', raw, flags=re.S)
            assert len(diagrams) == 1
            source_file = folder / 'diagrams' / (Path(name).stem + '.mmd')
            assert source_file.read_text('utf-8') == diagrams[0], 'Stale diagram source'
            for suffix in ('.svg', '.png'):
                assert source_file.with_suffix(suffix).stat().st_size > 0, 'Missing diagram rendering'
    if manifest:
        rows = json.loads((folder / 'package-manifest.json').read_text('utf-8'))['files']
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*')
                  if p.is_file() and p.name != 'package-manifest.json'}
        assert set(rows) == actual, 'Manifest does not cover the exact package'
        for name, expected in rows.items():
            target = (folder / name).resolve()
            assert target.is_relative_to(folder), 'Manifest path escape'
            assert hashlib.sha256(target.read_bytes()).hexdigest() == expected, 'Stale package hash'
    return {'required_documents': len(REQUIRED), 'local_links': links,
            'responsibility_groups': len(OWNERS), 'rendered_diagrams': 4}


if __name__ == '__main__':
    import sys
    print(json.dumps(validate(sys.argv[1], manifest='--manifest' in sys.argv), indent=2))
