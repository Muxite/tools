import unittest
from accuracy_ledger import summarize

def row(**changes):
    value=dict(case_id='case-1',repetition=1,arm='cc_checked',answerability='answerable',
               candidate='correct',gate='accepted',release='answer',scientific_result='FAIL',
               failure_reason=None,elapsed_seconds=None,usage=None,input_sha256='a'*64,
               configuration_sha256='b'*64,prompt_ref='prompt.txt',output_ref='output.json')
    value.update(changes)
    return value

class AccuracyLedgerTests(unittest.TestCase):
    def test_correct_negative_is_answer_not_failure(self):
        result=summarize([row()])['arms']['cc_checked']['counts']
        self.assertEqual(result['correct_scientific_negative_released'],1)
        self.assertNotIn('operational_failures',result)

    def test_blocked_wrong_and_blocked_correct_are_separate(self):
        rows=[row(candidate='incorrect',gate='blocked',release='none'),
              row(case_id='case-2',gate='blocked',release='none')]
        counts=summarize(rows)['arms']['cc_checked']['counts']
        self.assertEqual(counts['incorrect_blocked'],1)
        self.assertEqual(counts['correct_blocked'],1)
        self.assertNotIn('operational_failures',counts)

    def test_abstention_cannot_win_by_silence(self):
        rows=[row(candidate='abstain',release='abstention'),
              row(case_id='case-2',candidate='abstain',release='abstention',answerability='unanswerable')]
        arm=summarize(rows)['arms']['cc_checked']
        self.assertIsNone(arm['released_accuracy']['value'])
        self.assertEqual(arm['substantive_answer_coverage']['value'],0)
        self.assertEqual(arm['counts']['abstention_avoidable'],1)
        self.assertEqual(arm['counts']['abstention_appropriate'],1)

    def test_failures_not_wrong_answers(self):
        value=row(candidate='none',gate='error',release='none',failure_reason='interrupted')
        arm=summarize([value])['arms']['cc_checked']
        self.assertEqual(arm['counts']['operational_failures'],1)
        self.assertEqual(arm['incorrect_release_rate']['value'],0)
        self.assertIsNone(arm['candidate_accuracy']['value'])

    def test_release_requires_gate(self):
        with self.assertRaises(ValueError): summarize([row(gate='blocked')])

    def test_mismatch_and_duplicate_rejected(self):
        with self.assertRaises(ValueError): summarize([row(),row()])
        with self.assertRaises(ValueError): summarize([row(),row(arm='plain_checked',input_sha256='c'*64)])

    def test_missing_arm_remains_visible(self):
        self.assertEqual(summarize([row()])['incomplete_pairs'],1)

if __name__=='__main__': unittest.main()
