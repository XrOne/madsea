### Script pour ajouter ComfyUI (sans les modèles) au commit
Write-Host "Ajout de ComfyUI sans les modèles..." -ForegroundColor Cyan

# Aller à la racine du projet
Set-Location "i:\Madsea"

# Nettoyer l'index Git pour ComfyUI
git rm -r --cached ComfyUI/ 2>$null

# Méthode 1: Ajouter ComfyUI/* en excluant models/
Write-Host "1. Ajout de tous les fichiers ComfyUI (sauf models/)..." -ForegroundColor Yellow

# Créer un fichier .git/info/exclude temporaire pour être sûr
$excludePath = ".git/info/exclude"
$currentExclude = Get-Content $excludePath -ErrorAction SilentlyContinue
$newExclude = @"
# Temporary excludes
ComfyUI/models/
ComfyUI/models/**
*.safetensors
*.pt
*.ckpt
*.bin
*.pth
"@

Set-Content -Path $excludePath -Value ($currentExclude + $newExclude)

# Ajouter le dossier ComfyUI
Write-Host "2. Ajout du dossier ComfyUI (avec exclusions)..." -ForegroundColor Yellow
git add ComfyUI/

# Vérifier l'état
git status

Write-Host "`nVérification des fichiers ComfyUI/models qui seraient inclus:" -ForegroundColor Yellow
$stagedFiles = git diff --name-only --cached
$modelFiles = $stagedFiles | Where-Object { $_ -like "ComfyUI/models/*" }

if ($modelFiles) {
    Write-Host "ATTENTION: Certains fichiers models/ sont inclus dans le commit:" -ForegroundColor Red
    $modelFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    
    # Retirer les fichiers models/ du staging
    Write-Host "Suppression des fichiers models/ du staging..." -ForegroundColor Yellow
    $modelFiles | ForEach-Object { git reset HEAD $_ }
} else {
    Write-Host "✅ Aucun fichier du dossier models/ n'est inclus dans le commit." -ForegroundColor Green
}

# Instructions finales
Write-Host "`n✅ PRÊT POUR LE COMMIT!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant exécuter:" -ForegroundColor Cyan
Write-Host "   git commit -m 'Ajout ComfyUI (hors modèles)'" -ForegroundColor White
Write-Host "   git push origin test" -ForegroundColor White
