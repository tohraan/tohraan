#!/usr/bin/env python3
"""Convert a prepped grayscale photo into a monochrome, self-typing ASCII SVG.

Downsamples to a ~100x53 character grid, maps brightness to a density
ramp, and wraps each row in a clip-path that wipes left-to-right with a
small block cursor, staggered top to bottom. Plays once and freezes
(SMIL, no <script>, no loop) so it renders and animates on GitHub.

    python scripts/make_ascii_svg.py source-prepped.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears background
COLS = 100
ROWS = 53

FONT_SIZE = 14
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.15

ROW_DURATION = 0.55   # seconds for one row's wipe
ROW_STAGGER = 0.035   # seconds between the start of consecutive rows

# Monochrome fill. GitHub renders the profile README on a theme-dependent
# page background (no card), so a single flat gray risks low contrast in
# one theme. We use one color at a time via a prefers-color-scheme media
# query inside the SVG -- still monochrome, just theme-adaptive.
FILL_LIGHT = "#3b4048"
FILL_DARK = "#c9d1d9"


def image_to_grid(path: Path) -> list[str]:
    img = Image.open(path).convert("L")
    w, h = img.size

    target_ratio = (COLS * CHAR_W) / (ROWS * CHAR_H)
    src_ratio = w / h
    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((COLS, ROWS), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    idx = np.clip(((255 - arr) / 255) * (len(RAMP) - 1), 0, len(RAMP) - 1).round().astype(int)
    return ["".join(RAMP[i] for i in row) for row in idx]


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" '
        f'width="{width:.0f}" height="{height:.0f}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>",
        f"  text {{ fill: {FILL_LIGHT}; }}",
        "  @media (prefers-color-scheme: dark) {",
        f"    text {{ fill: {FILL_DARK}; }}",
        "  }",
        "  .cursor { fill: inherit; }",
        "</style>",
    ]

    for r, row_text in enumerate(rows):
        y = (r + 1) * CHAR_H - CHAR_H * 0.28
        clip_id = f"clip{r}"
        begin = r * ROW_STAGGER
        row_px_width = width

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'  <rect x="0" y="{r * CHAR_H:.1f}" width="0" height="{CHAR_H:.1f}">')
        parts.append(
            f'    <animate attributeName="width" from="0" to="{row_px_width:.1f}" '
            f'begin="{begin:.3f}s" dur="{ROW_DURATION:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1" />'
        )
        parts.append("  </rect>")
        parts.append("</clipPath>")

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(f'  <text x="0" y="{y:.1f}" font-size="{FONT_SIZE}" xml:space="preserve">{esc(row_text)}</text>')
        parts.append("</g>")

        cursor_h = CHAR_H * 0.85
        cursor_y = r * CHAR_H + CHAR_H * 0.1
        parts.append(
            f'<rect class="cursor" x="0" y="{cursor_y:.1f}" width="{CHAR_W:.1f}" height="{cursor_h:.1f}" opacity="0">'
        )
        parts.append(
            f'  <animate attributeName="x" from="0" to="{max(row_px_width - CHAR_W, 0):.1f}" '
            f'begin="{begin:.3f}s" dur="{ROW_DURATION:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1" />'
        )
        parts.append(
            f'  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.85;1" '
            f'begin="{begin:.3f}s" dur="{ROW_DURATION:.2f}s" fill="freeze" />'
        )
        parts.append("</rect>")

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "source-prepped.png"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "tohraan-ascii.svg"
    rows = image_to_grid(src)
    out.write_text(build_svg(rows), encoding="utf-8")
    total = ROW_STAGGER * (ROWS - 1) + ROW_DURATION
    print(f"wrote {out} ({COLS}x{ROWS} grid, ~{total:.2f}s to fully print)")


if __name__ == "__main__":
    main()
