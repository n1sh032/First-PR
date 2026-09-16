import sys
import os

# so python can find the first_pr package from inside scripts/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from first_pr.github import check_token, get_repo, TOKEN

if not TOKEN:
    print("set GITHUB_TOKEN first")
    sys.exit(1)

if not check_token():
    sys.exit(1)

owner = sys.argv[1]
name = sys.argv[2]

repo = get_repo(owner, name)
if repo:
    print("archived:", repo["archived"])
    print("fork:", repo["fork"])
    print("has_issues:", repo["has_issues"])