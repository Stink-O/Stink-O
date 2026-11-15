"""Shared look for the profile SVGs: palette, pane frame, entrance animation.

Every image is an 860px-wide tmux-style pane: a thin border with the pane
name set into the top edge. Set STATIC=1 to drop all animation (for
rasterized previews).
"""
import html
import os

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
DIM = "#8b949e"
KEY = "#39d353"
ACCENT = "#58a6ff"
TITLE = "#f0f6fc"
GOLD = "#e3b341"

W = 860
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
STATIC = os.environ.get("STATIC") == "1"

CSS = (
    "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
    ".a{opacity:0;animation:in .45s ease-out forwards}"
    "@keyframes fade{to{opacity:1}}"
    ".f{opacity:0;animation:fade .3s linear forwards}"
    "@keyframes draw{to{stroke-dashoffset:0}}"
    ".b{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.1s ease-out forwards}"
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    ".k{opacity:0;animation:blink 1.2s steps(1) infinite}"
    "@keyframes drop{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}"
    ".d{opacity:0;animation:drop .45s ease-out forwards}"
    "@media (prefers-reduced-motion:reduce){.a,.f,.b,.d{animation:none;opacity:1;stroke-dashoffset:0}.k{animation:none}}"
)


def esc(s):
    return html.escape(str(s), quote=False)


def anim(cls, delay=0.0):
    """Attribute string that plays entrance animation `cls` after `delay` s."""
    if STATIC:
        return ""
    return f' class="{cls}" style="animation-delay:{delay:.3f}s"'


def svg_open(h, size=13, w=W):
    style = "" if STATIC else f"<style>{CSS}</style>"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}" font-size="{size}">{style}'
    )


def pane(h, label, w=W):
    """Filled pane whose border draws itself in, with `label` set into a
    gap in the top edge."""
    x0, y0, x1, y1, r = 0.5, 8.5, w - 0.5, h - 0.5, 8
    g0 = 18
    g1 = g0 + len(label) * 7.3 + 16
    cls = "" if STATIC else ' class="b"'
    return [
        f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{BG}"/>',
        f'<path{cls} pathLength="1" fill="none" stroke="{BORDER}" d="M{g1:.1f} {y0}H{x1 - r}'
        f'A{r} {r} 0 0 1 {x1} {y0 + r}V{y1 - r}A{r} {r} 0 0 1 {x1 - r} {y1}H{x0 + r}'
        f'A{r} {r} 0 0 1 {x0} {y1 - r}V{y0 + r}A{r} {r} 0 0 1 {x0 + r} {y0}H{g0}"/>',
        f'<text x="{g0 + 8}" y="{y0 + 4}" font-size="12" fill="{DIM}">{esc(label)}</text>',
    ]


def prompt(x, y, cmd, start=0.2):
    """`stink-o@github ~ $ cmd`, typed one character at a time with a
    blinking block cursor. Returns (svg, time the typing ends)."""
    chars = "".join(
        f'<tspan{anim("f", start + i * 0.07)} fill="{TITLE}">{esc(c)}</tspan>'
        for i, c in enumerate(cmd)
    )
    end = start + len(cmd) * 0.07
    cursor = "" if STATIC else f'<tspan{anim("k", end)} fill="{KEY}"> █</tspan>'
    return (
        f'<text x="{x}" y="{y}" xml:space="preserve"><tspan fill="{KEY}">stink-o@github</tspan>'
        f'<tspan fill="{DIM}"> ~ $ </tspan>{chars}{cursor}</text>',
        end,
    )


def write(name, parts):
    svg = "\n".join(parts + ["</svg>"])
    with open(name, "w") as f:
        f.write(svg)
    print(f"wrote {name} ({len(svg)} bytes)")
