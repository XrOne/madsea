
import os
import shutil
import re
import json
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any
import io

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