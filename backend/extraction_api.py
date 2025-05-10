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
import zipfile
import re

# Configuration par défaut de Tesseract - sera configuré dynamiquement dans les fonctions
DEFAULT_TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
UPLOAD_FOLDER = 'uploads' # Sous-dossier dans chaque projet
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}
PROJECTS_BASE_PATH = 'projects' # Dossier racine pour tous les projets
NOMENCLATURE_TEST_OUTPUT_BASE = Path("i:/Madsea/outputs/nomenclature_test")

# Configuration du logger
logger = logging.getLogger(__name__)

# Définition du Blueprint pour l'extraction
extraction_bp = Blueprint('extraction', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _process_page_content_advanced(page, page_num, project_id, episode_id, sequence_number, output_path, doc, original_filename_base, image_index_offset):
    # Vérifier et configurer Tesseract au début de chaque traitement de page
    try:
        # Utiliser la configuration globale définie dans app.py
        # Si besoin, on peut aussi la redéfinir ici en cas d'erreur
        if not pytesseract.pytesseract.tesseract_cmd or not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            # Fallback sur le chemin standard si la config globale échoue
            logger.warning("Configuration Tesseract non trouvée, utilisation du chemin standard")
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Vérification optionnelle que Tesseract fonctionne
        # tesseract_version = pytesseract.get_tesseract_version()
        # logger.info(f"Tesseract version: {tesseract_version}")
    except Exception as e:
        logger.error(f"Erreur configuration Tesseract: {e}")
        
    page_data = {
        'page_number': page_num + 1,
        'images': [],
        'texts': [],
        'voice_off': '',
        'title_highlighted': '', # Placeholder
        'technical_breakdown': '' # Placeholder
    }
    image_counter = 0
    text_content = ""
    blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_WORDS | fitz.TEXTFLAGS_TEXT | fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE | fitz.TEXT_PRESERVE_IMAGES )["blocks"]

    voice_off_texts = []

    for block in blocks:
        if block['type'] == 0:  # Text block
            for line in block['lines']:
                line_text_parts = []
                for span in line['spans']:
                    span_text = span['text'].strip()
                    if span_text:
                        line_text_parts.append(span_text)
                        # Tentative d'extraction du texte en gras pour la voix off
                        # Les flags de police de PyMuPDF: 2^0=superscript, 2^1=italic, 2^2=serifed, 2^3=monospaced, 2^4=bold
                        if span['flags'] & (1 << 4): # Check for bold flag
                            voice_off_texts.append(span_text)
                full_line_text = " ".join(line_text_parts)
                if full_line_text:
                    page_data['texts'].append({
                        'text': full_line_text,
                        'bbox': [round(coord) for coord in line['bbox']]
                    })
                    text_content += full_line_text + "\n"

    if voice_off_texts:
        page_data['voice_off'] = "\n".join(voice_off_texts)

    # Extraction des images
    images = page.get_images(full=True)
    for img_index, img in enumerate(images):
        image_counter += 1
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        plan_index = image_index_offset + image_counter # Index global de l'image (1, 2, 3...)
        plan_number_actual = plan_index * 10 # Numéro de plan effectif (10, 20, 30...)
        plan_number_str = f"{plan_number_actual:04d}" # Formaté sur 4 chiffres (0010, 0020, 0030...)

        # Nomenclature pour l'image extraite brute
        # E{episode_id}_SQ{sequence_number}-{plan_number}_extracted-raw_v0001.{ext}
        raw_filename = f"E{episode_id}_SQ{sequence_number}-{plan_number_str}_extracted-raw_v0001.{image_ext}"
        raw_dir = os.path.join(NOMENCLATURE_TEST_OUTPUT_BASE, episode_id, sequence_number, "extracted-raw") # Ajustement pour inclure sequence_number
        os.makedirs(raw_dir, exist_ok=True)
        raw_image_path = os.path.join(raw_dir, raw_filename)

        with open(raw_image_path, "wb") as f_img:
            f_img.write(image_bytes)
        logger.info(f"Image brute extraite et sauvegardée: {raw_image_path}")

        # Création d'un placeholder pour l'image AI-concept
        # E{episode_id}_SQ{sequence_number}-{plan_number}_AI-concept_v0001.png
        ai_concept_filename = f"E{episode_id}_SQ{sequence_number}-{plan_number_str}_AI-concept_v0001.png"
        ai_concept_dir = os.path.join(NOMENCLATURE_TEST_OUTPUT_BASE, episode_id, sequence_number, "AI-concept") # Ajustement pour inclure sequence_number
        os.makedirs(ai_concept_dir, exist_ok=True)
        ai_concept_placeholder_path = os.path.join(ai_concept_dir, ai_concept_filename)

        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            width, height = pil_image.size
            placeholder_img = Image.new('RGB', (width, height), color = 'white')
            draw = ImageDraw.Draw(placeholder_img)
            # Optionnel: ajouter du texte au placeholder
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            draw.text((10, 10), "AI-Concept Placeholder", fill=(0,0,0), font=font)
            placeholder_img.save(ai_concept_placeholder_path, "PNG")
            logger.info(f"Placeholder AI-concept créé: {ai_concept_placeholder_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du placeholder pour {ai_concept_filename}: {e}")
            # Créer un placeholder vide en cas d'erreur de traitement de l'image originale
            placeholder_img = Image.new('RGB', (600, 400), color = 'lightgray') # Taille par défaut
            draw = ImageDraw.Draw(placeholder_img)
            draw.text((10,10), "Error Creating Placeholder", fill=(0,0,0))
            placeholder_img.save(ai_concept_placeholder_path, "PNG")

        page_data['images'].append({
            'path': raw_image_path.replace(NOMENCLATURE_TEST_OUTPUT_BASE, "/outputs/nomenclature_test").replace('\\', '/'), # Chemin relatif pour le client
            'ai_concept_placeholder_path': ai_concept_placeholder_path.replace(NOMENCLATURE_TEST_OUTPUT_BASE, "/outputs/nomenclature_test").replace('\\', '/'),
            'filename': raw_filename,
            'ai_concept_filename': ai_concept_filename,
            'page': page_num + 1,
            'index_on_page': image_counter,
            'plan_number': plan_number_str,
            'episode_id': episode_id,
            'sequence_number': sequence_number,
            'version': 'v0001',
            'task_raw': 'extracted-raw',
            'task_ai_concept': 'AI-concept',
            'extension_raw': image_ext,
            'extension_ai_concept': 'png'
        })

    # Si aucune image n'a été trouvée via get_images, essayez de capturer la page entière comme image
    # Cela est utile pour les PDF où chaque page est une seule grande image (scan, etc.)
    if not images and page.get_text("text").strip() == "": # Si pas d'images ET pas de texte, considérer la page comme une image
        logger.info(f"Aucune image extraite ni texte trouvé sur la page {page_num + 1}. Traitement de la page entière comme une image.")
        pix = page.get_pixmap()
        image_bytes = pix.tobytes("png") # Sauvegarder en PNG
        image_ext = "png"

        image_counter +=1 # Une seule "image" (la page entière)
        plan_index = image_index_offset + image_counter # Index global de l'image (1, 2, 3...)
        plan_number_actual = plan_index * 10 # Numéro de plan effectif (10, 20, 30...)
        plan_number_str = f"{plan_number_actual:04d}" # Formaté sur 4 chiffres (0010, 0020, 0030...)

        raw_filename = f"E{episode_id}_SQ{sequence_number}-{plan_number_str}_extracted-raw_v0001.{image_ext}"
        raw_dir = os.path.join(NOMENCLATURE_TEST_OUTPUT_BASE, episode_id, sequence_number, "extracted-raw")
        os.makedirs(raw_dir, exist_ok=True)
        raw_image_path = os.path.join(raw_dir, raw_filename)

        with open(raw_image_path, "wb") as f_img:
            f_img.write(image_bytes)
        logger.info(f"Image de page entière sauvegardée: {raw_image_path}")

        ai_concept_filename = f"E{episode_id}_SQ{sequence_number}-{plan_number_str}_AI-concept_v0001.png"
        ai_concept_dir = os.path.join(NOMENCLATURE_TEST_OUTPUT_BASE, episode_id, sequence_number, "AI-concept")
        os.makedirs(ai_concept_dir, exist_ok=True)
        ai_concept_placeholder_path = os.path.join(ai_concept_dir, ai_concept_filename)

        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            width, height = pil_image.size
            placeholder_img = Image.new('RGB', (width, height), color = 'white')
            draw = ImageDraw.Draw(placeholder_img)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            draw.text((10, 10), "AI-Concept Placeholder", fill=(0,0,0), font=font)
            placeholder_img.save(ai_concept_placeholder_path, "PNG")
            logger.info(f"Placeholder AI-concept pour page entière créé: {ai_concept_placeholder_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du placeholder page entière pour {ai_concept_filename}: {e}")
            placeholder_img = Image.new('RGB', (width, height), color = 'lightgray')
            draw = ImageDraw.Draw(placeholder_img)
            draw.text((10,10), "Error Creating Placeholder", fill=(0,0,0))
            placeholder_img.save(ai_concept_placeholder_path, "PNG")

        page_data['images'].append({
            'path': raw_image_path.replace(NOMENCLATURE_TEST_OUTPUT_BASE, "/outputs/nomenclature_test").replace('\\', '/'),
            'ai_concept_placeholder_path': ai_concept_placeholder_path.replace(NOMENCLATURE_TEST_OUTPUT_BASE, "/outputs/nomenclature_test").replace('\\', '/'),
            'filename': raw_filename,
            'ai_concept_filename': ai_concept_filename,
            'page': page_num + 1,
            'index_on_page': image_counter,
            'plan_number': plan_number_str,
            'episode_id': episode_id,
            'sequence_number': sequence_number,
            'version': 'v0001',
            'task_raw': 'extracted-raw',
            'task_ai_concept': 'AI-concept',
            'extension_raw': image_ext,
            'extension_ai_concept': 'png'
        })

    return page_data, text_content, (image_index_offset + image_counter) # Retourner le nouvel offset

