"""Capture concrete source, imported class, interpreter and dependency evidence."""
import argparse
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import platform
import subprocess
import sys

PINS = {'delegate': '26acdaddae1fa0daf0f888f8012f0284a2548204',
        'agent-core': '4dbaa84ca568af3f181da4f9cd26b713a5b73039',
        'mapie': '90db8996a8c38c8e6574a901a1700ba889c3ac58'}


def command(args):
    result = subprocess.run(args, capture_output=True, text=True)
    return {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


def run(environment):
    from mapie.regression import SplitConformalRegressor
    from openjiuwen.core.foundation.tool.mcp.client.stdio_client import StdioClient
    from openjiuwen.harness.tools.subagent.task_tool import TaskTool
    from openjiuwen.core.sys_operation import SysOperation
    sys.path.insert(0, str(environment / 'delegate'))
    from jiuwenswarm.runtime.mcp_references import McpReferenceValidationInput
    reference_validation = McpReferenceValidationInput.from_iterable(['cc_mapie', 'cc_mapie'])
    assert reference_validation.references == ('cc_mapie',)
    sources = {}
    for name, pin in PINS.items():
        path = environment / name
        head = command(['git', '-C', str(path), 'rev-parse', 'HEAD'])['stdout'].strip()
        assert head == pin, (name, head, pin)
        status = command(['git', '-C', str(path), 'status', '--porcelain=v1'])
        assert status['stdout'] == '', status
        sources[name] = {'path': str(path), 'commit': head,
                         'origin': command(['git', '-C', str(path), 'remote', 'get-url', 'origin'])['stdout'].strip(),
                         'status': status}
    imported = {}
    for cls in (SplitConformalRegressor, StdioClient, TaskTool, SysOperation, McpReferenceValidationInput):
        path = Path(inspect.getfile(cls))
        imported[cls.__name__] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return {'scope': 'Reduced dependencies for tested imports; not a complete JiuwenSwarm installation',
            'python': {'executable': sys.executable, 'version': platform.python_version(),
                       'sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
            'sources': sources, 'imported': imported,
            'jiuwenswarm_reference_validation': list(reference_validation.references),
            'packages': dict(sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions())),
            'pip_check': command([sys.executable, '-m', 'pip', 'check']),
            'limitations': ['Upstream JiuwenSwarm LFS video object missing (404); checkout used GIT_LFS_SKIP_SMUDGE=1.',
                            'Native coding demo exercises core TaskTool and SysOperation used by JiuwenSwarm; not the full JiuwenSwarm code-agent factory or a live LLM.',
                            'MAPIE v1.1.0 with sklearn1.9.1 failed __sklearn_tags__; tested pin sklearn1.5.2.',
                            'Initial cold scientific-package native call reached default60s timeout; retained attempt in local external mapie-store.',
                            'Initial native quoted absolute python command was rejected by upstream allowlist; corrected to allowlisted python command.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--environment', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--lock', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.environment)
    args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    freeze = command([sys.executable, '-m', 'pip', 'freeze'])['stdout'].splitlines()
    lines = ['# Tested Windows Python3.12 reduced integration environment.',
             '# Install packages below, then install isolated exact source checkouts with --no-deps.',
             '# Source pins are in environment-report.json; do not install editable workstation paths.']
    lines += ['# JiuwenSwarm git@github.com:openJiuwen-ai/jiuwenswarm.git@' + PINS['delegate'],
              '# openjiuwen git+https://github.com/openJiuwen-ai/agent-core.git@' + PINS['agent-core'],
              '# MAPIE git+https://github.com/scikit-learn-contrib/MAPIE.git@' + PINS['mapie']]
    skip_next = False
    for line in freeze:
        if line.startswith('# Editable') or line.startswith('-e '):
            continue
        if line.lower().startswith(('openjiuwen', 'mapie')):
            continue
        lines.append(line)
    args.lock.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'sources': {name: value['commit'] for name, value in report['sources'].items()},
                      'pip_check': report['pip_check']}))
