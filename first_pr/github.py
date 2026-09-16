import requests
import os

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
        if p["state"] == "open": # draft prs are still "open" state on github, this catches both
            return True
    return False