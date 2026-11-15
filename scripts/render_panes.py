#!/usr/bin/env python3
"""Render the whoami pane, the projects pane and the status bar.

The text below is the hand-written part of the profile; every number comes
from data/profile.json (see fetch_profile.py).

Usage: python scripts/render_panes.py
Writes: hero.svg, projects.svg, statusbar.svg
"""
import json

from theme import (ACCENT, BAR, BG, DIM, FG, GOLD, KEY, TITLE, W, anim, esc,
                   pane, prompt, svg_open, write)

NAME = "Stink-O"
TAGLINE = "games, mods and tools, built on Linux"
ROWS = [
    ("now", "orbital-laser, a strike mod for Horizon"),
    ("stack", "Rust / TypeScript / Python"),
    ("engines", "Bevy, Godot"),
    ("desk", "Fedora, KDE Plasma, Wayland"),
    ("motto", "ship weird things that work"),
]

# (repo, one-line description); listed by live star count
PROJECTS = [
    ("box3d-godot", "Box3D physics in Godot, with a full sample project"),
    ("orbital-laser", "Orbital laser strike mod for Horizon, the Rust Minecraft"),
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
    art_top = 30
    art_h = len(art) * CH_H
    h = round(art_top + art_h + 24)
    out = [svg_open(h)] + pane(h, "whoami")

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
    x = 456
    y = art_top + (art_h - 276) / 2 + 16
    cmd, t = prompt(x, y, "whoami")
    out.append(cmd)
    t += 0.15
    out.append(f'<text{anim("a", t)} x="{x}" y="{y + 44}" font-size="30" font-weight="700" '
               f'fill="{TITLE}">{esc(NAME)}</text>')
    out.append(f'<text{anim("a", t + 0.1)} x="{x}" y="{y + 68}" fill="{DIM}">{esc(TAGLINE)}</text>')
    ry = y + 106
    for i, (key, val) in enumerate(ROWS):
        out.append(
            f'<text{anim("a", t + 0.2 + i * 0.1)} x="{x}" y="{ry + i * 24}" xml:space="preserve">'
            f'<tspan fill="{KEY}">{key.ljust(9)}</tspan><tspan fill="{FG}">{esc(val)}</tspan></text>'
        )
    ty = ry + len(ROWS) * 24 + 34
    tiles = [(profile["stars"], "stars"), (profile["followers"], "followers"),
             (profile["public_repos"], "public repos")]
    for i, (num, label) in enumerate(tiles):
        tx = x + i * 128
        out.append(
            f'<g{anim("a", t + 0.8 + i * 0.1)}>'
            f'<text x="{tx}" y="{ty}" font-size="24" font-weight="700" fill="{TITLE}">{num}</text>'
            f'<text x="{tx}" y="{ty + 18}" font-size="11" fill="{DIM}">{label}</text></g>'
        )
    write("hero.svg", out)


def projects(profile):
    rows = sorted(PROJECTS, key=lambda p: -profile["repos"][p[0]]["stars"])
    top, step = 78, 28
    h = top + (len(rows) - 1) * step + 28
    out = [svg_open(h)] + pane(h, "projects")
    cmd, t = prompt(26, 44, "ls --sort=stars ~/projects")
    out.append(cmd)
    for i, (name, desc) in enumerate(rows):
        repo = profile["repos"][name]
        lang = repo["language"] or ""
        y = top + i * step
        out.append(
            f'<g{anim("a", t + 0.15 + i * 0.09)}>'
            f'<text x="30" y="{y}" fill="{GOLD}">★</text>'
            f'<text x="84" y="{y}" text-anchor="end" fill="{GOLD}">{repo["stars"]}</text>'
            f'<text x="106" y="{y}" font-weight="700" fill="{TITLE}">{esc(name)}</text>'
            f'<text x="290" y="{y}" fill="{LANG_COLOR.get(lang, DIM)}">{esc(lang)}</text>'
            f'<text x="388" y="{y}" fill="{FG}">{esc(desc)}</text></g>'
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
        f'<text x="{W - 14}" y="{y}" text-anchor="end" fill="{DIM}">hand-rolled svg, no stat services '
        f'<tspan fill="{ACCENT}">|</tspan> refreshed {profile["fetched"]}</text>',
    ]
    write("statusbar.svg", out)


def main():
    profile = json.load(open("data/profile.json"))
    hero(profile)
    projects(profile)
    statusbar(profile)


if __name__ == "__main__":
    main()
