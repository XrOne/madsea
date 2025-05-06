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
- **Concept** (fixe IA) : remplacez `@task@` par **AI-concept** lors de la génération d'images.
- **Animation** (vidéo) : remplacez `@task@` par **Animation** lors de la génération de vidéos.
- Exemple image : `E202_SQ0010-0010_AI-concept_v0001.jpg`
- Exemple vidéo : `E202_SQ0010-0010_Animation_v0001.mp4`

---

## 5. Organisation des livrables
- **Images** : dossier `/E202/` ou `/SQ0010-0010/`, versions v0001, v0002...
- **Workflow** : importer JSON, configurer variables `${storyboard_image_path}`, `${prompt_text}`, `${output_path}`
- **Export** : images prêtes pour FTP/drive, puis animations

---

## Styles prédéfinis et paramètres techniques

### Style "Ombre chinoise" (Déclics)

Un style minimaliste inspiré du théâtre d'ombres, caractérisé par des silhouettes noires sur fonds colorés.

```json
{
  "id": "ombre_chinoise",
  "nom": "Ombres chinoises",
  "description": "Silhouettes noires sur fond coloré",
  "modele_base": "v1-5-pruned-emaonly.safetensors",
  "lora": "OmbresChinoises.safetensors",
  "lora_poids": 1.0,
  "controlnets": [
    {
      "type": "canny",
      "poids": 1.0,
      "preprocesseur": {
        "low_threshold": 100,
        "high_threshold": 200
      }
    },
    {
      "type": "depth",
      "poids": 0.8,
      "preprocesseur": {
        "a_mult": 1.0,
        "bg_threshold": 0.0
      }
    }
  ],
  "sampler": "dpmpp_2m_karras",
  "steps": 40,
  "guidance": 8.0,
  "prompt_template": "silhouette en contre-jour, contraste élevé, style théâtre d'ombres, noir sur fond coloré, minimaliste, ombres chinoises, style déclics, design épuré, graphisme contrasté, éclairage dramatique, {prompt}",
  "negative_prompt": "flou, détails excessifs, low contrast, couleurs multiples, texture, grain, bruit, photo réaliste, 3D"
}
```

**Effet des paramètres :**
- ControlNet Canny accentue les contours principaux, créant des silhouettes nettes
- ControlNet Depth préserve la profondeur tout en simplifiant
- Guidance élevée pour le respect du prompt minimaliste
- Prompt négatif pour éviter les détails superflus

---

### Style "Laboratoire réaliste"

Un style photoréaliste adapté aux environnements scientifiques et technologiques.

```json
{
  "id": "laboratoire",
  "nom": "Laboratoire",
  "description": "Style scientifique, rendu photoréaliste",
  "modele_base": "realisticVisionV6_v6B1.safetensors",
  "controlnets": [
    {
      "type": "depth",
      "poids": 0.7,
      "preprocesseur": {
        "a_mult": 1.0,
        "bg_threshold": 0.1
      }
    },
    {
      "type": "normal",
      "poids": 0.5,
      "preprocesseur": {}
    }
  ],
  "sampler": "dpmpp_sde_karras",
  "steps": 50,
  "guidance": 7.0,
  "prompt_template": "laboratoire scientifique, instruments, lumière blanche, rendu réaliste, {prompt}",
  "negative_prompt": "flou, couleurs saturées, style cartoon, ombres portées, bruit"
}
```

**Effet des paramètres :**
- ControlNet Depth pour la structure spatiale
- ControlNet Normal pour les détails de surface
- Sampler réaliste
- Prompt négatif pour éviter l'effet cartoon

---

### Style "Expressionniste"

Un style créatif, inspiré de l'expressionnisme pictural, avec des contours déformés et des couleurs vives.

```json
{
  "id": "expressionnisme",
  "nom": "Expressionnisme",
  "description": "Style pictural, couleurs vives, contours déformés",
  "modele_base": "expressionistModel.safetensors",
  "controlnets": [
    {
      "type": "canny",
      "poids": 0.65
    }
  ],
  "sampler": "euler_a",
  "steps": 30,
  "guidance": 9.0,
  "prompt_template": "expressionnisme, couleurs vives, contours déformés, style peinture, {prompt}",
  "negative_prompt": "photo réaliste, détails fins, couleurs ternes"
}
```

**Effet des paramètres :**
- ControlNet Canny avec poids réduit pour la liberté créative
- Sampler Euler Ancestral pour la variation
- Guidance élevée pour forcer le style
- Moins de steps pour un rendu rugueux