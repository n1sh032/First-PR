import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from first_pr.github import get_response_threshold, get_open_issues, is_stale

owner = sys.argv[1]
name = sys.argv[2]

threshold, fallback = get_response_threshold(owner, name)
tag = "FALLBACK, not enough data" if fallback else "real median"
print(f"threshold: {threshold:.1f} days ({tag})")

issues = get_open_issues(owner, name)
for i in issues:
    print(f"#{i['number']} updated={i['updated_at']} stale={is_stale(i, threshold)}")