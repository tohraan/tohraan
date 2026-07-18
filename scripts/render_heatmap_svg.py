#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53-week x 7-day heatmap SVG.

Boxes slide down diagonally (staggered by week+day) and freeze -- no
looping "glow". Level 5 is a neon top-end reserved for the single best
day, on top of GitHub's own 0-4 intensity levels.

    python scripts/render_heatmap_svg.py
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
STEP = CELL + GAP
MARGIN_LEFT = 30
MARGIN_TOP = 26
LEGEND_GAP = 20
FOOTER_GAP = 22

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ROW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}

LABEL_LIGHT = "#57606a"
LABEL_DARK = "#8b949e"


def sun0_weekday(d: date) -> int:
    return (d.weekday() + 1) % 7  # 0=Sunday ... 6=Saturday


def load_data(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_grid(days: list[dict]):
    by_date = {datetime.strptime(d["date"], "%Y-%m-%d").date(): d for d in days}
    min_date, max_date = min(by_date), max(by_date)

    grid_start = min_date - timedelta(days=sun0_weekday(min_date))
    grid_end = max_date + timedelta(days=6 - sun0_weekday(max_date))

    total_days = (grid_end - grid_start).days + 1
    weeks = total_days // 7

    grid = [[None] * 7 for _ in range(weeks)]
    for i in range(total_days):
        d = grid_start + timedelta(days=i)
        week_idx, day_idx = divmod(i, 7)
        grid[week_idx][day_idx] = by_date.get(d)

    return grid, grid_start, weeks


def level_for(entry: dict | None, best_count: int) -> int:
    if entry is None or entry["count"] == 0:
        return 0
    if best_count > 0 and entry["count"] == best_count:
        return 5
    return max(1, min(4, entry.get("level", 1)))


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(grid, grid_start: date, weeks: int, stats: dict) -> str:
    width = MARGIN_LEFT + weeks * STEP
    grid_height = MARGIN_TOP + 7 * STEP
    legend_y = grid_height + LEGEND_GAP
    footer_y = legend_y + CELL + FOOTER_GAP
    height = footer_y + 6

    best_count = stats.get("best_day", {}).get("count", 0)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>",
        "  .cell { animation: slideIn 0.45s cubic-bezier(0.2,0.6,0.3,1) both; }",
        "  @keyframes slideIn { 0% { opacity: 0; transform: translateY(-9px); } 100% { opacity: 1; transform: translateY(0); } }",
        f"  .label {{ fill: {LABEL_LIGHT}; font-size: 10px; }}",
        f"  .footer {{ fill: {LABEL_LIGHT}; font-size: 11px; }}",
        "  @media (prefers-color-scheme: dark) {",
        f"    .label {{ fill: {LABEL_DARK}; }}",
        f"    .footer {{ fill: {LABEL_DARK}; }}",
        "  }",
        "</style>",
    ]

    last_month = None
    for week_idx in range(weeks):
        ref_date = grid_start + timedelta(days=week_idx * 7)
        if ref_date.month != last_month:
            x = MARGIN_LEFT + week_idx * STEP
            parts.append(f'<text class="label" x="{x}" y="{MARGIN_TOP - 9}">{MONTH_ABBR[ref_date.month - 1]}</text>')
            last_month = ref_date.month

    for day_idx, label in ROW_LABELS.items():
        y = MARGIN_TOP + day_idx * STEP + CELL - 1
        parts.append(f'<text class="label" x="0" y="{y}">{label}</text>')

    for week_idx, week in enumerate(grid):
        for day_idx, entry in enumerate(week):
            x = MARGIN_LEFT + week_idx * STEP
            y = MARGIN_TOP + day_idx * STEP
            lvl = level_for(entry, best_count)
            color = PALETTE[lvl]
            delay = (week_idx + day_idx) * 0.011

            title = ""
            if entry is not None:
                c = entry["count"]
                title = f'<title>{c} contribution{"s" if c != 1 else ""} on {esc(entry["date"])}</title>'

            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" ry="2.5" '
                f'fill="{color}" style="animation-delay:{delay:.3f}s">{title}</rect>'
            )

    legend_x = MARGIN_LEFT
    parts.append(f'<text class="footer" x="{legend_x}" y="{legend_y + CELL - 2}">Less</text>')
    lx = legend_x + 32
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx + i * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" ry="2.5" fill="{color}" />')
    parts.append(f'<text class="footer" x="{lx + len(PALETTE) * STEP + 6}" y="{legend_y + CELL - 2}">More</text>')

    total = stats.get("total_contributions", 0)
    cur = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    best = stats.get("best_day", {})
    footer_text = (
        f'{total:,} contributions in the last year   ·   '
        f'current streak {cur}d   ·   longest streak {longest}d   ·   '
        f'best day {esc(best.get("date", "-"))} ({best.get("count", 0)})'
    )
    parts.append(f'<text class="footer" x="{MARGIN_LEFT}" y="{footer_y}">{footer_text}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    data = load_data(root / "data" / "contributions.json")
    grid, grid_start, weeks = build_grid(data["days"])
    svg = build_svg(grid, grid_start, weeks, data.get("stats", {}))

    out_path = root / "contrib-heatmap.svg"
    out_path.write_text(svg, encoding="utf-8")
    print(f"wrote {out_path} ({weeks} weeks x 7 days)")


if __name__ == "__main__":
    main()
