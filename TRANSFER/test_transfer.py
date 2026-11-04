"""Portability checks independent of the source-machine repositories."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

import bootstrap
import verify_transfer


class TransferTests(unittest.TestCase):
    def test_plan_is_root_relative_and_has_exact_pins(self):
        configuration = bootstrap.plan('integration')
        self.assertEqual(Path(configuration['environment']), bootstrap.ROOT / 'research/cc-v2-environment')
        self.assertEqual(len(configuration['source_checkouts']), 4)
        for source in configuration['source_checkouts'].values():
            self.assertEqual(len(source['commit']), 40)
            self.assertNotIn('m50066326', source['location'])

    def test_verifier_rejects_missing_changed_duplicate_and_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            previous = verify_transfer.ROOT
            verify_transfer.ROOT = Path(temp).resolve()
            try:
                p = verify_transfer.ROOT / 'note.md'; p.write_text('original', encoding='utf-8')
                row = {'path': 'note.md', 'sha256': verify_transfer.digest(p)}
                self.assertEqual(verify_transfer.verify_rows([row]), [])
                p.write_text('changed', encoding='utf-8')
                self.assertTrue(verify_transfer.verify_rows([row]))
                self.assertTrue(verify_transfer.verify_rows([dict(row, path='../escape')]))
                self.assertTrue(verify_transfer.verify_rows([row, row]))
                self.assertTrue(verify_transfer.verify_rows([dict(row, path='missing')]))
            finally:
                verify_transfer.ROOT = previous


if __name__ == '__main__':
    unittest.main()
