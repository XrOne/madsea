# Documentation des paramètres de style pour Madsea

Cette documentation technique détaille les paramètres de style disponibles dans Madsea et leurs effets sur la génération d'images. Ces paramètres peuvent être configurés via l'interface graphique ou en ligne de commande.

## Styles prédéfinis

Madsea propose plusieurs styles visuels prédéfinis, chacun avec une configuration optimisée pour des rendus spécifiques.

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

#### Effet des paramètres :

- Le **ControlNet Canny** est configuré avec des seuils qui accentuent les contours principaux, créant des silhouettes nettes
- Le **ControlNet Depth** avec un poids de 0.8 préserve la profondeur de la scène tout en permettant des simplifications
- La **guidance élevée** (8.0) force le modèle à respecter strictement le prompt, important pour le style minimaliste
- Le **prompt négatif** rejette activement les détails et textures qui nuiraient à l'esthétique épurée

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
  "prompt_template": "laboratoire scientifique réaliste, éclairage néon doux, ambiance sombre, style cinéma, détaillé, photoréaliste, équipement scientifique de haute technologie, reflets sur les surfaces métalliques, éclairage d'ambiance, profondeur de champ réduite, {prompt}",
  "negative_prompt": "cartoon, dessin, style artistique, low quality, mauvaise anatomie, déformé, flou, grain visible, basse résolution"
}
```

#### Effet des paramètres :

- Le modèle **RealisticVision** comme base, spécialement optimisé pour le photoréalisme
- La combinaison **Depth + Normal** offre un contrôle précis sur les volumes et l'orientation des surfaces
- Le **sampler DPM++ SDE** produit des résultats plus détaillés, adapté aux rendus réalistes
- Plus de **steps** (50) pour un rendu plus fin et précis
- **Guidance** légèrement plus basse (7.0) pour permettre une certaine liberté créative dans les détails

### Style "Expressionniste"

Un style artistique inspiré du cinéma expressionniste, avec contrastes dramatiques et perspectives déformées.

```json
{
  "id": "expressionniste",
  "nom": "Expressionniste",
  "description": "Émotionnel, contrastes intenses",
  "modele_base": "dreamshaper_6BakedVae.safetensors",
  "lora": "expressionism.safetensors",
  "lora_poids": 0.85,
  "controlnets": [
    {
      "type": "canny",
      "poids": 0.65,
      "preprocesseur": {
        "low_threshold": 100,
        "high_threshold": 200
      }
    }
  ],
  "sampler": "euler_ancestral",
  "steps": 30,
  "guidance": 9.0,
  "prompt_template": "style expressionniste, contrastes intenses, angles dramatiques, ombres prononcées, atmosphère inquiétante, textures visibles, perspective déformée, émotionnel, cinéma noir et blanc des années 1920, {prompt}",
  "negative_prompt": "réaliste, photographie, couleurs vives, symétrique, proportions normales, composition équilibrée"
}
```

#### Effet des paramètres :

- **DreamShaper** est choisi comme modèle base pour sa capacité à créer des images stylisées
- **LoRA expressionniste** avec un poids de 0.85 apporte les caractéristiques visuelles du mouvement
- Un seul **ControlNet Canny** avec poids réduit (0.65) pour préserver la composition tout en permettant des déformations expressives
- Le **sampler Euler Ancestral** introduit des variations créatives intéressantes
- **Guidance élevée** (9.0) pour forcer le style expressionniste
- **Moins de steps** (30) pour conserver une certaine rugosité dans le rendu

## Options de ControlNet

Les ControlNets sont essentiels pour préserver la composition du storyboard tout en appliquant un style. Voici leur fonctionnement :

### Canny Edge Detection

```json
{
  "type": "canny",
  "modele": "control_v11p_sd15_canny.pth",
  "poids": 1.0,
  "preprocesseur": {
    "low_threshold": 100,
    "high_threshold": 200,
    "detect_resolution": 512,
    "image_resolution": 512
  }
}
```

- **Fonction** : Extrait les contours/silhouettes de l'image source
- **low_threshold/high_threshold** : Ajuste la sensibilité de détection des contours
- **Effet sur l'image** : Préserve la position et forme des éléments
- **Usage optimal** : Styles graphiques, compositions avec contours nets

### MiDaS Depth Map

```json
{
  "type": "depth",
  "modele": "control_v11f1p_sd15_depth.pth",
  "poids": 0.8,
  "preprocesseur": {
    "a_mult": 1.0,
    "bg_threshold": 0.0,
    "detect_resolution": 512,
    "image_resolution": 512
  }
}
```

- **Fonction** : Extrait une carte de profondeur de l'image source
- **a_mult** : Multiplicateur d'amplitude pour accentuer les différences de profondeur
- **bg_threshold** : Seuil pour la détection d'arrière-plan
- **Effet sur l'image** : Maintient les relations spatiales entre éléments
- **Usage optimal** : Préservation de la perspective et des plans

### Normal Map

```json
{
  "type": "normal",
  "modele": "control_v11p_sd15_normalbae.pth",
  "poids": 0.5,
  "preprocesseur": {
    "detect_resolution": 512,
    "image_resolution": 512
  }
}
```

- **Fonction** : Détermine l'orientation des surfaces
- **Effet sur l'image** : Conserve la direction et courbure des volumes
- **Usage optimal** : Scènes avec surfaces complexes (visages, objets 3D)

## Paramètres de sampling

### Samplers disponibles

| Sampler | Description | Cas d'usage optimal |
|---------|-------------|---------------------|
| `dpmpp_2m_karras` | Diffusion Probabilistic Models++, 2e ordre, planificateur Karras | Équilibre qualité/vitesse, bon pour la plupart des styles |
| `dpmpp_sde_karras` | DPM++ avec équation différentielle stochastique | Détails fins, textures complexes |
| `euler_ancestral` | Méthode d'Euler avec bruit ajouté | Créativité, styles artistiques |
| `ddim` | Denoising Diffusion Implicit Models | Précision, fidélité au prompt |
| `lms` | Linear Multi-Step | Stabilité, peu d'artefacts |

### Autres paramètres de sampling

| Paramètre | Plage | Description | Effet |
|-----------|-------|-------------|-------|
| `steps` | 20-100 | Nombre d'étapes de débruitage | Plus élevé = plus de détails mais plus long |
| `guidance` (cfg) | 5.0-15.0 | Échelle de guidance du texte | Plus élevé = plus fidèle au prompt mais moins naturel |
| `denoise` | 0.0-1.0 | Force du débruitage (en img2img) | Plus élevé = plus d'influence du prompt vs. image source |

## Création de styles personnalisés

### Entraînement de LoRA

Pour créer un style personnalisé, vous pouvez entraîner un LoRA (Low-Rank Adaptation) avec ces paramètres recommandés :

```bash
Madsea> EntrainerLoRA "mon_style" \
  --images="dossier/references" \
  --resolution=512 \
  --epochs=1500 \
  --learning_rate=1e-4 \
  --batch_size=1 \
  --network_dim=32 \
  --network_alpha=16
