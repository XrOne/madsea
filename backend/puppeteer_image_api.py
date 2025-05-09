from flask import Blueprint, request, jsonify
import os
import werkzeug
from services.ComfyUI.service import ComfyUIService

puppeteer_image_bp = Blueprint('puppeteer_image_bp', __name__)

@puppeteer_image_bp.route('/api/puppeteer/process-image', methods=['POST'])
def puppeteer_process_image():
    """
    Upload d'une image et génération auto via MCP Puppeteer
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier image fourni'}), 400
    file = request.files['file']
    if not (file.filename.endswith('.png') or file.filename.endswith('.jpg') or file.filename.endswith('.jpeg')):
        return jsonify({'error': 'Format non supporté (PNG/JPG attendu)'}), 400
    filename = werkzeug.utils.secure_filename(file.filename)
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'temp'))
    os.makedirs(temp_dir, exist_ok=True)
    save_path = os.path.join(temp_dir, filename)
    file.save(save_path)

    # Appel MCP Puppeteer
    prompt = request.form.get('prompt', 'silhouette style, shadow art, high contrast black and white, minimalist, backlit figures, strong shadows, cinematic lighting, crisp edges, declic animation style')
    negative_prompt = request.form.get('negative_prompt', 'color, blurry, detailed, noise, grain, text, low contrast, soft edges, multiple figures, busy background')
    lora_strength = float(request.form.get('lora_strength', 0.8))
    comfyui_service = ComfyUIService()
    result = comfyui_service.generate_with_puppeteer(
        image_path=save_path,
        prompt=prompt,
        negative_prompt=negative_prompt,
        lora_strength=lora_strength
    )
    if result['status'] == 'success':
        return jsonify({'status': 'success', 'result': result['result'], 'message': 'Test image MCP Puppeteer réussi'}), 200
    else:
        return jsonify({'status': 'error', 'message': result['message']}), 500
