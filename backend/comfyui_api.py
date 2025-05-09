from flask import Blueprint, request, jsonify
import os
import asyncio
import json
from services.ComfyUI.service import ComfyUIService

comfyui_bp = Blueprint('comfyui_bp', __name__)

# Chemin de base où sont stockées les données des projets (images extraites, concepts IA, etc.)
# Doit correspondre à la configuration du serveur de fichiers statiques si Flask sert les images
# ou être accessible par le backend pour lire/écrire les fichiers.
BASE_PROJECT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'projects'))

@comfyui_bp.route('/api/comfyui/process_plans', methods=['POST'])
def handle_process_plans():
    """
    Endpoint principal pour le traitement des plans
    Supporte deux modes :
    - Manuel : via API REST standard
    - Automatique : via Puppeteer MCP
    """
    data = request.json
    
    # Vérification des paramètres requis
    if not all(k in data for k in ['project_id', 'episode_id', 'plan_data', 'mode']):
        return jsonify({'error': 'Paramètres manquants'}), 400
    
    try:
        # Initialisation du service ComfyUI
        comfyui = ComfyUIService()
        
        if data['mode'] == 'auto':
            # Mode automatique via Puppeteer
            result = asyncio.run(
                comfyui.generate_with_puppeteer(
                    image_path=data['plan_data']['image_path'],
                    style="ombre_chinoise"
                )
            )
        else:
            # Mode manuel standard
            result = comfyui.generate_image(
                image_path=data['plan_data']['image_path'],
                output_dir=os.path.join(BASE_PROJECT_DATA_PATH, data['project_id'], 'generated'),
                style="ombre_chinoise",
                prompt=data['plan_data'].get('description', '')
            )
            result = {'status': 'success', 'result': result}
        
        if result['status'] == 'success':
            return jsonify({
                'message': 'Plan traité avec succès',
                'result': result['result']
            }), 200
        else:
            return jsonify({'error': result['message']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
