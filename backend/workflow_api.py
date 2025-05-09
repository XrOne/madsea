from flask import Blueprint, request, jsonify
import os
import werkzeug

workflow_bp = Blueprint('workflow_bp', __name__)

WORKFLOW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ComfyUI', 'workflows'))

@workflow_bp.route('/api/workflow/upload', methods=['POST'])
def upload_workflow():
    """
    Upload d'un fichier JSON de workflow ComfyUI
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Format non supporté (JSON attendu)'}), 400
    filename = werkzeug.utils.secure_filename(file.filename)
    save_path = os.path.join(WORKFLOW_DIR, filename)
    file.save(save_path)
    return jsonify({'message': f'Workflow {filename} uploadé avec succès', 'path': save_path}), 200
