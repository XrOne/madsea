#!/bin/bash

# Configuration
MADSEA_DIR="/mnt/i/Madsea"
COMFYUI_DIR="$MADSEA_DIR/ComfyUI"
VENV_ACTIVATE="$MADSEA_DIR/venv/bin/activate"
MADSEA_LOG="$MADSEA_DIR/madsea.log"
COMFYUI_LOG="$MADSEA_DIR/comfyui.log"

echo "Démarrage des serveurs..."

# Vérifier si les répertoires existent
if [ ! -d "$MADSEA_DIR" ]; then
    echo "Erreur: Le répertoire Madsea n'existe pas: $MADSEA_DIR"
    exit 1
fi

if [ ! -d "$COMFYUI_DIR" ]; then
    echo "Erreur: Le répertoire ComfyUI n'existe pas: $COMFYUI_DIR"
    exit 1
fi

# Vérifier si l'environnement virtuel existe
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Erreur: L'environnement virtuel n'existe pas: $VENV_ACTIVATE"
    exit 1
fi

# Fonction pour arrêter les processus
cleanup() {
    echo "Arrêt des serveurs..."
    pkill -f "python startup.py"
    pkill -f "python main.py"
    exit 0
}

# Capture du signal d'interruption
trap cleanup SIGINT SIGTERM

# Activer l'environnement virtuel
source "$VENV_ACTIVATE"

# Lancer Madsea
cd "$MADSEA_DIR"
echo "Démarrage de Madsea..."
python startup.py > "$MADSEA_LOG" 2>&1 &
MADSEA_PID=$!

# Lancer ComfyUI
cd "$COMFYUI_DIR"
echo "Démarrage de ComfyUI..."
nohup bash -c "source \"$VENV_ACTIVATE\" && cd \"$COMFYUI_DIR\" && echo '--- ComfyUI Server Log Start ---' && python3 \"$COMFYUI_START_SCRIPT\" --port 8188" > "$COMFYUI_LOG" 2>&1 &
COMFYUI_PID=$!
sleep 5 # Augmentation du délai à 5 secondes

echo "Serveurs démarrés !"
echo "Madsea PID: $MADSEA_PID (logs dans $MADSEA_LOG)"
echo "ComfyUI PID: $COMFYUI_PID (logs dans $COMFYUI_LOG)"
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"

# Attendre que les processus se terminent
wait 