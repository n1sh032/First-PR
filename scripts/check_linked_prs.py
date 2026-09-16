import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from first_pr.github import get_linked_prs

owner = sys.argv[1]
name = sys.argv[2]
num = sys.argv[3]

prs = get_linked_prs(owner, name, num)

if len(prs) == 0:
    print("nothing linked")
else:
    for p in prs:
        print("PR #" + str(p["number"]), "state:", p["state"], "draft:", p["draft"])