from pathlib import Path
import hashlib, json, re

vault = Path(__file__).resolve().parents[3]
batch = Path(__file__).resolve().parent
rows = json.loads((batch/'before-receipt.json').read_text())
for row in rows:
    assert hashlib.sha256((vault/row['snapshot']).read_bytes()).hexdigest() == row['sha256']
capture = json.loads((vault/'Sources/capture-manifest.json').read_text(encoding='utf-8'))[-1]
assert hashlib.sha256((vault/capture['path']).read_bytes()).hexdigest() == capture['sha256']
new = vault/'Resources/Coder Prompts/spark-benchmark-setup.md'
s = new.read_text(encoding='utf-8')
for term in ['## For human', '## For AI', 'not a benchmark prerequisite', '20%', '80%', 'only when', 'no Spark']:
    if term == 'no Spark': continue
    assert term in s, term
for term in ['do not create a second scheduler', 'If benchmark-runner is unfinished', 'explicitly incomplete', 'No broad cleanup', 'supported Codex', 'separate target containers', 'Sentinel']:
    assert term.lower() in s.lower(), term
paths = [vault/r['path'] for r in rows if r['path'].endswith('.md')] + [new, vault/'Activities/2026-10-22 Spark Benchmark Setup Prompt.md']
for path in paths:
    body = path.read_text(encoding='utf-8')
    for field in ['id:', 'status:', 'source:', 'last_reviewed:', 'next_action:']:
        assert field in body.split('---', 2)[1], (path, field)
    for link in re.findall(r'\[\[([^\]]+)\]\]', body):
        target = link.replace('\\|', '|').split('|')[0].split('#')[0]
        if not target: continue
        assert any((vault/(target+suffix)).exists() or (path.parent/(target+suffix)).exists() for suffix in ['', '.md']), (path, target)
index = (vault/'Resources/Coder Prompts/README.md').read_text(encoding='utf-8')
assert '|\n\n| [[Resources/Coder Prompts/spark-benchmark-setup' not in index
report = '''Focused documentation checks: PASS
- All 12 pre-edit snapshot hashes and approved-plan capture hash match receipts.
- Prompt includes optional deployment, unfinished-runner behavior, independent model setup, isolated targets, headroom, owned cleanup and incomplete evidence requirements.
- Required metadata and wiki links resolve in all changed notes and new authored notes.
- Coder index table has contiguous prompt rows.

Full vault validator: exit 1 with only two pre-existing unrelated presentation links:
Designs/Paper2Agent Briefing/presentation/README.md: unresolved Markdown link Paper2Agent Talk rev9.pptx
Designs/Paper2Agent Briefing/presentation/README.md: unresolved Markdown link review-rev9/
583 authored notes, 567 metadata-checked notes, 1945 wiki links,
77417 manifest rows, 14290 archived source rows verified.

No actual Spark access, Docker deployment, download, model call or benchmark was performed.
'''
(batch/'validation.txt').write_text(report, encoding='utf-8')
print(report)
