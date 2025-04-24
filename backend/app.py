import os
import uuid
import zipfile
import subprocess
import datetime
import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import werkzeug.utils
import fitz  # PyMuPDF
from PIL import Image

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_images_from_pdf(pdf_path, output_folder):
    print(f'[Backend] Extraction images du PDF: {pdf_path} vers {output_folder}')
    doc = fitz.open(pdf_path)
    image_paths = []
    for page_index in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_index)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            img_filename = f"page{page_index+1}_img{img_index+1}.{ext}"
            img_path = os.path.join(output_folder, img_filename)
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)
            print(f'[Backend] Image extraite: {img_path}')
            image_paths.append(img_path)
    return image_paths

def extract_images_from_zip(zip_path, output_folder):
    image_paths = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                zip_ref.extract(file, output_folder)
                image_paths.append(os.path.join(output_folder, file))
    return image_paths

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/upload_storyboard', methods=['POST'])
def upload_storyboard():
    if 'storyboard_file' not in request.files:
        return jsonify({'error': 'Aucun fichier trouvé dans la requête'}), 400

    file = request.files['storyboard_file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        images_folder = os.path.join(session_folder, "images")
        os.makedirs(images_folder, exist_ok=True)
        filename = werkzeug.utils.secure_filename(file.filename)
        file_path = os.path.join(session_folder, filename)
        file.save(file_path)

        # Extraction
        image_paths = []
        if ext == "pdf":
            print(f'[Backend] Extraction du fichier {file_path} (type: {ext})')
            image_paths = extract_images_from_pdf(file_path, images_folder)
            print(f'[Backend] {len(image_paths)} images extraites: {image_paths}')
        elif ext == "zip":
            image_paths = extract_images_from_zip(file_path, images_folder)
        else:
            return jsonify({'error': 'Type de fichier non supporté pour extraction'}), 400

        # Générer les URLs accessibles côté front
        image_urls = [
            f"/uploads/{session_id}/images/{os.path.basename(p)}"
            for p in image_paths
        ]
        print(f'[Backend] URLs images générées: {image_urls}')
        return jsonify({
            'message': f"{len(image_urls)} images extraites.",
            'images': image_urls,
            'session_id': session_id
        }), 200
    else:
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

@app.route('/api/extraction_storyboard', methods=['POST'])
def extraction_storyboard():
    """
    Endpoint : Extraction enrichie images+textes à partir d’un PDF storyboard (upload ou chemin).
    Utilise le script parsing/003-prototype-extraction-pdf.py. Stocke images+JSON dans outputs/.
    Retourne le JSON structuré au front. Autosave à chaque extraction.
    """
    if 'storyboard_file' not in request.files:
        return jsonify({'error': 'Aucun fichier trouvé dans la requête'}), 400
    file = request.files['storyboard_file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    # Création dossier outputs et autosave
    outputs_dir = os.path.join(os.path.dirname(__file__), '../outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # Sauvegarde initiale dans uploads
    upload_folder = app.config['UPLOAD_FOLDER'] # Utilise UPLOAD_FOLDER défini plus haut
    os.makedirs(upload_folder, exist_ok=True)
    safe_filename = werkzeug.utils.secure_filename(file.filename)
    base_name, ext = os.path.splitext(safe_filename)
    pdf_filename = f"{base_name}_{now}{ext}"
    pdf_path_upload = os.path.join(upload_folder, pdf_filename)
    file.save(pdf_path_upload)
    # Création d’un dossier images unique par session sous UPLOAD_FOLDER
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    session_base_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    session_images_dir = os.path.join(session_base_dir, "images")
    os.makedirs(session_images_dir, exist_ok=True)
    # Copie persistante dans outputs pour traitement
    pdf_path_outputs = os.path.join(outputs_dir, pdf_filename)
    shutil.copy2(pdf_path_upload, pdf_path_outputs)
    # Appel extraction avec --output_dir
    script_path_rel = '../parsing/003-prototype-extraction-pdf.py'
    script_path_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), script_path_rel))
    pdf_path_abs = os.path.abspath(pdf_path_outputs)
    project_root = os.path.dirname(os.path.dirname(script_path_abs))
    try:
        # Passage des paramètres de nomenclature pipeline prod (E202_SQ0010-0010)
        subprocess.run([
            'python', script_path_abs, pdf_path_abs,
            '--output_dir', os.path.abspath(session_images_dir),
            '--episode_code', 'E202',
            '--sequence_offset', '10',
            '--shot_offset', '10'
        ], check=True, cwd=project_root, capture_output=True, text=True)
        print(f"[Backend] Script extraction exécuté avec succès pour {pdf_path_abs}")
    except Exception as e:
        print(f"[Backend] Erreur extraction: {e}")
        return jsonify({'error': f'Erreur extraction: {e}'}), 500
    # Lecture du JSON généré
    # Le JSON est généré à côté du PDF dans outputs
    json_path = os.path.splitext(pdf_path_outputs)[0] + '_extraction.json'
    if not os.path.exists(json_path):
        return jsonify({'error': 'Extraction JSON non trouvé'}), 500
    with open(json_path, 'r', encoding='utf-8') as f:
        results = f.read()
    # Correction des chemins images dans le JSON pour URLs front
    import json as _json
    data = _json.loads(results)
    for scene in data.get("scenes", []):
        if scene.get("image"):
            # Le chemin relatif est maintenant déjà sous uploads/session/images
            # L'URL doit être construite correctement pour pointer vers uploads/session/images
            # Note: Le script d'extraction retourne un chemin relatif au PDF *dans* uploads/session/images.
            # On doit reconstruire l'URL pour /uploads/
            img_relative_path_in_json = scene["image"] # Ex: page_1.jpg (ou similaire, relatif à son dir)
            # Correctif : On prend juste le nom du fichier car on sait qu'il est dans session_images_dir
            img_name = os.path.basename(img_relative_path_in_json)
            scene["image_url"] = f"/uploads/{session_id}/images/{img_name}"
    results = _json.dumps(data, ensure_ascii=False, indent=2)
    # Autosave dans backups/<project_id>/ (si besoin, à améliorer avec vrai ID projet)
    backups_dir = os.path.join(os.path.dirname(__file__), '../backups/autosave')
    os.makedirs(backups_dir, exist_ok=True)
    backup_json = os.path.join(backups_dir, f'{now}_extraction.json')
    with open(backup_json, 'w', encoding='utf-8') as f:
        f.write(results)
    print(f"[Backend] Extraction enrichie terminée. JSON: {json_path} | Autosave: {backup_json}")
    return results, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    print("[Backend] Serveur Flask extraction images démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)
