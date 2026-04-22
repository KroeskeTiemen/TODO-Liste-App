from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

API_BASE = "http://127.0.0.1:5000"


@app.route("/")
def index():
    lists = requests.get(f"{API_BASE}/todo-list").json()

    for lst in lists:
        res = requests.get(f"{API_BASE}/todo-list/{lst['id']}")
        lst["entries"] = res.json()

    return render_template("index.html", lists=lists)


@app.route("/create-list", methods=["POST"])
def create_list():
    name = request.form["name"]
    requests.post(f"{API_BASE}/todo-list", json={"name": name})
    return redirect("/")


@app.route("/add-entry/<list_id>", methods=["POST"])
def add_entry(list_id):
    requests.post(
        f"{API_BASE}/todo-list/{list_id}/entry",
        json={
            "name": request.form["name"],
            "description": request.form["description"]
        }
    )
    return redirect("/")


@app.route("/delete-entry/<entry_id>")
def delete_entry(entry_id):
    requests.delete(f"{API_BASE}/entry/{entry_id}")
    return redirect("/")


@app.route("/delete-list/<list_id>")
def delete_list(list_id):
    requests.delete(f"{API_BASE}/todo-list/{list_id}")
    return redirect("/")


if __name__ == "__main__":
    app.run(port=5001, debug=True)