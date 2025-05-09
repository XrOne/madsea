@echo off
echo ===== MADSEA - DEMARRAGE DES SERVEURS =====
echo.
echo Ce script va demarrer :
echo  1. Backend Flask avec bridge ComfyUI (localhost:5000)
echo  2. ComfyUI (localhost:8188)
echo  3. Frontend React/TailwindCSS (via backend)
echo.
echo Appuyez sur une touche pour continuer...
pause > nul

REM Demarrer le backend dans sa propre fenetre
echo Demarrage du backend Flask avec bridge ComfyUI...
start "Madsea Backend" cmd /k "cd /d I:\Madsea\backend && python app.py"

REM Attendre 5 secondes pour que le backend se lance
echo Attente du démarrage du backend (5s)...
timeout /t 5 /nobreak > nul

REM Demarrer ComfyUI dans sa propre fenetre
echo Demarrage de ComfyUI...
start "Madsea ComfyUI" cmd /k "cd /d I:\Madsea\ComfyUI && python main.py"

REM Attendre 8 secondes pour que ComfyUI se lance
echo Attente du démarrage de ComfyUI (8s)...
timeout /t 8 /nobreak > nul

REM Ouvrir le navigateur vers le frontend servi par Flask
echo Ouverture du frontend via le backend Flask...
start "" "http://localhost:5000"

echo.
echo ===== SERVEURS DEMARRES =====
echo.
echo Backend Flask  : http://localhost:5000   (interface principale)
echo ComfyUI        : http://localhost:8188   (interface directe, optionnelle)
echo Bridge ComfyUI : Intégré au backend
echo.
echo FLUX DE TRAVAIL:
echo 1. Utiliser l'interface principale (http://localhost:5000)
echo 2. Importer un storyboard PDF
echo 3. Sélectionner les plans à générer
echo 4. Envoyer à ComfyUI via le bridge
echo.
echo Pour arreter les serveurs, fermez les fenetres de commande.
echo.
