# Xiaohongshu Graphic Notes Skill

An original, portable Agent Skill and local Pillow renderer for Chinese portrait image notes. It produces 1344 × 1792 PNGs and a ZIP. It does not sign in, upload, create cloud drafts, or publish posts. The included three-page reading-corner example is fictional and uses no external images.

## Requirements and quick start

Python 3.11+ and Pillow 12.3.0. In a virtual environment, from this repository's root:

```sh
python -m pip install -r requirements.txt
python xiaohongshu-graphic-notes-skill/scripts/render_notes.py --input examples/fictional-note.json --out outputs/demo
python -m unittest discover -s tests -v
```

Use a new or empty output directory. Review `outputs/demo/01.png` through `03.png` and `notes.zip`; outputs are intentionally ignored by Git. Rerun into a different folder for revisions. No accounts, API keys, private configuration, or network access are needed during rendering.

## Install the Agent Skill

Copy the entire `xiaohongshu-graphic-notes-skill` folder into the skill directory supported by your agent. For Codex, one option is `~/.agents/skills/`. Keep `scripts/` and `references/` with `SKILL.md`; the installed folder is self-contained and includes its own rendering reference and minimal example. Alternatively, keep the complete repository together and load its `SKILL.md` directly. Install Python dependencies separately; installation does not execute the renderer automatically.

Ask: “Use xiaohongshu-graphic-notes to draft a three-page carousel about a fictional reading corner. Confirm the copy before rendering.”

## Fonts

The renderer searches installed Microsoft YaHei/SimHei on Windows, Noto Sans CJK on Linux, and PingFang on macOS, then Latin-only alternatives. Fonts are not distributed here. A Latin fallback can render English but may show boxes for Chinese: a successful command does not prove glyph coverage. Install a legally usable CJK font through your OS, or supply a local font file:

```sh
python xiaohongshu-graphic-notes-skill/scripts/render_notes.py --input examples/fictional-note.json --out outputs/custom-font --font /path/to/font.ttf
```

Alternatively set `NOTES_FONT` to a font file. `--font` takes precedence. Font licensing is separate from this project's MIT license. Always inspect all Chinese glyphs and small mobile previews.

## JSON input

Read UTF-8 JSON. Relative image paths resolve from the input file's parent directory, not the current working directory. Absolute image paths, `..` escapes, and symlinks escaping that directory are rejected. No URL images are fetched. The renderer contains images with original proportions and keeps all edges; it does not crop images.

| Field | Meaning |
| --- | --- |
| `pages` | Required non-empty list, maximum 20 pages |
| `pages[].title` | Required non-empty string; explicit newlines allowed |
| `pages[].body` | Required non-empty string; explicit newlines allowed |
| `pages[].caption` | Optional short string; source/credit can go here |
| `pages[].image` | Optional authorized local image path inside the JSON directory |
| `handle` | Optional label, maximum 40 characters and must fit footer width; omitted means anonymous |
| `palette` | Optional object with `background`, `ink`, `accent` Pillow color strings |

See [the fictional input](examples/fictional-note.json). The default palette is cream, dark green, and terracotta. Text is measured and wrapped by pixel width. Long content is rejected instead of silently clipped; shorten or split it. Prefer two-line titles and short bodies. With an image, less body space is available. Palette contrast and font glyph coverage require human review. Delivery names are `01.png`, `02.png`, etc., plus `notes.zip` containing only the current numbered pages. Failed validation/rendering does not publish a partial set.

## Editorial and rights boundaries

The [Skill](xiaohongshu-graphic-notes-skill/SKILL.md) covers topic selection, copy approval, fact checks, image rights, rendering, visual review, and local handoff. This is not a platform trend or policy service. Check current platform rules and applicable AI disclosure requirements before manual posting. Do not remove or conceal third-party watermarks or source credits. Only use assets you own or have permission to reuse, and preserve required attribution. Do not include private material in commits. No identifiable real people, accounts, creator imitation, or third-party art is included in the demo.

## License

MIT, copyright 2026 JoyM1993. See [LICENSE](LICENSE). This covers this repository's original code, prose, and fictional demo, not user-supplied assets, fonts, or the Pillow dependency.
