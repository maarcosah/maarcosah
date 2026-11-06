#!/usr/bin/env python3
"""Render the About me card: a Python REPL session that types itself out.

Edit LINES and rerun:  python scripts/gen_about.py
"""
import os
from xml.sax.saxutils import escape

# each line is a list of (text, style); styles map to THEMES colors
P = ("prompt", ">>> ")
LINES = [
    [P, ("kw", "from "), ("code", "maarcosah "), ("kw", "import "), ("attr", "Marcos")],
    [P, ("code", "me = "), ("attr", "Marcos"), ("punct", "()")],
    [P, ("code", "me."), ("attr", "focus")],
    [("punct", "["), ("str", "'Data Engineering'"), ("punct", ", "), ("str", "'Data Science'"), ("punct", "]")],
    [P, ("code", "me."), ("attr", "wrangles_with")],
    [("punct", "["), ("str", "'pandas'"), ("punct", ", "), ("str", "'Dask'"), ("punct", ", "),
     ("str", "'Parquet'"), ("punct", ", "), ("str", "'SQL'"), ("punct", "]")],
    [P, ("code", "me."), ("attr", "trains_with")],
    [("punct", "["), ("str", "'scikit-learn'"), ("punct", ", "), ("str", "'TensorFlow'"), ("punct", "]")],
    [P, ("code", "me."), ("attr", "background")],
    [("str", "'software dev: web apps, backends & the odd Unity game'")],
    [P, ("code", "me."), ("attr", "hobbies")],
    [("punct", "["), ("str", "'gym'"), ("punct", ", "), ("str", "'music'"), ("punct", ", "),
     ("str", "'videogames'"), ("punct", "]")],
    [P],
]

THEMES = {
    "dark": {"bg": "#0d1117", "bar": "#161b22", "border": "#30363d", "prompt": "#F70000",
             "code": "#c9d1d9", "kw": "#ff7b72", "attr": "#d2a8ff", "str": "#a5d6ff",
             "punct": "#8b949e", "title": "#8b949e"},
    "light": {"bg": "#ffffff", "bar": "#f6f8fa", "border": "#d0d7de", "prompt": "#B00000",
              "code": "#1f2328", "kw": "#cf222e", "attr": "#8250df", "str": "#0a3069",
              "punct": "#57606a", "title": "#57606a"},
}

W, PAD, BAR, LINE_H, STEP = 720, 24, 36, 24, 0.45


def build(theme):
    c = THEMES[theme]
    h = BAR + PAD * 2 + len(LINES) * LINE_H
    last = len(LINES) - 1
    css = (
        "@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
        "@keyframes blink{50%{opacity:0}}"
        ".l{opacity:0;animation:in .35s ease-out forwards}"
        f".cur{{opacity:0;animation:in .2s {last * STEP:.2f}s forwards,"
        f"blink 1s step-end {last * STEP + 0.2:.2f}s infinite}}"
        + "".join(f".l{i}{{animation-delay:{i * STEP:.2f}s}}" for i in range(len(LINES)))
    )
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" '
        f'aria-label="About me">',
        f"<style>{css}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<path d="M10.5 .5h{W - 21}a10 10 0 0 1 10 10V{BAR}H.5V10.5a10 10 0 0 1 10-10z" fill="{c["bar"]}"/>',
        f'<line x1=".5" y1="{BAR}" x2="{W - .5}" y2="{BAR}" stroke="{c["border"]}"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{20 + i * 20}" cy="{BAR / 2}" r="6" fill="{color}"/>')
    out.append(f'<text x="{W / 2}" y="{BAR / 2 + 4}" font-size="12" fill="{c["title"]}" '
               f'text-anchor="middle">marcos@data: ~ python3</text>')

    for i, segs in enumerate(LINES):
        y = BAR + PAD + 14 + i * LINE_H
        spans = "".join(f'<tspan fill="{c[s]}">{escape(t)}</tspan>' for s, t in segs)
        out.append(f'<text class="l l{i}" x="{PAD}" y="{y}" font-size="14" xml:space="preserve">{spans}</text>')

    # ">>> " is 4 chars of a 14px monospace font (~8.4px each)
    cy = BAR + PAD + last * LINE_H
    out.append(f'<rect class="cur" x="{PAD + 4 * 8.4:.1f}" y="{cy + 1}" width="9" height="17" fill="{c["prompt"]}"/>')
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    for theme in THEMES:
        path = os.path.join(out_dir, f"about-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(theme))
        print("wrote", path)
