# ComfyUI – Protocol Nodal Madsea

## 1. Pipeline nodal détaillé pour DéCLICS

### 1.1. Chargement et pré-traitement

```
LoadImage → MiDaSDepth → ControlNetDepth (1.0)
             CannyEdge → ControlNetCanny (1.0)
             OpenPose → ControlNetPose (1.0) [optionnel]
```

### 1.2. Chargement des modèles

```
CheckpointLoader (RealVisXL/juggernaut_xl)
LoRALoader silhouette (1.0)
LoRALoader rimlight (0.8)
```

### 1.3. Prompt & Conditionnement

- **Prompt** : `${prompt_text}`
- **Negative** : `${negative_prompt}`
- Connecter aux deux branches texte du sampler SDXL

### 1.4. Diffusion & Upscale

```
KSampler: DPM++ 2M Karras, steps 30–40, cfg 7–8, res 1920×1080 (ou 768×432 + Upscale)
Upscale: RealESRGAN_x4, scale 2 [optionnel]
```

### 1.5. Sauvegarde

```
SaveImage path : ${output_path} (placeholder Windsurf)
```

---

## 2. Schémas et templates avancés

- Voir le template JSON dans ComfyUI_Config.md pour l'exemple minimal.
- Pour les diagrammes nodaux, se référer au PDF original ou à une version PNG/SVG placée dans `docs/MCP/`.

---

## 3. Notes complémentaires

- Adapter les réglages LoRA/ControlNet selon le style souhaité.
- Pour l'animation, voir la section modèles vidéo dans ComfyUI_Config.md.

---

*Document de référence pour toute automatisation Windsurf/ComfyUI Madsea.*