@echo off
setlocal enabledelayedexpansion

echo ===============================================================
echo  Création du package d'installation Madsea
echo  Pour artistes et créateurs
echo ===============================================================
echo.

:: Vérifier si 7-Zip est installé
where 7z >nul 2>&1
if %errorLevel% neq 0 (
    echo AVERTISSEMENT: 7-Zip n'est pas installé ou n'est pas dans le PATH.
    echo Le package sera créé avec PowerShell Compress-Archive (moins efficace).
    set USE_POWERSHELL=1
) else (
    set USE_POWERSHELL=0
)

:: Créer le répertoire de sortie
if not exist dist mkdir dist

:: Définir le nom du package
set PACKAGE_NAME=Madsea_Installation_Package_v1.0.0
set PACKAGE_DIR=dist\%PACKAGE_NAME%

:: Supprimer le répertoire s'il existe déjà
if exist %PACKAGE_DIR% rd /s /q %PACKAGE_DIR%

:: Créer la structure du package
echo Création de la structure du package...
mkdir %PACKAGE_DIR%
mkdir %PACKAGE_DIR%\config
mkdir %PACKAGE_DIR%\parsing
mkdir %PACKAGE_DIR%\generation
mkdir %PACKAGE_DIR%\styles
mkdir %PACKAGE_DIR%\video
mkdir %PACKAGE_DIR%\ui
mkdir %PACKAGE_DIR%\ui\static
mkdir %PACKAGE_DIR%\ui\templates
mkdir %PACKAGE_DIR%\utils
mkdir %PACKAGE_DIR%\workflows

:: Copier les fichiers principaux
echo Copie des fichiers principaux...
copy install_windows.bat %PACKAGE_DIR%\
copy install_all_models.bat %PACKAGE_DIR%\
copy README_INSTALLATION.md %PACKAGE_DIR%\README.md
copy GUIDE_INSTALLATION.md %PACKAGE_DIR%\
copy requirements.txt %PACKAGE_DIR%\
copy main.py %PACKAGE_DIR%\
copy startup.py %PACKAGE_DIR%\

:: Copier les fichiers de configuration
copy config\default.yaml %PACKAGE_DIR%\config\

:: Copier les modules Python
xcopy /E /I parsing\* %PACKAGE_DIR%\parsing\
xcopy /E /I generation\* %PACKAGE_DIR%\generation\
xcopy /E /I styles\* %PACKAGE_DIR%\styles\
xcopy /E /I video\* %PACKAGE_DIR%\video\
xcopy /E /I utils\* %PACKAGE_DIR%\utils\
xcopy /E /I ui\* %PACKAGE_DIR%\ui\
xcopy /E /I workflows\* %PACKAGE_DIR%\workflows\

:: Créer le fichier ZIP
echo Création du package ZIP...

if %USE_POWERSHELL%==1 (
    powershell -command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'dist\%PACKAGE_NAME%.zip' -Force"
) else (
    cd dist
    7z a -tzip %PACKAGE_NAME%.zip %PACKAGE_NAME%
    cd ..
)

echo.
echo Package créé avec succès: dist\%PACKAGE_NAME%.zip
echo.
echo Ce package contient tous les éléments nécessaires pour installer
echo et utiliser Madsea sur un système Windows.
echo.

pause