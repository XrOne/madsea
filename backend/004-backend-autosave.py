"""
Module de gestion des autosauvegardes pour Madsea
Implémente la sauvegarde automatique des projets, épisodes et scènes,
avec historique et restauration (inspiré des systèmes d'autosauve d'Adobe Premiere).
"""

import os
import json
import time
import shutil
import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import logging
from collections import deque

# Configuration du logger
logging.basicConfig(
    filename='logs/autosave.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Création du blueprint Flask
autosave_bp = Blueprint('autosave', __name__)

# Constantes
MAX_AUTOSAVES_PER_PROJECT = 10  # Nombre maximum d'autosauvegardes par projet (FIFO)
BACKUP_ROOT = 'backups'  # Répertoire racine pour les sauvegardes (hors uploads/)

# Structure d'enregistrement des autosauvegardes (en mémoire)
# Dans une vraie application, cela pourrait être dans une base de données
autosave_registry = {}

def ensure_backup_dir(project_id):
    """Crée le répertoire de sauvegarde pour un projet s'il n'existe pas."""
    backup_dir = os.path.join(BACKUP_ROOT, project_id)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def register_autosave(project_id, version_id, description, trigger, changes):
    """Enregistre une nouvelle autosauvegarde dans le registre et maintient la limite FIFO."""
    if project_id not in autosave_registry:
        autosave_registry[project_id] = deque(maxlen=MAX_AUTOSAVES_PER_PROJECT)
    
    # Ajouter la nouvelle version
    version_info = {
        'id': version_id,
        'timestamp': datetime.datetime.now().isoformat(),
        'description': description,
        'trigger': trigger,
        'changes': changes if changes else []
    }
    
    # Utiliser deque avec maxlen garantit automatiquement la limite FIFO
    autosave_registry[project_id].appendleft(version_info)
    
    # Sauvegarder le registre dans un fichier JSON
    registry_file = os.path.join(BACKUP_ROOT, 'registry.json')
    with open(registry_file, 'w') as f:
        # Convertir les deques en listes pour la sérialisation JSON
        serializable_registry = {pid: list(versions) for pid, versions in autosave_registry.items()}
        json.dump(serializable_registry, f, indent=2)
    
    return version_info

def load_autosave_registry():
    """Charge le registre d'autosauvegardes depuis le fichier."""
    global autosave_registry
    registry_file = os.path.join(BACKUP_ROOT, 'registry.json')
    
    if not os.path.exists(BACKUP_ROOT):
        os.makedirs(BACKUP_ROOT)
    
    if os.path.exists(registry_file):
        try:
            with open(registry_file, 'r') as f:
                loaded_registry = json.load(f)
                
            # Convertir les listes en deques avec la maxlen appropriée
            autosave_registry = {
                pid: deque(versions, maxlen=MAX_AUTOSAVES_PER_PROJECT)
                for pid, versions in loaded_registry.items()
            }
        except Exception as e:
            logging.error(f"Erreur lors du chargement du registre d'autosauvegardes: {e}")
            autosave_registry = {}
    else:
        autosave_registry = {}

# Charger le registre au démarrage
load_autosave_registry()

@autosave_bp.route('/project/<project_id>/autosave', methods=['POST'])
def create_autosave(project_id):
    """
    Crée une nouvelle autosauvegarde d'un projet.
    
    L'autosauvegarde inclut l'état complet du projet, avec ses épisodes et ses scènes.
    La sauvegarde est horodatée et peut être associée à une description et un type d'événement.
    """
    try:
        # Vérifier si le répertoire des projets existe
        projects_dir = 'uploads/projects'
        project_dir = os.path.join(projects_dir, project_id)
        
        if not os.path.exists(project_dir):
            return jsonify({'error': 'Project not found'}), 404
        
        # Créer un identifiant unique pour cette version
        timestamp = int(time.time())
        version_id = f"v{timestamp}"
        
        # Préparer le répertoire de sauvegarde
        backup_dir = ensure_backup_dir(project_id)
        version_dir = os.path.join(backup_dir, version_id)
        
        # Copier tout le contenu du projet dans le répertoire de sauvegarde
        shutil.copytree(project_dir, version_dir)
        
        # Récupérer les métadonnées de la sauvegarde depuis la requête
        data = request.json or {}
        description = data.get('description', 'Sauvegarde automatique')
        trigger = data.get('trigger', 'user_action')  # 'user_action', 'timer', 'system', etc.
        changes = data.get('changes', [])
        
        # Enregistrer l'autosauvegarde dans le registre
        version_info = register_autosave(
            project_id, version_id, description, trigger, changes
        )
        
        logging.info(f"Autosauvegarde créée: {project_id}/{version_id} - {description}")
        
        return jsonify({
            'success': True,
            'version': version_info
        })
        
    except Exception as e:
        logging.error(f"Erreur lors de la création de l'autosauvegarde: {e}")
        return jsonify({'error': str(e)}), 500

@autosave_bp.route('/project/<project_id>/autosaves', methods=['GET'])
def list_autosaves(project_id):
    """Liste toutes les autosauvegardes disponibles pour un projet."""
    try:
        if project_id not in autosave_registry:
            return jsonify({'versions': []})
        
        versions = list(autosave_registry[project_id])
        return jsonify({'versions': versions})
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des autosauvegardes: {e}")
        return jsonify({'error': str(e)}), 500

@autosave_bp.route('/project/<project_id>/restore/<version_id>', methods=['POST'])
def restore_autosave(project_id, version_id):
    """
    Restaure une version précédente d'un projet.
    
    Attention: cela écrase l'état actuel du projet!
    """
    try:
        # Vérifier si le projet et la version existent
        backup_dir = os.path.join(BACKUP_ROOT, project_id)
        version_dir = os.path.join(backup_dir, version_id)
        
        if not os.path.exists(version_dir):
            return jsonify({'error': 'Version not found'}), 404
        
        # Vérifier si le répertoire du projet existe
        projects_dir = 'uploads/projects'
        project_dir = os.path.join(projects_dir, project_id)
        
        if not os.path.exists(project_dir):
            return jsonify({'error': 'Project not found'}), 404
        
        # Créer une sauvegarde de l'état actuel avant restauration
        timestamp = int(time.time())
        pre_restore_version_id = f"pre_restore_{timestamp}"
        pre_restore_dir = os.path.join(backup_dir, pre_restore_version_id)
        
        # Copier l'état actuel dans une sauvegarde de secours
        shutil.copytree(project_dir, pre_restore_dir)
        
        # Enregistrer l'autosauvegarde pré-restauration
        register_autosave(
            project_id, 
            pre_restore_version_id, 
            "Sauvegarde automatique avant restauration", 
            "pre_restore", 
            ["Sauvegarde automatique créée avant restauration d'une version antérieure"]
        )
        
        # Supprimer le contenu actuel du projet
        shutil.rmtree(project_dir)
        
        # Copier le contenu de la version à restaurer
        shutil.copytree(version_dir, project_dir)
        
        logging.info(f"Projet restauré: {project_id} vers la version {version_id}")
        
        return jsonify({
            'success': True,
            'message': f"Projet restauré à la version {version_id}",
            'pre_restore_version': pre_restore_version_id
        })
        
    except Exception as e:
        logging.error(f"Erreur lors de la restauration: {e}")
        return jsonify({'error': str(e)}), 500

@autosave_bp.route('/project/<project_id>/autosave/<version_id>', methods=['DELETE'])
def delete_autosave(project_id, version_id):
    """
    Supprime une autosauvegarde spécifique.
    
    Nécessite une confirmation explicite.
    """
    try:
        # Vérifier la confirmation
        data = request.json or {}
        if not data.get('confirm', False):
            return jsonify({
                'error': 'Confirmation requise pour supprimer une sauvegarde',
                'needsConfirmation': True
            }), 400
        
        # Vérifier si la version existe
        backup_dir = os.path.join(BACKUP_ROOT, project_id)
        version_dir = os.path.join(backup_dir, version_id)
        
        if not os.path.exists(version_dir):
            return jsonify({'error': 'Version not found'}), 404
        
        # Supprimer le répertoire de la version
        shutil.rmtree(version_dir)
        
        # Mettre à jour le registre
        if project_id in autosave_registry:
            autosave_registry[project_id] = deque(
                [v for v in autosave_registry[project_id] if v['id'] != version_id],
                maxlen=MAX_AUTOSAVES_PER_PROJECT
            )
            
            # Sauvegarder le registre mis à jour
            registry_file = os.path.join(BACKUP_ROOT, 'registry.json')
            with open(registry_file, 'w') as f:
                serializable_registry = {pid: list(versions) for pid, versions in autosave_registry.items()}
                json.dump(serializable_registry, f, indent=2)
        
        logging.info(f"Autosauvegarde supprimée: {project_id}/{version_id}")
        
        return jsonify({
            'success': True,
            'message': f"Version {version_id} supprimée"
        })
        
    except Exception as e:
        logging.error(f"Erreur lors de la suppression de l'autosauvegarde: {e}")
        return jsonify({'error': str(e)}), 500