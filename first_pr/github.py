import requests
import os
import re
from datetime import datetime, timezone


TOKEN = os.environ.get("GITHUB_TOKEN")

def check_token():
    r = requests.get("https://api.github.com/user", headers={
        "Authorization": f"Bearer {TOKEN}"
    })
    if r.status_code == 401:
        print("token is bad or expired")
        return False
    return True


def get_repo(owner, name):
    url = f"https://api.github.com/repos/{owner}/{name}"
    r = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    if r.status_code == 404:
        # could be doesnt exist OR private and we cant see it, github hides which
        print("repo not found (or private and we cant see it)")
        return None

    if r.status_code != 200:
        print("something went wrong:", r.status_code, r.text)
        return None

    return r.json()
def get_open_issues(owner, name):
    url = f"https://api.github.com/repos/{owner}/{name}/issues"
    params = {"state": "open", "per_page": 30}
    r = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"}, params=params)

    if r.status_code != 200:
        print("couldnt get issues:", r.status_code, r.text)
        return []

    issues = r.json()
    # github lumps PRs into the issues endpoint too, gotta filter them out
    return [i for i in issues if "pull_request" not in i]

def get_linked_prs(owner, name, issue_number):
    # the timeline endpoint picks up stuff a normal "linked issues" check misses
    # like when a PR just mentions the issue number somewhere instead of saying "fixes #x"
    url = f"https://api.github.com/repos/{owner}/{name}/issues/{issue_number}/timeline"
    headers = {
      "Authorization": f"Bearer {TOKEN}",
      "Accept": "application/vnd.github.mockingbird-preview+json" # need this weird header or it 404s
    }
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("timeline fetch failed", r.status_code)
        return []

    events = r.json()

    linked = []
    for e in events:
        if e.get("event") != "cross-referenced":
            continue
        src = e.get("source", {}).get("issue", {})
        if "pull_request" not in src:
            continue
        # not sure if draft is always there, being safe
        linked.append({"number": src["number"], "state": src["state"], "draft": src.get("draft", False)})

    return linked
def has_open_linked_pr(owner, name, issue_number):
    prs = get_linked_prs(owner, name, issue_number)
    for p in prs:
        if p["state"] == "open": # covers drafts too
            return True

    # nothing in the official timeline, try the messier regex approach before giving up
    informal = find_informal_links(owner, name, issue_number)
    if len(informal) > 0:
        return True

    return False
def get_open_prs(owner, name):
    url = f"https://api.github.com/repos/{owner}/{name}/pulls"
    params = {"state": "open", "per_page": 50}
    r = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"}, params=params)
    if r.status_code != 200:
        print("pr fetch failed", r.status_code)
        return []
    return r.json()


def find_informal_links(owner, name, issue_number):
    # timeline api misses stuff like "- #123" with no keyword, see KNOWN_LIMITATIONS.md
    # this just brute force greps open pr titles/bodies for the number instead
    prs = get_open_prs(owner, name)
    pattern = re.compile(r"#" + str(issue_number) + r"\b")
    hits = []
    for p in prs:
        blob = (p.get("title") or "") + " " + (p.get("body") or "")
        if pattern.search(blob):
            hits.append({"number": p["number"], "state": p["state"], "draft": p.get("draft", False)})
    return hits
ABANDONED_DAYS = 30 # if assigned but nothing moved in this long, treat as fair game again

def is_abandoned_assignment(issue):
    if issue.get("assignee") is None:
        return False # not assigned at all, this check doesnt even apply

    updated = issue["updated_at"] # format like 2024-05-01T12:00:00Z
    updated_dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    days_since = (datetime.now(timezone.utc) - updated_dt).days

    return days_since > ABANDONED_DAYS


def should_reject_for_assignment(issue):
    if issue.get("assignee") is None:
        return False
    # assigned AND recently touched = someone's probably actively on it, reject
    # assigned but stale = effectively abandoned, dont reject just for having a name on it
    return not is_abandoned_assignment(issue)