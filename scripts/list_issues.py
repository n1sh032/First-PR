import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from first_pr.github import get_open_issues

owner = sys.argv[1]
name = sys.argv[2]

issues = get_open_issues(owner, name)
print(f"found {len(issues)} open issues")
for i in issues[:5]:
    print(f"#{i['number']}: {i['title']} (assignee: {i['assignee']})")