def _process_pdf_advanced(pdf_temp_path, project_id, episode_id, sequence_number, output_path, original_filename):
    logger.info(f"Début du traitement avancé du PDF: {original_filename} pour projet {project_id}, épisode {episode_id}, séquence {sequence_number}")
    structured_data = {'project_id': project_id, 'episode_id': episode_id, 'sequence_number': sequence_number, 'original_filename': original_filename, 'pages': []}
    full_text_content = ""
    original_filename_base = os.path.splitext(original_filename)[0]
    images_processed_count_total = 0 # Compteur global pour le numéro de plan

    try:
        doc = fitz.open(pdf_temp_path)
        logger.info(f"PDF ouvert avec {doc.page_count} pages.")
        for page_num in range(doc.page_count):
            logger.info(f"Traitement de la page {page_num + 1}")
            page = doc.load_page(page_num)
            # L'offset pour le numéro de plan est le nombre total d'images déjà traitées des pages précédentes
            page_content, text_content, images_processed_count_total = _process_page_content_advanced(page, page_num, project_id, episode_id, sequence_number, output_path, doc, original_filename_base, images_processed_count_total)
            structured_data['pages'].append(page_content)
            full_text_content += f"--- Page {page_num + 1} ---\n{text_content}\n"
        doc.close()
    except Exception as e:
        logger.error(f"Erreur lors du traitement du PDF {original_filename}: {e}")
        return None, None

    # Sauvegarde du texte complet extrait (optionnel)
    # text_output_filename = os.path.join(output_path, f"{original_filename_base}_full_text.txt")
    # with open(text_output_filename, "w", encoding="utf-8") as f_text:
    #     f_text.write(full_text_content)
    # logger.info(f"Texte complet sauvegardé dans {text_output_filename}")

    # Sauvegarde des données structurées en JSON (optionnel)
    # json_output_filename = os.path.join(output_path, f"{original_filename_base}_structured_data.json")
    # with open(json_output_filename, "w", encoding="utf-8") as f_json:
    #     json.dump(structured_data, f_json, ensure_ascii=False, indent=4)
    # logger.info(f"Données structurées sauvegardées dans {json_output_filename}")

    logger.info(f"Traitement avancé du PDF {original_filename} terminé.")
    return structured_data, full_text_content

