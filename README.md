# Storyboard-to-Video AI Platform

This application converts movie storyboards (sequences of sketched scenes with text annotations) into stylized animated videos. It parses input PDF/images, generates key frame images for each scene using AI (Stable Diffusion + custom styles), and compiles these into an animated video.

## Features

- **Storyboard Parsing**: Extract images and text from PDFs or image sets
- **AI Image Generation**: Convert storyboard scenes to high-quality images using Stable Diffusion and ControlNet
- **Style Management**: Load pre-trained styles or train new ones using LoRA
- **Video Generation**: Assemble generated images into video sequences with transitions
- **Flexible Processing**: Use local computation or cloud-based resources

## Technical Stack

- **Frontend UI**: SwarmUI (web interface built on ComfyUI)
- **Backend**: Python
- **AI Models**: Stable Diffusion, ControlNet, LoRA, AnimateDiff
- **Tools**: PyMuPDF/pdfplumber, Tesseract OCR, ComfyUI, FFmpeg

## Project Structure

```
├── parsing/            # Storyboard parsing module
├── generation/         # Image generation module
├── styles/             # Style management module
├── video/              # Video generation module
├── ui/                 # User interface module
├── utils/              # Utility functions
├── config/             # Configuration files
├── requirements.txt    # Project dependencies
└── main.py             # Main entry point
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Or use the web interface by running:

```bash
python -m ui.app
```

## Installation des modèles

Les modèles d'IA ne sont pas inclus dans ce dépôt en raison de leur taille. Voici comment les installer :

### 1. Modèles ComfyUI

Les modèles doivent être placés dans les dossiers suivants de ComfyUI :

```
ComfyUI/models/
├── checkpoints/    # Modèles Stable Diffusion
├── controlnet/     # Modèles ControlNet
├── vae/           # Modèles VAE
├── loras/         # Modèles LoRA
└── upscale_models/ # Modèles d'upscaling
```

#### Modèles requis :
- Stable Diffusion v1.5 (checkpoints)
- ControlNet v1.1 (controlnet)
- VAE (vae)
- Modèles LoRA spécifiques (loras)

### 2. Téléchargement des modèles

1. Accédez à l'interface ComfyUI (http://127.0.0.1:8188)
2. Utilisez le gestionnaire de modèles intégré pour télécharger les modèles nécessaires
3. Ou téléchargez manuellement depuis :
   - [Hugging Face](https://huggingface.co)
   - [Civitai](https://civitai.com)
   - [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

### 3. Vérification

Après l'installation, redémarrez ComfyUI et vérifiez que tous les modèles sont correctement chargés dans l'interface.

## Note importante

Les modèles d'IA sont des fichiers volumineux qui ne doivent pas être versionnés. Le fichier `.gitignore` est configuré pour exclure ces fichiers du dépôt Git.