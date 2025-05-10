# Documentation des Scripts et OCR Madsea

## 1. Architecture Globale des Scripts

L'architecture des scripts de Madsea suit une organisation modulaire et cohérente, facilitant la maintenance et le déploiement sur différents environnements.

```
i:\Madsea\
├── scripts/                    # Scripts utilitaires
│   ├── check_integrity.bat     # Vérifie l'intégrité de l'installation
│   ├── install_tesseract.bat   # Guide d'installation de Tesseract
│   ├── portable_install.bat    # Prépare une version portable
│   ├── archive_workflow.ps1    # Archivage des workflows
│   └── clean_outputs.ps1       # Nettoyage des sorties
├── backend/                    # Backend Flask
│   ├── app.py                  # Point d'entrée principal
│   ├── extraction_api.py       # API d'extraction PDF
│   └── services/               # Services modulaires
│       └── ocr_manager.py      # Gestionnaire OCR portable
├── config/                     # Configuration centralisée
│   ├── default.yaml            # Configuration générale
│   └── ocr_config.json         # Configuration OCR spécifique
└── start_madsea.bat            # Script de démarrage principal
```

## 2. Objectifs et Fonctionnement des Scripts

### `start_madsea.bat` - Script Principal de Démarrage

**Objectif** : Lance tous les composants de l'application Madsea dans le bon ordre.

**Fonctionnement** :
1. Vérifie les prérequis (Tesseract, Python, dépendances)
2. Démarre ComfyUI (port 8188)
3. Démarre le backend Flask (port 5000)
4. Démarre le frontend React (port 5173)
5. Ouvre les interfaces dans le navigateur

**Exécution** : `i:\Madsea\start_madsea.bat`

### `scripts\check_integrity.bat` - Vérification de l'Installation

**Objectif** : Valide que tous les composants nécessaires sont installés et fonctionnels.

**Fonctionnement** :
1. Vérifie la présence de Tesseract OCR
2. Teste les dépendances Python
3. Confirme l'existence des dossiers critiques

**Exécution** : `i:\Madsea\scripts\check_integrity.bat`

### `scripts\install_tesseract.bat` - Installation de Tesseract

**Objectif** : Guide l'utilisateur pour installer Tesseract OCR.

**Fonctionnement** :
1. Vérifie si Chocolatey est disponible
2. Propose l'installation manuelle ou via Chocolatey
3. Configure Tesseract pour Madsea

**Exécution** : `i:\Madsea\scripts\install_tesseract.bat`

### `scripts\portable_install.bat` - Préparation Version Portable

**Objectif** : Crée une version portable de Madsea pour distribution.

**Fonctionnement** :
1. Copie Tesseract dans un dossier embarqué
2. Configure l'application pour utiliser Tesseract embarqué
3. Crée un script de lancement portable

**Exécution** : `i:\Madsea\scripts\portable_install.bat`

## 3. Service OCR Modulaire

Le service OCR a été conçu comme un module indépendant, suivant les principes d'architecture modulaire de Madsea.

### `backend\services\ocr_manager.py`

**Objectif** : Fournir une API unifiée pour l'OCR, indépendante de l'installation système.

**Caractéristiques clés** :
- Détection automatique de Tesseract dans multiples emplacements
- Configuration externalisée via JSON
- Support pour mode embarqué (portable)
- API simplifiée pour l'extraction

**Utilisation dans le code** :
```python
from services.ocr_manager import extract_text_from_image

# Simple appel de fonction
text = extract_text_from_image(image_path)
```

## 4. Configuration OCR

La configuration OCR est externalisée dans un fichier JSON pour faciliter les modifications sans changer le code.

### `config\ocr_config.json`

**Objectif** : Centraliser les paramètres OCR.

**Structure** :
```json
{
    "tesseract_paths": [
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "%MADSEA_HOME%\\ocr\\tesseract.exe"
    ],
    "embedded_mode": false,
    "languages": ["fra", "eng"],
    "default_lang": "fra"
}
```

**Paramètres clés** :
- `tesseract_paths` : Liste des chemins possibles (ordre de priorité)
- `embedded_mode` : Active le mode portable
- `languages` : Langues OCR supportées

## 5. Workflow de Développement et Déploiement

### Développement Local

1. **Installation** : Installer Tesseract via `install_tesseract.bat`
2. **Vérification** : Exécuter `check_integrity.bat`
3. **Lancement** : Démarrer avec `start_madsea.bat`
4. **Tests** : Valider l'extraction OCR via l'interface

### Déploiement chez un Client

1. **Préparation** : Exécuter `portable_install.bat`
2. **Distribution** : Copier le dossier Madsea complet
3. **Installation Client** : Le client exécute `portable\start_madsea_portable.bat`

## 6. Structure des Dossiers Clés

### `/ocr` - Tesseract Embarqué

Contient une installation portable de Tesseract pour distribution :
- `tesseract.exe` : Exécutable principal
- `*.dll` : Bibliothèques requises
- `tessdata/*.traineddata` : Données de langues (fra, eng)

### `/temp` - Fichiers Temporaires

Stockage temporaire pour les fichiers en cours de traitement :
- PDF uploadés avant extraction
- Images intermédiaires
- Données de traitement

### `/uploads` - Fichiers Uploadés

Destination temporaire des fichiers uploadés via l'interface.

### `/outputs` - Résultats Générés

Organisation des résultats selon la nomenclature standardisée :
```
outputs/
└── E202/                  # Épisode
    └── SQ0010/            # Séquence
        ├── extracted-raw/ # Images extraites
        └── AI-concept/    # Images générées
```

## 7. Nomenclature des Fichiers

La nomenclature des fichiers respecte le format standardisé :

```
E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}
```

Exemple : `E202_SQ0010-0010_AI-concept_v0001.png`

Cette structure garantit la traçabilité et la cohérence des fichiers générés.