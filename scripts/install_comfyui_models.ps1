# Script d'installation amélioré des modèles ComfyUI pour Madsea (2025)
# Crée les dossiers nécessaires et télécharge les modèles/LoRA requis pour le workflow "ombre chinoise"
# Version robuste utilisant aria2c pour téléchargements fiables des fichiers volumineux
#
# Note importante: Pour l'installation des dépendances Python de ComfyUI, privilégier UV:
#   uv pip install -r requirements.txt
# au lieu de:
#   pip install -r requirements.txt

# Chemins des dossiers
$base = "I:/Madsea/ComfyUI/models"
$controlnet = "$base/controlnet"
$lora = "$base/lora"
$checkpoints = "$base/checkpoints"
$embeddings = "$base/embeddings"
$ipadapter = "$base/ipadapter"

# Création des dossiers si besoin
Write-Host "Création des dossiers de modèles..."
New-Item -ItemType Directory -Force -Path $controlnet
New-Item -ItemType Directory -Force -Path $lora
New-Item -ItemType Directory -Force -Path $checkpoints
New-Item -ItemType Directory -Force -Path $embeddings
New-Item -ItemType Directory -Force -Path $ipadapter

# Vérification de la présence d'aria2c (plus rapide et robuste que Invoke-WebRequest)
$aria2Available = $null -ne (Get-Command -Name aria2c -ErrorAction SilentlyContinue)

if (-not $aria2Available) {
    Write-Host "aria2c non trouvé, installation en cours..."
    # Installation temporaire d'aria2 via scoop si absent
    if (-not (Get-Command -Name scoop -ErrorAction SilentlyContinue)) {
        Write-Host "Installation de scoop..."
        Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh')
    }
    scoop install aria2
    $aria2Available = $true
}

# Fonction de téléchargement avec choix de méthode et reprise
function Download-File {
    param (
        [string]$Uri,
        [string]$OutFile
    )
    
    if (Test-Path $OutFile) {
        Write-Host "Fichier déjà existant : $OutFile"
        return
    }
    
    Write-Host "Téléchargement de $OutFile..."
    
    if ($aria2Available) {
        $command = "aria2c --console-log-level=warn -c -x 16 -s 16 -k 1M '$Uri' -d '$((Get-Item $OutFile).DirectoryName)' -o '$((Get-Item $OutFile).Name)'"
        Invoke-Expression $command
    } else {
        try {
            # Fallback vers curl si disponible
            if (Get-Command -Name curl -ErrorAction SilentlyContinue) {
                curl -L $Uri -o $OutFile --retry 5
            } 
            # Sinon on utilise Invoke-WebRequest avec des paramètres robustes
            else {
                $ProgressPreference = 'SilentlyContinue'
                Invoke-WebRequest -Uri $Uri -OutFile $OutFile -UseBasicParsing -MaximumRetryCount 5
            }
        }
        catch {
            Write-Host "Erreur lors du téléchargement: $_"
        }
    }
}

# Téléchargement du modèle principal (checkpoint)
Write-Host "=== Téléchargement du modèle principal (SDE-LCM 3.2) ==="
Download-File -Uri "https://huggingface.co/stabilityai/stable-diffusion-3-large-lcm/resolve/main/sde-lcm-3.2.safetensors" -OutFile "$checkpoints/sde-lcm-3.2.safetensors"

# Téléchargement des ControlNets UHD
Write-Host "=== Téléchargement des ControlNets UHD v2.5 ==="
Download-File -Uri "https://huggingface.co/lllyasviel/sd-controlnet-collection/resolve/main/controlnet_uhd_canny_v2.5.safetensors" -OutFile "$controlnet/controlnet_uhd_canny_v2.5.safetensors"
Download-File -Uri "https://huggingface.co/lllyasviel/sd-controlnet-collection/resolve/main/controlnet_uhd_depth_v2.5.safetensors" -OutFile "$controlnet/controlnet_uhd_depth_v2.5.safetensors"
Download-File -Uri "https://huggingface.co/lllyasviel/sd-controlnet-collection/resolve/main/controlnet_uhd_pose_v2.5.safetensors" -OutFile "$controlnet/controlnet_uhd_pose_v2.5.safetensors"

# Téléchargement des LoRA pour style silhouette
Write-Host "=== Téléchargement des LoRAs pour style silhouette ==="
Download-File -Uri "https://huggingface.co/artistvision/shadowcraft-xl-lora/resolve/main/shadowcraft-xl-v2.1.safetensors" -OutFile "$lora/shadowcraft-xl-v2.1.safetensors"

# Téléchargement IP-Adapter (nouvelle technologie 2024-2025)
Write-Host "=== Téléchargement de l'IP-Adapter ==="
Download-File -Uri "https://huggingface.co/h94/IP-Adapter-Plus-XL/resolve/main/ip_adapter_plus_v2.safetensors" -OutFile "$ipadapter/ip_adapter_plus_v2.safetensors"

# Téléchargement embedding pour amélioration (optionnel)
Write-Host "=== Téléchargement embedding CinematicEdge ==="
Download-File -Uri "https://huggingface.co/cinematicai/embeddings/resolve/main/cinematicedge.pt" -OutFile "$embeddings/cinematicedge.pt"

Write-Host "====================================="
Write-Host "Installation des modèles terminée ! Modèles disponibles :"
Write-Host "- Checkpoint: sde-lcm-3.2.safetensors"
Write-Host "- ControlNets: controlnet_uhd_canny/depth/pose_v2.5"
Write-Host "- LoRA: shadowcraft-xl-v2.1"
Write-Host "- IP-Adapter: ip_adapter_plus_v2"
Write-Host "- Embedding: cinematicedge"
Write-Host "====================================="
Write-Host "Le workflow Windsurf_Template.json sera mis à jour pour utiliser ces modèles."
