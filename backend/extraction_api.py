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

# Configuration du chemin vers l'exécutable Tesseract (à ajuster selon l'installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
UPLOAD_FOLDER = 'uploads' # Sous-dossier dans chaque projet
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}
PROJECTS_BASE_PATH = 'projects' # Dossier racine pour tous les projets
NOMENCLATURE_TEST_OUTPUT_BASE = Path("i:/Madsea/outputs/nomenclature_test")

# Configuration du logger
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _process_pdf_advanced(pdf_temp_path, project_id, episode_id, output_path, original_filename):
    """
    Processes a PDF file to extract images and structured text from each panel.

    Args:
        pdf_temp_path (str): Temporary path to the uploaded PDF file.
        project_id (str): The ID of the project.
        episode_id (str): The ID of the episode.
        output_path (str): The directory path to save extracted images.
        original_filename (str): The original name of the PDF file.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
              {'panel_id': str, 'image_path': str, 'title': str, 
               'voice_over': str, 'action': str, 'text': str}
              Returns an empty list if an error occurs or no data is extracted.
    """
    extracted_data = []
    try:
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        doc = fitz.open(pdf_temp_path)
        current_app.logger.info(f"Processing PDF: {original_filename} with {len(doc)} pages.")

        panel_counter = 0  # Global counter for panels across pages

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_id = f"E{episode_id}_SQ{page_num + 1:04d}"
            
            # 1. Extract images from the page
            images = page.get_images(full=True)
            current_app.logger.info(f"Page {page_num + 1}: Found {len(images)} images.")
            
            # Get all image rectangles on the page
            image_rects = []
            for img in images:
                # Get all instances of this image on the page
                rects = page.get_image_bbox(img)
                for rect in rects:
                    image_rects.append({"img": img, "rect": rect})
            
            # Sort images by vertical position (top to bottom)
            image_rects.sort(key=lambda x: x["rect"].y0)
            
            # 2. Extract text with detailed formatting (for bold detection - voix off)
            page_dict = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT)
            
            if not image_rects:  # No images found on page
                # Treat the whole page as one panel
                panel_counter += 1
                panel_id = f"{page_id}_PNL{panel_counter:03d}"
                
                # Save page as image
                img_filename = f"{panel_id}_extracted_v001.png"
                img_save_path = os.path.join(output_path, img_filename)
                
                try:
                    pix = page.get_pixmap(dpi=300)
                    pix.save(img_save_path)
                    
                    # Extract text directly or via OCR if needed
                    page_text = page.get_text("text")
                    if not page_text.strip():
                        current_app.logger.info(f"No direct text found, attempting OCR on page {page_num + 1}.")
                        try:
                            img_bytes = pix.tobytes("png")
                            pil_image = Image.open(io.BytesIO(img_bytes))
                            page_text = pytesseract.image_to_string(pil_image, lang='fra')
                        except Exception as e_ocr:
                            current_app.logger.error(f"OCR error: {e_ocr}")
                            page_text = ""
                    
                    # Parse text into title, voice_over, action
                    title, voice_over, action = parse_panel_text(page_text, page_dict)
                    
                    extracted_data.append({
                        'panel_id': panel_id,
                        'image_path': img_save_path,
                        'title': title,
                        'voice_over': voice_over,
                        'action': action,
                        'text': page_text.strip()  # Full raw text
                    })
                    current_app.logger.info(f"Saved page {page_num + 1} as panel image: {img_save_path}")
                except Exception as e:
                    current_app.logger.error(f"Error saving page {page_num + 1} as image: {e}")
            else:
                # Process each image on the page and find its associated text
                for img_idx, img_data in enumerate(image_rects):
                    panel_counter += 1
                    panel_id = f"{page_id}_PNL{panel_counter:03d}"
                    
                    # Extract and save the image
                    img_info = img_data["img"]
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    img_filename = f"{panel_id}_extracted_v001.{image_ext}"
                    img_save_path = os.path.join(output_path, img_filename)
                    
                    with open(img_save_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # Find text associated with this image (below it)
                    img_rect = img_data["rect"]
                    associated_text = find_text_for_image(page, img_rect, page_dict, image_rects)
                    
                    # Parse the associated text into title, voice_over, action
                    title, voice_over, action = parse_panel_text(associated_text, page_dict)
                    
                    extracted_data.append({
                        'panel_id': panel_id,
                        'image_path': img_save_path,
                        'title': title,
                        'voice_over': voice_over,
                        'action': action,
                        'text': associated_text.strip()  # Full raw text
                    })
                    current_app.logger.info(f"Saved panel {panel_id} image: {img_save_path}")
                    
        doc.close()
        current_app.logger.info(f"Successfully processed PDF. Extracted {len(extracted_data)} panels.")

    except Exception as e:
        current_app.logger.error(f"Error processing PDF {original_filename}: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return []  # Return empty list on error

    return extracted_data

def find_text_for_image(page, img_rect, page_dict, all_image_rects):
    """
    Find text that is associated with an image, typically below it.
    """
    associated_text = ""
    
    # Define a reasonable vertical search zone below the image
    max_y_search = img_rect.y1 + (page.rect.height * 0.2)  # Search up to 20% of page height below image
    
    # Find all text blocks that are below this image and within its horizontal bounds
    relevant_blocks = []
    
    for block in page_dict.get("blocks", []):
        if block["type"] == 0:  # Text block
            block_rect = fitz.Rect(block["bbox"])
            
            # Check if block is below the image and within a reasonable vertical distance
            is_below = block_rect.y0 >= img_rect.y1
            is_in_search_zone = block_rect.y0 <= max_y_search
            
            # Check if block overlaps horizontally with the image
            h_overlap = max(0, min(img_rect.x1, block_rect.x1) - max(img_rect.x0, block_rect.x0))
            is_horizontally_aligned = h_overlap > 0
            
            # Check if this block is not closer to another image
            is_closest_to_this_image = True
            for other_img_data in all_image_rects:
                other_rect = other_img_data["rect"]
                if other_rect == img_rect:
                    continue  # Skip comparing with itself
                
                # If another image is between this image and the text block, skip this block
                if (other_rect.y0 > img_rect.y1) and (other_rect.y1 < block_rect.y0):
                    if h_overlap > 0:  # If there's horizontal overlap with the other image
                        is_closest_to_this_image = False
                        break
            
            if is_below and is_in_search_zone and is_horizontally_aligned and is_closest_to_this_image:
                relevant_blocks.append(block)
    
    # Sort blocks by vertical position (top to bottom)
    relevant_blocks.sort(key=lambda b: fitz.Rect(b["bbox"]).y0)
    
    # Extract text from relevant blocks
    for block in relevant_blocks:
        for line in block.get("lines", []):
            line_text = "".join(span["text"] for span in line.get("spans", []))
            associated_text += line_text + "\n"
    
    return associated_text

def parse_panel_text(text, page_dict=None):
    """
    Parse panel text into title, voice_over, and action.
    """
    title = ""
    voice_over = ""
    action_lines = []
    
    lines = text.split("\n")
    remaining_lines = []
    
    # 1. Extract title (starts with INT./EXT.)
    for i, line in enumerate(lines):
        if line.strip().startswith(("INT.", "EXT.")):
            title = line.strip()
            remaining_lines = lines[:i] + lines[i+1:]  # All lines except title
            break
    else:
        remaining_lines = lines  # No title found
    
    # 2. Extract voice over (bold text)
    if page_dict:
        # Use formatting information from page_dict to find bold text
        bold_spans = []
        for block in page_dict.get("blocks", []):
            if block["type"] == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        # In PyMuPDF, bold text often has font weight > 400
                        if span.get("font").lower().find("bold") >= 0 or span.get("weight", 0) > 400:
                            bold_spans.append(span["text"])
        
        if bold_spans:
            voice_over = " ".join(bold_spans)
    
    # 3. If we couldn't identify bold text, fall back to heuristics
    if not voice_over and remaining_lines:
        # Heuristic: look for lines that might be voice over (ALL CAPS, special prefixes, etc.)
        for i, line in enumerate(remaining_lines):
            line_stripped = line.strip()
            if line_stripped.isupper() and len(line_stripped) > 10:  # Potential voice over in ALL CAPS
                voice_over = line_stripped
                remaining_lines.pop(i)
                break
    
    # 4. All remaining lines are considered action description
    action = "\n".join(line for line in remaining_lines if line.strip())
    
    return title, voice_over, action

extraction_bp = Blueprint('extraction_bp', __name__)

@extraction_bp.route('/upload_storyboard', methods=['POST'])
def upload_storyboard_v3():
    """Endpoint pour uploader un storyboard PDF (v3), extrait images et textes.
    Utilise _process_pdf_advanced et sauvegarde les sorties dans NOMENCLATURE_TEST_OUTPUT_BASE.
    Crée des placeholders AI-concept.
    """
    current_app.logger.info(f"Entrée dans /upload_storyboard")
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
    
    current_app.logger.info(f"Traitement avancé terminé pour {filename}. Nombre d'images extraites (raw): {len(extracted_data)}")

    # Création des placeholders AI-concept
    ai_concept_images_info_list = [] # Initialiser ici pour toujours l'avoir
    if extracted_data:
        raw_images_info_list = extracted_data
        
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

    current_app.logger.info(f"Réponse JSON pour /upload_storyboard: {extracted_data}")
    return jsonify(extracted_data), 200

# ... Rest of the file remains the same ...
