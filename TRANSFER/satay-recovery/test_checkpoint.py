"""No hardware, no live state: verify the checkpoint whitelist and SQLite copies."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from checkpoint import checkpoint


class CheckpointTest(unittest.TestCase):
    def test_consistent_whitelisted_databases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'factory'
            (source / 'ccstore').mkdir(parents=True)
            for relative in ('factory.sqlite', 'ccstore/calls.sqlite'):
                with sqlite3.connect(source / relative) as db:
                    db.execute('CREATE TABLE evidence(value TEXT)')
                    db.execute('INSERT INTO evidence VALUES (?)', ('fixture',))
            (source / 'auth.json').write_text('do not copy')
            result = checkpoint(source, root / 'backups')
            manifest = json.loads((result / 'manifest.json').read_text())
            self.assertEqual(len(manifest['files']), 2)
            for item in manifest['files']:
                self.assertEqual(hashlib.sha256((result / item['path']).read_bytes()).hexdigest(), item['sha256'])
                with sqlite3.connect(result / item['path']) as db:
                    self.assertEqual(db.execute('SELECT value FROM evidence').fetchone(), ('fixture',))
            self.assertFalse((result / 'auth.json').exists())
            self.assertFalse(list((root / 'backups').glob('.checkpoint-*')))

    def test_missing_database_leaves_no_published_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'factory'; source.mkdir()
            with self.assertRaises(FileNotFoundError):
                checkpoint(source, root / 'backups')
            self.assertEqual(list((root / 'backups').iterdir()), [])


if __name__ == '__main__':
    unittest.main()
