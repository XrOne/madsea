# Script d'initialisation pour UV (gestionnaire de paquets Python ultrarapide)
# Auteur: CTO Madsea
# Date: 2025-04-27

# Définition des couleurs pour les messages
$colorInfo = "Cyan"
$colorSuccess = "Green"
$colorWarning = "Yellow"
$colorError = "Red"

function Write-ColoredMessage {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param (
        [string]$Message
    )
    Write-Host "`n==> $Message" -ForegroundColor $colorInfo
}

# Affichage du header
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor $colorInfo
Write-Host "║              MADSEA - INITIALISATION UV                  ║" -ForegroundColor $colorInfo
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor $colorInfo
Write-Host "  Gestionnaire de paquets Python ultrarapide (Rust-powered)`n" -ForegroundColor $colorInfo

# 1. Vérification de l'installation d'UV
Write-Step "Vérification de l'installation d'UV"
try {
    $uvVersion = uv --version
    Write-ColoredMessage "UV détecté: $uvVersion" -Color $colorSuccess
}
catch {
    Write-ColoredMessage "UV n'est pas installé sur ce système!" -Color $colorError
    Write-ColoredMessage "Installation avec la commande: pip install uv" -Color $colorWarning
    Write-ColoredMessage "Plus d'infos: https://github.com/astral-sh/uv" -Color $colorWarning
    exit 1
}

# 2. Création de l'environnement virtuel
Write-Step "Création/Vérification de l'environnement virtuel"
$venvPath = ".venv"

if (Test-Path $venvPath) {
    Write-ColoredMessage "Environnement virtuel existant détecté dans $venvPath" -Color $colorWarning
    $response = Read-Host "Voulez-vous le recréer? (o/N)"
    
    if ($response -eq "o" -or $response -eq "O") {
        Write-ColoredMessage "Suppression de l'environnement existant..." -Color $colorWarning
        Remove-Item -Path $venvPath -Recurse -Force
        Write-ColoredMessage "Création d'un nouvel environnement avec UV..." -Color $colorInfo
        uv venv $venvPath
    } else {
        Write-ColoredMessage "Conservation de l'environnement existant." -Color $colorInfo
    }
} else {
    Write-ColoredMessage "Création d'un environnement virtuel avec UV..." -Color $colorInfo
    uv venv $venvPath
}

# 3. Activation de l'environnement virtuel
Write-Step "Activation de l'environnement virtuel"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    Write-ColoredMessage "Activation de l'environnement..." -Color $colorInfo
    & $activateScript
    Write-ColoredMessage "Environnement activé avec succès!" -Color $colorSuccess
} else {
    Write-ColoredMessage "Script d'activation non trouvé: $activateScript" -Color $colorError
    exit 1
}

# 4. Installation des dépendances depuis requirements.txt
Write-Step "Installation des dépendances"

$reqFiles = @(
    "requirements.txt",
    "backend\requirements.txt"
)

$reqInstalled = $false

foreach ($reqFile in $reqFiles) {
    if (Test-Path $reqFile) {
        Write-ColoredMessage "Installation des dépendances depuis $reqFile..." -Color $colorInfo
        uv pip install -r $reqFile
        $reqInstalled = $true
        Write-ColoredMessage "Dépendances installées avec succès!" -Color $colorSuccess
    }
}

if (-not $reqInstalled) {
    Write-ColoredMessage "Aucun fichier requirements.txt trouvé. Aucune dépendance installée." -Color $colorWarning
}

# 5. Affichage des informations finales
Write-Step "Configuration terminée"
Write-ColoredMessage "L'environnement UV est prêt à être utilisé!" -Color $colorSuccess
Write-ColoredMessage "Pour installer un nouveau paquet: uv pip install <nom_paquet>" -Color $colorInfo
Write-ColoredMessage "Pour exécuter des scripts: python <script.py>" -Color $colorInfo
Write-ColoredMessage "Pour mettre à jour requirements.txt: uv pip freeze > requirements.txt" -Color $colorInfo

# 6. Lancement de VS Code (optionnel)
Write-ColoredMessage "`nVoulez-vous ouvrir VS Code maintenant? (o/N)" -Color $colorInfo
$response = Read-Host
if ($response -eq "o" -or $response -eq "O") {
    code .
}