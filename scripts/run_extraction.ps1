# PowerShell wrapper pour exécuter l'extraction via UV
# Compatible avec la nomenclature stricte Madsea
param(
    [Parameter(Mandatory=$true)]
    [string]$PdfPath,
    
    [string]$OutputDir = "i:\Madsea\outputs\extraction_test",
    
    [string]$Episode = "666",
    
    [int]$Version = 1
)

# Création du répertoire de sortie si nécessaire
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force
    Write-Host "Répertoire de sortie créé: $OutputDir"
}

# Chemin relatif du PDF pour UV
$RelativePdfPath = $PdfPath

# Si le chemin est absolu, le convertir en relatif par rapport à Madsea
if ([System.IO.Path]::IsPathRooted($PdfPath)) {
    if ($PdfPath.StartsWith("i:\Madsea\")) {
        $RelativePdfPath = $PdfPath.Substring("i:\Madsea\".Length)
    }
}

# Chemin relatif du dossier de sortie
$RelativeOutputDir = $OutputDir
if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    if ($OutputDir.StartsWith("i:\Madsea\")) {
        $RelativeOutputDir = $OutputDir.Substring("i:\Madsea\".Length)
    }
}

# Affichage des paramètres
Write-Host "Extraction avec nomenclature stricte Madsea:" -ForegroundColor Green
Write-Host "  PDF: $RelativePdfPath" -ForegroundColor Cyan
Write-Host "  Sortie: $RelativeOutputDir" -ForegroundColor Cyan
Write-Host "  Episode: $Episode" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan

# Exécution avec UV
Set-Location "i:\Madsea"
uv run scripts/test_extraction.py "$RelativePdfPath" "$RelativeOutputDir" "$Episode" "$Version"

# Vérification et affichage des résultats
$ExtractedFiles = Get-ChildItem -Path $OutputDir -Filter "E${Episode}_SQ*_storyboard_v*.png"
Write-Host "`nExtraction terminée. $($ExtractedFiles.Count) panels extraits." -ForegroundColor Green

# Affichage des premiers fichiers extraits
if ($ExtractedFiles.Count -gt 0) {
    Write-Host "Exemples de fichiers extraits (nomenclature stricte):" -ForegroundColor Cyan
    $ExtractedFiles | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $($_.Name)" -ForegroundColor White
    }
}