```

### Structure du fichier de style personnalisé

```json
{
  "id": "mon_style_custom",
  "nom": "Mon Style Personnalisé",
  "description": "Description du style",
  "modele_base": "choix_du_modele.safetensors",
  "lora": "mon_style.safetensors",
  "lora_poids": 0.8,
  "controlnets": [
    {
      "type": "canny",
      "poids": 0.7
    },
    {
      "type": "depth",
      "poids": 0.6
    }
  ],
  "sampler": "dpmpp_2m_karras",
  "steps": 35,
  "guidance": 7.5,
  "prompt_template": "style mon_style, caractéristique 1, caractéristique 2, {prompt}",
  "negative_prompt": "éléments à éviter, style contradictoire"
}
```

## Recommandations de paramètres par type de scène

### Scènes d'extérieur jour

```json
{
  "controlnets": [
    {"type": "depth", "poids": 0.7},
    {"type": "canny", "poids": 0.6}
  ],
  "guidance": 7.0,
  "steps": 35
}
```

### Scènes de nuit/faible lumière

```json
{
  "controlnets": [
    {"type": "depth", "poids": 0.8},
    {"type": "canny", "poids": 0.5}
  ],
  "guidance": 7.5,
  "steps": 45,
  "additions_prompt": "éclairage nocturne, ombres prononcées, ambiance sombre"
}
```

### Gros plans sur personnages

```json
{
  "controlnets": [
    {"type": "canny", "poids": 0.6},
    {"type": "normal", "poids": 0.8}
  ],
  "guidance": 8.0,
  "steps": 50,
  "additions_prompt": "détails du visage, expression faciale claire"
}
```

### Plans d'action/mouvements

```json
{
  "controlnets": [
    {"type": "openpose", "poids": 0.7},
    {"type": "depth", "poids": 0.6}
  ],
  "guidance": 7.0,
  "steps": 40,
  "additions_prompt": "dynamique, mouvement fluide, action"
}
```

## Optimisation des performances

### Pour vitesse maximale

```json
{
  "sampler": "ddim",
  "steps": 25,
  "controlnets": [{"type": "canny", "poids": 0.7}]
}
```

### Pour qualité maximale

```json
{
  "sampler": "dpmpp_sde_karras",
  "steps": 60,
  "controlnets": [
    {"type": "depth", "poids": 0.7},
    {"type": "normal", "poids": 0.6}
  ],
  "guidance": 8.5
}
```