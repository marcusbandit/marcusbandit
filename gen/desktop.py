import math

from tokens import THEMES, SANS, SIZE, RAMP, smooth, chase, thin, f1, Outline, bump
from wordmark import blend

W, H = 800, 300
BAND = 14
R_OUT = 26
R_IN = 12
X0, Y0, X1, Y1 = BAND, BAND, W - BAND, H - BAND
TOTAL = 11.8
FPS = 30
SHAPE_FPS = 12
FILLET = 16
RADIUS = 14
NECK = 3
PAD = 16
ORDER = ["top", "right", "bottom", "left"]

SIDE = {"d": 56, "flare": 26, "tray": ["dot", "ring", "square"], "status": ["update", "signal", "battery"],
        "slot": 22, "plates": 5, "plate": (32, 20), "plate_gap": 8, "path": [1, 3, 2], "hover": "battery"}
PEEK = {"d": 128, "fillet": 14, "level": 0.72}
ISLAND = {"x": W / 2, "w": 132, "h": 32, "rest": 44, "gap": 16}
LAUNCHER = {"x": W / 2, "w": 340, "d": 100, "rest": 70, "apps": 7, "hover": 4}
BLOB = {"r": 34, "points": 24}
WORD_SCALE = 2.25
WORD = {"advance": 0.56, "sweep": 2.6, "swell": 1.2}


def frame(o, t, n):
    return lambda u, v: (o[0] + t[0] * u + n[0] * v, o[1] + t[1] * u + n[1] * v)


def panel_bump(w, d, fillet=FILLET, radius=RADIUS):
    f = min(fillet, d / 2)
    return w, d, f, min(radius, d - f, w / 2)


def inner(x0, y0, x1, y1, radii, bumps, step=(0.0, 0.0)):
    pd, top = step
    rc, fc = min(RADIUS, pd / 2), min(PEEK["fillet"], pd / 2)
    xb = x0 + pd
    edges = {"top": ((x0, y0), (1, 0), x1 - x0), "right": ((x1, y0), (0, 1), y1 - y0),
             "bottom": ((x1, y1), (-1, 0), x1 - xb), "left": ((x0, y1), (0, -1), y1 - y0)}
    out = Outline((x0 + radii[3], y0))
    for i, e in enumerate(ORDER):
        o, t, length = edges[e]
        P = frame(o, t, (-t[1], t[0]))
        mine = [(((b[1] - o[0]) * t[0] + (b[1] - o[1]) * t[1]),) + b[2:] for b in bumps if b[0] == e]
        for b in sorted(mine):
            bump(out, P, *b)
        if e == "left":
            out.line((x0, y0 + radii[3]))
        else:
            out.line(P(length - radii[i], 0))
        nxt = edges[ORDER[(i + 1) % 4]][1]
        out.corner(t, nxt, radii[i])
        if e == "bottom":
            out.line((xb, top + rc))
            out.corner((0, -1), (-1, 0), rc)
            out.line((x0 + fc, top))
            out.corner((-1, 0), (0, -1), fc)
    return out


def rounded(x, y, w, h, r):
    return inner(x, y, x + w, y + h, [r] * 4, [])


def island_shape(pw, ph, g, n, link):
    cx = ISLAND["x"]
    nw = pw - n * (pw - NECK)
    room = (pw - nw) / 2
    rt = min(ph / 2, room / 2)
    db = link * (g + ph / 2)
    dp = link * (g + min(ph / 2, BAND / 2))
    fp = max(0.0, min(FILLET, room - rt, g / 2, dp / 2))
    fb = max(0.0, min(FILLET, g - fp, db / 2))
    rb = min(ph / 2, pw / 2)
    nub = ("top", cx, nw, db, fb, max(0.0, min(RADIUS, nw / 2, db - fb)))
    py = Y0 + g
    P = frame((cx - pw / 2, py), (1, 0), (0, -1))
    out = Outline(P(rt, 0))
    bump(out, P, pw / 2, nw, dp, fp, max(0.0, min(RADIUS, nw / 2, dp - fp)))
    out.line(P(pw - rt, 0))
    out.corner((1, 0), (0, 1), rt)
    out.line((cx + pw / 2, py + ph - rb))
    out.corner((0, 1), (-1, 0), rb)
    out.line((cx - pw / 2 + rb, py + ph))
    out.corner((-1, 0), (0, -1), rb)
    out.line((cx - pw / 2, py + rt))
    out.corner((0, -1), (1, 0), rt)
    return nub, out


