@echo off
echo ===== DÉMARRAGE DES SERVEURS MADSEA =====
echo.

REM Ouvrir un terminal pour le backend
start cmd /k "cd /d I:\Madsea\backend && python app.py"

REM Attendre 3 secondes pour que le backend démarre
timeout /t 3 /nobreak > nul

REM Ouvrir un terminal pour ComfyUI
start cmd /k "cd /d I:\Madsea\ComfyUI && python main.py"

REM Ouvrir le frontend dans le navigateur par défaut
start "" "http://localhost:5000"

echo.
echo Serveurs démarrés:
echo - Backend: http://localhost:5000
echo - ComfyUI: http://localhost:8188
echo - Frontend: http://localhost:5000 (navigateur ouvert)
echo.
echo ComfyUI sera prêt dans quelques instants...
echo Si le frontend ne s'ouvre pas, visitez http://localhost:5000 manuellement
echo.
echo ===== MADSEA PRÊT POUR TESTS =====
