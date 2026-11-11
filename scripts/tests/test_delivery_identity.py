"""CLI contract tests; fixtures are not delivered manufacturing projects."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'delivery_identity.py'


class DeliveryIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='身份 空格_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '参数 源.txt').write_bytes(b'abc')
        self.spec = {'revision': 'R01', 'entries': [
            {'id': 'source', 'role': 'source', 'path': '参数 源.txt', 'version': 'v1'}]}
        self.selection = self.root / '选择.json'
        self.manifest = self.root / '身份.json'
        self.save_spec()

    def save_spec(self):
        self.selection.write_text(json.dumps(self.spec, ensure_ascii=False), encoding='utf-8')

    def cli(self, action, *extra):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPT), action,
            '--root', str(self.root), '--selection', str(self.selection),
            '--manifest', str(self.manifest), *extra], capture_output=True, text=True,
            encoding='utf-8')

    def test_capture_and_verify_unicode_identity(self):
        r = self.cli('capture')
        self.assertEqual(r.returncode, 0, r.stderr)
        m = json.loads(self.manifest.read_text(encoding='utf-8'))
        self.assertEqual(m['entries'][0]['sha256'],
            'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
        r = self.cli('verify')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['entries'][0]['status'], 'matched')

    def test_changed_missing_and_legacy_unverified_are_distinct(self):
        self.assertEqual(self.cli('capture').returncode, 0)
        source = self.root / '参数 源.txt'
        source.write_bytes(b'abd')
        r = self.cli('verify')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)['entries'][0]['status'], 'changed')
        source.unlink()
        r = self.cli('verify')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)['entries'][0]['status'], 'missing')
        self.manifest.unlink()
        r = self.cli('capture')
        self.assertEqual(r.returncode, 1)
        self.assertIsNone(json.loads(self.manifest.read_text(encoding='utf-8'))['entries'][0]['sha256'])
        source.write_bytes(b'abc')
        r = self.cli('verify')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)['entries'][0]['status'], 'unverified')

    def test_pairing_and_revision_changes_cannot_pass_same_bytes(self):
        (self.root / '副本.txt').write_bytes(b'abc')
        self.assertEqual(self.cli('capture').returncode, 0)
        for field, value in [('path', '副本.txt'), ('role', 'delivery'), ('version', 'v2')]:
            with self.subTest(field=field):
                old = self.spec['entries'][0][field]
                self.spec['entries'][0][field] = value
                self.save_spec()
                r = self.cli('verify')
                self.assertEqual(r.returncode, 1)
                self.assertEqual(json.loads(r.stdout)['entries'][0]['status'], 'changed')
                self.spec['entries'][0][field] = old
        self.spec['revision'] = 'R02'
        self.save_spec()
        self.assertEqual(self.cli('verify').returncode, 1)

    def test_root_context_change_cannot_pass_identical_bytes(self):
        self.assertEqual(self.cli('capture').returncode, 0)
        other = self.root / 'other root'
        other.mkdir()
        (other / '参数 源.txt').write_bytes(b'abc')
        original = self.manifest.read_bytes()
        r = self.cli('verify', '--root', str(other))
        self.assertEqual(r.returncode, 1, r.stderr)
        report = json.loads(r.stdout)
        self.assertFalse(report['context_matched'])
        self.assertEqual(report['entries'][0]['status'], 'matched')
        self.assertEqual(self.manifest.read_bytes(), original)

    def test_added_and_removed_entries_are_changed(self):
        self.assertEqual(self.cli('capture').returncode, 0)
        self.spec['entries'].append({'id': 'extra', 'role': 'reference',
            'path': '参数 源.txt', 'version': 'unknown'})
        self.save_spec()
        r = self.cli('verify')
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual({e['id']: e['status'] for e in json.loads(r.stdout)['entries']},
                         {'source': 'matched', 'extra': 'changed'})
        self.spec['entries'].pop(0)
        self.save_spec()
        r = self.cli('verify')
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(all(e['status'] == 'changed' for e in json.loads(r.stdout)['entries']))

    def test_bad_selection_is_rejected_without_output(self):
        import copy
        valid = copy.deepcopy(self.spec)
        cases = [dict(valid, entries=[]), dict(valid, entries=valid['entries'] * 2)]
        for field, value in [('role', 'banana'), ('id', ''), ('path', ''),
                             ('path', '../outside'), ('path', 'C:relative.txt'),
                             ('path', 'file.txt:stream'), ('path', 'NUL'),
                             ('relates_to', ['unknown'])]:
            changed = copy.deepcopy(valid)
            changed['entries'][0][field] = value
            cases.append(changed)
        for case in cases:
            with self.subTest(case=case):
                self.spec = case
                self.save_spec()
                self.manifest.unlink(missing_ok=True)
                r = self.cli('capture')
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse(self.manifest.exists())

    def test_output_never_overwrites_or_materializes_an_input(self):
        self.manifest.write_bytes(b'sentinel')
        self.assertEqual(self.cli('capture').returncode, 2)
        self.assertEqual(self.manifest.read_bytes(), b'sentinel')
        self.manifest = self.root / '参数 源.txt'
        self.assertEqual(self.cli('capture').returncode, 2)
        self.assertEqual(self.manifest.read_bytes(), b'abc')
        self.spec['entries'][0]['path'] = 'missing.txt'
        self.save_spec()
        self.manifest = self.root / 'missing.txt'
        self.assertEqual(self.cli('capture').returncode, 2)
        self.assertFalse(self.manifest.exists())
        self.manifest = self.selection
        original = self.selection.read_bytes()
        self.assertEqual(self.cli('capture').returncode, 2)
        self.assertEqual(self.selection.read_bytes(), original)

    def test_linked_roles_absolute_windows_paths_and_read_only_verification(self):
        for ident, role in [('params', 'parameters'), ('mesh', 'export'),
                            ('package', 'delivery'), ('audit', 'evidence'), ('view', 'image'),
                            ('choice', 'decision')]:
            path = self.root / (ident + ' 中文.txt')
            path.write_bytes(ident.encode())
            self.spec['entries'].append({'id': ident, 'role': role, 'path': str(path),
                'version': 'v1', 'relates_to': ['source']})
        self.save_spec()
        self.assertEqual(self.cli('capture').returncode, 0)
        original = self.manifest.read_bytes()
        self.assertEqual(self.cli('verify').returncode, 0)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.spec['entries'][-1]['relates_to'] = ['mesh']
        self.save_spec()
        self.assertEqual(self.cli('verify').returncode, 1)
        self.assertEqual(self.manifest.read_bytes(), original)

    def test_malformed_manifest_and_no_baseline_never_pass(self):
        self.assertEqual(self.cli('verify').returncode, 2)
        self.assertFalse(self.manifest.exists())
        self.assertEqual(self.cli('capture').returncode, 0)
        valid = json.loads(self.manifest.read_text(encoding='utf-8'))
        import copy
        cases = [dict(valid, entries=[]), dict(valid, schema=99),
                 dict(valid, entries=valid['entries'] * 2)]
        bad = copy.deepcopy(valid)
        bad['entries'][0]['sha256'] = 'not-a-hash'
        cases.append(bad)
        for case in cases:
            self.manifest.write_text(json.dumps(case), encoding='utf-8')
            self.assertEqual(self.cli('verify').returncode, 2)

    def test_directory_input_is_unverified_not_missing_or_matched(self):
        (self.root / 'directory').mkdir()
        self.spec['entries'][0]['path'] = 'directory'
        self.save_spec()
        r = self.cli('capture')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)['entries'][0]['status'], 'unverified')

    def test_guidance_entrypoints_and_boundaries_exist(self):
        skill = SCRIPT.parent.parent
        entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
        org = (skill / 'references/project-organization.md').read_text(encoding='utf-8')
        review = (skill / 'references/requirements-and-review.md').read_text(encoding='utf-8')
        self.assertIn('project-organization.md#轻量交付身份清单', entry)
        self.assertIn('requirements-and-review.md#实质选图留档', entry)
        for text in ['## 轻量交付身份清单', '../scripts/delivery_identity.py',
                     '不能证明来源依赖', '未验证', '不覆盖', '不强制迁目录']:
            self.assertIn(text, org)
        for text in ['## 实质选图留档', '用户原话', '未选不等于反感',
                     'Agent建议不是用户选择', '选形不授权打印', '不固定候选套数']:
            self.assertIn(text, review)


if __name__ == '__main__':
    unittest.main()
