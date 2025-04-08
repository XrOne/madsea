@echo off
setlocal enabledelayedexpansion

echo ===============================================================
echo  Installation Madsea (Storyboard-to-Video AI) - Revised
echo ===============================================================
echo.

:: Configuration
set VENV_DIR=venv
set LOG_FILENAME=installation_revised_log.txt
set LOG_FILE=logs\%LOG_FILENAME%
set COMFYUI_DIR=ComfyUI

:: Créer le répertoire de logs
echo Tentative de creation du dossier logs...
if not exist logs mkdir logs
if not exist logs (
    echo ERREUR: Impossible de creer le dossier logs.
    pause
    exit /b 1
)
echo Dossier logs OK.

:: Vider/Creer le fichier log initial
(echo Installation demarree a %date% %time%) > %LOG_FILE%
if not exist %LOG_FILE% (
    echo ERREUR: Impossible de creer le fichier log %LOG_FILE%
    pause
    exit /b 1
)
echo Fichier log %LOG_FILE% cree.

:: === Fonctions Helper (Simplifiees) ===
:log
  :: Affiche seulement a la console
  echo [%time%] %~1
  :: Ecrit aussi dans le log
  echo [%time%] %~1 >> %LOG_FILE%
  goto :eof

:log_error
  :: Affiche seulement a la console
  echo [%time%] ERREUR: %~1
  :: Ecrit aussi dans le log
  echo [%time%] ERREUR: %~1 >> %LOG_FILE%
  goto :eof

:check_command
where /q %1
if %errorlevel% neq 0 (
    call :log_error "%1 non trouve. Veuillez l'installer ou verifier votre PATH."
    exit /b 1
)
goto :eof
:: === Fin Fonctions Helper ===

:: --- 1. Vérification Préalable ---
:: Removed debug pauses
call :log "--- Etape 1: Verification des outils requis ---"

:: Vérifier winget
call :log "Verification de winget..."
where /q winget
if %errorlevel% neq 0 (
    call :log "winget non trouve. Tentative d'installation des outils manuels..."
    set USE_WINGET=0
) else (
    call :log "winget trouve."
    set USE_WINGET=1
)

:: Vérifier Git
call :log "Verification de Git..."
where /q git
if %errorlevel% neq 0 (
    if %USE_WINGET%==1 (
        call :log "Installation de Git via winget..."
        winget install -e --id Git.Git >> %LOG_FILE%
        if %errorlevel% neq 0 (
            call :log_error "Echec de l'installation de Git via winget."
            goto manual_install_prompt
        )
    ) else (
        goto manual_install_prompt
    )
)
call :log "Git OK."

