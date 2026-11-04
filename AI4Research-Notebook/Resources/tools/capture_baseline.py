"""Capture public Git baseline and selected source hashes; never reads account state."""
from pathlib import Path
import subprocess
import json
import hashlib

VAULT = Path(__file__).resolve().parents[2]
ROOT = VAULT.parent
REPO = ROOT / 'AI4Research-Development/jiuwenswarm-m1'
REVIEW = ROOT / 'AI4Research-Development/jiuwenswarm-m1-review-d3d7f56'

def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args],capture_output=True,text=True,check=True).stdout.strip()

if __name__ == '__main__':
    old = git('rev-parse', 'HEAD')
    new = git('rev-parse', 'origin/ai4r_M1')
    if old != '98bd9d913f9ddae5f0d6a3ae256bff10f25ee743' or new != 'd3d7f565c6c05ccf764fe0780fde149b7dc89b95':
        raise SystemExit('Baseline moved; review before issuing a new receipt')
    selected = ['AGENTS.md','docs/code/Missions/M1/TASKS.md','deploy/m1/start-local.sh',
                'deploy/m1/compose.yaml','jiuwenswarm/research/native.py','jiuwenswarm/research/runner.py',
                'jiuwenswarm/research/library.py','jiuwenswarm/research/capsules/assets.py',
                'jiuwenswarm/research/shell_auth.py','jiuwenswarm/research/bootstrap_gateway.py',
                'jiuwenswarm/server/runtime/codex_subscription/service.py']
    receipt = {'captured_date':'2026-10-21','date_basis':'client capture date, not original author date',
               'preserved_revision':old,'captured_revision':new,'remote':'https://github.com/Stellven/jiuwenswarm.git',
               'preserved_checkout':str(REPO),'captured_checkout':str(REVIEW),
               'preserved_worktree_status':git('status','--porcelain'),
               'changed_files':git('diff','--name-only',old,new).splitlines(),
               'core_capsule_check_native_runner_delta':git('diff','--name-only',old,new,'--',
                    'jiuwenswarm/research/capsules','jiuwenswarm/research/checks',
                    'jiuwenswarm/research/native.py','jiuwenswarm/research/runner.py'),
               'source_receipts':[{'path':p,'sha256':hashlib.sha256((REVIEW/p).read_bytes()).hexdigest()} for p in selected],
               'runtime_qualification':'Not built or run by this source review; lab checks recorded separately'}
    (VAULT/'Resources/verification/baseline-2026-10-21.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'preserved':old,'captured':new,'changed_paths':len(receipt['changed_files'])}))
