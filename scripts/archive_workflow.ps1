# Script pour archiver le dossier obsolète Workflow

Write-Host "=== Archivage du dossier Workflow ==="

# Chemins
$workflowDir = "I:\Madsea\Workflow"
$archiveDir = "I:\Madsea\backups\Workflow_archive_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Vérifier si le dossier source existe
if (Test-Path $workflowDir) {
    # Créer le dossier d'archives si inexistant
    if (!(Test-Path (Split-Path $archiveDir -Parent))) {
        New-Item -ItemType Directory -Path (Split-Path $archiveDir -Parent) | Out-Null
        Write-Host "Dossier parent des archives créé."
    }
    
    # Déplacer le dossier Workflow vers backups
    Move-Item -Path $workflowDir -Destination $archiveDir -Force
    Write-Host "Dossier Workflow archivé vers : $archiveDir"
} else {
    Write-Host "Dossier Workflow inexistant, aucune action effectuée."
}

Write-Host "=== Archivage terminé ==="
