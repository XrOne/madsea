import asyncio
from typing import Optional, Dict, Any
import requests
import time
import os
import json
import logging
import base64
from pathlib import Path

# MCP Puppeteer client (Windsurf)
from functions import mcp4_puppeteer_navigate, mcp4_puppeteer_click, mcp4_puppeteer_fill, mcp4_puppeteer_screenshot, mcp4_puppeteer_evaluate

# Configuration
COMFYUI_URL = "http://localhost:8188/"
COMFYUI_API_URL = "http://localhost:8188/prompt"
COMFYUI_UPLOAD_URL = "http://localhost:8188/upload/image"
COMFYUI_WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ComfyUI', 'workflows')
DEFAULT_WORKFLOW = "Madsea_OmbresChiCX.json"

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("comfyui_puppeteer")

async def upload_image_comfyui(input_path: str) -> Dict[str, Any]:
    """
    Charge une image dans ComfyUI via l'interface utilisateur
    Retourne un dict avec status et file_id en cas de succès
    """
    try:
        # Extraire le nom de fichier depuis le chemin
        filename = os.path.basename(input_path)
        logger.info(f"Tentative d'upload de l'image: {filename}")
        
        # 1. Cliquer sur le bouton d'upload (sélecteur UI ComfyUI)
        upload_button = await mcp4_puppeteer_evaluate({
            "script": """
            // Trouver le bouton d'upload dans l'UI ComfyUI
            const uploadButton = Array.from(document.querySelectorAll('button'))
                .find(el => el.textContent.includes('Load'));
            if (uploadButton) uploadButton.click();
            return !!uploadButton;
            """
        })
        
        if not upload_button.get("result"):
            raise Exception("Bouton d'upload non trouvé dans l'UI ComfyUI")
        
        time.sleep(1)
        
        # 2. Simuler l'upload via l'API REST (plus fiable que l'UI)
        with open(input_path, 'rb') as img_file:
            files = {'image': (filename, img_file, 'image/png')}
            response = requests.post(COMFYUI_UPLOAD_URL, files=files)
            
        if response.status_code != 200:
            raise Exception(f"Échec de l'upload via API REST: {response.status_code}")
            
        result = response.json()
        logger.info(f"Image uploadée avec succès, ID: {result.get('name', 'inconnu')}")
        
        # 3. Prendre un screenshot pour confirmation
        screenshot = await mcp4_puppeteer_screenshot({"name": "upload_complete", "storeBase64": True})
        
        return {
            "status": "success", 
            "file_id": result.get('name', ''),
            "screenshot": screenshot.get("base64", "")
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de l'image: {str(e)}")
        screenshot = await mcp4_puppeteer_screenshot({"name": "upload_error", "storeBase64": True})
        return {
            "status": "error", 
            "message": str(e),
            "screenshot": screenshot.get("base64", "")
        }

async def load_workflow(workflow_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Charge un workflow dans ComfyUI via l'interface utilisateur
    Retourne un dict avec status et workflow_data en cas de succès
    """
    try:
        workflow_file = workflow_name or DEFAULT_WORKFLOW
        workflow_path = os.path.join(COMFYUI_WORKFLOWS_DIR, workflow_file)
        logger.info(f"Chargement du workflow: {workflow_path}")
        
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow non trouvé: {workflow_path}")
        
        # 1. Lire le contenu du workflow
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
            
        # 2. Injecter le workflow via l'évaluation JavaScript
        load_result = await mcp4_puppeteer_evaluate({
            "script": f"""
            // Charger le workflow via l'API ComfyUI
            const workflowData = {json.dumps(workflow_data)};
            try {{
                // Méthode standard pour charger un workflow dans ComfyUI
                app.loadGraphData(workflowData);
                return {{success: true}};
            }} catch (error) {{
                return {{success: false, error: error.toString()}};
            }}
            """
        })
        
        result = load_result.get("result", {})
        if not result.get("success", False):
            raise Exception(f"Échec du chargement du workflow: {result.get('error', 'erreur inconnue')}")
        
        logger.info(f"Workflow chargé avec succès: {workflow_file}")
        
        # 3. Prendre un screenshot pour confirmation
        screenshot = await mcp4_puppeteer_screenshot({"name": "workflow_loaded", "storeBase64": True})
        
        return {
            "status": "success",
            "workflow": workflow_file,
            "screenshot": screenshot.get("base64", "")
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement du workflow: {str(e)}")
        screenshot = await mcp4_puppeteer_screenshot({"name": "workflow_error", "storeBase64": True})
        return {
            "status": "error", 
            "message": str(e),
            "screenshot": screenshot.get("base64", "")
        }

async def generate_image() -> Dict[str, Any]:
    """
    Déclenche la génération d'image dans ComfyUI
    Retourne un dict avec status et prompt_id en cas de succès
    """
    try:
        logger.info("Déclenchement de la génération ComfyUI")
        
        # 1. Cliquer sur le bouton Generate
        generate_click = await mcp4_puppeteer_evaluate({
            "script": """
            // Trouver et cliquer sur le bouton Generate
            const generateButton = Array.from(document.querySelectorAll('button'))
                .find(el => el.textContent.includes('Generate') || el.textContent.includes('Queue Prompt'));
            if (generateButton) {
                generateButton.click();
                return {success: true};
            }
            return {success: false, error: 'Bouton Generate non trouvé'};
            """
        })
        
        result = generate_click.get("result", {})
        if not result.get("success", False):
            raise Exception(f"Échec du clic sur Generate: {result.get('error', 'erreur inconnue')}")
        
        # 2. Attendre et vérifier si la génération est en cours
        time.sleep(2)  # Court délai pour laisser le temps à l'UI de réagir
        
        # 3. Prendre un screenshot pour confirmation
        screenshot = await mcp4_puppeteer_screenshot({"name": "generation_started", "storeBase64": True})
        
        # 4. Récupérer l'ID de prompt via JavaScript
        prompt_info = await mcp4_puppeteer_evaluate({
            "script": """
            // Tenter de récupérer l'ID du prompt en cours
            try {
                // Cette méthode peut varier selon la version de ComfyUI
                const promptId = app.lastPromptId || document.querySelector('.comfy-prompt-id')?.textContent;
                return {success: true, promptId: promptId || 'inconnu'};
            } catch (error) {
                return {success: false, error: error.toString()};
            }
            """
        })
        
        prompt_id = prompt_info.get("result", {}).get("promptId", "inconnu")
        logger.info(f"Génération démarrée, Prompt ID: {prompt_id}")
        
        return {
            "status": "success",
            "prompt_id": prompt_id,
            "screenshot": screenshot.get("base64", "")
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du déclenchement de la génération: {str(e)}")
        screenshot = await mcp4_puppeteer_screenshot({"name": "generation_error", "storeBase64": True})
        return {
            "status": "error", 
            "message": str(e),
            "screenshot": screenshot.get("base64", "")
        }

async def wait_for_result(timeout: int = 120) -> Dict[str, Any]:
    """
    Attend que la génération se termine et récupère le résultat
    Retourne un dict avec status et output_file en cas de succès
    """
    try:
        logger.info(f"Attente du résultat (timeout: {timeout}s)")
        start_time = time.time()
        result_found = False
        output_filename = ""
        
        # Boucle d'attente avec vérification périodique
        while (time.time() - start_time) < timeout and not result_found:
            # Vérifier si la génération est terminée
            status_check = await mcp4_puppeteer_evaluate({
                "script": """
                // Vérifier si la génération est terminée (image visible)
                const imageElements = document.querySelectorAll('img.comfy-preview-image, .comfy-image-preview img');
                const latestImages = Array.from(imageElements).filter(img => 
                    img.src && img.src.includes('view?filename=') && img.complete
                );
                
                if (latestImages.length > 0) {
                    // Prendre la dernière image générée
                    const latestImage = latestImages[latestImages.length - 1];
                    // Extraire le nom du fichier depuis l'URL
                    const url = new URL(latestImage.src);
                    const filename = url.searchParams.get('filename');
                    return {success: true, filename: filename || '', complete: true};
                }
                
                // Vérifier si une erreur est affichée
                const errorElement = document.querySelector('.comfy-error-message');
                if (errorElement && errorElement.textContent) {
                    return {success: false, error: errorElement.textContent, complete: true};
                }
                
                // Génération encore en cours
                return {success: true, complete: false};
                """
            })
            
            result = status_check.get("result", {})
            
            # Génération terminée avec succès et image disponible
            if result.get("complete", False) and result.get("success", False):
                output_filename = result.get("filename", "")
                if output_filename:
                    result_found = True
                    break
            # Erreur détectée
            elif result.get("complete", False) and not result.get("success", False):
                raise Exception(f"Erreur de génération: {result.get('error', 'erreur inconnue')}")
            
            # Attendre avant la prochaine vérification
            await asyncio.sleep(2)  # Non-bloquant
            
        if not result_found:
            raise TimeoutError(f"Timeout après {timeout}s d'attente")
        
        # Prendre un screenshot final
        screenshot = await mcp4_puppeteer_screenshot({"name": "generation_complete", "storeBase64": True})
        
        logger.info(f"Génération terminée, fichier de sortie: {output_filename}")
        return {
            "status": "success",
            "output_file": output_filename,
            "screenshot": screenshot.get("base64", "")
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'attente du résultat: {str(e)}")
        screenshot = await mcp4_puppeteer_screenshot({"name": "wait_result_error", "storeBase64": True})
        return {
            "status": "error", 
            "message": str(e),
            "screenshot": screenshot.get("base64", "")
        }

async def save_result_to_path(output_file: str, target_path: str) -> Dict[str, Any]:
    """
    Télécharge et sauvegarde le résultat à l'emplacement spécifié
    """
    try:
        if not output_file:
            raise ValueError("Nom de fichier de sortie manquant")
            
        # 1. Construire l'URL pour télécharger l'image
        download_url = f"{COMFYUI_URL}view?filename={output_file}&subfolder=output"
        logger.info(f"Téléchargement de l'image: {download_url}")
        
        # 2. Télécharger le fichier
        response = requests.get(download_url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Échec du téléchargement: {response.status_code}")
            
        # 3. Assurer que le répertoire cible existe
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
        # 4. Sauvegarder le fichier à l'emplacement demandé
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Image sauvegardée avec succès: {target_path}")
        return {
            "status": "success",
            "output_path": target_path
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du résultat: {str(e)}")
        return {
            "status": "error", 
            "message": str(e)
        }

async def upload_style_reference(style_path: str) -> Dict[str, Any]:
    """
    Charge une image de référence de style dans ComfyUI
    Retourne un dict avec status et file_id en cas de succès
    """
    try:
        filename = os.path.basename(style_path)
        logger.info(f"Upload de l'image de référence de style: {filename}")
        
        # Utiliser l'API REST directement (plus fiable pour un second upload)
        with open(style_path, 'rb') as img_file:
            files = {'image': (filename, img_file, 'image/png')}
            response = requests.post(COMFYUI_UPLOAD_URL, files=files)
            
        if response.status_code != 200:
            raise Exception(f"Échec de l'upload de l'image de référence: {response.status_code}")
            
        result = response.json()
        style_file_id = result.get('name', '')
        logger.info(f"Image de style uploadée avec succès, ID: {style_file_id}")
        
        # Prendre un screenshot pour confirmation
        screenshot = await mcp4_puppeteer_screenshot({"name": "style_uploaded", "storeBase64": True})
        
        return {
            "status": "success", 
            "file_id": style_file_id,
            "screenshot": screenshot.get("base64", "")
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de l'image de style: {str(e)}")
        return {
            "status": "error", 
            "message": str(e)
        }

async def adapt_workflow_for_style_reference(workflow_data: Dict, input_file_id: str, style_file_id: str) -> Dict:
    """
    Modifie le workflow ComfyUI pour utiliser l'image de référence comme guide de style
    """
    try:
        logger.info("Adaptation du workflow pour utiliser l'image de référence de style")
        
        # Trouver les nœuds clés dans le workflow
        input_node_id = None
        style_node_id = None
        
        # Parcourir tous les nœuds du workflow
        for node_id, node in workflow_data.items():
            # Identifier les nœuds d'entrée d'image par leur classe et titre
            if node.get('class_type') == 'LoadImage':
                if 'input' in node.get('title', '').lower() or input_node_id is None:
                    input_node_id = node_id
                elif 'style' in node.get('title', '').lower() or style_node_id is None:
                    style_node_id = node_id
        
        # Si aucun nœud de style n'est trouvé, chercher un second nœud LoadImage
        if style_node_id is None:
            for node_id, node in workflow_data.items():
                if node.get('class_type') == 'LoadImage' and node_id != input_node_id:
                    style_node_id = node_id
                    break
        
        # Si nous avons identifié les deux nœuds, mettre à jour les IDs de fichiers
        if input_node_id is not None:
            workflow_data[input_node_id]['inputs']['image'] = input_file_id
            logger.info(f"Nœud d'entrée mis à jour avec l'ID: {input_file_id}")
        
        # Si nous avons un nœud de style et une image de style, mettre à jour
        if style_node_id is not None and style_file_id:
            workflow_data[style_node_id]['inputs']['image'] = style_file_id
            logger.info(f"Nœud de style mis à jour avec l'ID: {style_file_id}")
        
        # Si nous n'avons pas de nœud de style mais une image de style,
        # nous pourrions créer dynamiquement un nœud de référence de style
        # et l'injecter dans le workflow - à implémenter selon le type de workflow
        
        return workflow_data
        
    except Exception as e:
        logger.error(f"Erreur lors de l'adaptation du workflow pour le style: {str(e)}")
        # Retourner le workflow original en cas d'erreur
        return workflow_data

async def run_comfyui_workflow(input_path: str, output_path: str, workflow_name: Optional[str] = None, style_reference_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Pilote ComfyUI via Puppeteer MCP pour automatiser un workflow complet.
    - input_path: chemin du fichier image ou input à traiter
    - output_path: où sauvegarder le résultat généré
    - workflow_name: nom du workflow à charger (optionnel)
    Retourne un dict avec le statut et le chemin du résultat.
    """
    try:
        logger.info(f"Démarrage du workflow automatisé ComfyUI")
        logs = ["Démarrage du workflow automatisé"]
        screenshots = {}
        result_data = {}
        
        # 1. Ouvrir l'UI ComfyUI
        logger.info(f"Ouverture de l'UI ComfyUI: {COMFYUI_URL}")
        logs.append(f"Ouverture de l'UI ComfyUI")
        nav_result = await mcp4_puppeteer_navigate({"url": COMFYUI_URL})
        await asyncio.sleep(2)  # Laisser le temps à l'UI de charger complètement
        
        # 2. Charger le workflow
        logs.append(f"Chargement du workflow: {workflow_name or DEFAULT_WORKFLOW}")
        workflow_result = await load_workflow(workflow_name)
        if workflow_result["status"] == "error":
            logs.append(f"Erreur de chargement du workflow: {workflow_result['message']}")
            return {
                "status": "error",
                "message": workflow_result["message"],
                "logs": logs,
                "screenshots": {"workflow_error": workflow_result.get("screenshot", "")}
            }
        
        screenshots["workflow_loaded"] = workflow_result.get("screenshot", "")
        
        # 2b. Si nous avons un workflow chargé et une référence de style, adapter le workflow
        # Récupérer les données du workflow depuis JavaScript pour adaptation
        if style_reference_path:
            logs.append("Récupération des données du workflow pour adaptation au style de référence")
            workflow_data_result = await mcp4_puppeteer_evaluate({
                "script": """
                // Récupérer les données du workflow actuel
                try {
                    const workflowData = app.graph.serialize();
                    return {success: true, workflow: workflowData};
                } catch (error) {
                    return {success: false, error: error.toString()};
                }
                """
            })
            
            if workflow_data_result.get("result", {}).get("success", False):
                workflow_data = workflow_data_result.get("result", {}).get("workflow", {})
                logs.append("Workflow récupéré avec succès pour adaptation")
                
                # On attend que les deux uploads (principal et style) soient terminés
                if result_data.get("file_id") and result_data.get("style_file_id"):
                    logs.append("Adaptation du workflow pour intégrer l'image de référence de style")
                    # Adapter le workflow avec les deux IDs d'images
                    adapted_workflow = await adapt_workflow_for_style_reference(
                        workflow_data, 
                        result_data["file_id"], 
                        result_data["style_file_id"]
                    )
                    
                    # Recharger le workflow adapté
                    inject_result = await mcp4_puppeteer_evaluate({
                        "script": f"""
                        // Injecter le workflow adapté
                        try {{
                            const adaptedWorkflow = {json.dumps(adapted_workflow)};
                            app.loadGraphData(adaptedWorkflow);
                            return {{success: true}};
                        }} catch (error) {{
                            return {{success: false, error: error.toString()}};
                        }}
                        """
                    })
                    
                    if inject_result.get("result", {}).get("success", False):
                        logs.append("Workflow adapté avec succès pour utiliser l'image de référence de style")
                        screenshots["workflow_adapted"] = await mcp4_puppeteer_screenshot({"name": "workflow_adapted", "storeBase64": True})
                    else:
                        error_msg = inject_result.get("result", {}).get("error", "erreur inconnue")
                        logs.append(f"Avertissement: Erreur lors de l'injection du workflow adapté: {error_msg}")
                        logs.append("Continuation avec le workflow standard")
                else:
                    logs.append("Adaptation du workflow impossible - IDs d'images manquants")
            else:
                error_msg = workflow_data_result.get("result", {}).get("error", "erreur inconnue")
                logs.append(f"Avertissement: Erreur lors de la récupération des données du workflow: {error_msg}")
                logs.append("Continuation avec le workflow standard sans adaptation de style")
        
        # 3. Uploader l'image principale
        logs.append(f"Upload de l'image d'entrée: {input_path}")
        upload_result = await upload_image_comfyui(input_path)
        if upload_result["status"] == "error":
            logs.append(f"Erreur d'upload: {upload_result['message']}")
            return {
                "status": "error",
                "message": upload_result["message"],
                "logs": logs,
                "screenshots": {**screenshots, "upload_error": upload_result.get("screenshot", "")}
            }
        
        screenshots["upload_complete"] = upload_result.get("screenshot", "")
        result_data["file_id"] = upload_result.get("file_id", "")
        
        # 3b. Uploader l'image de référence de style si fournie
        style_file_id = None
        if style_reference_path and os.path.exists(style_reference_path):
            logs.append(f"Upload de l'image de référence de style: {style_reference_path}")
            style_upload_result = await upload_style_reference(style_reference_path)
            if style_upload_result["status"] == "error":
                logs.append(f"Attention - Erreur d'upload du style: {style_upload_result.get('message', 'erreur inconnue')}")
                logs.append("Continuation avec l'image principale uniquement.")
            else:
                style_file_id = style_upload_result.get("file_id", "")
                screenshots["style_upload_complete"] = style_upload_result.get("screenshot", "")
                logs.append(f"Image de style uploadée avec succès (ID: {style_file_id})")
                result_data["style_file_id"] = style_file_id
        
        # 4. Déclencher la génération
        logs.append(f"Déclenchement de la génération")
        generate_result = await generate_image()
        if generate_result["status"] == "error":
            logs.append(f"Erreur de génération: {generate_result['message']}")
            return {
                "status": "error",
                "message": generate_result["message"],
                "logs": logs,
                "screenshots": {**screenshots, "generate_error": generate_result.get("screenshot", "")}
            }
        
        screenshots["generation_started"] = generate_result.get("screenshot", "")
        result_data["prompt_id"] = generate_result.get("prompt_id", "")
        
        # 5. Attendre le résultat
        logs.append(f"En attente du résultat...")
        wait_result = await wait_for_result(timeout=180)  # 3 minutes maximum d'attente
        if wait_result["status"] == "error":
            logs.append(f"Erreur d'attente du résultat: {wait_result['message']}")
            return {
                "status": "error",
                "message": wait_result["message"],
                "logs": logs,
                "screenshots": {**screenshots, "wait_error": wait_result.get("screenshot", "")}
            }
        
        screenshots["generation_complete"] = wait_result.get("screenshot", "")
        result_data["output_file"] = wait_result.get("output_file", "")
        
        # 6. Sauvegarder le résultat dans le chemin spécifié
        output_file = result_data["output_file"]
        logs.append(f"Sauvegarde du résultat: {output_file} -> {output_path}")
        save_result = await save_result_to_path(output_file, output_path)
        if save_result["status"] == "error":
            logs.append(f"Erreur de sauvegarde: {save_result['message']}")
            return {
                "status": "error",
                "message": save_result["message"],
                "logs": logs,
                "screenshots": screenshots
            }
        
        # 7. Workflow complet avec succès
        logs.append(f"Workflow terminé avec succès. Résultat sauvegardé: {output_path}")
        return {
            "status": "success",
            "message": "Workflow ComfyUI automatisé terminé avec succès",
            "output_path": output_path,
            "logs": logs,
            "screenshots": screenshots,
            **result_data
        }
    except Exception as e:
        logger.error(f"Erreur globale dans le workflow automatisé: {str(e)}")
        try:
            # Tenter de prendre un screenshot final en cas d'erreur
            error_screenshot = await mcp4_puppeteer_screenshot({"name": "global_error", "storeBase64": True})
            screenshot_data = error_screenshot.get("base64", "")
        except:
            screenshot_data = ""
            
        return {
            "status": "error", 
            "message": f"Erreur globale: {str(e)}",
            "logs": [f"Démarrage du workflow", f"Erreur: {str(e)}"],
            "screenshots": {"global_error": screenshot_data}
        }

# Pour usage backend :
# import asyncio
# result = asyncio.run(run_comfyui_workflow(input_path, output_path))

# Fonction utilitaire pour exécuter le workflow de manière synchrone (pour Flask)
def run_comfyui_workflow_sync(input_path: str, output_path: str, workflow_name: Optional[str] = None, style_reference_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Version synchrone pour l'intégration dans Flask/FastAPI
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_comfyui_workflow(input_path, output_path, workflow_name))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Erreur dans run_comfyui_workflow_sync: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur d'exécution synchrone: {str(e)}",
            "logs": [f"Erreur d'exécution synchrone: {str(e)}"],
        }
