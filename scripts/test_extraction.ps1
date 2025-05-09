# Script PowerShell pour tester l'API d'extraction avec OCR
$filePath = "D:\Mad films\visuels\storyboard\E202_nanoTech 2024-04-09 11.25.08.pdf"
$projectId = "proj_test_001"
$episodeId = "ep_test_001"
$ocrEnabled = "true"
$apiUrl = "http://localhost:5000/api/extraction_storyboard"

# Préparation de la requête multipart/form-data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = @()
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"project_id`""
$bodyLines += ""
$bodyLines += "$projectId"
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"episode_id`""
$bodyLines += ""
$bodyLines += "$episodeId"
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"ocr_enabled`""
$bodyLines += ""
$bodyLines += "$ocrEnabled"
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"storyboard_file`"; filename=`"$(Split-Path $filePath -Leaf)`""
$bodyLines += "Content-Type: application/pdf"
$bodyLines += ""
$bodyLines += [System.IO.File]::ReadAllText($filePath)
$bodyLines += "--$boundary--"

$body = $bodyLines -join $LF

# Envoi de la requête
try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $body
    # Affichage de la réponse
    $response | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "Erreur lors de l'appel à l'API : $_"
}
