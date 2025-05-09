# Script PowerShell pour vérifier les fichiers Git trackés/ignorés
# Vérifie spécifiquement que ComfyUI est versionné mais pas ComfyUI/models

# Fonction pour afficher un message avec couleur
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Vérifier si Git est installé
$gitVersion = git --version
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput red "Git n'est pas installé ou n'est pas dans le PATH."
    exit 1
}
Write-ColorOutput green "Git détecté: $gitVersion"

# Allez au répertoire racine du projet
Set-Location "i:\Madsea"
Write-ColorOutput green "Vérifcation dans le dossier: $(Get-Location)"

# Analysez les fichiers suivis par Git
Write-ColorOutput cyan "`n== FICHIERS TRACKÉS PAR GIT =="

# Vérifier que ComfyUI est tracké mais pas ComfyUI/models
$trackedFiles = git ls-files | Where-Object { $_ -like "ComfyUI/*" }
$modelFiles = $trackedFiles | Where-Object { $_ -like "ComfyUI/models/*" }

# Afficher les fichiers ComfyUI trackés
Write-ColorOutput green "`nFichiers ComfyUI trackés ($($trackedFiles.Count)) :"
if ($trackedFiles.Count -gt 20) {
    $trackedFiles | Select-Object -First 10 | ForEach-Object { Write-Output "✓ $_" }
    Write-Output "... (et $($trackedFiles.Count - 10) autres fichiers)"
} else {
    $trackedFiles | ForEach-Object { Write-Output "✓ $_" }
}

# Vérifier si des fichiers models sont trackés (ils ne devraient pas l'être)
if ($modelFiles.Count -gt 0) {
    Write-ColorOutput red "`n⚠️ ALERTE: $($modelFiles.Count) fichiers dans ComfyUI/models/ sont trackés!"
    Write-ColorOutput red "Ces fichiers devraient être ignorés par .gitignore:"
    $modelFiles | ForEach-Object { Write-ColorOutput red "❌ $_" }
} else {
    Write-ColorOutput green "`n✅ Excellent! Aucun fichier du dossier ComfyUI/models/ n'est tracké."
}

# Vérifier les fichiers ignorés mais présents
Write-ColorOutput cyan "`n== FICHIERS IGNORÉS PAR GIT =="
$ignoredFiles = git status --ignored --porcelain | Where-Object { $_ -like "!! ComfyUI/*" } | ForEach-Object { $_.Substring(3) }
$ignoredModelFiles = $ignoredFiles | Where-Object { $_ -like "ComfyUI/models*" }

# Afficher les fichiers ComfyUI/models ignorés
Write-ColorOutput green "`nFichiers ComfyUI/models ignorés :"
if ($ignoredModelFiles.Count -gt 10) {
    $ignoredModelFiles | Select-Object -First 5 | ForEach-Object { Write-Output "✓ $_" }
    Write-Output "... (et $($ignoredModelFiles.Count - 5) autres fichiers ignorés)"
} else {
    $ignoredModelFiles | ForEach-Object { Write-Output "✓ $_" }
}

# Vérifier les extensions de fichiers lourds
$heavyExtensions = @("*.safetensors", "*.pt", "*.ckpt", "*.bin", "*.pth")
$trackedHeavyFiles = git ls-files | Where-Object { 
    $file = $_
    $heavyExtensions | Where-Object { $file -like $_ }
}

if ($trackedHeavyFiles.Count -gt 0) {
    Write-ColorOutput red "`n⚠️ ALERTE: $($trackedHeavyFiles.Count) fichiers lourds sont trackés!"
    $trackedHeavyFiles | ForEach-Object { Write-ColorOutput red "❌ $_" }
} else {
    Write-ColorOutput green "`n✅ Excellent! Aucun fichier lourd (.safetensors, .pt, etc.) n'est tracké."
}

# Conseils finaux pour le commit
Write-ColorOutput cyan "`n== RÉSUMÉ POUR COMMIT =="
if ($modelFiles.Count -eq 0 -and $trackedHeavyFiles.Count -eq 0) {
    Write-ColorOutput green "✅ Votre dépôt est prêt pour le commit! ComfyUI est bien versionné sans les modèles."
    Write-ColorOutput green "Vous pouvez procéder avec:"
    Write-ColorOutput cyan "git add ."
    Write-ColorOutput cyan "git commit -m 'Ajout ComfyUI (hors modèles)'"
    Write-ColorOutput cyan "git push origin test"
} else {
    Write-ColorOutput red "❌ Votre dépôt contient des fichiers qui ne devraient pas être versionnés."
    Write-ColorOutput red "Veuillez corriger les problèmes ci-dessus avant de committer."
}
