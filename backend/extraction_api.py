# backend/005-backend-extraction.py

import os
import fitz  # PyMuPDF
import json
import hashlib
import io
from datetime import datetime
from pathlib import Path
from PIL import Image
import pytesseract
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import time
import shutil
import tempfile
import logging

# Configuration du chemin vers l'exécutable Tesseract (à ajuster selon l'installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
UPLOAD_FOLDER = 'uploads' # Sous-dossier dans chaque projet
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}
PROJECTS_BASE_PATH = 'projects' # Dossier racine pour tous les projets
NOMENCLATURE_TEST_OUTPUT_BASE = Path("i:/Madsea/outputs/nomenclature_test")

extraction_bp = Blueprint('extraction_bp', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@extraction_bp.route('/api/v1/upload_storyboard_v3', methods=['POST'])
def upload_storyboard_v3():
    """Endpoint pour uploader un storyboard PDF (v3), extrait images et textes.
    Utilise _process_pdf_advanced et sauvegarde les sorties dans NOMENCLATURE_TEST_OUTPUT_BASE.
    Crée des placeholders AI-concept.
    """
    current_app.logger.info(f"Entrée dans /api/v1/upload_storyboard_v3")
    if 'storyboard_file' not in request.files:
        current_app.logger.error("Aucun fichier 'storyboard_file' dans la requête v3")
        return jsonify({'error': 'Aucun fichier storyboard_file trouvé'}), 400

    file = request.files['storyboard_file']
    if file.filename == '':
        current_app.logger.error("Nom de fichier vide dans la requête v3")
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if not allowed_file(file.filename):
        current_app.logger.error(f"Type de fichier non autorisé: {file.filename}")
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

    # Récupération de project_id et episode_id depuis le formulaire
    project_id = request.form.get('project_id')
    episode_id = request.form.get('episode_id')

    if not project_id or not episode_id:
        current_app.logger.error("project_id ou episode_id manquant dans la requête v3")
        return jsonify({'error': 'project_id et episode_id sont requis'}), 400

    project_name = request.form.get('project_name', project_id) # Fallback si non fourni
    episode_name = request.form.get('episode_name', episode_id) # Fallback si non fourni

    current_app.logger.info(f"Requête v3 reçue: projet '{project_name}' (ID: {project_id}), épisode '{episode_name}' (ID: {episode_id}), fichier '{file.filename}'")

    # Pour le test de nomenclature, nous ne sauvegardons pas dans le dossier projet/upload
    # On utilise un dossier temporaire pour le PDF uploadé.
    filename = secure_filename(file.filename)
    temp_dir_obj = tempfile.TemporaryDirectory() # Creates a temporary directory
    temp_dir_path = Path(temp_dir_obj.name)
    pdf_temp_path = temp_dir_path / filename
    
    # project_episode_path n'est pas utilisé pour la sortie dans ce mode de test, mais la fonction _process_pdf_advanced l'attend.
    # On peut passer un Path vide ou le temp_dir_path pour satisfaire l'argument.
    dummy_project_episode_path = temp_dir_path # Ou Path() si la fonction le gère bien.

    try:
        file.save(pdf_temp_path)
        current_app.logger.info(f"Fichier PDF '{filename}' sauvegardé temporairement pour traitement: {pdf_temp_path}")

        # Appel de la fonction de traitement avancé
        extracted_data = _process_pdf_advanced(pdf_temp_path, project_id, episode_id, dummy_project_episode_path, filename)

    except Exception as e_main_proc:
        current_app.logger.exception(f"Erreur majeure durant la sauvegarde temporaire ou le traitement avancé du PDF '{filename}': {e_main_proc}")
        return jsonify({'error': f'Erreur serveur: {e_main_proc}'}), 500
    finally:
        # Nettoyage du dossier temporaire et de son contenu
        try:
            temp_dir_obj.cleanup()
            current_app.logger.info(f"Dossier temporaire {temp_dir_path} et son contenu (incluant {pdf_temp_path}) supprimés.")
        except Exception as e_clean:
            current_app.logger.error(f"Erreur lors du nettoyage du dossier temporaire {temp_dir_path}: {e_clean}")

    if extracted_data is None:
        current_app.logger.error(f"Échec du traitement avancé du PDF pour {filename}. extracted_data est None.")
        return jsonify({'error': 'Échec du traitement avancé du PDF (extracted_data is None). Vérifiez les logs serveur.'}), 500
    
    current_app.logger.info(f"Traitement avancé terminé pour {filename}. Nombre d'images extraites (raw): {len(extracted_data.get('images', []))}")

    # Création des placeholders AI-concept
    ai_concept_images_info_list = [] # Initialiser ici pour toujours l'avoir
    if "images" in extracted_data and extracted_data["images"]:
        raw_images_info_list = extracted_data["images"]
        
        ai_concept_task_str = "AI-concept"
        ai_concept_output_dir = NOMENCLATURE_TEST_OUTPUT_BASE / episode_id / ai_concept_task_str
        try:
            os.makedirs(ai_concept_output_dir, exist_ok=True)
            current_app.logger.info(f"Dossier de sortie pour AI-concept créé/vérifié: {ai_concept_output_dir}")
        except OSError as e:
            current_app.logger.error(f"Erreur de création de dossier {ai_concept_output_dir}: {e}")
            # Continuer sans créer les placeholders AI-concept si le dossier échoue, mais logguer

        if ai_concept_output_dir.exists(): # S'assurer que le dossier a été créé ou existe
            # Génération de placeholders blancs avec la nomenclature cible
            shot_counter = 0
            for raw_image_detail in raw_images_info_list:
                shot_counter += 1
                plan_num = shot_counter * 10
                plan_num_str = str(plan_num).zfill(4)
                ai_concept_filename = f"{episode_id}_SQ0010-{plan_num_str}_AI-concept_v0001.png"
                ai_concept_image_path_final = ai_concept_output_dir / ai_concept_filename

                # Création de l'image blanche placeholder
                img = Image.new("RGB", (100, 100), "white")
                img.save(ai_concept_image_path_final)

                ai_concept_images_info_list.append({
                    "path": str(ai_concept_image_path_final),
                    "page": raw_image_detail.get("page"),
                    "image_index_on_page": raw_image_detail.get("image_index_on_page")
                })
                current_app.logger.info(f"Placeholder AI-concept créé: {ai_concept_image_path_final}")
        else:
             current_app.logger.warning(f"Le dossier AI-concept {ai_concept_output_dir} n'a pas pu être créé ou n'existe pas. Placeholders AI-concept non générés.")

        extracted_data["ai_concept_images"] = ai_concept_images_info_list
        current_app.logger.info(f"{len(ai_concept_images_info_list)} placeholders AI-concept créés pour épisode {episode_id}.")
    else:
        current_app.logger.info(f"Aucune image brute ('images') extraite pour épisode {episode_id}, donc aucun placeholder AI-concept créé.")
        extracted_data["ai_concept_images"] = [] # Assurer que la clé existe même si aucune image

    # Ajouter des informations sur les chemins de sortie pour le client, même si vide
    extracted_data["nomenclature_test_output_paths"] = {
        "extracted_raw_base": str(NOMENCLATURE_TEST_OUTPUT_BASE / episode_id / "extracted-raw"),
        "ai_concept_base": str(NOMENCLATURE_TEST_OUTPUT_BASE / episode_id / "AI-concept")
    }

    current_app.logger.info(f"Réponse JSON pour /api/v1/upload_storyboard_v3: {extracted_data}")
    return jsonify(extracted_data), 200

# ... Rest of the file remains the same ...
