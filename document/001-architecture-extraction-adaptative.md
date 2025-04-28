# 001-architecture-extraction-adaptative.md

## 1. Résumé exécutif

Le pipeline d’extraction adaptative Madsea permet d’importer un storyboard (PDF ou images), d’en découper automatiquement chaque scène/panel, d’extraire les annotations (type de plan, dialogues, indications) via OCR, puis de structurer ces données pour la génération d’images clés et la gestion de projet. L’architecture privilégie la modularité (OCR, découpage, structuration) et l’extensibilité (plugins, nouveaux formats).

## 2. Schéma d’architecture (Markdown/ASCII)

```
+-------------------+
|   Import Storyboard|
| (PDF / Images)    |
+---------+---------+
          |
          v
+---------------------+
|  Découpage visuel   |
| (pages, panels)     |
+---------+-----------+
          |
          v
+---------------------+
|   OCR & Extraction  |
|  (Tesseract, etc.)  |
+---------+-----------+
          |
          v
+---------------------+
| Structuration JSON  |
| (scènes, textes,    |
|  timecodes, etc.)   |
+---------+-----------+
          |
          v
+---------------------+
| Stockage & API      |
| (images + meta)     |
+---------------------+
```

## 3. Description détaillée des modules

### Module 1 : Extraction d’images
- Découpe chaque page ou panel du storyboard en images individuelles.
- Outils : PyMuPDF, pdf2image, Pillow.
- Adaptable pour formats complexes (storyboards multi-panneaux, scans).

### Module 2 : Extraction de texte (OCR)
- Applique l’OCR à chaque image ou panel.
- Outils : Tesseract (open source), EasyOCR, PaddleOCR.
- Nettoyage des résultats et structuration : filtrage, reconnaissance des types de plans, dialogues, etc.

### Module 3 : Structuration des métadonnées
- Associe chaque image à ses textes/annotations.
- Génère un JSON structuré : scènes, timecodes, descriptions, type de plan, etc.
- Permet l’édition/correction par l’utilisateur.

### Module 4 : Stockage et API
- Sauvegarde les images extraites et le JSON dans le dossier projet.
- Expose des endpoints Flask pour : lister, extraire, modifier, télécharger les scènes et métadonnées.

### Extensibilité
- Adapteurs/plugins pour nouveaux formats (Figma, PSD, etc.).
- Modules OCR ou segmentation IA interchangeables.
- Documentation prévue pour l’intégration de nouveaux moteurs.

## 4. Points d’extension et choix techniques
- Modularité : chaque étape du pipeline est un module indépendant, facilement remplaçable.
- Robustesse : gestion des erreurs, logs, possibilité de relancer une étape isolée.
- Open source privilégié (Tesseract, PyMuPDF, etc.).
- API RESTful pour communication frontend/backend.
- Documentation systématique.

---

**Prochaine étape suggérée : plan de déploiement extraction-adaptative (`002-plan-deploiement-extraction-adaptative.md`).**

