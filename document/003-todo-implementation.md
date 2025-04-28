instale avec mcp 
# 003-todo-implementation.md

## Liste des Tâches d'Implémentation Madsea

Ce document centralise les tâches d'implémentation prioritaires pour Madsea, en suivant une approche incrémentielle pour minimiser les régressions et maximiser la qualité.

### 1. Audit et Stabilisation de l'Existant

- [x] **1.1 Audit du code backend existant**
  - [x] Réviser `app.py` pour identifier les endpoints d'extraction
  - [ ] Vérifier les dépendances (PyMuPDF, Tesseract, etc.) -> *Vérification partielle faite, à compléter*
  - [ ] Documenter l'architecture et les flux actuels

- [x] **1.2 Audit du frontend**
  - [x] Vérifier les composants UploadStoryboard, SceneDisplay, SceneGrid -> *UploadStoryboard adapté, reste à vérifier les autres*
  - [x] Identifier les points d'intégration avec le backend
  - [x] Documenter les besoins en APIs non couverts -> *Partiellement couvert par l'adaptation UploadStoryboard*

- [ ] **1.3 Vérification des dépendances**
  - [ ] Lister les bibliothèques requises pour extraction et OCR
  - [ ] Vérifier les versions et compatibilités
  - [x] Créer/mettre à jour un fichier requirements.txt -> *Fichier présent, vérifier s'il est complet*

### 2. Extraction Adaptative (Pipeline d'Ingestion)

- [ ] **2.1 Refactoring du code d'extraction existant (Backend)**
  - [x] Modulariser le code d'extraction en fonctions autonomes -> *Blueprint créé (`005-backend-extraction.py`)*
  - [ ] Améliorer la gestion d'erreurs et logging
  - [ ] Ajouter des commentaires et documentation
  - [ ] **Implémenter la logique d'extraction réelle (simple et OCR)** pour remplacer les placeholders actuels dans `005-backend-extraction.py`.
  - [ ] **Optionnel :** Mettre en place une extraction asynchrone (e.g., Celery, RQ) pour les traitements longs (OCR).

- [ ] **2.2 Amélioration de l'OCR (Backend)**
  - [ ] Implémenter/optimiser Tesseract (ou autre) pour l'extraction de texte
  - [ ] Ajouter des filtres de prétraitement pour optimiser la détection
  - [ ] Structurer le texte extrait (type de plan, dialogues, etc.)

- [ ] **2.3 Structuration JSON (Backend)**
  - [ ] Définir un schéma JSON clair et robuste pour les scènes extraites
  - [ ] Implémenter l'export/import de ce format
  - [ ] Assurer la compatibilité avec le frontend

- [x] **2.4 Intégration Frontend `UploadStoryboard.jsx`**
  - [x] Adapter l'UI pour choisir entre extraction simple et OCR.
  - [x] Appeler les bons endpoints backend (`/api/upload_storyboard` ou `/api/extraction_storyboard`).
  - [x] Afficher la progression détaillée (uploading, extracting, saving).
  - [x] Intégrer l'appel à `createAutosave` après extraction.

- [ ] **2.5 Intégration Frontend `ProjectView.jsx`**
  - [ ] Passer le `projectId` et `episodeId` actifs au composant `UploadStoryboard`.
  - [ ] Implémenter le handler `onUploadSuccess` pour recevoir les scènes extraites.
  - [ ] Mettre à jour l'affichage des scènes dans `ProjectView` après une extraction réussie.

### 3. Autosauvegardes et Continuité

- [ ] **3.1 Vérification de l'implémentation existante (Backend)**
  - [ ] Tester les endpoints d'autosauvegarde (`/project/<id>/autosave`, `/project/<id>/autosaves`, `/project/<id>/restore/<version>`).
  - [ ] Vérifier la génération et restauration de versions.
  - [ ] Tester la limite FIFO (10 versions max).

- [x] **3.2 Intégration avec le workflow d'extraction (Frontend/Backend)**
  - [x] Déclencher une autosauvegarde après extraction réussie depuis `UploadStoryboard.jsx`.
  - [ ] Sauvegarder les métadonnées d'extraction pertinentes dans l'autosave.
  - [ ] Assurer la restauration complète du contexte après une restauration d'autosave.

- [ ] **3.3 UI Timeline (Frontend)**
  - [ ] Créer/Valider l'implémentation du composant `TimelineVersions`.
  - [ ] Afficher les versions avec détails (date, action, commentaire).
  - [ ] Ajouter des vignettes/previews aux versions sauvegardées.
  - [ ] Permettre la comparaison visuelle entre versions (optionnel).
  - [ ] Améliorer les notifications de sauvegarde/restauration.

### 4. Génération et Styles

- [ ] **4.1 Audit des fonctionnalités de style**
{{ ... }}
- [ ] **4.2 Génération d'images**
    - [ ] Intégrer dans l’UX frontend et backend la possibilité de saisir et stocker une clé API OpenAI (champ sécurisé, validation, feedback utilisateur)
    - [ ] Permettre la génération d’images via OpenAI (GPT-4 Vision, DALL·E, GPT-Image-1) en cloud, avec sélection du moteur (OpenAI, Midjourney, etc.)
    - [ ] Ajouter une gestion d’erreur claire si la clé n’est pas valide ou si le quota est dépassé
    - [ ] Prévoir une interface pour saisir une clé API Midjourney (ou relai Discord/Bridge)
    - [ ] Documenter la procédure pour ajouter une clé API et choisir le moteur dans l’UI
    - [ ] Permettre la sélection du moteur IA (OpenAI, Midjourney, SwarmUI, ComfyUI local) pour chaque génération
    - [ ] Assurer la compatibilité avec les flux locaux (SwarmUI, ComfyUI) et cloud (OpenAI, Midjourney)
    - [ ] Gérer la priorisation locale/cloud (fallback si absence de clé ou quota)

- [ ] **4.3 Intégration styles personnalisés**
{{ ... }}

### 5. Intégration Globale et Finalisation

- [ ] **5.1 Tests bout en bout**
  - [ ] Tester le flux complet : Upload (simple + OCR) -> Affichage Scènes -> Autosave -> Restauration.
  - [ ] Vérifier la gestion des erreurs à chaque étape (frontend et backend).
  - [ ] Valider l'interface utilisateur complète sur différents navigateurs/résolutions.

- [ ] **5.2 Documentation utilisateur**
{{ ... }}
- [ ] **5.3 Optimisations finales**
{{ ... }}

### Prochaines étapes prioritaires

1.  **IMMÉDIAT** : Finaliser l'intégration de `ProjectView.jsx` (tâche 2.5) pour afficher les scènes après upload.
2.  **COURT TERME** : Implémenter la logique d'extraction réelle (simple et OCR) dans le backend (tâche 2.1).
3.  **MOYEN TERME** : Tester et valider le système d'autosauvegarde de bout en bout (tâches 3.1, 3.2, 5.1).
4.  **MOYEN TERME** : Développer l'UI Timeline pour la gestion des versions (tâche 3.3).
5.  **LONG TERME** : Amélioration de l'OCR, génération d'images, styles personnalisés.

## Notes et dépendances

- L'audit doit précéder toute modification pour éviter les régressions
- Chaque tâche complétée doit être documentée dans `log-projet.md`
- Les modifications doivent respecter l'architecture définie dans `001-architecture-extraction-adaptative.md`
- Privilégier les améliorations incrémentales aux réécritures complètes
- **IMPORTANT :** Toujours valider les changements avec Charly avant de les appliquer.