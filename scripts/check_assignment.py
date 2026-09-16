import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from first_pr.github import get_open_issues, should_reject_for_assignment

owner = sys.argv[1]
name = sys.argv[2]

issues = get_open_issues(owner, name)
for i in issues:
    reject = should_reject_for_assignment(i)
    who = i["assignee"]["login"] if i["assignee"] else "nobody"
    print(f"#{i['number']} assignee={who} updated={i['updated_at']} reject={reject}")