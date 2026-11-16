#!/usr/bin/env python3
"""Render the whoami pane, the projects pane and the status bar.

The text below is the hand-written part of the profile; every number comes
from data/profile.json (see fetch_profile.py).

Usage: python scripts/render_panes.py
Writes: hero.svg, projects.svg, statusbar.svg
"""
import json

from theme import (BAR, BG, DIM, FG, GOLD, KEY, TITLE, W, anim, esc,
                   pane, prompt, svg_open, write)

NAME = "Stink-O"
ROWS = [
    ("now", "mods for Horizon, the Rust Minecraft"),
    ("stack", "Rust / TypeScript / Python"),
    ("engines", "Bevy, Godot"),
    ("desk", "Fedora, KDE Plasma, Wayland"),
    ("motto", "ship weird things that work"),
]

# (repo, one-line description); listed by live star count
PROJECTS = [
    ("box3d-godot", "Box3D physics in Godot, with a full sample project"),
    ("orbital-laser", "Orbital strike: custom shader, synthesized sound, craters"),
    ("Portal2-rust-engine", "Portal 2's portals and player controller as Bevy plugins"),
    ("portalcraft", "Portal 2's campaign played as a Minecraft player"),
    ("Homefield", "Self-hosted AI image + music studio, Docker, no GPU"),
    ("better-voice-Linux", "Voice dictation that reads the screen you point at"),
]

LANG_COLOR = {
    "Rust": "#dea584", "C": "#9aa4af", "C++": "#f34b7d", "TypeScript": "#58a6ff",
    "JavaScript": "#f1e05a", "Python": "#79b8ff", "QML": "#44a51c",
}

# dog portrait: glyph cell size in px
CH_W, CH_H, CH_SIZE = 6.0, 10.4, 10


def hero(profile):
    art = open("data/dog-ascii.txt").read().rstrip("\n").split("\n")
    indent = min(len(l) - len(l.lstrip()) for l in art if l.strip())
    art = [l[indent:] for l in art]
    art_x = 26 + (410 - max(map(len, art)) * CH_W) / 2
    art_top = 22
    art_h = len(art) * CH_H
    h = round(art_top + art_h + 22)
    out = [svg_open(h)] + pane(h)

    # portrait, revealed as a top-to-bottom scan
    out.append(f'<g font-size="{CH_SIZE}" fill="{FG}">')
    for i, line in enumerate(art):
        if not line.strip():
            continue
        lead = len(line) - len(line.lstrip())
        body = line.strip()
        out.append(
            f'<text{anim("f", 0.1 + i * 0.03)} x="{art_x + lead * CH_W:.1f}" y="{art_top + (i + 1) * CH_H:.1f}" '
            f'textLength="{len(body) * CH_W:.1f}" lengthAdjust="spacing" '
            f'xml:space="preserve">{esc(body)}</text>'
        )
    out.append("</g>")

    # identity column, vertically centred against the portrait
    rows = ROWS + [("stars", f'{profile["stars"]} across {profile["public_repos"]} public repos')]
    x = 456
    y = art_top + (art_h - (72 + len(rows) * 24)) / 2 + 12
    cmd, t = prompt(x, y, "whoami", host=True)
    out.append(cmd)
    t += 0.15
    out.append(f'<text{anim("a", t)} x="{x}" y="{y + 46}" font-size="30" font-weight="700" '
               f'fill="{TITLE}">{esc(NAME)}</text>')
    for i, (key, val) in enumerate(rows):
        out.append(
            f'<text{anim("a", t + 0.1 + i * 0.1)} x="{x}" y="{y + 88 + i * 24}" xml:space="preserve">'
            f'<tspan fill="{KEY}">{key.ljust(9)}</tspan><tspan fill="{FG}">{esc(val)}</tspan></text>'
        )
    write("hero.svg", out)


def projects(profile):
    rows = sorted(PROJECTS, key=lambda p: -profile["repos"][p[0]]["stars"])
    top, step = 70, 28
    h = top + (len(rows) - 1) * step + 28
    out = [svg_open(h)] + pane(h)
    cmd, t = prompt(26, 36, "ls --sort=stars ~/projects")
    out.append(cmd)
    for i, (name, desc) in enumerate(rows):
        repo = profile["repos"][name]
        lang = repo["language"] or ""
        y = top + i * step
        out.append(
            f'<g{anim("a", t + 0.15 + i * 0.09)}>'
            f'<text x="62" y="{y}" text-anchor="end" fill="{GOLD}">{repo["stars"]}</text>'
            f'<text x="84" y="{y}" font-weight="700" fill="{TITLE}">{esc(name)}</text>'
            f'<text x="270" y="{y}" fill="{LANG_COLOR.get(lang, DIM)}">{esc(lang)}</text>'
            f'<text x="370" y="{y}" fill="{FG}">{esc(desc)}</text></g>'
        )
    write("projects.svg", out)


def statusbar(profile):
    h = 28
    y = 19
    out = [
        svg_open(h, size=12),
        f'<rect width="{W}" height="{h}" rx="6" fill="{BAR}"/>',
        f'<path d="M6 0H96V{h}H6A6 6 0 0 1 0 {h - 6}V6A6 6 0 0 1 6 0Z" fill="{KEY}"/>',
        f'<text x="48" y="{y}" text-anchor="middle" font-weight="700" fill="{BG}">[stink-o]</text>',
        f'<text x="114" y="{y}" xml:space="preserve" fill="{DIM}">0:whoami  1:projects  '
        f'<tspan fill="{TITLE}">2:contrib*</tspan></text>',
        f'<text x="{W - 14}" y="{y}" text-anchor="end" fill="{DIM}">refreshed {profile["fetched"]}</text>',
    ]
    write("statusbar.svg", out)


def main():
    profile = json.load(open("data/profile.json"))
    hero(profile)
    projects(profile)
    statusbar(profile)


if __name__ == "__main__":
    main()
