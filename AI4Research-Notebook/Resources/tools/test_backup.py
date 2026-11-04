import tempfile
import unittest
from pathlib import Path
from backup import backup,verify

class BackupTests(unittest.TestCase):
    def test_roundtrip_and_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); vault=root/'vault';vault.mkdir()
            (vault/'note.md').write_text('Exact text\n',encoding='utf-8')
            (vault/'asset.bin').write_bytes(b'\x00\x01\xff')
            (vault/'.env').write_text('NOT_A_REAL_SECRET=test')
            (vault/'.git'/'objects').mkdir(parents=True)
            (vault/'.git'/'objects'/'fixture').write_text('local history stays in the repository')
            result=backup(root/'backup',vault)
            self.assertEqual(result['files'],2)
            self.assertEqual(verify(result['verified'])['files'],2)
            with Path(result['verified']).open('ab') as f:f.write(b'tamper')
            with self.assertRaises(ValueError):verify(result['verified'])
    def test_no_recursive_backup(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):backup(Path(t)/'backups',Path(t))

if __name__=='__main__':unittest.main()
