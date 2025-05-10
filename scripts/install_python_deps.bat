@echo off
echo ===== INSTALLATION DEPENDANCES PYTHON MADSEA =====
echo.

cd /d I:\Madsea\backend

echo [1/3] Verification de l'environnement virtuel...
if not exist ".venv\Scripts\python.exe" (
    echo [ERREUR] Environnement virtuel non trouve
    echo Creation de l'environnement virtuel...
    python -m venv .venv
)

echo [2/3] Activation et installation des dependances...
call .venv\Scripts\activate.bat

echo Installation des dependances principales...
pip install flask flask-cors werkzeug pymupdf pillow opencv-python-headless

echo Installation specifique de pytesseract...
pip install pytesseract --upgrade

echo Installation des dependances pour ComfyUI...
pip install comfy-mcp-server websocket-client

echo [3/3] Test de configuration Tesseract...
python -c "import pytesseract; print('Configuration Tesseract en cours...'); pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'; print('Chemin Tesseract configure:',pytesseract.pytesseract.tesseract_cmd)"

echo.
echo Installation terminee. Verifiez que Tesseract est bien installe a:
echo C:\Program Files\Tesseract-OCR\tesseract.exe
echo.
echo Executez 'scripts\check_integrity.bat' pour verifier toutes les dependances.
echo.
pause