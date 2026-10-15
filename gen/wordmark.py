import math

from tokens import SANS, SIZE, RAMP, THEMES, smooth, chase, thin, animate, closed_curve, num

FAMILY = [(0, 0.0, 0), (4, 0.16, 0), (3, 0.22, 90), (4, -0.16, 0), (5, 0.18, -90), (6, 0.18, 0)]

W, H = 800, 220
TOTAL = 13.0
FPS = 30
SHAPE_FPS = 10
POINTS = 36
SCALE = 2.85
MID_Y = H / 2
EDGE = 46

LEGS = [
    (0.0, EDGE, 20, 0),
    (1.3, W * 0.42, 78, 4),
    (4.4, W - EDGE, 20, 1),
    (6.7, W * 0.6, 72, 2),
    (9.6, EDGE, 20, 0),
]


def radius(member, phi):
    lobes, depth, turn = member
    weight = 1 / math.sqrt(1 + depth * depth / 2)
    return (1 - depth * math.cos(lobes * (phi - math.radians(turn)))) * weight


def blend(s, phi):
    i = min(int(math.floor(s)), len(FAMILY) - 2)
    f = s - i
    return radius(FAMILY[i], phi) * (1 - f) + radius(FAMILY[i + 1], phi) * f


def tracks():
    _, x = smooth([(t, x) for t, x, _, _ in LEGS], TOTAL, FPS, speed=2.6)
    _, r = smooth([(t, r) for t, _, r, _ in LEGS], TOTAL, FPS, speed=3.4)
    times, s = smooth([(t, s) for t, _, _, s in LEGS], TOTAL, FPS, speed=2.2)
    x, r, s = chase(x, FPS, 7), chase(r, FPS, 7), chase(s, FPS, 7)
    span = max(x) - min(x)
    vx = [(x[(k + 1) % len(x)] - x[k - 1]) * FPS / 2 for k in range(len(x))]
    vmax = max(abs(v) for v in vx)
    y = [MID_Y + 4 * math.sin(2 * math.pi * 3 * t / TOTAL) for t in times]
    roll = [-(xi - EDGE) / span * 2 * math.pi for xi in x]
    return times, x, y, r, s, roll, [v / vmax for v in vx]


def outline(t, r, s, roll, v):
    phase = 2 * math.pi * t / TOTAL
    pts = []
    for i in range(POINTS):
        phi = 2 * math.pi * i / POINTS
        wob = 1 + (0.02 + 0.03 * abs(v)) * math.sin(2 * phi + 4 * phase) + 0.018 * math.sin(3 * phi - 5 * phase)
        stretch = 1 + 0.09 * abs(v) * math.cos(2 * phi) + 0.05 * v * math.cos(phi)
        rad = r * blend(s, phi + roll) * wob * stretch
        pts.append((rad * math.cos(phi), rad * math.sin(phi)))
    return closed_curve(pts)


def svg(theme):
    c = THEMES[theme]
    dark = theme == "dark"
    plate, rim = (RAMP[2], RAMP[4]) if dark else (RAMP[10], RAMP[9])
    ink, over = c["text"], (RAMP[1] if dark else RAMP[10])

    times, x, y, r, s, roll, v = tracks()
    step = FPS // SHAPE_FPS
    picks = list(range(0, len(times), step))
    if picks[-1] != len(times) - 1:
        picks.append(len(times) - 1)
    shape_t = [times[k] for k in picks]
    shapes = [outline(times[k], r[k], s[k], roll[k], v[k]) for k in picks]
    shapes[-1] = shapes[0]
    d_anim = animate("d", shape_t, shapes, TOTAL, fmt=str)

    mt, mv = thin(times, list(zip(x, y)), eps=0.2)
    move = (f'<animateTransform attributeName="transform" type="translate" dur="{num(TOTAL)}s" '
            f'repeatCount="indefinite" calcMode="linear" keyTimes="'
            + ";".join("0" if t <= 0 else "1" if t >= TOTAL else f"{t / TOTAL:.5f}" for t in mt)
            + '" values="' + ";".join(f"{num(a)} {num(b)}" for a, b in mv) + '"/>')

    baseline = MID_Y + 0.36 * SIZE["large"] * SCALE
    word = (f'<text x="0" y="0" text-anchor="middle" '
            f'transform="translate({num(W / 2)} {num(baseline)}) scale({num(SCALE)})">banditshell</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <path id="blob" d="{shapes[0]}">{d_anim}{move}</path>
    <clipPath id="inside"><use href="#blob"/></clipPath>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  </defs>
  <style>
    text {{ font: 700 {SIZE["large"]}px {SANS}; letter-spacing: -0.6px; }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="{plate}" stroke="{rim}"/>
  <g clip-path="url(#frame)">
    <g fill="{ink}">{word}</g>
    <use href="#blob" fill="{c["accent"]}"/>
    <g fill="{over}" clip-path="url(#inside)">{word}</g>
  </g>
</svg>
"""
