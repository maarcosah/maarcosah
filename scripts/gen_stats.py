#!/usr/bin/env python3
"""Query the GitHub GraphQL API (as the account owner) for real contribution
stats -- including private commits, which the public stats-card services
can't see -- and render them as a small terminal-style SVG card.

Requires a PAT with repo + read:user scope in the STATS_PAT env var
(a token belonging to the account being queried; GITHUB_TOKEN cannot see
that account's private contributions).
"""
import json
import os
import sys
import urllib.request

USERNAME = "maarcosah"
API = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
      contributionCalendar {
        weeks { contributionDays { contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { stargazerCount }
    }
  }
}
"""


def graphql(token, variables):
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def streaks(counts):
    """(current, longest) runs of days with contributions, oldest day first.

    Today still in progress with no contributions doesn't break the current
    streak, so it's skipped.
    """
    longest = run = 0
    for n in counts:
        run = run + 1 if n else 0
        longest = max(longest, run)
    days = counts[:-1] if counts and not counts[-1] else counts
    current = 0
    for n in reversed(days):
        if not n:
            break
        current += 1
    return current, longest


def fetch_stats(token):
    cursor = None
    stars = 0
    contrib = None
    repo_count = 0
    # ponytail: paginates all owned repos for an exact star total; contribution
    # totals themselves are single-shot (GitHub caps that block at one page)
    while True:
        data = graphql(token, {"login": USERNAME, "cursor": cursor})
        contrib = contrib or data["contributionsCollection"]
        repos = data["repositories"]
        stars += sum(n["stargazerCount"] for n in repos["nodes"])
        repo_count = repos["totalCount"]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]

    commits = contrib["totalCommitContributions"] + contrib["restrictedContributionsCount"]
    days = [d["contributionCount"]
            for w in contrib["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    current, longest = streaks(days)
    return {
        "current_streak": f"{current} days",
        "longest_streak": f"{longest} days",
        "stars": stars,
        "repos": repo_count,
        "commits": commits,
        "prs": contrib["totalPullRequestContributions"],
        "issues": contrib["totalIssueContributions"],
        "contributed_to": contrib["totalRepositoryContributions"],
    }


THEMES = {
    "dark": {"bg": "#0d1117", "border": "#30363d", "fg": "#c9d1d9", "dim": "#8b949e", "accent": "#F70000"},
    "light": {"bg": "#ffffff", "border": "#d0d7de", "fg": "#1f2328", "dim": "#57606a", "accent": "#B00000"},
}

ROWS = [
    ("Total Stars Earned", "stars"),
    ("Total Commits (last year, incl. private)", "commits"),
    ("Total PRs", "prs"),
    ("Total Issues", "issues"),
    ("Contributed to (last year)", "contributed_to"),
    ("Current Streak", "current_streak"),
    ("Longest Streak (last year)", "longest_streak"),
]


def build_svg(stats, theme):
    c = THEMES[theme]
    w, pad, row_h = 480, 24, 26
    h = pad * 2 + 34 + len(ROWS) * row_h
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" role="img" aria-label="GitHub stats">',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<text x="{pad}" y="{pad + 18}" font-size="16" font-weight="700" fill="{c["accent"]}">{USERNAME}\'s real GitHub stats</text>',
    ]
    y = pad + 34 + 16
    for label, key in ROWS:
        parts.append(f'<text x="{pad}" y="{y}" font-size="13" fill="{c["dim"]}">{label}:</text>')
        parts.append(f'<text x="{w - pad}" y="{y}" font-size="13" font-weight="700" fill="{c["fg"]}" text-anchor="end">{stats[key]}</text>')
        y += row_h
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    token = os.environ["STATS_PAT"]
    stats = fetch_stats(token)
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    for theme in THEMES:
        svg = build_svg(stats, theme)
        path = os.path.join(out_dir, f"stats-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", path)
