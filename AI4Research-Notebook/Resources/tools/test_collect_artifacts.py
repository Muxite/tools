"""Verify that library receipts reject changed files and substituted ZIP members."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import collect_artifacts as collector


class ArtifactReceiptTests(unittest.TestCase):
    def verify(self, root, manifest):
        (root / 'Resources').mkdir(exist_ok=True)
        (root / 'Resources/artifact-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        with patch.object(collector, 'VAULT', root), patch.object(sys, 'argv', ['collect_artifacts', '--verify']), redirect_stdout(io.StringIO()):
            collector.main()

    def test_exact_file_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'report.bin').write_bytes(b'recorded bytes')
            self.verify(root, {'artifacts': [{'destination': 'report.bin', 'sha256': hashlib.sha256(b'recorded bytes').hexdigest()}], 'packages': []})

    def test_same_size_file_substitution_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'report.bin').write_bytes(b'changed!')
            with self.assertRaises(SystemExit) as raised:
                self.verify(root, {'artifacts': [{'destination': 'report.bin', 'sha256': hashlib.sha256(b'original').hexdigest()}], 'packages': []})
            self.assertEqual(raised.exception.code, 1)

    def test_package_member_substitution_is_rejected_even_with_matching_outer_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'source.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('source.txt', b'substituted member')
            record = {'destination': 'source.zip', 'sha256': collector.sha(path), 'source_files': [{'path': 'source.txt', 'sha256': hashlib.sha256(b'original member').hexdigest()}]}
            with self.assertRaises(SystemExit) as raised:
                self.verify(root, {'artifacts': [], 'packages': [record]})
            self.assertEqual(raised.exception.code, 1)


class CollectionIntegrityTests(unittest.TestCase):
    def test_direct_document_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / 'prd.txt.snapshot'
            document.write_bytes(b'original product input\r\n')
            manifest = {'reference_documents': [{'destination': document.name, 'sha256': hashlib.sha256(document.read_bytes()).hexdigest()}]}
            self.assertEqual(collector.verify_destinations(manifest, root)['failures'], [])
            document.write_bytes(b'changed input\r\n')
            self.assertEqual(collector.verify_destinations(manifest, root)['failures'], [document.name])

    def test_missing_direct_document_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = {'reference_documents': [{'destination': 'missing.txt.snapshot', 'sha256': '0' * 64}]}
            self.assertEqual(collector.verify_destinations(manifest, Path(directory))['failures'], ['missing.txt.snapshot'])


if __name__ == '__main__':
    unittest.main()
