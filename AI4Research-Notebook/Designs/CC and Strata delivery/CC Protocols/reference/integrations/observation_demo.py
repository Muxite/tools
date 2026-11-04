"""Export optional observations from a saved run without rerunning its producer."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host, encoded


def export(host, report):
    with tempfile.TemporaryDirectory() as directory:
        metrics = Path(directory)/'metrics.json'
        metrics.write_bytes(encoded(report['measurement']))
        artifact = host.put_artifact(metrics)
    instance = report['instance']
    return {'format': 'cc-observation/1',
            'subject': {'release': instance['release'], 'instance': instance['id'], 'capability': instance['capability']},
            'source': {'id': 'example.http-client', 'kind': 'observer'},
            'coverage': {'status': 'partial', 'scope': report['measurement']['scope'],
                         'reason': 'External client measurement only; engine internals uninstrumented, no trace/span coverage claimed'},
            'signals': [{'kind': 'metrics', 'format': 'application/json', 'artifact': artifact}]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run-report', type=Path, required=True)
    parser.add_argument('--store', type=Path, required=True); parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = export(Host(args.store), json.loads(args.run_report.read_text(encoding='utf-8')))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_bytes(encoded(result))
    print(json.dumps({'format': result['format'], 'coverage': result['coverage']['status'], 'producer_rerun': False}))
