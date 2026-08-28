#!/usr/bin/env python3
"""Render source-prepped.png as an animated monochrome ASCII SVG.

Each text row is revealed by a horizontal wipe (SMIL clip-path animation),
staggered top-to-bottom. Plays once and freezes.

Usage: python scripts/make_ascii_svg.py
Writes: dog-ascii.svg
"""
import html

import numpy as np
from PIL import Image

# bright -> dark
RAMP = " .`:-=+*cs#%@"
COLS = 78
CHAR_W = 7.2          # monospace advance at font-size 12
LINE_H = 12.5
FG = "#c9d1d9"
BG = "#0d1117"
ROW_STAGGER = 0.045   # seconds between row reveals
WIPE_DUR = 0.5        # seconds for one row's wipe


def main():
    img = Image.open("source-prepped.png").convert("L")
    # Character cells are ~2x taller than wide, so halve the vertical sampling
    rows = int(img.height / img.width * COLS * 0.5)
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = np.array(img)

    lines = []
    for r in range(rows):
        chars = []
        for c in range(COLS):
            # bright (255) -> index 0 (space); dark -> dense glyphs
            idx = int((255 - px[r, c]) / 256 * len(RAMP))
            chars.append(RAMP[min(idx, len(RAMP) - 1)])
        lines.append("".join(chars).rstrip())

    width = round(COLS * CHAR_W + 20)
    height = round(rows * LINE_H + 20)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="12">',
        f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    ]

    for i, line in enumerate(lines):
        if not line:
            continue
        y = 10 + (i + 1) * LINE_H - 3
        begin = f"{i * ROW_STAGGER:.3f}s"
        clip_id = f"c{i}"
        out.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="{y - LINE_H:.1f}" width="0" height="{LINE_H + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{width}" begin="{begin}" '
            f'dur="{WIPE_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        out.append(
            f'<text x="10" y="{y:.1f}" xml:space="preserve" fill="{FG}" '
            f'clip-path="url(#{clip_id})">{html.escape(line)}</text>'
        )

    out.append("</svg>")
    svg = "\n".join(out)
    with open("dog-ascii.svg", "w") as f:
        f.write(svg)
    print(f"wrote dog-ascii.svg ({width}x{height}, {rows} rows, {len(svg)} bytes)")


if __name__ == "__main__":
    main()
