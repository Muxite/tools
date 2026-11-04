"""Create and verify a complete vault ZIP; external linked sources need their own backups."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import zipfile

VAULT = Path(__file__).resolve().parents[2]
EXCLUDED = {'.git', '__pycache__', '.lab-state', '.venv', 'node_modules', '.pytest_cache'}
SECRET = re.compile(r'(^\.env($|\.)|credential|secret|id_rsa|id_ed25519|\.pem$|\.key$)', re.I)

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def verify(path):
    path=Path(path)
    receipt=Path(str(path)+'.sha256')
    if not receipt.is_file() or receipt.read_text().split()[0] != digest(path):
        raise ValueError('Missing receipt or ZIP checksum mismatch')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('ZIP CRC check failed')
        manifest=json.loads(z.read('BACKUP-CONTENTS.json'))
        if set(z.namelist()) != set(manifest)|{'BACKUP-CONTENTS.json'}:
            raise ValueError('Backup file list differs from manifest')
        for name, expected in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=expected:
                raise ValueError('Backup content hash mismatch: '+name)
    return {'verified':str(path.resolve()), 'files':len(manifest)}

def backup(destination, vault=VAULT):
    destination=Path(destination).resolve(); vault=Path(vault).resolve()
    if destination==vault or vault in destination.parents:
        raise ValueError('Backup destination must be outside the vault')
    destination.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target=destination/f'AI4Research-Notebook-{stamp}.zip'
    temp=target.with_suffix('.zip.partial'); contents={}
    with zipfile.ZipFile(temp,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(vault.rglob('*')):
            rel=p.relative_to(vault)
            if p.is_symlink() or not p.is_file() or any(x in EXCLUDED for x in rel.parts) or SECRET.search(p.name): continue
            name=rel.as_posix()
            if name=='BACKUP-CONTENTS.json': raise ValueError('reserved backup manifest filename exists in vault')
            data=p.read_bytes()
            contents[name]=hashlib.sha256(data).hexdigest()
            z.writestr(name,data)
        z.writestr('BACKUP-CONTENTS.json',json.dumps(contents,indent=2))
    temp.rename(target)
    Path(str(target)+'.sha256').write_text(digest(target)+'  '+target.name+'\n',encoding='utf-8')
    return verify(target)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--destination',type=Path)
    group.add_argument('--verify',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.verify) if args.verify else backup(args.destination),indent=2))
