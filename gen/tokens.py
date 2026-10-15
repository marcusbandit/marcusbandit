import math

SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Ubuntu, Cantarell, 'Noto Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"

SIZE = {"small": 14, "normal": 18, "large": 34}

RAMP = ["#08090b", "#0f1114", "#181b1f", "#1d2126", "#262b31", "#3a4149",
        "#545d67", "#78838f", "#a5aeb8", "#d0d7dd", "#eef2f5"]

THEMES = {
    "dark": {
        "screen": RAMP[0], "band": RAMP[3], "raised": RAMP[4], "line": RAMP[5],
        "text": RAMP[10], "sub": RAMP[8], "faint": RAMP[6],
        "accent": "#7fb3d4", "accentDim": "#5b8fb0", "accentBright": "#b8dcf0",
        "alarm": "#ff7a4d", "cursor": RAMP[10], "cursorEdge": RAMP[0],
    },
    "light": {
        "screen": RAMP[10], "band": RAMP[9], "raised": RAMP[8], "line": RAMP[7],
        "text": RAMP[1], "sub": RAMP[5], "faint": RAMP[7],
        "accent": "#5b8fb0", "accentDim": "#7fb3d4", "accentBright": "#3a6f91",
        "alarm": "#e0582b", "cursor": RAMP[1], "cursorEdge": RAMP[10],
    },
}

EASE = "cubic-bezier(0.16, 1, 0.3, 1)"
KAPPA = 0.5522847498


def pct(t, total):
    return f"{100 * t / total:.3f}%"


def num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def smooth(targets, total, fps=30, speed=9.0):
    """Exponential smoothing toward a step schedule of targets.

    targets: [(time_s, value), ...] sorted; value is a float or a tuple of floats.
    Returns (times, values) sampled at fps over [0, total], where the value chases
    the most recent target with position += (target - position) * (1 - exp(-speed * dt)).
    The first and last samples are pinned to the first target so the loop is seamless.
    """
    dt = 1 / fps
    tup = isinstance(targets[0][1], (tuple, list))
    vec = lambda v: list(v) if tup else [v]
    pos = vec(targets[0][1])
    factor = 1 - math.exp(-speed * dt)
    times, values = [], []
    steps = round(total * fps)
    for k in range(steps + 1):
        t = k * dt
        target = vec(targets[0][1])
        for tt, v in targets:
            if tt <= t + 1e-9:
                target = vec(v)
        if k:
            pos = [p + (g - p) * factor for p, g in zip(pos, target)]
        times.append(t)
        values.append(tuple(pos) if tup else pos[0])
    values[-1] = tuple(vec(targets[0][1])) if tup else targets[0][1]
    return times, values


def thin(times, values, eps=0.05):
    """Drop samples that a straight line between the kept neighbours reproduces within eps."""
    def flat(v):
        return v if isinstance(v, (tuple, list)) else (v,)
    vals = [flat(v) for v in values]

    def fits(a, b):
        t0, t1 = times[a], times[b]
        for i in range(a + 1, b):
            u = (times[i] - t0) / (t1 - t0)
            if any(abs(x0 + (x1 - x0) * u - x) > eps for x0, x1, x in zip(vals[a], vals[b], vals[i])):
                return False
        return True

    keep, a, n = [0], 0, len(times)
    while a < n - 1:
        b = a + 1
        while b + 1 < n and fits(a, b + 1):
            b += 1
        keep.append(b)
        a = b
    return [times[i] for i in keep], [values[i] for i in keep]


def animate(attr, times, values, total, fmt=num):
    """SMIL <animate> over a sampled track; linear between samples, looped."""
    kt = ";".join("0" if t <= 0 else "1" if t >= total else f"{t / total:.5f}" for t in times)
    vs = ";".join(fmt(v) for v in values)
    return (f'<animate attributeName="{attr}" dur="{num(total)}s" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="{kt}" values="{vs}"/>')


