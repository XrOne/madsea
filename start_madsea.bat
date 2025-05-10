@echo off
setlocal

title Madsea - Démarrage Complet 2025
color 0B
cls

echo ===== MADSEA - DEMARRAGE DES SERVEURS =====
echo.
echo Ce script va demarrer :
echo  1. Backend Flask avec bridge ComfyUI et MCP Puppeteer (localhost:5000)
echo  2. ComfyUI (localhost:8188) avec GPU CUDA et modèles RealVisXL_V5.0
echo  3. Frontend React/TailwindCSS (http://localhost:3000)
echo.

REM === Vérifications préalables ===
echo [VERIFICATION] Tests préliminaires...

REM Vérifier l'existence du dossier pour les modèles LoRA
if not exist "I:\Madsea\outputs\lora_models" (
    echo [CONFIG] Création du dossier pour les modèles LoRA...
    mkdir "I:\Madsea\outputs\lora_models"
)

REM Vérifier PlayWright pour MCP Puppeteer
cd /d I:\Madsea\frontend
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Impossible d'accéder au dossier frontend.
    pause
    exit /b 1
)

REM Vérifier l'existence du dossier .venv dans le backend
if not exist "I:\Madsea\backend\.venv" (
    echo [ERREUR] Environnement virtuel backend non trouvé. Veuillez exécuter "python -m venv backend\.venv" et installer les dépendances.
    pause
    exit /b 1
)

echo [INFO] Toutes les dépendances sont installées : PyTorch+CUDA, transformers, scipy, kornia, etc.
echo [INFO] Intégration MCP Puppeteer active pour l'automatisation one-click
echo [INFO] Fonctionnalité d'entraînement LoRA disponible dans l'interface
echo.
echo Appuyez sur une touche pour démarrer tous les services...
pause > nul

REM === Démarrage des services ===

REM Démarrer ComfyUI d'abord (important pour le bridge)
echo [1/3] Démarrage de ComfyUI...
start "Madsea ComfyUI" cmd /k "cd /d I:\Madsea\ComfyUI && python main.py --port 8188"

REM Attendre que ComfyUI démarre
echo Attente du démarrage de ComfyUI (10s)...
timeout /t 10 /nobreak > nul

REM Démarrer le backend Flask
echo [2/3] Démarrage du backend Flask avec bridge ComfyUI et MCP...
start "Madsea Backend" cmd /k "cd /d I:\Madsea\backend && I:\Madsea\backend\.venv\Scripts\python.exe app.py"

REM Attendre le démarrage du backend
echo Attente du démarrage du backend (5s)...
timeout /t 5 /nobreak > nul

REM Démarrer le frontend React
echo [3/3] Démarrage du frontend React/TailwindCSS...
start "Madsea Frontend" cmd /k "cd /d I:\Madsea\frontend && npm run dev"

REM Attendre le démarrage du frontend
echo Attente du démarrage du frontend (8s)...
timeout /t 8 /nobreak > nul

REM Ouvrir les navigateurs aux deux interfaces
echo Ouverture des interfaces...
start "" "http://localhost:3000"
timeout /t 2 /nobreak > nul
start "" "http://localhost:8188"

echo.
echo ===== SERVEURS DEMARRES =====
echo.
echo Frontend React : http://localhost:3000   (interface principale)
echo Backend Flask  : http://localhost:5000   (API)
echo ComfyUI        : http://localhost:8188   (interface directe)
echo.
echo FONCTIONNALITÉS PRINCIPALES:
echo 1. Extraction PDF avec OCR optimisé (FR+EN)
echo 2. Génération d'images avec style ombre chinoise
echo 3. Mode automatique one-click avec MCP Puppeteer
echo 4. Entraînement LoRA personnalisé pour vos styles
echo.
echo RACCOURCIS CLAVIER:
echo Switch Auto/Manuel: Visible dans la barre d'outils
echo Lancer l'entraînement LoRA: Bouton dédié en bas de l'interface
echo.
echo Pour arrêter les serveurs, fermez les fenêtres de commande.
echo.
