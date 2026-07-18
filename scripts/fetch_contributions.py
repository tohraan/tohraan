#!/usr/bin/env python3
"""Scrape the public GitHub contributions calendar (no auth, no token).

GitHub serves the profile's contribution calendar as a public HTML
fragment at /users/<username>/contributions -- the same markup the
profile page itself uses. We pull day cells (date + GitHub's own 0-4
intensity level) and their tooltip text (exact count), then derive
streaks / best day / monthly totals.

    python scripts/fetch_contributions.py
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "tohraan"
URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"}

TOOLTIP_RE = re.compile(r"^(No|\d+)\s+contributions?\s+on\s+.+\.$", re.IGNORECASE)
COUNT_RE = re.compile(r"^(No|\d+)")


def fetch_html() -> str:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    tooltip_by_id = {}
    for tip in soup.select("tool-tip[for]"):
        tooltip_by_id[tip["for"]] = tip.get_text(strip=True)

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        cell_id = td.get("id")
        raw_date = td["data-date"]
        level = int(td.get("data-level", 0))
        tooltip = tooltip_by_id.get(cell_id, "")

        count = 0
        m = COUNT_RE.match(tooltip)
        if m and m.group(1).lower() != "no":
            count = int(m.group(1))

        days.append({"date": raw_date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    total = sum(d["count"] for d in days)

    longest = current_run = 0
    for d in days:
        if d["count"] > 0:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 0

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"])

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> None:
    html = fetch_html()
    days = parse_days(html)
    if not days:
        print("warning: no contribution cells parsed; GitHub markup may have changed", file=sys.stderr)

    stats = compute_stats(days)

    out = {
        "username": USERNAME,
        "generated_at": date.today().isoformat(),
        "days": days,
        "stats": stats,
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path}: {len(days)} days, {stats.get('total_contributions', 0)} total contributions")


if __name__ == "__main__":
    main()
