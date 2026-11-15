#!/usr/bin/env python3
"""Render data/contributions.json as the contributions pane.

53x7 calendar grid in the GitHub palette with a diagonal drop-in reveal,
and a row of figures underneath.

Usage: python scripts/render_heatmap_svg.py
Writes: contrib-heatmap.svg
"""
import datetime as dt
import json

from theme import DIM, FG, TITLE, W, anim, pane, prompt, svg_open, write

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT = 46   # room for weekday labels
TOP = 82    # room for the prompt and month labels


def main():
    data = json.load(open("data/contributions.json"))
    days = data["days"]
    ordered = sorted(days)

    # week columns starting from the Sunday on/before the first day
    first = dt.date.fromisoformat(ordered[0])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    last = dt.date.fromisoformat(ordered[-1])
    weeks = []
    d = start
    while d <= last:
        weeks.append([d + dt.timedelta(days=i) for i in range(7)])
        d += dt.timedelta(days=7)

    grid_w = len(weeks) * STEP - GAP
    x0 = LEFT + (W - LEFT - 20 - grid_w) / 2
    h = TOP + 7 * STEP + 76

    out = [svg_open(h, size=11)] + pane(h, "contrib")
    cmd, t = prompt(26, 44, "./contributions.sh")
    out.append(cmd.replace("<text ", '<text font-size="13" ', 1))

    seen = None
    for wi, week in enumerate(weeks):
        m = week[0].strftime("%b")
        if m != seen:
            seen = m
            out.append(f'<text x="{x0 + wi * STEP:.1f}" y="{TOP - 9}" fill="{DIM}">{m}</text>')
    for lbl, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        out.append(f'<text x="{x0 - 30:.1f}" y="{TOP + row * STEP + CELL - 2}" fill="{DIM}">{lbl}</text>')

    for wi, week in enumerate(weeks):
        for di, date in enumerate(week):
            iso = date.isoformat()
            if iso not in days:
                continue
            level = min(days[iso]["level"], len(PALETTE) - 1)
            out.append(
                f'<rect{anim("d", t + (wi + di) * 0.018)} x="{x0 + wi * STEP:.1f}" y="{TOP + di * STEP}" '
                f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level]}"/>'
            )

    # figures left, legend right
    fy = TOP + 7 * STEP + 34
    best = data.get("best_day") or {}
    figures = [
        (data["total"], "contributions, forks included"),
        (f'{data["current_streak"]}d', "current streak"),
        (f'{data["longest_streak"]}d', "longest streak"),
        (best.get("count", 0), "best day"),
    ]
    fx = x0
    after = t + (len(weeks) + 7) * 0.018
    for i, (num, label) in enumerate(figures):
        out.append(
            f'<g{anim("a", after + i * 0.1)}>'
            f'<text x="{fx:.1f}" y="{fy}" font-size="20" font-weight="700" fill="{TITLE}">{num}</text>'
            f'<text x="{fx:.1f}" y="{fy + 17}" fill="{DIM}">{label}</text></g>'
        )
        fx += max(len(label) * 6.7, len(str(num)) * 12.2) + 34

    lx = x0 + grid_w - 5 * STEP + GAP - 36
    ly = fy + 6
    out.append(f'<text x="{lx - 8:.1f}" y="{ly + 10}" text-anchor="end" fill="{DIM}">Less</text>')
    for i, color in enumerate(PALETTE):
        out.append(f'<rect x="{lx + i * STEP:.1f}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>')
    out.append(f'<text x="{lx + 5 * STEP + 5:.1f}" y="{ly + 10}" fill="{DIM}">More</text>')

    write("contrib-heatmap.svg", out)


if __name__ == "__main__":
    main()
