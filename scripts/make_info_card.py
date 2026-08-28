#!/usr/bin/env python3
"""Generate the neofetch-style info card SVG.

Lines fade-and-slide in with staggered timing; plays once and freezes.
Set STATIC=1 to skip animation (useful for preview rasterization).

Usage: python scripts/make_info_card.py
Writes: info-card.svg
"""
import html
import os

BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
DIM = "#8b949e"
KEY = "#39d353"
ACCENT = "#58a6ff"
TITLE = "#f0f6fc"

W, H = 490, 508
LINE_H = 24
STATIC = os.environ.get("STATIC") == "1"

# (key, value) rows; key "" = plain line, key None = blank spacer
ROWS = [
    ("stink-o@github", None),
    ("----------------", None),
    ("Now", "Homefield — self-hosted AI image + music studio"),
    ("Also", "Cheesybread — small-batch bakery shop build"),
    ("", ""),
    ("Stack", "TypeScript / JavaScript / Python"),
    ("Tools", "Godot, Docker, Node, KDE / Linux"),
    ("", ""),
    ("Projects", "box3d-godot — 3D physics for Godot (126 stars)"),
    ("", "PausePoint — human-in-the-loop agent gate"),
    ("", "PathLab — pathfinding + sorting visualizer"),
    ("", "ascii-renderer — real-time video-to-ASCII"),
    ("", "plasma-claude-usage — KDE usage widget"),
    ("", ""),
    ("Motto", "ship weird things that work"),
]


def line(x, y, parts, idx):
    tspans = "".join(
        f'<tspan fill="{c}">{html.escape(t)}</tspan>' for t, c in parts
    )
    anim = ""
    if not STATIC:
        begin = f"{0.15 + idx * 0.12:.2f}s"
        anim = (
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin}" dur="0.45s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-14 0" to="0 0" '
            f'begin="{begin}" dur="0.45s" fill="freeze"/>'
        )
        return f'<text x="{x}" y="{y}" xml:space="preserve" opacity="0">{tspans}{anim}</text>'
    return f'<text x="{x}" y="{y}" xml:space="preserve">{tspans}</text>'


def main():
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13">',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
        # title bar
        f'<circle cx="22" cy="20" r="6" fill="#ff5f56"/>'
        f'<circle cx="42" cy="20" r="6" fill="#ffbd2e"/>'
        f'<circle cx="62" cy="20" r="6" fill="#27c93f"/>',
        f'<text x="{W//2}" y="25" text-anchor="middle" fill="{DIM}">~/whoami</text>',
        f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="{BORDER}"/>',
    ]

    y = 72
    idx = 0
    for key, val in ROWS:
        if val is None:  # header / divider lines
            color = TITLE if "@" in key else BORDER
            out.append(line(24, y, [(key, color)], idx))
        elif key == "" and val == "":
            y += LINE_H // 2
            continue
        elif key == "":
            out.append(line(24, y, [(" " * 10, FG), (val, FG)], idx))
        else:
            pad = key.ljust(8)
            out.append(line(24, y, [(pad, KEY), ("> ", ACCENT), (val, FG)], idx))
        y += LINE_H
        idx += 1

    if not STATIC:
        # blinking cursor after everything lands
        out.append(
            f'<rect x="24" y="{y - 12}" width="8" height="15" fill="{KEY}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0;0" begin="{0.15 + idx * 0.12:.2f}s" '
            f'dur="1.2s" repeatCount="indefinite"/></rect>'
        )

    out.append("</svg>")
    svg = "\n".join(out)
    with open("info-card.svg", "w") as f:
        f.write(svg)
    print(f"wrote info-card.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
