import sys, os, requests
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from first_pr.github import TOKEN

owner = sys.argv[1]
name = sys.argv[2]
num = sys.argv[3]

url = f"https://api.github.com/repos/{owner}/{name}/issues/{num}/timeline"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.mockingbird-preview+json"
}
r = requests.get(url, headers=headers)
print("status:", r.status_code)

events = r.json()
print(f"{len(events)} total events")
for e in events:
    print("-", e.get("event"))