@extraction_bp.route('/api/upload_storyboard_v3', methods=['POST'])
def upload_storyboard_v3():
    # Vérification des dossiers critiques
    required_dirs = [
        current_app.config.get('TEMP_DIR', 'temp'),
        current_app.config.get('UPLOAD_FOLDER', 'uploads'),
        NOMENCLATURE_TEST_OUTPUT_BASE
    ]
    
    for dir_path in required_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            if not os.access(dir_path, os.W_OK):
                logger.error(f"Permissions manquantes pour : {dir_path}")
                return jsonify({"error": "Erreur de configuration serveur"}), 500
        except Exception as e:
            logger.error(f"Erreur création dossier {dir_path}: {str(e)}")
            return jsonify({"error": "Erreur de configuration serveur"}), 500

    # Vérification Tesseract
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        logger.error(f"Tesseract non disponible: {str(e)}")
        return jsonify({"error": "OCR non configuré"}), 500

    logger.info(f"Requête reçue sur /upload_storyboard (v3) - {request.method}")
    if 'file' not in request.files:
        logger.warning("Aucun fichier trouvé dans la requête")
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.warning("Nom de fichier vide")
        return jsonify({'error': 'Nom de fichier vide'}), 400

    project_id = request.form.get('project_id', 'default_project')
    episode_id = request.form.get('episode_id', 'E001') # Ex: E202
    # Récupérer le numéro de séquence, avec une valeur par défaut si non fourni
    sequence_number = request.form.get('sequence_number', 'SQ0010')
    # Valider le format de sequence_number (e.g., SQxxxx)
    if not re.match(r"^SQ\d{4}$", sequence_number):
        logger.warning(f"Format de numéro de séquence invalide: {sequence_number}. Utilisation de SQ0010 par défaut.")
        sequence_number = 'SQ0010'

    # Valider le format de episode_id (e.g., Exxx)
    if not re.match(r"^E\d{3,}", episode_id):
         logger.warning(f"Format de numéro d'épisode invalide: {episode_id}. Utilisation de E001 par défaut.")
         episode_id = 'E001'

    # Créer le chemin de sortie basé sur nomenclature_test et les IDs
    # Le répertoire de base pour l'épisode contiendra les sous-dossiers de séquence
    # Exemple: i:\Madsea\outputs\nomenclature_test\E202\SQ0010\
    # Note: _process_pdf_advanced créera les sous-dossiers extracted-raw et AI-concept à l'intérieur
    # episode_specific_output_path = os.path.join(NOMENCLATURE_TEST_OUTPUT_BASE, episode_id, sequence_number)
    # Le chemin output_path passé à _process_pdf_advanced n'est plus aussi critique car les noms sont absolus
    # Mais il est bon de le garder pour une organisation générale si d'autres fichiers y sont écrits.
    # Pour l'instant, on va laisser _process_page_content_advanced gérer la création complète des chemins.
    output_base_for_episode = os.path.join(NOMENCLATURE_TEST_OUTPUT_BASE, episode_id)
    os.makedirs(output_base_for_episode, exist_ok=True) # Crée le dossier pour l'épisode s'il n'existe pas

    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        temp_dir = current_app.config.get('TEMP_DIR', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_pdf_path = os.path.join(temp_dir, original_filename)
        file.save(temp_pdf_path)
        logger.info(f"Fichier '{original_filename}' sauvegardé temporairement dans '{temp_pdf_path}'")

        # Utiliser output_base_for_episode comme base, _process_pdf_advanced s'occupera du reste avec sequence_number
        structured_data, _ = _process_pdf_advanced(temp_pdf_path, project_id, episode_id, sequence_number, output_base_for_episode, original_filename)

        try:
            os.remove(temp_pdf_path)
            logger.info(f"Fichier temporaire '{temp_pdf_path}' supprimé.")
        except OSError as e:
            logger.error(f"Erreur lors de la suppression du fichier temporaire {temp_pdf_path}: {e.strerror}")

        if structured_data:
            # S'assurer que les chemins dans structured_data sont corrects pour le client
            # La correction est déjà faite dans _process_page_content_advanced
            logger.info(f"Données structurées retournées pour {original_filename}")
            return jsonify(structured_data), 200
        else:
            logger.error(f"Échec du traitement du PDF {original_filename}")
            return jsonify({'error': 'Échec du traitement du PDF'}), 500
    else:
        logger.warning(f"Type de fichier non autorisé: {file.filename}")
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

# ... Rest of the file remains the same ...
