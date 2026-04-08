from flask import Flask, jsonify, request
import uuid

todo_lists = {}
todo_entries = {}

app = Flask(__name__)

# UUID generator Fuer IDs
def create_uuid():
    return str(uuid.uuid4())

# Fehlerantwort
def error(message, code):
    return jsonify({"message": message}), code

#Add List Method
@app.route("/todo-list", methods=["POST"])
def create_list():
    data = request.get_json()
    if not data or "name" not in data:
        return error("Invalid input", 406)

    list_id = create_uuid()
    todo_lists[list_id] = {
        "id": list_id,
        "name": data["name"]
    }
    return jsonify(todo_lists[list_id]), 201


@app.route("/todo-list/<list_id>", methods=["GET"])
def get_entries(list_id):
    if list_id not in todo_lists:
        return error("List not found", 404)

    entries = [entry for entry in todo_entries.values()
                if entry["list_id"] == list_id]
    
    return jsonify(entries), 200

@app.route("/todo-list/<list_id>/entry", methods=["POST"])
def add_entry(list_id):
    if list_id not in todo_lists:
        return error("List not found", 404)

    data = request.get_json()
    if "name" not in data or "description" not in data:
        return error("Invalid input", 406)

    entry_id = create_uuid()
    entry = {
        "id": entry_id,
        "name": data["name"],
        "description": data["description"],
        "list_id": list_id
    }
    todo_entries[entry_id] = entry
    return jsonify(entry), 201

app.run(debug=True)