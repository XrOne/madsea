# ComfyUI – Configuration Technique Madsea

## 1. Modèles à télécharger

- **SDXL base 1.0** (`sdxl_base_1.0.safetensors`)
- **SDXL refiner 1.0** (`sdxl_refiner_1.0.safetensors`)
- **Juggernaut XL** (`juggernaut_xl.safetensors`)
- **RealVisXL** (`RealisticVisionXL.safetensors`)
- *(Optionnel)* DreamShaper XL (`dreamshaper_xl.safetensors`)

### LoRA styles
- `silhouette_photographic_style_lora.safetensors` (poids 1.0)
- `rimlight_lora.safetensors` (poids 0.8)
- *(Optionnel)* `greenscreen_lora.safetensors`

### ControlNet
- `diffusion_xl_depth.safetensors` (Depth, poids 1.0)
- `control_sd_xl_canny.safetensors` (Edges, poids 1.0)
- `diffusion_xl_openpose.safetensors` (Pose, poids 1.0)

### Modèles vidéo (phase Animation)
- `wan_1_3b.safetensors` (Wan 1.3B Lite) 720p
- ModelScope T2V (Text2Video, ~1.7B)
- Text2Video-Zero (Stable Diffusion adaptation)

**Organisation des dossiers :**
```
ComfyUI/
└─ models/
   ├─ checkpoints/
   ├─ lora/
   └─ controlnet/
```

---

## 2. Variantes lumineuses (Prompts & Réglages)

| Variante           | Prompt positif                            | Prompt négatif                    | Steps | CFG | Sampler         | LoRA weight    |
| ------------------ | ----------------------------------------- | --------------------------------- | ----- | --- | --------------- | -------------- |
| **Golden Hour**    | `golden hour, strong orange rim light...` | `no cartoon, no CGI, no faces...` | 30–40 | 7–8 | DPM++ 2M Karras | Silhouette 1.0 |
| **Blue Hour**      | `blue hour, cool rim light...`            | `no warm tones, no blur...`       | ~40  | ~8 | DPM++ 2M Karras | Silhouette 1.0 |
| **Neutre rasante** | `neutral backlight, white halo...`        | `no color grading, no vector...`  | 30–40 | ~7 | DPM++ 2M Karras | Silhouette 1.0 |

> ControlNet Depth+Edge à poids 1.0 pour chaque workflow.

---

## 3. Workflow Windsurf / ComfyUI (Template JSON)

```json
{
  "nodes": [ /* LoadImage, preprocessors, ControlNet, checkpoint, LoRA, prompt, sampler, upscale, save */ ],
  "settings": { "cuda_device": "TITAN X Pascal", "use_low_vram": true }
}
```

---

## 4. Nomenclature automatique Madsea

```
@episode@@sequence@-@shot@@task@_@version@@extension@
```
- **Concept** (fixe IA) : remplacez `@task@` par **AI-concept** lors de la génération d’images.
- **Animation** (vidéo) : remplacez `@task@` par **Animation** lors de la génération de vidéos.
- Exemple image : `E202_SQ0010-0010_AI-concept_v0001.jpg`
- Exemple vidéo : `E202_SQ0010-0010_Animation_v0001.mp4`

---

## 5. Organisation des livrables
- **Images** : dossier `/E202/` ou `/SQ0010-0010/`, versions v0001, v0002...
- **Workflow** : importer JSON, configurer variables `${storyboard_image_path}`, `${prompt_text}`, `${output_path}`
- **Export** : images prêtes pour FTP/drive, puis animations
