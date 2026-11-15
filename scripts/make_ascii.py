#!/usr/bin/env python3
"""Convert source-prepped.png to the ASCII portrait shown in the whoami pane.

Only needed when the photo changes; render_panes.py draws the saved text.

Usage: python scripts/make_ascii.py
Writes: data/dog-ascii.txt
"""
import numpy as np
from PIL import Image

# bright -> dark
RAMP = " .`:-=+*cs#%@"
COLS = 78


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

    while lines and not lines[0]:
        lines.pop(0)
    with open("data/dog-ascii.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote data/dog-ascii.txt ({len(lines)} rows)")


if __name__ == "__main__":
    main()
