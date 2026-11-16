from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
m=json.loads((root/'MANIFEST.json').read_text())
errors=[]
for name,meta in m['files'].items():
 p=root/name
 if not p.is_file(): errors.append('missing: '+name); continue
 b=p.read_bytes()
 if len(b)!=meta['bytes'] or hashlib.sha256(b).hexdigest()!=meta['sha256']:errors.append('changed: '+name)
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=root/'MANIFEST.json'}
errors += ['unlisted: '+x for x in sorted(actual-set(m['files']))]
print(json.dumps({'checked':len(m['files']),'errors':errors,'scope':'package integrity only'},indent=2))
raise SystemExit(bool(errors))
