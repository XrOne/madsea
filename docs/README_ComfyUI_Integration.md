# Intégration et Exécution d'un Workflow ComfyUI pour Madsea

Ce document détaille les étapes précises pour intégrer et exécuter un workflow JSON dans ComfyUI, en partant du principe que ComfyUI est déjà installé sur votre machine (par exemple, via WSL avec accès GPU).

Le processus général est le suivant : placer le fichier JSON du workflow dans un répertoire accessible, s'assurer que les modèles requis sont dans les bons dossiers de ComfyUI, configurer les variables d'environnement si nécessaire, installer les dépendances Python, lancer ComfyUI, charger le workflow, régler les variables (placeholders) et enfin, exécuter le workflow.

## 1. Préparer votre environnement ComfyUI

1.  **Vérifiez que ComfyUI est installé.** (Si vous avez cloné un dépôt comme SwarmUI qui l'inclut, c’est probablement déjà fait).
2.  **Positionnez-vous** dans le dossier racine de ComfyUI. Si Madsea utilise l'instance dans `i:\Madsea\ComfyUI`, le chemin serait adapté à votre environnement d'exécution (ex: `cd /mnt/i/Madsea/ComfyUI` depuis WSL, ou le chemin direct si ComfyUI tourne nativement sur Windows).
    ```bash
    # Exemple pour WSL, adaptez selon votre installation
    cd /mnt/i/Madsea/ComfyUI 
    ```
3.  **Activez votre environnement virtuel Python (`venv`)** si vous en utilisez un pour ComfyUI :
    ```bash
    source venv/bin/activate 
    # Sur Windows: .\venv\Scripts\activate
    ```
4.  **Installez les dépendances** si ce n'est pas déjà fait (ou pour mettre à jour) :
    ```bash
    pip install -r requirements.txt
    ```

## 2. Placer les modèles

Assurez-vous que les modèles nécessaires (checkpoints, LoRA, ControlNet, etc.) sont placés dans les sous-dossiers appropriés de `ComfyUI/models/`. Voici une structure d'exemple basée sur les besoins courants pour des styles comme "Ombre Chinoise" avec SDXL :

```plaintext
ComfyUI/models/
├── checkpoints/ # Modèles principaux (Stable Diffusion)
│   ├── sdxl_base_1.0.safetensors
│   ├── sdxl_refiner_1.0.safetensors
│   ├── juggernaut_xl.safetensors
│   └── RealisticVisionXL.safetensors
├── loras/       # Modèles LoRA
│   ├── silhouette_photographic_style_lora.safetensors
│   └── rimlight_lora.safetensors
└── controlnet/  # Modèles ControlNet
    ├── diffusion_xl_depth.safetensors
    ├── control_sd_xl_canny.safetensors
    └── diffusion_xl_openpose.safetensors
```

*Note : Adaptez les noms de fichiers et les types de modèles en fonction des exigences exactes de vos workflows.* Le fichier `i:\Madsea\config\default.yaml` peut aussi spécifier des modèles par défaut.

## 3. Placer le workflow JSON

1.  Les workflows Madsea (comme `Windsurf_ComfyUI_Workflow_Template.json`) sont stockés dans `i:\Madsea\Workflow\`.
2.  Lorsque le backend Madsea interagit avec ComfyUI, il chargera ces workflows via l'API de ComfyUI. Pour un usage manuel ou des tests directs dans ComfyUI, vous pouvez copier un workflow spécifique (par exemple, `Windsurf_ComfyUI_Workflow_Template.json`) dans un sous-dossier de votre installation ComfyUI, par exemple `ComfyUI/workflows_madsea/` pour les garder organisés, ou le charger directement depuis son emplacement original via l'interface de ComfyUI si l'accès est possible.

## 4. Lancer ComfyUI

1.  Depuis votre terminal (avec l'environnement virtuel activé et dans le dossier racine de ComfyUI) :
    ```bash
    python main.py
    ```
2.  Par défaut, ComfyUI est accessible via un navigateur web à l'adresse `http://127.0.0.1:8188` (ou un port similaire si celui-ci est déjà utilisé, comme configuré dans `i:\Madsea\config\default.yaml`).

## 5. Importer et Charger un Workflow (pour test manuel)

1.  Dans l’interface web de ComfyUI, cliquez sur le bouton **Load** (ou **File → Load workflow** selon les versions).
2.  Naviguez jusqu’au fichier JSON de votre workflow (ex: `i:\Madsea\Workflow\Windsurf_ComfyUI_Workflow_Template.json`) et ouvrez-le.
3.  Le graphe des nœuds du workflow devrait apparaître dans la zone centrale de l'interface.

## 6. Configurer les « Placeholders » (Variables Dynamiques)

Les workflows Madsea sont conçus pour être dynamiques. Le backend Madsea remplira ces placeholders lors de l'exécution automatisée. Pour un test manuel, vous devrez les renseigner dans l'interface ComfyUI :

*   **`storyboard_image_path`** : Chemin absolu vers l'image de storyboard (ex: `/mnt/i/Madsea/projects/PROJ001/EP001/SQ0010/E001_SQ0010-0010_REF_v0001.png`).
*   **`prompt_text`** : Prompt principal pour la génération.
*   **`negative_prompt`** : Prompt négatif.
*   **`output_filename_prefix`** : Préfixe du nom de fichier de sortie (ComfyUI ajoutera souvent des informations comme le seed ou le numéro de batch). Le backend Madsea gérera la nomenclature finale pour respecter `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`.
*   **`seed`** (optionnel) : Pour la reproductibilité. Un entier.

**Pour remplir manuellement dans ComfyUI :**

1.  Localisez les nœuds qui utilisent ces placeholders (souvent des nœuds `LoadImage`, des champs de texte pour les prompts, ou des nœuds `SaveImage`).
2.  Cliquez sur le nœud concerné.
3.  Dans le panneau de propriétés du nœud (souvent à gauche ou en pop-up), modifiez les valeurs des champs correspondants.
    *   **LoadImage** : Mettez à jour le champ `image` avec le chemin de votre image de storyboard.
    *   **CLIPTextEncode (Prompt)** : Entrez vos textes dans les champs `text` (pour le prompt positif et négatif).
    *   **SaveImage** : Ajustez le `filename_prefix`.

## 7. Ajuster les Paramètres GPU (si nécessaire)

1.  Dans le menu latéral de ComfyUI (souvent une icône d'engrenage ou un menu "Settings") :
    *   **CUDA Device** : Sélectionnez votre GPU (ex: `TITAN X Pascal`).
    *   Cochez **Use low VRAM mode** si votre GPU a une VRAM limitée, pour activer des optimisations.
2.  Vérifiez que la résolution dans les nœuds de génération (ex: `EmptyLatentImage` ou `KSampler`) correspond à vos attentes (ex: 1920x1080 ou un format adapté à SDXL).

## 8. Exécuter le Workflow (pour test manuel)

1.  Cliquez sur le bouton **Queue Prompt** (ou un bouton similaire) dans l'interface de ComfyUI.
2.  Vous pouvez suivre la progression (les nœuds actifs sont souvent mis en évidence).
3.  Vérifiez la console où vous avez lancé `python main.py` pour des logs détaillés et d'éventuels messages d'erreur.

## 9. Récupérer vos Images (pour test manuel)

*   Les images générées seront sauvegardées dans le dossier `ComfyUI/output/` par défaut, ou dans le chemin spécifié dans le nœud `SaveImage` si vous l'avez modifié.
*   Le backend Madsea, lors de l'exécution automatisée, récupérera ces images pour les placer dans la structure de projet Madsea (`i:\Madsea\outputs\` ou `i:\Madsea\projects\...`) en respectant la nomenclature.

## Bonnes Pratiques

*   **Sauvegardez vos workflows modifiés** : Si vous ajustez un workflow dans ComfyUI pour des tests, utilisez **File → Save workflow** pour conserver vos modifications (enregistrez-le sous un nouveau nom pour ne pas écraser le template Madsea).
*   **Organisation** : Gardez vos modèles et workflows bien organisés. Utilisez des sous-dossiers si nécessaire.
*   **Tests Incrémentiels** : Lorsque vous créez ou modifiez un workflow complexe, testez-le par petites étapes pour identifier plus facilement les problèmes.

Ces étapes devraient vous permettre d'opérer efficacement avec ComfyUI dans le contexte du projet Madsea.
