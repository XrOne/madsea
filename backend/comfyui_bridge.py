import requests
import json
import uuid
import os
import shutil
from urllib.parse import urlparse

COMFYUI_API_URL = "http://127.0.0.1:8188/prompt"
COMFYUI_UPLOAD_URL = "http://127.0.0.1:8188/upload/image"

# Chemin vers le template de workflow ComfyUI
# S'assurer que ce chemin est correct par rapport à l'emplacement de comfyui_bridge.py
WORKFLOW_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'ComfyUI', 'workflows', 'Windsurf_Template.json')

# Configuration de base pour la nomenclature
# Ces valeurs seraient normalement passées en paramètres ou récupérées du contexte du projet
BASE_PROJECT_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'projects')

def rename_ai_concept_placeholder(original_placeholder_path, new_sequence_number, plan_data):
    """
    Renomme le fichier placeholder AI-concept si le numéro de séquence a changé.
    Met à jour plan_data avec les nouveaux noms/chemins.
    Retourne le nouveau chemin relatif du placeholder et le nouveau nom de fichier.
    """
    if not os.path.exists(original_placeholder_path):
        print(f"Avertissement: Placeholder original non trouvé à {original_placeholder_path}")
        # Créer un placeholder vide si non existant pour éviter des erreurs plus loin
        try:
            os.makedirs(os.path.dirname(original_placeholder_path), exist_ok=True)
            with open(original_placeholder_path, 'w') as f:
                f.write('') # Crée un fichier vide
            print(f"Création d'un placeholder vide à: {original_placeholder_path}")
        except Exception as e:
            print(f"Erreur lors de la création du placeholder vide: {e}")
            # Retourner les originaux si la création échoue pour ne pas bloquer
            return plan_data['ai_concept_placeholder_path'], plan_data['ai_concept_filename']

    original_filename = plan_data['ai_concept_filename']
    # Exemple: E202_SQ0010-0010_AI-concept_v0001.png
    parts = original_filename.split('_')
    episode_part = parts[0]
    plan_part = parts[1].split('-')[1] # 0010 de SQ0010-0010
    task_version_ext = '_'.join(parts[2:]) # AI-concept_v0001.png

    new_ai_concept_filename = f"{episode_part}_{new_sequence_number}-{plan_part}_{task_version_ext}"
    
    if new_ai_concept_filename == original_filename:
        return plan_data['ai_concept_placeholder_path'], plan_data['ai_concept_filename'] # Pas de changement

    # Construire le nouveau chemin complet
    # Le chemin dans plan_data['ai_concept_placeholder_path'] est relatif à la racine du serveur de données, ex: 'P001_TestProd/episodes/E01/sequences/SQ0010/AI-concept/E01_SQ0010-0010_AI-concept_v0001.png'
    # Nous devons le reconstruire correctement
    path_segments = plan_data['ai_concept_placeholder_path'].split('/')
    # Remplacer l'ancien nom de fichier par le nouveau
    path_segments[-1] = new_ai_concept_filename
    # Remplacer l'ancien numéro de séquence dans le chemin du dossier par le nouveau
    # Chercher le segment qui contient l'ancien numéro de séquence, ex: SQ0010
    old_sequence_number_in_path = parts[1].split('-')[0] # SQ0010 de SQ0010-0010
    for i, segment in enumerate(path_segments):
        if segment == old_sequence_number_in_path:
            path_segments[i] = new_sequence_number
            break
    new_relative_placeholder_path = '/'.join(path_segments)
    
    # Chemin absolu pour le renommage
    abs_original_placeholder_path = os.path.join(BASE_PROJECT_DATA_PATH, plan_data['project_id'], 'episodes', plan_data['episode_id'], 'sequences', old_sequence_number_in_path, 'AI-concept', original_filename)
    abs_new_placeholder_path = os.path.join(BASE_PROJECT_DATA_PATH, plan_data['project_id'], 'episodes', plan_data['episode_id'], 'sequences', new_sequence_number, 'AI-concept', new_ai_concept_filename)
    
    try:
        os.makedirs(os.path.dirname(abs_new_placeholder_path), exist_ok=True)
        shutil.move(abs_original_placeholder_path, abs_new_placeholder_path)
        print(f"Placeholder renommé de {abs_original_placeholder_path} à {abs_new_placeholder_path}")
        # Mettre à jour plan_data
        plan_data['ai_concept_filename'] = new_ai_concept_filename
        plan_data['ai_concept_placeholder_path'] = new_relative_placeholder_path
        return new_relative_placeholder_path, new_ai_concept_filename
    except Exception as e:
        print(f"Erreur lors du renommage du placeholder {original_filename} en {new_ai_concept_filename}: {e}")
        # Retourner les originaux si le renommage échoue pour éviter de bloquer
        return plan_data['ai_concept_placeholder_path'], plan_data['ai_concept_filename']

