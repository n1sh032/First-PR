from flask import Flask, render_template, request
from first_pr.github import check_token, get_repo

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        repo_url = request.form.get("repo_url", "")
        # quick and dirty parsing, doesnt handle .git suffix or trailing slash yet
        parts = repo_url.strip().split("/")

        if len(parts) >= 2:
            owner = parts[-2]
            name = parts[-1]

            if not check_token():
                error = "server's github token is dead, oops"
            else:
                repo = get_repo(owner, name)
                if repo is None:
                    error = "couldnt find that repo (or its private)"
                else:
                    result = repo
        else:
            error = "that doesnt look like a repo url"

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)