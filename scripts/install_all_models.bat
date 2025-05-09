@echo off
setlocal enabledelayedexpansion

echo ===============================================================
echo  Installation des modèles externes pour Madsea
echo  (Qwen 2.1, Google Gemini Studio, WAN 2.1)
echo ===============================================================
echo.

:: Vérifier si Ollama est installé
ollama list >nul 2>&1
if %errorLevel% neq 0 (
    echo ERREUR: Ollama n'est pas installé.
    echo Veuillez d'abord exécuter le script d'installation principal (install_windows.bat)
    pause
    exit /b 1
)

:: Installer le modèle Qwen 2.1
echo Installation du modèle Qwen 2.1 via Ollama...
echo (Cette opération peut prendre plusieurs minutes)
echo.

:: Vérifier si le modèle est déjà installé
ollama list | findstr "qwen2:1.5b" >nul 2>&1
if %errorLevel% neq 0 (
    echo Téléchargement et installation du modèle Qwen 2.1...
    ollama pull qwen2:1.5b
    
    if %errorLevel% neq 0 (
        echo ERREUR: L'installation du modèle Qwen 2.1 a échoué.
        pause
        exit /b 1
    )
    
    echo Modèle Qwen 2.1 installé avec succès.
) else (
    echo Le modèle Qwen 2.1 est déjà installé.
)

echo.

:: Configuration des clés API
echo Configuration des clés API pour Google Gemini Studio et WAN 2.1...
echo.

:: Créer le fichier de configuration si nécessaire
if not exist config\external_models.yaml (
    if not exist config mkdir config
    
    echo # Configuration des modèles externes > config\external_models.yaml
    echo external_models: >> config\external_models.yaml
    echo   use_qwen: true >> config\external_models.yaml
    echo   use_gemini: true >> config\external_models.yaml
    echo   use_wan: true >> config\external_models.yaml
    echo   gemini_api_key: "" >> config\external_models.yaml
    echo   wan_api_key: "" >> config\external_models.yaml
)

:: Demander la clé API Google Gemini Studio
set /p GEMINI_API_KEY=Entrez votre clé API Google Gemini Studio (ou appuyez sur Entrée pour ignorer): 

if not "%GEMINI_API_KEY%"=="" (
    powershell -command "(Get-Content config\external_models.yaml) -replace 'gemini_api_key: .*', 'gemini_api_key: "%GEMINI_API_KEY%"' | Set-Content config\external_models.yaml"
    echo Clé API Google Gemini Studio enregistrée.
)

:: Demander la clé API WAN 2.1
set /p WAN_API_KEY=Entrez votre clé API WAN 2.1 (ou appuyez sur Entrée pour ignorer): 

if not "%WAN_API_KEY%"=="" (
    powershell -command "(Get-Content config\external_models.yaml) -replace 'wan_api_key: .*', 'wan_api_key: "%WAN_API_KEY%"' | Set-Content config\external_models.yaml"
    echo Clé API WAN 2.1 enregistrée.
)

echo.
echo Configuration des modèles externes terminée.
echo.
echo Pour tester les modèles, démarrez Madsea et accédez à l'interface web.
echo.

pause