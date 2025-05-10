# Journal de Bord - Projet Madsea

## Dernière mise à jour : 2025-05-10

### 2025-05-10 : Implémentation OCR Modulaire et Portable
- **Problème initial** : Tesseract OCR non détecté correctement, absence d'installation portable
- **Solution** : 
  - Mise en place d'un gestionnaire OCR modulaire (`backend/services/ocr_manager.py`)
  - Configuration externalisée dans `config/ocr_config.json`
  - Support pour installation embarquée via `scripts/portable_install.bat`
  - Documentation complète du module OCR et des scripts dans `doc/`
- **Responsable** : Équipe dev backend
- **Statut** : ✅ Complété

### 2025-05-08 : Consolidation Frontend et Structure
- **Modifications** :
  - Le frontend principal de Madsea est désormais situé dans le dossier `frontend/` sous le nom `index.html` (ex-DeepSite migré)
  - Le dossier `front madsea` n'existe plus ou est vide
  - Toute la documentation, les guides et les workflows doivent pointer vers `frontend/index.html` comme unique interface utilisateur
  - Le dossier `frontend/` ne contient plus de version React/Vite active, mais la version HTML/React simple (DeepSite migré)
- **Responsable** : Équipe frontend
- **Statut** : ✅ Complété

### 2025-05-01 : Intégration ComfyUI et Extraction PDF
- **Développements** :
  - API backend complète pour l'extraction PDF avec OCR
  - Configuration initiale de l'intégration ComfyUI 
  - Interfaces pour la génération d'images basées sur les storyboards extraits
- **Problèmes résolus** :
  - Format de nomenclature standardisé
  - Gestion des uploads multi-pages
  - Analyse du texte et extraction des métadonnées de plan
- **Responsable** : Équipe backend
- **Statut** : ✅ Complété

### 2025-04-24 : Mise en place de l'Architecture Initiale
- **Développements** :
  - Structure de dossier définie
  - Configuration du backend Flask
  - Mise en place du pipeline d'extraction
  - Définition de la nomenclature des fichiers
- **Décisions techniques** :
  - Utilisation de PyMuPDF pour extraction PDF
  - Tesseract OCR pour reconnaissance de texte
  - ComfyUI comme moteur de génération d'images
- **Responsable** : Équipe architecture
- **Statut** : ✅ Complété