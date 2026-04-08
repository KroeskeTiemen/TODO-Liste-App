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

app.run(debug=True)