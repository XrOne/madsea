### Script pour préparer le commit de ComfyUI (sans les modèles)
Write-Host "Préparation du commit ComfyUI sans les modèles..." -ForegroundColor Cyan

# Aller à la racine du projet
Set-Location "i:\Madsea"

# 1. Vérifier que le dossier ComfyUI existe
if (-not (Test-Path "ComfyUI")) {
    Write-Host "ERREUR: Le dossier ComfyUI n'existe pas!" -ForegroundColor Red
    exit 1
}

# 2. S'assurer que le .gitignore est bien appliqué
Write-Host "1. Application du .gitignore mis à jour..." -ForegroundColor Yellow
git rm -r --cached .
git add .gitignore
git commit -m "Mise à jour du .gitignore pour ComfyUI"

# 3. Lister tous les fichiers ComfyUI à ajouter (hors models)
Write-Host "2. Ajout de tous les fichiers ComfyUI (sauf models/)..." -ForegroundColor Yellow
$files = Get-ChildItem -Path "ComfyUI" -Recurse -Exclude "models", "*.safetensors", "*.pt", "*.ckpt", "*.bin", "*.pth" -File

# Créer une liste pour git add
$filesList = @()
foreach ($file in $files) {
    # Vérifier que le chemin ne contient pas 'models'
    if ($file.FullName -notlike "*\models\*") {
        $relativePath = $file.FullName.Replace("i:\Madsea\", "").Replace("\", "/")
        $filesList += $relativePath
    }
}

# 4. Ajouter chaque fichier individuellement
Write-Host "3. Ajout de $($filesList.Count) fichiers ComfyUI (individuellement)..." -ForegroundColor Yellow
$count = 0
foreach ($file in $filesList) {
    git add $file
    $count++
    if ($count % 50 -eq 0) {
        Write-Host "   $count fichiers ajoutés..." -ForegroundColor Gray
    }
}

# 5. Ajouter les dossiers vides (structure)
Get-ChildItem -Path "ComfyUI" -Directory -Recurse | 
    Where-Object { $_.FullName -notlike "*\models*" -and $_.GetFiles().Count -eq 0 -and $_.GetDirectories().Count -eq 0 } | 
    ForEach-Object {
        $relativePath = $_.FullName.Replace("i:\Madsea\", "").Replace("\", "/")
        Write-Host "Ajout dossier vide: $relativePath" -ForegroundColor Gray
        # Créer un fichier .gitkeep pour pouvoir suivre le dossier vide
        $gitkeepPath = Join-Path $_.FullName ".gitkeep"
        New-Item -Path $gitkeepPath -ItemType File -Force | Out-Null
        git add "$relativePath/.gitkeep"
    }

# 6. Vérifier l'état
Write-Host "4. Vérification du statut..." -ForegroundColor Yellow
git status

# 7. Instructions finales
Write-Host "`n✅ PRÊT POUR LE COMMIT!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant exécuter:" -ForegroundColor Cyan
Write-Host "   git commit -m 'Ajout ComfyUI (hors modèles)'" -ForegroundColor White
Write-Host "   git push origin test" -ForegroundColor White