def rounded_rect(x, y, w, h, r):
    """Rounded rectangle as cubics only, so every instance shares one command structure
    and SMIL can interpolate between any two of them."""
    r = max(0.0, min(r, w / 2, h / 2))
    k = r * (1 - KAPPA)
    return (f"M{num(x + r)},{num(y)} H{num(x + w - r)} "
            f"C{num(x + w - k)},{num(y)} {num(x + w)},{num(y + k)} {num(x + w)},{num(y + r)} "
            f"V{num(y + h - r)} "
            f"C{num(x + w)},{num(y + h - k)} {num(x + w - k)},{num(y + h)} {num(x + w - r)},{num(y + h)} "
            f"H{num(x + r)} "
            f"C{num(x + k)},{num(y + h)} {num(x)},{num(y + h - k)} {num(x)},{num(y + h - r)} "
            f"V{num(y + r)} "
            f"C{num(x)},{num(y + k)} {num(x + k)},{num(y)} {num(x + r)},{num(y)} Z")


def closed_curve(points):
    """Closed Catmull-Rom spline through points, as cubics; fixed structure for a fixed count."""
    n = len(points)
    out = [f"M{num(points[0][0])},{num(points[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{num(c1[0])},{num(c1[1])} {num(c2[0])},{num(c2[1])} {num(p2[0])},{num(p2[1])}")
    return " ".join(out) + " Z"


def chase(values, fps=30, speed=9.0):
    """Exponential smoothing of an already sampled track, one more pass, same house rule.
    Rounds off the instant start that a step target gives."""
    factor = 1 - math.exp(-speed / fps)
    tup = isinstance(values[0], (tuple, list))
    pos = list(values[0]) if tup else [values[0]]
    out = []
    for v in values:
        g = list(v) if tup else [v]
        pos = [p + (q - p) * factor for p, q in zip(pos, g)]
        out.append(tuple(pos) if tup else pos[0])
    out[0] = values[0]
    out[-1] = values[-1]
    return out


def f1(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Outline:
    """Closed outline of lines and cubics with a fixed command structure; d() can reverse it."""

    def __init__(self, start):
        self.start, self.segs = start, []

    def end(self):
        return self.segs[-1][-1] if self.segs else self.start

    def line(self, p):
        self.segs.append((p,))

    def curve(self, c1, c2, p):
        self.segs.append((c1, c2, p))

    def corner(self, t0, t1, r):
        p0 = self.end()
        p1 = (p0[0] + (t0[0] + t1[0]) * r, p0[1] + (t0[1] + t1[1]) * r)
        k = KAPPA * r
        self.curve((p0[0] + t0[0] * k, p0[1] + t0[1] * k), (p1[0] - t1[0] * k, p1[1] - t1[1] * k), p1)

    def d(self, reverse=False):
        pt = lambda p: f"{f1(p[0])},{f1(p[1])}"
        if not reverse:
            body = "".join(("L" if len(s) == 1 else "C") + " ".join(pt(p) for p in s) for s in self.segs)
            return f"M{pt(self.start)}{body}Z"
        ends = [self.start] + [s[-1] for s in self.segs]
        out = [f"M{pt(ends[-1])}"]
        for i in range(len(self.segs) - 1, -1, -1):
            s = self.segs[i]
            out.append("L" + pt(ends[i]) if len(s) == 1 else "C" + " ".join(pt(p) for p in (s[1], s[0], ends[i])))
        return "".join(out) + "Z"


def bump(out, P, c, w, d, f, r):
    """Panel bump along an edge in frame P(u, v): concave fillet, side, convex corner, face,
    convex corner, side, concave fillet. Same commands for every size, flat when d is 0."""
    a, b, k = c - w / 2, c + w / 2, KAPPA
    out.line(P(a - f, 0))
    out.curve(P(a - f + k * f, 0), P(a, f - k * f), P(a, f))
    out.line(P(a, d - r))
    out.curve(P(a, d - r + k * r), P(a + r - k * r, d), P(a + r, d))
    out.line(P(b - r, d))
    out.curve(P(b - r + k * r, d), P(b, d - r + k * r), P(b, d - r))
    out.line(P(b, f))
    out.curve(P(b, f - k * f), P(b + f - k * f, 0), P(b + f, 0))
