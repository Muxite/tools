"""Protect authority classification against sibling-prefix and baseline mistakes."""
import json
from pathlib import Path
import tempfile
import unittest
from migrate import authority, source_role, load_registry

class SourceRegistryTests(unittest.TestCase):
    def test_preserved_implementation_is_linked(self):
        role = source_role(Path('AI4Research-Development/jiuwenswarm-m1/jiuwenswarm/research/runner.py'))
        self.assertTrue(role['maintained'])
        self.assertEqual(role['authority'], 'pinned-implementation-source')

    def test_captured_record_does_not_become_approval(self):
        self.assertEqual(authority(Path('AI4Research-Development/jiuwenswarm-m1-review-d3d7f56/docs/code/Missions/M1/TASKS.md')), 'captured-coding-record')

    def test_longest_prefix_and_directory_boundary(self):
        self.assertEqual(authority(Path('jiuwenswarm/docs/architecture/design-package/README.md')), 'maintained-design')
        self.assertEqual(authority(Path('jiuwenswarm/docs/architecture/design-package-old/README.md')), 'repository-source')
        self.assertFalse(source_role(Path('jiuwenswarm/docs/architecture/notes/idea.md'))['maintained'])
        self.assertFalse(source_role(Path('jiuwenswarm-copy/docs/architecture/design-package/README.md'))['maintained'])

    def test_unknown_fails_to_historical(self):
        self.assertFalse(source_role(Path('unreviewed/approved.md'))['maintained'])

    def test_bad_registry_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'registry.json'
            for prefix in ('../outside', '/outside', 'C:/outside'):
                p.write_text(json.dumps({'version': 1, 'rules': [{'id':'x','prefix':prefix}]}))
                with self.assertRaises(ValueError): load_registry(p)

if __name__ == '__main__': unittest.main()
