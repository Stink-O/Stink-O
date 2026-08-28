#!/usr/bin/env python3
"""Scrape the public contributions calendar into data/contributions.json,
then add commits made in forks (which GitHub's own graph excludes).

Works unauthenticated; set GITHUB_TOKEN for a higher API rate limit
(GitHub Actions provides one automatically).

Usage: python scripts/fetch_contributions.py
"""
import datetime as dt
import json
import os

import requests
from bs4 import BeautifulSoup

USERNAME = "Stink-O"
URL = f"https://github.com/users/{USERNAME}/contributions"
API = "https://api.github.com"


def api_get(path, **params):
    headers = {"User-Agent": "profile-art-refresh",
               "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(f"{API}{path}", headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fork_commit_dates(since):
    """Dates of commits authored by USERNAME on the default branch of each
    fork — the commits GitHub's contribution graph leaves out."""
    dates = []
    repos = api_get(f"/users/{USERNAME}/repos", per_page=100, type="owner")
    for repo in repos:
        if not repo.get("fork"):
            continue
        page = 1
        while True:
            commits = api_get(
                f"/repos/{repo['full_name']}/commits",
                author=USERNAME, since=since, per_page=100, page=page,
            )
            for c in commits:
                dates.append(c["commit"]["author"]["date"][:10])
            if len(commits) < 100:
                break
            page += 1
    return dates


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

    # Fold in fork commits, which GitHub's graph doesn't count
    fork_days = 0
    try:
        for date in fork_commit_dates(since=min(days) + "T00:00:00Z"):
            if date in days:
                days[date]["count"] += 1
                fork_days += 1
    except requests.RequestException as e:
        print(f"warning: skipping fork commits ({e})")

    # Recompute levels from merged counts (quartiles of nonzero days)
    nonzero = sorted(d["count"] for d in days.values() if d["count"] > 0)
    if nonzero:
        qs = [nonzero[int(len(nonzero) * q)] for q in (0.25, 0.5, 0.75)]
        for d in days.values():
            c = d["count"]
            d["level"] = 0 if c == 0 else 1 + sum(c > q for q in qs)

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
    print(f"{total} contributions across {len(ordered)} days "
          f"({fork_days} from forks); streak {current} (longest {longest})")


if __name__ == "__main__":
    main()
