@echo off
REM Script d'entraînement LoRA pour ComfyUI
REM Usage: train_lora.bat [dossier_images] [chemin_sortie_lora] [epochs] [learning_rate]

echo Démarrage de l'entraînement LoRA...
echo Images: %1
echo Sortie: %2
echo Epochs: %3
echo Learning Rate: %4

REM Vérifier que ComfyUI est installé
if not exist "i:\Madsea\ComfyUI\main.py" (
    echo ERREUR: ComfyUI n'est pas installé dans i:\Madsea\ComfyUI
    exit /b 1
)

REM Créer le dossier de sortie si nécessaire
if not exist "%~dp2" mkdir "%~dp2"

REM Créer un workflow temporaire pour l'entraînement LoRA
set WORKFLOW_PATH=i:\Madsea\workflows\temp_lora_training.json
echo {"nodes":[{"id":1,"type":"LoraTrainNode","input_images_dir":"%1","output_lora_path":"%2","epochs":%3,"learning_rate":%4,"batch_size":4,"resolution":"768,768"}]} > %WORKFLOW_PATH%

REM Copier les images dans le dossier input de ComfyUI
set COMFYUI_INPUT=i:\Madsea\ComfyUI\input\lora_training
mkdir %COMFYUI_INPUT% 2>NUL
xcopy /E /Y "%1\*" "%COMFYUI_INPUT%\"

REM Lancer ComfyUI avec le workflow
start "ComfyUI" /B /WAIT python "i:\Madsea\ComfyUI\main.py" --port 8188

REM Utiliser l'API pour lancer l'entraînement
curl -X POST http://localhost:8188/api/queue -H "Content-Type: application/json" -d @%WORKFLOW_PATH%

echo Entraînement LoRA démarré!
echo Une fois terminé, le modèle sera sauvegardé dans: %2
echo Consultez l'interface ComfyUI sur http://localhost:8188 pour suivre l'avancement