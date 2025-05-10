"""
Module de gestion des dépendances pour Madsea
---------------------------------------------
Architecture robuste pour la vérification et l'auto-réparation des dépendances système.
Ce module implémente une approche modulaire qui vérifie les dépendances directement dans le code
plutôt que via des scripts externes, conformément aux meilleures pratiques de développement.
"""

import os
import sys
import logging
import importlib
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

# Configuration du logging
logger = logging.getLogger(__name__)

class DependencyManager:
    """
    Gestionnaire de dépendances centralisé pour Madsea.
    
    Fournit des capacités de:
    - Vérification de dépendances externes (Tesseract, etc.)
    - Vérification de modules Python
    - Auto-réparation quand possible
    - Génération de diagnostics détaillés
    """
    
    def __init__(self, config_path: Optional[str] = None, auto_repair: bool = True):
        """
        Initialise le gestionnaire de dépendances.
        
        Args:
            config_path: Chemin vers le fichier de configuration (JSON)
            auto_repair: Tenter de réparer automatiquement les problèmes
        """
        self.madsea_root = self._find_madsea_root()
        self.config_path = config_path or os.path.join(self.madsea_root, 'config', 'dependencies.json')
        self.auto_repair = auto_repair
        self.status: Dict[str, Dict[str, Any]] = {}
        self.config = self._load_config()
        
    def _find_madsea_root(self) -> str:
        """Trouve le dossier racine de Madsea en remontant depuis le fichier actuel."""
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Vérifier si nous sommes dans le dossier Madsea (présence de marqueurs)
        if os.path.exists(os.path.join(current_dir, 'backend')) and os.path.exists(os.path.join(current_dir, 'config')):
            return current_dir
            
        # Fallback en configurant une variable d'environnement
        if 'MADSEA_HOME' in os.environ:
            return os.environ['MADSEA_HOME']
            
        # Dernier recours: dossier parent du backend
        return current_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration des dépendances depuis le fichier JSON."""
        default_config = {
            "python_modules": {
                "required": ["flask", "pymupdf", "pytesseract", "pillow", "opencv-python-headless"],
                "optional": ["comfy-mcp-server", "websocket-client"]
            },
            "external_dependencies": {
                "tesseract": {
                    "name": "Tesseract OCR",
                    "paths": [
                        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                        "%MADSEA_HOME%\\ocr\\tesseract.exe"
                    ],
                    "version_command": "{path} --version",
                    "version_pattern": r"tesseract ([\d.]+)",
                    "install_guide": "Téléchargez Tesseract depuis https://github.com/UB-Mannheim/tesseract/wiki",
                    "critical": True
                }
            },
            "directories": {
                "temp": {"path": "%MADSEA_HOME%/temp", "permissions": "write"},
                "uploads": {"path": "%MADSEA_HOME%/uploads", "permissions": "write"},
                "outputs": {"path": "%MADSEA_HOME%/outputs", "permissions": "write"}
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Créer le fichier de configuration avec les valeurs par défaut
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return default_config
    
    def _expand_vars(self, path: str) -> str:
        """Remplace les variables dans les chemins."""
        if '%MADSEA_HOME%' in path:
            path = path.replace('%MADSEA_HOME%', self.madsea_root)
        return os.path.expandvars(path)
    
    def check_python_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie les modules Python requis et optionnels.
        
        Returns:
            Dictionnaire avec l'état de chaque module.
        """
        results = {}
        
        # Vérifier les modules requis
        for module_name in self.config.get("python_modules", {}).get("required", []):
            results[module_name] = self._check_python_module(module_name, required=True)
            
        # Vérifier les modules optionnels
        for module_name in self.config.get("python_modules", {}).get("optional", []):
            results[module_name] = self._check_python_module(module_name, required=False)
            
        self.status["python_modules"] = results
        return results
    
    def _check_python_module(self, module_name: str, required: bool) -> Dict[str, Any]:
        """Vérifie un module Python spécifique."""
        result = {
            "name": module_name,
            "required": required,
            "installed": False,
            "version": None,
            "error": None
        }
        
        try:
            module = importlib.import_module(module_name)
            result["installed"] = True
            
            # Essayer de récupérer la version
            try:
                if hasattr(module, '__version__'):
                    result["version"] = getattr(module, '__version__')
                elif hasattr(module, 'version'):
                    result["version"] = getattr(module, 'version')
            except Exception:
                pass
                
        except ImportError as e:
            result["error"] = str(e)
            
            # Auto-réparation si activée et module requis
            if self.auto_repair and required:
                try:
                    logger.info(f"Tentative d'installation automatique de {module_name}...")
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', module_name])
                    
                    # Vérifier à nouveau
                    try:
                        module = importlib.import_module(module_name)
                        result["installed"] = True
                        result["auto_repaired"] = True
                        
                        if hasattr(module, '__version__'):
                            result["version"] = getattr(module, '__version__')
                    except ImportError:
                        result["auto_repaired"] = False
                except Exception as install_error:
                    result["auto_repair_error"] = str(install_error)
        
        return result
    
    def check_external_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie les dépendances externes comme Tesseract.
        
        Returns:
            Dictionnaire avec l'état de chaque dépendance.
        """
        results = {}
        
        for dep_id, dep_info in self.config.get("external_dependencies", {}).items():
            results[dep_id] = self._check_external_dependency(dep_id, dep_info)
            
        self.status["external_dependencies"] = results
        return results
    
    def _check_external_dependency(self, dep_id: str, dep_info: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie une dépendance externe spécifique."""
        result = {
            "id": dep_id,
            "name": dep_info.get("name", dep_id),
            "installed": False,
            "path": None,
            "version": None,
            "error": None,
            "critical": dep_info.get("critical", False)
        }
        
        # Vérifier les chemins possibles
        paths = dep_info.get("paths", [])
        for path in paths:
            expanded_path = self._expand_vars(path)
            if os.path.exists(expanded_path):
                result["installed"] = True
                result["path"] = expanded_path
                
                # Vérifier la version
                if "version_command" in dep_info:
                    try:
                        cmd = dep_info["version_command"].replace("{path}", f'"{expanded_path}"')
                        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                        
                        # Extraire la version avec regex si disponible
                        if "version_pattern" in dep_info:
                            import re
                            match = re.search(dep_info["version_pattern"], output)
                            if match:
                                result["version"] = match.group(1)
                        else:
                            result["version"] = output.strip()
                    except Exception as e:
                        result["error"] = f"Erreur lors de la vérification de la version: {e}"
                
                break
        
        # Si non trouvé et auto-réparation activée
        if not result["installed"] and self.auto_repair and dep_id == "tesseract":
            embedded_path = os.path.join(self.madsea_root, "ocr")
            if not os.path.exists(embedded_path):
                os.makedirs(embedded_path, exist_ok=True)
                result["repair_note"] = f"Dossier {embedded_path} créé pour Tesseract embarqué"
                
        return result
    
    def check_directories(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie les dossiers requis et leurs permissions.
        
        Returns:
            Dictionnaire avec l'état de chaque dossier.
        """
        results = {}
        
        for dir_id, dir_info in self.config.get("directories", {}).items():
            results[dir_id] = self._check_directory(dir_id, dir_info)
            
        self.status["directories"] = results
        return results
    
    def _check_directory(self, dir_id: str, dir_info: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie un dossier spécifique et ses permissions."""
        path = self._expand_vars(dir_info.get("path", ""))
        result = {
            "id": dir_id,
            "path": path,
            "exists": os.path.exists(path),
            "is_dir": os.path.isdir(path) if os.path.exists(path) else False,
            "writable": os.access(path, os.W_OK) if os.path.exists(path) else False,
            "readable": os.access(path, os.R_OK) if os.path.exists(path) else False
        }
        
        # Auto-réparation: créer le dossier s'il n'existe pas
        if not result["exists"] and self.auto_repair:
            try:
                os.makedirs(path, exist_ok=True)
                result["exists"] = True
                result["is_dir"] = True
                result["auto_repaired"] = True
                
                # Vérifier à nouveau les permissions
                result["writable"] = os.access(path, os.W_OK)
                result["readable"] = os.access(path, os.R_OK)
            except Exception as e:
                result["error"] = f"Erreur lors de la création du dossier: {e}"
                result["auto_repaired"] = False
                
        return result
    
    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie toutes les dépendances et prérequis.
        
        Returns:
            Dictionnaire avec tous les résultats.
        """
        logger.info("Vérification complète des dépendances en cours...")
        
        # Exécuter toutes les vérifications
        python_modules = self.check_python_modules()
        external_deps = self.check_external_dependencies()
        directories = self.check_directories()
        
        # Assembler les résultats
        self.status = {
            "python_modules": python_modules,
            "external_dependencies": external_deps,
            "directories": directories,
            "overall": self._calculate_overall_status()
        }
        
        return self.status
    
    def _calculate_overall_status(self) -> Dict[str, Any]:
        """Calcule le statut global à partir des vérifications individuelles."""
        critical_errors = []
        warnings = []
        auto_repairs = []
        
        # Vérifier les modules Python requis
        if "python_modules" in self.status:
            for module_name, module_info in self.status["python_modules"].items():
                if module_info.get("required", False) and not module_info.get("installed", False):
                    critical_errors.append(f"Module Python requis non installé: {module_name}")
                if module_info.get("auto_repaired", False):
                    auto_repairs.append(f"Module Python réparé automatiquement: {module_name}")
        
        # Vérifier les dépendances externes critiques
        if "external_dependencies" in self.status:
            for dep_id, dep_info in self.status["external_dependencies"].items():
                if dep_info.get("critical", False) and not dep_info.get("installed", False):
                    critical_errors.append(f"Dépendance critique non installée: {dep_info.get('name', dep_id)}")
                
        # Vérifier les dossiers
        if "directories" in self.status:
            for dir_id, dir_info in self.status["directories"].items():
                if not dir_info.get("exists", False):
                    critical_errors.append(f"Dossier requis absent: {dir_id} ({dir_info.get('path', '')})")
                elif not dir_info.get("writable", False) and dir_info.get("is_dir", False):
                    warnings.append(f"Dossier sans permission d'écriture: {dir_id} ({dir_info.get('path', '')})")
                if dir_info.get("auto_repaired", False):
                    auto_repairs.append(f"Dossier créé automatiquement: {dir_id} ({dir_info.get('path', '')})")
        
        # Déterminer le statut global
        if critical_errors:
            status = "critical"
        elif warnings:
            status = "warning"
        else:
            status = "ok"
            
        return {
            "status": status,
            "critical_errors": critical_errors,
            "warnings": warnings,
            "auto_repairs": auto_repairs
        }
    
    def generate_report(self, format: str = "text") -> str:
        """
        Génère un rapport détaillé de toutes les dépendances.
        
        Args:
            format: Format du rapport ('text', 'json', 'html')
            
        Returns:
            Rapport formaté
        """
        if not self.status:
            self.check_all()
            
        if format == "json":
            return json.dumps(self.status, indent=2)
        
        elif format == "html":
            # Template HTML simple
            html = """<!DOCTYPE html>
            <html>
            <head>
                <title>Rapport de dépendances Madsea</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .ok { color: green; }
                    .warning { color: orange; }
                    .critical { color: red; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <h1>Rapport de dépendances Madsea</h1>
                <h2>Statut global: <span class="{0}">{0}</span></h2>
            """.format(self.status["overall"]["status"])
            
            # Erreurs critiques
            if self.status["overall"]["critical_errors"]:
                html += "<h3>Erreurs critiques:</h3><ul>"
                for error in self.status["overall"]["critical_errors"]:
                    html += f"<li class='critical'>{error}</li>"
                html += "</ul>"
                
            # Avertissements
            if self.status["overall"]["warnings"]:
                html += "<h3>Avertissements:</h3><ul>"
                for warning in self.status["overall"]["warnings"]:
                    html += f"<li class='warning'>{warning}</li>"
                html += "</ul>"
                
            # Auto-réparations
            if self.status["overall"]["auto_repairs"]:
                html += "<h3>Réparations automatiques:</h3><ul>"
                for repair in self.status["overall"]["auto_repairs"]:
                    html += f"<li>{repair}</li>"
                html += "</ul>"
                
            # Modules Python
            html += """
                <h2>Modules Python</h2>
                <table>
                    <tr>
                        <th>Module</th>
                        <th>Requis</th>
                        <th>Installé</th>
                        <th>Version</th>
                        <th>Statut</th>
                    </tr>
            """
            
            for name, info in self.status["python_modules"].items():
                status_class = "ok" if info.get("installed", False) else "critical" if info.get("required", False) else "warning"
                html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{"Oui" if info.get("required", False) else "Non"}</td>
                        <td>{"Oui" if info.get("installed", False) else "Non"}</td>
                        <td>{info.get("version", "N/A")}</td>
                        <td class='{status_class}'>{status_class.upper()}</td>
                    </tr>
                """
            
            html += "</table>"
            
            # Dépendances externes
            html += """
                <h2>Dépendances externes</h2>
                <table>
                    <tr>
                        <th>Nom</th>
                        <th>Critique</th>
                        <th>Installé</th>
                        <th>Chemin</th>
                        <th>Version</th>
                    </tr>
            """
            
            for name, info in self.status["external_dependencies"].items():
                status_class = "ok" if info.get("installed", False) else "critical" if info.get("critical", False) else "warning"
                html += f"""
                    <tr>
                        <td>{info.get("name", name)}</td>
                        <td>{"Oui" if info.get("critical", False) else "Non"}</td>
                        <td>{"Oui" if info.get("installed", False) else "Non"}</td>
                        <td>{info.get("path", "N/A")}</td>
                        <td>{info.get("version", "N/A")}</td>
                    </tr>
                """
            
            html += "</table>"
            
            # Dossiers
            html += """
                <h2>Dossiers requis</h2>
                <table>
                    <tr>
                        <th>Nom</th>
                        <th>Chemin</th>
                        <th>Existe</th>
                        <th>Lecture</th>
                        <th>Écriture</th>
                    </tr>
            """
            
            for name, info in self.status["directories"].items():
                status_class = "ok" if info.get("exists", False) and info.get("writable", False) else "critical"
                html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{info.get("path", "N/A")}</td>
                        <td>{"Oui" if info.get("exists", False) else "Non"}</td>
                        <td>{"Oui" if info.get("readable", False) else "Non"}</td>
                        <td>{"Oui" if info.get("writable", False) else "Non"}</td>
                    </tr>
                """
            
            html += "</table></body></html>"
            return html
            
        else:  # Text format (default)
            lines = []
            lines.append("=== RAPPORT DE DÉPENDANCES MADSEA ===")
            lines.append(f"Statut global: {self.status['overall']['status'].upper()}")
            
            # Erreurs critiques
            if self.status["overall"]["critical_errors"]:
                lines.append("\nErreurs critiques:")
                for error in self.status["overall"]["critical_errors"]:
                    lines.append(f"  - {error}")
                    
            # Avertissements
            if self.status["overall"]["warnings"]:
                lines.append("\nAvertissements:")
                for warning in self.status["overall"]["warnings"]:
                    lines.append(f"  - {warning}")
                    
            # Auto-réparations
            if self.status["overall"]["auto_repairs"]:
                lines.append("\nRéparations automatiques:")
                for repair in self.status["overall"]["auto_repairs"]:
                    lines.append(f"  - {repair}")
            
            # Modules Python
            lines.append("\n== Modules Python ==")
            for name, info in self.status["python_modules"].items():
                status = "OK" if info.get("installed", False) else "MANQUANT (CRITIQUE)" if info.get("required", False) else "MANQUANT (OPTIONNEL)"
                lines.append(f"  {name}: {status} {info.get('version', '')}")
                
            # Dépendances externes
            lines.append("\n== Dépendances externes ==")
            for name, info in self.status["external_dependencies"].items():
                status = "OK" if info.get("installed", False) else "MANQUANT (CRITIQUE)" if info.get("critical", False) else "MANQUANT (OPTIONNEL)"
                lines.append(f"  {info.get('name', name)}: {status}")
                if info.get("path"):
                    lines.append(f"    Chemin: {info.get('path')}")
                if info.get("version"):
                    lines.append(f"    Version: {info.get('version')}")
                    
            # Dossiers
            lines.append("\n== Dossiers requis ==")
            for name, info in self.status["directories"].items():
                status = "OK" if info.get("exists", False) and info.get("writable", False) else "PROBLÈME"
                lines.append(f"  {name}: {status}")
                lines.append(f"    Chemin: {info.get('path', 'N/A')}")
                if info.get("exists", False):
                    lines.append(f"    Permissions: {'Lecture' if info.get('readable', False) else ''}{', Écriture' if info.get('writable', False) else ''}")
                    
            return "\n".join(lines)
    
    def save_report(self, output_path: Optional[str] = None, format: str = "text") -> str:
        """
        Sauvegarde le rapport dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie (généré automatiquement si None)
            format: Format du rapport ('text', 'json', 'html')
            
        Returns:
            Chemin du fichier sauvegardé
        """
        if not output_path:
            ext = ".txt" if format == "text" else f".{format}"
            output_path = os.path.join(self.madsea_root, f"dependency_report{ext}")
            
        report = self.generate_report(format)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Rapport de dépendances sauvegardé dans {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            return ""
    
    def configure_tesseract(self) -> Dict[str, Any]:
        """
        Configure Tesseract OCR dans le système.
        
        Returns:
            Informations sur la configuration Tesseract.
        """
        import importlib
        
        try:
            pytesseract = importlib.import_module('pytesseract')
        except ImportError:
            return {
                "success": False,
                "error": "Module pytesseract non installé."
            }
            
        # Vérifier Tesseract
        if "external_dependencies" not in self.status:
            self.check_external_dependencies()
            
        tesseract_info = self.status.get("external_dependencies", {}).get("tesseract", {})
        
        if tesseract_info.get("installed", False) and tesseract_info.get("path"):
            # Configurer le chemin Tesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_info["path"]
            
            return {
                "success": True,
                "path": tesseract_info["path"],
                "version": tesseract_info.get("version", "Inconnue")
            }
        else:
            # Fallback sur les chemins connus
            standard_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                os.path.join(self.madsea_root, 'ocr', 'tesseract.exe')
            ]
            
            for path in standard_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    return {
                        "success": True,
                        "path": path,
                        "note": "Utilisé le chemin par défaut"
                    }
                    
            return {
                "success": False,
                "error": "Tesseract non trouvé. Installation requise.",
                "install_guide": self.config.get("external_dependencies", {}).get("tesseract", {}).get("install_guide", "")
            }

# Fonction utilitaire pour obtenir une instance unique
_dependency_manager = None

def get_dependency_manager() -> DependencyManager:
    """
    Obtient l'instance unique du gestionnaire de dépendances.
    
    Returns:
        Instance du gestionnaire de dépendances
    """
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager()
    return _dependency_manager

def check_environment():
    """
    Vérifie rapidement l'environnement au démarrage.
    
    Returns:
        Statut global de l'environnement
    """
    manager = get_dependency_manager()
    status = manager.check_all()
    
    # Configurer automatiquement Tesseract
    _ = manager.configure_tesseract()
    
    return status["overall"]["status"]

def get_tesseract_path() -> str:
    """
    Obtient le chemin Tesseract configuré.
    
    Returns:
        Chemin vers l'exécutable Tesseract
    """
    manager = get_dependency_manager()
    if "external_dependencies" not in manager.status:
        manager.check_external_dependencies()
        
    tesseract_info = manager.status.get("external_dependencies", {}).get("tesseract", {})
    
    if tesseract_info.get("installed", False) and tesseract_info.get("path"):
        return tesseract_info["path"]
    else:
        # Reconfigurer et revérifier
        result = manager.configure_tesseract()
        return result.get("path", "")

# Fonction pour génération de rapport console
def print_status_report():
    """Affiche un rapport de statut dans la console."""
    manager = get_dependency_manager()
    print(manager.generate_report())

# Exécution automatique au démarrage du module
if __name__ == '__main__':
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Vérification complète et rapport
    manager = get_dependency_manager()
    manager.check_all()
    print(manager.generate_report())
    
    # Sauvegarder le rapport HTML
    manager.save_report(format="html")