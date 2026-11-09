---
name: xiaohongshu-graphic-notes
description: Use when a user wants Xiaohongshu image notes, Chinese social carousel copy, or locally rendered portrait graphic cards from an approved topic or draft.
---

# Xiaohongshu Graphic Notes

Create original, readable image notes as local drafts. Preserve the user's intent and get approval before turning an unconfirmed direction into finished pages. This skill does not access accounts or publish content.

## Workflow

1. **Select:** collect the audience, topic, purpose, desired page count, and constraints. Offer two or three original angles if the topic is open. Ask the user to select one before writing the full copy. If a finished brief is already approved, use it directly.
2. **Confirm copy:** propose a cover title, page-by-page title/body, closing question, and optional post caption. Use [narrative structures](references/structure.md). Ask for approval of this copy before rendering; do not invent personal experiences, statistics, testimonials, or guarantees.
3. **Check evidence and rights:** separate facts from opinions. Ask for supporting sources for material factual claims; label unknowns or omit them. Record each image's source, permission/license, and required attribution. Use only authorized assets. With no assets, use text and geometry. Never remove, cover, or crop a watermark or attribution to disguise ownership. Preserve required credit. Review applicable platform disclosure requirements for AI-assisted content; never suggest evasion.
4. **Render:** use [the JSON schema and CLI guide](references/rendering.md) and [renderer](scripts/render_notes.py). Keep asset paths relative to the JSON directory. Pass a suitable installed font explicitly when needed. Never guess a private workspace or fetch files from unrelated folders. The guide includes a wholly invented input.
5. **Inspect:** open every numbered PNG. Check actual glyphs (no missing-glyph boxes), text size, wrapping, page sequence, margins, contrast, image proportions, and attribution. Reject clipped or crowded pages. Split long copy instead of shrinking it beyond readability. Recheck at a small mobile preview size. Use a fresh output folder for each revision.
6. **Deliver locally:** provide the numbered PNGs and ZIP, approved caption, asset/source notes, and any unresolved review items. Explicitly say these are local drafts, not published posts. Never auto-post or claim an account action occurred. The user performs final fact, rights, disclosure, and platform review before manually publishing.

## Quick checks

| Situation | Action |
| --- | --- |
| User says "just publish it" | Deliver local drafts; this package has no publishing capability. |
| No authorized image | Use original text/geometric cards. |
| Font lacks Chinese glyphs | Ask for/install a suitable licensed CJK font, then rerender and inspect. |
| Unsupported claim or uncertain identity | Ask for evidence or remove/qualify the claim before approval. |
| Copy does not fit | Split the page; obtain approval for changed copy. |

Common mistakes: rendering unapproved copy, treating a web-found picture as licensed, imitating a named creator's distinctive style, relying only on a successful command without looking at images, and presenting drafts as published content.
