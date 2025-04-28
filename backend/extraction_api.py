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

# Configuration du chemin vers l'exécutable Tesseract (à ajuster selon l'installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
UPLOAD_FOLDER = 'uploads' # Sous-dossier dans chaque projet
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}
PROJECTS_BASE_PATH = 'projects' # Dossier racine pour tous les projets

extraction_bp = Blueprint('extraction_bp', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @extraction_bp.route('/upload_storyboard', methods=['POST'])
# def upload_storyboard():
#     """Endpoint pour uploader un fichier storyboard (PDF ou ZIP d'images).
#     Réalise une extraction *simple* des images uniquement.
#     Crée une structure de dossier par projet/épisode.
#     """
#     print("Appel à l'ANCIEN /upload_storyboard") # Log modifié pour clarté
#     if 'storyboard_file' not in request.files:
#         print("Aucun fichier trouvé dans la requête /upload_storyboard")
#         return jsonify({'error': 'Aucun fichier trouvé dans la requête'}), 400
# 
#     file = request.files['storyboard_file']
# 
#     if file.filename == '':
#         print("Nom de fichier vide dans /upload_storyboard")
#         return jsonify({'error': 'Aucun fichier sélectionné'}), 400
# 
#     if 'project_id' not in request.form or 'episode_id' not in request.form:
#         print("Project ID ou Episode ID manquant dans /upload_storyboard")
#         return jsonify({'error': 'Project ID ou Episode ID non spécifié'}), 400
# 
#     project_id = request.form['project_id']
#     episode_id = request.form['episode_id']
# 
#     print(f"Upload pour Projet: {project_id}, Épisode: {episode_id}")
# 
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         # Chemin basé sur l'ID du projet et de l'épisode
#         project_path = os.path.join(current_app.config.get('PROJECTS_BASE_PATH', PROJECTS_BASE_PATH), project_id)
#         episode_path = os.path.join(project_path, 'episodes', episode_id)
#         upload_path = os.path.join(episode_path, UPLOAD_FOLDER)
# 
#         # Créer les répertoires si nécessaire
#         try:
#             os.makedirs(upload_path, exist_ok=True)
#             print(f"Dossier créé ou existant: {upload_path}")
#         except OSError as e:
#             print(f"Erreur création dossier {upload_path}: {e}")
#             return jsonify({'error': f'Impossible de créer le dossier du projet: {e}'}), 500
# 
#         file_path = os.path.join(upload_path, filename)
#         print(f"Chemin de sauvegarde fichier: {file_path}")
# 
#         try:
#             file.save(file_path)
#             print(f"Fichier sauvegardé: {file_path}")
#             # Extraction simple des images après sauvegarde
#             output_image_folder = os.path.join(episode_path, 'extracted_images') # Dossier pour images extraites
#             os.makedirs(output_image_folder, exist_ok=True)
# 
#             image_paths = []
#             file_ext = filename.rsplit('.', 1)[1].lower()
# 
#             if file_ext == 'pdf':
#                 image_paths = extract_images_from_pdf(file_path, output_image_folder)
#             elif file_ext == 'zip':
#                 # TODO: Implémenter l'extraction depuis ZIP si nécessaire
#                 # image_paths = extract_images_from_zip(file_path, output_image_folder)
#                 print("Extraction depuis ZIP non implémentée")
#                 pass # Pour l'instant
#             else: # Images simples
#                 # Si c'est déjà une image, on la "copie" logiquement
#                 new_image_path = os.path.join(output_image_folder, filename)
#                 import shutil
#                 shutil.copy(file_path, new_image_path)
#                 image_paths.append(new_image_path)
#                 print(f"Image copiée vers: {new_image_path}")
# 
#             # Convertir les chemins absolus en relatifs pour l'API
#             relative_image_paths = [
#                 os.path.relpath(p, current_app.config.get('PROJECTS_BASE_PATH', PROJECTS_BASE_PATH)).replace(os.sep, '/')
#                 for p in image_paths
#             ]
#             print(f"{len(relative_image_paths)} images extraites.")
# 
#             return jsonify({
#                 'message': 'Storyboard uploadé et images extraites (simple)',
#                 'file_path': os.path.relpath(file_path, current_app.config.get('PROJECTS_BASE_PATH', PROJECTS_BASE_PATH)).replace(os.sep, '/'),
#                 'project_id': project_id,
#                 'episode_id': episode_id,
#                 'extracted_images': relative_image_paths
#             }), 201
# 
#         except Exception as e:
#             print(f"Erreur lors de la sauvegarde ou extraction simple: {e}", exc_info=True)
#             return jsonify({'error': f'Échec de l\'upload ou extraction simple: {str(e)}'}), 500
#     else:
#         print(f"Type de fichier non autorisé: {file.filename}")
#         return jsonify({'error': 'Type de fichier non autorisé'}), 400

@extraction_bp.route('/upload_storyboard', methods=['POST']) # RENOMMÉ pour correspondre au frontend
def extraction_storyboard():
    """Endpoint pour uploader un fichier storyboard et réaliser une extraction avancée
    (images + texte + structure).
    """
    print("Appel à /upload_storyboard")
    if 'storyboard_file' not in request.files:
        print("Aucun fichier trouvé dans /upload_storyboard")
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['storyboard_file']
    if file.filename == '':
        print("Nom de fichier vide dans /upload_storyboard")
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
    if 'project_id' not in request.form or 'episode_id' not in request.form:
        print("Project ID ou Episode ID manquant dans /upload_storyboard")
        return jsonify({'error': 'Projet ou épisode non spécifié'}), 400
        
    project_id = request.form['project_id']
    episode_id = request.form['episode_id']
    print(f"Extraction avancée pour Projet: {project_id}, Épisode: {episode_id}")
    
    # Récupérer les options (si fournies)
    options = {}
    if 'options' in request.form:
        try:
            options = json.loads(request.form['options'])
            print(f"Options reçues: {options}")
        except Exception as e:
            print(f"Impossible de parser les options JSON: {e}")
            pass

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        project_path = os.path.join(current_app.config.get('PROJECTS_BASE_PATH', PROJECTS_BASE_PATH), project_id)
        episode_path = os.path.join(project_path, 'episodes', episode_id)
        upload_path = os.path.join(episode_path, UPLOAD_FOLDER)
        
        # Créer les répertoires si nécessaire
        os.makedirs(upload_path, exist_ok=True)
        
        file_path_abs = os.path.join(upload_path, filename)
        file_path_rel = os.path.relpath(file_path_abs, current_app.config.get('PROJECTS_BASE_PATH', PROJECTS_BASE_PATH)).replace(os.sep, '/')
        
        try:
            file.save(file_path_abs)
            print(f"Fichier sauvegardé: {file_path_abs}")
            
            # --- Nouvelle Logique d'Extraction --- 
            # Dossier pour le contenu extrait (images, json...)
            extraction_output_folder = os.path.join(episode_path, 'extracted_content') 
            extracted_data = extract_content_from_pdf(file_path_abs, extraction_output_folder)
            print(f"Extraction brute terminée. {len(extracted_data.get('images',[]))} images, {len(extracted_data.get('texts',[]))} textes.")
            
            # Vérifier si l'extraction a retourné une erreur
            if 'error' in extracted_data:
                print(f"Erreur retournée par extract_content_from_pdf: {extracted_data['error']}")
                return jsonify({'error': extracted_data['error']}), 500

            # TODO: 1. Sauvegarder extracted_data dans un fichier JSON
            # TODO: 2. Associer textes et images basé sur les bbox et la structure
            # TODO: 3. Analyser le contenu (titres, plans, dialogues, actions...)
            # TODO: 4. Retourner la structure finale analysée
            
            # Pour l'instant, retourner les données brutes extraites pour débogage
            
            # Sauvegarde temporaire des données brutes en JSON
            output_json_path = os.path.join(extraction_output_folder, 'raw_extracted_data.json')
            try:
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=4)
                print(f"Données brutes sauvegardées dans: {output_json_path}")
            except Exception as e:
                print(f"Erreur sauvegarde JSON brut: {e}")
                # Continuer même si la sauvegarde échoue

            return jsonify({
                'message': 'Storyboard extrait avec succès (Contenu brut)',
                'file_path': file_path_rel,
                'project_id': project_id,
                'episode_id': episode_id,
                'extracted_data': extracted_data, # Retourne les données brutes
                'ocr_enabled': True # Indique que l'extraction avancée a été tentée
            }), 201
        except Exception as e:
            print(f"Échec de l'extraction avancée: {e}", exc_info=True)
            return jsonify({'error': f'Échec de l\'extraction avancée: {str(e)}'}), 500
    else:
        print(f"Type de fichier non autorisé: {file.filename}")
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

