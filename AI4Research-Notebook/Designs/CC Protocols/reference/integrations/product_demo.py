"""Actual synthetic source/diff/build/application experiment; no Strata or GPU claim."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host
from source_build import materialize


def fixture(directory, host):
    directory = Path(directory); directory.mkdir(parents=True)
    repository = directory/'repository'; repository.mkdir()
    example = REFERENCE/'examples/http_product'
    (repository/'server.py').write_bytes((example/'payload/server.py').read_bytes())
    (repository/'.gitignore').write_text('dist/\n', encoding='utf-8')
    (repository/'dependencies.json').write_text('{"python":">=3.10","packages":[],"runtime":"stdlib"}\n', encoding='utf-8')
    (repository/'build.py').write_text("from pathlib import Path\nimport shutil\nPath('dist').mkdir(exist_ok=True)\nshutil.copyfile('server.py', 'dist/server.py')\n", encoding='utf-8')
    def git(*arguments):
        return subprocess.check_output(['git', '-c', 'core.autocrlf=false', *arguments], cwd=repository, stderr=subprocess.PIPE)
    git('init'); git('add', '.')
    git('-c', 'user.name=CC synthetic fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'Synthetic base')
    base = git('rev-parse', 'HEAD').decode().strip()
    source = (repository/'server.py').read_text(encoding='utf-8').replace('FACTOR = 1', 'FACTOR = 2')
    (repository/'server.py').write_text(source, encoding='utf-8', newline='\n')
    git('add', 'server.py')
    patch = directory/'candidate.patch'; patch.write_bytes(git('diff', '--cached', '--binary', '--full-index', base))
    tree = git('write-tree').decode().strip()
    template = directory/'template'; template.mkdir()
    for name in ('cc.yaml', 'inspect.py', 'api.json'):
        shutil.copyfile(example/name, template/name)
    change = {'format': 'cc-source-change/1', 'repository': str(repository), 'base': base,
              'patch': host.put_artifact(patch), 'tree': tree,
              'build': {'command': ['{python}', 'build.py'], 'lock': 'dependencies.json', 'output': 'dist'}}
    (directory/'source-change.json').write_text(json.dumps(change, indent=2), encoding='utf-8')
    return template, change


def run(directory):
    directory = Path(directory)
    host = Host(directory/'store', session_grants=['process.exec', 'network.listen'])
    template, change = fixture(directory/'input', host)
    built = materialize(host, template, change, directory/'product', trusted_build=True)
    inspected = host.call(built['release'], 'inspect', {})
    instance = host.start(built['release'], 'api', key='synthetic-candidate-start')
    try:
        assert instance['state'] == 'running' and instance['readiness'] == 'ready', instance
        started = time.perf_counter()
        with urllib.request.urlopen(instance['endpoints']['api']+'compute?x=3', timeout=3) as response:
            result = json.load(response)
        http_client_ms = (time.perf_counter()-started)*1000
        assert result == {'value': 6.0, 'factor': 2}, result
        assert inspected['outputs']['report']['source_tree'] == change['tree'], inspected
    finally:
        stopped = host.stop(instance['id'])
    return {'evidence_level': 'Actual local Git reconstruction, native build, native application lifecycle and HTTP invocation',
            'limits': 'Synthetic CPU service; no inference engine, live model, container or hardware measurement',
            'source_change': change, 'materialization': built, 'inspection': inspected,
            'instance': instance, 'response': result, 'stopped': stopped,
            'measurement': {'http_client_ms': http_client_ms,
                            'scope': 'One loopback HTTP request including client overhead; synthetic CPU fixture, not engine latency'}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True); args = parser.parse_args()
    report = run(args.directory)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'state': report['instance']['state'], 'readiness': report['instance']['readiness'],
                      'response': report['response'], 'stopped': report['stopped']['state']}))
