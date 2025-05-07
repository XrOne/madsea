# Guide d'installation et utilisation ComfyUI - Madsea

## 1. Présentation

Ce guide vous aide à installer et configurer tous les modèles nécessaires pour utiliser le workflow "ombre chinoise" dans ComfyUI avec Madsea.

## 2. Structure des dossiers

```
Madsea/
├── ComfyUI/
│   ├── models/
│   │   ├── checkpoints/        # Modèles principaux
│   │   │   └── RealVisXL.safetensors
│   │   ├── controlnet/         # Modèles ControlNet
│   │   │   ├── diffusion_xl_depth.safetensors
│   │   │   ├── control_sd_xl_canny.safetensors
│   │   │   └── diffusion_xl_openpose.safetensors
│   │   └── lora/               # LoRA pour stylisation
│   │       ├── silhouette_photographic_style_lora.safetensors
│   │       └── epiNoiseoffset_v2.safetensors
│   └── workflows/              # Workflows prédéfinis
│       └── Windsurf_Template.json
├── scripts/                    # Scripts d'installation et d'automatisation
│   └── install_comfyui_models.ps1
└── styles/                     # Configuration des styles
    ├── cinematic.json
    ├── declic.json
    └── declic_ombre_chinoise.json
```

## 3. Installation automatique

### Méthode 1 : Via PowerShell (Windows)

1. Ouvrez PowerShell (clic droit sur le menu Démarrer > Windows PowerShell)
2. Naviguez jusqu'au dossier Madsea :
   ```powershell
   cd I:\Madsea
   ```
3. Exécutez le script d'installation :
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/install_comfyui_models.ps1
   ```

### Méthode 2 : Installation manuelle

Si le script ne fonctionne pas, téléchargez manuellement les fichiers suivants :

#### Modèles principaux (dans `ComfyUI/models/checkpoints/`)
- RealVisXL.safetensors : [HuggingFace](https://huggingface.co/SG161222/RealVisXL/resolve/main/RealVisXL.safetensors)

#### ControlNet (dans `ComfyUI/models/controlnet/`)
- diffusion_xl_depth.safetensors : [HuggingFace](https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/diffusion_xl_depth.safetensors)
- control_sd_xl_canny.safetensors : [HuggingFace](https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_sd_xl_canny.safetensors)
- diffusion_xl_openpose.safetensors : [HuggingFace](https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/diffusion_xl_openpose.safetensors)

#### LoRA (dans `ComfyUI/models/lora/`)
- silhouette_photographic_style_lora.safetensors : [HuggingFace](https://huggingface.co/DoctorDiffusion/doctor-diffusion-s-stylized-silhouette-photography-xl-lora/resolve/main/DD-sli-v1.safetensors)
- epiNoiseoffset_v2.safetensors : [CivitAI](https://civitai.com/api/download/models/13941)

## 4. Utilisation du workflow

1. Démarrez ComfyUI (depuis la racine ComfyUI) :
   ```bash
   python main.py
   ```

2. Dans l'interface web (http://localhost:8188 par défaut) :
   - Cliquez sur "Load" dans le menu supérieur
   - Chargez le fichier `Windsurf_Template.json` depuis `ComfyUI/workflows/`

3. Configurez les paramètres dans les nœuds :
   - `load_image` : Chemin de l'image du storyboard
   - `prompt_main` : Prompt positif/négatif
   - `save_image` : Chemin de sauvegarde

4. Cliquez sur le nœud `save_image` pour lancer la génération

## 5. Nomenclature des fichiers

Format : `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`
Exemple : `E202_SQ0010-0010_AI-concept_v0001.png`

## 6. Dépannage

- **LoRA manquant** : Vérifiez les noms exacts dans le workflow; ils doivent correspondre aux fichiers téléchargés
- **Erreur ComfyUI** : Consultez les logs dans la console
- **Erreurs d'installation** : Téléchargez manuellement les fichiers en utilisant les liens fournis

## 7. Pour aller plus loin

- Consultez la documentation ComfyUI pour ajouter d'autres modèles ou styles
- Explorez le dossier `styles/` pour d'autres préréglages comme `declic.json`
