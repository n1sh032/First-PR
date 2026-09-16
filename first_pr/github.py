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