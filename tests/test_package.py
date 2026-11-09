import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import unittest


def public_text_files(root):
    """Cover every tracked UTF-8 file; also work in downloaded source archives."""
    if (root / '.git').exists() and shutil.which('git'):
        result = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'],
                                capture_output=True, check=True)
        paths = [root / os.fsdecode(name) for name in result.stdout.split(b'\0') if name]
    else:
        paths = []
        excluded = {'.git', '.venv', '__pycache__', 'outputs', 'source-media'}
        for folder, directories, files in os.walk(root):
            directories[:] = [name for name in directories if name not in excluded]
            paths.extend(Path(folder) / name for name in files
                         if not name.startswith(('.env', 'creator.local.')))
    for path in sorted(paths):
        try:
            path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        yield path


def privacy_findings(text, identities=()):
    """Return categories only: never expose the text or matched secret values."""
    patterns = {
        'machine-path': r'(?i)\b[a-z]:[\\/]|/' + r'(?:Users|home)/[^/\s]+/',
        'email': r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
        'credential': (
            r'\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|'
            r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}|\bAKIA[A-Z0-9]{16}\b|'
            r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
            r'\b(?:api[_-]?key|password|access[_-]?token|client[_-]?secret)'
            r'\s*[:=]\s*[\'\"][A-Za-z0-9_/-]{12,}[\'\"]'),
        'account-identity': r'(?im)^\s*(?:account|username|handle)\s*[:=]\s*[\'\"]?@[\w-]{3,}',
    }
    findings = [category for category, pattern in patterns.items()
                if re.search(pattern, text, flags=re.IGNORECASE)]
    if any(identity and len(identity) >= 4 and identity.casefold() in text.casefold()
           for identity in identities):
        findings.append('local-identity')
    return findings


class PrivacyGateRegressionTests(unittest.TestCase):
    def scanner(self):
        scanner = globals().get('privacy_findings')
        self.assertTrue(callable(scanner), 'Privacy scanner is missing')
        return scanner

    def test_detects_paths_identity_and_credentials_without_echoing_values(self):
        scanner = self.scanner()
        samples = [
            ('Z' + ':/private/data.txt', 'machine-path'),
            ('/' + 'Users/example/private.txt', 'machine-path'),
            ('person' + '@' + 'example.invalid', 'email'),
            ('gh' + 'p_' + 'A' * 36, 'credential'),
            ('sk' + '-proj-' + 'B' * 40, 'credential'),
            ('AK' + 'IA' + 'C' * 16, 'credential'),
            ('api_' + 'key = "' + 'D' * 28 + '"', 'credential'),
            ('PRIVATE PERSON in a draft', 'local-identity'),
        ]
        for sample, category in samples:
            findings = scanner(sample, identities=('Private Person',))
            self.assertIn(category, findings)
            self.assertNotIn(sample, str(findings))

    def test_generic_copy_and_public_attribution_allowed(self):
        scanner = self.scanner()
        self.assertEqual(scanner('Copyright (c) 2026 JoyM1993. No API keys required.'), [])

    def test_discovery_includes_rendering_reference_and_tests(self):
        discover = globals().get('public_text_files')
        self.assertTrue(callable(discover), 'Tracked text discovery is missing')
        files = {path.relative_to(ROOT).as_posix() for path in discover(ROOT)}
        self.assertIn('xiaohongshu-graphic-notes-skill/references/rendering.md', files)
        self.assertIn('tests/test_package.py', files)
        self.assertIn('.gitignore', files)

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'xiaohongshu-graphic-notes-skill/SKILL.md'


class PackageTests(unittest.TestCase):
    def test_skill_frontmatter_and_relative_references(self):
        self.assertTrue(SKILL.is_file(), 'Skill entry missing')
        text = SKILL.read_text(encoding='utf-8')
        front = text.split('---', 2)[1]
        fields = dict(line.split(': ', 1) for line in front.strip().splitlines())
        self.assertEqual(fields['name'], 'xiaohongshu-graphic-notes')
        self.assertTrue(fields['description'].startswith('Use when'))
        for link in re.findall(r'\]\(([^)]+)\)', text):
            self.assertTrue((SKILL.parent / link).is_file(), link)

    def test_fictional_demo_and_documented_cli(self):
        path = ROOT / 'examples/fictional-note.json'
        self.assertTrue(path.is_file(), 'Demo missing')
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(data['handle'], '虚构练习室')
        self.assertEqual(len(data['pages']), 3)
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('python xiaohongshu-graphic-notes-skill/scripts/render_notes.py --input examples/fictional-note.json --out outputs/demo', readme)
        self.assertIn('Pillow', readme)

    def test_required_policy_and_license(self):
        self.assertTrue((ROOT / 'LICENSE').is_file(), 'License missing')
        self.assertIn('Copyright (c) 2026 JoyM1993', (ROOT / 'LICENSE').read_text())
        skill = SKILL.read_text(encoding='utf-8')
        for phrase in ('watermark', 'disclosure', 'Never auto-post', 'rights', 'approval'):
            self.assertIn(phrase, skill)
        ignore = (ROOT / '.gitignore').read_text()
        for pattern in ('outputs/', '.env*', 'creator.local.*', 'source-media/'):
            self.assertIn(pattern, ignore)

    def test_privacy_gate_covers_all_publishable_text(self):
        generic = {'root', 'user', 'admin', 'administrator', 'runner', 'default'}
        identities = {os.environ.get('USERNAME', ''), os.environ.get('USER', ''), Path.home().name}
        identities = {value for value in identities if value.casefold() not in generic}
        findings = []
        for path in public_text_files(ROOT):
            categories = privacy_findings(path.read_text(encoding='utf-8'), identities)
            if categories:
                findings.append(f'{path.relative_to(ROOT).as_posix()}: {", ".join(categories)}')
        self.assertEqual(findings, [], 'Privacy scan failed (filenames/categories only)')


if __name__ == '__main__':
    unittest.main()
