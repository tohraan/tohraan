#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG.

A title bar plus key/value rows (Now / Prev / Stack / Highlights), each
line fading and sliding in on a short stagger -- CSS keyframes, plays
once and freezes. Set STATIC=1 to skip the animation and emit a frozen
frame (handy for local Quick Look previews).

    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py    # frozen preview frame
"""
import os
from pathlib import Path

PROMPT = "tohraan@github"

# --- content -------------------------------------------------------------
NOW = "Founder & CEO @ Triaxon Automation"
PREV = "CRM Developer @ Weez Entertainment"
STACK = "Python, TS, React, Next.js, OpenAI API"
HIGHLIGHTS = [
    "Closed first paying B2B clients before age 19",
    "3rd place, Deriv AI Hackathon (agentic AI)",
    "Building ONCA (AI fintech), targeting YC",
]
# --------------------------------------------------------------------------

WIDTH = 500
PAD_X = 20
TITLEBAR_H = 34
ROW_H = 24
GAP_AFTER_TITLE = 14
GAP_AFTER_KV = 6

KEY_COLOR = "#39d353"
MUTED_COLOR = "#6e7681"
VALUE_LIGHT = "#3b4048"
VALUE_DARK = "#c9d1d9"
BORDER_LIGHT = "#d0d7de"
BORDER_DARK = "#30363d"
TITLEBAR_BG = "#161b22"

STAGGER = 0.10
ROW_DUR = 0.38

STATIC = os.environ.get("STATIC") == "1"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kv_row(y: float, key: str, value: str, delay: float, parts: list[str]) -> None:
    anim = "" if STATIC else (
        f' style="animation-delay:{delay:.3f}s"'
    )
    cls = "row" if not STATIC else "row row-static"
    parts.append(f'<g class="{cls}"{anim}>')
    parts.append(f'  <text class="key" x="{PAD_X}" y="{y}">{esc(key)}</text>')
    parts.append(f'  <text class="value" x="{PAD_X + 100}" y="{y}">{esc(value)}</text>')
    parts.append('</g>')


def bullet_row(y: float, text: str, delay: float, parts: list[str]) -> None:
    anim = "" if STATIC else (
        f' style="animation-delay:{delay:.3f}s"'
    )
    cls = "row" if not STATIC else "row row-static"
    parts.append(f'<g class="{cls}"{anim}>')
    parts.append(f'  <text class="value" x="{PAD_X + 12}" y="{y}">- {esc(text)}</text>')
    parts.append('</g>')


def build_svg() -> str:
    rows = 3 + 1 + len(HIGHLIGHTS)  # Now, Prev, Stack, Highlights label, bullets
    height = TITLEBAR_H + GAP_AFTER_TITLE + rows * ROW_H + GAP_AFTER_KV + 14

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>",
        f"  .panel {{ fill: none; stroke: {BORDER_LIGHT}; }}",
        f"  .titlebar {{ fill: {TITLEBAR_BG}; }}",
        f"  .prompt {{ fill: #ffffff; font-size: 13px; font-weight: 600; }}",
        f"  .dot {{ fill: {MUTED_COLOR}; opacity: 0.6; }}",
        f"  .key {{ fill: {KEY_COLOR}; font-size: 13px; font-weight: 600; }}",
        f"  .value {{ fill: {VALUE_LIGHT}; font-size: 13px; }}",
        "  @media (prefers-color-scheme: dark) {",
        f"    .panel {{ stroke: {BORDER_DARK}; }}",
        f"    .value {{ fill: {VALUE_DARK}; }}",
        "  }",
    ]

    if not STATIC:
        parts.append(
            "  .row { opacity: 0; transform: translateX(-8px); "
            "animation: rowIn 0.38s cubic-bezier(0.25,0.6,0.3,1) both; }"
        )
        parts.append(
            "  @keyframes rowIn { 0% { opacity: 0; transform: translateX(-8px); } "
            "100% { opacity: 1; transform: translateX(0); } }"
        )
    else:
        parts.append("  .row-static { opacity: 1; transform: translateX(0); }")

    parts.append("</style>")

    # panel border
    parts.append(f'<rect class="panel" x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" ry="8" />')

    # title bar
    parts.append(f'<path class="titlebar" d="M0.5 8.5 a8 8 0 0 1 8 -8 h{WIDTH - 17} a8 8 0 0 1 8 8 v{TITLEBAR_H - 8.5} h-{WIDTH - 1} z" />')
    for i, cx in enumerate((18, 34, 50)):
        parts.append(f'<circle class="dot" cx="{cx}" cy="{TITLEBAR_H / 2}" r="4.5" />')
    parts.append(f'<text class="prompt" x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4.5}" text-anchor="middle">{esc(PROMPT)}</text>')

    y = TITLEBAR_H + GAP_AFTER_TITLE + ROW_H * 0.5
    idx = 0

    kv_row(y, "Now", NOW, idx * STAGGER, parts); idx += 1; y += ROW_H
    kv_row(y, "Prev", PREV, idx * STAGGER, parts); idx += 1; y += ROW_H
    kv_row(y, "Stack", STACK, idx * STAGGER, parts); idx += 1; y += ROW_H

    parts.append(f'<g class="row{"" if not STATIC else " row-static"}" {"" if STATIC else f"style=\"animation-delay:{idx * STAGGER:.3f}s\""}>')
    parts.append(f'  <text class="key" x="{PAD_X}" y="{y}">Highlights</text>')
    parts.append('</g>')
    idx += 1
    y += ROW_H

    for h in HIGHLIGHTS:
        bullet_row(y, h, idx * STAGGER, parts)
        idx += 1
        y += ROW_H

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "info-card.svg"
    out.write_text(build_svg(), encoding="utf-8")
    mode = "static" if STATIC else "animated"
    print(f"wrote {out} ({mode})")


if __name__ == "__main__":
    main()
