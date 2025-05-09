"""
project_manager.py
------------------
Service central pour gérer les projets Madsea, les plans extraits, la nomenclature stricte,
l'historique des générations IA, et la sauvegarde des données de projet.

Tout est pensé pour être simple, pédagogique et robuste.
"""

import os
import json
import datetime
from typing import Dict, Any

# Chemin où sont stockés les fichiers project_data.json
PROJECTS_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'projects'))

# 1. Créer un projet (dossier + fichier project_data.json)
def initialize_project(project_id: str, episode_prefix: str, sequence_prefix: str) -> Dict[str, Any]:
    """
    Crée un nouveau projet avec les préfixes d'épisode et de séquence par défaut.
    Ex : project_id = "MonFilmS2E2", episode_prefix = "E202", sequence_prefix = "SQ0010"
    """
    project_dir = os.path.join(PROJECTS_BASE_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    project_data_path = os.path.join(project_dir, 'project_data.json')
    if os.path.exists(project_data_path):
        raise FileExistsError(f"Le projet '{project_id}' existe déjà.")
    project_data = {
        "project_id": project_id,
        "default_episode_prefix": episode_prefix,
        "default_sequence_prefix": sequence_prefix,
        "plans": []  # Liste de plans extraits
    }
    with open(project_data_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2)
    return project_data

# 2. Charger les données d'un projet
def load_project_data(project_id: str) -> Dict[str, Any]:
    project_data_path = os.path.join(PROJECTS_BASE_DIR, project_id, 'project_data.json')
    if not os.path.exists(project_data_path):
        raise FileNotFoundError(f"Projet '{project_id}' non trouvé.")
    with open(project_data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 3. Sauvegarder les données d'un projet
def save_project_data(project_id: str, data: Dict[str, Any]):
    project_data_path = os.path.join(PROJECTS_BASE_DIR, project_id, 'project_data.json')
    with open(project_data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# 4. Initialiser un plan extrait dans un projet
def initialize_plan_in_project(project_id: str, plan_base_id: str, source_image_path: str, initial_text: str, initial_nomenclature_base: str) -> Dict[str, Any]:
    """
    Ajoute un plan extrait au projet, avec nomenclature stricte.
    - plan_base_id : ex "E202_SQ0010-0001"
    - source_image_path : chemin vers l'image brute extraite
    - initial_text : texte OCR extrait
    - initial_nomenclature_base : identique à plan_base_id sauf correction manuelle
    """
    data = load_project_data(project_id)
    # Vérifier si le plan existe déjà
    for plan in data['plans']:
        if plan['plan_base_id'] == plan_base_id:
            return plan  # Ne pas dupliquer
    plan = {
        "plan_base_id": plan_base_id,
        "current_nomenclature_base": initial_nomenclature_base,
        "source_image_path": source_image_path,
        "extracted_text": initial_text,
        "history": []  # Historique des générations IA
    }
    data['plans'].append(plan)
    save_project_data(project_id, data)
    return plan

# 5. Mettre à jour le texte d'un plan
def update_plan_text(project_id: str, plan_base_id: str, new_text: str) -> Dict[str, Any]:
    data = load_project_data(project_id)
    for plan in data['plans']:
        if plan['plan_base_id'] == plan_base_id:
            plan['extracted_text'] = new_text
            save_project_data(project_id, data)
            return plan
    raise ValueError(f"Plan '{plan_base_id}' non trouvé dans le projet '{project_id}'.")

# 6. Correction manuelle de la nomenclature de base (rare)
def update_plan_nomenclature_base(project_id: str, plan_base_id: str, new_nomenclature_base: str) -> Dict[str, Any]:
    data = load_project_data(project_id)
    for plan in data['plans']:
        if plan['plan_base_id'] == plan_base_id:
            plan['current_nomenclature_base'] = new_nomenclature_base
            save_project_data(project_id, data)
            return plan
    raise ValueError(f"Plan '{plan_base_id}' non trouvé dans le projet '{project_id}'.")

# 7. Générer le nom de fichier IA strict (versionné)
def get_next_ai_filename(project_id: str, plan_base_id: str, task: str, ext: str = "png") -> str:
    """
    Donne le prochain nom de fichier IA pour un plan et un type de tâche (style), en incrémentant la version.
    Ex : get_next_ai_filename("MonFilm", "E202_SQ0010-0001", "AI-concept")
    -> "E202_SQ0010-0001_AI-concept_v0001.png"
    """
    data = load_project_data(project_id)
    plan = next((p for p in data['plans'] if p['plan_base_id'] == plan_base_id), None)
    if not plan:
        raise ValueError(f"Plan '{plan_base_id}' non trouvé dans le projet '{project_id}'.")
    nomenclature_base = plan['current_nomenclature_base']
    # Compter les générations IA déjà faites pour ce plan et ce task
    count = 0
    for hist in plan['history']:
        if hist['task'] == task:
            count += 1
    version = count + 1
    filename = f"{nomenclature_base}_{task}_v{version:04d}.{ext}"
    return filename

# 8. Ajouter une génération IA à l'historique du plan
def add_ai_generation_to_history(project_id: str, plan_base_id: str, generated_filename: str, prompt_used: str, task: str):
    data = load_project_data(project_id)
    plan = next((p for p in data['plans'] if p['plan_base_id'] == plan_base_id), None)
    if not plan:
        raise ValueError(f"Plan '{plan_base_id}' non trouvé dans le projet '{project_id}'.")
    entry = {
        "filename": generated_filename,
        "prompt": prompt_used,
        "task": task,
        "timestamp": datetime.datetime.now().isoformat(timespec='seconds')
    }
    plan['history'].append(entry)
    save_project_data(project_id, data)

# ---
# Chaque fonction est prévue pour être appelée par le reste du backend (extraction, comfyui, API)
# et garantir la cohérence de la nomenclature et de l'historique.
# ---