def side_radius(sd):
    return R_IN + (SIDE["flare"] - R_IN) * min(1.0, sd / SIDE["d"])


def side_layout():
    xc = (X0 + SIDE["d"]) / 2 + BAND / 4
    slot = SIDE["slot"]
    tray = [Y0 + slot * (i + 0.5) for i in range(len(SIDE["tray"]))]
    n = len(SIDE["status"])
    status = [Y1 - slot * (n - i - 0.5) - BAND / 2 for i in range(n)]
    pw, ph = SIDE["plate"]
    k = SIDE["plates"]
    span = k * ph + (k - 1) * SIDE["plate_gap"]
    plates = [H / 2 - span / 2 + ph / 2 + i * (ph + SIDE["plate_gap"]) for i in range(k)]
    return {"xc": xc, "tray": tray, "status": dict(zip(SIDE["status"], status)), "plates": plates}


def peek_top():
    lay = side_layout()
    return min(lay["status"].values()) - SIDE["slot"] / 2 - PAD / 2


def island_box():
    return ISLAND["x"] - ISLAND["w"] / 2, Y0 + ISLAND["gap"], ISLAND["w"], ISLAND["h"]


def launcher_layout():
    w, h = LAUNCHER["w"], LAUNCHER["d"]
    x, y = LAUNCHER["x"] - w / 2, Y1 - h
    n = LAUNCHER["apps"]
    search_h = 26
    s = h - 3 * PAD - search_h
    inner_w = w - 2 * PAD
    gap = (inner_w - n * s) / (n - 1)
    apps = [(x + PAD + i * (s + gap), y + 2 * PAD + search_h) for i in range(n)]
    return {"box": (x, y, w, h), "search": (x + PAD, y + PAD, inner_w, search_h), "apps": apps, "size": s}


def word_center():
    return (X0 + X1) / 2, (Y0 + Y1) / 2


def word_span():
    return WORD["advance"] * len("banditshell") * SIZE["large"] * WORD_SCALE


class Timeline:
    def __init__(self):
        self.tracks = {}

    def set(self, t, **kv):
        for k, v in kv.items():
            self.tracks.setdefault(k, []).append((t, v))

    def sample(self, speeds, default):
        out = {}
        for k, ev in self.tracks.items():
            times, out[k] = smooth(sorted(ev, key=lambda e: e[0]), TOTAL, FPS, speeds.get(k, default))
        return times, out


