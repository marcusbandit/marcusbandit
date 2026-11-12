"""The AniBeam card: the logo and wordmark over the beam, its speed lines drawn as light with
glints running along them, and three columns of posters drifting past on the right.

Posters are embedded as small JPEGs so the SVG stands alone when GitHub serves it as an image.
They come from AniList covers; gen/posters/ holds the JPEGs this reads.
"""
import base64
from pathlib import Path

from tokens import SANS, MONO, RAMP

W, H = 800, 300
INSET = 14
R = 26

THEMES = {
    "dark": {"screen": "#07080a", "edge": RAMP[4], "text": RAMP[10], "sub": RAMP[8], "faint": RAMP[6], "beam": 1.0},
    "light": {"screen": RAMP[10], "edge": RAMP[8], "text": RAMP[1], "sub": RAMP[5], "faint": RAMP[7], "beam": 0.8},
}

BRAND = "#fdc901"
INK = "#0d0e11"
POSTERS = Path(__file__).parent / "posters"

# Three columns of posters: up, down, up.
COLUMNS = [
    ["frieren", "bebop", "aot", "spirited", "jjk"],
    ["csm", "gits", "eva", "spyfamily", "yourname"],
    ["akira", "demonslayer", "oshinoko", "mononoke", "steinsgate"],
]
PW, PH, GAP = 92, 138, 12
COL_X = [482, 586, 690]
LOOP = len(COLUMNS[0]) * (PH + GAP)

# The logo: the katakana a inside the rounded square, in its 1024 box.
GLYPH = (Path(__file__).parent / "anibeam-glyph.txt").read_text().strip()

# Beams rise from the bottom left at -30 degrees: x, y, length, thickness, alpha, blur, glint
# period and delay (0 period means no glint on that line).
BEAMS = [
    (-40, 330, 560, 26, 0.38, 12, 0, 0),
    (40, 352, 520, 8, 0.55, 3, 6.0, 1.2),
    (-80, 300, 460, 54, 0.14, 26, 0, 0),
    (150, 360, 470, 2.5, 0.9, 0.5, 4.8, 0.3),
    (230, 350, 420, 2, 0.7, 0.4, 5.6, 2.4),
    (330, 368, 360, 2, 0.55, 0.4, 6.8, 3.6),
]


def b64(name):
    return base64.b64encode((POSTERS / f"{name}.jpg").read_bytes()).decode()


def svg(theme):
    c = THEMES[theme]
    defs, beams, cols = [], [], []

    defs.append(f'<clipPath id="screen"><rect x="{INSET}" y="{INSET}" width="{W - 2 * INSET}" height="{H - 2 * INSET}" rx="{R - 8}"/></clipPath>')
    defs.append('<linearGradient id="fadeY" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".2" stop-color="#fff"/>'
                '<stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                f'<mask id="posterMask"><rect x="460" y="{INSET}" width="{W - 460 - INSET}" height="{H - 2 * INSET}" fill="url(#fadeY)"/></mask>')
    defs.append('<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="{BRAND}" stop-opacity="0"/><stop offset=".35" stop-color="{BRAND}"/>'
                '<stop offset=".7" stop-color="#ffe278"/><stop offset="1" stop-color="#ffe278" stop-opacity="0"/></linearGradient>'
                '<linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">'
                '<stop offset="0" stop-color="#fff6d2" stop-opacity="0"/><stop offset=".5" stop-color="#fff6d2"/>'
                '<stop offset="1" stop-color="#fff6d2" stop-opacity="0"/></linearGradient>')
    for i, (_, _, _, _, _, blur, _, _) in enumerate(BEAMS):
        if blur:
            defs.append(f'<filter id="blur{i}" x="-20%" y="-300%" width="140%" height="700%"><feGaussianBlur stdDeviation="{blur}"/></filter>')

    for i, (x, y, length, thick, alpha, blur, period, delay) in enumerate(BEAMS):
        a = alpha * c["beam"]
        glint = ""
        if period:
            glint = (f'<rect x="-80" y="{-thick / 2 - 1}" width="80" height="{thick + 2}" rx="{thick / 2 + 1}" fill="url(#glint)">'
                     f'<animate attributeName="x" values="-80;{length};{length}" keyTimes="0;0.45;1" dur="{period}s" begin="{delay}s" repeatCount="indefinite"/>'
                     '</rect>')
        beams.append(
            f'<g transform="translate({x} {y}) rotate(-30)">'
            f'<rect x="0" y="{-thick / 2}" width="{length}" height="{thick}" rx="{thick / 2}" fill="url(#beam)" opacity="{a}" filter="url(#blur{i})">'
            f'<animate attributeName="opacity" values="{a};{a * 0.7};{a}" dur="{7 + i}s" repeatCount="indefinite"/></rect>'
            f'{glint}</g>')

    for k, (column, x) in enumerate(zip(COLUMNS, COL_X)):
        # One set of posters per column, drawn twice: a move of one set's height loops cleanly.
        imgs = []
        for j, name in enumerate(column):
            y = 20 + j * (PH + GAP)
            defs.append(f'<clipPath id="poster{k}_{j}"><rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="10"/></clipPath>')
            imgs.append(f'<image href="data:image/jpeg;base64,{b64(name)}" x="{x}" y="{y}" width="{PW}" height="{PH}" '
                        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#poster{k}_{j})"/>')
        defs.append(f'<g id="col{k}">{"".join(imgs)}</g>')
        up = k % 2 == 0
        frm, to = (f"0 {-LOOP / 2}", f"0 {-LOOP - LOOP / 2}") if up else (f"0 {-LOOP - LOOP / 2}", f"0 {-LOOP / 2}")
        cols.append(f'<g><animateTransform attributeName="transform" type="translate" values="{frm};{to}" dur="{44 + 6 * k}s" repeatCount="indefinite"/>'
                    f'<use href="#col{k}"/><use href="#col{k}" y="{LOOP}"/></g>')

    logo = (f'<g transform="translate(58 84) scale({64 / 1024})">'
            f'<rect x="14" y="14" width="996" height="996" rx="225" fill="{BRAND}"/>'
            f'<path fill="{INK}" d="{GLYPH}"/></g>')
    words = (f'<text x="140" y="134" font-family="{SANS}" font-size="54" font-weight="700" letter-spacing="-1.6" fill="{c["text"]}">AniBeam</text>'
             f'<text x="60" y="196" font-family="{SANS}" font-size="19" fill="{c["sub"]}">Your anime folder, as a library</text>'
             f'<text x="60" y="222" font-family="{SANS}" font-size="19" fill="{c["sub"]}">you can watch and track.</text>'
             f'<text x="60" y="262" font-family="{MONO}" font-size="14" fill="{c["faint"]}">anibeam.app</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="AniBeam">'
            f'<defs>{"".join(defs)}</defs>'
            f'<rect x="{INSET - 0.5}" y="{INSET - 0.5}" width="{W - 2 * INSET + 1}" height="{H - 2 * INSET + 1}" rx="{R - 8}" fill="{c["screen"]}" stroke="{c["edge"]}"/>'
            f'<g clip-path="url(#screen)">{"".join(beams)}<g mask="url(#posterMask)">{"".join(cols)}</g></g>'
            f'{logo}{words}</svg>\n')
