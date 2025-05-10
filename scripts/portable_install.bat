@echo off
setlocal enabledelayedexpansion

echo ===== INSTALLATION PORTABLE MADSEA =====
echo.
echo Ce script prépare une installation portable de Madsea
echo pour distribution à d'autres organisations.
echo.

set "MADSEA_ROOT=i:\Madsea"
set "PORTABLE_DIR=%MADSEA_ROOT%\portable"
set "EMBEDDED_TESSERACT=%PORTABLE_DIR%\ocr"
set "TEMP_DIR=%TEMP%\madsea_portable"

echo [1/4] Préparation de l'environnement portable...
if not exist "%PORTABLE_DIR%" mkdir "%PORTABLE_DIR%"
if not exist "%EMBEDDED_TESSERACT%" mkdir "%EMBEDDED_TESSERACT%"
if not exist "%PORTABLE_DIR%\config" mkdir "%PORTABLE_DIR%\config"

echo [2/4] Copie du Tesseract embarqué...
echo Recherche de Tesseract installé...

REM Rechercher Tesseract dans les emplacements standards
set "TESSERACT_FOUND=0"
set "TESSERACT_SOURCE="

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    set "TESSERACT_SOURCE=C:\Program Files\Tesseract-OCR"
    set "TESSERACT_FOUND=1"
)

if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
    if "!TESSERACT_FOUND!"=="0" (
        set "TESSERACT_SOURCE=C:\Program Files (x86)\Tesseract-OCR"
        set "TESSERACT_FOUND=1"
    )
)

if "!TESSERACT_FOUND!"=="1" (
    echo Tesseract trouvé: !TESSERACT_SOURCE!
    echo Copie des fichiers essentiels de Tesseract...
    
    REM Création des dossiers cibles
    if not exist "%EMBEDDED_TESSERACT%\tessdata" mkdir "%EMBEDDED_TESSERACT%\tessdata"
    
    REM Copie des exécutables et DLLs
    copy "!TESSERACT_SOURCE!\tesseract.exe" "%EMBEDDED_TESSERACT%\" >nul
    copy "!TESSERACT_SOURCE!\*.dll" "%EMBEDDED_TESSERACT%\" >nul
    
    REM Copie des données de langues (fra, eng)
    copy "!TESSERACT_SOURCE!\tessdata\fra.traineddata" "%EMBEDDED_TESSERACT%\tessdata\" >nul
    copy "!TESSERACT_SOURCE!\tessdata\eng.traineddata" "%EMBEDDED_TESSERACT%\tessdata\" >nul
    copy "!TESSERACT_SOURCE!\tessdata\osd.traineddata" "%EMBEDDED_TESSERACT%\tessdata\" >nul
    
    echo Tesseract embarqué copié dans %EMBEDDED_TESSERACT%
) else (
    echo [AVERTISSEMENT] Tesseract non trouvé sur ce système
    echo L'installation portable nécessitera Tesseract sur le système cible
    echo ou vous devrez manuellement copier les fichiers dans %EMBEDDED_TESSERACT%
)

echo [3/4] Mise à jour de la configuration...

REM Mise à jour du fichier de configuration OCR pour pointer vers le Tesseract embarqué
echo {
echo     "tesseract_paths": [
echo         "%%MADSEA_HOME%%\\ocr\\tesseract.exe",
echo         "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
echo         "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
echo     ],
echo     "embedded_mode": true,
echo     "languages": ["fra", "eng"],
echo     "default_lang": "fra",
echo     "options": {
echo         "config": "",
echo         "dpi": 300
echo     }
echo } > "%PORTABLE_DIR%\config\ocr_config.json"

echo [4/4] Création du script de lancement portable...

echo @echo off > "%PORTABLE_DIR%\start_madsea_portable.bat"
echo setlocal >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo. >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo set "MADSEA_HOME=%%~dp0.." >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo set "PATH=%%MADSEA_HOME%%\ocr;%%PATH%%" >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo. >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo echo ===== MADSEA PORTABLE - DÉMARRAGE ===== >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo echo. >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo echo Configuration Tesseract embarqué... >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo. >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo REM Copie de la configuration embarquée >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo copy /Y "%%MADSEA_HOME%%\portable\config\ocr_config.json" "%%MADSEA_HOME%%\config\" ^>nul >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo. >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo REM Lancer le script standard >> "%PORTABLE_DIR%\start_madsea_portable.bat" 
echo cd /d "%%MADSEA_HOME%%" >> "%PORTABLE_DIR%\start_madsea_portable.bat"
echo call start_madsea.bat >> "%PORTABLE_DIR%\start_madsea_portable.bat"

echo.
echo ===== INSTALLATION PORTABLE TERMINÉE =====
echo.
echo Une version portable de Madsea a été préparée dans:
echo %PORTABLE_DIR%
echo.
echo Pour distribuer à d'autres organisations:
echo 1. Copiez le dossier Madsea complet
echo 2. Demandez-leur de lancer: portable\start_madsea_portable.bat
echo.
echo Cette version inclut Tesseract embarqué et fonctionnera
echo sur n'importe quel système Windows compatible.
echo.
pause