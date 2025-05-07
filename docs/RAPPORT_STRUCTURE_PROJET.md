# Rapport d'Analyse - Structure du Projet Madsea

## 1. Vue d'ensemble

Le projet Madsea est une application permettant de transformer des storyboards en séquences visuelles stylisées via l'IA, en respectant la composition et permettant différents styles visuels. L'organisation du projet suit une architecture modulaire avec plusieurs composants clés.

## 2. Structure des dossiers principaux

### Racine du projet
- `.git`, `.gitignore` : Configuration Git pour le versionnage
- `.venv` : Environnement virtuel Python
- `main.py` et `startup.py` : Points d'entrée de l'application

### Composants principaux
- `backend/` : API Flask pour le traitement des données et l'extraction
- `front madsea/` : Frontend HTML/JS actif (DeepSite)
- `frontend/` : Frontend React/Vite (actuellement désactivé)
- `ComfyUI/` : Intégration avec ComfyUI pour la génération d'images
- `scripts/` : Scripts d'automatisation et d'installation

### Ressources et données
- `models/` : Modèles IA pour la génération
- `outputs/` : Images générées et résultats
- `docs/` : Documentation du projet
- `pdf storyboard/` : Exemples et fichiers de storyboard

## 3. Analyse détaillée des composants

### 3.1 Backend (Flask)
- **Structure** : Architecture Flask avec blueprints (API modulaire)
- **Modules principaux** :
  - `app.py` : Application principale Flask
  - `extraction_api.py` : Gestion de l'extraction des images depuis PDF
  - `projects_api.py` : Gestion des projets et méta-données
  - `services/` : Services métier (extraction, gestion de fichiers)

- **Configuration** :
  - Port : 5000
  - CORS activé pour les requêtes cross-origin
  - Dossier d'upload configuré

### 3.2 Frontend
#### 3.2.1 Front Madsea (DeepSite) - ACTIF
- **Type** : Interface HTML/JS simple
- **Fichiers clés** :
  - `index.html` : Page principale
  - `preview_selection_restylage.html` : Prévisualisation du restylage
  - `validation_button.js` : Script de validation

#### 3.2.2 Frontend React/Vite - DÉSACTIVÉ
- **Type** : Application React moderne avec Vite
- **Structure** :
  - `package.json` : Configuration npm et scripts
  - `src/` : Code source React
  - `public/` : Assets statiques

### 3.3 ComfyUI
- **Intégration** :
  - `workflows/` : Workflows préconfigurés (dont Windsurf_Template.json)
  - `models/` : Stockage des modèles IA
- **Fichiers clés** :
  - `main.py` : Point d'entrée de ComfyUI
  - `Windsurf_ComfyUI_Workflow_Template.json` : Template pour "ombre chinoise"

### 3.4 Scripts
- `install_comfyui_models.ps1` : Installation automatisée des modèles
- `start_servers.sh` : Démarrage des serveurs (backend et ComfyUI)
- Autres scripts d'installation et de nettoyage

## 4. Fichiers de configuration
- `requirements.txt` : Dépendances Python
- `.gitignore` : Configuration des exclusions Git
- `.windsurfrules` : Règles et configuration du projet

## 5. Documentation
- `docs/GUIDE_COMFYUI_MADSEA.md` : Guide d'utilisation de ComfyUI
- `docs/MODELES_COMFYUI_URLS.md` : Liens vers les modèles à télécharger
- `README.md` et autres fichiers d'information

## 6. Workflow fonctionnel

Le workflow de Madsea fonctionne ainsi :
1. **Upload** : L'utilisateur charge un storyboard PDF via l'interface DeepSite
2. **Extraction** : Le backend extrait les images du PDF
3. **Traitement** : Les images sont envoyées à ComfyUI pour application du style
4. **Stockage** : Les images générées sont nommées selon la convention `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`
5. **Visualisation** : L'utilisateur peut prévisualiser et valider les résultats

## 7. État actuel

- Backend Flask fonctionnel sur http://localhost:5000
- Frontend DeepSite actif via `front madsea/index.html`
- ComfyUI intégré mais nécessite l'installation des modèles
- Nomenclature standardisée implémentée

## 8. Prochaines étapes recommandées

1. **Tester l'extraction PDF** vers ComfyUI
2. **Vérifier la nomenclature** des fichiers générés
3. **Installer tous les modèles** nécessaires via `install_comfyui_models.ps1`
4. **Explorer le dossier `styles/`** pour les configurations de style
