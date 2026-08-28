#!/usr/bin/env python3
"""Scrape the public contributions calendar (no token needed) into
data/contributions.json.

Usage: python scripts/fetch_contributions.py
"""
import datetime as dt
import json

import requests
from bs4 import BeautifulSoup

USERNAME = "Stink-O"
URL = f"https://github.com/users/{USERNAME}/contributions"


def main():
    r = requests.get(URL, headers={"User-Agent": "profile-art-refresh"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    days = {}
    # Day cells carry data-date + data-level; the count lives in a tooltip
    # sibling ("N contributions on ...") or the cell text.
    tooltips = {}
    for tt in soup.select("tool-tip"):
        target = tt.get("for", "")
        tooltips[target] = tt.get_text(strip=True)

    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        date = cell["data-date"]
        level = int(cell.get("data-level", 0))
        text = tooltips.get(cell.get("id", ""), cell.get_text(strip=True))
        first = text.split(" ")[0].replace(",", "")
        count = int(first) if first.isdigit() else (0 if first.lower() == "no" else level)
        days[date] = {"count": count, "level": level}

    if not days:
        raise SystemExit("no day cells parsed — GitHub markup may have changed")

    ordered = sorted(days)
    counts = [days[d]["count"] for d in ordered]
    total = sum(counts)

    # streaks
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    current = 0
    for d in reversed(ordered):
        if days[d]["count"] > 0:
            current += 1
        elif d != ordered[-1]:  # today being 0 doesn't break the streak
            break

    best_day = max(ordered, key=lambda d: days[d]["count"])
    monthly = {}
    for d in ordered:
        monthly[d[:7]] = monthly.get(d[:7], 0) + days[d]["count"]

    out = {
        "fetched": dt.date.today().isoformat(),
        "username": USERNAME,
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best_day, "count": days[best_day]["count"]},
        "monthly": monthly,
        "days": {d: days[d] for d in ordered},
    }
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"{total} contributions across {len(ordered)} days; "
          f"streak {current} (longest {longest})")


if __name__ == "__main__":
    main()
