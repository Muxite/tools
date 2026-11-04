"""Collect bounded personal artifacts; retain byte identity and explicit source scope.

Run from any directory: python collect_artifacts.py --review-date YYYY-MM-DD
No original is edited. Existing content-addressed archives are reused after hashing.
This is an inventory/structural check, not a content or security certification.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import quote

VAULT = Path(__file__).resolve().parents[2]
WORKSPACE = VAULT.parent
BINARY = {'.pptx', '.ppt', '.docx', '.doc', '.pdf'}
TEXT = {'.md', '.txt', '.json', '.yaml', '.yml', '.py', '.js', '.mjs', '.cjs', '.ts', '.cts', '.ps1', '.html', '.css', '.svg', '.toml'}
ASSETS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', '.snapshot', '.build', '.build-orange'}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def safe(path):
    return not any(p in SKIP for p in path.parts) and not re.search(r'(^|[._-])(credential|secret|token|password)([._-]|$)', path.name, re.I) and not path.name.startswith('.env')

def files(root):
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob('*') if p.is_file() and safe(p.relative_to(root)))

def structural(path):
    ext = path.suffix.lower()
    try:
        if ext in {'.pptx', '.docx'}:
            with zipfile.ZipFile(path) as z:
                bad = z.testzip()
                if bad:
                    return {'status': 'failed', 'detail': 'ZIP CRC failure: ' + bad}
                required = ['[Content_Types].xml', 'ppt/presentation.xml' if ext == '.pptx' else 'word/document.xml']
                for name in required:
                    ET.fromstring(z.read(name))
                members = z.namelist()
                return {'status': 'structurally-readable', 'zip_members': len(members), 'slide_xml_files': sum(bool(re.fullmatch(r'ppt/slides/slide\d+\.xml', n)) for n in members), 'speaker_note_xml_files': sum(bool(re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)) for n in members), 'limit': 'ZIP CRC and core XML only; no visual or claim verification'}
        if ext == '.pdf':
            with path.open('rb') as f:
                head = f.read(1024)
                f.seek(max(0, path.stat().st_size - 2048))
                tail = f.read()
            return {'status': 'signature-checked' if b'%PDF-' in head and b'%%EOF' in tail else 'failed', 'limit': 'header/trailer check only; pages not rendered'}
        if ext in TEXT:
            path.read_bytes().decode('utf-8-sig')
            return {'status': 'utf8-readable', 'limit': 'source bytes only; code not executed'}
        if ext == '.zip':
            with zipfile.ZipFile(path) as z:
                return {'status': 'structurally-readable' if z.testzip() is None else 'failed', 'zip_members': len(z.namelist())}
        return {'status': 'not-structurally-checked'}
    except Exception as exc:
        return {'status': 'failed', 'detail': str(exc)}

def revision(root):
    try:
        p = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=10)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None

def verify_destinations(recorded, vault):
    """Check portable stored bytes, including directly openable reference documents."""
    failures = []
    checked = 0
    for record in recorded.get('artifacts', []) + recorded.get('packages', []) + recorded.get('reference_documents', []):
        if 'destination' not in record:
            continue
        p = vault / record['destination']
        if not p.is_file() or sha(p) != record['sha256']:
            failures.append(record['destination'])
            continue
        checked += 1
        if 'source_files' in record:
            with zipfile.ZipFile(p) as z:
                for member in record['source_files']:
                    try:
                        matches = hashlib.sha256(z.read(member['path'])).hexdigest() == member['sha256']
                    except KeyError:
                        matches = False
                    if not matches:
                        failures.append(record['destination'] + ':' + member['path'])
    return {'checked_artifacts_packages_and_documents': checked, 'failures': failures}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--review-date')
    ap.add_argument('--verify', action='store_true', help='Verify local artifact/package hashes without rewriting the collection')
    args = ap.parse_args()
    if args.verify:
        recorded = json.loads((VAULT / 'Resources/artifact-manifest.json').read_text(encoding='utf8'))
        verification = verify_destinations(recorded, VAULT)
        print(json.dumps(verification, indent=2))
        if verification['failures']:
            raise SystemExit(1)
        return
    if not args.review_date:
        ap.error('--review-date is required when collecting')
    date = args.review_date
    index = {}
    migration = [json.loads(x) for x in (VAULT / 'Resources/migration/manifest.jsonl').read_text(encoding='utf8').splitlines()]
    for r in migration:
        if r['disposition'] in {'copied', 'duplicate'}:
            dest = VAULT / r['destination']
            if dest.is_file() and r.get('sha256') and r['sha256'] not in index:
                index[r['sha256']] = dest

    requests = {}
    exclusions = []
    def request(path, group):
        path = path.resolve()
        requests.setdefault(str(path), {'path': path, 'groups': set()})['groups'].add(group)

    for r in migration:
        if r.get('extension', '').lower() in BINARY:
            if '/skills/' in r['source'] and r['source'].endswith('template.pptx'):
                exclusions.append({'source': r['source'], 'reason': 'third-party skill template; not personal project artifact'})
                continue
            request(WORKSPACE / r['source'], 'Research papers' if '/papers/' in r['source'] or '/references/' in r['source'] else 'Project decks and documents')

    presentation_roots = [
        WORKSPACE / 'jiuwenswarm/docs/research/paper2agent/presentation',
        WORKSPACE / 'jiuwenswarm/docs/research/resource-aware-planning/presentation',
        WORKSPACE / 'AI4Research_private_planning/ai4r_muk/paper2agent-reference/deck',
        VAULT / 'Designs/Paper2Agent Briefing/presentation',
        VAULT / 'Designs/Nuwa Briefing/presentation',
        WORKSPACE / 'capsule-openjiuwen/deck',
        WORKSPACE / 'capsule-openjiuwen/merged',
    ]
    # Keep bounded packages with supporting relative files, rather than entire repositories.
    reference_roots = [
        WORKSPACE / 'jiuwenswarm/docs/product',
        WORKSPACE / 'jiuwenswarm/docs/architecture/design-package',
        WORKSPACE / 'AI4Research-Development/jiuwenswarm-m1-current/docs/product',
        WORKSPACE / 'AI4Research-Development/jiuwenswarm-m1-current/docs/architecture/design-package',
        WORKSPACE / 'RSI Design Docs',
        WORKSPACE / 'AI4Research-Development/jiuwenswarm-m1-current',
    ]
    for root in [WORKSPACE / 'outputs', VAULT / 'Designs', WORKSPACE / 'tundle', WORKSPACE / 'stellven/AI4Research']:
        for p in files(root):
            if p.suffix.lower() in BINARY:
                if any(part in {'tests', 'fixtures', 'runs', 'node_modules'} for part in p.relative_to(root).parts):
                    exclusions.append({'source': p.relative_to(WORKSPACE).as_posix(), 'reason': 'test fixture or execution input, not an authored presentation/document'})
                    continue
                request(p, 'Vault decks' if VAULT in p.parents else 'Project decks and documents')
    for p in files(WORKSPACE / 'outputs'):
        if p.suffix.lower() in {'.md', '.txt'} and p.name.startswith('ai4r-labs-and-capabilities'):
            request(p, 'Shareable briefs')

    bundle_root = VAULT / 'Archive/Imported/curated-artifacts/packages'
    bundle_root.mkdir(parents=True, exist_ok=True)
    packages = []
    for root in presentation_roots + reference_roots:
        if not root.is_dir():
            packages.append({'source': root.relative_to(WORKSPACE).as_posix(), 'status': 'source-directory-unavailable'})
            continue
        if root.name == 'jiuwenswarm-m1-current':
            selected = [root / name for name in ['AGENTS.md', 'deploy/m1/INTEGRATION-STATUS.md', 'deploy/m1/OPERATIONS.md'] if (root / name).is_file()]
        else:
            selected = [p for p in files(root) if p.suffix.lower() in BINARY | TEXT | ASSETS]
        records = [(p.relative_to(root).as_posix(), sha(p)) for p in selected]
        text_checks = []
        imports = set()
        for p in selected:
            if p.suffix.lower() in TEXT:
                check = structural(p)
                if check['status'] == 'failed':
                    text_checks.append({'path': p.relative_to(root).as_posix(), **check})
                if p.suffix.lower() == '.py':
                    try:
                        body = p.read_text(encoding='utf-8-sig')
                        imports.update(re.findall(r'^\s*(?:from|import)\s+([A-Za-z_][\w.]*)', body, re.M))
                    except UnicodeError:
                        pass
        fingerprint = hashlib.sha256(json.dumps(records).encode()).hexdigest()
        stem = re.sub(r'[^a-zA-Z0-9._-]+', '-', root.relative_to(WORKSPACE).as_posix())
        bundle = bundle_root / (stem + '-' + fingerprint[:12] + '.zip')
        if not bundle.exists():
            with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
                for p in selected:
                    z.write(p, p.relative_to(root).as_posix())
        with zipfile.ZipFile(bundle) as z:
            for name, digest in records:
                if hashlib.sha256(z.read(name)).hexdigest() != digest:
                    raise RuntimeError('bundle byte verification failed: ' + name)
        source_role = 'Builder-branch working-tree reference, not current remote' if 'jiuwenswarm-m1-current' in root.parts else 'Maintained-owner working-tree reference' if root in reference_roots and root.name != 'RSI Design Docs' else 'Historical or personal source reference'
        packages.append({'source': root.relative_to(WORKSPACE).as_posix(), 'destination': bundle.relative_to(VAULT).as_posix(), 'sha256': sha(bundle), 'files': len(selected), 'source_files': [{'path': n, 'sha256': h} for n, h in records], 'source_head': revision(root), 'source_role': source_role, 'status': 'byte-verified-reference-package', 'text_format_failures': text_checks, 'dependency_status': 'not installed or resolved by collection; import scan is partial and includes standard-library modules', 'python_imports_observed': sorted(imports), 'limitations': 'Working-tree bytes may include uncommitted changes; HEAD alone does not identify these bytes. Dated source snapshot, not maintained authority. Relative files within this package retained; links outside it and environment/dependency requirements may remain external. No build or visual verification.'})
        for p in selected:
            if p.suffix.lower() in BINARY:
                request(p, 'Project decks and documents')

    rows = []
    for req in sorted(requests.values(), key=lambda r: str(r['path'])):
        path = req['path']
        source = path.relative_to(WORKSPACE).as_posix()
        row = {'source': source, 'groups': sorted(req['groups'])}
        if not path.is_file():
            rows.append({**row, 'status': 'source-unavailable'})
            continue
        digest = sha(path)
        if VAULT in path.parents:
            dest, disposition = path, 'already-in-vault'
        elif digest in index and sha(index[digest]) == digest:
            dest, disposition = index[digest], 'reused-archive'
        else:
            name = path.name + ('.snapshot' if path.suffix.lower() in TEXT else '')
            dest = VAULT / 'Archive/Imported/curated-artifacts/files' / digest[:16] / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                shutil.copy2(path, dest)
            disposition = 'copied'
            index[digest] = dest
        if sha(dest) != digest:
            raise RuntimeError('copy byte verification failed: ' + str(dest))
        rows.append({**row, 'destination': dest.relative_to(VAULT).as_posix(), 'bytes': path.stat().st_size, 'sha256': digest, 'status': disposition, 'format_check': structural(path), 'authority': 'source artifact only; filename or collection does not establish approval'})

    # Direct text snapshots supplement complete ZIPs; original relative links stay source text.
    owner = WORKSPACE / 'jiuwenswarm'
    owner_root = owner / 'docs/architecture/design-package'
    product_navigation = owner / 'docs/product/README.md'
    product_receipt = owner_root / 'reference/product-input.md'
    reference_specs = [
        ('PRD V10 — M1 requirements', owner / 'docs/product/received-prds/prd-m1-v10-2026-10-15.txt', product_navigation, 'docs/product'),
        ('M1 system architecture', owner_root / '1-system.md', owner_root / 'README.md', 'docs/architecture/design-package'),
        ('Capability capsule contract', owner_root / '2-capability-capsules.md', owner_root / 'README.md', 'docs/architecture/design-package'),
        ('RSI workbench design', owner_root / 'side-systems/rsi-workbench.md', owner_root / 'README.md', 'docs/architecture/design-package'),
    ]
    reference_documents = []
    for title, source, selection_owner, package_suffix in reference_specs:
        record = {'title': title, 'source': source.relative_to(WORKSPACE).as_posix(), 'role': 'Maintained-owner working-tree reference snapshot; not a remote freshness or runtime claim', 'source_head': revision(owner), 'selection_evidence': [{'source': selection_owner.relative_to(WORKSPACE).as_posix(), 'sha256': sha(selection_owner)}]}
        if not source.is_file():
            reference_documents.append({**record, 'status': 'source-unavailable'})
            continue
        digest = sha(source)
        if source.suffix == '.txt' and title.startswith('PRD V10'):
            receipt = product_receipt.read_text(encoding='utf8')
            byte_match = re.search(r'(\d+) bytes; SHA-256 `([a-f0-9]{64})`', receipt)
            if not byte_match or int(byte_match[1]) != source.stat().st_size or byte_match[2] != digest:
                raise RuntimeError('PRD V10 bytes do not match the owner receipt; reconcile before collecting')
            record['selection_evidence'].append({'source': product_receipt.relative_to(WORKSPACE).as_posix(), 'sha256': sha(product_receipt), 'prd_identity_check': 'exact byte count and SHA256 match'})
        dest = VAULT / 'Archive/Imported/curated-artifacts/documents' / digest[:16] / (source.name + '.snapshot')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(source, dest)
        if sha(dest) != digest:
            raise RuntimeError('direct document byte mismatch: ' + str(dest))
        package = next((p for p in packages if p['source'] == 'jiuwenswarm/' + package_suffix), None)
        record.update({'destination': dest.relative_to(VAULT).as_posix(), 'sha256': digest, 'bytes': source.stat().st_size, 'status': 'byte-verified-reference-document', 'format_check': structural(source), 'package_destination': package.get('destination') if package else None, 'limitations': 'Raw text snapshot, not maintained notebook architecture. Original relative links may require the matching source package. HEAD is context; per-file hash identifies these working-tree bytes.'})
        reference_documents.append(record)

    expected = ['Designs/Paper2Agent Briefing/presentation/Paper2Agent Talk rev8.pptx']
    retired = [{'source': 'AI4Research-Notebook/Designs/Paper2Agent Briefing/presentation/' + name, 'status': 'deliberately-removed-not-required', 'basis': 'Sources/Prompts/2026-10-23-paper2agent-final-rev8.txt'} for name in ['Paper2Agent Talk rev9.pptx', 'review-rev9']]
    prior_deck = VAULT / 'Designs/Paper2Agent Briefing/presentation/Paper2Agent Talk rev8.pptx'
    missing = [{'source': 'AI4Research-Notebook/' + name, 'status': 'not-present-at-expected-location', 'search_scope': 'expected vault path checked on ' + date, 'fallback': prior_deck.relative_to(VAULT).as_posix() if prior_deck.is_file() else None} for name in expected if not (VAULT / name).exists()]
    result = {'schema_version': 2, 'review_date': date, 'workspace': str(WORKSPACE), 'scope': 'All inventoried non-template Office/PDF artifacts including papers; current vault/project deck roots; bounded presentation source packages, two branch-local PRD/design reference sets and four directly openable maintained-owner text snapshots. Not a complete filesystem or semantic audit.', 'exclusions': exclusions, 'known_missing': missing, 'retired_artifacts': retired, 'artifacts': rows, 'packages': packages, 'reference_documents': reference_documents, 'counts': dict(collections.Counter(r['status'] for r in rows)), 'format_failures': [r['source'] for r in rows + reference_documents if r.get('format_check', {}).get('status') == 'failed']}
    dest_manifest = VAULT / 'Resources/artifact-manifest.json'
    dest_manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf8')

    def link(path, start):
        return quote(os.path.relpath(VAULT / path, start).replace('\\', '/'), safe='/')
    def metadata(identity, title):
        return f'---\nid: {identity}\nstatus: source-indexed\nsource: Resources/artifact-manifest.json\nlast_reviewed: {date}\nnext_action: Open local artifacts; re-collect after owner sources change\n---\n# {title}\n\n'

    out = metadata('artifact-library', 'Local artifact library')
    out += '## Quick open\n\n- [Labs, sandboxes and capability capsules](../Designs/Labs%20and%20Capability%20Capsules.md) — current high-level design and diagram.\n- [Current document references](#current-document-references) — directly openable PRD, architecture, CC and RSI source snapshots.\n- [Deck Catalog](../Presentation%20Library/Deck%20Catalog.md) — current presentation entrypoints and prior decks.\n- [PRD/design reference packages and build sources](#reference-packages-and-build-sources) — dated local source bundles; owner scope is shown beside each.\n\n'
    out += 'Actual files are inside this vault. The [manifest](artifact-manifest.json) records original paths, SHA-256, dispositions and bounded format checks. Reused archived originals remain byte-for-byte unchanged. These are source artifacts and dated reference copies; product/design authority stays with the owning repository.\n\n'
    out += f"Indexed **{len(rows)} source artifact paths** ({len({r.get('sha256') for r in rows if r.get('sha256')})} unique file hashes), with **{sum(p.get('files', 0) for p in packages)} supporting files** in {sum('destination' in p for p in packages)} portable source packages. Source aliases can point to the same local file.\n\n"
    out += f'**{len(reference_documents)} directly openable text reference snapshots** supplement the artifact counts above; their original byte hashes and owner receipts are recorded separately in the manifest.\n\n## Current document references\n\nThese are dated copies of the maintained owner working tree, not claims of latest remote state or implementation. Open the local source text directly; use the matching package for original relative links/assets. Product and design authority remain with the owner.\n\n| Document | Local reference | Maintained owner | Scope |\n|---|---|---|---|\n'
    for doc in reference_documents:
        if 'destination' not in doc:
            out += '| ' + doc['title'] + ' | unavailable | source path in manifest | unresolved |\n'
            continue
        scope = 'PRD V10 exact owner receipt match' if doc['title'].startswith('PRD V10') else 'M1 design source snapshot'
        package_link = ' · [package](' + link(doc['package_destination'], VAULT / 'Resources') + ')' if doc.get('package_destination') else ''
        owner_link = quote(os.path.relpath(WORKSPACE / doc['source'], VAULT / 'Resources').replace('\\', '/'), safe='/')
        out += '| ' + doc['title'] + ' | [local text](' + link(doc['destination'], VAULT / 'Resources') + ')' + package_link + ' | [owner](' + owner_link + ') | ' + scope + ' |\n'
    out += '\n## Decks and reports\n\nSee the [Deck Catalog](../Presentation%20Library/Deck%20Catalog.md) for editable presentations, reports and available embedded speaker notes.\n\n## Reference packages and build sources\n\nExtract packages to an empty directory to retain their internal relative paths. Presentation dependencies and references outside each package are not vendored. XML/ZIP readability is not a successful build. PRD/design bundles are dated, branch-local reference snapshots, not competing maintained copies.\n\n'
    for p in packages:
        out += '- [' + p['source'] + '](' + link(p['destination'], VAULT / 'Resources') + f") — {p['files']} files; {p['source_role']}; source HEAD `{p['source_head'] or 'not recorded'}`.\n" if 'destination' in p else '- ' + p['source'] + ' — unavailable.\n'
    for group in ['Research papers', 'Shareable briefs']:
        out += '\n## ' + group + '\n\n'
        unique = {}
        for r in rows:
            if group in r['groups'] and 'destination' in r:
                # Prefer descriptive paper filenames; aliases remain in the manifest.
                old = unique.get(r['sha256'])
                if old is None or len(Path(r['source']).stem) > len(Path(old['source']).stem):
                    unique[r['sha256']] = r
        for r in sorted(unique.values(), key=lambda r: r['source']):
            out += '- [' + r['source'] + '](' + link(r['destination'], VAULT / 'Resources') + ')\n'
    out += '\n## Limits and unavailable items\n\n'
    out += 'Unavailable expected paths at this collection: ' + ', '.join('`' + r['source'] + '`' for r in missing) + '.\n\n' if missing else 'All tracked expected revision paths are present; presence alone does not establish review or approval.\n\n'
    out += 'Paper2Agent rev8 is the user-confirmed final version; rev9 and its render directory were deliberately removed and are not missing-artifact tasks.\n\n'
    out += 'Structural checks cover ZIP CRC/core XML, PDF signatures and UTF-8 readability where applicable. No slides or pages were rendered, code executed, scientific claims verified, or malware certification performed.\n\nSource Markdown inside ZIPs preserves its original syntax; links outside each package can require its original repository. Binary attachments are excluded by Git and need the documented vault backup. The manifest records the exact source and destination for every selected artifact; source-unavailable entries and format failures remain explicit. Third-party skill templates, caches, dependency trees, private state and entire source repositories are excluded.\n'
    (VAULT / 'Resources/Artifact Library.md').write_text(out, encoding='utf8')

    deck = metadata('presentation-deck-catalog', 'Deck and report catalog')
    deck += '## Quick open\n\n'
    nuwa = VAULT / 'Designs/Nuwa Briefing/presentation/output/Nuwa Talk rev3.pptx'
    if nuwa.is_file():
        deck += '- [Nuwa: currently documented rev3](../Designs/Nuwa%20Briefing/presentation/output/Nuwa%20Talk%20rev3.pptx) · [reading notes and revision scope](../Designs/Nuwa%20Briefing/presentation/README.md).\n'
    workload_source = 'jiuwenswarm/docs/research/resource-aware-planning/presentation/output/AI4Research Workload Profiling - Dense 2026-10-19 r9.pptx'
    workload = next((r for r in rows if r['source'] == workload_source and 'destination' in r), None)
    workload_owner = WORKSPACE / 'jiuwenswarm/docs/research/resource-aware-planning/presentation/README.md'
    if workload and workload_owner.is_file() and 'Dense%202026-10-19%20r9.pptx' in workload_owner.read_text(encoding='utf8'):
        workload_package = next(p for p in packages if p['source'] == 'jiuwenswarm/docs/research/resource-aware-planning/presentation')
        deck += '- [Workload Profiling: source-documented checked r9](' + link(workload['destination'], VAULT / 'Presentation Library') + ') · [dated source notes and build package](' + link(workload_package['destination'], VAULT / 'Presentation Library') + '). Owner README identifies the October 19 r9 deck; this is not a user-confirmed final or a fresh validation.\n'
    if prior_deck.is_file():
        deck += '- [Paper2Agent: final rev8](../Designs/Paper2Agent%20Briefing/presentation/Paper2Agent%20Talk%20rev8.pptx) · [reading notes and revision history](../Designs/Paper2Agent%20Briefing/presentation/README.md). User-confirmed final version; rev9 was deliberately removed.\n'
    else:
        deck += '- Paper2Agent final rev8 is unavailable at its expected path; consult the manifest. Revision 9 is retired.\n'
    deck += '\n'
    deck += 'Local clickable copies, including earlier revisions. “Indexed” means located and structurally checked where supported; it does not mean current, approved, visually reviewed or presented. The [Artifact Library](../Resources/Artifact%20Library.md) includes source bundles, papers, checks and unavailable items. Speaker-note counts report embedded notes XML, without claiming rehearsal or script quality.\n\n'
    groups = collections.defaultdict(list)
    for r in rows:
        if Path(r['source']).suffix.lower() in {'.pptx', '.ppt', '.docx', '.doc'} or (Path(r['source']).suffix.lower() == '.pdf' and 'Research papers' not in r['groups']):
            parts = r['source'].split('/')
            groups[parts[0]].append(r)
    for group, records in sorted(groups.items()):
        deck += '## ' + group + '\n\n'
        for r in records:
            if 'destination' not in r:
                deck += '- ' + r['source'] + ' — source unavailable.\n'
                continue
            check = r['format_check']
            info = check['status']
            if 'speaker_note_xml_files' in check and r['source'].endswith('.pptx'):
                info += f"; {check['slide_xml_files']} slides, {check['speaker_note_xml_files']} note parts"
            deck += '- [' + r['source'] + '](' + link(r['destination'], VAULT / 'Presentation Library') + ') — ' + info + '.\n'
    if missing:
        deck += '\n## Unavailable expected paths\n\n' + '\n'.join('- `' + r['source'] + '`' for r in missing) + '\n'
    (VAULT / 'Presentation Library/Deck Catalog.md').write_text(deck, encoding='utf8')
    print(json.dumps({'artifacts': len(rows), 'unique_hashes': len({r.get('sha256') for r in rows if r.get('sha256')}), 'reference_documents': len(reference_documents), 'counts': result['counts'], 'packages': len(packages), 'format_failures': result['format_failures'], 'missing': len(missing)}, indent=2))

if __name__ == '__main__':
    main()
