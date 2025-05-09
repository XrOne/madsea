"""
003-backend-projects.py
Backend local CRUD pour gestion projets/épisodes/scènes Madsea (stockage JSON, prêt à migrer cloud)
API REST minimaliste pour intégration front.
"""
from flask import Blueprint, request, jsonify
import os, json

project_bp = Blueprint('project_bp', __name__)

PROJECTS_FILE = os.path.join(os.path.dirname(__file__), '../projects.json')

def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return {"projects": []}
    with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_projects(data):
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@project_bp.route('/projects', methods=['GET'])
def get_projects():
    return jsonify(load_projects())

@project_bp.route('/projects', methods=['POST'])
def create_project():
    data = load_projects()
    body = request.json
    # Création du projet avec métadonnées complètes pour la nomenclature
    new_proj = {
        "id": body.get('id'),
        "name": body.get('name'),
        "type": body.get('type'),
        "duration": body.get('duration'),
        "season": body.get('season'),
        "episode": body.get('episode'),
        "title": body.get('title'),
        "nomenclature": body.get('nomenclature'),
        "code": body.get('code'),
        "episodes": body.get('episodes', [])
    }
    data["projects"].append(new_proj)
    save_projects(data)
    return jsonify(new_proj), 201

@project_bp.route('/projects/<proj_id>/episodes', methods=['POST'])
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

@project_bp.route('/projects/<proj_id>', methods=['GET'])
def get_project(proj_id):
    data = load_projects()
    proj = next((p for p in data["projects"] if p["id"] == proj_id), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(proj)
