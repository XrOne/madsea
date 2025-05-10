import os
import sys  # Ajout pour résoudre les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from flask import Flask, jsonify, request, send_from_directory, current_app
from flask_cors import CORS
import werkzeug.utils
import fitz  # PyMuPDF
import uuid
import zipfile
import subprocess
import datetime
import shutil
import logging
import pytesseract  # Ajout de l'import ici pour configuration globale

# Intégration MCP ComfyUI
try:
    from comfy_mcp import init_comfy_mcp
    COMFY_MCP_AVAILABLE = True
    print("[Backend] Intégration MCP ComfyUI disponible")
except ImportError:
    COMFY_MCP_AVAILABLE = False
    print("[Backend] AVERTISSEMENT: MCP ComfyUI non disponible - pip install comfy-mcp-server pour l'activer")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)

# Configuration Tesseract - Recherche automatique du binaire avec priorité à l'installation standard
def find_tesseract():
    # Installation standard (prioritaire) - ajouté '/bin' car dans les versions récentes tesseract.exe est dans le sous-dossier bin
    standard_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Installation standard 5.0.x
        r'C:\Program Files\Tesseract-OCR\bin\tesseract.exe',  # Installation standard 5.3.x+
    ]
    
    # Vérification des chemins standards d'abord (les plus probables)
    for path in standard_paths:
        if os.path.exists(path):
            print(f"[Backend] Tesseract trouvé à: {path}")
            return path
    
    # Autres emplacements possibles
    fallback_paths = [
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',  # 32-bit sur système 64-bit
        r'C:\Program Files (x86)\Tesseract-OCR\bin\tesseract.exe',  # 32-bit avec bin
        r'i:\Madsea\ocr\tesseract.exe',  # Installation locale au projet
    ]
    
    # Essayer les chemins alternatifs
    for path in fallback_paths:
        if os.path.exists(path):
            print(f"[Backend] Tesseract trouvé à: {path}")
            return path
    
    # Essai via PATH (least likely to work but worth trying)
    try:
        from shutil import which
        system_path = which('tesseract')
        if system_path:
            print(f"[Backend] Tesseract trouvé dans le PATH: {system_path}")
            return system_path
    except Exception as e:
        pass
    
    # Par défaut, on retourne un chemin standard même s'il n'existe pas
    default_path = r'C:\Program Files\Tesseract-OCR\bin\tesseract.exe'
    print(f"[Backend] AVERTISSEMENT: Tesseract non trouvé, utilisation du chemin par défaut: {default_path}")
    return default_path

# Trouver Tesseract et configurer l'application
tesseract_path = find_tesseract()
app.config['TESSERACT_PATH'] = tesseract_path
app.config['OCR_LANGUAGES'] = 'fra+eng'
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100 MB limit

# Configuration globale de Tesseract pour tout le backend
pytesseract.pytesseract.tesseract_cmd = tesseract_path

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Configuration du Logging --- 
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Niveau de log général
app.logger.setLevel(logging.DEBUG)
for handler in app.logger.handlers:
    handler.setLevel(logging.DEBUG)

# Route de test simple pour diagnostiquer les problèmes d'accès
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "L'API fonctionne!"})

# Configuration Tesseract dans le contexte d'application
with app.app_context():
    # Définition explicite de Tesseract avant l'import des modules
    pytesseract.pytesseract.tesseract_cmd = app.config['TESSERACT_PATH']

# --- Importation et Enregistrement des Blueprints (Corrigé) ---
try:
    from projects_api import project_bp
    from extraction_api import extraction_bp
    from comfyui_api import comfyui_bp
    from comfyui_puppeteer_api import puppeteer_bp
    from workflow_api import workflow_bp
    from puppeteer_image_api import puppeteer_image_bp

    print("[Backend] Enregistrement du blueprint 'project_bp'")
    app.register_blueprint(project_bp, url_prefix='/api')
    print("[Backend] Enregistrement du blueprint 'extraction_bp'")
    app.register_blueprint(extraction_bp, url_prefix='/api')
    print("[Backend] Enregistrement du blueprint 'comfyui_bp'")
    app.register_blueprint(comfyui_bp, url_prefix='/api')
    print("[Backend] Enregistrement du blueprint 'puppeteer_bp'")
    app.register_blueprint(puppeteer_bp, url_prefix='/api')
    print("[Backend] Enregistrement du blueprint 'workflow_bp'")
    app.register_blueprint(workflow_bp, url_prefix='/api')
    print("[Backend] Enregistrement du blueprint 'puppeteer_image_bp'")
    app.register_blueprint(puppeteer_image_bp, url_prefix='/api')

except ImportError as e:
    print(f"[Backend] ERREUR CRITIQUE: Impossible d'importer les blueprints: {e}")
    # sys.exit(1)

# --- Initialisation du MCP ComfyUI ---
if COMFY_MCP_AVAILABLE:
    try:
        # Initialiser le serveur MCP ComfyUI avec l'URL de votre instance
        init_comfy_mcp(app, "http://127.0.0.1:8188")
        print("[Backend] MCP ComfyUI initialisé avec succès - Endpoints disponibles")
    except Exception as e:
        print(f"[Backend] Erreur d'initialisation MCP ComfyUI: {e}")

# Route racine pour servir le frontend React/Tailwind
@app.route('/', methods=['GET'])
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

# --- Bloc d'exécution principal ---
if __name__ == '__main__':
    print("[Backend] Serveur Flask principal démarré sur http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')