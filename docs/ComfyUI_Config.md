# ComfyUI – Configuration Technique Madsea Complète

## 1. Modèles à télécharger

### Modèles de base
- **SDXL base 1.0** (`sdxl_base_1.0.safetensors`)
- **SDXL refiner 1.0** (`sdxl_refiner_1.0.safetensors`)
- **Juggernaut XL** (`juggernaut_xl.safetensors`)
- **RealVisXL** (`RealisticVisionXL.safetensors`)
- **SD 1.5** (`v1-5-pruned-emaonly.safetensors`)
- **Stable Diffusion 3** (quand disponible)
- *(Optionnel)* DreamShaper XL (`dreamshaper_xl.safetensors`)

### LoRA styles
- `silhouette_photographic_style_lora.safetensors` (poids 1.0)
- `rimlight_lora.safetensors` (poids 0.8)
- `declic_ombres_chinoises_lora.safetensors` (poids 1.0)
- `laboratoire_scientifique_lora.safetensors` (poids 0.7)
- *(Optionnel)* `greenscreen_lora.safetensors` (poids 0.5)
- *(Optionnel)* `expressionist_art_lora.safetensors` (poids 0.8)

### ControlNet
- `diffusion_xl_depth.safetensors` (Depth, poids 1.0)
- `control_sd_xl_canny.safetensors` (Edges, poids 1.0)
- `diffusion_xl_openpose.safetensors` (Pose, poids 1.0)
- `sd15_depth.safetensors` (Depth pour SD1.5)
- `sd15_canny.safetensors` (Canny pour SD1.5)
- `sd15_openpose.safetensors` (Openpose pour SD1.5)

### Modèles vidéo (phase Animation)
- `wan_1_3b.safetensors` (Wan 1.3B Lite) 720p
- ModelScope T2V (Text2Video, ~1.7B)
- VideoCrafter2
- Text2Video-Zero (Stable Diffusion adaptation)
- Gen-2 (Runway) via API

### Modèles d'interpolation
- `film_interpolation.safetensors` (FILM)
- `rife_v4.safetensors` (RIFE)
- `cain_v4.safetensors` (CAIN)

**Organisation des dossiers :**
```
ComfyUI/
└─ models/
   ├─ checkpoints/        # Modèles de base
   ├─ lora/               # Adaptateurs LoRA
   ├─ controlnet/         # Modèles ControlNet
   ├─ upscale/            # Modèles d'upscaling
   ├─ vae/                # VAE spécifiques (si nécessaire)
   └─ video/              # Modèles de génération vidéo
```

## 2. Variantes lumineuses (Prompts & Réglages)

| Variante           | Prompt positif                            | Prompt négatif                    | Steps | CFG | Sampler         | LoRA weight    |
| ------------------ | ----------------------------------------- | --------------------------------- | ----- | --- | --------------- | -------------- |
| **Golden Hour**    | `golden hour, strong orange rim light...` | `no cartoon, no CGI, no faces...` | 30–40 | 7–8 | DPM++ 2M Karras | Silhouette 1.0 |
| **Blue Hour**      | `blue hour, cool rim light...`            | `no warm tones, no blur...`       | ~40  | ~8 | DPM++ 2M Karras | Silhouette 1.0 |
| **Neutre rasante** | `neutral backlight, white halo...`        | `no color grading, no vector...`  | 30–40 | ~7 | DPM++ 2M Karras | Silhouette 1.0 |
| **Labo brillant**  | `clean laboratory, glossy surfaces...`    | `no dirt, no grime, no clutter...`| 50   | 7  | DPM++ SDE Karras| Labo 0.7      |
| **Labo sombre**    | `dark laboratory, dramatic lighting...`   | `no bright lights, no colors...`  | 40   | 7.5| Euler A         | Labo 0.8      |

> ControlNet Depth+Edge à poids 1.0 pour chaque workflow standard.  
> Possibilité d'ajouter ControlNet Pose (poids 0.6-0.8) pour les compositions complexes.

## 3. Configuration APIs cloud

### DALL-E 3 / Image 1 (OpenAI)
- **Endpoint** : `https://api.openai.com/v1/images/generations`
- **Modèle** : `dall-e-3`
- **Qualité** : `hd` (recommandé) ou `standard`
- **Taille** : `1792x1024` ou `1024x1792`
- **Style** : `natural` (recommandé) ou `vivid`
- **Paramètres** :
  ```json
  {
    "model": "dall-e-3",
    "prompt": "${prompt}",
    "n": 1,
    "quality": "hd",
    "size": "1792x1024",
    "style": "natural",
    "response_format": "url"
  }
  ```

### Midjourney API Bridge
- **Endpoint** : Via Discord API ou solutions tierces
- **Version** : Midjourney v6
- **Paramètres** :
  - `/imagine prompt: ${prompt} --style raw --ar 16:9 --v 6.0`
  - `/imagine prompt: ${prompt} --style ${style} --ar 16:9 --v 6.0`

