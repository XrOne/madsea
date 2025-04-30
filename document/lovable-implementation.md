# Guide d'implémentation Lovable pour Madsea

Ce guide détaille comment implémenter progressivement l'application Madsea en utilisant Lovable.dev pour accélérer le développement tout en maintenant la qualité et l'extensibilité.

## Préparation et configuration initiale

### 1. Configuration du projet Lovable

1. Connectez-vous à [Lovable.dev](https://lovable.dev)
2. Créez un nouveau projet en fournissant le prompt technique (voir section dédiée)
3. Configurez les services essentiels :
   - Base de données SQLite (local) ou PostgreSQL (via Supabase)
   - Stockage de fichiers local

### 2. Préparation du frontend existant

1. Analysez la structure de l'interface HTML/TailwindCSS/React existante
2. Identifiez les composants réutilisables
3. Préparez les assets statiques (logos, icônes)

### 3. Configuration de l'environnement local

1. Installez les dépendances nécessaires pour ComfyUI :
   ```bash
   # Installation des dépendances Python
   pip install torch torchvision torchaudio
   pip install fastapi uvicorn pillow numpy opencv-python pymupdf pytesseract
   
   # Clonage et configuration de ComfyUI
   git clone https://github.com/comfyanonymous/ComfyUI
   cd ComfyUI
   pip install -r requirements.txt
   ```

2. Téléchargez les modèles de base (ceux-ci devront être placés dans le dossier `models` de ComfyUI) :
   - Stable Diffusion 1.5 ou XL : [huggingface.co/runwayml/stable-diffusion-v1-5](https://huggingface.co/runwayml/stable-diffusion-v1-5)
   - ControlNet Canny : [huggingface.co/lllyasviel/ControlNet-v1-1](https://huggingface.co/lllya