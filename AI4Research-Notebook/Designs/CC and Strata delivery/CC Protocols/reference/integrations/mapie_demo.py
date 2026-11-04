"""Repeatable, tiny MAPIE pipeline through the CC host and artifact edges."""
import argparse
import json
from pathlib import Path
import shutil
import sys
from urllib.parse import unquote, urlparse

import numpy as np

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host


def synthetic_data():
    rng = np.random.default_rng(20261104)
    x = rng.uniform(-3, 3, (160, 1))
    y = 2.5 * x[:, 0] + 1.2 + rng.normal(0, 0.5, len(x))
    return {'train_x': x[:60].tolist(), 'train_y': y[:60].tolist(),
            'calibrate_x': x[60:110].tolist(), 'calibrate_y': y[60:110].tolist()}, {
            'x': x[110:].tolist()}, y[110:].tolist()


def run(store):
    host = Host(store)
    release = host.seal(REFERENCE / 'examples' / 'mapie')
    fit_data, prediction_data, labels = synthetic_data()
    fit = host.call(release, 'fit_calibrate', {'data': fit_data})
    assert fit['state'] == 'succeeded', fit
    predict = host.call(release, 'predict_intervals', {'model': fit['outputs']['model'], 'data': prediction_data})
    assert predict['state'] == 'succeeded', predict
    evaluate = host.call(release, 'evaluate', {'intervals': predict['outputs']['intervals'], 'labels': labels})
    assert evaluate['state'] == 'succeeded', evaluate
    assert 0.75 <= evaluate['outputs']['coverage'] <= 1.0, evaluate
    assert evaluate['outputs']['mean_width'] > 0, evaluate
    shifted_labels = [value + 1000 for value in labels]
    negative = host.call(release, 'evaluate', {'intervals': predict['outputs']['intervals'], 'labels': shifted_labels})
    assert negative['state'] == 'succeeded' and negative['outputs']['coverage'] == 0.0, negative
    return {'release': release, 'sample_sizes': {'train': 60, 'calibrate': 50, 'test': 50},
            'seed': 20261104, 'implementation': 'MAPIE SplitConformalRegressor.fit/conformalize/predict_interval',
            'fit': fit, 'predict': predict, 'evaluate': evaluate,
            'negative_scientific_case': {'description': 'Labels shifted by +1000; valid execution with zero empirical coverage.',
                                         'receipt': negative}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = run(args.store)
    if args.report:
        evidence_dir = args.report.parent / 'mapie-artifacts'
        evidence_dir.mkdir(exist_ok=True)
        report['portable_artifact_evidence'] = {}
        for stage, port in [('fit', 'model'), ('predict', 'intervals')]:
            artifact = report[stage]['outputs'][port]
            parsed_path = unquote(urlparse(artifact['uri']).path)
            if sys.platform == 'win32' and parsed_path.startswith('/'):
                parsed_path = parsed_path[1:]
            target = evidence_dir / (port + ('.pkl' if port == 'model' else '.json'))
            shutil.copyfile(parsed_path, target)
            report['portable_artifact_evidence'][port] = {'path': str(target), 'sha256': artifact['sha256']}
        fit_data, prediction_data, labels = synthetic_data()
        (evidence_dir / 'inputs.json').write_text(json.dumps({'fit': fit_data, 'predict': prediction_data,
            'labels': labels, 'negative_labels': [value + 1000 for value in labels]}, indent=2), encoding='utf-8')
        args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
