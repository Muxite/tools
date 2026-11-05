"""Workspace-relative setup for the transferred CC v2 experiments."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
REFERENCE = ROOT / 'AI4Research-Notebook/Designs/CC Protocols/reference'


def python_path(directory):
    return directory / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def run(command, *, env=None, capture=False):
    print('Running: ' + ' '.join(map(str, command)), flush=True)
    return subprocess.run(list(map(str, command)), cwd=ROOT, env=env, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def checkout(target, source, env):
    target = target.resolve()
    if (target / '.git').exists():
        head = run(['git', '-C', target, 'rev-parse', 'HEAD'], env=env, capture=True).strip()
        dirty = run(['git', '-C', target, 'status', '--porcelain=v1'], env=env, capture=True).strip()
        if head != source['commit'] or dirty:
            raise RuntimeError(f'Refusing to replace a different or dirty source checkout: {target}')
        return
    if target.exists() and any(target.iterdir()):
        raise RuntimeError(f'Refusing nonempty non-Git source directory: {target}')
    target.mkdir(parents=True, exist_ok=True)
    run(['git', 'init', target], env=env)
    run(['git', '-C', target, 'remote', 'add', 'origin', source['url']], env=env)
    run(['git', '-C', target, 'fetch', '--depth=1', 'origin', source['commit']], env=env)
    run(['git', '-C', target, 'checkout', '--detach', source['commit']], env=env)


def plan(profile):
    environment = ROOT / 'research/cc-v2-environment'
    directory = ROOT / '.venv-transfer' if profile == 'basic' else environment / 'venv'
    return {'profile': profile, 'root': str(ROOT), 'environment': str(environment), 'venv': str(directory),
            'python': str(python_path(directory)),
            'requirements': str(REFERENCE / 'requirements.txt' if profile == 'basic' else HERE / 'requirements-portable.lock'),
            'source_checkouts': {} if profile == 'basic' else json.loads((HERE / 'sources.json').read_text(encoding='utf-8')),
            'limits': 'Integration dependency projection is not a tested Linux/GPU installation; failures must be reported.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['basic', 'integration'], default='basic')
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    configuration = plan(args.profile)
    if args.plan:
        print(json.dumps(configuration, indent=2))
        return
    if sys.version_info[:2] != (3, 12):
        raise SystemExit('Use Python 3.12 for the recorded dependency baseline; rerun using that interpreter.')
    directory = Path(configuration['venv'])
    python = python_path(directory)
    if not python.is_file():
        print('Creating isolated Python environment: ' + str(directory), flush=True)
        venv.EnvBuilder(with_pip=True).create(directory)
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE='1', GIT_TERMINAL_PROMPT='0', PYTHONUTF8='1')
    env['PATH'] = str(python.parent) + os.pathsep + env.get('PATH', '')
    run([python, '-m', 'pip', 'install', '-r', configuration['requirements']], env=env)
    if args.profile == 'integration':
        run([python, '-m', 'pip', 'install', '-r', REFERENCE / 'requirements-test.txt'], env=env)
        sources = configuration['source_checkouts']
        for source in sources.values():
            checkout(ROOT / source['location'], source, env)
        for name in ('agent-core', 'mapie'):
            run([python, '-m', 'pip', 'install', '--no-deps', '-e', ROOT / sources[name]['location']], env=env)
    if args.run:
        if args.profile == 'basic':
            for name in ('check_cc_protocol_examples.py', 'check_cc_request_examples.py'):
                run([python, ROOT / 'AI4Research-Notebook/Resources/tools' / name], env=env)
        else:
            run([python, REFERENCE / 'run_experiments.py', '--environment', configuration['environment']], env=env)
    print('Setup completed for ' + args.profile + '. Revalidate each target-specific capability separately.', flush=True)


if __name__ == '__main__':
    main()
