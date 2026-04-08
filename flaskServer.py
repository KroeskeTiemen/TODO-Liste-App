from flask import Flask, jsonify
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

app.run(debug=True)