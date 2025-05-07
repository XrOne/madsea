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

# Téléchargement des modèles (liens à compléter selon disponibilité)
Invoke-WebRequest -Uri "https://huggingface.co/SG161222/RealVisXL/resolve/main/RealVisXL.safetensors" -OutFile "$checkpoints/RealVisXL.safetensors"
Invoke-WebRequest -Uri "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/diffusion_xl_depth.safetensors" -OutFile "$controlnet/diffusion_xl_depth.safetensors"
Invoke-WebRequest -Uri "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_sd_xl_canny.safetensors" -OutFile "$controlnet/control_sd_xl_canny.safetensors"
Invoke-WebRequest -Uri "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/diffusion_xl_openpose.safetensors" -OutFile "$controlnet/diffusion_xl_openpose.safetensors"
# Les liens suivants sont à compléter selon l'emplacement exact des LoRA
#Invoke-WebRequest -Uri "LIEN_LORA_SILHOUETTE" -OutFile "$lora/silhouette_photographic_style_lora.safetensors"
#Invoke-WebRequest -Uri "LIEN_LORA_RIMLIGHT" -OutFile "$lora/rimlight_lora.safetensors"

Write-Host "Installation des modèles/checkpoints terminée. Pensez à compléter les liens LoRA si besoin."
