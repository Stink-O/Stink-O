#!/usr/bin/env python3
"""Fetch the live numbers the panes show (followers, repo count, stars per
repo) into data/profile.json, so nothing on the profile is typed by hand.

Works unauthenticated; set GITHUB_TOKEN for a higher API rate limit.

Usage: python scripts/fetch_profile.py
"""
import datetime as dt
import json

from fetch_contributions import USERNAME, api_get


def main():
    user = api_get(f"/users/{USERNAME}")
    repos = api_get(f"/users/{USERNAME}/repos", per_page=100, type="owner")
    data = {
        "fetched": dt.date.today().isoformat(),
        "followers": user["followers"],
        "public_repos": user["public_repos"],
        "stars": sum(r["stargazers_count"] for r in repos),
        "repos": {
            r["name"]: {
                "stars": r["stargazers_count"],
                "forks": r["forks_count"],
                "language": r["language"],
            }
            for r in repos
        },
    }
    with open("data/profile.json", "w") as f:
        json.dump(data, f, indent=1)
    print(f"wrote data/profile.json ({data['stars']} stars, {len(repos)} repos)")


if __name__ == "__main__":
    main()
