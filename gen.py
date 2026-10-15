#!/usr/bin/env python3
from pathlib import Path

OUT = Path(__file__).parent / "assets"

SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Ubuntu, Cantarell, 'Noto Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"

SIZE = {"small": 14, "normal": 18, "large": 34}

RAMP = ["#08090b", "#0f1114", "#181b1f", "#1d2126", "#262b31", "#3a4149",
        "#545d67", "#78838f", "#a5aeb8", "#d0d7dd", "#eef2f5"]

THEMES = {
    "dark": {
        "screen": RAMP[0], "band": RAMP[3], "text": RAMP[10], "sub": RAMP[8],
        "accent": "#7fb3d4", "cursor": RAMP[10], "cursorEdge": RAMP[0],
    },
    "light": {
        "screen": RAMP[10], "band": RAMP[9], "text": RAMP[1], "sub": RAMP[5],
        "accent": "#5b8fb0", "cursor": RAMP[1], "cursorEdge": RAMP[10],
    },
}

EASE = "cubic-bezier(0.16, 1, 0.3, 1)"

PHRASES = [
    "building my own desktop, from the shell up",
    "Hyprland, Quickshell and a lot of QML",
    "studying at DTU",
]


def pct(t, total):
    return f"{100 * t / total:.3f}%"


def title_svg(theme):
    c = THEMES[theme]
    w, h = 520, 84
    char_w = 0.6 * SIZE["normal"]
    type_s, delete_s, hold_s, gap_s = 0.065, 0.025, 2.2, 0.5
    spans, t = [], 0.6
    for p in PHRASES:
        n = len(p)
        start, typed = t, t + n * type_s
        held = typed + hold_s
        gone = held + n * delete_s
        spans.append((p, start, typed, held, gone))
        t = gone + gap_s
    total = t

    base_y = 70
    styles, texts = [], []
    for i, (p, start, typed, held, gone) in enumerate(spans):
        n = len(p)
        full = n * char_w
        shown_from = 0 if i == 0 else spans[i - 1][4]
        last = i == len(spans) - 1
        styles.append(f"""
    #clip{i} rect {{ animation: w{i} {total:.3f}s infinite; }}
    @keyframes w{i} {{
      0%, {pct(start, total)} {{ width: 0px; animation-timing-function: steps({n}, end); }}
      {pct(typed, total)}, {pct(held, total)} {{ width: {full:.1f}px; animation-timing-function: steps({n}, end); }}
      {pct(gone, total)}, 100% {{ width: 0px; }}
    }}
    #caret{i} {{ animation: c{i} {total:.3f}s infinite; }}
    @keyframes c{i} {{
      0%, {pct(shown_from, total)} {{ opacity: {1 if i == 0 else 0}; transform: translateX(0px); }}
      {pct(shown_from + 0.001, total)}, {pct(start, total)} {{ opacity: 1; transform: translateX(0px); animation-timing-function: steps({n}, end); }}
      {pct(typed, total)}, {pct(held, total)} {{ opacity: 1; transform: translateX({full:.1f}px); animation-timing-function: steps({n}, end); }}
      {pct(gone, total)} {{ opacity: 1; transform: translateX(0px); }}
      {pct(gone + 0.001, total)}, 100% {{ opacity: {1 if last else 0}; transform: translateX(0px); }}
    }}""")
        texts.append(f"""
  <clipPath id="clip{i}"><rect x="0" y="{base_y - 20}" width="0" height="28"/></clipPath>
  <text class="line" x="0" y="{base_y}" clip-path="url(#clip{i})">{p}</text>
  <g id="caret{i}"><rect class="caret" x="1" y="{base_y - 15}" width="2" height="19"/></g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    .name {{ font: 700 {SIZE["large"]}px {SANS}; fill: {c["text"]}; }}
    .line {{ font: 400 {SIZE["normal"]}px {MONO}; fill: {c["sub"]}; }}
    .caret {{ fill: {c["accent"]}; animation: blink 1s steps(1, end) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    {"".join(styles)}
    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; }}
      #clip0 rect {{ width: 100%; }}
      g[id^="caret"] {{ opacity: 0; }}
    }}
  </style>
  <text class="name" x="0" y="34">Marcus Rosado</text>{"".join(texts)}
</svg>
"""


def card_svg(theme):
    c = THEMES[theme]
    w, h = 800, 260
    r, band = 26, 14
    inner_r = r - band
    px_w, px_h = 470, 168
    px_x = (w - px_w) / 2
    rest_sx, rest_sy = 90 / px_w, band / px_h

    total = 10.0
    arrive, emerge, shown, leave, retract, empty = 1.3, 2.3, 2.7, 7.2, 8.1, 10.0

    start_x, start_y = w * 0.78, h * 0.86
    summon_x, summon_y = w / 2 + 18, px_h + 18
    edge_x, edge_y = w / 2, band * 0.6
    exit_x, exit_y = w * 0.26, h * 0.9

    band_path = (
        f"M{r},0 H{w - r} A{r},{r} 0 0 1 {w},{r} V{h - r} A{r},{r} 0 0 1 {w - r},{h} "
        f"H{r} A{r},{r} 0 0 1 0,{h - r} V{r} A{r},{r} 0 0 1 {r},0 Z "
        f"M{band + inner_r},{band} A{inner_r},{inner_r} 0 0 0 {band},{band + inner_r} "
        f"V{h - band - inner_r} A{inner_r},{inner_r} 0 0 0 {band + inner_r},{h - band} "
        f"H{w - band - inner_r} A{inner_r},{inner_r} 0 0 0 {w - band},{h - band - inner_r} "
        f"V{band + inner_r} A{inner_r},{inner_r} 0 0 0 {w - band - inner_r},{band} Z"
    )

    cx = w / 2
    ty = [band + 54, band + 92, band + 126]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <filter id="goo" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="blur"/>
      <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -11"/>
    </filter>
    <clipPath id="frame"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>
  </defs>
  <style>
    .title {{ font: 700 {SIZE["large"]}px {SANS}; fill: {c["text"]}; }}
    .tag {{ font: 400 {SIZE["normal"]}px {SANS}; fill: {c["sub"]}; }}
    .stack {{ font: 400 {SIZE["small"]}px {MONO}; fill: {c["accent"]}; }}

    #panel {{
      transform-box: fill-box; transform-origin: 50% 0%;
      animation: panel {total}s infinite;
    }}
    @keyframes panel {{
      0%, {pct(arrive, total)} {{ transform: scale({rest_sx:.4f}, {rest_sy:.4f}); animation-timing-function: {EASE}; }}
      {pct(emerge, total)}, {pct(leave + 0.5, total)} {{ transform: scale(1, 1); animation-timing-function: cubic-bezier(0.7, 0, 0.84, 0); }}
      {pct(retract, total)}, 100% {{ transform: scale({rest_sx:.4f}, {rest_sy:.4f}); }}
    }}

    #content {{ animation: content {total}s infinite; }}
    @keyframes content {{
      0%, {pct(emerge - 0.3, total)} {{ opacity: 0; transform: translateY(-8px); animation-timing-function: {EASE}; }}
      {pct(shown, total)}, {pct(leave + 0.2, total)} {{ opacity: 1; transform: translateY(0); animation-timing-function: ease-in; }}
      {pct(leave + 0.55, total)}, 100% {{ opacity: 0; transform: translateY(-8px); }}
    }}

    #cursor {{ animation: cursor {total}s infinite; }}
    @keyframes cursor {{
      0% {{ transform: translate({start_x}px, {start_y}px); opacity: 0; animation-timing-function: {EASE}; }}
      3% {{ transform: translate({start_x}px, {start_y}px); opacity: 1; animation-timing-function: {EASE}; }}
      {pct(arrive, total)} {{ transform: translate({edge_x}px, {edge_y}px); animation-timing-function: {EASE}; }}
      {pct(emerge + 0.4, total)}, {pct(leave, total)} {{ transform: translate({summon_x}px, {summon_y}px); opacity: 1; animation-timing-function: {EASE}; }}
      {pct(retract + 0.6, total)} {{ transform: translate({exit_x}px, {exit_y}px); opacity: 1; }}
      {pct(empty - 0.4, total)}, 100% {{ transform: translate({exit_x}px, {exit_y}px); opacity: 0; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; }}
      #panel {{ transform: none; }}
      #content {{ opacity: 1; }}
      #cursor {{ opacity: 0; }}
    }}
  </style>

  <rect width="{w}" height="{h}" rx="{r}" fill="{c["screen"]}"/>
  <g clip-path="url(#frame)">
    <g filter="url(#goo)" fill="{c["band"]}">
      <path d="{band_path}" fill-rule="evenodd"/>
      <rect id="panel" x="{px_x}" y="0" width="{px_w}" height="{px_h}" rx="22"/>
    </g>
  </g>

  <g id="content" text-anchor="middle">
    <text class="title" x="{cx}" y="{ty[0]}">banditshell</text>
    <text class="tag" x="{cx}" y="{ty[1]}">Empty at rest, summoned on intent.</text>
    <text class="stack" x="{cx}" y="{ty[2]}">quickshell / qml / hyprland</text>
  </g>

  <g id="cursor">
    <path d="M0,0 V19 L4.6,14.6 L8,22.4 L11.4,21 L8,13.4 H14.4 Z" fill="{c["cursor"]}" stroke="{c["cursorEdge"]}" stroke-width="1.4" stroke-linejoin="round"/>
  </g>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"title-{theme}.svg").write_text(title_svg(theme))
        (OUT / f"banditshell-{theme}.svg").write_text(card_svg(theme))