def schedule():
    tl = Timeline()
    wx, wy = word_center()
    half = word_span() / 2
    rest = (wx + half - BLOB["r"] * 0.6, wy + 4)
    hand = (rest[0] + 18, rest[1] + 40)
    lay = side_layout()
    path = SIDE["path"]
    tl.set(0, cx=hand[0], cy=hand[1], bx=rest[0], by=rest[1], br=BLOB["r"],
           sd=0.0, sc=0.0, wa=float(path[0]), pk=0.0, pc=0.0,
           pw=ISLAND["rest"], ph=0.0, g=0.0, n=0.0, link=1.0, ci=0.0,
           lw=LAUNCHER["rest"], ld=0.0, lc=0.0, lh=0.0)

    def go(t, p, lag=0.1):
        tl.set(t, cx=p[0], cy=p[1])
        tl.set(t + lag, bx=p[0], by=p[1])

    def absorb(t, p, settle=0.3):
        tl.set(t, bx=p[0], by=p[1])
        tl.set(t + settle, br=0.0)

    def emit(t, p):
        tl.set(t, bx=p[0], by=p[1], br=BLOB["r"])

    plate_x = lay["xc"] + SIDE["plate"][0] * 0.15
    mid = lay["plates"][len(lay["plates"]) // 2]
    t = 0.15
    go(t, (X0 + 6, mid))
    absorb(t + 0.2, (X0 - 10, mid))
    tl.set(t + 0.6, sd=float(SIDE["d"]))
    tl.set(t + 0.9, sc=1.0)
    t += 0.85
    for ws in path[1:]:
        go(t, (plate_x, lay["plates"][ws]), lag=0.0)
        tl.set(t + 0.35, wa=float(ws))
        t += 0.8
    hy = lay["status"][SIDE["hover"]]
    go(t, (plate_x, hy), lag=0.0)
    tl.set(t + 0.25, pk=1.0)
    tl.set(t + 0.5, pc=1.0)
    t += 1.6
    tl.set(t, pc=0.0, sc=0.0)
    tl.set(t + 0.12, pk=0.0)
    tl.set(t + 0.2, sd=0.0)
    tl.set(t + 0.8, wa=float(path[0]))

    ix, iy, iw, ih = island_box()
    top = (ISLAND["x"] + ISLAND["w"] * 0.32, Y0 + 6)
    tl.set(t, cx=top[0], cy=top[1])
    emit(t + 0.05, (X0 + SIDE["d"] / 2, hy))
    inside = (ISLAND["x"] + ISLAND["w"] * 0.2, Y0 + ISLAND["gap"] + ISLAND["h"] / 2)
    absorb(t + 0.15, inside, settle=0.45)
    t += 0.5
    tl.set(t, pw=ISLAND["w"], ph=ISLAND["h"], g=FILLET)
    tl.set(t + 0.3, n=1.0, g=ISLAND["gap"])
    tl.set(t + 0.55, link=0.0)
    tl.set(t + 0.6, ci=1.0)
    tl.set(t + 0.6, cx=ix + iw * 0.72, cy=iy + ih * 0.55)
    t += 1.35
    tl.set(t, ci=0.0)
    tl.set(t + 0.2, link=1.0)
    tl.set(t + 0.35, n=0.0, g=FILLET)
    tl.set(t + 0.65, pw=ISLAND["rest"], ph=0.0, g=0.0)

    bottom = (LAUNCHER["x"] - 30, Y1 - 6)
    tl.set(t, cx=bottom[0], cy=bottom[1])
    emit(t + 0.05, inside)
    absorb(t + 0.15, (bottom[0], Y1 - 8), settle=0.4)
    t += 0.45
    tl.set(t, lw=LAUNCHER["w"], ld=LAUNCHER["d"])
    tl.set(t + 0.3, lc=1.0)
    ll = launcher_layout()
    hx, hy = ll["apps"][LAUNCHER["hover"]]
    tl.set(t + 0.4, cx=hx + ll["size"] * 0.55, cy=hy + ll["size"] * 0.5)
    tl.set(t + 0.6, lh=1.0)
    t += 1.25
    tl.set(t, lc=0.0, lh=0.0)
    tl.set(t + 0.12, lw=LAUNCHER["rest"], ld=0.0)
    start = (wx - half - BLOB["r"] * 0.4, wy + 4)
    tl.set(t, cx=start[0], cy=start[1] + 40)
    emit(t + 0.05, (hx + ll["size"] / 2, Y1 - LAUNCHER["d"] + 10))
    tl.set(t + 0.15, bx=start[0], by=start[1])
    t += 0.6
    tl.set(t, br=BLOB["r"] * WORD["swell"])
    n = round(WORD["sweep"] * FPS)
    for i in range(n + 1):
        u = 0.5 - 0.5 * math.cos(math.pi * i / n)
        x = start[0] + (rest[0] - start[0]) * u
        y = rest[1] + 5 * math.sin(math.pi * 2 * u)
        tl.set(t + WORD["sweep"] * i / n, bx=x, by=y, cx=x + 18, cy=y + 40)
    t += WORD["sweep"] + 0.2
    tl.set(t, br=BLOB["r"])
    return tl


def outline(t, r, s, roll, v):
    phase = 2 * math.pi * t / TOTAL
    pts = []
    n = BLOB["points"]
    for i in range(n):
        phi = 2 * math.pi * i / n
        wob = 1 + (0.02 + 0.03 * abs(v)) * math.sin(2 * phi + 4 * phase) + 0.018 * math.sin(3 * phi - 5 * phase)
        stretch = 1 + 0.09 * abs(v) * math.cos(2 * phi) + 0.05 * v * math.cos(phi)
        rad = r * blend(s, phi + roll) * wob * stretch
        pts.append((rad * math.cos(phi), rad * math.sin(phi)))
    out = [f"M{f1(pts[0][0])},{f1(pts[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{f1(c1[0])},{f1(c1[1])} {f1(c2[0])},{f1(c2[1])} {f1(p2[0])},{f1(p2[1])}")
    return "".join(out) + "Z"


def key_times(times):
    return ";".join("0" if t <= 0 else "1" if t >= TOTAL else f"{t / TOTAL:.4f}" for t in times)


def anim(attr, times, values, fmt):
    return (f'<animate attributeName="{attr}" dur="{f1(TOTAL)}s" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="{key_times(times)}" values="{";".join(fmt(v) for v in values)}"/>')


def anim_translate(times, values):
    vs = ";".join(f"{f1(x)} {f1(y)}" for x, y in values)
    return (f'<animateTransform attributeName="transform" type="translate" dur="{f1(TOTAL)}s" '
            f'repeatCount="indefinite" calcMode="linear" keyTimes="{key_times(times)}" values="{vs}"/>')


def opacity(v):
    return f"{v:.2f}"


def svg(theme):
    c = dict(THEMES[theme])
    dark = theme == "dark"
    c["well"] = c["raised"] if dark else c["screen"]
    c["ink"] = RAMP[5] if dark else RAMP[8]
    c["over"] = RAMP[1] if dark else RAMP[10]

    speeds = {"cx": 7.0, "cy": 7.0, "bx": 7.5, "by": 7.5, "br": 7.0, "wa": 9.0,
              "ci": 14.0, "lc": 14.0, "sc": 14.0, "lh": 14.0, "pc": 14.0, "pk": 12.0, "sd": 10.0}
    times, tr = schedule().sample(speeds, 11.0)
    for k in ("bx", "by", "br"):
        tr[k] = chase(tr[k], FPS, 12)
    for k in ("ph", "g", "ld", "sd", "pk", "br"):
        tr[k] = [0.0 if v < 0.15 else v for v in tr[k]]
    nf = len(times)

    def series(*keys):
        return [tuple(tr[k][i] for k in keys) for i in range(nf)]

    outer = rounded(0, 0, W, H, R_OUT).d()
    ptop = peek_top()
    keys = ("pw", "ph", "g", "n", "link", "lw", "ld", "sd", "pk")
    st, srows = thin(times, series(*keys), 0.08)
    shapes = []
    for pw, ph, g, n, link, lw, ld, sd, pk in srows:
        nub, pill = island_shape(pw, ph, g, n, link)
        bumps = [nub, ("bottom", LAUNCHER["x"]) + panel_bump(lw, ld)]
        rs = side_radius(sd)
        shapes.append(outer + inner(X0 + sd, Y0, X1, Y1, [R_IN, R_IN, rs, rs], bumps, (PEEK["d"] * pk, ptop)).d(reverse=True)
                      + pill.d())
    band = f'<path fill="{c["band"]}" d="{shapes[0]}">' + anim("d", st, shapes, str) + "</path>"

    defs, groups = [], []

    def content(name, keys, box_fn, offset_fn, op_key, body):
        rows = series(*keys)
        bt, brows = thin(times, [box_fn(*r) for r in rows], 0.06)
        defs.append(f'<clipPath id="clip-{name}"><rect x="0" y="0" width="0" height="0">'
                    + "".join(anim(a, bt, [b[j] for b in brows], f1) for j, a in enumerate(("x", "y", "width", "height")))
                    + "</rect></clipPath>")
        ot, orows = thin(times, [offset_fn(*r) for r in rows], 0.06)
        at, arows = thin(times, tr[op_key], 0.01)
        groups.append(f'<g clip-path="url(#clip-{name})"><g opacity="0">' + anim("opacity", at, arows, opacity)
                      + f'<g>{anim_translate(ot, orows)}{body}</g></g></g>')

    lay = side_layout()
    xc = lay["xc"]
    icons = []
    for kind, y in zip(SIDE["tray"], lay["tray"]):
        if kind == "dot":
            icons.append(f'<circle cx="{f1(xc)}" cy="{f1(y)}" r="5" fill="{c["sub"]}"/>')
        elif kind == "ring":
            icons.append(f'<circle cx="{f1(xc)}" cy="{f1(y)}" r="5" fill="none" stroke="{c["sub"]}" stroke-width="2"/>')
        else:
            icons.append(f'<rect x="{f1(xc - 5)}" y="{f1(y - 5)}" width="10" height="10" rx="2.5" fill="{c["faint"]}"/>')
    pw_, ph_ = SIDE["plate"]
    for y in lay["plates"]:
        icons.append(f'<rect x="{f1(xc - pw_ / 2)}" y="{f1(y - ph_ / 2)}" width="{pw_}" height="{ph_}" rx="5" fill="{c["well"]}"/>')
    plates = lay["plates"]
    step = plates[1] - plates[0]
    wt, wv = thin(times, tr["wa"], 0.003)
    mark_y = [plates[0] + v * step - ph_ / 2 for v in wv]
    icons.append(f'<rect x="{f1(xc - pw_ / 2)}" y="{f1(mark_y[0])}" width="{pw_}" height="{ph_}" rx="5" fill="{c["accent"]}">'
                 + anim("y", wt, mark_y, f1) + "</rect>")
    st_ = lay["status"]
    y = st_["update"]
    icons.append(f'<circle cx="{f1(xc)}" cy="{f1(y)}" r="5.5" fill="none" stroke="{c["accent"]}" stroke-width="2"/>'
                 f'<circle cx="{f1(xc)}" cy="{f1(y)}" r="2" fill="{c["accent"]}"/>')
    y = st_["signal"]
    bars, bw, bg = 4, 3, 2
    sx = xc - (bars * bw + (bars - 1) * bg) / 2
    for i in range(bars):
        bh = 4 + 8 * i / (bars - 1)
        icons.append(f'<rect x="{f1(sx + i * (bw + bg))}" y="{f1(y + 6 - bh)}" width="{bw}" height="{f1(bh)}" rx="1" '
                     f'fill="{c["sub"] if i < bars - 1 else c["faint"]}"/>')
    y = st_["battery"]
    bw_, bh_ = 18, 10
    icons.append(f'<rect x="{f1(xc - bw_ / 2 - 1)}" y="{f1(y - bh_ / 2)}" width="{bw_}" height="{bh_}" rx="2.5" fill="none" stroke="{c["sub"]}" stroke-width="1.6"/>'
                 f'<rect x="{f1(xc - bw_ / 2 + 1.5)}" y="{f1(y - bh_ / 2 + 2.5)}" width="{f1((bw_ - 5) * PEEK["level"])}" height="{bh_ - 5}" rx="1" fill="{c["sub"]}"/>'
                 f'<rect x="{f1(xc + bw_ / 2)}" y="{f1(y - 2)}" width="2" height="4" rx="1" fill="{c["sub"]}"/>')
    content("side", ("sd",), lambda sd: (0.0, 0.0, X0 + sd, float(H)),
            lambda sd: (sd - SIDE["d"], 0.0), "sc", "".join(icons))

    px0 = X0 + SIDE["d"]
    ring_r, ring_w = 15, 4
    rcx, rcy = px0 + PAD + ring_r + 2, (ptop + Y1) / 2
    circ = 2 * math.pi * ring_r
    bar_x = rcx + ring_r + 14
    bar_w = px0 + PEEK["d"] - PAD - bar_x
    peek_body = (
        f'<circle cx="{f1(rcx)}" cy="{f1(rcy)}" r="{ring_r}" fill="none" stroke="{c["well"]}" stroke-width="{ring_w}"/>'
        f'<circle cx="{f1(rcx)}" cy="{f1(rcy)}" r="{ring_r}" fill="none" stroke="{c["accent"]}" stroke-width="{ring_w}" '
        f'stroke-linecap="round" stroke-dasharray="{f1(circ * PEEK["level"])} {f1(circ)}" transform="rotate(-90 {f1(rcx)} {f1(rcy)})"/>'
        + "".join(f'<rect x="{f1(bar_x)}" y="{f1(rcy + dy - 3)}" width="{f1(bar_w * fr)}" height="6" rx="3" fill="{col}"/>'
                  for dy, fr, col in ((-8, 1.0, c["faint"]), (8, 0.6, c["well"]))))

    def peek_clip(pk, sd):
        return X0 + sd, ptop, PEEK["d"] * pk, Y1 - ptop

    content("peek", ("pk", "sd"), peek_clip, lambda pk, sd: (PEEK["d"] * (pk - 1), 0.0), "pc", peek_body)

    ix, iy, iw, ih = island_box()
    wave_n, wave_w, wave_gap = 4, 3, 4
    beat = TOTAL / round(TOTAL / 0.9)
    wx0 = ix + iw - ih / 2 - (wave_n * wave_w + (wave_n - 1) * wave_gap)
    waves = []
    for j in range(wave_n):
        hs = [6 + 8 * (0.5 + 0.5 * math.sin(2 * math.pi * (s / 8 + j * 0.27))) for s in range(9)]
        hs[-1] = hs[0]
        ys = [iy + ih / 2 - v / 2 for v in hs]
        rep = f'dur="{beat:.4f}s" repeatCount="indefinite"'
        waves.append(
            f'<rect x="{f1(wx0 + j * (wave_w + wave_gap))}" y="{f1(ys[0])}" width="{wave_w}" height="{f1(hs[0])}" rx="1.5" fill="{c["accent"]}">'
            f'<animate attributeName="height" {rep} values="{";".join(f1(v) for v in hs)}"/>'
            f'<animate attributeName="y" {rep} values="{";".join(f1(v) for v in ys)}"/></rect>')
    island_body = (
        f'<circle cx="{f1(ix + ih / 2)}" cy="{f1(iy + ih / 2)}" r="7" fill="{c["well"]}"/>'
        f'<circle cx="{f1(ix + ih / 2)}" cy="{f1(iy + ih / 2)}" r="3" fill="{c["accent"]}"/>'
        f'<rect x="{f1(ix + ih)}" y="{f1(iy + ih / 2 - 3)}" width="{f1(iw * 0.3)}" height="6" rx="3" fill="{c["faint"]}"/>'
        + "".join(waves))
    content("island", ("pw", "ph", "g"), lambda pw, ph, g: (ISLAND["x"] - pw / 2, Y0 + g, pw, ph),
            lambda pw, ph, g: (0.0, g - ISLAND["gap"]), "ci", island_body)

    ll = launcher_layout()
    sx, sy, sw, sh = ll["search"]
    s = ll["size"]
    hover = ll["apps"][LAUNCHER["hover"]]
    lt, lv = thin(times, tr["lh"], 0.01)
    launcher_body = (
        f'<rect x="{f1(sx)}" y="{f1(sy)}" width="{f1(sw)}" height="{f1(sh)}" rx="{f1(sh / 2)}" fill="{c["well"]}"/>'
        f'<rect x="{f1(sx + sh / 2)}" y="{f1(sy + 7)}" width="2" height="{f1(sh - 14)}" fill="{c["accent"]}"/>'
        + "".join(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(s)}" height="{f1(s)}" rx="8" fill="{c["well"]}"/>'
                  for x, y in ll["apps"])
        + f'<rect x="{f1(hover[0])}" y="{f1(hover[1])}" width="{f1(s)}" height="{f1(s)}" rx="8" fill="{c["accent"]}" opacity="0">'
        + anim("opacity", lt, lv, opacity) + "</rect>")
    content("launcher", ("lw", "ld"), lambda w, d: (LAUNCHER["x"] - w / 2, Y1 - d, w, d),
            lambda w, d: (0.0, LAUNCHER["d"] - d), "lc", launcher_body)

    bx, by, br = tr["bx"], tr["by"], tr["br"]
    vx = [(bx[(k + 1) % nf] - bx[k - 1]) * FPS / 2 for k in range(nf)]
    vmax = max(abs(v) for v in vx) or 1
    morph = [2.5 - 2.5 * math.cos(2 * math.pi * t / TOTAL) for t in times]
    picks = list(range(0, nf, FPS // SHAPE_FPS))
    if picks[-1] != nf - 1:
        picks.append(nf - 1)
    blob_t, blob_d = [], []
    for k in picks:
        d = outline(times[k], br[k], morph[k], -(bx[k] - bx[0]) / (1.5 * BLOB["r"]), vx[k] / vmax)
        blob_t.append(times[k])
        blob_d.append(d)
    blob_d[-1] = blob_d[0]
    keep = [i for i in range(len(blob_d)) if i in (0, len(blob_d) - 1)
            or not (blob_d[i] == blob_d[i - 1] == blob_d[i + 1])]
    blob_t, blob_d = [blob_t[i] for i in keep], [blob_d[i] for i in keep]
    mt, mv = thin(times, list(zip(bx, by)), 0.15)
    blob = (f'<path id="blob" d="{blob_d[0]}" transform="translate({f1(mv[0][0])} {f1(mv[0][1])})">'
            + anim("d", blob_t, blob_d, str) + anim_translate(mt, mv) + "</path>")

    wx, wy = word_center()
    baseline = wy + 0.36 * SIZE["large"] * WORD_SCALE
    word = (f'<text x="0" y="0" text-anchor="middle" font-family="{SANS}" font-size="{SIZE["large"]}" '
            f'font-weight="700" letter-spacing="-0.6" '
            f'transform="translate({f1(wx)} {f1(baseline)}) scale({WORD_SCALE})">banditshell</text>')

    ct, cpos = thin(times, series("cx", "cy"), 0.08)
    arrow = "M0,0L0,17L4.4,12.9L7.3,19.4L10.1,18.2L7.3,11.8L13,11.8Z"
    cursor = (f'<g transform="translate({f1(cpos[0][0])} {f1(cpos[0][1])})">{anim_translate(ct, cpos)}'
              f'<path d="{arrow}" fill="{c["cursor"]}" stroke="{c["cursorEdge"]}" stroke-width="1.3" stroke-linejoin="round"/></g>')

    inset = BAND / 2
    screen = (f'<rect x="{inset}" y="{inset}" width="{W - 2 * inset}" height="{H - 2 * inset}" '
              f'rx="{R_IN + inset}" fill="{c["screen"]}"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            f'<defs>{blob}<clipPath id="inside"><use href="#blob"/></clipPath>{"".join(defs)}</defs>\n'
            f'{screen}\n<g fill="{c["ink"]}">{word}</g>\n<use href="#blob" fill="{c["accent"]}"/>\n'
            f'<g fill="{c["over"]}" clip-path="url(#inside)">{word}</g>\n{band}\n'
            + "\n".join(groups) + f"\n{cursor}\n</svg>\n")
