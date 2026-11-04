"""Validate and summarize three-arm accuracy ledgers without collapsing abstention into error.

Input: JSONL, one row per case/repetition/arm. This analyzes evidence, never generates it.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

ARMS = {'raw', 'plain_checked', 'cc_checked'}

def validate_row(row):
    required = {'case_id', 'repetition', 'arm', 'answerability', 'candidate', 'gate',
                'release', 'scientific_result', 'failure_reason', 'elapsed_seconds', 'usage',
                'input_sha256', 'configuration_sha256', 'prompt_ref', 'output_ref'}
    missing = required - row.keys()
    if missing: raise ValueError('Missing fields: ' + ', '.join(sorted(missing)))
    if row['arm'] not in ARMS: raise ValueError('Unknown arm')
    for key, allowed in {
        'answerability': {'answerable', 'unanswerable', 'unknown'},
        'candidate': {'correct', 'incorrect', 'abstain', 'unjudged', 'none'},
        'gate': {'accepted', 'blocked', 'not_applied', 'error'},
        'release': {'answer', 'abstention', 'none'},
        'scientific_result': {'PASS', 'FAIL', 'INCONCLUSIVE', 'not_applicable'},
    }.items():
        if row[key] not in allowed: raise ValueError('Invalid ' + key)
    if row['arm'] != 'raw' and row['release'] != 'none' and row['gate'] != 'accepted':
        raise ValueError('Checked arm cannot release without gate acceptance')
    if row['gate'] in {'blocked', 'error'} and row['release'] != 'none':
        raise ValueError('Blocked/error output was released')
    if row['release'] == 'answer' and row['candidate'] in {'none', 'abstain'}:
        raise ValueError('No substantive candidate to release')
    if row['release'] == 'abstention' and row['candidate'] != 'abstain':
        raise ValueError('Abstention requires an abstaining candidate')
    if row['failure_reason'] is not None and row['release'] != 'none':
        raise ValueError('Operational failure cannot also release')
    if row['gate'] == 'error' and not row['failure_reason']:
        raise ValueError('Gate error requires operational reason')
    if row['candidate'] == 'none' and not row['failure_reason']:
        raise ValueError('Missing candidate needs explicit operational failure')
    if row['elapsed_seconds'] is not None and row['elapsed_seconds'] < 0:
        raise ValueError('Negative elapsed time')
    for key in ('input_sha256', 'configuration_sha256'):
        value = row[key]
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Invalid ' + key)
    if not row['case_id'] or not row['prompt_ref'] or not row['output_ref']:
        raise ValueError('Evidence references and case identity required')
    if not isinstance(row['repetition'], int) or row['repetition'] < 1:
        raise ValueError('Repetition must be a positive integer')

def summarize(rows):
    groups = collections.defaultdict(dict)
    metrics = {arm: collections.Counter() for arm in sorted(ARMS)}
    for row in rows:
        validate_row(row)
        group = groups[(row['case_id'], row['repetition'])]
        if row['arm'] in group: raise ValueError('Duplicate paired observation')
        group[row['arm']] = row
        m = metrics[row['arm']]
        m['runs'] += 1
        candidate, gate, release = (row[k] for k in ('candidate', 'gate', 'release'))
        m['candidate_' + candidate] += 1
        m['gate_' + gate] += 1
        if release == 'answer':
            m['answers_released'] += 1
            m['released_' + candidate] += 1
            if candidate == 'correct' and row['scientific_result'] in {'FAIL', 'INCONCLUSIVE'}:
                m['correct_scientific_negative_released'] += 1
        if candidate == 'incorrect' and gate == 'blocked': m['incorrect_blocked'] += 1
        if candidate == 'correct' and gate == 'blocked': m['correct_blocked'] += 1
        if candidate == 'abstain':
            category = {'answerable':'avoidable', 'unanswerable':'appropriate', 'unknown':'unjudged'}[row['answerability']]
            m['abstention_' + category] += 1
            if release == 'abstention': m['abstention_released_' + category] += 1
        if row['failure_reason'] is not None: m['operational_failures'] += 1
        if row['elapsed_seconds'] is None: m['elapsed_unavailable'] += 1
        if row['usage'] is None: m['usage_unavailable'] += 1
    paired = []
    for (case, rep), group in sorted(groups.items()):
        # Configuration is the matched comparison envelope, not arm-specific prompts.
        for key in ('input_sha256', 'configuration_sha256', 'answerability'):
            if len({r[key] for r in group.values()}) != 1:
                raise ValueError('Unmatched ' + key + ': ' + case)
        paired.append({'case_id':case, 'repetition':rep, 'complete':set(group)==ARMS,
                       'arms':{arm:{k:r[k] for k in ('candidate','gate','release','failure_reason')} for arm,r in sorted(group.items())}})
    def rate(n, d): return {'numerator':n, 'denominator':d, 'value':n/d if d else None}
    output = {}
    for arm, m in metrics.items():
        judged_released = m['released_correct'] + m['released_incorrect']
        judged_candidates = m['candidate_correct'] + m['candidate_incorrect']
        output[arm] = {'counts':dict(m),
            'candidate_accuracy':rate(m['candidate_correct'], judged_candidates),
            'released_accuracy':rate(m['released_correct'], judged_released),
            'substantive_answer_coverage':rate(m['answers_released'],m['runs']),
            'incorrect_release_rate':rate(m['released_incorrect'],m['runs']),
            'gate_false_accept_rate':rate(m['released_incorrect'],m['candidate_incorrect']) if arm!='raw' else None,
            'gate_false_reject_rate':rate(m['correct_blocked'],m['candidate_correct']) if arm!='raw' else None}
    return {'arms':output, 'paired_outcomes':paired,
            'incomplete_pairs':sum(not p['complete'] for p in paired),
            'interpretation':'Descriptive only. No significance or CC improvement claim is inferred; unjudged outputs, failures and abstentions remain visible.'}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger',type=Path)
    args=parser.parse_args()
    print(json.dumps(summarize([json.loads(s) for s in args.ledger.read_text(encoding='utf-8').splitlines() if s.strip()]),indent=2))
