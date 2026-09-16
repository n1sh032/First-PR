import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from first_pr.github import get_closed_issues, TOKEN
from datetime import datetime, timezone
import requests

closed = get_closed_issues("facebook", "react")

for i in closed:
    num = i["number"]
    author = i["user"]["login"]
    url = f"https://api.github.com/repos/facebook/react/issues/{num}/comments"
    r = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"}, params={"per_page": 1})
    comments = r.json()
    if not comments:
        continue

    commenter = comments[0]["user"]["login"]
    same_person = commenter == author
    print(num, "- issue author:", author, "| first commenter:", commenter, "| same person:", same_person)