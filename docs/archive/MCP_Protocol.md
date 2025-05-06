# PROTOCOL MADSEA

## Workflows utilisateur
1. Importer PDF → Extraire pages automatiquement
2. Vérifier extraction → Ajuster OCR si nécessaire
3. Sélectionner style → Générer images pour tous les plans
4. Prévisualiser/Comparer → Exporter résultats finaux

---

### Pipeline extraction adaptative Madsea

#### Schéma d’architecture
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

#### Détail des modules
- **Extraction d’images** : découpe chaque page ou panel du storyboard en images individuelles (PyMuPDF, pdf2image, Pillow). Adaptable aux formats complexes.
- **Extraction de texte (OCR)** : applique l’OCR à chaque image/panel (Tesseract, EasyOCR, PaddleOCR). Nettoyage, filtrage, reconnaissance des types de plans, dialogues…
- **Structuration des métadonnées** : associe chaque image à ses textes/annotations. Génère un JSON structuré (scènes, timecodes, descriptions, etc.). Permet l’édition/correction par l’utilisateur.
- **Stockage et API** : sauvegarde images extraites + JSON dans le dossier projet. Expose des endpoints Flask pour lister, extraire, modifier, télécharger scènes et métadonnées.

#### Extensibilité
- Pipeline modulaire : chaque étape est un module indépendant, facilement remplaçable (OCR, découpage, structuration, stockage).
- Possibilité d’intégrer de nouveaux formats (Figma, PSD…), modules OCR ou segmentation IA interchangeables.
- Gestion des erreurs, logs, relance d’étape isolée.
- Open source privilégié (Tesseract, PyMuPDF, etc.).
- API RESTful pour communication frontend/backend.
- Documentation systématique.

## Workflows développeur
1. Développer services indépendamment (extraction, génération, UI)
2. Tester extraction PDF en priorité (multi-pages, OCR)
3. Configurer ComfyUI avec workflows ControlNet
4. Respecter nomenclature pour tous les fichiers générés

## Standards de code
- Python: docstrings Google format, typing hints
- Frontend: React fonctionnel, Tailwind pour UI
- Tests: unitaires avant intégration
- Documentation: Markdown dans docs/

## Tests et validation
- Tester chaque extraction PDF séparément
- Valider visuellement les images générées
- Vérifier nomenclature des fichiers générés
- Interface intuitive pour utilisateurs non-techniques

---

## Annexe : Plan de modification front-end

### Objectif
Aligner l'interface utilisateur avec la vision "production SwarmUI modifié" : gestion avancée des styles (Ombres chinoises réalistes/Labo), paramétrage technique, feedback utilisateur, intégration de la todo-list MCP.

### 1. Accueil / Création de projet
- Ajouter un écran ou une section pour la création d'un nouveau projet
- Permettre la sélection du style principal dès la création (Ombres chinoises réalistes / Labo scientifique)
- Afficher les presets styles disponibles (LoRA, ControlNet, prompts), possibilité de dupliquer/éditer

### 2. Paramétrage technique avancé
- Ajouter des sliders/options pour :
    - Lumière (intensité, direction, ambiance : golden hour…)
    - Caméra (angle, profondeur de champ, perspective)
    - Profondeur (activation ControlNet depth, scribble)
- Grouper ces paramètres dans une section dédiée, accessible lors de la création ou édition d'une scène

### 3. Gestion des styles et presets
- Section dédiée à l'upload, l'activation, le training et l'édition de LoRA
- Possibilité d'appliquer un preset à tout le projet ou à une scène spécifique
- Feedback visuel sur le respect du style (preview silhouette, alerte visage détecté)

### 4. Génération et post-process
- Intégrer l'application automatique du negative prompt et des presets techniques (CFG, steps, sampling, ratio)
- Ajouter des options de post-process (grain film, cohérence couleur)

### 5. Intégration de la todo-list MCP
- Afficher la liste des tâches (todo-list) du projet, avec boutons pour lancer/valider chaque étape
- Suivi d'avancement visuel (progress bar, checklist)

### 6. Guidage utilisateur
- Ajouter des bulles d'aide, explications, workflow étape par étape pour chaque action clé

### 7. Respect du code front existant
- Adapter tous les ajouts/modifications à la structure HTML/CSS/JS déjà en place (pas de refonte totale)
- Prévoir des commentaires pour chaque modification afin de faciliter la maintenance

### Sécurité et robustesse
- Vérifier la compatibilité avec les modules Cursor et Gemini 2.5
- Ajouter des messages d'erreur clairs et des fallback si une intégration IA échoue
- Documenter toute limitation ou bug connu lors de l'intégration pour comparaison
- Nomenclature stricte E202_SQ0010-0010_AI-concept_v0001.png

## Gestion des versions
- Incrémentation automatique des versions de fichiers
- Conservation des archives pour comparaison
- Nomenclature stricte E202_SQ0010-0010_AI-concept_v0001.png
