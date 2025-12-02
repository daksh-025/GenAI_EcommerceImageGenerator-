# Fonts Directory

Place Japanese font files in this directory for accurate text rendering.

## Recommended Fonts

1. **Noto Sans CJK** (Recommended)
   - Download from: https://www.google.com/get/noto/
   - Files: `NotoSansCJK-Regular.ttc` or `NotoSansJP-Regular.otf`
   - Supports Japanese, Chinese, and Korean characters

2. **Meiryo** (Windows default)
   - Usually available on Windows systems
   - Path: `C:\Windows\Fonts\meiryo.ttc`
   - Copy to this directory if needed

3. **Yu Gothic** (Windows default)
   - Usually available on Windows systems
   - Path: `C:\Windows\Fonts\yugothic.ttf`

## Font File Formats Supported

- `.ttf` (TrueType Font)
- `.otf` (OpenType Font)
- `.ttc` (TrueType Collection)

## Installation

1. Download a Japanese font (Noto Sans CJK recommended)
2. Place the font file(s) in this `fonts/` directory
3. Update font path in `config.py` if using a different filename

## Configuration

The system automatically tries to load fonts in this order:
1. `fonts/NotoSansCJK-Regular.ttc` (default)
2. `fonts/NotoSansJP-Regular.otf` (fallback 1)
3. `fonts/Meiryo.ttf` (fallback 2)
4. System default font (last resort, may not support Japanese)

## Note

Font files are typically large (several MB). They are excluded from git by default (see `.gitignore`).

If no Japanese fonts are found, the system will use the default system font, which may not render Japanese characters correctly.

