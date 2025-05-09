# Guide de démarrage Madsea - Pipeline d'industrialisation

## Résumé exécutif
Guide complet pour démarrer le pipeline Madsea, incluant l'extraction de storyboards, la génération AI via ComfyUI bridge, et la validation des plans selon la nomenclature standardisée.

---

## 1. Prérequis et installation

### Dépendances principales
- Python 3.10+ avec packages:
  - Flask (backend)
  - PyMuPDF (extraction PDF)
  - safetensors, torch (ComfyUI)
  - Pillow, aiohttp (traitement images et API)

### Structure vérifiée
- `backend/` : Backend Flask avec extraction API et bridge ComfyUI
- `ComfyUI/` : Moteur de génération d'images (sans modèles dans Git)
- `frontend/` : Interface React/TailwindCSS unique (migration DeepSite complète)
- `document/` : Documentation à jour du projet
- `scripts/` : Scripts d'automatisation et utilitaires

## 2. Démarrage du système

### Méthode 1 : Script automatisé
```bash
# Double-cliquer sur le fichier batch
i:\Madsea\start_madsea.bat
```

### Méthode 2 : Démarrage manuel
```bash
# Terminal 1 : Backend avec bridge ComfyUI
cd i:\Madsea\backend
python app.py

# Terminal 2 : ComfyUI
cd i:\Madsea\ComfyUI
python main.py

# Navigateur : Frontend
http://localhost:5000
```

## 3. Workflow d'industrialisation

### Étape 1 : Import et extraction
1. Accéder à http://localhost:5000
2. Importer un storyboard PDF
3. Validation extraction avec nomenclature standardisée

### Étape 2 : Sélection et configuration
1. Sélectionner les plans à générer
2. Configurer le style (Ombres Chinoises)
3. Vérifier les séquences et numéros de plans

### Étape 3 : Génération via bridge
1. Lancer la génération par le bridge ComfyUI
2. Suivre la progression dans l'interface
3. Vérifier les images générées et leur nomenclature

### Étape 4 : Export et validation
1. Exporter les séquences finalisées
2. Vérifier le respect de la nomenclature `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`
3. Visualiser le résultat final

## 4. Points techniques importants

- **Backend (port 5000)** : Sert l'API ET l'interface utilisateur
- **ComfyUI (port 8188)** : Interface indépendante disponible mais généralement utilisée via bridge
- **Bridge ComfyUI** : Intégré au backend, gère la communication automatisée
- **Logs** : Disponibles dans les terminaux et l'interface

## 5. Dépannage rapide

- **Erreur 'extraction_bp not defined'** : Corrigée par l'ajout du Blueprint dans `extraction_api.py`
- **Erreur 'No module named safetensors'** : Installer via `pip install safetensors torch`
- **Frontend inaccessible** : Vérifier que le backend est bien lancé sur le port 5000
- **ComfyUI non réactif** : Vérifier que le serveur ComfyUI est bien lancé sur le port 8188

---

**Structure de l'industrialisation : 70 plans en 10 jours**  
En suivant ce workflow, l'équipe peut générer environ 10 plans par jour, avec validation intégrée et respect strict de la nomenclature.
