# CONTEXT MADSEA

## État actuel du projet
- Version de développement: 1.0.0
- Focus prioritaire: extraction PDF multi-pages
- Contrainte technique: GPU 12Go (Titan X)
- Nomenclature validée: E202_SQ0010-0010_AI-concept_v0001.png

## Technologies validées
- Extraction: PyMuPDF + Tesseract OCR
- Génération: ComfyUI + ControlNet (Depth/Edge)
- Styles: LoRA silhouette, laboratoire (modèles entraînés)
- Workflows: Intégration storyboard via ControlNet

## Intégrations
- ComfyUI en local (http://localhost:8188)
- Stockage local des fichiers (pas de cloud)
- Modèles LoRA personnalisés pour les styles

## Audience
- Designers
- Réalisateurs
- Artistes visuels sans compétences techniques

---

## Annexe : Intégration Lovable.dev

### Configuration rapide pour développement accéléré

#### Prérequis
1. Connexion à [Lovable.dev](https://lovable.dev)
2. Python 3.8+ avec pip installé
3. Carte graphique NVIDIA recommandée (min. 8GB VRAM)

#### Installation ComfyUI
```bash
# Dépendances Python pour ComfyUI
pip install torch torchvision torchaudio
pip install fastapi uvicorn pillow numpy opencv-python pymupdf pytesseract

# Clonage et configuration ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt
```

#### Modèles requis
- **Modèles de base** : 
  - Stable Diffusion 1.5 ou XL dans le dossier `models/` de ComfyUI
  - ControlNet (Canny, Depth) pour respecter la composition

#### Intégration backend/frontend
1. Configurer le proxy dans le frontend pour communiquer avec le backend Flask/FastAPI
2. Mettre en place la communication backend → ComfyUI via API REST (port 8188)
3. Assurer le partage des fichiers entre backend et ComfyUI

#### Structure projet Lovable recommandée
```
lovable_madsea/
├── backend/          # Services Flask/FastAPI
├── frontend/         # UI HTML ou React
├── comfyui/          # Instance ComfyUI
├── extraction/       # Service d'OCR/extraction
├── styles/           # Gestion des styles IA
├── models/           # Modèles et LoRAs
└── outputs/          # Résultats générés
```