"""Replay mathematically invalid interval inputs and confidence metadata drift."""
import argparse
import json
from pathlib import Path
import pickle
import sys
import tempfile

import numpy as np
from mapie.regression import SplitConformalRegressor
from sklearn.linear_model import LinearRegression

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host
from mapie_demo import synthetic_data


def run(store):
    host = Host(store)
    release = host.seal(REFERENCE / 'examples' / 'mapie')
    cases = {'broadcast_upper': {'lower': [0, 0], 'upper': [[1], [10]], 'labels': [0.5, 5]},
             'inverted_bounds': {'lower': [2, 2], 'upper': [1, 1], 'labels': [1.5, 1.5]},
             'mismatched_count': {'lower': [0, 0], 'upper': [1], 'labels': [0, 0]},
             'nonfinite_bounds': {'lower': [0, 0], 'upper': [float('inf'), 1], 'labels': [0, 0]},
             'nonfinite_labels': {'lower': [0, 0], 'upper': [1, 1], 'labels': [0, float('nan')]},
             'empty': {'lower': [], 'upper': [], 'labels': []}}
    rejected = {}
    with tempfile.TemporaryDirectory(prefix='cc-mapie-replays-') as tmp:
        tmp = Path(tmp)
        for name, case in cases.items():
            artifact_path = tmp / (name + '.json')
            artifact_path.write_text(json.dumps({'lower': case['lower'], 'upper': case['upper']}), encoding='utf-8')
            try:
                result = host.call(release, 'evaluate', {'intervals': host.put_artifact(artifact_path), 'labels': case['labels']})
            except ValueError as error:
                assert name == 'nonfinite_labels', (name, error)
                rejected[name] = {'state': 'rejected_before_call', 'reason': 'Nonfinite values cannot be encoded as strict JSON',
                                  'message': str(error)}
                continue
            assert result['state'] in ('failed', 'blocked'), result
            rejected[name] = result
        data, points, _ = synthetic_data()
        model = SplitConformalRegressor(LinearRegression(), confidence_level=0.5, prefit=False)
        model.fit(np.asarray(data['train_x']), np.asarray(data['train_y']))
        model.conformalize(np.asarray(data['calibrate_x']), np.asarray(data['calibrate_y']))
        model_path = tmp / 'confidence-50.pkl'
        model_path.write_bytes(pickle.dumps(model))
        result = host.call(release, 'predict_intervals', {'model': host.put_artifact(model_path), 'data': points})
        assert result['state'] == 'succeeded', result
        intervals = json.loads(host.artifact_path(result['outputs']['intervals']).read_text(encoding='utf-8'))
        assert intervals['confidence_level'] == 0.5, intervals
    return {'reviewer_reported_previous_failures': ['Fixed confidence0.9 label on fitted0.5 model',
             'Broadcast upper bounds caused unintended2x2 coverage', 'Inverted intervals returned negative width'],
            'release': release, 'invalid_cases': rejected,
            'confidence_metadata_replay': {'receipt': result, 'observed_confidence_level': intervals['confidence_level']}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.store)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'rejected_cases': list(result['invalid_cases']), 'confidence_level': 0.5}))
