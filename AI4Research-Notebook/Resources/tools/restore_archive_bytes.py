"""Restore archive copies only when the original still matches the migration receipt."""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime,timezone

VAULT=Path(__file__).resolve().parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def restore():
    changed=[]; seen=set(); errors=[]
    for line in (VAULT/'Resources/migration/manifest.jsonl').read_text(encoding='utf-8').splitlines():
        r=json.loads(line)
        if r['disposition'] not in {'copied','duplicate'} or r['destination'] in seen:continue
        seen.add(r['destination']); target=VAULT/r['destination']; original=VAULT.parent/r['source']
        if target.is_file() and sha(target)==r['sha256']:continue
        if not original.is_file() or sha(original)!=r['sha256']:
            errors.append(r['source']);continue
        before=target.read_bytes() if target.is_file() else None
        data=original.read_bytes()
        reason='line-ending conversion' if before is not None and before.replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n') else 'other difference'
        shutil.copyfile(original,target)
        if sha(target)!=r['sha256']:raise RuntimeError('Restore verification failed: '+r['destination'])
        changed.append({'source':r['source'],'destination':r['destination'],'difference':reason})
    result={'archive_files_checked':len(seen),'restored':len(changed),'changes':changed,'errors':errors}
    target_report=VAULT/'Resources/migration/byte-restoration.json'
    if changed or not target_report.exists():
        target_report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    history_file=VAULT/'Resources/migration/byte-check-history.json'
    history=json.loads(history_file.read_text(encoding='utf-8')) if history_file.exists() else []
    history.append({'checked_utc':datetime.now(timezone.utc).isoformat(),'archive_files_checked':len(seen),'restored':len(changed),'errors':errors})
    history_file.write_text(json.dumps(history,indent=2),encoding='utf-8')
    print(json.dumps({**result,'changes':changed[:3]},indent=2))
    return result

if __name__=='__main__':raise SystemExit(bool(restore()['errors']))
