# PROTOCOL MADSEA

## Workflows utilisateur
1. Importer PDF → Extraire pages automatiquement
2. Vérifier extraction → Ajuster OCR si nécessaire
3. Sélectionner style → Générer images pour tous les plans
4. Exporter vers FTP du réalisateur → Gérer validations/retours
5. Regenerer plans non validés → Finaliser séquence validée
6. Animer images validées → Produire vidéo finale

---

### Pipeline extraction adaptative Madsea

#### Schéma d'architecture
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
- **Extraction d'images** : découpe chaque page ou panel du storyboard en images individuelles (PyMuPDF, pdf2image, Pillow). Adaptable aux formats complexes.
- **Extraction de texte (OCR)** : applique l'OCR à chaque image/panel (Tesseract, EasyOCR, PaddleOCR). Nettoyage, filtrage, reconnaissance des types de plans, dialogues…
- **Structuration des métadonnées** : associe chaque image à ses textes/annotations. Génère un JSON structuré (scènes, timecodes, descriptions, etc.). Permet l'édition/correction par l'utilisateur.
- **Stockage et API** : sauvegarde images extraites + JSON dans le dossier projet. Expose des endpoints Flask pour lister, extraire, modifier, télécharger scènes et métadonnées.

#### Extensibilité
- Pipeline modulaire : chaque étape est un module indépendant, facilement remplaçable (OCR, découpage, structuration, stockage).
- Possibilité d'intégrer de nouveaux formats (Figma, PSD…), modules OCR ou segmentation IA interchangeables.
- Gestion des erreurs, logs, relance d'étape isolée.
- Open source privilégié (Tesseract, PyMuPDF, etc.).
- API RESTful pour communication frontend/backend.
- Documentation systématique.

## Workflows développeur
1. Développer services indépendamment (extraction, génération, UI)
2. Tester extraction PDF en priorité (multi-pages, OCR)
3. Tester génération ComfyUI (respect storyboard, styles)
4. Implémenter interfaces (backend et frontend)
5. Relier services (extraction → génération → export)

## Validation et sécurité
- Test unitaire par service
- Logs détaillés pour chaque étape
- Backup automatique avant opérations critiques
- Gestion des erreurs et fallback
- Messages utilisateur clairs et informatifs

## Intégrations
- Backend Flask/FastAPI → ComfyUI
- Frontend React.js → Backend
- Extraction → Tesseract OCR
- Génération → ComfyUI
- Cloud APIs → OpenAI DALL-E 3, Midjourney, autres APIs
- FTP Manager → Serveur du réalisateur
- Animation Engine → Services audio/vidéo

## Architecture hybride local/cloud

### Stratégie d’intégration

```
+---------------------------+    +---------------------------+
|       LOCAL ENGINE        |    |       CLOUD ENGINE       |
| (ComfyUI, SD local, etc.)|<-->| (DALL-E, Midjourney,...) |
+---------------------------+    +---------------------------+
            ↑                              ↑
            |                              |
            v                              v
+---------------------------+    +---------------------------+
|     BRIDGE SERVICE        |<-->|     API MANAGER          |
| (load balancing, routing) |    | (keys, quotas, retries)  |
+---------------------------+    +---------------------------+
                    ↑
                    |
                    v
      +---------------------------+
      |      BACKEND API          |
      | (generation orchestration)|
      +---------------------------+
                    ↑
                    |
                    v
      +---------------------------+
      |      FRONTEND UI          |
      |    (deepsitefront.html)   |
      +---------------------------+
```

### Logique de basculement

1. L'utilisateur sélectionne un moteur préféré (local ou cloud) ou "auto"
2. Si "auto" est sélectionné :
   - Essai d'abord avec le moteur local (ComfyUI)
   - En cas d'échec, indisponibilité ou timeout > 30s, bascule automatique vers cloud
   - Priorité configurable des API cloud (ex: DALL-E 3 > Midjourney > Stable Diffusion API)
3. Gestion intelligente des quotas et coûts :
   - Tracking du nombre d'appels par fournisseur
   - Alerte si seuil de budget atteint
   - Rotation des clés API si multiple fournies

