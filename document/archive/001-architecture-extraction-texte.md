# 001-architecture-extraction-texte.md

## Architecture extraction et correction texte Madsea (v1)

### 1. Objectif business
Extraire, structurer et corriger manuellement toutes les informations textuelles d’un storyboard (PDF/images) : dialogues, voix off, indications techniques, hashtags de style (#ombrechinoise, #labo…), pour générer facilement des prompts IA et piloter la suite du pipeline vidéo Madsea.

---

### 2. Workflow global

1. **Ingestion PDF/ZIP**
    - Extraction images (pages, cases)
    - Extraction texte natif (PyMuPDF)
    - OCR sur images (Tesseract/EasyOCR)
2. **Structuration**
    - Mapping image <-> texte(s) (par page/case)
    - Champs : `scene_number`, `image_path`, `dialogue`, `voix_off`, `indications_techniques`, `hashtags_style`, `prompt_suggestion`
3. **Correction manuelle (inline UI)**
    - Pour chaque image : affichage et édition directe des champs
    - Détection/édition des hashtags (#style)
    - Validation rapide scène par scène
4. **Export/usage**
    - Prompts structurés pour génération IA (images/vidéo)
    - Hashtags utilisés pour router le pipeline (ex : #ombrechinoise → LoRA dédié)

---

### 3. Schéma d’architecture (simplifié)

```
PDF/ZIP
  │
  ├─> Extraction images (PyMuPDF, PIL)
  │
  ├─> Extraction texte natif (PyMuPDF)
  │
  └─> OCR images (Tesseract/EasyOCR)
         │
         └─> Mapping image <-> textes (par page/case)
                │
                └─> API REST /api/extract_text
                        │
                        └─> Frontend UI correction inline
                                │
                                └─> Prompts structurés pour pipeline IA/vidéo
```

---

### 4. Exemple de JSON structuré (API REST)

```json
[
  {
    "scene_number": 1,
    "image_path": "page1_img1.jpg",
    "dialogue": "Bonjour, bienvenue au labo!",
    "voix_off": "Le professeur entre en scène.",
    "indications_techniques": "Plan large, ambiance sombre.",
    "hashtags_style": ["#ombrechinoise", "#labo"],
    "prompt_suggestion": "#ombrechinoise Laboratoire sombre, professeur entre, ambiance mystérieuse, dialogue: Bonjour, bienvenue au labo!"
  },
  ...
]
```

---

### 5. Nomenclature & compatibilité API partenaire
- Respect du mapping attendu par l’API partenaire (vérifier les champs exacts)
- Tous les champs sont éditables et exportables en JSON ou prompt texte
- Hashtags reconnus automatiquement, modifiables manuellement

---

### 6. Étapes suivantes
- Prototype backend extraction hybride (texte natif + OCR)
- Prototype API `/api/extract_text`
- Prototype UI correction inline (front)
- Itération UX/UI selon retours

---

**Livrable à jour, prêt pour validation et implémentation.**
