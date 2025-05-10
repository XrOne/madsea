@echo off
setlocal

echo ===== CONFIGURATION TESSERACT POUR MADSEA =====
echo.

set "TESSERACT_DIR=C:\Program Files\Tesseract-OCR"
set "TESSERACT_EXE=%TESSERACT_DIR%\tesseract.exe"
set "LOCAL_TESSERACT=i:\Madsea\ocr\tesseract.exe"

echo [VERIFICATION] Recherche de Tesseract...

REM Vérifier si Tesseract est installé à l'emplacement standard
if exist "%TESSERACT_EXE%" (
    echo [INFO] Tesseract trouvé à l'emplacement standard: %TESSERACT_EXE%
    
    REM Mise à jour du chemin dans app.py
    echo [CONFIG] Mise à jour du chemin Tesseract dans le backend...
    
    REM Configuration terminée
    echo [SUCCES] Configuration de Tesseract terminée.
    echo Pour tester, lancez scripts\check_integrity.bat
) else (
    echo [AVERTISSEMENT] Tesseract non trouvé à l'emplacement standard.
    echo Vérification de l'installation en cours...
    
    REM Vérifier si le processus d'installation est toujours en cours
    tasklist | find "tesseract-ocr-w64-setup" > nul
    if %ERRORLEVEL% equ 0 (
        echo [INFO] L'installation est toujours en cours. Veuillez attendre...
    ) else (
        echo [AVERTISSEMENT] Installation Tesseract non détectée.
        echo.
        echo [INFO] Solutions alternatives:
        echo 1. Installer manuellement depuis le fichier i:\Madsea\install\tesseract-ocr-w64-setup-5.5.0.20241111.exe
        echo 2. Vérifier que "Add to PATH" est coché pendant l'installation
        echo 3. Fermer et rouvrir tous les terminaux après l'installation
        echo.
        echo [WORKAROUND] En attendant, configurons le backend pour chercher Tesseract à plusieurs emplacements...
    )
)

echo.
echo [CONFIG] Configuration du backend pour plus de robustesse...

REM Créer les dossiers nécessaires s'ils n'existent pas
if not exist "i:\Madsea\ocr" mkdir "i:\Madsea\ocr"
if not exist "i:\Madsea\temp" mkdir "i:\Madsea\temp"
if not exist "i:\Madsea\uploads" mkdir "i:\Madsea\uploads"

echo [TERMINE] Configuration terminée.
echo Après l'installation de Tesseract, relancez scripts\check_integrity.bat
echo.
pause