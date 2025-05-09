# Journal des correctifs Madsea - 09/05/2025

## Corrections backend

| Fichier | Problème | Solution |
|---------|----------|----------|
| `backend/app.py` | Import `os` manquant | Ajout de l'import au début du fichier |
| `backend/app.py` | Route racine manquante | Ajout d'une route pour servir `frontend/index.html` |
| `backend/extraction_api.py` | Route d'upload incorrecte | Correction vers `/api/upload_storyboard_v3` |
| `backend/comfyui_api.py` | Import relatif | Remplacé par import absolu pour stabilité |

## Corrections ComfyUI

| Dépendance | Statut | Utilité |
|------------|--------|---------|
| PyTorch CUDA | ✅ Installé | Génération sur GPU (2.7.0+cu118) |
| transformers | ✅ Installé | Traitement de texte et modèles |
| torchsde | ✅ Installé | Équations différentielles stochastiques |
| scipy | ✅ Installé | Traitement mathématique |
| kornia | ✅ Installé | Traitement d'image (Canny, morphologie) |
| av | ✅ Installé | Traitement vidéo |
| spandrel | ✅ Installé | Modèles d'upscaling |
| comfyui-frontend-package | ✅ Installé | Interface utilisateur web |
| comfyui-workflow-templates | ✅ Installé | Templates de workflows |

## Configuration GPU

```python
# Configuration pour utiliser le GPU pour Madsea
# Pour désactiver CUDA, décommenter la ligne suivante
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
```

## Validation

- ✅ Backend Flask démarre correctement sur port 5000
- ✅ ComfyUI démarre correctement sur port 8188
- ✅ ComfyUI détecte le GPU NVIDIA TITAN X (12GB VRAM)
- ✅ Frontend servi via Flask à l'URL racine
- ✅ Format de sortie 1920×1080 (16:9) confirmé

## Prochaines étapes

1. Tester l'upload de storyboards PDF
2. Vérifier la génération de concepts IA via ComfyUI
3. Valider la nomenclature standardisée des fichiers générés