:: Vérifier Python (besoin d'une version >= 3.10)
call :log "Verification de Python 3.10+..."
python --version > nul 2>&1
if %errorlevel% neq 0 (
    if %USE_WINGET%==1 (
        call :log "Installation de Python 3.11 via winget..."
        winget install -e --id Python.Python.3.11 >> %LOG_FILE%
        if %errorlevel% neq 0 (
            call :log_error "Echec de l'installation de Python via winget."
             goto manual_install_prompt
        )
         call :log "IMPORTANT: Fermez et relancez ce script dans un NOUVEAU terminal pour que Python soit detecte."
         pause
         exit /b 1
    ) else (
         goto manual_install_prompt
    )
)
call :log "Python OK."


:: --- 2. Installation Outils Externes (FFmpeg, Tesseract) ---
call :log "--- Etape 2: Installation des outils externes (FFmpeg, Tesseract) ---"
set FFMPEG_OK=0
set TESSERACT_OK=0

:: Vérifier/Installer FFmpeg
call :log "Verification de FFmpeg..."
where /q ffmpeg
if %errorlevel% == 0 (
    call :log "FFmpeg deja installe."
    set FFMPEG_OK=1
) else (
    if %USE_WINGET%==1 (
        call :log "Installation de FFmpeg via winget..."
        winget install -e --id FFmpeg.FFmpeg >> %LOG_FILE%
        if %errorlevel% == 0 (
            call :log "FFmpeg installe via winget."
            set FFMPEG_OK=1
        ) else (
            call :log_error "Echec de l'installation de FFmpeg via winget."
        )
    )
)
if %FFMPEG_OK%==0 (
     call :log "ATTENTION: FFmpeg n'a pas pu etre installe automatiquement."
     call :log "Veuillez l'installer manuellement depuis https://ffmpeg.org/download.html"
     call :log "et assurez-vous que le dossier 'bin' est dans votre PATH systeme."
     call :log "L'assemblage video ne fonctionnera pas sans FFmpeg."
     pause
)

:: Vérifier/Installer Tesseract
call :log "Verification de Tesseract OCR..."
where /q tesseract
if %errorlevel% == 0 (
     call :log "Tesseract OCR deja installe."
     set TESSERACT_OK=1
) else (
    if %USE_WINGET%==1 (
        call :log "Installation de Tesseract OCR via winget..."
        winget install -e --id Tesseract.Tesseract >> %LOG_FILE%
         if %errorlevel% == 0 (
             call :log "Tesseract OCR installe via winget."
             call :log "ATTENTION: Vous devrez peut-etre ajouter manuellement le dossier d'installation de Tesseract a votre PATH systeme."
             call :log "(Ex: C:\Program Files\Tesseract-OCR)"
             set TESSERACT_OK=1
        ) else (
             call :log_error "Echec de l'installation de Tesseract via winget."
         )
    )
)
if %TESSERACT_OK%==0 (
    call :log "ATTENTION: Tesseract OCR n'a pas pu etre installe automatiquement."
    call :log "Veuillez l'installer manuellement depuis https://github.com/tesseract-ocr/tesseract"
    call :log "et assurez-vous qu'il est dans votre PATH systeme."
    call :log "L'analyse de certains storyboards pourrait echouer sans Tesseract."
    pause
)

:: --- 3. Environnement Virtuel Python ---
call :log "--- Etape 3: Creation de l'environnement virtuel Python (%VENV_DIR%) ---"
if exist %VENV_DIR% (
    call :log "Le dossier %VENV_DIR% existe deja. Suppression..."
    rd /s /q %VENV_DIR%
)
python -m venv %VENV_DIR% >> %LOG_FILE%
if %errorlevel% neq 0 (
    call :log_error "Echec de la creation de l'environnement virtuel."
    pause
    exit /b 1
)
call :log "Environnement virtuel cree."

:: --- 4. Installation des Dependances Python ---
call :log "--- Etape 4: Installation des dependances Python dans %VENV_DIR% ---"
call :log "Mise a jour de pip..."
call %VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip >> %LOG_FILE%
if %errorlevel% neq 0 ( call :log "Attention: Echec de la mise a jour de pip." )

call :log "Installation des dependances depuis requirements.txt..."
call %VENV_DIR%\Scripts\python.exe -m pip install -r requirements.txt >> %LOG_FILE%
if %errorlevel% neq 0 (
    call :log_error "Echec de l'installation des dependances Python. Verifiez %LOG_FILE%."
    pause
    exit /b 1
)
call :log "Dependances Python installees."

:: --- 5. Clonage/Mise à jour de ComfyUI ---
call :log "--- Etape 5: Verification/Installation de ComfyUI ---"
if not exist %COMFYUI_DIR% (
    call :log "Clonage de ComfyUI depuis GitHub..."
    git clone https://github.com/comfyanonymous/ComfyUI.git %COMFYUI_DIR% >> %LOG_FILE%
    if %errorlevel% neq 0 (
        call :log_error "Echec du clonage de ComfyUI."
        pause
        exit /b 1
    )
    call :log "ComfyUI clone."
) else (
    call :log "Mise a jour de ComfyUI..."
    cd %COMFYUI_DIR%
    git pull >> ..\%LOG_FILE%
    cd ..
    call :log "ComfyUI mis a jour."
)

:: --- 6. Installation des Dépendances ComfyUI ---
call :log "--- Etape 6: Installation des dependances ComfyUI ---"
call :log "Installation depuis ComfyUI/requirements.txt..."
call %VENV_DIR%\Scripts\python.exe -m pip install -r %COMFYUI_DIR%\requirements.txt >> %LOG_FILE%
if %errorlevel% neq 0 (
    call :log "Attention: Echec de l'installation des dependances ComfyUI. Certaines fonctionnalites pourraient manquer."
) else (
    call :log "Dependances ComfyUI installees."
)

:: --- 7. Message Final ---
call :log "--- Installation Terminee ---"
echo.
echo L'installation de base de Madsea est terminee.
echo.
echo *** ETAPES SUIVANTES IMPORTANTES ***
echo 1. Lancer ComfyUI:
echo    Ouvrez un NOUVEAU terminal, allez dans le dossier '%cd%\%COMFYUI_DIR%' et executez:
echo    ..\venv\Scripts\python.exe main.py
echo    Laissez ce terminal ouvert.
echo.
echo 2. Lancer Madsea:
echo    Ouvrez un AUTRE NOUVEAU terminal, restez dans le dossier '%cd%' et executez:
echo    venv\Scripts\python.exe startup.py --web
echo.
echo L'interface web Madsea sera accessible a l'adresse indiquee (generalement http://127.0.0.1:5000).
echo.
echo Pour configurer les cles API (Gemini, etc.), modifiez le fichier config/default.yaml.
echo.
pause
exit /b 0

:manual_install_prompt
call :log_error "Un outil requis (Git, Python, ou winget) n'a pas pu etre installe/trouve automatiquement."
call :log "Veuillez installer manuellement les elements suivants:"
call :log " - Git: https://git-scm.com/download/win"
call :log " - Python 3.10 ou 3.11: https://www.python.org/downloads/windows/"
call :log " - FFmpeg: https://ffmpeg.org/download.html"
call :log " - Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
call :log "Assurez-vous qu'ils sont ajoutes a votre PATH systeme."
call :log "Relancez ce script apres les installations manuelles."
pause
exit /b 1 