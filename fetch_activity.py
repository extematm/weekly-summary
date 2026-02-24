import requests
from datetime import datetime, timedelta, timezone
import os

github_repo = os.environ['GITHUB_REPOSITORY']

now = datetime.now(timezone.utc)
current_monday = (now - timedelta(days=now.weekday())).replace(
    hour=0, minute=0, second=0, microsecond=0
)
start = current_monday - timedelta(days=7)
end = current_monday

headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}

def get_paginated(url, params):
    results = []
    while url:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        params = {}
        if response.status_code != 200:
            raise Exception(f"GitHub API error ({url}): {response.status_code} - {response.text}")
        data = response.json()
        if isinstance(data, list):
            results.extend(data)
        else:
            results.append(data)
        link = response.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                next_url = part[part.find("<")+1:part.find(">")]
                break
        url = next_url
    return results

time_params = {
    "since": start.isoformat().replace("+00:00", "Z"),
    "until": end.isoformat().replace("+00:00", "Z"),
    "per_page": 100
}

commits = get_paginated(f"https://api.github.com/repos/{github_repo}/commits", time_params.copy())
pulls = get_paginated(
    f"https://api.github.com/repos/{github_repo}/pulls",
    {"state": "all", "sort": "updated", "direction": "desc", "per_page": 100}
)
issues = get_paginated(
    f"https://api.github.com/repos/{github_repo}/issues",
    {"state": "all", "sort": "updated", "direction": "desc", "per_page": 100}
)

def in_window(iso_ts):
    ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    return start <= ts < end

commit_lines = [
    f"- {c['commit']['author']['date']}: {c['commit']['message'].splitlines()[0]}"
    for c in commits
]

pull_lines = []
for pr in pulls:
    updated = pr.get("updated_at")
    if updated and in_window(updated):
        pull_lines.append(
            f"- PR #{pr['number']} [{pr['state']}] updated {updated}: {pr['title']}"
        )

issue_lines = []
for issue in issues:
    if "pull_request" in issue:
        continue
    updated = issue.get("updated_at")
    if updated and in_window(updated):
        issue_lines.append(
            f"- Issue #{issue['number']} [{issue['state']}] updated {updated}: {issue['title']}"
        )

with open("activity.txt", "w", encoding="utf-8") as f:
    f.write(
        "Week window (UTC): "
        f"{start.isoformat()} to {end.isoformat()}\n\n"
        f"Commits ({len(commit_lines)}):\n"
        + ("\n".join(commit_lines) if commit_lines else "- None")
        + f"\n\nPull Requests ({len(pull_lines)}):\n"
        + ("\n".join(pull_lines) if pull_lines else "- None")
        + f"\n\nIssues ({len(issue_lines)}):\n"
        + ("\n".join(issue_lines) if issue_lines else "- None")
    )
