import os
import shutil
import re
import json
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any
import io
import csv
import datetime

class FileManager:
    """
    Service de gestion des fichiers pour Madsea
    Gère l'organisation, la nomenclature et le versioning des fichiers
    """
    
    def __init__(self, upload_dir: str, output_dir: str):
        """
        Initialise le gestionnaire de fichiers
        
        Args:
            upload_dir: Répertoire pour les fichiers uploadés
            output_dir: Répertoire pour les fichiers générés
        """
    
    def auto_log_nomenclature(self, file_path: str, episode: str, sequence: str, plan: str, task: str, version: int):
        """
        Enregistre automatiquement une entrée dans log-nomenclature.csv après génération.
        
        Args:
            file_path: Chemin complet du fichier généré
            episode: Numéro d'épisode
            sequence: Numéro de séquence
            plan: Numéro de plan
            task: Tâche (e.g., 'AI-concept')
            version: Numéro de version
        """
        # Construire la nomenclature standard
        nomenclature = f"E{episode}_SQ{sequence}-{plan}_{task}_v{version:04d}.png"
        
        # Vérifier si le fichier respecte la nomenclature
        if not file_path.endswith(nomenclature):
            raise ValueError(f"Nomenclature incorrecte. Attendu : {nomenclature}, Trouvé : {os.path.basename(file_path)}")
        
        # Obtenir le timestamp actuel
        timestamp = datetime.datetime.now().isoformat()
        
        # Écrire dans log-nomenclature.csv
        log_path = "i:\\Madsea\\document\\log-nomenclature.csv"
        with open(log_path, 'a', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow([file_path, episode, sequence, plan, task, version, timestamp])
        
        return True