# UV Wrapper pour Madsea - Simplification d'accès au gestionnaire de paquets ultra-rapide
# Auteur: CTO Madsea
# Date: 2025-04-27

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

# Activation automatique de l'environnement virtuel si nécessaire
$venvPath = Join-Path $PSScriptRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if ((Get-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue) -eq $null) {
    if (Test-Path $activateScript) {
        Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Cyan
        & $activateScript
    }
}

# Commandes personnalisées
switch ($Command) {
    "help" {
        Write-Host "UV Wrapper - Commandes disponibles:" -ForegroundColor Cyan
        Write-Host "  install <paquet>     : Installer un paquet avec UV"
        Write-Host "  uninstall <paquet>   : Désinstaller un paquet avec UV"
        Write-Host "  list                 : Lister les paquets installés"
        Write-Host "  update-reqs          : Mettre à jour requirements.txt avec les dépendances actuelles"
        Write-Host "  init                 : (Ré)initialiser l'environnement virtual avec UV"
        Write-Host "  run <script.py>      : Exécuter un script Python avec l'environnement UV"
        Write-Host "  direct <args>        : Transmettre la commande directement à UV"
    }
    "install" {
        if ($Arguments.Count -eq 0) {
            Write-Host "Spécifiez un paquet à installer. Ex: ./uv-wrapper.ps1 install numpy" -ForegroundColor Yellow
            return
        }
        Write-Host "Installation de: $($Arguments -join ' ')" -ForegroundColor Cyan
        uv pip install $Arguments
    }
    "uninstall" {
        if ($Arguments.Count -eq 0) {
            Write-Host "Spécifiez un paquet à désinstaller. Ex: ./uv-wrapper.ps1 uninstall numpy" -ForegroundColor Yellow
            return
        }
        Write-Host "Désinstallation de: $($Arguments -join ' ')" -ForegroundColor Cyan
        uv pip uninstall $Arguments
    }
    "list" {
        uv pip list
    }
    "update-reqs" {
        $reqPath = Join-Path $PSScriptRoot "backend\requirements.txt"
        Write-Host "Mise à jour du fichier $reqPath..." -ForegroundColor Cyan
        uv pip freeze > $reqPath
        Write-Host "Le fichier requirements.txt a été mis à jour!" -ForegroundColor Green
    }
    "init" {
        $initScript = Join-Path $PSScriptRoot "init-uv.ps1"
        & $initScript
    }
    "run" {
        if ($Arguments.Count -eq 0) {
            Write-Host "Spécifiez un script à exécuter. Ex: ./uv-wrapper.ps1 run backend/app.py" -ForegroundColor Yellow
            return
        }
        python $Arguments
    }
    "direct" {
        uv $Arguments
    }
    default {
        Write-Host "Commande inconnue: $Command" -ForegroundColor Red
        Write-Host "Utilisez ./uv-wrapper.ps1 help pour voir les commandes disponibles" -ForegroundColor Yellow
    }
}