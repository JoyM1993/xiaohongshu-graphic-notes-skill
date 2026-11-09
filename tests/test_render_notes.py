import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'xiaohongshu-graphic-notes-skill/scripts/render_notes.py'


class RenderTests(unittest.TestCase):
    def invoke(self, folder, data, *extra):
        source = folder / 'input.json'
        source.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return subprocess.run([sys.executable, str(SCRIPT), '--input', str(source),
                               '--out', str(folder / 'output'), *extra],
                              capture_output=True, text=True)

    def test_two_pages_without_images_and_anonymous_handle(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.invoke(folder, {'pages': [
                {'title': 'A fictional reading corner', 'body': 'Try a small first step.'},
                {'title': '虚构阅读角', 'body': '先整理一本书，再留十分钟阅读。'}]})
            self.assertEqual(result.returncode, 0, result.stderr)
            files = sorted((folder / 'output').glob('*.png'))
            self.assertEqual(len(files), 2)
            for path in files:
                with Image.open(path) as image:
                    self.assertEqual(image.size, (1344, 1792))
            with zipfile.ZipFile(folder / 'output/notes.zip') as archive:
                self.assertEqual(archive.namelist(), ['01.png', '02.png'])

    def test_rejects_image_escape_and_absolute_path(self):
        with tempfile.TemporaryDirectory() as temp:
            for image in ('../outside.png', str(Path(temp) / 'outside.png')):
                result = self.invoke(Path(temp), {'pages': [
                    {'title': 'Sample', 'body': 'Text', 'image': image}]})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('inside the input directory', result.stderr)

    def test_local_image_with_caption(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            Image.new('RGB', (300, 200), '#80aaa0').save(folder / 'own.png')
            result = self.invoke(folder, {'handle': 'Fictional workshop', 'pages': [
                {'title': 'A local image', 'body': 'Original synthetic asset.',
                 'image': 'own.png', 'caption': 'Self-made placeholder'}]})
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_pages_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.invoke(Path(temp), {'pages': []})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('pages must be a non-empty list', result.stderr)

    def test_long_handle_rejected_instead_of_overlapping_footer(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.invoke(Path(temp), {'handle': '宽' * 40,
                                 'pages': [{'title': 'Title', 'body': 'Text'}]})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('handle does not fit', result.stderr)

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            data = {'pages': [{'title': 'Original', 'body': 'Text'}]}
            self.assertEqual(self.invoke(folder, data).returncode, 0)
            old = (folder / 'output/01.png').read_bytes()
            result = self.invoke(folder, {'pages': [{'title': 'New', 'body': 'Text'}]})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('new or empty directory', result.stderr)
            self.assertEqual(old, (folder / 'output/01.png').read_bytes())

    def test_validation_errors_are_clear(self):
        cases = [({'pages': [{'title': '', 'body': 'Text'}]}, 'non-empty title'),
                 ({'pages': [{'title': 'Title', 'body': 'Text'}], 'palette': {'bad': '#fff'}}, 'palette accepts'),
                 ({'pages': [{'title': 'Title', 'body': 'Text', 'caption': 12}]}, 'caption must')]
        with tempfile.TemporaryDirectory() as temp:
            for data, message in cases:
                result = self.invoke(Path(temp), data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_explicit_missing_font_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.invoke(Path(temp), {'pages': [{'title': 'Title', 'body': 'Text'}]},
                                 '--font', str(Path(temp) / 'missing.ttf'))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Configured font file does not exist', result.stderr)

    def test_overflow_rejected_without_partial_output(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.invoke(folder, {'pages': [
                {'title': 'Readable first', 'body': 'Short text.'},
                {'title': 'Too much', 'body': 'Long content ' * 2000}]})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('does not fit', result.stderr)
            self.assertEqual(list((folder / 'output').glob('*.png')), [])


if __name__ == '__main__':
    unittest.main()
