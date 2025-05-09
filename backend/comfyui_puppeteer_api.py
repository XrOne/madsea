"""
API de liaison entre Madsea et Puppeteer pour l'automatisation de ComfyUI
Ce module facilite l'exécution automatisée des workflows ComfyUI via Puppeteer
"""

from flask import Blueprint, request, jsonify
import os
import logging
import time
import json
from services.ComfyUI.service import ComfyUIService

# Création du blueprint pour les routes Puppeteer
puppeteer_bp = Blueprint('puppeteer_bp', __name__)

# Configuration du logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@puppeteer_bp.route('/api/puppeteer/status', methods=['GET'])
def check_puppeteer_status():
    """
    Vérifie si Puppeteer est disponible et fonctionnel
    """
    try:
        # Simuler une vérification de statut
        return jsonify({
            "status": "available",
            "message": "Puppeteer est prêt à l'emploi",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut Puppeteer: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Puppeteer n'est pas disponible: {str(e)}"
        }), 500

@puppeteer_bp.route('/api/puppeteer/process', methods=['POST'])
def process_with_puppeteer():
    """
    Traite un plan avec Puppeteer pour automatiser ComfyUI
    Permet l'automatisation complète du workflow de génération
    """
    data = request.json
    
    # Vérification des données obligatoires
    if not data or 'image_path' not in data:
        return jsonify({"error": "Image path manquant"}), 400
    
    # Initialisation du service ComfyUI
    comfyui_service = ComfyUIService()
    
    try:
        # Appel réel au MCP Puppeteer pour automatisation one-click
        prompt = data.get('prompt', 'silhouette style, shadow art, high contrast black and white, minimalist, backlit figures, strong shadows, cinematic lighting, crisp edges, declic animation style')
        negative_prompt = data.get('negative_prompt', 'color, blurry, detailed, noise, grain, text, low contrast, soft edges, multiple figures, busy background')
        lora_strength = data.get('lora_strength', 0.8)

        mcp_result = comfyui_service.generate_with_puppeteer(
            image_path=data['image_path'],
            prompt=prompt,
            negative_prompt=negative_prompt,
            lora_strength=lora_strength
        )

        if mcp_result['status'] == 'success':
            return jsonify({
                "status": "success",
                "result": mcp_result['result'],
                "message": "Traitement automatisé MCP Puppeteer réussi"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": mcp_result['message']
            }), 500
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement Puppeteer: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500