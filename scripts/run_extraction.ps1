# PowerShell wrapper pour exécuter l'extraction via UV
# Compatible avec la nomenclature stricte Madsea et gestion des chemins Windows sécurisée
param(
    [Parameter(Mandatory=$true)]
    [string]$PdfPath,
    
    [string]$OutputDir = "i:\Madsea\outputs\extraction_test",
    
    [string]$Episode = "666",
    
    [int]$Version = 1
)

# Fonction pour normaliser les chemins et garantir qu'ils fonctionnent avec PyMuPDF
function NormalizePath {
    param([string]$Path)
    # Ne touche pas aux espaces, convertit juste les backslashs
    return $Path -replace '\\', '/'
}

# Fonction pour vérifier si un fichier existe et retourne son chemin absolu
function ValidateFile {
    param([string]$Path)
    
    # Vérifier si c'est un chemin absolu
    if ([System.IO.Path]::IsPathRooted($Path)) {
        if (Test-Path $Path) {
            return $Path
        }
    } else {
        # Si c'est un chemin relatif, essayer plusieurs bases
        $bases = @(
            (Get-Location),
            "i:\Madsea"
        )
        
        foreach ($base in $bases) {
            $fullPath = Join-Path $base $Path
            if (Test-Path $fullPath) {
                return $fullPath
            }
        }
    }
    
    Write-Host "ERREUR: Fichier non trouvé: $Path" -ForegroundColor Red
    Write-Host "Veuillez vérifier que le fichier existe et que le chemin est correct." -ForegroundColor Yellow
    exit 1
}

# Création du répertoire de sortie si nécessaire
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force
    Write-Host "Répertoire de sortie créé: $OutputDir" -ForegroundColor Green
}

# Valider et obtenir le chemin absolu du PDF
$AbsolutePdfPath = ValidateFile $PdfPath
Write-Host "PDF trouvé: $AbsolutePdfPath" -ForegroundColor Green

# Obtenir le chemin absolu du dossier de sortie
$AbsoluteOutputDir = $OutputDir
if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $AbsoluteOutputDir = Join-Path (Get-Location) $OutputDir
}

# Normaliser les chemins pour PyMuPDF (utiliser des forward slashes)
$NormalizedPdfPath = NormalizePath $AbsolutePdfPath
$NormalizedOutputDir = NormalizePath $AbsoluteOutputDir

# Affichage des paramètres
Write-Host "Extraction avec nomenclature stricte Madsea:" -ForegroundColor Green
Write-Host "  PDF: $NormalizedPdfPath" -ForegroundColor Cyan
Write-Host "  Sortie: $NormalizedOutputDir" -ForegroundColor Cyan
Write-Host "  Episode: $Episode" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan

# Affichage du chemin transmis à Python pour traçabilité
Write-Host "Appel Python avec : $NormalizedPdfPath" -ForegroundColor Yellow

# Exécution avec UV (toujours utiliser des chemins absolus normalisés pour éviter les erreurs de chemin)
Set-Location "i:\Madsea"
uv run scripts/test_extraction.py "$NormalizedPdfPath" "$NormalizedOutputDir" "$Episode" "$Version"

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