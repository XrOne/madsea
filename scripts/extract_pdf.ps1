# Script simplifié et robuste pour l'extraction de PDF avec UV
# Aucun problème de chemin ou d'encodage

# Paramètres
param(
    [string]$Episode = "666",
    [int]$Version = 1
)

Write-Host "Extraction PDF Madsea avec nomenclature stricte" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Green

# Dossier racine du projet
$MADSEA_ROOT = "i:\Madsea"
Set-Location $MADSEA_ROOT

# Création du dossier de sortie
$OUTPUT_DIR = Join-Path $MADSEA_ROOT "outputs\extraction_test"
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR -Force | Out-Null
    Write-Host "✓ Dossier de sortie créé: $OUTPUT_DIR" -ForegroundColor Cyan
}
else {
    Write-Host "✓ Dossier de sortie prêt: $OUTPUT_DIR" -ForegroundColor Cyan
}

# Recherche de PDFs dans le dossier storyboard
$PDF_DIR = Join-Path $MADSEA_ROOT "pdf storyboard"
$ALL_PDFS = @(Get-ChildItem -Path $PDF_DIR -Filter "*.pdf" -ErrorAction SilentlyContinue)

if ($ALL_PDFS.Count -eq 0) {
    Write-Host "❌ ERREUR: Aucun fichier PDF trouvé dans $PDF_DIR" -ForegroundColor Red
    exit 1
}

# Affichage des PDFs disponibles
Write-Host "PDFs disponibles dans $PDF_DIR :" -ForegroundColor Yellow
for ($i = 0; $i -lt $ALL_PDFS.Count; $i++) {
    Write-Host "  $($i+1). $($ALL_PDFS[$i].Name)" -ForegroundColor White
}

# Sélection automatique si un seul PDF
$selectedIndex = 0
if ($ALL_PDFS.Count -gt 1) {
    $selectedIndex = 0  # Par défaut, utilise le premier
    Write-Host "⚠️ Plusieurs PDFs trouvés. Utilisation du premier: $($ALL_PDFS[$selectedIndex].Name)" -ForegroundColor Yellow
}

# Récupère le chemin absolu du PDF sélectionné
$selectedPDF = $ALL_PDFS[$selectedIndex].FullName
Write-Host "✓ PDF sélectionné: $selectedPDF" -ForegroundColor Green

# Convertir en chemin normalisé pour Python (slashs avant)
$normalizedPath = $selectedPDF -replace '\\', '/'
Write-Host "✓ Chemin normalisé: $normalizedPath" -ForegroundColor Cyan

# Paramètres d'extraction
Write-Host "`nParamètres d'extraction:" -ForegroundColor Yellow
Write-Host "  • Épisode: E$Episode" -ForegroundColor White
Write-Host "  • Version: v$($Version.ToString("0000"))" -ForegroundColor White
Write-Host "  • Format: E{episode}_SQ{sequence}-{plan}_storyboard_v{version}.png" -ForegroundColor White

# Exécution de l'extraction avec UV
Write-Host "`nLancement de l'extraction..." -ForegroundColor Green
try {
    # Commande complète pour le debugging
    $fullCommand = "uv run scripts/test_extraction.py `"$normalizedPath`" `"$($OUTPUT_DIR -replace '\\', '/')`" `"$Episode`" `"$Version`""
    Write-Host "Commande: $fullCommand" -ForegroundColor Gray
    
    # Exécution réelle
    $output = & uv run scripts/test_extraction.py "$normalizedPath" "$($OUTPUT_DIR -replace '\\', '/')" "$Episode" "$Version" 2>&1
    
    # Affichage du résultat
    $output | ForEach-Object { Write-Host $_ }
    
    # Inspection complète du dossier de sortie (tous les fichiers)
    Write-Host "`n📁 Contenu du dossier de sortie ($OUTPUT_DIR):" -ForegroundColor Yellow
    $allFiles = @(Get-ChildItem -Path $OUTPUT_DIR -File -ErrorAction SilentlyContinue)
    
    if ($allFiles.Count -eq 0) {
        Write-Host "  Le dossier est vide" -ForegroundColor Red
    } else {
        $allFiles | ForEach-Object {
            Write-Host "  • $($_.Name) ($($_.Length) octets - $($_.LastWriteTime))" -ForegroundColor Gray
        }
    }
    
    # Vérification avec pattern explicite
    Write-Host "`n🔍 Recherche de fichiers extraits avec pattern: 'E${Episode}_SQ*_storyboard_v*.png'" -ForegroundColor Yellow
    $extractedFiles = @(Get-ChildItem -Path $OUTPUT_DIR -Filter "E${Episode}_SQ*_storyboard_v*.png" -ErrorAction SilentlyContinue)
    
    if ($extractedFiles.Count -gt 0) {
        Write-Host "✅ Extraction réussie: $($extractedFiles.Count) fichiers générés" -ForegroundColor Green
        Write-Host "Fichiers extraits (nomenclature stricte Madsea):" -ForegroundColor Cyan
        $extractedFiles | Select-Object -First 5 | ForEach-Object {
            Write-Host "  • $($_.Name) ($($_.Length) octets)" -ForegroundColor White
        }
        if ($extractedFiles.Count -gt 5) {
            Write-Host "  • ... et $($extractedFiles.Count - 5) autres fichiers" -ForegroundColor White
        }
        
        # Ouvrir l'explorateur sur le dossier
        Write-Host "`n📂 Ouverture du dossier de sortie..." -ForegroundColor Yellow
        Start-Process "explorer.exe" -ArgumentList $OUTPUT_DIR
    }
    else {
        Write-Host "❌ Aucun fichier avec le pattern 'E${Episode}_SQ*_storyboard_v*.png' trouvé dans $OUTPUT_DIR" -ForegroundColor Red
        
        # Vérifions s'il y a des fichiers dans le dossier mais avec un pattern différent
        $anyPngFiles = @(Get-ChildItem -Path $OUTPUT_DIR -Filter "*.png" -ErrorAction SilentlyContinue)
        if ($anyPngFiles.Count -gt 0) {
            Write-Host "⚠️ Cependant, il y a $($anyPngFiles.Count) fichiers PNG avec d'autres noms:" -ForegroundColor Yellow
            $anyPngFiles | Select-Object -First 5 | ForEach-Object {
                Write-Host "  • $($_.Name)" -ForegroundColor White
            }
        }
        
        # Vérifions les permissions du dossier
        try {
            $acl = Get-Acl -Path $OUTPUT_DIR
            Write-Host "📋 Permissions du dossier: $($acl.AccessToString)" -ForegroundColor Gray
        } catch {
            Write-Host "❓ Impossible de vérifier les permissions du dossier: $_" -ForegroundColor Red
        }
    }
}
catch {
    Write-Host "❌ ERREUR lors de l'extraction: $_" -ForegroundColor Red
}