# Local rendering reference

Install Python 3.11+ and `Pillow==12.3.0` in a virtual environment. Run from the installed skill directory:

```sh
python scripts/render_notes.py --input /path/to/note.json --out /path/to/new-output --font /path/to/cjk-font.ttf
```

All paths above are placeholders. Use actual user-approved locations. `--font` is optional when a suitable font is installed; `NOTES_FONT` is an alternative. Font search covers common Windows, Linux, and macOS fonts. Chinese requires CJK glyph coverage. This repository distributes no fonts. Use only fonts with appropriate rights, and visually verify glyphs after rendering.

## Input contract

Save UTF-8 JSON. Here is a fictional minimal input (no image required):

```json
{
  "pages": [{"title": "虚构阅读角", "body": "从一本书开始。"}]
}
```

Required: `pages`, a non-empty list with at most 20 objects, each with non-empty string `title` and `body`. Optional page fields: `caption` (short string) and `image` (relative local image path within the JSON directory). Absolute image paths and directory/symlink escapes are rejected. Images are contained without cropping, preserving all edges and attribution marks. The renderer does not verify legal rights: the agent and user must do that first.

Optional root fields: `handle` (label, at most 40 characters and subject to pixel-width fit), `palette` (object with `background`, `ink`, `accent` Pillow color strings). The default is cream, dark green, and terracotta. Palette contrast requires manual review.

Explicit newlines are preserved; text wraps by measured pixel width. Split long pages if rendering reports overflow. Output must be new or empty; existing work is never overwritten. A successful render creates 1344 × 1792 images named `01.png`, `02.png`, etc. and `notes.zip` with those pages. Inspect every image at full and mobile-preview sizes before local delivery. No network calls, account actions, or posting are performed.
