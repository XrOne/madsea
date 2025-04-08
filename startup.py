#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de démarrage global pour la plateforme Storyboard-to-Video AI (Madsea)

Ce script initialise tous les composants nécessaires au fonctionnement de la plateforme:
- Parsing: extraction des scènes à partir de storyboards
- Generation: génération d'images avec Stable Diffusion, ControlNet et LoRA
- Styles: gestion des styles visuels, y compris Déclic Ombre Chinoise
- Video: assemblage des images en séquences vidéo
- UI: interface web basée sur Flask et intégration avec ComfyUI/SwarmUI

Il configure également les modèles externes (Qwen 2.1, Google Gemini Studio, WAN 2.1)
pour le style Déclic Ombre Chinoise.

Utilisation:
    python startup.py [options]

Options:
    --config, -c: Chemin vers le fichier de configuration (default: config/default.yaml)
    --web, -w: Démarrer l'interface web
    --install-models, -i: Installer et configurer les modèles externes
    --check-dependencies, -d: Vérifier les dépendances requises
    --verbose, -v: Afficher les logs détaillés
"""

import argparse
import logging
import os
import sys
import subprocess
import time
import json
import yaml
from pathlib import Path
import asyncio # Added for async manager operations

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer les modules du projet
from parsing.parser import StoryboardParser
from generation.generator import ImageGenerator
from styles.manager import StyleManager
from video.assembler import VideoAssembler
from utils.config import load_config, save_config
# Import new managers
from utils.api_manager import APIManager
from utils.model_manager import ModelManager
from utils.cache_manager import CacheManager
from utils.security import SecurityManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("madsea.log"),
    ],
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Analyse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Script de démarrage global pour la plateforme Storyboard-to-Video AI"
    )
    parser.add_argument(
        "--config", "-c", type=str, default="config/default.yaml", 
        help="Chemin vers le fichier de configuration"
    )
    parser.add_argument(
        "--web", "-w", action="store_true", 
        help="Démarrer l'interface web"
    )
    parser.add_argument(
        "--install-models", "-i", action="store_true",
        help="Installer et configurer les modèles externes"
    )
    parser.add_argument(
        "--check-dependencies", "-d", action="store_true",
        help="Vérifier les dépendances requises"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Afficher les logs détaillés"
    )
    return parser.parse_args()


# Modify check_dependencies to accept managers
async def check_dependencies(config, api_manager):
    """Vérifie que toutes les dépendances requises sont installées."""
    logger.info("Vérification des dépendances...")
    all_ok = True
    
    # Vérifier les dépendances Python
    try:
        import torch
        import numpy
        import PIL
        import flask
        import fitz  # PyMuPDF
        import pytesseract
        import cv2
        import diffusers
        import transformers
        import aiohttp # Needed for APIManager
        import cryptography # Needed for SecurityManager
        
        logger.info("✓ Dépendances Python de base installées")
    except ImportError as e:
        logger.error(f"✗ Dépendance Python manquante: {e}")
        logger.info("Exécutez 'pip install -r requirements.txt' pour installer les dépendances")
        logger.info("Assurez-vous aussi d'installer 'aiohttp' et 'cryptography'.")
        all_ok = False
        # Return early if core dependencies are missing
        return False
    
    # Vérifier Tesseract OCR
    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"✓ Tesseract OCR installé (version {version})")
    except Exception:
        logger.warning("✗ Tesseract OCR non détecté. L'OCR ne fonctionnera pas correctement.")
        logger.info("Installez Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        # Optional dependency, don't set all_ok = False
    
    # Vérifier FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✓ FFmpeg installé ({version_line})")
        else:
            raise Exception("FFmpeg command failed")
    except Exception:
        logger.warning("✗ FFmpeg non détecté ou erreur lors de la vérification. La génération de vidéos ne fonctionnera pas.")
        logger.info("Installez FFmpeg: https://ffmpeg.org/download.html")
        all_ok = False # Video generation is core

    # Vérifier ComfyUI using APIManager (if configured)
    comfyui_config = config.get("comfyui", {})
    comfyui_host = comfyui_config.get("host", "127.0.0.1")
    comfyui_port = comfyui_config.get("port", 8188)
    comfyui_url = f"http://{comfyui_host}:{comfyui_port}"
    # Register comfyui endpoint info if not already done
    api_manager.register_api("comfyui", endpoint=comfyui_url)

    logger.info(f"Vérification de l'accessibilité de ComfyUI à {comfyui_url}...")
    try:
        # Use APIManager without Auth for simple check
        response = await api_manager.call_api("comfyui", method="GET", endpoint_suffix="/system_stats", headers={}) # No auth needed typically
        if response is not None: # Check if call was successful (didn't return None)
             # We might want to check the content of response here if needed
             logger.info(f"✓ ComfyUI accessible à {comfyui_url}")
        else:
             raise Exception(f"ComfyUI non accessible ou réponse invalide")
    except Exception as e:
        logger.warning(f"✗ ComfyUI non accessible: {e}")
        logger.info("Assurez-vous que ComfyUI est en cours d'exécution et que l'URL/port est correct dans la config.")
        all_ok = False # Local generation depends on this

    return all_ok


# Modify install_external_models to accept managers
async def install_external_models(config, api_manager, model_manager, security_manager):
    """Installe et configure les modèles externes."""
    logger.info("Installation et configuration des modèles externes via les gestionnaires...")
    
    results = {
        "qwen": {"status": "unknown", "message": "Vérification non implémentée via ModelManager"},
        "gemini": {"status": "unknown", "message": "Vérification non implémentée via APIManager"},
        "wan": {"status": "unknown", "message": "Vérification non implémentée via APIManager"}
    }

    # TODO: Refactor logic to use ModelManager for listing/installing (e.g., Ollama)
    # TODO: Refactor logic to use APIManager for configuring/testing API keys (Gemini, WAN)
    # TODO: Use SecurityManager to handle API keys securely

    # Example for Gemini configuration check using APIManager (conceptual)
    gemini_api_key = security_manager.decrypt_string(config.get("api_keys_encrypted", {}).get("gemini")) or config.get("api_keys",{}).get("gemini") # Prefer encrypted
    if gemini_api_key:
        api_manager.register_api("gemini", api_key=gemini_api_key, endpoint="https://generativelanguage.googleapis.com") # Example endpoint
        logger.info("Test de l'API Gemini...")
        # Construct a simple test call payload for Gemini
        test_payload = {
             "contents": [{"parts": [{"text": "Test"}]}]
        }
        # Note: Ensure the endpoint_suffix matches the actual Gemini API endpoint for content generation
        response = await api_manager.call_api("gemini", endpoint_suffix="/v1beta/models/gemini-pro:generateContent", data=test_payload)
        if response is not None:
            logger.info("✓ API Google Gemini Studio semble configurée et fonctionnelle.")
            results["gemini"] = {"status": "configured", "message": "API testée avec succès"}
        else:
            logger.warning("✗ Test de l'API Gemini échoué. Vérifiez la clé et l'endpoint.")
            results["gemini"] = {"status": "error", "message": "Test API échoué"}
    else:
        logger.warning("✗ Clé API Google Gemini Studio non trouvée dans la configuration.")
        results["gemini"] = {"status": "not_configured", "message": "Clé API manquante"}


    # Placeholder for Qwen check (requires Ollama interaction logic, potentially via subprocess or dedicated Ollama client)
    logger.info("Vérification Qwen via Ollama (logique à implémenter dans ModelManager/APIManager)")

    # Placeholder for WAN check
    logger.info("Vérification WAN (logique à implémenter dans APIManager)")


    logger.info(f"Résultats de la vérification des modèles externes: {results}")
    return results


def initialize_components(config):
    """Initialise tous les composants de la plateforme."""
    logger.info("Initialisation des composants...")
    
    # Créer les répertoires nécessaires
    os.makedirs(config.get("temp_dir", "temp"), exist_ok=True)
    os.makedirs(os.path.dirname(config.get("output_path", "output/output.mp4")), exist_ok=True)
    
    # Initialiser les composants
    parser = StoryboardParser(config)
    style_manager = StyleManager(config)
    generator = ImageGenerator(config, style_manager)
    assembler = VideoAssembler(config)
    
    logger.info("✓ Composants initialisés avec succès")
    return parser, style_manager, generator, assembler


def start_web_interface(config):
    """Démarre l'interface web de la plateforme."""
    logger.info("Démarrage de l'interface web...")
    
    from ui.app import init_app, app
    
    # Initialiser l'application
    init_app(config)
    
    # Démarrer le serveur web
    host = config.get("web", {}).get("host", "127.0.0.1")
    port = config.get("web", {}).get("port", 5000)
    debug = config.get("web", {}).get("debug", False)
    
    logger.info(f"Interface web accessible à http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


# Modify main to be async and use managers
async def main():
    """Point d'entrée principal asynchrone pour l'application."""
    args = parse_arguments()
    
    # Setup logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    for handler in logging.getLogger().handlers:
        handler.setLevel(log_level)

    logger.info("Démarrage de la plateforme Madsea...")

    # Load configuration
    try:
        config = load_config(args.config)
        logger.info(f"Configuration chargée depuis: {args.config}")
    except FileNotFoundError:
        logger.error(f"Fichier de configuration non trouvé: {args.config}")
        return
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        return

    # Initialize managers
    logger.info("Initialisation des gestionnaires principaux...")
    try:
        # Note: SecurityManager might need password prompt if key needs derivation
        security_manager = SecurityManager(config)
        api_manager = APIManager(config)
        model_manager = ModelManager(config)
        cache_manager = CacheManager(config)
        logger.info("Gestionnaires principaux initialisés.")
    except Exception as e:
        logger.critical(f"Échec de l'initialisation des gestionnaires principaux: {e}")
        # Clean up any partially initialized managers if necessary (e.g., close sessions)
        if 'api_manager' in locals() and api_manager:
             await api_manager.close_session()
        return # Cannot proceed without managers


    # Check dependencies using managers
    if args.check_dependencies:
        if not await check_dependencies(config, api_manager):
            logger.error("Vérification des dépendances échouée. Veuillez installer les composants manquants.")
            await api_manager.close_session()
            return
        else:
             logger.info("Vérification des dépendances réussie.")
             # Optionally exit after check if only check was requested
             # await api_manager.close_session()
             # return

    # Install external models if requested using managers
    if args.install_models:
        logger.info("Installation/Configuration des modèles externes demandée...")
        await install_external_models(config, api_manager, model_manager, security_manager)
        # Optionally save updated config if keys were added/verified
        # save_config(config, args.config) # Be careful with overwriting
        # Optionally exit after install if only install was requested
        # await api_manager.close_session()
        # return

    # Start web interface if requested
    if args.web:
        logger.info("Démarrage de l'interface web...")
        try:
            from ui.app import start_web_app
            # Pass managers to the web app factory/startup function
            start_web_app(config, api_manager, model_manager, cache_manager, security_manager)
            # Note: start_web_app might block here, or run in background
            # Need to handle cleanup like closing the api_manager session appropriately
        except ImportError:
             logger.error("Module UI non trouvé. Impossible de démarrer l'interface web.")
        except Exception as e:
             logger.error(f"Erreur lors du démarrage de l'interface web: {e}")
        finally:
            # Ensure API manager session is closed when web app stops (if not handled internally)
            # This might need signal handling or a different structure if start_web_app blocks
             await api_manager.close_session()
        return # Exit after starting web app usually

    # --- CLI Workflow (if not --web) ---
    logger.info("Démarrage du flux de travail CLI...")

    # Override config with command line arguments (if applicable after manager init)
    if args.storyboard:
        config["storyboard_path"] = args.storyboard
    if args.style:
        config["style"] = args.style
    if args.output:
        config["output_path"] = args.output
    if args.use_cloud:
        config["use_cloud"] = True # This might influence which generator is chosen

    # Check if required parameters are provided for CLI mode
    if "storyboard_path" not in config or not config["storyboard_path"]:
        logger.error("Aucun chemin de storyboard fourni pour le mode CLI. Utilisez --storyboard ou spécifiez dans la config.")
        await api_manager.close_session()
        return

    # Create output directory if it doesn't exist
    output_path = Path(config.get("output_path", "output/output.mp4"))
    output_dir = output_path.parent
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Répertoire de sortie: {output_dir}")

    # Initialize components, passing managers
    logger.info("Initialisation des composants du pipeline...")
    try:
        # TODO: Update constructors of these classes to accept managers
        parser = StoryboardParser(config, cache_manager=cache_manager)
        style_manager = StyleManager(config, model_manager=model_manager, cache_manager=cache_manager)
        # Pass all relevant managers to ImageGenerator
        generator = ImageGenerator(config, style_manager, model_manager, api_manager, cache_manager)
        assembler = VideoAssembler(config, cache_manager=cache_manager)
        logger.info("Composants initialisés.")
    except Exception as e:
         logger.error(f"Erreur lors de l'initialisation des composants: {e}")
         await api_manager.close_session()
         return

    # --- Execute Pipeline ---
    generated_video_path = None
    try:
        # Process storyboard
        logger.info(f"Analyse du storyboard: {config['storyboard_path']}")
        scenes = parser.parse(config["storyboard_path"])
        if not scenes:
             logger.error("Aucune scène extraite du storyboard.")
             raise ValueError("Parsing failed")

        # Generate images for each scene
        logger.info(f"Génération des images avec le style: {config.get('style', 'default')}")
        generated_images = []
        # Use asyncio.gather for parallel generation if ImageGenerator.generate is async
        generation_tasks = []
        for i, scene in enumerate(scenes):
            logger.info(f"Préparation de la génération pour la scène {i+1}/{len(scenes)}")
            # Assuming generator.generate becomes async
            generation_tasks.append(generator.generate(scene["image"], scene["text"], scene_index=i))

        # Wait for all images to be generated
        generated_image_paths = await asyncio.gather(*generation_tasks)

        # Filter out potential None results from failed generations
        valid_image_paths = [path for path in generated_image_paths if path]
        if len(valid_image_paths) != len(scenes):
             logger.warning(f"{len(scenes) - len(valid_image_paths)} scènes n'ont pas pu être générées.")
             # Decide if we should proceed or stop

        if not valid_image_paths:
             logger.error("Aucune image n'a pu être générée.")
             raise ValueError("Image generation failed completely")

        # Assemble video
        logger.info(f"Assemblage de la vidéo: {output_path}")
        # Pass image paths, not PIL objects if generator saves files
        generated_video_path = assembler.create_video(valid_image_paths, scenes)

        logger.info(f"Vidéo créée avec succès: {generated_video_path}")

    except Exception as e:
        logger.error(f"Une erreur est survenue durant l'exécution du pipeline: {e}", exc_info=True) # Log traceback
    finally:
        # Cleanup: close API session, release models?
        logger.info("Nettoyage des ressources...")
        await api_manager.close_session()
        # Potentially release models from ModelManager if loaded directly
        # model_manager.release_all_models() # Example method

    logger.info("Script terminé.")
    return generated_video_path


if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exécution interrompue par l'utilisateur.")
    except Exception as e:
        logger.critical(f"Erreur fatale non interceptée: {e}", exc_info=True)