"""
Module de gestion OCR pour Madsea
--------------------------------
Gestionnaire centralisé pour l'OCR avec Tesseract.
Ce module permet de:
1. Localiser Tesseract de manière dynamique
2. Embarquer Tesseract si nécessaire
3. Fournir une API unifiée pour l'OCR de texte et d'images
"""

import os
import json
import logging
import subprocess
import pytesseract
from pathlib import Path
from flask import current_app
import shutil
from typing import Optional, List, Dict, Any, Union

logger = logging.getLogger(__name__)

class OCRManager:
    """Gestionnaire OCR centralisé pour Madsea"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le gestionnaire OCR
        
        Args:
            config_path: Chemin vers le fichier de configuration OCR
        """
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                       'config', 'ocr_config.json')
        self.config = self._load_config()
        self.tesseract_path = self._find_tesseract()
        self._configure_tesseract()
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration OCR depuis un fichier JSON"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Fichier de configuration OCR non trouvé: {self.config_path}. Utilisation config par défaut.")
                return {
                    "tesseract_paths": [
                        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                        "%MADSEA_HOME%\\ocr\\tesseract.exe"
                    ],
                    "embedded_mode": False,
                    "languages": ["fra", "eng"],
                    "default_lang": "fra"
                }
        except Exception as e:
            logger.error(f"Erreur chargement config OCR: {e}")
            return {
                "tesseract_paths": ["C:\\Program Files\\Tesseract-OCR\\tesseract.exe"],
                "embedded_mode": False,
                "languages": ["fra", "eng"],
                "default_lang": "fra"
            }
    
    def _expand_env_vars(self, path: str) -> str:
        """Remplace les variables d'environnement dans un chemin"""
        # Support pour %MADSEA_HOME%
        if '%MADSEA_HOME%' in path:
            madsea_home = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            return path.replace('%MADSEA_HOME%', madsea_home)
        return os.path.expandvars(path)  # Gère %APPDATA%, etc.
    
    def _find_tesseract(self) -> str:
        """
        Recherche dynamique de Tesseract à partir de la liste de chemins configurés
        """
        for path in self.config.get("tesseract_paths", []):
            expanded_path = self._expand_env_vars(path)
            if os.path.exists(expanded_path):
                logger.info(f"Tesseract trouvé à: {expanded_path}")
                return expanded_path
        
        # Si on est en mode app Flask, regarder dans la config
        try:
            if current_app and 'TESSERACT_PATH' in current_app.config:
                path = current_app.config['TESSERACT_PATH']
                if os.path.exists(path):
                    return path
        except Exception:
            pass
        
        # Essayer de trouver Tesseract dans le PATH
        try:
            from shutil import which
            system_path = which('tesseract')
            if system_path:
                logger.info(f"Tesseract trouvé dans le PATH: {system_path}")
                return system_path
        except Exception as e:
            logger.warning(f"Erreur recherche Tesseract dans PATH: {e}")
        
        # Fallback: retourner le premier chemin même s'il n'existe pas
        default_path = self._expand_env_vars(self.config["tesseract_paths"][0])
        logger.warning(f"Tesseract non trouvé, utilisation du chemin par défaut: {default_path}")
        return default_path
    
    def _configure_tesseract(self):
        """Configure pytesseract avec le chemin trouvé"""
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        
    def get_tesseract_info(self) -> Dict[str, str]:
        """
        Retourne les informations sur l'installation Tesseract
        
        Returns:
            Dict avec version, chemin, et status
        """
        info = {
            "path": self.tesseract_path,
            "exists": os.path.exists(self.tesseract_path),
            "version": "Inconnu",
            "status": "Non disponible"
        }
        
        try:
            if info["exists"]:
                version = pytesseract.get_tesseract_version()
                info["version"] = str(version)
                info["status"] = "Disponible"
        except Exception as e:
            logger.error(f"Erreur obtention version Tesseract: {e}")
            info["status"] = f"Erreur: {str(e)}"
        
        return info
    
    def perform_ocr(self, image_path: str, lang: str = None) -> str:
        """
        Effectue la reconnaissance OCR sur une image
        
        Args:
            image_path: Chemin vers l'image
            lang: Code de langue (par défaut utilise config)
            
        Returns:
            Texte extrait
        """
        if not os.path.exists(image_path):
            logger.error(f"Image inexistante: {image_path}")
            return ""
        
        if not lang:
            # Utiliser la langue par défaut ou les langues configurées
            if "languages" in self.config and self.config["languages"]:
                lang = "+".join(self.config["languages"])
            else:
                lang = self.config.get("default_lang", "fra")
        
        try:
            custom_config = self.config.get("options", {}).get("config", "")
            dpi = self.config.get("options", {}).get("dpi", 300)
            
            logger.info(f"OCR sur {image_path} avec lang={lang}, dpi={dpi}")
            text = pytesseract.image_to_string(
                image_path, 
                lang=lang,
                config=custom_config
            )
            return text
        except Exception as e:
            logger.error(f"Erreur OCR: {e}")
            return ""

# Instance globale du gestionnaire OCR
ocr_manager = OCRManager()

def get_ocr_manager() -> OCRManager:
    """
    Fonction utilitaire pour accéder au gestionnaire OCR
    
    Returns:
        Instance du gestionnaire OCR
    """
    return ocr_manager

def extract_text_from_image(image_path: str, lang: str = None) -> str:
    """
    API simplifiée pour l'extraction de texte depuis une image
    
    Args:
        image_path: Chemin vers l'image
        lang: Code de langue (par défaut utilise config)
        
    Returns:
        Texte extrait
    """
    return ocr_manager.perform_ocr(image_path, lang)