#!/usr/bin/env python3
"""Render local image notes. No network calls, account access, or posting."""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

SIZE = (1344, 1792)
MARGIN = 112
WIDTH = SIZE[0] - 2 * MARGIN
DEFAULT_PALETTE = {'background': '#F7F3E9', 'ink': '#203D36', 'accent': '#CE6B43'}


def discover_font(explicit=None):
    """Prefer CJK-capable installed fonts; never bundle third-party fonts."""
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ValueError('Configured font file does not exist')
        return str(path)
    fonts = Path(os.environ.get('WINDIR', '/nonexistent')) / 'Fonts'
    candidates = [fonts / 'msyh.ttc', fonts / 'simhei.ttf',
                  Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
                  Path('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'),
                  Path('/System/Library/Fonts/PingFang.ttc'),
                  Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
                  fonts / 'arial.ttf']
    for path in candidates:
        if path.is_file():
            return str(path)
    raise ValueError('No suitable font found; supply --font with a local font file')


def wrap(text, draw, font, width):
    """Wrap CJK and Latin text by measured pixels; preserve paragraph breaks."""
    lines = []
    for paragraph in text.split('\n'):
        line = ''
        for char in paragraph:
            if draw.textlength(line + char, font=font) > width and line:
                # Prefer a Latin word boundary when available.
                cut = line.rfind(' ')
                if cut > len(line) // 2:
                    lines.append(line[:cut])
                    line = line[cut + 1:] + char
                else:
                    lines.append(line)
                    line = char
            else:
                line += char
        lines.append(line.rstrip())
    return lines


def text_block(draw, text, font, y, bottom, color, step):
    lines = wrap(text, draw, font, WIDTH)
    if y + len(lines) * step > bottom:
        raise ValueError('Text does not fit; shorten it or split this page')
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=color, anchor='lt')
        y += step
    return y


def local_asset(root, value):
    path = Path(value)
    resolved = (root / path).resolve()
    if path.is_absolute() or not resolved.is_relative_to(root):
        raise ValueError('Images must be relative paths inside the input directory')
    if not resolved.is_file():
        raise ValueError('Local image file does not exist')
    return resolved


def validate(data, root):
    if not isinstance(data, dict):
        raise ValueError('Input must be a JSON object')
    pages = data.get('pages')
    if not isinstance(pages, list) or not pages:
        raise ValueError('pages must be a non-empty list')
    if len(pages) > 20:
        raise ValueError('At most 20 pages are supported')
    if not isinstance(data.get('handle', ''), str) or len(data.get('handle', '')) > 40:
        raise ValueError('handle must be a string of at most 40 characters')
    palette = data.get('palette', {})
    if not isinstance(palette, dict) or set(palette) - set(DEFAULT_PALETTE):
        raise ValueError('palette accepts background, ink, and accent only')
    colors = {**DEFAULT_PALETTE, **palette}
    for color in colors.values():
        if not isinstance(color, str):
            raise ValueError('Palette colors must be color strings')
        ImageColor.getrgb(color)
    for page in pages:
        if not isinstance(page, dict):
            raise ValueError('Each page must be an object')
        for field in ('title', 'body'):
            if not isinstance(page.get(field), str) or not page[field].strip():
                raise ValueError('Each page needs non-empty title and body strings')
            if len(page[field]) > 20000:
                raise ValueError('Text does not fit; split this page')
        if not isinstance(page.get('caption', ''), str):
            raise ValueError('caption must be a string')
        if 'image' in page:
            if not isinstance(page['image'], str) or not page['image']:
                raise ValueError('image must be a relative path string')
            local_asset(root, page['image'])
    return pages, colors


def render(page, root, font_path, palette, handle, index, count):
    canvas = Image.new('RGB', SIZE, palette['background'])
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(font_path, 88)
    body_font = ImageFont.truetype(font_path, 50)
    small_font = ImageFont.truetype(font_path, 30)
    if draw.textlength(handle, font=small_font) > WIDTH - 220:
        raise ValueError('handle does not fit; shorten the footer label')
    draw.rounded_rectangle((MARGIN, 112, MARGIN + 92, 128), radius=8, fill=palette['accent'])
    draw.text((MARGIN, 158), 'NOTES / %02d' % index, font=small_font, fill=palette['accent'], anchor='lt')
    y = text_block(draw, page['title'], title_font, 244, 700, palette['ink'], 116) + 60
    has_image = 'image' in page
    bottom = 980 if has_image else 1510
    text_block(draw, page['body'], body_font, y, bottom, palette['ink'], 80)
    if has_image:
        with Image.open(local_asset(root, page['image'])) as source:
            # Contain, do not crop: retain all edges and attribution marks.
            asset = ImageOps.contain(ImageOps.exif_transpose(source).convert('RGB'), (WIDTH, 480))
            canvas.paste(asset, ((SIZE[0] - asset.width) // 2, 1020 + (480 - asset.height) // 2))
    if page.get('caption'):
        text_block(draw, page['caption'], small_font, 1524, 1620, palette['ink'], 44)
    draw.line((MARGIN, 1660, SIZE[0] - MARGIN, 1660), fill=palette['accent'], width=2)
    draw.text((MARGIN, 1692), handle, font=small_font, fill=palette['ink'], anchor='lt')
    draw.text((SIZE[0] - MARGIN, 1692), f'{index:02d} / {count:02d}', font=small_font,
              fill=palette['ink'], anchor='rt')
    return canvas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='UTF-8 JSON input')
    parser.add_argument('--out', type=Path, required=True, help='New or empty output directory')
    parser.add_argument('--font', help='Local .ttf/.otf/.ttc font with required glyph coverage')
    args = parser.parse_args(argv)
    try:
        source = args.input.resolve()
        root = source.parent
        data = json.loads(source.read_text(encoding='utf-8'))
        pages, colors = validate(data, root)
        font = discover_font(args.font or os.environ.get('NOTES_FONT'))
        output = args.out.resolve()
        if output.exists() and (not output.is_dir() or any(output.iterdir())):
            raise ValueError('Output must be a new or empty directory')
        # Finish validation and all rendering before writing delivery files.
        with tempfile.TemporaryDirectory() as temp:
            staged = Path(temp)
            for i, page in enumerate(pages, 1):
                image = render(page, root, font, colors, data.get('handle', ''), i, len(pages))
                image.save(staged / f'{i:02d}.png')
            with zipfile.ZipFile(staged / 'notes.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
                for png in sorted(staged.glob('*.png')):
                    archive.write(png, png.name)
            output.mkdir(parents=True, exist_ok=True)
            for file in staged.iterdir():
                (output / file.name).write_bytes(file.read_bytes())
        print(f'Rendered {len(pages)} pages and notes.zip')
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
