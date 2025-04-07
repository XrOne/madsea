@echo off
setlocal enabledelayedexpansion

echo ===============================================================
echo  Installation du package Madsea (Storyboard-to-Video AI)
echo  Pour artistes et créateurs
echo ===============================================================
echo.

:: Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERREUR: Veuillez exécuter ce script en tant qu'administrateur
    echo Clic droit sur le fichier -^> Exécuter en tant qu'administrateur
    pause
    exit /b 1
)

:: Créer le répertoire de logs
if not exist logs mkdir logs

:: Fichier de log
set LOG_FILE=logs\installation_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

echo Installation démarrée à %date% %time% > %LOG_FILE%
echo.

:: Fonction pour afficher et logger
:log
echo %~1
echo %~1 >> %LOG_FILE%
exit /b 0

:: Vérifier si Python est installé
call :log "Vérification de Python..."
python --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "Python n'est pas installé. Installation de Python 3.10..."
    
    :: Télécharger Python
    call :log "Téléchargement de Python 3.10.11..."
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    
    :: Installer Python
    call :log "Installation de Python 3.10.11..."
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Supprimer l'installateur
    del python_installer.exe
    
    :: Vérifier l'installation
    python --version >nul 2>&1
    if %errorLevel% neq 0 (
        call :log "ERREUR: L'installation de Python a échoué."
        pause
        exit /b 1
    )
    
    call :log "Python 3.10.11 installé avec succès."
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
    call :log "Python %PYTHON_VERSION% est déjà installé."
)

:: Installer les dépendances Python
call :log "Installation des dépendances Python..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Vérifier si FFmpeg est installé
call :log "Vérification de FFmpeg..."
ffmpeg -version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "FFmpeg n'est pas installé. Installation de FFmpeg..."
    
    :: Créer le répertoire pour FFmpeg
    if not exist tools mkdir tools
    
    :: Télécharger FFmpeg
    call :log "Téléchargement de FFmpeg..."
    curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
    
    :: Extraire FFmpeg
    call :log "Extraction de FFmpeg..."
    powershell -command "Expand-Archive -Force ffmpeg.zip tools/"
    
    :: Déplacer les fichiers FFmpeg
    for /d %%a in (tools\ffmpeg-*) do (
        move "%%a\bin\*" tools\
        rd /s /q "%%a"
    )
    
    :: Ajouter FFmpeg au PATH
    setx PATH "%PATH%;%cd%\tools" /M
    
    :: Supprimer l'archive
    del ffmpeg.zip
    
    call :log "FFmpeg installé avec succès."
) else (
    call :log "FFmpeg est déjà installé."
)

:: Vérifier si Tesseract OCR est installé
call :log "Vérification de Tesseract OCR..."
tesseract --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "Tesseract OCR n'est pas installé. Installation de Tesseract OCR..."
    
    :: Télécharger Tesseract OCR
    call :log "Téléchargement de Tesseract OCR..."
    curl -L -o tesseract_installer.exe https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe
    
    :: Installer Tesseract OCR
    call :log "Installation de Tesseract OCR..."
    start /wait tesseract_installer.exe /S /D=%cd%\tools\tesseract
    
    :: Ajouter Tesseract au PATH
    setx PATH "%PATH%;%cd%\tools\tesseract" /M
    
    :: Supprimer l'installateur
    del tesseract_installer.exe
    
    call :log "Tesseract OCR installé avec succès."
) else (
    call :log "Tesseract OCR est déjà installé."
)

:: Vérifier si ComfyUI est installé
call :log "Vérification de ComfyUI..."
if not exist ComfyUI (
    call :log "ComfyUI n'est pas installé. Installation de ComfyUI..."
    
    :: Cloner ComfyUI
    call :log "Téléchargement de ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
    
    :: Installer les dépendances de ComfyUI
    cd ComfyUI
    call :log "Installation des dépendances de ComfyUI..."
    python -m pip install -r requirements.txt
    cd ..
    
    call :log "ComfyUI installé avec succès."
) else (
    call :log "ComfyUI est déjà installé."
)

:: Vérifier si Ollama est installé (pour Qwen 2.1)
call :log "Vérification d'Ollama..."
ollama list >nul 2>&1
if %errorLevel% neq 0 (
    call :log "Ollama n'est pas installé. Installation d'Ollama..."
    
    :: Télécharger Ollama
    call :log "Téléchargement d'Ollama..."
    curl -L -o ollama_installer.exe https://github.com/ollama/ollama/releases/download/v0.1.20/ollama-windows-amd64.exe
    
    :: Installer Ollama
    call :log "Installation d'Ollama..."
    move ollama_installer.exe tools\ollama.exe
    
    :: Ajouter Ollama au PATH
    setx PATH "%PATH%;%cd%\tools" /M
    
    call :log "Ollama installé avec succès."
) else (
    call :log "Ollama est déjà installé."
)

:: Créer un script de démarrage facile
call :log "Création du script de démarrage..."
echo @echo off > start_madsea.bat
echo echo Démarrage de Madsea (Storyboard-to-Video AI)... >> start_madsea.bat
echo echo. >> start_madsea.bat
echo start "ComfyUI" cmd /c "cd ComfyUI && python main.py" >> start_madsea.bat
echo timeout /t 5 >> start_madsea.bat
echo start "Madsea" cmd /c "python startup.py --web" >> start_madsea.bat
echo echo. >> start_madsea.bat
echo echo Interface web accessible à http://127.0.0.1:5000 >> start_madsea.bat
echo echo Appuyez sur Ctrl+C pour quitter >> start_madsea.bat
echo pause >> start_madsea.bat

:: Créer un raccourci sur le bureau
call :log "Création du raccourci sur le bureau..."
powershell -command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\Madsea.lnk'); $Shortcut.TargetPath = '%cd%\start_madsea.bat'; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.IconLocation = '%cd%\ui\static\favicon.ico,0'; $Shortcut.Description = 'Madsea - Storyboard-to-Video AI'; $Shortcut.Save()"

:: Installation terminée
call :log "Installation terminée avec succès!"
call :log "Vous pouvez démarrer Madsea en double-cliquant sur le raccourci 'Madsea' sur votre bureau."
call :log "Ou en exécutant le fichier 'start_madsea.bat' dans le répertoire d'installation."
echo.
echo Pour configurer les modèles externes (Qwen 2.1, Google Gemini, WAN 2.1),
echo exécutez: python startup.py --install-models
echo.

pause