### Autres APIs supportées
- **Stability AI** : `https://api.stability.ai/v1/generation`
- **Leonardo AI** : `https://cloud.leonardo.ai/api/rest/v1/generations`
- **Google Imagen** : Via API Vertex AI
- **Qwen VL** : Via API Alibaba Cloud

## 4. Workflow Madsea / ComfyUI (Template JSON)

```json
{
  "nodes": [
    {
      "id": 1,
      "type": "LoadImage",
      "inputs": {
        "image": "${input_image_path}"
      }
    },
    {
      "id": 2,
      "type": "ControlNetPreprocessor",
      "inputs": {
        "image": 1,
        "preprocessor_type": "canny",
        "threshold_a": 100,
        "threshold_b": 200
      }
    },
    {
      "id": 3,
      "type": "ControlNetPreprocessor",
      "inputs": {
        "image": 1,
        "preprocessor_type": "depth",
        "threshold_a": 0,
        "threshold_b": 1
      }
    },
    {
      "id": 4,
      "type": "CheckpointLoader",
      "inputs": {
        "checkpoint_name": "juggernaut_xl.safetensors"
      }
    },
    {
      "id": 5,
      "type": "CLIPTextEncode",
      "inputs": {
        "text": "${positive_prompt}",
        "clip": 4
      }
    },
    {
      "id": 6,
      "type": "CLIPTextEncode",
      "inputs": {
        "text": "${negative_prompt}",
        "clip": 4
      }
    },
    {
      "id": 7,
      "type": "ControlNetApply",
      "inputs": {
        "conditioning": 5,
        "control_net": "control_sd_xl_canny.safetensors",
        "image": 2,
        "strength": 1.0
      }
    },
    {
      "id": 8,
      "type": "ControlNetApply",
      "inputs": {
        "conditioning": 7,
        "control_net": "diffusion_xl_depth.safetensors",
        "image": 3,
        "strength": 0.8
      }
    },
    {
      "id": 9,
      "type": "LoraLoader",
      "inputs": {
        "model": 4,
        "clip": 4,
        "lora_name": "${lora_name}",
        "strength_model": "${lora_strength}",
        "strength_clip": "${lora_strength}"
      }
    },
    {
      "id": 10,
      "type": "KSampler",
      "inputs": {
        "model": 9,
        "positive": 8,
        "negative": 6,
        "latent_image": [1920, 1080],
        "seed": "${seed}",
        "steps": "${steps}",
        "cfg": "${cfg}",
        "sampler_name": "${sampler}",
        "scheduler": "karras",
        "denoise": 1
      }
    },
    {
      "id": 11,
      "type": "VAEDecode",
      "inputs": {
        "samples": 10,
        "vae": 4
      }
    },
    {
      "id": 12,
      "type": "SaveImage",
      "inputs": {
        "images": 11,
        "filename_prefix": "${output_prefix}",
        "output_dir": "${output_path}"
      }
    }
  ],
  "settings": { 
    "cuda_device": "TITAN X Pascal", 
    "use_low_vram": true,
    "metadata": {
      "project": "${project_name}",
      "episode": "${episode}",
      "sequence": "${sequence}",
      "style": "${style_name}"
    }
  }
}
```

## 5. Nomenclature automatique Madsea

```
@episode@@sequence@-@shot@@task@_@version@@extension@
```
- **Concept** (fixe IA) : remplacez `@task@` par **AI-concept** lors de la génération d'images.
- **Animation** (vidéo) : remplacez `@task@` par **Animation** lors de la génération de vidéos.
- Exemple image : `E202_SQ0010-0010_AI-concept_v0001.jpg`
- Exemple vidéo : `E202_SQ0010-0010_Animation_v0001.mp4`

## 6. Organisation des livrables
- **Images** : dossier `/E202/` ou `/SQ0010-0010/`, versions v0001, v0002...
- **Workflow** : importer JSON, configurer variables `${storyboard_image_path}`, `${prompt_text}`, `${output_path}`
- **Export** : images prêtes pour FTP/drive, puis animations

## 7. Configuration FTP
```json
{
  "ftp": {
    "host": "${ftp_host}",
    "port": 21,
    "user": "${ftp_username}",
    "password": "${ftp_password}",
    "root_dir": "/declics/episodes/${episode}/",
    "passive_mode": true,
    "timeout": 30,
    "retries": 3,
    "notify_on_complete": true
  },
  "export": {
    "auto_upload": false,
    "upload_on_validation": true,
    "batch_size": 10,
    "compress": false
  }
}
```

## 8. Paramètres Animation
```json
{
  "animation": {
    "generator": "local",  // "local", "api", "hybrid"
    "fps": 24,
    "resolution": "1920x1080",
    "video_format": "mp4",
    "codec": "h264",
    "bitrate": "12M",
    "models": {
      "interpolation": "film_interpolation.safetensors",
      "text2video": "modelscope_t2v.safetensors",
      "motion": "ebsynth_plus.safetensors"
    },
    "transitions": {
      "default": "crossfade",
      "duration": 24,  // frames
      "custom": {}
    }
  }
}
```

## 9. Styles prédéfinis et paramètres techniques

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