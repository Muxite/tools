"""Demonstrate usable results first, optional acceptance later, and session reuse."""
import argparse
import json
from pathlib import Path
import sys

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host


def run(store):
    host = Host(store)
    bundle = REFERENCE / 'examples/easy_results'
    production = host.run(bundle, 'produce', {'task': 'Produce a result', 'context': {'score': 0.25, 'new_metadata': {'free': ['form', 'JSON']}}})
    assert production['state'] == 'succeeded' and production['assessment']['verdict'] == 'not_requested', production
    saved = production['outputs']['result']
    review = host.run(bundle, 'review', {'result': saved, 'policy': {'minimum_score': 0.8}})
    assert review['state'] == 'succeeded' and review['outputs']['assessment']['accepted'] is False, review
    assert host.artifact_path(saved).is_file()
    return {'scope': 'Synthetic deterministic usability demonstration; no LLM or scientific quality claim',
            'production': production, 'later_acceptance': review,
            'producer_rerun_for_verification': False, 'review_input_sha256': saved['sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = run(args.store)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'state': report['production']['state'], 'verification': report['production']['assessment']['verdict'],
                      'later_accepted': report['later_acceptance']['outputs']['assessment']['accepted'], 'producer_rerun': False}))