@extraction_bp.route('/projects/<project_id>/episodes/<episode_id>/scenes', methods=['GET'])
def get_extracted_scenes(project_id, episode_id):
    """Endpoint pour récupérer les scènes extraites pour un épisode spécifique.
    Lit le fichier JSON final généré par l'analyse (pas encore implémenté).
    Pour l'instant, lit le fichier JSON brut s'il existe.
    """
    print(f"Demande des scènes pour Projet: {project_id}, Épisode: {episode_id}")
    project_path = os.path.join(current_app.config.get('PROJECTS_BASE_PATH', PROJECTS_BASE_PATH), project_id)
    episode_path = os.path.join(project_path, 'episodes', episode_id)
    extraction_output_folder = os.path.join(episode_path, 'extracted_content')
    
    # TODO: Lire le fichier JSON final quand il existera
    # final_json_path = os.path.join(extraction_output_folder, 'analyzed_scenes.json')
    
    # Pour l'instant, lire le fichier JSON brut
    raw_json_path = os.path.join(extraction_output_folder, 'raw_extracted_data.json')
    
    if os.path.exists(raw_json_path):
        try:
            with open(raw_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Données brutes lues depuis {raw_json_path}")
            # Idéalement, retourner les scènes structurées, pas les données brutes
            return jsonify({'scenes': data}), 200 
        except Exception as e:
            print(f"Erreur lecture JSON brut {raw_json_path}: {e}")
            return jsonify({'error': f'Impossible de lire les données extraites: {e}'}), 500
    else:
        print(f"Fichier de données extraites non trouvé: {raw_json_path}")
        return jsonify({'error': 'Aucune donnée extraite trouvée pour cet épisode'}), 404


# --- Fonctions utilitaires pour l'extraction ---

def extract_images_from_pdf(pdf_path, output_folder):
    """Extrait toutes les images d'un fichier PDF et les sauvegarde.

    Args:
        pdf_path (str): Chemin vers le fichier PDF.
        output_folder (str): Dossier où sauvegarder les images extraites.

    Returns:
        list: Liste des chemins complets des images sauvegardées.
    """
    image_paths = []
    try:
        doc = fitz.open(pdf_path)
        img_index = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            if not image_list:
                continue
            for img_info in image_list:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Générer un nom de fichier unique et nettoyer l'extension
                safe_ext = image_ext.split('+')[0].lower() # Garder que la partie avant un '+' potentiel et mettre en minuscule
                if safe_ext not in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']:
                    safe_ext = 'png' # fallback sur png si extension inconnue/invalide
                    
                image_filename = f"page{page_num + 1}_img{img_index + 1}.{safe_ext}"
                image_save_path = os.path.join(output_folder, image_filename)
                
                print(f"Sauvegarde de l'image extraite : {image_save_path}")
                with open(image_save_path, "wb") as img_file:
                    img_file.write(image_bytes)
                image_paths.append(image_save_path)
                img_index += 1
        doc.close()
    except Exception as e:
        print(f"Erreur lors de l'extraction d'images du PDF {pdf_path}: {e}")
        return [] # Retourner une liste vide en cas d'erreur
    return image_paths

def extract_content_from_pdf(pdf_path, output_folder):
    """
    Extrait les images et les blocs de texte d'un PDF avec leurs positions.
    Pour l'instant, extraction basique, l'analyse sémantique viendra ensuite.
    """
    try:
        # ====> NOUVEAU LOG OUVERTURE DOC
        print(f"Tentative d'ouverture du PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        print(f"PDF ouvert avec succès. Nombre de pages: {len(doc)}")
        
        # ====> NOUVEAU LOG DEBUT BOUCLE PAGES
        print(f"Début de la boucle sur les pages...")
        results = {'images': [], 'texts': []}
        for page_index, page in enumerate(doc):
            print(f"--- Traitement Page {page_index + 1} --- ")
            # Extraire les images
            try:
                image_list = page.get_images(full=True)
                print(f"Page {page_index + 1}: {len(image_list)} images trouvées par get_images.")
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                    except Exception as e:
                        print(f"Erreur lors de l'extraction de l'image xref {xref} page {page_index}: {e}")
                        continue # Passer à l'image suivante
                        
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    img_filename = f"page{page_index+1}_img{img_index+1}.{ext}"
                    img_path_abs = os.path.join(output_folder, img_filename)
                    img_path_rel = f"{os.path.relpath(output_folder, current_app.config.get('PROJECTS_BASE_PATH', 'projects')).replace(os.sep, '/')}/{img_filename}" # Chemin relatif pour URL
                    
                    try:
                        with open(img_path_abs, "wb") as img_file:
                            img_file.write(image_bytes)
                    except Exception as e:
                        print(f"Impossible d'écrire l'image {img_path_abs}: {e}")
                        continue # Passer à l'image suivante
                    
                    # Trouver les infos de position de l'image
                    try:
                        img_rects = page.get_image_rects(img)
                        if img_rects:
                             # Prend le premier rect si plusieurs
                            img_rect = img_rects[0]
                        else:
                            img_rect = fitz.Rect(0,0,0,0) # Bbox par défaut si non trouvée
                            print(f"Impossible de trouver la bbox pour image xref {xref} page {page_index}")
                    except Exception as e:
                        print(f"Erreur get_image_rects pour image xref {xref} page {page_index}: {e}")
                        img_rect = fitz.Rect(0,0,0,0)
                    
                    results['images'].append({
                        'path': img_path_rel,
                        'page': page_index + 1,
                        'bbox': list(img_rect) # [x0, y0, x1, y1]
                    })
            except Exception as e:
                 print(f"Erreur lors de l'extraction des images page {page_index}: {e}")

            # ====> NOUVEAU LOG FIN EXTRACTION IMAGES PAGE
            print(f"Page {page_index + 1}: Fin de la section extraction images.")

            # ====> EXTRACTION DU TEXTE VIA OCR <====
            print(f"Page {page_index + 1}: Début de l'extraction OCR sur les images")
            
            # Tenter d'abord l'extraction directe (pour les PDF avec du texte natif)
            try:
                raw_text = page.get_text("text")
                if raw_text.strip():
                    print(f"Page {page_index + 1}: Texte natif trouvé ({len(raw_text)} caractères)")
                    # Ajout du texte natif à la liste des textes
                    results['texts'].append({
                        'text': raw_text.strip(),
                        'page': page_index + 1,
                        'source': 'native',
                        'bbox': [0, 0, page.rect.width, page.rect.height]  # Page entière
                    })
                else:
                    print(f"Page {page_index + 1}: Pas de texte natif trouvé - passage à l'OCR")
            except Exception as e:
                print(f"Erreur lors de l'extraction de texte natif page {page_index}: {e}")
            
            # Application de l'OCR sur les images extraites de cette page
            try:
                # On prend seulement les images de la page courante
                page_images = [img for img in results['images'] if img['page'] == page_index + 1]
                print(f"Page {page_index + 1}: {len(page_images)} images à analyser par OCR")
                
                for img_index, img_data in enumerate(page_images):
                    try:
                        img_path = os.path.join(current_app.config.get('PROJECTS_BASE_PATH', 'projects'), img_data['path'])
                        print(f"OCR sur image: {img_path}")
                        
                        # Ouvrir l'image avec Pillow
                        with Image.open(img_path) as img:
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            img_byte_arr = img_byte_arr.getvalue()

                            # Prétraitement de l'image avec OpenCV
                            nparr = np.frombuffer(img_byte_arr, np.uint8)
                            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            
                            # Convertir en niveaux de gris
                            gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                            
                            # Appliquer un seuillage pour binariser l'image (améliorer le contraste)
                            # Utilisation de OTSU pour déterminer automatiquement le seuil optimal
                            _, processed_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                            
                            # Optionnel : Appliquer un léger flou pour réduire le bruit
                            # processed_img = cv2.medianBlur(processed_img, 3)

                            # Utiliser l'image prétraitée pour l'OCR
                            ocr_text = pytesseract.image_to_string(processed_img, lang='fra+eng', config='--psm 6') # PSM 6 assume a single uniform block of text.
                            if ocr_text.strip():
                                print(f"Texte OCR trouvé dans image {img_index+1}: '{ocr_text[:100]}...'")
                                
                                # Ajouter le texte OCR aux résultats
                                results['texts'].append({
                                    'text': ocr_text.strip(),
                                    'page': page_index + 1,
                                    'source': 'ocr',
                                    'image_index': img_index,
                                    'bbox': img_data['bbox']  # Utilise la boîte englobante de l'image
                                })
                            else:
                                print(f"Pas de texte OCR trouvé dans image {img_index+1}")
                    except Exception as e:
                        print(f"Erreur OCR sur image {img_index} de la page {page_index+1}: {e}")
            except Exception as e:
                print(f"Erreur générale lors du traitement OCR pour la page {page_index}: {e}")
                        
        # ====> NOUVEAU LOG AVANT RETURN
        print(f"Fin de extract_content_from_pdf. Données retournées : {results}")
        return results

    except Exception as e:
        print(f"Erreur majeure lors de l'ouverture ou du traitement du PDF {pdf_path}: {e}")
    finally:
        if doc:
            # ====> NOUVEAU LOG FERMETURE DOC
            print(f"Fermeture du document PDF.")
            doc.close()

# --- Fonctions utilitaires pour l'extraction (anciennes, à revoir/supprimer) ---

import logging

# Configuration simple du logging pour le module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_content_from_pdf(pdf_path, output_folder):
    extracted_texts = []
    extracted_images_info = []
    doc = None # Initialiser doc à None

    try:
        # Vérifier si le fichier PDF existe
        if not os.path.exists(pdf_path):
            logging.error(f"Le fichier PDF n'existe pas: {pdf_path}")
            return None

        # Créer le dossier de sortie s'il n'existe pas
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        logging.info(f"Traitement du fichier PDF: {pdf_path}")
        logging.info(f"Dossier de sortie: {output_folder}")

        # Ouvrir le document PDF
        doc = fitz.open(pdf_path)
        logging.info(f"Nombre de pages: {len(doc)}")

        # Parcourir chaque page
        for page_num in range(len(doc)):
            page = doc[page_num]
            logging.debug(f"Traitement de la page {page_num + 1}/{len(doc)}")

            # 1. Extraire le texte natif de la page
            raw_text = page.get_text("text").strip()
            if raw_text:
                logging.debug(f"Texte natif trouvé sur la page {page_num + 1} ({len(raw_text)} caractères)")
                extracted_texts.append(f"--- Page {page_num + 1} Texte Natif ---\
{raw_text}")
            else:
                 logging.debug(f"Aucun texte natif trouvé sur la page {page_num + 1}")

            # 2. Extraire les images et appliquer l'OCR
            image_list = page.get_images(full=True)
            logging.debug(f"Nombre d'images trouvées sur la page {page_num + 1}: {len(image_list)}")

            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                logging.debug(f"Traitement de l'image {img_index + 1} (xref: {xref}) sur la page {page_num + 1}")
                
                base_image = None
                try:
                    base_image = doc.extract_image(xref)
                except Exception as extraction_error:
                     logging.error(f"Erreur lors de l'extraction de l'image xref {xref} page {page_num + 1}: {extraction_error}")
                     continue # Passer à l'image suivante
                
                if not base_image:
                    logging.warning(f"Impossible d'extraire l'image xref {xref} page {page_num + 1}")
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_size = len(image_bytes)

                # Sauvegarder l'image extraite
                img_filename = f"page{page_num + 1}_panel{img_index + 1}.{image_ext}"
                img_filepath = os.path.join(output_folder, img_filename)
                
                try:
                    with open(img_filepath, "wb") as img_file:
                        img_file.write(image_bytes)
                    logging.debug(f"Image sauvegardée: {img_filepath} ({image_size} bytes)")
                    extracted_images_info.append({
                        'filename': img_filename,
                        'path': img_filepath,
                        'panel_index': img_index + 1,
                        'page_number': page_num + 1,
                        'size': image_size
                    })
                except IOError as save_error:
                    logging.error(f"Erreur lors de la sauvegarde de l'image {img_filepath}: {save_error}")
                    # Ne pas continuer l'OCR si on ne peut pas sauvegarder (ou lire plus tard)
                    continue

                # Appliquer l'OCR avec prétraitement
                try:
                    # Convertir les bytes en image OpenCV directement
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if cv_img is None:
                         logging.warning(f"Impossible de décoder l'image {img_index + 1} (page {page_num + 1}) avec OpenCV. Tentative avec Pillow.")
                         # Tentative de fallback avec Pillow directement depuis les bytes
                         try:
                             pil_img = Image.open(io.BytesIO(image_bytes))
                             ocr_text = pytesseract.image_to_string(pil_img, lang='fra+eng', config='--psm 6')
                         except Exception as pillow_fallback_error:
                             logging.error(f"Erreur OCR (Pillow fallback) image {img_index + 1} page {page_num + 1}: {pillow_fallback_error}")
                             ocr_text = "" # Pas de texte extrait
                    else:
                        # Convertir en niveaux de gris
                        gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                        # Appliquer un seuillage
                        _, processed_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        # Appliquer l'OCR sur l'image prétraitée
                        ocr_text = pytesseract.image_to_string(processed_img, lang='fra+eng', config='--psm 6')

                    ocr_text = ocr_text.strip()
                    if ocr_text:
                        extracted_texts.append(f"--- Page {page_num + 1} Image OCR (Panel {img_index + 1}) ---\
{ocr_text}")
                        logging.debug(f"Texte OCR trouvé image {img_index+1} page {page_num + 1} ({len(ocr_text)} caractères)")
                    else:
                        logging.debug(f"Aucun texte OCR trouvé image {img_index+1} page {page_num + 1}")

                except Exception as ocr_error:
                    logging.error(f"Erreur générale pendant l'OCR/Prétraitement image {img_index + 1} page {page_num + 1}: {ocr_error}")
                    # Optionnel : tenter un fallback OCR sans prétraitement si OpenCV a échoué
                    if 'cv_img' not in locals() or cv_img is None:
                        try:
                            pil_img_fallback = Image.open(io.BytesIO(image_bytes))
                            ocr_text_fallback = pytesseract.image_to_string(pil_img_fallback, lang='fra+eng', config='--psm 6').strip()
                            if ocr_text_fallback:
                                extracted_texts.append(f"--- Page {page_num + 1} Image OCR (Fallback Panel {img_index + 1}) ---\
{ocr_text_fallback}")
                                logging.debug(f"Texte OCR (Fallback) trouvé image {img_index+1} page {page_num + 1} ({len(ocr_text_fallback)} caractères)")
                        except Exception as fallback_error:
                            logging.error(f"Erreur OCR (Fallback général) image {img_index + 1} page {page_num + 1}: {fallback_error}")
        
        # Construction du résultat final
        results = {
            "texts": extracted_texts,
            "images": extracted_images_info
        }
        logging.info(f"Extraction terminée pour {pdf_path}. {len(extracted_texts)} blocs de texte, {len(extracted_images_info)} images.")
        return results

    except fitz.fitz.FileNotFoundError:
        logging.error(f"Erreur critique: Fichier PDF non trouvé ou inaccessible: {pdf_path}")
        return None
    except Exception as e:
        logging.exception(f"Erreur inattendue lors du traitement du PDF {pdf_path}: {e}") # Log l'exception complète
        return None
    finally:
        # Assurer la fermeture du document PDF s'il a été ouvert
        if doc:
            try:
                doc.close()
                logging.info(f"Document PDF fermé: {pdf_path}")
            except Exception as close_error:
                logging.error(f"Erreur lors de la fermeture du document PDF {pdf_path}: {close_error}")

# --- Reste du fichier (routes Flask, etc.) ---
