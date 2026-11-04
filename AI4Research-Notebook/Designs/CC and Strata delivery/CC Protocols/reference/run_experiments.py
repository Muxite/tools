"""Run the bounded CC v2 experiments in the prepared isolated environment."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

REFERENCE = Path(__file__).resolve().parent
WORKSPACE = Path(__file__).resolve().parents[5]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', type=Path, default=WORKSPACE / 'research/cc-v2-environment')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--skip-image', action='store_true')
    args = parser.parse_args()
    python = args.environment / 'venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if not python.is_file():
        raise SystemExit('Prepare the environment described in integrations/README.md, then pass --environment.')
    root = args.output or args.environment / ('run-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    root.mkdir(parents=True, exist_ok=True)
    stages = [
        ('local-regressions', ['-m', 'unittest', '-q', 'test_ccv2', 'test_products', 'test_source_build', 'test_unified']),
        ('mapie', ['integrations/mapie_demo.py', '--store', str(root / 'mapie-store'), '--report', str(root / 'mapie-report.json')]),
        ('scientific-replays', ['integrations/mapie_negative_replays.py', '--store', str(root / 'scientific-store'), '--report', str(root / 'mapie-replays-report.json')]),
        ('upstream-mcp', ['integrations/upstream_mcp_demo.py', '--store', str(root / 'mcp-store'), '--report', str(root / 'mcp-report.json')]),
        ('upstream-native-task', ['integrations/upstream_native_demo.py', '--root', str(root / 'native'), '--report', str(root / 'native-report.json')]),
        ('native-product-handoff', ['integrations/factory_lab_demo.py', '--root', str(root / 'factory-lab'), '--strata-source', str(WORKSPACE / 'Strata'), '--report', str(root / 'factory-lab-report.json')]),
        ('product-upstream-mcp', ['integrations/product_mcp_demo.py', '--directory', str(root / 'product-mcp'), '--report', str(root / 'product-mcp-report.json')]),
        ('source-product-lifecycle', ['integrations/product_demo.py', '--directory', str(root / 'product'), '--report', str(root / 'product-report.json')]),
    ]
    results = []
    for name, command in stages:
        start = time.time()
        print('Running ' + name, flush=True)
        with (root / (name + '.stdout.log')).open('wb') as out, (root / (name + '.stderr.log')).open('wb') as err:
            try:
                proc = subprocess.run([str(python), *command], cwd=REFERENCE, stdout=out, stderr=err, timeout=180)
                result = {'stage': name, 'status': 'passed' if proc.returncode == 0 else 'failed', 'exit_code': proc.returncode}
            except subprocess.TimeoutExpired:
                result = {'stage': name, 'status': 'failed', 'reason': 'HARNESS_TIMEOUT'}
        result['seconds'] = round(time.time() - start, 3)
        results.append(result)
        print(name + ': ' + result['status'], flush=True)
    if not args.skip_image:
        from ccv2 import Host
        image = root / 'image-bundle'
        shutil.copytree(REFERENCE / 'examples/portable', image, dirs_exist_ok=True)
        shutil.copyfile(image / 'image.yaml', image / 'cc.yaml')
        host = Host(root / 'image-store', python=str(python))
        release = host.seal(image)
        receipt = host.call(release, 'trim', {'text': '  portable  '}, timeout=30)
        (root / 'image-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        results.append({'stage': 'actual-image', 'status': 'passed' if receipt['state'] == 'succeeded' else 'blocked',
                        'reason': receipt['reason'], 'worker_executed': receipt['state'] == 'succeeded'})
        print('actual-image: ' + results[-1]['status'], flush=True)
    summary = {'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scope': 'deterministic feasibility checks; no live LLM, full deployment or GPU inference',
               'environment': str(args.environment), 'python': str(python), 'results': results}
    (root / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('Reports: ' + str(root), flush=True)
    if any(r['status'] == 'failed' for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
