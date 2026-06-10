# Raspberry Pi Webapp Setup

---

## 1. Statische IP setzen

```bash
sudo nmcli connection modify "netplan-eth0" \
  ipv4.addresses 192.168.24.103/24 \
  ipv4.method manual \
  ipv4.gateway 192.168.24.254 \
  ipv4.dns 192.168.24.254
```

Danach Pi neu starten (aus und an).

---

## 2. Users erstellen

**Willi:**
```bash
sudo useradd -m willi
sudo passwd willi
```

**Fernzugriff:**
```bash
sudo adduser fernzugriff
sudo usermod -aG sudo fernzugriff
```

---

## 3. SSH aktivieren

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

Config editieren:
```bash
sudo nano /etc/ssh/sshd_config
```

Folgendes hinzufügen:
```
PermitRootLogin no
PasswordAuthentication yes
AllowUsers fernzugriff
```

SSH neustarten:
```bash
sudo systemctl restart ssh
```

---

## 4. Datum setzen (muss öfters gemacht werden)

```bash
sudo date -s "2026-05-27 12:10:00"
```

---

## 5. System updaten + Docker installieren

```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker.service
sudo docker run hello-world
sudo apt install docker-compose-plugin
```

---

## 6. Webapp-Ordner erstellen

```bash
mkdir webapp
cd webapp
mkdir templates
```

---

## 7. Dateien erstellen

### flaskServer.py
```bash
nano flaskServer.py
```
```python
from flask import Flask, jsonify, request
import uuid

todo_lists = {}
todo_entries = {}

app = Flask(__name__)

def create_uuid():
    return str(uuid.uuid4())

def error(message, code):
    return jsonify({"message": message}), code

@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route("/todo-list", methods=["POST"])
def create_list():
    data = request.get_json()
    if not data or "name" not in data:
        return error("Invalid input", 406)
    list_id = create_uuid()
    todo_lists[list_id] = {"id": list_id, "name": data["name"]}
    return jsonify(todo_lists[list_id]), 201

@app.route("/todo-list/<list_id>", methods=["GET"])
def get_entries(list_id):
    if list_id not in todo_lists:
        return error("List not found", 404)
    entries = [e for e in todo_entries.values() if e["list_id"] == list_id]
    return jsonify(entries), 200

@app.route("/todo-list", methods=["GET"])
def get_all_lists():
    return jsonify(list(todo_lists.values())), 200

@app.route("/todo-list/<list_id>/entry", methods=["POST"])
def add_entry(list_id):
    if list_id not in todo_lists:
        return error("List not found", 404)
    data = request.get_json()
    if "name" not in data or "description" not in data:
        return error("Invalid input", 406)
    entry_id = create_uuid()
    entry = {"id": entry_id, "name": data["name"], "description": data["description"], "list_id": list_id}
    todo_entries[entry_id] = entry
    return jsonify(entry), 201

@app.route("/entry/<entry_id>", methods=["PATCH"])
def update_entry(entry_id):
    if entry_id not in todo_entries:
        return error("Entry not found", 404)
    data = request.get_json()
    entry = todo_entries[entry_id]
    if "name" in data:
        entry["name"] = data["name"]
    if "description" in data:
        entry["description"] = data["description"]
    return jsonify(entry), 200

@app.route("/entry/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    if entry_id not in todo_entries:
        return error("Entry not found", 404)
    del todo_entries[entry_id]
    return jsonify({"message": "Entry deleted"}), 204

@app.route("/todo-list/<list_id>", methods=["DELETE"])
def delete_list(list_id):
    if list_id not in todo_lists:
        return error("List not found", 404)
    del todo_lists[list_id]
    return jsonify({"message": "Entry deleted"}), 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

---

### client.py
```bash
nano client.py
```
```python
from flask import Flask, render_template, request, redirect
import requests
import os

app = Flask(__name__)

API_BASE = os.environ.get("API_BASE", "http://192.168.24.103:5000")

@app.route("/")
def index():
    lists = requests.get(f"{API_BASE}/todo-list").json()
    for lst in lists:
        lst["entries"] = requests.get(f"{API_BASE}/todo-list/{lst['id']}").json()
    return render_template("index.html", lists=lists)

@app.route("/create-list", methods=["POST"])
def create_list():
    requests.post(f"{API_BASE}/todo-list", json={"name": request.form["name"]})
    return redirect("/")

@app.route("/add-entry/<list_id>", methods=["POST"])
def add_entry(list_id):
    requests.post(f"{API_BASE}/todo-list/{list_id}/entry", json={
        "name": request.form["name"],
        "description": request.form["description"]
    })
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
    app.run(host="0.0.0.0", port=5001)
```

---

### templates/index.html
```bash
nano templates/index.html
```
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Todo Lists</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .list { border: 1px solid #ccc; padding: 15px; margin-bottom: 25px; }
        ul { padding-left: 20px; }
        li { margin-bottom: 6px; }
        input { margin-right: 5px; }
        button { margin-left: 5px; }
    </style>
</head>
<body>
<h1>Todo Lists</h1>
<h2>Create new list</h2>
<form method="post" action="/create-list">
    <input type="text" name="name" placeholder="List name" required>
    <button type="submit">Create</button>
</form>
<hr>
{% for list in lists %}
<div class="list">
    <h2>{{ list.name }} <a href="/delete-list/{{ list.id }}">[delete list]</a></h2>
    <form method="post" action="/add-entry/{{ list.id }}">
        <input type="text" name="name" placeholder="Entry name" required>
        <input type="text" name="description" placeholder="Description" required>
        <button type="submit">Add entry</button>
    </form>
    <ul>
        {% for entry in list.entries %}
            <li><strong>{{ entry.name }}</strong> – {{ entry.description }} <a href="/delete-entry/{{ entry.id }}">[x]</a></li>
        {% else %}
            <li><em>No entries yet</em></li>
        {% endfor %}
    </ul>
</div>
{% endfor %}
</body>
</html>
```

---

### Dockerfile
```bash
nano Dockerfile
```
```dockerfile
FROM python:3.11-slim
RUN pip install flask
WORKDIR /app
COPY flaskServer.py /app/
COPY templates/ /app/templates/
EXPOSE 5000
CMD ["python", "flaskServer.py"]
```

---

### Dockerfile.client
```bash
nano Dockerfile.client
```
```dockerfile
FROM python:3.11-slim
RUN pip install flask requests
WORKDIR /app
COPY client.py /app/
COPY templates/ /app/templates/
EXPOSE 5001
CMD ["python", "client.py"]
```

---

### docker-compose.yml
```bash
nano docker-compose.yml
```
```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"

  client:
    build:
      context: .
      dockerfile: Dockerfile.client
    ports:
      - "5001:5001"
    environment:
      - API_BASE=http://api:5000
    depends_on:
      - api
```

---

## 8. Container starten

```bash
sudo docker compose up
```

Danach erreichbar:
- **Client (HTML):** http://192.168.24.103:5001
- **API:** http://192.168.24.103:5000

