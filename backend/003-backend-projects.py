"""
003-backend-projects.py
Backend local CRUD pour gestion projets/épisodes/scènes Madsea (stockage JSON, prêt à migrer cloud)
API REST minimaliste pour intégration front.
"""
from flask import Flask, request, jsonify
import os, json

app = Flask(__name__)
PROJECTS_FILE = os.path.join(os.path.dirname(__file__), '../projects.json')

def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return {"projects": []}
    with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_projects(data):
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify(load_projects())

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = load_projects()
    body = request.json
    new_proj = {
        "id": body.get('id'),
        "name": body.get('name'),
        "episodes": []
    }
    data["projects"].append(new_proj)
    save_projects(data)
    return jsonify(new_proj), 201

@app.route('/api/projects/<proj_id>/episodes', methods=['POST'])
def add_episode(proj_id):
    data = load_projects()
    proj = next((p for p in data["projects"] if p["id"] == proj_id), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    body = request.json
    new_ep = {
        "id": body.get('id'),
        "number": body.get('number'),
        "name": body.get('name'),
        "scenes": []
    }
    proj["episodes"].append(new_ep)
    save_projects(data)
    return jsonify(new_ep), 201

@app.route('/api/projects/<proj_id>', methods=['GET'])
def get_project(proj_id):
    data = load_projects()
    proj = next((p for p in data["projects"] if p["id"] == proj_id), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(proj)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
