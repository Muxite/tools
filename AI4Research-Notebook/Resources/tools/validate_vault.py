"""Check authored navigation, source integrity, and migration accounting."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote, urlparse

VAULT=Path(__file__).resolve().parents[2]

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()

def validate():
    errors=[]; checked_notes=0; links=0
    authored=[p for p in VAULT.rglob('*.md') if 'Imported' not in p.relative_to(VAULT).parts and '.git' not in p.parts]
    ids={}
    for p in authored:
        rel=p.relative_to(VAULT).as_posix(); text=p.read_text(encoding='utf-8')
        # Tool READMEs, batch reports and executable fixture material keep their own format.
        exemption=rel.startswith(('Resources/lab/','Resources/review-batches/','Experiments/Development-Cases/'))
        template=rel.startswith('Templates/') and p.name!='README.md'
        if not exemption:
            checked_notes+=1
            for key in ('id','status','source','last_reviewed','next_action'):
                if not re.search(r'^'+key+r':\s*\S',text,re.M):errors.append(f'{rel}: missing {key}')
            match=re.search(r'^id:\s*(.*)',text,re.M)
            if match and not template:
                identity=match.group(1)
                if identity in ids:errors.append(f'{rel}: duplicate id with {ids[identity]}')
                ids[identity]=rel
        for target in re.findall(r'\[\[([^\]]+)\]\]',text):
            target=target.split('|')[0].rstrip('\\').split('#')[0].strip()
            if not target:continue
            # Templates use placeholders that do not denote a source yet.
            if '{{' in target:continue
            candidates=[VAULT/target,p.parent/target]
            if not Path(target).suffix:candidates += [Path(str(c)+'.md') for c in candidates]
            matches=[c for c in candidates if c.is_file()]
            if not matches and '/' not in target:
                matches=list(VAULT.rglob(target+'.md'))
                matches=[c for c in matches if 'Imported' not in c.parts]
            if not matches:errors.append(f'{rel}: unresolved wiki link {target}')
            links+=1
        # Check authored relative Markdown links; leave URLs and example placeholders alone.
        for match in re.finditer(r'\]\((<[^>]+>|[^\s)]+)\)',text):
            raw=match.group(1)
            raw=raw.strip('<>')
            if urlparse(raw).scheme or raw.startswith('#') or '{{' in raw:continue
            target=unquote(raw.split('#')[0])
            if target and not (p.parent/target).exists():errors.append(f'{rel}: unresolved Markdown link {target}')
    manifest=VAULT/'Resources/migration/manifest.jsonl'
    count=0; checked_copies=0
    if manifest.exists():
        for line in manifest.read_text(encoding='utf-8').splitlines():
            row=json.loads(line);count+=1
            if row['disposition'] not in {'copied','linked','duplicate','excluded','awaiting-review'}:errors.append('unknown disposition: '+row['source'])
            if row['disposition'] in {'copied','duplicate'}:
                p=VAULT/row['destination']
                actual=digest(p) if p.is_file() else None
                if actual!=row['sha256']:errors.append('archive hash mismatch: '+row['source']+' destination='+row['destination']+' expected='+str(row['sha256'])+' actual='+str(actual))
                checked_copies+=1
            elif row['disposition']=='linked':
                original=VAULT.parent/row['source']
                if not original.exists():errors.append('linked source missing: '+row['source'])
        summary=json.loads((manifest.parent/'summary.json').read_text())
        if count!=summary['manifest_rows'] or sum(summary['dispositions'].values())!=count:errors.append('manifest summary accounting mismatch')
    else:errors.append('migration manifest missing')
    source_manifest=VAULT/'Sources/capture-manifest.json'
    if source_manifest.exists():
        for row in json.loads(source_manifest.read_text()):
            if digest(VAULT/row['path'])!=row['sha256']:errors.append('prompt capture changed: '+row['path'])
    else:errors.append('prompt capture manifest missing')
    result={'authored_notes':len(authored),'metadata_checked_notes':checked_notes,'wiki_links':links,
            'manifest_rows':count,'archived_source_rows_verified':checked_copies,'errors':errors}
    (VAULT/'Resources/migration/validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({**result,'errors':errors[:12],'error_count':len(errors)},indent=2))
    return result

if __name__=='__main__':raise SystemExit(bool(validate()['errors']))
