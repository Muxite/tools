"""Run the vault's local checks and retain exact command/output receipts."""
from datetime import datetime,timezone
from pathlib import Path
import json
import subprocess
import sys
import argparse

VAULT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-only',action='store_true')
    args=parser.parse_args()
    receipt_dir=VAULT/'Resources/verification';receipt_dir.mkdir(exist_ok=True)
    commands=[
        ('lab-tests',[sys.executable,'-m','unittest','discover','-s','Resources/lab','-v']),
        ('analysis-tests',[sys.executable,'-m','unittest','discover','-s','Experiments/tools','-v']),
        ('backup-tests',[sys.executable,'-m','unittest','discover','-s','Resources/tools','-v']),
        ('vault-integrity',[sys.executable,'Resources/tools/validate_vault.py']),
    ]
    receipt=receipt_dir/'checks.json'
    results=json.loads(receipt.read_text(encoding='utf-8')) if args.integrity_only and receipt.exists() else []
    if args.integrity_only:
        commands=[c for c in commands if c[0]=='vault-integrity']
        results=[r for r in results if r['check']!='vault-integrity']
    # Create the index before link validation, including on a fresh checkout.
    receipt.write_text(json.dumps(results,indent=2),encoding='utf-8')
    for name,cmd in commands:
        start=datetime.now(timezone.utc).isoformat()
        p=subprocess.run(cmd,cwd=VAULT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (receipt_dir/(name+'.txt')).write_text(p.stdout,encoding='utf-8')
        results.append({'check':name,'command':cmd,'cwd':str(VAULT),'started_utc':start,
                        'ended_utc':datetime.now(timezone.utc).isoformat(),'exit_code':p.returncode,
                        'output':f'Resources/verification/{name}.txt'})
        print(f'{name}: exit {p.returncode}',flush=True)
    (receipt_dir/'checks.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    return any(r['exit_code'] for r in results)

if __name__=='__main__':raise SystemExit(main())
