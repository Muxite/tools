"""Non-destructive workspace inventory and content-addressed personal archive.

Run from any directory. Only writes inside this vault. Does not follow symlinks.
Originals are never deleted, moved, rewritten or committed.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from polish_tables import table_links
from datetime import datetime, timezone

VAULT = Path(__file__).resolve().parents[2]
ROOT = VAULT.parent
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.cache', '.pytest_cache',
        '.mypy_cache', '.ruff_cache', 'dist', 'target', '.next', '.obsidian', '.codex',
        '.claude', '.agents', '.heldout', 'site-packages', '.notebook-validation', 'AI4Research-Notebook-Backups'}
REFERENCE = {'deepseek', 'github', 'openjiuwen', 'other-repos', 'Paper2Agent', 'stellven'}
TEXT = {'.md', '.txt', '.mmd'}
ARTIFACT = {'.pdf', '.pptx', '.docx', '.xlsx'}
SECRET_NAME = re.compile(r'(^\.env($|\.)|credential|secret|token[-_]?file|id_rsa|id_ed25519|\.pem$|\.key$)', re.I)
SECRET_BODY = re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{25,})|(?:api[_-]?key|access[_-]?token|password)\s*[:=]\s*[\"\']?[A-Za-z0-9_/+.-]{24,}', re.I)
REGISTRY_PATH = VAULT / 'Resources/migration/source-collections.json'

def load_registry(path=REGISTRY_PATH):
    registry = json.loads(path.read_text(encoding='utf-8'))
    if registry.get('version') != 1 or not registry.get('rules'):
        raise ValueError('Missing or unsupported source registry')
    ids, prefixes = set(), set()
    for rule in registry['rules']:
        prefix = rule['prefix']
        if not prefix or prefix.startswith('/') or ':' in prefix or '..' in prefix.split('/'):
            raise ValueError('Unsafe collection prefix')
        if rule['id'] in ids or prefix in prefixes:
            raise ValueError('Duplicate collection identity or prefix')
        ids.add(rule['id']); prefixes.add(prefix)
    return registry

REGISTRY = load_registry()

def source_role(rel, registry=None):
    registry = REGISTRY if registry is None else registry
    source = rel.as_posix()
    matches = [r for r in registry['rules'] if source == r['prefix'] or source.startswith(r['prefix'] + '/')]
    if matches:
        return max(matches, key=lambda r: len(r['prefix']))
    return {'id': registry['default_rule'], 'authority': registry['default_authority'], 'maintained': False}

def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def authority(rel):
    return source_role(rel)['authority']

def stream_for(rel):
    s = rel.as_posix().lower()
    if any(x in s for x in ('workload', 'profil')): return 'Workload Characterization'
    if any(x in s for x in ('rsi', 'skill', 'paper2agent')): return 'Skills to CCs'
    if any(x in s for x in ('sandbox', 'sidecar', 'lab', 'container')): return 'Lab Infrastructure'
    if any(x in s for x in ('capsule', 'cc-')): return 'CC Effectiveness'
    return 'M1 Design Code and Tests'

def inventory(copy_budget_mb=384):
    out = VAULT / 'Resources' / 'migration'
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / 'manifest.jsonl'
    # Keep prior source receipts before refreshing classifications or destinations.
    if manifest.exists():
        history = out / 'history' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        history.mkdir(parents=True, exist_ok=False)
        for name in ('manifest.jsonl', 'summary.json', 'source-collections.json'):
            source = out / name
            if source.exists(): shutil.copy2(source, history / name)
    seen = {}
    counts, collections_counts = collections.Counter(), collections.defaultdict(collections.Counter)
    copied_bytes = 0
    rows = []
    def add(row):
        rows.append(row)
        counts[row['disposition']] += 1
        collections_counts[row['collection']][row['disposition']] += 1

    def boundary(path, reason, disposition='excluded'):
        rel = path.relative_to(ROOT)
        add(dict(source=rel.as_posix(), kind='directory-boundary', collection=rel.parts[0],
                 disposition=disposition, reason=reason, sha256=None, destination=None,
                 review='boundary-rule-reviewed; descendants intentionally not inventoried'))

    def visit(base):
        nonlocal copied_bytes
        for current, dirs, files in os.walk(base, followlinks=False):
            current = Path(current)
            for name in sorted(dirs.copy()):
                p = current / name
                registered_boundary = next((b for b in REGISTRY.get('boundaries', []) if p.relative_to(ROOT).as_posix() == b['prefix']), None)
                if name in SKIP or name.endswith('.egg-info') or p.is_symlink() or name == VAULT.name or registered_boundary:
                    dirs.remove(name)
                    if name != VAULT.name:
                        boundary(p, registered_boundary['reason'] if registered_boundary else 'dependency/cache/private-tool-state or symlink boundary')
            dirs.sort()
            for name in sorted(files):
                p = current / name
                rel = p.relative_to(ROOT)
                if p.is_symlink():
                    add(dict(source=rel.as_posix(), collection=rel.parts[0], kind='symlink', disposition='excluded', reason='do not follow symlinks', destination=None, sha256=None, review='rule-reviewed'))
                    continue
                try:
                    st = p.stat()
                    row = dict(source=rel.as_posix(), collection=rel.parts[0] if len(rel.parts)>1 else 'workspace-root',
                               kind='file', extension=p.suffix.lower(), bytes=st.st_size,
                               modified_utc=datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
                               authority=authority(rel), workstream=stream_for(rel), sha256=None,
                               source_rule=source_role(rel)['id'],
                               destination=None, review='automated-rule-reviewed; content not individually reviewed')
                    if SECRET_NAME.search(name) or name.lower() in {'.git', '.npmrc', '.pypirc', '.netrc'}:
                        row.update(disposition='excluded', reason='sensitive filename; content not read')
                        add(row); continue
                    # Hash all inventoried ordinary files, including linked large artifacts.
                    row['sha256'] = hash_file(p)
                    is_text = p.suffix.lower() in TEXT and st.st_size <= 4*1024*1024
                    if is_text and SECRET_BODY.search(p.read_text(encoding='utf-8', errors='replace')):
                        row.update(disposition='excluded', reason='potential credential pattern; no content copied')
                        add(row); continue
                    current_source = source_role(rel)['maintained']
                    preferred_artifact = rel.as_posix().startswith(('tundle/ai4research/', 'RSI Design Docs/'))
                    copy = not current_source and (is_text or (preferred_artifact and p.suffix.lower() in ARTIFACT and st.st_size <= 8*1024*1024))
                    digest = row['sha256']
                    if copy and digest in seen:
                        row.update(disposition='duplicate', destination=seen[digest], reason='byte-identical to archived source; source identity retained')
                    elif copy and copied_bytes + st.st_size <= copy_budget_mb*1024*1024:
                        safe = re.sub(r'[^\w .-]', '_', p.stem)[:48].rstrip(' .') or 'source'
                        dest = Path('Archive') / 'Imported' / digest[:2] / (digest[:16] + '--' + safe + p.suffix.lower())
                        target = VAULT / dest
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if target.exists() and hash_file(target) != digest:
                            raise RuntimeError(f'Archive collision: {target}')
                        if not target.exists(): shutil.copy2(p, target)
                        if hash_file(target) != digest: raise RuntimeError(f'Copy verification failed: {target}')
                        copied_bytes += st.st_size
                        seen[digest] = dest.as_posix()
                        row.update(disposition='copied', destination=dest.as_posix(), reason='exact source bytes; read-only historical snapshot')
                    else:
                        row.update(disposition='linked', destination=p.as_posix(), reason='maintained source stays authoritative' if current_source else 'code/large artifact/non-text collection linked in place or archive budget reached')
                    add(row)
                except OSError as e:
                    add(dict(source=rel.as_posix(), collection=rel.parts[0], kind='file', disposition='awaiting-review', reason=type(e).__name__, sha256=None, destination=None, review='unreadable-source'))

    for p in sorted(ROOT.iterdir()):
        if p.name == VAULT.name: continue
        if p.is_symlink(): boundary(p, 'symlink not followed'); continue
        if p.is_dir():
            if p.name in SKIP: boundary(p, 'private-tool-state/cache excluded'); continue
            if p.name in REFERENCE:
                boundary(p, 'third-party/reference collection indexed in place; descendants not imported', 'linked')
                # Explicitly retain personal output collections embedded in the archived AI4R clone.
                if p.name == 'stellven':
                    for suffix in ('AI4Research/outputs', 'AI4Research/Feature list stuff'):
                        selected = p / suffix
                        if selected.exists(): visit(selected)
                continue
            visit(p)
        elif p.is_file():
            # os.walk does not enumerate a single file; use root-only enumeration below.
            pass
    # Include root loose work without walking into directories a second time.
    for p in sorted(ROOT.iterdir()):
        if not p.is_file() or p.is_symlink(): continue
        st = p.stat()
        if SECRET_NAME.search(p.name):
            add(dict(source=p.name, collection='workspace-root', kind='file', disposition='excluded', reason='sensitive filename', destination=None, sha256=None, review='rule-reviewed')); continue
        digest = hash_file(p)
        row = dict(source=p.name, collection='workspace-root', kind='file', extension=p.suffix.lower(), bytes=st.st_size, modified_utc=datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(), sha256=digest, authority='personal-workspace-source', workstream=stream_for(Path(p.name)), destination=p.as_posix(), disposition='linked', reason='loose work preserved in place', review='automated-rule-reviewed')
        if p.suffix.lower() in TEXT and st.st_size <= 4*1024*1024:
            if SECRET_BODY.search(p.read_text(encoding='utf-8', errors='replace')):
                row.update(disposition='excluded', destination=None, reason='potential credential pattern')
            elif digest in seen:
                row.update(disposition='duplicate', destination=seen[digest], reason='identical archived bytes')
            else:
                dest = Path('Archive/Imported') / digest[:2] / (digest[:16] + '--' + p.name[:90])
                target = VAULT / dest; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                seen[digest] = dest.as_posix(); copied_bytes += st.st_size
                row.update(disposition='copied', destination=dest.as_posix(), reason='exact source bytes')
        add(row)
    manifest.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), root=ROOT.as_posix(),
                   manifest_rows=len(rows), dispositions=dict(counts), copied_bytes=copied_bytes,
                   collections={k:dict(v) for k,v in collections_counts.items()},
                   coverage='All files enumerated outside listed directory boundaries have a disposition. Boundaries are explicit, not descendant-level inventories.',
                   integrity='Copied source bytes verified by SHA-256; source tree never modified.',
                   source_registry_sha256=hash_file(REGISTRY_PATH),
                   classification='Explicit reviewed source roles from source-collections.json; roles do not imply approval or runtime acceptance. Historical summaries require source review.')
    (out/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    write_indexes(rows, summary)
    print(json.dumps(summary, indent=2))

def write_indexes(rows, summary):
    page_dir = VAULT/'Resources'/'Collections'; page_dir.mkdir(exist_ok=True)
    groups = collections.defaultdict(list)
    identity_path = VAULT/'Resources/migration/collection-identities.json'
    identities = json.loads(identity_path.read_text(encoding='utf-8')) if identity_path.exists() else {}
    for row in rows: groups[row['collection']].append(row)
    index = ['# Source collections', '', 'Browse the personal archive by original collection. File dates are filesystem modification dates, not inferred meeting dates.', '', '| Collection | Items | Index |', '|---|---:|---|']
    for i, (name, items) in enumerate(sorted(groups.items()), 1):
        filename = re.sub(r'[^\w .-]', '_', name)
        identity = identities.setdefault(filename, 'collection-' + hashlib.sha256(name.encode('utf-8')).hexdigest()[:12])
        page = page_dir/(filename+'.md')
        counts=collections.Counter(r['disposition'] for r in items)
        lines = [f'---\nid: {identity}\nstatus: indexed\nsource: "workspace/{name}"\nlast_reviewed: 2026-10-21\nnext_action: "Use the source map to open an item; resolve authority before reuse"\n---', f'# {name}', '', '[[Resources/Source Collections|All collections]] · [[Home]]', '', f"**{len(items):,} indexed entries.** " + '; '.join(f'{k}: {v:,}' for k,v in sorted(counts.items()))+'.', '', 'Exact source bytes and original paths are kept distinct from current implementation authority. Browse batches below; the range labels follow original source paths.', '', '| Batch | First source | Last source |', '|---|---|---|']
        detail_dir=page_dir/'Details';detail_dir.mkdir(exist_ok=True)
        for start in range(0,len(items),200):
            batch=items[start:start+200];part=start//200+1
            detail_name=f'{filename}-{part:03}'
            lines.append(f"| [[Resources/Collections/Details/{detail_name}|{part}]] | `{batch[0]['source']}` | `{batch[-1]['source']}` |")
            detail=[f'---\nid: {identity}-part-{part:03}\nstatus: indexed\nsource: Resources/migration/manifest.jsonl\nlast_reviewed: 2026-10-21\nnext_action: Open the original source or snapshot\n---',f'# {name} sources {start+1} to {start+len(batch)}','',f'[[Resources/Collections/{filename}|Collection overview]] · [[Resources/Source Collections|All collections]]','', 'Archived files preserve source bytes; original relative links inside snapshots may require the original location.', '', '| Original source | Disposition | Open | Authority or reason |','|---|---|---|---|']
            for r in batch:
                src=r['source'].replace('|','\\|');dest=r.get('destination')
                from urllib.parse import quote
                if dest and not Path(dest).is_absolute(): link='[snapshot]('+quote('../../../'+dest,safe='/')+')'
                elif dest:link='[original](file:///'+quote(dest,safe='/:')+')'
                else:link='—'
                detail.append(f"| `{src}` | {r['disposition']} | {link} | {r.get('authority',r['reason'])} |")
            (detail_dir/(detail_name+'.md')).write_text(table_links('\n'.join(detail)+'\n'),encoding='utf-8')
        page.write_text(table_links('\n'.join(lines)+'\n'), encoding='utf-8')
        index.append(f'| {name} | {len(items)} | [[Resources/Collections/{filename}|Browse]] |')
    index.extend(['', 'Detailed machine-readable provenance: [manifest](migration/manifest.jsonl). Directory boundaries are listed explicitly; excluded/reference directory descendants are not counted as migrated files.', '', f"Inventory: **{summary['manifest_rows']} entries**; **{summary['copied_bytes']:,} bytes** copied. See [summary](migration/summary.json) for dispositions."])
    identity_path.write_text(json.dumps(identities,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (VAULT/'Resources'/'Source Collections.md').write_text(table_links('---\nid: resource-source-collections\nstatus: indexed\nsource: Resources/migration/manifest.jsonl\nlast_reviewed: 2026-10-21\nnext_action: Resolve awaiting-review entries and refresh after source changes\n---\n'+'\n'.join(index)+'\n'), encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--copy-budget-mb', type=int, default=384)
    parser.add_argument('--indexes-only', action='store_true', help='Rebuild paginated navigation from the existing manifest without reading or copying sources')
    args = parser.parse_args()
    if args.indexes_only:
        manifest=VAULT/'Resources/migration/manifest.jsonl'
        rows=[json.loads(line) for line in manifest.read_text(encoding='utf-8').splitlines()]
        summary=json.loads(manifest.with_name('summary.json').read_text(encoding='utf-8'))
        write_indexes(rows,summary)
    else:
        inventory(args.copy_budget_mb)
