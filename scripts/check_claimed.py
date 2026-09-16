import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from first_pr.github import has_open_linked_pr, get_open_issues

owner = sys.argv[1]
name = sys.argv[2]

issues = get_open_issues(owner, name)
print(f"checking {len(issues)} issues...")

for i in issues:
    claimed = has_open_linked_pr(owner, name, i["number"])
    tag = "CLAIMED" if claimed else "open"
    print(f"#{i['number']} [{tag}]: {i['title'][:60]}")