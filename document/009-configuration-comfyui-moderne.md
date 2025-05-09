# Configuration ComfyUI moderne pour Madsea
*Document technique de référence - Mise à jour du 9 mai 2025*

## Objectif
Ce document décrit la configuration actuelle du système ComfyUI pour le projet Madsea, avec l'utilisation des modèles SDXL modernes pour la génération des images en style "ombre chinoise".

## Modèles utilisés

### Modèles de base (Checkpoints)
| Nom du modèle | Description | Usage |
|---------------|-------------|-------|
| `RealVisXL_V5.0_fp16.safetensors` | Version optimisée (fp16) du dernier RealVisXL | Production principale |
| `RealVisXL_V5.0_fp32.safetensors` | Version pleine précision | Qualité maximale (si besoin) |
| `sd_xl_turbo_1.0_fp16.safetensors` | Version turbo pour tests rapides | Prototypage rapide |

### LoRAs de style
| Nom du modèle | Description | Force recommandée |
|---------------|-------------|-------------------|
| `Shadow_Style_XL.safetensors` | Style silhouette pour SDXL | 0.65 - 0.85 |
| `silhouette_photographic_style_lora.safetensors` | Style photographique | 0.55 - 0.75 |

### ControlNet
| Nom du modèle | Description | Force recommandée |
|---------------|-------------|-------------------|
| `control_v11p_sd15_canny_fp16.safetensors` | Détection de contours pour préserver la composition | 0.7 - 0.85 |

## Workflow de génération

### Paramètres optimaux pour le style "ombre chinoise"
- **Modèle** : `RealVisXL_V5.0_fp16.safetensors`
- **Sampler** : DPM++ SDE Karras
- **Steps** : 25-30
- **CFG** : 7.0
- **Size** : 1024×1024 (SDXL natif)
- **LoRA** : `Shadow_Style_XL.safetensors` (force 0.8)
- **ControlNet** : `control_v11p_sd15_canny_fp16.safetensors` (force 0.75)

### Prompt type pour style "ombre chinoise"
```
silhouette style, shadow art, high contrast black and white, minimalist, backlit figures, strong shadows, cinematic lighting, crisp edges, declic animation style
```

### Negative prompt recommandé
```
color, blurry, detailed, noise, grain, text, low contrast, soft edges, multiple figures, busy background
```

## Performance et optimisation

### Ressources recommandées
- **GPU** : NVIDIA avec min. 8GB VRAM
- **Mémoire** : 16GB RAM
- **Stockage** : SSD pour les modèles

### Capacité estimée
- **Temps/image** : 30-45 secondes avec RealVisXL_V5.0_fp16
- **Batch/heure** : 80-100 images
- **Objectif** : 70 plans en 10 jours (facilement atteignable)

## Intégration frontend

L'interface utilisateur propose deux modes de génération :
1. **Mode manuel** : L'utilisateur sélectionne les images et paramètres
2. **Mode automatique** : L'automatisation traite les images par lot

## Workflow pour les 70 plans urgents
1. Extraction PDF → nomenclature correcte
2. Génération batch par séquence
3. Validation rapide
4. Export standardisé

---

*Document préparé par le CTO Madsea - Validé le 9 mai 2025*