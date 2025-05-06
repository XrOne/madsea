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
