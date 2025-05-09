import os
import sys
import json
import requests
import base64
from PIL import Image
import io
import time
from typing import Dict, List, Optional, Tuple, Union, Any

class ComfyUIService:
    """
    Service d'intégration avec ComfyUI pour Madsea
    Permet de générer des images stylisées à partir d'un storyboard
    """
    
    def __init__(self, comfyui_url: str = "http://127.0.0.1:8188"):
        """
        Initialise le service ComfyUI avec l'URL du serveur
        
        Args:
            comfyui_url: URL du serveur ComfyUI
        """
        self.comfyui_url = comfyui_url
        self.client_id = self._get_client_id()
        self.workflows_dir = os.path.join(os.path.dirname(__file__), "workflows")
        
        # Styles disponibles et fichiers de workflow associés
        self.available_styles = {
            "ombre_chinoise": "workflow_ombre_chinoise.json",
            "laboratoire": "workflow_laboratoire.json",
            "expressionniste": "workflow_expressionniste.json",
            "custom": "workflow_custom.json"
        }
        
        # Configuration spécifique pour Puppeteer
        self.puppeteer_config = {
            "ombre_chinoise": {
                "workflow": "Madsea_OmbresChiCX.json",
                "params": {
                    "controlnet_strength": 0.8,
                    "denoise": 0.4
                }
            }
        }
    
    def _get_client_id(self) -> str:
        """Génère un ID client unique pour les requêtes ComfyUI"""
        return f"madsea_{int(time.time() * 1000)}"
        
    def _create_default_workflow(self) -> Dict[str, Any]:
        """
        Crée un workflow par défaut avec ControlNet pour préserver la composition
        et le style ombre chinoise
        """
        return {
            "3": {
                "inputs": {
                    "seed": 123456789,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 0.8,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "v1-5-pruned-emaonly.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": "ombre chinoise, style silhouette, déclic, simple, minimal",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "mauvaise qualité, flou, surexposé, surchargé, confus",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "madsea_generated",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
    
    def check_status(self) -> Dict[str, Any]:
        """Vérifie le statut de ComfyUI"""
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats")
            if response.status_code == 200:
                return {
                    "status": "online",
                    "data": response.json()
                }
            return {"status": "error", "message": f"Status code: {response.status_code}"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    def load_workflow(self, style: str) -> Dict[str, Any]:
        """
        Charge un workflow ComfyUI basé sur le style sélectionné
        
        Args:
            style: Nom du style (ombre_chinoise, laboratoire, expressionniste, custom)
            
        Returns:
            Workflow JSON chargé
        """
        if style not in self.available_styles:
            raise ValueError(f"Style {style} non disponible. Styles valides: {list(self.available_styles.keys())}")
        
        workflow_path = os.path.join(self.workflows_dir, self.available_styles[style])
        
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        return workflow_data
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode une image en base64 pour ComfyUI
        
        Args:
            image_path: Chemin vers le fichier image
            
        Returns:
            Image encodée en base64
        """
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    
    def _prepare_input_nodes(self, workflow: Dict[str, Any], 
                            image_path: str, 
                            prompt: str,
                            negative_prompt: str = "",
                            controlnet_weight: float = 1.0) -> Dict[str, Any]:
        """
        Prépare les nœuds d'entrée du workflow avec les paramètres spécifiques
        
        Args:
            workflow: Workflow ComfyUI
            image_path: Chemin de l'image source
            prompt: Prompt de génération
            negative_prompt: Prompt négatif
            controlnet_weight: Poids du ControlNet
            
        Returns:
            Workflow modifié avec les entrées mises à jour
        """
        # Copier le workflow pour éviter de modifier l'original
        workflow_modified = workflow.copy()
        
        # Encoder l'image en base64
        image_b64 = self._encode_image_to_base64(image_path)
        
        # Mettre à jour les nœuds (à adapter selon la structure du workflow)
        for node_id, node in workflow_modified["nodes"].items():
            # Mise à jour du nœud d'image source (Load Image)
            if node["type"] == "LoadImage":
                node["inputs"]["image"] = image_b64
            
            # Mise à jour du nœud de prompt texte (CLIPTextEncode)
            elif node["type"] == "CLIPTextEncode" and "positive" in node["title"].lower():
                node["inputs"]["text"] = prompt
                
            # Mise à jour du nœud de prompt négatif
            elif node["type"] == "CLIPTextEncode" and "negative" in node["title"].lower():
                node["inputs"]["text"] = negative_prompt
            
            # Mise à jour du poids ControlNet
            elif node["type"] == "ControlNetApply":
                node["inputs"]["strength"] = controlnet_weight
        
        return workflow_modified
    
    def generate_with_puppeteer(self, image_path: str, prompt: str, negative_prompt: str = "", lora_strength: float = 0.8) -> dict:
        """
        Exécution réelle du workflow ComfyUI via MCP Puppeteer (one-click automation)
        Utilise RealVisXL_V5.0_fp16 et LoRA silhouette
        """
        url = "http://localhost:8188/mcp/puppeteer/run"
        payload = {
            "checkpoint": "RealVisXL_V5.0_fp16.safetensors",
            "lora": [
                {"name": "Shadow_Style_XL.safetensors", "strength": lora_strength}
            ],
            "controlnet": "control_v11p_sd15_canny_fp16.safetensors",
            "image_path": image_path,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": 28,
            "cfg": 7.0,
            "sampler": "dpmpp_2m_sde_gpu"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return {"status": "success", "result": response.json()}
            else:
                return {"status": "error", "message": f"Erreur MCP Puppeteer: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_image(self, 
                      image_path: str,
                      output_dir: str,
                      style: str,
                      prompt: str = "",
                      negative_prompt: str = "",
                      controlnet_weight: float = 1.0) -> str:
        """
        Génère une image stylisée à partir d'un storyboard
        
        Args:
            image_path: Chemin de l'image source
            output_dir: Répertoire de sortie pour l'image générée
            style: Nom du style (ombre_chinoise, laboratoire, expressionniste, custom)
            prompt: Prompt de génération (optionnel)
            negative_prompt: Prompt négatif (optionnel)
            controlnet_weight: Poids du ControlNet (optionnel)
            
        Returns:
            Chemin de l'image générée
        """
        # Charger le workflow correspondant au style sélectionné
        workflow = self.load_workflow(style)
        
        # Préparer les nœuds d'entrée du workflow
        workflow = self._prepare_input_nodes(workflow, image_path, prompt, negative_prompt, controlnet_weight)
        
        # Exécuter le workflow et récupérer l'image générée
        try:
            response = requests.post(f"{self.comfyui_url}/run_workflow", json=workflow)
            if response.status_code == 200:
                image_data = response.json()["image"]
                image_b64 = image_data["image"]
                image_bytes = base64.b64decode(image_b64)
                
                # Sauvegarder l'image générée
                output_path = os.path.join(output_dir, f"{style}_{int(time.time() * 1000)}.png")
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                
                return output_path
            else:
                raise Exception(f"Erreur lors de la génération de l'image : {response.status_code}")
        except Exception as e:
            raise Exception(f"Erreur lors de la génération de l'image : {str(e)}")