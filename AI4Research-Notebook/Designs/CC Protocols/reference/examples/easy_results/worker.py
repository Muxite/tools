"""Synthetic usability example, not a scientific method or semantic verifier."""
import json
from pathlib import Path
import sys


def run(packet):
    values = packet['inputs']
    if packet['capability'] == 'produce':
        result = {'task': values['task'], 'score': values['context'].get('score', 0.25), 'details': values['context']}
        output = Path(packet['output_dir']) / 'result.json'
        output.write_bytes(json.dumps(result).encode('utf-8'))
        return {'outcome': 'ok', 'outputs': {'result': {'path': output.name}}}
    if packet['capability'] == 'review':
        result = json.loads(Path(values['result']['path']).read_text(encoding='utf-8'))
        minimum = values['policy'].get('minimum_score', 0.5)
        score = result['score']
        if type(score) not in (int, float) or type(minimum) not in (int, float):
            raise ValueError('Review needs numerical score and minimum_score')
        return {'outcome': 'ok', 'outputs': {'assessment': {'accepted': score >= minimum, 'score': score, 'minimum_score': minimum}}}
    raise ValueError('Unknown capability')


if __name__ == '__main__':
    try:
        print(json.dumps(run(json.load(sys.stdin))))
    except Exception as error:
        print(json.dumps({'outcome': 'error', 'error': {'code': 'EXAMPLE_ERROR', 'message': str(error)}}))
        raise SystemExit(1)
