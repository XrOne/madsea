#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de gestion des modèles externes pour le projet Madsea

Ce module gère l'initialisation, la configuration et l'utilisation des modèles externes:
- Qwen 2.1: Modèle de génération de texte via Ollama
- Google Gemini Studio: API pour l'enrichissement des prompts
- WAN 2.1: Modèle de génération d'images de Tencent

Ces modèles sont principalement utilisés par le style Déclic Ombre Chinoise.
"""

import os
import json
import logging
import subprocess
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class ExternalModelsManager:
    """Gestionnaire des modèles externes pour le projet Madsea"""

    def __init__(self, config):
        """
        Initialise le gestionnaire de modèles externes
        
        Args:
            config (dict): Configuration du projet
        """
        self.config = config
        self.models_config = config.get("external_models", {})
        
        # État des modèles
        self.models_status = {
            "qwen": {"status": "not_configured", "message": "Non configuré"},
            "gemini": {"status": "not_configured", "message": "Non configuré"},
            "wan": {"status": "not_configured", "message": "Non configuré"}
        }
        
        # Initialiser les modèles
        self._init_models()
    
    def _init_models(self):
        """Initialise les modèles externes selon la configuration"""
        # Initialiser Qwen 2.1
        if self.models_config.get("use_qwen", True):
            self._init_qwen()
        
        # Initialiser Google Gemini Studio
        if self.models_config.get("use_gemini", True):
            self._init_gemini()
        
        # Initialiser WAN 2.1
        if self.models_config.get("use_wan", True):
            self._init_wan()
    
    def _init_qwen(self):
        """Initialise le modèle Qwen 2.1 via Ollama"""
        logger.info("Initialisation de Qwen 2.1 via Ollama...")
        
        try:
            # Vérifier si Ollama est installé et accessible
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning("Ollama n'est pas installé ou accessible")
                self.models_status["qwen"] = {
                    "status": "error",
                    "message": "Ollama non installé"
                }
                return
            
            # Vérifier si le modèle Qwen est déjà installé
            if "qwen2:1.5b" in result.stdout:
                logger.info("Modèle Qwen 2.1 déjà installé dans Ollama")
                self.models_status["qwen"] = {
                    "status": "available",
                    "message": "Prêt à l'emploi"
                }
            else:
                logger.warning("Modèle Qwen 2.1 non installé dans Ollama")
                self.models_status["qwen"] = {
                    "status": "not_installed",
                    "message": "Modèle non installé"
                }
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Qwen: {e}")
            self.models_status["qwen"] = {
                "status": "error",
                "message": str(e)
            }
    
    def _init_gemini(self):
        """Initialise l'API Google Gemini Studio"""
        logger.info("Initialisation de l'API Google Gemini Studio...")
        
        try:
            # Vérifier si la clé API est configurée
            api_key = self.models_config.get("gemini_api_key", "")
            
            if not api_key:
                logger.warning("Clé API Google Gemini Studio non configurée")
                self.models_status["gemini"] = {
                    "status": "not_configured",
                    "message": "Clé API non configurée"
                }
                return
            
            # Tester la clé API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "contents": [{
                    "parts": [{
                        "text": "Hello, Gemini!"
                    }]
                }]
            }
            
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info("API Google Gemini Studio configurée et fonctionnelle")
                self.models_status["gemini"] = {
                    "status": "configured",
                    "message": "API prête"
                }
            else:
                logger.warning(f"Erreur avec l'API Gemini: {response.status_code} - {response.text}")
                self.models_status["gemini"] = {
                    "status": "error",
                    "message": f"Erreur API: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Gemini: {e}")
            self.models_status["gemini"] = {
                "status": "error",
                "message": str(e)
            }
    
    def _init_wan(self):
        """Initialise l'API WAN 2.1 (Tencent)"""
        logger.info("Initialisation de l'API WAN 2.1 (Tencent)...")
        
        try:
            # Vérifier si la clé API est configurée
            api_key = self.models_config.get("wan_api_key", "")
            
            if not api_key:
                logger.warning("Clé API WAN 2.1 non configurée")
                self.models_status["wan"] = {
                    "status": "not_configured",
                    "message": "Clé API non configurée"
                }
                return
            
            # Pour WAN, nous ne faisons pas de test API car cela consommerait des crédits
            # Nous considérons simplement que si la clé est configurée, l'API est prête
            logger.info("API WAN 2.1 configurée")
            self.models_status["wan"] = {
                "status": "configured",
                "message": "API prête"
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de WAN: {e}")
            self.models_status["wan"] = {
                "status": "error",
                "message": str(e)
            }
    
    def install_qwen(self):
        """Installe le modèle Qwen 2.1 via Ollama"""
        logger.info("Installation du modèle Qwen 2.1...")
        
        try:
            # Vérifier si Ollama est installé
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error("Ollama n'est pas installé ou accessible")
                return {
                    "status": "error",
                    "message": "Ollama non installé"
                }
            
            # Vérifier si le modèle est déjà installé
            if "qwen2:1.5b" in result.stdout:
                logger.info("Modèle Qwen 2.1 déjà installé")
                self.models_status["qwen"] = {
                    "status": "available",
                    "message": "Déjà installé"
                }
                return self.models_status["qwen"]
            
            # Installer le modèle
            logger.info("Téléchargement et installation du modèle Qwen 2.1...")
            install_result = subprocess.run(
                ["ollama", "pull", "qwen2:1.5b"],
                capture_output=True,
                text=True
            )
            
            if install_result.returncode == 0:
                logger.info("Modèle Qwen 2.1 installé avec succès")
                self.models_status["qwen"] = {
                    "status": "available",
                    "message": "Installé avec succès"
                }
            else:
                logger.error(f"Erreur lors de l'installation: {install_result.stderr}")
                self.models_status["qwen"] = {
                    "status": "error",
                    "message": "Erreur d'installation"
                }
            
            return self.models_status["qwen"]
        except Exception as e:
            logger.error(f"Erreur lors de l'installation de Qwen: {e}")
            self.models_status["qwen"] = {
                "status": "error",
                "message": str(e)
            }
            return self.models_status["qwen"]
    
    def configure_gemini(self, api_key):
        """Configure l'API Google Gemini Studio"""
        logger.info("Configuration de l'API Google Gemini Studio...")
        
        try:
            # Mettre à jour la configuration
            if "external_models" not in self.config:
                self.config["external_models"] = {}
            
            self.config["external_models"]["gemini_api_key"] = api_key
            self.models_config["gemini_api_key"] = api_key
            
            # Tester la clé API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "contents": [{
                    "parts": [{
                        "text": "Hello, Gemini!"
                    }]
                }]
            }
            
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info("API Google Gemini Studio configurée et fonctionnelle")
                self.models_status["gemini"] = {
                    "status": "configured",
                    "message": "API configurée"
                }
            else:
                logger.warning(f"Erreur avec l'API Gemini: {response.status_code} - {response.text}")
                self.models_status["gemini"] = {
                    "status": "error",
                    "message": f"Erreur API: {response.status_code}"
                }
            
            return self.models_status["gemini"]
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de Gemini: {e}")
            self.models_status["gemini"] = {
                "status": "error",
                "message": str(e)
            }
            return self.models_status["gemini"]
    
    def configure_wan(self, api_key):
        """Configure l'API WAN 2.1 (Tencent)"""
        logger.info("Configuration de l'API WAN 2.1...")
        
        try:
            # Mettre à jour la configuration
            if "external_models" not in self.config:
                self.config["external_models"] = {}
            
            self.config["external_models"]["wan_api_key"] = api_key
            self.models_config["wan_api_key"] = api_key
            
            # Pour WAN, nous ne faisons pas de test API car cela consommerait des crédits
            logger.info("API WAN 2.1 configurée")
            self.models_status["wan"] = {
                "status": "configured",
                "message": "API configurée"
            }
            
            return self.models_status["wan"]
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de WAN: {e}")
            self.models_status["wan"] = {
                "status": "error",
                "message": str(e)
            }
            return self.models_status["wan"]
    
    def get_status(self):
        """Retourne l'état actuel des modèles externes"""
        return self.models_status
    
    def generate_text_with_qwen(self, prompt, max_tokens=512):
        """Génère du texte avec le modèle Qwen 2.1"""
        if self.models_status["qwen"]["status"] != "available":
            logger.error("Modèle Qwen 2.1 non disponible")
            return None
        
        try:
            # Préparer la requête pour Ollama
            data = {
                "model": "qwen2:1.5b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
            
            # Envoyer la requête
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Erreur lors de la génération avec Qwen: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec Qwen: {e}")
            return None
    
    def generate_text_with_gemini(self, prompt, max_tokens=512):
        """Génère du texte avec l'API Google Gemini Studio"""
        if self.models_status["gemini"]["status"] != "configured":
            logger.error("API Google Gemini Studio non configurée")
            return None
        
        try:
            # Préparer la requête pour Gemini
            api_key = self.models_config.get("gemini_api_key", "")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens
                }
            }
            
            # Envoyer la requête
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extraire le texte généré
                generated_text = ""
                for candidate in result.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        if "text" in part:
                            generated_text += part["text"]
                
                return generated_text
            else:
                logger.error(f"Erreur lors de la génération avec Gemini: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec Gemini: {e}")
            return None
    
    def generate_image_with_wan(self, prompt, negative_prompt="", width=1024, height=768):
        """Génère une image avec l'API WAN 2.1 (Tencent)"""
        if self.models_status["wan"]["status"] != "configured":
            logger.error("API WAN 2.1 non configurée")
            return None
        
        try:
            # Préparer la requête pour WAN
            api_key = self.models_config.get("wan_api_key", "")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_images": 1,
                "guidance_scale": 7.5
            }
            
            # Envoyer la requête
            response = requests.post(
                "https://api.tencent.com/wan/v1/images/generations",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extraire l'URL de l'image générée
                if "data" in result and len(result["data"]) > 0:
                    return result["data"][0].get("url", None)
                return None
            else:
                logger.error(f"Erreur lors de la génération avec WAN: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec WAN: {e}")
            return None


# Fonction pour installer et configurer tous les modèles externes
def setup_external_models(config, install_qwen=True, configure_gemini=True, configure_wan=True):
    """Configure et installe tous les modèles externes"""
    manager = ExternalModelsManager(config)
    results = {
        "qwen": {"status": "not_configured", "message": "Non configuré"},
        "gemini": {"status": "not_configured", "message": "Non configuré"},
        "wan": {"status": "not_configured", "message": "Non configuré"}
    }
    
    # Installer Qwen si demandé
    if install_qwen:
        results["qwen"] = manager.install_qwen()
    
    # Configurer Gemini si demandé
    if configure_gemini:
        api_key = config.get("external_models", {}).get("gemini_api_key", "")
        if api_key:
            results["gemini"] = manager.configure_gemini(api_key)
        else:
            logger.warning("Clé API Google Gemini Studio non configurée")
    
    # Configurer WAN si demandé
    if configure_wan:
        api_key = config.get("external_models", {}).get("wan_api_key", "")
        if api_key:
            results["wan"] = manager.configure_wan(api_key)
        else:
            logger.warning("Clé API WAN 2.1 non configurée")
    
    return results