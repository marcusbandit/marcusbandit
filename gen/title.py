from tokens import SANS, MONO, SIZE, RAMP, pct

THEMES = {
    "dark": {"text": RAMP[10], "sub": RAMP[8], "accent": "#7fb3d4"},
    "light": {"text": RAMP[1], "sub": RAMP[5], "accent": "#5b8fb0"},
}

PHRASES = [
    "building my own desktop, from the shell up",
    "Hyprland, Quickshell and a lot of QML",
    "studying at DTU",
]


def svg(theme):
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


