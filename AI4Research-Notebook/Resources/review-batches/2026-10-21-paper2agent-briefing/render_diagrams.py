"""Render the briefing's three Mermaid sources into presentation assets."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess

VAULT = Path(__file__).resolve().parents[3]
DIAGRAMS = VAULT / 'Designs/Paper2Agent Briefing/diagrams'
CLI = Path('C:/Users/m50066326/AppData/Local/npm-cache/_npx/fa58c8ce4c502b5d/node_modules/@mermaid-js/mermaid-cli/src/cli.js')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def render(source):
    row = {'source': source.name, 'source_sha256': digest(source)}
    for extension in ('svg', 'png'):
        target = source.with_suffix('.' + extension)
        result = subprocess.run(
            ['node', str(CLI), '-i', str(source), '-o', str(target),
             '-c', str(DIAGRAMS / 'mermaid-config.json'), '-b', 'white',
             '--size', '1800', '-s', '1.5'],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode:
            raise RuntimeError(source.name + ': ' + result.stdout + result.stderr)
        row[extension] = target.name
        row[extension + '_sha256'] = digest(target)
    print('Rendered ' + source.stem, flush=True)
    return row

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(render, sorted(DIAGRAMS.glob('*.mmd'))))
    version = subprocess.check_output(['node', str(CLI), '--version'], text=True).strip()
    receipt = {'renderer': 'mermaid-cli ' + version,
               'meaning': 'Proposed architecture, not runtime evidence',
               'config_sha256': digest(DIAGRAMS / 'mermaid-config.json'),
               'diagrams': rows}
    (DIAGRAMS / 'manifest.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
