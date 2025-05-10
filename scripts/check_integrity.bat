@echo off
setlocal

echo === Vérification intégrité Madsea ===
echo.

echo [1/3] Vérification Tesseract...
where tesseract
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Tesseract non installé
    echo Solution: choco install tesseract
) else (
    echo OK
)

echo [2/3] Vérification Python et dépendances...
if not exist "I:\Madsea\backend\.venv\Scripts\python.exe" (
    echo [ERREUR] Environnement virtuel manquant
) else (
    "I:\Madsea\backend\.venv\Scripts\python.exe" -c "import pytesseract, fitz; pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'; print(f'PyMuPDF {fitz.__version__}, Tesseract {pytesseract.get_tesseract_version()}')"
    if %ERRORLEVEL% neq 0 echo [ERREUR] Dépendances manquantes
)

echo [3/3] Vérification dossiers critiques...
for %%d in (temp uploads outputs projects) do (
    if exist "I:\Madsea\%%d" (
        echo %%d: OK 
    ) else (
        echo [ALERTE] Dossier manquant: %%d
    )
)

echo.
echo === Résumé ===
echo Exécutez 'start_madsea.bat' si tout est OK
pause
