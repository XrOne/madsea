# Rapport de Structure du Projet Madsea

## Présentation générale

Madsea est une application conçue pour transformer des storyboards en séquences visuelles stylisées par IA, en respectant la composition originale et en permettant différents styles visuels, principalement le style "Ombres Chinoises" pour la série "Déclic".

## Architecture globale

L'application se compose de trois composants principaux :

1. **Backend Flask** : Services modulaires pour l'extraction, la transformation et la gestion des fichiers
2. **Frontend** : Interface utilisateur simple et efficace
3. **Intégration ComfyUI** : Moteur de génération d'images stylisées

## Structure des dossiers

```
i:\Madsea\
├── backend\                      # Backend Flask
│   ├── app.py                    # Point d'entrée principal
│   ├── extraction_api.py         # API d'extraction PDF
│   ├── projects_api.py           # Gestion des projets
│   ├── comfyui_api.py            # API ComfyUI
│   └── comfyui_bridge.py         # Communication avec ComfyUI
├── ComfyUI\                      # Installation ComfyUI
│   ├── models\                   # Modèles IA
│   └── workflows\                # Templates de workflow
│       └── Windsurf_Template.json # Workflow pour Ombres Chinoises
├── declics\                      # Références et exemples
│   └── ombre chinoise\           # Style Ombres Chinoises
├── docs\                         # Documentation
│   ├── 004-definition-sequences-plans-styles.md
│   ├── GUIDE_COMFYUI_MADSEA.md
│   └── RAPPORT_STRUCTURE_PROJET.md
├── frontend\                     # Frontend React/Vite (en pause)
│   └── index.html
├── front madsea\                 # Frontend HTML actif
│   └── deepsitefront.html        # Interface principale
├── parsing\                      # Modules d'extraction
├── projects\                     # Données des projets
└── scripts\                      # Scripts utilitaires
    └── install_comfyui_models.ps1 # Installation des modèles
```

## Composants principaux

### 1. Backend Flask

Le backend est composé de plusieurs modules :

- **app.py** : Application Flask principale, point d'entrée qui enregistre tous les blueprints
- **extraction_api.py** : Extraction et OCR des PDFs de storyboard
- **projects_api.py** : Gestion des projets, épisodes et séquences
- **comfyui_api.py** : Endpoint `/api/comfyui/process_plans` pour traiter les plans avec ComfyUI
- **comfyui_bridge.py** : Module de communication avec l'API ComfyUI

Le backend implémente une API RESTful JSON pour toutes les opérations.

### 2. Frontend

Deux implémentations frontend existent :

- **Frontend HTML simple** (`front madsea/deepsitefront.html`) : Interface active et fonctionnelle
- **Frontend React/Vite** (`frontend/index.html`) : Version plus avancée, actuellement en pause

L'interface permet :
- L'upload de PDFs
- La visualisation des plans extraits
- La modification des numéros de séquence
- La sélection des plans à traiter
- L'envoi vers ComfyUI pour génération

### 3. Intégration ComfyUI

L'intégration avec ComfyUI se fait via :

- **comfyui_bridge.py** : Module qui gère la communication avec l'API ComfyUI
- **Windsurf_Template.json** : Workflow optimisé pour le style "Ombres Chinoises"
- **Models** : SDE-LCM 3.2, ControlNet UHD v2.5, ShadowCraft XL LoRA, IP-Adapter

Cette intégration permet de transformer automatiquement les plans extraits en respectant le style "Ombres Chinoises" tout en préservant la composition originale.

## Workflow utilisateur

1. Création d'un projet (avec saison/épisode)
2. Upload d'un PDF de storyboard
3. Visualisation des plans extraits
4. Modification des numéros de séquence si nécessaire
5. Sélection des plans à traiter
6. Envoi vers ComfyUI
7. Validation des résultats

## État du projet

- **✅ Fonctionnel** : Backend Flask, extraction PDF, frontend simple, OCR
- **✅ Implémenté** : Intégration ComfyUI, pipeline de génération
- **🔄 En cours** : Installation des modèles spécifiques, optimisation du workflow
- **⏳ Plannifié** : Interface de validation, export de séquences

## Objectif actuel

Production de 70 plans en style "Ombres Chinoises" sur 10 jours pour la série "Déclic".

## Documentation

La documentation du projet est disponible dans le dossier `docs/` et comprend :
- Guides d'utilisation
- Documentation technique
- Spécifications des styles visuels
- Définitions des concepts (plans, séquences)