def upload_image_to_comfyui(image_path):
    """Télécharge une image vers le serveur ComfyUI."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image source non trouvée: {image_path}")
    
    files = {'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/png')}
    data = {'overwrite': "true"} # Permet de remplacer si le fichier existe déjà avec le même nom
    try:
        response = requests.post(COMFYUI_UPLOAD_URL, files=files, data=data)
        response.raise_for_status()
        return response.json() # Devrait contenir le nom du fichier sur ComfyUI, son sous-dossier, etc.
    except requests.exceptions.RequestException as e:
        print(f"Erreur d'upload vers ComfyUI: {e}")
        if e.response is not None:
            print(f"Réponse de ComfyUI: {e.response.text}")
        raise

def trigger_comfyui_workflow(workflow_payload):
    """Déclenche un workflow sur ComfyUI avec le payload donné."""
    try:
        response = requests.post(COMFYUI_API_URL, json=workflow_payload)
        response.raise_for_status()
        return response.json() # Contient prompt_id, number, node_errors
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du déclenchement du workflow ComfyUI: {e}")
        if e.response is not None:
            print(f"Réponse de ComfyUI: {e.response.text}")
        raise

def get_comfyui_image_output(prompt_id):
    """Récupère le résultat d'image d'un prompt ComfyUI."""
    # Cette fonction est simplifiée. En réalité, il faut interroger /history/{prompt_id}
    # jusqu'à ce que le statut soit complété, puis extraire les données de sortie.
    # Pour l'instant, on simule la récupération.
    
    # Exemple de structure de réponse de /history/{prompt_id}
    # response_data = {
    #     "prompt_id": {
    #         "outputs": {
    #             "node_id_output": { # L'ID du nœud de sortie (SaveImage)
    #                 "images": [
    #                     {
    #                         "filename": "ComfyUI_00001_.png",
    #                         "subfolder": "",
    #                         "type": "output"
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    # }
    # Pour l'instant, cette fonction est un placeholder.
    # Une implémentation réelle nécessiterait une boucle de polling et une analyse de la réponse de l'historique.
    print(f"Récupération de l'image pour prompt_id {prompt_id} (simulation)")
    # Il faudrait ici attendre et récupérer le vrai nom de fichier généré.
    # La logique de sauvegarde dans le bon dossier (AI-concept avec la bonne nomenclature) 
    # se fait soit par ComfyUI directement (si on peut configurer le chemin de sortie via l'API), 
    # soit en téléchargeant l'image et en la sauvegardant manuellement.
    # Pour l'instant, on retourne un nom de fichier générique.
    return "image_generee_par_comfyui.png", ""


def process_plan_with_comfyui(plan_data, project_id, episode_id, base_data_path):
    """
    Traite un plan unique avec ComfyUI.
    plan_data est un dictionnaire contenant les infos du plan (path, ai_concept_placeholder_path, etc.)
    """
    print(f"Début du traitement ComfyUI pour le plan: {plan_data.get('id')}")

    # 1. Vérifier et renommer le placeholder si le numéro de séquence a changé
    # `plan_data['sequence_number']` contient le numéro de séquence potentiellement modifié par l'utilisateur
    # `plan_data['ai_concept_filename']` contient le nom de fichier basé sur le SQ original de l'upload
    
    # Construire le chemin absolu du placeholder original pour le renommage
    # Note: plan_data['ai_concept_placeholder_path'] est relatif, ex: P001_Test/episodes/E01/sequences/SQ0010/AI-concept/E01_SQ0010-0010_AI-concept_v0001.png
    # Il faut le joindre à la racine des données du projet
    original_sq_in_filename = plan_data['ai_concept_filename'].split('_')[1].split('-')[0]
    abs_original_placeholder_path = os.path.join(base_data_path, project_id, 'episodes', episode_id, 'sequences', original_sq_in_filename, 'AI-concept', plan_data['ai_concept_filename'])

    new_relative_placeholder_path, new_ai_concept_filename = rename_ai_concept_placeholder(
        abs_original_placeholder_path,
        plan_data['sequence_number'], # Nouveau SQ potentiellement modifié par l'utilisateur
        plan_data # Passe tout le dict pour que la fonction puisse le mettre à jour
    )
    # Mettre à jour plan_data avec les nouveaux chemins/noms après renommage
    plan_data['ai_concept_placeholder_path'] = new_relative_placeholder_path
    plan_data['ai_concept_filename'] = new_ai_concept_filename

    # 2. Charger le template de workflow ComfyUI
    try:
        with open(WORKFLOW_TEMPLATE_PATH, 'r') as f:
            workflow = json.load(f)
    except FileNotFoundError:
        print(f"Erreur: Template de workflow ComfyUI non trouvé à {WORKFLOW_TEMPLATE_PATH}")
        raise
    except json.JSONDecodeError:
        print(f"Erreur: Template de workflow ComfyUI malformé à {WORKFLOW_TEMPLATE_PATH}")
        raise

    # 3. Uploader l'image source (extracted-raw)
    # `plan_data['path']` est le chemin relatif à la racine du serveur de données, ex: P001_Test/episodes/E01/sequences/SQ0010/extracted-raw/E01_SQ0010-0010_extracted-raw_v0001.png
    abs_source_image_path = os.path.join(base_data_path, project_id, 'episodes', episode_id, 'sequences', plan_data['sequence_number'], 'extracted-raw', plan_data['filename'])
    # Note: Utiliser plan_data['sequence_number'] ici si on suppose que l'image brute est déjà dans le dossier du SQ final. 
    # Si ce n'est pas le cas, il faudrait aussi une étape de déplacement de l'image brute.
    # Pour l'instant, on suppose que l'image brute est accessible via son path original,
    # ou qu'elle est copiée vers un dossier temporaire ou input de ComfyUI.
    
    # Pour plus de robustesse, utilisons le chemin absolu de l'image brute originale
    original_raw_image_filename = plan_data['filename']
    original_raw_sq = original_raw_image_filename.split('_')[1].split('-')[0] # Le SQ de l'image brute est celui de l'upload
    abs_source_image_path_original = os.path.join(base_data_path, project_id, 'episodes', episode_id, 'sequences', original_raw_sq, 'extracted-raw', original_raw_image_filename)

    if not os.path.exists(abs_source_image_path_original):
        print(f"Erreur critique: Image source non trouvée à {abs_source_image_path_original}")
        plan_data['error'] = f"Image source non trouvée: {abs_source_image_path_original}"
        return plan_data # Retourner avec erreur

    try:
        upload_response = upload_image_to_comfyui(abs_source_image_path_original)
        comfyui_input_filename = upload_response.get('name')
        if not comfyui_input_filename:
            raise ValueError("Nom de fichier non retourné par l'upload ComfyUI")
    except Exception as e:
        print(f"Erreur lors de l'upload de l'image source vers ComfyUI: {e}")
        plan_data['error'] = str(e)
        return plan_data

    # 4. Modifier le workflow pour utiliser l'image uploadée et configurer la sortie
    # Trouver le nœud "Load Image" (ou équivalent) et le nœud "Save Image"
    # Les ID des nœuds peuvent varier selon votre workflow. Adaptez les IDs "4" et "5".
    # Vous devrez inspecter votre `Windsurf_Template.json` pour trouver les bons IDs.
    load_image_node_id = None # Ex: "4" pour un LoadImage standard
    save_image_node_id = None # Ex: "5" pour un SaveImage standard

    for node_id, node_data in workflow.items():
        if node_data.get("class_type") == "LoadImage":
            load_image_node_id = node_id
        elif node_data.get("class_type") == "SaveImage":
            save_image_node_id = node_id
    
    if not load_image_node_id or not save_image_node_id:
        print("Erreur: Nœuds LoadImage ou SaveImage non trouvés dans le template de workflow.")
        print(f"Assurez-vous que {WORKFLOW_TEMPLATE_PATH} contient ces types de nœuds.")
        plan_data['error'] = "Nœuds LoadImage/SaveImage manquants dans le workflow template."
        return plan_data

    workflow[load_image_node_id]['inputs']['image'] = comfyui_input_filename
    
    # Configurer le nom du fichier de sortie
    # Le nom de fichier utilisé par SaveImage dans ComfyUI
    # Doit correspondre à `new_ai_concept_filename` pour que ComfyUI sauvegarde directement au bon endroit/nom
    # ComfyUI ajoute souvent un préfixe et un suffixe numérique (ex: ComfyUI_00001_).
    # Pour un contrôle total, il faudrait un custom node ou une post-traitement.
    # Ici, on configure le préfixe du fichier pour SaveImage.
    # On enlève l'extension .png pour le préfixe.
    output_filename_prefix_for_comfyui = new_ai_concept_filename.rsplit('.', 1)[0]
    workflow[save_image_node_id]['inputs']['filename_prefix'] = output_filename_prefix_for_comfyui

    # 5. Déclencher le workflow
    prompt_payload = {"prompt": workflow, "client_id": str(uuid.uuid4())}
    try:
        trigger_response = trigger_comfyui_workflow(prompt_payload)
        prompt_id = trigger_response.get('prompt_id')
        if not prompt_id:
            raise ValueError("prompt_id non retourné par ComfyUI")
    except Exception as e:
        print(f"Erreur lors du déclenchement du workflow ComfyUI: {e}")
        plan_data['error'] = str(e)
        return plan_data

    # 6. Récupérer le résultat (simplifié pour l'instant)
    # Dans une implémentation réelle, il faudrait une boucle de polling ici.
    # On attendrait que ComfyUI ait fini de traiter le prompt_id.
    # Puis on récupérerait le chemin de l'image générée via /history ou /view.
    # Pour cet exemple, on va considérer que ComfyUI sauvegarde directement
    # le fichier avec le nom `new_ai_concept_filename` dans son dossier `output`.
    # Le frontend s'attend à un chemin relatif au serveur de données Madsea.
    
    # On suppose que ComfyUI a sauvegardé l'image et que le nom correspond à `new_ai_concept_filename`
    # et qu'elle est accessible via le même chemin relatif que le placeholder.
    # Mettre à jour le chemin vers le fichier concept AI généré.
    # Le `ai_concept_placeholder_path` a déjà été mis à jour par `rename_ai_concept_placeholder`.
    # Ce chemin est maintenant celui de l'image réellement générée.
    plan_data['ai_concept_path_final'] = plan_data['ai_concept_placeholder_path'] # Le placeholder est devenu le fichier final
    plan_data['status'] = 'completed'
    print(f"Traitement ComfyUI terminé pour le plan {plan_data.get('id')}. Image générée (supposée): {plan_data['ai_concept_path_final']}")

    return plan_data
