# Script d'installation automatique des modèles ComfyUI pour Madsea
# Crée les dossiers nécessaires et télécharge les modèles/LoRA requis pour le workflow "ombre chinoise"

$base = "I:/Madsea/ComfyUI/models"
$controlnet = "$base/controlnet"
$lora = "$base/lora"
$checkpoints = "$base/checkpoints"

# Création des dossiers si besoin
New-Item -ItemType Directory -Force -Path $controlnet
New-Item -ItemType Directory -Force -Path $lora
New-Item -ItemType Directory -Force -Path $checkpoints

# Téléchargement des modèles principaux
Invoke-WebRequest -Uri "https://huggingface.co/SG161222/RealVisXL/resolve/main/RealVisXL.safetensors" -OutFile "$checkpoints/RealVisXL.safetensors"
Invoke-WebRequest -Uri "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/diffusion_xl_depth.safetensors" -OutFile "$controlnet/diffusion_xl_depth.safetensors"
Invoke-WebRequest -Uri "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_sd_xl_canny.safetensors" -OutFile "$controlnet/control_sd_xl_canny.safetensors"
Invoke-WebRequest -Uri "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/diffusion_xl_openpose.safetensors" -OutFile "$controlnet/diffusion_xl_openpose.safetensors"

# LoRA Stylized Silhouette Photography XL
Invoke-WebRequest -Uri "https://huggingface.co/DoctorDiffusion/doctor-diffusion-s-stylized-silhouette-photography-xl-lora/resolve/main/DD-sli-v1.safetensors" -OutFile "$lora/silhouette_photographic_style_lora.safetensors"

# Rimlight LoRA - EpiNoiseoffset (à valider selon compatibilité)
Invoke-WebRequest -Uri "https://civitai.com/api/download/models/13941" -OutFile "$lora/epiNoiseoffset_v2.safetensors"

Write-Host "Installation des modèles/checkpoints terminée. Si besoin, adaptez les chemins et noms de fichiers dans vos workflows ComfyUI."