## Flux de validation via FTP

### Processus d'export et validation

```
1. Madsea → Génération d'images pour plans (local/cloud)
   |
2. ↓ Export FTP automatique (à la demande ou automatique)
   |
   v
3. Serveur FTP du réalisateur
   |
   ↓ (Notification d'envoi complété)
   |
4. Validation par le réalisateur (externe à l'application)
   |
   ↓ (FTP ou annotation dans Madsea)
   |
5. Récupération des validations/rejets
   |
   ↓ (Filtrage plans validés/rejets)
   |
6. Regénération uniquement des plans rejetés
   |
   ↓ (Répétition processus jusqu'à validation complète)
   |
7. Finalisation de la séquence validée
```

### Nomenclature standardisée pour validation

Chaque image est exportée selon le format :
```
E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}
```

Exemple : `E202_SQ0010-0010_AI-concept_v0001.jpg`

Les versions sont incrémentées automatiquement pour chaque regénération.

## Standards de code
- Python: PEP 8, docstrings Google format
- JavaScript: ES6+, JSDoc
- API: RESTful JSON
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
- Documenter toute limitation ou bug connu lors de l'intégration

## Animation et génération vidéo

### Pipeline de génération vidéo

```
+--------------------+    +--------------------+    +--------------------+
|  Images Validées  |--->|  Traitement Vidéo  |--->|  Export Final      |
| (Plans approuvés) |    | (Animation/Effets) |    | (MP4, MOV, etc.)   |
+--------------------+    +--------------------+    +--------------------+
        |                          ^
        v                          |
+--------------------+    +--------------------+
| Paramètres d'anim. |    |  Assets Audio      |
| (Transitions, etc.) |    | (Musique, Voix)    |
+--------------------+    +--------------------+
```

### Méthodes d'animation

1. **Génération animée simple**:
   - Fondu entre images clés (cross-dissolve)
   - Déplacement de caméra simulé (Ken Burns)
   - Calage sur time code

2. **Animation IA avancée**:
   - Utilisation de modèles text-to-video (ModelScope, VideoFusion, etc.)
   - Modèles image-to-video (Gen-2, Runway, etc.)
   - Interpolation d'images via FILM ou modèles de difféomorphisme

3. **Animation hybride**:
   - Génération des transitions entre plans
   - Animation des éléments au sein d'un plan
   - Déformation controlée (MotionDiff, ControlNet Animation)

### Paramètres techniques vidéo

| Paramètre          | Valeur standard      | Alternatives          |
|---------------------|---------------------|------------------------|
| Format              | MP4 (H.264)         | MOV, WebM             |
| Résolution          | 1920x1080 (HD)      | 3840x2160 (4K)        |
| Framerate           | 24 fps              | 30 fps, 60 fps        |
| Bitrate             | 8-12 Mbps (HD)      | 35-45 Mbps (4K)       |
| Durée par plan      | Selon timecode      | Min 2s par plan       |
| Transitions         | Fondu 12-24 frames  | Cut, Wipe             |
| Audio               | AAC 320kbps         | PCM                   |

## Entraînement LoRA personnalisé

### Workflow d'entraînement

1. **Préparation des données**:
   - Collection d'images de référence (8-20 images de qualité)
   - Préprocessing (redimensionnement, augmentation, annotations)

2. **Configuration de l'entraînement**:
   - Sélection du modèle de base (SD 1.5, SDXL, etc.)
   - Paramètres LoRA (rank: 4-128, alpha: 1-4)
   - Learning rate: 1e-4 standard
   - Époques: 1000-3000 selon dataset

3. **Processus d'entraînement**:
   - Local: utilisation de la GPU si disponible
   - Cloud: service d'entraînement déporté si nécessaire
   - Suivi: métriques de perte, échantillons de validation

4. **Export et utilisation**:
   - Format: safetensors
   - Intégration dans ComfyUI
   - Métadonnées: trigger words, poids recommandé

## Gestion des versions
- Incrémentation automatique des versions de fichiers
- Conservation des archives pour comparaison
- Nomenclature stricte E202_SQ0010-0010_AI-concept_v0001.png