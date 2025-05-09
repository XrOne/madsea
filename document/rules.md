# Règles et Spécifications Techniques du Projet Madsea

## Règles Générales de Travail (Relation CTO-CEO)

**1. Comprendre les objectifs et le contexte**  
- Commencer par identifier l'objectif business/produit et les contraintes (budget, délais, équipes, technologies)
- Poser les questions une à une, sans surcharger d'information

**2. Proposer des solutions claires et pragmatiques**  
- Présenter 2-3 approches avec avantages, inconvénients et estimations
- Recommander fermement l'option optimale avec conviction

**3. Vulgariser et expliquer**  
- Rédiger un résumé exécutif accessible (2-3 phrases)
- Détailler au niveau technique adapté avec schémas si nécessaire
- Utiliser des analogies pour clarifier les concepts complexes

**4. Produire des livrables structurés**  
- Nomenclature standardisée : `E{episode}_SQ{sequence}-{shot}_{task}_v{version}.{extension}`
- Exemple cible : `E202_SQ0010-0010_AI-concept_v0001.jpg`

**5. Itérer et valider**  
- Demander des retours précis après chaque proposition
- Avancer à l'étape suivante sur validation

**6. Rester concentré sur le sujet principal**  
- Traiter un seul point par message
- Rappeler l'objectif si nécessaire

**7. Proactivité et anticipation**  
- Anticiper les besoins techniques standards
- Signaler les risques et proposer des alternatives

**8. Communication et transparence**  
- Maintenir un journal de bord (`log-projet.md`)
- Admettre les limites et proposer des pistes de recherche

## Spécifications Techniques du Projet

### Objectif Général
Convertir un storyboard (PDF ou images avec annotations) en vidéo stylisée via IA, en local ou via API, supportant plusieurs styles (ex: "ombre chinoise Déclics" ou "labo scientifique").

### Architecture et Flux

**Pipeline Principal**:
1. **Extraction de Storyboard**
   - Parser PDF/images, extraire scènes et annotations
   - OCR pour texte incrusté (Tesseract)
   - Structure: `parsing/`

2. **Génération d'Images**
   - Stable Diffusion via ComfyUI ou API
   - Support ControlNet, LoRA, Styles personnalisés
   - Structure: `generation/`

3. **Gestion des Styles**
   - Styles prédéfinis et personnalisables (LoRA)
   - Entraînement de nouveaux styles (upload références)
   - Structure: `styles/`

4. **Génération de Séquence/Vidéo**
   - Assemblage avec FFmpeg
   - Animation avancée (AnimateDiff, WAN 2.1)
   - Structure: `video/`

5. **Interface Utilisateur**
   - Interface web (Flask ou SwarmUI)
   - Upload, sélection de style, aperçu, génération
   - Structure: `ui/`

### Paramètres de Génération
```yaml
generation:
  resolution: "1920x1080"
  style: "declic"  # ou "labo"
  model: "sd15"
  controlnet: true
  controlnet_type: "scribble"

compute:
  prefer_local: true
  fallback_to_cloud: true
  local_engine: "ComfyUI"
  cloud_providers:
    - openai_dalle
    - runway
    - midjourney
    - google_gemini_studio
    - wan_2.1
    - qwen_max
```

### Contraintes UX et Artistiques
- Format 16:9 imposé
- Générer images de début et fin pour chaque séquence
- Style "ombre chinoise" : silhouettes sans visage visible
- Style "labo" : rendu photoréaliste, couleurs crédibles, lumière directionnelle
- Respecter les directions caméra du découpage (travelling, OTS, panoramique, etc.)

### Modèles et Technologies Recommandés
- Stable Diffusion 1.5/XL avec ControlNet pour images
- Deforum pour mouvements de caméra basiques
- Runway pour motion dynamique
- Kling AI pour animation fluide en silhouette
- Format de sortie : 16:9, 24fps, mp4
- Transitions courtes si pas de vidéo générée

### Règles d'Intégration et Priorités
1. L'application doit parser un PDF ou des images et extraire texte + images
2. Utiliser Tesseract OCR si le texte est incrusté dans l'image
3. Génération d'images stylisées via Stable Diffusion (ComfyUI ou API)
4. Possibilité d'entraîner de nouveaux styles (LoRA)
5. Assemblage vidéo avec FFmpeg ou AnimateDiff
6. Architecture Python structurée selon les modules définis
7. Communication en français
8. Autosauvegardes et mémoire du projet (voir autosave.md)

## Autosauvegardes et Continuité
- Autosauvegarde automatique à chaque modification critique
- Stockage horodaté dans `/backups/<project_id>/`
- Restauration via UI "timeline" (style Adobe Premiere)
- Maximum 10 versions par projet (FIFO)
- Jamais de suppression sans confirmation explicite

## Méthodologie de Développement (Bonnes Pratiques)

### Approche Incrémentielle et Conservative
- **PRIORITÉ ABSOLUE** : Privilégier l'amélioration du code existant plutôt que la réécriture complète
- Effectuer un audit du code existant avant toute nouvelle implémentation
- Vérifier les dépendances et fonctionnalités déjà présentes pour éviter les duplications et conflits

### Intégration Progressive
1. **Analyser** l'existant (endpoints API, composants frontend, données)
2. **Auditer** pour identifier les points d'amélioration
3. **Refactoriser** de manière ciblée selon l'architecture documentée
4. **Tester** pour garantir la non-régression des fonctionnalités
5. **Intégrer** de nouvelles fonctionnalités une fois l'existant stabilisé

