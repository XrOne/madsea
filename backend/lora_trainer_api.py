from flask import Blueprint, request, jsonify
import os
import zipfile
import tempfile
import subprocess
import uuid

lora_trainer_bp = Blueprint('lora_trainer', __name__)

@lora_trainer_bp.route('/api/lora/train', methods=['POST'])
def train_lora():
    """
    Endpoint pour entraîner un LoRA à partir d'un dataset d'images et de paramètres.
    Reçoit un zip d'images et les paramètres de training, lance le training, et retourne le chemin du modèle généré.
    """
    if 'dataset' not in request.files:
        return jsonify({'error': 'Aucun dataset fourni'}), 400
    dataset_file = request.files['dataset']
    params = request.form.to_dict()
    lora_name = params.get('lora_name', f'lora_{uuid.uuid4().hex[:8]}')
    epochs = params.get('epochs', '10')
    learning_rate = params.get('learning_rate', '1e-4')

    # Créer un dossier temporaire pour extraire le dataset
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_zip = os.path.join(tmpdir, 'dataset.zip')
        dataset_file.save(dataset_zip)
        with zipfile.ZipFile(dataset_zip, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        images_dir = tmpdir  # Les images sont extraites ici

        # Construire la commande d'entraînement (adapter selon ton script ComfyUI/LoRA)
        output_dir = os.path.join('i:/Madsea/outputs/lora_models', lora_name)
        os.makedirs(output_dir, exist_ok=True)
        lora_path = os.path.join(output_dir, f'{lora_name}.safetensors')
        train_script = 'i:/Madsea/scripts/train_lora.bat'  # À adapter selon ton infra
        cmd = [train_script, images_dir, lora_path, str(epochs), str(learning_rate)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logs = result.stdout
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Erreur entraînement LoRA: {e.stderr}'}), 500

    return jsonify({'status': 'success', 'lora_path': lora_path, 'logs': logs})
