# Script pour ajouter tous les fichiers ComfyUI sauf models/
# Aller dans le répertoire du projet
Set-Location "i:/Madsea"

Write-Host "Ajout des fichiers ComfyUI (sauf models/) au commit..." -ForegroundColor Cyan

# Variable pour compter les fichiers
$addedFiles = 0

# Trouver tous les fichiers dans ComfyUI sauf dans models/
$files = Get-ChildItem -Path "ComfyUI" -Recurse -File -Exclude "*.safetensors","*.pt","*.ckpt","*.bin","*.pth" | 
         Where-Object { $_.FullName -notlike "*\models\*" }

# Ajouter chaque fichier individuellement
foreach ($file in $files) {
    $relativePath = $file.FullName.Replace("i:\Madsea\", "").Replace("\", "/")
    git add $relativePath
    $addedFiles++
    
    # Afficher un point de progression tous les 20 fichiers
    if ($addedFiles % 20 -eq 0) {
        Write-Host "." -NoNewline -ForegroundColor Green
    }
}

Write-Host "`nAjouté $addedFiles fichiers de ComfyUI (hors models/)" -ForegroundColor Green

# Créer des .gitkeep pour les dossiers vides importants
$emptyDirs = Get-ChildItem -Path "ComfyUI" -Directory -Recurse | 
    Where-Object { $_.FullName -notlike "*\models*" -and (Get-ChildItem -Path $_.FullName -File).Count -eq 0 }

foreach ($dir in $emptyDirs) {
    $gitkeepPath = Join-Path $dir.FullName ".gitkeep"
    New-Item -Path $gitkeepPath -ItemType File -Force | Out-Null
    $relativePath = $gitkeepPath.Replace("i:\Madsea\", "").Replace("\", "/")
    git add $relativePath
    Write-Host "Ajouté .gitkeep dans $($dir.FullName)" -ForegroundColor Yellow
}

# Vérifier le statut pour confirmer
Write-Host "`nVérification du commit..." -ForegroundColor Cyan
git status

# Instructions finales
Write-Host "`n✅ PRÊT POUR LE COMMIT!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant exécuter:" -ForegroundColor Cyan
Write-Host "   git commit -m 'Ajout ComfyUI (hors modèles)'" -ForegroundColor White
Write-Host "   git push origin test" -ForegroundColor White