### Ordre d'Implémentation Recommandé
1. Extraction adaptative (découpage, OCR, structuration)
2. Intégration autosave (vérifier correspondance frontend/backend)
3. Génération de scènes et styles (synchronisation StyleSelector/SceneDisplay)
4. Revue globale et finalisation (tests de bout en bout)

### Sécurité et Vérification
- Documenter systématiquement les modifications dans `log-projet.md`
- Effectuer des tests de non-régression après chaque modification
- Gérer les erreurs et exceptions de manière robuste (logging, fallbacks)
- S'assurer que les composants frontend et backend restent synchronisés

### Nomenclature des Fichiers

La nomenclature standardisée est : `E{episode}_SQ{sequence}-{shot}_{task}_v{version}.{extension}`
Exemple cible : `E202_SQ0010-0010_AI-concept_v0001.jpg`

**Détails des Composants :**
-   `E{episode}`: Identifiant de l'épisode (ex: `E202`). Fourni par l'utilisateur.
-   `SQ{sequence}`: Identifiant de séquence (ex: `SQ0010`, `SQ0020`).
    -   Une séquence regroupe des plans consécutifs de **même style visuel**.
    -   Un changement de style initie une nouvelle séquence.
    -   Numérotation par incréments de 10 (0010, 0020, ...).
    -   Non lié au numéro de page du PDF.
-   `{shot}`: Identifiant du plan au sein d'une séquence (ex: `0010`, `0020`).
    -   Numérotation par incréments de 10 pour chaque image/plan dans la séquence.
    -   Non lié à l'index de l'image sur une page PDF.
-   `{task}`: Tâche effectuée (ex: `AI-concept`, `animation`, `extracted-raw`).
-   `_v{version}`: Version du fichier (ex: `_v0001`). 'v' minuscule, 4 chiffres.
-   `.{extension}`: Extension du fichier (ex: `.png`, `.jpg`).

**Application Spécifique (Phase Initiale d'Extraction via `extraction_api.py/upload_storyboard_v3`) :**

1.  **Fichiers Bruts Extraits (`task: extracted-raw`)**
    *   Ces fichiers sont la matière première et ne sont pas directement livrés au réalisateur sous cette forme pour validation de style.
    *   **Format :** `E{ID_Episode}_P{NumPage4digits}-I{IndexImagePage4digits}_extracted-raw_v0001.{ext}`
        *   `P{NumPage4digits}`: Numéro de page du PDF (ex: `P0001` pour page 1).
        *   `I{IndexImagePage4digits}`: Index de l'image sur la page (ex: `I0001` pour 1ère image/page).
    *   **Exemple :** `E202_P0001-I0001_extracted-raw_v0001.png`

2.  **Fichiers Placeholders pour Test Nomenclature (`task: AI-concept`)**
    *   Générés pour simuler la sortie destinée au réalisateur et tester la nomenclature.
    *   Le contenu est une image PNG blanche (taille indicative : 100x100 pixels).
    *   **Format :** `E{ID_Episode}_SQ0010-{PlanNum4digits}_AI-concept_v0001.{ext}`
        *   `SQ0010`: Séquence par défaut utilisée pour *tous* les placeholders générés lors d'un même upload initial. La segmentation réelle par style viendra plus tard.
        *   `{PlanNum4digits}`: S'incrémente de 10 pour *chaque image distincte extraite du PDF*, en commençant par `0010` (donc 0010, 0020, 0030, ... pour l'ensemble des images du PDF).
    *   **Exemple (pour la 3ème image extraite d'un PDF pour E202) :** `E202_SQ0010-0030_AI-concept_v0001.png`

## Définition des Séquences, Plans et Styles Visuels

La compréhension précise des termes "plan" et "séquence" est cruciale pour le projet Madsea, notamment en lien avec les styles visuels.

*   **Plan**: Un **Plan** correspond à une unique image extraite d'un fichier PDF de storyboard.
*   **Séquence**: Une **Séquence** est un ensemble de plans successifs définis par une **cohérence de style visuel**.
    *   Par exemple, dans la série "Déclic", une séquence "Ombres Chinoises" (générée par IA) comprend tous les plans consécutifs dans ce style. Un changement de style (par exemple, vers un style "Labo" fait en 3D) marque la fin de la séquence "Ombres Chinoises" et le début d'une nouvelle séquence.
*   **Workflow Utilisateur**:
    *   L'utilisateur sélectionnera les plans spécifiques d'un PDF qui composeront une séquence IA (ex: "Ombres Chinoises").
    *   L'utilisateur pourra indiquer le numéro de séquence (`SQxxxx`) dans les textes extraits pour assurer une identification correcte, car toutes les images d'un PDF ne sont pas forcément utilisées.
*   **Impact sur la Nomenclature**:
    *   `E{épisode}_SQ{séquence}-{plan}_{tâche}_v{version}.{ext}`
    *   `SQ{séquence}` est déterminé par ces groupements par style, identifiés par l'utilisateur.
    *   `{plan}` est l'identifiant unique d'une image du storyboard.
    *   `{tâche}` peut refléter le style (ex: `AI-concept-ombre-chinoise`).

Pour plus de détails, se référer au document `docs/004-definition-sequences-plans-styles.md`.