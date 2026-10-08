#!/usr/bin/env python3
"""
Repair the Stars and Repositories trophies in the locally generated SVG.

The current Go trophy generator queries stargazers through a GraphQL connection
without a first/last argument, which GitHub's GraphQL API now requires.
We keep the generator for the rest of the card and repair these two metrics
from GitHub's public REST API before publishing the SVG.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USERNAME = "Advait550"
SVG_PATH = Path("dist/github-trophies.svg")


def github_json(url: str):
    token = os.environ.get("GITHUB_TOKEN", "")
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def get_public_repos():
    repos = []
    page = 1
    while True:
        data = github_json(
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&type=owner&sort=full_name&page={page}"
        )
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def rank_info(score: int, kind: str):
    if kind == "Stars":
        conditions = [
            ("SSS", "Super Stargazer", 2000),
            ("SS", "High Stargazer", 700),
            ("S", "Stargazer", 200),
            ("AAA", "Super Star", 100),
            ("AA", "High Star", 50),
            ("A", "You are a Star", 30),
            ("B", "Middle Star", 10),
            ("C", "First Star", 1),
        ]
    else:
        conditions = [
            ("SSS", "God Repo Creator", 50),
            ("SS", "Deep Repo Creator", 45),
            ("S", "Super Repo Creator", 40),
            ("AAA", "Ultra Repo Creator", 35),
            ("AA", "Hyper Repo Creator", 30),
            ("A", "High Repo Creator", 20),
            ("B", "Middle Repo Creator", 10),
            ("C", "First Repository", 1),
        ]

    for i, (rank, message, required) in enumerate(conditions):
        if score >= required:
            next_required = conditions[i - 1][2] if i > 0 else None
            if next_required is None:
                progress = 1.0
            else:
                progress = max(
                    0.0,
                    min(1.0, (score - required) / (next_required - required)),
                )
            return rank, message, f"{score}pt", progress

    return "UNKNOWN", "Unknown", "0pt", 0.0


def repair_card(svg: str, title: str, rank: str, message: str, points: str, progress: float):
    # Card boundaries are separated by the next top-level 110x110 SVG panel.
    pattern = re.compile(
        rf'(<svg\s+x="\d+"\s+y="0"\s+width="110".*?'
        rf'<text[^>]*>{re.escape(title)}</text>.*?)(?=\n        <svg\s+x="\d+"\s+y="0"\s+width="110")',
        re.DOTALL,
    )
    match = pattern.search(svg)
    if not match:
        raise RuntimeError(f"Could not find trophy card: {title}")

    block = match.group(1)

    # Rank letter inside the trophy icon.
    block, n = re.subn(
        r'(<text x="6" y="8" font-family="Courier, Monospace" font-size="7" fill="#0d1117">)\?</text>',
        rf'\g<1>{rank}</text>',
        block,
        count=1,
    )
    if n != 1:
        raise RuntimeError(f"Could not replace rank icon for {title}")

    # Rank message and score.
    block = re.sub(
        r'(<text x="50%" y="85"[^>]*>)Unknown</text>',
        rf'\g<1>{message}</text>',
        block,
        count=1,
    )
    block = re.sub(
        r'(<text x="50%" y="97"[^>]*>)0pt</text>',
        rf'\g<1>{points}</text>',
        block,
        count=1,
    )

    # Progress bar width. The renderer uses 80px as the full track width.
    block = re.sub(
        r'(width: )0\.00px(;)',
        rf'\g<1>{80.0 * progress:.2f}px\g<2>',
        block,
        count=1,
    )

    return svg[:match.start()] + block + svg[match.end():]


def main():
    if not SVG_PATH.exists():
        raise SystemExit(f"Missing {SVG_PATH}")

    repos = get_public_repos()
    repo_count = len(repos)
    star_count = sum(int(repo.get("stargazers_count", 0)) for repo in repos)

    stars = rank_info(star_count, "Stars")
    repositories = rank_info(repo_count, "Repositories")

    svg = SVG_PATH.read_text(encoding="utf-8")
    svg = repair_card(svg, "Stars", *stars)
    svg = repair_card(svg, "Repositories", *repositories)

    # Keep the zero-progress cards at their actual boundary instead of
    # inheriting a bar width from a neighbouring SVG fragment.
    svg = repair_card(svg, "PullRequest", "C", "First Pull", "1pt", 0.0)
    svg = repair_card(svg, "Followers", "C", "First Friend", "1pt", 0.0)
    SVG_PATH.write_text(svg, encoding="utf-8")

    print(
        f"Repaired trophies: Stars={star_count} ({stars[0]}), "
        f"Repositories={repo_count} ({repositories[0]})"
    )


if __name__ == "__main__":
    main()
