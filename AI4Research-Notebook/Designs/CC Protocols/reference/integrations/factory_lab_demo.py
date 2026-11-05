"""Factory native product -> CC inspection in Lab, with zero product CCs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host


def product(path, tamper=False):
    # A CPU-inspectable schema2 fixture, not a built Strata binary or inference product.
    payload = b'fixture-only: not an executable Strata engine\n'
    manifest = {'schema_version': 2, 'id': 'strata-engine', 'name': 'strata-engine', 'version': '0.0.1',
                'platform': 'windows-x86_64', 'backend': 'cpu', 'archs': [],
                'build_id': 'cc-native-handoff-synthetic-fixture', 'entrypoint': 'fixture-engine.txt',
                'signature': None, 'files': [{'path': 'fixture-engine.txt', 'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload)}]}
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('engine-component.json', json.dumps(manifest, sort_keys=True))
        archive.writestr('fixture-engine.txt', payload if not tamper else b'x' * len(payload))
    return manifest


def run(root, source):
    root.mkdir(parents=True, exist_ok=True)
    artifact = root / 'native-product.zip'
    manifest = product(artifact)
    host = Host(root / 'store')
    release = host.seal(REFERENCE / 'examples' / 'factory_lab')
    reference = host.put_artifact(artifact)
    result = host.call(release, 'inspect_product', {'product': reference, 'data': {'strata_source': str(source)}})
    assert result['state'] == 'succeeded', result
    assert result['outputs']['inspection']['product_sha256'] == reference['sha256']
    tampered = root / 'tampered-native-product.zip'
    product(tampered, tamper=True)
    rejected = host.call(release, 'inspect_product', {'product': host.put_artifact(tampered), 'data': {'strata_source': str(source)}})
    assert rejected['state'] == 'failed' and rejected['reason'] == 'PRODUCT_INVALID', rejected
    return {'scope': 'Synthetic CPU-inspectable native manifest handoff; no engine loading, inference, GPU or performance claim',
            'factory_product_manifest': manifest, 'factory_product_artifact': reference,
            'inspection_receipt': result, 'tampered_payload_rejected': rejected}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--strata-source', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root, args.strata_source)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'state': result['inspection_receipt']['state'], 'tamper': result['tampered_payload_rejected']['state']}))
