import os
import sys  # Ajout pour résoudre les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
import sys

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

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100 MB limit

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

# --- Importation et Enregistrement des Blueprints (Corrigé) ---
try:
    from projects_api import project_bp
    from extraction_api import extraction_bp

    print("[Backend] Enregistrement du blueprint 'project_bp'")
    app.register_blueprint(project_bp, url_prefix='/api')

    print("[Backend] Enregistrement du blueprint 'extraction_bp'")
    app.register_blueprint(extraction_bp, url_prefix='/api')

except ImportError as e:
    print(f"[Backend] ERREUR CRITIQUE: Impossible d'importer les blueprints: {e}")
    # sys.exit(1)

# --- Bloc d'exécution principal ---
if __name__ == '__main__':
    print("[Backend] Serveur Flask principal démarré sur http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')