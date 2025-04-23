import os
import uuid
import zipfile
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
            image_paths = extract_images_from_pdf(file_path, images_folder)
        elif ext == "zip":
            image_paths = extract_images_from_zip(file_path, images_folder)
        else:
            return jsonify({'error': 'Type de fichier non supporté pour extraction'}), 400

        # Générer les URLs accessibles côté front
        image_urls = [
            f"/uploads/{session_id}/images/{os.path.basename(p)}"
            for p in image_paths
        ]

        return jsonify({
            'message': f"{len(image_urls)} images extraites.",
            'images': image_urls,
            'session_id': session_id
        }), 200
    else:
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

if __name__ == '__main__':
    print("[Backend] Serveur Flask extraction images démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)
