# Script de nettoyage pour le dossier outputs
# Supprime ou archive les fichiers anciens pour gérer l'espace disque

Write-Host "=== Nettoyage du dossier outputs ==="

# Chemins
$outputsDir = "I:\Madsea\outputs"
$archiveDir = "I:\Madsea\backups\outputs_archive"
$tempDir = "I:\Madsea\outputs\temp"

# Créer le dossier d'archives si inexistant
if (!(Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir | Out-Null
    Write-Host "Dossier d'archives créé : $archiveDir"
}

# Supprimer les fichiers temporaires de plus de 7 jours
if (Test-Path $tempDir) {
    $tempFiles = Get-ChildItem -Path $tempDir | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
    foreach ($file in $tempFiles) {
        Remove-Item -Path $file.FullName -Force
        Write-Host "Supprimé (temp > 7 jours) : $($file.Name)"
    }
} else {
    Write-Host "Dossier temp inexistant, ignoré."
}

# Archiver les fichiers de plus de 30 jours dans outputs (hors temp)
$oldFiles = Get-ChildItem -Path $outputsDir -Recurse -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) -and $_.DirectoryName -notlike "*$tempDir*" }
foreach ($file in $oldFiles) {
    $relativePath = $file.FullName.Replace($outputsDir, "").TrimStart("\")
    $archivePath = Join-Path $archiveDir $relativePath
    $archiveDirPath = Split-Path $archivePath -Parent
    
    if (!(Test-Path $archiveDirPath)) {
        New-Item -ItemType Directory -Path $archiveDirPath | Out-Null
    }
    
    Move-Item -Path $file.FullName -Destination $archivePath -Force
    Write-Host "Archivé (> 30 jours) : $relativePath vers $archivePath"
}

Write-Host "=== Nettoyage terminé ==="
