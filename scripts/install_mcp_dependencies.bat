@echo off
echo ===== INSTALLATION DES DEPENDANCES MCP POUR MADSEA =====
echo.
echo Ce script va installer:
echo  - comfy-mcp-server (pour l'intégration avec MCP Puppeteer)
echo  - Les dépendances manquantes pour l'automatisation
echo.

REM Vérifier que l'environnement virtuel existe
if not exist "I:\Madsea\backend\.venv\Scripts\python.exe" (
    echo [ERREUR] Environnement virtuel backend non trouvé.
    echo Veuillez d'abord créer l'environnement avec "python -m venv backend\.venv"
    pause
    exit /b 1
)

REM Installation de comfy-mcp-server
echo [1/2] Installation de comfy-mcp-server...
I:\Madsea\backend\.venv\Scripts\python.exe -m pip install comfy-mcp-server

REM Installation des autres dépendances
echo [2/2] Installation des dépendances complémentaires...
I:\Madsea\backend\.venv\Scripts\python.exe -m pip install flask_cors werkzeug uuid

echo.
echo ===== INSTALLATION TERMINÉE =====
echo.
echo Toutes les dépendances sont maintenant installées.
echo Vous pouvez lancer Madsea avec le script start_madsea.bat
echo.
pause