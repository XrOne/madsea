from flask import Blueprint, request, jsonify
import os
from flask import Blueprint, request, jsonify
from comfyui_bridge import process_plan_with_comfyui

comfyui_bp = Blueprint('comfyui_bp', __name__)

# Chemin de base où sont stockées les données des projets (images extraites, concepts IA, etc.)
# Doit correspondre à la configuration du serveur de fichiers statiques si Flask sert les images
# ou être accessible par le backend pour lire/écrire les fichiers.
BASE_PROJECT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'projects'))

@comfyui_bp.route('/api/comfyui/process_plans', methods=['POST'])
def handle_process_plans():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    plans_to_process = data.get('plans')
    project_id = data.get('project_id')
    episode_id = data.get('episode_id')

    if not plans_to_process or not project_id or not episode_id:
        return jsonify({"error": "Données manquantes: plans, project_id ou episode_id"}), 400

    processed_plans_results = []
    all_successful = True

    for plan_data in plans_to_process:
        try:
            # S'assurer que plan_data contient toutes les infos nécessaires, notamment:
            # id, filename (nom du fichier brut extrait), path (chemin relatif du fichier brut extrait),
            # ai_concept_placeholder_path (chemin relatif du placeholder), 
            # ai_concept_filename (nom du fichier placeholder),
            # sequence_number (le SQxxxx, potentiellement modifié par l'utilisateur)
            
            # On passe également project_id et episode_id à la fonction de traitement
            # pour qu'elle puisse construire les chemins absolus correctement.
            result = process_plan_with_comfyui(plan_data, project_id, episode_id, BASE_PROJECT_DATA_PATH)
            processed_plans_results.append(result)
            if 'error' in result:
                all_successful = False
        except Exception as e:
            print(f"Erreur interne lors du traitement du plan {plan_data.get('id')}: {e}")
            processed_plans_results.append({
                "id": plan_data.get('id'),
                "error": str(e),
                "status": "failed"
            })
            all_successful = False

    if all_successful:
        return jsonify({"message": "Tous les plans ont été traités avec succès", "results": processed_plans_results}), 200
    else:
        return jsonify({"message": "Certains plans n'ont pas pu être traités", "results": processed_plans_results}), 500
