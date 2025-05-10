# Architecture du Module OCR Portable de Madsea

## 1. Principes de Conception

Le module OCR de Madsea a été conçu selon les principes d'architecture modulaire suivants :

- **Séparation des préoccupations** : Le module OCR est indépendant des autres services
- **Configuration externalisée** : Paramètres dans un fichier JSON séparé
- **Portabilité** : Fonctionne sur différents environnements sans modification du code
- **Robustesse** : Gestion des erreurs et fallbacks intelligents
- **API unifiée** : Interface simple masquant la complexité interne

## 2. Structure du Module

```
backend/
├── services/
│   └── ocr_manager.py    # Module principal OCR
├── extraction_api.py     # Utilisation du module OCR
└── app.py                # Configuration Flask

config/
└── ocr_config.json       # Configuration externalisée
```

## 3. Composants Principaux

### OCR Manager (`backend/services/ocr_manager.py`)

Classe centrale qui gère toutes les opérations OCR avec les fonctionnalités :

- Détection automatique de Tesseract
- Substitution de variables d'environnement (`%MADSEA_HOME%`, etc.)
- API simplifiée pour l'extraction de texte
- Cache des résultats pour optimiser les performances
- Gestion des erreurs avec logs détaillés

```python
# Exemple d'utilisation
from services.ocr_manager import get_ocr_manager

# Obtenir le gestionnaire OCR
ocr_manager = get_ocr_manager()

# Informations sur l'installation
info = ocr_manager.get_tesseract_info()
print(f"Tesseract version: {info['version']}")

# Extraction de texte
text = ocr_manager.perform_ocr("chemin/vers/image.png", lang="fra+eng")
```

### Configuration OCR (`config/ocr_config.json`)

```json
{
    "tesseract_paths": [
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "%MADSEA_HOME%\\ocr\\tesseract.exe",
        "%APPDATA%\\Madsea\\tools\\tesseract.exe"
    ],
    "embedded_mode": false,
    "languages": ["fra", "eng"],
    "default_lang": "fra",
    "options": {
        "config": "",
        "dpi": 300
    }
}
```

## 4. Fonctionnement du Mode Portable

Le mode portable active plusieurs mécanismes :

1. **Recherche prioritaire** dans le dossier `%MADSEA_HOME%\ocr`
2. **Variable d'environnement** `MADSEA_HOME` définie par le script de lancement portable
3. **Configuration adaptative** avec `embedded_mode: true`

### Sequence d'initialisation en mode portable :

1. Lancement de `portable\start_madsea_portable.bat`
2. Définition de `MADSEA_HOME` et ajout au PATH
3. Copie de la configuration OCR embarquée
4. Démarrage de l'application standard
5. Initialisation de `OCRManager` qui trouve Tesseract dans le dossier embarqué

## 5. Intégration avec l'Extraction PDF

Dans `extraction_api.py`, le code a été modifié pour utiliser le gestionnaire OCR :

```python
def _process_page_content_advanced(page, page_num, ...):
    # Utilisation du gestionnaire OCR centralisé
    ocr_manager = get_ocr_manager()
    
    # Extraction du texte depuis l'image
    for img_index, img in enumerate(images):
        # [...] Prétraitement de l'image
        text = ocr_manager.perform_ocr(temp_img_path)
        # [...] Traitement du texte extrait
```

## 6. Avantages Techniques

Cette architecture présente plusieurs avantages techniques :

- **Maintenance simplifiée** : Modifications OCR centralisées dans un seul module
- **Tests unitaires facilités** : Interface claire pour tester l'OCR séparément
- **Évolutivité** : Possibilité d'intégrer d'autres moteurs OCR sans changer le reste du code
- **Déploiement flexible** : Fonctionne avec Tesseract installé ou embarqué
- **Logs précis** : Messages de diagnostic qui facilitent le dépannage

## 7. Extensibilité Future

Le module est conçu pour être étendu avec de nouvelles fonctionnalités :

- Support pour d'autres langues (ajout simple dans `ocr_config.json`)
- Intégration d'autres moteurs OCR comme alternative (Azure AI, etc.)
- Prétraitement d'image spécifique au domaine (cinéma, animation)
- Cache d'extraction pour les pages similaires

Cette conception modulaire s'aligne parfaitement avec l'architecture globale du projet Madsea, permettant une évolution indépendante du module OCR sans impacter les autres composants.