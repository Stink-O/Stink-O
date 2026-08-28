#!/usr/bin/env python3
"""Render data/contributions.json as an animated heatmap SVG.

53x7 calendar grid, GitHub palette, diagonal slide-down reveal that plays
once and freezes. Stats footer underneath.

Usage: python scripts/render_heatmap_svg.py
Writes: contrib-heatmap.svg
"""
import datetime as dt
import json

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG = "#0d1117"
BORDER = "#30363d"
DIM = "#8b949e"
FG = "#c9d1d9"
KEY = "#39d353"

CELL = 13
GAP = 3
LEFT = 46   # room for weekday labels
TOP = 34    # room for month labels


def main():
    data = json.load(open("data/contributions.json"))
    days = data["days"]
    ordered = sorted(days)

    # Build week columns starting from the Sunday on/before the first day
    first = dt.date.fromisoformat(ordered[0])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    last = dt.date.fromisoformat(ordered[-1])
    weeks = []
    d = start
    while d <= last:
        weeks.append([d + dt.timedelta(days=i) for i in range(7)])
        d += dt.timedelta(days=7)

    grid_w = len(weeks) * (CELL + GAP)
    x0 = LEFT
    W = LEFT + grid_w + 16
    H = TOP + 7 * (CELL + GAP) + 58

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">',
        '<style>'
        '@keyframes drop{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}'
        '.d{opacity:0;animation:drop .45s ease-out forwards}'
        '</style>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
    ]

    # month labels
    seen = None
    for wi, week in enumerate(weeks):
        m = week[0].strftime("%b")
        if m != seen:
            seen = m
            out.append(f'<text x="{x0 + wi * (CELL + GAP)}" y="{TOP - 10}" fill="{DIM}">{m}</text>')

    # weekday labels
    for lbl, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = TOP + row * (CELL + GAP) + CELL - 3
        out.append(f'<text x="{x0 - 30}" y="{y}" fill="{DIM}">{lbl}</text>')

    # cells with diagonal-staggered reveal
    for wi, week in enumerate(weeks):
        for di, date in enumerate(week):
            iso = date.isoformat()
            if iso not in days:
                continue
            level = min(days[iso]["level"], len(PALETTE) - 1)
            x = x0 + wi * (CELL + GAP)
            y = TOP + di * (CELL + GAP)
            delay = (wi + di) * 0.018
            out.append(
                f'<rect class="d" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"/>'
            )

    # footer: stats left, legend right
    fy = H - 22
    total = data["total"]
    streak = data["current_streak"]
    longest = data["longest_streak"]
    out.append(
        f'<text x="{x0}" y="{fy}" fill="{DIM}">'
        f'<tspan fill="{KEY}">{total}</tspan> contributions in the last year'
        f'<tspan dx="16" fill="{DIM}">|</tspan>'
        f'<tspan dx="16">streak </tspan><tspan fill="{KEY}">{streak}d</tspan>'
        f'<tspan dx="10">(longest {longest}d)</tspan></text>'
    )
    lx = x0 + grid_w - 5 * (CELL + GAP) - 78
    out.append(f'<text x="{lx - 38}" y="{fy}" fill="{DIM}">Less</text>')
    for i, color in enumerate(PALETTE):
        out.append(
            f'<rect x="{lx + i * (CELL + GAP)}" y="{fy - 10}" width="{CELL}" height="{CELL}" '
            f'rx="3" fill="{color}"/>'
        )
    out.append(f'<text x="{lx + 5 * (CELL + GAP) + 6}" y="{fy}" fill="{DIM}">More</text>')

    out.append("</svg>")
    svg = "\n".join(out)
    with open("contrib-heatmap.svg", "w") as f:
        f.write(svg)
    print(f"wrote contrib-heatmap.svg ({len(weeks)} weeks, {len(svg)} bytes)")


if __name__ == "__main__":
    main()
