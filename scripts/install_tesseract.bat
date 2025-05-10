@echo off
setlocal

echo ===== INSTALLATION TESSERACT OCR POUR MADSEA =====
echo.
echo Ce script va installer/configurer :
echo  - Tesseract OCR (via chocolatey si disponible)
echo  - Dépendances Python requises
echo  - Configuration des chemins absolus
echo.

REM Vérifier si choco est disponible
where choco >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [AVERTISSEMENT] Chocolatey non trouvé. Installation manuelle requise.
    echo 1. Téléchargez Tesseract 5.x depuis https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Installez dans C:\Program Files\Tesseract-OCR\
    pause
) else (
    echo [INFO] Installation de Tesseract OCR via Chocolatey...
    echo [INFO] Exécutez cette commande en mode administrateur :
    echo choco install tesseract --version=5.3.3 -y
    echo.
    echo 1. Ouvrir PowerShell en admin
    echo 2. Exécuter : choco install tesseract --version=5.3.3 -y
    echo 3. Relancer ce script après installation
    pause
)

REM Vérifier si Tesseract est maintenant disponible
where tesseract >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Tesseract toujours non disponible dans le PATH
    echo Vérification alternative dans C:\Program Files\Tesseract-OCR...
    
    if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo [INFO] Tesseract trouvé à l'emplacement standard, mais pas dans le PATH
        echo [INFO] Ajout de Tesseract au PATH du script...
        set "PATH=%PATH%;C:\Program Files\Tesseract-OCR"
        echo [INFO] Le chemin est maintenant défini correctement dans le backend
    ) else (
        echo [ERREUR] Tesseract non trouvé à l'emplacement standard
        echo Veuillez l'installer manuellement depuis https://github.com/UB-Mannheim/tesseract/wiki
        echo Installez la version 5.x dans C:\Program Files\Tesseract-OCR\
        pause
        exit /b 1
    )
) else (
    echo [SUCCÈS] Tesseract trouvé dans le PATH :
    where tesseract
)

REM Installer les dépendances Python
echo [INFO] Installation des dépendances Python...
if not exist "I:\Madsea\backend\.venv\Scripts\python.exe" (
    echo [ERREUR] Environnement virtuel Python non trouvé
    echo Exécutez 'python -m venv backend\.venv' d'abord
    pause
    exit /b 1
)

echo [INFO] Installation des packages Python requis...
I:\Madsea\backend\.venv\Scripts\pip install pytesseract pillow PyMuPDF opencv-python

echo.
echo [INFO] Configuration terminée. Exécutez scripts\check_integrity.bat pour vérifier.
echo.
pause