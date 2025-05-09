# Guide d'Intégration ComfyUI pour Madsea

## Introduction

Ce guide détaille le processus d'intégration de ComfyUI avec Madsea pour la génération d'images en style "Ombres Chinoises" pour la série "Déclic". Il couvre l'installation, la configuration et l'utilisation du workflow optimisé.

## Table des matières

1. [Structure des dossiers](#structure-des-dossiers)
2. [Installation des modèles](#installation-des-modèles)
3. [Workflow ComfyUI](#workflow-comfyui)
4. [Intégration avec le backend Madsea](#intégration-avec-le-backend-madsea)
5. [Nomenclature des fichiers](#nomenclature-des-fichiers)
6. [Troubleshooting](#troubleshooting)

## Structure des dossiers

L'intégration ComfyUI utilise la structure de dossiers suivante :

```
i:\Madsea\
├── ComfyUI\                      # Installation ComfyUI
│   ├── models\                   # Dossier des modèles
│   │   ├── checkpoints\          # Modèles principaux (SDE-LCM 3.2)
│   │   ├── controlnet\           # ControlNets UHD v2.5
│   │   ├── lora\                 # LoRA silhouette
│   │   ├── embeddings\           # Embeddings additionnels
│   │   └── ipadapter\            # Modèles IP-Adapter
│   └── workflows\                # Templates de workflow
│       └── Windsurf_Template.json # Template optimisé pour Madsea
├── backend\                      # Backend Madsea
│   ├── comfyui_bridge.py         # Module de communication avec ComfyUI
│   └── comfyui_api.py            # Endpoints API pour ComfyUI
├── declics\                      # Références et exemples 
│   └── ombre chinoise\           # Images de référence pour le style
└── scripts\                      # Scripts utilitaires
    └── install_comfyui_models.ps1 # Script d'installation des modèles
```

## Installation des modèles

Pour installer les modèles requis :

1. **Option automatique** (recommandée) :
   - Exécutez le script PowerShell : `i:\Madsea\scripts\install_comfyui_models.ps1`
   - Ce script télécharge automatiquement tous les modèles nécessaires et les place dans les bons dossiers

2. **Option manuelle** :
   - Téléchargez les modèles depuis les URLs suivantes :
     - SDE-LCM 3.2 : [lien](https://huggingface.co/stabilityai/stable-diffusion-3-large-lcm/resolve/main/sde-lcm-3.2.safetensors)
     - ControlNet UHD Canny : [lien](https://huggingface.co/lllyasviel/sd-controlnet-collection/resolve/main/controlnet_uhd_canny_v2.5.safetensors)
     - ControlNet UHD Depth : [lien](https://huggingface.co/lllyasviel/sd-controlnet-collection/resolve/main/controlnet_uhd_depth_v2.5.safetensors)
     - ControlNet UHD Pose : [lien](https://huggingface.co/lllyasviel/sd-controlnet-collection/resolve/main/controlnet_uhd_pose_v2.5.safetensors)
     - ShadowCraft XL LoRA : [lien](https://huggingface.co/artistvision/shadowcraft-xl-lora/resolve/main/shadowcraft-xl-v2.1.safetensors)
     - IP-Adapter Plus v2 : [lien](https://huggingface.co/h94/IP-Adapter-Plus-XL/resolve/main/ip_adapter_plus_v2.safetensors)
     - CinematicEdge : [lien](https://huggingface.co/cinematicai/embeddings/resolve/main/cinematicedge.pt)
   - Placez-les dans les dossiers appropriés de la structure décrite ci-dessus

## Workflow ComfyUI

Le workflow Madsea utilise une combinaison optimisée pour le style "Ombres Chinoises" :

1. **Modèle de base** : SDE-LCM 3.2 (génération rapide en 2-4 étapes)
2. **Contrôle de composition** : ControlNet UHD v2.5 pour préserver la structure du storyboard
3. **Style ombres chinoises** : ShadowCraft XL LoRA pour l'effet silhouette distinctif
4. **Référence de style** : IP-Adapter avec exemples du dossier `declics/ombre chinoise/`
5. **Amélioration** : Embedding CinematicEdge pour qualité visuelle cinématographique

Le fichier `Windsurf_Template.json` dans `i:\Madsea\ComfyUI\workflows\` contient cette configuration. Il est automatiquement utilisé par le backend Madsea pour chaque plan envoyé à ComfyUI.

## Intégration avec le backend Madsea

L'intégration entre Madsea et ComfyUI fonctionne comme suit :

1. L'utilisateur sélectionne des plans dans l'interface Madsea et clique sur "Envoyer à ComfyUI"
2. Le backend prépare les données via `comfyui_bridge.py` :
   - Renomme les fichiers selon la nomenclature si les numéros de séquence ont été modifiés
   - Charge le workflow template (`Windsurf_Template.json`)
   - Y injecte l'image source et autres paramètres spécifiques au plan
   - Sélectionne aléatoirement une image de référence du dossier `declics/ombre chinoise/`
3. Le backend envoie le workflow à ComfyUI via son API
4. ComfyUI génère l'image en style "Ombres Chinoises"
5. Le backend récupère l'image générée et met à jour les informations du plan

## Nomenclature des fichiers

La nomenclature stricte des fichiers est respectée à toutes les étapes :

```
E{saison_episode}_SQ{sequence}-{plan}_{tache}_v{version}.{extension}
```

Exemple : `E202_SQ0010-0010_AI-concept_v0001.png`

- `E{saison_episode}` : Identifiant saison et épisode (ex: E202)
- `SQ{sequence}` : Identifiant de séquence sur 4 chiffres (ex: SQ0010)
- `{plan}` : Identifiant de plan sur 4 chiffres, incrémenté de 10 (ex: 0010, 0020)
- `{tache}` : Type de fichier/traitement
  - `extracted-raw` : Image extraite du PDF storyboard
  - `AI-concept` : Image générée par ComfyUI
- `v{version}` : Indicateur de version, 'v' minuscule, 4 chiffres (ex: v0001)

Cette nomenclature est appliquée automatiquement par `comfyui_bridge.py` lors de la génération.

## Troubleshooting

### Problèmes courants et solutions

1. **Erreur "Model not found" dans ComfyUI** :
   - Vérifiez que tous les modèles sont bien présents dans les dossiers appropriés
   - Relancez ComfyUI pour qu'il détecte les nouveaux modèles

2. **Problème de communication entre Madsea et ComfyUI** :
   - Vérifiez que ComfyUI est bien lancé et accessible à l'URL `http://127.0.0.1:8188`
   - Si ComfyUI utilise un port différent, modifiez `COMFYUI_API_URL` dans `comfyui_bridge.py`

3. **Style "Ombres Chinoises" non conforme aux attentes** :
   - Ajoutez de nouvelles images de référence dans le dossier `declics/ombre chinoise/`
   - Ajustez les paramètres du LoRA dans le workflow template

4. **Workflow trop lent** :
   - Réduisez le nombre d'étapes de génération (SDE-LCM 3.2 peut fonctionner avec seulement 2-4 étapes)
   - Utilisez une résolution plus basse pour les tests, puis faites un upscaling si nécessaire

### Installation des dépendances avec UV

UV est le gestionnaire de paquets Python recommandé pour ce projet, offrant des installations plus rapides et plus fiables que pip.

Pour installer UV (si ce n'est pas déjà fait) :
```
pip install -U uv
```

Pour installer toutes les dépendances ComfyUI avec UV :
```
cd i:\Madsea\ComfyUI\
uv pip install -r requirements.txt
```

Pour installer les dépendances du backend Madsea :
```
cd i:\Madsea\backend\
uv pip install flask flask-cors pymupdf pillow requests
```

### Commandes utiles

Pour lancer ComfyUI :
```
cd i:\Madsea\ComfyUI\
python main.py
```

Pour lancer le backend Madsea :
```
cd i:\Madsea\backend\
python app.py
```

Pour lancer le frontend :
```
cd i:\Madsea\frontend\
python -m http.server 8000
```